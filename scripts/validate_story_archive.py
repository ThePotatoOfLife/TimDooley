from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ALLOWED_CLASSES = {"person", "collective", "great_book_character", "created_being", "platform_or_system"}
ALLOWED_SOURCE_CLASSES = {
    "consecutive_transcript", "public_chat_transcript", "public_thread", "public_post_sequence",
    "single_recovered_turn", "isolated_quote_recovery", "later_autobiographical_retelling",
    "great_book_literary_text", "creative_artifact", "archaeology_summary", "statement_ledger",
    "external_documentary_source",
}
ALLOWED_CONTINUITY = {"consecutive", "partially_consecutive", "isolated", "retrospective", "literary"}
ALLOWED_PUBLIC_STATUS = {
    "public_source", "public_safe_excerpt", "private_source_public_safe_excerpt",
    "private_source_no_quote", "internal_recovery_only",
}
ALLOWED_DEPTH = {"FRAGMENT", "ANECDOTE", "SCENE", "TRANSCRIPT_DEPTH", "LITERARY_COMPLETE"}
ALLOWED_MODES = {"documentary", "literary", "mixed"}
ALLOWED_STORY_TYPES = {"MAIN STORY", "SIDE STORY"}
ALLOWED_MIGRATION_STATUS = {"unclassified", "classified", "packetized", "verified"}
ALLOWED_ENDING_STATUS = {"resolved", "explicitly_unresolved"}
ALLOWED_BEAT_KINDS = {
    "exact_turn", "near_verbatim_turn", "public_post", "documented_action",
    "artifact_created", "later_retelling_context", "narrative_bridge",
}
QUALIFYING_DOCUMENTARY_SOURCES = {
    "consecutive_transcript", "public_chat_transcript", "public_thread", "public_post_sequence",
    "external_documentary_source", "creative_artifact",
}
QUALIFYING_LITERARY_SOURCES = {"great_book_literary_text", "creative_artifact"}
NO_QUOTE_STATUSES = {"private_source_no_quote", "internal_recovery_only"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _duplicates(values):
    seen = set()
    dupes = set()
    for value in values:
        if value in seen:
            dupes.add(value)
        seen.add(value)
    return sorted(dupes)


def depth_allows_full_story(mode: str, depth: str) -> bool:
    if mode == "literary":
        return depth == "LITERARY_COMPLETE"
    return depth in {"SCENE", "TRANSCRIPT_DEPTH"}


class _StoryHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.entries: list[dict] = []
        self._stack: list[dict] = []

    @staticmethod
    def _attrs(attrs):
        return {k: v for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        a = self._attrs(attrs)
        classes = set((a.get("class") or "").split())
        if tag == "article" and "story-entry" in classes:
            self._stack.append({
                "id": a.get("id"),
                "story_type": a.get("data-story-type"),
                "depth": a.get("data-story-depth"),
                "mode": a.get("data-story-mode"),
                "datetime": None,
                "has_full_story": False,
            })
            return
        if not self._stack:
            return
        if tag == "details" and "full-story" in classes:
            self._stack[-1]["has_full_story"] = True
        elif tag == "time" and self._stack[-1]["datetime"] is None:
            self._stack[-1]["datetime"] = a.get("datetime")

    def handle_endtag(self, tag):
        if tag == "article" and self._stack:
            self.entries.append(self._stack.pop())


def scan_public_story_entries(root: Path) -> list[dict]:
    out: list[dict] = []
    content = root / "story-content"
    if not content.exists():
        return out
    for path in sorted(content.glob("*.html")):
        parser = _StoryHTMLParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        for entry in parser.entries:
            item = dict(entry)
            item["path"] = path.relative_to(root).as_posix()
            out.append(item)
    return out


def validate_story_archive(root: Path) -> list[str]:
    story = root / "knowledge" / "story"
    errors: list[str] = []

    for path in (story / "cast-book.json", story / "arc-season-map.json"):
        if not path.exists():
            errors.append(f"missing {path.relative_to(root)}")
            return errors

    try:
        cast_data = _load(story / "cast-book.json")
        arc_data = _load(story / "arc-season-map.json")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"story archive parse error: {exc}"]

    cast = cast_data.get("cast", [])
    cast_ids = [entry.get("id") for entry in cast]
    for duplicate in _duplicates(cast_ids):
        errors.append(f"duplicate cast id {duplicate}")
    for entry in cast:
        if not entry.get("id"):
            errors.append("cast entry missing id")
        if entry.get("class") not in ALLOWED_CLASSES:
            errors.append(f"invalid cast class for {entry.get('id', '<unknown>')}")

    arcs = arc_data.get("arcs", [])
    for duplicate in _duplicates([entry.get("id") for entry in arcs]):
        errors.append(f"duplicate arc id {duplicate}")
    for entry in arcs:
        if not entry.get("id"):
            errors.append("arc entry missing id")
        for cast_id in entry.get("cast", []):
            if cast_id not in cast_ids:
                errors.append(f"arc {entry.get('id')} references unknown cast id {cast_id}")

    evidence_paths = [story / "source-records.json", story / "scene-packets.json", story / "story-registry.json"]
    if not any(path.exists() for path in evidence_paths):
        return errors
    for path in evidence_paths:
        if not path.exists():
            errors.append(f"missing {path.relative_to(root)}")
    if errors:
        return errors

    try:
        source_data = _load(story / "source-records.json")
        scene_data = _load(story / "scene-packets.json")
        registry_data = _load(story / "story-registry.json")
    except (OSError, json.JSONDecodeError) as exc:
        return [*errors, f"story evidence parse error: {exc}"]

    sources = source_data.get("sources", [])
    source_ids = [x.get("id") for x in sources]
    for duplicate in _duplicates(source_ids):
        errors.append(f"duplicate source id {duplicate}")
    source_map = {x.get("id"): x for x in sources if x.get("id")}
    for src in sources:
        sid = src.get("id", "<unknown>")
        if not src.get("id"):
            errors.append("source entry missing id")
        if src.get("source_class") not in ALLOWED_SOURCE_CLASSES:
            errors.append(f"invalid source class for {sid}")
        if src.get("continuity") not in ALLOWED_CONTINUITY:
            errors.append(f"invalid continuity for {sid}")
        status = src.get("public_status")
        if status not in ALLOWED_PUBLIC_STATUS:
            errors.append(f"invalid public_status for {sid}")
        if not isinstance(src.get("locator"), dict) or not src.get("locator"):
            errors.append(f"source {sid} missing locator")
        if status in NO_QUOTE_STATUSES and src.get("public_excerpt") is not None:
            errors.append(f"source {sid} public_excerpt forbidden for {status}")
        if status == "private_source_public_safe_excerpt" and src.get("public_excerpt") is not None and src.get("public_excerpt_reviewed") is not True:
            errors.append(f"source {sid} private public_excerpt requires public_excerpt_reviewed true")

    scenes = scene_data.get("scenes", [])
    for duplicate in _duplicates([x.get("id") for x in scenes]):
        errors.append(f"duplicate scene id {duplicate}")
    scene_map = {x.get("id"): x for x in scenes if x.get("id")}
    for sc in scenes:
        scid = sc.get("id", "<unknown>")
        if not sc.get("id"):
            errors.append("scene entry missing id")
        if not sc.get("story_id"):
            errors.append(f"scene {scid} missing story_id")
        for sid in sc.get("source_ids", []):
            if sid not in source_map:
                errors.append(f"scene {scid} references unknown source {sid}")
        for cid in sc.get("cast", []):
            if cid not in cast_ids:
                errors.append(f"scene {scid} references unknown cast id {cid}")
        if not sc.get("opening_state"):
            errors.append(f"scene {scid} missing opening_state")
        if not sc.get("resistance_or_problem"):
            errors.append(f"scene {scid} missing resistance_or_problem")
        if not sc.get("ending_state"):
            errors.append(f"scene {scid} missing ending_state")
        if sc.get("ending_status") not in ALLOWED_ENDING_STATUS:
            errors.append(f"scene {scid} invalid ending_status")
        beats = sc.get("ordered_beats", [])
        seqs = [beat.get("seq") for beat in beats]
        if any(not isinstance(v, int) for v in seqs) or any(b <= a for a, b in zip(seqs, seqs[1:])):
            errors.append(f"scene {scid} beat sequence must be strictly increasing")
        for beat in beats:
            kind = beat.get("kind")
            if kind not in ALLOWED_BEAT_KINDS:
                errors.append(f"scene {scid} invalid beat kind {kind}")
            sid = beat.get("source_id")
            src = source_map.get(sid)
            if not src:
                errors.append(f"scene {scid} beat references unknown source {sid}")
                continue
            if kind in {"exact_turn", "near_verbatim_turn"} and not isinstance(beat.get("source_locator"), dict):
                errors.append(f"scene {scid} {kind} beat missing source_locator")
            if beat.get("public_text") is not None and src.get("public_status") in NO_QUOTE_STATUSES:
                errors.append(f"scene {scid} public_text forbidden by source {sid} status")

    registry = registry_data.get("stories", [])
    for duplicate in _duplicates([x.get("id") for x in registry]):
        errors.append(f"duplicate story registry id {duplicate}")
    reg_map = {x.get("id"): x for x in registry if x.get("id")}

    public_entries = scan_public_story_entries(root)
    public_ids = [x.get("id") for x in public_entries]
    for duplicate in _duplicates(public_ids):
        errors.append(f"duplicate public story id {duplicate}")
    public_by_id: dict[str, list[dict]] = {}
    for item in public_entries:
        public_by_id.setdefault(item.get("id"), []).append(item)

    enforcement = registry_data.get("enforcement", "migration")
    if enforcement not in {"migration", "strict"}:
        errors.append(f"invalid story registry enforcement {enforcement}")

    for reg in registry:
        rid = reg.get("id", "<unknown>")
        mode = reg.get("mode")
        depth = reg.get("depth")
        if mode not in ALLOWED_MODES:
            errors.append(f"story {rid} invalid mode {mode}")
        if depth not in ALLOWED_DEPTH:
            errors.append(f"story {rid} invalid depth {depth}")
        if reg.get("story_type") not in ALLOWED_STORY_TYPES:
            errors.append(f"story {rid} invalid story_type")
        if reg.get("migration_status") not in ALLOWED_MIGRATION_STATUS:
            errors.append(f"story {rid} invalid migration_status")
        path = root / str(reg.get("path", ""))
        if not reg.get("path") or not path.exists():
            errors.append(f"story {rid} registry path missing: {reg.get('path')}")
        for sid in reg.get("source_ids", []):
            if sid not in source_map:
                errors.append(f"story {rid} references unknown source {sid}")
        for scid in reg.get("scene_ids", []):
            if scid not in scene_map:
                errors.append(f"story {rid} references unknown scene {scid}")

        allowed_full = depth_allows_full_story(mode, depth) if mode in ALLOWED_MODES and depth in ALLOWED_DEPTH else False
        if bool(reg.get("full_story_allowed")) != allowed_full:
            errors.append(f"story {rid} depth {depth} / mode {mode} full_story_allowed mismatch")
        if depth in {"SCENE", "TRANSCRIPT_DEPTH"} and mode in {"documentary", "mixed"}:
            story_sources = [source_map[sid] for sid in reg.get("source_ids", []) if sid in source_map]
            if not any(src.get("source_class") in QUALIFYING_DOCUMENTARY_SOURCES for src in story_sources):
                errors.append(f"story {rid} {depth} lacks qualifying documentary source; archaeology/ledger alone cannot promote it")
            if not reg.get("scene_ids"):
                errors.append(f"story {rid} {depth} missing scene packet")
        if depth == "TRANSCRIPT_DEPTH":
            story_sources = [source_map[sid] for sid in reg.get("source_ids", []) if sid in source_map]
            if not any(src.get("continuity") in {"consecutive", "partially_consecutive"} for src in story_sources):
                errors.append(f"story {rid} TRANSCRIPT_DEPTH lacks consecutive source")
            linked = [scene_map[sid] for sid in reg.get("scene_ids", []) if sid in scene_map]
            if not any(len(sc.get("ordered_beats", [])) >= 2 for sc in linked):
                errors.append(f"story {rid} TRANSCRIPT_DEPTH requires multiple ordered beats")
        if depth == "LITERARY_COMPLETE":
            story_sources = [source_map[sid] for sid in reg.get("source_ids", []) if sid in source_map]
            if not any(
                src.get("source_class") in QUALIFYING_LITERARY_SOURCES
                and src.get("continuity") == "literary"
                for src in story_sources
            ):
                errors.append(f"story {rid} LITERARY_COMPLETE lacks qualifying literary source")

        matches = public_by_id.get(rid, [])
        if len(matches) != 1:
            if not matches:
                errors.append(f"story {rid} registered article missing from public Story HTML")
        else:
            item = matches[0]
            if item.get("has_full_story") != bool(reg.get("full_story_allowed")):
                errors.append(f"story {rid} HTML full-story disagrees with registry")
            if item.get("depth") and item.get("depth").upper() != depth:
                errors.append(f"story {rid} HTML data-story-depth disagrees with registry")
            if item.get("mode") and item.get("mode") != mode:
                errors.append(f"story {rid} HTML data-story-mode disagrees with registry")

    if enforcement == "strict":
        for item in public_entries:
            if item.get("id") not in reg_map:
                errors.append(f"unregistered public Story entry {item.get('id')}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_story_archive(root)
    if errors:
        print("Story archive validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Story archive validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
