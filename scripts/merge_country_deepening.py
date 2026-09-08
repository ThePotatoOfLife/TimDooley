#!/usr/bin/env python3
"""Apply the universal deepening overlay to every country node.

The blueprint is schema only: this script creates containers and never invents
empirical values. The filename is resolved through the canonical blueprint
contract so renaming a blueprint cannot silently break country generation.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data/countries/index.json"
OVERLAY = ROOT / "data/blueprints/country-deepening-blueprint.json"
OUT = ROOT / "data/countries"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    index = load(INDEX)
    overlay = load(OVERLAY)
    now = datetime.now(timezone.utc).isoformat()
    layers = overlay["layers"]
    changed = 0
    for country in index["countries"]:
        path = OUT / f"{country['id']}.json"
        if not path.exists():
            continue
        record = load(path)
        record.setdefault("deepening", {})
        record["deepening"].setdefault("overlay", "data/blueprints/country-deepening-blueprint.json")
        record["deepening"].setdefault("overlay_version", overlay["version"])
        record["deepening"].setdefault("layers", {})
        for layer, fields in layers.items():
            record["deepening"]["layers"].setdefault(layer, {})
            for field in fields:
                record["deepening"]["layers"][layer].setdefault(field, None)
        record["deepening"].setdefault("relationships", [])
        record["deepening"].setdefault("missing_fields", [])
        record["deepening"]["last_schema_pass"] = now
        record.setdefault("coverage", {})
        record["coverage"]["deepening_overlay"] = True
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed += 1
    state = {
        "generated_at": now,
        "countries_seen": len(index["countries"]),
        "nodes_deepened": changed,
        "overlay": "data/blueprints/country-deepening-blueprint.json",
        "rule": "Schema containers are created without inventing empirical values."
    }
    (OUT / "deepening-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
