from __future__ import annotations

import argparse
import json
import tomllib
from html.parser import HTMLParser
from pathlib import Path

SOURCE_DEFAULTS = {
    "consecutive_transcript": ("0_direct_contemporaneous", "full_session_or_thread"),
    "public_chat_transcript": ("0_direct_contemporaneous", "contiguous_exchange"),
    "public_thread": ("0_direct_contemporaneous", "full_session_or_thread"),
    "public_post_sequence": ("1_contemporaneous_compilation", "partial_exchange"),
    "creative_artifact": ("0_direct_contemporaneous", "artifact_plus_context"),
    "external_documentary_source": ("1_contemporaneous_compilation", "partial_exchange"),
    "single_recovered_turn": ("3_project_reconstruction", "isolated_phrase"),
    "isolated_quote_recovery": ("3_project_reconstruction", "isolated_phrase"),
    "statement_ledger": ("3_project_reconstruction", "phrase_cluster"),
    "archaeology_summary": ("4_archive_synthesis", "phrase_cluster"),
    "later_autobiographical_retelling": ("2_later_first_person_retelling", "phrase_cluster"),
    "great_book_literary_text": ("0_direct_contemporaneous", "complete_literary_scene"),
    "conversation_recovery": ("3_project_reconstruction", "phrase_cluster"),
}

EVENT_RANK = {
    "0_direct_contemporaneous": 0,
    "1_contemporaneous_compilation": 1,
    "2_later_first_person_retelling": 2,
    "3_project_reconstruction": 3,
    "4_archive_synthesis": 4,
}


class StoryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.entries: list[dict] = []
        self.current: dict | None = None
        self.capture_source = False
        self.source_chunks: list[str] = []
        self.capture_note = False
        self.note_chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "article":
            classes = set((data.get("class") or "").split())
            if "story-entry" not in classes:
                return
            self.current = {
                "id": data.get("id"),
                "story_type": data.get("data-story-type"),
                "depth": data.get("data-story-depth"),
                "mode": data.get("data-story-mode"),
                "source_hints": [],
                "source_note_text": "",
            }
            self.entries.append(self.current)
            return
        if tag == "details" and self.current is not None:
            classes = set((data.get("class") or "").split())
            if "source-note" in classes:
                self.capture_note = True
                self.note_chunks = []
                return
        if tag == "span" and self.current is not None:
            classes = set((data.get("class") or "").split())
            if "source-paths" in classes:
                self.capture_source = True
                self.source_chunks = []

    def handle_data(self, data):
        if self.capture_source:
            self.source_chunks.append(data)
        if self.capture_note:
            self.note_chunks.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.capture_source:
            hint = " ".join("".join(self.source_chunks).split())
            if hint and self.current is not None:
                self.current["source_hints"].append(hint)
            self.capture_source = False
            self.source_chunks = []
        elif tag == "details" and self.capture_note:
            note = " ".join("".join(self.note_chunks).split())
            if note and self.current is not None:
                self.current["source_note_text"] = note
            self.capture_note = False
            self.note_chunks = []
        elif tag == "article":
            self.current = None


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_overrides(root: Path) -> dict:
    path = root / "docs" / "story-source-closeness" / "overrides.toml"
    if not path.exists():
        return {"story_overrides": [], "excavation_targets": []}
    with path.open("rb") as fh:
        return tomllib.load(fh)


def scan_public(root: Path) -> list[dict]:
    entries = []
    for path in sorted((root / "story-content").glob("*.html")):
        parser = StoryParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        for item in parser.entries:
            item["path"] = path.relative_to(root).as_posix()
            entries.append(item)
    return entries


