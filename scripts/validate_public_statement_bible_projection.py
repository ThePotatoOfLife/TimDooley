from __future__ import annotations

import json
from pathlib import Path
import sys


def validate_bible_projection(
    payload: dict,
    root_ids: set[str],
    episode_ids: set[str],
    relation_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    if payload.get('id') != 'public-statement-bible-projection':
        errors.append('projection id must be public-statement-bible-projection')
    if payload.get('model') != 'rooted-reference-projection':
        errors.append('projection model must be rooted-reference-projection')

    for root_id, refs in (payload.get('root_relations') or {}).items():
        if root_id not in root_ids:
            errors.append(f'unknown root {root_id}')
        for relation_id in refs or []:
            if relation_id not in relation_ids:
                errors.append(f'unknown relation {relation_id} on root {root_id}')

    for episode_id, record in (payload.get('episode_relations') or {}).items():
        if episode_id not in episode_ids:
            errors.append(f'unknown episode {episode_id}')
        if record.get('inheritance') != 'member_union':
            errors.append(f'episode {episode_id}: inheritance must be member_union')
        for relation_id in record.get('relation_ids') or []:
            if relation_id not in relation_ids:
                errors.append(f'unknown relation {relation_id} on episode {episode_id}')
        if record.get('sequence_relation_ids'):
            errors.append(
                f'episode {episode_id}: sequence_relation_ids must remain empty in member-inheritance projection'
            )

    seen_gap_ids: set[str] = set()
    for gap in payload.get('gaps') or []:
        gap_id = str(gap.get('id') or '').strip()
        if not gap_id:
            errors.append('projection gap missing id')
        elif gap_id in seen_gap_ids:
            errors.append(f'duplicate projection gap {gap_id}')
        seen_gap_ids.add(gap_id)
        relation_id = str(gap.get('relation_id') or '').strip()
        if relation_id and relation_id not in relation_ids:
            errors.append(f'projection gap references unknown relation {relation_id}')
        if gap.get('gap_type') != 'comparator':
            errors.append(f'projection gap {gap_id}: gap_type must be comparator')
        if gap.get('state') not in {'open', 'resolved', 'rejected'}:
            errors.append(f'projection gap {gap_id}: invalid state')

    return errors


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    root_path = repository_root / 'data' / 'evidence' / 'public-statement-evidence-root.json'
    episode_path = repository_root / 'data' / 'evidence' / 'public-statement-episodes.json'
    projection_path = repository_root / 'data' / 'evidence' / 'public-statement-bible-projection.json'
    relation_paths = [
        repository_root / 'knowledge' / 'traditions' / 'public-x-biblical-occurrence-relations-01-09.json',
        repository_root / 'knowledge' / 'traditions' / 'public-x-biblical-occurrence-relations-10-18.json',
        repository_root / 'knowledge' / 'traditions' / 'public-x-biblical-occurrence-relations-19-27.json',
    ]
    required = [root_path, episode_path, projection_path, *relation_paths]
    missing = [path for path in required if not path.exists()]
    if missing:
        print('PUBLIC STATEMENT BIBLE PROJECTION VALIDATION FAILED')
        for path in missing:
            print(' - missing', path.relative_to(repository_root))
        return 1

    root = json.loads(root_path.read_text(encoding='utf-8'))
    episodes = json.loads(episode_path.read_text(encoding='utf-8'))
    projection = json.loads(projection_path.read_text(encoding='utf-8'))
    relation_payloads = [json.loads(path.read_text(encoding='utf-8')) for path in relation_paths]

    root_ids = {str(row.get('id')) for row in root.get('roots', []) if row.get('id')}
    episode_ids = {str(row.get('id')) for row in episodes.get('episodes', []) if row.get('id')}
    relation_ids = {
        str(row.get('id'))
        for payload in relation_payloads
        for row in payload.get('relations', [])
        if row.get('id')
    }
    errors = validate_bible_projection(projection, root_ids, episode_ids, relation_ids)
    if errors:
        print('PUBLIC STATEMENT BIBLE PROJECTION VALIDATION FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(
        'PUBLIC STATEMENT BIBLE PROJECTION VALIDATION PASSED '
        f"({len(projection.get('root_relations', {}))} rooted links; {len(projection.get('gaps', []))} gaps)"
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
