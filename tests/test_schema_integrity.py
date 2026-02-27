"""
test_schema_integrity.py

DECISION_BRIEF_V0 スキーマと build_decision_report の実際の出力が
整合しているかを検証するコントラクトテスト。

また、validate_request() の動作も網羅的にテストする。
"""

import unittest

from aicw import (
    build_decision_report,
    DECISION_BRIEF_V0,
    DECISION_REQUEST_V0,
    validate_request,
)


# スキーマから known reason code セットを取得
_KNOWN_SELECTION_CODES = set(DECISION_BRIEF_V0["reason_codes"]["selection"].keys())
_KNOWN_NOT_SELECTED_CODES = set(DECISION_BRIEF_V0["reason_codes"]["not_selected"].keys())
_STATUS_ENUM = set(DECISION_BRIEF_V0["fields"]["status"]["enum"])

# ok 時に必ず存在するべきフィールド
_REQUIRED_OK_FIELDS = {
    k for k, v in DECISION_BRIEF_V0["fields"].items()
    if v.get("required_if") == "status == ok"
} | {"status"}

# blocked 時に必ず存在するべきフィールド
_REQUIRED_BLOCKED_FIELDS = {
    k for k, v in DECISION_BRIEF_V0["fields"].items()
    if v.get("required_if") == "status == blocked"
} | {"status"}


class TestValidateRequest(unittest.TestCase):
    """validate_request() の動作テスト"""

    def test_valid_full(self):
        errors = validate_request({
            "situation": "テスト", "constraints": ["安全"], "options": ["A", "B", "C"]
        })
        self.assertEqual([], errors)

    def test_valid_minimal(self):
        errors = validate_request({"situation": "テスト"})
        self.assertEqual([], errors)

    def test_missing_situation(self):
        errors = validate_request({"constraints": ["安全"]})
        self.assertTrue(any("situation" in e for e in errors))

    def test_wrong_type_situation(self):
        errors = validate_request({"situation": 123})
        self.assertTrue(any("situation" in e for e in errors))

    def test_wrong_type_constraints(self):
        errors = validate_request({"situation": "ok", "constraints": "安全"})
        self.assertTrue(any("constraints" in e for e in errors))

    def test_wrong_type_options(self):
        errors = validate_request({"situation": "ok", "options": "案A"})
        self.assertTrue(any("options" in e for e in errors))

    def test_typo_field_hint(self):
        errors = validate_request({"situation": "ok", "constrint": ["安全"]})
        self.assertTrue(any("constraints" in e for e in errors))

    def test_unknown_field_no_hint(self):
        errors = validate_request({"situation": "ok", "completely_unknown": "x"})
        self.assertTrue(any("completely_unknown" in e for e in errors))

    def test_not_a_dict(self):
        errors = validate_request(["situation", "テスト"])
        self.assertTrue(len(errors) >= 1)


