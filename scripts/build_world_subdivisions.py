#!/usr/bin/env python3
"""Build bounded same-origin subdivision snapshots for the World Map.

Partitions are independent build-time acquisitions. The browser reads only the
same-origin snapshots and the lightweight partition/search index.
"""
from __future__ import annotations

import csv
import io
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path(os.environ.get("ATLAS_SUBDIVISIONS_OUT_DIR", ROOT / "data" / "world-subdivisions"))

CENSUS_KML_ZIP = "https://www2.census.gov/geo/tiger/GENZ2025/kml/cb_2025_us_state_20m.zip"
POPULATION_CSV = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv"
DAWA_REGIONS_GEOJSON = "https://api.dataforsyningen.dk/regioner?format=geojson"
DAWA_SOURCE_NAME = "Danish Agency for Climate Data (DAWA/Dataforsyningen)"
USER_AGENT = "ThePotatoOfLife-world-atlas-subdivisions/1.4"
EXPECTED_US_UNITS = 51
KML_NS = {"k": "http://www.opengis.net/kml/2.2"}

STATE_FIPS_50_DC = {
    "01","02","04","05","06","08","09","10","11","12","13","15","16","17","18","19","20","21","22","23",
    "24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","44",
    "45","46","47","48","49","50","51","53","54","55","56",
}


def fetch_bytes(url: str, timeout: int = 180) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 180) -> str:
    return fetch_bytes(url, timeout=timeout).decode("utf-8-sig")


def fetch_json(url: str, timeout: int = 180) -> dict:
    return json.loads(fetch_text(url, timeout=timeout))


def coordinate_ring(text: str | None) -> list[list[float]]:
    points: list[list[float]] = []
    for token in (text or "").split():
        parts = token.split(",")
        if len(parts) < 2:
            continue
        try:
            points.append([float(parts[0]), float(parts[1])])
        except ValueError:
            continue
    return points


def polygon_coordinates(node: ET.Element) -> list[list[list[float]]]:
    rings: list[list[list[float]]] = []
    outer = node.find("k:outerBoundaryIs/k:LinearRing/k:coordinates", KML_NS)
    ring = coordinate_ring(outer.text if outer is not None else None)
    if ring:
        rings.append(ring)
    for inner in node.findall("k:innerBoundaryIs/k:LinearRing/k:coordinates", KML_NS):
        hole = coordinate_ring(inner.text)
        if hole:
            rings.append(hole)
    return rings


