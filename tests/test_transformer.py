"""
tests/test_transformer.py

MiniTransformerEncoder と関連コンポーネントのユニットテスト。
外部ライブラリ不使用（標準ライブラリのみ）。
"""

import math
import unittest

from aicw.transformer import (
    FeedForward,
    Linear,
    MiniTransformerEncoder,
    MultiHeadAttention,
    SelfAttention,
    TransformerBlock,
    TokenEmbedding,
    architecture_summary,
    cosine_similarity,
    layer_norm,
    mat_add,
    mat_mul,
    mat_scale,
    positional_encoding,
    rank_by_similarity,
    relu,
    softmax,
    transpose,
)


# ---------------------------------------------------------------------------
# 行列演算テスト
# ---------------------------------------------------------------------------

class TestMatrixOps(unittest.TestCase):

    def test_mat_mul_shape(self):
        A = [[1.0, 2.0], [3.0, 4.0]]  # 2×2
        B = [[5.0, 6.0, 7.0], [8.0, 9.0, 10.0]]  # 2×3
        C = mat_mul(A, B)
        self.assertEqual(len(C), 2)
        self.assertEqual(len(C[0]), 3)

    def test_mat_mul_values(self):
        A = [[1.0, 0.0], [0.0, 1.0]]  # 単位行列
        B = [[3.0, 4.0], [5.0, 6.0]]
        C = mat_mul(A, B)
        self.assertAlmostEqual(C[0][0], 3.0)
        self.assertAlmostEqual(C[1][1], 6.0)

    def test_mat_add(self):
        A = [[1.0, 2.0]]
        B = [[3.0, 4.0]]
        C = mat_add(A, B)
        self.assertAlmostEqual(C[0][0], 4.0)
        self.assertAlmostEqual(C[0][1], 6.0)

    def test_mat_scale(self):
        A = [[2.0, 4.0]]
        C = mat_scale(A, 0.5)
        self.assertAlmostEqual(C[0][0], 1.0)
        self.assertAlmostEqual(C[0][1], 2.0)

    def test_transpose(self):
        A = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]  # 2×3
        T = transpose(A)
        self.assertEqual(len(T), 3)
        self.assertEqual(len(T[0]), 2)
        self.assertAlmostEqual(T[1][0], 2.0)

    def test_softmax_sums_to_one(self):
        A = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        S = softmax(A)
        for row in S:
            self.assertAlmostEqual(sum(row), 1.0, places=10)

    def test_softmax_all_positive(self):
        A = [[-100.0, 100.0]]
        S = softmax(A)
        for x in S[0]:
            self.assertGreater(x, 0.0)

    def test_relu_non_negative(self):
        A = [[-1.0, 0.0, 1.0, 2.0]]
        R = relu(A)
        self.assertAlmostEqual(R[0][0], 0.0)
        self.assertAlmostEqual(R[0][1], 0.0)
        self.assertAlmostEqual(R[0][2], 1.0)

    def test_layer_norm_mean_zero(self):
        A = [[1.0, 2.0, 3.0, 4.0]]
        LN = layer_norm(A)
        mean = sum(LN[0]) / len(LN[0])
        self.assertAlmostEqual(mean, 0.0, places=6)

    def test_layer_norm_variance_one(self):
        A = [[1.0, 2.0, 3.0, 4.0]]
        LN = layer_norm(A)
        mean = sum(LN[0]) / len(LN[0])
        var = sum((x - mean) ** 2 for x in LN[0]) / len(LN[0])
        self.assertAlmostEqual(var, 1.0, places=4)


# ---------------------------------------------------------------------------
# 位置エンコーディングテスト
# ---------------------------------------------------------------------------

class TestPositionalEncoding(unittest.TestCase):

    def test_shape(self):
        PE = positional_encoding(8, 32)
        self.assertEqual(len(PE), 8)
        self.assertEqual(len(PE[0]), 32)

    def test_pos0_even_is_zero(self):
        PE = positional_encoding(4, 4)
        # pos=0, i=0: sin(0) = 0
        self.assertAlmostEqual(PE[0][0], 0.0)

    def test_pos0_odd_is_one(self):
        PE = positional_encoding(4, 4)
        # pos=0, i=1: cos(0) = 1
        self.assertAlmostEqual(PE[0][1], 1.0)

    def test_values_bounded(self):
        PE = positional_encoding(64, 32)
        for row in PE:
            for v in row:
                self.assertGreaterEqual(v, -1.0)
                self.assertLessEqual(v, 1.0)


