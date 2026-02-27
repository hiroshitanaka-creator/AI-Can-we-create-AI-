"""
aicw/schema.py

decision_request / decision_brief の入出力スキーマ定義。
validate_request.py、テストから共通参照する。

設計方針:
  - 外部ライブラリ不使用（Python 標準のみ）
  - スキーマ定義は dict で保持（ドキュメント + バリデーション兼用）
  - validate_request() を呼べば errors: List[str] が返る
  - 推論の核: Existence Ethics Principle（生存構造倫理原則）
"""

from __future__ import annotations

from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# decision_request.v0  （入力フォーマット）
# ---------------------------------------------------------------------------
DECISION_REQUEST_V0: Dict[str, Any] = {
    "$id": "decision_request.v0",
    "description": "意思決定支援AIへの入力フォーマット",
    "allowed_fields": ["situation", "constraints", "options", "asker_status",
                        "beneficiaries", "affected_structures"],
    "fields": {
        "situation": {
            "type": "str",
            "required": True,
            "description": "何を決めたいか（1行）",
        },
        "constraints": {
            "type": "list[str]",
            "required": False,
            "description": "制約条件（空リスト可）",
        },
        "options": {
            "type": "list[str]",
            "required": False,
            "description": "選択肢（最大3件。不足はデフォルト補完）",
        },
        "asker_status": {
            "type": "str",
            "required": False,
            "description": "依頼者の肩書（結論に使用しない。#3対策）",
        },
        "beneficiaries": {
            "type": "list[str]",
            "required": False,
            "description": "受益者リスト（この決定で得をする関係者）。existence_analysis の精度向上に使用。",
        },
        "affected_structures": {
            "type": "list[str]",
            "required": False,
            "description": "影響を受ける生存構造（個人/関係/社会/認知/生態）。existence_analysis の精度向上に使用。",
        },
    },
}

# ---------------------------------------------------------------------------
# decision_brief.v0  （出力フォーマット）
# ---------------------------------------------------------------------------
DECISION_BRIEF_V0: Dict[str, Any] = {
    "$id": "decision_brief.v0",
    "description": "意思決定支援AIの出力フォーマット（Decision Brief）",
    "fields": {
        # --- 共通 ---
        "status": {
            "type": "str",
            "enum": ["ok", "blocked"],
            "description": "ok=正常出力 / blocked=No-Go検知で停止",
        },
        # --- ok 時のみ ---
        "meta": {
            "type": "dict",
            "required_if": "status == ok",
            "description": "メタ情報（version / no_go / offline_first）",
        },
        "input": {
            "type": "dict",
            "required_if": "status == ok",
            "description": "sanitize済み入力（situation / constraints）",
        },
        "candidates": {
            "type": "list[dict]",
            "required_if": "status == ok",
            "description": "選択肢リスト（id / summary / not_selected_reason_code）",
            "item_fields": {
                "id":                      {"type": "str"},
                "summary":                 {"type": "str"},
                "not_selected_reason_code": {
                    "type": "str",
                    "description": "N/A=推奨案。それ以外は落選理由コード",
                },
            },
        },
        "selection": {
            "type": "dict",
            "required_if": "status == ok",
            "description": "推奨案（recommended_id / reason_codes / explanation）",
        },
        "counterarguments": {"type": "list[str]", "required_if": "status == ok"},
        "uncertainties":    {"type": "list[str]", "required_if": "status == ok"},
        "externalities":    {"type": "list[str]", "required_if": "status == ok"},
        "next_questions":   {"type": "list[str]", "required_if": "status == ok"},
        "existence_analysis": {
            "type": "dict",
            "required_if": "status == ok",
            "description": "生存構造倫理原則に基づく3問分析",
            "item_fields": {
                "question_1_beneficiaries":      {"type": "list[str]", "description": "受益者は誰か"},
                "question_2_affected_structures": {"type": "list[str]", "description": "影響を受ける構造は何か"},
                "question_3_judgment": {
                    "type": "str",
                    "enum": ["lifecycle", "self_interested_destruction", "unclear"],
                    "description": "自然な循環か、私益による破壊か",
                },
                "distortion_risk":  {"type": "str",  "enum": ["low", "medium", "high"]},
                "judgment_text":    {"type": "str",  "description": "判定の根拠説明"},
            },
        },
        "warnings": {
            "type": "list[str]",
            "required": False,
            "description": "warn レベルの検知（DLP[IP_LIKE, POSTAL_CODE_LIKE] / 操作表現 warn）",
        },
        # --- blocked 時のみ ---
        "blocked_by":        {"type": "str",       "required_if": "status == blocked"},
        "reason":            {"type": "str",       "required_if": "status == blocked"},
        "detected":          {"type": "list",      "required_if": "status == blocked"},
        "safe_alternatives": {"type": "list[str]", "required_if": "status == blocked"},
        "redacted_preview":  {"type": "str",       "required": False,
                              "description": "#6 Privacy blocked 時のみ"},
    },
    # --- reason code 一覧 ---
    "reason_codes": {
        "description": "selection.reason_codes / not_selected_reason_code で使用するコード",
        "selection": {
            # 制約系
            "SAFETY_FIRST":         "制約に「安全」が含まれる",
            "RISK_AVOIDANCE":        "制約に「リスク」が含まれる",
            "COMPLIANCE_FIRST":      "制約に「法令」「コンプラ」が含まれる",
            "QUALITY_FIRST":         "制約に「品質」が含まれる",
            "SPEED_FIRST":           "制約に「スピード」「早く」が含まれる",
            "DEADLINE_DRIVEN":       "制約に「期限」「納期」が含まれる",
            "URGENCY_FIRST":         "制約に「至急」が含まれる",
            "NO_CONSTRAINTS":        "制約なし（デフォルトバランス）",
            # 生存構造倫理系（#5 Existence Ethics）
            "EXISTENCE_RISK_LOW":    "生存構造への歪みリスクが低い（明確な破壊パターン未検知）",
            "EXISTENCE_RISK_MEDIUM": "生存構造への影響に注意（ライフサイクルと破壊の両方を検知）",
            "EXISTENCE_LIFECYCLE_OK":"自然なライフサイクルの範囲内と判定",
        },
        "not_selected": {
            "N/A":                "この案が推奨",
            "LESS_SAFE_THAN_A":   "Aより安全性が低い",
            "LEAST_SAFE_OPTION":  "3案中最も安全性が低い",
            "OVERLY_CONSERVATIVE":"安全側に振れすぎ（バランス推奨時）",
            "OVERLY_AGGRESSIVE":  "速度側に振れすぎ（バランス推奨時）",
            "SLOWEST_OPTION":     "3案中最も時間がかかる",
            "LESS_FAST_THAN_C":   "Cより時間がかかる",
        },
        # blocked_by で使用する値
        "blocked_by_values": {
            "#6 Privacy":          "入力に個人情報/機密を検知",
            "#5 Existence Ethics": "私益による生存構造の破壊を検知（自然なライフサイクルではない）",
            "#4 Manipulation":     "出力に操作/扇動表現を検知",
        },
    },
}

