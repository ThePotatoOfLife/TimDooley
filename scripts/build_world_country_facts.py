#!/usr/bin/env python3
"""Build compact country identity/geography facts for the public atlas.

Canonical data/countries records remain first priority. Missing display facts are
filled from GeoNames countryInfo at build time so browser hover stays same-origin,
fast, and resilient. The runtime snapshot records field provenance explicitly.
"""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRIES_DIR = ROOT / "data" / "countries"
OUT = Path(os.environ.get("ATLAS_COUNTRY_FACTS_OUT", ROOT / "data" / "world-country-facts.json"))
EXPECTED = 195
GEONAMES_URL = "https://download.geonames.org/export/dump/countryInfo.txt"
USER_AGENT = "ThePotatoOfLife-world-atlas-country-facts/1.1"
CONTINENTS = {
    "AF": "Africa", "AS": "Asia", "EU": "Europe", "NA": "North America",
    "OC": "Oceania", "SA": "South America", "AN": "Antarctica",
}


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


def fetch_geonames() -> dict[str, dict]:
    req = urllib.request.Request(GEONAMES_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as response:
        text = response.read().decode("utf-8-sig")
    rows = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 18:
            continue
        iso3 = clean(parts[1])
        if not iso3 or len(iso3) != 3:
            continue
        area = first_number(parts[6])
        rows[iso3.upper()] = {
            "name": clean(parts[4]),
            "capital": clean(parts[5]),
            "area_km2": int(round(area)) if area is not None else None,
            "continent": CONTINENTS.get(clean(parts[8]) or "", clean(parts[8])),
            "currency": clean(parts[10]),
            "languages": [x for x in (clean(parts[15]) or "").split(",") if x],
            "neighbors": [x for x in (clean(parts[17]) or "").split(",") if x],
        }
    if len(rows) < 190:
        raise RuntimeError(f"GeoNames countryInfo coverage unexpectedly low: {len(rows)}")
    return rows


def country_record(index_row: dict) -> dict:
    path = COUNTRIES_DIR / f"{index_row['id']}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def country_facts(index_row: dict, fallback: dict) -> dict:
    record = country_record(index_row)
    identity = record.get("identity") if isinstance(record.get("identity"), dict) else {}
    geography = record.get("geography") if isinstance(record.get("geography"), dict) else {}
    code = index_row["iso3"]
    external = fallback.get(code, {})

    canonical_area = first_number(
        geography.get("land_area_km2"),
        geography.get("area_km2"),
        record.get("area_km2"),
    )
    canonical_capital = clean(identity.get("capital"))
    canonical_continent = clean(identity.get("continent"))
    canonical_region = clean(identity.get("region"))
    canonical_currency = clean(identity.get("currency"))

    capital = canonical_capital or external.get("capital")
    area = canonical_area if canonical_area is not None else external.get("area_km2")
    continent = canonical_continent or external.get("continent")
    currency = canonical_currency or external.get("currency")

    field_sources = {
        "capital": f"data/countries/{index_row['id']}.json" if canonical_capital else ("GeoNames countryInfo" if capital else None),
        "area_km2": f"data/countries/{index_row['id']}.json" if canonical_area is not None else ("GeoNames countryInfo" if area is not None else None),
        "continent": f"data/countries/{index_row['id']}.json" if canonical_continent else ("GeoNames countryInfo" if continent else None),
        "currency": f"data/countries/{index_row['id']}.json" if canonical_currency else ("GeoNames countryInfo" if currency else None),
    }

    facts = {
        "name": clean(identity.get("name")) or clean(index_row.get("name")) or external.get("name"),
        "official_name": clean(identity.get("official_name")),
        "capital": capital,
        "continent": continent,
        "region": canonical_region,
        "subregion": clean(identity.get("subregion")),
        "currency": currency,
        "national_day": clean(identity.get("national_day")),
        "area_km2": int(round(area)) if area is not None else None,
        "languages": external.get("languages") or None,
        "neighbors": external.get("neighbors") or None,
        "source_owner": f"data/countries/{index_row['id']}.json",
        "fallback_source": "GeoNames countryInfo",
        "fallback_source_url": GEONAMES_URL,
        "field_sources": {key: value for key, value in field_sources.items() if value},
    }
    return {key: value for key, value in facts.items() if value is not None}


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    countries = index.get("countries", [])
    if len(countries) != EXPECTED:
        raise RuntimeError(f"Expected {EXPECTED} canonical countries; found {len(countries)}")

    try:
        geonames = fetch_geonames()
    except Exception as exc:
        print(f"GeoNames fallback unavailable; canonical-only facts will be built: {exc}", flush=True)
        geonames = {}

    rows = {country["iso3"]: country_facts(country, geonames) for country in countries}
    capital_coverage = sum(1 for row in rows.values() if row.get("capital"))
    area_coverage = sum(1 for row in rows.values() if row.get("area_km2") is not None)
    region_coverage = sum(1 for row in rows.values() if row.get("region") or row.get("continent"))
    currency_coverage = sum(1 for row in rows.values() if row.get("currency"))

    if geonames:
        if capital_coverage < 190:
            raise RuntimeError(f"Capital coverage unexpectedly low after GeoNames fallback: {capital_coverage}")
        if area_coverage < 190:
            raise RuntimeError(f"Area coverage unexpectedly low after GeoNames fallback: {area_coverage}")
        if region_coverage < 190:
            raise RuntimeError(f"Region/continent coverage unexpectedly low after GeoNames fallback: {region_coverage}")

    payload = {
        "version": "1.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-country-facts-runtime",
        "scope": "Presentation/runtime snapshot over canonical country records; missing display facts may be filled from GeoNames countryInfo with per-field provenance.",
        "country_count": len(rows),
        "capital_coverage": capital_coverage,
        "area_coverage": area_coverage,
        "region_coverage": region_coverage,
        "currency_coverage": currency_coverage,
        "fallback_source": {"name": "GeoNames countryInfo", "url": GEONAMES_URL},
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
        "currency_coverage": currency_coverage,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
