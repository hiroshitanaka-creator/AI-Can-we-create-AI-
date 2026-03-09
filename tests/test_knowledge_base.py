"""tests/test_knowledge_base.py — KnowledgeBase のユニットテスト"""
import json
import os
import tempfile
import unittest

from aicw.knowledge_base import KnowledgeBase, _jaccard


class TestJaccard(unittest.TestCase):
    def test_identical(self):
        self.assertAlmostEqual(_jaccard(["A", "B"], ["A", "B"]), 1.0)

    def test_disjoint(self):
        self.assertAlmostEqual(_jaccard(["A", "B"], ["C", "D"]), 0.0)

    def test_partial(self):
        # {A,B} ∩ {B,C} = {B}, {A,B} ∪ {B,C} = {A,B,C}
        self.assertAlmostEqual(_jaccard(["A", "B"], ["B", "C"]), 1/3, places=4)

    def test_empty_both(self):
        self.assertAlmostEqual(_jaccard([], []), 1.0)

    def test_one_empty(self):
        self.assertAlmostEqual(_jaccard(["A"], []), 0.0)

    def test_symmetric(self):
        a = ["SAFETY_FIRST", "COMPLIANCE_FIRST"]
        b = ["SAFETY_FIRST", "QUALITY_FIRST"]
        self.assertAlmostEqual(_jaccard(a, b), _jaccard(b, a))


