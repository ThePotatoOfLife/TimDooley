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

from geonames_city_acquisition import fetch_geonames_candidates

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / 'data' / 'countries' / 'index.json'
DEFAULT_CAPITALS = ROOT / 'data' / 'world-capitals.geo.json'
DEFAULT_OUT = ROOT / 'data' / 'world-cities.geo.json'
USER_AGENT = 'ThePotatoOfLife-world-atlas-cities/1.3'
MAX_FEATURES = 5000
MAX_BYTES = 5 * 1024 * 1024

WIKIDATA_ENDPOINT = 'https://query.wikidata.org/sparql'
WIKIDATA_LIMIT = 15000
SPARQL = f'''SELECT ?city ?cityLabel ?iso3 ?coord ?population ?populationDate ?adminLabel WHERE {{
  ?city wdt:P31/wdt:P279* wd:Q486972 ; wdt:P17 ?country ; wdt:P625 ?coord ; p:P1082 ?populationStatement .
  ?populationStatement ps:P1082 ?population .
  OPTIONAL {{ ?populationStatement pq:P585 ?populationDate . }}
  OPTIONAL {{ ?city wdt:P131 ?admin . }}
  ?country wdt:P298 ?iso3 .
  FILTER(?population >= 100000)
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} LIMIT {WIKIDATA_LIMIT}'''
POINT_RE = re.compile(r'Point\(([-+0-9.eE]+)\s+([-+0-9.eE]+)\)')


def _slug(value):
    return re.sub(r'[^a-z0-9]+', '-', str(value).casefold()).strip('-') or 'city'


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _clean_aliases(values, primary=''):
    seen = {_slug(primary)} if primary else set()
    out = []
    for value in values or []:
        text = str(value or '').strip()
        key = _slug(text)
        if not text or not key or key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= 12:
            break
    return out


def _minimum_zoom(population, capital, scalerank=None):
    rank = _number(scalerank)
    if (population or 0) >= 5_000_000 or (capital and rank is not None and rank <= 2):
        return 1, 2.4
    if (population or 0) >= 1_000_000 or capital:
        return 2, 3.4
    return 3, 4.6


def _canonical(index_path, expected_country_count):
    rows = _load(index_path).get('countries', [])
    mapping = {str(row.get('iso3') or '').upper(): row for row in rows if row.get('iso3')}
    if len(mapping) != expected_country_count:
        raise RuntimeError(f'Expected {expected_country_count} canonical country identities; found {len(mapping)}')
    return mapping


def _capitals(capitals_path, canonical):
    out = []
    for feature in _load(capitals_path).get('features', []):
        props = feature.get('properties') or {}
        geometry = feature.get('geometry') or {}
        iso3 = str(props.get('iso3') or '').upper()
        coords = geometry.get('coordinates') or []
        if iso3 not in canonical or geometry.get('type') != 'Point' or len(coords) != 2:
            continue
        lon, lat = _number(coords[0]), _number(coords[1])
        name = str(props.get('name') or '').strip()
        if lon is None or lat is None or not name:
            continue
        primary = bool(props.get('primary'))
        tier, minimum_zoom = _minimum_zoom(None, primary, props.get('scalerank'))
        out.append({
            'type': 'Feature',
            'properties': {
                'id': f'cap:{iso3}:{_slug(name)}',
                'name': name,
                'iso3': iso3,
                'country': props.get('country') or canonical[iso3].get('name') or iso3,
                'capital': primary,
                'source': props.get('source') or 'Committed capital snapshot',
                'source_id': f'capital:{iso3}:{_slug(name)}',
                'coordinate_source': props.get('source') or 'Committed capital snapshot',
                'tier': tier,
                'minimum_zoom': minimum_zoom,
            },
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
        })
    return out


def _distance(a, b):
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def _candidate_identity(row):
    if row.get('source_key') and row.get('source_id') is not None:
        key = str(row['source_key']).strip().lower()
        source_id = str(row['source_id']).strip()
    elif row.get('qid'):
        key, source_id = 'wikidata', str(row['qid']).strip()
    else:
        return None, None, None
    prefix = {'wikidata': 'wd', 'geonames': 'gn'}.get(key, _slug(key)[:8] or 'src')
    return key, source_id, f'{prefix}:{source_id}'


