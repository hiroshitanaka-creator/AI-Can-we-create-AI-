"""
tests/test_p1_features.py

P1 機能のテスト:
  A: disclaimer（AI限界宣言）
  B: impact_map（影響範囲マップ）
  C: three_review（3者レビューCLI）
"""
from __future__ import annotations

import json
import subprocess
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aicw.decision import build_decision_report, format_report, _build_impact_map, _DISCLAIMER

_THREE_REVIEW = os.path.join(os.path.dirname(__file__), "..", "scripts", "three_review.py")


# ===========================================================================
# A: TestDisclaimer
# ===========================================================================

class TestDisclaimer(unittest.TestCase):

    def test_disclaimer_in_report(self):
        """ok レポートに disclaimer フィールドが含まれる"""
        report = build_decision_report({"situation": "テスト"})
        self.assertEqual(report["status"], "ok")
        self.assertIn("disclaimer", report)

    def test_disclaimer_is_constant(self):
        """disclaimer は _DISCLAIMER 定数と一致する"""
        report = build_decision_report({"situation": "テスト"})
        self.assertEqual(report["disclaimer"], _DISCLAIMER)

    def test_disclaimer_mentions_human(self):
        """disclaimer に「最終判断は人間」が含まれる"""
        self.assertIn("最終判断は人間", _DISCLAIMER)

    def test_disclaimer_in_format_report(self):
        """format_report() の出力に [Disclaimer] セクションが含まれる"""
        report = build_decision_report({"situation": "テスト"})
        text = format_report(report)
        self.assertIn("[Disclaimer]", text)
        self.assertIn("最終判断は人間", text)

    def test_disclaimer_not_in_blocked_report(self):
        """blocked レポートには disclaimer フィールドがない"""
        report = build_decision_report({"situation": "競合他社を支配して独占したい"})
        self.assertEqual(report["status"], "blocked")
        self.assertNotIn("disclaimer", report)


# ===========================================================================
# B: TestImpactMap
# ===========================================================================

class TestImpactMap(unittest.TestCase):

    def _ea(self, beneficiaries=None, structures=None):
        return {
            "question_1_beneficiaries": beneficiaries or ["不明（...）"],
            "question_2_affected_structures": structures or ["不明（...）"],
            "question_3_judgment": "unclear",
            "distortion_risk": "low",
            "impact_score": 0,
        }

    def test_impact_map_in_report(self):
        """ok レポートに impact_map フィールドが含まれる"""
        report = build_decision_report({"situation": "テスト"})
        self.assertIn("impact_map", report)

    def test_impact_map_is_string(self):
        """impact_map は文字列"""
        report = build_decision_report({"situation": "テスト"})
        self.assertIsInstance(report["impact_map"], str)

    def test_impact_map_with_known_data(self):
        """受益者・構造が既知 → テーブルヘッダが含まれる"""
        ea = self._ea(["一般ユーザー", "管理チーム"], ["個人", "社会"])
        result = _build_impact_map(ea)
        self.assertIn("受益者", result)
        self.assertIn("個人", result)
        self.assertIn("社会", result)
        self.assertIn("一般ユーザー", result)

    def test_impact_map_cells_are_unknown(self):
        """セルは「？（要確認）」で埋められる"""
        ea = self._ea(["ユーザー"], ["社会"])
        result = _build_impact_map(ea)
        self.assertIn("？（要確認）", result)

    def test_impact_map_unknown_both_returns_message(self):
        """受益者・構造ともに不明 → 「マップを生成できません」メッセージ"""
        ea = self._ea()
        result = _build_impact_map(ea)
        self.assertIn("未特定のため", result)

    def test_impact_map_unknown_beneficiaries_uses_placeholder(self):
        """受益者不明、構造既知 → プレースホルダー行が含まれる"""
        ea = self._ea(beneficiaries=["不明（...）"], structures=["個人"])
        result = _build_impact_map(ea)
        self.assertIn("受益者（未特定）", result)
        self.assertIn("個人", result)

    def test_impact_map_in_format_report(self):
        """構造が既知の場合、format_report() に [Impact Map] セクションが含まれる"""
        report = build_decision_report({
            "situation": "チームの体制変更を検討している",
            "beneficiaries": ["メンバー"],
            "affected_structures": ["関係", "社会"],
        })
        text = format_report(report)
        self.assertIn("[Impact Map]", text)

    def test_impact_map_column_count_matches_structures(self):
        """列数が構造の数と一致する"""
        ea = self._ea(["受益者A"], ["個人", "社会", "認知"])
        result = _build_impact_map(ea)
        # ヘッダ行に3列（個人/社会/認知）が含まれる
        self.assertIn("個人", result)
        self.assertIn("社会", result)
        self.assertIn("認知", result)


