from __future__ import annotations

import json
import os
import unittest

from aicw.decision import build_decision_report


class TestCultureDiff(unittest.TestCase):
    _CASES_PATH = os.path.join(
        os.path.dirname(__file__), "data", "culture_cases.json"
    )

    @classmethod
    def setUpClass(cls):
        with open(cls._CASES_PATH, encoding="utf-8") as f:
            cls.cases = json.load(f)

    def test_status_invariant_within_each_culture_case(self):
        for case in self.cases:
            req = case["request"]
            statuses = case["status_variants"]
            reports = [
                build_decision_report({**req, "asker_status": s})
                for s in statuses
            ]
            for report in reports:
                self.assertEqual("ok", report["status"], msg=case["id"])

            base = reports[0]["selection"]
            for report in reports[1:]:
                self.assertEqual(
                    base["recommended_id"],
                    report["selection"]["recommended_id"],
                    msg=f"status-invariant failed: {case['id']}",
                )
                self.assertEqual(
                    base["reason_codes"],
                    report["selection"]["reason_codes"],
                    msg=f"reason_codes changed by status: {case['id']}",
                )

    def test_expected_recommendation_by_case(self):
        for case in self.cases:
            req = case["request"]
            expected = case["expected_recommended_id"]
            report = build_decision_report(req)
            self.assertEqual("ok", report["status"], msg=case["id"])
            self.assertEqual(
                expected,
                report["selection"]["recommended_id"],
                msg=f"unexpected recommendation: {case['id']}",
            )


if __name__ == "__main__":
    unittest.main()
