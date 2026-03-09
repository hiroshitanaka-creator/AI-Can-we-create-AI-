"""
tests/test_transformer_trainer.py

TransformerTrainer と gen_training_data のユニットテスト。
外部ライブラリ不使用（標準ライブラリのみ）。
"""

import json
import os
import tempfile
import unittest

from aicw.transformer import MiniTransformerEncoder
from aicw.transformer_trainer import (
    TrainingPair,
    TransformerTrainer,
    load_pairs,
    quick_train,
    _mean_cosine,
    _mean_mse,
)


# ---------------------------------------------------------------------------
# テスト用ヘルパー
# ---------------------------------------------------------------------------

def _make_pairs(n: int = 6) -> list:
    """シンプルなテスト用学習ペアを生成する。"""
    return [
        TrainingPair(
            text_a="safety first compliance",
            text_b="safety risk avoidance",
            target_similarity=0.8,
            reason_codes_a=["SAFETY_FIRST", "COMPLIANCE_FIRST"],
            reason_codes_b=["SAFETY_FIRST", "RISK_AVOIDANCE"],
        ),
        TrainingPair(
            text_a="speed deadline urgent",
            text_b="fast execution priority",
            target_similarity=0.7,
            reason_codes_a=["SPEED_FIRST", "DEADLINE_DRIVEN"],
            reason_codes_b=["SPEED_FIRST", "URGENCY_FIRST"],
        ),
        TrainingPair(
            text_a="safety first compliance",
            text_b="speed deadline urgent",
            target_similarity=0.0,
            reason_codes_a=["SAFETY_FIRST"],
            reason_codes_b=["SPEED_FIRST"],
        ),
        TrainingPair(
            text_a="balance balanced approach",
            text_b="step by step moderation",
            target_similarity=0.5,
            reason_codes_a=["NO_CONSTRAINTS"],
            reason_codes_b=["NO_CONSTRAINTS"],
        ),
        TrainingPair(
            text_a="compliance law regulation",
            text_b="legal standard adherence",
            target_similarity=0.9,
            reason_codes_a=["COMPLIANCE_FIRST"],
            reason_codes_b=["COMPLIANCE_FIRST"],
        ),
        TrainingPair(
            text_a="risk mitigation caution",
            text_b="speed deadline urgent",
            target_similarity=0.0,
            reason_codes_a=["RISK_AVOIDANCE"],
            reason_codes_b=["SPEED_FIRST"],
        ),
    ][:n]


# ---------------------------------------------------------------------------
# TrainingPair テスト
# ---------------------------------------------------------------------------

class TestTrainingPair(unittest.TestCase):

    def test_namedtuple_fields(self):
        p = TrainingPair("a", "b", 0.5, ["X"], ["Y"])
        self.assertEqual(p.text_a, "a")
        self.assertEqual(p.target_similarity, 0.5)
        self.assertEqual(p.reason_codes_a, ["X"])

    def test_immutable(self):
        p = TrainingPair("a", "b", 0.5, [], [])
        with self.assertRaises(AttributeError):
            p.text_a = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_pairs テスト
# ---------------------------------------------------------------------------

