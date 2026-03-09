"""Repository self-improvement suggester.

Reads project docs and prints top 3 actionable suggestions.
Standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_FILES = [
    "guideline.md",
    "README.md",
    "progress_log.md",
    "idea_note.md",
]


_ACTION_HEADING_HINTS = (
    "current next actions",
    "next actions",
    "next steps",
    "upcoming milestones",
    "sprint plan",
    "todo",
)

_BOLD_HEADING_WITH_SUFFIX_COLON_RE = re.compile(r"^\*\*(.+?)\*\*\s*:\s*$")
_BOLD_HEADING_WITH_INNER_COLON_RE = re.compile(r"^\*\*(.+?:)\*\*\s*$")


def _is_action_heading_text(heading: str) -> bool:
    lowered = heading.lower().strip()
    return any(hint in lowered for hint in _ACTION_HEADING_HINTS)


def _classify_heading(line: str) -> Tuple[bool, bool]:
    """Return (is_heading, is_action_heading)."""
    stripped = line.strip()
    lowered = stripped.lower()

    if lowered.startswith("#"):
        heading = lowered.lstrip("#").strip()
        return True, _is_action_heading_text(heading)

    # README の "**Upcoming Milestones (2026):**" / "**Todo**:" のような見出し記法に対応
    # 太字行は「コロン付き」の場合のみ見出しとして扱い、通常の強調文を誤検知しない。
    m = _BOLD_HEADING_WITH_SUFFIX_COLON_RE.match(stripped)
    if not m:
        m = _BOLD_HEADING_WITH_INNER_COLON_RE.match(stripped)
    if m:
        heading = m.group(1).strip().rstrip(":")
        return True, _is_action_heading_text(heading)

    return False, False


def _extract_unchecked_tasks(text: str) -> List[Dict[str, object]]:
    unchecked_anywhere: List[Dict[str, object]] = []
    in_action_section = False

    for line in text.splitlines():
        stripped = line.strip()

        is_heading, is_action_heading = _classify_heading(stripped)
        if is_heading:
            in_action_section = is_action_heading
            continue

        if stripped.startswith("- [ ] "):
            unchecked_anywhere.append(
                {
                    "task": stripped[6:].strip(),
                    "is_action_scoped": in_action_section,
                }
            )

    return unchecked_anywhere


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def build_suggestions(base_dir: Path, top_k: int = 3) -> Dict[str, object]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    all_tasks: List[Dict[str, object]] = []
    for rel in DEFAULT_FILES:
        p = base_dir / rel
        content = _read_text(p)
        for item in _extract_unchecked_tasks(content):
            all_tasks.append(
                {
                    "source": rel,
                    "task": item["task"],
                    "is_action_scoped": bool(item["is_action_scoped"]),
                }
            )

    # 1) action-scoped を常に優先
    # 2) その上で source 優先度を適用
    priority = {
        "guideline.md": 0,
        "README.md": 1,
        "idea_note.md": 2,
        "progress_log.md": 3,
    }
    all_tasks.sort(
        key=lambda x: (
            0 if x["is_action_scoped"] else 1,
            priority.get(str(x["source"]), 9),
        )
    )

    picked = all_tasks[:top_k]
    suggestions = []
    for idx, item in enumerate(picked, start=1):
        suggestions.append(
            {
                "rank": idx,
                "proposal": item["task"],
                "source": item["source"],
                "rationale": "未完了タスクのため、次スプリント候補として優先。",
            }
        )

    if not suggestions:
        suggestions.append(
            {
                "rank": 1,
                "proposal": "未完了タスクが見つからないため、既存テストの回帰実行と文書同期を行う",
                "source": "system",
                "rationale": "運用品質維持のための保守タスク。",
            }
        )

    return {
        "summary": {
            "scanned_files": DEFAULT_FILES,
            "total_candidates": len(all_tasks),
            "returned": len(suggestions),
        },
        "suggestions": suggestions,
    }


def main(argv: List[str]) -> int:
    if len(argv) > 2:
        print("Usage: python scripts/meta_suggest.py [top_k]", file=sys.stderr)
        return 2

    top_k = 3
    if len(argv) == 2:
        try:
            top_k = int(argv[1])
        except ValueError:
            print("top_k must be an integer", file=sys.stderr)
            return 2

    try:
        result = build_suggestions(Path.cwd(), top_k=top_k)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
