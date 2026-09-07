"""Refresh the static country atlas from authoritative international data.

External APIs are acquisition inputs only. The website consumes the generated
repository snapshot and never depends on a live API at page-load time.
"""
import json, os, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'data', 'countries', 'index.json')
OUT = os.path.join(ROOT, 'data', 'countries')
STATIC = os.path.join(ROOT, 'data', 'country-static.json')
STATE = os.path.join(ROOT, 'data', 'country-refresh-state.json')

INDICATORS = {
    'population': 'SP.POP.TOTL', 'gdp': 'NY.GDP.MKTP.CD', 'gdp_per_capita': 'NY.GDP.PCAP.CD',
    'gdp_per_capita_ppp': 'NY.GDP.PCAP.PP.CD', 'real_growth': 'NY.GDP.MKTP.KD.ZG',
    'inflation': 'FP.CPI.TOTL.ZG', 'unemployment': 'SL.UEM.TOTL.ZS',
    'labour_force_participation': 'SL.TLF.CACT.ZS', 'life_expectancy': 'SP.DYN.LE00.IN',
    'fertility': 'SP.DYN.TFRT.IN', 'urbanization': 'SP.URB.TOTL.IN.ZS', 'poverty': 'SI.POV.NAHC',
    'co2_emissions': 'EN.ATM.CO2E.PC', 'internet_penetration': 'IT.NET.USER.ZS'
}

# A small number of bulk multi-indicator calls is much more reliable on CI than
# opening fourteen large all-country connections concurrently.
INDICATOR_GROUPS = [
    ['population', 'gdp', 'gdp_per_capita', 'gdp_per_capita_ppp', 'real_growth'],
    ['inflation', 'unemployment', 'labour_force_participation', 'life_expectancy', 'fertility'],
    ['urbanization', 'poverty', 'co2_emissions', 'internet_penetration']
]


def get_json(url, timeout=180):
    req = urllib.request.Request(url, headers={'User-Agent': 'ThePotatoOfLife-country-atlas/2.1'})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def world_bank_group(fields):
    codes = ';'.join(INDICATORS[field] for field in fields)
    url = 'https://api.worldbank.org/v2/country/all/indicator/' + urllib.parse.quote(codes, safe=';') + '?format=json&per_page=10000&mrv=5'
    payload = get_json(url)
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    result = {field: {} for field in fields}
    code_to_field = {INDICATORS[field]: field for field in fields}
    for row in rows:
        indicator = row.get('indicator', {}).get('id')
        field = code_to_field.get(indicator)
        iso3 = str(row.get('countryiso3code') or '').upper()
        if not field or not iso3 or row.get('value') is None:
            continue
        year = str(row.get('date') or '')
        current = result[field].get(iso3)
        if current is None or year > str(current.get('year') or ''):
            result[field][iso3] = {
                'value': row['value'],
                'year': int(year) if year.isdigit() else year,
                'source': 'world-bank',
                'indicator': indicator
            }
    return result


def load_existing(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def compact_record(record, directory_entry, enrichment):
    observations = record.get('observations') or {}
    identity = record.get('identity') or {}
    coverage = record.get('coverage') or {}
    enriched = {}
    for key, value in (enrichment or {}).items():
        if key in {'country_id', 'iso2', 'iso3', 'blueprint', 'updated', 'provenance'}:
            continue
        if value not in (None, '', [], {}):
            enriched[key] = value
    return {
        'id': identity.get('id') or directory_entry['id'], 'name': identity.get('name') or directory_entry['name'],
        'status': directory_entry.get('status'), 'iso2': identity.get('iso2') or directory_entry.get('iso2'),
        'iso3': identity.get('iso3') or directory_entry.get('iso3'), 'capital': directory_entry.get('capital'),
        'region': directory_entry.get('region'), 'subregion': directory_entry.get('subregion'),
        'profile_url': directory_entry.get('profile_url'), 'record_status': record.get('status'),
        'coverage': coverage, 'observations': observations, 'relationships': record.get('relationships') or [],
        'history': record.get('history') or [], 'research_queue': record.get('research_queue') or [],
        'provenance': record.get('provenance') or {}, 'enrichment': enriched
    }


def write_static_atlas(index, now):
    countries = []
    for directory_entry in index['countries']:
        record = load_existing(os.path.join(OUT, f"{directory_entry['id']}.json"))
        enrichment = load_existing(os.path.join(OUT, f"{directory_entry['id']}-enrichment.json"))
        countries.append(compact_record(record, directory_entry, enrichment))
    payload = {
        'version': '2.1.0',
        'generated_at': now,
        'source_policy': 'Repository snapshot. External APIs are used only by the scheduled acquisition workflow, never by the browser.',
        'canonical_count': len(countries),
        'countries': countries
    }
    with open(STATIC, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
    return len(countries)


def main():
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    now = datetime.now(timezone.utc).isoformat()
    canonical_count = len(index['countries'])
    summary = {
        'updated_at': now, 'source': 'world-bank', 'countries': 0, 'observations': 0,
        'errors': [], 'preserved_records': 0, 'bulk_indicator_requests': 0,
        'static_snapshot': STATIC, 'canonical_count_from_index': canonical_count
    }

    if canonical_count != 195:
        summary['errors'].append({
            'type': 'canonical-index-count',
            'expected': 195,
            'actual': canonical_count,
            'message': 'Canonical country index must contain 193 UN members plus Holy See and State of Palestine.'
        })

    by_field = {field: {} for field in INDICATORS}
    for group in INDICATOR_GROUPS:
        try:
            result = world_bank_group(group)
            for field, values in result.items():
                by_field[field].update(values)
            summary['bulk_indicator_requests'] += 1
        except Exception as exc:
            summary['errors'].append({'indicator_group': [INDICATORS[f] for f in group], 'error': str(exc)})

    for country in index['countries']:
        path = os.path.join(OUT, f"{country['id']}.json")
        record = load_existing(path)
        record.setdefault('record_type', 'country')
        record.setdefault('status', 'instantiated')
        record.setdefault('identity', {})
        record['identity'].update({'id': country['id'], 'name': country['name'], 'iso2': country['iso2'], 'iso3': country['iso3']})
        record.setdefault('blueprint', 'data/countries-blueprint.json')
        record.setdefault('observations', {})
        record.setdefault('relationships', [])
        record.setdefault('history', [])
        record.setdefault('provenance', {})
        record.setdefault('data_freshness', {})
        previous = dict(record['observations'])
        for field in INDICATORS:
            value = by_field.get(field, {}).get(str(country['iso3']).upper())
            if not value:
                continue
            value = dict(value)
            value['retrieved_at'] = now
            value['confidence'] = 'international-official'
            old = record['observations'].get(field)
            if old and isinstance(old, dict) and old.get('value') != value.get('value'):
                record['history'].append({'field': field, 'previous': old, 'replaced_at': now, 'reason': 'new source observation'})
            record['observations'][field] = value
            summary['observations'] += 1
        record['coverage'] = record.get('coverage', {})
        record['coverage'].update({
            'observations': len(record['observations']),
            'relationships': len(record['relationships']),
            'sources': max(record['coverage'].get('sources', 0), 1 if record['observations'] else 0)
        })
        record['data_freshness'].update({'last_refresh_attempt': now, 'source': 'world-bank'})
        record['provenance']['last_refresh'] = now
        record['provenance']['source_priority'] = 'international-official'
        record['provenance']['historical_observations_preserved'] = True
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        summary['countries'] += 1
        if previous or record.get('research_queue'):
            summary['preserved_records'] += 1

    summary['static_countries'] = write_static_atlas(index, now)
    with open(STATE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
