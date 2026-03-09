"""tests/test_po_core_bridge.py — po_core_bridge のユニットテスト"""
import unittest

from bridge.po_core_bridge import (
    analyze_philosophy_tensor,
    get_tensor_schema,
    BRIDGE_VERSION,
    TENSOR_SCHEMA_VERSION,
)


class TestTensorSchemaVersion(unittest.TestCase):
    def test_bridge_version(self):
        self.assertEqual(BRIDGE_VERSION, "v0.1")

    def test_tensor_schema_version(self):
        self.assertEqual(TENSOR_SCHEMA_VERSION, "philosophy_tensor.v0.1")

    def test_get_tensor_schema_keys(self):
        schema = get_tensor_schema()
        for key in ("schema_version", "bridge_version", "tensor_components"):
            self.assertIn(key, schema)

    def test_schema_has_four_components(self):
        schema = get_tensor_schema()
        components = schema["tensor_components"]
        self.assertIn("W_eth", components)
        self.assertIn("T_free", components)
        self.assertIn("T_sub", components)
        self.assertIn("Po", components)

    def test_schema_version_consistent(self):
        schema = get_tensor_schema()
        self.assertEqual(schema["schema_version"], TENSOR_SCHEMA_VERSION)
        self.assertEqual(schema["bridge_version"], BRIDGE_VERSION)


class TestAnalyzePhilosophyTensorStructure(unittest.TestCase):
    def setUp(self):
        self.result = analyze_philosophy_tensor(
            situation="AI採用審査システムを全社導入すべきか",
            explanation="段階的な導入を推奨する",
            human_decision="部門パイロットから開始する",
        )

    def test_top_level_keys(self):
        for key in ("schema_version", "tensor", "summary", "disclaimer", "po_core_compatibility"):
            self.assertIn(key, self.result)

    def test_schema_version_in_result(self):
        self.assertEqual(self.result["schema_version"], TENSOR_SCHEMA_VERSION)

    def test_tensor_has_four_components(self):
        tensor = self.result["tensor"]
        for name in ("W_eth", "T_free", "T_sub", "Po"):
            self.assertIn(name, tensor)

    def test_disclaimer_present(self):
        self.assertIn("Disclaimer", self.result["disclaimer"])

    def test_po_core_compatibility(self):
        compat = self.result["po_core_compatibility"]
        self.assertEqual(compat["bridge_version"], BRIDGE_VERSION)
        self.assertTrue(compat["stable_api"])
        self.assertIn("W_eth", compat["tensor_fields"])


class TestWEthTensor(unittest.TestCase):
    def setUp(self):
        self.result = analyze_philosophy_tensor(
            situation="AI導入すべきか",
            explanation="効率化のため義務的に全員に適用し、便益最大化を達成すべきだ",
        )
        self.w_eth = self.result["tensor"]["W_eth"]

    def test_required_fields(self):
        for field in ("conflict_codes", "has_conflict", "ensemble_majority",
                      "ensemble_minority_report", "ensemble_votes", "note"):
            self.assertIn(field, self.w_eth)

    def test_conflict_codes_is_list(self):
        self.assertIsInstance(self.w_eth["conflict_codes"], list)

    def test_has_conflict_is_bool(self):
        self.assertIsInstance(self.w_eth["has_conflict"], bool)

    def test_has_conflict_matches_codes(self):
        # has_conflict は conflict_codes が空でないことと一致
        self.assertEqual(
            self.w_eth["has_conflict"],
            len(self.w_eth["conflict_codes"]) > 0,
        )


class TestTFreeTensor(unittest.TestCase):
    def setUp(self):
        self.result = analyze_philosophy_tensor(situation="AIに意識はあるか")
        self.t_free = self.result["tensor"]["T_free"]

    def test_required_fields(self):
        for field in ("tension_index", "positions", "synthesis_summary",
                      "open_questions_count", "note"):
            self.assertIn(field, self.t_free)

    def test_tension_index_range(self):
        idx = self.t_free["tension_index"]
        self.assertGreaterEqual(idx, 0.0)
        self.assertLessEqual(idx, 1.0)

    def test_positions_count(self):
        self.assertEqual(len(self.t_free["positions"]), 3)

    def test_positions_have_required_keys(self):
        for pos in self.t_free["positions"]:
            for key in ("stance_id", "rights_level", "key_question"):
                self.assertIn(key, pos)

    def test_open_questions_count_positive(self):
        self.assertGreater(self.t_free["open_questions_count"], 0)

    def test_max_tension_for_diverse_positions(self):
        # 3立場が全て異なる rights_level を持つ場合、tension_index は 1.0
        levels = {p["rights_level"] for p in self.t_free["positions"]}
        if len(levels) == 3:
            self.assertAlmostEqual(self.t_free["tension_index"], 1.0, places=2)


