#!/usr/bin/env python3
"""Validate the shared project formal grammar and its current integrations."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR = ROOT / "data" / "project-formal-grammar.json"
CONCEPTS = ROOT / "data" / "house" / "concept-topology.json"
INTERFACES = ROOT / "data" / "house" / "interfaces.json"
AXIS = ROOT / "data" / "axis-depths.json"
BODY = ROOT / "data" / "house" / "body-relational-overlay.json"
SCIENCE = ROOT / "knowledge" / "science" / "science-model-registry.json"

EXPECTED_REF = "data/project-formal-grammar.json"
VALID_C = {f"C{i}" for i in range(6)}
VALID_E = {f"E{i}" for i in range(7)}
REQUIRED_TEMPLATES = {"Door","Axis","Spiral","House","Room","Eye","Root","Tree","Seed","Ladder","Fruit","Flow"}

def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data

def main() -> int:
    errors: list[str] = []
    paths = (GRAMMAR, CONCEPTS, INTERFACES, AXIS, BODY, SCIENCE)
    for path in paths:
        if not path.exists():
            errors.append(f"missing required formal-grammar integration file: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("FORMAL GRAMMAR ERROR:", e)
        return 1

    try:
        grammar = load(GRAMMAR)
        concepts = load(CONCEPTS)
        interfaces = load(INTERFACES)
        axis = load(AXIS)
        body = load(BODY)
        science = load(SCIENCE)
    except Exception as exc:
        print("FORMAL GRAMMAR VALIDATION FAILED:", exc)
        return 1

    typed = grammar.get("typed_objects", {})
    missing_templates = sorted(REQUIRED_TEMPLATES - set(typed))
    if missing_templates:
        errors.append(f"grammar missing typed object templates: {missing_templates}")

    dimension_types = grammar.get("dimension_types", {})
    expected_dims = {"P","S","C","E","H","Q","M","F"}
    if set(dimension_types) != expected_dims:
        errors.append(f"dimension types drifted: expected {sorted(expected_dims)}, got {sorted(dimension_types)}")

    corr = grammar.get("correspondence_maturity", {})
    epistemic = grammar.get("epistemic_scale", {})
    if set(corr) != VALID_C:
        errors.append("correspondence maturity scale must be exactly C0-C5")
    if set(epistemic) != VALID_E:
        errors.append("epistemic scale must be exactly E0-E6")

    for label, data in (
        ("concept topology", concepts),
        ("House interfaces", interfaces),
        ("Axis depths", axis),
        ("body overlay", body),
    ):
        if data.get("formal_grammar_ref") != EXPECTED_REF:
            errors.append(f"{label} does not point to {EXPECTED_REF}")

    if science.get("shared_formal_grammar") != EXPECTED_REF:
        errors.append("science model registry does not point to the shared formal grammar")

    for concept in concepts.get("concepts", []):
        ft = concept.get("formal_type")
        if not ft:
            continue
        template = ft.get("template")
        if template not in typed:
            errors.append(f"concept {concept.get('id')} uses unknown formal template {template!r}")
            continue
        expected_schema = typed[template].get("schema")
        if expected_schema and ft.get("schema") != expected_schema:
            errors.append(f"concept {concept.get('id')} schema drifted from grammar template {template}")

    contract_ext = interfaces.get("interface_contract_extension")
    if not isinstance(contract_ext, dict):
        errors.append("House interfaces missing interface_contract_extension")
    for interface in interfaces.get("interfaces", []):
        fc = interface.get("formal_contract")
        if not fc:
            continue
        if not fc.get("morphism_type"):
            errors.append(f"interface {interface.get('id')} formal_contract lacks morphism_type")
        if not isinstance(fc.get("preserved_invariants"), list) or not fc["preserved_invariants"]:
            errors.append(f"interface {interface.get('id')} formal_contract lacks preserved invariants")
        if not isinstance(fc.get("lost_or_not_preserved"), list):
            errors.append(f"interface {interface.get('id')} formal_contract lacks loss/mismatch list")

    dt = axis.get("dimension_type", {})
    if dt.get("code") != "P":
        errors.append("Axis global dimension type must be P")
    levels = axis.get("levels", [])
    if not levels:
        errors.append("Axis has no levels")
    for level in levels:
        if level.get("dimension_type") != "P":
            errors.append(f"Axis D{level.get('dimension')} is not typed P")
        expected = f"D^(P)={level.get('dimension')}"
        if level.get("dimension_notation") != expected:
            errors.append(f"Axis D{level.get('dimension')} notation must be {expected}")
    anchor = axis.get("anchor")
    if isinstance(anchor, dict) and anchor.get("dimension_type") != "P":
        errors.append("Axis anchor is not typed P")

    for obj in body.get("objects", []):
        fc = obj.get("formal_correspondence")
        if not fc:
            continue
        c = fc.get("correspondence_maturity")
        e = fc.get("epistemic_status")
        if c not in VALID_C:
            errors.append(f"body object {obj.get('id')} has invalid correspondence maturity {c!r}")
        if e not in VALID_E:
            errors.append(f"body object {obj.get('id')} has invalid epistemic status {e!r}")
        if not isinstance(fc.get("preserves"), list) or not fc["preserves"]:
            errors.append(f"body object {obj.get('id')} correspondence lacks preserved structure")
        if not isinstance(fc.get("does_not_preserve"), list) or not fc["does_not_preserve"]:
            errors.append(f"body object {obj.get('id')} correspondence lacks mismatch boundary")

    model = next((x for x in science.get("models", []) if x.get("id") == "eleven-dimensional-projection"), None)
    if not model:
        errors.append("science model registry missing eleven-dimensional-projection model")
    else:
        if model.get("formal_grammar") != EXPECTED_REF:
            errors.append("11D model does not link the shared formal grammar")
        if not model.get("primary_thesis") or not model.get("structured_thesis"):
            errors.append("11D model missing primary/structured thesis links")

    if errors:
        print("PROJECT FORMAL GRAMMAR VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print(
        "PROJECT FORMAL GRAMMAR VALIDATION PASSED "
        f"({len(typed)} templates, {len(levels)} Axis levels, "
        f"{sum(1 for x in concepts.get('concepts', []) if x.get('formal_type'))} typed concepts)"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
