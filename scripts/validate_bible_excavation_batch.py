#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'knowledge' / 'indexes' / 'bible-excavation-batch-01.json'
QUEUE = ROOT / 'knowledge' / 'indexes' / 'bible-comparator-research-queue.json'


def main() -> int:
    errors: list[str] = []
    batch = json.loads(BATCH.read_text(encoding='utf-8'))
    queue = json.loads(QUEUE.read_text(encoding='utf-8'))

    if batch.get('status') != 'research planning projection':
        errors.append('batch status must remain research planning projection')
    policy = batch.get('policy') or {}
    for key in ('no_strength_upgrade_from_context', 'no_backdating_later_comparison', 'no_primary_source_inference'):
        if policy.get(key) is not True:
            errors.append(f'policy must enforce {key}')

    queue_ids = [item.get('relation_id') for item in queue.get('items', [])]
    items = batch.get('items', [])
    batch_ids = [item.get('relation_id') for item in items]
    if len(batch_ids) != len(set(batch_ids)):
        errors.append('duplicate relation ids in excavation batch')
    if batch_ids != queue_ids:
        errors.append(f'batch relation order/coverage differs from research queue: expected {queue_ids}, got {batch_ids}')

    queue_by_id = {item.get('relation_id'): item for item in queue.get('items', [])}
    for item in items:
        rid = item.get('relation_id')
        source = queue_by_id.get(rid) or {}
        if item.get('current_strength') != source.get('strength'):
            errors.append(f'{rid}: current_strength must mirror research queue and may not be upgraded')
        if item.get('current_dossier_level') != source.get('dossier_level'):
            errors.append(f'{rid}: current_dossier_level must mirror research queue and may not be upgraded')
        for key in ('source_backed_findings', 'still_missing', 'next_actions'):
            if not item.get(key):
                errors.append(f'{rid}: missing non-empty {key}')
        candidate = item.get('candidate_enrichment') or {}
        if not candidate.get('research_frontier'):
            errors.append(f'{rid}: missing candidate research_frontier')
        if not candidate.get('relation_argument.why_it_matters'):
            errors.append(f'{rid}: missing candidate why_it_matters')
        if not item.get('no_upgrade_reason'):
            errors.append(f'{rid}: missing no_upgrade_reason')

    if errors:
        print('BIBLE EXCAVATION BATCH VALIDATION FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(f'BIBLE EXCAVATION BATCH VALIDATION PASSED ({len(items)} relations)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
