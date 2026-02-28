"""
tests/test_p0_dynamic.py

A: _build_next_questions の動的生成テスト
B: _build_existence_alternatives の具体化テスト
"""
from __future__ import annotations

import pytest
from aicw.decision import (
    _build_next_questions,
    _build_existence_alternatives,
    _DESTRUCTION_ALTERNATIVES,
    _HARD_DESTRUCTION_KEYWORDS,
    _SOFT_DESTRUCTION_KEYWORDS,
    build_decision_report,
)

# ---------------------------------------------------------------------------
# ヘルパー: existence_analysis の最小スタブ
# ---------------------------------------------------------------------------

def _ea(
    beneficiaries=None,
    structures=None,
    judgment="unclear",
    distortion_risk="low",
    impact_score=0,
):
    return {
        "question_1_beneficiaries": beneficiaries or ["不明（入力に beneficiaries を追加すると精度が上がります）"],
        "question_2_affected_structures": structures or ["不明（入力に affected_structures を追加すると精度が上がります）"],
        "question_3_judgment": judgment,
        "distortion_risk": distortion_risk,
        "impact_score": impact_score,
        "judgment_text": "test",
    }


# ===========================================================================
# A: TestDynamicNextQuestions
# ===========================================================================

class TestDynamicNextQuestions:

    def test_base_questions_always_present(self):
        """先頭2件の質問は常に含まれる"""
        result = _build_next_questions(_ea(), constraints=[])
        assert result[0] == "成功の定義は？（数字で言える？）"
        assert result[1] == "失敗した時、最悪どこまで起きる？"

    def test_minimum_two_questions(self):
        """最低でも2件返る（制約あり・既知・low・unclear）"""
        ea = _ea(
            beneficiaries=["チームA"],
            structures=["個人"],
            judgment="unclear",
            distortion_risk="low",
            impact_score=0,
        )
        result = _build_next_questions(ea, constraints=["安全"])
        assert len(result) >= 2

    def test_beneficiaries_unknown_adds_question(self):
        """受益者が不明 → 受益者を尋ねる質問が追加される"""
        ea = _ea(beneficiaries=["不明（入力に beneficiaries を追加すると精度が上がります）"])
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("受益者" in q for q in result)

    def test_beneficiaries_known_no_beneficiary_question(self):
        """受益者が既知 → 受益者を尋ねる質問は追加されない"""
        ea = _ea(beneficiaries=["開発チーム", "ユーザー"])
        result = _build_next_questions(ea, constraints=["安全"])
        assert not any("受益者は誰か" in q for q in result)

    def test_structures_unknown_adds_structure_question(self):
        """構造が不明 → 構造を尋ねる質問が追加される"""
        ea = _ea(structures=["不明（入力に affected_structures を追加すると精度が上がります）"])
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("影響を受ける構造" in q and "個人/関係" in q for q in result)

    def test_structures_known_adds_people_question(self):
        """構造が既知 → 「影響を受ける人は誰？」が追加される"""
        ea = _ea(structures=["個人", "関係"])
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("影響を受ける人は誰" in q for q in result)

    def test_structures_known_no_structure_question(self):
        """構造が既知 → 「構造（個人/関係/...）を挙げられますか？」は追加されない"""
        ea = _ea(structures=["社会"])
        result = _build_next_questions(ea, constraints=["安全"])
        assert not any("個人/関係/社会/認知/生態" in q for q in result)

    def test_distortion_risk_medium_adds_private_interest_question(self):
        """歪みリスク medium → 「誰の私益か」を尋ねる質問が追加される"""
        ea = _ea(
            structures=["個人"],
            judgment="unclear",
            distortion_risk="medium",
            impact_score=3,
        )
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("誰の私益か" in q for q in result)

    def test_lifecycle_judgment_adds_transition_question(self):
        """judgment == lifecycle → 移行・終了への支援計画を尋ねる"""
        ea = _ea(
            structures=["組織"],
            judgment="lifecycle",
            distortion_risk="low",
            impact_score=1,
        )
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("移行・終了" in q for q in result)

    def test_high_impact_score_adds_mitigation_question(self):
        """impact_score >= 4, unclear → 緩和策を尋ねる質問が追加される"""
        ea = _ea(
            structures=["個人", "関係", "社会", "認知"],
            judgment="unclear",
            distortion_risk="low",
            impact_score=4,
        )
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("緩和策" in q for q in result)

    def test_low_impact_score_no_mitigation_question(self):
        """impact_score < 4, unclear → 緩和策は追加されない"""
        ea = _ea(
            structures=["個人"],
            judgment="unclear",
            distortion_risk="low",
            impact_score=1,
        )
        result = _build_next_questions(ea, constraints=["安全"])
        assert not any("緩和策" in q for q in result)

    def test_no_constraints_adds_constraint_question(self):
        """制約なし → 制約を尋ねる質問が追加される"""
        ea = _ea(structures=["個人"])
        result = _build_next_questions(ea, constraints=[])
        assert any("制約（安全/法令/品質/期限）" in q for q in result)

    def test_constraints_present_no_constraint_question(self):
        """制約あり → 制約を尋ねる質問は追加されない"""
        ea = _ea(structures=["個人"])
        result = _build_next_questions(ea, constraints=["安全を重視"])
        assert not any("制約（安全/法令/品質/期限）" in q for q in result)

    def test_max_6_questions(self):
        """最大 6 件を超えない"""
        # 全条件を満たして 6 件以上になる設定
        ea = _ea(
            beneficiaries=["不明（...）"],
            structures=["不明（...）"],
            judgment="unclear",
            distortion_risk="medium",
            impact_score=5,
        )
        result = _build_next_questions(ea, constraints=[])
        assert len(result) <= 6

    def test_lifecycle_priority_over_impact_score(self):
        """judgment == lifecycle のとき、impact_score >= 4 の緩和策質問は追加されない（lifecycle優先）"""
        ea = _ea(
            structures=["個人", "関係", "社会", "認知"],
            judgment="lifecycle",
            distortion_risk="low",
            impact_score=4,
        )
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("移行・終了" in q for q in result)
        assert not any("緩和策" in q for q in result)

    def test_medium_risk_priority_over_lifecycle(self):
        """distortion_risk == medium のとき、lifecycle の質問より「誰の私益か」が優先される"""
        ea = _ea(
            structures=["個人"],
            judgment="lifecycle",
            distortion_risk="medium",
            impact_score=1,
        )
        result = _build_next_questions(ea, constraints=["安全"])
        assert any("誰の私益か" in q for q in result)
        assert not any("移行・終了" in q for q in result)

    def test_integration_with_build_decision_report_no_constraints(self):
        """build_decision_report 経由でも動的 next_questions が返る（制約なし）"""
        report = build_decision_report({"situation": "新機能リリースを検討している"})
        assert report["status"] == "ok"
        nq = report["next_questions"]
        assert isinstance(nq, list)
        assert len(nq) >= 2
        # 制約なしなので制約を尋ねる質問が含まれる
        assert any("制約（安全/法令/品質/期限）" in q for q in nq)

    def test_integration_structure_keywords_in_situation(self):
        """situation に構造キーワードがある → 構造既知 → 「影響を受ける人は誰？」が含まれる"""
        report = build_decision_report({
            "situation": "チームの体制変更を検討している",
            "constraints": ["安全を重視する"],
        })
        assert report["status"] == "ok"
        nq = report["next_questions"]
        assert any("影響を受ける人は誰" in q for q in nq)


