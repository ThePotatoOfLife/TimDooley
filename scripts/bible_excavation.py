from __future__ import annotations

from collections import Counter
from typing import Any
import re

STATUSES = {'complete','partial','missing','not_applicable','blocked_external'}
DIMENSIONS = [
    'project_exact_wording','project_primary_source','project_earliest_attestation',
    'project_scene_context','project_before_after','project_recurrence','project_wording_status',
    'bible_exact_passage','bible_primary_scene','bible_literary_context','bible_historical_context',
    'bible_parallel_passages','bible_counter_texts','relation_type','relation_sequence_project',
    'relation_sequence_bible','relation_argument','relation_mismatch','maximum_defensible_claim',
    'source_direction','event_date','first_attestation_date','first_comparison_date','formal_archive_date',
    'owner_paths','public_occurrence_links','timeline_links','provenance_summary','related_relations',
    'shared_scene_links','shared_motif_links','shared_operator_links','research_frontier'
]
LEVEL_LABELS={0:'stub',1:'attested',2:'contextualized',3:'dossier-complete',4:'excavated',5:'research-frontier explicit'}
WEIGHTS={
    'project_exact_wording':100,'project_earliest_attestation':90,'bible_exact_passage':85,
    'bible_primary_scene':80,'relation_sequence_project':72,'relation_sequence_bible':72,
    'relation_mismatch':68,'bible_counter_texts':66,'maximum_defensible_claim':65,
    'source_direction':62,'project_primary_source':58,'owner_paths':54,'provenance_summary':52,
    'project_scene_context':48,'project_recurrence':44,'first_attestation_date':42,
    'first_comparison_date':38,'formal_archive_date':34,'research_frontier':30,
}
QUEUE_MAP={
    'project_exact_wording':'missing_exact_project_wording',
    'project_earliest_attestation':'missing_earliest_attestation',
    'bible_exact_passage':'imprecise_scripture_span',
    'bible_primary_scene':'missing_whole_biblical_scene',
    'relation_sequence_project':'missing_relation_sequence',
    'relation_sequence_bible':'missing_relation_sequence',
    'relation_mismatch':'missing_counterpressure',
    'bible_counter_texts':'missing_counterpressure',
    'maximum_defensible_claim':'missing_maximum_claim',
    'source_direction':'missing_source_direction',
    'owner_paths':'missing_provenance_links',
    'provenance_summary':'missing_provenance_links',
    'research_frontier':'missing_research_frontier',
}
MULT={'missing':3,'partial':2,'blocked_external':1}


def arr(value: Any) -> list:
    if value is None:return []
    return value if isinstance(value,list) else [value]

def present(value: Any) -> bool:
    if value is None:return False
    if isinstance(value,str):return bool(value.strip())
    if isinstance(value,(list,dict,tuple,set)):return bool(value)
    return True

def uniq(values: list[Any]) -> list[str]:
    out=[];seen=set()
    for value in values:
        if value is None:continue
        text=str(value).strip()
        if text and text not in seen:seen.add(text);out.append(text)
    return out

def item(status:str, reason:str, evidence:list[Any]|None=None, next_action:str='')->dict:
    if status not in STATUSES:raise ValueError(status)
    return {'status':status,'reason':reason,'evidence':uniq(evidence or []),'next_action':'' if status in {'complete','not_applicable'} else next_action}

def _date(value:Any,label:str)->dict:
    if not present(value):return item('missing',f'{label} is not recorded.',[],f'Recover or classify {label}.')
    text=str(value).strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}',text):return item('complete',f'{label} is day-specific.',[text])
    if re.search(r'\d{4}',text):return item('partial',f'{label} is only partially resolved.',[text],f'Refine {label} if evidence permits.')
    return item('partial',f'{label} is present but not normalized.',[text],f'Normalize {label}.')

def _precise_ref(value:str)->bool:
    parts=[p.strip().replace('–','-').replace('—','-') for p in str(value or '').split(';') if p.strip()]
    if not parts:return False
    pattern=re.compile(r'^(?:[1-3]\s+)?[A-Za-z][A-Za-z ]*\s+\d+(?::\d+(?:-\d+(?::\d+)?)?(?:\s*,\s*\d+(?:-\d+)?)*)?$')
    return all(pattern.match(p) for p in parts)

