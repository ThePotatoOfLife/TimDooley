#!/usr/bin/env python3
"""Build the curated Atlas registry from explicit owner seeds.

Atlas membership is intentionally explicit. This builder does not scan arbitrary
JSON objects and promote them into Nodes. Seeds decide membership/orientation;
canonical owner files retain subject truth.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "data/atlas-owner-seeds.json"
SOURCE_MAP = ROOT / "data/canonical-source-map.json"
REGISTRY = ROOT / "data/atlas-registry.json"

NODE_FIELDS = (
    "id",
    "title",
    "kind",
    "status",
    "owner_path",
    "north_parent",
    "summary",
    "epistemic_classes",
    "relations",
    "archive_refs",
    "views",
    "route",
)

DERIVED_KEYS = {
    "derived_views",
    "related_views",
    "legacy_or_fallback",
    "retired_layers",
    "enrichment",
    "expansion",
    "legacy_or_classification_view",
    "additional_research",
    "country_view",
    "graph_view",
    "research_wave",
    "derived_or_scoped_layers",
    "source_layers",
    "expansion_layers",
    "research_or_extrapolation",
    "deep_research_layer",
    "system_view",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                yield item


def derived_patterns(source_map: dict[str, Any]) -> list[str]:
    patterns: set[str] = set()
    families = source_map.get("families", {})
    if not isinstance(families, dict):
        return []
    for family in families.values():
        if not isinstance(family, dict):
            continue
        for key, value in family.items():
            if key in DERIVED_KEYS:
                patterns.update(strings(value))
    return sorted(patterns)


def is_explicitly_derived(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def normalize_seed(seed: dict[str, Any], patterns: list[str]) -> dict[str, Any]:
    node_id = seed.get("id")
    owner_path = seed.get("owner_path")
    if not isinstance(node_id, str) or not node_id.strip():
        raise ValueError("Atlas owner seed requires a non-empty id")
    if not isinstance(owner_path, str) or not owner_path.strip():
        raise ValueError(f"Atlas owner seed {node_id!r} requires owner_path")
    if is_explicitly_derived(owner_path, patterns):
        raise ValueError(f"Atlas owner seed {node_id!r} points at derived/view layer: {owner_path}")

    owner_file = ROOT / owner_path
    if not owner_file.is_file():
        raise ValueError(f"Atlas owner seed {node_id!r} points at missing owner: {owner_path}")
    owner = load_json(owner_file)
    if not isinstance(owner, dict):
        raise ValueError(f"Atlas owner {owner_path} must be a JSON object")
    if seed.get("status") == "active" and owner.get("canonical") is False:
        raise ValueError(f"Active Atlas seed {node_id!r} points at explicitly non-canonical owner: {owner_path}")

    defaults: dict[str, Any] = {
        "title": str(owner.get("title") or owner.get("name") or node_id),
        "kind": str(owner.get("kind") or "subject"),
        "status": "candidate",
        "north_parent": None,
        "summary": str(owner.get("summary") or owner.get("purpose") or owner.get("description") or ""),
        "epistemic_classes": owner.get("epistemic_classes") if isinstance(owner.get("epistemic_classes"), list) else [],
        "relations": [],
        "archive_refs": [],
        "views": [],
        "route": f"/atlas/{node_id}/",
    }
    node: dict[str, Any] = {"id": node_id}
    for field in NODE_FIELDS[1:]:
        if field == "owner_path":
            node[field] = owner_path
        elif field in seed:
            node[field] = seed[field]
        else:
            node[field] = defaults[field]
    return node


def build_registry() -> dict[str, Any]:
    seeds = load_json(SEEDS)
    source_map = load_json(SOURCE_MAP)
    if not isinstance(seeds, dict):
        raise ValueError("atlas-owner-seeds.json must be a JSON object")
    owners = seeds.get("owners")
    if not isinstance(owners, list):
        raise ValueError("atlas-owner-seeds.json owners must be a list")

    patterns = derived_patterns(source_map if isinstance(source_map, dict) else {})
    nodes = [normalize_seed(seed, patterns) for seed in owners if isinstance(seed, dict)]
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        duplicates = sorted({node_id for node_id in ids if ids.count(node_id) > 1})
        raise ValueError(f"Duplicate Atlas seed IDs: {duplicates}")

    root_id = seeds.get("root_id")
    if not isinstance(root_id, str) or root_id not in set(ids):
        raise ValueError("Atlas seed root_id must resolve to an explicit seed")

    return {
        "version": str(seeds.get("registry_version") or seeds.get("version") or "1.0.0"),
        "root_id": root_id,
        "nodes": nodes,
    }


def write_registry(path: Path = REGISTRY) -> dict[str, Any]:
    registry = build_registry()
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when committed registry differs from generated output")
    args = parser.parse_args()
    generated = build_registry()
    if args.check:
        committed = load_json(REGISTRY)
        if committed != generated:
            print("FAIL: data/atlas-registry.json differs from deterministic seed output")
            return 1
        print(f"ATLAS REGISTRY CHECK PASS: {len(generated['nodes'])} explicit Nodes")
        return 0
    write_registry()
    print(f"ATLAS REGISTRY BUILT: {len(generated['nodes'])} explicit Nodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