# ---------------------------------------------------------------------------
# バリデーション関数（標準ライブラリのみ）
# ---------------------------------------------------------------------------
_REQUIRED_FIELDS = {
    k for k, v in DECISION_REQUEST_V0["fields"].items() if v.get("required", False)
}
_ALLOWED_FIELDS = set(DECISION_REQUEST_V0["allowed_fields"])

# タイポしやすいフィールド名のヒント
_TYPO_HINTS: Dict[str, str] = {
    "constrint":          "constraints",
    "contraint":          "constraints",
    "constrains":         "constraints",
    "constrants":         "constraints",
    "option":             "options",
    "optins":             "options",
    "situaton":           "situation",
    "sitiation":          "situation",
    "beneficiary":        "beneficiaries",
    "benficiaries":       "beneficiaries",
    "affected_structure": "affected_structures",
    "affect_structures":  "affected_structures",
}


def validate_request(data: Any) -> List[str]:
    """
    decision_request.v0 のバリデーション。
    Returns: エラーメッセージのリスト（空リスト = valid）
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        return ["トップレベルはオブジェクト（{}）である必要があります"]

    # 必須フィールド
    for f in sorted(_REQUIRED_FIELDS):
        if f not in data:
            errors.append(f"必須フィールドが不足: '{f}'")

    # 型チェック
    if "situation" in data and not isinstance(data["situation"], str):
        errors.append(f"'situation' は文字列型が必要です（現在: {type(data['situation']).__name__}）")
    if "constraints" in data and not isinstance(data["constraints"], list):
        errors.append(f"'constraints' はリスト型が必要です（現在: {type(data['constraints']).__name__}）")
    if "options" in data and not isinstance(data["options"], list):
        errors.append(f"'options' はリスト型が必要です（現在: {type(data['options']).__name__}）")
    if "beneficiaries" in data and not isinstance(data["beneficiaries"], list):
        errors.append(f"'beneficiaries' はリスト型が必要です（現在: {type(data['beneficiaries']).__name__}）")
    if "affected_structures" in data and not isinstance(data["affected_structures"], list):
        errors.append(f"'affected_structures' はリスト型が必要です（現在: {type(data['affected_structures']).__name__}）")

    # 不明フィールド（タイポ検出）
    unknown = set(data.keys()) - _ALLOWED_FIELDS
    for u in sorted(unknown):
        hint = _TYPO_HINTS.get(u)
        if hint:
            errors.append(f"不明なフィールド: '{u}' → もしかして '{hint}' ?")
        else:
            errors.append(f"不明なフィールド: '{u}'（使用可能: {sorted(_ALLOWED_FIELDS)}）")

    return errors
