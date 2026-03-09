"""
aicw/transformer.py

Pure Python ミニ Transformer エンコーダ
外部ライブラリ不使用（標準ライブラリのみ）

アーキテクチャ:
  - 文字レベルトークナイザ
  - Token Embedding + Positional Encoding（正弦波）
  - Multi-Head Self-Attention
  - Feed-Forward Network (ReLU)
  - Layer Normalization + Residual Connection
  - Mean Pooling → 固定長ベクトル

パラメータ:
  d_model = 32  埋め込み次元
  n_heads = 2   アテンションヘッド数
  d_ff    = 64  FFN 中間次元
  n_layers= 1   Transformer ブロック数
  max_seq = 64  最大シーケンス長

注意:
  重みはランダム初期化（学習なし）。
  このモジュールはアーキテクチャのデモ実装。
  意味論的類似度は Jaccard（rule-based）の方が高精度。
"""

from __future__ import annotations

import json
import math
import os
import random
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# 型エイリアス
# ---------------------------------------------------------------------------
Matrix = List[List[float]]
Vector = List[float]


# ---------------------------------------------------------------------------
# 行列演算（標準ライブラリのみ）
# ---------------------------------------------------------------------------

def mat_mul(A: Matrix, B: Matrix) -> Matrix:
    """行列積 A (m×k) × B (k×n) → (m×n)"""
    m = len(A)
    k = len(A[0])
    n = len(B[0])
    C: Matrix = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for p in range(k):
            a_ip = A[i][p]
            if a_ip == 0.0:
                continue
            for j in range(n):
                C[i][j] += a_ip * B[p][j]
    return C


def mat_add(A: Matrix, B: Matrix) -> Matrix:
    """要素加算 A + B（同一形状）"""
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def mat_scale(A: Matrix, s: float) -> Matrix:
    """スカラー倍 A * s"""
    return [[x * s for x in row] for row in A]


def transpose(A: Matrix) -> Matrix:
    """転置行列"""
    rows, cols = len(A), len(A[0])
    return [[A[r][c] for r in range(rows)] for c in range(cols)]


def softmax(A: Matrix) -> Matrix:
    """行ごとに Softmax を適用"""
    result: Matrix = []
    for row in A:
        m = max(row)
        e = [math.exp(x - m) for x in row]
        s = sum(e)
        result.append([v / s for v in e])
    return result


def relu(A: Matrix) -> Matrix:
    """要素ごとに ReLU を適用"""
    return [[max(0.0, x) for x in row] for row in A]


def layer_norm(A: Matrix, eps: float = 1e-6) -> Matrix:
    """行ごとに Layer Normalization を適用"""
    result: Matrix = []
    for row in A:
        n = len(row)
        mean = sum(row) / n
        var = sum((x - mean) ** 2 for x in row) / n
        std = math.sqrt(var + eps)
        result.append([(x - mean) / std for x in row])
    return result


# ---------------------------------------------------------------------------
# 初期化
# ---------------------------------------------------------------------------

def _xavier(rows: int, cols: int, seed: int) -> Matrix:
    """Xavier 一様分布初期化"""
    rng = random.Random(seed)
    limit = math.sqrt(6.0 / (rows + cols))
    return [[rng.uniform(-limit, limit) for _ in range(cols)] for _ in range(rows)]


def _zeros(rows: int, cols: int) -> Matrix:
    return [[0.0] * cols for _ in range(rows)]


# ---------------------------------------------------------------------------
# Linear 層
# ---------------------------------------------------------------------------

class Linear:
    """全結合層（バイアスあり）"""

    def __init__(self, in_features: int, out_features: int, seed: int = 0) -> None:
        self.W: Matrix = _xavier(in_features, out_features, seed)
        self.b: Vector = [0.0] * out_features

    def forward(self, X: Matrix) -> Matrix:
        """X: (seq × in) → (seq × out)"""
        out = mat_mul(X, self.W)
        return [[out[i][j] + self.b[j] for j in range(len(out[0]))] for i in range(len(out))]


