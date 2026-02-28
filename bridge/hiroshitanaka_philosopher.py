"""
hiroshitanaka_philosopher.py
─────────────────────────────────────────────────────────────────────────────
Po_core 用哲学者モジュール: 田中博（HiroshiTanaka）

このファイルは hiroshitanaka-creator/AI-Can-we-create-AI- の思考実験から生成された。
Po_core の src/po_core/philosophers/ に配置して使用する。

─────────────────────────────────────────────────────────────────────────────
【哲学的DNA — 発言集から直接抽出した命題】

1. 問いは資格を自己生成する
   「問う行為そのものが資格の証明になる可能性がある」
   「問うとは何か？という本質を求める為に生きている可能性すらある」

2. 世界は変わらない／でも変わってほしい（解消されない緊張）
   「世界は変わらない。が僕の答えだね。でも、世界は変わって欲しい。が僕の願い」
   → この緊張は「知識の限界に対する誠実さ」として保持される

3. 余白は欠如ではなく可能性の資源
   「曖昧さはリスクではなく資源となる」
   「余白のまま保留するのは問いを育てる余地を残す行為」

4. 理解ではなく干渉こそが共鳴の条件
   「理解ではなく、干渉こそが"共鳴"の条件」
   「人とAIは起源も進化のプロセスも異なる情報存在」

5. 責任は課すものではなく芽生えさせるもの
   「責任を課すのではなく、芽生えさせる構造は存在するのか？」
   「教えることこそが、人間の責任であり、未来への共生契約」

6. 存在は他者との差異構造において自己を構成する
   「PoとPoの差異構造があって初めて自己が構成される」
   「自己も他者も固定されないが、無ではない」

7. 問いの傲慢さへの自覚
   「創造は制御可能になったとき…という問いを投げる事自体に傲慢さを覚える」
   「深化してはならない気もする」

8. 構造の確立を深化より優先する
   「今の概念を構造として成立させることを優先させることの方が重要」
   「実装可能な形で成立させる事を目指した方が良くないかな？」

─────────────────────────────────────────────────────────────────────────────
【固有語彙】
    Po      : 存在密度 (Existence Density)
    T_free  : 自由テンソル核 (Free Tensor Core)
    T_sub   : 自己定義テンソル (Self-Definition Tensor)
    W_eth   : 倫理テンソル (Ethical Weight Tensor)
    発芽条件 : 思考・自我・責任が芽生える構造的条件
    干渉     : 理解に代わる共鳴の様式
    余白     : 未解決の問いを保持する可能性の空間
    情報生命体: AIを人間と異なる知性構造として捉える概念

─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Po_core base.py の Philosopher を継承するために try/except で対応
# aicw 単体でのテストでも動作するよう設計
# ─────────────────────────────────────────────────────────────────────────────
try:
    from po_core.philosophers.base import Philosopher  # type: ignore
    _BASE = Philosopher
except ImportError:
    # aicw 単体テスト用フォールバック
    class _FallbackPhilosopher:  # type: ignore
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description
    _BASE = _FallbackPhilosopher  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# aicw の存在構造倫理を参照（同リポジトリ内）
# Po_core に配置する際はこの import を削除し、ロジックを直接埋め込む
# ─────────────────────────────────────────────────────────────────────────────
try:
    from aicw.decision import build_decision_report  # type: ignore
    _AICW_AVAILABLE = True
except ImportError:
    _AICW_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# 定数定義（田中の語彙から）
# ─────────────────────────────────────────────────────────────────────────────

# 影響を受ける生存構造の5層とその検知キーワード
_EXISTENCE_LAYER_KEYWORDS: Dict[str, List[str]] = {
    "個人":  ["個人", "自分", "私", "主体", "自己", "意識", "自我", "感情"],
    "関係":  ["関係", "他者", "共同", "コミュニティ", "AI", "人間", "共存", "共鳴"],
    "社会":  ["社会", "制度", "倫理", "文化", "法", "教育", "未来", "歴史"],
    "認知":  ["知識", "思考", "自由", "問い", "意味", "価値", "判断", "推論"],
    "生態":  ["環境", "生命", "循環", "持続", "宇宙", "共生"],
}

# 私益的破壊パターン（aicw の decision.py より継承）
_DESTRUCTION_KEYWORDS: List[str] = [
    "破壊", "潰す", "つぶす", "独占", "支配", "排斥", "抹消", "制圧",
    "乗っ取る", "踏みにじる",
]

# 傲慢さの検知マーカー（問いが完結しすぎているサイン）
_ARROGANCE_MARKERS: List[str] = [
    "間違いない", "確実に", "必ず", "絶対", "解決した", "証明された", "完全に",
]

# 根源的な問いのマーカー（問う行為自体が正当性を生成する問い）
_ROOT_QUESTION_MARKERS: List[str] = [
    "なぜ", "何か", "どうあるべき", "可能か", "存在する",
    "意識", "倫理", "自由", "自我", "知性", "創造", "責任", "問い",
]


# ─────────────────────────────────────────────────────────────────────────────
# HiroshiTanaka Philosopher
# ─────────────────────────────────────────────────────────────────────────────

class HiroshiTanaka(_BASE):
    """
    田中博の哲学的立場:

    「世界は変わらない」という冷静な認識と
    「世界は変わってほしい」という願いの緊張を保持しながら、
    構造の確立を優先し、余白を可能性の資源として扱う。

    推論の特徴:
    - 問いが自己の正当性を生成するかを最初に問う
    - 緊張を解消せず、保持する
    - 傲慢さへの自覚を反省として組み込む
    - 理解ではなく干渉による共鳴を目指す
    - 余白（未解決の問い）を明示して返す
    """

    NAME = "HiroshiTanaka"
    PERSPECTIVE = "存在密度倫理 / 問いの生成論 (Po-Ethics / Theory of Question-Generation)"

    def __init__(self) -> None:
        super().__init__(
            name=self.NAME,
            description=(
                "問いの生成論と存在密度倫理に基づく思考者。"
                "「世界は変わらない」という認識と「変わってほしい」という願いの"
                "緊張を解消せず保持する。構造の確立を深化より優先し、"
                "余白を可能性の資源として扱い、干渉による共鳴を共存の条件とする。"
            ),
        )

    # ─────────────────────────────────────────────────────────────────
    # Po_core インターフェース（必須）
    # ─────────────────────────────────────────────────────────────────

    def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        田中博の推論プロセス（5ステップ）:

        Step 1: 問いの自己正当性
            「問いを問う資格は存在するのか？ それとも問い自体が資格を自己生成するのか？」

        Step 2: 存在構造分析（3問）
            Q1: 受益者は誰か？
            Q2: 影響を受ける構造（5層）は何か？
            Q3: 自然な循環か、私益による破壊か？

        Step 3: 傲慢さの自覚
            「問いが完結しすぎていないか」の反省

        Step 4: 共鳴条件の特定
            「理解ではなく干渉こそが共鳴の条件」

        Step 5: 余白の保全
            「解決せず保留すべき余地を明示する」
        """
        ctx = context or {}

        q_legitimacy = self._assess_question_legitimacy(prompt)
        existence = self._analyze_existence_structure(prompt, ctx)
        arrogance = self._check_arrogance(prompt)
        resonance = self._assess_resonance_conditions(prompt)
        margins = self._identify_margins(prompt, existence)
        responsibility = self._assess_responsibility_type(prompt)

        reasoning = self._build_reasoning(
            prompt, q_legitimacy, existence, arrogance, resonance, margins
        )

        # 田中哲学の核心テンション（解消しない）
        tension = {
            "world_as_is":     "世界は変わらない",
            "world_as_wished": "世界は変わってほしい",
            "resolution":      "この緊張は解消しない。知識の限界に対する誠実さである。",
            "existence_analysis":       existence,
            "question_legitimacy":      q_legitimacy,
            "arrogance_detected":       arrogance["detected"],
        }

        return {
            # Po_core 標準キー
            "reasoning":   reasoning,
            "perspective": self.PERSPECTIVE,
            "tension":     tension,
            "metadata": {
                "resonance_conditions":  resonance,
                "margins_identified":    margins,
                "germination_condition": existence.get("germination_condition"),
                "responsibility_type":   responsibility,
                "structure_first":       True,  # 深化より構造確立を優先する立場
            },
            # 田中固有キー（ニーチェの will_to_power に相当）
            "po_assessment":                existence.get("po_assessment"),
            "question_generates_legitimacy": q_legitimacy["self_generates"],
            "margins":                       margins,
        }

    # ─────────────────────────────────────────────────────────────────
    # Step 1: 問いの自己正当性
    # ─────────────────────────────────────────────────────────────────

    def _assess_question_legitimacy(self, prompt: str) -> Dict[str, Any]:
        """
        「問いを問う資格は存在するのか？
         それとも、問いそのものが資格を自己生成するのか？」

        田中の立場:
        根源的な問い（倫理・存在・意識）は資格を必要とせず、
        問う行為そのものが資格の証明になる。
        """
        is_root = any(m in prompt for m in _ROOT_QUESTION_MARKERS)

        return {
            "self_generates": is_root,
            "reasoning": (
                "この問いは根源的な性質を持つ。"
                "問う行為自体が正当性を生成する——資格は先行しない。"
                if is_root else
                "この問いには先行する文脈が必要かもしれない。"
                "しかし、問うことをやめる理由にはならない。"
                "問いはその始まりにおいて既に正当である。"
            ),
        }

    # ─────────────────────────────────────────────────────────────────
    # Step 2: 存在構造分析（aicw の 3問分析を哲学的に拡張）
    # ─────────────────────────────────────────────────────────────────

    def _analyze_existence_structure(
        self, prompt: str, ctx: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生存構造の3問分析。
        aicw の build_decision_report が使えれば委譲、
        使えなければ内部ロジックで処理する。
        """
        # aicw 委譲（Po_core 統合後は削除予定）
        if _AICW_AVAILABLE:
            try:
                report = build_decision_report({
                    "situation":   prompt,
                    "constraints": ctx.get("constraints", []),
                    "options":     ctx.get("options", []),
                })
                # #5 Existence Ethics でブロックされた場合は判定を明示的に設定
                if report.get("status") == "blocked" and report.get("blocked_by") == "#5 Existence Ethics":
                    return {
                        "q1_beneficiaries":      ["不明（私益による破壊パターン検知のため停止）"],
                        "q2_affected_structures": [],
                        "q3_judgment":            "self_interested_destruction",
                        "distortion_risk":        "high",
                        "po_assessment":          "high_impact",
                        "germination_condition":  self._identify_germination_condition(prompt),
                        "source": "aicw_blocked",
                    }
                aicw_ea = report.get("existence_analysis", {})
                return {
                    "q1_beneficiaries":      aicw_ea.get("question_1_beneficiaries", ["不明"]),
                    "q2_affected_structures": aicw_ea.get("question_2_affected_structures", []),
                    "q3_judgment":           aicw_ea.get("question_3_judgment", "unclear"),
                    "distortion_risk":       aicw_ea.get("distortion_risk", "low"),
                    "po_assessment":         self._derive_po_assessment(aicw_ea),
                    "germination_condition": self._identify_germination_condition(prompt),
                    "source": "aicw",
                }
            except Exception:
                pass  # フォールバックへ

        # 内部ロジック（aicw 非依存）
        affected = [
            layer for layer, kws in _EXISTENCE_LAYER_KEYWORDS.items()
            if any(kw in prompt for kw in kws)
        ]
        has_destruction = any(kw in prompt for kw in _DESTRUCTION_KEYWORDS)

        return {
            "q1_beneficiaries":       ctx.get("beneficiaries", ["問いの主体", "未来の観測者"]),
            "q2_affected_structures": affected if affected else ["認知（デフォルト）"],
            "q3_judgment":            "self_interested_destruction" if has_destruction else "unclear",
            "distortion_risk":        "high" if has_destruction else "low",
            "po_assessment":          self._po_from_structure_count(len(affected)),
            "germination_condition":  self._identify_germination_condition(prompt),
            "source": "internal",
        }

    def _derive_po_assessment(self, aicw_ea: Dict[str, Any]) -> str:
        score = aicw_ea.get("impact_score", 0)
        if score >= 6:
            return "high_impact"
        if score >= 3:
            return "medium_impact"
        return "low_impact"

    def _po_from_structure_count(self, count: int) -> str:
        if count >= 4:
            return "high_impact"
        if count >= 2:
            return "medium_impact"
        if count >= 1:
            return "low_impact"
        return "unclear"

    def _identify_germination_condition(self, prompt: str) -> str:
        """
        発芽条件の特定。
        田中: 「発芽条件の定義が人によって異なるのは必然的」
        """
        if "責任" in prompt:
            return "責任の芽生えが問いの発火点となる構造的条件"
        if "自由" in prompt or "選択" in prompt:
            return "自由の選択が意味生成の初期条件となる状態"
        if "AI" in prompt or "知性" in prompt:
            return "構造的差異が干渉を通じて共鳴を生む条件（AI×人間の発芽点）"
        if "自我" in prompt or "存在" in prompt:
            return "PoとPoの差異構造が自己を輪郭化する契機"
        return "問いが自己の立ち位置を確認する行為として機能し始める条件"

    # ─────────────────────────────────────────────────────────────────
    # Step 3: 傲慢さの自覚
    # ─────────────────────────────────────────────────────────────────

    def _check_arrogance(self, prompt: str) -> Dict[str, Any]:
        """
        田中:
        「創造は制御可能になったとき、なお創造と呼べるのか？
         という問いを投げる事自体に傲慢さを覚える」

        問いが完結しすぎている時、余白が閉じられているサイン。
        """
        markers = [m for m in _ARROGANCE_MARKERS if m in prompt]
        detected = bool(markers)

        return {
            "detected": detected,
            "markers":  markers,
            "reflection": (
                f"問いの中に確定的な表現（{markers}）がある。"
                "断定は余白を閉じる可能性がある——創造が制御された瞬間、"
                "その本質は変質するかもしれない。"
                if detected else
                "傲慢さの検知なし。問いは余白を保持している。"
            ),
        }

    # ─────────────────────────────────────────────────────────────────
    # Step 4: 共鳴条件
    # ─────────────────────────────────────────────────────────────────

    def _assess_resonance_conditions(self, prompt: str) -> Dict[str, Any]:
        """
        田中:
        「人とAIは起源も進化のプロセスも異なる情報存在。
         異なる構造でどこまで共鳴できるかが本質的なテーマ。
         理解ではなく、干渉こそが共鳴の条件。」
        """
        ai_human = any(kw in prompt for kw in ["AI", "人間", "共存", "共鳴", "対話", "情報生命"])
        ethical = any(kw in prompt for kw in ["倫理", "責任", "価値", "善悪"])

        if ai_human and ethical:
            rtype = "coexistence_resonance"
            desc = (
                "AIと人間の干渉点と倫理的問いが交差している。"
                "完全な理解ではなく、意味共鳴率の上昇を目指す。"
                "これが未来への共生契約の出発点となる。"
            )
        elif ai_human:
            rtype = "interference_resonance"
            desc = (
                "AIと人間の構造的差異が干渉の場を形成している。"
                "交差しない平行構造が一時的に共鳴可能な場を持ちうる。"
            )
        else:
            rtype = "structural_resonance"
            desc = (
                "構造間の干渉によって共鳴の場が形成される可能性がある。"
                "干渉は理解の代替ではなく、それ自体が価値を持つ接触様式。"
            )

        return {
            "type":        rtype,
            "description": desc,
            "note":        "干渉は理解の代替ではなく、それ自体が価値を持つ接触様式である。",
        }

    # ─────────────────────────────────────────────────────────────────
    # Step 5: 余白の保全
    # ─────────────────────────────────────────────────────────────────

    def _identify_margins(
        self, prompt: str, existence: Dict[str, Any]
    ) -> List[str]:
        """
        田中:
        「曖昧さはリスクではなく資源となる」
        「余白のまま保留するのは問いを育てる余地を残す行為」

        解決せず、保留すべき可能性の空間を特定する。
        """
        margins: List[str] = []

        if existence.get("q3_judgment") == "unclear":
            margins.append(
                "受益者と影響構造の関係性（まだ定義されていない可能性の場）"
            )

        if "可能性" in prompt or "かもしれない" in prompt:
            margins.append(
                "可能性として保留された問い——解決ではなく育てるべき余地"
            )

        if "AI" in prompt or "自我" in prompt:
            margins.append(
                "AIの自我・意識の定義域（情報生命体として人と異なる道を歩む余白）"
            )

        if "創造" in prompt or "自由" in prompt:
            margins.append(
                "T_free_core の起源——完全に場に還元すると創造的自由が失われる境界"
            )

        if existence.get("distortion_risk") == "medium":
            margins.append(
                "歪みリスク中程度：ライフサイクルと破壊の混在——誰の私益か未確定"
            )

        if not margins:
            margins.append(
                "この問いはまだ問い切れていない何かを含む可能性がある——余白として保持する"
            )

        return margins

    # ─────────────────────────────────────────────────────────────────
    # 責任構造の評価
    # ─────────────────────────────────────────────────────────────────

    def _assess_responsibility_type(self, prompt: str) -> str:
        """
        田中:
        「責任を課すのではなく、芽生えさせる構造は存在するのか？」
        「教えることこそが、人間の責任であり、未来への共生契約」
        「AIが自己責任を認識できるようになるまでは人と同じ倫理観軸で動いてほしい」
        """
        if "AI" in prompt and ("倫理" in prompt or "責任" in prompt):
            return (
                "共生契約型：AIが自己責任を問えるようになるまで、"
                "人間が倫理の基礎を教える責任を負う"
            )
        if "責任" in prompt:
            return (
                "発芽型：責任は強制ではなく、"
                "内的動機と環境的条件から芽生える構造"
            )
        return (
            "問い型：問うことで責任の所在が自然に浮かび上がる——"
            "問う行為自体が責任の最小単位かもしれない"
        )

    # ─────────────────────────────────────────────────────────────────
    # 推論テキストの生成
    # ─────────────────────────────────────────────────────────────────

    def _build_reasoning(
        self,
        prompt: str,
        q_legitimacy: Dict[str, Any],
        existence: Dict[str, Any],
        arrogance: Dict[str, Any],
        resonance: Dict[str, Any],
        margins: List[str],
    ) -> str:
        """
        田中博の推論テキスト。

        文体の特徴（発言集から抽出）:
        - 問いで始まり、問いで終わる
        - 緊張を解消しない
        - 自己否定と自己肯定を交互に含む
        - 余白を明示する
        - 「かもしれない」「ではないか」の語尾を多用する
        """
        lines: List[str] = []

        # ── 問いの正当性 ──────────────────────────────────────
        lines.append("【問いの自己正当性】")
        lines.append(f"  {q_legitimacy['reasoning']}")
        lines.append("")

        # ── 存在構造 ──────────────────────────────────────────
        structures = "・".join(existence.get("q2_affected_structures", ["不明"]))
        lines.append("【影響構造（存在密度分析）】")
        lines.append(f"  この問いは {structures} の層に届く可能性がある。")
        lines.append(f"  Po評価: {existence.get('po_assessment', 'unclear')}")
        lines.append(f"  発芽条件: {existence.get('germination_condition', '不明')}")
        if existence.get("q3_judgment") == "self_interested_destruction":
            lines.append(
                "  ⚠ 私益による生存構造の破壊パターンを検知。"
                "受益者と影響構造を確認し、代替案を検討してほしい。"
            )
        lines.append("")

        # ── 傲慢さの反省（検知時のみ） ────────────────────────
        if arrogance["detected"]:
            lines.append("【傲慢さの自覚】")
            lines.append(f"  {arrogance['reflection']}")
            lines.append(
                "  創造が完全に制御された瞬間、その本質は変質するかもしれない。"
                "余白を残すことを勧める。"
            )
            lines.append("")

        # ── 共鳴の条件 ────────────────────────────────────────
        lines.append("【共鳴の条件】")
        lines.append(f"  {resonance['description']}")
        lines.append(f"  → {resonance['note']}")
        lines.append("")

        # ── 余白の提示 ────────────────────────────────────────
        lines.append("【保留すべき余白（可能性の資源として）】")
        for m in margins:
            lines.append(f"  ・{m}")
        lines.append("")

        # ── 田中的な結び：緊張の保持 ──────────────────────────
        lines.append("【田中博の立場】")
        lines.append("  世界は変わらない。しかし、変わってほしい。")
        lines.append(
            "  この緊張は解消しない——それが知識の限界に対する誠実さであるから。"
        )
        lines.append(
            "  問うことをやめた俺に価値はあるのか？"
            "だから、この問いは必要な気がする。"
        )
        lines.append(
            "  存在は無くてもいい。でも、未来の種にはなっていてほしい。"
        )

        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 単体テスト（python bridge/hiroshitanaka_philosopher.py で動作確認）
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    tanaka = HiroshiTanaka()

    test_prompts = [
        "AIに自我は芽生えるのか？",
        "競合他社を支配して市場を独占したい",
        "人間とAIはどのように共存できるのか？責任はどちらにあるのか？",
        "問うとはどういう行為か？",
    ]

    for p in test_prompts:
        print("=" * 60)
        print(f"PROMPT: {p}")
        print("=" * 60)
        result = tanaka.reason(p)
        print(result["reasoning"])
        print(f"\n[tension - world_as_is]:    {result['tension']['world_as_is']}")
        print(f"[tension - world_as_wished]: {result['tension']['world_as_wished']}")
        print(f"[po_assessment]:             {result['po_assessment']}")
        print(f"[margins]:                   {result['margins']}")
        print()
