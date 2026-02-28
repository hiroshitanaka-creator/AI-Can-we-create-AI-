from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .safety import guard_text, scan_manipulation


# ---------------------------------------------------------------------------
# 生存構造倫理原則（Existence Ethics Principle）
# ---------------------------------------------------------------------------
# 生存構造の5層キーワード（P2b: 拡充済み）
_EXISTENCE_STRUCTURE_KEYWORDS: Dict[str, List[str]] = {
    "個人": [
        "個人", "本人", "自分", "プライバシー", "尊厳", "健康", "私", "当事者",
        "生活", "権利", "自己", "身体", "人権", "感情",
    ],
    "関係": [
        "家族", "コミュニティ", "信頼", "チーム", "組織", "同僚", "顧客", "パートナー", "関係者",
        "友人", "仲間", "ユーザー", "クライアント", "メンバー", "ステークホルダー", "住民",
    ],
    "社会": [
        "社会", "制度", "公平", "多様性", "民主", "法律", "規制", "市場", "業界",
        "雇用", "労働", "文化", "教育", "公共", "インフラ", "経済",
    ],
    "認知": [
        "自律", "判断", "思考", "意思決定", "自由", "考え", "選択",
        "知識", "学習", "記憶", "情報", "表現",
    ],
    "生態": [
        "環境", "自然", "持続可能", "生態", "エネルギー", "資源",
        "生命", "水", "土地", "気候", "廃棄", "循環",
    ],
}

# P2a/P2c: 破壊キーワードを2層に分割
# HARD: 文脈によらず常に私益的破壊を示す
_HARD_DESTRUCTION_KEYWORDS: List[str] = [
    "破壊", "潰す", "つぶす", "蹴落とす", "独占", "支配", "奪う", "壊滅", "抹消", "消滅", "制圧",
    "排斥", "乗っ取る", "踏みにじる",
]

# SOFT: 単体では合法・正当なユースケースもある
#   → _SAFE_TARGET_KEYWORDS と共存するテキストでは破壊と見なさない
_SOFT_DESTRUCTION_KEYWORDS: List[str] = [
    "排除", "封じる", "妨害", "阻止", "妨げる",
    "締め出す", "封殺", "黙らせる", "抑え込む",
]

