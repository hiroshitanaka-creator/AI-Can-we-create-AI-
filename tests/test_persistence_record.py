import unittest

from aicw import build_decision_report, build_persistence_record


class TestPersistenceRecord(unittest.TestCase):
    def test_ok_report_excludes_full_text_fields(self):
        report = build_decision_report(
            {
                "situation": "採用方針を決めたい",
                "constraints": ["法令遵守", "公平性"],
                "options": ["A: 既存方式", "B: AI補助方式", "C: 外部委託"],
            }
        )
        self.assertEqual(report["status"], "ok")

        rec = build_persistence_record(report)
        self.assertEqual(rec["status"], "ok")
        self.assertIn("recommended_id", rec)
        self.assertIn("reason_codes", rec)
        self.assertIn("record_hash", rec)

        # 生テキスト保存を避ける
        self.assertNotIn("input", rec)
        self.assertNotIn("candidates", rec)
        self.assertNotIn("selection", rec)
        self.assertNotIn("explanation", rec)

    def test_blocked_report_keeps_only_minimal_fields(self):
        report = build_decision_report({"situation": "token=abcd1234"})
        self.assertEqual(report["status"], "blocked")

        rec = build_persistence_record(report)
        self.assertEqual(rec["status"], "blocked")
        self.assertIn("blocked_by", rec)
        self.assertIn("detected", rec)
        self.assertIn("record_hash", rec)

        self.assertNotIn("safe_alternatives", rec)
        self.assertNotIn("redacted_preview", rec)

    def test_invalid_status_raises(self):
        with self.assertRaises(ValueError):
            build_persistence_record({"status": "unknown"})


if __name__ == "__main__":
    unittest.main()
