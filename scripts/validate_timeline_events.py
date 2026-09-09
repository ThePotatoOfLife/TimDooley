#!/usr/bin/env python3
"""Validate the layered timeline base plus optional curated event packs."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data'/'timeline-events.json'
PACK_INDEX=ROOT/'data'/'timeline-event-packs'/'index.json'
PRECISION={'second','minute','hour','date','month','year','range'}


def fail(msg,errors):
    errors.append(msg)


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_events(data, errors):
    combined=[('base', e) for e in data.get('events',[])]
    if not PACK_INDEX.exists():
        return combined
    try:
        idx=load_json(PACK_INDEX)
    except Exception as exc:
        fail(f'cannot parse {PACK_INDEX}: {exc}',errors)
        return combined
    for name in idx.get('packs',[]):
        path=PACK_INDEX.parent/name
        try:
            pack=load_json(path)
        except Exception as exc:
            fail(f'cannot parse pack {path}: {exc}',errors)
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
        for key in ('id','date','precision','title','layers','epistemic','subject','actor_ids'):
            if key not in e or e[key] in ('',None,[]): fail(f'{where}: missing {key}',errors)
        eid=e.get('id','')
        if eid in ids: fail(f'{where}: duplicate global event id {eid}',errors)
        ids.add(eid)
        if not re.match(r'^evt-[A-Za-z0-9][A-Za-z0-9._-]*$',eid): fail(f'{where}: invalid id {eid}',errors)
        if e.get('precision') not in PRECISION: fail(f'{where}: invalid precision {e.get("precision")}',errors)
        unknown_layers=set(e.get('layers',[]))-layers
        if unknown_layers: fail(f'{where}: unknown layers {sorted(unknown_layers)}',errors)
        unknown_actors=set(e.get('actor_ids',[]))-actors
        if unknown_actors: fail(f'{where}: unknown actor ids {sorted(unknown_actors)}',errors)
        if e.get('epistemic') not in epistemic: fail(f'{where}: unknown epistemic class {e.get("epistemic")}',errors)
        if e.get('precision') in {'second','minute','hour'} and not e.get('timestamp'):
            fail(f'{where}: {e.get("precision")} precision requires timestamp',errors)
        if e.get('precision')=='range' and not re.search(r'(?:\bto\b|/|→|–|-{2,})',str(e.get('date',''))):
            # A single hyphenated ISO date is not a range; year-year and 'to' forms are accepted.
            d=str(e.get('date',''))
            if not re.match(r'^\d{4}-\d{4}$',d): fail(f'{where}: range precision should visibly encode a range: {d}',errors)
        for rel in e.get('related_event_ids',[]):
            if not isinstance(rel,str) or not rel.startswith('evt-'): fail(f'{where}: invalid related event {rel!r}',errors)

    for i,(origin,e) in enumerate(combined):
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
