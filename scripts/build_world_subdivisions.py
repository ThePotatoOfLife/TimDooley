#!/usr/bin/env python3
"""Build same-origin subdivision snapshots for the World Map.

The first partition is the United States: 50 states plus the District of Columbia.
Geometry comes from the U.S. Census Bureau TIGERweb 2025 state layer and population
comes from Census Vintage 2025 state estimates. Browser code consumes only the
generated repository/deployment snapshot; Census is a build-time acquisition source.
"""
from __future__ import annotations

import csv
import io
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path(os.environ.get("ATLAS_SUBDIVISIONS_OUT_DIR", ROOT / "data" / "world-subdivisions"))

TIGER_LAYER = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/80/query"
POPULATION_CSV = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv"
USER_AGENT = "ThePotatoOfLife-world-atlas-subdivisions/1.0"
EXPECTED_US_UNITS = 51

# 50 states + District of Columbia. Territories are intentionally excluded from
# this first state layer and can later be represented with their correct types.
STATE_FIPS_50_DC = {
    "01","02","04","05","06","08","09","10","11","12","13","15","16","17","18","19","20","21","22","23",
    "24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","44",
    "45","46","47","48","49","50","51","53","54","55","56",
}


def fetch_text(url: str, timeout: int = 180) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8-sig")


def fetch_json(url: str, timeout: int = 180) -> dict:
    return json.loads(fetch_text(url, timeout=timeout))


def tiger_geojson() -> dict:
    query = urllib.parse.urlencode({
        "where": "1=1",
        "outFields": "STATE,STUSAB,NAME,AREALAND,AREAWATER,CENTLAT,CENTLON",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    })
    payload = fetch_json(f"{TIGER_LAYER}?{query}")
    features = payload.get("features") if isinstance(payload, dict) else None
    if not isinstance(features, list):
        raise RuntimeError("Census TIGERweb state query did not return a GeoJSON FeatureCollection")
    return payload


def census_population_2025() -> dict[str, int]:
    reader = csv.DictReader(io.StringIO(fetch_text(POPULATION_CSV)))
    out: dict[str, int] = {}
    for row in reader:
        fips = str(row.get("STATE") or "").strip().zfill(2)
        if fips not in STATE_FIPS_50_DC:
            continue
        raw = str(row.get("POPESTIMATE2025") or "").replace(",", "").strip()
        try:
            value = int(float(raw))
        except ValueError:
            continue
        if value > 0:
            out[fips] = value
    if len(out) != EXPECTED_US_UNITS:
        missing = sorted(STATE_FIPS_50_DC - set(out))
        raise RuntimeError(f"Census state population coverage must be {EXPECTED_US_UNITS}; found {len(out)}; missing={missing}")
    return out


def square_metres(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def normalize_us_state(feature: dict, population_by_fips: dict[str, int]) -> dict:
    source_props = feature.get("properties") or {}
    fips = str(source_props.get("STATE") or "").zfill(2)
    abbreviation = str(source_props.get("STUSAB") or "").upper()
    name = str(source_props.get("NAME") or "").strip()
    if fips not in STATE_FIPS_50_DC:
        raise ValueError(f"unsupported first-wave U.S. subdivision FIPS: {fips}")
    population = population_by_fips.get(fips)
    if not population:
        raise ValueError(f"missing 2025 population for U.S. subdivision {fips} {name}")

    land_m2 = square_metres(source_props.get("AREALAND"))
    water_m2 = square_metres(source_props.get("AREAWATER"))
    total_km2 = round((land_m2 + water_m2) / 1_000_000, 2)
    centroid = None
    try:
        centroid = [float(source_props.get("CENTLON")), float(source_props.get("CENTLAT"))]
    except (TypeError, ValueError):
        pass

    properties = {
        "id": f"US-{abbreviation}",
        "name": name,
        "code": abbreviation,
        "fips": fips,
        "parent_iso3": "USA",
        "subdivision_type": "federal district" if abbreviation == "DC" else "state",
        "area_km2": total_km2,
        "area_definition": "total area = Census AREALAND + AREAWATER",
        "population": {
            "value": int(population),
            "unit": "persons",
            "period": 2025,
            "source": "U.S. Census Bureau, Vintage 2025 Population Estimates",
            "source_url": POPULATION_CSV,
        },
        "geometry_source": "U.S. Census Bureau TIGERweb States, January 1 2025 vintage",
        "geometry_source_url": TIGER_LAYER.rsplit("/query", 1)[0],
    }
    if centroid:
        properties["centroid"] = centroid

    return {
        "type": "Feature",
        "id": properties["id"],
        "properties": properties,
        "geometry": feature.get("geometry"),
    }


def build_usa() -> dict:
    geometry = tiger_geojson()
    population = census_population_2025()
    features = []
    for feature in geometry.get("features", []):
        fips = str((feature.get("properties") or {}).get("STATE") or "").zfill(2)
        if fips not in STATE_FIPS_50_DC:
            continue
        features.append(normalize_us_state(feature, population))
    features.sort(key=lambda item: item["properties"]["name"])
    if len(features) != EXPECTED_US_UNITS:
        raise RuntimeError(f"Expected {EXPECTED_US_UNITS} U.S. first-wave subdivisions; found {len(features)}")
    ids = [feature["properties"]["id"] for feature in features]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate U.S. subdivision ids detected")
    return {
        "type": "FeatureCollection",
        "name": "world-subdivisions-USA",
        "metadata": {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "parent_iso3": "USA",
            "feature_count": len(features),
            "scope": "50 U.S. states plus District of Columbia; territories remain separately typed and are not included in this first state partition.",
            "geometry_vintage": "2025-01-01",
            "population_vintage": "2025-07-01",
            "geometry_source": "U.S. Census Bureau TIGERweb",
            "population_source": "U.S. Census Bureau Vintage 2025 Population Estimates",
        },
        "features": features,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    usa = build_usa()
    usa_path = OUT_DIR / "USA.geo.json"
    usa_path.write_text(json.dumps(usa, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    index = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-subdivision-partition-index",
        "partitions": {
            "USA": {
                "path": "USA.geo.json",
                "feature_count": EXPECTED_US_UNITS,
                "admin_level": 1,
                "status": "implemented-first-wave",
                "source": "U.S. Census Bureau",
                "geometry_vintage": "2025-01-01",
                "population_vintage": "2025-07-01",
            }
        },
    }
    (OUT_DIR / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(usa_path), "features": EXPECTED_US_UNITS}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
