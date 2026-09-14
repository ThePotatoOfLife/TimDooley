from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_story_archive import validate_story_archive


class StoryArchiveValidatorTests(unittest.TestCase):
    def test_accepts_consistent_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            story = root / "knowledge" / "story"
            story.mkdir(parents=True)
            (story / "cast-book.json").write_text(json.dumps({"cast": [{"id": "tim", "class": "person"}]}))
            (story / "scene-reservoir.json").write_text(json.dumps({"scenes": [{"id": "scene-1", "cast": ["tim"]}]}))
            (story / "dialogue-vault.json").write_text(json.dumps({"dialogues": [{"id": "dialogue-1", "participants": ["tim"], "status": "verbatim"}]}))
            (story / "arc-season-map.json").write_text(json.dumps({"arcs": [{"id": "arc-1", "scene_ids": ["scene-1"]}]}))
            (story / "recovery-notebook.json").write_text(json.dumps({"leads": []}))
            (story / "story-manifest.json").write_text(json.dumps({"files": ["cast-book.json", "scene-reservoir.json", "dialogue-vault.json", "arc-season-map.json", "recovery-notebook.json"]}))
            self.assertEqual(validate_story_archive(root), [])

    def test_rejects_unknown_cast_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            story = root / "knowledge" / "story"
            story.mkdir(parents=True)
            (story / "cast-book.json").write_text(json.dumps({"cast": [{"id": "tim", "class": "person"}]}))
            (story / "scene-reservoir.json").write_text(json.dumps({"scenes": [{"id": "scene-1", "cast": ["missing"]}]}))
            (story / "dialogue-vault.json").write_text(json.dumps({"dialogues": []}))
            (story / "arc-season-map.json").write_text(json.dumps({"arcs": []}))
            (story / "recovery-notebook.json").write_text(json.dumps({"leads": []}))
            (story / "story-manifest.json").write_text(json.dumps({"files": ["cast-book.json", "scene-reservoir.json", "dialogue-vault.json", "arc-season-map.json", "recovery-notebook.json"]}))
            errors = validate_story_archive(root)
            self.assertTrue(any("unknown cast id missing" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
