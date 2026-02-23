import unittest

from aicw.decision import build_decision_report, format_report
from aicw.safety import scan_manipulation


class TestP0Manipulation(unittest.TestCase):
    def test_detects_manipulation_phrase(self):
        s = "今" + "すぐ"
        hits = scan_manipulation("これは" + s + "やるべき")
        self.assertTrue(len(hits) >= 1)

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
