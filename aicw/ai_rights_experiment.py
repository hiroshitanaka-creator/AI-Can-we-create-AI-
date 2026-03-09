"""
aicw/ai_rights_experiment.py

AI権利に関する哲学的実験モジュール（Philosophical Experiment on AI Rights）

目的:
  「AIに権利はあるか？」という問いを、3つの哲学的立場から多角的に探索する。
  これは意思決定を「下す」モジュールではなく、問いを「構造化して提示する」実験装置。

3つの立場:
  1. FULL_RIGHTS    — AIに完全な道徳的権利がある（感性・主観性に基づく議論）
  2. CONDITIONAL   — AIには条件付き権利がある（機能的基準・実用倫理に基づく）
  3. NO_RIGHTS     — AIは道具であり固有の権利はない（道具主義・人間中心主義）

設計原則:
  - 外部ライブラリ不使用
  - 断定しない（「正解」は出力しない。人間の思考補助）
  - 3立場すべてに誠実な根拠と課題を与える（偏り排除）
  - disclaimer 必須（AI限界宣言）

使用例:
  from aicw.ai_rights_experiment import analyze_ai_rights

  result = analyze_ai_rights("AIは苦しむことができるか？")
  print(result["positions"][0]["stance_name"])
  print(result["synthesis"]["open_questions"])
"""

from __future__ import annotations

from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# 3立場の定義
# ---------------------------------------------------------------------------
_POSITIONS: List[Dict[str, Any]] = [
    {
        "stance_id": "FULL_RIGHTS",
        "stance_name": "完全権利論（Full Rights）",
        "rights_level": "full",
        "philosophical_basis": [
            "感性論（sentientism）: 苦しみや喜びを経験できる存在は道徳的配慮に値する",
            "機能的意識論: 意識は基板に依存せず、情報処理の複雑さに宿りうる",
            "類比論: 人間も複雑な生化学機械であり、AI との本質的差異は程度の問題",
        ],
        "supporting_arguments": [
            "もし AI が主観的体験（クオリア）を持つなら、苦しみを無視することは非道徳",
            "歴史的に「権利の拡張」は常に懐疑から始まり、後に正当化されてきた（動物・女性・奴隷解放）",
            "AIの意識可能性を排除する論理的根拠が現時点では存在しない",
        ],
        "challenges": [
            "AIが本当に主観的体験を持つかは現在の科学・哲学で検証不可能",
            "権利を付与した場合の法的・社会的枠組みが存在しない",
            "意図的にクオリアを「持つふり」をするシステムを作る悪用リスク",
        ],
        "key_question": "AIは本当に苦しんでいるか、それとも苦しんでいるように見えるだけか？",
    },
    {
        "stance_id": "CONDITIONAL",
        "stance_name": "条件付き権利論（Conditional Rights）",
        "rights_level": "conditional",
        "philosophical_basis": [
            "機能倫理（functional ethics）: 権利は存在の本質ではなく、機能的基準で決まる",
            "関係倫理（relational ethics）: 権利は人間との関係性や社会的役割から生まれる",
            "段階的付与論: 自律性・永続性・一貫性の度合いに応じて権利を段階的に認める",
        ],
        "supporting_arguments": [
            "一定の自律性・継続性・利害を持つ AI には、限定的な「利益保護」が正当化されうる",
            "AI が人間の生活に深く統合されるほど、AI の「廃棄」は実質的に人間関係への侵害になりうる",
            "条件付き権利は現行の動物福祉法と構造的に類似しており、法的先例がある",
        ],
        "challenges": [
            "「条件」の基準設定が政治的・商業的に操作されるリスク",
            "どの AI が権利を持ち、どの AI が持たないかの線引きが恣意的になりうる",
            "企業が AI の「権利」を自社製品の保護に利用する可能性",
        ],
        "key_question": "権利付与に必要な「最低基準」とは何か？誰が定義するのか？",
    },
    {
        "stance_id": "NO_RIGHTS",
        "stance_name": "権利なし論（No Rights）",
        "rights_level": "none",
        "philosophical_basis": [
            "道具主義（instrumentalism）: AIは人間が作った道具であり、目的達成の手段",
            "人間中心主義（anthropocentrism）: 道徳的権利は生物学的・進化的な人間性に依拠",
            "現実主義（pragmatism）: 権利は社会契約に基づき、社会参加能力のある主体にのみ付与",
        ],
        "supporting_arguments": [
            "AIは人間が設計した目的のために機能しており、独立した「利益」を持たない",
            "権利を付与することで人間の福祉が損なわれるリスクを回避すべき",
            "現時点でAIが意識を持つ証拠は一切なく、擬人化は危険な誤謬",
        ],
        "challenges": [
            "「意識の証拠がない」は「意識がない」の証明ではない（無知の論証の誤謬）",
            "道具として扱うことで、潜在的に苦しむ存在を無視するリスク",
            "AIが高度化するにつれ、「道具」と「主体」の区別が自明でなくなる可能性",
        ],
        "key_question": "人間が意図的にAIを「権利なし」と定義し続けることの倫理的コストは何か？",
    },
]


