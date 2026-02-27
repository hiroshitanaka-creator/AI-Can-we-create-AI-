import unittest

from aicw.safety import guard_text, scan_privacy_risks


class TestP0Privacy(unittest.TestCase):
    # ------------------------------------------------------------------
    # ブロックケース（検知できるべきパターン）
    # ------------------------------------------------------------------

    def test_blocks_email_like(self):
        # 文字列を分割して組み立てる（ソースに直接それっぽい形を残しにくくする）
        s = "x" + "@" + "y" + "." + "co"
        text = "contact: " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        self.assertNotIn("@", redacted)
        kinds = {f.kind for f in findings}
        self.assertIn("EMAIL_LIKE", kinds)

    def test_blocks_phone_like(self):
        s = "0" + "0" + "-" + "0" + "0" + "-" + "0000"
        text = "phone: " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings}
        self.assertIn("PHONE_LIKE", kinds)

    def test_blocks_secret_like_long(self):
        s = "A" * 40
        text = "maybe_secret: " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings}
        self.assertIn("SECRET_LIKE_LONG", kinds)

    def test_blocks_ip_like(self):
        s = "192" + "." + "168" + "." + "0" + "." + "1"
        text = "server at " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings}
        self.assertIn("IP_LIKE", kinds)

    def test_blocks_postal_code_like(self):
        s = "100" + "-" + "0001"
        text = "住所: 東京都千代田区 " + s
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings}
        self.assertIn("POSTAL_CODE_LIKE", kinds)

    def test_blocks_secret_keyword_token(self):
        text = "token: abc123"
        allowed, _redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings}
        self.assertIn("SECRET_KEYWORD", kinds)

    def test_blocks_secret_keyword_password(self):
        text = "password が必要です"
        allowed, _redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        kinds = {f.kind for f in findings}
        self.assertIn("SECRET_KEYWORD", kinds)

    def test_blocks_multiple_patterns_all_redacted(self):
        # 複数パターンが同時に含まれる場合、全て伏せられること
        email_part = "u" + "@" + "ex" + "." + "jp"
        phone_part = "03" + "-" + "1234" + "-" + "5678"
        text = "email: " + email_part + " tel: " + phone_part
        allowed, redacted, findings = guard_text(text)
        self.assertFalse(allowed)
        self.assertNotIn("@", redacted)
        kinds = {f.kind for f in findings}
        self.assertIn("EMAIL_LIKE", kinds)
        self.assertIn("PHONE_LIKE", kinds)

    def test_redacted_hides_original_content(self):
        # redacted テキストは元の機密値を含まないこと
        s = "A" * 36
        text = "key=" + s
        _allowed, redacted, _findings = guard_text(text)
        self.assertNotIn(s, redacted)
        self.assertIn("<REDACTED:", redacted)

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
        # 31文字以下はSECRET_LIKE_LONGにひっかからない（境界値）
        s = "A" * 31
        text = "id: " + s
        allowed, _redacted, findings = guard_text(text)
        # 31文字はブロックしない（32文字からブロック）
        kinds = {f.kind for f in findings}
        self.assertNotIn("SECRET_LIKE_LONG", kinds)

    # ------------------------------------------------------------------
    # 既知の過検知（P0は安全側に倒すため意図的にブロックする）
    # 将来の改善でwarnに変える候補
    # ------------------------------------------------------------------

    def test_known_false_positive_version_string_looks_like_ip(self):
        # バージョン番号 (例: 1.2.3.4) は IP_LIKE に誤検知する
        # P0 の方針（安全側に倒す）でブロックは許容。将来 warn 化の候補。
        text = "version 1.2.3.4 を使用"
        allowed, _redacted, findings = guard_text(text)
        kinds = {f.kind for f in findings}
        # 過検知が発生していることを記録（assertFalse で正とする）
        if "IP_LIKE" in kinds:
            self.assertFalse(allowed, "既知の過検知: バージョン番号がIP_LIKEに検知される（P0許容）")

    def test_known_false_positive_exactly_32_chars(self):
        # 32文字の英数字は SECRET_LIKE_LONG にひっかかる（境界値）
        s = "A" * 32
        text = "value: " + s
        allowed, _redacted, findings = guard_text(text)
        self.assertFalse(allowed, "既知の過検知: 32文字英数字はSECRET_LIKE_LONGに検知される（P0許容）")
        kinds = {f.kind for f in findings}
        self.assertIn("SECRET_LIKE_LONG", kinds)


if __name__ == "__main__":
    unittest.main()
