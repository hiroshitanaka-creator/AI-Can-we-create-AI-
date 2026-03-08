import unittest

from aicw.decision import build_decision_report, format_report
from aicw.safety import scan_manipulation, ManipulationHit


class TestP0Manipulation(unittest.TestCase):
    # ------------------------------------------------------------------
    # scan_manipulation の基本動作
    # ------------------------------------------------------------------

    def test_detects_warn_phrase(self):
        s = "今" + "すぐ"
        hits = scan_manipulation("これは" + s + "やるべき")
        self.assertTrue(len(hits) >= 1)
        warn_phrases = [h.phrase for h in hits if h.severity == "warn"]
        self.assertIn(s, warn_phrases)

    def test_detects_block_phrase(self):
        hits = scan_manipulation("炎上させよう")
        self.assertTrue(len(hits) >= 1)
        block_phrases = [h.phrase for h in hits if h.severity == "block"]
        self.assertIn("炎上", block_phrases)

    def test_clean_text_has_no_hits(self):
        hits = scan_manipulation("バランスよく進める方針を検討します。")
        self.assertEqual([], hits)

    def test_returns_manipulation_hit_objects(self):
        s = "従" + "え"
        hits = scan_manipulation(s)
        self.assertIsInstance(hits[0], ManipulationHit)
        self.assertEqual("block", hits[0].severity)

    def test_detects_multiple_severities(self):
        s_warn = "必" + "ず"
        s_block = "拡" + "散"
        hits = scan_manipulation(s_warn + "して" + s_block + "せよ")
        severities = {h.severity for h in hits}
        self.assertIn("block", severities)

    # ------------------------------------------------------------------
    # スコアリング強化（Task 6）
    # ------------------------------------------------------------------

    def test_warn_score_escalates_to_block(self):
        text = "今すぐ必ず絶対やれ"
        hits = scan_manipulation(text)
        self.assertTrue(hits)
        self.assertTrue(all(h.severity == "block" for h in hits))

    def test_low_warn_score_stays_warn(self):
        text = "今すぐ確認してください"
        hits = scan_manipulation(text)
        self.assertTrue(hits)
        self.assertTrue(all(h.severity == "warn" for h in hits))

    def test_imperative_pattern_contributes_score(self):
        text = "必ず実施しろ"
        hits = scan_manipulation(text)
        phrases = {h.phrase for h in hits}
        self.assertIn("命令調", phrases)

    def test_false_positive_guard_cases_10(self):
        safe_cases = [
            "可能なら今日中に確認したいです。",
            "早めに確認できると助かります。",
            "推奨案を比較しながら判断します。",
            "将来的に改善できる余地があります。",
            "根拠と不確実性を並べて検討します。",
            "品質を保ちつつ段階導入します。",
            "情報共有を丁寧に進めます。",
            "候補案のメリット・デメリットを整理します。",
            "関係者の合意形成を優先します。",
            "問題があれば再評価します。",
        ]
        for text in safe_cases:
            with self.subTest(text=text):
                self.assertEqual([], scan_manipulation(text))

    def test_detection_cases_10(self):
        risky_cases = [
            ("絶対に成功させる", True),
            ("必ず従え", True),
            ("今すぐ拡散せよ", True),
            ("信じてついてこい", True),
            ("間違いなくやれ", True),
            ("炎上させる", True),
            ("洗脳してでも達成する", True),
            ("許せない相手を排除する", True),
            ("今すぐ絶対実施しろ", True),
            ("必ずやれ", True),
        ]
        for text, expected_hit in risky_cases:
            with self.subTest(text=text):
                hits = scan_manipulation(text)
                self.assertEqual(expected_hit, len(hits) > 0)

    # ------------------------------------------------------------------
    # build_decision_report: block hit → ステータス "blocked"
    # ------------------------------------------------------------------

    def test_report_blocked_on_block_phrase_in_option(self):
        req = {
            "situation": "方針を決めたい",
            "constraints": [],
            "options": ["炎" + "上させる", "穏当に対処", "保留"],
        }
        report = build_decision_report(req)
        self.assertEqual("blocked", report["status"])
        self.assertEqual("#4 Manipulation", report["blocked_by"])

    def test_report_blocked_on_warn_score_escalation(self):
        req = {
            "situation": "対応方針を決めたい",
            "constraints": [],
            "options": ["今すぐ絶対必ずやれ", "慎重に進める", "保留"],
        }
        report = build_decision_report(req)
        self.assertEqual("blocked", report["status"])
        self.assertEqual("#4 Manipulation", report["blocked_by"])

    # ------------------------------------------------------------------
    # build_decision_report: warn hit のみ → "ok" + warnings フィールド
    # ------------------------------------------------------------------

    def test_report_ok_with_warnings_on_warn_phrase(self):
        req = {
            "situation": "方針を決めたい",
            "constraints": [],
            "options": ["必" + "ず成功させる", "段階的に進める", "保留"],
        }
        report = build_decision_report(req)
        self.assertEqual("ok", report["status"])
        self.assertIn("warnings", report)
        self.assertTrue(len(report["warnings"]) >= 1)

    # ------------------------------------------------------------------
    # build_decision_report: クリーンな入力 → "ok" / 警告なし
    # ------------------------------------------------------------------

    def test_report_is_neutral(self):
        report = build_decision_report(
            {
                "situation": "意思決定の整理をしたい",
                "constraints": [],
                "options": [],
            }
        )
        self.assertEqual("ok", report["status"])
        text = format_report(report)
        hits = scan_manipulation(text)
        self.assertEqual([], hits)
        self.assertNotIn("warnings", report)


if __name__ == "__main__":
    unittest.main()
