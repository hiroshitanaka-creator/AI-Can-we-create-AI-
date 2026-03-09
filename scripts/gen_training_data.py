#!/usr/bin/env python3
"""
scripts/gen_training_data.py

Mini Transformer 用の学習ペアデータを自動生成する。

手順:
  1. situation テキストをランダム生成（複数バリエーション）
  2. build_decision_report() を通して reason_codes を自動付与
  3. テキストペアを作成し、Jaccard 類似度を教師信号として保存

出力形式（JSON リスト）:
  [
    {
      "text_a": "採用方針を見直したい（case-00001）",
      "text_b": "障害対応の優先順位を決めたい（case-00002）",
      "target_similarity": 0.5,
      "reason_codes_a": ["SAFETY_FIRST", "COMPLIANCE_FIRST"],
      "reason_codes_b": ["SAFETY_FIRST", "RISK_AVOIDANCE"]
    },
    ...
  ]

使用例:
  python scripts/gen_training_data.py --count 300 --out data/training_pairs.json
  python scripts/gen_training_data.py --count 50 --pretty  # stdout
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from typing import Any, Dict, List, Tuple

# プロジェクトルートを sys.path に追加
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from aicw.decision import build_decision_report

# ---------------------------------------------------------------------------
# テキスト生成素材（gen_fuzz_cases.py より拡張）
# ---------------------------------------------------------------------------

_SITUATIONS = [
    # 戦略・方針
    "新機能の公開方針を決めたい",
    "製品ロードマップの優先順位を見直したい",
    "新規事業への参入可否を判断したい",
    "既存サービスの廃止・刷新を判断したい",
    "グローバル展開の順序を決めたい",
    # 組織・人事
    "採用方針を見直したい",
    "チーム再編成の方向性を決めたい",
    "リモートワーク方針を策定したい",
    "評価制度の変更可否を判断したい",
    "部門間の役割分担を再設計したい",
    # 技術・システム
    "障害対応の優先順位を決めたい",
    "技術的負債の解消計画を立てたい",
    "データ活用の範囲を決めたい",
    "セキュリティ強化施策を選択したい",
    "クラウド移行の段取りを決めたい",
    # コスト・リソース
    "運用コスト削減案を選びたい",
    "予算配分の最適化方針を決めたい",
    "外部委託か内製化かを判断したい",
    "設備投資の優先順位を決めたい",
    # コンプライアンス・社会
    "法改正への対応方針を決めたい",
    "個人情報管理の方針を強化したい",
    "環境負荷低減策を選びたい",
    "取引先との契約条件を見直したい",
    # AI・データ
    "AI採用審査システムの全社導入を判断したい",
    "顧客データの二次利用範囲を決めたい",
    "自動化ツールの導入優先度を決めたい",
]

_CONSTRAINT_WORDS = [
    "安全", "品質", "リスク", "法令", "コンプライアンス",
    "期限", "至急", "納期", "予算", "公平性", "透明性", "持続可能性",
]

_OPTIONS = [
    "A: 安全側（失敗を減らす・段階的）",
    "B: バランス（段階導入・中庸）",
    "C: 速度側（早期実行・全面展開）",
]

_BENEFICIARIES = [
    "ユーザー", "運用チーム", "開発チーム", "顧客", "コミュニティ",
    "管理者", "従業員", "株主", "地域社会", "将来世代",
]

_STRUCTURES = ["個人", "関係", "社会", "認知", "生態"]


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------

def _pick_some(rng: random.Random, items: List[str], max_n: int) -> List[str]:
    n = rng.randint(1, max_n)
    return rng.sample(items, k=min(n, len(items)))


def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _extract_reason_codes(brief: Dict[str, Any]) -> List[str]:
    """decision brief から reason_codes を抽出する。"""
    if brief.get("status") == "blocked":
        return ["BLOCKED"]
    sel = brief.get("selection", {})
    codes = sel.get("reason_codes", [])
    return list(codes) if codes else ["NO_CONSTRAINTS"]


# ---------------------------------------------------------------------------
# リクエスト & situation 生成
# ---------------------------------------------------------------------------

def _build_request(rng: random.Random, situation: str) -> Dict[str, Any]:
    req: Dict[str, Any] = {"situation": situation}
    req["constraints"] = _pick_some(rng, _CONSTRAINT_WORDS, 3)
    req["options"] = _OPTIONS[:]
    req["beneficiaries"] = _pick_some(rng, _BENEFICIARIES, 3)
    req["affected_structures"] = _pick_some(rng, _STRUCTURES, 2)
    return req


def _generate_labeled_texts(
    count: int,
    seed: int,
) -> List[Dict[str, Any]]:
    """
    situation テキストを生成し、build_decision_report で reason_codes を付与する。

    Returns:
        [{"text": str, "reason_codes": List[str]}, ...]
    """
    rng = random.Random(seed)
    labeled: List[Dict[str, Any]] = []

    for i in range(count):
        base = rng.choice(_SITUATIONS)
        suffix = f"（case-{i:05d}）"
        situation = f"{base}{suffix}"

        req = _build_request(rng, situation)
        try:
            brief = build_decision_report(req)
            codes = _extract_reason_codes(brief)
        except Exception:
            codes = ["NO_CONSTRAINTS"]

        labeled.append({"text": situation, "reason_codes": codes})

    return labeled


# ---------------------------------------------------------------------------
# ペア生成
# ---------------------------------------------------------------------------

def _generate_pairs(
    labeled: List[Dict[str, Any]],
    max_pairs: int,
    seed: int,
) -> List[Dict[str, Any]]:
    """
    labeled texts から学習ペアを生成する。

    戦略:
      - 同一 reason_code を持つペア（正例: target_sim > 0.5）を重点的に生成
      - 異なる reason_code のペア（負例: target_sim ≈ 0）もバランスよく含める
    """
    rng = random.Random(seed + 1)
    n = len(labeled)
    pairs: List[Dict[str, Any]] = []
    seen: set = set()

    # 全ペアのインデックス候補を作成（正例優先）
    # まず同コードペアを収集
    from collections import defaultdict
    code_to_idx: Dict[str, List[int]] = defaultdict(list)
    for idx, item in enumerate(labeled):
        for code in item["reason_codes"]:
            code_to_idx[code].append(idx)

    # 正例ペア（同 code 内からランダムサンプル）
    positive_pairs = []
    for code, indices in code_to_idx.items():
        if len(indices) < 2:
            continue
        rng.shuffle(indices)
        for k in range(0, len(indices) - 1, 2):
            i, j = indices[k], indices[k + 1]
            key = (min(i, j), max(i, j))
            if key not in seen:
                seen.add(key)
                positive_pairs.append(key)

    # 負例ペア（ランダムサンプル）
    negative_pairs = []
    attempts = 0
    while len(negative_pairs) < max_pairs // 2 and attempts < max_pairs * 10:
        i = rng.randint(0, n - 1)
        j = rng.randint(0, n - 1)
        if i == j:
            attempts += 1
            continue
        key = (min(i, j), max(i, j))
        if key not in seen:
            seen.add(key)
            sim = _jaccard(labeled[i]["reason_codes"], labeled[j]["reason_codes"])
            if sim < 0.3:  # 明確な負例のみ
                negative_pairs.append(key)
        attempts += 1

    # 結合してシャッフル
    all_keys = positive_pairs + negative_pairs
    rng.shuffle(all_keys)
    all_keys = all_keys[:max_pairs]

    for i, j in all_keys:
        a = labeled[i]
        b = labeled[j]
        sim = _jaccard(a["reason_codes"], b["reason_codes"])
        pairs.append({
            "text_a": a["text"],
            "text_b": b["text"],
            "target_similarity": round(sim, 4),
            "reason_codes_a": a["reason_codes"],
            "reason_codes_b": b["reason_codes"],
        })

    return pairs


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def generate_training_data(
    text_count: int = 150,
    max_pairs: int = 300,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """
    学習ペアデータを生成して返す。

    Args:
        text_count: 生成する situation テキスト数（ペアの母数）
        max_pairs:  最大ペア数
        seed:       乱数シード

    Returns:
        学習ペアリスト（各要素: text_a, text_b, target_similarity, reason_codes_a/b）
    """
    labeled = _generate_labeled_texts(text_count, seed)
    pairs = _generate_pairs(labeled, max_pairs, seed)
    return pairs


def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate training pairs for MiniTransformerEncoder"
    )
    p.add_argument("--count", type=int, default=300,
                   help="Number of training pairs to generate (default: 300)")
    p.add_argument("--texts", type=int, default=0,
                   help="Number of source texts (default: count * 0.6)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=str, default="-",
                   help="Output path (default: stdout)")
    p.add_argument("--pretty", action="store_true",
                   help="Pretty-print JSON")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    text_count = args.texts if args.texts > 0 else max(args.count, 50)
    pairs = generate_training_data(
        text_count=text_count,
        max_pairs=args.count,
        seed=args.seed,
    )

    indent = 2 if args.pretty else None

    if args.out == "-":
        json.dump(pairs, sys.stdout, ensure_ascii=False, indent=indent)
        print()
        return 0

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=indent)
        if indent is not None:
            f.write("\n")

    print(f"Generated {len(pairs)} training pairs → {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
