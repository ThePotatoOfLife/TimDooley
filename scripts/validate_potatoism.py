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

def read(rel):
    p=ROOT/rel
    if not p.exists(): errors.append(f'Missing: {rel}'); return ''
    return p.read_text(encoding='utf-8',errors='replace')

def main():
    religion=load('data/potatoism-religion.json')
    cosm=load('data/potatoism-cosmology.json')
    lex=load('data/potatoism-lexicon.json')
    graph=load('data/potatoism-relationships.json')
    research=load('data/potatoism-research-expansion.json')
    manifest=load('manifest.json')
    interpretive=load('knowledge/philosophy/interpretive-justice-laws.json')
    archive=load('knowledge/philosophy/archive-epistemics.json')
    authority=load('knowledge/philosophy/source-authority-and-provenance-policy.json')
    culture=load('data/culture-ontology.json')
    bridge=load('knowledge/philosophy/information-war-interpretive-justice-bridge.json')
    interpretive_page=read('philosophy/interpretive-justice.html')

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

    required_laws={
        'irreducible_subjecthood','situated_first_person_authority','recognition_without_ownership',
        'bounded_jurisdiction','hearing_before_totalization','evidentiary_proportionality',
        'independent_witness','reply_and_correctability','contextual_reaction',
        'proportional_memory','non_retaliatory_correction'
    }
    laws=interpretive.get('laws',{}) if isinstance(interpretive,dict) else {}
    missing_laws=sorted(required_laws-set(laws))
    if missing_laws: errors.append('Interpretive Justice missing laws: '+', '.join(missing_laws))
    if 'disciplines judgment' not in str(interpretive.get('boundary','')).casefold():
        errors.append('Interpretive Justice must explicitly discipline rather than abolish judgment')
    situated=laws.get('situated_first_person_authority',{}) if isinstance(laws,dict) else {}
    if 'does not automatically settle external empirical' not in str(situated.get('boundary','')).casefold():
        errors.append('Situated first-person authority lacks external-fact boundary')

    mechanics=archive.get('representation_mechanics',{}) if isinstance(archive,dict) else {}
    for key in ('representation_gap','identity_compression','narrative_lock_in','jurisdiction_creep','falsifier_loss','proportional_memory'):
        if key not in mechanics: errors.append(f'Archive Epistemics missing representation mechanic: {key}')

    protocol=authority.get('living_subject_representation_protocol',{}) if isinstance(authority,dict) else {}
    if not protocol.get('sequence'): errors.append('Source authority missing living-subject representation protocol')
    if not protocol.get('symmetry'): errors.append('Living-subject representation protocol missing symmetry rule')

    metrics=culture.get('interpretive_justice_metrics',{}) if isinstance(culture,dict) else {}
    for key in ('RepresentationGap','IndependentSourceRatio','ReplyAvailability','CorrectionReachRatio','ContextRetention','LabelPersistenceAfterCorrection','ClassificationReviewLatency','ClassifierClassifiedAsymmetry'):
        if key not in metrics: errors.append(f'Culture ontology missing Interpretive Justice metric: {key}')

    for marker in ('Person Before Dossier','Hear Before You Close the Case','Memory That Can Update'):
        if marker.casefold() not in interpretive_page.casefold():
            errors.append(f'Interpretive Justice reader missing teaching: {marker}')
    if 'interpretive-justice-laws.json' not in interpretive_page:
        errors.append('Interpretive Justice reader does not link canonical law owner')
    if 'hearing can strengthen a criticism' not in interpretive_page.casefold():
        errors.append('Interpretive Justice reader must state that hearing can strengthen criticism as well as revise it')

    if bridge.get('canonical_owner')!='knowledge/philosophy/interpretive-justice-laws.json':
        errors.append('Information-war bridge missing canonical Interpretive Justice owner link')
    if bridge.get('information_war_owner')!='data/spiritual-war-information-war.json':
        errors.append('Information-war bridge missing information-war owner link')
    for key in ('representation_gap','identity_compression','narrative_lock_in','correction_asymmetry','source_independence'):
        if key not in bridge.get('shared_operators',[]):
            errors.append(f'Information-war bridge missing shared operator: {key}')
    if 'does not prove' not in str(bridge.get('boundary','')).casefold():
        errors.append('Information-war Interpretive Justice bridge needs non-verdict boundary')

    branches={b.get('id'):b for b in manifest.get('branches',[]) if isinstance(b,dict) and b.get('id')}
    if manifest.get('root',{}).get('id')!='potato-of-life': errors.append('Potatoism public root must be potato-of-life')
    routed=[]
    for bid in ('tim','transformation','cosmology','traditions','timeline','sources'):
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
    print(f'Interpretive Justice laws: {len(laws)}')
    print(f'Public manifest branches: {len(branches)} · root: {manifest.get("root",{}).get("id","?")}')
    print(f'Errors: {len(errors)}')
    for e in errors: print('ERROR:',e)
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
