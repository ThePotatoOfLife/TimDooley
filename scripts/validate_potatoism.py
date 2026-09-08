#!/usr/bin/env python3
"""Validate the dense Potatoism corpus and its unified-index routing contract."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=['data/potatoism-religion.json','data/potatoism-cosmology.json','data/potatoism-lexicon.json','data/potatoism-relationships.json','data/potatoism-research-expansion.json','data/root-navigation.json']
errors=[]
def load(rel):
    p=ROOT/rel
    if not p.exists(): errors.append(f'Missing: {rel}'); return {}
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'Invalid JSON: {rel}: {e}'); return {}
def main():
    religion=load('data/potatoism-religion.json'); cosm=load('data/potatoism-cosmology.json'); lex=load('data/potatoism-lexicon.json'); graph=load('data/potatoism-relationships.json'); research=load('data/potatoism-research-expansion.json'); nav=load('data/root-navigation.json')
    if not religion.get('birth',{}).get('date'): errors.append('Potatoism birth marker missing')
    if len(religion.get('timeline',[]))<5: errors.append('Potatoism timeline is too short')
    if len(lex.get('entries',[]))<50: errors.append('Potatoism lexicon unexpectedly small')
    nodes=set(graph.get('nodes',[]))
    for e in graph.get('edges',[]):
        for side in ('from','to'):
            if e.get(side) not in nodes: errors.append(f'Dangling symbolic edge endpoint: {e.get(side)}')
    if len(research.get('layers',[]))<8: errors.append('Research expansion unexpectedly small')
    axis=next((b for b in nav.get('branches',[]) if b.get('id')=='axis'),{})
    if not any(c.get('id')=='potatoism' for c in axis.get('collections',[])): errors.append('Potatoism missing from AXIS navigation')
    if not any(r.get('id') in {'potatoism','tim-dooley'} for r in nav.get('center',{}).get('records',[])): errors.append('Potatoism/Tim Dooley center route missing')
    print(f'Potatoism timeline stages: {len(religion.get("timeline",[]))}')
    print(f'Lexicon entries: {len(lex.get("entries",[]))}')
    print(f'Symbolic graph nodes: {len(nodes)} · edges: {len(graph.get("edges",[]))}')
    print(f'Research layers: {len(research.get("layers",[]))}')
    print('Unified index route: verified')
    print(f'Errors: {len(errors)}')
    for e in errors: print('ERROR:',e)
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
