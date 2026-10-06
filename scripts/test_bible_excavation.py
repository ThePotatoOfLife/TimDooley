#!/usr/bin/env python3
from __future__ import annotations
from bible_excavation import DIMENSIONS, assess_relation, build_report


def rich():
    return {
        'id':'r1','date':'2026-01-01','project_quote':'q','owners':['x'],
        'biblical_refs':['John 10:7, 9'],'biblical_scene_ids':['s1'],'primary_biblical_scene_id':'s1',
        'relation_class':'structural','discovery_mode':'public',
        'scene_context':{'summary':'s','setting':'x','before':'b','after':'a','source_status':'exact'},
        'wording_status':'exact','recurrences':['r'],'parallel_passages':['John 10:1-18'],
        'weaknesses':['limit'],
        'relation_argument':{'project_sequence':['a','b'],'biblical_sequence':['c','d'],'why_dense':'why','maximum_claim':'bounded'},
        'source_direction':'explicit','first_attestation_date':'2026-01-01','first_comparison_date':'2026-01-02',
        'formal_archive_date':'2026-01-03','occurrence_ids':['o'],'timeline_event_ids':['t'],
        'provenance':'p','related_relations':['r2'],'research_frontier':'next','motifs':['m'],'operators':['op'],
    }

SCENES=[{'id':'s1','literary_context':'l','historical_context':'h','counterreadings_or_limits':['c']}]

def main()->int:
    row=rich();report=build_report([row],SCENES,'x')
    assert len(DIMENSIONS)==33
    assert report['relation_count']==1
    assert report['relations'][0]['dimensions']['first_attestation_date']['status']=='complete'

    no_attestation=rich();no_attestation.pop('first_attestation_date');no_attestation['discovery_history']={}
    assessed=assess_relation(no_attestation,SCENES,[no_attestation])
    assert assessed['dimensions']['first_attestation_date']['status']=='missing'

    inferred_direction=rich();inferred_direction.pop('source_direction');inferred_direction['discovery_mode']='public'
    assessed=assess_relation(inferred_direction,SCENES,[inferred_direction])
    assert assessed['dimensions']['source_direction']['status']=='partial'

    incomplete={'id':'r2','biblical_refs':['John 10:7'],'relation_class':'structural'}
    queued=build_report([incomplete],SCENES,'x')
    assert queued['mine_next'] and queued['mine_next'][0]['relation_id']=='r2'
    print('BIBLE EXCAVATION TESTS PASSED')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
