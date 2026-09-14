from __future__ import annotations
import json, math, re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import urllib.parse, urllib.request, os

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_INDEX=ROOT/'data'/'countries'/'index.json'
DEFAULT_CAPITALS=ROOT/'data'/'world-capitals.geo.json'
DEFAULT_OUT=ROOT/'data'/'world-cities.geo.json'
WIKIDATA_ENDPOINT='https://query.wikidata.org/sparql'
USER_AGENT='ThePotatoOfLife-world-atlas-cities/1.1'
MAX_FEATURES=5000
MAX_BYTES=5*1024*1024
WIKIDATA_LIMIT=15000
SPARQL=f'''SELECT ?city ?cityLabel ?iso3 ?coord ?population ?populationDate ?adminLabel WHERE {{
  ?city wdt:P31/wdt:P279* wd:Q486972 ; wdt:P17 ?country ; wdt:P625 ?coord ; p:P1082 ?populationStatement .
  ?populationStatement ps:P1082 ?population .
  OPTIONAL {{ ?populationStatement pq:P585 ?populationDate . }}
  OPTIONAL {{ ?city wdt:P131 ?admin . }}
  ?country wdt:P298 ?iso3 .
  FILTER(?population >= 100000)
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} LIMIT {WIKIDATA_LIMIT}'''
POINT_RE=re.compile(r'Point\(([-+0-9.eE]+)\s+([-+0-9.eE]+)\)')


def _slug(value):
    return re.sub(r'[^a-z0-9]+','-',str(value).casefold()).strip('-') or 'city'


def _number(value):
    if isinstance(value,bool): return None
    try: v=float(value)
    except (TypeError,ValueError): return None
    return v if math.isfinite(v) else None


