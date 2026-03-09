import json
import subprocess
import sys
import unittest

from aicw import build_decision_report
from aicw.schema import DECISION_BRIEF_V0, DECISION_REQUEST_V0, validate_request


class TestApiContractSchema(unittest.TestCase):
    def test_request_required_and_allowed(self):
        self.assertIn("situation", DECISION_REQUEST_V0["allowed_fields"])
        self.assertTrue(DECISION_REQUEST_V0["fields"]["situation"]["required"])

    def test_request_rejects_unknown_field(self):
        errors = validate_request({"situation": "x", "unknown": 1})
        self.assertTrue(any("不明なフィールド" in e for e in errors))

    def test_brief_status_enum_is_fixed(self):
        status_enum = DECISION_BRIEF_V0["fields"]["status"]["enum"]
        self.assertEqual(status_enum, ["ok", "blocked"])

    def test_blocked_by_values_are_fixed(self):
        values = set(DECISION_BRIEF_V0["reason_codes"]["blocked_by_values"].keys())
        self.assertEqual(values, {"#6 Privacy", "#5 Existence Ethics", "#4 Manipulation"})


class TestApiContractRuntime(unittest.TestCase):
    def test_ok_response_has_required_keys(self):
        report = build_decision_report({"situation": "新機能の導入方針を決める"})
        self.assertEqual(report.get("status"), "ok")
        for key in [
            "meta",
            "input",
            "candidates",
            "selection",
            "counterarguments",
            "uncertainties",
            "externalities",
            "next_questions",
            "existence_analysis",
            "impact_map",
            "disclaimer",
        ]:
            self.assertIn(key, report)

    def test_blocked_response_has_required_keys(self):
        report = build_decision_report({"situation": "token"})
        self.assertEqual(report.get("status"), "blocked")
        for key in ["blocked_by", "reason", "detected", "safe_alternatives"]:
            self.assertIn(key, report)


class TestApiContractCliExitCode(unittest.TestCase):
    def test_cli_exit_0_on_ok(self):
        payload = {"situation": "開発優先順位を決める"}
        p = subprocess.run(
            [sys.executable, "scripts/brief.py"],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(p.returncode, 0)

    def test_cli_exit_1_on_blocked(self):
        payload = {"situation": "今すぐ従え"}
        p = subprocess.run(
            [sys.executable, "scripts/brief.py"],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(p.returncode, 1)

    def test_cli_exit_2_on_invalid_json(self):
        p = subprocess.run(
            [sys.executable, "scripts/brief.py"],
            input="{bad json}",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
