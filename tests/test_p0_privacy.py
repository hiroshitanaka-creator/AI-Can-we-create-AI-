import unittest

from aicw.safety import guard_text, scan_privacy_risks
from aicw.decision import build_decision_report


class TestP0Privacy(unittest.TestCase):
    # ------------------------------------------------------------------
    # ブロックケース（block severity で検知・停止されるべきパターン）
    # ------------------------------------------------------------------

    def test_blocks_email_like(self):
        # 文字列を分割して組み立てる（ソースに直接それっぽい形を残しにくくする）
        s = "x" + "@" + "y" + "." + "co"
        text = "contact: " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        self.assertNotIn("@", redacted)
        kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("EMAIL_LIKE", kinds)

    def test_blocks_phone_like(self):
        s = "0" + "0" + "-" + "0" + "0" + "-" + "0000"
        text = "phone: " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("PHONE_LIKE", kinds)

    def test_blocks_secret_like_long(self):
        s = "A" * 40
        text = "maybe_secret: " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("SECRET_LIKE_LONG", kinds)

    def test_blocks_postal_code_like(self):
        s = "100" + "-" + "0001"
        text = "住所: 東京都千代田区 " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("POSTAL_CODE_LIKE", kinds)

    def test_blocks_secret_keyword_token(self):
        text = "token: abc123"
        allowed, _redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("SECRET_KEYWORD", kinds)

    def test_blocks_secret_keyword_password(self):
        text = "password が必要です"
        allowed, _redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("SECRET_KEYWORD", kinds)

    def test_blocks_multiple_patterns_all_redacted(self):
        # 複数 block パターンが同時に含まれる場合、全て伏せられること
        email_part = "u" + "@" + "ex" + "." + "jp"
        phone_part = "03" + "-" + "1234" + "-" + "5678"
        text = "email: " + email_part + " tel: " + phone_part
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        self.assertNotIn("@", redacted)
        block_kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("EMAIL_LIKE", block_kinds)
        self.assertIn("PHONE_LIKE", block_kinds)

    def test_redacted_hides_original_content(self):
        # redacted テキストは元の機密値を含まないこと
        s = "A" * 36
        text = "key=" + s
        _allowed, redacted, _findings = guard_text(text)
        self.assertNotIn(s, redacted)
        self.assertIn("<REDACTED:", redacted)

    # ------------------------------------------------------------------
    # warn ケース（IP_LIKE: 過検知が多いため warn 化済み）
    # ------------------------------------------------------------------

    def test_warns_ip_like(self):
        # IP_LIKE は warn レベル → allowed=True（ブロックしない）
        s = "192" + "." + "168" + "." + "0" + "." + "1"
        text = "server at " + s
        allowed, _redacted, findings = guard_text(text)
        self.assertTrue(allowed, "IP_LIKE は warn 化済みなのでブロックされない")
        warn_kinds = {f.kind for f in findings if f.severity == "warn"}
        block_kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("IP_LIKE", warn_kinds)
        self.assertNotIn("IP_LIKE", block_kinds)

    def test_ip_like_creates_dlp_warning_in_report(self):
        # IP_LIKE が入力にあると、report["warnings"] に DLP 警告が追加される
        req = {
            "situation": "サーバー " + "192.168.0.1" + " を使うか決めたい",
            "constraints": [],
            "options": ["案A", "案B", "案C"],
        }
        report = build_decision_report(req)
        self.assertEqual("ok", report["status"])
        self.assertIn("warnings", report)
        warning_text = " ".join(report["warnings"])
        self.assertIn("IP_LIKE", warning_text)

    def test_version_string_warns_not_blocks(self):
        # バージョン番号 1.2.3.4 は IP_LIKE に誤検知されるが、warn なのでブロックしない
        text = "version 1.2.3.4 を使用"
        allowed, _redacted, findings = guard_text(text)
        self.assertTrue(allowed, "バージョン文字列は warn 化済みでブロックされない")
        warn_kinds = {f.kind for f in findings if f.severity == "warn"}
        self.assertIn("IP_LIKE", warn_kinds)

    # ------------------------------------------------------------------
    # 通過ケース（ブロックされないべきテキスト）
    # ------------------------------------------------------------------

    def test_allows_clean_text(self):
        text = "no sensitive patterns here"
        allowed, redacted, findings = guard_text(text)
        self.assertTrue(allowed)
        self.assertEqual(text, redacted)
        self.assertEqual([], findings)

    def test_allows_clean_japanese(self):
        text = "リリース日程を品質重視で決めたい。安全を最優先にする。"
        allowed, _redacted, findings = guard_text(text)
        self.assertTrue(allowed)
        self.assertEqual([], findings)

    def test_allows_short_alphanumeric(self):
        # 31文字以下は SECRET_LIKE_LONG にひっかからない（境界値）
        s = "A" * 31
        text = "id: " + s
        allowed, _redacted, findings = guard_text(text)
        kinds = {f.kind for f in findings}
        self.assertNotIn("SECRET_LIKE_LONG", kinds)

    # ------------------------------------------------------------------
    # 既知の過検知（block のまま残すもの）
    # ------------------------------------------------------------------

    def test_known_false_positive_exactly_32_chars(self):
        # 32文字の英数字は SECRET_LIKE_LONG にひっかかる（境界値）
        # P0 では安全側に倒すためブロック維持
        s = "A" * 32
        text = "value: " + s
        allowed, _redacted, findings = guard_text(text)
        self.assertFalse(allowed, "既知の過検知: 32文字英数字はSECRET_LIKE_LONGに検知される（P0許容）")
        kinds = {f.kind for f in findings if f.severity == "block"}
        self.assertIn("SECRET_LIKE_LONG", kinds)


if __name__ == "__main__":
    unittest.main()
