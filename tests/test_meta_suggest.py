import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.meta_suggest import build_suggestions


class TestMetaSuggestCore(unittest.TestCase):
    def test_build_suggestions_picks_unchecked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text("- [ ] A task\n- [x] done\n", encoding="utf-8")
            (root / "idea_note.md").write_text("- [ ] B task\n", encoding="utf-8")
            (root / "progress_log.md").write_text("- [ ] C task\n", encoding="utf-8")

            result = build_suggestions(root, top_k=2)

            self.assertEqual(result["summary"]["total_candidates"], 3)
            self.assertEqual(result["summary"]["returned"], 2)
            self.assertEqual(result["suggestions"][0]["proposal"], "A task")
            self.assertEqual(result["suggestions"][1]["proposal"], "B task")

    def test_build_suggestions_fallback_when_no_unchecked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("guideline.md", "idea_note.md", "progress_log.md"):
                (root / name).write_text("- [x] done\n", encoding="utf-8")

            result = build_suggestions(root, top_k=3)
            self.assertEqual(result["summary"]["total_candidates"], 0)
            self.assertEqual(result["suggestions"][0]["source"], "system")

    def test_invalid_top_k(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                build_suggestions(Path(td), top_k=0)


class TestMetaSuggestCLI(unittest.TestCase):
    def test_cli_runs(self):
        proc = subprocess.run(
            ["python", "scripts/meta_suggest.py", "2"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertIn("suggestions", data)

    def test_cli_invalid_args(self):
        proc = subprocess.run(
            ["python", "scripts/meta_suggest.py", "abc"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("top_k must be an integer", proc.stderr)


if __name__ == "__main__":
    unittest.main()
