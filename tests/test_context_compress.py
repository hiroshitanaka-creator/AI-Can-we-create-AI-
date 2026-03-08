from __future__ import annotations

import unittest

from aicw.context_compress import compress_situation


class TestContextCompress(unittest.TestCase):
    def test_returns_original_when_disabled(self):
        text = "これは長い入力です。品質と安全を確認します。期限もあります。"
        out = compress_situation(text, enabled=False)
        self.assertEqual(text, out)

    def test_short_text_not_compressed(self):
        text = "短文です。"
        out = compress_situation(text, max_chars=100)
        self.assertEqual(text, out)

    def test_keeps_keyword_sentences_first(self):
        text = (
            "背景説明です。"
            "安全を優先したい。"
            "品質は維持する。"
            "補足説明です。"
            "期限は来週です。"
        )
        out = compress_situation(text, max_sentences=2, max_chars=30)
        self.assertIn("安全", out)
        self.assertTrue("背景説明" not in out or out.index("安全") <= out.index("背景説明"))

    def test_applies_ellipsis_when_trimmed(self):
        text = "A" * 300
        out = compress_situation(text, max_chars=50)
        self.assertTrue(len(out) <= 50)
        self.assertTrue(out.endswith("…"))

    def test_custom_keywords(self):
        text = "intro sentence. privacy is critical. another sentence."
        out = compress_situation(text, max_sentences=1, max_chars=60, keywords=["privacy"])
        self.assertIn("privacy", out.lower())


if __name__ == "__main__":
    unittest.main()
