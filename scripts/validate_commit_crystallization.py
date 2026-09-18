#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'knowledge/research/recent-commit-materialization-crystallization-257-283.json'
SYNTH=ROOT/'data/house/project-synthesis.json'
NAV=ROOT/'data/house/navigation-manifest.json'
INDEX=ROOT/'knowledge/indexes/core-index.json'
HOLDINGS=ROOT/'data/house/holdings.json'
DOSSIERS=ROOT/'data/house/room-dossiers.json'
CENTER=ROOT/'potato-of-life/index.html'
HOME=ROOT/'index.html'

def load(path:Path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    errors=[]
    for path in (LEDGER,SYNTH,NAV,INDEX,HOLDINGS,DOSSIERS,CENTER,HOME):
        if not path.is_file(): errors.append(f'missing crystallization artifact: {path.relative_to(ROOT)}')
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)

    ledger=load(LEDGER)
    synth=load(SYNTH)
    nav=load(NAV)
    index=load(INDEX)
    holdings=load(HOLDINGS)
    dossiers=load(DOSSIERS)

    if ledger.get('range',{}).get('from_sequence')!=257 or ledger.get('range',{}).get('to_sequence')!=283:
        errors.append('crystallization ledger must cover sequence 257 through 283')
    commits=ledger.get('commits',[])
    seq=[x.get('sequence') for x in commits if isinstance(x,dict)]
    if seq!=list(range(257,284)):
        errors.append('crystallization ledger sequence must be contiguous 257..283')
    for row in commits:
        if not row.get('commit'): errors.append(f"sequence {row.get('sequence')} missing commit SHA")
        if not row.get('canonical_materialization'): errors.append(f"sequence {row.get('sequence')} missing canonical materialization")
        if not row.get('state'): errors.append(f"sequence {row.get('sequence')} missing crystallization state")

    mat=synth.get('materialization_crystallization',{})
    if mat.get('authority')!=str(LEDGER.relative_to(ROOT)).replace('\\','/'):
        errors.append('project synthesis must point to crystallization ledger')
    if mat.get('crystallized_through_sequence')!=283:
        errors.append('project synthesis crystallized sequence must remain 283 until ledger advances')
    if synth.get('generative_crystallization',{}).get('route')!=['seed','foundation','reproduction','branching','fruit','memory','refoundation/return']:
        errors.append('generative crystallization route drifted')

    nav_rows=nav.get('authorities',[])
    if not any(x.get('owner')==str(LEDGER.relative_to(ROOT)).replace('\\','/') for x in nav_rows if isinstance(x,dict)):
        errors.append('navigation manifest missing crystallization authority')

    rid='recent-commit-materialization-crystallization-257-283'
    if rid not in index.get('canonical_groups',{}).get('house_and_navigation',[]):
        errors.append('core index house_and_navigation missing crystallization ledger')
    if not any(x.get('id')==rid for x in index.get('records',[]) if isinstance(x,dict)):
        errors.append('core index records missing crystallization ledger')

    path=str(LEDGER.relative_to(ROOT)).replace('\\','/')
    assigned=[x for x in holdings.get('file_assignments',[]) if isinstance(x,dict) and x.get('path')==path]
    if len(assigned)!=1 or assigned[0].get('primary_owner_room_id')!='research-programmes':
        errors.append('crystallization ledger must have one Research Programmes owner')

    rp=next((x for x in dossiers.get('dossiers',[]) if x.get('room_id')=='research-programmes'),{})
    if rp.get('crystallization_lens',{}).get('authority')!=path:
        errors.append('Research Programmes dossier missing crystallization lens')

    center_text=CENTER.read_text(encoding='utf-8',errors='replace')
    for marker in ('id="materialized-crystallization"','Open crystallization ledger','Seed → Foundation'):
        if marker not in center_text: errors.append(f'Potato center missing crystallization marker: {marker}')

    home_text=HOME.read_text(encoding='utf-8',errors='replace')
    for marker in ('class="project-spine"','class="public-doors"','One project, one visible spine'):
        if marker not in home_text: errors.append(f'homepage missing crystallized spine marker: {marker}')

    if errors:
        print('Commit materialization/crystallization validation failed:')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('Commit materialization/crystallization validation passed.')

if __name__=='__main__':
    main()
