"""Repository-wide lightweight integrity checks."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
json_files = sorted((ROOT / "data").rglob("*.json"))

for path in json_files:
    raw = path.read_text(encoding="utf-8")
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        start = max(0, exc.pos - 100)
        end = min(len(raw), exc.pos + 140)
        context = raw[start:end].replace("\n", "\\n")
        errors.append(f"invalid JSON: {path.relative_to(ROOT)}: {exc}; context={context!r}")
    except Exception as exc:
        errors.append(f"invalid JSON: {path.relative_to(ROOT)}: {exc}")

ids: dict[str, str] = {}
for path in json_files:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    collections = []
    if isinstance(obj, dict):
        for key in ("nodes", "entities", "entries", "records", "events"):
            value = obj.get(key)
            if isinstance(value, list):
                collections.append((key, value))
    for key, rows in collections:
        for row in rows:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            rid = str(row["id"])
            origin = f"{path.relative_to(ROOT)}:{key}"
            if rid in ids and ids[rid] != origin:
                continue
            ids.setdefault(rid, origin)

for path in json_files:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(obj, dict):
        continue
    for key in ("nodes", "entities", "entries", "records", "events"):
        rows = obj.get(key)
        if not isinstance(rows, list):
            continue
        seen: set[str] = set()
        for row in rows:
            if isinstance(row, dict) and row.get("id"):
                rid = str(row["id"])
                if rid in seen:
                    errors.append(f"duplicate id {rid!r} in {path.relative_to(ROOT)}[{key}]")
                seen.add(rid)

contract_path = ROOT / "data/potatoism-integration.json"
master_path = ROOT / "data/potatoism-master-corpus.json"
entity_path = ROOT / "data/potatoism-entities.json"
for required in (contract_path, master_path, entity_path):
    if not required.exists():
        errors.append(f"missing required integration file: {required.relative_to(ROOT)}")

if contract_path.exists():
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    for rel in contract.get("sources", []):
        if not (ROOT / rel).exists():
            errors.append(f"contract source missing: {rel}")
    for rel in contract.get("ui_targets", []):
        if not (ROOT / rel).exists():
            errors.append(f"contract UI target missing: {rel}")

if entity_path.exists():
    entity_data = json.loads(entity_path.read_text(encoding="utf-8"))
    canonical = {str(x.get("id")) for x in entity_data.get("entities", []) if isinstance(x, dict) and x.get("id")}
    relation_path = ROOT / "data/potatoism-event-and-relation-atlas.json"
    if relation_path.exists():
        relation_data = json.loads(relation_path.read_text(encoding="utf-8"))
        for relation in relation_data.get("canonical_relations", []):
            if not isinstance(relation, list) or len(relation) != 3:
                errors.append("malformed canonical Potatoism relation")
                continue
            for endpoint in (relation[0], relation[2]):
                if endpoint not in canonical:
                    errors.append(f"unresolved Potatoism endpoint: {endpoint}")

if errors:
    print("PROJECT INTEGRITY: FAIL")
    print("\n".join(f"- {e}" for e in errors))
    raise SystemExit(1)

print(f"PROJECT INTEGRITY: PASS ({len(json_files)} JSON files parsed)")
