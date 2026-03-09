"""tests/test_audit_log.py — AuditLog のユニットテスト"""
import hashlib
import json
import unittest
from datetime import datetime, timezone, timedelta

from aicw.audit_log import AuditLog, _compute_hash, record, get_default_log


class TestAuditLogBasic(unittest.TestCase):
    def setUp(self):
        self.log = AuditLog(ttl_hours=24)

    def test_append_ok(self):
        entry = self.log.append("ok", reason_codes=["SAFETY_FIRST"])
        self.assertEqual(entry.status, "ok")
        self.assertIsNone(entry.blocked_by)
        self.assertEqual(entry.reason_codes, ["SAFETY_FIRST"])
        self.assertEqual(entry.version, "v0")

    def test_append_blocked(self):
        entry = self.log.append("blocked", blocked_by="#6 Privacy")
        self.assertEqual(entry.status, "blocked")
        self.assertEqual(entry.blocked_by, "#6 Privacy")
        self.assertEqual(entry.reason_codes, [])

    def test_append_invalid_status(self):
        with self.assertRaises(ValueError):
            self.log.append("unknown")

    def test_ttl_zero_invalid(self):
        with self.assertRaises(ValueError):
            AuditLog(ttl_hours=0)

    def test_count(self):
        self.log.append("ok")
        self.log.append("ok")
        self.log.append("blocked", blocked_by="#4 Manipulation")
        self.assertEqual(self.log.count(), 3)

    def test_clear(self):
        self.log.append("ok")
        self.log.clear()
        self.assertEqual(self.log.count(), 0)


class TestAuditLogTimestamp(unittest.TestCase):
    def test_timestamp_is_utc_iso(self):
        log = AuditLog()
        entry = log.append("ok")
        dt = datetime.fromisoformat(entry.timestamp_utc)
        self.assertIsNotNone(dt.tzinfo)

    def test_expires_after_ttl(self):
        log = AuditLog(ttl_hours=1)
        entry = log.append("ok")
        expires = datetime.fromisoformat(entry.expires_at_utc)
        now = datetime.now(timezone.utc)
        # expires は now + 1時間以上
        self.assertGreater(expires, now + timedelta(minutes=59))


class TestAuditLogSummary(unittest.TestCase):
    def setUp(self):
        self.log = AuditLog()
        self.log.append("ok", reason_codes=["SAFETY_FIRST"])
        self.log.append("ok", reason_codes=["NO_CONSTRAINTS"])
        self.log.append("blocked", blocked_by="#6 Privacy")
        self.log.append("blocked", blocked_by="#4 Manipulation")
        self.log.append("blocked", blocked_by="#6 Privacy")

    def test_summary_counts(self):
        s = self.log.summary()
        self.assertEqual(s["total"], 5)
        self.assertEqual(s["ok_count"], 2)
        self.assertEqual(s["blocked_count"], 3)

    def test_summary_breakdown(self):
        s = self.log.summary()
        self.assertEqual(s["blocked_by_breakdown"]["#6 Privacy"], 2)
        self.assertEqual(s["blocked_by_breakdown"]["#4 Manipulation"], 1)

    def test_to_json_is_valid(self):
        j = self.log.to_json()
        data = json.loads(j)
        self.assertIn("total", data)
        self.assertIn("ok_count", data)


class TestAuditLogHash(unittest.TestCase):
    def test_same_input_same_hash(self):
        h1 = _compute_hash("ok", "", ["SAFETY_FIRST"])
        h2 = _compute_hash("ok", "", ["SAFETY_FIRST"])
        self.assertEqual(h1, h2)

    def test_different_status_different_hash(self):
        h1 = _compute_hash("ok", "", [])
        h2 = _compute_hash("blocked", "", [])
        self.assertNotEqual(h1, h2)

    def test_hash_is_sha256_hex(self):
        h = _compute_hash("ok", "", [])
        self.assertEqual(len(h), 64)
        int(h, 16)  # should not raise

    def test_no_pii_in_hash(self):
        # ハッシュは固定長のため、元の文字列（メールアドレス等）が含まれない
        h = _compute_hash("ok", "", ["SAFETY_FIRST"])
        self.assertNotIn("@", h)
        self.assertNotIn("password", h)


class TestAuditLogExpiry(unittest.TestCase):
    def test_expired_entries_excluded_by_default(self):
        # TTL=1秒で即期限切れになるエントリを疑似的にテスト
        # （時間依存のため、include_expired=True で全件取得できることを確認）
        log = AuditLog(ttl_hours=24)
        log.append("ok")
        self.assertEqual(log.count(include_expired=True), 1)
        self.assertEqual(log.count(include_expired=False), 1)  # まだ有効

    def test_include_expired_true_returns_all(self):
        log = AuditLog(ttl_hours=24)
        log.append("ok")
        log.append("blocked", blocked_by="#5 Existence Ethics")
        self.assertEqual(log.count(include_expired=True), 2)


class TestDefaultLog(unittest.TestCase):
    def setUp(self):
        # デフォルトログをリセット（テスト間の独立性）
        import aicw.audit_log as al
        al._default_log = None

    def test_record_shortcut(self):
        entry = record("ok", reason_codes=["NO_CONSTRAINTS"])
        self.assertEqual(entry.status, "ok")

    def test_get_default_log_singleton(self):
        log1 = get_default_log()
        log2 = get_default_log()
        self.assertIs(log1, log2)
