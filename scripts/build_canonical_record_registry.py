#!/usr/bin/env python3
"""Generate a deterministic registry of record-like IDs and their source files."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "canonical-record-registry.json"
SKIP = {"canonical-record-registry.json", "depth-audit-live.json"}

def walk():
    rows = []
    for path in sorted(DATA.rglob("*.json")):
        if path.name in SKIP:
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        stack = [value]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                rid = item.get("id") or item.get("slug") or item.get("key")
                if isinstance(rid, str) and rid.strip():
                    role = item.get("record_role") or item.get("role") or "unclassified"
                    rows.append({"id": rid, "source": str(path.relative_to(ROOT)), "record_role": role})
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    return rows

def main():
    rows = walk()
    by_id = {}
    for row in rows:
        by_id.setdefault(row["id"], []).append({"source": row["source"], "record_role": row["record_role"]})
    duplicates = {rid: sources for rid, sources in by_id.items() if len(sources) > 1}
    result = {
        "version": "1.0.0",
        "updated": "2026-09-08",
        "purpose": "Generated inventory of record-like IDs across data files; it exposes duplicate ownership candidates without deciding canonical ownership automatically.",
        "policy": {"canonical_decisions_live_in": "data/canonical-source-map.json", "duplicates_require_review": True, "generated": True},
        "record_count": len(rows),
        "unique_id_count": len(by_id),
        "duplicate_id_count": len(duplicates),
        "records": [{"id": rid, "occurrences": occurrences} for rid, occurrences in sorted(by_id.items())],
        "duplicate_ids": [{"id": rid, "occurrences": occurrences} for rid, occurrences in sorted(duplicates.items())]
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Indexed {len(rows)} record-like objects across {len(by_id)} IDs; {len(duplicates)} duplicate IDs.")

if __name__ == "__main__":
    main()
