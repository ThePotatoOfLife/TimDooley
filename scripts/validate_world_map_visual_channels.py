#!/usr/bin/env python3
"""Validate World Map visual-channel ownership and incompatible-combination policy."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "world-map-visual-channel-contract.json"
REGISTRY = ROOT / "data" / "world-map-layer-registry.json"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"

def load(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid or missing {path.relative_to(ROOT)}: {exc}")
        return {}

def main() -> int:
    errors: list[str] = []
    contract = load(CONTRACT, errors)
    registry = load(REGISTRY, errors)
    compositor = COMPOSITOR.read_text(encoding="utf-8", errors="replace") if COMPOSITOR.is_file() else ""
    ui = (ROOT / "world-map" / "3d-ui.js").read_text(encoding="utf-8", errors="replace") if (ROOT / "world-map" / "3d-ui.js").is_file() else ""
    selection = (ROOT / "world-map" / "3d-country-selection.js").read_text(encoding="utf-8", errors="replace") if (ROOT / "world-map" / "3d-country-selection.js").is_file() else ""
    physical = (ROOT / "world-map" / "3d-physical-layers.js").read_text(encoding="utf-8", errors="replace") if (ROOT / "world-map" / "3d-physical-layers.js").is_file() else ""
    world_bar = (ROOT / "world-map" / "3d-world-bar.js").read_text(encoding="utf-8", errors="replace") if (ROOT / "world-map" / "3d-world-bar.js").is_file() else ""
    lenses = (ROOT / "world-map" / "3d-lenses.js").read_text(encoding="utf-8", errors="replace") if (ROOT / "world-map" / "3d-lenses.js").is_file() else ""

    channels = contract.get("channels") or {}
    required = {"fill","pattern","outline","line","point","height","card","timeline","scene"}
    if set(channels) != required:
        errors.append(f"visual-channel contract must define exactly {sorted(required)}")

    compatibility = contract.get("compatibility") or {}
    pattern_height = compatibility.get("pattern+height") or {}
    if pattern_height.get("status") != "incompatible-current-renderer":
        errors.append("pattern+height must remain explicitly incompatible until patterns are mapped onto extrusion surfaces")
    if pattern_height.get("policy") != "prefer-pattern-flatten-height":
        errors.append("pattern+height policy must preserve set information by flattening height")

    entries = registry.get("entries") or []
    unknown = sorted({
        str(row.get("visual_channel"))
        for row in entries
        if row.get("visual_channel") and row.get("visual_channel") not in channels
    })
    if unknown:
        errors.append(f"layer registry uses unknown visual channels: {unknown}")
    for row in entries:
        if row.get("kind") == "scalar" and row.get("availability") == "current" and row.get("visual_channel") != "fill":
            errors.append(f"current scalar {row.get('id')} must use fill visual channel")
        if row.get("kind") == "set" and row.get("availability") == "current" and row.get("visual_channel") != "pattern":
            errors.append(f"current set {row.get('id')} must use pattern visual channel")

    expected_owners = {
        "countries-fill.fill-color": "world-map/3d-compositor.js",
        "countries-extrude.fill-extrusion-color": "world-map/3d-compositor.js",
        "countries-line.line-color": "world-map/3d-country-selection.js",
        "countries-line.line-width": "world-map/3d-country-selection.js",
        "countries-fill.fill-opacity": "world-map/3d-physical-layers.js",
        "countries-extrude.fill-extrusion-height": "world-map/3d-app.js",
        "countries-fill/countries-extrude.visibility": "world-map/3d-app.js",
    }
    if contract.get("country_surface_owners") != expected_owners:
        errors.append("country surface owner map must preserve one canonical owner per visual channel")

    for forbidden in (
        "setPaintProperty('countries-fill','fill-color'",
        "setPaintProperty('countries-extrude','fill-extrusion-color'",
        "setPaintProperty('countries-line','line-color'",
        "setPaintProperty('countries-line','line-width'",
        "setPaintProperty('countries-fill','fill-opacity'",
    ):
        if forbidden in ui:
            errors.append(f"legacy 3d-ui.js must not write canonical country visual channels: {forbidden}")

    if "setBaseFill" not in compositor or "countries-fill" not in compositor or "countries-extrude" not in compositor:
        errors.append("compositor must retain canonical country fill/extrusion color ownership")
    for forbidden in (
        "setPaintProperty('countries-fill'",
        "setPaintProperty('countries-extrude'",
        "setPaintProperty('countries-line'",
        "setFeatureState({ source: 'countries'",
    ):
        if forbidden in lenses:
            errors.append(f"legacy Lens adapter must not regain canonical country render ownership: {forbidden}")
    for token in ("LEGACY_TO_LAYER", "layers.activate(layerId)", "compositor.render()", "compatibility:true"):
        if token not in lenses:
            errors.append(f"legacy Lens adapter missing canonical translation marker: {token}")
    for marker in ("setPaintProperty('countries-line', 'line-color'", "setPaintProperty('countries-line', 'line-width'"):
        if marker not in selection:
            errors.append(f"country selection must retain canonical outline ownership: {marker}")
    if "setPaintProperty('countries-fill', 'fill-opacity'" not in physical:
        errors.append("Physical World must retain canonical country fill-opacity ownership")
    for token in ("Color fill + exact value text", "Pattern + membership text", "aria-pressed", "aria-label"):
        if token not in world_bar:
            errors.append(f"World Bar missing non-color/accessibility redundancy marker: {token}")

    for token in (
        "VISUAL_CHANNEL_URL",
        "enforceVisualCompatibility",
        "pattern+height",
        "prefer-pattern-flatten-height",
        "height.disabled = incompatible",
        "height.value = 'flat'",
        "potato-atlas-visual-channel-resolution",
    ):
        if token not in compositor:
            errors.append(f"compositor missing visual-channel enforcement marker: {token}")

    if errors:
        print("WORLD MAP VISUAL CHANNEL VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP VISUAL CHANNEL VALIDATION PASSED")
    print(f"Channels: {len(channels)} · registry entries: {len(entries)} · pattern+height fallback enforced")
    return 0

if __name__ == "__main__":
    sys.exit(main())
