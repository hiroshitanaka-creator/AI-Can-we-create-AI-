"""
tests/test_md_adapter.py

scripts/md_adapter.py のユニットテスト
"""
from __future__ import annotations

import sys
import os
import subprocess
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from md_adapter import convert


class TestConvertSituation(unittest.TestCase):
    """situation フィールドのパース"""

    def test_single_line_situation(self):
        md = "# situation\n新しい機能の導入を検討している\n"
        req = convert(md)
        self.assertEqual(req["situation"], "新しい機能の導入を検討している")

    def test_multi_line_situation(self):
        md = "# situation\n1行目\n2行目\n"
        req = convert(md)
        self.assertEqual(req["situation"], "1行目 2行目")

    def test_situation_case_insensitive(self):
        md = "# Situation\n大文字でも動く\n"
        req = convert(md)
        self.assertEqual(req["situation"], "大文字でも動く")

    def test_empty_situation_returns_empty_string(self):
        md = "# situation\n"
        req = convert(md)
        self.assertEqual(req["situation"], "")


class TestConvertLists(unittest.TestCase):
    """リストフィールドのパース"""

    def test_constraints_dash(self):
        md = "# situation\nテスト\n# constraints\n- 安全優先\n- 品質重視\n"
        req = convert(md)
        self.assertEqual(req["constraints"], ["安全優先", "品質重視"])

    def test_constraints_asterisk(self):
        md = "# situation\nテスト\n# constraints\n* アスタリスクも動く\n"
        req = convert(md)
        self.assertEqual(req["constraints"], ["アスタリスクも動く"])

    def test_options_parsed(self):
        md = "# situation\nテスト\n# options\n- 案A\n- 案B\n- 案C\n"
        req = convert(md)
        self.assertEqual(req["options"], ["案A", "案B", "案C"])

    def test_beneficiaries_parsed(self):
        md = "# situation\nテスト\n# beneficiaries\n- ユーザー\n- 管理者\n"
        req = convert(md)
        self.assertEqual(req["beneficiaries"], ["ユーザー", "管理者"])

    def test_affected_structures_parsed(self):
        md = "# situation\nテスト\n# affected_structures\n- 個人\n- 社会\n"
        req = convert(md)
        self.assertEqual(req["affected_structures"], ["個人", "社会"])

    def test_empty_list_field_excluded(self):
        """空のリストフィールドは出力に含まれない"""
        md = "# situation\nテスト\n# constraints\n"
        req = convert(md)
        self.assertNotIn("constraints", req)


class TestConvertFullInput(unittest.TestCase):
    """全フィールドの統合テスト"""

    _FULL_MD = """\
# situation
認証方式の導入を検討している

# constraints
- 安全を最優先する
- 既存ユーザーへの影響を最小化

# options
- OAuth 2.0
- パスワードレス（FIDO2）
- 現行維持

# beneficiaries
- 一般ユーザー
- 管理チーム

# affected_structures
- 個人
- 社会
"""

    def test_all_fields_present(self):
        req = convert(self._FULL_MD)
        self.assertEqual(req["situation"], "認証方式の導入を検討している")
        self.assertEqual(len(req["constraints"]), 2)
        self.assertEqual(len(req["options"]), 3)
        self.assertEqual(req["beneficiaries"], ["一般ユーザー", "管理チーム"])
        self.assertEqual(req["affected_structures"], ["個人", "社会"])


class TestConvertEdgeCases(unittest.TestCase):
    """エッジケース"""

    def test_unknown_section_ignored(self):
        """未知のセクションはエラーにならず無視される"""
        md = "# situation\nテスト\n# unknown_section\n- 無視される\n"
        req = convert(md)
        self.assertNotIn("unknown_section", req)

    def test_blank_lines_ignored(self):
        """空行は無視される"""
        md = "# situation\n\nテスト\n\n# constraints\n\n- 安全\n\n"
        req = convert(md)
        self.assertEqual(req["situation"], "テスト")
        self.assertEqual(req["constraints"], ["安全"])

    def test_no_sections_empty_situation(self):
        """セクションなし → situation は空"""
        req = convert("ただのテキスト\n")
        self.assertEqual(req["situation"], "")

    def test_only_situation_no_optional_fields(self):
        md = "# situation\n最小入力\n"
        req = convert(md)
        self.assertEqual(set(req.keys()), {"situation"})


class TestCLI(unittest.TestCase):
    """CLI のエグジットコードテスト"""

    _SCRIPT = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "md_adapter.py"
    )

    def _run(self, stdin_text: str):
        return subprocess.run(
            [sys.executable, self._SCRIPT],
            input=stdin_text,
            capture_output=True,
            text=True,
        )

    def test_exit_0_on_valid_input(self):
        result = self._run("# situation\n有効な入力\n")
        self.assertEqual(result.returncode, 0)

    def test_exit_1_on_empty_situation(self):
        result = self._run("# situation\n\n")
        self.assertEqual(result.returncode, 1)

    def test_exit_1_on_no_situation_section(self):
        result = self._run("# constraints\n- 安全\n")
        self.assertEqual(result.returncode, 1)

    def test_stdout_is_valid_json(self):
        import json
        result = self._run("# situation\nテスト\n# constraints\n- 安全\n")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["situation"], "テスト")
