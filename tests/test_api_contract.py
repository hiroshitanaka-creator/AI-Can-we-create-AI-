import json
import subprocess
import sys
import unittest

from aicw import build_decision_report
from aicw.schema import DECISION_BRIEF_V0, DECISION_REQUEST_V0, validate_request
from bridge.po_core_bridge import analyze_philosophy_tensor, get_tensor_schema


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

class TestPoCoreBridgeContract(unittest.TestCase):
    def test_tensor_schema_contract_is_fixed(self):
        schema = get_tensor_schema()
        self.assertEqual(schema["bridge_version"], "v0.1")
        self.assertEqual(schema["schema_version"], "philosophy_tensor.v0.1")
        self.assertEqual(
            set(schema["tensor_components"].keys()),
            {"W_eth", "T_free", "T_sub", "Po"},
        )

    def test_t_sub_risk_enum_is_fixed(self):
        schema = get_tensor_schema()
        self.assertEqual(
            schema["tensor_components"]["T_sub"]["risk_level_values"],
            ["block", "warn", "clear"],
        )

    def test_analyze_tensor_output_has_required_keys(self):
        result = analyze_philosophy_tensor(
            situation="新しい評価制度の導入方針を決める",
            explanation="効率化と公平性の両立を重視する",
            human_decision="段階導入で進める",
            existence_analysis={
                "q1_beneficiary": "employees",
                "q2_structures": ["社会", "認知"],
                "q3_judgment": "lifecycle",
                "impact_score": 4,
            },
        )
        for key in ["schema_version", "tensor", "summary", "disclaimer", "po_core_compatibility"]:
            self.assertIn(key, result)

        self.assertEqual(result["schema_version"], "philosophy_tensor.v0.1")
        self.assertEqual(result["po_core_compatibility"]["bridge_version"], "v0.1")
        self.assertEqual(result["po_core_compatibility"]["tensor_fields"], ["W_eth", "T_free", "T_sub", "Po"])
        self.assertTrue(result["po_core_compatibility"]["stable_api"])

    def test_tensor_component_required_fields_exist(self):
        schema = get_tensor_schema()
        result = analyze_philosophy_tensor(
            situation="人員再配置方針を検討する",
            explanation="短期効率を優先して進める",
            human_decision="再配置を実施する",
            existence_analysis={
                "q1_beneficiary": "company",
                "q2_structures": ["個人", "社会"],
                "q3_judgment": "lifecycle",
                "impact_score": 3,
            },
        )

        tensor = result["tensor"]
        for name in ["W_eth", "T_free", "T_sub"]:
            required = schema["tensor_components"][name]["required_fields"]
            for field in required:
                self.assertIn(field, tensor[name], f"{name}.{field} is missing")

        self.assertIn("available", tensor["Po"])
        self.assertIn("note", tensor["Po"])
        if tensor["Po"]["available"]:
            for field in schema["tensor_components"]["Po"]["required_fields_if_available"]:
                self.assertIn(field, tensor["Po"], f"Po.{field} is missing")

