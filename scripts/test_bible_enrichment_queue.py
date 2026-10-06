#!/usr/bin/env python3
from bible_enrichment_queue import build_enrichment_queue


def main()->int:
    report={
      'relations':[
        {'id':'a','strength':5,'dossier_level':'A','missing':['why_it_matters','supported_conclusion'],'recommended_action':'enrich'},
        {'id':'b','strength':4,'dossier_level':'A','missing':['project_sequence'],'recommended_action':'enrich'},
        {'id':'c','strength':3,'dossier_level':'B','missing':['why_it_matters'],'recommended_action':'research'},
        {'id':'d','strength':5,'dossier_level':'A','missing':[],'recommended_action':'retain'}
      ]
    }
    rows=[
      {'id':'a','owners':['owner-a']},
      {'id':'b','owners':['owner-b']},
      {'id':'c','owners':['owner-c']},
      {'id':'d','owners':['owner-d']}
    ]
    queue=build_enrichment_queue(report,rows)
    assert [item['relation_id'] for item in queue['items']]==['a','b']
    assert queue['items'][0]['priority_score']>queue['items'][1]['priority_score']
    assert queue['items'][0]['owners']==['owner-a']
    assert queue['items'][0]['status']=='reader-enrichment'
    assert queue['enrichment_relation_count']==2
    print('BIBLE ENRICHMENT QUEUE TESTS PASSED')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
