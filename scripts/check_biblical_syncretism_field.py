#!/usr/bin/env python3
"""Validate the canonical Biblical Syncretism Field.

This checker protects the registry from becoming another untyped overlap dump.
It validates unique IDs, relation/discovery vocabularies, required provenance fields,
owner paths, and chronological source-direction metadata.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "knowledge/traditions/biblical-syncretism-field.json"

REQUIRED = {"id", "actor", "project_anchor", "discovery_mode", "relation_class", "biblical_refs", "motifs", "strength", "owners"}


def main() -> int:
    errors: list[str] = []
    data = json.loads(FIELD.read_text(encoding="utf-8"))
    rows = data.get("relations")
    if not isinstance(rows, list) or not rows:
        errors.append("relations must be a non-empty list")
        rows = []

    allowed_modes = {x["id"] for x in data.get("discovery_modes", [])}
    allowed_classes = {x["id"] for x in data.get("relation_classes", [])}
    seen: set[str] = set()

    for i, row in enumerate(rows):
        where = f"relations[{i}]"
        missing = sorted(REQUIRED - set(row))
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
        rid = row.get("id")
        if rid in seen:
            errors.append(f"{where}: duplicate id {rid}")
        if rid:
            seen.add(rid)
        if row.get("discovery_mode") not in allowed_modes:
            errors.append(f"{where}: unknown discovery_mode {row.get('discovery_mode')!r}")
        if row.get("relation_class") not in allowed_classes:
            errors.append(f"{where}: unknown relation_class {row.get('relation_class')!r}")
        strength = row.get("strength")
        if not isinstance(strength, int) or not 1 <= strength <= 5:
            errors.append(f"{where}: strength must be integer 1..5")
        if not row.get("biblical_refs"):
            errors.append(f"{where}: biblical_refs cannot be empty")
        if not row.get("owners"):
            errors.append(f"{where}: owners cannot be empty")
        for owner in row.get("owners", []):
            # Library/book names can be provenance pointers rather than repo paths.
            if "/" in owner and not (ROOT / owner).exists():
                errors.append(f"{where}: missing repo owner path {owner}")
        if row.get("relation_class") in {"later-structural-parallel", "research-unlock"} and not row.get("date"):
            errors.append(f"{where}: later/research relation requires a date")

    if errors:
        print("Biblical Syncretism Field: FAIL")
        for e in errors:
            print(" -", e)
        return 1

    print(f"Biblical Syncretism Field: OK — {len(rows)} relations, {len(seen)} unique IDs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
