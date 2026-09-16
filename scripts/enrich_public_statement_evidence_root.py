from __future__ import annotations

from copy import deepcopy


def _minute_key(date: str, time_utc: str) -> tuple[str, str]:
    return (str(date or '').strip(), str(time_utc or '').strip()[:5])


def _root_minute_key(root: dict) -> tuple[str, str] | None:
    timestamp = str(root.get('timestamp_utc') or '').strip()
    date = str(root.get('date') or '').strip()
    if not timestamp or 'T' not in timestamp:
        return None
    time_utc = timestamp.split('T', 1)[1].replace('Z', '')
    return _minute_key(date or timestamp[:10], time_utc)


def _gap(source_id: str, record: dict, reason: str, candidates: list[str]) -> dict:
    status_id = str(record.get('status_id') or '').strip()
    date = str(record.get('date') or '').strip()
    time_utc = str(record.get('time_utc') or '').strip()[:5]
    return {
        'id': f'gap-status-{status_id or "unknown"}',
        'gap_type': 'evidence',
        'state': 'open',
        'reason': reason,
        'status_id': status_id,
        'date': date,
        'time_utc': time_utc,
        'source_record': source_id,
        'candidate_root_ids': sorted(candidates),
    }


def enrich_status_ids(evidence_root: dict, specialist_payloads: list[dict]) -> dict:
    result = deepcopy(evidence_root)
    result.setdefault('discovery_gaps', [])
    roots = result.get('roots', [])

    minute_index: dict[tuple[str, str], list[dict]] = {}
    for root in roots:
        key = _root_minute_key(root)
        if key is not None:
            minute_index.setdefault(key, []).append(root)

    new_gaps: list[dict] = []
    for payload in sorted(specialist_payloads, key=lambda item: str(item.get('id') or '')):
        source_id = str(payload.get('id') or '').strip()
        records = sorted(
            payload.get('records', []),
            key=lambda row: (
                str(row.get('date') or ''),
                str(row.get('time_utc') or ''),
                str(row.get('status_id') or ''),
            ),
        )
        for record in records:
            status_id = str(record.get('status_id') or '').strip()
            date = str(record.get('date') or '').strip()
            time_utc = str(record.get('time_utc') or '').strip()[:5]
            if not status_id or not date or not time_utc:
                continue
            candidates = minute_index.get(_minute_key(date, time_utc), [])
            candidate_ids = [row['id'] for row in candidates]
            if not candidates:
                new_gaps.append(_gap(source_id, record, 'no_statement_at_minute', []))
                continue
            if len(candidates) > 1:
                new_gaps.append(_gap(source_id, record, 'ambiguous_statement_minute', candidate_ids))
                continue

            root = candidates[0]
            existing = str(root.get('status_id') or '').strip()
            if existing and existing != status_id:
                new_gaps.append(_gap(source_id, record, 'conflicting_status_id', [root['id']]))
                continue

            root['status_id'] = status_id
            external_ids = list(root.get('external_ids') or [])
            candidate = {'scheme': 'x_status_id', 'value': status_id}
            if candidate not in external_ids:
                external_ids.append(candidate)
            root['external_ids'] = sorted(external_ids, key=lambda row: (row['scheme'], row['value']))
            status_sources = list(root.get('status_sources') or [])
            if source_id and source_id not in status_sources:
                status_sources.append(source_id)
            root['status_sources'] = sorted(status_sources)

    existing_gap_ids = {str(row.get('id') or '') for row in result['discovery_gaps']}
    for gap in sorted(new_gaps, key=lambda row: (row['date'], row['time_utc'], row['status_id'])):
        if gap['id'] not in existing_gap_ids:
            result['discovery_gaps'].append(gap)
            existing_gap_ids.add(gap['id'])
    result['discovery_gaps'].sort(
        key=lambda row: (
            str(row.get('gap_type') or ''),
            str(row.get('date') or ''),
            str(row.get('time_utc') or ''),
            str(row.get('status_id') or ''),
        )
    )
    return result
