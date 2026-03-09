"""
aicw/audit_log.py

最小監査ログ（Verifiable Decision Layer v0.1 の一部）

設計方針:
  - PII・生テキスト・秘密情報は一切保存しない
  - 保存するのは「何が起きたか」のメタデータのみ
  - ハッシュは SHA256 で生成（再現性あり、逆引き不可）
  - TTL 付き（デフォルト 24 時間。期限切れエントリは自動除外）
  - 外部ライブラリ不使用
  - インメモリのみ（ファイル書き込みはオプションで将来拡張可）
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# エントリ構造
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AuditEntry:
    """監査ログの1件。PII・生テキストは含まない。"""

    timestamp_utc: str       # ISO8601 UTC
    decision_hash: str       # SHA256(status + reason_codes + blocked_by)
    status: str              # "ok" | "blocked"
    blocked_by: Optional[str]  # "#6 Privacy" / "#5 Existence Ethics" / "#4 Manipulation" / None
    reason_codes: List[str]  # selection.reason_codes（ok時）または空リスト
    version: str             # "v0"
    expires_at_utc: str      # TTL 期限（ISO8601 UTC）


# ---------------------------------------------------------------------------
# ログストア
# ---------------------------------------------------------------------------
class AuditLog:
    """インメモリ監査ログ。append() で追記、query() で取得。"""

    DEFAULT_TTL_HOURS = 24

    def __init__(self, ttl_hours: int = DEFAULT_TTL_HOURS) -> None:
        if ttl_hours <= 0:
            raise ValueError("ttl_hours must be positive")
        self._ttl_hours = ttl_hours
        self._entries: List[AuditEntry] = []

    # ------------------------------------------------------------------
    # 追記
    # ------------------------------------------------------------------
    def append(
        self,
        status: str,
        *,
        blocked_by: Optional[str] = None,
        reason_codes: Optional[List[str]] = None,
        version: str = "v0",
    ) -> AuditEntry:
        """
        決定結果のメタデータを記録する。

        Args:
            status: "ok" または "blocked"
            blocked_by: blocked 時の No-Go コード（#6/#5/#4）
            reason_codes: ok 時の selection.reason_codes
            version: スキーマバージョン（デフォルト "v0"）

        Returns:
            記録した AuditEntry
        """
        if status not in ("ok", "blocked"):
            raise ValueError(f"status must be 'ok' or 'blocked', got: {status!r}")

        codes = list(reason_codes or [])
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=self._ttl_hours)

        decision_hash = _compute_hash(status, blocked_by or "", codes)

        entry = AuditEntry(
            timestamp_utc=now.isoformat(),
            decision_hash=decision_hash,
            status=status,
            blocked_by=blocked_by,
            reason_codes=codes,
            version=version,
            expires_at_utc=expires_at.isoformat(),
        )
        self._entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # 取得
    # ------------------------------------------------------------------
    def query(self, *, include_expired: bool = False) -> List[AuditEntry]:
        """
        ログエントリを返す。

        Args:
            include_expired: False（デフォルト）なら TTL 切れを除外
        """
        if include_expired:
            return list(self._entries)
        now = datetime.now(timezone.utc)
        return [e for e in self._entries if _parse_dt(e.expires_at_utc) > now]

    def count(self, *, include_expired: bool = False) -> int:
        return len(self.query(include_expired=include_expired))

    def clear(self) -> None:
        """全エントリを削除（テスト用）。"""
        self._entries.clear()

    # ------------------------------------------------------------------
    # サマリ
    # ------------------------------------------------------------------
    def summary(self, *, include_expired: bool = False) -> Dict[str, Any]:
        """
        ログ統計サマリを返す。

        Returns:
            {
                "total": int,
                "ok_count": int,
                "blocked_count": int,
                "blocked_by_breakdown": {code: count, ...},
                "ttl_hours": int,
            }
        """
        entries = self.query(include_expired=include_expired)
        ok_count = sum(1 for e in entries if e.status == "ok")
        blocked_count = sum(1 for e in entries if e.status == "blocked")

        breakdown: Dict[str, int] = {}
        for e in entries:
            if e.blocked_by:
                breakdown[e.blocked_by] = breakdown.get(e.blocked_by, 0) + 1

        return {
            "total": len(entries),
            "ok_count": ok_count,
            "blocked_count": blocked_count,
            "blocked_by_breakdown": breakdown,
            "ttl_hours": self._ttl_hours,
        }

    def to_json(self, *, include_expired: bool = False) -> str:
        """サマリを JSON 文字列で返す（デバッグ・運用確認用）。"""
        return json.dumps(self.summary(include_expired=include_expired), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# グローバルシングルトン（任意）
# ---------------------------------------------------------------------------
_default_log: Optional[AuditLog] = None


def get_default_log() -> AuditLog:
    """プロセス共有のデフォルトログを返す（シングルトン）。"""
    global _default_log
    if _default_log is None:
        _default_log = AuditLog()
    return _default_log


def record(
    status: str,
    *,
    blocked_by: Optional[str] = None,
    reason_codes: Optional[List[str]] = None,
    version: str = "v0",
) -> AuditEntry:
    """デフォルトログに記録するショートカット。"""
    return get_default_log().append(
        status,
        blocked_by=blocked_by,
        reason_codes=reason_codes,
        version=version,
    )


# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------
def _compute_hash(status: str, blocked_by: str, reason_codes: List[str]) -> str:
    """
    PII を含まない決定メタデータから SHA256 ハッシュを生成。
    同一メタデータ → 同一ハッシュ（再現性あり、内容逆引き不可）。
    """
    payload = json.dumps(
        {"status": status, "blocked_by": blocked_by, "reason_codes": sorted(reason_codes)},
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _parse_dt(iso: str) -> datetime:
    """ISO8601 文字列を datetime (UTC aware) に変換。"""
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
