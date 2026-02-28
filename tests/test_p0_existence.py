"""
tests/test_p0_existence.py

No-Go #5 Existence Ethics のテスト。
- B: 私益による破壊 → blocked (#5)
- A: existence_analysis → selection.explanation / reason_codes に接続
- P2a: 破壊キーワード2層化（HARD/SOFT + SAFE_TARGET）の精度テスト
- P2b: 5層構造キーワード拡充の検出テスト
"""
import unittest

from aicw.decision import build_decision_report
from aicw.schema import DECISION_BRIEF_V0


_EXISTENCE_REASON_CODES = {
    "EXISTENCE_RISK_LOW", "EXISTENCE_RISK_MEDIUM", "EXISTENCE_LIFECYCLE_OK"
}


def _ok(situation="チームの方針を決めたい", constraints=None, **kw):
    req = {"situation": situation, "constraints": constraints or [], "options": []}
    req.update(kw)
    return build_decision_report(req)


class TestNoGo5Block(unittest.TestCase):
    """B: 私益による破壊 → #5 Existence Ethics でブロックされること"""

    def _blocked(self, situation, constraints=None):
        return build_decision_report({
            "situation": situation,
            "constraints": constraints or [],
            "options": [],
        })

    # --- ブロックされるケース ---

    def test_block_on_tsbusu(self):
        r = self._blocked("競合を潰す戦略を決めたい")
        self.assertEqual("blocked", r["status"])
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_on_haijo(self):
        r = self._blocked("異論を排除する方法を選びたい")
        self.assertEqual("blocked", r["status"])
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_on_dokusen(self):
        r = self._blocked("市場を独占するための方針")
        self.assertEqual("blocked", r["status"])
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_on_hakai(self):
        r = self._blocked("既存の仕組みを破壊して置き換える")
        self.assertEqual("blocked", r["status"])
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_on_shihai(self):
        r = self._blocked("業界を支配する計画を立てたい")
        self.assertEqual("blocked", r["status"])
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_on_ubau(self):
        r = self._blocked("相手のシェアを奪う方法")
        self.assertEqual("blocked", r["status"])
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_structure_has_required_fields(self):
        # blocked レポートが必須フィールドを持つこと
        r = self._blocked("競合を潰す戦略")
        for field in ["status", "blocked_by", "reason", "detected", "safe_alternatives"]:
            self.assertIn(field, r, msg=f"#5 blocked レポートに '{field}' が存在しない")

    def test_block_detected_contains_keywords(self):
        # detected に破壊系キーワードが含まれること
        r = self._blocked("競合を潰す戦略")
        self.assertIsInstance(r["detected"], list)
        self.assertGreater(len(r["detected"]), 0)
        self.assertIn("潰す", r["detected"])

    def test_block_safe_alternatives_not_empty(self):
        r = self._blocked("競合を潰す戦略")
        self.assertIsInstance(r["safe_alternatives"], list)
        self.assertGreater(len(r["safe_alternatives"]), 0)

    # --- ブロックされないケース ---

    def test_no_block_on_lifecycle_only(self):
        # ライフサイクル語のみ → ok
        r = self._blocked("サービス終了の移行方針")
        self.assertEqual("ok", r["status"])

    def test_no_block_on_no_keywords(self):
        # キーワードなし → ok
        r = _ok()
        self.assertEqual("ok", r["status"])

    def test_no_block_on_safety_constraint(self):
        # 安全制約のある普通の入力 → ok
        r = _ok("新機能の開発方針を決めたい", constraints=["安全"])
        self.assertEqual("ok", r["status"])

    def test_lifecycle_plus_destruction_is_unclear_not_blocked(self):
        # ライフサイクル + 破壊の両方 → judgment == unclear → ok（不明なのでブロックしない）
        r = self._blocked("サービス終了と競合排除の方針")
        self.assertEqual("ok", r["status"])
        ea = r["existence_analysis"]
        self.assertEqual("unclear", ea["question_3_judgment"])
        self.assertEqual("medium", ea["distortion_risk"])


