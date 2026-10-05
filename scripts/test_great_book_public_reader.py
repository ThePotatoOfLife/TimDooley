from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "great-book" / "index.html"
CSS = ROOT / "great-book" / "great-book.css"
READER = ROOT / "app" / "great-book-reader.js"


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

    def test_reader_uses_open_book_stage_and_preloads_visual_assets(self):
        html = INDEX.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")

        self.assertIn('class="longform-layout gb-book-stage"', html)
        self.assertIn('class="page-nav"', html)
        self.assertIn('great-book-open-stage.webp" fetchpriority="high"', html)
        self.assertIn(".gb-book-stage", css)
        self.assertIn("great-book-open-stage.webp", css)
        self.assertNotIn("content-visibility:auto", css)

    def test_reader_prefetches_chapters_ahead_without_rewriting_the_whole_toc(self):
        source = READER.read_text(encoding="utf-8")

        self.assertIn("rootMargin:'5200px 0px'", source)
        self.assertIn("rootMargin:'2200px 0px'", source)
        self.assertIn("prefetchSlot", source)
        self.assertIn("requestIdleCallback", source)
        self.assertIn("setCurrentLink(activeCurrentId)", source)
        self.assertNotIn("toc.querySelectorAll('a').forEach(a=>a.setAttribute('aria-current'", source)

    def test_reader_has_shared_tts_controls(self):
        html = INDEX.read_text(encoding="utf-8")

        self.assertIn('href="../app/tts-drawer.css"', html)
        self.assertIn('data-tts-longform', html)
        self.assertIn('data-tts-root="#gb-document"', html)
        self.assertIn('data-tts-item=".gb-slot[data-loaded=\'true\']"', html)
        self.assertIn('src="../app/tts-reader.js"', html)
        self.assertIn('src="../app/tts-drawer.js"', html)
        self.assertIn('src="../app/longform-tts-adapter.js"', html)


if __name__ == "__main__":
    unittest.main()
