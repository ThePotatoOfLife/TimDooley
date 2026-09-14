#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from build_excavation_enrichments import build_layer

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'knowledge'/'indexes'/'bible-excavation-batch-01.json'
LAYER=ROOT/'knowledge'/'traditions'/'biblical-excavation-enrichments-batch01.json'
FORBIDDEN={'strength','dossier_level','date','project_anchor','exact_wording','public_wording','biblical_refs'}


def main()->int:
    batch=json.loads(BATCH.read_text(encoding='utf-8'))
    committed=json.loads(LAYER.read_text(encoding='utf-8'))
    expected=build_layer(batch)
    errors=[]
    if committed!=expected:
        errors.append('committed enrichment layer is stale relative to excavation batch')
    for row in committed.get('enrichments',[]):
        leaked=FORBIDDEN.intersection(row)
        if leaked:
            errors.append(f"{row.get('relation_id')}: forbidden promoted fields {sorted(leaked)}")
        if not row.get('research_frontier'):
            errors.append(f"{row.get('relation_id')}: missing research_frontier")
        recovered=row.get('recovered_wording')
        if recovered is not None and (not isinstance(recovered,list) or not recovered or any(not isinstance(value,str) or not value.strip() for value in recovered)):
            errors.append(f"{row.get('relation_id')}: recovered_wording must be a non-empty list of non-empty strings")
    if errors:
        print('BIBLE EXCAVATION ENRICHMENTS VALIDATION FAILED')
        for error in errors:
            print(' -',error)
        return 1
    print(f"BIBLE EXCAVATION ENRICHMENTS VALIDATION PASSED ({len(committed.get('enrichments',[]))} relations)")
    return 0


if __name__=='__main__':
    raise SystemExit(main())
