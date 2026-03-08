#!/usr/bin/env python3
"""
Decision Brief から事後検証テンプレートを生成する。

Usage:
  python scripts/postmortem_template.py brief.json
  cat brief.json | python scripts/postmortem_template.py

Exit codes:
  0: success
  2: invalid input / usage error
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

_USAGE = "usage: python scripts/postmortem_template.py [brief.json] (or pipe JSON to stdin)"


def _load_input(argv: List[str]) -> Dict[str, Any]:
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


def build_postmortem_template(brief: Dict[str, Any]) -> str:
    status = brief.get("status")

    lines: List[str] = ["# Postmortem Template", ""]

    if status == "blocked":
        blocked_by = brief.get("blocked_by", "unknown")
        reason = brief.get("reason", "(no reason)")
        lines.extend([
            "## BLOCKED Case",
            f"- blocked_by: {blocked_by}",
            f"- reason: {reason}",
            "",
            "## Follow-up Checklist",
            "- [ ] unsafe request を安全な言い換えに変換したか",
            "- [ ] safe_alternatives を再検討したか",
            "- [ ] No-Go 該当箇所をチームで共有したか",
        ])
        return "\n".join(lines)

    if status != "ok":
        lines.extend([
            "## Invalid input",
            "- status が `ok` または `blocked` の Decision Brief を入力してください。",
        ])
        return "\n".join(lines)

    selection = brief.get("selection", {})
    recommended_id = selection.get("recommended_id", "N/A")
    explanation = selection.get("explanation", "")
    next_questions = brief.get("next_questions", [])

    if not isinstance(next_questions, list):
        next_questions = []

    def _pick(idx: int, fallback: str) -> str:
        if idx < len(next_questions) and isinstance(next_questions[idx], str):
            return next_questions[idx]
        return fallback

    lines.extend([
        "## Decision Snapshot",
        f"- recommended_id: {recommended_id}",
        f"- rationale: {explanation}",
        "",
        "## 30-day checks",
        f"- [ ] 初期KPIの変化を確認: {_pick(0, '期待した効果は出ているか')}",
        f"- [ ] 想定外の副作用を確認: {_pick(1, '副作用は誰に出ているか')}",
        "",
        "## 60-day checks",
        f"- [ ] 継続可否の判断材料を更新: {_pick(2, '前提条件は変化したか')}",
        f"- [ ] 代替案比較を再評価: {_pick(3, '代替案との比較で優位性は維持されるか')}",
        "",
        "## 90-day checks",
        f"- [ ] 長期影響の棚卸し: {_pick(4, '影響を受ける構造への歪みはないか')}",
        f"- [ ] 次の意思決定へ接続: {_pick(5, '次に検証すべき問いは何か')}",
    ])

    return "\n".join(lines)


def main() -> None:
    brief = _load_input(sys.argv)
    print(build_postmortem_template(brief))


if __name__ == "__main__":
    main()
