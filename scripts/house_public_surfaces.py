#!/usr/bin/env python3
"""Small shared resolver for Potato House public route authority."""
from __future__ import annotations

import json
from pathlib import Path

EXPECTED_PRIMARY_GATEWAY_IDS = ("tim", "religion", "philosophy", "science", "world")


def load_public_surfaces(root: Path) -> dict:
    path = root / "data" / "house" / "public-surfaces.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot load House public-surface authority: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("House public-surface authority must be a JSON object")
    return data


def surface_rows(root: Path, *, active_only: bool = True) -> list[dict]:
    data = load_public_surfaces(root)
    rows = [row for row in data.get("surfaces", []) if isinstance(row, dict) and row.get("id")]
    if active_only:
        rows = [row for row in rows if row.get("status") == "active"]
    return rows


def surface_by_id(root: Path, *, active_only: bool = True) -> dict[str, dict]:
    return {row["id"]: row for row in surface_rows(root, active_only=active_only)}


def surface_route_map(root: Path, *, active_only: bool = True) -> dict[str, str]:
    return {
        row["id"]: row.get("canonical_route") or row.get("route")
        for row in surface_rows(root, active_only=active_only)
        if row.get("canonical_route") or row.get("route")
    }


def primary_gateway_route_map(root: Path) -> dict[str, str]:
    return {row["id"]: row["canonical_route"] for row in primary_gateway_rows(root)}


def secondary_global_route_map(root: Path, *, compatibility_keys: bool = True) -> dict[str, str]:
    data = load_public_surfaces(root)
    routes = surface_route_map(root)
    out: dict[str, str] = {}
    for surface_id in data.get("secondary_global_ids", []):
        if surface_id not in routes:
            raise ValueError(f"secondary global surface is missing or inactive: {surface_id}")
        key = surface_id.replace("-", "_") if compatibility_keys else surface_id
        out[key] = routes[surface_id]
    return out


def visibility_layer(row: dict) -> str:
    visibility = row.get("visibility")
    if visibility in {"primary", "secondary"}:
        return "visible"
    if visibility == "specialist":
        return "semi-visible"
    if visibility == "compatibility":
        return "compatibility"
    return "invisible"



def derived_route_topology_records(root: Path) -> list[dict]:
    """Derive route topology from the one public-surface authority.

    This replaces hand-maintained duplication. Topology is a projection:
    route/type/Rooms come from public-surfaces; primary hub is the nearest
    active ancestor whose surface_type is 'hub'.
    """
    rows = surface_rows(root)
    by_id = {row["id"]: row for row in rows}
    records: list[dict] = []
    for row in rows:
        parent_id = row.get("primary_parent")
        hub_id = None
        seen: set[str] = set()
        while parent_id and parent_id not in seen:
            seen.add(parent_id)
            parent = by_id.get(parent_id)
            if not parent:
                break
            if parent.get("surface_type") == "hub":
                hub_id = parent_id
                break
            parent_id = parent.get("primary_parent")
        if row.get("surface_type") == "hub":
            hub_id = row["id"]
        records.append({
            "surface_id": row["id"],
            "surface_type": row.get("surface_type"),
            "canonical_route": row.get("canonical_route") or row.get("route"),
            "primary_hub_id": hub_id,
            "room_ids": list(row.get("primary_room_ids") or []),
            "specialist_view": row.get("surface_type") not in {"home", "hub"},
            "migration_status": "current" if row.get("status") == "active" else row.get("status"),
            "compatibility_routes": list(row.get("legacy_routes") or []),
        })
    return records


def primary_gateway_rows(root: Path) -> list[dict]:
    data = load_public_surfaces(root)
    ids = tuple(data.get("primary_gateway_ids", []))
    if ids != EXPECTED_PRIMARY_GATEWAY_IDS:
        raise ValueError(f"primary gateway IDs must equal {EXPECTED_PRIMARY_GATEWAY_IDS!r}; got {ids!r}")
    by_id = {
        row.get("id"): row
        for row in data.get("surfaces", [])
        if isinstance(row, dict) and row.get("id")
    }
    rows: list[dict] = []
    for surface_id in ids:
        row = by_id.get(surface_id)
        if not row:
            raise ValueError(f"missing registered primary surface: {surface_id}")
        if not row.get("canonical_route") or not row.get("title"):
            raise ValueError(f"primary surface lacks title/route: {surface_id}")
        if not row.get("primary_navigation") or row.get("status") != "active":
            raise ValueError(f"primary surface is not active primary navigation: {surface_id}")
        rows.append(row)
    return rows