def parse_state_kml(kml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(kml_bytes)
    features: list[dict] = []
    for placemark in root.findall(".//k:Placemark", KML_NS):
        attrs = {
            str(node.get("name") or ""): (node.text or "").strip()
            for node in placemark.findall(".//k:SimpleData", KML_NS)
        }
        fips = attrs.get("STATEFP") or attrs.get("GEOID")
        abbreviation = attrs.get("STUSPS")
        name = attrs.get("NAME")
        if not fips or not abbreviation or not name:
            continue
        polygons = []
        for polygon in placemark.findall(".//k:Polygon", KML_NS):
            rings = polygon_coordinates(polygon)
            if rings:
                polygons.append(rings)
        if not polygons:
            continue
        geometry = (
            {"type": "Polygon", "coordinates": polygons[0]}
            if len(polygons) == 1
            else {"type": "MultiPolygon", "coordinates": polygons}
        )
        features.append({
            "type": "Feature",
            "properties": {
                "STATE": fips,
                "STUSAB": abbreviation,
                "NAME": name,
                "AREALAND": attrs.get("ALAND"),
                "AREAWATER": attrs.get("AWATER"),
            },
            "geometry": geometry,
        })
    return features


def census_state_geojson() -> dict:
    payload = fetch_bytes(CENSUS_KML_ZIP)
    with ZipFile(io.BytesIO(payload)) as archive:
        name = next((entry for entry in archive.namelist() if entry.lower().endswith(".kml")), None)
        if not name:
            raise RuntimeError("Census state boundary archive contains no KML file")
        features = parse_state_kml(archive.read(name))
    if len(features) < EXPECTED_US_UNITS:
        raise RuntimeError(f"Census state KML coverage unexpectedly low: {len(features)}")
    return {"type": "FeatureCollection", "features": features}


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
    properties = {
        "id": f"US-{abbreviation}",
        "name": name,
        "code": abbreviation,
        "fips": fips,
        "parent_iso3": "USA",
        "parent_name": "United States of America",
        "subdivision_type": "federal district" if abbreviation == "DC" else "state",
        "area_km2": total_km2,
        "area_definition": "Census ALAND + AWATER attributes; not calculated from simplified display geometry",
        "population": {
            "value": int(population),
            "unit": "persons",
            "period": 2025,
            "source": "U.S. Census Bureau, Vintage 2025 Population Estimates",
            "source_url": POPULATION_CSV,
        },
        "geometry_source": "U.S. Census Bureau 2025 Cartographic Boundary Files, 1:20,000,000",
        "geometry_source_url": CENSUS_KML_ZIP,
    }
    return {"type": "Feature", "id": properties["id"], "properties": properties, "geometry": feature.get("geometry")}


def subdivision_search_records(features: list[dict], parent_name: str) -> list[dict]:
    records = []
    for feature in features:
        props = feature.get("properties") or {}
        if not props.get("id") or not props.get("name"):
            continue
        records.append({
            "id": props["id"],
            "name": props["name"],
            "code": props.get("code"),
            "subdivision_type": props.get("subdivision_type") or "subdivision",
            "parent_iso3": props.get("parent_iso3"),
            "parent_name": props.get("parent_name") or parent_name,
        })
    return records


def normalize_denmark_regions(payload: dict) -> dict:
    """Normalize DAWA/Dataforsyningen region GeoJSON without inventing missing facts."""
    if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise RuntimeError("Danish region source is not a GeoJSON FeatureCollection")
    features = []
    for source in payload["features"]:
        props = source.get("properties") or {}
        geometry = source.get("geometry") or {}
        code = str(props.get("kode") or props.get("code") or "").strip()
        name = str(props.get("navn") or props.get("name") or "").strip()
        if not code or not name or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            continue
        normalized = {
            "id": f"DK-{code}",
            "name": name,
            "code": code,
            "nuts2": props.get("nuts2"),
            "parent_iso3": "DNK",
            "parent_name": "Denmark",
            "subdivision_type": "region",
            "geometry_source": DAWA_SOURCE_NAME,
            "geometry_source_url": DAWA_REGIONS_GEOJSON,
        }
        if props.get("geo_version") is not None:
            normalized["geometry_version"] = props.get("geo_version")
        features.append({"type": "Feature", "id": normalized["id"], "properties": normalized, "geometry": geometry})
    features.sort(key=lambda item: item["properties"]["name"])
    ids = [feature["properties"]["id"] for feature in features]
    if not features or len(ids) != len(set(ids)):
        raise RuntimeError("Danish region coverage is empty or contains duplicate ids")
    return {
        "type": "FeatureCollection",
        "name": "world-subdivisions-DNK",
        "metadata": {
            "version": "1.4.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "parent_iso3": "DNK",
            "feature_count": len(features),
            "scope": "Current first-order Danish regions returned by the official DAWA/Dataforsyningen region endpoint.",
            "geometry_source": DAWA_SOURCE_NAME,
            "geometry_source_url": DAWA_REGIONS_GEOJSON,
            "population_status": "unknown-not-zero; Statistics Denmark enrichment pending",
        },
        "features": features,
    }


def build_usa() -> dict:
    geometry = census_state_geojson()
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
            "version": "1.4.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "parent_iso3": "USA",
            "feature_count": len(features),
            "scope": "50 U.S. states plus District of Columbia; territories remain separately typed and are not included in this first state partition.",
            "geometry_vintage": "2025",
            "population_vintage": "2025-07-01",
            "geometry_source": "U.S. Census Bureau 2025 Cartographic Boundary Files, 1:20,000,000",
            "population_source": "U.S. Census Bureau Vintage 2025 Population Estimates",
        },
        "features": features,
    }


def build_denmark() -> dict:
    return normalize_denmark_regions(fetch_json(DAWA_REGIONS_GEOJSON))


def write_compact(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    usa = build_usa()
    denmark = build_denmark()
    usa_path = OUT_DIR / "USA.geo.json"
    denmark_path = OUT_DIR / "DNK.geo.json"
    write_compact(usa_path, usa)
    write_compact(denmark_path, denmark)

    index = {
        "version": "1.4.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-subdivision-partition-index",
        "partitions": {
            "USA": {
                "path": "USA.geo.json",
                "feature_count": len(usa["features"]),
                "admin_level": 1,
                "status": "implemented-first-wave",
                "source": "U.S. Census Bureau",
                "geometry_vintage": "2025",
                "population_vintage": "2025-07-01",
                "id_prefix": "US-",
                "parent_name": "United States of America",
                "viewport_bounds": {"west": -179.5, "east": -65, "south": 17, "north": 72.5},
                "search_records": subdivision_search_records(usa["features"], "United States of America"),
            },
            "DNK": {
                "path": "DNK.geo.json",
                "feature_count": len(denmark["features"]),
                "admin_level": 1,
                "status": "implemented-geometry-first",
                "source": DAWA_SOURCE_NAME,
                "population_status": "unknown-not-zero",
                "id_prefix": "DK-",
                "parent_name": "Denmark",
                "viewport_bounds": {"west": 7.5, "east": 15.3, "south": 54.4, "north": 57.9},
                "search_records": subdivision_search_records(denmark["features"], "Denmark"),
            },
        },
    }
    (OUT_DIR / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output_dir": str(OUT_DIR),
        "USA_features": len(usa["features"]),
        "DNK_features": len(denmark["features"]),
        "search_records": sum(len(p["search_records"]) for p in index["partitions"].values()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
