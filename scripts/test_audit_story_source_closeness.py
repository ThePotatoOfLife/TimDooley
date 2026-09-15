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
                '<article class="story-entry" data-story-type="side" id="great-book-retro">'
                '<details class="source-note"><p>great-book retrospective<br/>'
                '<span class="source-paths">The Great Book Of Potato2.odt</span></p></details></article>',
                encoding="utf-8",
            )
            (content / "d.html").write_text(
                '<article class="story-entry" data-story-type="side" id="conversation-recovery">'
                '<details class="source-note"><p>conversation recovery<br/>'
                '<span class="source-paths">knowledge/timeline/developmental-genealogy.json</span></p></details></article>',
                encoding="utf-8",
            )
            (content / "e.html").write_text(
                '<article class="story-entry" data-story-type="side" id="blank"></article>',
                encoding="utf-8",
            )

            audit = build_audit(root)
            records = {record["story_id"]: record for record in audit["records"]}

            self.assertEqual(records["public-post"]["mapping_status"], "hinted")
            self.assertEqual(
                records["public-post"]["hinted_source_classes"],
                ["public_post_sequence"],
            )
            self.assertEqual(records["song"]["hinted_source_classes"], ["creative_artifact"])
            self.assertEqual(
                records["great-book-retro"]["hinted_source_classes"],
                ["later_autobiographical_retelling"],
            )
            self.assertEqual(
                records["great-book-retro"]["event_distance"],
                "2_later_first_person_retelling",
            )
            self.assertEqual(
                records["conversation-recovery"]["hinted_source_classes"],
                ["conversation_recovery"],
            )
            self.assertEqual(records["blank"]["mapping_status"], "unmapped")
            self.assertEqual(audit["summary"]["source_hinted"], 4)
            self.assertEqual(audit["summary"]["unmapped"], 1)
            self.assertEqual(
                audit["summary"]["hinted_source_class_counts"],
                {
                    "conversation_recovery": 1,
                    "creative_artifact": 1,
                    "later_autobiographical_retelling": 1,
                    "public_post_sequence": 1,
                },
            )


if __name__ == "__main__":
    unittest.main()
