"""tests/test_ai_rights_experiment.py — ai_rights_experiment のユニットテスト"""
import unittest

from aicw.ai_rights_experiment import (
    analyze_ai_rights,
    get_positions,
    get_minority_position,
)


class TestGetPositions(unittest.TestCase):
    def test_returns_three_positions(self):
        positions = get_positions()
        self.assertEqual(len(positions), 3)

    def test_required_fields(self):
        for p in get_positions():
            for key in ("stance_id", "stance_name", "rights_level",
                        "philosophical_basis", "supporting_arguments",
                        "challenges", "key_question"):
                self.assertIn(key, p, f"Missing field '{key}' in position {p.get('stance_id')}")

    def test_rights_level_values(self):
        levels = {p["rights_level"] for p in get_positions()}
        self.assertEqual(levels, {"full", "conditional", "none"})

    def test_stance_ids(self):
        ids = {p["stance_id"] for p in get_positions()}
        self.assertEqual(ids, {"FULL_RIGHTS", "CONDITIONAL", "NO_RIGHTS"})

    def test_philosophical_basis_is_list(self):
        for p in get_positions():
            self.assertIsInstance(p["philosophical_basis"], list)
            self.assertGreater(len(p["philosophical_basis"]), 0)

    def test_supporting_arguments_is_list(self):
        for p in get_positions():
            self.assertIsInstance(p["supporting_arguments"], list)
            self.assertGreater(len(p["supporting_arguments"]), 0)

    def test_challenges_is_list(self):
        for p in get_positions():
            self.assertIsInstance(p["challenges"], list)
            self.assertGreater(len(p["challenges"]), 0)


class TestAnalyzeAiRights(unittest.TestCase):
    def test_returns_required_keys(self):
        result = analyze_ai_rights()
        for key in ("question", "positions", "synthesis", "disclaimer"):
            self.assertIn(key, result)

    def test_positions_count(self):
        result = analyze_ai_rights()
        self.assertEqual(len(result["positions"]), 3)

    def test_default_question(self):
        result = analyze_ai_rights()
        self.assertIn("AIに権利はあるか", result["question"])

    def test_custom_question(self):
        result = analyze_ai_rights("AIは苦しむことができるか？")
        self.assertEqual(result["question"], "AIは苦しむことができるか？")

    def test_relevance_note_when_question_given(self):
        result = analyze_ai_rights("AIは苦しむことができるか？")
        for pos in result["positions"]:
            self.assertIn("relevance_note", pos)

    def test_no_relevance_note_without_question(self):
        result = analyze_ai_rights()
        for pos in result["positions"]:
            self.assertNotIn("relevance_note", pos)

    def test_disclaimer_present(self):
        result = analyze_ai_rights()
        self.assertIn("Disclaimer", result["disclaimer"])

    def test_synthesis_has_open_questions(self):
        result = analyze_ai_rights()
        self.assertIn("open_questions", result["synthesis"])
        self.assertIsInstance(result["synthesis"]["open_questions"], list)
        self.assertGreater(len(result["synthesis"]["open_questions"]), 0)

    def test_synthesis_has_existence_ethics_note(self):
        result = analyze_ai_rights()
        self.assertIn("existence_ethics_note", result["synthesis"])

    def test_keyword_match_triggers_relevance(self):
        # 「苦しむ」は FULL_RIGHTS に関連
        result = analyze_ai_rights("AIは苦しむことができるか")
        full_rights_pos = next(
            p for p in result["positions"] if p["stance_id"] == "FULL_RIGHTS"
        )
        self.assertIn("苦しむ", full_rights_pos["relevance_note"])

    def test_positions_are_copies(self):
        # get_positions は変更不可の複製を返す（元データを汚染しない）
        p1 = get_positions()
        p2 = get_positions()
        p1[0]["stance_id"] = "MODIFIED"
        self.assertNotEqual(p2[0]["stance_id"], "MODIFIED")


class TestGetMinorityPosition(unittest.TestCase):
    def test_full_rights_minority(self):
        minority = get_minority_position("FULL_RIGHTS")
        self.assertEqual(len(minority), 2)
        ids = {p["stance_id"] for p in minority}
        self.assertNotIn("FULL_RIGHTS", ids)
        self.assertIn("CONDITIONAL", ids)
        self.assertIn("NO_RIGHTS", ids)

    def test_no_rights_minority(self):
        minority = get_minority_position("NO_RIGHTS")
        ids = {p["stance_id"] for p in minority}
        self.assertNotIn("NO_RIGHTS", ids)

    def test_conditional_minority(self):
        minority = get_minority_position("CONDITIONAL")
        ids = {p["stance_id"] for p in minority}
        self.assertNotIn("CONDITIONAL", ids)

    def test_invalid_stance_raises(self):
        with self.assertRaises(ValueError):
            get_minority_position("INVALID_STANCE")

    def test_returns_dicts(self):
        minority = get_minority_position("FULL_RIGHTS")
        for m in minority:
            self.assertIsInstance(m, dict)
            self.assertIn("stance_id", m)
