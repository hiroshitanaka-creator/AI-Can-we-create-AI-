#!/usr/bin/env python3
"""
scripts/interactive_sim.py

インタラクティブ意思決定シミュレーター

ユーザーが対話形式で decision_request フィールドを入力し、
全パイプライン（意思決定 → 監査ログ → 哲学テンソル → 事後検証）を体験するCLI。

設計方針:
  - 外部ライブラリ不使用（標準 input() ベース）
  - テスト可能（stdin を差し替えられる設計）
  - 途中で Ctrl+C したら安全に終了
  - "--auto" オプションでデフォルト値を使いデモ実行

実行:
  python scripts/interactive_sim.py
  python scripts/interactive_sim.py --auto    # 非インタラクティブ（デモ）
  python scripts/interactive_sim.py --json    # JSON 出力

外部依存: なし
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, IO, List, Optional


# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------
_SEPARATOR = "─" * 60
_DISCLAIMER = (
    "[Disclaimer] 最終判断は人間が行ってください。"
    "このシミュレーターはAIの支援ツールであり、結論を押しつけません。"
)

# auto モード用デフォルト値
_AUTO_DEFAULTS: Dict[str, Any] = {
    "situation": "新規事業への参入可否を判断したい",
    "constraints": ["法令遵守", "品質重視"],
    "options": [
        "A: 今期中に全面参入",
        "B: パイロット事業から始めて段階的に拡大",
        "C: 参入しない（現事業に集中）",
    ],
    "beneficiaries": ["顧客", "従業員", "地域社会"],
    "affected_structures": ["社会", "関係", "経済"],
}


# ---------------------------------------------------------------------------
# インタラクティブ入力収集
# ---------------------------------------------------------------------------

def _prompt(message: str, default: str = "", stdin: IO[str] = None) -> str:
    """1行プロンプト。stdin が None なら sys.stdin を使用。"""
    _stdin = stdin or sys.stdin
    if default:
        sys.stdout.write(f"{message} [{default}]: ")
    else:
        sys.stdout.write(f"{message}: ")
    sys.stdout.flush()
    line = _stdin.readline()
    if not line:  # EOF
        return default
    value = line.rstrip("\n").strip()
    return value if value else default


def _prompt_list(message: str, defaults: List[str] = None, stdin: IO[str] = None) -> List[str]:
    """複数行入力（空行で終了）。"""
    defaults = defaults or []
    sys.stdout.write(f"{message}（空行で終了。デフォルト: {defaults!r}）:\n")
    sys.stdout.flush()
    items: List[str] = []
    _stdin = stdin or sys.stdin
    while True:
        sys.stdout.write(f"  [{len(items)+1}] ")
        sys.stdout.flush()
        line = _stdin.readline()
        if not line:  # EOF
            break
        value = line.rstrip("\n").strip()
        if not value:
            break
        items.append(value)
    return items if items else list(defaults)


def collect_request(
    auto: bool = False,
    stdin: IO[str] = None,
) -> Dict[str, Any]:
    """
    ユーザーから decision_request フィールドを収集する。

    Args:
        auto: True なら入力を省略してデフォルト値を使用
        stdin: テスト用 stdin（None なら sys.stdin）

    Returns:
        decision_request.v0 形式の dict
    """
    if auto:
        return dict(_AUTO_DEFAULTS)

    print(_SEPARATOR)
    print("  意思決定シミュレーター — 入力フォーム")
    print("  ※ Ctrl+C で中断できます")
    print(_SEPARATOR)

    # situation（必須）
    situation = _prompt(
        "\n[1] 何を決めたいか（1行で）",
        default=_AUTO_DEFAULTS["situation"],
        stdin=stdin,
    )

    # constraints
    print(f"\n[2] 制約条件（空行で終了。例: 法令遵守 / コスト上限あり）")
    constraints = _prompt_list("    制約条件", defaults=_AUTO_DEFAULTS["constraints"], stdin=stdin)

    # options
    print(f"\n[3] 選択肢（最大3件。空行で終了）")
    options = _prompt_list("    選択肢", defaults=_AUTO_DEFAULTS["options"], stdin=stdin)
    if len(options) > 3:
        print(f"    ⚠ 選択肢は最大3件です。最初の3件のみ使用します。")
        options = options[:3]

    # beneficiaries（任意）
    print(f"\n[4] 受益者リスト（任意。空行でスキップ）")
    beneficiaries = _prompt_list(
        "    受益者", defaults=_AUTO_DEFAULTS["beneficiaries"], stdin=stdin
    )

    # affected_structures（任意）
    print(f"\n[5] 影響を受ける生存構造（任意。個人/関係/社会/認知/生態）")
    affected = _prompt_list(
        "    構造", defaults=_AUTO_DEFAULTS["affected_structures"], stdin=stdin
    )

    return {
        "situation": situation,
        "constraints": constraints,
        "options": options,
        "beneficiaries": beneficiaries,
        "affected_structures": affected,
    }


# ---------------------------------------------------------------------------
# 結果表示フォーマッタ
# ---------------------------------------------------------------------------

def _print_section(title: str) -> None:
    pad = (56 - len(title)) // 2
    print(f"\n{'─'*pad} {title} {'─'*pad}")


def display_result(
    brief: Dict[str, Any],
    tensor: Dict[str, Any],
    audit_hash: str,
    knowledge_similar: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """分析結果を人間が読みやすい形式で表示する。"""
    if knowledge_similar:
        _print_section("過去類似決定（参考）")
        for i, past in enumerate(knowledge_similar[:3], 1):
            print(f"  [{i}] {past['timestamp_utc'][:10]} | {past['status']} "
                  f"| {past['reason_codes']} | 類似度 {past['similarity']:.2f}")

    _print_section("意思決定ブリーフ")
    status = brief.get("status")
    print(f"  status: {status}")

    if status == "ok":
        sel = brief.get("selection", {})
        print(f"  推奨案: {sel.get('recommended_id', '?')}")
        print(f"  理由コード: {sel.get('reason_codes', [])}")
        explanation = sel.get("explanation", "")
        print(f"  説明: {explanation[:100]}{'...' if len(explanation)>100 else ''}")

        uncertainties = brief.get("uncertainties", [])
        if uncertainties:
            print(f"\n  不確実性:")
            for u in uncertainties[:3]:
                print(f"    · {u}")

        next_q = brief.get("next_questions", [])
        if next_q:
            print(f"\n  次に考えるべき問い:")
            for q in next_q[:3]:
                print(f"    ? {q}")
    else:
        print(f"  blocked_by: {brief.get('blocked_by')}")
        print(f"  理由: {brief.get('reason')}")
        print(f"  代替案: {brief.get('safe_alternatives', [])}")

    _print_section("監査ログ")
    print(f"  ハッシュ（PII不含）: {audit_hash[:20]}...")
    print(f"  status: {status}")

    _print_section("哲学テンソル分析")
    ts = tensor.get("summary", {})
    print(f"  最大リスク: {ts.get('highest_risk', '?')}")
    print(f"  哲学的矛盾: {ts.get('has_ethical_conflict', False)}")
    print(f"  AI権利緊張指数: {ts.get('ai_rights_tension', '?')}")
    print(f"  推奨アクション: {ts.get('recommended_action', '?')}")

    w_eth = tensor.get("tensor", {}).get("W_eth", {})
    if w_eth.get("conflict_codes"):
        print(f"  哲学的矛盾コード: {w_eth['conflict_codes']}")

    t_sub = tensor.get("tensor", {}).get("T_sub", {})
    if t_sub.get("reverse_manipulation_warning"):
        print(f"  ⚠ 逆算誘導警告（スコア {t_sub['reverse_similarity_score']:.2f}）")

    print(f"\n{_SEPARATOR}")
    print(f"  {_DISCLAIMER}")
    print(_SEPARATOR)


# ---------------------------------------------------------------------------
# メインシミュレーションフロー
# ---------------------------------------------------------------------------

def run_simulation(
    auto: bool = False,
    json_mode: bool = False,
    stdin: IO[str] = None,
    record_to_kb: bool = True,
    kb_path: str = "",
) -> Dict[str, Any]:
    """
    シミュレーションを実行して結果を返す。

    Args:
        auto: True なら非インタラクティブ（デモ）モード
        json_mode: True なら結果を JSON 文字列として返す
        stdin: テスト用 stdin 差し替え
        record_to_kb: True なら knowledge_base に記録する

    Returns:
        {
            "request": dict,
            "brief_status": str,
            "audit_hash": str,
            "philosophy_summary": dict,
            "knowledge_recorded": bool,
        }
    """
    from aicw.decision import build_decision_report
    from aicw.audit_log import AuditLog
    from bridge.po_core_bridge import analyze_philosophy_tensor
    from aicw.knowledge_base import KnowledgeBase

    # Step 1: 入力収集
    if not auto:
        print(f"\n{_SEPARATOR}")
        print("  AI意思決定シミュレーター へようこそ")
        print("  ─ 全ての最終判断は あなた が行います ─")
        print(_SEPARATOR)

    request = collect_request(auto=auto, stdin=stdin)

    if not auto:
        print(f"\n{_SEPARATOR}")
        print("  入力を受け取りました。分析中...")
        print(_SEPARATOR)

    # Step 2: 意思決定ブリーフ生成
    brief = build_decision_report(request)

    # Step 3: 監査ログ
    log = AuditLog()
    if brief["status"] == "ok":
        sel = brief.get("selection", {})
        entry = log.append("ok", reason_codes=sel.get("reason_codes", []))
    else:
        entry = log.append("blocked", blocked_by=brief.get("blocked_by"))

    # Step 4: 哲学テンソル
    explanation = ""
    if brief["status"] == "ok":
        explanation = brief.get("selection", {}).get("explanation", "")

    human_decision = request.get("situation", "")  # まだ未入力なので situation で代替
    tensor = analyze_philosophy_tensor(
        situation=request["situation"],
        explanation=explanation,
        existence_analysis=brief.get("existence_analysis"),
    )

    # Step 5: 知識ベース（類似検索 + 記録）
    kb = KnowledgeBase(path=kb_path or None)
    similar = []
    if record_to_kb:
        reason_codes = []
        if brief["status"] == "ok":
            reason_codes = brief.get("selection", {}).get("reason_codes", [])
        similar = kb.find_similar(reason_codes, top_k=3)
        save_to_kb = True
        if not auto:
            answer = _prompt("\n今回の決定を KB に保存しますか？ (Y/n)", default="Y", stdin=stdin)
            save_to_kb = answer.strip().lower() not in ("n", "no")

        if save_to_kb:
            kb.record(
                decision_hash=entry.decision_hash,
                status=brief["status"],
                reason_codes=reason_codes,
                blocked_by=brief.get("blocked_by"),
            )
            record_to_kb = True
        else:
            record_to_kb = False

    # Step 6: 表示 or JSON 出力
    if not json_mode:
        display_result(brief, tensor, entry.decision_hash, similar)

    return {
        "request": request,
        "brief_status": brief["status"],
        "audit_hash": entry.decision_hash,
        "philosophy_summary": tensor["summary"],
        "knowledge_recorded": record_to_kb,
        "similar_count": len(similar),
    }


# ---------------------------------------------------------------------------
# CLI エントリポイント
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="インタラクティブ意思決定シミュレーター"
    )
    parser.add_argument(
        "--auto", action="store_true",
        help="非インタラクティブモード（デフォルト値を使ってデモ実行）",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="JSON 形式で結果を出力する",
    )
    parser.add_argument(
        "--no-kb", action="store_true",
        help="知識ベースへの記録をスキップする",
    )
    parser.add_argument(
        "--kb-path",
        default="",
        help="知識ベースJSONの保存/読込パス（未指定時はインメモリ）",
    )
    args = parser.parse_args()

    try:
        result = run_simulation(
            auto=args.auto,
            json_mode=args.json,
            record_to_kb=not args.no_kb,
            kb_path=args.kb_path,
        )
    except KeyboardInterrupt:
        print("\n\n  中断しました。またいつでも使ってください。")
        return 1
    except Exception as e:
        print(f"\nエラー: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
