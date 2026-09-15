#!/usr/bin/env python3
"""Validate World Map spatial-overlay manifest and GeoJSON ownership."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "world-map-spatial-overlays.json"
ALLOWED_TYPES = {
    "current_observed",
    "current_disputed",
    "historical_reconstruction",
    "textual_reconstruction",
    "political_ideology",
    "project_interpretive",
    "event_observed",
    "humanitarian_observed",
}
REQUIRED_ENTRY = {
    "id", "label", "family", "epistemic_type", "geometry_owner", "feature_ids",
    "source_ids", "confidence", "availability", "measurable", "status_note", "visual",
}
REQUIRED_FEATURE = {
    "feature_id", "overlay_id", "label", "epistemic_type", "source_ids",
    "geometry_version", "confidence", "status_note", "measurement_policy",
}


def load_json(path: Path, errors: list[str]):
    if not path.is_file():
        errors.append(f"missing required spatial overlay file: {path.relative_to(ROOT)}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return None


def main() -> int:
    errors: list[str] = []
    manifest = load_json(MANIFEST, errors)
    if not isinstance(manifest, dict):
        manifest = {}

    declared_types = set(manifest.get("epistemic_types") or [])
    if declared_types != ALLOWED_TYPES:
        errors.append("manifest epistemic_types must exactly match the canonical spatial epistemic enum")

    entries = manifest.get("entries") or []
    if not isinstance(entries, list) or not entries:
        errors.append("spatial overlay manifest must contain entries")
        entries = []

    seen_ids: set[str] = set()
    owners: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("every spatial overlay entry must be an object")
            continue
        missing = sorted(REQUIRED_ENTRY - set(entry))
        if missing:
            errors.append(f"overlay {entry.get('id', '<unknown>')} missing fields: {', '.join(missing)}")
        overlay_id = entry.get("id")
        if not overlay_id:
            continue
        if overlay_id in seen_ids:
            errors.append(f"duplicate spatial overlay id: {overlay_id}")
        seen_ids.add(overlay_id)
        if entry.get("epistemic_type") not in ALLOWED_TYPES:
            errors.append(f"overlay {overlay_id} has invalid epistemic_type {entry.get('epistemic_type')}")
        if entry.get("availability") not in {"current", "planned", "retired"}:
            errors.append(f"overlay {overlay_id} has invalid availability")
        visual = entry.get("visual") or {}
        if not visual.get("legend_class"):
            errors.append(f"overlay {overlay_id} must define visual.legend_class")
        owner = entry.get("geometry_owner")
        feature_ids = entry.get("feature_ids") or []
        if entry.get("availability") == "current" and not feature_ids:
            errors.append(f"current overlay {overlay_id} must own at least one feature")
        if feature_ids:
            if not owner:
                errors.append(f"overlay {overlay_id} has features but no geometry_owner")
                continue
            if owner not in owners:
                data = load_json(ROOT / owner, errors)
                owners[owner] = data if isinstance(data, dict) else {}

    for owner, collection in owners.items():
        if collection.get("type") != "FeatureCollection":
            errors.append(f"{owner} must be a GeoJSON FeatureCollection")
            continue
        feature_map = {}
        for feature in collection.get("features") or []:
            props = feature.get("properties") or {}
            fid = props.get("feature_id")
            if not fid:
                errors.append(f"{owner} contains a feature without feature_id")
                continue
            if fid in feature_map:
                errors.append(f"{owner} contains duplicate feature_id {fid}")
            feature_map[fid] = feature
            missing = sorted(REQUIRED_FEATURE - set(props))
            if missing:
                errors.append(f"feature {fid} missing properties: {', '.join(missing)}")
            if props.get("epistemic_type") not in ALLOWED_TYPES:
                errors.append(f"feature {fid} has invalid epistemic_type")
            geometry = feature.get("geometry") or {}
            if geometry.get("type") not in {"Polygon", "MultiPolygon", "LineString", "MultiLineString", "Point", "MultiPoint"}:
                errors.append(f"feature {fid} has unsupported or missing geometry")

        for entry in entries:
            if entry.get("geometry_owner") != owner:
                continue
            for fid in entry.get("feature_ids") or []:
                feature = feature_map.get(fid)
                if not feature:
                    errors.append(f"overlay {entry.get('id')} references missing feature {fid} in {owner}")
                    continue
                props = feature.get("properties") or {}
                if props.get("overlay_id") != entry.get("id"):
                    errors.append(f"feature {fid} overlay_id does not match manifest owner {entry.get('id')}")
                if props.get("epistemic_type") != entry.get("epistemic_type"):
                    errors.append(f"feature {fid} epistemic_type differs from manifest")

    if errors:
        print("World Map spatial overlay validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"World Map spatial overlay validation passed: {len(entries)} overlays, {len(owners)} geometry owner(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
