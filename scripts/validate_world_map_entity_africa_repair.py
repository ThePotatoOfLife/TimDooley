#!/usr/bin/env python3
"""Validate the World Map entity/Greenland/Africa repair contract."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTRY_INDEX = ROOT / "data" / "countries" / "index.json"
ENTITIES = ROOT / "data" / "world-map-entities.json"
AFRICA = ROOT / "data" / "world-africa-regional-systems.json"
RUNTIME_BUILDER = ROOT / "scripts" / "build_world_map_runtime.py"
ENTITY_UTILS = ROOT / "scripts" / "world_map_entity_utils.py"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
SELECTION = ROOT / "world-map" / "3d-country-selection.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
DEMOGRAPHY = ROOT / "world-map" / "3d-demography.js"
HOVER = ROOT / "world-map" / "3d-hover.js"
AXIS = ROOT / "data" / "world-axis-profiles.json"
CHAINS = ROOT / "data" / "world-system-chains.json"


def load_json(path: Path, errors: list[str]):
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}


def text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require(haystack: str, needle: str, label: str, errors: list[str]) -> None:
    if needle not in haystack:
        errors.append(f"{label} missing marker: {needle}")


def main() -> int:
    errors: list[str] = []
    country_index = load_json(COUNTRY_INDEX, errors)
    entities = load_json(ENTITIES, errors)
    africa = load_json(AFRICA, errors)
    axis = load_json(AXIS, errors)
    chains = load_json(CHAINS, errors)

    countries = country_index.get("countries", [])
    if len(countries) != 195:
        errors.append(f"sovereign country count must stay 195; found {len(countries)}")

    grl = (entities.get("entities") or {}).get("GRL")
    if not isinstance(grl, dict):
        errors.append("GRL must exist in data/world-map-entities.json")
    else:
        if grl.get("canonical_country") is not False:
            errors.append("GRL must be explicitly non-country")
        if grl.get("constitutional_parent") != "DNK":
            errors.append("GRL constitutional_parent must be DNK")
        if grl.get("capital") != "Nuuk":
            errors.append("GRL capital must be Nuuk")
        pop = grl.get("population") or {}
        if not str(pop.get("source_url") or "").startswith("https://stat.gl/"):
            errors.append("GRL population must cite Statistics Greenland")
        anchor = grl.get("label_anchor") or {}
        coords = anchor.get("coordinates") if isinstance(anchor, dict) else None
        if not (isinstance(coords, list) and len(coords) == 2):
            errors.append("GRL requires a two-coordinate label_anchor")

    systems = africa.get("systems") or {}
    eac = systems.get("eac") or {}
    sadc = systems.get("sadc") or {}
    ecowas = systems.get("ecowas") or {}
    if len(eac.get("members") or []) != 8:
        errors.append("EAC must have 8 current partner states")
    if len(sadc.get("members") or []) != 16:
        errors.append("SADC must have 16 current member states")
    ecowas_members = set(ecowas.get("members") or [])
    if ecowas_members & {"BFA", "MLI", "NER"}:
        errors.append("ECOWAS current membership must exclude BFA/MLI/NER")
    if not {"COD", "TZA"}.issubset(set(eac.get("members") or []) & set(sadc.get("members") or [])):
        errors.append("COD and TZA must resolve to both EAC and SADC")
    transitions = {row.get("code"): row for row in ecowas.get("former_or_transition_members", []) if isinstance(row, dict)}
    for code in ("BFA", "MLI", "NER"):
        if transitions.get(code, {}).get("effective_date") != "2025-01-29":
            errors.append(f"ECOWAS transition history missing 2025-01-29 for {code}")

    axis_profiles = axis.get("profiles") or {}
    if "GRL" not in axis_profiles:
        errors.append("GRL requires an Axis profile")
    if (axis_profiles.get("COD") or {}).get("orientations"):
        errors.append("COD must remain directionally unresolved in this wave")

    for chain_id in ("arctic", "north-atlantic"):
        if "GRL" not in ((chains.get("chains") or {}).get(chain_id, {}).get("members") or []):
            errors.append(f"GRL must belong to {chain_id} chain")

    compositor = text(COMPOSITOR, errors)
    selection = text(SELECTION, errors)
    card = text(CARD, errors)
    demography = text(DEMOGRAPHY, errors)
    hover = text(HOVER, errors)
    runtime_builder = text(RUNTIME_BUILDER, errors)

    for marker in ("entity(code)", "entityName(code)", "entityType(code)", "populationObservation(code)", "labelAnchor(code)"):
        require(compositor, marker, "3d-compositor.js", errors)
    require(runtime_builder, "world-map-entities.json", "build_world_map_runtime.py", errors)
    require(runtime_builder, "world-africa-regional-systems.json", "build_world_map_runtime.py", errors)
    require(selection, "entity", "3d-country-selection.js", errors)
    require(card, "Self-governing territory", "3d-country-card.js", errors)
    require(demography, "population-label-anchor", "3d-demography.js", errors)

    add_labels_start = demography.find("async function addPopulationLabels")
    if add_labels_start >= 0:
        block = demography[add_labels_start:add_labels_start + 5000]
        if "REST_URL" in block or ".latlng" in block:
            errors.append("addPopulationLabels must not use REST country latlng as label authority")

    if "(minY + maxY) / 2" in hover and "(minX + maxX) / 2" in hover:
        errors.append("3d-hover.js still contains unsafe geometry-wide bbox midpoint fallback")

    if not ENTITY_UTILS.is_file():
        errors.append("missing scripts/world_map_entity_utils.py")
    else:
        spec = importlib.util.spec_from_file_location("world_map_entity_utils", ENTITY_UTILS)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        fixture = {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [[[170, 55], [179, 55], [179, 65], [170, 65], [170, 55]]],
                    [[[-179, 60], [-170, 60], [-170, 66], [-179, 66], [-179, 60]]],
                ],
            },
        }
        anchor = module.representative_component_anchor(fixture)
        if not (isinstance(anchor, list) and len(anchor) == 2):
            errors.append("representative_component_anchor must return [lon, lat]")
        elif abs(float(anchor[0])) < 120:
            errors.append(f"antimeridian fallback regressed toward longitude zero: {anchor}")

    if errors:
        print("World Map entity/Africa repair validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("World Map entity/Africa repair validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