class TestKnowledgeBaseBasic(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()

    def test_initial_empty(self):
        self.assertEqual(self.kb.count(), 0)

    def test_record_ok(self):
        entry = self.kb.record("abc123", "ok", ["SAFETY_FIRST"])
        self.assertEqual(entry["status"], "ok")
        self.assertEqual(entry["reason_codes"], ["SAFETY_FIRST"])
        self.assertIsNone(entry["blocked_by"])
        self.assertIn("timestamp_utc", entry)

    def test_record_blocked(self):
        entry = self.kb.record("def456", "blocked", [], blocked_by="#6 Privacy")
        self.assertEqual(entry["status"], "blocked")
        self.assertEqual(entry["blocked_by"], "#6 Privacy")

    def test_record_invalid_status(self):
        with self.assertRaises(ValueError):
            self.kb.record("hash", "unknown", [])

    def test_record_increments_count(self):
        self.kb.record("h1", "ok", ["A"])
        self.kb.record("h2", "ok", ["B"])
        self.assertEqual(self.kb.count(), 2)

    def test_clear(self):
        self.kb.record("h1", "ok", ["A"])
        self.kb.clear()
        self.assertEqual(self.kb.count(), 0)

    def test_max_entries_enforced(self):
        kb = KnowledgeBase(max_entries=3)
        for i in range(5):
            kb.record(f"hash{i}", "ok", [f"CODE{i}"])
        self.assertEqual(kb.count(), 3)
        # 最新3件が残る
        entries = kb.all_entries()
        hashes = [e["decision_hash"] for e in entries]
        self.assertIn("hash4", hashes)
        self.assertIn("hash3", hashes)
        self.assertIn("hash2", hashes)

    def test_max_entries_zero_invalid(self):
        with self.assertRaises(ValueError):
            KnowledgeBase(max_entries=0)

    def test_reason_codes_sorted(self):
        entry = self.kb.record("h", "ok", ["C", "A", "B"])
        self.assertEqual(entry["reason_codes"], ["A", "B", "C"])


class TestKnowledgeBaseFind(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()
        self.kb.record("h1", "ok", ["SAFETY_FIRST", "COMPLIANCE_FIRST"])
        self.kb.record("h2", "ok", ["QUALITY_FIRST", "COMPLIANCE_FIRST"])
        self.kb.record("h3", "blocked", [], blocked_by="#6 Privacy")
        self.kb.record("h4", "ok", ["SAFETY_FIRST", "QUALITY_FIRST"])
        self.kb.record("h5", "ok", ["NO_CONSTRAINTS"])

    def test_find_similar_returns_list(self):
        result = self.kb.find_similar(["SAFETY_FIRST"])
        self.assertIsInstance(result, list)

    def test_find_similar_has_similarity_key(self):
        result = self.kb.find_similar(["SAFETY_FIRST"])
        for r in result:
            self.assertIn("similarity", r)

    def test_find_similar_top_k(self):
        result = self.kb.find_similar(["SAFETY_FIRST"], top_k=2)
        self.assertLessEqual(len(result), 2)

    def test_find_similar_sorted_desc(self):
        result = self.kb.find_similar(["SAFETY_FIRST", "COMPLIANCE_FIRST"])
        similarities = [r["similarity"] for r in result]
        self.assertEqual(similarities, sorted(similarities, reverse=True))

    def test_find_similar_perfect_match_first(self):
        result = self.kb.find_similar(["SAFETY_FIRST", "COMPLIANCE_FIRST"])
        self.assertAlmostEqual(result[0]["similarity"], 1.0, places=2)
        self.assertEqual(result[0]["decision_hash"], "h1")

    def test_find_similar_min_similarity_filter(self):
        result = self.kb.find_similar(["NO_CONSTRAINTS"], min_similarity=0.5)
        # NO_CONSTRAINTS の完全一致は h5 のみ（similarity=1.0 > 0.5）
        for r in result:
            self.assertGreaterEqual(r["similarity"], 0.5)

    def test_find_similar_status_filter_ok(self):
        result = self.kb.find_similar([], status_filter="ok")
        for r in result:
            self.assertEqual(r["status"], "ok")

    def test_find_similar_status_filter_blocked(self):
        result = self.kb.find_similar([], status_filter="blocked")
        for r in result:
            self.assertEqual(r["status"], "blocked")

    def test_find_empty_query_returns_entries(self):
        # 空クエリは全エントリと similarity=0.0（両空=1.0 なので空+非空=0.0）
        result = self.kb.find_similar([], top_k=5)
        # h3 の reason_codes は [] → _jaccard([], []) = 1.0
        hashes = [r["decision_hash"] for r in result]
        self.assertIn("h3", hashes)

    def test_find_disjoint_similarity_zero(self):
        result = self.kb.find_similar(["UNKNOWN_CODE_XYZ"])
        for r in result:
            self.assertAlmostEqual(r["similarity"], 0.0, places=4)


class TestKnowledgeBaseStats(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()
        self.kb.record("h1", "ok", ["SAFETY_FIRST", "COMPLIANCE_FIRST"])
        self.kb.record("h2", "ok", ["SAFETY_FIRST"])
        self.kb.record("h3", "blocked", [], blocked_by="#4 Manipulation")

    def test_stats_counts(self):
        s = self.kb.stats()
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["ok_count"], 2)
        self.assertEqual(s["blocked_count"], 1)

    def test_top_reason_codes(self):
        s = self.kb.stats()
        top_codes = dict(s["top_reason_codes"])
        self.assertEqual(top_codes.get("SAFETY_FIRST"), 2)
        self.assertEqual(top_codes.get("COMPLIANCE_FIRST"), 1)

    def test_has_persistent_storage_false(self):
        s = self.kb.stats()
        self.assertFalse(s["has_persistent_storage"])


class TestKnowledgeBasePersistence(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            kb1 = KnowledgeBase(path=path)
            kb1.record("h1", "ok", ["SAFETY_FIRST"])
            kb1.record("h2", "blocked", [], blocked_by="#6 Privacy")

            # 新しいインスタンスでロード
            kb2 = KnowledgeBase(path=path)
            self.assertEqual(kb2.count(), 2)
            entries = kb2.all_entries()
            hashes = {e["decision_hash"] for e in entries}
            self.assertIn("h1", hashes)
            self.assertIn("h2", hashes)
        finally:
            os.unlink(path)

    def test_json_format_valid(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name

        try:
            kb = KnowledgeBase(path=path)
            kb.record("h1", "ok", ["A", "B"])
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertIn("version", data)
            self.assertIn("entries", data)
            self.assertEqual(len(data["entries"]), 1)
        finally:
            os.unlink(path)

    def test_load_nonexistent_file_empty(self):
        kb = KnowledgeBase(path="/tmp/nonexistent_aicw_kb_xyz.json")
        self.assertEqual(kb.count(), 0)

    def test_save_without_path_raises(self):
        kb = KnowledgeBase()  # パスなし
        kb.record("h", "ok", [])
        with self.assertRaises(ValueError):
            kb.save()  # path 未指定

    def test_save_to_explicit_path(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            kb = KnowledgeBase()
            kb.record("h1", "ok", ["A"])
            kb.save(path=path)
            kb2 = KnowledgeBase(path=path)
            self.assertEqual(kb2.count(), 1)
        finally:
            os.unlink(path)

    def test_max_entries_on_load(self):
        """ファイルにエントリが多すぎる場合、max_entries に収まるよう切り捨て。"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
            entries = [
                {"decision_hash": f"h{i}", "status": "ok",
                 "reason_codes": [], "timestamp_utc": "2026-01-01T00:00:00+00:00"}
                for i in range(10)
            ]
            json.dump({"version": "knowledge_base.v0.1", "max_entries": 10, "entries": entries}, f)

        try:
            kb = KnowledgeBase(path=path, max_entries=3)
            self.assertLessEqual(kb.count(), 3)
        finally:
            os.unlink(path)
