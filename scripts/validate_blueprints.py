#!/usr/bin/env python3
"""Validate the blueprint contract before data expansion gets larger.

Implementation notes:
- Standalone blueprint filenames must end in ``-blueprint.json``.
- The meta-blueprint is the contract for the other blueprint files.
- The registry may contain structural section references; those are not files.
- A blueprint is a specification, not a data dump: it should describe how to
  acquire, normalize, relate and validate records rather than invent values.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_DIR = ROOT / "data" / "blueprints"
REGISTRY = ROOT / "data" / "blueprint-registry.json"
REQUIRED = {"version", "status", "purpose", "entity"}
QUALITY = {"record_schema", "validation_rules", "implementation_notes"}

errors: list[str] = []
files = sorted(BLUEPRINT_DIR.glob("*.json"))
for path in files:
    if path.name == "blueprint-blueprint.json":
        continue
    if not path.name.endswith("-blueprint.json"):
        errors.append(f"non-standard blueprint filename: {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON: {path.relative_to(ROOT)} ({exc})")
        continue
    missing = sorted(REQUIRED - set(data))
    if missing:
        errors.append(f"{path.relative_to(ROOT)} missing metadata: {', '.join(missing)}")
    if not (QUALITY & set(data)):
        errors.append(f"{path.relative_to(ROOT)} has no schema/validation/implementation guidance")

registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
ids = [x.get("id") for x in registry.get("blueprints", []) if isinstance(x, dict)]
seen = set()
for blueprint_id in ids:
    if not blueprint_id:
        errors.append("blueprint registry contains entry without id")
    elif blueprint_id in seen:
        errors.append(f"duplicate blueprint id: {blueprint_id}")
    seen.add(blueprint_id)

for item in registry.get("blueprints", []):
    if not isinstance(item, dict):
        continue
    ref = item.get("file", "")
    if "#" in ref:
        continue
    if ref == "data/countries-blueprint.json":
        continue
    p = ROOT / ref
    if not p.exists():
        errors.append(f"registry points to missing blueprint: {ref}")

print(f"Blueprint files checked: {len(files)}")
print(f"Registry blueprint IDs: {len(ids)}")
if errors:
    print("\nBLUEPRINT VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print("BLUEPRINT VALIDATION PASSED")
