from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from postmortem_template import build_postmortem_template


class TestPostmortemTemplate(unittest.TestCase):
    _SCRIPT = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "postmortem_template.py"
    )

    def test_ok_template_contains_30_60_90_sections(self):
        brief = {
            "status": "ok",
            "selection": {
                "recommended_id": "A",
                "explanation": "安全重視のため A を選択",
            },
            "next_questions": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
        }
        out = build_postmortem_template(brief)
        self.assertIn("## 30-day checks", out)
        self.assertIn("## 60-day checks", out)
        self.assertIn("## 90-day checks", out)
        self.assertIn("recommended_id: A", out)

    def test_blocked_template_contains_follow_up(self):
        brief = {
            "status": "blocked",
            "blocked_by": "#5 Existence Ethics",
            "reason": "私益的破壊の表現を検知",
        }
        out = build_postmortem_template(brief)
        self.assertIn("## BLOCKED Case", out)
        self.assertIn("Follow-up Checklist", out)
        self.assertIn("#5 Existence Ethics", out)

    def test_cli_from_stdin(self):
        brief = {
            "status": "ok",
            "selection": {"recommended_id": "B", "explanation": "バランス"},
            "next_questions": [],
        }
        p = subprocess.run(
            [sys.executable, self._SCRIPT],
            input=json.dumps(brief, ensure_ascii=False),
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, p.returncode, msg=p.stderr)
        self.assertIn("# Postmortem Template", p.stdout)

    def test_cli_from_file(self):
        brief = {
            "status": "ok",
            "selection": {"recommended_id": "C", "explanation": "速度重視"},
            "next_questions": ["Q1"],
        }
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
            self.assertIn("recommended_id: C", p.stdout)

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
