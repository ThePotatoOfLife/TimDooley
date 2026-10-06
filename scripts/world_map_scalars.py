#!/usr/bin/env python3
"""Shared scalar resolution for World Map countries and first-class entities."""
from __future__ import annotations

import math


def _number(value):
    try:
        candidate = float(value)
    except (TypeError, ValueError):
        return None
    return candidate if math.isfinite(candidate) else None


def _period(raw: dict, record: dict):
    return raw.get("year") or raw.get("reference_date") or raw.get("reference_period") or raw.get("period") or record.get("updated")


def _population_cell(raw: dict, record: dict):
    value = _number(raw.get("value"))
    if value is None:
        return None
    unit = str(raw.get("unit") or "persons").strip().lower()
    multiplier = 1
    if unit in {"million", "millions", "million persons", "million people"}:
        multiplier = 1_000_000
    elif unit in {"thousand", "thousands", "thousand persons", "thousand people"}:
        multiplier = 1_000
    elif unit not in {"person", "persons", "people", "population", ""}:
        # Unknown population units should not be guessed.
        return None
    return {
        "value": int(round(value * multiplier)),
        "unit": "persons",
        "period": _period(raw, record),
        "source": raw.get("source") or "canonical record",
        "source_url": raw.get("source_url"),
        "confidence": raw.get("confidence"),
    }


def resolve_population(record: dict, fallback: dict | None = None) -> dict | None:
    observations = record.get("observations") if isinstance(record.get("observations"), dict) else {}
    raw = observations.get("population")
    if isinstance(raw, dict):
        cell = _population_cell(raw, record)
        if cell:
            return cell

    raw = record.get("population")
    if isinstance(raw, dict):
        cell = _population_cell(raw, record)
        if cell:
            return cell
    elif _number(raw) is not None:
        return {
            "value": int(round(float(raw))),
            "unit": "persons",
            "period": record.get("updated"),
            "source": "canonical record",
            "source_url": None,
            "confidence": None,
        }

    if isinstance(fallback, dict):
        cell = _population_cell(fallback, record)
        if cell:
            return cell
    return None


def _area_cell(raw: dict, record: dict, default_definition: str | None = None):
    value = _number(raw.get("value"))
    if value is None:
        return None
    unit = str(raw.get("unit") or "km²").strip().lower()
    if unit not in {"km²", "km2", "sq km", "square kilometres", "square kilometers"}:
        return None
    return {
        "value": value,
        "unit": "km²",
        "definition": raw.get("definition") or default_definition or "area",
        "period": _period(raw, record),
        "source": raw.get("source") or "canonical record",
        "source_url": raw.get("source_url"),
        "confidence": raw.get("confidence"),
    }


def resolve_area(record: dict, fallback: dict | None = None) -> dict | None:
    raw = record.get("area")
    if isinstance(raw, dict):
        cell = _area_cell(raw, record)
        if cell:
            return cell

    geography = record.get("geography") if isinstance(record.get("geography"), dict) else {}
    candidates = (
        (geography.get("land_area_km2"), "land area"),
        (geography.get("area_km2"), "area"),
        (record.get("area_km2"), "area"),
    )
    for value, definition in candidates:
        parsed = _number(value)
        if parsed is not None:
            return {
                "value": parsed,
                "unit": "km²",
                "definition": definition,
                "period": record.get("updated"),
                "source": "canonical record",
                "source_url": None,
                "confidence": None,
            }

    if isinstance(fallback, dict):
        cell = _area_cell(fallback, record, fallback.get("definition") or "area")
        if cell:
            return cell
    return None
