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


def _surface_rows_by_id(data: dict) -> dict[str, dict]:
    return {
        str(row.get("id")): row
        for row in data.get("surfaces", [])
        if isinstance(row, dict) and row.get("id")
    }


def primary_gateway_rows(root: Path) -> list[dict]:
    data = load_public_surfaces(root)
    ids = tuple(data.get("primary_gateway_ids", []))
    if ids != EXPECTED_PRIMARY_GATEWAY_IDS:
        raise ValueError(f"primary gateway IDs must equal {EXPECTED_PRIMARY_GATEWAY_IDS!r}; got {ids!r}")
    by_id = _surface_rows_by_id(data)
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


def generated_public_route_roots(root: Path) -> set[str]:
    """Return top-level route roots intentionally generated at build time.

    Public route identity lives in ``data/house/public-surfaces.json``.  Validators
    should consume this resolver instead of maintaining their own generated-route
    allowlists, otherwise source-time audits can disagree about legitimate routes.
    """
    data = load_public_surfaces(root)
    by_id = _surface_rows_by_id(data)
    roots: set[str] = set()
    for surface_id in data.get("generated_surface_ids", []):
        row = by_id.get(str(surface_id))
        if not row:
            raise ValueError(f"missing registered generated surface: {surface_id}")
        route = str(row.get("canonical_route") or "").strip()
        if not route.startswith("/"):
            raise ValueError(f"generated surface lacks canonical route: {surface_id}")
        parts = [part for part in route.strip("/").split("/") if part]
        if not parts:
            raise ValueError(f"generated surface must not resolve to site root: {surface_id}")
        roots.add(parts[0])
    return roots
