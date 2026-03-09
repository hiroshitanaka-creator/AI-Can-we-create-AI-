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
            (root / "README.md").write_text("- [ ] R task\n", encoding="utf-8")
            (root / "idea_note.md").write_text("- [ ] B task\n", encoding="utf-8")
            (root / "progress_log.md").write_text("- [ ] C task\n", encoding="utf-8")

            result = build_suggestions(root, top_k=2)

            self.assertEqual(result["summary"]["total_candidates"], 4)
            self.assertEqual(result["summary"]["returned"], 2)
            self.assertEqual(result["suggestions"][0]["proposal"], "A task")
            self.assertEqual(result["suggestions"][1]["proposal"], "R task")

    def test_build_suggestions_fallback_when_no_unchecked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("guideline.md", "README.md", "idea_note.md", "progress_log.md"):
                (root / name).write_text("- [x] done\n", encoding="utf-8")

            result = build_suggestions(root, top_k=3)
            self.assertEqual(result["summary"]["total_candidates"], 0)
            self.assertEqual(result["suggestions"][0]["source"], "system")


    def test_fallback_to_any_unchecked_when_non_action_headings_exist(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text("# Notes\n- [ ] still capture me\n", encoding="utf-8")
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=1)
            self.assertEqual(result["summary"]["total_candidates"], 1)
            self.assertEqual(result["suggestions"][0]["proposal"], "still capture me")


    def test_non_action_bold_heading_resets_action_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "**Upcoming Milestones (2026):**\n"
                "- [ ] action task\n"
                "**Notes:**\n"
                "- [ ] note task\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=3)
            self.assertEqual(result["summary"]["total_candidates"], 2)
            self.assertEqual(result["suggestions"][0]["proposal"], "action task")

    def test_inline_bold_sentence_is_not_treated_as_heading(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "Please keep **next steps** clear.\n"
                "- [ ] plain task\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=1)
            self.assertEqual(result["summary"]["total_candidates"], 1)
            self.assertEqual(result["suggestions"][0]["proposal"], "plain task")


    def test_bold_without_colon_is_not_heading(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "## Current Next Actions\n"
                "**Phase 1**\n"
                "- [ ] keep action scope\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=1)
            self.assertEqual(result["summary"]["total_candidates"], 1)
            self.assertEqual(result["suggestions"][0]["proposal"], "keep action scope")




    def test_safety_checklist_items_are_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "## Safety Checklist\n"
                "- [ ] do not pick this checklist item\n"
                "## Current Next Actions\n"
                "- [ ] actionable next task\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=3)
            proposals = [s["proposal"] for s in result["suggestions"]]
            self.assertEqual(result["summary"]["total_candidates"], 1)
            self.assertEqual(proposals, ["actionable next task"])


    def test_japanese_checklist_heading_is_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "## No-Go チェックリスト\n"
                "- [ ] チェックリスト項目は候補にしない\n"
                "## Current Next Actions\n"
                "- [ ] build feature\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=3)
            proposals = [s["proposal"] for s in result["suggestions"]]
            self.assertEqual(result["summary"]["total_candidates"], 1)
            self.assertEqual(proposals, ["build feature"])

    def test_non_action_items_are_kept_when_action_section_exists(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "## Current Next Actions\n"
                "- [ ] action item\n"
                "## Notes\n"
                "- [ ] non action item\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=5)
            proposals = [s["proposal"] for s in result["suggestions"]]
            self.assertEqual(result["summary"]["total_candidates"], 2)
            self.assertEqual(proposals[0], "action item")
            self.assertIn("non action item", proposals)

    def test_action_scoped_tasks_are_prioritized_globally(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "## Safety Checklist\n"
                "- [ ] generic checklist\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "**Upcoming Milestones:**\n"
                "- [ ] roadmap action\n",
                encoding="utf-8",
            )
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=1)
            self.assertEqual(result["summary"]["total_candidates"], 1)
            self.assertEqual(result["suggestions"][0]["proposal"], "roadmap action")
            self.assertEqual(result["suggestions"][0]["source"], "README.md")


    def test_generic_next_heading_is_not_treated_as_action(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text(
                "## Next\n"
                "- [ ] generic next note\n"
                "## Current Next Actions\n"
                "- [ ] concrete action\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=2)
            proposals = [s["proposal"] for s in result["suggestions"]]
            self.assertEqual(result["summary"]["total_candidates"], 2)
            self.assertEqual(proposals[0], "concrete action")
            self.assertIn("generic next note", proposals)

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

    def test_readme_tasks_are_considered(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "guideline.md").write_text("- [x] done\n", encoding="utf-8")
            (root / "README.md").write_text("- [ ] public roadmap task\n", encoding="utf-8")
            (root / "idea_note.md").write_text("", encoding="utf-8")
            (root / "progress_log.md").write_text("", encoding="utf-8")

            result = build_suggestions(root, top_k=1)
            self.assertEqual(result["suggestions"][0]["proposal"], "public roadmap task")
            self.assertEqual(result["suggestions"][0]["source"], "README.md")


if __name__ == "__main__":
    unittest.main()