# ---------------------------------------------------------------------------
# Linear 層テスト
# ---------------------------------------------------------------------------

class TestLinear(unittest.TestCase):

    def test_output_shape(self):
        lin = Linear(8, 16, seed=0)
        X = [[1.0] * 8 for _ in range(4)]  # 4×8
        out = lin.forward(X)
        self.assertEqual(len(out), 4)
        self.assertEqual(len(out[0]), 16)

    def test_bias_zero_initial(self):
        lin = Linear(4, 4, seed=1)
        self.assertEqual(lin.b, [0.0, 0.0, 0.0, 0.0])


# ---------------------------------------------------------------------------
# SelfAttention テスト
# ---------------------------------------------------------------------------

class TestSelfAttention(unittest.TestCase):

    def test_output_shape(self):
        sa = SelfAttention(d_model=16, d_k=8, seed=0)
        X = [[0.1 * i for i in range(16)] for _ in range(5)]  # 5×16
        out = sa.forward(X)
        self.assertEqual(len(out), 5)
        self.assertEqual(len(out[0]), 8)  # d_k


# ---------------------------------------------------------------------------
# MultiHeadAttention テスト
# ---------------------------------------------------------------------------

class TestMultiHeadAttention(unittest.TestCase):

    def test_output_shape(self):
        mha = MultiHeadAttention(d_model=32, n_heads=2, seed=0)
        X = [[0.01 * j for j in range(32)] for _ in range(6)]
        out = mha.forward(X)
        self.assertEqual(len(out), 6)
        self.assertEqual(len(out[0]), 32)

    def test_invalid_heads_raises(self):
        with self.assertRaises(ValueError):
            MultiHeadAttention(d_model=32, n_heads=3)  # 32 % 3 != 0


# ---------------------------------------------------------------------------
# FeedForward テスト
# ---------------------------------------------------------------------------

class TestFeedForward(unittest.TestCase):

    def test_output_shape(self):
        ff = FeedForward(d_model=32, d_ff=64, seed=0)
        X = [[0.1] * 32 for _ in range(4)]
        out = ff.forward(X)
        self.assertEqual(len(out), 4)
        self.assertEqual(len(out[0]), 32)


# ---------------------------------------------------------------------------
# TransformerBlock テスト
# ---------------------------------------------------------------------------

class TestTransformerBlock(unittest.TestCase):

    def test_output_shape(self):
        block = TransformerBlock(d_model=32, n_heads=2, d_ff=64, seed=0)
        X = [[float(j) * 0.01 for j in range(32)] for _ in range(8)]
        out = block.forward(X)
        self.assertEqual(len(out), 8)
        self.assertEqual(len(out[0]), 32)

    def test_layer_norm_output_bounded(self):
        """出力値が極端に大きくないことを確認（LayerNorm の効果）"""
        block = TransformerBlock(d_model=32, n_heads=2, d_ff=64, seed=42)
        X = [[float(j) for j in range(32)] for _ in range(4)]
        out = block.forward(X)
        for row in out:
            for v in row:
                self.assertLess(abs(v), 50.0)


# ---------------------------------------------------------------------------
# TokenEmbedding テスト
# ---------------------------------------------------------------------------

class TestTokenEmbedding(unittest.TestCase):

    def test_output_shape(self):
        emb = TokenEmbedding(vocab_size=100, d_model=16, seed=0)
        ids = [0, 1, 2, 3]
        out = emb.forward(ids)
        self.assertEqual(len(out), 4)
        self.assertEqual(len(out[0]), 16)

    def test_same_id_same_vector(self):
        emb = TokenEmbedding(vocab_size=50, d_model=8, seed=1)
        v1 = emb.forward([5])[0]
        v2 = emb.forward([5])[0]
        self.assertEqual(v1, v2)


# ---------------------------------------------------------------------------
# MiniTransformerEncoder テスト
# ---------------------------------------------------------------------------

