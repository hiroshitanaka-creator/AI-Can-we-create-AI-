import unittest

from aicw import build_decision_report
from aicw.philosophy_check import (
    DUTY_OUTCOME_CONFLICT,
    FAIRNESS_EFFICIENCY_CONFLICT,
    RIGHTS_TOTAL_BENEFIT_CONFLICT,
    detect_philosophy_conflicts,
)


class TestPhilosophyCheck(unittest.TestCase):
    def test_empty_text_returns_empty(self):
        self.assertEqual(detect_philosophy_conflicts(""), [])

    def test_detects_duty_vs_outcome_conflict(self):
        text = "規則は絶対に守るべきだが、成果を最大化するため例外を容認する。"
        codes = detect_philosophy_conflicts(text)
        self.assertIn(DUTY_OUTCOME_CONFLICT, codes)

    def test_detects_fairness_vs_efficiency_conflict(self):
        text = "公平を重視する。しかし効率と生産性のため一部犠牲を許容する。"
        codes = detect_philosophy_conflicts(text)
        self.assertIn(FAIRNESS_EFFICIENCY_CONFLICT, codes)

    def test_detects_rights_vs_total_benefit_conflict(self):
        text = "権利を守ると言いつつ、全体の便益と多数の利益のため例外を優先する。"
        codes = detect_philosophy_conflicts(text)
        self.assertIn(RIGHTS_TOTAL_BENEFIT_CONFLICT, codes)

    def test_no_conflict_when_single_axis(self):
        text = "公平と公正を守り、差別を避ける。"
        self.assertEqual(detect_philosophy_conflicts(text), [])


class TestPhilosophyIntegration(unittest.TestCase):
    def test_reason_codes_include_philo_code_in_report(self):
        req = {
            "situation": "規則を守るべきだが、成果を最大化するため例外を容認する方針を検討"
        }
        report = build_decision_report(req)
        self.assertEqual(report["status"], "ok")
        self.assertIn("PHILO_DUTY_OUTCOME_CONFLICT", report["selection"]["reason_codes"])


if __name__ == "__main__":
    unittest.main()
