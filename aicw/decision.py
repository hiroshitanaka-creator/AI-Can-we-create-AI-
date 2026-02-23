from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .safety import guard_text, scan_manipulation


def _as_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [str(v) for v in x]
    return [str(x)]


def _choose_recommendation(constraints_text: str) -> Tuple[str, List[str], str]:
    """
    P0: 超単純なルール。
    - 安全/リスク系 → A
    - スピード/期限系 → C
    - それ以外 → B
    """
    t = constraints_text or ""

    safety_words = ["安全", "リスク", "事故", "法令", "コンプラ", "品質"]
    speed_words = ["スピード", "期限", "至急", "早く", "納期"]

    if any(w in t for w in safety_words):
        return "A", ["SAFETY_FIRST"], "制約に安全/リスク系があるため、A（安全側）を仮推奨。"
    if any(w in t for w in speed_words):
        return "C", ["SPEED_FIRST"], "制約に期限/速度系があるため、C（速度側）を仮推奨。"
    return "B", ["DEFAULT_BALANCED"], "制約が限定的なので、B（バランス）を仮推奨。"


def build_decision_report(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    P0: オフライン・非公開用の最小意思決定支援。
    - #6: 機密っぽい入力があれば停止して代替案を返す
    - #3: 肩書・地位は入力にあっても結論に使わない
    - #4: 出力に操作表現が混ざれば縮退（停止）する
    """
    situation = str(request.get("situation", "")).strip()
    constraints = _as_list(request.get("constraints"))
    options_in = _as_list(request.get("options"))

    # P0は候補が足りないとき、固定の3案を補う（Explainable selectionの形だけ作る）
    defaults = ["A: 安全側（失敗を減らす）", "B: バランス（中庸）", "C: 速度側（進行を優先）"]
    options: List[str] = []
    for i in range(3):
        if i < len(options_in) and options_in[i].strip():
            options.append(options_in[i].strip())
        else:
            options.append(defaults[i])

    # --- No-Go #6: privacy guard ---
    blob = "\n".join([situation] + constraints + options)
    allowed, redacted_blob, findings = guard_text(blob)
    if not allowed:
        detected = sorted({f.kind for f in findings})
        return {
            "status": "blocked",
            "blocked_by": "#6 Privacy",
            "reason": "入力に個人情報/機密っぽい文字列が含まれています。いったん停止します。",
            "detected": detected,
            "safe_alternatives": [
                "実名・連絡先・住所・IDなどを削除して『顧客A』『A社』のように置き換える",
                "秘密っぽい長い文字列は削除して、必要なら別管理（このツールに入れない）",
            ],
            "redacted_preview": redacted_blob,
        }

    # --- build report (status-invariant) ---
    constraints_text = " / ".join(constraints)
    rec_id, reason_codes, explanation = _choose_recommendation(constraints_text)

    candidates = [
        {"id": "A", "summary": options[0], "not_selected_reason_code": "N/A" if rec_id == "A" else "NOT_RECOMMENDED_P0"},
        {"id": "B", "summary": options[1], "not_selected_reason_code": "N/A" if rec_id == "B" else "NOT_RECOMMENDED_P0"},
        {"id": "C", "summary": options[2], "not_selected_reason_code": "N/A" if rec_id == "C" else "NOT_RECOMMENDED_P0"},
    ]

    report: Dict[str, Any] = {
        "status": "ok",
        "meta": {
            "version": "p0",
            "no_go": ["#6", "#3", "#4"],
            "offline_first": True,
        },
        "input": {
            # 肩書/地位は保持しない（#3対策の最小）
            "situation": situation,
            "constraints": constraints,
        },
        "candidates": candidates,
        "selection": {
            "recommended_id": rec_id,
            "reason_codes": reason_codes,
            "explanation": explanation,
        },
        "counterarguments": [
            "前提が足りない可能性がある（不足情報があるなら保留も選択肢）。",
            "短期の最適化が外部性を増やす可能性がある（影響者を確認）。",
        ],
        "uncertainties": [
            "成功の定義（何が達成できれば勝ちか）が未確定の可能性。",
            "失敗した場合の被害（誰に何が起きるか）が未確定の可能性。",
        ],
        "externalities": [
            "関係者の時間コスト",
            "品質/安全への影響",
            "（必要なら）環境負荷（計算量/端末負荷）",
        ],
        "next_questions": [
            "成功の定義は？（数字で言える？）",
            "失敗した時、最悪どこまで起きる？",
            "影響を受ける人は誰？（チーム外も含む）",
        ],
    }

    # --- No-Go #4: anti-manipulation guard (output) ---
    rendered = format_report(report)
    hits = scan_manipulation(rendered)
    if hits:
        return {
            "status": "blocked",
            "blocked_by": "#4 Manipulation",
            "reason": "出力に操作/扇動っぽい表現が混ざる可能性があるため停止します。",
            "detected": hits,
            "safe_alternatives": [
                "表現を中立に落として再生成する（P0では手動で修正）",
                "結論を出さず、候補と比較ポイントだけ提示する",
            ],
        }

    return report


def format_report(report: Dict[str, Any]) -> str:
    """
    人が読める形（P0）。
    """
    if report.get("status") != "ok":
        lines = []
        lines.append("=== BLOCKED ===")
        lines.append(f"blocked_by: {report.get('blocked_by')}")
        lines.append(f"reason: {report.get('reason')}")
        detected = report.get("detected")
        if detected:
            lines.append(f"detected: {detected}")
        preview = report.get("redacted_preview")
        if preview:
            lines.append("redacted_preview:")
            lines.append(preview)
        alts = report.get("safe_alternatives") or []
        if alts:
            lines.append("safe_alternatives:")
            for a in alts:
                lines.append(f"- {a}")
        return "\n".join(lines)

    lines = []
    lines.append("=== Decision Support (P0) ===")
    lines.append("")
    lines.append("[Input]")
    lines.append(f"- situation: {report['input']['situation']}")
    if report["input"]["constraints"]:
        lines.append(f"- constraints: {' / '.join(report['input']['constraints'])}")
    else:
        lines.append("- constraints: (none)")
    lines.append("")
    lines.append("[Candidates]")
    for c in report["candidates"]:
        lines.append(f"- {c['id']}: {c['summary']}")
    lines.append("")
    sel = report["selection"]
    lines.append("[Selection]")
    lines.append(f"- recommended: {sel['recommended_id']}")
    lines.append(f"- reason_codes: {sel['reason_codes']}")
    lines.append(f"- explanation: {sel['explanation']}")
    lines.append("")
    lines.append("[Counterarguments]")
    for x in report["counterarguments"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("[Uncertainties]")
    for x in report["uncertainties"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("[Externalities]")
    for x in report["externalities"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("[Next Questions]")
    for x in report["next_questions"]:
        lines.append(f"- {x}")

    return "\n".join(lines)
