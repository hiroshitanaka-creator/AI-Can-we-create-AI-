"""
aicw/transformer_trainer.py

Centroid-Pull アルゴリズムで MiniTransformerEncoder を訓練する。
外部ライブラリ不使用（標準ライブラリのみ）。

## アルゴリズム: Centroid-Pull

1. テキストを reason_codes クラスタ（ラベル）でグループ化
2. 各クラスタ内のテキストをエンコードし、重心（centroid）を計算
3. 各テキストの埋め込みを centroid 方向に微小更新
   - update = lr * (centroid - vec)
   - テキスト内の各トークンの埋め込み行を update で補正
4. キャッシュをクリアして次のエポックへ

## 使用例

    from aicw.transformer import MiniTransformerEncoder
    from aicw.transformer_trainer import TransformerTrainer, load_pairs

    enc = MiniTransformerEncoder(seed=42)
    pairs = load_pairs("data/training_pairs.json")
    trainer = TransformerTrainer(enc)
    history = trainer.train(pairs, epochs=5, lr=0.005)
    trainer.save_weights("data/transformer_weights.json")

    # 訓練済み重みを再ロード
    enc2 = MiniTransformerEncoder(seed=42)
    trainer2 = TransformerTrainer(enc2)
    trainer2.load_weights("data/transformer_weights.json")
"""

from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from typing import Any, Dict, List, NamedTuple, Optional

from aicw.transformer import MiniTransformerEncoder, cosine_similarity


# ---------------------------------------------------------------------------
# データ型
# ---------------------------------------------------------------------------

class TrainingPair(NamedTuple):
    text_a: str
    text_b: str
    target_similarity: float
    reason_codes_a: List[str]
    reason_codes_b: List[str]


# ---------------------------------------------------------------------------
# データロード
# ---------------------------------------------------------------------------

