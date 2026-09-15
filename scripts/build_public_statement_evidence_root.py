from __future__ import annotations

from copy import deepcopy
import hashlib

from scripts.public_statement_evidence_root import reconcile_records


def _canonical_id(record: dict) -> str:
    status_id = str(record.get('status_id') or '').strip()
    if status_id:
        return f'stmt-x-status-{status_id}'
    anchor = str(record.get('timestamp_utc') or record.get('date') or 'undated')
    safe_anchor = anchor.lower().replace(':', '-').replace('t', '-').replace('z', '').replace(' ', '-')
    digest = hashlib.sha256(str(record.get('quote') or '').encode('utf-8')).hexdigest()[:12]
    return f'stmt-x-{safe_anchor}-{digest}'


def _chronology_key(record: dict) -> tuple:
    timestamp = str(record.get('timestamp_utc') or '')
    date = str(record.get('date') or '')
    return (timestamp or f'{date}T00:00:00Z', record['id'])


def build_evidence_root(source_payloads: list[dict]) -> dict:
    neutral_records = []
    coverage_notes = []
    source_owners = []

    for payload in sorted(source_payloads, key=lambda item: str(item.get('id') or '')):
        source_id = str(payload.get('id') or '').strip()
        if source_id:
            source_owners.append(source_id)
        for occurrence in payload.get('occurrences', []):
            row = deepcopy(occurrence)
            row.setdefault('source_record', source_id)
            row.setdefault('source_occurrence_id', row.get('id'))
            neutral_records.append(row)
        for note in payload.get('coverage_notes', []):
            item = deepcopy(note)
            item['source_record'] = source_id
            coverage_notes.append(item)

    reconciled = reconcile_records(neutral_records)
    roots = []
    for record in reconciled:
        root = deepcopy(record)
        root['source_identity'] = root.get('id')
        root['id'] = _canonical_id(root)
        root['kind'] = 'statement'
        root['ring'] = 0
        roots.append(root)

    roots.sort(key=lambda row: row['id'])
    chronological = [row['id'] for row in sorted(roots, key=_chronology_key)]
    coverage_notes.sort(key=lambda row: (str(row.get('period') or ''), str(row.get('source_record') or ''), str(row.get('kind') or '')))

    return {
        'id': 'public-statement-evidence-root',
        'version': '1.0.0',
        'model': 'rooted-spiral',
        'source_owners': sorted(set(source_owners)),
        'roots': roots,
        'coverage_notes': coverage_notes,
        'traversals': {'chronological': chronological},
        'reconciliation': {
            'merged_groups': sum(1 for row in roots if len(row.get('provenance', [])) > 1),
            'unresolved': [],
        },
    }