def _neighbors(row:dict, relations:list[dict], field:str)->list[str]:
    mine=set(str(x) for x in arr(row.get(field)) if x)
    if not mine:return []
    return sorted({str(other.get('id')) for other in relations if other.get('id')!=row.get('id') and mine.intersection(str(x) for x in arr(other.get(field)) if x) and other.get('id')})

def assess_relation(row:dict, scenes:list[dict], relations:list[dict])->dict:
    scene=row.get('scene_context') or {}; scripture=row.get('scripture_context') or {}
    arg=row.get('relation_argument') or {}; discovery=row.get('discovery_history') or {}
    scene_ids={str(s.get('id')):s for s in scenes if s.get('id')}
    linked=[scene_ids[sid] for sid in arr(row.get('biblical_scene_ids')) if sid in scene_ids]
    primary=scene_ids.get(row.get('primary_biblical_scene_id')) or (linked[0] if linked else None)
    dims={}
    def put(name,value):dims[name]=value

    exact=uniq(arr(row.get('project_quote'))+arr(row.get('exact_wording'))+arr(row.get('quote'))+arr(row.get('public_wording')))
    recovered=uniq(arr(row.get('recovered_wording')))
    put('project_exact_wording', item('complete','Exact/public wording is linked.',exact) if exact else item('partial','Only recovered wording is linked.',recovered,'Recover exact/public wording.') if recovered else item('missing','No direct wording is linked.',[],'Recover direct wording.'))
    owners=uniq(arr(row.get('owners'))+arr(row.get('source_refs')))
    occurrences=uniq(arr(row.get('occurrence_ids')))
    put('project_primary_source',item('complete','A public/source identifier is linked.',occurrences+owners) if occurrences else item('partial','Owner paths exist but a primary artifact is not explicit.',owners,'Link the strongest primary source.') if owners else item('missing','No owner/source link is present.',[],'Link a primary source or canonical owner.'))
    earliest=discovery.get('first_attestation_date') or row.get('first_attestation_date')
    put('project_earliest_attestation',_date(earliest,'earliest attestation'))
    context_fields=[scene.get(k) for k in ('summary','setting','activity','trigger','participants','surrounding_topics')]
    put('project_scene_context',item('complete','Project context is materially described.',context_fields) if sum(present(x) for x in context_fields)>=2 else item('partial','Some project context exists.',context_fields,'Add independent project-side context.') if any(present(x) for x in context_fields) else item('missing','No project scene context is recorded.',[],'Add project-side context.'))
    before_after=[scene.get('before'),scene.get('lead_up'),scene.get('after')]
    put('project_before_after',item('complete','Lead-up and aftermath are both represented.',before_after) if present(scene.get('after')) and (present(scene.get('before')) or present(scene.get('lead_up'))) else item('partial','Only part of the immediate sequence is recorded.',before_after,'Recover before/after context.') if any(present(x) for x in before_after) else item('missing','No before/after sequence is recorded.',[],'Recover before/after context.'))
    recurrence=uniq(arr(row.get('recurrences'))+arr(row.get('repetitions'))+arr(row.get('related_occurrences')))
    put('project_recurrence',item('complete','Recurrence records are linked.',recurrence) if recurrence else item('missing','No recurrence audit is recorded.',[],'Find earlier/later repetitions or mark not applicable.'))
    wording=row.get('wording_status') or scene.get('source_status')
    put('project_wording_status',item('complete','Wording status is classified.',[wording]) if present(wording) else item('partial','Wording evidence exists but status is not explicit.',exact+recovered,'Classify wording status.') if exact or recovered else item('missing','Wording status is absent.',[],'Classify wording status.'))

    refs=uniq(arr(row.get('biblical_refs')))
    precise=[ref for ref in refs if _precise_ref(ref)]
    put('bible_exact_passage',item('complete','All attached references are precise.',refs) if refs and len(precise)==len(refs) else item('partial','Some references are precise.',precise,'Refine remaining references.') if precise else item('missing','No precise passage span is attached.',refs,'Attach a precise passage span.'))
    put('bible_primary_scene',item('complete','A reusable scene is linked.',[primary.get('id')]) if primary else item('missing','No reusable scene is linked.',arr(row.get('biblical_scene_ids')),'Link the best reusable scene.'))
    literary=(primary or {}).get('literary_context') or scripture.get('literary_context') or scripture.get('canonical_context')
    historical=(primary or {}).get('historical_context') or scripture.get('historical_context')
    put('bible_literary_context',item('complete','Literary context is present.',[literary]) if present(literary) else item('missing','Literary context is absent.',[],'Add local literary context.'))
    put('bible_historical_context',item('complete','Historical context is present.',[historical]) if present(historical) else item('partial','Historical context is not yet classified as needed or not applicable.',[],'Add context or mark not applicable.'))
    parallels=uniq(arr(row.get('parallel_passages'))+arr(scripture.get('parallel_passages')))
    put('bible_parallel_passages',item('complete','Parallel passages are linked.',parallels) if parallels else item('partial','No parallel-passage decision is recorded.',[],'Link meaningful parallels or mark not applicable.'))
    counter=uniq(arr(row.get('counter_text'))+arr(row.get('weaknesses'))+arr((primary or {}).get('counterreadings_or_limits')))
    put('bible_counter_texts',item('complete','Counterpressure is represented.',counter) if counter else item('partial','No counter-text decision is recorded.',[],'Add counterpressure or mark not applicable.'))

    relation_type=uniq([row.get('relation_class'),row.get('classification'),row.get('discovery_mode')])
    put('relation_type',item('complete','Relation/discovery type is classified.',relation_type) if relation_type else item('missing','Relation type is absent.',[],'Classify relation and discovery mode.'))
    ps=uniq(arr(arg.get('project_sequence'))+arr(row.get('project_sequence')))
    bs=uniq(arr(arg.get('biblical_sequence'))+arr(row.get('biblical_sequence')))
    put('relation_sequence_project',item('complete','Project sequence is explicit.',ps) if len(ps)>=2 else item('partial','Project sequence is thin.',ps,'Write an ordered project sequence.') if ps else item('missing','Project sequence is absent.',[],'Write an ordered project sequence.'))
    put('relation_sequence_bible',item('complete','Text sequence is explicit.',bs) if len(bs)>=2 else item('partial','Text sequence is thin.',bs,'Write an ordered text sequence.') if bs else item('missing','Text sequence is absent.',[],'Write an ordered text sequence.'))
    why=arg.get('why_dense') or arg.get('why_it_matters') or row.get('relation_arguments') or row.get('overlap') or row.get('project_value')
    put('relation_argument',item('complete','A comparison argument is present.',arr(why)) if present(why) else item('missing','Comparison argument is absent.',[],'Write why this relation is retained.'))
    mismatch=uniq([row.get('mismatch'),*arr(row.get('weaknesses')),row.get('counter_text'),row.get('source_correction'),row.get('difference'),row.get('boundary')])
    put('relation_mismatch',item('complete','A limitation/mismatch is explicit.',mismatch) if mismatch else item('missing','No limitation/mismatch is explicit.',[],'State where the comparison breaks.'))
    max_claim=arg.get('maximum_claim') or row.get('maximum_claim')
    put('maximum_defensible_claim',item('complete','A maximum claim is explicit.',[max_claim]) if present(max_claim) else item('missing','No maximum claim is explicit.',[],'State the strongest supported conclusion.'))
    direction=discovery.get('source_direction') or row.get('source_direction')
    if present(direction):put('source_direction',item('complete','Source direction is explicit.',[direction]))
    elif present(row.get('discovery_mode')):put('source_direction',item('partial','Discovery mode exists but source direction is not explicit.',[row.get('discovery_mode')],'Classify source direction explicitly.'))
    else:put('source_direction',item('missing','Source direction is absent.',[],'Classify source direction.'))

    put('event_date',_date(row.get('date') or discovery.get('project_anchor_date'),'event date'))
    put('first_attestation_date',_date(discovery.get('first_attestation_date') or row.get('first_attestation_date'),'first attestation date'))
    put('first_comparison_date',_date(discovery.get('first_comparison_date') or row.get('first_comparison_date'),'first comparison date'))
    put('formal_archive_date',_date(discovery.get('first_formal_archive_date') or row.get('formal_archive_date'),'formal archive date'))
    put('owner_paths',item('complete','Canonical owner paths are linked.',owners) if owners else item('missing','No owner path is linked.',[],'Link canonical owner paths.'))
    put('public_occurrence_links',item('complete','Public occurrence IDs are linked.',occurrences) if occurrences else item('partial','No public occurrence decision is recorded.',[],'Link public occurrences or mark not applicable.'))
    timeline=uniq(arr(row.get('timeline_event_ids')))
    put('timeline_links',item('complete','Timeline IDs are linked.',timeline) if timeline else item('partial','No timeline-link decision is recorded.',[],'Link timeline events or mark not applicable.'))
    provenance=row.get('provenance') or row.get('provenance_summary') or discovery.get('provenance')
    put('provenance_summary',item('complete','A provenance summary is present.',[provenance]) if present(provenance) else item('missing','Provenance summary is absent.',[],'Write a compact provenance summary.'))
    related=uniq(arr(row.get('related_relations'))+arr(row.get('related_relation_ids')))
    put('related_relations',item('complete','Related relations are explicit.',related) if related else item('partial','Related relations are not explicit.',[],'Link structural neighbors.'))
    shared_scene=_neighbors(row,relations,'biblical_scene_ids'); shared_motif=_neighbors(row,relations,'motifs'); shared_op=_neighbors(row,relations,'operators')
    put('shared_scene_links',item('complete','Shared-scene neighbors exist.',shared_scene) if shared_scene else item('not_applicable','No shared-scene neighbor is currently present.',[]))
    put('shared_motif_links',item('complete','Shared-motif neighbors exist.',shared_motif) if shared_motif else item('not_applicable','No shared-motif neighbor is currently present.',[]))
    put('shared_operator_links',item('complete','Shared-operator neighbors exist.',shared_op) if shared_op else item('not_applicable','No shared-operator neighbor is currently present.',[]))
    frontier=row.get('research_frontier') or row.get('research_gap') or row.get('research_needed')
    put('research_frontier',item('complete','A next research question is explicit.',arr(frontier)) if present(frontier) else item('missing','No explicit research frontier is recorded.',[],'State the next concrete research question.'))

    level=derive_level(dims)
    return {'relation_id':row.get('id'),'date':row.get('date'),'level':level,'level_label':LEVEL_LABELS[level],'dimensions':dims,'next_actions':priority_actions(dims)}

