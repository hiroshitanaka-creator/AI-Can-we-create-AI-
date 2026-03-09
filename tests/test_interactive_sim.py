"""tests/test_interactive_sim.py — interactive_sim のユニット / スモークテスト"""
import io
import json
import os
import subprocess
import sys
import unittest


class TestCollectRequest(unittest.TestCase):
    """collect_request の入力収集ロジック（stdin 差し替えでテスト）"""

    def _make_stdin(self, lines: list) -> io.StringIO:
        return io.StringIO("\n".join(lines) + "\n")

    def _import(self):
        from scripts.interactive_sim import collect_request
        return collect_request

    def test_auto_returns_defaults(self):
        collect_request = self._import()
        req = collect_request(auto=True)
        self.assertIn("situation", req)
        self.assertIsInstance(req["constraints"], list)
        self.assertIsInstance(req["options"], list)

    def test_auto_options_max_three(self):
        collect_request = self._import()
        req = collect_request(auto=True)
        self.assertLessEqual(len(req["options"]), 3)

    def test_stdin_situation(self):
        collect_request = self._import()
        # situation=カスタム入力、残りは空行（デフォルトにフォールバック）
        stdin = self._make_stdin(
            ["カスタムシチュエーション", "", "", "", "", ""]
        )
        req = collect_request(auto=False, stdin=stdin)
        self.assertEqual(req["situation"], "カスタムシチュエーション")

    def test_stdin_empty_uses_default_situation(self):
        collect_request = self._import()
        stdin = self._make_stdin(["", "", "", "", ""])  # 全て空行
        req = collect_request(auto=False, stdin=stdin)
        # 空文字列はデフォルトにフォールバック
        self.assertTrue(req["situation"])

    def test_stdin_constraints(self):
        collect_request = self._import()
        stdin = self._make_stdin(
            ["シチュエーション", "制約A", "制約B", "", "", "", "", ""]
        )
        req = collect_request(auto=False, stdin=stdin)
        self.assertIn("制約A", req["constraints"])
        self.assertIn("制約B", req["constraints"])

    def test_options_truncated_to_three(self):
        collect_request = self._import()
        stdin = self._make_stdin(
            ["状況", "",                             # situation, constraints
             "案A", "案B", "案C", "案D", "",        # options (4件 → 3件)
             "", ""]                                 # beneficiaries, structures
        )
        req = collect_request(auto=False, stdin=stdin)
        self.assertLessEqual(len(req["options"]), 3)


class TestRunSimulation(unittest.TestCase):
    def test_auto_mode_returns_dict(self):
        from scripts.interactive_sim import run_simulation
        result = run_simulation(auto=True, json_mode=True)
        self.assertIn("brief_status", result)
        self.assertIn("audit_hash", result)
        self.assertIn("philosophy_summary", result)

    def test_audit_hash_is_sha256(self):
        from scripts.interactive_sim import run_simulation
        result = run_simulation(auto=True, json_mode=True)
        self.assertEqual(len(result["audit_hash"]), 64)

    def test_brief_status_valid(self):
        from scripts.interactive_sim import run_simulation
        result = run_simulation(auto=True, json_mode=True)
        self.assertIn(result["brief_status"], ("ok", "blocked"))

    def test_philosophy_summary_structure(self):
        from scripts.interactive_sim import run_simulation
        result = run_simulation(auto=True, json_mode=True)
        ps = result["philosophy_summary"]
        for key in ("highest_risk", "has_ethical_conflict", "ai_rights_tension"):
            self.assertIn(key, ps)

    def test_knowledge_recorded_true(self):
        from scripts.interactive_sim import run_simulation
        result = run_simulation(auto=True, json_mode=True, record_to_kb=True)
        self.assertTrue(result["knowledge_recorded"])

    def test_knowledge_recorded_false(self):
        from scripts.interactive_sim import run_simulation
        result = run_simulation(auto=True, json_mode=True, record_to_kb=False)
        self.assertFalse(result["knowledge_recorded"])


class TestInteractiveSimCLI(unittest.TestCase):
    """CLI の動作テスト（サブプロセスで実行）"""

    def _run(self, *args) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        return subprocess.run(
            [sys.executable, "scripts/interactive_sim.py", *args],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

    def test_auto_mode_exits_zero(self):
        proc = self._run("--auto")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

    def test_auto_mode_outputs_brief(self):
        proc = self._run("--auto")
        self.assertIn("意思決定ブリーフ", proc.stdout)

    def test_auto_mode_outputs_disclaimer(self):
        proc = self._run("--auto")
        self.assertIn("Disclaimer", proc.stdout)

    def test_json_mode_valid_json(self):
        proc = self._run("--auto", "--json")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("brief_status", data)

    def test_no_kb_flag(self):
        proc = self._run("--auto", "--no-kb")
        self.assertEqual(proc.returncode, 0)

    def test_audit_hash_in_output(self):
        proc = self._run("--auto")
        self.assertIn("ハッシュ", proc.stdout)
