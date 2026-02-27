#!/usr/bin/env python3
"""
Decision Request JSON バリデータ

バリデーションロジックは aicw/schema.py に集約。
このスクリプトは CLI ラッパーのみ。

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
from typing import Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aicw.schema import validate_request

_USAGE = "usage: python scripts/validate_request.py [request.json]  (or pipe JSON to stdin)"


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
    errors = validate_request(data)
    if errors:
        print("INVALID:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("OK: request JSON は有効です。")


if __name__ == "__main__":
    main()
