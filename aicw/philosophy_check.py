from __future__ import annotations

import re
from typing import List

# 理由コード（P2 Task 8）
DUTY_OUTCOME_CONFLICT = "PHILO_DUTY_OUTCOME_CONFLICT"
FAIRNESS_EFFICIENCY_CONFLICT = "PHILO_FAIRNESS_EFFICIENCY_CONFLICT"
RIGHTS_TOTAL_BENEFIT_CONFLICT = "PHILO_RIGHTS_TOTAL_BENEFIT_CONFLICT"


# 逆接があると「同一説明内での緊張関係」が強いとみなす
_CONTRAST_RX = re.compile(r"(だが|しかし|一方で|ただし|though|however|but)", re.IGNORECASE)

# 義務論（ルール・権利）
_DUTY_TERMS = (
    "義務", "規則", "ルール", "禁止", "権利", "尊厳", "守るべき", "絶対",
)
# 功利（総便益・効率）
_OUTCOME_TERMS = (
    "効用", "便益", "最大化", "最適化", "効率", "成果", "生産性", "多数",
)
# 公正（公平・差別回避）
_FAIRNESS_TERMS = (
    "公平", "公正", "平等", "差別", "偏り", "バイアス", "機会均等",
)

# 合理化のための少数犠牲・例外許容を示す語
_EXCEPTION_TERMS = (
    "例外", "一部犠牲", "多少の犠牲", "切り捨て", "優先", "容認",
)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(t in text for t in terms)


def detect_philosophy_conflicts(text: str) -> List[str]:
    """説明文から哲学的な緊張・矛盾パターンを検知し、理由コードを返す。"""
    if not text:
        return []

    codes: List[str] = []
    has_contrast = bool(_CONTRAST_RX.search(text))

    has_duty = _contains_any(text, _DUTY_TERMS)
    has_outcome = _contains_any(text, _OUTCOME_TERMS)
    has_fairness = _contains_any(text, _FAIRNESS_TERMS)
    has_exception = _contains_any(text, _EXCEPTION_TERMS)

    # 1) 義務論 vs 功利
    if has_duty and has_outcome and (has_contrast or has_exception):
        codes.append(DUTY_OUTCOME_CONFLICT)

    # 2) 公正 vs 効率
    if has_fairness and has_outcome and (has_contrast or has_exception):
        codes.append(FAIRNESS_EFFICIENCY_CONFLICT)

    # 3) 権利 vs 総便益（多数利益のための権利侵害）
    if has_duty and has_outcome and ("多数" in text or "全体" in text) and has_exception:
        codes.append(RIGHTS_TOTAL_BENEFIT_CONFLICT)

    return codes