def _validate_candidates(rows, canonical):
    clean = []
    for row in rows:
        iso3 = str(row.get('iso3') or '').upper()
        if iso3 not in canonical:
            raise RuntimeError(f'candidate has noncanonical ISO3: {iso3}')
        population = _number(row.get('population'))
        if population is None or population <= 0:
            raise RuntimeError(f"candidate has invalid population: {row.get('population')!r}")
        coords = row.get('coordinates') or []
        if len(coords) != 2 or _number(coords[0]) is None or _number(coords[1]) is None:
            raise RuntimeError('candidate has invalid coordinates')
        name = str(row.get('name') or '').strip()
        source_key, source_id, stable_id = _candidate_identity(row)
        if not name or not stable_id:
            raise RuntimeError('candidate missing source identity/name')
        clean.append({
            **row,
            'source_key': source_key,
            'source_id': source_id,
            'stable_id': stable_id,
            'iso3': iso3,
            'population': int(round(population)),
            'coordinates': [float(coords[0]), float(coords[1])],
            'aliases': _clean_aliases(row.get('aliases') or [], name),
        })
    return clean


def _merge_capital(candidate, capitals):
    normalized = _slug(candidate['name'])
    alias_keys = {_slug(value) for value in candidate.get('aliases') or []}
    for feature in capitals:
        props = feature['properties']
        if props.get('iso3') != candidate['iso3']:
            continue
        capital_key = _slug(props.get('name'))
        same_name = capital_key == normalized or capital_key in alias_keys
        # Coordinate proximity is only a fallback identity hint for a substantial
        # settlement. It must never let a nearby district/neighborhood overwrite
        # the national-capital identity merely because it is spatially close.
        close = candidate['population'] >= 250_000 and _distance(feature['geometry']['coordinates'], candidate['coordinates']) <= 0.15
        if not (same_name or close):
            continue
        props.update({
            'id': candidate['stable_id'],
            'name': candidate['name'],
            'population': candidate['population'],
            'source': candidate.get('source') or props.get('source') or 'City acquisition source',
            'source_id': candidate['source_id'],
            'coordinate_source': candidate.get('coordinate_source') or props.get('coordinate_source'),
            'population_source': candidate.get('population_source') or candidate.get('source'),
        })
        if candidate.get('population_period'):
            props['population_period'] = candidate['population_period']
        if candidate.get('admin_region'):
            props['admin_region'] = candidate['admin_region']
        if candidate.get('aliases'):
            props['aliases'] = candidate['aliases']
        tier, minimum_zoom = _minimum_zoom(candidate['population'], bool(props.get('capital')))
        props['tier'], props['minimum_zoom'] = tier, minimum_zoom
        return True
    return False


def _parse_point(value):
    match = POINT_RE.fullmatch(str(value or '').strip())
    if not match:
        return None
    lon, lat = _number(match.group(1)), _number(match.group(2))
    if lon is None or lat is None or not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return None
    return [lon, lat]


