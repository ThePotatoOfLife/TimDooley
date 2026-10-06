#!/usr/bin/env python3
"""Validate the generated World Map coverage ledger and its derivation rules."""
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_world_map_coverage.py"
OUT = ROOT / "data" / "world-map-coverage-ledger.json"
FORBIDDEN_KEYS = {
    "score", "power_score", "resilience_score", "importance_score",
    "completion_score", "completion_percentage", "geopolitical_score",
}
VALID_STATES = {"represented", "partial", "missing", "unknown", "pending-source", "not-applicable"}


def load_builder():
    if not BUILDER.is_file():
        raise AssertionError("missing scripts/build_world_map_coverage.py")
    spec = importlib.util.spec_from_file_location("build_world_map_coverage", BUILDER)
    assert spec and spec.loader, "could not load coverage builder"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).lower()
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def main() -> int:
    errors: list[str] = []
    try:
        builder = load_builder()
        payload = builder.build_coverage_ledger()
    except Exception as exc:
        print("World Map coverage validation FAILED:")
        print(f" - {exc}")
        return 1

    policy = payload.get("policy", {})
    if policy.get("country_count") != 195:
        errors.append(f"coverage policy must preserve 195 canonical countries, got {policy.get('country_count')!r}")
    if policy.get("missing_is_zero") is not False:
        errors.append("coverage policy must state missing_is_zero=false")
    if policy.get("ranking_is_operational_not_geopolitical") is not True:
        errors.append("coverage policy must distinguish operational enrichment priority from geopolitical ranking")

    entities = payload.get("entities", {})
    canonical = [row for row in entities.values() if row.get("canonical_country") is True]
    if len(canonical) != 195:
        errors.append(f"coverage ledger must contain 195 canonical-country rows, got {len(canonical)}")
    if "GRL" not in entities or entities.get("GRL", {}).get("canonical_country") is not False:
        errors.append("Greenland must be represented as a registered non-country entity")

    forbidden_found = sorted(FORBIDDEN_KEYS.intersection(set(walk_keys(payload))))
    if forbidden_found:
        errors.append(f"coverage ledger contains forbidden aggregate score keys: {', '.join(forbidden_found)}")

    fixture = {
        "coverage": {"relationships": 0, "sources": 0},
        "observations": {
            "population": {
                "value": 123,
                "unit": "persons",
                "period": "2026",
                "source": "Fixture Source",
                "source_url": "https://example.invalid/source",
            }
        },
        "relationships": [{"type": "depends-on", "target": "fixture-system"}],
    }
    try:
        derived = builder.derive_record_coverage(fixture)
        represented = derived.get("relationships", {}).get("represented")
        if represented != 1:
            errors.append(f"actual relationship content must outrank stale stored counters; expected 1 got {represented!r}")
        source_records = derived.get("provenance", {}).get("source_records", 0)
        if not isinstance(source_records, int) or source_records < 1:
            errors.append("coverage derivation must count actual source/provenance records")
    except Exception as exc:
        errors.append(f"derive_record_coverage fixture failed: {exc}")

    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            one = tmpdir / "one.json"
            two = tmpdir / "two.json"
            one.write_text(json.dumps({"identity": {"iso3": "ZZZ"}}), encoding="utf-8")
            two.write_text(json.dumps({"identity": {"iso3": "ZZZ"}}), encoding="utf-8")
            audit = builder.audit_country_owners(
                [{"iso3": "ZZZ", "id": "one"}],
                [one, two],
            )
            duplicates = audit.get("duplicate_iso3", audit.get("duplicates", []))
            serialized = json.dumps(duplicates)
            if "ZZZ" not in serialized:
                errors.append("duplicate ISO3 audit fixture did not detect duplicate owner ZZZ")
    except Exception as exc:
        errors.append(f"duplicate owner fixture failed: {exc}")

    state_values: set[str] = set()
    for row in entities.values():
        for domain_state in (row.get("domains") or {}).values():
            if isinstance(domain_state, str):
                state_values.add(domain_state)
    invalid_states = sorted(state_values - VALID_STATES)
    if invalid_states:
        errors.append(f"coverage ledger uses unsupported state values: {invalid_states}")

    try:
        second = builder.build_coverage_ledger()
        if json.dumps(payload, sort_keys=True) != json.dumps(second, sort_keys=True):
            errors.append("coverage builder must be deterministic for unchanged repository state")
    except Exception as exc:
        errors.append(f"determinism check failed: {exc}")

    if OUT.is_file():
        try:
            saved = json.loads(OUT.read_text(encoding="utf-8"))
            normalized_saved = dict(saved); normalized_payload = dict(payload)
            normalized_saved.pop("generated_at", None); normalized_payload.pop("generated_at", None)
            if normalized_saved != normalized_payload:
                errors.append("saved coverage ledger does not match current generated derivation")
        except Exception as exc:
            errors.append(f"could not validate saved coverage ledger: {exc}")

    if errors:
        print("World Map coverage validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"World Map coverage ledger validation passed: {len(canonical)} countries · {len(entities) - len(canonical)} registered non-country entities.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
