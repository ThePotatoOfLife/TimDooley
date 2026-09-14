#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'knowledge'/'indexes'/'bible-excavation-batch-01.json'
LOG=ROOT/'knowledge'/'indexes'/'bible-excavation-batch-01-mining-log.json'


def main()->int:
    batch=json.loads(BATCH.read_text(encoding='utf-8'))
    log=json.loads(LOG.read_text(encoding='utf-8'))
    batch_ids=[item.get('relation_id') for item in batch.get('items',[])]
    findings=log.get('findings',[])
    finding_ids=[item.get('relation_id') for item in findings]
    errors=[]
    if finding_ids!=batch_ids:
        errors.append(f'mining log must cover Batch 01 exactly and in order: expected {batch_ids}, got {finding_ids}')
    if len(finding_ids)!=len(set(finding_ids)):
        errors.append('duplicate relation id in mining log')
    forbidden={'strength','dossier_level','new_strength','promoted_strength','date_upgrade'}
    for item in findings:
        rid=item.get('relation_id')
        for key in ('finding_type','finding','sources','source_status','what_this_improves','what_this_does_not_improve','next_action'):
            if not item.get(key):
                errors.append(f'{rid}: missing non-empty {key}')
        leaked=forbidden.intersection(item)
        if leaked:
            errors.append(f'{rid}: mining log may not carry upgrade fields {sorted(leaked)}')
        if len(item.get('what_this_does_not_improve') or [])<2:
            errors.append(f'{rid}: must preserve at least two explicit non-upgrade boundaries')
    if errors:
        print('BIBLE EXCAVATION MINING LOG VALIDATION FAILED')
        for error in errors:
            print(' -',error)
        return 1
    print(f'BIBLE EXCAVATION MINING LOG VALIDATION PASSED ({len(findings)} relations)')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
