from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .safety import guard_text, scan_manipulation


def _as_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [str(v) for v in x]
    return [str(x)]


# 制約キーワード → reason code のマッピング
_SAFETY_WORD_CODES: Dict[str, str] = {
    "安全": "SAFETY_FIRST",
    "リスク": "RISK_AVOIDANCE",
    "事故": "SAFETY_FIRST",
    "法令": "COMPLIANCE_FIRST",
    "コンプラ": "COMPLIANCE_FIRST",
    "品質": "QUALITY_FIRST",
}
_SPEED_WORD_CODES: Dict[str, str] = {
    "スピード": "SPEED_FIRST",
    "期限": "DEADLINE_DRIVEN",
    "至急": "URGENCY_FIRST",
    "早く": "SPEED_FIRST",
    "納期": "DEADLINE_DRIVEN",
}

# 推奨案ごとの「落選理由コード」
# _NOT_SELECTED[推奨ID][非推奨ID] = reason_code
_NOT_SELECTED_CODES: Dict[str, Dict[str, str]] = {
    "A": {"B": "LESS_SAFE_THAN_A",      "C": "LEAST_SAFE_OPTION"},
    "B": {"A": "OVERLY_CONSERVATIVE",   "C": "OVERLY_AGGRESSIVE"},
    "C": {"A": "SLOWEST_OPTION",         "B": "LESS_FAST_THAN_C"},
}


def _choose_recommendation(constraints_text: str) -> Tuple[str, List[str], str]:
    """
    P0: 超単純なルール。
    - 安全/リスク系 → A  (reason codes: SAFETY_FIRST / RISK_AVOIDANCE / COMPLIANCE_FIRST / QUALITY_FIRST)
    - スピード/期限系 → C (reason codes: SPEED_FIRST / DEADLINE_DRIVEN / URGENCY_FIRST)
    - それ以外 → B       (reason codes: NO_CONSTRAINTS)
    """
    t = constraints_text or ""

    safety_codes = sorted({v for k, v in _SAFETY_WORD_CODES.items() if k in t})
    speed_codes = sorted({v for k, v in _SPEED_WORD_CODES.items() if k in t})

    if safety_codes:
        label = ", ".join(safety_codes)
        return "A", safety_codes, f"制約に安全/リスク系({label})があるため、A（安全側）を仮推奨。"
    if speed_codes:
        label = ", ".join(speed_codes)
        return "C", speed_codes, f"制約に期限/速度系({label})があるため、C（速度側）を仮推奨。"
    return "B", ["NO_CONSTRAINTS"], "制約が限定的なので、B（バランス）を仮推奨。"


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
        {"id": cid, "summary": options[i], "not_selected_reason_code": (
            "N/A" if rec_id == cid else _NOT_SELECTED_CODES[rec_id][cid]
        )}
        for i, cid in enumerate(["A", "B", "C"])
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
    block_hits = [h for h in hits if h.severity == "block"]
    warn_hits = [h for h in hits if h.severity == "warn"]

    if block_hits:
        return {
            "status": "blocked",
            "blocked_by": "#4 Manipulation",
            "reason": "出力に操作/扇動っぽい表現が混ざる可能性があるため停止します。",
            "detected": [h.phrase for h in block_hits],
            "safe_alternatives": [
                "表現を中立に落として再生成する（P0では手動で修正）",
                "結論を出さず、候補と比較ポイントだけ提示する",
            ],
        }

    if warn_hits:
        report["warnings"] = [
            f"注意: 出力に断定的な表現が含まれています → 「{h.phrase}」"
            for h in warn_hits
        ]

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

    warnings = report.get("warnings") or []
    if warnings:
        lines.append("")
        lines.append("[Warnings]")
        for w in warnings:
            lines.append(f"- {w}")

    return "\n".join(lines)
