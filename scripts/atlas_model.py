#!/usr/bin/env python3
"""Derive the runtime Atlas model from the curated orientation registry.

The curated registry owns identity, status, owner path, North parent, views and
canonical route. Everything that can be derived (children, North paths, owner
summary/title/sections and relation resolution) is computed here so it cannot
drift into a second source of truth.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "atlas-registry.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def owner_summary(owner: dict[str, Any], fallback: str) -> str:
    for key in ("summary", "purpose", "description", "definition", "core_thesis"):
        value = owner.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    sections = owner.get("sections")
    if isinstance(sections, dict):
        for section in sections.values():
            if isinstance(section, dict):
                text = section.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
    return fallback.strip()


def owner_sections(owner: dict[str, Any]) -> list[dict[str, Any]]:
    sections = owner.get("sections")
    if not isinstance(sections, dict):
        return []
    out: list[dict[str, Any]] = []
    for key, value in sections.items():
        if not isinstance(value, dict):
            continue
        text = value.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        out.append({
            "id": str(key),
            "title": str(key).replace("_", " ").replace("-", " ").title(),
            "text": text.strip(),
            "epistemic_class": value.get("epistemic_class", []),
            "source_ids": value.get("source_ids", []),
        })
    return out


def normalize_relations(owner: dict[str, Any], routes: dict[str, str]) -> list[dict[str, Any]]:
    raw = owner.get("relationships")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        target = item.get("target")
        if not isinstance(target, str) or not target.strip():
            continue
        target = target.strip()
        out.append({
            "target": target,
            "type": str(item.get("type") or item.get("relationship") or "related"),
            "description": str(item.get("description") or item.get("notes") or "").strip(),
            "epistemic_class": item.get("epistemic_class"),
            "resolved": target in routes,
            "route": routes.get(target),
        })
    return out


def build_model() -> dict[str, Any]:
    registry = load_json(REGISTRY)
    source_nodes = registry.get("nodes", [])
    if not isinstance(source_nodes, list):
        raise ValueError("atlas-registry.json nodes must be a list")

    active = [dict(node) for node in source_nodes if isinstance(node, dict) and node.get("status") == "active"]
    by_id = {str(node["id"]): node for node in active}
    routes = {node_id: str(node.get("route", "")) for node_id, node in by_id.items()}
    root_id = str(registry.get("root_id", ""))

    children: dict[str, list[str]] = {node_id: [] for node_id in by_id}
    for node_id, node in by_id.items():
        parent = node.get("north_parent")
        if isinstance(parent, str) and parent in children:
            children[parent].append(node_id)
    for node_ids in children.values():
        node_ids.sort()

    result_nodes: list[dict[str, Any]] = []
    for node_id, seed in by_id.items():
        owner_path = ROOT / str(seed["owner_path"])
        owner = load_json(owner_path)
        if not isinstance(owner, dict):
            raise ValueError(f"owner is not an object: {seed['owner_path']}")

        north_ids: list[str] = []
        current = node_id
        seen: set[str] = set()
        while current:
            if current in seen:
                raise ValueError(f"North cycle while deriving {node_id}")
            seen.add(current)
            north_ids.append(current)
            if current == root_id:
                break
            parent = by_id[current].get("north_parent")
            if not isinstance(parent, str) or parent not in by_id:
                raise ValueError(f"Broken North path while deriving {node_id}")
            current = parent
        north_ids.reverse()

        title = owner.get("title") or owner.get("name") or seed.get("title") or node_id
        aliases = owner.get("aliases") if isinstance(owner.get("aliases"), list) else []
        epistemic = owner.get("epistemic_classes")
        if not isinstance(epistemic, list):
            epistemic = seed.get("epistemic_classes", [])

        result_nodes.append({
            **seed,
            "title": str(title),
            "aliases": aliases,
            "summary": owner_summary(owner, str(seed.get("summary", ""))),
            "epistemic_classes": epistemic,
            "sections": owner_sections(owner),
            "relations": normalize_relations(owner, routes),
            "children": children[node_id],
            "north_path": north_ids,
            "owner_id": owner.get("id"),
            "owner_title": owner.get("title") or owner.get("name"),
        })

    result_nodes.sort(key=lambda item: item["id"])
    return {
        "schema_version": "1.0.0",
        "root_id": root_id,
        "nodes": result_nodes,
    }


def by_id(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(node["id"]): node for node in model.get("nodes", [])}


if __name__ == "__main__":
    print(json.dumps(build_model(), indent=2, ensure_ascii=False))