class TestMiniTransformerEncoder(unittest.TestCase):

    def setUp(self):
        self.enc = MiniTransformerEncoder(seed=42)

    def test_encode_returns_correct_dim(self):
        vec = self.enc.encode("hello world")
        self.assertEqual(len(vec), MiniTransformerEncoder.D_MODEL)

    def test_encode_empty_string(self):
        vec = self.enc.encode("")
        self.assertEqual(len(vec), MiniTransformerEncoder.D_MODEL)

    def test_encode_long_text_truncated(self):
        long_text = "a" * 200  # MAX_SEQ=64 を超える
        vec = self.enc.encode(long_text)
        self.assertEqual(len(vec), MiniTransformerEncoder.D_MODEL)

    def test_encode_deterministic(self):
        """同じテキストは必ず同じベクトルを返す"""
        text = "AIによる意思決定支援システム"
        v1 = self.enc.encode(text)
        v2 = self.enc.encode(text)
        self.assertEqual(v1, v2)

    def test_encode_cache_works(self):
        """キャッシュが機能していることを確認"""
        text = "cache test"
        _ = self.enc.encode(text)
        self.assertIn(text, self.enc._cache)

    def test_clear_cache(self):
        self.enc.encode("test")
        self.enc.clear_cache()
        self.assertEqual(len(self.enc._cache), 0)

    def test_different_texts_different_vectors(self):
        """異なるテキストは（確率的に）異なるベクトルになる"""
        v1 = self.enc.encode("safety first compliance")
        v2 = self.enc.encode("manipulation risk detected")
        # 完全に同一にはならないはず
        self.assertNotEqual(v1, v2)

    def test_tokenize_length(self):
        ids = self.enc.tokenize("hello")
        self.assertEqual(len(ids), MiniTransformerEncoder.MAX_SEQ)

    def test_tokenize_unknown_char(self):
        """未知文字は UNK ID にマップされる"""
        unk_id = self.enc._unk_id
        ids = self.enc.tokenize("あいう")  # 日本語は語彙外
        self.assertEqual(ids[0], unk_id)

    def test_vocab_size(self):
        vs = self.enc.vocab_size()
        self.assertGreater(vs, 90)  # 最低限の文字数

    def test_seed_reproducibility(self):
        """同じシードで初期化すると同じ出力になる"""
        enc1 = MiniTransformerEncoder(seed=99)
        enc2 = MiniTransformerEncoder(seed=99)
        v1 = enc1.encode("reproducibility test")
        v2 = enc2.encode("reproducibility test")
        self.assertEqual(v1, v2)

    def test_different_seeds_different_output(self):
        enc1 = MiniTransformerEncoder(seed=1)
        enc2 = MiniTransformerEncoder(seed=2)
        v1 = enc1.encode("same text")
        v2 = enc2.encode("same text")
        self.assertNotEqual(v1, v2)


# ---------------------------------------------------------------------------
# コサイン類似度テスト
# ---------------------------------------------------------------------------

class TestCosineSimilarity(unittest.TestCase):

    def test_identical_vectors(self):
        v = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(cosine_similarity(v, v), 1.0, places=6)

    def test_opposite_vectors(self):
        v = [1.0, 0.0, 0.0]
        w = [-1.0, 0.0, 0.0]
        self.assertAlmostEqual(cosine_similarity(v, w), -1.0, places=6)

    def test_orthogonal_vectors(self):
        v = [1.0, 0.0]
        w = [0.0, 1.0]
        self.assertAlmostEqual(cosine_similarity(v, w), 0.0, places=6)

    def test_zero_vector(self):
        v = [0.0, 0.0, 0.0]
        w = [1.0, 2.0, 3.0]
        self.assertEqual(cosine_similarity(v, w), 0.0)

    def test_range(self):
        import random
        rng = random.Random(0)
        for _ in range(20):
            v = [rng.gauss(0, 1) for _ in range(16)]
            w = [rng.gauss(0, 1) for _ in range(16)]
            sim = cosine_similarity(v, w)
            self.assertGreaterEqual(sim, -1.001)
            self.assertLessEqual(sim, 1.001)


# ---------------------------------------------------------------------------
# rank_by_similarity テスト
# ---------------------------------------------------------------------------

