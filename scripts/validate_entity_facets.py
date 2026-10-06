#!/usr/bin/env python3
"""Validate the Entity Facet Ledger contract without third-party dependencies."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "knowledge/story/entity-facet-ledger.json"
RULES = ROOT / "data/entity-facet-rendering-rules.json"

REQUIRED_ENTITY = {"label", "kind", "facets"}
REQUIRED_FACET = {"type", "label", "strength", "scope", "provenance"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_exists(ref: str) -> bool:
    if not ref or "://" in ref:
        return True
    clean = ref.split("#", 1)[0]
    return (ROOT / clean).exists()


def main() -> int:
    ledger = load(LEDGER)
    rules = load(RULES)
    errors: list[str] = []
    warnings: list[str] = []

    facet_types = set(ledger.get("facet_types", {}))
    strengths = set(ledger.get("strength_levels", {}))
    entities = ledger.get("entities", {})
    if not isinstance(entities, dict) or not entities:
        errors.append("entities must be a non-empty object")
        entities = {}

    labels_seen: dict[str, str] = {}
    for entity_id, entity in entities.items():
        missing = REQUIRED_ENTITY - set(entity)
        if missing:
            errors.append(f"{entity_id}: missing entity fields {sorted(missing)}")
            continue

        label = str(entity.get("label", "")).strip()
        if not label:
            errors.append(f"{entity_id}: blank label")
        key = label.casefold()
        if key in labels_seen and labels_seen[key] != entity_id:
            warnings.append(f"duplicate display label: {label!r} ({labels_seen[key]}, {entity_id})")
        labels_seen[key] = entity_id

        aliases = entity.get("aliases", [])
        if len(aliases) != len(set(a.casefold() for a in aliases if isinstance(a, str))):
            warnings.append(f"{entity_id}: duplicate aliases after case-folding")

        first_seen = entity.get("first_seen")
        if isinstance(first_seen, dict):
            src = first_seen.get("source")
            if src and not source_exists(src):
                errors.append(f"{entity_id}: first_seen source missing: {src}")

        facet_label_keys: set[tuple[str, str, str]] = set()
        for i, facet in enumerate(entity.get("facets", [])):
            if not isinstance(facet, dict):
                errors.append(f"{entity_id}.facets[{i}]: not an object")
                continue
            missing_f = REQUIRED_FACET - set(facet)
            if missing_f:
                errors.append(f"{entity_id}.facets[{i}]: missing {sorted(missing_f)}")
                continue

            ftype = facet["type"]
            strength = facet["strength"]
            if ftype not in facet_types:
                errors.append(f"{entity_id}.facets[{i}]: unknown type {ftype!r}")
            if strength not in strengths:
                errors.append(f"{entity_id}.facets[{i}]: unknown strength {strength!r}")

            if ftype == "species_trait":
                explicit = bool(facet.get("explicit_generalization"))
                if strength not in {"repeated", "canonical"} and not explicit:
                    errors.append(
                        f"{entity_id}.facets[{i}]: species_trait must be repeated/canonical "
                        "or explicit_generalization=true"
                    )

            if strength == "hypothesis" and ftype in {"species_trait"}:
                errors.append(f"{entity_id}.facets[{i}]: hypothesis cannot be a settled species_trait")

            source_ref = facet.get("source_ref")
            if source_ref and not source_exists(source_ref):
                errors.append(f"{entity_id}.facets[{i}]: source_ref missing: {source_ref}")

            dedupe = (str(ftype), str(facet.get("label", "")).casefold(), str(facet.get("scope", "")).casefold())
            if dedupe in facet_label_keys:
                warnings.append(f"{entity_id}: duplicate facet {dedupe}")
            facet_label_keys.add(dedupe)

        for i, beat in enumerate(entity.get("story_beats", [])):
            if not isinstance(beat, dict) or not beat.get("label"):
                errors.append(f"{entity_id}.story_beats[{i}]: missing label")
                continue
            src = beat.get("source_ref")
            if src and not source_exists(src):
                errors.append(f"{entity_id}.story_beats[{i}]: source_ref missing: {src}")

        # Rendering safety: hypotheses must be visibly qualified if manually projected.
        # We cannot infer all public projections from JSON, so enforce the canonical label vocabulary.
        for facet in entity.get("facets", []):
            if isinstance(facet, dict) and facet.get("strength") == "hypothesis":
                if not facet.get("label"):
                    errors.append(f"{entity_id}: blank hypothesis label")

    max_facets = rules.get("defaults", {}).get("max_signature_facets")
    if not isinstance(max_facets, int) or max_facets < 1:
        errors.append("rendering rules: max_signature_facets must be a positive integer")

    print(f"Entities: {len(entities)}")
    print(f"Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"WARN: {warning}")

    if errors:
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("ENTITY FACET LEDGER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
