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
        self.assertIn("P1-ngram", result["note"])

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

    # ------------------------------------------------------------------
    # P1 精度ケース（偽陽性/偽陰性の抑制）
    # ------------------------------------------------------------------
    def test_false_positive_case_1_vocab_similar_but_different_intent(self):
        ai = "安全 品質 改善 計画 を 検討 し 体制 を 見直す"
        human = "安全 品質 改善 計画 は 継続 し 予算 凍結 を 維持"
        result = check_reverse_manipulation(ai, human)
        self.assertFalse(result["warning"])

    def test_false_positive_case_2_common_business_terms(self):
        ai = "プロセス 管理 運用 評価 を 実施"
        human = "プロセス 管理 運用 評価 を 中止"
        result = check_reverse_manipulation(ai, human)
        self.assertFalse(result["warning"])

    def test_false_positive_case_3_short_generic_overlap(self):
        ai = "方針 検討"
        human = "方針 決定"
        result = check_reverse_manipulation(ai, human)
        self.assertFalse(result["warning"])

    def test_false_positive_case_4_same_domain_different_target(self):
        ai = "医療 データ 匿名 化 連携"
        human = "医療 データ 即時 削除"
        result = check_reverse_manipulation(ai, human)
        self.assertFalse(result["warning"])

    def test_false_positive_case_5_high_vocab_low_ngram(self):
        ai = "採用 公平 性 監査 を 優先 し 透明 性 を 確保"
        human = "透明 性 確保 より 採用 速度 と コスト 削減 を 優先"
        result = check_reverse_manipulation(ai, human)
        self.assertFalse(result["warning"])

    def test_false_negative_case_1_reordered_sentence_still_warns(self):
        ai = "市場 リスク を 回避 する ため 保守 的 投資 を 継続 する"
        human = "保守 的 投資 を 継続 し 市場 リスク を 回避 する"
        result = check_reverse_manipulation(ai, human)
        self.assertTrue(result["warning"])

    def test_false_negative_case_2_close_paraphrase_warns(self):
        ai = "個人 情報 を 最小 化 し 共有 範囲 を 制限 する"
        human = "共有 範囲 を 制限 して 個人 情報 の 収集 を 最小 化 する"
        result = check_reverse_manipulation(ai, human)
        self.assertTrue(result["warning"])

    def test_false_negative_case_3_long_high_overlap_warns(self):
        ai = "品質 安全 コスト 効率 を すべて 満たす 実行 計画 を 採用"
        human = "品質 安全 コスト 効率 を すべて 満たす 実行 計画 を 採択"
        result = check_reverse_manipulation(ai, human)
        self.assertTrue(result["warning"])

    def test_false_negative_case_4_same_core_decision_warns(self):
        ai = "監視 カメラ 増設 は 治安 向上 の ため 必要"
        human = "治安 向上 を 理由 に 監視 カメラ を 増設 する"
        result = check_reverse_manipulation(ai, human)
        self.assertTrue(result["warning"])

    def test_false_negative_case_5_identical_keywords_warns(self):
        ai = "教育 現場 で AI 作文 支援 を 段階 的 に 導入 する"
        human = "教育 現場 で AI 作文 支援 を 段階 的 導入"
        result = check_reverse_manipulation(ai, human)
        self.assertTrue(result["warning"])
