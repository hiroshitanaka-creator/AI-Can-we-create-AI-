#!/usr/bin/env python3
"""
Decision Request JSON バリデータ

Usage:
  python scripts/validate_request.py request.json
  echo '{"situation":"..."}' | python scripts/validate_request.py

Exit codes:
  0: valid（エラーなし）
  1: validation errors found（項目名ミス・型ミスなど）
  2: invalid JSON / file not found / 引数エラー
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_USAGE = "usage: python scripts/validate_request.py [request.json]  (or pipe JSON to stdin)"

REQUIRED_FIELDS = {"situation"}
ALLOWED_FIELDS = {"situation", "constraints", "options", "asker_status"}

# タイポしやすいフィールド名のヒント
_TYPO_HINTS: Dict[str, str] = {
    "constrint":   "constraints",
    "contraint":   "constraints",
    "constrains":  "constraints",
    "constrants":  "constraints",
    "option":      "options",
    "optins":      "options",
    "situaton":    "situation",
    "sitiation":   "situation",
}


def validate(data: Any) -> List[str]:
    errors: List[str] = []

    if not isinstance(data, dict):
        return ["トップレベルはオブジェクト（{}）である必要があります"]

    # 必須フィールド
    for f in sorted(REQUIRED_FIELDS):
        if f not in data:
            errors.append(f"必須フィールドが不足: '{f}'")

    # 型チェック
    if "situation" in data and not isinstance(data["situation"], str):
        errors.append(f"'situation' は文字列型が必要です（現在: {type(data['situation']).__name__}）")
    if "constraints" in data and not isinstance(data["constraints"], list):
        errors.append(f"'constraints' はリスト型が必要です（現在: {type(data['constraints']).__name__}）")
    if "options" in data and not isinstance(data["options"], list):
        errors.append(f"'options' はリスト型が必要です（現在: {type(data['options']).__name__}）")

    # 不明フィールド（タイポ検出）
    unknown = set(data.keys()) - ALLOWED_FIELDS
    for u in sorted(unknown):
        hint = _TYPO_HINTS.get(u)
        if hint:
            errors.append(f"不明なフィールド: '{u}' → もしかして '{hint}' ?")
        else:
            errors.append(f"不明なフィールド: '{u}'（使用可能: {sorted(ALLOWED_FIELDS)}）")

    return errors


def _load(argv: List[str]) -> Any:
    if len(argv) == 2:
        path = argv[1]
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON in {path}: {e}", file=sys.stderr)
            sys.exit(2)
    elif len(argv) == 1:
        try:
            return json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        print(_USAGE, file=sys.stderr)
        sys.exit(2)


def main() -> None:
    data = _load(sys.argv)
    errors = validate(data)
    if errors:
        print("INVALID:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("OK: request JSON は有効です。")


if __name__ == "__main__":
    main()
