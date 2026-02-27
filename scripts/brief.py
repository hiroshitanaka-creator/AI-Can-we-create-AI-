#!/usr/bin/env python3
"""
Decision Brief CLI (P0)

Usage:
  # ファイル指定
  python scripts/brief.py request.json

  # stdin（パイプ）
  echo '{"situation":"...","constraints":[],"options":[]}' | python scripts/brief.py

Output:
  Markdown 形式の Decision Brief を stdout に出力。
  blocked 時は BLOCKED メッセージを stdout に出力し、exit code 1 で終了。

Input JSON format:
  {
    "situation":   "何を決めたいか（必須）",
    "constraints": ["制約1", "制約2"],   // 任意
    "options":     ["候補A", "候補B", "候補C"]  // 任意
  }
"""

from __future__ import annotations

import json
import sys

# プロジェクトルートを sys.path に追加（スクリプト単体実行対応）
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aicw import build_decision_report, format_report

_USAGE = "usage: python scripts/brief.py [request.json]  (or pipe JSON to stdin)"


def _load_request() -> dict:
    if len(sys.argv) == 2:
        path = sys.argv[1]
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON in {path}: {e}", file=sys.stderr)
            sys.exit(2)
    elif len(sys.argv) == 1:
        raw = sys.stdin.read()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        print(_USAGE, file=sys.stderr)
        sys.exit(2)


def main() -> None:
    req = _load_request()
    report = build_decision_report(req)
    output = format_report(report)
    print(output)
    if report.get("status") != "ok":
        sys.exit(1)


if __name__ == "__main__":
    main()
