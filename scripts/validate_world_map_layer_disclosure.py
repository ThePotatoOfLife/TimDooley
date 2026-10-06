#!/usr/bin/env python3
"""Validate semantic disclosure for current World Map analytical layers and UI."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "world-map-layer-registry.json"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"

REQUIRED_CURRENT = {
    "id",
    "label",
    "family",
    "kind",
    "visual_channel",
    "epistemic_type",
    "source_owner",
    "spatiality",
}


def main() -> int:
    errors: list[str] = []
    if not REGISTRY.exists():
        errors.append("missing data/world-map-layer-registry.json")
    else:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        channels = set((data.get("visual_channels") or {}).keys())
        if not channels:
            errors.append("layer registry does not declare visual_channels")
        for entry in data.get("entries", []):
            if entry.get("availability") != "current":
                continue
            missing = sorted(key for key in REQUIRED_CURRENT if not entry.get(key))
            if missing:
                errors.append(f"{entry.get('id', '<unknown>')}: missing semantic metadata {', '.join(missing)}")
            channel = entry.get("visual_channel")
            if channel and channel not in channels:
                errors.append(f"{entry.get('id', '<unknown>')}: undeclared visual channel {channel}")

    if not WORLD_BAR.exists():
        errors.append("missing world-map/3d-world-bar.js")
    else:
        text = WORLD_BAR.read_text(encoding="utf-8")
        for token in (
            "function layerMeta",
            "function layerSource",
            "function layerTitle",
            "Layer type",
            "Source owner",
            "Set types",
            "entry.epistemic_type",
            "entry.visual_channel",
            "entry?.source_owner",
        ):
            if token not in text:
                errors.append(f"World Bar missing layer disclosure marker {token}")
        if "<small>${esc(layerMeta(entry))}</small>" not in text:
            errors.append("analytical menu rows do not expose semantic layer metadata")

    if errors:
        print("WORLD MAP LAYER DISCLOSURE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP LAYER DISCLOSURE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
