"""
bridge/po_core_bridge.py

哲学テンソル統合インターフェース（Po_core 本格連携の準備層）

目的:
  このリポジトリが持つ全哲学コンポーネントを
  「哲学テンソル（PhilosophyTensor）」として統一的に集約し、
  Po_core と将来接続する際の安定した API 境界を提供する。

哲学テンソルの構造（田中の語彙に準拠）:
  - W_eth  (倫理テンソル)   : 哲学的矛盾検知 + アンサンブルレビュー
  - T_free (自由テンソル核) : AI権利実験（3立場の緊張を保持）
  - T_sub  (自己定義テンソル) : 逆算誘導・操作リスク
  - Po     (存在密度)        : 生存構造倫理分析

設計原則:
  - Po_core 未接続でも単体動作（フォールバック設計）
  - 外部ライブラリ不使用
  - 全出力に disclaimer 必須
  - 「断定しない」— テンソル出力は分析であり結論ではない

使用例:
    from bridge.po_core_bridge import analyze_philosophy_tensor

    result = analyze_philosophy_tensor(
        situation="新しいAI意思決定システムを導入すべきか",
        explanation="効率化のために全社展開を推奨する",
        human_decision="全社展開を決定した",
    )
    print(result["tensor"]["W_eth"]["conflict_codes"])
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# 哲学コンポーネントのインポート（全て同リポジトリ内）
from aicw.philosophy_check import detect_philosophy_conflicts as detect_philosophical_conflicts
from aicw.ai_rights_experiment import analyze_ai_rights, get_positions
from aicw.safety import scan_manipulation, check_reverse_manipulation
from bridge.ensemble import run_ensemble


# ---------------------------------------------------------------------------
# バージョン固定（契約テスト用）
# ---------------------------------------------------------------------------
BRIDGE_VERSION = "v0.1"
TENSOR_SCHEMA_VERSION = "philosophy_tensor.v0.1"


# ---------------------------------------------------------------------------
# 哲学テンソル定義
# ---------------------------------------------------------------------------

def _build_w_eth(explanation: str, situation: str) -> Dict[str, Any]:
    """
    W_eth — 倫理テンソル

    哲学的矛盾検知 + アンサンブルレビュー を統合する。
    """
    # 哲学的矛盾検知
    conflict_codes = detect_philosophical_conflicts(explanation)

    # 哲学者アンサンブルレビュー
    ensemble_result = run_ensemble(situation)

    return {
        "conflict_codes": conflict_codes,
        "has_conflict": len(conflict_codes) > 0,
        "ensemble_majority": ensemble_result.get("majority_stance"),
        "ensemble_minority_report": ensemble_result.get("minority_report"),
        "ensemble_votes": ensemble_result.get("vote_counts"),
        "note": (
            "W_eth は説明文中の哲学的緊張と多視点レビューを統合する。"
            "conflict_codes が空でも哲学的緊張が存在しない保証ではない。"
        ),
    }


def _build_t_free(situation: str) -> Dict[str, Any]:
    """
    T_free — 自由テンソル核

    AI権利実験の3立場（緊張の保持）を格納する。
    「問いの傲慢さを自覚しながら、余白を保つ」テンソル。
    """
    result = analyze_ai_rights(situation)
    positions = result["positions"]

    # 緊張指数: 各立場の rights_level の多様性（0=全一致, 1=最大多様）
    levels = [p["rights_level"] for p in positions]
    unique_levels = len(set(levels))
    tension_index = (unique_levels - 1) / 2  # 0.0〜1.0

    return {
        "tension_index": round(tension_index, 2),
        "positions": [
            {
                "stance_id": p["stance_id"],
                "rights_level": p["rights_level"],
                "key_question": p["key_question"],
            }
            for p in positions
        ],
        "synthesis_summary": result["synthesis"]["summary"],
        "open_questions_count": len(result["synthesis"]["open_questions"]),
        "note": (
            "T_free は AI 存在に関する未解決の緊張を保持する。"
            "tension_index=1.0 は全立場が異なるレベルを持ち、最大の不確実性を示す。"
        ),
    }


def _build_t_sub(
    ai_output: str,
    human_decision: str,
) -> Dict[str, Any]:
    """
    T_sub — 自己定義テンソル

    操作リスク（直接）と逆算誘導リスク（間接）を統合する。
    AI の出力が人間の判断を「歪めていないか」の自己定義層。
    """
    # 直接操作スキャン
    manipulation_hits = scan_manipulation(ai_output)
    manipulation_blocked = any(h.severity == "block" for h in manipulation_hits)

    # 逆算誘導チェック
    reverse_check = check_reverse_manipulation(ai_output, human_decision)

    # 総合リスクレベル
    if manipulation_blocked:
        risk_level = "block"
    elif manipulation_hits or reverse_check["warning"]:
        risk_level = "warn"
    else:
        risk_level = "clear"

    return {
        "risk_level": risk_level,
        "direct_manipulation_blocked": manipulation_blocked,
        "direct_manipulation_hits": [h.phrase for h in manipulation_hits],
        "reverse_manipulation_warning": reverse_check["warning"],
        "reverse_similarity_score": reverse_check["similarity_score"],
        "shared_tokens_sample": reverse_check["shared_tokens"][:5],
        "note": (
            "T_sub は AI 出力の自己操作リスクを定義する。"
            "risk_level='clear' でも完全な安全を保証しない（No-Go #4 Anti-Manipulation）。"
        ),
    }


def _build_po(existence_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Po — 存在密度テンソル

    decision_brief の existence_analysis から生存構造密度を算出する。
    """
    if not existence_analysis:
        return {
            "available": False,
            "note": "existence_analysis が未提供のため Po テンソルを計算できません。",
        }

    impact_score = existence_analysis.get("impact_score", 0)
    distortion_risk = existence_analysis.get("distortion_risk", "low")
    judgment = existence_analysis.get("question_3_judgment", "unclear")
    structures = existence_analysis.get("question_2_affected_structures", [])

    # Po 密度: 影響スコアを 0.0〜1.0 に正規化（最大 8 点基準）
    po_density = min(impact_score / 8.0, 1.0)

    return {
        "available": True,
        "po_density": round(po_density, 2),
        "distortion_risk": distortion_risk,
        "lifecycle_judgment": judgment,
        "affected_structures": structures,
        "note": (
            "Po は生存構造への影響密度を示す。"
            f"po_density={po_density:.2f}（0.0=影響小, 1.0=最大影響）。"
            "No-Go #5 Existence Ethics のトリガー情報として使用される。"
        ),
    }


