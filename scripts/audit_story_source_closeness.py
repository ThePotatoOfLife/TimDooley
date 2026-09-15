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
            }
            self.entries.append(self.current)
            return
        if tag == "span" and self.current is not None:
            classes = set((data.get("class") or "").split())
            if "source-paths" in classes:
                self.capture_source = True
                self.source_chunks = []

    def handle_data(self, data):
        if self.capture_source:
            self.source_chunks.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.capture_source:
            hint = " ".join("".join(self.source_chunks).split())
            if hint and self.current is not None:
                self.current["source_hints"].append(hint)
            self.capture_source = False
            self.source_chunks = []
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
    entries: list[dict] = []
    for path in sorted((root / "story-content").glob("*.html")):
        parser = StoryParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        for item in parser.entries:
            item["path"] = path.relative_to(root).as_posix()
            entries.append(item)
    return entries


def infer_source_hints(hints: list[str]) -> tuple[list[str], str | None, str | None]:
    text = " ".join(hints).lower()
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
        )
    ):
        classes.append("public_post_sequence")
    classes = sorted(set(classes))
    if not classes:
        return [], None, None
    candidates = [SOURCE_DEFAULTS[source_class] for source_class in classes]
    candidates.sort(key=lambda item: EVENT_RANK[item[0]])
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

    records: list[dict] = []
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
            "hinted_source_classes": [],
            "event_distance": None,
            "editorial_distance": None,
            "continuity": None,
            "source_near_status": "none",
            "closer_source_expected": None,
            "lost_texture": [],
            "next_excavation": None,
        }

        if not reg and record["source_hints"]:
            hinted_classes, event_distance, continuity = infer_source_hints(record["source_hints"])
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

    direct_distances = {"0_direct_contemporaneous", "1_contemporaneous_compilation"}
    summary = {
        "total_public_entries": len(records),
        "registered": sum(1 for x in records if x["story_id"] in registry),
        "source_hinted": sum(1 for x in records if x["mapping_status"] == "hinted"),
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
