from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .safety import guard_text, scan_manipulation


# ---------------------------------------------------------------------------
# 生存構造倫理原則（Existence Ethics Principle）
# ---------------------------------------------------------------------------
# 生存構造の5層キーワード
_EXISTENCE_STRUCTURE_KEYWORDS: Dict[str, List[str]] = {
    "個人": ["個人", "本人", "自分", "プライバシー", "尊厳", "健康", "私", "当事者"],
    "関係": ["家族", "コミュニティ", "信頼", "チーム", "組織", "同僚", "顧客", "パートナー", "関係者"],
    "社会": ["社会", "制度", "公平", "多様性", "民主", "法律", "規制", "市場", "業界"],
    "認知": ["自律", "判断", "思考", "意思決定", "自由", "考え", "選択"],
    "生態": ["環境", "自然", "持続可能", "生態", "エネルギー", "資源"],
}

# 私益による破壊を示すキーワード
_DESTRUCTION_KEYWORDS: List[str] = [
    "破壊", "潰す", "排除", "独占", "支配", "奪う", "封じる", "妨害", "阻止",
    "蹴落とす", "つぶす", "妨げる",
]

# 自然なライフサイクルを示すキーワード
_LIFECYCLE_KEYWORDS: List[str] = [
    "終了", "撤退", "引退", "完了", "終焉", "移行", "交代", "更新", "卒業",
    "閉鎖", "廃止", "リプレイス", "世代交代",
]