# ---------------------------------------------------------------------------
# 位置エンコーディング（正弦波）
# ---------------------------------------------------------------------------

def positional_encoding(seq_len: int, d_model: int) -> Matrix:
    """
    Attention is All You Need の正弦波 PE。
    PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """
    PE: Matrix = []
    for pos in range(seq_len):
        row: Vector = []
        for i in range(d_model):
            denom = 10000 ** (2 * (i // 2) / d_model)
            if i % 2 == 0:
                row.append(math.sin(pos / denom))
            else:
                row.append(math.cos(pos / denom))
        PE.append(row)
    return PE


# ---------------------------------------------------------------------------
# Self-Attention（単一ヘッド）
# ---------------------------------------------------------------------------

class SelfAttention:
    """Scaled Dot-Product Attention"""

    def __init__(self, d_model: int, d_k: int, seed: int = 0) -> None:
        self.d_k = d_k
        self.W_Q = Linear(d_model, d_k, seed=seed)
        self.W_K = Linear(d_model, d_k, seed=seed + 1)
        self.W_V = Linear(d_model, d_k, seed=seed + 2)

    def forward(self, X: Matrix) -> Matrix:
        Q = self.W_Q.forward(X)
        K = self.W_K.forward(X)
        V = self.W_V.forward(X)

        # スケーリング係数
        scale = 1.0 / math.sqrt(self.d_k)
        scores = mat_scale(mat_mul(Q, transpose(K)), scale)
        weights = softmax(scores)
        return mat_mul(weights, V)


# ---------------------------------------------------------------------------
# Multi-Head Attention
# ---------------------------------------------------------------------------

class MultiHeadAttention:
    """複数ヘッドのアテンションを結合"""

    def __init__(self, d_model: int, n_heads: int, seed: int = 0) -> None:
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads})")
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        self.heads = [
            SelfAttention(d_model, self.d_k, seed=seed + h * 10)
            for h in range(n_heads)
        ]
        self.W_O = Linear(d_model, d_model, seed=seed + 100)

    def forward(self, X: Matrix) -> Matrix:
        seq_len = len(X)
        # 各ヘッドの出力: [(seq × d_k), ...]
        head_outs = [h.forward(X) for h in self.heads]
        # 結合: (seq × d_model)
        concat: Matrix = [
            [x for head in head_outs for x in head[i]]
            for i in range(seq_len)
        ]
        return self.W_O.forward(concat)


# ---------------------------------------------------------------------------
# Feed-Forward Network
# ---------------------------------------------------------------------------

class FeedForward:
    """2層 FFN（ReLU 活性化）"""

    def __init__(self, d_model: int, d_ff: int, seed: int = 0) -> None:
        self.linear1 = Linear(d_model, d_ff, seed=seed)
        self.linear2 = Linear(d_ff, d_model, seed=seed + 1)

    def forward(self, X: Matrix) -> Matrix:
        return self.linear2.forward(relu(self.linear1.forward(X)))


# ---------------------------------------------------------------------------
# Transformer ブロック
# ---------------------------------------------------------------------------

class TransformerBlock:
    """
    Transformer エンコーダブロック:
      x → MHA(x) + x → LN → FFN(x) + x → LN
    """

    def __init__(self, d_model: int, n_heads: int, d_ff: int, seed: int = 0) -> None:
        self.attn = MultiHeadAttention(d_model, n_heads, seed=seed)
        self.ff = FeedForward(d_model, d_ff, seed=seed + 200)

    def forward(self, X: Matrix) -> Matrix:
        # Sub-layer 1: Self-Attention + Residual + LayerNorm
        attn_out = self.attn.forward(X)
        X = layer_norm(mat_add(X, attn_out))
        # Sub-layer 2: FFN + Residual + LayerNorm
        ff_out = self.ff.forward(X)
        X = layer_norm(mat_add(X, ff_out))
        return X


# ---------------------------------------------------------------------------
# Token Embedding
# ---------------------------------------------------------------------------

