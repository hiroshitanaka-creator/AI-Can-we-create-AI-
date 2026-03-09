#!/usr/bin/env python3
"""
scripts/train_transformer.py

MiniTransformerEncoder を Centroid-Pull アルゴリズムで訓練する CLI。

使用例:
  # データ生成 → 訓練 の 2 ステップ
  python scripts/gen_training_data.py --count 300 --out data/training_pairs.json
  python scripts/train_transformer.py --data data/training_pairs.json \\
      --weights data/transformer_weights.json --epochs 10

  # ワンライナー（データ生成も含む）
  python scripts/train_transformer.py --auto-gen --count 300 --epochs 10 \\
      --weights data/transformer_weights.json

  # 訓練済み重みのロードと評価
  python scripts/train_transformer.py --data data/training_pairs.json \\
      --load-weights data/transformer_weights.json --eval-only
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from aicw.transformer import MiniTransformerEncoder
from aicw.transformer_trainer import TransformerTrainer, load_pairs


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Train MiniTransformerEncoder with Centroid-Pull algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--data", type=str, default="data/training_pairs.json",
        help="Path to training_pairs.json (default: data/training_pairs.json)",
    )
    p.add_argument(
        "--weights", type=str, default=None,
        help="Path to save trained weights (optional)",
    )
    p.add_argument(
        "--load-weights", type=str, default=None,
        help="Path to pre-trained weights to load before training",
    )
    p.add_argument(
        "--epochs", type=int, default=5,
        help="Number of training epochs (default: 5)",
    )
    p.add_argument(
        "--lr", type=float, default=0.005,
        help="Learning rate (default: 0.005)",
    )
    p.add_argument(
        "--seed", type=int, default=42,
        help="Encoder initialization seed (default: 42)",
    )
    p.add_argument(
        "--auto-gen", action="store_true",
        help="Auto-generate training data before training",
    )
    p.add_argument(
        "--count", type=int, default=300,
        help="Number of training pairs to generate (with --auto-gen, default: 300)",
    )
    p.add_argument(
        "--eval-only", action="store_true",
        help="Skip training; only evaluate with loaded weights",
    )
    p.add_argument(
        "--json", action="store_true",
        help="Output result as JSON",
    )
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    # ─ データ生成（--auto-gen 指定時）────────────────────────────────────
    if args.auto_gen:
        print(f"[gen]  Generating {args.count} training pairs...", file=sys.stderr)
        from scripts.gen_training_data import generate_training_data
        pairs_raw = generate_training_data(
            text_count=max(args.count, 50),
            max_pairs=args.count,
            seed=args.seed,
        )
        data_path = args.data
        os.makedirs(os.path.dirname(os.path.abspath(data_path)), exist_ok=True)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(pairs_raw, f, ensure_ascii=False)
        print(f"[gen]  Saved to {data_path}", file=sys.stderr)

    # ─ データロード ────────────────────────────────────────────────────────
    if not os.path.isfile(args.data):
        print(
            f"error: training data not found: {args.data}\n"
            f"  Run with --auto-gen to generate, or specify --data path.",
            file=sys.stderr,
        )
        return 1

    pairs = load_pairs(args.data)
    if not pairs:
        print(f"error: no pairs loaded from {args.data}", file=sys.stderr)
        return 1

    print(f"[data] Loaded {len(pairs)} pairs from {args.data}", file=sys.stderr)

    # ─ エンコーダ & トレーナー初期化 ────────────────────────────────────
    enc = MiniTransformerEncoder(seed=args.seed)
    trainer = TransformerTrainer(enc)

    # ─ 既存重みのロード ─────────────────────────────────────────────────
    if args.load_weights:
        if not os.path.isfile(args.load_weights):
            print(
                f"error: weights file not found: {args.load_weights}",
                file=sys.stderr,
            )
            return 1
        trainer.load_weights(args.load_weights)
        print(f"[load] Weights loaded from {args.load_weights}", file=sys.stderr)

    # ─ 評価のみモード ─────────────────────────────────────────────────────
    if args.eval_only:
        metrics = trainer.evaluate(pairs)
        if args.json:
            print(json.dumps(metrics, ensure_ascii=False))
        else:
            print(f"[eval] mse={metrics['mse']:.4f}  "
                  f"mean_cosine={metrics['mean_cosine']:.4f}  "
                  f"n={metrics['n_pairs']}")
        return 0

    # ─ 訓練 ────────────────────────────────────────────────────────────────
    print(
        f"[train] epochs={args.epochs}  lr={args.lr}  seed={args.seed}",
        file=sys.stderr,
    )
    history = trainer.train(pairs, epochs=args.epochs, lr=args.lr, verbose=not args.json)

    # ─ 訓練後評価 ──────────────────────────────────────────────────────────
    metrics = trainer.evaluate(pairs)

    # ─ 重みの保存 ──────────────────────────────────────────────────────────
    if args.weights:
        trainer.save_weights(args.weights)
        print(f"[save] Weights saved to {args.weights}", file=sys.stderr)

    # ─ 出力 ────────────────────────────────────────────────────────────────
    result = {
        "history": history,
        "final_metrics": metrics,
        "weights_path": args.weights,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        last = history[-1] if history else {}
        print(
            f"\n[done] final mse={last.get('mse', 0):.4f}  "
            f"mean_cosine={last.get('mean_cosine', 0):.4f}"
        )
        if args.weights:
            print(f"       weights → {args.weights}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
