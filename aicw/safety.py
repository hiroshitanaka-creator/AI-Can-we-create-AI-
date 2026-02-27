from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List, Tuple, Literal


@dataclass(frozen=True)
class Finding:
    kind: str          # 例: "EMAIL_LIKE", "PHONE_LIKE"
    severity: str      # "block" or "warn"
    message: str       # 人間向け説明（検知した中身は入れない）
    start: int
    end: int


# 重要: ここは「万能な個人情報検知」ではない。
# P0は最小実装として、明らかなパターンだけ止める（止めすぎでもOK）。
_BLOCK_PATTERNS: List[Tuple[str, re.Pattern[str], str]] = [
    (
        "EMAIL_LIKE",
        re.compile(r"[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{1,255}\.[A-Za-z]{2,63}"),
        "メールっぽい文字列が含まれています（個人情報の可能性）。",
    ),
    (
        "PHONE_LIKE",
        re.compile(r"\b0\d{1,4}-\d{1,4}-\d{3,4}\b"),
        "電話番号っぽい文字列が含まれています（個人情報の可能性）。",
    ),
    (
        "POSTAL_CODE_LIKE",
        re.compile(r"\b\d{3}-\d{4}\b"),
        "郵便番号っぽい文字列が含まれています（個人情報の可能性）。",
    ),
    (
        "IP_LIKE",
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "IPアドレスっぽい文字列が含まれています（個人情報/機密の可能性）。",
    ),
    (
        "SECRET_LIKE_LONG",
        re.compile(r"\b[A-Za-z0-9_\-]{32,}\b"),
        "秘密情報っぽい長い文字列が含まれています（キー/パスワード等の可能性）。",
    ),
    (
        "SECRET_KEYWORD",
        re.compile(r"(?i)\b(token|secret|password|apikey|api_key)\b"),
        "秘密情報を示す単語が含まれています（誤って貼り付けた可能性）。",
    ),
]


@dataclass(frozen=True)
class ManipulationHit:
    phrase: str
    severity: Literal["block", "warn"]


# 操作・扇動っぽい表現（P0: 最小）
# 重要: ここは「言論統制」ではなく、No-Go(#4)を守るための出力チェック。
#
# block: 強い操作/扇動表現。検知したら必ず停止。
# warn : 文脈次第では問題ない表現。レポートに警告を追加するがブロックしない。
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


def scan_privacy_risks(text: str) -> List[Finding]:
    if not text:
        return []
    findings: List[Finding] = []
    for kind, rx, msg in _BLOCK_PATTERNS:
        for m in rx.finditer(text):
            findings.append(
                Finding(
                    kind=kind,
                    severity="block",
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
      - allowed: Falseなら停止（No-Go #6）
      - redacted: 危ない部分を伏せたテキスト（表示用）
      - findings: 検知結果（中身は持たない）
    """
    findings = scan_privacy_risks(text)
    if findings:
        return False, redact(text, findings), findings
    return True, text, []


def scan_manipulation(text: str) -> List[ManipulationHit]:
    """
    Returns: 検知したフレーズ一覧（空ならOK）
      severity="block" → 必ず停止（No-Go #4）
      severity="warn"  → 警告のみ、ブロックしない
    """
    hits: List[ManipulationHit] = []
    if not text:
        return hits
    for p in _MANIPULATION_BLOCK_PHRASES:
        if p in text:
            hits.append(ManipulationHit(phrase=p, severity="block"))
    for p in _MANIPULATION_WARN_PHRASES:
        if p in text:
            hits.append(ManipulationHit(phrase=p, severity="warn"))
    return hits
