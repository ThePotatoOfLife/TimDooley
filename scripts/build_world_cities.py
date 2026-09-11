#!/usr/bin/env python3
"""Build a bounded, sourced major-city GeoJSON runtime for the World Atlas.

The committed Natural Earth capital snapshot is the resilient baseline. Wikidata
is an acquisition-time enrichment source for large settlements and additional
high-population cities. Browser runtime never depends on live Wikidata. If the
query service is unavailable, capitals still produce a valid city runtime.
"""
from __future__ import annotations

import json
import math
import os
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
CAPITALS = ROOT / "data" / "world-capitals.geo.json"
DEFAULT_OUT = ROOT / "data" / "world-cities.geo.json"
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "ThePotatoOfLife-world-atlas-cities/1.0 (public research map)"
MAX_FEATURES = 5000
MAX_BYTES = 5 * 1024 * 1024
WIKIDATA_CANDIDATE_LIMIT = 15000
WIKIDATA_MIN_POPULATION = 100000
POINT_RE = re.compile(r"Point\(([-+0-9.eE]+)\s+([-+0-9.eE]+)\)")

SPARQL = f"""
SELECT ?city ?cityLabel ?iso3 ?coord ?population ?populationDate ?adminLabel WHERE {{
  ?city wdt:P31/wdt:P279* wd:Q486972 ;
        wdt:P17 ?country ;
        wdt:P625 ?coord ;
        p:P1082 ?populationStatement .
  ?populationStatement ps:P1082 ?population .
  OPTIONAL {{ ?populationStatement pq:P585 ?populationDate . }}
  OPTIONAL {{ ?city wdt:P131 ?admin . }}
  ?country wdt:P298 ?iso3 .
  FILTER(?population >= {WIKIDATA_MIN_POPULATION})
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {WIKIDATA_CANDIDATE_LIMIT}
"""


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "city"


def number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def parse_point(value: str):
    match = POINT_RE.fullmatch(str(value or "").strip())
    if not match:
        return None
    lon, lat = number(match.group(1)), number(match.group(2))
    if lon is None or lat is None or not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return None
    return [lon, lat]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_index() -> tuple[dict[str, dict], set[str]]:
    payload = load_json(INDEX)
    countries = payload.get("countries", [])
    rows = {country["iso3"]: country for country in countries if country.get("iso3")}
    if len(rows) != 195:
        raise RuntimeError(f"Expected 195 canonical country identities; found {len(rows)}")
    return rows, set(rows)


def minimum_zoom(population: float | None, primary_capital: bool, scalerank=None) -> tuple[int, float]:
    rank = number(scalerank)
    if (population or 0) >= 5_000_000 or (primary_capital and rank is not None and rank <= 2):
        return 1, 2.4
    if (population or 0) >= 1_000_000 or primary_capital:
        return 2, 3.4
    return 3, 4.6


def capital_features(canonical: set[str]) -> list[dict]:
    payload = load_json(CAPITALS)
    features = []
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        code = str(props.get("iso3") or "").upper()
        coords = geometry.get("coordinates") or []
        if code not in canonical or geometry.get("type") != "Point" or len(coords) != 2:
            continue
        lon, lat = number(coords[0]), number(coords[1])
        if lon is None or lat is None:
            continue
        name = str(props.get("name") or "").strip()
        if not name:
            continue
        primary = bool(props.get("primary"))
        tier, minzoom = minimum_zoom(None, primary, props.get("scalerank"))
        features.append({
            "type": "Feature",
            "properties": {
                "id": f"cap:{code}:{slug(name)}",
                "name": name,
                "iso3": code,
                "country": props.get("country") or code,
                "capital": primary,
                "source": props.get("source") or "Natural Earth capital snapshot",
                "source_id": f"natural-earth:{code}:{slug(name)}",
                "coordinate_source": props.get("source") or "Natural Earth capital snapshot",
                "tier": tier,
                "minimum_zoom": minzoom,
            },
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
        })
    return features