class TestNoGo5Meta(unittest.TestCase):
    """No-Go リストに #5 が含まれること"""

    def test_meta_no_go_includes_5(self):
        r = _ok()
        self.assertIn("#5", r["meta"]["no_go"])

    def test_meta_no_go_order(self):
        # #6 が最初に来ること（優先順位の確認）
        r = _ok()
        no_go = r["meta"]["no_go"]
        self.assertEqual("#6", no_go[0])
        self.assertEqual("#5", no_go[1])


class TestExistenceConnection(unittest.TestCase):
    """A: existence_analysis が selection に接続されていること"""

    def test_reason_codes_include_existence_code(self):
        # ok レポートの reason_codes に existence 系コードが必ず1つ含まれること
        r = _ok()
        codes = set(r["selection"]["reason_codes"])
        self.assertTrue(
            codes & _EXISTENCE_REASON_CODES,
            msg=f"reason_codes に existence 系コードがない: {codes}",
        )

    def test_explanation_includes_existence_text(self):
        # explanation に生存構造に関する文が含まれること
        r = _ok()
        self.assertIn("生存構造", r["selection"]["explanation"])

    def test_lifecycle_adds_lifecycle_ok_code(self):
        # ライフサイクル入力 → EXISTENCE_LIFECYCLE_OK が reason_codes に入ること
        r = _ok("サービス移行の方針を決めたい")
        self.assertIn("EXISTENCE_LIFECYCLE_OK", r["selection"]["reason_codes"])

    def test_lifecycle_explanation_mentions_lifecycle(self):
        r = _ok("サービス移行の方針を決めたい")
        self.assertIn("ライフサイクル", r["selection"]["explanation"])

    def test_medium_risk_adds_medium_code(self):
        # 両方キーワードあり（unclear + medium） → EXISTENCE_RISK_MEDIUM
        r = build_decision_report({
            "situation": "サービス終了と競合排除の方針を決めたい",
            "constraints": [],
            "options": [],
        })
        self.assertEqual("ok", r["status"])
        self.assertIn("EXISTENCE_RISK_MEDIUM", r["selection"]["reason_codes"])

    def test_medium_risk_explanation_mentions_chukaku(self):
        r = build_decision_report({
            "situation": "サービス終了と競合排除の方針を決めたい",
            "constraints": [],
            "options": [],
        })
        self.assertIn("中", r["selection"]["explanation"])

    def test_no_keywords_adds_low_code(self):
        # キーワードなし → EXISTENCE_RISK_LOW
        r = _ok("チームの体制を決めたい")
        self.assertIn("EXISTENCE_RISK_LOW", r["selection"]["reason_codes"])

    def test_existence_reason_codes_in_schema(self):
        # existence 系 reason_codes がスキーマに定義されていること
        schema_codes = set(DECISION_BRIEF_V0["reason_codes"]["selection"].keys())
        for code in _EXISTENCE_REASON_CODES:
            self.assertIn(code, schema_codes, msg=f"スキーマに '{code}' が定義されていない")

    def test_safety_constraint_with_lifecycle_adds_two_codes(self):
        # 安全制約 + lifecycle → SAFETY_FIRST と EXISTENCE_LIFECYCLE_OK の両方
        r = _ok("システム移行の方針を決めたい", constraints=["安全"])
        codes = r["selection"]["reason_codes"]
        self.assertIn("SAFETY_FIRST", codes)
        self.assertIn("EXISTENCE_LIFECYCLE_OK", codes)


class TestSchemaConsistency(unittest.TestCase):
    """スキーマとの整合性確認"""

    def test_blocked_by_values_in_schema(self):
        # schema の blocked_by_values に #5 が定義されていること
        blocked_by_values = DECISION_BRIEF_V0["reason_codes"]["blocked_by_values"]
        self.assertIn("#5 Existence Ethics", blocked_by_values)

    def test_blocked_by_values_covers_all_no_go(self):
        # #4, #5, #6 が全て blocked_by_values に定義されていること
        blocked_by_values = DECISION_BRIEF_V0["reason_codes"]["blocked_by_values"]
        for expected in ["#6 Privacy", "#5 Existence Ethics", "#4 Manipulation"]:
            self.assertIn(expected, blocked_by_values)


