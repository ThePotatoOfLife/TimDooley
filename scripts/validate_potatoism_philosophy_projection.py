#!/usr/bin/env python3
"""Validate the public Philosophy projection of the Potatoism long-form.

The full long-form remains the deep source. Religion remains Potatoism's
primary public owner for religious/theological material; Philosophy exposes a
concise philosophical reader projection without becoming a second canon.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHILOSOPHY = ROOT / "philosophy" / "index.html"
RELIGION = ROOT / "religion" / "index.html"
DEEP_SOURCE = ROOT / "knowledge" / "philosophy" / "potatoism-reader-philosophy.md"
CANONICAL = ROOT / "knowledge" / "philosophy" / "potato-philosophy.json"

STAGES = ("potato", "grow", "transform", "see", "relate", "learn", "give", "cultivate")


def main() -> int:
    errors: list[str] = []
    philosophy = PHILOSOPHY.read_text(encoding="utf-8", errors="replace") if PHILOSOPHY.exists() else ""
    religion = RELIGION.read_text(encoding="utf-8", errors="replace") if RELIGION.exists() else ""
    deep_source = DEEP_SOURCE.read_text(encoding="utf-8", errors="replace") if DEEP_SOURCE.exists() else ""
    canonical = CANONICAL.read_text(encoding="utf-8", errors="replace") if CANONICAL.exists() else ""

    if not philosophy:
        errors.append("missing philosophy/index.html")
    if not religion:
        errors.append("missing religion/index.html")
    if not deep_source:
        errors.append("missing deep Potatoism long-form source")
    if not canonical:
        errors.append("missing canonical Potato philosophy record")

    required_canonical_keys = (
        '"constitutional_laws"',
        '"core_doctrines"',
        '"ontology_types"',
        '"concept_grammar"',
        '"negative_definitions"',
        '"evaluation_sequence"',
    )
    for marker in required_canonical_keys:
        if marker not in canonical:
            errors.append(f"Canonical philosophy missing enrichment marker: {marker}")

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
        "Orient each part toward the conditions required by its function",
        "biology does not prove theology",
    )
    for marker in required_philosophy:
        if marker.lower() not in philosophy.lower():
            errors.append(f"Philosophy missing projection contract marker: {marker}")

    required_religion = (
        'data-reader-surface="religion"',
        'data-placement-role="theological-center"',
        "The Potatoist center",
        "What is Potatoism?",
    )
    for marker in required_religion:
        if marker.lower() not in religion.lower():
            errors.append(f"Religion lost primary-owner marker: {marker}")

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
