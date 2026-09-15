from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_story_archive import validate_story_archive


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def base(root: Path, enforcement="migration") -> Path:
    story = root / "knowledge" / "story"
    (root / "story-content").mkdir(parents=True)
    story.mkdir(parents=True)
    dump(story / "cast-book.json", {"cast": [{"id": "tim", "class": "person"}]})
    dump(story / "arc-season-map.json", {"arcs": []})
    dump(story / "source-records.json", {"schema_version": 1, "sources": []})
    dump(story / "scene-packets.json", {"schema_version": 1, "scenes": []})
    dump(story / "story-registry.json", {"schema_version": 1, "enforcement": enforcement, "stories": []})
    return story


def html(root: Path, story_id="story-1", *, full=False, depth=None, mode=None, name="story.html") -> None:
    attrs = [f'id="{story_id}"', 'class="story-entry story-entry--side"', 'data-story-type="side"']
    if depth:
        attrs.append(f'data-story-depth="{depth.lower()}"')
    if mode:
        attrs.append(f'data-story-mode="{mode}"')
    details = '<details class="full-story"><summary>Hear the full story</summary></details>' if full else ''
    (root / "story-content" / name).write_text(
        f'<article {" ".join(attrs)}><time datetime="2026-03-02">2 March 2026</time>{details}</article>',
        encoding="utf-8",
    )


def source(*, source_class="consecutive_transcript", continuity="consecutive", public_status="public_source", public_excerpt=None):
    return {
        "id": "src-1", "source_class": source_class, "date_or_period": "2026-03-02", "origin": "library",
        "locator": {"name": "raw.txt", "file_id": "file_1", "line_start": 1, "line_end": 20},
        "speaker_scope": ["tim", "other"], "public_status": public_status, "continuity": continuity,
        "attestation": "primary_or_near_primary", "public_excerpt": public_excerpt, "notes": [],
    }


def scene(*, ending_state="changed", seqs=(1, 2)):
    return {
        "id": "scene-1", "story_id": "story-1", "source_ids": ["src-1"], "date_or_period": "2026-03-02",
        "cast": ["tim"], "scene_type": "conversation_investigation", "opening_state": "question",
        "tim_goal": "understand", "resistance_or_problem": "disagreement",
        "ordered_beats": [
            {"seq": seq, "speaker": "tim" if i % 2 == 0 else "other", "kind": "exact_turn", "source_id": "src-1",
             "source_locator": {"line_start": i + 1, "line_end": i + 1}, "public_text": None, "summary": f"beat {i+1}"}
            for i, seq in enumerate(seqs)
        ],
        "turning_points": ["correction"], "ending_state": ending_state, "ending_status": "resolved",
        "what_changed_after": "position clarified", "unknowns": [], "publication_notes": [],
    }


def reg(*, depth="TRANSCRIPT_DEPTH", mode="documentary", full=True, sources=None, scenes=None, path="story-content/story.html"):
    return {
        "id": "story-1", "path": path, "story_type": "SIDE STORY", "mode": mode, "depth": depth,
        "date_or_period": "2026-03-02", "source_ids": sources or [], "scene_ids": scenes or [],
        "public_safe": True, "full_story_allowed": full, "migration_status": "verified", "recovery_targets": [],
    }