def infer_source_hints(
    hints: list[str], note_text: str = ""
) -> tuple[list[str], str | None, str | None]:
    text = " ".join([*hints, note_text]).lower()
    classes: list[str] = []

    if "suno" in text or "creative catalogue" in text or "creative archive" in text:
        classes.append("creative_artifact")

    if any(
        token in text
        for token in (
            "public-post",
            "public post",
            "twitter",
            "rational_potato",
            "x occurrence",
            "public indexed",
            "public compilation",
            "dated public",
            "buy me a coffee",
        )
    ):
        classes.append("public_post_sequence")

    if "great-book" in text or "great book" in text:
        if any(
            token in text
            for token in (
                "retrospective",
                "later retelling",
                "autobiographical",
                "project autobiography",
                "project-autobiographical",
            )
        ):
            classes.append("later_autobiographical_retelling")
        elif any(token in text for token in ("literary", "direct chapter", "creative scene", "creative/social layer")):
            classes.append("great_book_literary_text")

    if any(
        token in text
        for token in (
            "conversation recovery",
            "conversation-derived",
            "prior-conversation recovery",
            "conversation archaeology",
        )
    ):
        classes.append("conversation_recovery")

    classes = sorted(set(classes))
    if not classes:
        return [], None, None
    candidates = [SOURCE_DEFAULTS[source_class] for source_class in classes if source_class in SOURCE_DEFAULTS]
    candidates.sort(key=lambda item: EVENT_RANK[item[0]])
    if not candidates:
        return classes, None, None
    event_distance, continuity = candidates[0]
    return classes, event_distance, continuity


def choose_closest(sources: list[dict]) -> tuple[str | None, str | None]:
    choices: list[tuple[int, str, str]] = []
    for src in sources:
        default = SOURCE_DEFAULTS.get(src.get("source_class"))
        if not default:
            continue
        event_distance, continuity = default
        choices.append((EVENT_RANK[event_distance], event_distance, continuity))
    if not choices:
        return None, None
    choices.sort(key=lambda x: x[0])
    return choices[0][1], choices[0][2]


def excavation_priority(record: dict) -> tuple[int, str]:
    if record["mapping_status"] == "unmapped":
        return 100, "find_any_source_trail"
    if record["mapping_status"] == "hinted" and not record["hinted_source_classes"]:
        return 90, "classify_existing_source_hint"
    if record["mapping_status"] == "hinted":
        distance = record.get("event_distance")
        if distance == "4_archive_synthesis":
            return 85, "recover_underlying_source"
        if distance == "3_project_reconstruction":
            return 80, "recover_underlying_conversation_or_artifact"
        if distance == "2_later_first_person_retelling":
            return 70, "find_contemporaneous_corroboration"
        if distance == "1_contemporaneous_compilation":
            return 35, "register_existing_near_primary_source"
        if distance == "0_direct_contemporaneous":
            return 25, "register_existing_direct_source"
        return 60, "inspect_source_hint"
    if record["mapping_status"] in {"mapped", "partially_mapped"}:
        if record.get("closer_source_expected"):
            return 65, "pursue_registered_recovery_target"
        return 10, "no_immediate_excavation"
    return 50, "review_manually"


def build_excavation_queue(records: list[dict]) -> list[dict]:
    queue = []
    for record in records:
        priority, action = excavation_priority(record)
        queue.append(
            {
                "story_id": record["story_id"],
                "path": record["path"],
                "priority": priority,
                "mapping_status": record["mapping_status"],
                "event_distance": record["event_distance"],
                "hinted_source_classes": record["hinted_source_classes"],
                "recommended_next_action": action,
                "source_hints": record["source_hints"],
                "next_excavation": record["next_excavation"],
            }
        )
    queue.sort(key=lambda item: (-item["priority"], item["story_id"] or ""))
    return queue


