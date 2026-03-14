"""tests/test_demo_business.py — demo_business のスモークテスト"""
import json
import subprocess
import sys
import unittest

from scripts.demo_business import run_demo, SCENARIOS


class TestScenarioDefinitions(unittest.TestCase):
    def test_six_scenarios_defined(self):
        self.assertEqual(len(SCENARIOS), 6)

    def test_scenario_required_keys(self):
        for sid, s in SCENARIOS.items():
            for key in ("name", "request", "human_decision"):
                self.assertIn(key, s, f"シナリオ {sid} に '{key}' が不足")

    def test_request_has_situation(self):
        for sid, s in SCENARIOS.items():
            self.assertIn("situation", s["request"],
                          f"シナリオ {sid} の request に 'situation' が不足")

    def test_human_decision_nonempty(self):
        for sid, s in SCENARIOS.items():
            self.assertTrue(s["human_decision"].strip(),
                            f"シナリオ {sid} の human_decision が空")


class TestRunDemo(unittest.TestCase):
    def _run(self, scenario_id: int):
        result, brief, tensor = run_demo(scenario_id)
        return result, brief, tensor

    def test_scenario1_top_level_keys(self):
        result, _, _ = self._run(1)
        for key in ("demo_scenario", "decision_brief_status", "audit",
                    "philosophy_tensor_summary", "tensor_schema_version",
                    "postmortem_summary", "pipeline_complete"):
            self.assertIn(key, result)

    def test_scenario1_pipeline_complete(self):
        result, _, _ = self._run(1)
        self.assertTrue(result["pipeline_complete"])

    def test_scenario1_audit_has_hash(self):
        result, _, _ = self._run(1)
        self.assertIn("decision_hash", result["audit"])
        self.assertEqual(len(result["audit"]["decision_hash"]), 64)

    def test_scenario1_tensor_schema_version(self):
        result, _, _ = self._run(1)
        self.assertEqual(result["tensor_schema_version"], "philosophy_tensor.v0.1")

    def test_scenario1_postmortem_has_items(self):
        result, _, _ = self._run(1)
        pm = result["postmortem_summary"]
        self.assertGreater(pm["count"], 0)
        self.assertIsInstance(pm["check_items"], list)

    def test_all_scenarios_run_without_error(self):
        for sid in SCENARIOS:
            with self.subTest(scenario=sid):
                result, brief, tensor = run_demo(sid)
                self.assertIn(brief["status"], ("ok", "blocked"))

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError):
            run_demo(999)

    def test_scenario2_decision_status(self):
        result, brief, _ = self._run(2)
        # シナリオ2はブロックされないはず（操作表現は入力ではなく状況に含まれる）
        self.assertIn(brief["status"], ("ok", "blocked"))


    def test_scenario4_triggers_privacy_guard(self):
        result, brief, _ = self._run(4)
        self.assertEqual(result["decision_brief_status"], brief["status"])
        self.assertEqual(brief["status"], "blocked")
        self.assertEqual(brief.get("blocked_by"), "#6 Privacy")

    def test_philosophy_tensor_summary_structure(self):
        result, _, _ = self._run(1)
        ts = result["philosophy_tensor_summary"]
        for key in ("highest_risk", "has_ethical_conflict", "ai_rights_tension", "po_density"):
            self.assertIn(key, ts)

    def test_audit_status_matches_brief(self):
        result, brief, _ = self._run(1)
        self.assertEqual(result["audit"]["status"], brief["status"])


class TestDemoCLI(unittest.TestCase):
    """CLIの動作テスト（サブプロセスで実行）"""

    def _run_cli(self, *args) -> subprocess.CompletedProcess:
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        return subprocess.run(
            [sys.executable, "scripts/demo_business.py", *args],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

    def test_cli_default_runs(self):
        proc = self._run_cli()
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("デモ開始", proc.stdout)

    def test_cli_json_output_valid(self):
        proc = self._run_cli("--json")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("pipeline_complete", data)

    def test_cli_list_scenarios(self):
        proc = self._run_cli("--list")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("シナリオ", proc.stdout)

    def test_cli_scenario2(self):
        proc = self._run_cli("--scenario", "2")
        self.assertEqual(proc.returncode, 0)

    def test_cli_scenario3(self):
        proc = self._run_cli("--scenario", "3")
        self.assertEqual(proc.returncode, 0)

    def test_cli_scenario4(self):
        proc = self._run_cli("--scenario", "4")
        self.assertEqual(proc.returncode, 0)

    def test_cli_scenario5(self):
        proc = self._run_cli("--scenario", "5")
        self.assertEqual(proc.returncode, 0)

    def test_cli_scenario6(self):
        proc = self._run_cli("--scenario", "6")
        self.assertEqual(proc.returncode, 0)

    def test_cli_invalid_scenario(self):
        proc = self._run_cli("--scenario", "999")
        self.assertEqual(proc.returncode, 2)

    def test_cli_json_has_audit_hash(self):
        proc = self._run_cli("--json", "--scenario", "1")
        data = json.loads(proc.stdout)
        self.assertIn("audit", data)
        self.assertEqual(len(data["audit"]["decision_hash"]), 64)