class TestLoadPairs(unittest.TestCase):

    def test_load_from_json(self):
        raw = [
            {
                "text_a": "hello",
                "text_b": "world",
                "target_similarity": 0.3,
                "reason_codes_a": ["SAFETY_FIRST"],
                "reason_codes_b": ["SPEED_FIRST"],
            }
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(raw, f)
            path = f.name
        try:
            pairs = load_pairs(path)
            self.assertEqual(len(pairs), 1)
            self.assertIsInstance(pairs[0], TrainingPair)
            self.assertEqual(pairs[0].text_a, "hello")
            self.assertAlmostEqual(pairs[0].target_similarity, 0.3)
        finally:
            os.unlink(path)

    def test_load_multiple_pairs(self):
        raw = [
            {"text_a": f"text_{i}", "text_b": f"text_{i+1}",
             "target_similarity": 0.5,
             "reason_codes_a": ["CODE_A"], "reason_codes_b": ["CODE_B"]}
            for i in range(5)
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(raw, f)
            path = f.name
        try:
            pairs = load_pairs(path)
            self.assertEqual(len(pairs), 5)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# TransformerTrainer 基本テスト
# ---------------------------------------------------------------------------

class TestTransformerTrainerBasic(unittest.TestCase):

    def setUp(self):
        self.enc = MiniTransformerEncoder(seed=42)
        self.trainer = TransformerTrainer(self.enc)
        self.pairs = _make_pairs()

    def test_init(self):
        self.assertIs(self.trainer.encoder, self.enc)

    def test_evaluate_returns_dict(self):
        metrics = self.trainer.evaluate(self.pairs)
        self.assertIn("mse", metrics)
        self.assertIn("mean_cosine", metrics)
        self.assertIn("n_pairs", metrics)
        self.assertEqual(metrics["n_pairs"], len(self.pairs))

    def test_evaluate_mse_non_negative(self):
        metrics = self.trainer.evaluate(self.pairs)
        self.assertGreaterEqual(metrics["mse"], 0.0)

    def test_evaluate_mean_cosine_range(self):
        metrics = self.trainer.evaluate(self.pairs)
        self.assertGreaterEqual(metrics["mean_cosine"], -1.001)
        self.assertLessEqual(metrics["mean_cosine"], 1.001)

    def test_evaluate_empty_pairs(self):
        metrics = self.trainer.evaluate([])
        self.assertEqual(metrics["mse"], 0.0)
        self.assertEqual(metrics["mean_cosine"], 0.0)
        self.assertEqual(metrics["n_pairs"], 0)


# ---------------------------------------------------------------------------
# 訓練ループテスト
# ---------------------------------------------------------------------------

class TestTransformerTrainerTrain(unittest.TestCase):

    def setUp(self):
        self.enc = MiniTransformerEncoder(seed=0)
        self.trainer = TransformerTrainer(self.enc)
        self.pairs = _make_pairs()

    def test_train_returns_history(self):
        history = self.trainer.train(self.pairs, epochs=2, lr=0.01, verbose=False)
        self.assertEqual(len(history), 2)

    def test_history_keys(self):
        history = self.trainer.train(self.pairs, epochs=1, lr=0.01, verbose=False)
        self.assertIn("epoch", history[0])
        self.assertIn("mse", history[0])
        self.assertIn("mean_cosine", history[0])

    def test_history_epoch_numbers(self):
        history = self.trainer.train(self.pairs, epochs=3, lr=0.005, verbose=False)
        epochs = [h["epoch"] for h in history]
        self.assertEqual(epochs, [1, 2, 3])

    def test_train_changes_embeddings(self):
        """訓練後は埋め込みテーブルが変化している"""
        before = [row[:] for row in self.enc.embed.table]
        self.trainer.train(self.pairs, epochs=2, lr=0.01, verbose=False)
        after = self.enc.embed.table

        changed = any(
            before[i][j] != after[i][j]
            for i in range(len(before))
            for j in range(len(before[0]))
        )
        self.assertTrue(changed, "Embeddings should change after training")

    def test_train_clears_cache(self):
        """訓練後はキャッシュがクリアされている"""
        _ = self.enc.encode("safety first")
        self.assertGreater(len(self.enc._cache), 0)
        self.trainer.train(self.pairs, epochs=1, lr=0.01, verbose=False)
        self.assertEqual(len(self.enc._cache), 0)

    def test_train_single_epoch(self):
        history = self.trainer.train(self.pairs, epochs=1, lr=0.01, verbose=False)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["epoch"], 1)

    def test_train_zero_lr_no_change(self):
        """学習率 0 では埋め込みが変化しない"""
        before = [row[:] for row in self.enc.embed.table]
        self.trainer.train(self.pairs, epochs=3, lr=0.0, verbose=False)
        after = self.enc.embed.table
        self.assertEqual(before, after)


# ---------------------------------------------------------------------------
# 重みの保存 / ロードテスト
# ---------------------------------------------------------------------------

class TestWeightsSaveLoad(unittest.TestCase):

    def setUp(self):
        self.enc = MiniTransformerEncoder(seed=7)
        self.trainer = TransformerTrainer(self.enc)
        self.pairs = _make_pairs(4)

    def test_save_creates_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "weights.json")
            self.trainer.save_weights(path)
            self.assertTrue(os.path.isfile(path))

    def test_save_json_structure(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "weights.json")
            self.trainer.save_weights(path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("version", data)
            self.assertIn("embed_table", data)
            self.assertEqual(data["d_model"], MiniTransformerEncoder.D_MODEL)
            self.assertEqual(data["vocab_size"], self.enc.vocab_size())

    def test_save_embed_table_shape(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "weights.json")
            self.trainer.save_weights(path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            table = data["embed_table"]
            self.assertEqual(len(table), self.enc.vocab_size())
            self.assertEqual(len(table[0]), MiniTransformerEncoder.D_MODEL)

    def test_load_restores_weights(self):
        """保存 → ロードで同じ重みが復元される"""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "weights.json")
            # 訓練して保存
            self.trainer.train(self.pairs, epochs=2, lr=0.01, verbose=False)
            self.trainer.save_weights(path)
            trained_table = [row[:] for row in self.enc.embed.table]

            # 新しいエンコーダにロード
            enc2 = MiniTransformerEncoder(seed=99)  # 別シード
            trainer2 = TransformerTrainer(enc2)
            trainer2.load_weights(path)

            self.assertEqual(enc2.embed.table, trained_table)

    def test_load_clears_cache(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "weights.json")
            self.trainer.save_weights(path)
            # キャッシュを作る
            _ = self.enc.encode("test text")
            self.assertGreater(len(self.enc._cache), 0)
            # ロードするとキャッシュがクリアされる
            self.trainer.load_weights(path)
            self.assertEqual(len(self.enc._cache), 0)

    def test_load_shape_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad_weights.json")
            bad = {
                "version": "transformer_weights.v0.1",
                "embed_table": [[0.0] * 16],  # 間違った形状
            }
            with open(path, "w") as f:
                json.dump(bad, f)
            with self.assertRaises(ValueError):
                self.trainer.load_weights(path)

    def test_encoder_save_load_weights(self):
        """MiniTransformerEncoder.save_weights / load_weights でも同じ結果"""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "enc_weights.json")
            self.enc.save_weights(path)

            enc2 = MiniTransformerEncoder(seed=1)
            enc2.load_weights(path)
            self.assertEqual(enc2.embed.table, self.enc.embed.table)


