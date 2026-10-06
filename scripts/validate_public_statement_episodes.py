from __future__ import annotations

import json
from pathlib import Path
import sys


def validate_episodes(payload: dict, root_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if payload.get('id') != 'public-statement-episodes':
        errors.append('episode payload id must be public-statement-episodes')
    if payload.get('model') != 'rooted-spiral-episodes':
        errors.append('episode payload model must be rooted-spiral-episodes')

    seen: set[str] = set()
    for index, episode in enumerate(payload.get('episodes') or []):
        prefix = f'episode[{index}]'
        episode_id = str(episode.get('id') or '').strip()
        if not episode_id:
            errors.append(f'{prefix}: missing id')
        elif episode_id in seen:
            errors.append(f'{prefix}: duplicate id {episode_id}')
        else:
            seen.add(episode_id)

        start = str(episode.get('start_utc') or '')
        end = str(episode.get('end_utc') or '')
        if not start or not end or start > end:
            errors.append(f'{prefix}: invalid bounds')

        members = list(episode.get('member_root_ids') or [])
        if len(members) != len(set(members)):
            errors.append(f'{prefix}: duplicate member root')
        for root_id in members:
            if root_id not in root_ids:
                errors.append(f'{prefix}: unknown root {root_id}')

        member_count = episode.get('member_count')
        if member_count != len(members):
            errors.append(f'{prefix}: member_count does not match members')
        minimum = int(episode.get('minimum_members') or 1)
        if len(members) < minimum:
            errors.append(f'{prefix}: minimum_members not met')

        status = str(episode.get('status') or '')
        if status not in {'candidate', 'tested', 'consolidated', 'rejected'}:
            errors.append(f'{prefix}: invalid status {status!r}')
        if status == 'candidate' and episode.get('interpretive_claims'):
            errors.append(f'{prefix}: candidate episode cannot contain interpretive claims')

    return errors


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    root_path = repository_root / 'data' / 'evidence' / 'public-statement-evidence-root.json'
    episode_path = repository_root / 'data' / 'evidence' / 'public-statement-episodes.json'
    if not root_path.exists() or not episode_path.exists():
        print('PUBLIC STATEMENT EPISODE VALIDATION FAILED')
        print(' - generated Evidence Root and Episode files must exist')
        return 1
    root = json.loads(root_path.read_text(encoding='utf-8'))
    payload = json.loads(episode_path.read_text(encoding='utf-8'))
    root_ids = {str(row.get('id')) for row in root.get('roots', []) if row.get('id')}
    errors = validate_episodes(payload, root_ids)
    if errors:
        print('PUBLIC STATEMENT EPISODE VALIDATION FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(f"PUBLIC STATEMENT EPISODE VALIDATION PASSED ({len(payload.get('episodes', []))} episodes)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
