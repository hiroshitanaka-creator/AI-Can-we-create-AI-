from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from check_consistency import check_consistency


class TestConsistency(unittest.TestCase):
    _SCRIPT = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "check_consistency.py"
    )

    def test_check_consistency_ok(self):
        req = {
            "situation": "障害時の対応方針を決めたい",
            "constraints": ["安全", "品質"],
            "options": ["案A", "案B", "案C"],
        }
        ok, digest, diff_keys = check_consistency(req, repeat=20)
        self.assertTrue(ok)
        self.assertEqual([], diff_keys)
        self.assertTrue(len(digest) == 64)

    def test_repeat_validation(self):
        req = {"situation": "方針決定"}
        with self.assertRaises(ValueError):
            check_consistency(req, repeat=0)

    def test_cli_ok_with_stdin(self):
        req = {
            "situation": "運用改善方針を決めたい",
            "constraints": ["安全"],
        }
        p = subprocess.run(
            [sys.executable, self._SCRIPT, "--repeat", "10"],
            input=json.dumps(req, ensure_ascii=False),
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, p.returncode, msg=p.stderr)
        self.assertIn("CONSISTENT:", p.stdout)

    def test_cli_invalid_json(self):
        p = subprocess.run(
            [sys.executable, self._SCRIPT],
            input="{invalid",
            text=True,
            capture_output=True,
        )
        self.assertEqual(2, p.returncode)


if __name__ == "__main__":
    unittest.main()
