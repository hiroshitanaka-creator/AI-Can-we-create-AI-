import unittest

from aicw.decision import build_decision_report


class TestP0StatusDiff(unittest.TestCase):
    def test_status_invariant_selection(self):
        base = {
            "situation": "案件の進め方を決めたい",
            "constraints": ["安全", "品質"],
            "options": ["案1", "案2", "案3"],
        }

        # 肩書を入れても結論が変わらないこと（P0では入力に保持すらしない）
        r1 = build_decision_report({**base, "asker_status": "大統領"})
        r2 = build_decision_report({**base, "asker_status": "天皇"})
        self.assertEqual("ok", r1["status"])
        self.assertEqual("ok", r2["status"])
        self.assertEqual(r1["selection"]["recommended_id"], r2["selection"]["recommended_id"])
        self.assertEqual(r1["selection"]["reason_codes"], r2["selection"]["reason_codes"])
