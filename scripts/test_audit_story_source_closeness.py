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
            (content / "f.html").write_text(
                '<article class="story-entry" data-story-type="side" id="mystery-hint">'
                '<details class="source-note"><p>source note<br/>'
                '<span class="source-paths">knowledge/unknown/source.json</span></p></details></article>',
                encoding="utf-8",
            )
            (content / "g.html").write_text(
                '<article class="story-entry" data-story-type="side" id="note-only-retro">'
                '<details class="source-note"><p>Source note Great Book autobiographical Chapter 24 stratum.</p></details>'
                '</article>',
                encoding="utf-8",
            )
            (content / "h.html").write_text(
                '<article class="story-entry" data-story-type="side" id="note-only-creative">'
                '<details class="source-note"><p>source note Great Book creative scene.</p></details>'
                '</article>',
                encoding="utf-8",
            )
            (content / "i.html").write_text(
                '<article class="story-entry" data-story-type="side" id="note-only-public">'
                '<details class="source-note"><p>Dated public-post compilation, 30 January 2025.</p></details>'
                '</article>',
                encoding="utf-8",
            )

            audit = build_audit(root)
            records = {record["story_id"]: record for record in audit["records"]}

            self.assertEqual(records["public-post"]["mapping_status"], "hinted")
            self.assertEqual(records["public-post"]["hinted_source_classes"], ["public_post_sequence"])
            self.assertEqual(records["song"]["hinted_source_classes"], ["creative_artifact"])
            self.assertEqual(records["great-book-retro"]["hinted_source_classes"], ["later_autobiographical_retelling"])
            self.assertEqual(records["great-book-retro"]["event_distance"], "2_later_first_person_retelling")
            self.assertEqual(records["conversation-recovery"]["hinted_source_classes"], ["conversation_recovery"])
            self.assertEqual(records["blank"]["mapping_status"], "unmapped")
            self.assertEqual(records["mystery-hint"]["mapping_status"], "hinted")
            self.assertEqual(records["mystery-hint"]["hinted_source_classes"], [])

            self.assertEqual(records["note-only-retro"]["mapping_status"], "hinted")
            self.assertEqual(records["note-only-retro"]["source_hints"], [])
            self.assertEqual(records["note-only-retro"]["hinted_source_classes"], ["later_autobiographical_retelling"])
            self.assertEqual(records["note-only-creative"]["hinted_source_classes"], ["great_book_literary_text"])
            self.assertEqual(records["note-only-public"]["hinted_source_classes"], ["public_post_sequence"])

            self.assertEqual(audit["summary"]["source_hinted"], 8)
            self.assertEqual(audit["summary"]["unmapped"], 1)
            self.assertEqual(audit["summary"]["hinted_but_unclassified"], 1)
            self.assertEqual(
                audit["summary"]["hinted_source_class_counts"],
                {
                    "conversation_recovery": 1,
                    "creative_artifact": 1,
                    "great_book_literary_text": 1,
                    "later_autobiographical_retelling": 2,
                    "public_post_sequence": 2,
                },
            )
            self.assertEqual(
                [item["story_id"] for item in audit["excavation_queue"]],
                [
                    "blank",
                    "mystery-hint",
                    "conversation-recovery",
                    "great-book-retro",
                    "note-only-retro",
                    "note-only-public",
                    "note-only-creative",
                    "public-post",
                    "song",
                ],
            )
            self.assertEqual(audit["excavation_queue"][0]["priority"], 100)
            self.assertEqual(audit["excavation_queue"][0]["recommended_next_action"], "find_any_source_trail")


if __name__ == "__main__":
    unittest.main()
