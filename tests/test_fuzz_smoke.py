from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from gen_fuzz_cases import generate_cases

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aicw.schema import validate_request


class TestFuzzGeneration(unittest.TestCase):
    _SCRIPT = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "gen_fuzz_cases.py"
    )

    def test_generate_cases_count_and_required_field(self):
        cases = generate_cases(count=30, seed=7)
        self.assertEqual(30, len(cases))
        for case in cases:
            self.assertIn("situation", case)
            self.assertIsInstance(case["situation"], str)
            self.assertTrue(case["situation"].strip())

    def test_generate_cases_are_schema_valid(self):
        cases = generate_cases(count=50, seed=21)
        errors = []
        for i, case in enumerate(cases):
            e = validate_request(case)
            if e:
                errors.append((i, e))
        self.assertEqual([], errors, msg=f"schema errors found: {errors[:3]}")

    def test_seed_is_deterministic(self):
        a = generate_cases(count=10, seed=123)
        b = generate_cases(count=10, seed=123)
        self.assertEqual(a, b)

    def test_cli_writes_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "cases.json")
            p = subprocess.run(
                [
                    sys.executable,
                    self._SCRIPT,
                    "--count",
                    "12",
                    "--seed",
                    "9",
                    "--out",
                    out,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, p.returncode, msg=p.stderr)
            with open(out, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(12, len(data))

    def test_cli_count_validation(self):
        p = subprocess.run(
            [sys.executable, self._SCRIPT, "--count", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, p.returncode)


if __name__ == "__main__":
    unittest.main()