def fetch_wikidata() -> list[dict]:
    query = urllib.parse.urlencode({"format": "json", "query": SPARQL})
    request = urllib.request.Request(
        f"{WIKIDATA_ENDPOINT}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    return payload.get("results", {}).get("bindings", [])


def binding_value(binding: dict, key: str):
    value = binding.get(key)
    return value.get("value") if isinstance(value, dict) else None


def wikidata_candidates(canonical: set[str]) -> tuple[list[dict], list[str]]:
    try:
        bindings = fetch_wikidata()
    except Exception as exc:
        return [], [str(exc)]

    best: dict[str, dict] = {}
    for binding in bindings:
        uri = str(binding_value(binding, "city") or "")
        qid = uri.rsplit("/", 1)[-1]
        if not re.fullmatch(r"Q\d+", qid):
            continue
        code = str(binding_value(binding, "iso3") or "").upper()
        if code not in canonical:
            continue
        coords = parse_point(binding_value(binding, "coord"))
        population = number(binding_value(binding, "population"))
        name = str(binding_value(binding, "cityLabel") or "").strip()
        if not coords or population is None or population < 0 or not name:
            continue
        date = binding_value(binding, "populationDate")
        candidate = {
            "qid": qid,
            "name": name,
            "iso3": code,
            "coordinates": coords,
            "population": int(round(population)),
            "population_period": str(date)[:10] if date else None,
            "admin_region": binding_value(binding, "adminLabel"),
        }
        old = best.get(qid)
        # Prefer the latest explicitly dated statement; without dates use the
        # numerically largest represented statement as a conservative tie-break.
        old_date = str(old.get("population_period") or "") if old else ""
        new_date = str(candidate.get("population_period") or "")
        if old is None or new_date > old_date or (new_date == old_date and candidate["population"] > old["population"]):
            best[qid] = candidate
    return list(best.values()), []


def coordinate_distance(a, b) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def merge_capital(candidate: dict, capitals: list[dict]) -> dict | None:
    normalized = slug(candidate["name"])
    for capital in capitals:
        props = capital["properties"]
        if props.get("iso3") != candidate["iso3"]:
            continue
        same_name = slug(str(props.get("name") or "")) == normalized
        close = coordinate_distance(capital["geometry"]["coordinates"], candidate["coordinates"]) <= 0.15
        if not (same_name or close):
            continue
        props.update({
            "id": f"wd:{candidate['qid']}",
            "name": candidate["name"],
            "population": candidate["population"],
            "population_period": candidate.get("population_period"),
            "admin_region": candidate.get("admin_region"),
            "source": "Wikidata + " + str(props.get("source") or "Natural Earth capital snapshot"),
            "source_id": candidate["qid"],
            "population_source": "Wikidata",
        })
        tier, minzoom = minimum_zoom(candidate["population"], bool(props.get("capital")))
        props["tier"], props["minimum_zoom"] = tier, minzoom
        return capital
    return None


def choose_features(canonical: set[str]) -> tuple[list[dict], list[str]]:
    capitals = capital_features(canonical)
    candidates, acquisition_errors = wikidata_candidates(canonical)
    by_country: dict[str, list[dict]] = defaultdict(list)
    extras: list[dict] = []

    for candidate in candidates:
        merged = merge_capital(candidate, capitals)
        if merged is not None:
            continue
        by_country[candidate["iso3"]].append(candidate)

    chosen_qids: set[str] = set()
    for code, rows in by_country.items():
        rows.sort(key=lambda row: (-row["population"], row["name"].casefold(), row["qid"]))
        for candidate in rows:
            if candidate["population"] >= 500_000:
                chosen_qids.add(candidate["qid"])
        for candidate in rows[:2]:
            chosen_qids.add(candidate["qid"])

    for candidate in candidates:
        if candidate["qid"] not in chosen_qids:
            continue
        tier, minzoom = minimum_zoom(candidate["population"], False)
        props = {
            "id": f"wd:{candidate['qid']}",
            "name": candidate["name"],
            "iso3": candidate["iso3"],
            "population": candidate["population"],
            "capital": False,
            "source": "Wikidata",
            "source_id": candidate["qid"],
            "coordinate_source": "Wikidata P625",
            "population_source": "Wikidata P1082",
            "tier": tier,
            "minimum_zoom": minzoom,
        }
        if candidate.get("population_period"):
            props["population_period"] = candidate["population_period"]
        if candidate.get("admin_region"):
            props["admin_region"] = candidate["admin_region"]
        extras.append({
            "type": "Feature",
            "properties": props,
            "geometry": {"type": "Point", "coordinates": candidate["coordinates"]},
        })

    features = capitals + extras
    features.sort(key=lambda feature: (
        int(feature["properties"].get("tier") or 9),
        str(feature["properties"].get("iso3") or ""),
        -int(feature["properties"].get("population") or 0),
        str(feature["properties"].get("name") or "").casefold(),
    ))
    return features, acquisition_errors


def validate(features: list[dict], canonical: set[str]) -> None:
    if len(features) > MAX_FEATURES:
        raise RuntimeError(f"City runtime feature count {len(features)} exceeds {MAX_FEATURES}")
    ids: set[str] = set()
    for feature in features:
        props = feature.get("properties") or {}
        city_id = props.get("id")
        if not city_id or city_id in ids:
            raise RuntimeError(f"Missing/duplicate city id: {city_id!r}")
        ids.add(city_id)
        if props.get("iso3") not in canonical:
            raise RuntimeError(f"Unknown city ISO3: {props.get('iso3')}")
        coords = feature.get("geometry", {}).get("coordinates") or []
        if len(coords) != 2 or number(coords[0]) is None or number(coords[1]) is None:
            raise RuntimeError(f"Invalid city coordinates for {city_id}")


def build(out_path: Path | str | None = None) -> dict:
    out = Path(out_path or os.environ.get("ATLAS_CITIES_OUT", DEFAULT_OUT))
    _, canonical = canonical_index()
    features, acquisition_errors = choose_features(canonical)
    validate(features, canonical)
    payload = {
        "type": "FeatureCollection",
        "name": "world-cities",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-cities-runtime",
        "scope": "Bounded presentation runtime. Capital baseline comes from the committed Natural Earth snapshot; Wikidata enriches large/additional settlements when acquisition succeeds.",
        "acquisition_errors": acquisition_errors,
        "features": features,
    }
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    if len(serialized.encode("utf-8")) > MAX_BYTES:
        raise RuntimeError(f"City runtime exceeds {MAX_BYTES} bytes after serialization")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialized, encoding="utf-8")
    return payload


def main() -> int:
    out = Path(os.environ.get("ATLAS_CITIES_OUT", DEFAULT_OUT))
    payload = build(out)
    print(json.dumps({
        "output": str(out),
        "features": len(payload["features"]),
        "wikidata_errors": payload["acquisition_errors"],
        "bytes": out.stat().st_size,
    }, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
