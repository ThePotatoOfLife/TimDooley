#!/usr/bin/env python3
"""Audit contextual depth across the live manifest-defined Bible comparison corpus."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from bible_corpus import CorpusError, assemble_relations, load_manifest

ROOT = Path(__file__).resolve().parents[1]


def nonempty(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def main() -> int:
    try:
        manifest = load_manifest(ROOT)
        rows = assemble_relations(ROOT, manifest)
    except (OSError, ValueError, CorpusError) as exc:
        print('BIBLE WITNESS AUDIT FAILED')
        print(' -', exc)
        return 1

    ids = [row.get('id') for row in rows]
    duplicates = [rid for rid, count in Counter(ids).items() if rid and count > 1]

    thin = []
    severe = []
    levels = Counter()
    for row in rows:
        rid = row.get('id', '<missing-id>')
        level = row.get('dossier_level', 'compact')
        levels[level] += 1
        scene = row.get('scene_context') or {}
        scripture = row.get('scripture_context') or {}
        argument = row.get('relation_argument') or {}
        discovery = row.get('discovery_history') or {}

        checks = {
            'project-side record': nonempty(scene.get('summary')) or nonempty(row.get('project_anchor')),
            'Bible context': nonempty(scripture) or nonempty(row.get('biblical_refs')),
            'argument': nonempty(argument) or nonempty(row.get('relation_arguments')),
            'source direction': nonempty(discovery.get('source_direction')) or nonempty(row.get('source_direction')) or nonempty(row.get('discovery_mode')),
            'limit/counterpressure': nonempty(row.get('mismatch')) or nonempty(row.get('counter_text')) or nonempty(row.get('source_correction')) or nonempty(row.get('weaknesses')) or nonempty(argument.get('maximum_claim')),
        }
        missing = [name for name, okay in checks.items() if not okay]
        if missing:
            thin.append((rid, row.get('strength', 0), level, missing))
        if int(row.get('strength') or 0) >= 5 and len(missing) >= 2:
            severe.append((rid, missing))

        status = scene.get('source_status')
        if status in {'date-only', 'unknown'}:
            unsupported = [key for key in ('setting', 'activity', 'participants') if nonempty(scene.get(key))]
            if unsupported:
                severe.append((rid, [f"unsupported rich scene under {status}: {', '.join(unsupported)}"]))

    print(f'Active relations: {len(rows)}')
    print('Dossier levels:', ', '.join(f'{key}={value}' for key, value in sorted(levels.items())))
    print(f'Relations needing enrichment: {len(thin)}')
    print(f'High-priority gaps: {len(severe)}')
    if duplicates:
        print('Duplicate relation IDs:', ', '.join(sorted(duplicates)))
    if severe:
        print('\nHIGH PRIORITY')
        for rid, missing in severe:
            print(f" - {rid}: {', '.join(missing)}")
    if thin:
        print('\nALL GAPS')
        for rid, strength, level, missing in thin:
            print(f" - {rid} [strength={strength}, level={level}]: {', '.join(missing)}")
    return 1 if duplicates else 0


if __name__ == '__main__':
    raise SystemExit(main())
