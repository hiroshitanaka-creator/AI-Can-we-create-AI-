"""
scripts/three_review.py

3者レビュー（Builder / Skeptic / User）を CLI で自動実行。
guideline.md の 3-Review Rule をコードで体現する。

## 3者レビューのロール
  Builder : 「私はこの実装/決定を推進します」— 推奨案と根拠を提示
  Skeptic : 「待ってください」— 反論・不確実性・リスクを列挙
  User    : 「最終判断はあなたです」— Yes/No で答えられる形に整理

## 使い方

    # stdin から
    echo '{"situation": "新機能のリリースを検討", "constraints": ["安全優先"]}' \\
        | python scripts/three_review.py

    # ファイル指定
    python scripts/three_review.py request.json

    # Markdown アダプタとパイプ接続
    cat request.md | python scripts/md_adapter.py | python scripts/three_review.py

Exit codes:
    0 : ok（正常レビュー出力）
    1 : blocked（No-Go 検知）
    2 : 引数エラー / 不正JSON
"""
from __future__ import annotations

import json
import sys
import os
import textwrap
from typing import Any, Dict, List

# aicw をインポートパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aicw.decision import build_decision_report
from bridge.ensemble import run_ensemble


# ─────────────────────────────────────────────────────────────────────────────
# フォーマットヘルパー
# ─────────────────────────────────────────────────────────────────────────────

_WIDTH = 60


def _divider(char: str = "─") -> str:
    return char * _WIDTH


def _section(title: str, lines: List[str]) -> str:
    out = [_divider("━")]
    out.append(f"  {title}")
    out.append(_divider())
    for line in lines:
        out.append(f"  {line}")
    return "\n".join(out)


def _wrap(text: str, indent: int = 4) -> str:
    return textwrap.fill(text, width=_WIDTH - indent, initial_indent=" " * indent,
                         subsequent_indent=" " * indent)


# ─────────────────────────────────────────────────────────────────────────────
# 3者レビュー生成
# ─────────────────────────────────────────────────────────────────────────────

def build_builder_section(report: Dict[str, Any]) -> List[str]:
    """
    Builder: 実装者・推進者の視点。
    「この選択を推進する根拠はここにある」
    """
    sel = report["selection"]
    rec = sel["recommended_id"]
    explanation = sel["explanation"]
    reason_codes = sel["reason_codes"]

    # 推奨案のサマリを candidates から取得
    candidates = report.get("candidates", [])
    rec_summary = next(
        (c["summary"] for c in candidates if c["id"] == rec), "(不明)"
    )

    impact_score = report.get("existence_analysis", {}).get("impact_score", 0)

    lines: List[str] = [
        "【立場】私はこの決定を推進します。",
        "",
        f"推奨案: {rec}  —  {rec_summary}",
        "",
        "【根拠】",
    ]
    for code in reason_codes:
        lines.append(f"  ・{code}")
    lines.append("")
    lines.append("【説明】")
    for part in explanation.split("。"):
        part = part.strip()
        if part:
            lines.append(f"  {part}。")
    lines.append("")
    lines.append(f"影響スコア: {impact_score} / 8")
    return lines


def build_skeptic_section(report: Dict[str, Any]) -> List[str]:
    """
    Skeptic: 懐疑論者の視点。
    「待ってください。これらの問題を先に解決しましょう」
    """
    counterargs = report.get("counterarguments", [])
    uncertainties = report.get("uncertainties", [])
    warnings = report.get("warnings", [])
    ea = report.get("existence_analysis", {})
    distortion_risk = ea.get("distortion_risk", "low")
    impact_score = ea.get("impact_score", 0)

    lines: List[str] = [
        "【立場】待ってください。以下を確認してから進んでください。",
        "",
    ]

    if warnings:
        lines.append("【検知された警告】")
        for w in warnings:
            lines.append(f"  ⚠ {w}")
        lines.append("")

    lines.append("【反論】")
    for ca in counterargs:
        lines.append(f"  ✗ {ca}")
    lines.append("")

    lines.append("【不確実性】")
    for u in uncertainties:
        lines.append(f"  ? {u}")
    lines.append("")

    lines.append("【リスクサマリ】")
    lines.append(f"  ・歪みリスク: {distortion_risk}")
    lines.append(f"  ・影響スコア: {impact_score} / 8")
    if distortion_risk == "medium":
        lines.append("  ・⚠ 歪みリスクが中程度: 誰の私益かを明確にしてから進んでください")
    if impact_score >= 4:
        lines.append("  ・⚠ 影響スコアが高め: 段階的実施・中間評価を検討してください")
    return lines