def _load(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def _minimum_zoom(population, capital, scalerank=None):
    rank=_number(scalerank)
    if (population or 0)>=5_000_000 or (capital and rank is not None and rank<=2): return 1,2.4
    if (population or 0)>=1_000_000 or capital: return 2,3.4
    return 3,4.6


def _canonical(index_path, expected_country_count):
    rows=_load(index_path).get('countries',[])
    mapping={str(r.get('iso3') or '').upper():r for r in rows if r.get('iso3')}
    if len(mapping)!=expected_country_count:
        raise RuntimeError(f'Expected {expected_country_count} canonical country identities; found {len(mapping)}')
    return mapping


def _capitals(capitals_path, canonical):
    out=[]
    for feature in _load(capitals_path).get('features',[]):
        p=feature.get('properties') or {}; g=feature.get('geometry') or {}
        iso=str(p.get('iso3') or '').upper(); coords=g.get('coordinates') or []
        if iso not in canonical or g.get('type')!='Point' or len(coords)!=2: continue
        lon,lat=_number(coords[0]),_number(coords[1]); name=str(p.get('name') or '').strip()
        if lon is None or lat is None or not name: continue
        primary=bool(p.get('primary')); tier,minz=_minimum_zoom(None,primary,p.get('scalerank'))
        out.append({'type':'Feature','properties':{
            'id':f'cap:{iso}:{_slug(name)}','name':name,'iso3':iso,'country':p.get('country') or canonical[iso].get('name') or iso,
            'capital':primary,'source':p.get('source') or 'Committed capital snapshot','source_id':f'capital:{iso}:{_slug(name)}',
            'coordinate_source':p.get('source') or 'Committed capital snapshot','tier':tier,'minimum_zoom':minz,
        },'geometry':{'type':'Point','coordinates':[lon,lat]}})
    return out


def _distance(a,b): return math.hypot(float(a[0])-float(b[0]),float(a[1])-float(b[1]))


def _validate_candidates(rows, canonical):
    clean=[]
    for row in rows:
        iso=str(row.get('iso3') or '').upper()
        if iso not in canonical: raise RuntimeError(f'candidate has noncanonical ISO3: {iso}')
        pop=_number(row.get('population'))
        if pop is None or pop<=0: raise RuntimeError(f"candidate has invalid population: {row.get('population')!r}")
        coords=row.get('coordinates') or []
        if len(coords)!=2 or _number(coords[0]) is None or _number(coords[1]) is None: raise RuntimeError('candidate has invalid coordinates')
        name=str(row.get('name') or '').strip(); qid=str(row.get('qid') or '').strip()
        if not name or not qid: raise RuntimeError('candidate missing qid/name')
        clean.append({**row,'iso3':iso,'population':int(round(pop)),'coordinates':[float(coords[0]),float(coords[1])]})
    return clean


def _merge_capital(candidate, capitals):
    normalized=_slug(candidate['name'])
    for feature in capitals:
        p=feature['properties']
        if p.get('iso3')!=candidate['iso3']: continue
        same=_slug(p.get('name'))==normalized
        close=_distance(feature['geometry']['coordinates'],candidate['coordinates'])<=0.15
        if not (same or close): continue
        p.update({'id':f"wd:{candidate['qid']}",'name':candidate['name'],'population':candidate['population'],
                  'population_period':candidate.get('population_period'),'admin_region':candidate.get('admin_region'),
                  'source':f"Wikidata + {p.get('source') or 'capital snapshot'}",'source_id':candidate['qid'],'population_source':'Wikidata'})
        tier,minz=_minimum_zoom(candidate['population'],bool(p.get('capital')))
        p['tier']=tier; p['minimum_zoom']=minz
        return True
    return False


def _parse_point(value):
    m=POINT_RE.fullmatch(str(value or '').strip())
    if not m: return None
    lon,lat=_number(m.group(1)),_number(m.group(2))
    if lon is None or lat is None or not (-180<=lon<=180 and -90<=lat<=90): return None
    return [lon,lat]


def fetch_wikidata_candidates():
    query=urllib.parse.urlencode({'format':'json','query':SPARQL})
    req=urllib.request.Request(f'{WIKIDATA_ENDPOINT}?{query}',headers={'User-Agent':USER_AGENT,'Accept':'application/sparql-results+json'})
    with urllib.request.urlopen(req,timeout=180) as response:
        payload=json.load(response)
    best={}
    for binding in payload.get('results',{}).get('bindings',[]):
        def val(key):
            cell=binding.get(key); return cell.get('value') if isinstance(cell,dict) else None
        uri=str(val('city') or ''); qid=uri.rsplit('/',1)[-1]
        if not re.fullmatch(r'Q\d+',qid): continue
        coords=_parse_point(val('coord')); pop=_number(val('population')); name=str(val('cityLabel') or '').strip(); iso=str(val('iso3') or '').upper()
        if not coords or pop is None or pop<=0 or not name or not iso: continue
        row={'qid':qid,'name':name,'iso3':iso,'coordinates':coords,'population':int(round(pop)),'population_period':str(val('populationDate') or '')[:10] or None,'admin_region':val('adminLabel')}
        old=best.get(qid); old_date=str((old or {}).get('population_period') or ''); new_date=str(row.get('population_period') or '')
        if old is None or new_date>old_date or (new_date==old_date and row['population']>old['population']): best[qid]=row
    return list(best.values())


def build(*, out_path=DEFAULT_OUT, index_path=DEFAULT_INDEX, capitals_path=DEFAULT_CAPITALS, acquisition=fetch_wikidata_candidates, expected_country_count=195):
    canonical=_canonical(index_path,expected_country_count)
    capitals=_capitals(capitals_path,canonical)
    errors=[]
    try:
        acquired=acquisition() or []
    except Exception as exc:
        acquired=[]; errors=[str(exc)]
    candidates=_validate_candidates(acquired,canonical)
    by_country=defaultdict(list)
    for c in candidates:
        if not _merge_capital(c,capitals): by_country[c['iso3']].append(c)
    chosen=set()
    for iso,rows in by_country.items():
        rows.sort(key=lambda r:(-r['population'],r['name'].casefold(),r['qid']))
        chosen.update(r['qid'] for r in rows if r['population']>=500_000)
        chosen.update(r['qid'] for r in rows[:2])
    extras=[]
    for c in candidates:
        if c['qid'] not in chosen or any(f['properties'].get('id')==f"wd:{c['qid']}" for f in capitals): continue
        tier,minz=_minimum_zoom(c['population'],False)
        props={'id':f"wd:{c['qid']}",'name':c['name'],'iso3':c['iso3'],'country':canonical[c['iso3']].get('name') or c['iso3'],
               'population':c['population'],'capital':False,'source':'Wikidata','source_id':c['qid'],'coordinate_source':'Wikidata P625',
               'population_source':'Wikidata P1082','tier':tier,'minimum_zoom':minz}
        if c.get('population_period'): props['population_period']=c['population_period']
        if c.get('admin_region'): props['admin_region']=c['admin_region']
        if c.get('aliases'): props['aliases']=c['aliases']
        extras.append({'type':'Feature','properties':props,'geometry':{'type':'Point','coordinates':c['coordinates']}})
    features=capitals+extras
    features.sort(key=lambda f:(int(f['properties'].get('tier') or 9),f['properties'].get('iso3',''),-int(f['properties'].get('population') or 0),f['properties'].get('name','').casefold()))
    if len(features)>MAX_FEATURES: raise RuntimeError(f'City runtime feature count {len(features)} exceeds {MAX_FEATURES}')
    payload={'type':'FeatureCollection','name':'world-cities','generated_at':datetime.now(timezone.utc).isoformat(),
             'record_type':'world-cities-runtime','scope':'Bounded presentation runtime; capital baseline is committed and external enrichment is acquisition-time only.',
             'acquisition_errors':errors,'features':features}
    text=json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n'
    if len(text.encode())>MAX_BYTES: raise RuntimeError(f'City runtime exceeds {MAX_BYTES} bytes after serialization')
    Path(out_path).write_text(text,encoding='utf-8')
    return payload


def main():
    out=Path(os.environ.get('ATLAS_CITIES_OUT',DEFAULT_OUT))
    payload=build(out_path=out)
    print(json.dumps({'output':str(out),'features':len(payload['features']),'acquisition_errors':payload['acquisition_errors'],'bytes':out.stat().st_size},indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
