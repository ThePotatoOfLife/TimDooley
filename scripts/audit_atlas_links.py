#!/usr/bin/env python3
"""Verify that Atlas targets resolve across the canonical and research layers."""
from __future__ import annotations
import json
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
graph_registry = ids_from('data/graph-registry.json', ['records'])
political = {x[0] for x in load('data/political-lexicon.json').get('entries', []) if isinstance(x, list) and x}
religious = {x[0] for x in load('data/religious-lexicon.json').get('entries', []) if isinstance(x, list) and x}
foundations = ids_from('data/religious-foundations.json', ['records'])
foundation_records = ids_from('data/religious-foundations/records.json', ['records'])
adjacent = ids_from('data/religious-adjacent/records.json', ['records'])
for path in ('data/religious-adjacent/deep-expansions.json', 'data/religious-adjacent/deep-expansions-2.json', 'data/religious-adjacent/deep-expansions-3.json'):
    adjacent |= ids_from(path, ['records'])
nations = {x['id'] for x in load('data/nations.json').get('nations', []) if x.get('id')}
events = {x['id'] for x in load('data/events.json').get('events', []) if x.get('id')}
sectors = {x['id'] for x in load('data/european-sector-atlas.json').get('sector_families', []) if x.get('id')}
all_records = (nodes | graph_registry | political | religious | foundations | foundation_records |
               adjacent | nations | events | sectors)

rels = load('data/relationships.json').get('relationships', [])
relationship_endpoints = {r.get(side) for r in rels for side in ('source', 'target') if r.get(side)}
addressable = all_records | relationship_endpoints

html = (ROOT / 'repository.html').read_text(encoding='utf-8')
route_templates = ['node.html?id=', 'nation.html?id=']
missing_routes = [route for route in route_templates if route not in html]

tree = load('data/tree.json')
tree_refs = [l.get('id') for l in tree.get('levels', [])]
tree_refs += [c for l in tree.get('levels', []) for c in l.get('children', [])]
tree_missing = sorted(x for x in tree_refs if x and x not in addressable)
reference_only = sorted(relationship_endpoints - all_records)

print(f"Canonical nations: {len(nations)}")
print(f"Dedicated/addressable record IDs: {len(all_records)}")
print(f"Core node records: {len(nodes)}")
print(f"Graph-registry records: {len(graph_registry)}")
print(f"Political records: {len(political)}")
print(f"Religious lexicon records: {len(religious)}")
print(f"Religious foundation layers: {len(foundations | foundation_records)}")
print(f"Religious-adjacent records: {len(adjacent)}")
print(f"Events: {len(events)}")
print(f"Sectors: {len(sectors)}")
print(f"Relationship endpoints: {len(relationship_endpoints)}")
print(f"Reference-only endpoints: {len(reference_only)}")

errors = []
if len(nations) != 195:
    errors.append(f"expected 195 nations, found {len(nations)}")
if missing_routes:
    errors.append("repository.html is missing route templates: " + ', '.join(missing_routes))
if tree_missing:
    errors.append("unresolved tree references: " + ', '.join(tree_missing))

if errors:
    print("\nATLAS LINK AUDIT FAILED")
    for error in errors:
        print("- " + error)
    raise SystemExit(1)

if reference_only:
    print("\nReference-only relationship endpoints remain addressable through node.html and are intentionally tracked for later dedicated research:")
    print("- " + ', '.join(reference_only))

print("\nATLAS LINK AUDIT PASSED")
