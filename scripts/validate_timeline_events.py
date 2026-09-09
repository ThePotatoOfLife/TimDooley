#!/usr/bin/env python3
"""Validate the layered timeline base plus optional curated event packs."""
from __future__ import annotations
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data'/'timeline-events.json'
PACK_INDEX=ROOT/'data'/'timeline-event-packs'/'index.json'
PRECISION={'second','minute','hour','date','month','year','range'}
BIBLE_RELATIONS={
    'explicit-at-time',
    'explicit-context-at-time',
    'explicit-symbolic-at-time',
    'explicit-Christian-vocabulary-at-time',
    'later-parallel',
    'mixed-explicit-and-later',
    'mixed-explicit-scriptural-vocabulary',
}


def fail(msg,errors):
    errors.append(msg)


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def valid_http_url(value: str) -> bool:
    return bool(re.match(r'^https?://', value or '', flags=re.I))


def parse_iso_timestamp(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:
        return None


def load_events(data, errors):
    combined=[('base', e) for e in data.get('events',[])]
    if not PACK_INDEX.exists():
        return combined
    try:
        idx=load_json(PACK_INDEX)
    except Exception as exc:
        fail(f'cannot parse {PACK_INDEX}: {exc}',errors)
        return combined

    packs=idx.get('packs',[])
    if len(packs)!=len(set(packs)):
        fail(f'{PACK_INDEX}: duplicate pack filename(s)',errors)

    for name in packs:
        if not isinstance(name,str) or not name.endswith('.json') or '/' in name or '\\' in name or '..' in name:
            fail(f'{PACK_INDEX}: unsafe/invalid pack name {name!r}',errors)
            continue
        path=PACK_INDEX.parent/name
        try:
            pack=load_json(path)
        except Exception as exc:
            fail(f'cannot parse pack {path}: {exc}',errors)
            continue
        if not isinstance(pack.get('events',[]),list):
            fail(f'{path}: events must be a list',errors)
            continue
        combined.extend((f'pack:{name}',e) for e in pack.get('events',[]))
    return combined


def main():
    errors=[]
    try:
        data=load_json(PATH)
    except Exception as exc:
        print(f'ERROR: cannot parse {PATH}: {exc}')
        return 1

    layers={x.get('id') for x in data.get('layers',[]) if x.get('id')}
    actors={x.get('id') for x in data.get('actors',[]) if x.get('id')}
    epistemic={x.get('id') for x in data.get('epistemic_classes',[]) if x.get('id')}
    combined=load_events(data,errors)
    ids=set()

    for i,(origin,e) in enumerate(combined):
        where=f'{origin}:events[{i}]'
        if not isinstance(e,dict):
            fail(f'{where}: event must be an object',errors)
            continue
        for key in ('id','date','precision','title','layers','epistemic','subject','actor_ids'):
            if key not in e or e[key] in ('',None,[]): fail(f'{where}: missing {key}',errors)
        eid=e.get('id','')
        if eid in ids: fail(f'{where}: duplicate global event id {eid}',errors)
        ids.add(eid)
        if not re.match(r'^evt-[A-Za-z0-9][A-Za-z0-9._-]*$',eid): fail(f'{where}: invalid id {eid}',errors)
        if e.get('precision') not in PRECISION: fail(f'{where}: invalid precision {e.get("precision")}',errors)

        event_layers=e.get('layers',[])
        event_actors=e.get('actor_ids',[])
        if len(event_layers)!=len(set(event_layers)): fail(f'{where}: duplicate layer id inside event',errors)
        if len(event_actors)!=len(set(event_actors)): fail(f'{where}: duplicate actor id inside event',errors)
        unknown_layers=set(event_layers)-layers
        if unknown_layers: fail(f'{where}: unknown layers {sorted(unknown_layers)}',errors)
        unknown_actors=set(event_actors)-actors
        if unknown_actors: fail(f'{where}: unknown actor ids {sorted(unknown_actors)}',errors)
        if e.get('epistemic') not in epistemic: fail(f'{where}: unknown epistemic class {e.get("epistemic")}',errors)

        precision=e.get('precision')
        timestamp=e.get('timestamp')
        if precision in {'second','minute','hour'} and not timestamp:
            fail(f'{where}: {precision} precision requires timestamp',errors)
        if timestamp:
            parsed=parse_iso_timestamp(timestamp)
            if not parsed: fail(f'{where}: invalid ISO timestamp {timestamp!r}',errors)
            date_year=re.match(r'^(\d{4})',str(e.get('date','')))
            ts_year=re.match(r'^(\d{4})',str(timestamp))
            if date_year and ts_year and date_year.group(1)!=ts_year.group(1):
                fail(f'{where}: timestamp year disagrees with date field',errors)

        if precision=='range' and not re.search(r'(?:\bto\b|/|→|–|-{2,})',str(e.get('date',''))):
            d=str(e.get('date',''))
            if not re.match(r'^\d{4}-\d{4}$',d): fail(f'{where}: range precision should visibly encode a range: {d}',errors)
        if (e.get('date_start') or e.get('date_end')) and precision!='range':
            fail(f'{where}: date_start/date_end should be used only with range precision',errors)

        bible=e.get('bible_relation')
        if bible and bible not in BIBLE_RELATIONS:
            fail(f'{where}: invalid bible_relation {bible!r}',errors)

        public_url=e.get('public_url')
        if public_url and not valid_http_url(public_url):
            fail(f'{where}: public_url must be http(s): {public_url!r}',errors)
        if public_url and not e.get('platform'):
            fail(f'{where}: public_url should identify platform',errors)

        source_records=e.get('source_records',[])
        if source_records and not isinstance(source_records,list):
            fail(f'{where}: source_records must be a list',errors)
        elif isinstance(source_records,list):
            if len(source_records)!=len(set(source_records)):
                fail(f'{where}: duplicate source_records entry',errors)
            for src in source_records:
                if not isinstance(src,str) or not src.strip():
                    fail(f'{where}: invalid source record {src!r}',errors)
                elif src.startswith('occurrence:'):
                    fail(f'{where}: occurrence locator belongs in occurrence_ids, not source_records: {src!r}',errors)

        occurrence_ids=e.get('occurrence_ids',[])
        if occurrence_ids and not isinstance(occurrence_ids,list):
            fail(f'{where}: occurrence_ids must be a list',errors)
        elif isinstance(occurrence_ids,list):
            if len(occurrence_ids)!=len(set(occurrence_ids)):
                fail(f'{where}: duplicate occurrence_ids entry',errors)
            for oid in occurrence_ids:
                if not isinstance(oid,str) or not oid.strip():
                    fail(f'{where}: invalid occurrence id {oid!r}',errors)

        related=e.get('related_event_ids',[])
        if len(related)!=len(set(related)): fail(f'{where}: duplicate related_event_ids entry',errors)
        for rel in related:
            if not isinstance(rel,str) or not rel.startswith('evt-'): fail(f'{where}: invalid related event {rel!r}',errors)

    for i,(origin,e) in enumerate(combined):
        if not isinstance(e,dict):
            continue
        for rel in e.get('related_event_ids',[]):
            if rel not in ids: fail(f'{origin}:events[{i}]: related event does not exist: {rel}',errors)

    if errors:
        print('\n'.join('ERROR: '+x for x in errors))
        print(f'FAILED: {len(errors)} timeline validation error(s)')
        return 1
    packs=max(0,len({origin for origin,_ in combined if origin.startswith("pack:")}))
    print(f'OK: {len(combined)} events across base + {packs} pack(s), {len(layers)} layers, {len(actors)} actor tracks, {len(epistemic)} epistemic classes')
    return 0

if __name__=='__main__':
    sys.exit(main())
