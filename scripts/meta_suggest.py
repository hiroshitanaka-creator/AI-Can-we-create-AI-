"""Repository self-improvement suggester.

Reads project docs and prints top 3 actionable suggestions.
Standard library only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

DEFAULT_FILES = [
    "guideline.md",
    "progress_log.md",
    "idea_note.md",
]


def _extract_unchecked_tasks(text: str) -> List[str]:
    tasks: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ] "):
            tasks.append(stripped[6:].strip())
    return tasks


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def build_suggestions(base_dir: Path, top_k: int = 3) -> Dict[str, object]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    all_tasks: List[Dict[str, str]] = []
    for rel in DEFAULT_FILES:
        p = base_dir / rel
        content = _read_text(p)
        for task in _extract_unchecked_tasks(content):
            all_tasks.append({"source": rel, "task": task})

    # prioritize core guidance first, then ideas/progress.
    priority = {"guideline.md": 0, "idea_note.md": 1, "progress_log.md": 2}
    all_tasks.sort(key=lambda x: priority.get(x["source"], 9))

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