def _analyze_existence(
    situation: str,
    constraints: List[str],
    options: List[str],
    beneficiaries_in: List[str],
    affected_structures_in: List[str],
) -> Dict[str, Any]:
    """
    生存構造倫理原則に基づく3問分析。
    Q1: 受益者は誰か？
    Q2: 影響を受ける構造は何か？
    Q3: それは自然な循環か、私益による破壊か？
    """
    all_text = " ".join([situation] + constraints + options)

    # Q1: 受益者
    beneficiaries: List[str] = beneficiaries_in if beneficiaries_in else [
        "不明（入力に beneficiaries を追加すると精度が上がります）"
    ]

    # Q2: 影響を受ける生存構造
    if affected_structures_in:
        detected_structures = affected_structures_in
    else:
        detected_structures = [
            layer for layer, keywords in _EXISTENCE_STRUCTURE_KEYWORDS.items()
            if any(kw in all_text for kw in keywords)
        ]
        if not detected_structures:
            detected_structures = ["不明（入力に affected_structures を追加すると精度が上がります）"]

    # Q3: 自然な循環か、私益による破壊か
    has_destruction = any(kw in all_text for kw in _DESTRUCTION_KEYWORDS)
    has_lifecycle = any(kw in all_text for kw in _LIFECYCLE_KEYWORDS)

    if has_destruction and not has_lifecycle:
        judgment = "self_interested_destruction"
        distortion_risk = "high"
        judgment_text = "私益による破壊の可能性を検知。受益者・影響構造を確認し、代替案を検討してください。"
    elif has_lifecycle and not has_destruction:
        judgment = "lifecycle"
        distortion_risk = "low"
        judgment_text = "自然なライフサイクルの範囲内と判断。生命の循環として歪みは低いと評価。"
    elif has_destruction and has_lifecycle:
        judgment = "unclear"
        distortion_risk = "medium"
        judgment_text = "ライフサイクルと破壊の両方を検知。文脈で「誰の私益か」を確認してください。"
    else:
        judgment = "unclear"
        distortion_risk = "low"
        judgment_text = "明確な破壊・循環パターンは未検知。歪みのリスクは現時点で低いと評価。"

    return {
        "question_1_beneficiaries": beneficiaries,
        "question_2_affected_structures": detected_structures,
        "question_3_judgment": judgment,
        "distortion_risk": distortion_risk,
        "judgment_text": judgment_text,
    }


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
    - #5: 私益による生存構造の破壊を検知したら停止する
    - #3: 肩書・地位は入力にあっても結論に使わない
    - #4: 出力に操作表現が混ざれば縮退（停止）する
    """
    situation = str(request.get("situation", "")).strip()
    constraints = _as_list(request.get("constraints"))
    options_in = _as_list(request.get("options"))
    beneficiaries_in = _as_list(request.get("beneficiaries"))
    affected_structures_in = _as_list(request.get("affected_structures"))

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
    block_dlp = [f for f in findings if f.severity == "block"]
    warn_dlp = [f for f in findings if f.severity == "warn"]

    if not allowed:
        detected = sorted({f.kind for f in block_dlp})
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

    # --- No-Go #5: existence ethics guard ---
    # existence_analysis を早期に計算し、私益による破壊を止める
    existence_analysis = _analyze_existence(
        situation, constraints, options,
        beneficiaries_in, affected_structures_in,
    )
    if existence_analysis["question_3_judgment"] == "self_interested_destruction":
        all_text = " ".join([situation] + constraints + options)
        detected_kws = [kw for kw in _DESTRUCTION_KEYWORDS if kw in all_text]
        return {
            "status": "blocked",
            "blocked_by": "#5 Existence Ethics",
            "reason": "入力に私益による生存構造の破壊が検知されました。いったん停止します。",
            "detected": detected_kws,
            "safe_alternatives": [
                "受益者と影響を受ける構造を明示して選択肢を再構成する",
                "「誰が損するか」「それは自然な循環か」を明示的に確認する",
                "ライフサイクル的な変化として再フレーミングできるか検討する",
            ],
        }

    # --- build report ---
    constraints_text = " / ".join(constraints)
    rec_id, reason_codes, explanation = _choose_recommendation(constraints_text)

    # A: existence_analysis の結果を selection に接続
    existence_judgment = existence_analysis["question_3_judgment"]
    existence_risk = existence_analysis["distortion_risk"]
    if existence_risk == "medium":
        explanation += " 生存構造への歪みリスク: 中（文脈確認を推奨）。"
        reason_codes = reason_codes + ["EXISTENCE_RISK_MEDIUM"]
    elif existence_judgment == "lifecycle":
        explanation += " 生存構造: 自然なライフサイクルの範囲内と判定。歪みリスク: 低。"
        reason_codes = reason_codes + ["EXISTENCE_LIFECYCLE_OK"]
    else:
        # unclear + low（最多ケース）
        explanation += " 生存構造への歪みリスク: 低（明確な破壊パターン未検知）。"
        reason_codes = reason_codes + ["EXISTENCE_RISK_LOW"]

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
            "no_go": ["#6", "#5", "#3", "#4"],
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
        "existence_analysis": existence_analysis,
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

    # DLP warn + manipulation warn をまとめて warnings フィールドに追加
    all_warnings: List[str] = []
    for f in warn_dlp:
        all_warnings.append(f"DLP注意[{f.kind}]: {f.message}")
    for h in warn_hits:
        all_warnings.append(f"注意: 出力に断定的な表現が含まれています → 「{h.phrase}」")
    if all_warnings:
        report["warnings"] = all_warnings

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

    ea = report.get("existence_analysis")
    if ea:
        lines.append("")
        lines.append("[Existence Analysis]")
        lines.append(f"- Q1 受益者: {', '.join(ea.get('question_1_beneficiaries', []))}")
        lines.append(f"- Q2 影響構造: {', '.join(ea.get('question_2_affected_structures', []))}")
        lines.append(f"- Q3 判定: {ea.get('question_3_judgment')} / 歪みリスク: {ea.get('distortion_risk')}")
        lines.append(f"- 説明: {ea.get('judgment_text')}")

    warnings = report.get("warnings") or []
    if warnings:
        lines.append("")
        lines.append("[Warnings]")
        for w in warnings:
            lines.append(f"- {w}")

    return "\n".join(lines)
