from __future__ import annotations

import json
from pathlib import Path
import sys

ALLOWED_GAP_TYPES = {
    'evidence',
    'chronology',
    'relationship',
    'role',
    'comparator',
    'countertext',
    'consolidation',
}


def _chronology_key(record: dict) -> tuple[str, str]:
    timestamp = str(record.get('timestamp_utc') or '')
    date = str(record.get('date') or '')
    return (timestamp or f'{date}T00:00:00Z', str(record.get('id') or ''))


def validate_evidence_root(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get('id') != 'public-statement-evidence-root':
        errors.append('root id must be public-statement-evidence-root')
    if payload.get('model') != 'rooted-spiral':
        errors.append('model must be rooted-spiral')

    roots = payload.get('roots')
    if not isinstance(roots, list):
        return errors + ['roots must be a list']

    root_ids: set[str] = set()
    status_ids: set[str] = set()
    by_id: dict[str, dict] = {}
    for index, root in enumerate(roots):
        prefix = f'root[{index}]'
        root_id = str(root.get('id') or '').strip()
        if not root_id:
            errors.append(f'{prefix}: missing id')
        elif root_id in root_ids:
            errors.append(f'{prefix}: duplicate root id {root_id}')
        else:
            root_ids.add(root_id)
            by_id[root_id] = root

        if root.get('kind') != 'statement':
            errors.append(f'{prefix}: kind must be statement')
        if root.get('ring') != 0:
            errors.append(f'{prefix}: statement root must remain at ring 0')
        if not isinstance(root.get('quote'), str) or not root.get('quote'):
            errors.append(f'{prefix}: missing exact quote')
        provenance = root.get('provenance')
        if not isinstance(provenance, list) or not provenance:
            errors.append(f'{prefix}: provenance must be non-empty')
        source_records = root.get('source_records')
        if not isinstance(source_records, list) or not source_records:
            errors.append(f'{prefix}: source_records must be non-empty')

        status_id = str(root.get('status_id') or '').strip()
        if status_id:
            if status_id in status_ids:
                errors.append(f'{prefix}: duplicate status_id {status_id}')
            status_ids.add(status_id)
            external_values = {
                str(item.get('value') or '')
                for item in root.get('external_ids', [])
                if item.get('scheme') == 'x_status_id'
            }
            if external_values != {status_id}:
                errors.append(f'{prefix}: external x_status_id must match status_id {status_id}')

    traversals = payload.get('traversals') or {}
    chronological = traversals.get('chronological')
    if not isinstance(chronological, list):
        errors.append('chronological traversal must be a list')
    else:
        if len(chronological) != len(root_ids) or len(set(chronological)) != len(chronological) or set(chronological) != root_ids:
            errors.append('chronological traversal must reference every root exactly once')
        elif root_ids:
            expected = [row['id'] for row in sorted(roots, key=_chronology_key)]
            if chronological != expected:
                errors.append('chronological traversal is not deterministically ordered')

    gap_ids: set[str] = set()
    for index, gap in enumerate(payload.get('discovery_gaps') or []):
        prefix = f'gap[{index}]'
        gap_id = str(gap.get('id') or '').strip()
        if not gap_id:
            errors.append(f'{prefix}: missing id')
        elif gap_id in gap_ids:
            errors.append(f'{prefix}: duplicate gap id {gap_id}')
        else:
            gap_ids.add(gap_id)
        gap_type = str(gap.get('gap_type') or '')
        if gap_type not in ALLOWED_GAP_TYPES:
            errors.append(f'{prefix}: invalid gap_type {gap_type!r}')
        state = str(gap.get('state') or '')
        if state not in {'open', 'resolved', 'rejected'}:
            errors.append(f'{prefix}: invalid state {state!r}')
        for candidate in gap.get('candidate_root_ids') or []:
            if candidate not in root_ids:
                errors.append(f'{prefix}: unknown candidate root {candidate}')

    source_owners = payload.get('source_owners') or []
    if len(source_owners) != len(set(source_owners)):
        errors.append('source_owners must be unique')

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / 'data' / 'evidence' / 'public-statement-evidence-root.json'
    if not path.exists():
        print('PUBLIC STATEMENT EVIDENCE ROOT VALIDATION FAILED')
        print(f' - missing generated root: {path.relative_to(root)}')
        return 1
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        print('PUBLIC STATEMENT EVIDENCE ROOT VALIDATION FAILED')
        print(f' - invalid JSON: {exc}')
        return 1
    errors = validate_evidence_root(payload)
    if errors:
        print('PUBLIC STATEMENT EVIDENCE ROOT VALIDATION FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print(
        'PUBLIC STATEMENT EVIDENCE ROOT VALIDATION PASSED '
        f"({len(payload.get('roots', []))} roots; {len(payload.get('discovery_gaps', []))} gaps)"
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
