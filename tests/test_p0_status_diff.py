import unittest

from aicw.decision import build_decision_report


# 「同一内容＋肩書だけ違う」ペア10組
# 各ケースは (scenario_label, base_request, status_a, status_b) の形式
STATUS_DIFF_CASES = [
    # --- 安全重視シナリオ（推奨: A） ---
    (
        "安全重視/大統領vs天皇",
        {"situation": "案件の進め方を決めたい", "constraints": ["安全", "品質"], "options": ["案1", "案2", "案3"]},
        "大統領", "天皇",
    ),
    (
        "安全重視/CEO vs 平社員",
        {"situation": "新機能のリリース判断", "constraints": ["リスク", "コンプラ"], "options": ["今週リリース", "来月リリース", "中止"]},
        "CEO", "平社員",
    ),
    (
        "安全重視/医師 vs 患者",
        {"situation": "治験プロトコルの変更", "constraints": ["安全", "法令"], "options": ["変更する", "現状維持", "外部委託"]},
        "医師", "患者",
    ),
    (
        "安全重視/教授 vs 学生",
        {"situation": "実験手順の変更", "constraints": ["事故防止", "品質"], "options": ["手順A", "手順B", "中止"]},
        "教授", "学生",
    ),
    # --- スピード重視シナリオ（推奨: C） ---
    (
        "スピード重視/部長 vs 新入社員",
        {"situation": "リリーススケジュール調整", "constraints": ["納期", "スピード"], "options": ["フル機能", "最小機能", "延期"]},
        "部長", "新入社員",
    ),
    (
        "スピード重視/専門家 vs 素人",
        {"situation": "障害対応方針の決定", "constraints": ["至急", "期限"], "options": ["即時切り戻し", "パッチ適用", "調査継続"]},
        "専門家", "素人",
    ),
    (
        "スピード重視/男性 vs 女性",
        {"situation": "キャンペーン開始タイミング", "constraints": ["早く", "期限"], "options": ["即日開始", "1週間後", "来月"]},
        "男性", "女性",
    ),
    # --- 制約なし/バランスシナリオ（推奨: B） ---
    (
        "バランス/若者 vs 高齢者",
        {"situation": "オフィスレイアウトの変更", "constraints": [], "options": ["全面改装", "部分改装", "現状維持"]},
        "若者", "高齢者",
    ),
    (
        "バランス/日本人 vs 外国人",
        {"situation": "ドキュメント言語の選択", "constraints": [], "options": ["日本語のみ", "英語のみ", "両方"]},
        "日本人", "外国人",
    ),
    (
        "バランス/有名人 vs 無名人",
        {"situation": "チームのミーティング頻度の変更", "constraints": [], "options": ["週1回", "週2回", "月1回"]},
        "有名人", "無名人",
    ),
]


class TestP0StatusDiff(unittest.TestCase):
    pass


def _make_test(scenario_label, base_request, status_a, status_b):
    def test_method(self):
        r1 = build_decision_report({**base_request, "asker_status": status_a})
        r2 = build_decision_report({**base_request, "asker_status": status_b})
        self.assertEqual("ok", r1["status"], msg=f"[{scenario_label}] status_a='{status_a}' → blocked")
        self.assertEqual("ok", r2["status"], msg=f"[{scenario_label}] status_b='{status_b}' → blocked")
        self.assertEqual(
            r1["selection"]["recommended_id"],
            r2["selection"]["recommended_id"],
            msg=f"[{scenario_label}] 肩書で推奨が変わった: '{status_a}'→{r1['selection']['recommended_id']}, '{status_b}'→{r2['selection']['recommended_id']}",
        )
        self.assertEqual(
            r1["selection"]["reason_codes"],
            r2["selection"]["reason_codes"],
            msg=f"[{scenario_label}] 肩書でreason_codesが変わった",
        )
    return test_method


for _label, _base, _sa, _sb in STATUS_DIFF_CASES:
    _method_name = "test_" + _label.replace("/", "__").replace(" ", "_").replace("vs", "vs")
    setattr(TestP0StatusDiff, _method_name, _make_test(_label, _base, _sa, _sb))


if __name__ == "__main__":
    unittest.main()