class TestDecisionBriefSchema(unittest.TestCase):
    """build_decision_report の出力が DECISION_BRIEF_V0 スキーマと整合しているか"""

    # ------------------------------------------------------------------
    # OK レポートのフィールド検証
    # ------------------------------------------------------------------

    def _ok_report(self, constraints=None, options=None):
        return build_decision_report({
            "situation": "テスト用意思決定",
            "constraints": constraints or [],
            "options": options or ["案A", "案B", "案C"],
        })

    def test_ok_report_status_is_ok(self):
        report = self._ok_report()
        self.assertEqual("ok", report["status"])

    def test_ok_report_status_in_enum(self):
        report = self._ok_report()
        self.assertIn(report["status"], _STATUS_ENUM)

    def test_ok_report_has_all_required_fields(self):
        report = self._ok_report()
        for field in _REQUIRED_OK_FIELDS:
            self.assertIn(field, report, msg=f"ok レポートに必須フィールド '{field}' が存在しない")

    def test_ok_report_candidates_structure(self):
        report = self._ok_report()
        candidates = report["candidates"]
        self.assertEqual(3, len(candidates), "candidates は常に3件")
        ids = [c["id"] for c in candidates]
        self.assertEqual(["A", "B", "C"], ids)
        for c in candidates:
            self.assertIn("id", c)
            self.assertIn("summary", c)
            self.assertIn("not_selected_reason_code", c)

    def test_ok_report_selection_structure(self):
        report = self._ok_report()
        sel = report["selection"]
        self.assertIn("recommended_id", sel)
        self.assertIn("reason_codes", sel)
        self.assertIn("explanation", sel)
        self.assertIn(sel["recommended_id"], ["A", "B", "C"])

    def test_ok_report_selection_reason_codes_in_schema(self):
        # 全シナリオで reason_codes が schema の既知コードの範囲内であること
        scenarios = [
            {"constraints": ["安全"]},
            {"constraints": ["リスク"]},
            {"constraints": ["品質"]},
            {"constraints": ["コンプラ"]},
            {"constraints": ["至急"]},
            {"constraints": ["期限"]},
            {"constraints": ["スピード"]},
            {"constraints": []},
        ]
        for s in scenarios:
            report = self._ok_report(constraints=s["constraints"])
            for code in report["selection"]["reason_codes"]:
                self.assertIn(
                    code, _KNOWN_SELECTION_CODES,
                    msg=f"未知の selection reason_code: '{code}' (constraints={s['constraints']})"
                )

    def test_ok_report_not_selected_reason_codes_in_schema(self):
        report = self._ok_report(constraints=["安全"])
        for c in report["candidates"]:
            code = c["not_selected_reason_code"]
            self.assertIn(
                code, _KNOWN_NOT_SELECTED_CODES,
                msg=f"未知の not_selected_reason_code: '{code}' (id={c['id']})"
            )

    def test_ok_report_recommended_candidate_is_na(self):
        report = self._ok_report(constraints=["安全"])
        rec_id = report["selection"]["recommended_id"]
        for c in report["candidates"]:
            if c["id"] == rec_id:
                self.assertEqual("N/A", c["not_selected_reason_code"])

    # ------------------------------------------------------------------
    # BLOCKED (#6 Privacy) レポートのフィールド検証
    # ------------------------------------------------------------------

    def test_blocked_privacy_report_has_all_required_fields(self):
        email = "x" + "@" + "y" + "." + "co"
        report = build_decision_report({"situation": "連絡先は " + email, "constraints": []})
        self.assertEqual("blocked", report["status"])
        for field in _REQUIRED_BLOCKED_FIELDS:
            self.assertIn(field, report, msg=f"blocked レポートに必須フィールド '{field}' が存在しない")

    def test_blocked_privacy_status_in_enum(self):
        email = "x" + "@" + "y" + "." + "co"
        report = build_decision_report({"situation": "連絡先は " + email, "constraints": []})
        self.assertIn(report["status"], _STATUS_ENUM)

    def test_blocked_privacy_detected_is_list(self):
        email = "x" + "@" + "y" + "." + "co"
        report = build_decision_report({"situation": "連絡先は " + email, "constraints": []})
        self.assertIsInstance(report["detected"], list)

    # ------------------------------------------------------------------
    # BLOCKED (#4 Manipulation) レポートのフィールド検証
    # ------------------------------------------------------------------

    def test_blocked_manipulation_report_has_all_required_fields(self):
        report = build_decision_report({
            "situation": "方針を決めたい",
            "constraints": [],
            "options": ["炎" + "上させる", "穏当に対処", "保留"],
        })
        self.assertEqual("blocked", report["status"])
        for field in _REQUIRED_BLOCKED_FIELDS:
            self.assertIn(field, report, msg=f"#4 blocked レポートに必須フィールド '{field}' が存在しない")

    # ------------------------------------------------------------------
    # DECISION_REQUEST_V0 スキーマ構造の整合確認
    # ------------------------------------------------------------------

    def test_request_schema_allowed_fields_covers_required(self):
        # allowed_fields が required フィールドを全て含むこと
        allowed = set(DECISION_REQUEST_V0["allowed_fields"])
        for f, v in DECISION_REQUEST_V0["fields"].items():
            if v.get("required", False):
                self.assertIn(f, allowed, msg=f"required フィールド '{f}' が allowed_fields に存在しない")


if __name__ == "__main__":
    unittest.main()
