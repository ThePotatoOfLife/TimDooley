#!/usr/bin/env python3
"""Validate evidence-backed World Map system-intelligence and gateway contracts."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build_world_map_runtime.py"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
REGISTRY = ROOT / "data" / "world-map-layer-registry.json"
CARD = ROOT / "world-map" / "3d-country-card.js"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
GATEWAY_MODULE = ROOT / "world-map" / "3d-gateways.js"

REQUIRED_GATEWAYS = {
    "malacca-strait",
    "hormuz-strait",
    "suez-sumed",
    "bab-el-mandeb",
    "danish-straits",
    "turkish-straits",
    "panama-canal",
    "cape-good-hope-route",
}
REQUIRED_CONTEXTUAL_ENTRIES = {
    "derived.capability",
    "derived.dependency",
    "derived.resilience",
    "derived.builds",
    "gateway.context",
}


def load_json(path: Path):
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def canonical_codes() -> set[str]:
    data = load_json(ROOT / "data" / "countries" / "index.json")
    rows = data.get("countries", []) if isinstance(data, dict) else []
    codes = {str(row.get("iso3") or "").upper() for row in rows}
    codes.discard("")
    assert len(codes) == 195, f"expected 195 canonical countries, got {len(codes)}"
    return codes


def load_generator():
    assert GENERATOR.is_file(), "missing runtime generator"
    spec = importlib.util.spec_from_file_location("build_world_map_runtime", GENERATOR)
    assert spec and spec.loader, "could not load runtime generator"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_gateways(codes: set[str]) -> None:
    data = load_json(GATEWAYS)
    gateways = data.get("gateways") or {}
    assert REQUIRED_GATEWAYS.issubset(gateways), f"missing gateways: {sorted(REQUIRED_GATEWAYS - set(gateways))}"
    for gateway_id, gateway in gateways.items():
        assert gateway.get("epistemic_type") == "observed", f"{gateway_id}: gateway must be observed"
        assert gateway.get("type") in {"maritime-chokepoint", "canal", "strategic-maritime-route"}, f"{gateway_id}: invalid type"
        coords = gateway.get("coordinates") or []
        assert isinstance(coords, list) and len(coords) == 2, f"{gateway_id}: coordinates must be [lon, lat]"
        lon, lat = coords
        assert isinstance(lon, (int, float)) and -180 <= lon <= 180, f"{gateway_id}: invalid longitude"
        assert isinstance(lat, (int, float)) and -90 <= lat <= 90, f"{gateway_id}: invalid latitude"
        assert gateway.get("coordinate_precision") == "approximate-center", f"{gateway_id}: precision boundary required"
        assert "navigation" in str(gateway.get("coordinate_note") or "").lower(), f"{gateway_id}: coordinate warning required"
        countries = gateway.get("countries") or []
        assert all(code in codes for code in countries), f"{gateway_id}: noncanonical country code"
        observation = gateway.get("observation") or {}
        assert isinstance(observation.get("value"), (int, float)), f"{gateway_id}: numeric observation required"
        assert str(observation.get("unit") or "").strip(), f"{gateway_id}: observation unit required"
        assert str(observation.get("period") or "").strip(), f"{gateway_id}: observation period required"
        assert str(observation.get("source") or "").strip(), f"{gateway_id}: source required"
        assert str(observation.get("source_url") or "").startswith("https://"), f"{gateway_id}: source URL required"
        assert str(gateway.get("description") or "").strip(), f"{gateway_id}: description required"


def validate_runtime(codes: set[str]) -> None:
    generator = load_generator()
    runtime = generator.build_runtime()
    assert runtime.get("country_count") == 195
    countries = runtime.get("countries") or {}
    assert set(countries) == codes, "runtime country coverage drift"
    for code, country in countries.items():
        systems = country.get("systems")
        assert isinstance(systems, dict), f"{code}: systems context required"
        for key in ("capabilities", "dependencies", "builds", "chains", "gateways"):
            assert isinstance(systems.get(key), list), f"{code}: systems.{key} must be a list"
        resilience = systems.get("resilience") or {}
        assert resilience.get("policy") == "no aggregate score inferred", f"{code}: resilience policy boundary missing"
        assert "score" not in resilience, f"{code}: resilience score forbidden"
        text = json.dumps(systems).lower()
        assert "capability_score" not in text and "resilience_score" not in text and "power_score" not in text, f"{code}: synthetic score forbidden"
    coverage = runtime.get("system_coverage") or {}
    for key in ("capabilities", "dependencies", "builds", "chains", "gateways"):
        assert isinstance(coverage.get(key), int), f"system coverage missing {key}"
        assert 0 <= coverage[key] <= 195, f"system coverage invalid for {key}"
    runtime_gateways = runtime.get("gateways") or {}
    assert REQUIRED_GATEWAYS.issubset(runtime_gateways), "runtime gateway projection incomplete"


def validate_registry_browser() -> None:
    registry = load_json(REGISTRY)
    entries = {entry.get("id"): entry for entry in registry.get("entries", []) if isinstance(entry, dict)}
    for entry_id in REQUIRED_CONTEXTUAL_ENTRIES:
        entry = entries.get(entry_id) or {}
        assert entry.get("availability") == "current", f"{entry_id} must be current"
        assert entry.get("map_priority") == "contextual", f"{entry_id} must remain contextual"
        assert entry.get("source_owner") == "data/world-map-data-runtime.json", f"{entry_id} must use shared runtime"
        assert entry.get("family") not in {"axis", "groups", "religion", "stats", "relations"} or entry.get("map_priority") != "ordinary"

    compositor = read(COMPOSITOR)
    for token in ("systemContext", "gatewaysForCountry", "gateway(", "systemCoverage"):
        assert token in compositor, f"compositor missing runtime API: {token}"

    card = read(CARD)
    for token in ("systemContext", "System role", "Building", "Gateways"):
        assert token in card, f"country card missing system-intelligence marker: {token}"
    assert "resilience score" not in card.lower(), "country card must not render resilience score"

    bootstrap = read(BOOTSTRAP)
    assert "./3d-gateways.js" in bootstrap, "gateway module must be booted"
    gateway_module = read(GATEWAY_MODULE)
    for token in ("potato-atlas-working-selection-change", "gatewaysForCountry", "GeoJSON", "Popup"):
        assert token in gateway_module, f"gateway module missing marker: {token}"


def main() -> int:
    try:
        codes = canonical_codes()
        validate_gateways(codes)
        validate_runtime(codes)
        validate_registry_browser()
    except (AssertionError, json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"World Map system-intelligence validation failed: {exc}", file=sys.stderr)
        return 1
    print("World Map system-intelligence validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
