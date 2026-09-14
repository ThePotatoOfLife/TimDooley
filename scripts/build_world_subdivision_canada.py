#!/usr/bin/env python3
"""Build the Canada province/territory partition from Statistics Canada.

Uses the official 2021 Census cartographic boundary ArcGIS REST layer. The
browser consumes the same-origin snapshot; the external API is build-time only.
The layer is queried one province/territory at a time because asking ArcGIS to
transform Canada's full coastline in one request can return HTTP 500.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path(os.environ.get("ATLAS_SUBDIVISIONS_OUT_DIR", ROOT / "data" / "world-subdivisions"))
INDEX_PATH = OUT_DIR / "index.json"
OUT_PATH = OUT_DIR / "CAN.geo.json"
SOURCE_LAYER = "https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer/0"
SOURCE_QUERY = SOURCE_LAYER + "/query"
SOURCE_NAME = "Statistics Canada, 2021 Census Cartographic Boundary Files"
USER_AGENT = "ThePotatoOfLife-world-atlas-subdivision-canada/1.1"
EXPECTED_UNITS = 13

PRUID_TO_POSTAL = {
    "10":"NL", "11":"PE", "12":"NS", "13":"NB", "24":"QC", "35":"ON",
    "46":"MB", "47":"SK", "48":"AB", "59":"BC", "60":"YT", "61":"NT", "62":"NU",
}
TERRITORY_UIDS = {"60", "61", "62"}


def fetch_json(url: str, *, timeout: int = 90, attempts: int = 3) -> dict:
    last_error = None
    for attempt in range(attempts):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8-sig"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Statistics Canada request failed after {attempts} attempts: {last_error}") from last_error


def source_url(pruid: str) -> str:
    query = urllib.parse.urlencode({
        "where": f"PRUID='{pruid}'",
        "outFields": "PRUID,PRNAME,PREABBR,LANDAREA,DGUID",
        "returnGeometry": "true",
        "outSR": "4326",
        "geometryPrecision": "5",
        "f": "geojson",
    })
    return f"{SOURCE_QUERY}?{query}"


def number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None


def normalize_canada(source_features: list[dict]) -> dict:
    features = []
    for source in source_features or []:
        props = source.get("properties") or {}
        geometry = source.get("geometry") or {}
        uid = str(props.get("PRUID") or "").strip()
        postal = PRUID_TO_POSTAL.get(uid)
        name = str(props.get("PRNAME") or "").strip()
        if not uid or not postal or not name or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            continue
        land_area = number(props.get("LANDAREA"))
        normalized = {
            "id": f"CA-{postal}",
            "name": name,
            "code": postal,
            "source_uid": uid,
            "source_abbreviation": props.get("PREABBR"),
            "dguide": props.get("DGUID"),
            "parent_iso3": "CAN",
            "parent_name": "Canada",
            "subdivision_type": "territory" if uid in TERRITORY_UIDS else "province",
            "geometry_source": SOURCE_NAME,
            "geometry_source_url": SOURCE_LAYER,
        }
        if land_area is not None:
            normalized["area_km2"] = round(land_area, 2)
            normalized["area_definition"] = "Statistics Canada LANDAREA attribute; not calculated from presentation geometry"
        features.append({
            "type":"Feature",
            "id":normalized["id"],
            "properties":normalized,
            "geometry":geometry,
        })
    features.sort(key=lambda feature: feature["properties"]["name"])
    ids = [feature["properties"]["id"] for feature in features]
    source_uids = {feature["properties"]["source_uid"] for feature in features}
    if len(features) != EXPECTED_UNITS or len(set(ids)) != EXPECTED_UNITS or source_uids != set(PRUID_TO_POSTAL):
        missing = sorted(set(PRUID_TO_POSTAL) - source_uids)
        raise RuntimeError(f"Canada subdivision coverage must be {EXPECTED_UNITS}; found {len(features)}; missing={missing}")
    return {
        "type":"FeatureCollection",
        "name":"world-subdivisions-CAN",
        "metadata":{
            "version":"1.1.0",
            "generated_at":datetime.now(timezone.utc).isoformat(),
            "parent_iso3":"CAN",
            "feature_count":len(features),
            "scope":"10 Canadian provinces plus 3 territories from Statistics Canada 2021 Census cartographic boundaries.",
            "geometry_vintage":"2021 Census",
            "geometry_source":SOURCE_NAME,
            "geometry_source_url":SOURCE_LAYER,
            "acquisition":"13 province/territory-scoped ArcGIS GeoJSON queries assembled only after complete coverage",
            "population_status":"unknown-not-zero; demographic enrichment pending",
        },
        "features":features,
    }


def search_records(features: list[dict]) -> list[dict]:
    rows = []
    for feature in features:
        props = feature.get("properties") or {}
        rows.append({
            "id":props.get("id"),
            "name":props.get("name"),
            "code":props.get("code"),
            "aliases":[value for value in [props.get("source_abbreviation")] if value],
            "subdivision_type":props.get("subdivision_type"),
            "parent_iso3":"CAN",
            "parent_name":"Canada",
        })
    return rows


def canada_descriptor(features: list[dict]) -> dict:
    return {
        "path":"CAN.geo.json",
        "feature_count":len(features),
        "admin_level":1,
        "status":"implemented-geometry-first",
        "source":SOURCE_NAME,
        "geometry_vintage":"2021 Census",
        "population_status":"unknown-not-zero",
        "id_prefix":"CA-",
        "parent_name":"Canada",
        "viewport_bounds":{"west":-141.1,"east":-52.5,"south":41.6,"north":83.2},
        "search_records":search_records(features),
    }


def build() -> dict:
    source_features = []
    for pruid in PRUID_TO_POSTAL:
        payload = fetch_json(source_url(pruid))
        if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
            raise RuntimeError(f"Statistics Canada province query {pruid} did not return GeoJSON FeatureCollection")
        matches = [
            feature for feature in payload["features"]
            if str((feature.get("properties") or {}).get("PRUID") or "").strip() == pruid
        ]
        if len(matches) != 1:
            raise RuntimeError(f"Statistics Canada province query {pruid} returned {len(matches)} matching features")
        source_features.extend(matches)
    return normalize_canada(source_features)


def write_compact(path: Path, payload: dict) -> int:
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    canada = build()
    size = write_compact(OUT_PATH, canada)
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8")) if INDEX_PATH.exists() else {
        "version":"1.5.0", "record_type":"world-subdivision-partition-index", "partitions":{},
    }
    index["generated_at"] = datetime.now(timezone.utc).isoformat()
    index.setdefault("partitions", {})["CAN"] = canada_descriptor(canada["features"])
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"partition":"CAN","features":len(canada["features"]),"bytes":size,"output":str(OUT_PATH)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