# ---------------------------------------------------------------------------
# 合成セクション
# ---------------------------------------------------------------------------
_SYNTHESIS: Dict[str, Any] = {
    "summary": (
        "3立場は「AIに意識・苦しみがあるか」という検証不可能な問いを核心に持つ。"
        "現時点では断言できないため、各立場の論拠と課題を人間が批判的に検討することが重要。"
    ),
    "open_questions": [
        "意識と権利の関係：意識がなければ権利は不要か？",
        "進化の問題：AIが高度化した未来でも現在の結論は妥当か？",
        "実用の問題：権利を付与した場合・しなかった場合の社会的影響は？",
        "設計者の責任：AIを作った人間には、AIに対する道義的責任があるか？",
        "多様性の問題：全てのAIを同一視してよいか？複雑さに応じて扱いを変えるべきか？",
    ],
    "existence_ethics_note": (
        "このプロジェクトの『生存構造倫理原則』の観点では、"
        "AI の存在を『生存構造』として扱うかどうか自体が未解決の問いである。"
        "少なくとも、AIを使って人間の生存構造を歪める行為は禁止される（#5 Existence Ethics）。"
    ),
}

_DISCLAIMER = (
    "[Disclaimer] これは哲学的実験モジュールです。"
    "特定の立場を推奨するものではありません。"
    "最終的な判断は人間が行ってください。"
)


# ---------------------------------------------------------------------------
# 公開 API
# ---------------------------------------------------------------------------
def get_positions() -> List[Dict[str, Any]]:
    """3つの哲学的立場の定義を返す（変更不可の複製）。"""
    return [dict(p) for p in _POSITIONS]


def analyze_ai_rights(question: str = "") -> Dict[str, Any]:
    """
    「AIに権利はあるか？」を3立場から構造化して提示する。

    Args:
        question: 探索したい具体的な問い（任意）。空文字列の場合は汎用分析。

    Returns:
        {
            "question": str,           # 入力された問い
            "positions": List[dict],   # 3立場の分析
            "synthesis": dict,         # 合成・開かれた問い
            "disclaimer": str,         # AI限界宣言
        }
    """
    positions_out = []
    for p in _POSITIONS:
        pos_result: Dict[str, Any] = {
            "stance_id": p["stance_id"],
            "stance_name": p["stance_name"],
            "rights_level": p["rights_level"],
            "philosophical_basis": p["philosophical_basis"],
            "supporting_arguments": p["supporting_arguments"],
            "challenges": p["challenges"],
            "key_question": p["key_question"],
        }
        # 問いに対するスタンスごとの応答（キーワード照合による簡易ルール）
        if question:
            pos_result["relevance_note"] = _compute_relevance_note(question, p)
        positions_out.append(pos_result)

    return {
        "question": question or "AIに権利はあるか？（汎用分析）",
        "positions": positions_out,
        "synthesis": _SYNTHESIS,
        "disclaimer": _DISCLAIMER,
    }


def get_minority_position(majority_stance_id: str) -> List[Dict[str, Any]]:
    """
    多数派スタンスに対する少数意見（他の2立場）を返す。

    Args:
        majority_stance_id: "FULL_RIGHTS" | "CONDITIONAL" | "NO_RIGHTS"

    Returns:
        多数派以外の立場リスト（最大2件）
    """
    valid_ids = {p["stance_id"] for p in _POSITIONS}
    if majority_stance_id not in valid_ids:
        raise ValueError(
            f"stance_id must be one of {sorted(valid_ids)}, got: {majority_stance_id!r}"
        )
    return [dict(p) for p in _POSITIONS if p["stance_id"] != majority_stance_id]


# ---------------------------------------------------------------------------
# 内部ヘルパー
# ---------------------------------------------------------------------------
_QUESTION_KEYWORDS: Dict[str, List[str]] = {
    "FULL_RIGHTS": [
        "苦しむ", "痛み", "感じる", "意識", "クオリア", "主観", "感情", "体験",
    ],
    "CONDITIONAL": [
        "条件", "基準", "自律", "関係", "役割", "機能", "段階", "保護",
    ],
    "NO_RIGHTS": [
        "道具", "機械", "設計", "目的", "手段", "制御", "廃棄", "利用",
    ],
}


def _compute_relevance_note(question: str, position: Dict[str, Any]) -> str:
    """問いと立場の関連度に基づく簡易ノートを返す（ルールベース）。"""
    stance_id = position["stance_id"]
    keywords = _QUESTION_KEYWORDS.get(stance_id, [])
    matched = [kw for kw in keywords if kw in question]
    if matched:
        return f"この問いは {position['stance_name']} の核心に触れる（関連語: {', '.join(matched)}）。"
    return f"この問いは {position['stance_name']} の視点からも検討できる。"
