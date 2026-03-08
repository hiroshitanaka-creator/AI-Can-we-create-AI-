"""長文 situation をルールベースで圧縮するユーティリティ。"""

from __future__ import annotations

from typing import List

_DEFAULT_KEYWORDS = [
    "安全", "品質", "リスク", "法令", "コンプラ", "期限", "至急", "納期",
    "privacy", "risk", "deadline", "compliance", "quality", "safety",
]


def _split_sentences(text: str) -> List[str]:
    normalized = (
        text.replace("\r\n", "\n")
        .replace("。", "。\n")
        .replace("!", "!\n")
        .replace("?", "?\n")
    )
    return [s.strip() for s in normalized.split("\n") if s.strip()]


def compress_situation(
    text: str,
    *,
    enabled: bool = True,
    max_sentences: int = 3,
    max_chars: int = 220,
    keywords: List[str] | None = None,
) -> str:
    """situation を要点優先で圧縮する。"""
    if not enabled:
        return text

    raw = (text or "").strip()
    if len(raw) <= max_chars:
        return raw

    sentences = _split_sentences(raw)
    if not sentences:
        return raw[:max_chars]

    kws = keywords if keywords is not None else _DEFAULT_KEYWORDS

    prioritized: List[str] = []
    remaining: List[str] = []
    for sent in sentences:
        if any(kw.lower() in sent.lower() for kw in kws):
            prioritized.append(sent)
        else:
            remaining.append(sent)

    picked: List[str] = []
    for sent in prioritized + remaining:
        if len(picked) >= max_sentences:
            break
        picked.append(sent)

    compressed = " ".join(picked).strip()
    if len(compressed) > max_chars:
        compressed = compressed[: max_chars - 1].rstrip() + "…"

    return compressed
