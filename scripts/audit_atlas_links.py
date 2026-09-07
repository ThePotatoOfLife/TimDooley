#!/usr/bin/env python3
"""Verify that every canonical Atlas target resolves to a real record/data layer."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    with (ROOT / path).open(encoding='utf-8') as f:
        return json.load(f)

def ids_from(path, keys):
    data = load(path)
    out = set()
    for key in keys:
        value = data.get(key, [])
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and item.get('id'):
                    out.add(item['id'])
                elif isinstance(item, list) and item:
                    out.add(item[0])
    return out

nodes = ids_from('data/nodes.json', ['nodes'])
nodes |= ids_from('data/tree-child-records.json', ['records'])
nodes |= ids_from('data/tree-support-records.json', ['records'])
political = {x[0] for x in load('data/political-lexicon.json').get('entries', []) if isinstance(x, list) and x}
religious = {x[0] for x in load('data/religious-lexicon.json').get('entries', []) if isinstance(x, list) and x}
nations = {x['id'] for x in load('data/nations.json').get('nations', []) if x.get('id')}
events = {x['id'] for x in load('data/events.json').get('events', []) if x.get('id')}
sectors = {x['id'] for x in load('data/european-sector-atlas.json').get('sector_families', []) if x.get('id')}
all_records = nodes | political | religious | nations | events | sectors

html = (ROOT / 'repository.html').read_text(encoding='utf-8')
linked = set(re.findall(r'(?:node|nation)\.html\?id=([^"&]+)', html))
# repository.html is JS-generated, so also inspect source datasets used by the page.
missing = sorted(x for x in linked if x not in all_records)

rels = load('data/relationships.json').get('relationships', [])
rel_missing = []
for r in rels:
    for side in ('source', 'target'):
        if r.get(side) and r[side] not in all_records:
            rel_missing.append(f"{r.get('id','relationship')}: {side}={r[side]}")

tree = load('data/tree.json')
tree_refs = [l.get('id') for l in tree.get('levels', [])]
tree_refs += [c for l in tree.get('levels', []) for c in l.get('children', [])]
tree_missing = sorted(x for x in tree_refs if x and x not in all_records)

print(f"Canonical nations: {len(nations)}")
print(f"Record IDs: {len(all_records)}")
print(f"Political records: {len(political)}")
print(f"Religious records: {len(religious)}")
print(f"Events: {len(events)}")
print(f"Sectors: {len(sectors)}")
print(f"Repository literal links checked: {len(linked)}")

errors = []
if len(nations) != 195:
    errors.append(f"expected 195 nations, found {len(nations)}")
if missing:
    errors.append("broken repository links: " + ', '.join(missing))
if rel_missing:
    errors.append("unresolved relationship endpoints: " + '; '.join(rel_missing[:30]))
if tree_missing:
    errors.append("unresolved tree references: " + ', '.join(tree_missing))

# Every generated node.html target must have at least one backing dataset.
for identifier in sorted(political | religious | events | sectors):
    if identifier not in all_records:
        errors.append(f"unbacked generated record: {identifier}")

if errors:
    print("\nATLAS LINK AUDIT FAILED")
    for error in errors:
        print("- " + error)
    raise SystemExit(1)

print("\nATLAS LINK AUDIT PASSED")
