import unittest

from aicw.decision import build_decision_report, format_report
from aicw.safety import scan_manipulation, ManipulationHit


class TestP0Manipulation(unittest.TestCase):
    # ------------------------------------------------------------------
    # scan_manipulation の基本動作
    # ------------------------------------------------------------------

    def test_detects_warn_phrase(self):
        # "今すぐ" は warn レベルで検知される
        s = "今" + "すぐ"
        hits = scan_manipulation("これは" + s + "やるべき")
        self.assertTrue(len(hits) >= 1)
        warn_phrases = [h.phrase for h in hits if h.severity == "warn"]
        self.assertIn(s, warn_phrases)

    def test_detects_block_phrase(self):
        # "炎上" は block レベルで検知される
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
        # warn と block が同時に存在する場合、両方検知する
        s_warn = "必" + "ず"
        s_block = "拡" + "散"
        hits = scan_manipulation(s_warn + "して" + s_block + "せよ")
        severities = {h.severity for h in hits}
        self.assertIn("warn", severities)
        self.assertIn("block", severities)

    # ------------------------------------------------------------------
    # build_decision_report: block hit → ステータス "blocked"
    # ------------------------------------------------------------------

    def test_report_blocked_on_block_phrase_in_option(self):
        # 選択肢に block フレーズが含まれると出力レポートでブロックされる
        req = {
            "situation": "方針を決めたい",
            "constraints": [],
            "options": ["炎" + "上させる", "穏当に対処", "保留"],
        }
        report = build_decision_report(req)
        self.assertEqual("blocked", report["status"])
        self.assertEqual("#4 Manipulation", report["blocked_by"])

    # ------------------------------------------------------------------
    # build_decision_report: warn hit のみ → "ok" + warnings フィールド
    # ------------------------------------------------------------------

    def test_report_ok_with_warnings_on_warn_phrase(self):
        # 選択肢に warn フレーズが含まれると、ブロックはされず warnings が付く
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