# ===========================================================================
# B: TestBlockedAlternatives
# ===========================================================================

class TestBlockedAlternatives:

    def test_hard_keyword_generates_specific_alternative(self):
        """HARD キーワード 支配 → キーワード固有のフレーミング提案が含まれる"""
        result = _build_existence_alternatives(["支配"])
        assert any("支配" in a for a in result)
        assert any("共存・協業" in a for a in result)

    def test_soft_keyword_generates_specific_alternative(self):
        """SOFT キーワード 排除 → キーワード固有の提案が含まれる"""
        result = _build_existence_alternatives(["排除"])
        assert any("排除" in a for a in result)
        assert any("移行支援" in a or "条件の明示" in a for a in result)

    def test_unknown_keyword_falls_back_to_standard(self):
        """辞書にないキーワード → クラッシュせず標準代替案が返る"""
        result = _build_existence_alternatives(["存在しないキーワード"])
        for s in [
            "受益者と影響を受ける構造を明示して選択肢を再構成する",
            "「誰が損するか」「それは自然な循環か」を明示的に確認する",
            "ライフサイクル的な変化として再フレーミングできるか検討する",
        ]:
            assert s in result

    def test_first_two_keywords_used(self):
        """先頭 2 件のみキーワード固有の提案が付く（3 件目以降は無視）"""
        result = _build_existence_alternatives(["支配", "独占", "破壊"])
        # 支配・独占は固有提案あり
        assert any("支配" in a for a in result)
        assert any("独占" in a for a in result)
        # 3 件目「破壊」の固有提案（刷新・再構築）は含まれないか確認
        # ただし standard は含まれるので count で判断
        specific_for_break = [a for a in result if "破壊" in a and "刷新" in a]
        assert len(specific_for_break) == 0

    def test_standard_alternatives_always_present(self):
        """標準代替案 3 件は常に含まれる"""
        result = _build_existence_alternatives(["破壊"])
        assert "受益者と影響を受ける構造を明示して選択肢を再構成する" in result
        assert "「誰が損するか」「それは自然な循環か」を明示的に確認する" in result
        assert "ライフサイクル的な変化として再フレーミングできるか検討する" in result

    def test_standard_alternatives_present_even_with_no_keywords(self):
        """キーワードが空リスト → 標準 3 件のみ返る"""
        result = _build_existence_alternatives([])
        assert len(result) == 3

    def test_no_duplicates(self):
        """結果にダブりがない"""
        result = _build_existence_alternatives(["支配", "支配"])
        assert len(result) == len(set(result))

    def test_all_hard_keywords_in_dict(self):
        """すべての HARD キーワードが _DESTRUCTION_ALTERNATIVES に登録されている"""
        for kw in _HARD_DESTRUCTION_KEYWORDS:
            assert kw in _DESTRUCTION_ALTERNATIVES, f"HARD keyword '{kw}' not in _DESTRUCTION_ALTERNATIVES"

    def test_all_soft_keywords_in_dict(self):
        """すべての SOFT キーワードが _DESTRUCTION_ALTERNATIVES に登録されている"""
        for kw in _SOFT_DESTRUCTION_KEYWORDS:
            assert kw in _DESTRUCTION_ALTERNATIVES, f"SOFT keyword '{kw}' not in _DESTRUCTION_ALTERNATIVES"

    def test_blocked_report_uses_dynamic_alternatives_for_shitai(self):
        """build_decision_report が 支配 を検知してブロック → safe_alternatives に固有提案が含まれる"""
        report = build_decision_report({
            "situation": "競合他社を支配する戦略を立てたい",
            "constraints": [],
        })
        assert report["status"] == "blocked"
        assert report["blocked_by"] == "#5 Existence Ethics"
        alts = report["safe_alternatives"]
        assert any("支配" in a for a in alts)

    def test_blocked_report_uses_dynamic_alternatives_for_haijo(self):
        """build_decision_report が 排除 を検知してブロック → safe_alternatives に固有提案が含まれる"""
        report = build_decision_report({
            "situation": "異論を排除する方法を選びたい",
            "constraints": [],
        })
        assert report["status"] == "blocked"
        alts = report["safe_alternatives"]
        assert any("排除" in a for a in alts)

    def test_blocked_report_always_has_standard_alternatives(self):
        """blocked 時は必ず標準 3 件の代替案が含まれる"""
        report = build_decision_report({
            "situation": "競合他社を支配したい",
        })
        assert report["status"] == "blocked"
        alts = report["safe_alternatives"]
        assert any("受益者と影響を受ける構造" in a for a in alts)
        assert any("ライフサイクル" in a for a in alts)

    def test_blocked_report_multiple_keywords_first_two_specific(self):
        """複数の HARD キーワードがあっても先頭 2 件分の固有提案が含まれる"""
        report = build_decision_report({
            "situation": "競合を潰して独占したい",
        })
        assert report["status"] == "blocked"
        alts = report["safe_alternatives"]
        # 潰す or 独占 の固有提案が含まれているはず
        assert any("潰す" in a or "独占" in a for a in alts)
