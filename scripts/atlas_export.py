#!/usr/bin/env python3
"""Create a compact public machine projection from the derived Atlas runtime.

This export is never a source of truth. It intentionally omits canonical owner
paths and reader blocks; those remain in repository owners and are re-derived on
build. The public index exists for search, discovery and future UI projections.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def public_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "target": row.get("target"),
        "type": row.get("canonical_type") or row.get("type") or "related",
        "source_type": row.get("type"),
        "label": row.get("label"),
        "orientation": row.get("orientation"),
        "resolved": bool(row.get("resolved")),
        "route": row.get("route"),
        "provisional": bool(row.get("provisional_type")),
    }


def public_artifact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "kind": row.get("kind"),
        "public_route": row.get("public_route"),
        "date_or_period": row.get("date_or_period"),
        "summary": row.get("summary"),
        "epistemic_classes": row.get("epistemic_classes", []),
    }


def public_node(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node.get("id"),
        "title": node.get("title"),
        "kind": node.get("kind"),
        "route": node.get("route"),
        "summary": node.get("summary"),
        "north_parent": node.get("north_parent"),
        "north_path": node.get("north_path", []),
        "children": node.get("children", []),
        "views": node.get("views", []),
        "epistemic_classes": node.get("epistemic_classes", []),
        "relations": [public_relation(row) for row in node.get("relations", []) if isinstance(row, dict)],
        "artifacts": [public_artifact(row) for row in node.get("artifacts", []) if isinstance(row, dict)],
    }


def build_public_index(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "authoritative": False,
        "authority_note": "Derived build projection. Canonical ownership remains in repository source records and curated Atlas registries.",
        "root_id": model.get("root_id"),
        "nodes": [public_node(node) for node in model.get("nodes", []) if isinstance(node, dict)],
        "views": [
            {
                "id": view.get("id"),
                "title": view.get("title"),
                "route": view.get("route"),
                "description": view.get("description"),
                "status": view.get("status"),
            }
            for view in model.get("views", [])
            if isinstance(view, dict)
        ],
    }


def write_public_index(model: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_public_index(model), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