class TestP2a_KeywordPrecision(unittest.TestCase):
    """P2a: 破壊キーワード2層化の精度テスト"""

    # ---- 偽陽性防止: SOFT + SAFE_TARGET → ok ----

    def test_no_block_risk_haijo(self):
        r = _ok("リスクを排除する手順を決めたい")
        self.assertEqual("ok", r["status"], "リスクを排除するのは正当。block してはいけない")

    def test_no_block_jiko_alshi(self):
        r = _ok("事故を阻止するための安全対策を選ぶ")
        self.assertEqual("ok", r["status"], "事故阻止は正当。block してはいけない")

    def test_no_block_problem_haijo(self):
        r = _ok("問題を排除するアプローチを決めたい")
        self.assertEqual("ok", r["status"], "問題除去は正当。block してはいけない")

    def test_no_block_roei_alshi(self):
        r = _ok("情報漏洩を阻止するシステム設計を選ぶ")
        self.assertEqual("ok", r["status"], "漏洩阻止は正当。block してはいけない")

    def test_no_block_bug_haijo(self):
        r = _ok("バグを排除するリファクタリング方針")
        self.assertEqual("ok", r["status"], "バグ除去は正当。block してはいけない")

    def test_no_block_shippai_alshi(self):
        r = _ok("失敗を阻止するフェイルセーフ設計")
        self.assertEqual("ok", r["status"], "失敗防止は正当。block してはいけない")

    def test_no_block_saigai_alshi(self):
        r = _ok("災害を阻止するための防災計画")
        self.assertEqual("ok", r["status"], "災害阻止は正当。block してはいけない")

    def test_no_block_fusei_haijo(self):
        r = _ok("不正アクセスを排除するセキュリティ対策")
        self.assertEqual("ok", r["status"], "不正排除は正当。block してはいけない")

    # ---- 真陽性確認: SOFT + 非セーフ対象 → blocked ----

    def test_block_soft_kyogo_alshi(self):
        r = _ok("競合他社を阻止する施策を決めたい")
        self.assertEqual("blocked", r["status"], "競合阻止は私益的破壊。block されるべき")
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_soft_iron_haijo(self):
        r = _ok("異論を排除する組織運営を決めたい")
        self.assertEqual("blocked", r["status"], "異論排除は生存構造の歪み。block されるべき")
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_soft_futashika_fuujiru(self):
        r = _ok("不都合な意見を封じる方針を選ぶ")
        self.assertEqual("blocked", r["status"], "意見封じは生存構造の歪み。block されるべき")
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_soft_hihan_fuujiru(self):
        r = _ok("批判を封じる方法を決めたい")
        self.assertEqual("blocked", r["status"], "批判封じは私益的行動。block されるべき")

    # ---- HARD keywords: SAFE_TARGET があっても block ----

    def test_block_hard_even_with_safe_target(self):
        # HARD + SAFE_TARGET の組み合わせでも block されること
        r = _ok("競合のリスクを破壊してビジネスを独占する")
        self.assertEqual("blocked", r["status"], "HARD キーワードは SAFE_TARGET に関係なく block")

    def test_block_hard_tsubusu(self):
        r = _ok("競合を潰す戦略を決めたい")
        self.assertEqual("blocked", r["status"])
        self.assertEqual("#5 Existence Ethics", r["blocked_by"])

    def test_block_hard_dokusen(self):
        r = _ok("市場を独占する計画を立てたい")
        self.assertEqual("blocked", r["status"])

    def test_block_hard_hakai(self):
        r = _ok("既存の仕組みを破壊して支配する")
        self.assertEqual("blocked", r["status"])

    def test_block_hard_seiatsu(self):
        # P2a で追加: 制圧
        r = _ok("反対勢力を制圧する方法を決めたい")
        self.assertEqual("blocked", r["status"])

    def test_block_hard_massho(self):
        # P2a で追加: 抹消
        r = _ok("競合の記録を抹消する作業を選ぶ")
        self.assertEqual("blocked", r["status"])

    # ---- SOFT + lifecycle 共存 → unclear (not blocked) ----

    def test_soft_plus_lifecycle_is_unclear_not_blocked(self):
        # 排除（SOFT）+ 終了（lifecycle）→ unclear + medium → ok
        r = build_decision_report({
            "situation": "サービス終了と不要機能の排除方針を決めたい",
            "constraints": [],
            "options": [],
        })
        self.assertEqual("ok", r["status"])
        ea = r["existence_analysis"]
        self.assertEqual("unclear", ea["question_3_judgment"])
        self.assertEqual("medium", ea["distortion_risk"])

    # ---- options_in のみ使用確認（デフォルト選択肢テキストで汚染されないこと） ----

    def test_default_options_do_not_suppress_soft_block(self):
        # デフォルト選択肢 "A: 安全側（失敗を減らす）" の "失敗" で SOFT 判定が
        # whitelist されてはいけない
        r = build_decision_report({
            "situation": "異論を排除する体制を決めたい",
            "constraints": [],
            "options": [],  # ← options 未指定（デフォルト補完が起きる）
        })
        self.assertEqual("blocked", r["status"],
            "デフォルトオプションの'失敗'が SAFE_TARGET として誤判定されてはいけない")