def build_audit(root: Path) -> dict:
    registry_data = load_json(root / "knowledge" / "story" / "story-registry.json")
    source_data = load_json(root / "knowledge" / "story" / "source-records.json")
    overrides_data = load_overrides(root)
    registry = {x["id"]: x for x in registry_data.get("stories", []) if x.get("id")}
    sources = {x["id"]: x for x in source_data.get("sources", []) if x.get("id")}
    overrides = {
        x["story_id"]: x
        for x in overrides_data.get("story_overrides", [])
        if x.get("story_id")
    }

    records = []
    for public in scan_public(root):
        story_id = public.get("id")
        reg = registry.get(story_id)
        override = overrides.get(story_id, {})
        record = {
            "story_id": story_id,
            "path": public.get("path"),
            "mapping_status": "unmapped",
            "closest_source_ids": [],
            "source_classes": [],
            "source_hints": list(public.get("source_hints", [])),
            "source_note_text": public.get("source_note_text", ""),
            "hinted_source_classes": [],
            "event_distance": None,
            "editorial_distance": None,
            "continuity": None,
            "source_near_status": "none",
            "closer_source_expected": None,
            "lost_texture": [],
            "next_excavation": None,
        }

        has_provenance_hint = bool(record["source_hints"] or record["source_note_text"])
        if not reg and has_provenance_hint:
            hinted_classes, event_distance, continuity = infer_source_hints(
                record["source_hints"], record["source_note_text"]
            )
            record.update(
                {
                    "mapping_status": "hinted",
                    "hinted_source_classes": hinted_classes,
                    "event_distance": event_distance,
                    "editorial_distance": "4_public_story_edit",
                    "continuity": continuity,
                }
            )

        if reg:
            source_ids = list(reg.get("source_ids", []))
            linked = [sources[sid] for sid in source_ids if sid in sources]
            event_distance, continuity = choose_closest(linked)
            record.update(
                {
                    "mapping_status": "mapped" if len(linked) == len(source_ids) else "partially_mapped",
                    "closest_source_ids": source_ids,
                    "source_classes": sorted(
                        {x.get("source_class") for x in linked if x.get("source_class")}
                    ),
                    "event_distance": event_distance,
                    "editorial_distance": "4_public_story_edit",
                    "continuity": continuity,
                    "closer_source_expected": bool(reg.get("recovery_targets")),
                    "next_excavation": (reg.get("recovery_targets") or [None])[0],
                }
            )

        if override:
            for key in (
                "closest_source_ids",
                "event_distance",
                "editorial_distance",
                "continuity",
                "source_near_status",
                "closer_source_expected",
                "lost_texture",
                "next_excavation",
            ):
                if key in override:
                    record[key] = override[key]
            record["mapping_status"] = "mapped"

        records.append(record)

    hinted_source_class_counts: dict[str, int] = {}
    for record in records:
        if record["mapping_status"] != "hinted":
            continue
        for source_class in record["hinted_source_classes"]:
            hinted_source_class_counts[source_class] = hinted_source_class_counts.get(source_class, 0) + 1

    direct_distances = {"0_direct_contemporaneous", "1_contemporaneous_compilation"}
    summary = {
        "total_public_entries": len(records),
        "registered": sum(1 for x in records if x["story_id"] in registry),
        "source_hinted": sum(1 for x in records if x["mapping_status"] == "hinted"),
        "hinted_but_unclassified": sum(
            1
            for x in records
            if x["mapping_status"] == "hinted" and not x["hinted_source_classes"]
        ),
        "hinted_source_class_counts": dict(sorted(hinted_source_class_counts.items())),
        "unmapped": sum(1 for x in records if x["mapping_status"] == "unmapped"),
        "direct_or_near_direct": sum(
            1
            for x in records
            if x["mapping_status"] in {"mapped", "partially_mapped"}
            and x["event_distance"] in direct_distances
        ),
        "hinted_direct_or_near_direct": sum(
            1
            for x in records
            if x["mapping_status"] == "hinted" and x["event_distance"] in direct_distances
        ),
        "source_near_present": sum(
            1 for x in records if x["source_near_status"] in {"draft", "complete"}
        ),
        "closer_source_expected": sum(
            1 for x in records if x["closer_source_expected"] is True
        ),
    }
    return {
        "schema_version": 1,
        "summary": summary,
        "records": records,
        "excavation_queue": build_excavation_queue(records),
        "excavation_targets": overrides_data.get("excavation_targets", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="Optional JSON output path")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    audit = build_audit(root)
    text = json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        output = args.write if args.write.is_absolute() else root / args.write
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(json.dumps(audit["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