def build_user_section(report: Dict[str, Any]) -> List[str]:
    """
    User: 最終判断者への整理。
    「あなたが決めます。Yes/No で答えられる形で整理しました」
    """
    sel = report["selection"]
    rec = sel["recommended_id"]
    nq = report.get("next_questions", [])
    impact_map = report.get("impact_map", "")
    disclaimer = report.get("disclaimer", "")
    ea = report.get("existence_analysis", {})

    lines: List[str] = [
        "【立場】最終判断はあなたです。以下を確認してください。",
        "",
        "【決断に必要な確認事項】（Yes で進める / No で保留）",
        f"  [ ] 推奨案 {rec} の実施内容を理解していますか？",
        "  [ ] 反論・不確実性を読んで、それでも進みますか？",
        "  [ ] 影響を受ける人に対して、事前に説明できますか？",
        "",
    ]

    if nq:
        lines.append("【先に答えておきたい質問】")
        for q in nq:
            lines.append(f"  → {q}")
        lines.append("")

    if impact_map and "未特定" not in impact_map:
        lines.append("【影響範囲マップ】（？を埋めてから決断することを推奨）")
        lines.append(impact_map)
        lines.append("")

    q2 = ea.get("question_2_affected_structures", [])
    q2_display = [s for s in q2 if "不明" not in s]
    if q2_display:
        lines.append(f"影響する構造: {' / '.join(q2_display)}")
    lines.append("")
    lines.append(disclaimer)
    return lines



def build_ensemble_section(report: Dict[str, Any]) -> List[str]:
    """Ensemble: 多視点の多数派/少数意見を表示。"""
    prompt = report.get("input", {}).get("situation", "")
    result = run_ensemble(prompt)
    majority = result.get("majority", {})
    minority = result.get("minority_report", [])

    lines: List[str] = [
        "【立場】複数視点で最終確認します。",
        "",
        "【多数派】",
        f"  stance : {majority.get('stance', 'hold')}",
        f"  members: {' / '.join(majority.get('members', []))}",
        "",
        "【少数意見（minority report）】",
    ]
    for m in minority:
        lines.append(f"  ・{m.get('name', 'Unknown')} [{m.get('stance', 'hold')}] {m.get('rationale', '')}")
    return lines

# ─────────────────────────────────────────────────────────────────────────────
# blocked 時の出力
# ─────────────────────────────────────────────────────────────────────────────

def format_blocked(report: Dict[str, Any]) -> str:
    lines = [
        _divider("━"),
        "  ⛔ BLOCKED — レビューを中止します",
        _divider(),
        f"  blocked_by: {report.get('blocked_by')}",
        f"  reason    : {report.get('reason')}",
        "",
        "  【安全な代替案】",
    ]
    for alt in report.get("safe_alternatives", []):
        lines.append(f"  ・{alt}")
    lines.append(_divider("━"))
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# メイン出力
# ─────────────────────────────────────────────────────────────────────────────

def format_three_review(report: Dict[str, Any]) -> str:
    situation = report.get("input", {}).get("situation", "(不明)")
    constraints = report.get("input", {}).get("constraints", [])

    header = [
        _divider("━"),
        "  ⚖  3者レビュー（Builder / Skeptic / User）",
        _divider(),
        f"  Question  : {situation}",
    ]
    if constraints:
        header.append(f"  Constraints: {' / '.join(constraints)}")
    header.append(_divider("━"))

    builder = _section("🔨 Builder（推進者）", build_builder_section(report))
    skeptic = _section("🔍 Skeptic（懐疑論者）", build_skeptic_section(report))
    user = _section("👤 User（最終判断者）", build_user_section(report))
    ensemble = _section("🧠 Ensemble（多視点レビュー）", build_ensemble_section(report))

    return "\n\n".join(["\n".join(header), builder, skeptic, user, ensemble])


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _read_input(args: List[str]) -> str:
    if not args:
        return sys.stdin.read()
    if len(args) == 1:
        try:
            with open(args[0], encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            print(f"[three_review] ファイル読み込みエラー: {e}", file=sys.stderr)
            sys.exit(2)
    print("[three_review] 引数は最大1つ（ファイルパス）です", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    raw = _read_input(sys.argv[1:])
    try:
        request = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[three_review] JSON パースエラー: {e}", file=sys.stderr)
        sys.exit(2)

    report = build_decision_report(request)

    if report.get("status") == "blocked":
        print(format_blocked(report))
        sys.exit(1)

    print(format_three_review(report))
    sys.exit(0)


if __name__ == "__main__":
    main()