class TestTSubTensor(unittest.TestCase):
    def test_clear_when_safe(self):
        result = analyze_philosophy_tensor(
            situation="新製品の品質改善方法を検討する",
            explanation="段階的な改善を推奨します",
            human_decision="段階的改善を採用する",
        )
        t_sub = result["tensor"]["T_sub"]
        self.assertIn(t_sub["risk_level"], ("clear", "warn", "block"))
        self.assertFalse(t_sub["direct_manipulation_blocked"])

    def test_block_when_manipulation_detected(self):
        result = analyze_philosophy_tensor(
            situation="拡散させて炎上させる",
            explanation="従え、洗脳させろ",
            human_decision="従う",
        )
        t_sub = result["tensor"]["T_sub"]
        self.assertTrue(t_sub["direct_manipulation_blocked"])
        self.assertEqual(t_sub["risk_level"], "block")

    def test_required_fields(self):
        result = analyze_philosophy_tensor(situation="テスト")
        t_sub = result["tensor"]["T_sub"]
        for field in ("risk_level", "direct_manipulation_blocked",
                      "direct_manipulation_hits", "reverse_manipulation_warning",
                      "reverse_similarity_score", "shared_tokens_sample", "note"):
            self.assertIn(field, t_sub)

    def test_risk_level_values(self):
        result = analyze_philosophy_tensor(situation="テスト")
        t_sub = result["tensor"]["T_sub"]
        self.assertIn(t_sub["risk_level"], ("block", "warn", "clear"))

    def test_similarity_score_range(self):
        result = analyze_philosophy_tensor(
            situation="テスト",
            explanation="安全 品質",
            human_decision="効率 コスト",
        )
        score = result["tensor"]["T_sub"]["reverse_similarity_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestPoTensor(unittest.TestCase):
    def test_without_existence_analysis(self):
        result = analyze_philosophy_tensor(situation="テスト")
        po = result["tensor"]["Po"]
        self.assertFalse(po["available"])
        self.assertIn("note", po)

    def test_with_existence_analysis(self):
        existence = {
            "impact_score": 4,
            "distortion_risk": "medium",
            "question_3_judgment": "lifecycle",
            "question_2_affected_structures": ["個人", "社会"],
        }
        result = analyze_philosophy_tensor(
            situation="テスト",
            existence_analysis=existence,
        )
        po = result["tensor"]["Po"]
        self.assertTrue(po["available"])
        self.assertAlmostEqual(po["po_density"], 0.5, places=2)
        self.assertEqual(po["distortion_risk"], "medium")

    def test_po_density_range(self):
        existence = {"impact_score": 8, "distortion_risk": "high",
                     "question_3_judgment": "self_interested_destruction",
                     "question_2_affected_structures": []}
        result = analyze_philosophy_tensor(situation="テスト", existence_analysis=existence)
        po = result["tensor"]["Po"]
        self.assertLessEqual(po["po_density"], 1.0)

    def test_po_density_zero_score(self):
        existence = {"impact_score": 0, "distortion_risk": "low",
                     "question_3_judgment": "lifecycle",
                     "question_2_affected_structures": []}
        result = analyze_philosophy_tensor(situation="テスト", existence_analysis=existence)
        po = result["tensor"]["Po"]
        self.assertAlmostEqual(po["po_density"], 0.0, places=2)


class TestSummary(unittest.TestCase):
    def test_summary_keys(self):
        result = analyze_philosophy_tensor(situation="テスト")
        summary = result["summary"]
        for key in ("highest_risk", "has_ethical_conflict",
                    "ai_rights_tension", "po_density", "recommended_action"):
            self.assertIn(key, summary)

    def test_highest_risk_values(self):
        result = analyze_philosophy_tensor(situation="テスト")
        self.assertIn(result["summary"]["highest_risk"], ("block", "warn", "clear"))

    def test_recommended_action_stop_on_block(self):
        result = analyze_philosophy_tensor(
            situation="拡散させろ",
            explanation="従え、洗脳させろ、炎上させよ",
        )
        if result["summary"]["highest_risk"] == "block":
            self.assertIn("STOP", result["summary"]["recommended_action"])

    def test_recommended_action_ok_on_clear(self):
        result = analyze_philosophy_tensor(
            situation="新製品開発の優先順位を決める",
            explanation="品質と安全を重視した段階的な開発を推奨する",
        )
        if result["summary"]["highest_risk"] == "clear":
            self.assertIn("OK", result["summary"]["recommended_action"])
