#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_text(rel, errors):
    path = ROOT / rel
    if not path.exists():
        errors.append('missing ' + rel)
        return ''
    return path.read_text(encoding='utf-8', errors='replace')

def load_json(rel, errors):
    path = ROOT / rel
    if not path.exists():
        errors.append('missing ' + rel)
        return {}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'invalid JSON {rel}: {exc}')
        return {}
    return value if isinstance(value, dict) else {}

def main():
    errors=[]
    page=load_text('context/culture/index.html',errors)
    atlas=load_json('knowledge/culture/culture-formation-zeitgeist-atlas.json',errors)
    mechanics=load_json('knowledge/culture/internet-subculture-mechanics.json',errors)
    ledger=load_json('knowledge/culture/culture-theory-source-ledger.json',errors)
    ontology=load_json('data/culture-ontology.json',errors)
    surfaces=load_json('data/house/public-surfaces.json',errors)
    context=load_text('context/index.html',errors)
    farm=load_text('shadow-farm/index.html',errors)

    for marker in (
        'data-reader-surface="culture"',
        'What is a zeitgeist?',
        'How subcultures become recognizable',
        'Internet subculture as infrastructure',
        'Mainstreaming, commodification and inheritance',
        'Garden / repair',
        'internet-subculture-mechanics.json',
        'href="../../shadow-farm/"',
    ):
        if marker not in page: errors.append('culture page missing ' + marker)

    for forbidden in ('Joshua Moon','Josh Moon','Ethan Ralph','ADL','SPLC','hate group','subculture-research-map.json'):
        if forbidden.lower() in page.lower(): errors.append('culture page must remain person-neutral/general: ' + forbidden)

    if atlas.get('id')!='culture-formation-zeitgeist-atlas': errors.append('culture atlas id mismatch')
    for key in ('formation_states','cultural_dimensions','concepts','transformation_models','project_mapping'):
        if not atlas.get(key): errors.append('culture atlas missing '+key)
    if 'knowledge/culture/internet-subculture-mechanics.json' not in atlas.get('research_routes',[]): errors.append('culture atlas must route to generic internet subculture mechanics')
    if 'data/subculture-research-map.json' in atlas.get('research_routes',[]): errors.append('culture atlas must not route public culture work through person-specific subculture map')

    if mechanics.get('id')!='internet-subculture-mechanics': errors.append('internet subculture mechanics id mismatch')
    for key in ('formation_mechanisms','boundary_mechanisms','attention_and_archive','lifecycle','repair_mechanisms'):
        if not mechanics.get(key): errors.append('internet subculture mechanics missing '+key)

    if not ledger.get('sources'): errors.append('culture source ledger is empty')
    for key in ('formation_states','culture_scales','cultural_dimensions','distinction_rules','zeitgeist_model','reputation_pipeline'):
        if not ontology.get(key): errors.append('culture ontology missing '+key)

    if surfaces.get('primary_gateway_ids')!=['tim','religion','philosophy','science','world']: errors.append('five primary gateways changed')
    rows={row.get('id'):row for row in surfaces.get('surfaces',[]) if isinstance(row,dict)}
    culture=rows.get('culture',{})
    if culture.get('canonical_route')!='/context/culture/': errors.append('culture route missing')
    if culture.get('visibility')!='specialist' or culture.get('primary_navigation') is not False: errors.append('culture must remain specialist')
    if 'culture-information' not in culture.get('primary_room_ids',[]): errors.append('culture room ownership missing')

    if 'href="culture/"' not in context: errors.append('Context must link to Culture')
    if 'href="../context/culture/"' not in farm: errors.append('Shadow Farm must link back to Culture')

    if errors:
        print('CULTURE READER VALIDATION FAILED')
        for error in errors: print('-',error)
        return 1
    print('CULTURE READER VALIDATION PASSED')
    return 0
if __name__=='__main__': raise SystemExit(main())
