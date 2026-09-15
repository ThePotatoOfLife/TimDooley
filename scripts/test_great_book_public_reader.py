from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "great-book" / "index.html"
BOOK_INDEX = ROOT / "great-book" / "book-index.json"


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

    def test_reader_has_shared_tts_controls(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="../app/tts-drawer.css"', html)
        self.assertIn('data-tts-longform', html)
        self.assertIn('data-tts-root="#gb-document"', html)
        self.assertIn('data-tts-item=".gb-slot[data-loaded=\'true\']"', html)
        self.assertIn('src="../app/tts-reader.js"', html)
        self.assertIn('src="../app/tts-drawer.js"', html)
        self.assertIn('src="../app/longform-tts-adapter.js"', html)

    def test_verified_restoration_batch_is_present_and_review_gaps_are_explicit(self):
        index = json.loads(BOOK_INDEX.read_text(encoding="utf-8"))
        restoration = index["restoration"]
        self.assertEqual(restoration["mode"], "verified-batches")
        self.assertEqual(restoration["reader_accounted_through_order"], 49)
        self.assertEqual(restoration["reader_accounted_through_chapter"], "19.82")
        self.assertEqual(
            restoration["deferred_public_review"],
            ["7.4", "9.3", "9.31", "9.32", "15.11"],
        )

        required = [
            "chapters/015--chapter-9-1--the-mud-dwellers-and-the-vibration-of-shame.html",
            "chapters/016--chapter-9-11--the-path-of-gluttony-and-the-sacred-potato.html",
            "chapters/017--chapter-9-2--the-ballad-of-the-mud-dwellers-and-the-potato-path.html",
            "chapters/041--chapter-19-6--axomamma-the-sacred-mother-of-potatoes.html",
            "chapters/042--chapter-19-66--the-cradle-of-judaism-from-ashes-to-identity.html",
            "chapters/043--chapter-19-67--africa-the-sacred-soil-and-the-potatos-journey.html",
            "chapters/044--chapter-19-7--roots-across-oceans-the-potatos-journey-to-europe.html",
            "chapters/045--chapter-19-8--from-rivers-to-roots-the-myth-of-tammuz-and-the-eternal-harvest-of-the-p.html",
            "chapters/046--chapter-19-81--the-shadow-of-the-dark-ages-seeds-of-dormancy-and-revival.html",
            "chapters/047--chapter-19-811--orthodoxy-and-the-quiet-roots-of-thought-a-potatoist-reflection-on-faith.html",
            "chapters/048--chapter-19-815--the-bridge-of-transformation-the-potatos-arrival-in-europe.html",
            "chapters/049--chapter-19-82--the-renaissance-humanitys-rebirth-and-rediscovery.html",
        ]
        for rel in required:
            self.assertTrue((ROOT / "great-book" / rel).is_file(), f"restoration batch missing {rel}")


if __name__ == "__main__":
    unittest.main()
