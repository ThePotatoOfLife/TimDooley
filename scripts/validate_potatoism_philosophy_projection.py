#!/usr/bin/env python3
"""Validate the public Philosophy projection of the Potatoism long-form.

The public Philosophy surface is a six-turn Spiral Reader. Canonical doctrine remains
owned by the philosophy JSON and long-form source; Religion remains the primary public
owner for explicit religion/theology. The Spiral Reader owns reader order, not doctrine.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHILOSOPHY = ROOT / "philosophy" / "index.html"
RELIGION = ROOT / "religion" / "index.html"
DEEP_SOURCE = ROOT / "knowledge" / "philosophy" / "potatoism-reader-philosophy.md"
ENGINE = ROOT / "knowledge" / "philosophy" / "potatoism-philosophy-engine.md"
SOURCE_MAP = ROOT / "knowledge" / "philosophy" / "potatoism-philosophy-source-map.md"
READER_MAP = ROOT / "knowledge" / "philosophy" / "potatoism-spiral-reader-map.json"
CANONICAL = ROOT / "knowledge" / "philosophy" / "potato-philosophy.json"

TURNS = ("seed", "root", "door", "spiral", "fruit", "garden")
ONTOLOGY_TYPES = {"structures", "operators", "states", "resources", "relations", "outcomes"}
DOCTRINE_FIELDS = {"title", "root", "principle", "corruption", "test"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def load_json(path: Path, label: str, errors: list[str]) -> dict:
    raw = read(path)
    if not raw:
        errors.append(f"missing {label}")
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append(f"{label} JSON invalid: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{label} must be a JSON object")
        return {}
    return data


def main() -> int:
    errors: list[str] = []
    philosophy = read(PHILOSOPHY)
    religion = read(RELIGION)
    deep_source = read(DEEP_SOURCE)
    engine = read(ENGINE)
    source_map = read(SOURCE_MAP)
    canonical = read(CANONICAL)

    if not philosophy:
        errors.append("missing philosophy/index.html")
    if not religion:
        errors.append("missing religion/index.html")
    if not deep_source:
        errors.append("missing deep Potatoism long-form source")
    if not engine:
        errors.append("missing Potatoism philosophy engine")
    if not source_map:
        errors.append("missing Potatoism philosophy source map")
    if not canonical:
        errors.append("missing canonical Potato philosophy record")

    canonical_data = load_json(CANONICAL, "canonical philosophy", errors)
    reader_map = load_json(READER_MAP, "Potatoism Spiral Reader map", errors)

    required_canonical_keys = (
        "constitutional_laws",
        "core_doctrines",
        "ontology_types",
        "concept_grammar",
        "negative_definitions",
        "evaluation_sequence",
        "gardeners_paradox",
        "filter_truth_pairing",
    )
    for key in required_canonical_keys:
        if key not in canonical_data:
            errors.append(f"Canonical philosophy missing enrichment key: {key}")

    required_canonical_concepts = (
        "Relational Valence",
        "Generativity",
        "Reciprocal Transformation",
        "Functional Identity",
        "Potato Truth",
        "Curiosity Before Allegiance",
        "Garden Over Shadow Farm",
        "Authority Increases Burden",
        "Return Is Not Reset",
    )
    for marker in required_canonical_concepts:
        if marker.lower() not in canonical.lower():
            errors.append(f"Canonical philosophy missing enrichment concept: {marker}")

    doctrines = canonical_data.get("core_doctrines", {}) if canonical_data else {}
    if doctrines and len(doctrines) != 14:
        errors.append(f"Canonical philosophy must contain exactly 14 core doctrines; found {len(doctrines)}")
    for doctrine_id, doctrine in doctrines.items():
        if not isinstance(doctrine, dict):
            errors.append(f"Doctrine {doctrine_id} must be an object")
            continue
        missing = DOCTRINE_FIELDS - set(doctrine)
        if missing:
            errors.append(f"Doctrine {doctrine_id} missing fields: {', '.join(sorted(missing))}")

    ontology_types = canonical_data.get("ontology_types", {}) if canonical_data else {}
    if ontology_types and set(ontology_types) != ONTOLOGY_TYPES:
        errors.append("Canonical ontology types must be exactly: " + ", ".join(sorted(ONTOLOGY_TYPES)))

    required_engine = (
        "# Four constitutional laws",
        "Law of Relational Valence",
        "Law of Generativity",
        "Law of Reciprocal Transformation",
        "Law of Functional Identity",
        "# Fourteen doctrines of the current mature philosophy",
        "A language, not a pile of symbols",
        "The Filter generates interpretations. Potato Truth disciplines them.",
        "The Gardener's Paradox",
        "Relation is not identity.",
        "Suffering is not proof.",
        "Return is not reset.",
        "Authority is not exemption.",
        "The Filter is not evidence.",
        "Observe → distinguish → relate → test → transform → evaluate fruit → cultivate.",
        "Let each part orient toward the conditions appropriate to its function",
    )
    for marker in required_engine:
        if marker.lower() not in engine.lower():
            errors.append(f"Philosophy engine missing enrichment marker: {marker}")

    required_source_map = (
        "not retroactively attributed to Tim Dooley as a historically published numbered creed",
        "GREAT_BOOK_ATTRIBUTED_TIM_QUOTE",
        "CONVERSATION_RECOVERY",
        "PUBLIC_COMPILATION",
        "ARCHIVE_SYNTHESIS",
        "Relational Valence",
        "Gardener’s Paradox",
        "Curiosity Before Allegiance",
    )
    for marker in required_source_map:
        if marker.lower() not in source_map.lower():
            errors.append(f"Philosophy source map missing provenance marker: {marker}")

    map_turns = reader_map.get("turns", []) if reader_map else []
    map_turn_ids = [turn.get("id") for turn in map_turns if isinstance(turn, dict)]
    if tuple(map_turn_ids) != TURNS:
        errors.append(f"Spiral Reader map turns must be exactly {TURNS}; found {tuple(map_turn_ids)}")

    map_station_ids: list[str] = []
    for turn in map_turns:
        if not isinstance(turn, dict):
            errors.append("Spiral Reader turn must be an object")
            continue
        for station in turn.get("stations", []):
            if not isinstance(station, dict):
                errors.append(f"Spiral Reader station in {turn.get('id')} must be an object")
                continue
            for field in ("id", "title", "question", "sources", "provenance", "previous", "next", "priority"):
                if field not in station:
                    errors.append(f"Spiral Reader station {station.get('id', '<unknown>')} missing field: {field}")
            station_id = station.get("id")
            if station_id:
                map_station_ids.append(station_id)

    if len(map_station_ids) != 47:
        errors.append(f"Spiral Reader map must contain exactly 47 stations; found {len(map_station_ids)}")
    if len(set(map_station_ids)) != len(map_station_ids):
        errors.append("Spiral Reader map contains duplicate station ids")

    # Turn identity is structural rather than dependent on a particular visual heading layout.
    for turn in TURNS:
        marker = f'data-potatoism-turn="{turn}"'
        count = philosophy.count(marker)
        if count != 1:
            errors.append(f"Public Philosophy must contain turn marker {turn} exactly once; found {count}")

    turn_count = philosophy.count('data-potatoism-turn="')
    if turn_count != len(TURNS):
        errors.append(f"Public Philosophy must expose exactly {len(TURNS)} turn markers; found {turn_count}")

    page_station_ids = re.findall(r'data-potatoism-station="([^"]+)"', philosophy)
    if not 40 <= len(page_station_ids) <= 50:
        errors.append(f"Public Philosophy must expose 40–50 station markers; found {len(page_station_ids)}")
    if map_station_ids and page_station_ids != map_station_ids:
        missing = [sid for sid in map_station_ids if sid not in page_station_ids]
        extra = [sid for sid in page_station_ids if sid not in map_station_ids]
        if missing:
            errors.append("Public Philosophy missing mapped station ids: " + ", ".join(missing))
        if extra:
            errors.append("Public Philosophy has unmapped station ids: " + ", ".join(extra))
        if not missing and not extra:
            errors.append("Public Philosophy station order does not match Spiral Reader map order")

    required_philosophy = (
        "So you want to be a potato",
        "Do you think you have what it takes?",
        "How to read this spiral",
        "Be simple. Grow toward light.",
        "Religion remains the primary public owner",
        'href="../religion/"',
        'href="../knowledge/philosophy/potatoism-reader-philosophy.md"',
        'href="../knowledge/philosophy/potatoism-philosophy-engine.md"',
        "biology does not prove theology",
        "We found a question. Who else has been here?",
        "Relation is not identity.",
        "Suffering is not proof.",
        "The Filter is not evidence.",
        "Return is not reset.",
        "Authority is not exemption.",
        "Does the participant become more capable without the system?",
        "The Filter generates interpretations. Potato Truth disciplines them.",
    )
    for marker in required_philosophy:
        if marker.lower() not in philosophy.lower():
            errors.append(f"Public Philosophy missing Spiral Reader marker: {marker}")

    required_religion = (
        'data-reader-surface="religion"',
        'data-placement-role="theological-center"',
        "The Potatoist center",
        "What is Potatoism?",
        "Philosophy develops the method, ethics and relational system",
        "Religion remains the owner of explicit Father/Son/Spirit theology",
    )
    for marker in required_religion:
        if marker.lower() not in religion.lower():
            errors.append(f"Religion lost ownership bridge marker: {marker}")

    deep_source_markers = (
        "# So You Want to Be a Potato",
        "canonical long-form reader philosophy / source text for the Philosophy surface",
        "Be simple.",
        "Grow toward light.",
    )
    for marker in deep_source_markers:
        if marker.lower() not in deep_source.lower():
            errors.append(f"Deep source missing expected source marker: {marker}")

    forbidden = (
        'class="stepper"',
        'class="progress-meter"',
        'data-next-stage',
        'id="next-stage"',
        "scrollIntoView(",
        "autofocus",
        "data-complete",
        "course-progress",
        "lesson-lock",
        "next-lesson",
    )
    for marker in forbidden:
        if marker.lower() in philosophy.lower():
            errors.append(f"Philosophy reader must stay calm and non-gamified; forbidden marker found: {marker}")

    # Retired public architecture: no eight-stage markers should survive the overhaul.
    if 'data-potatoism-stage="' in philosophy:
        errors.append("Public Philosophy still contains retired eight-stage markers")

    if errors:
        print("POTATOISM PHILOSOPHY PROJECTION VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("POTATOISM PHILOSOPHY PROJECTION VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
