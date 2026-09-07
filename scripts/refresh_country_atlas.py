"""Refresh the machine-readable country layer from the shared blueprint.

This first adapter is intentionally conservative: it creates/updates normalized
World Bank observations for every canonical country and records freshness.
Additional source adapters should write into the same observation model rather
than changing the country schema.
"""
import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'data', 'countries', 'index.json')
OUT = os.path.join(ROOT, 'data', 'countries')
STATE = os.path.join(ROOT, 'data', 'country-refresh-state.json')

INDICATORS = {
    'population': 'SP.POP.TOTL',
    'gdp': 'NY.GDP.MKTP.CD',
    'gdp_per_capita': 'NY.GDP.PCAP.CD',
    'gdp_per_capita_ppp': 'NY.GDP.PCAP.PP.CD',
    'real_growth': 'NY.GDP.MKTP.KD.ZG',
    'inflation': 'FP.CPI.TOTL.ZG',
    'unemployment': 'SL.UEM.TOTL.ZS',
    'labour_force_participation': 'SL.TLF.CACT.ZS',
    'life_expectancy': 'SP.DYN.LE00.IN',
    'fertility': 'SP.DYN.TFRT.IN',
    'urbanization': 'SP.URB.TOTL.IN.ZS',
    'poverty': 'SI.POV.NAHC',
    'co2_emissions': 'EN.ATM.CO2E.PC',
    'internet_penetration': 'IT.NET.USER.ZS'
}

def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'ThePotatoOfLife-country-atlas/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def world_bank(country, indicator):
    url = f"https://api.worldbank.org/v2/country/{urllib.parse.quote(country['iso2'])}/indicator/{indicator}?format=json&per_page=100"
    payload = get_json(url)
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    for row in rows:
        if row.get('value') is not None:
            return {'value': row['value'], 'year': int(row['date']), 'source': 'world-bank', 'indicator': indicator}
    return None

def main():
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    now = datetime.now(timezone.utc).isoformat()
    summary = {'updated_at': now, 'source': 'world-bank', 'countries': 0, 'observations': 0, 'errors': []}
    for country in index['countries']:
        record = {
            'id': country['id'], 'name': country['name'], 'iso2': country['iso2'], 'iso3': country['iso3'],
            'blueprint': 'data/countries-blueprint.json', 'observations': {}, 'relationships': [],
            'data_freshness': {'last_refresh_attempt': now},
            'provenance': {'schema_source': 'data/countries-blueprint.json'}
        }
        for field, indicator in INDICATORS.items():
            try:
                value = world_bank(country, indicator)
                if value:
                    value['retrieved_at'] = now
                    value['confidence'] = 'international-official'
                    record['observations'][field] = value
                    summary['observations'] += 1
            except Exception as exc:
                summary['errors'].append({'country': country['iso2'], 'field': field, 'error': str(exc)})
            time.sleep(0.05)
        record['data_freshness']['source'] = 'world-bank'
        path = os.path.join(OUT, f"{country['id']}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        summary['countries'] += 1
    with open(STATE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
