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

    def test_verified_restoration_frontier_is_complete(self):
        index = json.loads(BOOK_INDEX.read_text(encoding="utf-8"))
        restoration = index["restoration"]
        self.assertEqual(restoration["mode"], "verified-batches")
        self.assertEqual(restoration["contiguous_through_order"], 45)
        self.assertEqual(restoration["contiguous_through_chapter"], "19.8")

        records = []
        for shard in index["shards"]:
            records.extend(json.loads((ROOT / "great-book" / shard).read_text(encoding="utf-8")))
        for record in records[: restoration["contiguous_through_order"]]:
            if record["status"] != "body":
                continue
            chapter = ROOT / "great-book" / record["path"]
            self.assertTrue(chapter.is_file(), f"restored frontier missing {record['path']}")


if __name__ == "__main__":
    unittest.main()
