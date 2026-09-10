#!/usr/bin/env python3
"""Build compact country identity/geography facts for the public atlas.

This is a presentation/runtime snapshot over canonical data/countries records.
It keeps hover/tooltips fast and same-origin without duplicating source ownership.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRIES_DIR = ROOT / "data" / "countries"
OUT = Path(os.environ.get("ATLAS_COUNTRY_FACTS_OUT", ROOT / "data" / "world-country-facts.json"))
EXPECTED = 195


def clean(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def first_number(*values):
    for value in values:
        if value is None or value == "":
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            pass
    return None


def country_facts(index_row: dict) -> dict:
    path = COUNTRIES_DIR / f"{index_row['id']}.json"
    record = {}
    if path.exists():
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            record = {}

    identity = record.get("identity") if isinstance(record.get("identity"), dict) else {}
    geography = record.get("geography") if isinstance(record.get("geography"), dict) else {}

    area = first_number(
        geography.get("land_area_km2"),
        geography.get("area_km2"),
        record.get("area_km2"),
    )

    facts = {
        "name": clean(identity.get("name")) or clean(index_row.get("name")),
        "official_name": clean(identity.get("official_name")),
        "capital": clean(identity.get("capital")),
        "continent": clean(identity.get("continent")),
        "region": clean(identity.get("region")),
        "subregion": clean(identity.get("subregion")),
        "currency": clean(identity.get("currency")),
        "national_day": clean(identity.get("national_day")),
        "area_km2": int(round(area)) if area is not None else None,
        "source_owner": f"data/countries/{index_row['id']}.json",
    }
    return {key: value for key, value in facts.items() if value is not None}


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    countries = index.get("countries", [])
    if len(countries) != EXPECTED:
        raise RuntimeError(f"Expected {EXPECTED} canonical countries; found {len(countries)}")

    rows = {country["iso3"]: country_facts(country) for country in countries}
    capital_coverage = sum(1 for row in rows.values() if row.get("capital"))
    area_coverage = sum(1 for row in rows.values() if row.get("area_km2") is not None)
    region_coverage = sum(1 for row in rows.values() if row.get("region") or row.get("continent"))

    payload = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-country-facts-runtime",
        "scope": "Presentation/runtime snapshot over canonical country records; canonical files remain source owners.",
        "country_count": len(rows),
        "capital_coverage": capital_coverage,
        "area_coverage": area_coverage,
        "region_coverage": region_coverage,
        "countries": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT),
        "countries": len(rows),
        "capital_coverage": capital_coverage,
        "area_coverage": area_coverage,
        "region_coverage": region_coverage,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
