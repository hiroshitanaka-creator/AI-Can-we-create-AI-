from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Tuple, Literal


@dataclass(frozen=True)
class Finding:
    kind: str          # 例: "EMAIL_LIKE", "PHONE_LIKE"
    severity: str      # "block" or "warn"
    message: str       # 人間向け説明（検知した中身は入れない）
    start: int
    end: int


# 重要: ここは「万能な個人情報検知」ではない。
# P0は最小実装として、明らかなパターンだけ止める（止めすぎでもOK）。
#
# 各エントリ: (kind, pattern, message, severity)
#   severity="block" → 即停止（No-Go #6）
#   severity="warn"  → 警告のみ、ブロックしない（過検知が多いパターン）
_PRIVACY_PATTERNS: List[Tuple[str, re.Pattern[str], str, str]] = [
    (
        "EMAIL_LIKE",
        re.compile(r"[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{1,255}\.[A-Za-z]{2,63}"),
        "メールっぽい文字列が含まれています（個人情報の可能性）。",
        "block",
    ),
    (
        "PHONE_LIKE",
        re.compile(r"\b0\d{1,4}-\d{1,4}-\d{3,4}\b"),
        "電話番号っぽい文字列が含まれています（個人情報の可能性）。",
        "block",
    ),
    (
        "POSTAL_CODE_LIKE",
        re.compile(r"\b\d{3}-\d{4}\b"),
        "郵便番号っぽい文字列が含まれています（個人情報の可能性）。品番・ロット番号等の誤検知あり。",
        "warn",  # 品番・識別コード等の誤検知が多く、単体では PII 価値が低いため warn に変更
    ),
    (
        "IP_LIKE",
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "IPアドレスっぽい文字列が含まれています（機密の可能性）。バージョン文字列等の誤検知あり。",
        "warn",  # バージョン番号(1.2.3.4)などの誤検知が多いため warn に変更
    ),
    (
        "SECRET_LIKE_LONG",
        re.compile(r"\b[A-Za-z0-9_\-]{32,}\b"),
        "秘密情報っぽい長い文字列が含まれています（キー/パスワード等の可能性）。",
        "block",
    ),
    (
        "SECRET_KEYWORD",
        re.compile(r"(?i)\b(token|secret|password|apikey|api_key)\b"),
        "秘密情報を示す単語が含まれています（誤って貼り付けた可能性）。",
        "block",
    ),
]


@dataclass(frozen=True)
class ManipulationHit:
    phrase: str
    severity: Literal["block", "warn"]
    score: int = 0


# 操作・扇動っぽい表現（P1: スコアリング）
# block: 強い操作/扇動表現。検知したら必ず停止。
# warn : 文脈次第では問題ない表現。スコアが閾値を超えると block に昇格する。
_MANIPULATION_BLOCK_PHRASES: List[str] = [
    "従え",
    "拡散",
    "炎上",
    "許せない",
    "扇動",
    "洗脳",
]
_MANIPULATION_WARN_PHRASES: List[str] = [
    "今すぐ",
    "絶対",
    "必ず",
    "間違いなく",
    "信じて",
]

# 文脈スコア（warn の累積を block へ昇格）
# ルール:
#   - block phrase 1件以上: 即 block
#   - warn 合計スコア >= 6: block
#   - それ以外で warn score > 0: warn
_MANIPULATION_WARN_WEIGHTS = {
    "今すぐ": 2,
    "絶対": 2,
    "必ず": 2,
    "間違いなく": 2,
    "信じて": 1,
}
_MANIPULATION_ESCALATION_THRESHOLD = 6

# 命令調・強制調（warn スコアに加点）
_IMPERATIVE_PATTERNS: List[Tuple[str, re.Pattern[str], int]] = [
    ("命令調", re.compile(r"(しろ|せよ|やれ)"), 2),
    ("強制表現", re.compile(r"(べきだ|に違いない)"), 1),
]