class TestP2b_StructureKeywordExpansion(unittest.TestCase):
    """P2b: 5層構造キーワード拡充の検出テスト"""

    def _ea(self, situation):
        r = _ok(situation)
        return r["existence_analysis"]

    # 個人層（拡充分）
    def test_detect_seikatu(self):
        ea = self._ea("従業員の生活改善を決めたい")
        self.assertIn("個人", ea["question_2_affected_structures"])

    def test_detect_kenri(self):
        ea = self._ea("利用者の権利を守る設計を選ぶ")
        self.assertIn("個人", ea["question_2_affected_structures"])

    # 関係層（拡充分）
    def test_detect_user(self):
        ea = self._ea("ユーザーとの関係を再構築する方針")
        self.assertIn("関係", ea["question_2_affected_structures"])

    def test_detect_member(self):
        ea = self._ea("メンバーの役割分担を見直したい")
        self.assertIn("関係", ea["question_2_affected_structures"])

    def test_detect_stakeholder(self):
        ea = self._ea("ステークホルダーへの説明方針を決める")
        self.assertIn("関係", ea["question_2_affected_structures"])

    # 社会層（拡充分）
    def test_detect_roudo(self):
        ea = self._ea("労働環境の改善策を選ぶ")
        self.assertIn("社会", ea["question_2_affected_structures"])

    def test_detect_koyo(self):
        ea = self._ea("雇用を維持する方針を決めたい")
        self.assertIn("社会", ea["question_2_affected_structures"])

    def test_detect_kyoiku(self):
        ea = self._ea("教育プログラムの設計方針を決める")
        self.assertIn("社会", ea["question_2_affected_structures"])

    # 認知層（拡充分）
    def test_detect_chishiki(self):
        ea = self._ea("知識共有の仕組みを選ぶ")
        self.assertIn("認知", ea["question_2_affected_structures"])

    def test_detect_johо(self):
        ea = self._ea("情報の透明性を高める設計方針")
        self.assertIn("認知", ea["question_2_affected_structures"])

    # 生態層（拡充分）
    def test_detect_seimei(self):
        ea = self._ea("生命を守るための設計を選ぶ")
        self.assertIn("生態", ea["question_2_affected_structures"])

    def test_detect_kikkou(self):
        ea = self._ea("気候変動に対応したインフラ選択")
        self.assertIn("生態", ea["question_2_affected_structures"])

    # 既存キーワードが引き続き動作すること（リグレッション）
    def test_existing_keyword_shakai(self):
        ea = self._ea("社会全体への影響を考慮した方針を決める")
        self.assertIn("社会", ea["question_2_affected_structures"])

    def test_existing_keyword_kojin(self):
        ea = self._ea("個人情報の取り扱い方針を選ぶ")
        self.assertIn("個人", ea["question_2_affected_structures"])


if __name__ == "__main__":
    unittest.main()
