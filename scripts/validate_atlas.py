#!/usr/bin/env python3
"""Validate the relationship-first atlas before deployment.

Checks JSON syntax, backend registry paths, canonical 195-country coverage,
country/enrichment joins, graph endpoints, and local HTML asset references.
This is intentionally structural: it does not judge the truth of research claims.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def load_json(path: Path):
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        ERRORS.append(f"Invalid JSON: {path.relative_to(ROOT)} — {exc}")
        return None


def check_exists(rel: str, required: bool = True):
    path = ROOT / rel
    if not path.exists():
        (ERRORS if required else WARNINGS).append(f"Missing {'required' if required else 'optional'} path: {rel}")
        return False
    return True


def main() -> int:
    backend = load_json(ROOT / "data/backend.json")
    if not isinstance(backend, dict):
        print("ATLAS VALIDATION FAILED")
        return 1

    endpoints = backend.get("endpoints", {})
    required = set(backend.get("required", []))
    for key, value in endpoints.items():
        rel = value if isinstance(value, str) else value.get("path", "") if isinstance(value, dict) else ""
        if not rel:
            ERRORS.append(f"Backend endpoint has no path: {key}")
            continue
        if check_exists(rel, key in required) and rel.endswith(".json"):
            load_json(ROOT / rel)

    nations = load_json(ROOT / "data/nations.json") or {}
    country_index = load_json(ROOT / "data/countries/index.json") or {}
    enrichment_index = load_json(ROOT / "data/country-enrichment-index.json") or {}
    country_nodes = load_json(ROOT / "data/country-nodes.json") or {}
    relationships = load_json(ROOT / "data/relationships.json") or {}
    nodes = load_json(ROOT / "data/nodes.json") or {}
    children = load_json(ROOT / "data/tree-child-records.json") or {}
    tree = load_json(ROOT / "data/tree.json") or {}

    nation_rows = nations.get("nations", [])
    country_rows = country_index.get("countries", [])
    enriched_ids = enrichment_index.get("enriched_ids", [])
    country_node_rows = country_nodes.get("nodes", [])

    if len(nation_rows) != 195:
        ERRORS.append(f"Canonical nation directory has {len(nation_rows)} records; expected 195")
    if len(country_rows) != 195:
        ERRORS.append(f"Country index has {len(country_rows)} records; expected 195")
    nation_ids = {x.get("id") for x in nation_rows}
    country_ids = {x.get("id") for x in country_rows}
    if nation_ids != country_ids:
        ERRORS.append("data/nations.json and data/countries/index.json do not contain the same country IDs")

    for cid in sorted(country_ids):
        if not (ROOT / "data/countries" / f"{cid}.json").exists():
            ERRORS.append(f"Missing canonical country record: data/countries/{cid}.json")

    enriched_set = set(enriched_ids)
    unknown_enriched = enriched_set - country_ids
    if unknown_enriched:
        ERRORS.append(f"Enrichment index contains unknown country IDs: {sorted(unknown_enriched)}")
    node_country_ids = {x.get("country_id") for x in country_node_rows}
    if node_country_ids != enriched_set:
        ERRORS.append("Country graph nodes and enrichment index are out of sync")
    for cid in sorted(enriched_set):
        if not (ROOT / "data/countries" / f"{cid}-enrichment.json").exists():
            ERRORS.append(f"Enrichment index points to missing overlay: {cid}-enrichment.json")

    graph_ids = set()
    graph_ids.update(x.get("id") for x in nodes.get("nodes", []) if x.get("id"))
    graph_ids.update(x.get("id") for x in children.get("records", []) if x.get("id"))
    graph_ids.update(x.get("id") for x in country_node_rows if x.get("id"))
    graph_ids.update(country_ids)
    graph_ids.update(nation_ids)

    tree_ids = set()
    for level in tree.get("levels", []):
        if level.get("id"):
            tree_ids.add(level["id"])
        tree_ids.update(x for x in level.get("children", []) if x)
    missing_tree = sorted(tree_ids - graph_ids)
    WARNINGS.extend(f"Tree references a record not yet promoted into the graph registry: {x}" for x in missing_tree)

    rel_rows = relationships.get("relationships", [])
    for rel in rel_rows:
        if not rel.get("id"):
            ERRORS.append("Relationship without id")
        for side in ("source", "target"):
            endpoint = rel.get(side)
            if endpoint and endpoint not in graph_ids:
                ERRORS.append(f"Relationship {rel.get('id','?')} has unknown {side}: {endpoint}")

    local_ref = re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''', re.I)
    for html in ROOT.glob("*.html"):
        text = html.read_text(encoding="utf-8", errors="replace")
        for ref in local_ref.findall(text):
            if ref.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
                continue
            target = (ROOT / ref).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not target.exists():
                WARNINGS.append(f"Local HTML reference does not exist: {html.name} → {ref}")

    if len(enriched_set) != backend.get("countryLayer", {}).get("enrichedCount", len(enriched_set)):
        ERRORS.append("Backend countryLayer.enrichedCount disagrees with enrichment index")
    if len(country_node_rows) != backend.get("countryLayer", {}).get("nodeCount", len(country_node_rows)):
        ERRORS.append("Backend countryLayer.nodeCount disagrees with country-nodes.json")

    print(f"Canonical nations: {len(nation_rows)}/195")
    print(f"Country base records: {len(country_ids)}/195")
    print(f"Enrichment overlays: {len(enriched_set)}")
    print(f"Country graph nodes: {len(country_node_rows)}")
    print(f"Relationships checked: {len(rel_rows)}")
    print(f"Errors: {len(ERRORS)} · Warnings: {len(WARNINGS)}")
    for message in WARNINGS[:50]:
        print(f"WARNING: {message}")
    for message in ERRORS[:100]:
        print(f"ERROR: {message}")
    if len(ERRORS) > 100:
        print(f"ERROR: … {len(ERRORS)-100} more")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())