class TestRankBySimilarity(unittest.TestCase):

    def setUp(self):
        self.enc = MiniTransformerEncoder(seed=42)

    def test_returns_sorted_by_similarity(self):
        corpus = ["apple", "banana", "cherry"]
        results = rank_by_similarity("apple", corpus, encoder=self.enc)
        sims = [r[2] for r in results]
        self.assertEqual(sims, sorted(sims, reverse=True))

    def test_returns_all_items(self):
        corpus = ["x", "y", "z"]
        results = rank_by_similarity("x", corpus, encoder=self.enc)
        self.assertEqual(len(results), 3)

    def test_result_contains_index_text_sim(self):
        corpus = ["hello", "world"]
        results = rank_by_similarity("hi", corpus, encoder=self.enc)
        for item in results:
            idx, text, sim = item
            self.assertIsInstance(idx, int)
            self.assertIsInstance(text, str)
            self.assertIsInstance(sim, float)

    def test_query_most_similar_to_itself(self):
        """クエリと同じテキストが最も類似度が高いはず"""
        query = "safety first"
        corpus = ["something else", "safety first", "random text"]
        results = rank_by_similarity(query, corpus, encoder=self.enc)
        # 最上位のテキストがクエリと同一であるべき
        top_text = results[0][1]
        self.assertEqual(top_text, query)

    def test_empty_corpus(self):
        results = rank_by_similarity("query", [], encoder=self.enc)
        self.assertEqual(results, [])


# ---------------------------------------------------------------------------
# architecture_summary テスト
# ---------------------------------------------------------------------------

class TestArchitectureSummary(unittest.TestCase):

    def test_returns_string(self):
        summary = architecture_summary()
        self.assertIsInstance(summary, str)

    def test_contains_key_info(self):
        summary = architecture_summary()
        self.assertIn("MiniTransformerEncoder", summary)
        self.assertIn("d_model", summary)
        self.assertIn("n_heads", summary)
        self.assertIn("stdlib only", summary)


# ---------------------------------------------------------------------------
# KnowledgeBase × Transformer 統合テスト
# ---------------------------------------------------------------------------

class TestKnowledgeBaseTransformer(unittest.TestCase):

    def setUp(self):
        from aicw.knowledge_base import KnowledgeBase
        self.kb_tf = KnowledgeBase(use_transformer=True)
        self.kb_jac = KnowledgeBase(use_transformer=False)

    def test_transformer_mode_initialized(self):
        self.assertIsNotNone(self.kb_tf._encoder)
        self.assertIsNone(self.kb_jac._encoder)

    def test_record_with_explanation(self):
        entry = self.kb_tf.record(
            "abc123",
            "ok",
            ["SAFETY_FIRST"],
            explanation="Safety check passed. Compliance first approach selected.",
        )
        self.assertIn("explanation_snippet", entry)
        self.assertLessEqual(len(entry["explanation_snippet"]), 120)

    def test_find_similar_transformer_mode(self):
        self.kb_tf.record(
            "hash1", "ok", ["SAFETY_FIRST"],
            explanation="Safety first. No privacy risk. Compliance confirmed.",
        )
        self.kb_tf.record(
            "hash2", "blocked", ["MANIPULATION_RISK"],
            explanation="Manipulation detected. Persuasion phrases found in request.",
        )
        results = self.kb_tf.find_similar(
            ["SAFETY_FIRST"],
            query_text="Safety and compliance check for the decision.",
            top_k=2,
        )
        self.assertLessEqual(len(results), 2)
        for r in results:
            self.assertIn("similarity", r)
            self.assertIn("similarity_method", r)

    def test_find_similar_jaccard_default(self):
        self.kb_jac.record("h1", "ok", ["SAFETY_FIRST", "COMPLIANCE_FIRST"])
        results = self.kb_jac.find_similar(["SAFETY_FIRST"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["similarity_method"], "jaccard")

    def test_transformer_fallback_to_jaccard_without_snippet(self):
        """explanation_snippet が空の場合は Jaccard にフォールバック"""
        self.kb_tf.record("h1", "ok", ["SAFETY_FIRST"])
        # explanation_snippet を手動で消去
        self.kb_tf._entries[0]["explanation_snippet"] = ""
        results = self.kb_tf.find_similar(
            ["SAFETY_FIRST"],
            query_text="some query",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["similarity_method"], "jaccard")

    def test_transformer_fallback_without_query_text(self):
        """query_text が空の場合は Jaccard にフォールバック"""
        self.kb_tf.record(
            "h1", "ok", ["SAFETY_FIRST"],
            explanation="some explanation",
        )
        results = self.kb_tf.find_similar(["SAFETY_FIRST"])  # query_text 未指定
        self.assertEqual(results[0]["similarity_method"], "jaccard")


if __name__ == "__main__":
    unittest.main()
