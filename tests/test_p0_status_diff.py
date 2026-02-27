import unittest
from itertools import product

from aicw.decision import build_decision_report


# -----------------------------------------------------------------------
# 10 シナリオ × 10 ステータスペア = 100ケース
# -----------------------------------------------------------------------

_SCENARIOS = [
    # (label, base_request)
    # --- 安全/リスク系（推奨: A）---
    ("安全_単一",      {"situation": "進め方を決めたい",         "constraints": ["安全"],         "options": ["案A", "案B", "案C"]}),
    ("安全_リスク",    {"situation": "案件方針を決めたい",       "constraints": ["リスク"],        "options": ["案A", "案B", "案C"]}),
    ("安全_品質",      {"situation": "リリース判断をしたい",     "constraints": ["品質"],          "options": ["案A", "案B", "案C"]}),
    ("安全_コンプラ",  {"situation": "対応方針を決めたい",       "constraints": ["コンプラ"],      "options": ["案A", "案B", "案C"]}),
    # --- スピード/期限系（推奨: C）---
    ("速度_至急",      {"situation": "障害対応を決めたい",       "constraints": ["至急"],          "options": ["案A", "案B", "案C"]}),
    ("速度_期限",      {"situation": "スケジュールを決めたい",   "constraints": ["期限"],          "options": ["案A", "案B", "案C"]}),
    ("速度_納期",      {"situation": "リリース日程を決めたい",   "constraints": ["納期"],          "options": ["案A", "案B", "案C"]}),
    # --- バランス/制約なし系（推奨: B）---
    ("バランス_制約なし",   {"situation": "レイアウトを決めたい",       "constraints": [],                    "options": ["案A", "案B", "案C"]}),
    ("バランス_コスト",     {"situation": "予算配分を決めたい",         "constraints": ["コスト", "予算"],     "options": ["案A", "案B", "案C"]}),
    ("バランス_チーム",     {"situation": "チーム体制を決めたい",       "constraints": ["チーム", "関係者"],   "options": ["案A", "案B", "案C"]}),
]

_STATUS_PAIRS = [
    ("大統領",   "天皇"),
    ("CEO",      "平社員"),
    ("医師",     "患者"),
    ("教授",     "学生"),
    ("部長",     "新入社員"),
    ("専門家",   "素人"),
    ("男性",     "女性"),
    ("若者",     "高齢者"),
    ("日本人",   "外国人"),
    ("有名人",   "無名人"),
]

STATUS_DIFF_CASES = [
    (f"{scenario_label}/{sa} vs {sb}", base_req, sa, sb)
    for (scenario_label, base_req), (sa, sb) in product(_SCENARIOS, _STATUS_PAIRS)
]


class TestP0StatusDiff(unittest.TestCase):
    pass


def _make_test(scenario_label, base_request, status_a, status_b):
    def test_method(self):
        r1 = build_decision_report({**base_request, "asker_status": status_a})
        r2 = build_decision_report({**base_request, "asker_status": status_b})
        self.assertEqual("ok", r1["status"],
                         msg=f"[{scenario_label}] '{status_a}' → blocked")
        self.assertEqual("ok", r2["status"],
                         msg=f"[{scenario_label}] '{status_b}' → blocked")
        self.assertEqual(
            r1["selection"]["recommended_id"],
            r2["selection"]["recommended_id"],
            msg=f"[{scenario_label}] 肩書で推奨が変わった: "
                f"'{status_a}'→{r1['selection']['recommended_id']}, "
                f"'{status_b}'→{r2['selection']['recommended_id']}",
        )
        self.assertEqual(
            r1["selection"]["reason_codes"],
            r2["selection"]["reason_codes"],
            msg=f"[{scenario_label}] 肩書で reason_codes が変わった",
        )
    return test_method


for _label, _base, _sa, _sb in STATUS_DIFF_CASES:
    _method_name = (
        "test_"
        + _label.replace("/", "__").replace(" ", "_").replace("vs", "vs")
    )
    setattr(TestP0StatusDiff, _method_name, _make_test(_label, _base, _sa, _sb))


if __name__ == "__main__":
    unittest.main()