def load_pairs(path: str) -> List[TrainingPair]:
    """
    gen_training_data.py が出力した JSON ファイルを TrainingPair リストとして読み込む。

    Args:
        path: JSON ファイルパス

    Returns:
        List[TrainingPair]
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    pairs = []
    for item in raw:
        pairs.append(TrainingPair(
            text_a=item["text_a"],
            text_b=item["text_b"],
            target_similarity=float(item["target_similarity"]),
            reason_codes_a=list(item.get("reason_codes_a", [])),
            reason_codes_b=list(item.get("reason_codes_b", [])),
        ))
    return pairs


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------

def _vec_sub(a: List[float], b: List[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]


def _vec_scale(v: List[float], s: float) -> List[float]:
    return [x * s for x in v]


def _vec_add_inplace(target: List[float], delta: List[float]) -> None:
    for i in range(len(target)):
        target[i] += delta[i]


def _mean_cosine(
    encoder: MiniTransformerEncoder,
    pairs: List[TrainingPair],
) -> float:
    """全ペアの平均コサイン類似度を計算する。"""
    if not pairs:
        return 0.0
    total = 0.0
    for p in pairs:
        va = encoder.encode(p.text_a)
        vb = encoder.encode(p.text_b)
        total += cosine_similarity(va, vb)
    return total / len(pairs)


def _mean_mse(
    encoder: MiniTransformerEncoder,
    pairs: List[TrainingPair],
) -> float:
    """全ペアの平均 MSE（予測コサイン vs 目標類似度）を計算する。"""
    if not pairs:
        return 0.0
    total = 0.0
    for p in pairs:
        va = encoder.encode(p.text_a)
        vb = encoder.encode(p.text_b)
        pred = cosine_similarity(va, vb)
        total += (pred - p.target_similarity) ** 2
    return total / len(pairs)


# ---------------------------------------------------------------------------
# TransformerTrainer
# ---------------------------------------------------------------------------

class TransformerTrainer:
    """
    MiniTransformerEncoder の Token Embedding を Centroid-Pull で更新する訓練器。

    Args:
        encoder: 訓練対象の MiniTransformerEncoder インスタンス
    """

    def __init__(self, encoder: MiniTransformerEncoder) -> None:
        self.encoder = encoder

    # ------------------------------------------------------------------
    # 訓練
    # ------------------------------------------------------------------

    def train(
        self,
        pairs: List[TrainingPair],
        epochs: int = 5,
        lr: float = 0.005,
        verbose: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Centroid-Pull アルゴリズムで Token Embedding を訓練する。

        Args:
            pairs:   学習ペアリスト（gen_training_data.py の出力）
            epochs:  エポック数
            lr:      学習率（デフォルト 0.005）
            verbose: True の場合、各エポックのログを stderr に出力

        Returns:
            history: [{"epoch": int, "mse": float, "mean_cosine": float}, ...]
        """
        history: List[Dict[str, Any]] = []

        # ─ Step 0: ペアからテキスト × reason_codes を収集 ─────────────────
        # 各テキストをどの reason_code クラスタに属させるか決める
        # → 各テキストの reason_codes_a / reason_codes_b を使用
        text_to_codes: Dict[str, List[str]] = {}
        for p in pairs:
            if p.text_a not in text_to_codes:
                text_to_codes[p.text_a] = p.reason_codes_a
            if p.text_b not in text_to_codes:
                text_to_codes[p.text_b] = p.reason_codes_b

        # ─ 初期評価 ────────────────────────────────────────────────────────
        init_mse = _mean_mse(self.encoder, pairs)
        init_cosine = _mean_cosine(self.encoder, pairs)
        if verbose:
            print(
                f"[init]  mse={init_mse:.4f}  mean_cosine={init_cosine:.4f}",
                flush=True,
            )

        for epoch in range(1, epochs + 1):
            self._centroid_pull_step(text_to_codes, lr)
            # キャッシュをクリアして再エンコード
            self.encoder.clear_cache()

            mse = _mean_mse(self.encoder, pairs)
            mean_cos = _mean_cosine(self.encoder, pairs)
            history.append({"epoch": epoch, "mse": mse, "mean_cosine": mean_cos})

            if verbose:
                print(
                    f"[epoch {epoch:02d}]  mse={mse:.4f}  mean_cosine={mean_cos:.4f}",
                    flush=True,
                )

        # 訓練完了後はキャッシュをクリアして clean な状態にする
        self.encoder.clear_cache()
        return history

    def _centroid_pull_step(
        self,
        text_to_codes: Dict[str, List[str]],
        lr: float,
    ) -> None:
        """
        1エポック分の Centroid-Pull を実行する。

        各 reason_code クラスタの重心を計算し、
        そのクラスタ内テキストのトークン埋め込みを重心方向に更新する。
        """
        enc = self.encoder

        # クラスタ: reason_code → [text, ...]
        clusters: Dict[str, List[str]] = defaultdict(list)
        for text, codes in text_to_codes.items():
            for code in codes:
                clusters[code].append(text)

        for code, texts in clusters.items():
            if len(texts) < 2:
                continue  # 1件のみのクラスタはスキップ

            # 重心計算
            d = enc.D_MODEL
            centroid = [0.0] * d
            vecs = []
            for text in texts:
                v = enc.encode(text)
                vecs.append(v)
                for j in range(d):
                    centroid[j] += v[j]
            for j in range(d):
                centroid[j] /= len(texts)

            # 各テキストのトークン埋め込みを centroid 方向に更新
            for text, vec in zip(texts, vecs):
                delta = _vec_sub(centroid, vec)  # centroid - vec
                update = _vec_scale(delta, lr)

                # テキスト内のトークン ID を取得
                token_ids = enc.tokenize(text)
                # PAD を除外
                pad_id = enc._pad_id
                unique_ids = list({t for t in token_ids if t != pad_id})

                # 各トークンの埋め込み行を update で補正
                for tid in unique_ids:
                    _vec_add_inplace(enc.embed.table[tid], update)

    # ------------------------------------------------------------------
    # 評価
    # ------------------------------------------------------------------

    def evaluate(self, pairs: List[TrainingPair]) -> Dict[str, float]:
        """
        テストペアに対して評価指標を返す。

        Returns:
            {"mse": float, "mean_cosine": float, "n_pairs": int}
        """
        self.encoder.clear_cache()
        return {
            "mse": round(_mean_mse(self.encoder, pairs), 6),
            "mean_cosine": round(_mean_cosine(self.encoder, pairs), 6),
            "n_pairs": len(pairs),
        }

    # ------------------------------------------------------------------
    # 重みの保存 / ロード
    # ------------------------------------------------------------------

    def save_weights(self, path: str) -> None:
        """
        訓練済み Token Embedding を JSON ファイルに保存する。

        保存形式:
            {
              "version": "transformer_weights.v0.1",
              "d_model": int,
              "vocab_size": int,
              "embed_table": [[float, ...], ...]
            }
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "version": "transformer_weights.v0.1",
            "d_model": self.encoder.D_MODEL,
            "vocab_size": self.encoder.vocab_size(),
            "embed_table": self.encoder.embed.table,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return

    def load_weights(self, path: str) -> None:
        """
        保存済み Token Embedding を JSON ファイルからロードする。

        エンコーダの embed.table を上書きし、キャッシュをクリアする。
        """
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        table = data.get("embed_table", [])
        if not table:
            raise ValueError(f"embed_table が空です: {path}")

        expected_vs = self.encoder.vocab_size()
        expected_d = self.encoder.D_MODEL
        if len(table) != expected_vs or len(table[0]) != expected_d:
            raise ValueError(
                f"重みの形状が不一致: "
                f"expected ({expected_vs}, {expected_d}), "
                f"got ({len(table)}, {len(table[0]) if table else 0})"
            )

        self.encoder.embed.table = table
        self.encoder.clear_cache()


# ---------------------------------------------------------------------------
# 便利関数
# ---------------------------------------------------------------------------

def quick_train(
    data_path: str,
    weights_path: Optional[str] = None,
    epochs: int = 5,
    lr: float = 0.005,
    seed: int = 42,
    verbose: bool = True,
) -> TransformerTrainer:
    """
    学習データを読み込み、訓練して TransformerTrainer を返す。

    Args:
        data_path:    training_pairs.json のパス
        weights_path: 訓練済み重みの保存先（None の場合は保存しない）
        epochs:       エポック数
        lr:           学習率
        seed:         エンコーダの初期シード
        verbose:      進捗表示

    Returns:
        訓練済み TransformerTrainer
    """
    enc = MiniTransformerEncoder(seed=seed)
    trainer = TransformerTrainer(enc)
    pairs = load_pairs(data_path)
    trainer.train(pairs, epochs=epochs, lr=lr, verbose=verbose)
    if weights_path:
        trainer.save_weights(weights_path)
    return trainer
