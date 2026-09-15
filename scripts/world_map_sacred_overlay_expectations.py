#!/usr/bin/env python3
"""Focused expectations for the Mesopotamia / covenant-land map slice."""
from __future__ import annotations

import json
from pathlib import Path


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "data" / "world-map-spatial-overlays.json"
    ui_path = root / "world-map" / "3d-spatial-overlay-ui.js"
    world_bar_path = root / "world-map" / "3d-world-bar.js"
    guard_path = root / "world-map" / "3d-boot-guard.js"
    bootstrap_path = root / "world-map" / "3d-bootstrap.js"
    foundation_path = root / "data" / "world-map-spatial" / "sacred-covenant-foundation.geojson"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot read spatial overlay manifest for sacred-geography expectations: {exc}"]

    by_id = {row.get("id"): row for row in manifest.get("entries") or [] if isinstance(row, dict)}
    expected = {
        "father.mesopotamia-core": "father-mesopotamia-core-v2",
        "father.lower-mesopotamia-gulf": "father-lower-mesopotamia-gulf-v1",
        "physical.tigris-euphrates-basin": "tigris-euphrates-basin-reference-v1",
        "biblical.numbers-34": "numbers-34-v1",
        "biblical.genesis-15": "genesis-15-river-to-river-v2",
        "biblical.genesis-15-nile": "genesis-15-nile-to-euphrates-v1",
        "modern.greater-israel": "greater-israel-nile-euphrates-v2",
    }
    for overlay_id, feature_id in expected.items():
        row = by_id.get(overlay_id)
        if not row:
            errors.append(f"missing expected geography overlay: {overlay_id}")
            continue
        if row.get("availability") != "current":
            errors.append(f"{overlay_id} must be selectable now, not {row.get('availability')}")
        if feature_id not in (row.get("feature_ids") or []):
            errors.append(f"{overlay_id} must own {feature_id}")
        if not row.get("source_ids"):
            errors.append(f"{overlay_id} must carry explicit source identifiers")
        if not row.get("measurable"):
            errors.append(f"{overlay_id} must participate in geometry-derived measurement output")

    greater = by_id.get("modern.greater-israel") or {}
    greater_note = str(greater.get("status_note") or "").lower()
    for phrase in ("scenario", "not an official border", "not a sovereignty claim"):
        if phrase not in greater_note:
            errors.append(f"modern.greater-israel status note must state '{phrase}'")

    genesis = by_id.get("biblical.genesis-15") or {}
    genesis_note = str(genesis.get("status_note") or "").lower()
    if "wadi el-arish" not in genesis_note:
        errors.append("biblical.genesis-15 must name the Wadi el-Arish interpretation used by its geometry")
    nile_note = str((by_id.get("biblical.genesis-15-nile") or {}).get("status_note") or "").lower()
    if "nile" not in nile_note:
        errors.append("biblical.genesis-15-nile must explicitly identify the Nile interpretation")

    meso = by_id.get("father.mesopotamia-core") or {}
    meso_sources = set(meso.get("source_ids") or [])
    for source_id in ("british-museum-mesopotamia", "cambridge-mesopotamia-definition"):
        if source_id not in meso_sources:
            errors.append(f"father.mesopotamia-core must cite {source_id}")

    try:
        foundation = json.loads(foundation_path.read_text(encoding="utf-8"))
        feature_map = {f.get("properties", {}).get("feature_id"): f for f in foundation.get("features") or []}
    except Exception as exc:
        errors.append(f"cannot inspect sacred foundation geometry: {exc}")
        feature_map = {}
    meso_feature = feature_map.get("father-mesopotamia-core-v2") or {}
    coords = ((meso_feature.get("geometry") or {}).get("coordinates") or [[]])[0]
    if len(coords) < 20:
        errors.append("father-mesopotamia-core-v2 must be a denser sourced reconstruction, not the old coarse envelope")

    ui = ui_path.read_text(encoding="utf-8", errors="replace") if ui_path.is_file() else ""
    for token in (
        "spatialGeographyView", "Geographies", "Mesopotamia", "Genesis 15", "Greater Israel",
        "Chosen Children’s Land / Greater Israel scenarios",
    ):
        if token not in ui:
            errors.append(f"spatial geography UI missing geography marker: {token}")

    world_bar = world_bar_path.read_text(encoding="utf-8", errors="replace") if world_bar_path.is_file() else ""
    for token in (
        "GEOGRAPHIES", "Geography", "data-geography-overlay", "__potatoAtlasSpatialOverlays",
        "father.mesopotamia-core", "biblical.genesis-15", "modern.greater-israel",
        "father.lower-mesopotamia-gulf", "biblical.numbers-34", "biblical.genesis-15-nile",
    ):
        if token not in world_bar:
            errors.append(f"canonical visible World Map bar missing first-class geography marker: {token}")
    if "spatial.toggle(id)" not in world_bar:
        errors.append("Geography toolbar must use spatial.toggle(id) so a checked geography can be deselected")

    guard = guard_path.read_text(encoding="utf-8", errors="replace") if guard_path.is_file() else ""
    for event_name in ("error", "unhandledrejection"):
        marker = f"window.addEventListener('{event_name}'"
        start = guard.find(marker)
        end = guard.find("});", start)
        if start < 0:
            errors.append(f"boot guard missing {event_name} diagnostics listener")
        elif "showFailure(" in guard[start:end + 3]:
            errors.append(f"boot guard must record transient {event_name} diagnostics without painting an immediate red failure")
    if "showFailure(failures.length" not in guard:
        errors.append("boot watchdog must still surface a real boot failure after the deadline")

    bootstrap = bootstrap_path.read_text(encoding="utf-8", errors="replace") if bootstrap_path.is_file() else ""
    if "setStatus(`Atlas core failed to boot:" not in bootstrap:
        errors.append("bootstrap must still show a red error for an actual fatal core boot failure")

    return errors
