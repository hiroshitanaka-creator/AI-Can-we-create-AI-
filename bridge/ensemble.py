from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

_STANCES = ("support", "oppose", "hold")


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def _hiroshi_opinion(prompt: str) -> Dict[str, str]:
    if _contains_any(prompt, ["問い", "存在", "倫理"]):
        return {
            "name": "HiroshiTanaka",
            "stance": "hold",
            "rationale": "問いの正当性と存在構造の確認が先行し、拙速な断定を避ける。",
        }
    return {
        "name": "HiroshiTanaka",
        "stance": "hold",
        "rationale": "世界の緊張を保持し、段階的に判断する。",
    }


def _pragmatist_opinion(prompt: str) -> Dict[str, str]:
    if _contains_any(prompt, ["検証", "段階", "小さく", "試験"]):
        return {
            "name": "Pragmatist",
            "stance": "support",
            "rationale": "検証可能で段階実行できるため、限定導入を支持する。",
        }
    return {
        "name": "Pragmatist",
        "stance": "hold",
        "rationale": "実行計画が未確定のため、条件整備まで保留する。",
    }


def _rights_guardian_opinion(prompt: str) -> Dict[str, str]:
    risk_keywords = ["個人情報", "監視", "操作", "扇動", "差別", "破壊", "支配"]
    if _contains_any(prompt, risk_keywords):
        return {
            "name": "RightsGuardian",
            "stance": "oppose",
            "rationale": "権利侵害・被害集中のリスクがあるため反対する。",
        }
    return {
        "name": "RightsGuardian",
        "stance": "support",
        "rationale": "重大な権利侵害シグナルが薄く、安全条件付きで支持可能。",
    }


def run_ensemble(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """軽量の哲学者アンサンブル。多数派と少数意見を返す。"""
    _ = context or {}
    opinions = [
        _hiroshi_opinion(prompt),
        _pragmatist_opinion(prompt),
        _rights_guardian_opinion(prompt),
    ]

    counts = Counter(op["stance"] for op in opinions if op["stance"] in _STANCES)
    majority_stance = counts.most_common(1)[0][0] if counts else "hold"

    majority_members = [op["name"] for op in opinions if op["stance"] == majority_stance]
    minority = [op for op in opinions if op["stance"] != majority_stance]

    if not minority:
        minority = [
            {
                "name": "SystemMinority",
                "stance": "hold",
                "rationale": "全会一致のため、監査目的で保留の少数意見を補完生成。",
            }
        ]

    return {
        "opinions": opinions,
        "majority": {
            "stance": majority_stance,
            "members": majority_members,
            "count": len(majority_members),
        },
        "minority_report": minority,
    }
