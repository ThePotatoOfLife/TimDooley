from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

try:
    from scripts.enrich_public_statement_evidence_root import enrich_status_ids
    from scripts.public_statement_evidence_root import reconcile_records
except ModuleNotFoundError:
    from enrich_public_statement_evidence_root import enrich_status_ids
    from public_statement_evidence_root import reconcile_records


def _canonical_id(record: dict) -> str:
    anchor = str(record.get('timestamp_utc') or record.get('date') or 'undated')
    safe_anchor = anchor.lower().replace(':', '-').replace('t', '-').replace('z', '').replace(' ', '-')
    digest_source = f"{anchor}\n{str(record.get('quote') or '')}"
    digest = hashlib.sha256(digest_source.encode('utf-8')).hexdigest()[:12]
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
        'identifier_sources': [],
        'roots': roots,
        'coverage_notes': coverage_notes,
        'traversals': {'chronological': chronological},
        'discovery_gaps': [],
        'reconciliation': {
            'merged_groups': sum(1 for row in roots if len(row.get('provenance', [])) > 1),
            'unresolved': [],
        },
    }


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def build_live_root(repository_root: Path) -> dict:
    evidence_paths = [
        repository_root / 'data' / 'evidence' / 'rational-potato-x-occurrence-ledger-2024-2026.json',
        repository_root / 'data' / 'evidence' / 'rational-potato-x-timestamped-ledger-2025-2026.json',
    ]
    specialist_paths = [
        repository_root / 'knowledge' / 'traditions' / 'september-2026-x-biblical-overlap-01-10.json',
        repository_root / 'knowledge' / 'traditions' / 'september-2026-x-biblical-overlap-11-20.json',
    ]

    source_payloads = [_load_json(path) for path in evidence_paths]
    root = build_evidence_root(source_payloads)
    specialists = [_load_json(path) for path in specialist_paths if path.exists()]
    root = enrich_status_ids(root, specialists)
    root['identifier_sources'] = sorted(str(path.relative_to(repository_root)) for path in specialist_paths if path.exists())
    root['source_paths'] = sorted(str(path.relative_to(repository_root)) for path in evidence_paths)
    root['reconciliation']['open_gap_count'] = sum(
        1 for gap in root.get('discovery_gaps', []) if gap.get('state') == 'open'
    )
    return root


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    payload = build_live_root(repository_root)
    output = repository_root / 'data' / 'evidence' / 'public-statement-evidence-root.json'
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(
        'PUBLIC STATEMENT EVIDENCE ROOT BUILT '
        f"({len(payload['roots'])} roots; {len(payload.get('discovery_gaps', []))} gaps)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
