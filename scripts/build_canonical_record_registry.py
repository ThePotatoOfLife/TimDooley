#!/usr/bin/env python3
"""Generate a deterministic inventory of record-like IDs and their source paths.

This is an inventory, not an ownership decision. Canonical ownership remains in
canonical-source-map.json. Discovery intentionally mirrors repository-index.py
so an ID cannot disappear merely because its object uses ``term`` or ``iso3``
instead of ``id``.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "canonical-record-registry.json"
SKIP = {"canonical-record-registry.json", "depth-audit-live.json", "repository-index.json"}
ID_KEYS = ("id", "slug", "key", "term", "iso3", "country_id")
NAME_KEYS = ("name", "display_name", "proper_name", "title", "label", "term")

def scalar(value):
    return value if isinstance(value, (str, int, float, bool)) else ""

def first(item, keys):
    for key in keys:
        value = scalar(item.get(key))
        if str(value).strip():
            return str(value).strip()
    return ""

def walk(value, path, source, rows):
    if isinstance(value, dict):
        rid = first(value, ID_KEYS)
        name = first(value, NAME_KEYS)
        if rid and (name or value.get("type") or value.get("kind") or value.get("category")):
            rows.append({
                "id": rid,
                "name": name or rid,
                "source": source,
                "path": path,
                "record_role": str(value.get("record_role") or value.get("role") or "unclassified"),
            })
        for key, child in value.items():
            walk(child, path + [key], source, rows)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, path + [index], source, rows)

def main():
    rows = []
    json_errors = []
    for path in sorted(DATA.rglob("*.json")):
        if path.name in SKIP:
            continue
        source = path.relative_to(ROOT).as_posix()
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"source": source, "error": f"{type(exc).__name__}: {exc}"})
            continue
        walk(value, [], source, rows)

    by_id = {}
    seen = set()
    for row in rows:
        key = (row["id"], row["source"], json.dumps(row["path"], separators=(",", ":")))
        if key in seen:
            continue
        seen.add(key)
        by_id.setdefault(row["id"], []).append({
            "name": row["name"], "source": row["source"], "path": row["path"], "record_role": row["record_role"]
        })

    duplicates = {rid: occurrences for rid, occurrences in by_id.items() if len(occurrences) > 1}
    result = {
        "version": "2.0.0",
        "updated": "2026-09-08",
        "purpose": "Generated inventory of record-like IDs across data files; it exposes source/path duplication without deciding canonical ownership automatically.",
        "policy": {
            "canonical_decisions_live_in": "data/canonical-source-map.json",
            "duplicates_require_review": True,
            "generated": True,
            "discovery_contract": "Aligned with repository-index.py ID/name heuristics"
        },
        "record_count": len(rows),
        "unique_id_count": len(by_id),
        "duplicate_id_count": len(duplicates),
        "json_error_count": len(json_errors),
        "json_errors": json_errors,
        "records": [{"id": rid, "occurrences": occurrences} for rid, occurrences in sorted(by_id.items())],
        "duplicate_ids": [{"id": rid, "occurrences": occurrences} for rid, occurrences in sorted(duplicates.items())]
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Indexed {len(rows)} record-like objects across {len(by_id)} IDs; {len(duplicates)} duplicate IDs.")

if __name__ == "__main__":
    main()
