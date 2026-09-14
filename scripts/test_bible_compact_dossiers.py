#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from bible_corpus import assemble_relations

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    'chosen-gentile-potato-2024-10-02',
    'ben-david-ben-joseph-pair-2026-06-23',
    'sammy-weeping-tammuz-2019-2020',
    'hebrew-name-network-2026-08-08',
    'needle-communion-mountain-2026-08-10',
    'zion-2026-08-23',
    'christ-wedge-door-2026-08-31',
    'temple-pillars-jachin-boaz-2026-09-05',
    'house-seed-eye-ladder-2026-09-08',
    'zechariah-research-unlock-2026-09-09',
]


def check(row: dict) -> list[str]:
    argument = row.get('relation_argument') or {}
    scripture = row.get('scripture_context') or {}
    discovery = row.get('discovery_history') or {}
    missing: list[str] = []
    required_argument = ('project_sequence','biblical_sequence','correspondences','why_it_matters','maximum_claim')
    for key in required_argument:
        if not argument.get(key):
            missing.append(f'relation_argument.{key}')
    if not (scripture.get('literary_context') or scripture.get('canonical_context')):
        missing.append('scripture_context')
    if not (row.get('mismatch') or row.get('counter_text') or row.get('boundary')):
        missing.append('counterpressure')
    if not (discovery.get('source_direction') or row.get('source_direction') or row.get('discovery_mode')):
        missing.append('source_direction')
    return missing


def main() -> int:
    manifest = json.loads((ROOT / 'knowledge/traditions/bible-layer-manifest.json').read_text(encoding='utf-8'))
    rows = {row['id']: row for row in assemble_relations(ROOT, manifest)}
    failures = []
    for relation_id in TARGETS:
        if relation_id not in rows:
            failures.append(f'{relation_id}: missing relation')
            continue
        missing = check(rows[relation_id])
        if missing:
            failures.append(f"{relation_id}: {', '.join(missing)}")
    if failures:
        print('COMPACT DOSSIER CONTRACT FAILED')
        for failure in failures:
            print(f'- {failure}')
        return 1
    print('COMPACT DOSSIER CONTRACT PASSED (10 full dossiers)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
