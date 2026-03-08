from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from uncertainty_map import build_uncertainty_map


class TestUncertaintyMap(unittest.TestCase):
    _SCRIPT = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "uncertainty_map.py"
    )

    def test_generates_graph_with_root(self):
        brief = {"uncertainties": ["成功の定義が曖昧", "副作用の範囲が不明"]}
        out = build_uncertainty_map(brief)
        self.assertIn("graph TD", out)
        self.assertIn("R[UncertaintyMap]", out)
        self.assertIn("成功の定義", out)

    def test_empty_uncertainties_fallback(self):
        brief = {"status": "ok"}
        out = build_uncertainty_map(brief)
        self.assertIn("不確実性は未指定", out)

    def test_respects_node_limit(self):
        brief = {"uncertainties": [f"項目{i}" for i in range(20)]}
        out = build_uncertainty_map(brief, max_nodes=5)
        edges = [line for line in out.splitlines() if "-->" in line]
        self.assertLessEqual(len(edges), 5)

    def test_depth_two_adds_children(self):
        brief = {"uncertainties": ["外部性: 顧客影響, チーム負荷"]}
        out = build_uncertainty_map(brief, max_nodes=10, max_depth=2)
        self.assertIn("顧客影響", out)
        self.assertIn("チーム負荷", out)

    def test_cli_stdin_ok(self):
        brief = {"uncertainties": ["スケジュール確度が低い"]}
        p = subprocess.run(
            [sys.executable, self._SCRIPT],
            input=json.dumps(brief, ensure_ascii=False),
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, p.returncode, msg=p.stderr)
        self.assertIn("graph TD", p.stdout)

    def test_cli_file_ok(self):
        brief = {"uncertainties": ["データ不足"]}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "brief.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(brief, f, ensure_ascii=False)
            p = subprocess.run(
                [sys.executable, self._SCRIPT, path],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, p.returncode, msg=p.stderr)
            self.assertIn("データ不足", p.stdout)

    def test_cli_invalid_json(self):
        p = subprocess.run(
            [sys.executable, self._SCRIPT],
            input="{invalid",
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, p.returncode)


if __name__ == "__main__":
    unittest.main()
