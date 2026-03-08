#!/usr/bin/env python3
"""
同一入力に対する Decision Brief の一貫性チェック。

Usage:
  python scripts/check_consistency.py request.json --repeat 100
  cat request.json | python scripts/check_consistency.py --repeat 100

Exit codes:
  0: 一貫（全ハッシュ一致）
  1: 非一貫（差分あり）
  2: 入力エラー
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aicw import build_decision_report


def _canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_report(report: Dict[str, Any]) -> str:
    payload = _canonical_json(report).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _top_level_diff_keys(a: Dict[str, Any], b: Dict[str, Any]) -> List[str]:
    keys = sorted(set(a.keys()) | set(b.keys()))
    return [k for k in keys if a.get(k) != b.get(k)]


def check_consistency(request: Dict[str, Any], repeat: int) -> Tuple[bool, str, List[str]]:
    if repeat <= 0:
        raise ValueError("repeat must be positive")

    baseline = build_decision_report(request)
    baseline_hash = _hash_report(baseline)

    for _ in range(repeat - 1):
        current = build_decision_report(request)
        current_hash = _hash_report(current)
        if current_hash != baseline_hash:
            return False, baseline_hash, _top_level_diff_keys(baseline, current)

    return True, baseline_hash, []


def _load_request(path: str | None) -> Dict[str, Any]:
    try:
        if path:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return json.loads(sys.stdin.read())
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        raise SystemExit(2)


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check decision report consistency")
    parser.add_argument("request", nargs="?", default=None)
    parser.add_argument("--repeat", type=int, default=100)
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    request = _load_request(args.request)

    try:
        ok, report_hash, diff_keys = check_consistency(request, args.repeat)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if ok:
        print(f"CONSISTENT: hash={report_hash} repeat={args.repeat}")
        return 0

    print("INCONSISTENT: output changed across runs")
    print(f"baseline_hash={report_hash}")
    print("diff_keys=" + ",".join(diff_keys))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