def derive_level(dims:dict[str,dict])->int:
    def ok(names):return all(dims.get(name,{}).get('status') in {'complete','not_applicable'} for name in names)
    attested=['project_primary_source','bible_exact_passage','relation_type']
    contextual=['project_scene_context','bible_primary_scene','bible_literary_context']
    dossier=['project_exact_wording','relation_argument','relation_mismatch','maximum_defensible_claim','source_direction','event_date','owner_paths','provenance_summary']
    if not ok(attested):return 0
    if not ok(contextual):return 1
    if not ok(dossier):return 2
    if not ok([name for name in DIMENSIONS if name!='research_frontier']):return 3
    return 5 if dims['research_frontier']['status']=='complete' else 4

def priority_actions(dims:dict[str,dict])->list[dict]:
    actions=[]
    for name,data in dims.items():
        status=data.get('status');weight=WEIGHTS.get(name,10)*MULT.get(status,0)
        if weight:actions.append({'dimension':name,'status':status,'priority':weight,'next_action':data.get('next_action','')})
    return sorted(actions,key=lambda x:(-x['priority'],x['dimension']))

def build_report(relations:list[dict],scenes:list[dict],manifest_version:str='')->dict:
    assessments=[assess_relation(row,scenes,relations) for row in relations]
    levels=Counter(x['level_label'] for x in assessments)
    queues={}
    for assessment in assessments:
        for action in assessment['next_actions']:
            q=QUEUE_MAP.get(action['dimension'])
            if not q:continue
            queues.setdefault(q,[]).append({'relation_id':assessment['relation_id'],'priority':action['priority'],'dimension':action['dimension'],'status':action['status'],'next_action':action['next_action']})
    for items in queues.values():items.sort(key=lambda x:(-x['priority'],str(x['relation_id'])))
    mine_next=[];seen=set()
    for assessment in sorted(assessments,key=lambda a:-(a['next_actions'][0]['priority'] if a['next_actions'] else 0)):
        if assessment['relation_id'] in seen:continue
        top=assessment['next_actions'][0] if assessment['next_actions'] else None
        if top:mine_next.append({'relation_id':assessment['relation_id'],**top});seen.add(assessment['relation_id'])
        if len(mine_next)>=10:break
    return {'id':'bible-comparator-excavation','version':'1.0.0','manifest_version':manifest_version,'relation_count':len(relations),'scene_count':len(scenes),'dimensions':DIMENSIONS,'status_values':sorted(STATUSES),'level_counts':dict(levels),'relations':assessments,'queues':queues,'mine_next':mine_next}
