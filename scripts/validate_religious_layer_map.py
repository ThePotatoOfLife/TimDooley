#!/usr/bin/env python3
"""Validate that the religious backend coupling map points at real layers."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data/religious-layer-map.json"
errors = []

def main():
    if not MAP.exists():
        errors.append("missing data/religious-layer-map.json")
        data = {}
    else:
        data = json.loads(MAP.read_text(encoding="utf-8"))
        layers = data.get("layers", [])
        ids = [x.get("id") for x in layers]
        if len(ids) != len(set(ids)):
            errors.append("duplicate layer ids")
        for layer in layers:
            rel = layer.get("file")
            if not rel:
                errors.append(f"layer {layer.get('id')} has no file")
                continue
            path = ROOT / rel.split("#", 1)[0]
            if not path.exists():
                errors.append(f"layer {layer.get('id')} points to missing file {rel}")
        # Required means canonical and currently present, not historical/deleted layers.
        required = {"lexicon", "foundation", "foundation-research", "adjacent-base", "adjacent-deep-1", "adjacent-deep-2", "adjacent-deep-3", "adjacent-relationships", "external-nodes", "comparative-library", "canonical-texts", "potatoism", "global-relationships"}
        missing = sorted(required - set(ids))
        if missing:
            errors.append("missing canonical layer registrations: " + ", ".join(missing))
        rules = data.get("coupling_rules", [])
        if len(rules) < 6:
            errors.append("coupling_rules unexpectedly sparse")
    print(f"religious layers checked: {len(data.get('layers', [])) if MAP.exists() else 0}; errors={len(errors)}")
    for error in errors:
        print("ERROR:", error)
    if errors:
        raise SystemExit(1)
    print("RELIGIOUS LAYER MAP PASSED")

if __name__ == "__main__":
    main()
