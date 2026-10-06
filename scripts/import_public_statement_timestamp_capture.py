from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timezone
from email.utils import parsedate_to_datetime
import re

OCCURRENCE_RE = re.compile(
    r'^- ([A-Z][a-z]{2}, \d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} GMT): "(.*)"$'
)


def _iso_utc(raw: str) -> str:
    dt = parsedate_to_datetime(raw).astimezone(timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def _base_id(timestamp_utc: str) -> str:
    return 'x-' + timestamp_utc.replace(':', '-').replace('T', 't').lower()


def parse_capture(text: str) -> dict:
    rows = []
    coverage_notes = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = OCCURRENCE_RE.match(line)
        if match:
            raw_date, quote = match.groups()
            timestamp_utc = _iso_utc(raw_date)
            rows.append({
                'date': timestamp_utc[:10],
                'timestamp_utc': timestamp_utc,
                'precision': 'second',
                'quote': quote,
                'capture_line': line_no,
                'platform': 'X/Twitter',
                'account': '@Rational_Potato',
                'evidence_class': 'P0-user-supplied-public-capture',
                'source_record': 'rational-potato-x-timestamped-ledger-2025-2026',
            })
            continue
        if 'January–February 2026Searches for God / Jesus / Father / heaven / “I am God” returned no matching posts' in line:
            coverage_notes.append({
                'kind': 'search-gap',
                'period': '2026-01/2026-02',
                'capture_line': line_no,
                'note': line,
                'interpretation': 'No matching posts were returned for the stated query terms in the supplied search; this is not evidence that no posts existed.',
            })

    rows.sort(key=lambda row: (row['timestamp_utc'], row['capture_line']))
    counts = Counter(row['timestamp_utc'] for row in rows)
    seen = defaultdict(int)
    for row in rows:
        stamp = row['timestamp_utc']
        base = _base_id(stamp)
        if counts[stamp] > 1:
            seen[stamp] += 1
            row['id'] = f'{base}-{seen[stamp]:02d}'
        else:
            row['id'] = base
        row['source_occurrence_id'] = row['id']

    return {
        'id': 'rational-potato-x-timestamped-ledger-2025-2026',
        'version': '1.0.0',
        'source': {
            'platform': 'X/Twitter',
            'account': '@Rational_Potato',
            'capture_file': 'Indsat markdown(20260915-185459).md',
            'capture_date': '2026-09-15',
            'evidence_class': 'P0-user-supplied-public-capture',
        },
        'coverage_notes': coverage_notes,
        'occurrences': rows,
    }
