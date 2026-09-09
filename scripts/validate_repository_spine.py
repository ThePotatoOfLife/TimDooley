#!/usr/bin/env python3
"""Validate the internal Spirit / Mind / Matter filing spine and its public-manifest boundary."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []


def load(rel: str):
    p = ROOT / rel
    if not p.exists():
        errors.append(f"Missing: {rel}")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid JSON: {rel}: {exc}")
        return {}


def main():
    spine = load("data/repository-spine.json")
    root_order = spine.get("root_order", [])
    expected = ["spirit", "mind", "matter"]
    actual = [x.get("id") for x in root_order if isinstance(x, dict)]
    if actual != expected:
        errors.append(f"Internal spine root_order must be Spirit, Mind, Matter; found {actual}")

    if spine.get("matter_scale") != "data/repository-scale.json":
        errors.append("Matter must use data/repository-scale.json as its concrete scale")

    required_groups = {
        "spirit_layers": {"source", "meaning", "belief", "myths"},
        "mind_layers": {"psychology", "hawkinscale", "neurobiology"},
        "matter_layers": {"world", "region", "institution", "network", "person", "object", "event", "record", "ground"},
    }
    for field, required in required_groups.items():
        actual_ids = {x.get("id") for x in spine.get(field, []) if isinstance(x, dict)}
        missing = required - actual_ids
        if missing:
            errors.append(f"{field} missing: {sorted(missing)}")

    coordinates = spine.get("independent_coordinates", {})
    if not all(key in coordinates for key in ("scale", "domain", "time", "epistemic_status", "graph")):
        errors.append("Independent coordinates must include scale, domain, time, epistemic_status and graph")

    public = spine.get("public_navigation", {})
    if public.get("source") != "manifest.json" or public.get("root_id") != "potato-of-life":
        errors.append("Internal spine must delegate public navigation to manifest.json root potato-of-life")

    manifest = load("manifest.json")
    if manifest.get("root", {}).get("id") != "potato-of-life":
        errors.append("Public manifest root is not potato-of-life")
    branch_ids = {b.get("id") for b in manifest.get("branches", []) if isinstance(b, dict)}
    required_public = {"tim","son","spirit","transformation","cosmology","body","traditions","north","world","chronology","works","sources"}
    missing_public = required_public - branch_ids
    if missing_public:
        errors.append(f"Public manifest missing branches: {sorted(missing_public)}")
    if "axis" in branch_ids:
        warnings.append("Public manifest still exposes legacy AXIS branch")

    legacy = spine.get("legacy_navigation_mapping", {})
    for old in ("axis", "world"):
        if old not in legacy:
            errors.append(f"Internal spine must document legacy navigation mapping for {old}")

    # Ensure repository-index taxonomy values remain compatible with the spine.
    index = load("data/repository-index.json")
    allowed_layers = {
        "spirit": {x.get("id") for x in spine.get("spirit_layers", []) if isinstance(x, dict)},
        "mind": {x.get("id") for x in spine.get("mind_layers", []) if isinstance(x, dict)},
        "matter": {x.get("id") for x in spine.get("matter_layers", []) if isinstance(x, dict)},
    }
    bad = []
    for row in index.get("records", []):
        root = row.get("repository_root")
        layer = row.get("repository_layer")
        if root not in allowed_layers or layer not in allowed_layers[root]:
            bad.append((row.get("id"), root, layer))
    if bad:
        errors.append(f"Repository index has {len(bad)} records outside internal spine; examples: {bad[:8]}")

    print(f"Internal spine roots: {actual}")
    print(f"Spirit sections: {len(spine.get('spirit_layers', []))}")
    print(f"Mind sections: {len(spine.get('mind_layers', []))}")
    print(f"Matter sections: {len(spine.get('matter_layers', []))}")
    print(f"Public manifest branches: {len(branch_ids)}")
    print(f"Indexed records checked: {len(index.get('records', []))}")
    print(f"Errors: {len(errors)} · Warnings: {len(warnings)}")
    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
