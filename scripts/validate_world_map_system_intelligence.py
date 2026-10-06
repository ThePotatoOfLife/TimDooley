#!/usr/bin/env python3
"""Validate evidence-backed World Map system-intelligence and gateway contracts."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build_world_map_runtime.py"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
SYSTEM_REGISTRY = ROOT / "data" / "world-map-system-intelligence-registry.json"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
GATEWAY_MODULE = ROOT / "world-map" / "3d-gateways.js"

REQUIRED_GATEWAYS = {"malacca-strait","hormuz-strait","suez-sumed","bab-el-mandeb","danish-straits","turkish-straits","panama-canal","cape-good-hope-route"}
REQUIRED_CONTEXTUAL_ENTRIES = {"derived.capability","derived.dependency","derived.resilience","derived.builds","gateway.context"}


def load_json(path: Path):
    if not path.is_file(): raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    if not path.is_file(): raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def canonical_codes() -> set[str]:
    data = load_json(ROOT / "data" / "countries" / "index.json")
    codes = {str(row.get("iso3") or "").upper() for row in data.get("countries", [])}; codes.discard("")
    assert len(codes) == 195, f"expected 195 canonical countries, got {len(codes)}"
    return codes


def load_generator():
    spec = importlib.util.spec_from_file_location("build_world_map_runtime", GENERATOR)
    assert spec and spec.loader, "could not load runtime generator"
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def validate_gateways(codes: set[str]) -> None:
    gateways = (load_json(GATEWAYS).get("gateways") or {})
    assert REQUIRED_GATEWAYS.issubset(gateways), f"missing gateways: {sorted(REQUIRED_GATEWAYS - set(gateways))}"
    for gateway_id, gateway in gateways.items():
        assert gateway.get("epistemic_type") == "observed", f"{gateway_id}: gateway must be observed"
        assert gateway.get("type") in {"maritime-chokepoint","canal","strategic-maritime-route"}, f"{gateway_id}: invalid type"
        coords = gateway.get("coordinates") or []; assert isinstance(coords,list) and len(coords)==2, f"{gateway_id}: coordinates must be [lon, lat]"
        lon, lat = coords; assert isinstance(lon,(int,float)) and -180<=lon<=180; assert isinstance(lat,(int,float)) and -90<=lat<=90
        assert gateway.get("coordinate_precision") == "approximate-center"
        assert "navigation" in str(gateway.get("coordinate_note") or "").lower()
        assert all(code in codes for code in gateway.get("countries",[])), f"{gateway_id}: noncanonical country code"
        obs = gateway.get("observation") or {}
        assert isinstance(obs.get("value"),(int,float)) and obs.get("unit") and obs.get("period") and obs.get("source")
        assert str(obs.get("source_url") or "").startswith("https://")
        assert gateway.get("description")


def validate_runtime(codes: set[str]) -> None:
    runtime = load_generator().build_runtime()
    assert runtime.get("country_count") == 195
    countries = runtime.get("countries") or {}; assert set(countries) == codes
    for code, country in countries.items():
        systems = country.get("systems"); assert isinstance(systems,dict), f"{code}: systems context required"
        for key in ("capabilities","dependencies","builds","chains","gateways"):
            assert isinstance(systems.get(key),list), f"{code}: systems.{key} must be a list"
        resilience = systems.get("resilience") or {}
        assert resilience.get("policy") == "no aggregate score inferred"
        text = json.dumps(systems).lower()
        assert "capability_score" not in text and "resilience_score" not in text and "power_score" not in text
    coverage = runtime.get("system_coverage") or {}
    for key in ("capabilities","dependencies","builds","chains","gateways"):
        assert isinstance(coverage.get(key),int) and 0 <= coverage[key] <= 195, f"invalid system coverage: {key}"
    assert REQUIRED_GATEWAYS.issubset(runtime.get("gateways") or {}), "runtime gateway projection incomplete"


def validate_browser() -> None:
    registry = load_json(SYSTEM_REGISTRY)
    entries = {entry.get("id"):entry for entry in registry.get("entries",[]) if isinstance(entry,dict)}
    for entry_id in REQUIRED_CONTEXTUAL_ENTRIES:
        entry = entries.get(entry_id) or {}
        assert entry.get("availability") == "current", f"{entry_id} must be current"
        assert entry.get("map_priority") == "contextual", f"{entry_id} must remain contextual"
        assert entry.get("source_owner") == "data/world-map-data-runtime.json", f"{entry_id} must use shared runtime"
        assert entry.get("ordinary") is False, f"{entry_id} must not create ordinary navigation"

    module = read(GATEWAY_MODULE)
    for token in ("systemContext", "gatewaysForCountry", "systemCoverage", "System role", "Building", "Gateways", "potato-atlas-working-selection-change", "GeoJSON", "Popup"):
        assert token in module, f"system module missing marker: {token}"
    assert "resilience score" not in module.lower()
    bootstrap = read(BOOTSTRAP)
    assert "./3d-gateways.js" in bootstrap, "system/gateway module must be booted"


def main() -> int:
    try:
        codes = canonical_codes(); validate_gateways(codes); validate_runtime(codes); validate_browser()
    except (AssertionError, json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"World Map system-intelligence validation failed: {exc}", file=sys.stderr); return 1
    print("World Map system-intelligence validation passed."); return 0


if __name__ == "__main__": raise SystemExit(main())
