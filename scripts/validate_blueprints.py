#!/usr/bin/env python3
"""Validate the repository blueprint contract.

Hard failures are reserved for structural problems that can break discovery:
invalid JSON, non-canonical filenames, duplicate registry IDs, missing registry
files, or blueprints with no identifiable schema/domain guidance. Richer metadata
is reported as warnings so legacy blueprints can be upgraded deliberately rather
than blocking the whole site during migration.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_DIR = ROOT / "data" / "blueprints"
REGISTRY = ROOT / "data" / "blueprint-registry.json"

errors: list[str] = []
warnings: list[str] = []
files = sorted(BLUEPRINT_DIR.glob("*.json"))

for path in files:
    if path.name == "blueprint-blueprint.json":
        continue
    rel = str(path.relative_to(ROOT))
    if not path.name.endswith("-blueprint.json"):
        errors.append(f"non-standard blueprint filename: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON: {rel} ({exc})")
        continue
    if not isinstance(data, dict):
        errors.append(f"blueprint must be a JSON object: {rel}")
        continue
    if "version" not in data:
        errors.append(f"{rel} missing metadata: version")
    if "purpose" not in data:
        errors.append(f"{rel} missing metadata: purpose")
    identity_guidance = {"entity", "base_blueprint", "layers", "record_schema"}
    quality_guidance = {"record_schema", "validation_rules", "implementation_notes", "integrity_rules", "layers", "relationship_templates"}
    if not (identity_guidance & set(data)):
        errors.append(f"{rel} has no identifiable domain/schema guidance")
    if not (quality_guidance & set(data)):
        errors.append(f"{rel} has no schema/relationship/validation guidance")
    for key in ("status", "entity", "implementation_notes", "validation_rules", "acquisition_plan"):
        if key not in data:
            warnings.append(f"{rel} should eventually add: {key}")

try:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
except Exception as exc:
    errors.append(f"invalid blueprint registry: {exc}")
    registry = {}

entries = registry.get("blueprints", []) if isinstance(registry, dict) else []
ids = [x.get("id") for x in entries if isinstance(x, dict)]
seen = set()
for blueprint_id in ids:
    if not blueprint_id:
        errors.append("blueprint registry contains entry without id")
    elif blueprint_id in seen:
        errors.append(f"duplicate blueprint id: {blueprint_id}")
    seen.add(blueprint_id)

if isinstance(registry, dict) and registry.get("blueprint_count") != len(ids):
    errors.append(f"registry blueprint_count={registry.get('blueprint_count')} but contains {len(ids)} blueprint IDs")

for item in entries:
    if not isinstance(item, dict):
        continue
    ref = item.get("file", "")
    if "#" in ref:
        continue
    p = ROOT / ref
    if not p.exists():
        errors.append(f"registry points to missing blueprint: {ref}")

print(f"Blueprint files checked: {len(files)}")
print(f"Registry blueprint IDs: {len(ids)}")
print(f"Blueprint contract warnings: {len(warnings)}")
for warning in warnings:
    print(f"- WARNING: {warning}")
if errors:
    print("\nBLUEPRINT VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print("BLUEPRINT VALIDATION PASSED")
