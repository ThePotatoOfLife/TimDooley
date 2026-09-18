#!/usr/bin/env python3
"""Shared resolver for Potato House public route and navigation authority."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

EXPECTED_PRIMARY_GATEWAY_IDS = ("tim", "religion", "philosophy", "science", "world")
VALID_SHELL_TYPES = {
    "home",
    "editorial",
    "longform",
    "specialist",
    "utility",
    "redirect",
    "diagnostic",
}
VALID_NAVIGATION_GROUPS = {
    "home",
    "door",
    "read",
    "room",
    "discover",
    "specialist",
    "utility",
    "technical",
}


def _normalize_route(route: str) -> str:
    route = (route or "").strip()
    if not route:
        return ""
    if not route.startswith("/"):
        route = "/" + route
    if route != "/" and not route.endswith("/") and "." not in route.rsplit("/", 1)[-1]:
        route += "/"
    return route


def load_public_surfaces(root: Path) -> dict:
    path = root / "data" / "house" / "public-surfaces.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot load House public-surface authority: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("House public-surface authority must be a JSON object")
    return data


def surface_rows(root: Path) -> list[dict]:
    data = load_public_surfaces(root)
    rows = data.get("surfaces", [])
    if not isinstance(rows, list):
        raise ValueError("House public-surface 'surfaces' must be a list")

    seen_ids: set[str] = set()
    seen_routes: set[str] = set()
    normalized: list[dict] = []

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"public surface row {index} must be an object")
        surface_id = str(row.get("id", "")).strip()
        route = _normalize_route(str(row.get("canonical_route") or row.get("route") or ""))
        if not surface_id:
            raise ValueError(f"public surface row {index} lacks id")
        if surface_id in seen_ids:
            raise ValueError(f"duplicate public surface id: {surface_id}")
        if not route:
            raise ValueError(f"public surface {surface_id} lacks canonical route")
        if route in seen_routes:
            raise ValueError(f"duplicate public canonical route: {route}")

        shell_type = row.get("shell_type")
        navigation_group = row.get("navigation_group")
        if shell_type not in VALID_SHELL_TYPES:
            raise ValueError(
                f"public surface {surface_id} has invalid shell_type {shell_type!r}; "
                f"expected one of {sorted(VALID_SHELL_TYPES)!r}"
            )
        if navigation_group not in VALID_NAVIGATION_GROUPS:
            raise ValueError(
                f"public surface {surface_id} has invalid navigation_group {navigation_group!r}; "
                f"expected one of {sorted(VALID_NAVIGATION_GROUPS)!r}"
            )

        copy = dict(row)
        copy["route"] = _normalize_route(str(row.get("route") or route))
        copy["canonical_route"] = route
        normalized.append(copy)
        seen_ids.add(surface_id)
        seen_routes.add(route)

    by_id = {row["id"]: row for row in normalized}
    for row in normalized:
        parent = row.get("primary_parent")
        if parent is not None and parent not in by_id:
            raise ValueError(f"public surface {row['id']} references unknown parent {parent!r}")
        legacy_routes = row.get("legacy_routes", [])
        if not isinstance(legacy_routes, list):
            raise ValueError(f"public surface {row['id']} legacy_routes must be a list")

    return normalized


def surfaces_by_id(root: Path) -> dict[str, dict]:
    return {row["id"]: row for row in surface_rows(root)}


def surface_by_id(root: Path, surface_id: str) -> dict:
    row = surfaces_by_id(root).get(surface_id)
    if not row:
        raise ValueError(f"unknown public surface id: {surface_id}")
    return row


def surface_by_route(root: Path, route: str) -> dict | None:
    wanted = _normalize_route(route)
    for row in surface_rows(root):
        if row["canonical_route"] == wanted or row["route"] == wanted:
            return row
        if wanted in {_normalize_route(value) for value in row.get("legacy_routes", [])}:
            return row
    return None


def primary_gateway_rows(root: Path) -> list[dict]:
    data = load_public_surfaces(root)
    ids = tuple(data.get("primary_gateway_ids", []))
    if ids != EXPECTED_PRIMARY_GATEWAY_IDS:
        raise ValueError(f"primary gateway IDs must equal {EXPECTED_PRIMARY_GATEWAY_IDS!r}; got {ids!r}")
    by_id = surfaces_by_id(root)
    rows: list[dict] = []
    for surface_id in ids:
        row = by_id.get(surface_id)
        if not row:
            raise ValueError(f"missing registered primary surface: {surface_id}")
        if not row.get("canonical_route") or not row.get("title"):
            raise ValueError(f"primary surface lacks title/route: {surface_id}")
        if not row.get("primary_navigation") or row.get("status") != "active":
            raise ValueError(f"primary surface is not active primary navigation: {surface_id}")
        if row.get("navigation_group") != "door":
            raise ValueError(f"primary surface must use navigation_group='door': {surface_id}")
        rows.append(row)
    return rows


def secondary_global_rows(root: Path) -> list[dict]:
    data = load_public_surfaces(root)
    by_id = surfaces_by_id(root)
    rows: list[dict] = []
    for surface_id in data.get("secondary_global_ids", []):
        row = by_id.get(surface_id)
        if not row:
            raise ValueError(f"missing registered secondary global surface: {surface_id}")
        if row.get("status") != "active":
            raise ValueError(f"secondary global surface is not active: {surface_id}")
        rows.append(row)
    return rows


def rows_in_navigation_group(root: Path, navigation_group: str) -> list[dict]:
    if navigation_group not in VALID_NAVIGATION_GROUPS:
        raise ValueError(f"unknown navigation group: {navigation_group}")
    return [
        row
        for row in surface_rows(root)
        if row.get("status") == "active" and row.get("navigation_group") == navigation_group
    ]


def parent_chain(root: Path, surface_id: str) -> list[dict]:
    by_id = surfaces_by_id(root)
    current = by_id.get(surface_id)
    if not current:
        raise ValueError(f"unknown public surface id: {surface_id}")

    chain: list[dict] = []
    seen: set[str] = set()
    while current is not None:
        current_id = current["id"]
        if current_id in seen:
            raise ValueError(f"public surface parent cycle detected at {current_id}")
        seen.add(current_id)
        chain.append(current)
        parent_id = current.get("primary_parent")
        current = by_id.get(parent_id) if parent_id else None

    chain.reverse()
    return chain


def child_rows(root: Path, surface_id: str, *, active_only: bool = True) -> list[dict]:
    rows: Iterable[dict] = surface_rows(root)
    if active_only:
        rows = (row for row in rows if row.get("status") == "active")
    return [row for row in rows if row.get("primary_parent") == surface_id]
