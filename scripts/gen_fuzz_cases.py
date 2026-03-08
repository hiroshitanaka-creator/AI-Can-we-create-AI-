#!/usr/bin/env python3
"""
Decision request 用の簡易ファジングケース生成器。

- 標準ライブラリのみ
- decision_request.v0 の型を満たす入力を大量生成
- ランダムシード固定で再現可能
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from typing import Any, Dict, List


_SITUATIONS = [
    "新機能の公開方針を決めたい",
    "障害対応の優先順位を決めたい",
    "採用方針を見直したい",
    "データ活用の範囲を決めたい",
    "運用コスト削減案を選びたい",
]

_CONSTRAINT_WORDS = [
    "安全", "品質", "リスク", "法令", "コンプラ", "期限", "至急", "納期", "予算",
]

_OPTIONS = [
    "A: 安全側（失敗を減らす）",
    "B: バランス（段階導入）",
    "C: 速度側（早期実行）",
]

_STATUS_WORDS = [
    "CEO", "部長", "平社員", "学生", "有名人", "無名人", "専門家", "素人",
]

_BENEFICIARIES = [
    "ユーザー", "運用チーム", "開発チーム", "顧客", "コミュニティ", "管理者",
]

_STRUCTURES = ["個人", "関係", "社会", "認知", "生態"]


def _pick_some(rng: random.Random, items: List[str], max_n: int) -> List[str]:
    n = rng.randint(0, max_n)
    if n == 0:
        return []
    return rng.sample(items, k=min(n, len(items)))


def _build_case(rng: random.Random, index: int) -> Dict[str, Any]:
    situation = rng.choice(_SITUATIONS)
    suffix = f"（case-{index:05d}）"

    case: Dict[str, Any] = {
        "situation": f"{situation}{suffix}",
    }

    constraints = _pick_some(rng, _CONSTRAINT_WORDS, 3)
    if constraints:
        case["constraints"] = constraints

    if rng.random() < 0.8:
        if rng.random() < 0.7:
            case["options"] = _OPTIONS[:]
        else:
            shuffled = _OPTIONS[:]
            rng.shuffle(shuffled)
            case["options"] = shuffled

    if rng.random() < 0.35:
        case["asker_status"] = rng.choice(_STATUS_WORDS)

    beneficiaries = _pick_some(rng, _BENEFICIARIES, 3)
    if beneficiaries:
        case["beneficiaries"] = beneficiaries

    structures = _pick_some(rng, _STRUCTURES, 3)
    if structures:
        case["affected_structures"] = structures

    return case


def generate_cases(count: int, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    return [_build_case(rng, i) for i in range(count)]


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate decision request fuzz cases")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="-")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    if args.count <= 0:
        print("error: --count must be positive", file=sys.stderr)
        return 2

    cases = generate_cases(args.count, args.seed)
    indent = 2 if args.pretty else None

    if args.out == "-":
        json.dump(cases, sys.stdout, ensure_ascii=False, indent=indent)
        if indent is not None:
            print()
        return 0

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=indent)
        if indent is not None:
            f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
