from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "great-book" / "index.html"


class GreatBookPublicReaderTests(unittest.TestCase):
    def test_public_index_exposes_the_real_reader_shell(self):
        html = INDEX.read_text(encoding="utf-8")

        self.assertNotIn("Reader restoration in progress", html)
        self.assertIn('href="great-book.css"', html)
        self.assertIn('id="gb-search"', html)
        self.assertIn('for="gb-search"', html)
        self.assertIn('id="gb-toc"', html)
        self.assertIn('id="gb-document"', html)
        self.assertIn('id="gb-status"', html)
        self.assertIn('src="../app/great-book-reader.js"', html)

    def test_reader_keeps_primary_text_separate_from_later_project_routes(self):
        html = INDEX.read_text(encoding="utf-8")

        self.assertIn("Read the original book", html)
        self.assertIn("Continue the Potato", html)
        self.assertIn('href="../philosophy/"', html)
        self.assertIn('href="../tim-dooley/story/"', html)
        self.assertIn('href="../explore/"', html)


if __name__ == "__main__":
    unittest.main()
