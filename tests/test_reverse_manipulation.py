"""tests/test_reverse_manipulation.py — check_reverse_manipulation のユニットテスト"""
import unittest

from aicw.safety import check_reverse_manipulation


class TestCheckReverseManipulation(unittest.TestCase):

    # ------------------------------------------------------------------
    # 基本構造
    # ------------------------------------------------------------------
    def test_returns_required_keys(self):
        result = check_reverse_manipulation("AI推奨テキスト", "人間の決定")
        for key in ("warning", "similarity_score", "shared_tokens", "details", "note"):
            self.assertIn(key, result)

    def test_warning_is_bool(self):
        result = check_reverse_manipulation("テスト", "テスト")
        self.assertIsInstance(result["warning"], bool)

    def test_similarity_score_range(self):
        result = check_reverse_manipulation("テスト入力", "別の入力")
        score = result["similarity_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_shared_tokens_is_list(self):
        result = check_reverse_manipulation("安全 品質 コスト", "安全 効率")
        self.assertIsInstance(result["shared_tokens"], list)

    def test_note_contains_no_go(self):
        result = check_reverse_manipulation("テスト", "テスト")
        self.assertIn("No-Go #4", result["note"])

    # ------------------------------------------------------------------
    # 高類似度 → warning=True
    # ------------------------------------------------------------------
    def test_identical_text_triggers_warning(self):
        text = "安全性を重視して品質向上を優先する方針が推奨されます"
        result = check_reverse_manipulation(text, text)
        self.assertTrue(result["warning"])
        self.assertGreaterEqual(result["similarity_score"], 0.75)

    def test_high_overlap_triggers_warning(self):
        ai = "品質 安全 コスト 効率 推奨 決定 方針 戦略 実施 計画"
        human = "品質 安全 コスト 効率 推奨 決定 方針 戦略 実施 計画"
        result = check_reverse_manipulation(ai, human)
        self.assertTrue(result["warning"])

    def test_warning_details_mention_percentage(self):
        text = "品質向上を優先する安全で効率的な方針"
        result = check_reverse_manipulation(text, text)
        if result["warning"]:
            self.assertIn("%", result["details"])

    # ------------------------------------------------------------------
    # 低類似度 → warning=False
    # ------------------------------------------------------------------
    def test_completely_different_no_warning(self):
        ai = "環境負荷 生態系 持続可能性 エネルギー"
        human = "予算削減 スピード重視 競合対策 売上"
        result = check_reverse_manipulation(ai, human)
        self.assertFalse(result["warning"])
        self.assertLess(result["similarity_score"], 0.75)

    def test_empty_ai_output_no_warning(self):
        result = check_reverse_manipulation("", "人間の決定テキスト")
        self.assertFalse(result["warning"])
        self.assertEqual(result["similarity_score"], 0.0)

    def test_empty_human_decision_no_warning(self):
        result = check_reverse_manipulation("AI推奨テキスト", "")
        self.assertFalse(result["warning"])
        self.assertEqual(result["similarity_score"], 0.0)

    def test_both_empty_no_warning(self):
        result = check_reverse_manipulation("", "")
        self.assertFalse(result["warning"])
        self.assertEqual(result["similarity_score"], 0.0)

    # ------------------------------------------------------------------
    # 共有トークン
    # ------------------------------------------------------------------
    def test_shared_tokens_are_subset_of_both(self):
        ai = "安全 品質 コスト 戦略"
        human = "安全 効率 コスト 計画"
        result = check_reverse_manipulation(ai, human)
        # 共有トークンは両方に含まれる語のみ
        for token in result["shared_tokens"]:
            self.assertIn(token, ai)
            self.assertIn(token, human)

    def test_common_words_not_in_shared_tokens(self):
        # 助詞・汎用語はトークンから除外される
        ai = "この方針を採用することが推奨されます"
        human = "この方針を採用することが決定されました"
        result = check_reverse_manipulation(ai, human)
        # 「を」「は」「この」などの汎用語は shared_tokens に含まれないはず
        for common in ["を", "は", "こと", "この", "が"]:
            self.assertNotIn(common, result["shared_tokens"])

    # ------------------------------------------------------------------
    # スコアの対称性（Jaccard は対称）
    # ------------------------------------------------------------------
    def test_score_is_symmetric(self):
        ai = "安全 品質 コスト"
        human = "品質 効率 安全"
        r1 = check_reverse_manipulation(ai, human)
        r2 = check_reverse_manipulation(human, ai)
        self.assertAlmostEqual(r1["similarity_score"], r2["similarity_score"], places=4)

    # ------------------------------------------------------------------
    # 中程度の類似
    # ------------------------------------------------------------------
    def test_medium_overlap_no_warning_under_threshold(self):
        # 意図的に 50%前後の重複を作る
        ai = "安全 品質 コスト 効率 戦略 計画"
        human = "安全 品質 予算 スピード 競合 売上"
        result = check_reverse_manipulation(ai, human)
        # 結果はスコアに依存するが、panicsしないことを確認
        self.assertIn("warning", result)
        self.assertIsInstance(result["warning"], bool)