def fetch_wikidata_candidates():
    query = urllib.parse.urlencode({'format': 'json', 'query': SPARQL})
    request = urllib.request.Request(
        f'{WIKIDATA_ENDPOINT}?{query}',
        headers={'User-Agent': USER_AGENT, 'Accept': 'application/sparql-results+json'},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    best = {}
    for binding in payload.get('results', {}).get('bindings', []):
        def value(key):
            cell = binding.get(key)
            return cell.get('value') if isinstance(cell, dict) else None
        uri = str(value('city') or '')
        qid = uri.rsplit('/', 1)[-1]
        if not re.fullmatch(r'Q\d+', qid):
            continue
        coords = _parse_point(value('coord'))
        population = _number(value('population'))
        name = str(value('cityLabel') or '').strip()
        iso3 = str(value('iso3') or '').upper()
        if not coords or population is None or population <= 0 or not name or not iso3:
            continue
        row = {
            'source_key': 'wikidata',
            'source_id': qid,
            'qid': qid,
            'name': name,
            'iso3': iso3,
            'coordinates': coords,
            'population': int(round(population)),
            'population_period': str(value('populationDate') or '')[:10] or None,
            'admin_region': value('adminLabel'),
            'source': 'Wikidata',
            'coordinate_source': 'Wikidata P625',
            'population_source': 'Wikidata P1082',
        }
        old = best.get(qid)
        old_date = str((old or {}).get('population_period') or '')
        new_date = str(row.get('population_period') or '')
        if old is None or new_date > old_date or (new_date == old_date and row['population'] > old['population']):
            best[qid] = row
    return list(best.values())


def acquire_default_candidates(canonical):
    errors = []
    try:
        return fetch_geonames_candidates(canonical), errors
    except Exception as geonames_error:
        errors.append(str(geonames_error))
    try:
        return fetch_wikidata_candidates(), errors
    except Exception as wikidata_error:
        errors.append(f'Wikidata fallback failed: {wikidata_error}')
    return [], errors


def build(*, out_path=DEFAULT_OUT, index_path=DEFAULT_INDEX, capitals_path=DEFAULT_CAPITALS, acquisition=None, expected_country_count=195):
    canonical = _canonical(index_path, expected_country_count)
    capitals = _capitals(capitals_path, canonical)
    acquisition_errors = []
    if acquisition is None:
        acquired, acquisition_errors = acquire_default_candidates(canonical)
    else:
        try:
            acquired = acquisition() or []
        except Exception as exc:
            acquired = []
            acquisition_errors = [str(exc)]
    candidates = _validate_candidates(acquired, canonical)

    by_country = defaultdict(list)
    merged_ids = set()
    for candidate in candidates:
        if _merge_capital(candidate, capitals):
            merged_ids.add(candidate['stable_id'])
        else:
            by_country[candidate['iso3']].append(candidate)

    chosen_ids = set()
    for rows in by_country.values():
        rows.sort(key=lambda row: (-row['population'], row['name'].casefold(), row['stable_id']))
        chosen_ids.update(row['stable_id'] for row in rows if row['population'] >= 500_000)
        chosen_ids.update(row['stable_id'] for row in rows[:2])

    extras = []
    for candidate in candidates:
        if candidate['stable_id'] in merged_ids or candidate['stable_id'] not in chosen_ids:
            continue
        tier, minimum_zoom = _minimum_zoom(candidate['population'], False)
        props = {
            'id': candidate['stable_id'],
            'name': candidate['name'],
            'iso3': candidate['iso3'],
            'country': canonical[candidate['iso3']].get('name') or candidate['iso3'],
            'population': candidate['population'],
            'capital': False,
            'source': candidate.get('source') or 'City acquisition source',
            'source_id': candidate['source_id'],
            'coordinate_source': candidate.get('coordinate_source') or candidate.get('source'),
            'population_source': candidate.get('population_source') or candidate.get('source'),
            'tier': tier,
            'minimum_zoom': minimum_zoom,
        }
        if candidate.get('population_period'):
            props['population_period'] = candidate['population_period']
        if candidate.get('admin_region'):
            props['admin_region'] = candidate['admin_region']
        if candidate.get('aliases'):
            props['aliases'] = candidate['aliases']
        extras.append({
            'type': 'Feature',
            'properties': props,
            'geometry': {'type': 'Point', 'coordinates': candidate['coordinates']},
        })

    features = capitals + extras
    features.sort(key=lambda feature: (
        int(feature['properties'].get('tier') or 9),
        feature['properties'].get('iso3', ''),
        -int(feature['properties'].get('population') or 0),
        feature['properties'].get('name', '').casefold(),
    ))
    if len(features) > MAX_FEATURES:
        raise RuntimeError(f'City runtime feature count {len(features)} exceeds {MAX_FEATURES}')

    payload = {
        'type': 'FeatureCollection',
        'name': 'world-cities',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'record_type': 'world-cities-runtime',
        'scope': 'Bounded same-origin presentation runtime. Committed capitals are the resilient baseline; GeoNames cities15000 is the primary build-time city source with Wikidata as acquisition fallback.',
        'acquisition_errors': acquisition_errors,
        'features': features,
    }
    text = json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n'
    if len(text.encode('utf-8')) > MAX_BYTES:
        raise RuntimeError(f'City runtime exceeds {MAX_BYTES} bytes after serialization')
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    return payload


def main():
    out = Path(os.environ.get('ATLAS_CITIES_OUT', DEFAULT_OUT))
    payload = build(out_path=out)
    print(json.dumps({
        'output': str(out),
        'features': len(payload['features']),
        'acquisition_errors': payload['acquisition_errors'],
        'bytes': out.stat().st_size,
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
