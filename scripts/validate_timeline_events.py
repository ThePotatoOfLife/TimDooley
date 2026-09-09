#!/usr/bin/env python3
"""Validate data/timeline-events.json without external dependencies."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data'/'timeline-events.json'
PRECISION={'second','minute','hour','date','month','year','range'}


def fail(msg,errors):
    errors.append(msg)


def main():
    errors=[]
    try:
        data=json.loads(PATH.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'ERROR: cannot parse {PATH}: {exc}')
        return 1

    layers={x.get('id') for x in data.get('layers',[]) if x.get('id')}
    epistemic={x.get('id') for x in data.get('epistemic_classes',[]) if x.get('id')}
    ids=set()
    for i,e in enumerate(data.get('events',[])):
        where=f'events[{i}]'
        for key in ('id','date','precision','title','layers','epistemic','subject'):
            if key not in e or e[key] in ('',None,[]): fail(f'{where}: missing {key}',errors)
        eid=e.get('id','')
        if eid in ids: fail(f'{where}: duplicate id {eid}',errors)
        ids.add(eid)
        if not re.match(r'^evt-[A-Za-z0-9][A-Za-z0-9._-]*$',eid): fail(f'{where}: invalid id {eid}',errors)
        if e.get('precision') not in PRECISION: fail(f'{where}: invalid precision {e.get("precision")}',errors)
        unknown_layers=set(e.get('layers',[]))-layers
        if unknown_layers: fail(f'{where}: unknown layers {sorted(unknown_layers)}',errors)
        if e.get('epistemic') not in epistemic: fail(f'{where}: unknown epistemic class {e.get("epistemic")}',errors)
        if e.get('precision') in {'second','minute','hour'} and not e.get('timestamp'):
            fail(f'{where}: {e.get("precision")} precision requires timestamp',errors)
        for rel in e.get('related_event_ids',[]):
            if not isinstance(rel,str) or not rel.startswith('evt-'): fail(f'{where}: invalid related event {rel!r}',errors)

    for i,e in enumerate(data.get('events',[])):
        for rel in e.get('related_event_ids',[]):
            if rel not in ids: fail(f'events[{i}]: related event does not exist: {rel}',errors)

    if errors:
        print('\n'.join('ERROR: '+x for x in errors))
        print(f'FAILED: {len(errors)} timeline validation error(s)')
        return 1
    print(f'OK: {len(data.get("events",[]))} events, {len(layers)} layers, {len(epistemic)} epistemic classes')
    return 0

if __name__=='__main__':
    sys.exit(main())
