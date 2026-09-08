#!/usr/bin/env python3
"""Validate the canonical Root -> Spirit / Mind / Matter navigation model."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


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
    actual = [x.get("id") for x in root_order]
    if actual != expected:
        errors.append(f"Spine root_order must be Spirit, Mind, Matter; found {actual}")

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

    tree = load("data/tree.json")
    legacy = spine.get("legacy_tree_mapping", {})
    tree_ids = {x.get("id") for x in tree.get("levels", []) if isinstance(x, dict)}
    for key in legacy:
        if key not in tree_ids:
            errors.append(f"Legacy tree mapping references missing level: {key}")

    manifest = load("data/atlas-manifest.json")
    if "architecture" not in manifest.get("layers", {}):
        errors.append("Manifest architecture layer missing")

    print(f"Spine root branches: {len(root_order)}")
    print(f"Spirit sections: {len(spine.get('spirit_layers', []))}")
    print(f"Mind sections: {len(spine.get('mind_layers', []))}")
    print(f"Matter scale sections: {len(spine.get('matter_layers', []))}")
    print(f"Legacy tree levels mapped: {len(legacy)}")
    print(f"Errors: {len(errors)}")
    for error in errors:
        print("ERROR:", error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