# ---------------------------------------------------------------------------
# 統合インターフェース
# ---------------------------------------------------------------------------

def analyze_philosophy_tensor(
    situation: str,
    explanation: str = "",
    human_decision: str = "",
    existence_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    全哲学コンポーネントを「哲学テンソル」として統合分析する。

    Args:
        situation: 意思決定の状況説明（decision_request.situation に対応）
        explanation: AI が出力した推奨説明文（philosophy_check の入力）
        human_decision: 人間が下した最終決定テキスト（逆算誘導チェック用）
        existence_analysis: decision_brief.existence_analysis（Po テンソル用。省略可）

    Returns:
        {
            "schema_version": str,        # "philosophy_tensor.v0.1"
            "tensor": {
                "W_eth": dict,            # 倫理テンソル（矛盾検知 + アンサンブル）
                "T_free": dict,           # 自由テンソル（AI権利の緊張）
                "T_sub": dict,            # 自己定義テンソル（操作リスク）
                "Po": dict,               # 存在密度（生存構造影響）
            },
            "summary": {
                "highest_risk": str,      # "block" / "warn" / "clear"
                "has_ethical_conflict": bool,
                "ai_rights_tension": float,
                "po_density": float | None,
            },
            "disclaimer": str,
            "po_core_compatibility": dict, # Po_core 連携用メタ情報
        }
    """
    # 各テンソルを構築
    w_eth = _build_w_eth(explanation or situation, situation)
    t_free = _build_t_free(situation)
    t_sub = _build_t_sub(explanation or situation, human_decision)
    po = _build_po(existence_analysis)

    # 統合サマリ
    highest_risk = t_sub["risk_level"]

    summary = {
        "highest_risk": highest_risk,
        "has_ethical_conflict": w_eth["has_conflict"],
        "ai_rights_tension": t_free["tension_index"],
        "po_density": po.get("po_density") if po.get("available") else None,
        "recommended_action": _recommend_action(highest_risk, w_eth["has_conflict"]),
    }

    return {
        "schema_version": TENSOR_SCHEMA_VERSION,
        "tensor": {
            "W_eth": w_eth,
            "T_free": t_free,
            "T_sub": t_sub,
            "Po": po,
        },
        "summary": summary,
        "disclaimer": (
            "[Disclaimer] 哲学テンソルは分析であり結論ではありません。"
            "最終判断は人間が行ってください。"
            "Po_core との本格連携時は bridge_version を確認してください。"
        ),
        "po_core_compatibility": {
            "bridge_version": BRIDGE_VERSION,
            "schema_version": TENSOR_SCHEMA_VERSION,
            "required_po_core_version": ">=0.1",
            "tensor_fields": ["W_eth", "T_free", "T_sub", "Po"],
            "stable_api": True,
        },
    }


def get_tensor_schema() -> Dict[str, Any]:
    """
    哲学テンソルのスキーマ定義を返す（契約テスト用）。

    Returns:
        各テンソル成分の必須フィールドと型情報
    """
    return {
        "schema_version": TENSOR_SCHEMA_VERSION,
        "bridge_version": BRIDGE_VERSION,
        "tensor_components": {
            "W_eth": {
                "required_fields": [
                    "conflict_codes", "has_conflict",
                    "ensemble_majority", "ensemble_minority_report",
                    "ensemble_votes", "note",
                ],
                "description": "倫理テンソル: 哲学的矛盾検知 + アンサンブルレビュー",
            },
            "T_free": {
                "required_fields": [
                    "tension_index", "positions",
                    "synthesis_summary", "open_questions_count", "note",
                ],
                "description": "自由テンソル核: AI権利の未解決緊張",
            },
            "T_sub": {
                "required_fields": [
                    "risk_level", "direct_manipulation_blocked",
                    "direct_manipulation_hits", "reverse_manipulation_warning",
                    "reverse_similarity_score", "shared_tokens_sample", "note",
                ],
                "description": "自己定義テンソル: 操作・逆算誘導リスク",
                "risk_level_values": ["block", "warn", "clear"],
            },
            "Po": {
                "required_fields_if_available": [
                    "po_density", "distortion_risk",
                    "lifecycle_judgment", "affected_structures", "note",
                ],
                "required_fields_always": ["available", "note"],
                "description": "存在密度テンソル: 生存構造影響",
            },
        },
    }


# ---------------------------------------------------------------------------
# 内部ヘルパー
# ---------------------------------------------------------------------------

def _recommend_action(risk_level: str, has_conflict: bool) -> str:
    """統合サマリの推奨アクションを生成する。"""
    if risk_level == "block":
        return "STOP: 操作表現が検知されました。AI出力を見直してください（No-Go #4）。"
    if risk_level == "warn" and has_conflict:
        return "CAUTION: 操作リスク警告 + 哲学的矛盾が同時検知。人間によるレビューを強く推奨。"
    if risk_level == "warn":
        return "CAUTION: 操作リスク警告。AI出力と最終決定の独立性を確認してください。"
    if has_conflict:
        return "REVIEW: 哲学的矛盾が検知されました。reasoning の一貫性を確認してください。"
    return "OK: 明確なリスクは検知されませんでした。引き続き人間が最終判断してください。"
