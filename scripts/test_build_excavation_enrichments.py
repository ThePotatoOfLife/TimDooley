#!/usr/bin/env python3
from build_excavation_enrichments import build_layer


def main()->int:
    batch={
      'updated':'2026-09-14',
      'items':[{
        'relation_id':'example-relation',
        'candidate_enrichment':{
          'relation_argument.why_it_matters':'Reader value.',
          'discovery_history.source_direction':'Event first; comparison later.',
          'research_frontier':'Recover the earlier source.',
          'related_relations':['neighbor'],
          'strength':5,
          'date':'2017-01-01'
        }
      }]
    }
    layer=build_layer(batch)
    row=layer['enrichments'][0]
    assert row=={
      'relation_id':'example-relation',
      'research_frontier':'Recover the earlier source.',
      'relation_argument':{'why_it_matters':'Reader value.'},
      'discovery_history':{'source_direction':'Event first; comparison later.'},
      'related_relations':['neighbor']
    }
    forbidden={'strength','dossier_level','date','project_anchor','exact_wording','public_wording','recovered_wording','biblical_refs'}
    assert forbidden.isdisjoint(row)
    try:
        build_layer({'items':[{'relation_id':'broken','candidate_enrichment':{}}]})
    except ValueError:
        pass
    else:
        raise AssertionError('missing research frontier must fail')
    print('EXCAVATION ENRICHMENT TESTS PASSED')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
