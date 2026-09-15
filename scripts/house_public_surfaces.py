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
