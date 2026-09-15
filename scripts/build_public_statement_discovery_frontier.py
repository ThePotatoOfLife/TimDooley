from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path


def _timestamp_gap(root: dict) -> dict:
    return {
        'id': f"gap-timestamp-{root['id']}",
        'gap_type': 'evidence',
        'state': 'open',
        'reason': 'timestamp_precision_date_only',
        'date': str(root.get('date') or ''),
        'candidate_root_ids': [root['id']],
        'target': 'Recover an exact timestamp, status URL, or stronger primary-source locator.',
    }


def _coverage_gap(note: dict) -> dict:
    period = str(note.get('period') or 'unknown')
    safe_period = period.replace('/', '-')
    return {
        'id': f'gap-chronology-search-{safe_period}',
        'gap_type': 'chronology',
        'state': 'open',
        'reason': 'search_coverage_gap',
        'period': period,
        'source_record': str(note.get('source_record') or ''),
        'candidate_root_ids': [],
        'claim_boundary': 'No matching search result does not establish that no statements existed.',
        'note': str(note.get('interpretation') or note.get('note') or ''),
    }


def build_discovery_frontier(evidence_root: dict) -> dict:
    gaps: list[dict] = [deepcopy(gap) for gap in evidence_root.get('discovery_gaps', [])]

    for root in sorted(evidence_root.get('roots', []), key=lambda row: str(row.get('id') or '')):
        if root.get('precision') == 'date':
            gaps.append(_timestamp_gap(root))

    for note in sorted(
        evidence_root.get('coverage_notes', []),
        key=lambda row: (str(row.get('period') or ''), str(row.get('source_record') or '')),
    ):
        if note.get('kind') == 'search-gap':
            gaps.append(_coverage_gap(note))

    by_id: dict[str, dict] = {}
    for gap in gaps:
        gap_id = str(gap.get('id') or '').strip()
        if gap_id:
            by_id[gap_id] = gap
    ordered = sorted(
        by_id.values(),
        key=lambda row: (
            str(row.get('gap_type') or ''),
            str(row.get('date') or row.get('period') or ''),
            str(row.get('time_utc') or ''),
            str(row.get('id') or ''),
        ),
    )

    open_counts = Counter(
        str(gap.get('gap_type') or '')
        for gap in ordered
        if gap.get('state') == 'open'
    )

    return {
        'id': 'public-statement-discovery-frontier',
        'version': '1.0.0',
        'model': 'rooted-spiral-discovery-frontier',
        'source_root_id': str(evidence_root.get('id') or ''),
        'gaps': ordered,
        'summary': {
            'open_total': sum(open_counts.values()),
            'open_by_type': dict(sorted(open_counts.items())),
            'resolved_consolidations': int(
                (evidence_root.get('reconciliation') or {}).get('merged_groups') or 0
            ),
        },
    }


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    source = repository_root / 'data' / 'evidence' / 'public-statement-evidence-root.json'
    output = repository_root / 'data' / 'evidence' / 'public-statement-discovery-frontier.json'
    payload = json.loads(source.read_text(encoding='utf-8'))
    frontier = build_discovery_frontier(payload)
    output.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(
        'PUBLIC STATEMENT DISCOVERY FRONTIER BUILT '
        f"({frontier['summary']['open_total']} open gaps)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