class StoryEvidenceGateTests(unittest.TestCase):
    def test_rejects_anecdote_promoted_to_full_story(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True)
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="ANECDOTE", full=True)]})
            errors = validate_story_archive(root)
            self.assertTrue(any("ANECDOTE" in e and "full" in e.lower() for e in errors), errors)

    def test_accepts_transcript_depth_with_consecutive_source_and_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True, depth="TRANSCRIPT_DEPTH", mode="documentary")
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source()]})
            dump(story / "scene-packets.json", {"schema_version": 1, "scenes": [scene()]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(sources=["src-1"], scenes=["scene-1"])]})
            self.assertEqual(validate_story_archive(root), [])

    def test_rejects_transcript_depth_backed_only_by_archaeology_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True)
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source(source_class="archaeology_summary", continuity="retrospective")]})
            dump(story / "scene-packets.json", {"schema_version": 1, "scenes": [scene()]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(sources=["src-1"], scenes=["scene-1"])]})
            errors = validate_story_archive(root)
            self.assertTrue(any("qualifying" in e.lower() or "archaeology" in e.lower() for e in errors), errors)

    def test_rejects_scene_missing_ending_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True)
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source()]})
            dump(story / "scene-packets.json", {"schema_version": 1, "scenes": [scene(ending_state="")]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="SCENE", sources=["src-1"], scenes=["scene-1"])]})
            errors = validate_story_archive(root)
            self.assertTrue(any("ending" in e.lower() for e in errors), errors)

    def test_accepts_literary_complete_with_literary_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True, depth="LITERARY_COMPLETE", mode="literary")
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source(source_class="great_book_literary_text", continuity="literary")]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="LITERARY_COMPLETE", mode="literary", sources=["src-1"])]})
            self.assertEqual(validate_story_archive(root), [])

    def test_accepts_literary_complete_with_adopted_creative_artifact_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True, depth="LITERARY_COMPLETE", mode="literary")
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source(source_class="creative_artifact", continuity="literary")]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="LITERARY_COMPLETE", mode="literary", sources=["src-1"])]})
            self.assertEqual(validate_story_archive(root), [])

    def test_rejects_missing_source_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root)
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="FRAGMENT", full=False, sources=["missing"])]})
            self.assertTrue(any("unknown source" in e.lower() for e in validate_story_archive(root)))

    def test_rejects_missing_scene_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True)
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source()]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="SCENE", sources=["src-1"], scenes=["missing"])]})
            self.assertTrue(any("unknown scene" in e.lower() for e in validate_story_archive(root)))

    def test_rejects_duplicate_registry_story_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root)
            item = reg(depth="FRAGMENT", full=False)
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [item, dict(item)]})
            self.assertTrue(any("duplicate story registry id" in e.lower() for e in validate_story_archive(root)))

    def test_rejects_private_no_quote_source_with_public_excerpt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root)
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source(public_status="private_source_no_quote", public_excerpt="secret")]})
            self.assertTrue(any("public_excerpt" in e for e in validate_story_archive(root)))

    def test_rejects_public_text_from_private_no_quote_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True)
            sc = scene(); sc["ordered_beats"][0]["public_text"] = "secret"
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source(public_status="private_source_no_quote")]})
            dump(story / "scene-packets.json", {"schema_version": 1, "scenes": [sc]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="SCENE", sources=["src-1"], scenes=["scene-1"])]})
            self.assertTrue(any("public_text" in e for e in validate_story_archive(root)))

    def test_rejects_non_increasing_beat_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root); html(root, full=True)
            dump(story / "source-records.json", {"schema_version": 1, "sources": [source()]})
            dump(story / "scene-packets.json", {"schema_version": 1, "scenes": [scene(seqs=(2, 1))]})
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="SCENE", sources=["src-1"], scenes=["scene-1"])]})
            self.assertTrue(any("sequence" in e.lower() for e in validate_story_archive(root)))

    def test_rejects_missing_registry_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); story = base(root)
            dump(story / "story-registry.json", {"schema_version": 1, "enforcement": "migration", "stories": [reg(depth="FRAGMENT", full=False, path="story-content/missing.html")]})
            self.assertTrue(any("path" in e.lower() and "missing" in e.lower() for e in validate_story_archive(root)))

    def test_migration_mode_permits_unregistered_legacy_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); base(root, "migration"); html(root, story_id="legacy")
            self.assertEqual(validate_story_archive(root), [])

    def test_strict_mode_rejects_unregistered_legacy_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); base(root, "strict"); html(root, story_id="legacy")
            self.assertTrue(any("unregistered" in e.lower() for e in validate_story_archive(root)))

    def test_rejects_duplicate_public_story_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); base(root, "strict"); html(root, story_id="dupe", name="a.html"); html(root, story_id="dupe", name="b.html")
            self.assertTrue(any("duplicate public story id" in e.lower() for e in validate_story_archive(root)))


if __name__ == "__main__":
    unittest.main()
