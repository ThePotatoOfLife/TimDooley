#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE = ROOT / 'knowledge' / 'traditions' / 'biblical-syncretism-dossiers-wave28.json'
MANIFEST = ROOT / 'knowledge' / 'traditions' / 'bible-layer-manifest.json'

REQUIRED_IDS = {
    'memory-event-record-remembrance',
    'testing-claims-witness-fruit',
    'speech-tongue-building',
    'distributed-burden-authority',
    'hospitality-gleaning-room',
    'repair-breach-gate-city',
    'participation-body-branches-gates',
}


def main() -> int:
    errors: list[str] = []
    if not WAVE.exists():
        errors.append(f'missing {WAVE.relative_to(ROOT)}')
    else:
        data = json.loads(WAVE.read_text(encoding='utf-8'))
        rows = data.get('new_relations', [])
        ids = {row.get('id') for row in rows}
        missing = sorted(REQUIRED_IDS - ids)
        if missing:
            errors.append('missing required Wave 28 relations: ' + ', '.join(missing))
        for row in rows:
            rid = row.get('id', '<missing-id>')
            for key in ('project_anchor', 'biblical_refs', 'source_direction', 'boundary'):
                if not row.get(key):
                    errors.append(f'{rid}: missing {key}')
            argument = row.get('relation_argument') or {}
            for key in ('project_sequence', 'biblical_sequence', 'maximum_claim', 'why_it_matters'):
                if not argument.get(key):
                    errors.append(f'{rid}: missing relation_argument.{key}')

    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        serialized = json.dumps(manifest)
        if 'biblical-syncretism-dossiers-wave28.json' not in serialized:
            errors.append('Wave 28 is not registered in bible-layer-manifest.json')
    else:
        errors.append(f'missing {MANIFEST.relative_to(ROOT)}')

    if errors:
        print('Bible Wave 28 validation FAILED')
        for error in errors:
            print(f'- {error}')
        return 1
    print('Bible Wave 28 validation OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
