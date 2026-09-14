from __future__ import annotations

import io
import math
import urllib.request
import zipfile

USER_AGENT = 'ThePotatoOfLife-world-atlas-cities/1.2'
GEONAMES_ZIP_URL = 'https://download.geonames.org/export/dump/cities15000.zip'
GEONAMES_MIRROR_URL = 'https://raw.githubusercontent.com/river-jade/cities15000/master/cities15000.txt'
GEONAMES_ADMIN1_URL = 'https://download.geonames.org/export/dump/admin1CodesASCII.txt'


def _number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _fetch_bytes(url, timeout=180):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _cities_text():
    try:
        payload = _fetch_bytes(GEONAMES_ZIP_URL)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            return archive.read('cities15000.txt').decode('utf-8')
    except Exception as primary_error:
        try:
            return _fetch_bytes(GEONAMES_MIRROR_URL).decode('utf-8')
        except Exception as mirror_error:
            raise RuntimeError(f'GeoNames acquisition failed: official={primary_error}; mirror={mirror_error}') from mirror_error


def _admin1_names():
    try:
        text = _fetch_bytes(GEONAMES_ADMIN1_URL).decode('utf-8')
    except Exception as exc:
        print(f'GeoNames admin1 names unavailable; city country context remains usable: {exc}', flush=True)
        return {}
    out = {}
    for line in text.splitlines():
        fields = line.split('\t')
        if len(fields) >= 2 and fields[0] and fields[1]:
            out[fields[0]] = fields[1]
    return out


def _clean_aliases(values, primary=''):
    def key(value):
        return ''.join(ch.lower() for ch in str(value or '') if ch.isalnum())
    seen = {key(primary)} if primary else set()
    out = []
    for value in values or []:
        text = str(value or '').strip()
        normalized = key(text)
        if not text or not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(text)
        if len(out) >= 12:
            break
    return out


def parse_geonames_text(text, canonical, admin1_names=None):
    admin1_names = admin1_names or {}
    iso2_to_iso3 = {
        str(row.get('iso2') or '').upper(): iso3
        for iso3, row in canonical.items()
        if row.get('iso2')
    }
    rows = []
    for line in text.splitlines():
        fields = line.split('\t')
        if len(fields) < 19 or fields[6] != 'P':
            continue
        iso2 = fields[8].upper()
        iso3 = iso2_to_iso3.get(iso2)
        population = _number(fields[14])
        latitude, longitude = _number(fields[4]), _number(fields[5])
        source_id = fields[0].strip()
        name = (fields[2] or fields[1]).strip()
        if not iso3 or population is None or population <= 0 or latitude is None or longitude is None or not source_id or not name:
            continue
        alternate_names = [fields[1], *(fields[3].split(',') if fields[3] else [])]
        admin_key = f'{iso2}.{fields[10]}' if fields[10] else ''
        rows.append({
            'source_key': 'geonames',
            'source_id': source_id,
            'name': name,
            'iso3': iso3,
            'coordinates': [longitude, latitude],
            'population': int(round(population)),
            'aliases': _clean_aliases(alternate_names, name),
            'admin_region': admin1_names.get(admin_key),
            'source': 'GeoNames cities15000',
            'coordinate_source': 'GeoNames latitude/longitude',
            'population_source': 'GeoNames population field',
        })
    return rows


def fetch_geonames_candidates(canonical):
    rows = parse_geonames_text(_cities_text(), canonical, _admin1_names())
    if len(rows) < 10_000:
        raise RuntimeError(f'GeoNames cities15000 coverage unexpectedly low: {len(rows)} rows')
    return rows
