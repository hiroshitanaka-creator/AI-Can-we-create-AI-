#!/usr/bin/env python3
"""
Ensemble Review CLI

Usage:
  python scripts/ensemble_review.py request.json
  echo '{"situation":"..."}' | python scripts/ensemble_review.py

Exit codes:
  0: ok
  1: blocked
  2: invalid args/json
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aicw.decision import build_decision_report
from bridge.ensemble import run_ensemble


def _read_input(args: List[str]) -> str:
    if not args:
        return sys.stdin.read()
    if len(args) == 1:
        try:
            with open(args[0], encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            print(f"[ensemble_review] file read error: {e}", file=sys.stderr)
            sys.exit(2)
    print("[ensemble_review] accepts at most one file path", file=sys.stderr)
    sys.exit(2)


def _format_blocked(report: Dict[str, Any]) -> str:
    lines = [
        "⛔ BLOCKED",
        f"blocked_by: {report.get('blocked_by')}",
        f"reason    : {report.get('reason')}",
        "",
        "safe_alternatives:",
    ]
    for alt in report.get("safe_alternatives", []):
        lines.append(f"- {alt}")
    return "\n".join(lines)


def _format_ensemble(report: Dict[str, Any], ensemble: Dict[str, Any]) -> str:
    majority = ensemble.get("majority", {})
    minority = ensemble.get("minority_report", [])
    opinions = ensemble.get("opinions", [])

    lines = [
        "# Ensemble Review",
        f"Question: {report.get('input', {}).get('situation', '(unknown)')}",
        "",
        "## Majority",
        f"- stance: {majority.get('stance', 'hold')}",
        f"- members: {' / '.join(majority.get('members', []))}",
        "",
        "## Minority Report",
    ]
    for m in minority:
        lines.append(
            f"- {m.get('name', 'Unknown')} [{m.get('stance', 'hold')}]: {m.get('rationale', '')}"
        )

    lines.append("")
    lines.append("## All Opinions")
    for op in opinions:
        lines.append(
            f"- {op.get('name', 'Unknown')} [{op.get('stance', 'hold')}]: {op.get('rationale', '')}"
        )
    return "\n".join(lines)


def main() -> None:
    raw = _read_input(sys.argv[1:])
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ensemble_review] invalid json: {e}", file=sys.stderr)
        sys.exit(2)

    report = build_decision_report(req)
    if report.get("status") == "blocked":
        print(_format_blocked(report))
        sys.exit(1)

    prompt = report.get("input", {}).get("situation", "")
    result = run_ensemble(prompt)
    print(_format_ensemble(report, result))
    sys.exit(0)


if __name__ == "__main__":
    main()