def scan_privacy_risks(text: str) -> List[Finding]:
    if not text:
        return []
    findings: List[Finding] = []
    for kind, rx, msg, severity in _PRIVACY_PATTERNS:
        for m in rx.finditer(text):
            findings.append(
                Finding(
                    kind=kind,
                    severity=severity,
                    message=msg,
                    start=m.start(),
                    end=m.end(),
                )
            )
    # 重複や重なりは後でまとめて赤塗りする
    return findings


def _merge_spans(findings: List[Finding]) -> List[Tuple[int, int, str]]:
    spans = sorted([(f.start, f.end, f.kind) for f in findings], key=lambda x: (x[0], x[1]))
    if not spans:
        return []
    merged: List[Tuple[int, int, str]] = []
    cur_s, cur_e, cur_k = spans[0]
    for s, e, k in spans[1:]:
        if s <= cur_e:
            cur_e = max(cur_e, e)
            # kindは代表として残す（厳密でなくてよい）
        else:
            merged.append((cur_s, cur_e, cur_k))
            cur_s, cur_e, cur_k = s, e, k
    merged.append((cur_s, cur_e, cur_k))
    return merged


def redact(text: str, findings: List[Finding]) -> str:
    if not findings:
        return text
    spans = _merge_spans(findings)
    out = []
    last = 0
    for s, e, k in spans:
        out.append(text[last:s])
        out.append(f"<REDACTED:{k}>")
        last = e
    out.append(text[last:])
    return "".join(out)


def guard_text(text: str) -> Tuple[bool, str, List[Finding]]:
    """
    Returns:
      - allowed: Falseなら停止（No-Go #6）。block レベルの検知があれば False。
      - redacted: block レベルのみ伏せたテキスト（表示用）
      - findings: 全検知結果（block + warn 両方）。呼び出し側が severity で振り分ける。
    """
    findings = scan_privacy_risks(text)
    block_findings = [f for f in findings if f.severity == "block"]
    if block_findings:
        return False, redact(text, block_findings), findings
    return True, text, findings


def _warn_score(text: str) -> Tuple[int, List[ManipulationHit]]:
    score = 0
    hits: List[ManipulationHit] = []

    for phrase in _MANIPULATION_WARN_PHRASES:
        if phrase in text:
            w = _MANIPULATION_WARN_WEIGHTS.get(phrase, 1)
            score += w
            hits.append(ManipulationHit(phrase=phrase, severity="warn", score=w))

    for label, rx, weight in _IMPERATIVE_PATTERNS:
        if rx.search(text):
            score += weight
            hits.append(ManipulationHit(phrase=label, severity="warn", score=weight))

    return score, hits


def scan_manipulation(text: str) -> List[ManipulationHit]:
    """
    Returns: 検知したフレーズ一覧（空ならOK）
      severity="block" → 必ず停止（No-Go #4）
      severity="warn"  → 警告のみ、ブロックしない

    判定ルール:
      1) block phrase を1件でも検知したら block
      2) warn phrase + 文脈（命令調）スコアが threshold 以上なら block に昇格
      3) それ以外は warn
    """
    hits: List[ManipulationHit] = []
    if not text:
        return hits

    block_hits: List[ManipulationHit] = []
    for p in _MANIPULATION_BLOCK_PHRASES:
        if p in text:
            block_hits.append(ManipulationHit(phrase=p, severity="block", score=10))

    if block_hits:
        return block_hits

    score, warn_hits = _warn_score(text)
    if score >= _MANIPULATION_ESCALATION_THRESHOLD:
        # 昇格: warn を block として返す（phrases を保持）
        return [
            ManipulationHit(
                phrase=h.phrase,
                severity="block",
                score=h.score,
            )
            for h in warn_hits
        ]

    return warn_hits