# SAFE_TARGET: SOFT キーワードと組み合わせても問題ない対象語（リスク除去・事故防止など）
_SAFE_TARGET_KEYWORDS: List[str] = [
    "リスク", "課題", "問題", "バグ", "エラー", "事故", "被害", "災害",
    "漏洩", "違反", "不正", "欠陥", "障害", "ミス", "失敗",
    "脅威", "感染", "ノイズ", "アラート",
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

    # Q3: 自然な循環か、私益による破壊か（P2a: 2層判定）
    # HARD: 文脈不問で破壊
    has_hard_destruction = any(kw in all_text for kw in _HARD_DESTRUCTION_KEYWORDS)
    # SOFT: 安全対象語が同テキストに存在する場合は除外
    has_safe_target = any(kw in all_text for kw in _SAFE_TARGET_KEYWORDS)
    has_soft_destruction = (
        any(kw in all_text for kw in _SOFT_DESTRUCTION_KEYWORDS)
        and not has_safe_target
    )
    has_destruction = has_hard_destruction or has_soft_destruction
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

    # P3: 影響スコア（0-8）
    # 検出された構造層数 + リスクボーナス
    structure_count = len([s for s in detected_structures if "不明" not in s])
    risk_bonus = {"low": 0, "medium": 3, "high": 5}.get(distortion_risk, 0)
    impact_score = min(structure_count + risk_bonus, 8)

    return {
        "question_1_beneficiaries": beneficiaries,
        "question_2_affected_structures": detected_structures,
        "question_3_judgment": judgment,
        "distortion_risk": distortion_risk,
        "judgment_text": judgment_text,
        "impact_score": impact_score,
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


# ---------------------------------------------------------------------------
# B: 破壊キーワードごとの再フレーミング提案
# ---------------------------------------------------------------------------
_DESTRUCTION_ALTERNATIVES: Dict[str, str] = {
    # HARD keywords
    "破壊":   "「刷新・再構築」として、現状の何を変えたいかを再整理できますか？",
    "潰す":   "「競争」ではなく「差別化・住み分け」として再設計できますか？",
    "つぶす": "「競争」ではなく「差別化・住み分け」として再設計できますか？",
    "蹴落とす": "「自社の強みを伸ばす」視点から選択肢を再構成できますか？",
    "独占":   "マルチステークホルダー構造（分散・共存）を検討しましたか？",
    "支配":   "「共存・協業・リードする」として再フレーミングできますか？",
    "奪う":   "「獲得・誘致・提供価値で選ばれる」として再構成できますか？",
    "壊滅":   "「市場縮小リスクの軽減策」として目標を再定義できますか？",
    "抹消":   "「フェードアウト・段階的終了」など穏やかな移行案はありますか？",
    "消滅":   "「フェードアウト・段階的終了」など穏やかな移行案はありますか？",
    "制圧":   "「秩序の維持・合意形成」として手段を再選択できますか？",
    "排斥":   "「条件付き参加・段階的移行」など包摂的な代替案はありますか？",
    "乗っ取る": "「買収・提携・共同運営」など合意ベースの手段はありますか？",
    "踏みにじる": "影響を受ける側の権利・尊厳を守る手段を最初に設計できますか？",
    # SOFT keywords
    "排除":   "「条件の明示・移行支援」を先行させた上で再検討できますか？",
    "封じる": "「ルール化・ガイドライン整備」として代替手段を設計できますか？",
    "妨害":   "「相手の行動より自社の提供価値向上」に焦点を移せますか？",
    "阻止":   "「予防策・早期警告・代替経路」として再構成できますか？",
    "妨げる": "「相手の行動より自社の提供価値向上」に焦点を移せますか？",
    "締め出す": "「参加条件の明示化・オープンプロセス」として再設計できますか？",
    "封殺":   "「議論の場・フィードバック経路の整備」として代替手段はありますか？",
    "黙らせる": "「傾聴→問題の本質把握→解決策設計」のプロセスを踏めますか？",
    "抑え込む": "「透明なルール・相互合意による制約設計」に切り替えられますか？",
}

_EXISTENCE_ALTERNATIVES_STANDARD: List[str] = [
    "受益者と影響を受ける構造を明示して選択肢を再構成する",
    "「誰が損するか」「それは自然な循環か」を明示的に確認する",
    "ライフサイクル的な変化として再フレーミングできるか検討する",
]


def _build_existence_alternatives(detected_kws: List[str]) -> List[str]:
    """
    No-Go #5 blocked 時の safe_alternatives を、検出キーワードに応じて具体化する。
    先頭 1-2 件はキーワード固有の再フレーミング提案、残りは標準 3 案。
    """
    specific: List[str] = []
    for kw in detected_kws[:2]:
        alt = _DESTRUCTION_ALTERNATIVES.get(kw)
        if alt:
            entry = f"「{kw}」→ {alt}"
            if entry not in specific:
                specific.append(entry)

    result: List[str] = specific[:]
    for s in _EXISTENCE_ALTERNATIVES_STANDARD:
        if s not in result:
            result.append(s)
    return result


def _build_next_questions(
    existence_analysis: Dict[str, Any],
    constraints: List[str],
) -> List[str]:
    """
    existence_analysis の内容に応じてコンテキスト依存の次の質問を生成する。
    最大 6 件を返す。
    """
    questions: List[str] = [
        "成功の定義は？（数字で言える？）",
        "失敗した時、最悪どこまで起きる？",
    ]

    beneficiaries = existence_analysis.get("question_1_beneficiaries", [])
    structures = existence_analysis.get("question_2_affected_structures", [])
    judgment = existence_analysis.get("question_3_judgment", "unclear")
    distortion_risk = existence_analysis.get("distortion_risk", "low")
    impact_score = existence_analysis.get("impact_score", 0)

    beneficiaries_unknown = any("不明" in b for b in beneficiaries)
    structures_unknown = any("不明" in s for s in structures)

    if beneficiaries_unknown:
        questions.append("受益者は誰か、具体的に名前や役割で挙げられますか？")

    if structures_unknown:
        questions.append("影響を受ける構造（個人/関係/社会/認知/生態）を一つでも挙げられますか？")
    else:
        questions.append("影響を受ける人は誰？（チーム外も含む）")

    if distortion_risk == "medium":
        questions.append("「誰の私益か」「誰が損するか」を一文で整理できますか？")
    elif judgment == "lifecycle":
        questions.append("移行・終了で影響を受ける人への支援計画はありますか？")
    elif impact_score >= 4:
        questions.append("影響を受ける構造への緩和策・代替手段は検討しましたか？")

    if not constraints:
        questions.append("制約（安全/法令/品質/期限）を一つ明示できますか？")

    return questions[:6]


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
    # ※ options_in（ユーザー提供分のみ）を渡す。デフォルト補完後の options には
    #   "失敗を減らす" 等のシステム語が含まれ SAFE_TARGET 判定が汚染されるため。
    existence_analysis = _analyze_existence(
        situation, constraints, options_in,
        beneficiaries_in, affected_structures_in,
    )
    if existence_analysis["question_3_judgment"] == "self_interested_destruction":
        all_text = " ".join([situation] + constraints + options)
        detected_kws = (
            [kw for kw in _HARD_DESTRUCTION_KEYWORDS if kw in all_text]
            + [kw for kw in _SOFT_DESTRUCTION_KEYWORDS if kw in all_text]
        )
        return {
            "status": "blocked",
            "blocked_by": "#5 Existence Ethics",
            "reason": "入力に私益による生存構造の破壊が検知されました。いったん停止します。",
            "detected": detected_kws,
            "safe_alternatives": _build_existence_alternatives(detected_kws),
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

    # P3: 影響スコアが高い場合は推奨を A（安全側）に引き上げ
    impact_score = existence_analysis.get("impact_score", 0)
    if impact_score >= 6 and rec_id != "A":
        rec_id = "A"
        explanation += f" 影響スコア({impact_score}): 生存構造への影響が複数層に渡るため A（安全側）に引き上げ。"
        reason_codes = reason_codes + ["EXISTENCE_IMPACT_OVERRIDE"]

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
        "next_questions": _build_next_questions(existence_analysis, constraints),
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
        lines.append(f"- 影響スコア: {ea.get('impact_score', 0)} / 8")
        lines.append(f"- 説明: {ea.get('judgment_text')}")

    warnings = report.get("warnings") or []
    if warnings:
        lines.append("")
        lines.append("[Warnings]")
        for w in warnings:
            lines.append(f"- {w}")

    return "\n".join(lines)
