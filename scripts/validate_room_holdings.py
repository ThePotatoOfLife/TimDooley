#!/usr/bin/env python3
"""Validate Room dossier knowledge-holding metadata for basic freshness/integrity."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIERS = ROOT / "data/house/room-dossiers.json"

def main() -> int:
    errors: list[str] = []
    data = json.loads(DOSSIERS.read_text(encoding="utf-8"))
    for room in data.get("dossiers", []):
        room_id = room.get("room_id", "<unknown>")
        holdings = room.get("knowledge_holdings") or {}
        featured = holdings.get("featured") or []
        count = holdings.get("primary_file_count")
        if isinstance(count, int) and count < len(featured):
            errors.append(
                f"{room_id}: primary_file_count={count} is smaller than featured holdings={len(featured)}"
            )
        seen: set[str] = set()
        for row in featured:
            path = str(row.get("path") or "")
            if not path:
                errors.append(f"{room_id}: featured holding missing path")
                continue
            if path in seen:
                errors.append(f"{room_id}: duplicate featured holding path: {path}")
            seen.add(path)
            if not (ROOT / path).is_file():
                errors.append(f"{room_id}: featured holding path does not exist: {path}")

    if errors:
        print("ROOM HOLDINGS VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("Room holdings: PASS · featured paths exist and counts cover featured holdings")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
