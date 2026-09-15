from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from audit_story_source_closeness import build_audit


def dump(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class SourceHintTests(unittest.TestCase):
    def test_unregistered_source_notes_become_hints_without_claiming_verified_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dump(root / "knowledge/story/story-registry.json", {"stories": []})
            dump(root / "knowledge/story/source-records.json", {"sources": []})
            content = root / "story-content"
            content.mkdir(parents=True)

            (content / "a.html").write_text(
                '<article class="story-entry" data-story-type="side" id="public-post">'
                '<details class="source-note"><span class="source-paths">'
                'Rational_Potato public-post compilation · 4 Oct 2024'
                '</span></details></article>',
                encoding="utf-8",
            )
            (content / "b.html").write_text(
                '<article class="story-entry" data-story-type="side" id="song">'
                '<details class="source-note"><span class="source-paths">'
                'knowledge/creative/tim-dooley-suno-music-archive.json'
                '</span></details></article>',
                encoding="utf-8",
            )
            (content / "c.html").write_text(
                '<article class="story-entry" data-story-type="side" id="blank"></article>',
                encoding="utf-8",
            )

            audit = build_audit(root)
            records = {record["story_id"]: record for record in audit["records"]}

            self.assertEqual(records["public-post"]["mapping_status"], "hinted")
            self.assertEqual(
                records["public-post"]["source_hints"],
                ["Rational_Potato public-post compilation · 4 Oct 2024"],
            )
            self.assertEqual(
                records["public-post"]["hinted_source_classes"],
                ["public_post_sequence"],
            )
            self.assertEqual(
                records["public-post"]["event_distance"],
                "1_contemporaneous_compilation",
            )
            self.assertEqual(records["song"]["hinted_source_classes"], ["creative_artifact"])
            self.assertEqual(records["song"]["event_distance"], "0_direct_contemporaneous")
            self.assertEqual(records["blank"]["mapping_status"], "unmapped")
            self.assertEqual(audit["summary"]["source_hinted"], 2)
            self.assertEqual(audit["summary"]["unmapped"], 1)


if __name__ == "__main__":
    unittest.main()
