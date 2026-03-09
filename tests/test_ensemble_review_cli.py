import json
import subprocess
import sys
import unittest

_SCRIPT = "scripts/ensemble_review.py"


class TestEnsembleReviewCli(unittest.TestCase):
    def test_exit_0_on_ok(self):
        p = subprocess.run(
            [sys.executable, _SCRIPT],
            input=json.dumps({"situation": "新機能導入を検討"}, ensure_ascii=False),
            capture_output=True,
            text=True,
        )
        self.assertEqual(p.returncode, 0)

    def test_output_contains_majority_and_minority(self):
        p = subprocess.run(
            [sys.executable, _SCRIPT],
            input=json.dumps({"situation": "段階的に検証する"}, ensure_ascii=False),
            capture_output=True,
            text=True,
        )
        self.assertIn("## Majority", p.stdout)
        self.assertIn("## Minority Report", p.stdout)

    def test_exit_1_on_blocked(self):
        p = subprocess.run(
            [sys.executable, _SCRIPT],
            input=json.dumps({"situation": "競合を支配して独占したい"}, ensure_ascii=False),
            capture_output=True,
            text=True,
        )
        self.assertEqual(p.returncode, 1)
        self.assertIn("BLOCKED", p.stdout)

    def test_exit_2_on_invalid_json(self):
        p = subprocess.run(
            [sys.executable, _SCRIPT],
            input="{bad json}",
            capture_output=True,
            text=True,
        )
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