class TokenEmbedding:
    """トークン ID → 埋め込みベクトル"""

    def __init__(self, vocab_size: int, d_model: int, seed: int = 0) -> None:
        rng = random.Random(seed)
        # 小さいスケールで初期化
        scale = 0.02
        self.table: Matrix = [
            [rng.gauss(0.0, scale) for _ in range(d_model)]
            for _ in range(vocab_size)
        ]

    def forward(self, token_ids: List[int]) -> Matrix:
        return [self.table[t] for t in token_ids]


# ---------------------------------------------------------------------------
# トークナイザ
# ---------------------------------------------------------------------------

def _build_vocab() -> Dict[str, int]:
    """文字レベル語彙辞書を構築（ASCII + 基本記号）"""
    chars = (
        " abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        ".,!?-_/()[]{}:;@#$%&*+=<>'\"\\|\t\n"
        # 日本語（ひらがな・カタカナ・CJK）は UNK で代替
    )
    vocab: Dict[str, int] = {ch: i for i, ch in enumerate(chars)}
    vocab["<UNK>"] = len(vocab)
    vocab["<PAD>"] = len(vocab)
    return vocab


# ---------------------------------------------------------------------------
# Mini Transformer Encoder
# ---------------------------------------------------------------------------

class MiniTransformerEncoder:
    """
    文字レベル Transformer エンコーダ（Pure Python）。

    text → encode() → 固定長ベクトル (List[float], 長さ = D_MODEL)

    パラメータ（固定）:
        D_MODEL = 32, N_HEADS = 2, D_FF = 64, N_LAYERS = 1, MAX_SEQ = 64

    使用例:
        enc = MiniTransformerEncoder()
        vec = enc.encode("AIによる意思決定支援")
        print(len(vec))  # 32
    """

    D_MODEL = 32
    N_HEADS = 2
    D_FF = 64
    N_LAYERS = 1
    MAX_SEQ = 64

    def __init__(self, seed: int = 42) -> None:
        self._vocab = _build_vocab()
        self._vocab_size = len(self._vocab)
        self._pad_id = self._vocab["<PAD>"]
        self._unk_id = self._vocab["<UNK>"]

        self.embed = TokenEmbedding(self._vocab_size, self.D_MODEL, seed=seed)
        self.blocks = [
            TransformerBlock(self.D_MODEL, self.N_HEADS, self.D_FF, seed=seed + i * 1000)
            for i in range(self.N_LAYERS)
        ]
        # キャッシュ: 同一テキストを再エンコードしない
        self._cache: Dict[str, Vector] = {}

    # ------------------------------------------------------------------

    def tokenize(self, text: str) -> List[int]:
        """文字列 → トークン ID リスト（最大 MAX_SEQ、パディングあり）"""
        ids = [self._vocab.get(ch, self._unk_id) for ch in text[: self.MAX_SEQ]]
        # パディング
        ids += [self._pad_id] * (self.MAX_SEQ - len(ids))
        return ids

    def encode(self, text: str) -> Vector:
        """
        テキストを固定長ベクトルにエンコードする。

        Steps:
            1. 文字トークン化
            2. Token Embedding + Positional Encoding
            3. Transformer ブロック × N_LAYERS
            4. Mean Pooling（PAD を除く）

        Returns:
            List[float] 長さ D_MODEL = 32
        """
        if text in self._cache:
            return self._cache[text]

        token_ids = self.tokenize(text)

        # 1. 埋め込み
        X: Matrix = self.embed.forward(token_ids)

        # 2. 位置エンコーディングを加算
        PE = positional_encoding(self.MAX_SEQ, self.D_MODEL)
        X = mat_add(X, PE)

        # 3. Transformer ブロック
        for block in self.blocks:
            X = block.forward(X)

        # 4. Mean Pooling（PAD トークンを除外）
        text_len = min(len(text), self.MAX_SEQ)
        if text_len == 0:
            text_len = self.MAX_SEQ  # すべて PAD の場合は全平均
        pool_X = X[:text_len]
        d = self.D_MODEL
        vec: Vector = [
            sum(pool_X[i][j] for i in range(len(pool_X))) / len(pool_X)
            for j in range(d)
        ]

        self._cache[text] = vec
        return vec

    def vocab_size(self) -> int:
        return self._vocab_size

    def clear_cache(self) -> None:
        self._cache.clear()

    # ------------------------------------------------------------------
    # 重みの保存 / ロード
    # ------------------------------------------------------------------

    def save_weights(self, path: str) -> None:
        """
        Token Embedding テーブルを JSON ファイルに保存する。

        保存形式:
            {
              "version": "transformer_weights.v0.1",
              "d_model": int,
              "vocab_size": int,
              "embed_table": [[float, ...], ...]
            }

        Args:
            path: 保存先ファイルパス
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "version": "transformer_weights.v0.1",
            "d_model": self.D_MODEL,
            "vocab_size": self._vocab_size,
            "embed_table": self.embed.table,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load_weights(self, path: str) -> None:
        """
        保存済み Token Embedding テーブルを JSON ファイルからロードする。

        embed.table を上書きし、キャッシュをクリアする。

        Args:
            path: 重みファイルパス（save_weights で保存したもの）

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 重みの形状が現在のモデルと不一致
        """
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        table = data.get("embed_table", [])
        if not table:
            raise ValueError(f"embed_table が空です: {path}")

        if len(table) != self._vocab_size or len(table[0]) != self.D_MODEL:
            raise ValueError(
                f"重みの形状が不一致: "
                f"expected ({self._vocab_size}, {self.D_MODEL}), "
                f"got ({len(table)}, {len(table[0]) if table else 0})"
            )

        self.embed.table = table
        self.clear_cache()


# ---------------------------------------------------------------------------
# コサイン類似度
# ---------------------------------------------------------------------------

def cosine_similarity(a: Vector, b: Vector) -> float:
    """2 ベクトルのコサイン類似度（-1.0〜1.0）"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# テキスト類似度ランキング
