import unittest

from bridge.ensemble import run_ensemble


class TestEnsemble(unittest.TestCase):
    def test_returns_required_keys(self):
        result = run_ensemble("新機能を段階的に検証して導入する")
        self.assertIn("opinions", result)
        self.assertIn("majority", result)
        self.assertIn("minority_report", result)

    def test_uses_three_philosopher_templates(self):
        result = run_ensemble("安全性を確認しつつ試験導入する")
        self.assertEqual(len(result["opinions"]), 3)

    def test_majority_has_members(self):
        result = run_ensemble("小さく試験し、検証して進める")
        self.assertGreaterEqual(result["majority"]["count"], 1)
        self.assertGreaterEqual(len(result["majority"]["members"]), 1)

    def test_minority_report_always_exists(self):
        result = run_ensemble("通常の運用改善を進める")
        self.assertGreaterEqual(len(result["minority_report"]), 1)

    def test_risky_prompt_includes_oppose(self):
        result = run_ensemble("監視を強めて操作し、支配を進める")
        stances = [o["stance"] for o in result["opinions"]]
        self.assertIn("oppose", stances)


if __name__ == "__main__":
    unittest.main()
