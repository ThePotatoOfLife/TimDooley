#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'data' / 'countries' / 'index.json'
RUNTIME = Path(os.environ.get('ATLAS_CITIES_PATH', ROOT / 'data' / 'world-cities.geo.json'))
MAX_FEATURES = 5000
MAX_BYTES = 5 * 1024 * 1024


def main() -> int:
    errors: list[str] = []
    if not RUNTIME.exists():
        print(f'WORLD CITY VALIDATION SKIPPED: {RUNTIME} not generated yet; Places falls back to committed capitals.')
        return 0
    if RUNTIME.stat().st_size > MAX_BYTES:
        errors.append(f'city runtime exceeds {MAX_BYTES} bytes: {RUNTIME.stat().st_size}')
    try:
        payload = json.loads(RUNTIME.read_text(encoding='utf-8'))
        index = json.loads(INDEX.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'ERROR: invalid city/index JSON: {exc}')
        return 1

    if payload.get('type') != 'FeatureCollection':
        errors.append(f"city runtime type must be FeatureCollection, got {payload.get('type')!r}")
    features = payload.get('features') or []
    if len(features) > MAX_FEATURES:
        errors.append(f'city runtime has {len(features)} features; limit is {MAX_FEATURES}')
    canonical = {row['iso3'] for row in index.get('countries', []) if row.get('iso3')}
    ids: set[str] = set()

    for feature in features:
        props = feature.get('properties') or {}
        geometry = feature.get('geometry') or {}
        city_id = str(props.get('id') or '')
        if not city_id:
            errors.append('city feature missing stable id')
        elif city_id in ids:
            errors.append(f'duplicate city id: {city_id}')
        ids.add(city_id)
        if props.get('iso3') not in canonical:
            errors.append(f"city {city_id or props.get('name')} has noncanonical ISO3: {props.get('iso3')}")
        for key in ('name', 'source', 'coordinate_source'):
            if not props.get(key):
                errors.append(f'city {city_id or "?"} missing {key}')
        if props.get('minimum_zoom') is None:
            errors.append(f'city {city_id or "?"} missing minimum_zoom')
        if geometry.get('type') != 'Point':
            errors.append(f'city {city_id or "?"} geometry must be Point')
            continue
        coords = geometry.get('coordinates') or []
        if len(coords) != 2:
            errors.append(f'city {city_id or "?"} invalid coordinates: {coords!r}')
            continue
        lon, lat = coords
        if not all(isinstance(v, (int, float)) and math.isfinite(float(v)) for v in (lon, lat)):
            errors.append(f'city {city_id or "?"} non-finite coordinates: {coords!r}')
        elif not (-180 <= lon <= 180 and -90 <= lat <= 90):
            errors.append(f'city {city_id or "?"} coordinates out of bounds: {coords!r}')
        population = props.get('population')
        if population is not None and (isinstance(population, bool) or not isinstance(population, (int, float)) or population <= 0):
            errors.append(f'city {city_id or "?"} invalid population: {population!r}')

    if errors:
        print('WORLD CITY VALIDATION FAILED')
        for error in errors:
            print('-', error)
        return 1
    print(f'WORLD CITY VALIDATION PASSED: {len(features)} features · {RUNTIME.stat().st_size} bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
