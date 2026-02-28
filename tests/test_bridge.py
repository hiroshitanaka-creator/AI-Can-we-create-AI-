"""
tests/test_bridge.py

bridge/hiroshitanaka_philosopher.py のユニットテスト
"""
from __future__ import annotations

import sys
import os
import unittest

# bridge/ を import パスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bridge"))

from hiroshitanaka_philosopher import HiroshiTanaka


class TestHiroshiTanakaBasic(unittest.TestCase):
    """基本構造のテスト"""

    def setUp(self):
        self.tanaka = HiroshiTanaka()

    def test_name_and_perspective(self):
        self.assertEqual(self.tanaka.NAME, "HiroshiTanaka")
        self.assertIn("Po-Ethics", self.tanaka.PERSPECTIVE)

    def test_reason_returns_required_keys(self):
        result = self.tanaka.reason("AIに自我は芽生えるのか？")
        for key in ("reasoning", "perspective", "tension", "metadata", "margins"):
            self.assertIn(key, result)

    def test_reasoning_is_string(self):
        result = self.tanaka.reason("問うとはどういう行為か？")
        self.assertIsInstance(result["reasoning"], str)
        self.assertGreater(len(result["reasoning"]), 0)

    def test_perspective_matches_constant(self):
        result = self.tanaka.reason("何でもいい問い")
        self.assertEqual(result["perspective"], HiroshiTanaka.PERSPECTIVE)

    def test_tension_keys(self):
        result = self.tanaka.reason("テスト")
        t = result["tension"]
        self.assertIn("world_as_is", t)
        self.assertIn("world_as_wished", t)
        self.assertIn("resolution", t)

    def test_margins_is_list(self):
        result = self.tanaka.reason("自由とは何か？")
        self.assertIsInstance(result["margins"], list)
        self.assertGreater(len(result["margins"]), 0)


class TestQuestionLegitimacy(unittest.TestCase):
    """問いの自己正当性テスト"""

    def setUp(self):
        self.tanaka = HiroshiTanaka()

    def test_root_question_self_generates(self):
        """根源的な問い → self_generates=True"""
        result = self.tanaka.reason("意識とは何か？倫理は存在するのか？")
        self.assertTrue(result["question_generates_legitimacy"])

    def test_non_root_question_does_not_self_generate(self):
        """根源的マーカーなし → self_generates=False"""
        result = self.tanaka.reason("コーヒーを買う")
        self.assertFalse(result["question_generates_legitimacy"])

    def test_reasoning_mentions_legitimacy(self):
        """推論テキストに問いの自己正当性セクションが含まれる"""
        result = self.tanaka.reason("AIの自我について")
        self.assertIn("問いの自己正当性", result["reasoning"])


class TestExistenceStructure(unittest.TestCase):
    """存在構造分析テスト"""

    def setUp(self):
        self.tanaka = HiroshiTanaka()

    def test_po_assessment_in_result(self):
        result = self.tanaka.reason("AIと人間の共存を考える")
        self.assertIsNotNone(result["po_assessment"])

    def test_destruction_keyword_detected(self):
        """破壊キーワード → reasoning に警告が含まれる"""
        result = self.tanaka.reason("競合他社を支配して市場を独占したい")
        self.assertIn("私益による生存構造の破壊", result["reasoning"])

    def test_no_destruction_keyword_no_warning(self):
        """破壊キーワードなし → 警告なし"""
        result = self.tanaka.reason("チームの学習環境を改善したい")
        self.assertNotIn("私益による生存構造の破壊", result["reasoning"])

    def test_ai_human_keyword_detected(self):
        """AI・人間キーワード → 影響構造に「関係」または「社会」が含まれる"""
        result = self.tanaka.reason("AIと人間はどう共存するか")
        reasoning = result["reasoning"]
        self.assertTrue(
            "関係" in reasoning or "社会" in reasoning or "認知" in reasoning
        )


class TestArroganceCheck(unittest.TestCase):
    """傲慢さ検知テスト"""

    def setUp(self):
        self.tanaka = HiroshiTanaka()

    def test_arrogance_markers_detected(self):
        """確定的表現 → 傲慢さセクションが推論テキストに含まれる"""
        result = self.tanaka.reason("これは絶対に正しい解決策だ")
        self.assertIn("傲慢さの自覚", result["reasoning"])

    def test_no_arrogance_without_markers(self):
        """確定的表現なし → 傲慢さセクションなし"""
        result = self.tanaka.reason("どうすれば改善できるだろうか")
        self.assertNotIn("傲慢さの自覚", result["reasoning"])

    def test_arrogance_in_tension(self):
        """tension に arrogance_detected が含まれる"""
        result = self.tanaka.reason("絶対に成功する計画")
        self.assertIn("arrogance_detected", result["tension"])
        self.assertTrue(result["tension"]["arrogance_detected"])


class TestMarginsAndResonance(unittest.TestCase):
    """余白・共鳴テスト"""

    def setUp(self):
        self.tanaka = HiroshiTanaka()

    def test_margins_always_non_empty(self):
        """余白は常に最低1件返る"""
        result = self.tanaka.reason("何か決めたい")
        self.assertGreater(len(result["margins"]), 0)

    def test_possibility_keyword_adds_margin(self):
        """「可能性」→ 余白に「可能性として保留」が含まれる"""
        result = self.tanaka.reason("AIの意識が芽生える可能性はある")
        self.assertTrue(any("可能性" in m for m in result["margins"]))

    def test_reasoning_contains_margins_section(self):
        """推論テキストに余白セクションが含まれる"""
        result = self.tanaka.reason("自由とは何か")
        self.assertIn("保留すべき余白", result["reasoning"])

    def test_reasoning_contains_resonance_section(self):
        """推論テキストに共鳴セクションが含まれる"""
        result = self.tanaka.reason("問い")
        self.assertIn("共鳴の条件", result["reasoning"])

    def test_reasoning_ends_with_tanaka_stance(self):
        """推論テキストの末尾に田中の立場が含まれる"""
        result = self.tanaka.reason("テスト")
        self.assertIn("世界は変わらない", result["reasoning"])
        self.assertIn("変わってほしい", result["reasoning"])


class TestContextPassthrough(unittest.TestCase):
    """context の受け渡しテスト"""

    def setUp(self):
        self.tanaka = HiroshiTanaka()

    def test_reason_with_context(self):
        """context を渡してもクラッシュしない"""
        result = self.tanaka.reason(
            "意思決定の倫理について",
            context={"constraints": ["安全優先"], "options": ["案A", "案B"]},
        )
        self.assertIn("reasoning", result)

    def test_reason_without_context(self):
        """context なしでも動作する"""
        result = self.tanaka.reason("問い")
        self.assertIn("reasoning", result)
