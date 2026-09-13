#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/atlas-registry.json'
if not P.exists(): raise SystemExit('missing data/atlas-registry.json')
d=json.loads(P.read_text())
active=[n for n in d.get('nodes',[]) if n.get('status')=='active']
ids=[n['id'] for n in active]
if len(ids)!=len(set(ids)): raise SystemExit('duplicate active ids')
roots=[n for n in active if n.get('north_parent') is None]
if len(roots)!=1 or roots[0]['id']!=d.get('root_id'): raise SystemExit('invalid root')
by={n['id']:n for n in active}
routes=[n['route'] for n in active]
if len(routes)!=len(set(routes)): raise SystemExit('duplicate routes')
for n in active:
    if not (ROOT/n['owner_path']).exists(): raise SystemExit('missing owner '+n['id'])
    if n['id']==d['root_id']: continue
    p=n.get('north_parent')
    if not p or p not in by: raise SystemExit('bad parent '+n['id'])
    seen={n['id']}; cur=n
    while cur['id']!=d['root_id']:
        pid=cur.get('north_parent')
        if pid in seen: raise SystemExit('north cycle '+n['id'])
        if pid not in by: raise SystemExit('broken north chain '+n['id'])
        seen.add(pid); cur=by[pid]
print('ATLAS NORTH PASSED:',len(active),'active nodes')