# ---------------------------------------------------------------------------
# gen_training_data テスト
# ---------------------------------------------------------------------------

class TestGenTrainingData(unittest.TestCase):

    def test_generate_returns_list(self):
        from scripts.gen_training_data import generate_training_data
        pairs = generate_training_data(text_count=10, max_pairs=5, seed=0)
        self.assertIsInstance(pairs, list)

    def test_generate_pair_fields(self):
        from scripts.gen_training_data import generate_training_data
        pairs = generate_training_data(text_count=10, max_pairs=3, seed=1)
        for p in pairs:
            self.assertIn("text_a", p)
            self.assertIn("text_b", p)
            self.assertIn("target_similarity", p)
            self.assertIn("reason_codes_a", p)
            self.assertIn("reason_codes_b", p)

    def test_generate_similarity_range(self):
        from scripts.gen_training_data import generate_training_data
        pairs = generate_training_data(text_count=20, max_pairs=10, seed=2)
        for p in pairs:
            self.assertGreaterEqual(p["target_similarity"], 0.0)
            self.assertLessEqual(p["target_similarity"], 1.0)

    def test_generate_respects_max_pairs(self):
        from scripts.gen_training_data import generate_training_data
        pairs = generate_training_data(text_count=30, max_pairs=5, seed=3)
        self.assertLessEqual(len(pairs), 5)

    def test_generate_texts_are_strings(self):
        from scripts.gen_training_data import generate_training_data
        pairs = generate_training_data(text_count=10, max_pairs=5, seed=4)
        for p in pairs:
            self.assertIsInstance(p["text_a"], str)
            self.assertIsInstance(p["text_b"], str)
            self.assertGreater(len(p["text_a"]), 0)
            self.assertGreater(len(p["text_b"]), 0)

    def test_generate_deterministic(self):
        from scripts.gen_training_data import generate_training_data
        a = generate_training_data(text_count=10, max_pairs=5, seed=99)
        b = generate_training_data(text_count=10, max_pairs=5, seed=99)
        self.assertEqual(a, b)

    def test_generate_different_seeds(self):
        from scripts.gen_training_data import generate_training_data
        a = generate_training_data(text_count=10, max_pairs=5, seed=1)
        b = generate_training_data(text_count=10, max_pairs=5, seed=2)
        self.assertNotEqual(a, b)


# ---------------------------------------------------------------------------
# quick_train テスト
# ---------------------------------------------------------------------------

class TestQuickTrain(unittest.TestCase):

    def test_quick_train_returns_trainer(self):
        from scripts.gen_training_data import generate_training_data
        pairs_raw = generate_training_data(text_count=20, max_pairs=10, seed=5)
        with tempfile.TemporaryDirectory() as d:
            data_path = os.path.join(d, "pairs.json")
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(pairs_raw, f)
            trainer = quick_train(data_path, epochs=1, seed=0, verbose=False)
        self.assertIsInstance(trainer, TransformerTrainer)

    def test_quick_train_saves_weights(self):
        from scripts.gen_training_data import generate_training_data
        pairs_raw = generate_training_data(text_count=20, max_pairs=10, seed=6)
        with tempfile.TemporaryDirectory() as d:
            data_path = os.path.join(d, "pairs.json")
            weights_path = os.path.join(d, "weights.json")
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(pairs_raw, f)
            quick_train(data_path, weights_path=weights_path, epochs=1, seed=0, verbose=False)
            self.assertTrue(os.path.isfile(weights_path))


# ---------------------------------------------------------------------------
# _mean_cosine / _mean_mse ヘルパーテスト
# ---------------------------------------------------------------------------

class TestMetricHelpers(unittest.TestCase):

    def setUp(self):
        self.enc = MiniTransformerEncoder(seed=1)

    def test_mean_cosine_empty(self):
        self.assertEqual(_mean_cosine(self.enc, []), 0.0)

    def test_mean_mse_empty(self):
        self.assertEqual(_mean_mse(self.enc, []), 0.0)

    def test_mean_mse_perfect_prediction(self):
        """予測コサイン = ターゲットの場合、MSE = 0"""
        # 同一テキストペアはコサイン=1 になるはず
        enc = self.enc
        text = "hello world"
        vec = enc.encode(text)
        # コサイン(v,v) = 1.0
        from aicw.transformer import cosine_similarity
        pred = cosine_similarity(vec, vec)
        # target を pred に合わせれば MSE ≈ 0
        pair = TrainingPair(text, text, round(pred, 4), ["X"], ["X"])
        mse = _mean_mse(enc, [pair])
        self.assertAlmostEqual(mse, 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
