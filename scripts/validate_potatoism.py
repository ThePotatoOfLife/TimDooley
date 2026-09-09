#!/usr/bin/env python3
"""Validate the dense Potatoism corpus and its current manifest routing contract."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def load(rel):
    p=ROOT/rel
    if not p.exists(): errors.append(f'Missing: {rel}'); return {}
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'Invalid JSON: {rel}: {e}'); return {}

def main():
    religion=load('data/potatoism-religion.json')
    cosm=load('data/potatoism-cosmology.json')
    lex=load('data/potatoism-lexicon.json')
    graph=load('data/potatoism-relationships.json')
    research=load('data/potatoism-research-expansion.json')
    manifest=load('manifest.json')

    if not religion.get('birth',{}).get('date'): errors.append('Potatoism birth marker missing')
    if len(religion.get('timeline',[]))<5: errors.append('Potatoism timeline is too short')
    if len(lex.get('entries',[]))<50: errors.append('Potatoism lexicon unexpectedly small')

    nodes=set(graph.get('nodes',[]))
    for e in graph.get('edges',[]):
        for side in ('from','to'):
            if e.get(side) not in nodes: errors.append(f'Dangling symbolic edge endpoint: {e.get(side)}')

    if len(research.get('layers',[]))<8: errors.append('Research expansion unexpectedly small')
    if not research.get('deep_research_essays'): errors.append('Research expansion lacks deep research essays')
    if not research.get('cross_layer_synthesis'): errors.append('Research expansion lacks cross-layer synthesis')

    branches={b.get('id'):b for b in manifest.get('branches',[]) if isinstance(b,dict) and b.get('id')}
    if manifest.get('root',{}).get('id')!='potato-of-life': errors.append('Potatoism public root must be potato-of-life')
    routed=[]
    for bid in ('tim','transformation','cosmology','traditions','chronology','sources'):
        b=branches.get(bid,{})
        routed.extend(b.get('records',[]));routed.extend(b.get('children',[]))
    route_text=' '.join(map(str,routed)).casefold()
    if not any(x in route_text for x in ('potatoism','potato-of-life','potatoverse','potato')):
        errors.append('Potatoism is not reachable through current manifest branches')
    if 'axis' in branches:
        errors.append('Legacy AXIS branch should not be required for Potatoism navigation')

    root_record=manifest.get('root',{}).get('record')
    if not root_record or not (ROOT/root_record).exists(): errors.append('Potato of Life root record route is missing')

    print(f'Potatoism timeline stages: {len(religion.get("timeline",[]))}')
    print(f'Lexicon entries: {len(lex.get("entries",[]))}')
    print(f'Symbolic graph nodes: {len(nodes)} · edges: {len(graph.get("edges",[]))}')
    print(f'Research layers: {len(research.get("layers",[]))} · essays: {len(research.get("deep_research_essays",[]))}')
    print(f'Public manifest branches: {len(branches)} · root: {manifest.get("root",{}).get("id","?")}')
    print(f'Errors: {len(errors)}')
    for e in errors: print('ERROR:',e)
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