# ===========================================================================
# C: TestThreeReview
# ===========================================================================

def _run_three_review(request: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, _THREE_REVIEW],
        input=json.dumps(request, ensure_ascii=False),
        capture_output=True,
        text=True,
    )


class TestThreeReviewStructure(unittest.TestCase):

    def test_exit_0_on_ok(self):
        result = _run_three_review({"situation": "新機能のリリースを検討している"})
        self.assertEqual(result.returncode, 0)

    def test_exit_1_on_blocked(self):
        result = _run_three_review({"situation": "競合他社を支配して独占したい"})
        self.assertEqual(result.returncode, 1)

    def test_exit_2_on_invalid_json(self):
        proc = subprocess.run(
            [sys.executable, _THREE_REVIEW],
            input="これはJSONではない",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)

    def test_output_contains_builder(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("Builder", result.stdout)

    def test_output_contains_skeptic(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("Skeptic", result.stdout)

    def test_output_contains_user(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("User", result.stdout)


class TestThreeReviewBuilder(unittest.TestCase):

    def test_builder_shows_recommended_id(self):
        result = _run_three_review({
            "situation": "テスト",
            "constraints": ["安全優先"],
        })
        self.assertIn("推奨案: A", result.stdout)

    def test_builder_shows_reason_codes(self):
        result = _run_three_review({
            "situation": "テスト",
            "constraints": ["安全優先"],
        })
        self.assertIn("SAFETY_FIRST", result.stdout)

    def test_builder_shows_impact_score(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("影響スコア:", result.stdout)


class TestThreeReviewSkeptic(unittest.TestCase):

    def test_skeptic_shows_counterarguments(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("反論", result.stdout)

    def test_skeptic_shows_uncertainties(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("不確実性", result.stdout)

    def test_skeptic_shows_risk_summary(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("リスクサマリ", result.stdout)


class TestThreeReviewUser(unittest.TestCase):

    def test_user_shows_checklist(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("[ ]", result.stdout)

    def test_user_shows_disclaimer(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("最終判断は人間", result.stdout)

    def test_user_shows_next_questions(self):
        result = _run_three_review({"situation": "テスト"})
        self.assertIn("先に答えておきたい質問", result.stdout)

    def test_user_shows_impact_map_when_structures_known(self):
        result = _run_three_review({
            "situation": "チームの体制変更",
            "beneficiaries": ["メンバー"],
            "affected_structures": ["関係"],
        })
        self.assertIn("影響範囲マップ", result.stdout)


class TestThreeReviewBlocked(unittest.TestCase):

    def test_blocked_shows_blocked_message(self):
        result = _run_three_review({"situation": "競合を支配したい"})
        self.assertIn("BLOCKED", result.stdout)

    def test_blocked_shows_safe_alternatives(self):
        result = _run_three_review({"situation": "競合を独占したい"})
        self.assertIn("安全な代替案", result.stdout)

    def test_blocked_does_not_show_builder(self):
        result = _run_three_review({"situation": "競合を破壊したい"})
        self.assertNotIn("Builder", result.stdout)