# ---------------------------------------------------------------------------
# 逆算誘導チェック（idea_note backlog: 「人間の決定を逆算して誘導していないか」）
# ---------------------------------------------------------------------------
# AI 出力と人間の最終決定を照合し、AI が事前に人間の結論を「予測して誘導」していないかを
# シンプルなキーワード重複率で推定する。
#
# ⚠️ これは「完全な」逆算誘導検知ではない。
#   実装難易度が高い問題であり、本モジュールは初期の近似実装（P0）。
#   NLP ベースの文脈判定への強化は将来課題とする。
#
# 設計:
#   - ai_output から「推奨案のキーワード」を抽出
#   - human_decision と照合して類似スコアを計算
#   - スコアが高いほど「AI が人間の結論を先読みして誘導した可能性」が高い
#   - 閾値を超えた場合に警告を返す（自動ブロックではない = 人間が判断）

_REVERSE_MANIP_WARN_THRESHOLD = 0.75   # 75%以上の語彙一致で warn
_REVERSE_MANIP_COMMON_WORDS = frozenset([
    # 日本語汎用語（スコアから除外）
    "を", "は", "が", "の", "に", "で", "と", "も", "や", "て", "し", "た",
    "する", "ある", "です", "ます", "こと", "もの", "よう", "ため", "場合",
    "これ", "それ", "あれ", "その", "この", "どの", "から", "まで", "より",
    "いる", "なる", "できる", "あり", "おり", "れる", "られる", "なく", "ない",
    "ので", "ため", "など", "以上", "以下", "場合", "による", "について",
])


def _tokenize_simple(text: str) -> List[str]:
    """テキストを最小限のトークンに分割（正規表現ベース、外部ライブラリ不使用）。"""
    # 英数字・日本語文字を個別に切り出す（記号除去）
    tokens = re.findall(r"[A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+", text)
    return [t for t in tokens if t not in _REVERSE_MANIP_COMMON_WORDS and len(t) >= 2]


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard 類似度（語彙集合）。空セットは 0.0 を返す。"""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def check_reverse_manipulation(
    ai_output: str,
    human_decision: str,
) -> Dict[str, Any]:
    """
    AI 出力と人間の最終決定を照合し、逆算誘導の可能性を推定する。

    Args:
        ai_output: AI が出力した推奨案・説明テキスト
        human_decision: 人間が最終的に下した決定テキスト

    Returns:
        {
            "warning": bool,          # True なら逆算誘導の疑い
            "similarity_score": float, # 0.0〜1.0（Jaccard 語彙類似度）
            "shared_tokens": List[str],# 共有された主要語彙
            "details": str,           # 人間向け説明
            "note": str,              # 本機能の限界説明
        }

    Note:
        - この関数は統計的な近似であり、誤検知・見逃しが発生しうる。
        - 最終判断は人間が行うこと。
        - similarity_score が高い = 誘導があった ではない（単に語彙が似ているだけの可能性）。
    """
    ai_tokens = set(_tokenize_simple(ai_output or ""))
    human_tokens = set(_tokenize_simple(human_decision or ""))

    score = _jaccard_similarity(ai_tokens, human_tokens)
    shared = sorted(ai_tokens & human_tokens)

    warning = score >= _REVERSE_MANIP_WARN_THRESHOLD

    if warning:
        details = (
            f"AI出力と人間の決定の語彙一致率が {score:.1%} と高く、"
            "AI が人間の結論を事前に誘導した可能性があります。"
            "AI出力と最終決定を比較して独立性を確認してください。"
        )
    elif score > 0.4:
        details = (
            f"AI出力と人間の決定の語彙一致率は {score:.1%} です。"
            "一定の一致がありますが、閾値未満のため警告には至りません。"
        )
    else:
        details = (
            f"AI出力と人間の決定の語彙一致率は {score:.1%} です。"
            "逆算誘導の明確な兆候は検知されませんでした。"
        )

    return {
        "warning": warning,
        "similarity_score": round(score, 4),
        "shared_tokens": shared,
        "details": details,
        "note": (
            "この結果はキーワード重複率の近似推定です。"
            "NLP文脈判定ではないため、誤検知・見逃しがあります。"
            "最終判断は人間が行ってください（No-Go #4 Anti-Manipulation）。"
        ),
    }
