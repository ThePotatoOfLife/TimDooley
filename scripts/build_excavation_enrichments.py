#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'knowledge'/'indexes'/'bible-excavation-batch-01.json'
OUTPUT=ROOT/'knowledge'/'traditions'/'biblical-excavation-enrichments-batch01.json'


def build_layer(batch:dict)->dict:
    rows=[]
    for item in batch.get('items',[]):
        rid=item.get('relation_id')
        candidate=item.get('candidate_enrichment') or {}
        frontier=candidate.get('research_frontier')
        if not rid or not frontier:
            raise ValueError('relation_id and research_frontier are required')
        row={'relation_id':rid,'research_frontier':frontier}
        why=candidate.get('relation_argument.why_it_matters')
        if why: row['relation_argument']={'why_it_matters':why}
        direction=candidate.get('discovery_history.source_direction')
        if direction: row['discovery_history']={'source_direction':direction}
        related=candidate.get('related_relations')
        if related: row['related_relations']=list(related)
        recovered=candidate.get('recovered_wording')
        if recovered: row['recovered_wording']=list(recovered)
        rows.append(row)
    return {'id':'biblical-excavation-enrichments-batch01','version':'1.0.0','updated':batch.get('updated'),'status':'additive excavation enrichment layer','enrichments':rows}


def main()->int:
    layer=build_layer(json.loads(SOURCE.read_text(encoding='utf-8')))
    OUTPUT.write_text(json.dumps(layer,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"EXCAVATION ENRICHMENTS BUILT: {len(layer['enrichments'])}")
    return 0


if __name__=='__main__':
    raise SystemExit(main())
