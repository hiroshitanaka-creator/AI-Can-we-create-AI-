import unittest

from aicw.safety import guard_text


class TestP0Privacy(unittest.TestCase):
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

    def test_allows_clean_text(self):
        text = "no sensitive patterns here"
        allowed, redacted, findings = guard_text(text)
        self.assertTrue(allowed)
        self.assertEqual(text, redacted)
        self.assertEqual([], findings)
