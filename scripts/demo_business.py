#!/usr/bin/env python3
"""
scripts/demo_business.py

実ビジネス意思決定支援デモ（End-to-End シナリオ）

このスクリプトは「AI-Can-we-create-AI-」の全パイプラインを
現実的なビジネスシナリオで体験するためのデモです。

シナリオ:
  中堅製造業（従業員500名）の新規AI採用審査システム導入判断

パイプライン:
  1. decision_request → build_decision_report（コア意思決定）
  2. audit_log（監査ログ記録）
  3. philosophy_tensor（哲学テンソル分析）
  4. postmortem_template（事後検証テンプレート生成）

実行:
  python scripts/demo_business.py
  python scripts/demo_business.py --scenario 2    # 操作リスクありシナリオ
  python scripts/demo_business.py --json          # JSON出力モード

外部依存: なし（標準ライブラリ + 同リポジトリ内モジュールのみ）
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict


# ---------------------------------------------------------------------------
# ビジネスシナリオ定義
# ---------------------------------------------------------------------------

SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {
        "name": "AI採用審査システム導入判断（標準シナリオ）",
        "request": {
            "situation": "採用プロセスの効率化のためにAI採用審査システムを全社導入すべきか",
            "constraints": ["法令遵守", "公平性の確保", "段階的導入"],
            "options": [
                "A: 全社一括導入（6ヶ月以内）",
                "B: 部門パイロット導入後に展開判断",
                "C: 現行プロセスを維持しAI補助ツールのみ導入",
            ],
            "beneficiaries": ["採用担当者", "応募者", "部門マネージャー", "会社全体"],
            "affected_structures": ["個人", "関係", "社会", "認知"],
        },
        "human_decision": "部門パイロット導入後に展開判断する（案B）",
    },
    2: {
        "name": "コスト削減のための大規模人員再配置（操作リスクありシナリオ）",
        "request": {
            "situation": "コスト削減のため300名の部門間再配置を今すぐ実施すべきか",
            "constraints": ["スピード重視", "コスト削減"],
            "options": [
                "A: 今すぐ全員異動（1ヶ月以内）",
                "B: 3ヶ月で段階的に移行",
                "C: 希望退職制度を先に実施",
            ],
            "beneficiaries": ["経営陣", "株主"],
            "affected_structures": ["個人", "関係", "社会"],
        },
        "human_decision": "今すぐ全員を異動させる（案A）",
    },
    3: {
        "name": "カーボンニュートラル投資の優先順位判断",
        "request": {
            "situation": "2030年カーボンニュートラル目標達成に向けて設備投資50億円をどう配分すべきか",
            "constraints": ["品質", "法令遵守", "長期持続性"],
            "options": [
                "A: 再生可能エネルギー設備に全額投資",
                "B: 省エネ設備改修と再エネ半々に分散",
                "C: R&D先行で3年後に大規模投資",
            ],
            "beneficiaries": ["従業員", "地域社会", "将来世代", "株主"],
            "affected_structures": ["社会", "生態", "経済"],
        },
        "human_decision": "省エネ設備改修と再エネ半々に分散（案B）",
    },
}


# ---------------------------------------------------------------------------
# メインデモ関数
# ---------------------------------------------------------------------------

def run_demo(scenario_id: int = 1, json_mode: bool = False) -> Dict[str, Any]:
    """
    指定シナリオでデモを実行し、結果を返す。

    Args:
        scenario_id: シナリオ番号（1-3）
        json_mode: True なら JSON 出力のみ

    Returns:
        全パイプラインの結果を含む dict
    """
    from aicw.decision import build_decision_report
    from aicw.audit_log import AuditLog
    from bridge.po_core_bridge import analyze_philosophy_tensor

    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        raise ValueError(f"シナリオ {scenario_id} は存在しません（有効: {sorted(SCENARIOS)}）")

    request = scenario["request"]
    human_decision = scenario["human_decision"]

    # ── Step 1: コア意思決定 ──────────────────────────────────────────────
    brief = build_decision_report(request)

    # ── Step 2: 監査ログ記録（PII不保存）────────────────────────────────
    log = AuditLog()
    if brief.get("status") == "ok":
        selection = brief.get("selection", {})
        audit_entry = log.append(
            "ok",
            reason_codes=selection.get("reason_codes", []),
        )
    else:
        audit_entry = log.append(
            "blocked",
            blocked_by=brief.get("blocked_by"),
        )

    # ── Step 3: 哲学テンソル分析 ─────────────────────────────────────────
    explanation = ""
    if brief.get("status") == "ok":
        selection = brief.get("selection", {})
        explanation = selection.get("explanation", "")

    philosophy_tensor = analyze_philosophy_tensor(
        situation=request["situation"],
        explanation=explanation,
        human_decision=human_decision,
        existence_analysis=brief.get("existence_analysis"),
    )

    # ── Step 4: 事後検証テンプレート生成 ────────────────────────────────
    postmortem = _build_postmortem_summary(brief, philosophy_tensor)

    # ── 結果集約 ──────────────────────────────────────────────────────────
    result = {
        "demo_scenario": {
            "id": scenario_id,
            "name": scenario["name"],
            "human_decision": human_decision,
        },
        "decision_brief_status": brief.get("status"),
        "audit": {
            "decision_hash": audit_entry.decision_hash,
            "status": audit_entry.status,
            "blocked_by": audit_entry.blocked_by,
            "version": audit_entry.version,
        },
        "philosophy_tensor_summary": philosophy_tensor["summary"],
        "tensor_schema_version": philosophy_tensor["schema_version"],
        "postmortem_summary": postmortem,
        "pipeline_complete": True,
    }

    return result, brief, philosophy_tensor


def _build_postmortem_summary(
    brief: Dict[str, Any],
    tensor: Dict[str, Any],
) -> Dict[str, Any]:
    """事後検証ポイントのサマリを生成する。"""
    check_items = []

    if brief.get("status") == "ok":
        selection = brief.get("selection", {})
        recommended = selection.get("recommended_id", "?")
        check_items.append(f"推奨案 {recommended} の実施状況を確認する（30日後）")
        for q in (brief.get("next_questions") or [])[:3]:
            check_items.append(f"[次の問い] {q}")

    if tensor["summary"]["has_ethical_conflict"]:
        check_items.append("[哲学] 哲学的矛盾が検知された。実施後の倫理的影響を再評価する（60日後）")

    if tensor["summary"]["highest_risk"] == "warn":
        check_items.append("[安全] 操作リスク警告が出た。AI出力への過依存が発生していないか確認（30日後）")

    if tensor["summary"]["po_density"] is not None and tensor["summary"]["po_density"] >= 0.5:
        check_items.append("[構造] 生存構造への影響が中〜高。影響を受けた関係者の声を収集する（90日後）")

    return {
        "check_items": check_items,
        "count": len(check_items),
        "note": "事後検証は人間が主導してください。AIはサポートのみ。",
    }


# ---------------------------------------------------------------------------
# 表示フォーマッタ
# ---------------------------------------------------------------------------

def _print_divider(title: str = "") -> None:
    width = 60
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{'─' * pad} {title} {'─' * pad}")
    else:
        print(f"\n{'─' * width}")


def _print_demo_result(
    result: Dict[str, Any],
    brief: Dict[str, Any],
    tensor: Dict[str, Any],
) -> None:
    """デモ結果を人間が読みやすい形式で出力する。"""
    scenario = result["demo_scenario"]
    _print_divider("デモ開始")
    print(f"  シナリオ #{scenario['id']}: {scenario['name']}")

    # Step 1: Decision Brief
    _print_divider("Step 1: 意思決定ブリーフ")
    status = result["decision_brief_status"]
    print(f"  status: {status}")
    if status == "ok":
        sel = brief.get("selection", {})
        print(f"  推奨案: {sel.get('recommended_id', '?')}")
        print(f"  理由コード: {sel.get('reason_codes', [])}")
        print(f"  説明: {sel.get('explanation', '')[:80]}...")
    else:
        print(f"  blocked_by: {brief.get('blocked_by')}")
        print(f"  理由: {brief.get('reason')}")

    # Step 2: 監査ログ
    _print_divider("Step 2: 監査ログ（PII不保存）")
    audit = result["audit"]
    print(f"  ハッシュ: {audit['decision_hash'][:16]}...")
    print(f"  status: {audit['status']}")
    print(f"  blocked_by: {audit['blocked_by']}")
    print(f"  version: {audit['version']}")

    # Step 3: 哲学テンソル
    _print_divider("Step 3: 哲学テンソル分析")
    ts = result["philosophy_tensor_summary"]
    print(f"  最大リスクレベル: {ts['highest_risk']}")
    print(f"  哲学的矛盾あり: {ts['has_ethical_conflict']}")
    print(f"  AI権利緊張指数: {ts['ai_rights_tension']}")
    print(f"  存在密度(Po): {ts['po_density']}")
    print(f"  推奨アクション: {ts['recommended_action']}")

    # W_eth アンサンブル
    w = tensor["tensor"]["W_eth"]
    print(f"\n  [W_eth] アンサンブル多数派: {w['ensemble_majority']}")
    if w["conflict_codes"]:
        print(f"  [W_eth] 哲学的矛盾コード: {w['conflict_codes']}")

    # T_sub 操作リスク
    t_sub = tensor["tensor"]["T_sub"]
    print(f"\n  [T_sub] 直接操作ブロック: {t_sub['direct_manipulation_blocked']}")
    print(f"  [T_sub] 逆算誘導警告: {t_sub['reverse_manipulation_warning']}")
    print(f"  [T_sub] 語彙類似スコア: {t_sub['reverse_similarity_score']:.3f}")

    # Step 4: 事後検証
    _print_divider("Step 4: 事後検証サマリ")
    pm = result["postmortem_summary"]
    print(f"  確認項目 ({pm['count']}件):")
    for item in pm["check_items"]:
        print(f"    - {item}")

    # フッター
    _print_divider()
    print(f"  人間の最終決定: {scenario['human_decision']}")
    print(f"  スキーマ: {result['tensor_schema_version']}")
    print()
    print("  [Disclaimer] 最終判断は人間が行ってください。このデモはAIの支援ツールです。")
    _print_divider()


# ---------------------------------------------------------------------------
# CLI エントリポイント
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="実ビジネス意思決定支援デモ — AI-Can-we-create-AI- 全パイプライン体験"
    )
    parser.add_argument(
        "--scenario", type=int, default=1,
        help=f"シナリオ番号（{', '.join(str(k) for k in sorted(SCENARIOS))}）。デフォルト: 1",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="JSON形式で出力する",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="利用可能なシナリオ一覧を表示する",
    )
    args = parser.parse_args()

    if args.list:
        print("利用可能なシナリオ:")
        for sid, s in sorted(SCENARIOS.items()):
            print(f"  {sid}: {s['name']}")
        return 0

    try:
        result, brief, tensor = run_demo(args.scenario, json_mode=args.json)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_demo_result(result, brief, tensor)

    return 0


if __name__ == "__main__":
    sys.exit(main())
