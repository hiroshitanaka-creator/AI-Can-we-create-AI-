"""
aicw/knowledge_base.py

オフライン知識ベース（ローカル JSON）

目的:
  過去の意思決定の「メタデータ」を蓄積し、
  「以前似たような決定をした」という文脈を次回の判断補助に使う。

Privacy 方針（厳守）:
  - 生テキスト（situation / explanation / human_decision）は一切保存しない
  - 保存するのは: decision_hash / status / reason_codes / blocked_by / timestamp のみ
  - これは audit_log.py の設計方針と一致する（#6 Privacy 完全準拠）

類似検索の仕組み:
  - reason_codes の Jaccard 類似度で過去決定との類似度を計算
  - 類似度が高い = 似た制約・判断パターンの過去決定
  - raw text 比較は行わない（Privacy 保護）

設計:
  - インメモリ（デフォルト）＋ JSON ファイル永続化（オプション）
  - ファイルが存在すれば起動時に自動ロード
  - 外部ライブラリ不使用

使用例:
    from aicw.knowledge_base import KnowledgeBase

    kb = KnowledgeBase()  # インメモリのみ
    kb.record("abc123...", "ok", ["SAFETY_FIRST", "COMPLIANCE_FIRST"])

    kb_file = KnowledgeBase(path="data/kb.json")  # ファイル永続化
    similar = kb_file.find_similar(["SAFETY_FIRST"], top_k=3)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# エントリ構造
# ---------------------------------------------------------------------------

def _make_entry(
    decision_hash: str,
    status: str,
    reason_codes: List[str],
    blocked_by: Optional[str] = None,
) -> Dict[str, Any]:
    """知識ベースの1エントリを生成する。"""
    return {
        "decision_hash": decision_hash,
        "status": status,                          # "ok" | "blocked"
        "reason_codes": sorted(reason_codes),      # ソート済み（比較の一貫性）
        "blocked_by": blocked_by,                  # None | "#4" | "#5" | "#6"
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Jaccard 類似度
# ---------------------------------------------------------------------------

def _jaccard(a: List[str], b: List[str]) -> float:
    """reason_codes リストの Jaccard 類似度（0.0〜1.0）。"""
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return 1.0   # 両方空 = 完全一致とみなす
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# ---------------------------------------------------------------------------
# KnowledgeBase
# ---------------------------------------------------------------------------

class KnowledgeBase:
    """
    過去決定のメタデータを管理するオフライン知識ベース。

    Args:
        path: JSON ファイルのパス（None = インメモリのみ）
        max_entries: 最大保持エントリ数（古い順に削除。デフォルト 500）
    """

    DEFAULT_MAX = 500

    def __init__(
        self,
        path: Optional[str] = None,
        max_entries: int = DEFAULT_MAX,
    ) -> None:
        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        self._path = path
        self._max = max_entries
        self._entries: List[Dict[str, Any]] = []

        if path and os.path.isfile(path):
            self._load(path)

    # ------------------------------------------------------------------
    # 記録
    # ------------------------------------------------------------------
    def record(
        self,
        decision_hash: str,
        status: str,
        reason_codes: List[str],
        blocked_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        過去決定のメタデータを記録する。

        Args:
            decision_hash: audit_log と同じ SHA256 ハッシュ
            status: "ok" または "blocked"
            reason_codes: selection.reason_codes（ok 時）
            blocked_by: blocked 時の No-Go コード

        Returns:
            記録したエントリ
        """
        if status not in ("ok", "blocked"):
            raise ValueError(f"status must be 'ok' or 'blocked', got: {status!r}")

        entry = _make_entry(decision_hash, status, reason_codes, blocked_by)
        self._entries.append(entry)

        # 上限超過: 最古エントリを削除
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]

        if self._path:
            self._save(self._path)

        return entry

    # ------------------------------------------------------------------
    # 類似検索
    # ------------------------------------------------------------------
    def find_similar(
        self,
        reason_codes: List[str],
        *,
        top_k: int = 3,
        min_similarity: float = 0.0,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        reason_codes が似ている過去決定を返す。

        Args:
            reason_codes: 検索クエリとなる reason_codes
            top_k: 返す件数（デフォルト 3）
            min_similarity: 最低類似度（0.0〜1.0。デフォルト 0.0 = 全件）
            status_filter: "ok" / "blocked" で絞り込み（None = 全て）

        Returns:
            類似度降順のエントリリスト（各エントリに "similarity" キーを追加）
        """
        results = []
        for entry in self._entries:
            if status_filter and entry["status"] != status_filter:
                continue
            sim = _jaccard(reason_codes, entry["reason_codes"])
            if sim >= min_similarity:
                results.append({**entry, "similarity": round(sim, 4)})

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    # ------------------------------------------------------------------
    # クエリ
    # ------------------------------------------------------------------
    def count(self) -> int:
        return len(self._entries)

    def all_entries(self) -> List[Dict[str, Any]]:
        """全エントリを返す（変更不可の複製）。"""
        return list(self._entries)

    def stats(self) -> Dict[str, Any]:
        """
        統計サマリを返す。

        Returns:
            {
                "total": int,
                "ok_count": int,
                "blocked_count": int,
                "top_reason_codes": [(code, count), ...],
                "max_entries": int,
                "has_persistent_storage": bool,
            }
        """
        ok_count = sum(1 for e in self._entries if e["status"] == "ok")
        blocked_count = len(self._entries) - ok_count

        code_freq: Dict[str, int] = {}
        for entry in self._entries:
            for code in entry["reason_codes"]:
                code_freq[code] = code_freq.get(code, 0) + 1

        top_codes = sorted(code_freq.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total": len(self._entries),
            "ok_count": ok_count,
            "blocked_count": blocked_count,
            "top_reason_codes": top_codes,
            "max_entries": self._max,
            "has_persistent_storage": self._path is not None,
        }

    def clear(self) -> None:
        """全エントリを削除する（テスト用）。"""
        self._entries.clear()
        if self._path and os.path.isfile(self._path):
            self._save(self._path)

    # ------------------------------------------------------------------
    # 永続化
    # ------------------------------------------------------------------
    def save(self, path: Optional[str] = None) -> None:
        """
        エントリを JSON ファイルに保存する。

        Args:
            path: 保存先パス（None の場合は初期化時のパスを使用）
        """
        target = path or self._path
        if not target:
            raise ValueError("path が指定されていません。save(path=...) で指定してください。")
        self._save(target)

    def _save(self, path: str) -> None:
        data = {
            "version": "knowledge_base.v0.1",
            "max_entries": self._max,
            "entries": self._entries,
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self, path: str) -> None:
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                return  # 空ファイルは無視
            data = json.loads(content)
        except (json.JSONDecodeError, OSError):
            return  # 破損・読み込み不可ファイルは無視（エントリなしで初期化）
        loaded = data.get("entries", [])
        # バリデーション: 必須キーがあるエントリのみ取り込む
        required = {"decision_hash", "status", "reason_codes", "timestamp_utc"}
        valid = [e for e in loaded if required.issubset(e.keys())]
        self._entries = valid[-self._max:]  # 上限超過分は古い方を切り捨て