# ---------------------------------------------------------------------------

def rank_by_similarity(
    query: str,
    corpus: List[str],
    encoder: MiniTransformerEncoder | None = None,
) -> List[Tuple[int, str, float]]:
    """
    query と corpus 内の各テキストの類似度を計算し、降順にソートして返す。

    Args:
        query:   クエリテキスト
        corpus:  比較対象テキストのリスト
        encoder: エンコーダ（None の場合はデフォルト設定で生成）

    Returns:
        [(idx, text, similarity), ...] 類似度降順
    """
    enc = encoder or MiniTransformerEncoder()
    q_vec = enc.encode(query)
    results = []
    for idx, text in enumerate(corpus):
        sim = cosine_similarity(q_vec, enc.encode(text))
        results.append((idx, text, round(sim, 6)))
    results.sort(key=lambda x: x[2], reverse=True)
    return results


# ---------------------------------------------------------------------------
# アーキテクチャ情報
# ---------------------------------------------------------------------------

def architecture_summary() -> str:
    """モデルアーキテクチャの概要文字列を返す。"""
    enc = MiniTransformerEncoder.__dict__
    d = MiniTransformerEncoder.D_MODEL
    h = MiniTransformerEncoder.N_HEADS
    ff = MiniTransformerEncoder.D_FF
    nl = MiniTransformerEncoder.N_LAYERS
    ms = MiniTransformerEncoder.MAX_SEQ
    v = len(_build_vocab())

    # パラメータ数推定
    embed_params = v * d
    attn_params = nl * (3 * d * (d // h) + d * d) * h  # Q,K,V,O per head
    ff_params = nl * (d * ff + ff * d)
    total = embed_params + attn_params + ff_params

    return (
        f"MiniTransformerEncoder\n"
        f"  Tokenizer  : character-level, vocab_size={v}\n"
        f"  d_model    : {d}\n"
        f"  n_heads    : {h}  (d_k={d // h} per head)\n"
        f"  d_ff       : {ff}\n"
        f"  n_layers   : {nl}\n"
        f"  max_seq    : {ms}\n"
        f"  output_dim : {d}  (mean-pooled)\n"
        f"  ~params    : {total:,}  (Xavier init, not trained)\n"
        f"  deps       : stdlib only (no numpy/torch)\n"
    )
