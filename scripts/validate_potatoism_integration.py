"""Validate the declarative Potatoism integration contract and its live files."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing file: {rel}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON: {rel}: {exc}")
        return None

errors = []
contract = load("data/potatoism-integration.json")
if contract is None:
    raise SystemExit(1)

for rel in contract.get("sources", []):
    load(rel)
for rel in contract.get("graph_targets", []) + contract.get("ui_targets", []):
    if not (ROOT / rel).exists():
        errors.append(f"missing integration target: {rel}")

navigation = contract.get("navigation", {})
for key in ("master_corpus", "deep_corpus", "glossary", "public_observations", "entity_register", "events_relations"):
    rel = navigation.get(key)
    if rel and not (ROOT / rel).exists():
        errors.append(f"missing navigation target: {rel}")
if navigation.get("root") != "potatoism":
    errors.append("navigation root must be potatoism")

entities = load("data/potatoism-entities.json") or {}
entity_ids = [x.get("id") for x in entities.get("entities", [])]
if any(not x for x in entity_ids):
    errors.append("Potatoism entity register contains an entity without an id")
if len(entity_ids) != len(set(entity_ids)):
    errors.append("duplicate Potatoism entity IDs")

atlas = load("data/potatoism-event-and-relation-atlas.json") or {}
relation_types = {x.get("id") for x in atlas.get("relation_types", [])}
entity_set = set(entity_ids)
for triple in atlas.get("canonical_relations", []):
    if not isinstance(triple, list) or len(triple) != 3:
        errors.append(f"malformed canonical relation: {triple!r}")
        continue
    source, relation, target = triple
    if source not in entity_set:
        errors.append(f"unresolved Potatoism relation source: {source}")
    if target not in entity_set:
        errors.append(f"unresolved Potatoism relation target: {target}")
    if relation not in relation_types:
        errors.append(f"undefined Potatoism relation type: {relation}")

observations = load("data/potatoism-public-observations.json") or {}
for index, observation in enumerate(observations.get("observations", [])):
    for field in ("source", "url", "type", "confidence"):
        if not observation.get(field):
            errors.append(f"public observation {index} missing {field}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)

print(
    "Potatoism integration valid: "
    f"{len(contract.get('sources', []))} source files, "
    f"{len(entity_ids)} entities, "
    f"{len(atlas.get('canonical_relations', []))} canonical relations"
)