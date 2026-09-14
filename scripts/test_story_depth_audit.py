from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from build_story_depth_audit import audit_is_current, build_story_depth_audit


def dump(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def setup(root: Path):
    story = root / "knowledge" / "story"
    content = root / "story-content"
    story.mkdir(parents=True)
    content.mkdir(parents=True)
    dump(story / "story-registry.json", {
        "schema_version": 1,
        "enforcement": "migration",
        "stories": [
            {"id": "a", "path": "story-content/a.html", "story_type": "MAIN STORY", "mode": "documentary", "depth": "ANECDOTE", "source_ids": [], "scene_ids": [], "public_safe": True, "full_story_allowed": False, "migration_status": "classified", "recovery_targets": ["recover turns"]},
            {"id": "b", "path": "story-content/b.html", "story_type": "SIDE STORY", "mode": "literary", "depth": "LITERARY_COMPLETE", "source_ids": ["src-b"], "scene_ids": [], "public_safe": True, "full_story_allowed": True, "migration_status": "verified", "recovery_targets": []},
        ],
    })
    dump(story / "source-records.json", {"schema_version": 1, "sources": [{"id": "src-b", "source_class": "great_book_literary_text", "locator": {"name": "book"}, "public_status": "public_source", "continuity": "literary"}]})
    (content / "a.html").write_text('<article class="story-entry" data-story-type="main" id="a"><time datetime="2025-01-01"></time></article>', encoding="utf-8")
    (content / "b.html").write_text('<article class="story-entry" data-story-type="side" id="b"><time datetime="2025-01-02"></time><details class="full-story"></details></article>', encoding="utf-8")
    (content / "legacy.html").write_text('<article class="story-entry" data-story-type="side" id="legacy"><time datetime="2025-01-03"></time><details class="full-story"></details></article>', encoding="utf-8")


class AuditTests(unittest.TestCase):
    def test_counts_registry_depth_and_unregistered_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup(root)
            data = build_story_depth_audit(root)
            self.assertEqual(data["published"], {"total": 3, "main": 1, "side": 2})
            self.assertEqual(data["registry"], {"registered": 2, "unregistered": 1})
            self.assertEqual(data["depths"]["ANECDOTE"], 1)
            self.assertEqual(data["depths"]["LITERARY_COMPLETE"], 1)
            self.assertEqual(data["full_story"]["html_total"], 2)
            self.assertEqual(data["full_story"]["qualified_registered"], 1)
            self.assertEqual(data["full_story"]["unregistered_full_story"], ["legacy"])
            self.assertEqual(data["recovery_priorities"][0]["story_id"], "a")

    def test_audit_is_current_detects_match_and_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup(root)
            expected = build_story_depth_audit(root)
            dump(root / "knowledge" / "story" / "story-depth-audit.json", expected)
            self.assertTrue(audit_is_current(root))
            dump(root / "knowledge" / "story" / "story-depth-audit.json", {"stale": True})
            self.assertFalse(audit_is_current(root))

    def test_output_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup(root)
            self.assertEqual(build_story_depth_audit(root), build_story_depth_audit(root))


if __name__ == "__main__":
    unittest.main()
