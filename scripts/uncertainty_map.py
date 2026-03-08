#!/usr/bin/env python3
"""
Decision Brief の uncertainties から Mermaid 風テキストを生成する。

Usage:
  python scripts/uncertainty_map.py brief.json
  cat brief.json | python scripts/uncertainty_map.py

Exit codes:
  0: success
  2: invalid input / usage error
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

_USAGE = "usage: python scripts/uncertainty_map.py [brief.json] (or pipe JSON to stdin)"


def _load_brief(argv: List[str]) -> Dict[str, Any]:
    if len(argv) == 2:
        path = argv[1]
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            raise SystemExit(2)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON in {path}: {e}", file=sys.stderr)
            raise SystemExit(2)
    elif len(argv) == 1:
        try:
            data = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON from stdin: {e}", file=sys.stderr)
            raise SystemExit(2)
    else:
        print(_USAGE, file=sys.stderr)
        raise SystemExit(2)

    if not isinstance(data, dict):
        print("error: input must be a JSON object", file=sys.stderr)
        raise SystemExit(2)
    return data


def _split_children(text: str) -> List[str]:
    for sep in ["：", ":", "。", "、", ","]:
        if sep in text:
            parts = [p.strip() for p in text.split(sep) if p.strip()]
            if len(parts) > 1:
                return parts[1:3]
    return []


def build_uncertainty_map(
    brief: Dict[str, Any],
    *,
    max_nodes: int = 12,
    max_depth: int = 2,
) -> str:
    uncertainties = brief.get("uncertainties")
    if not isinstance(uncertainties, list):
        uncertainties = []

    root = "UncertaintyMap"
    lines = ["graph TD", f"  R[{root}]"]

    if not uncertainties:
        lines.append("  R --> N0[\"不確実性は未指定\"]")
        return "\n".join(lines)

    # 循環防止と重複回避（同一テキストは1ノードのみ）
    seen = set()
    node_count = 0

    for idx, raw in enumerate(uncertainties):
        if node_count >= max_nodes:
            break
        if not isinstance(raw, str):
            continue
        text = raw.strip()
        if not text or text in seen:
            continue
        seen.add(text)

        parent_id = f"U{idx}"
        lines.append(f"  R --> {parent_id}[\"{text}\"]")
        node_count += 1

        if max_depth >= 2 and node_count < max_nodes:
            for j, child in enumerate(_split_children(text)):
                if node_count >= max_nodes:
                    break
                if child in seen:
                    continue
                seen.add(child)
                child_id = f"U{idx}_{j}"
                lines.append(f"  {parent_id} --> {child_id}[\"{child}\"]")
                node_count += 1

    if node_count == 0:
        lines.append("  R --> N0[\"不確実性は未指定\"]")

    return "\n".join(lines)


def main() -> None:
    brief = _load_brief(sys.argv)
    print(build_uncertainty_map(brief))


if __name__ == "__main__":
    main()
