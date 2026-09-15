#!/usr/bin/env python3
"""Validate the public Philosophy projection of the Potatoism long-form.

The full long-form remains a deep source. Religion remains Potatoism's primary
public owner for religious/theological material; Philosophy exposes a concise
philosophical reader projection without becoming a second canon.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHILOSOPHY = ROOT / "philosophy" / "index.html"
RELIGION = ROOT / "religion" / "index.html"
DEEP_SOURCE = ROOT / "knowledge" / "philosophy" / "potatoism-reader-philosophy.md"
ENGINE = ROOT / "knowledge" / "philosophy" / "potatoism-philosophy-engine.md"
SOURCE_MAP = ROOT / "knowledge" / "philosophy" / "potatoism-philosophy-source-map.md"
CANONICAL = ROOT / "knowledge" / "philosophy" / "potato-philosophy.json"

STAGES = ("potato", "grow", "transform", "see", "relate", "learn", "give", "cultivate")
ONTOLOGY_TYPES = {"structures", "operators", "states", "resources", "relations", "outcomes"}
DOCTRINE_FIELDS = {"title", "root", "principle", "corruption", "test"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


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

    canonical_data: dict = {}
    if canonical:
        try:
            canonical_data = json.loads(canonical)
        except json.JSONDecodeError as exc:
            errors.append(f"Canonical philosophy JSON invalid: {exc}")

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
        errors.append(
            "Canonical ontology types must be exactly: " + ", ".join(sorted(ONTOLOGY_TYPES))
        )

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

    for stage in STAGES:
        marker = f'data-potatoism-stage="{stage}"'
        if marker not in philosophy:
            errors.append(f"Philosophy missing stage marker: {stage}")

    required_philosophy = (
        "So you want to be a potato",
        "Do you think you have what it takes?",
        "Be simple. Grow toward light.",
        "Religion remains the primary public owner",
        'href="../religion/"',
        'href="../knowledge/philosophy/potatoism-reader-philosophy.md"',
        'href="../knowledge/philosophy/potatoism-philosophy-engine.md"',
        "Orient each part toward the conditions required by its function",
        "biology does not prove theology",
        "Attend / reduce",
        "Orient / develop",
        "Metabolize",
        "Examine / distinguish",
        "Connect / differentiate",
        "Model / recurse",
        "Release / nourish",
        "Steward / enable",
        "The Filter generates interpretations. Potato Truth disciplines them.",
        "Relation is not identity.",
        "Return is not reset.",
        "Authority is not exemption.",
        "Does the participant become more capable without the system?",
    )
    for marker in required_philosophy:
        if marker.lower() not in philosophy.lower():
            errors.append(f"Public Philosophy missing projection marker: {marker}")

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
    )
    for marker in forbidden:
        if marker.lower() in philosophy.lower():
            errors.append(f"Philosophy projection must stay calm; forbidden marker found: {marker}")

    stage_count = philosophy.count('data-potatoism-stage="')
    if stage_count != len(STAGES):
        errors.append(f"Philosophy must expose exactly {len(STAGES)} stage markers; found {stage_count}")

    if errors:
        print("POTATOISM PHILOSOPHY PROJECTION VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("POTATOISM PHILOSOPHY PROJECTION VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
