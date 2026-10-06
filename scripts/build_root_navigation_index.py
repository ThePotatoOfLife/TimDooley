#!/usr/bin/env python3
"""Build the presentation index consumed by the fixed-center homepage.

The repository-index remains the canonical generated inventory. This file is only
an interface projection: it assigns each canonical/record row one or more paths
under WORLD or AXIS without creating another identity store.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE = DATA / "repository-index.json"
OUT = DATA / "root-record-index.json"


def path_for(record: dict) -> list[str]:
    family = str(record.get("owner_family", "general")).lower()
    typ = str(record.get("type", "record")).lower()
    role = str(record.get("record_role", "")).lower()
    layer = str(record.get("repository_layer", "world")).lower()
    root = str(record.get("repository_root", "matter")).lower()
    name = str(record.get("name", record.get("id", ""))).lower()

    if root == "matter":
        if typ in {"person", "people", "individual", "human"}:
            return ["WORLD", "PEOPLE"]
        if family == "countries" or layer in {"region", "ground"}:
            return ["WORLD", "PLACES"]
        if family == "religion-texts":
            return ["WORLD", "RELIGIONS"]
        if family == "north-europe-economic" or typ in {"market", "finance", "economic"}:
            return ["WORLD", "ECONOMY"]
        if typ in {"organization", "institution", "company", "bank", "university", "government", "authority", "system"}:
            return ["WORLD", "INSTITUTIONS"]
        if typ in {"event", "action", "transaction", "war", "election", "geopolitical-timeline", "economic-environmental-event", "mythic-event"}:
            return ["WORLD", "EVENTS"]
        if family in {"security-intelligence", "movements-swamp"}:
            return ["WORLD", "POLITICS"]
        if family in {"research", "general"} and any(word in name for word in ("culture", "language", "folk", "music", "art")):
            return ["WORLD", "CULTURE"]
        return ["WORLD", "RECORDS"]

    # Spirit/mind is the project's structural/interpretive material. It belongs
    # to the Axis presentation, while the original repository taxonomy remains
    # untouched in repository-index.json.
    if family == "potatoism":
        return ["AXIS", "POTATOISM"]
    if family == "religion-texts":
        return ["WORLD", "RELIGIONS"]
    if "north" in name or "axis" in name:
        return ["AXIS", "NORTH"]
    if "geometry" in name or "vesica" in name or "mandorla" in name:
        return ["AXIS", "GEOMETRY"]
    if role == "relationship" or family == "relationships-graph":
        return ["AXIS", "RELATIONS"]
    if family in {"movements-swamp"}:
        return ["AXIS", "TERRAIN"]
    return ["AXIS", "MODELS"]


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit("root navigation index: repository-index.json does not exist; build it first")
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = data.get("records", [])
    projected = []
    for record in records:
        row = dict(record)
        row["navigation_path"] = path_for(record)
        row["navigation_branch"] = row["navigation_path"][0]
        projected.append(row)
    projected.sort(key=lambda r: (r["navigation_path"], str(r.get("name", r.get("id", ""))).casefold(), str(r.get("id", ""))))
    counts = {}
    for row in projected:
        key = "/".join(row["navigation_path"])
        counts[key] = counts.get(key, 0) + 1
    OUT.write_text(json.dumps({
        "version": "1.0.0",
        "source": "data/repository-index.json",
        "record_count": len(projected),
        "paths": counts,
        "records": projected,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"root-record-index: {len(projected)} records projected into {len(counts)} navigation paths")


if __name__ == "__main__":
    main()
