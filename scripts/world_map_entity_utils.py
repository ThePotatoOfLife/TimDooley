#!/usr/bin/env python3
"""Shared geometry helpers for World Map entity anchors."""
from __future__ import annotations

from math import isfinite


def _ring_area(ring):
    area = 0.0
    if not isinstance(ring, list) or len(ring) < 3:
        return 0.0
    for i, point in enumerate(ring):
        nxt = ring[(i + 1) % len(ring)]
        try:
            x1, y1 = float(point[0]), float(point[1])
            x2, y2 = float(nxt[0]), float(nxt[1])
        except (TypeError, ValueError, IndexError):
            continue
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def _polygon_components(feature: dict):
    geometry = (feature or {}).get("geometry") or {}
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates") or []
    if kind == "Polygon":
        return [coordinates]
    if kind == "MultiPolygon":
        return coordinates
    return []


def _polygon_centroid(ring):
    if not isinstance(ring, list) or len(ring) < 3:
        return None
    signed = 0.0
    cx = cy = 0.0
    for i, point in enumerate(ring):
        nxt = ring[(i + 1) % len(ring)]
        try:
            x1, y1 = float(point[0]), float(point[1])
            x2, y2 = float(nxt[0]), float(nxt[1])
        except (TypeError, ValueError, IndexError):
            continue
        cross = x1 * y2 - x2 * y1
        signed += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(signed) < 1e-12:
        return None
    factor = 1.0 / (3.0 * signed)
    result = [cx * factor, cy * factor]
    return result if all(isfinite(v) for v in result) else None


def _point_in_ring(point, ring):
    if not point or not isinstance(ring, list) or len(ring) < 3:
        return False
    x, y = point
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        try:
            xi, yi = float(ring[i][0]), float(ring[i][1])
            xj, yj = float(ring[j][0]), float(ring[j][1])
        except (TypeError, ValueError, IndexError):
            j = i
            continue
        intersects = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside


def representative_component_anchor(feature: dict):
    """Return [lon, lat] from one polygon component, never a global bbox midpoint."""
    components = _polygon_components(feature)
    candidates = []
    for polygon in components:
        outer = polygon[0] if isinstance(polygon, list) and polygon else None
        if isinstance(outer, list) and len(outer) >= 3:
            candidates.append((_ring_area(outer), outer))
    if not candidates:
        return None
    _, ring = max(candidates, key=lambda item: item[0])
    centroid = _polygon_centroid(ring)
    if centroid and _point_in_ring(centroid, ring):
        return [round(centroid[0], 6), round(centroid[1], 6)]
    # Safe fallback stays on the owning polygon rather than averaging distant components.
    point = ring[len(ring) // 2]
    try:
        return [round(float(point[0]), 6), round(float(point[1]), 6)]
    except (TypeError, ValueError, IndexError):
        return None
