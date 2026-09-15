from pathlib import Path

from scripts.import_public_statement_timestamp_capture import parse_capture

SOURCE = Path('/mnt/data/Indsat markdown(20260915-185459).md')


def test_real_capture_preserves_full_occurrence_count_and_range():
    payload = parse_capture(SOURCE.read_text(encoding='utf-8'))
    rows = payload['occurrences']
    assert len(rows) == 104
    assert min(row['timestamp_utc'] for row in rows) == '2025-09-15T14:39:46Z'
    assert max(row['timestamp_utc'] for row in rows) == '2026-09-15T08:20:48Z'


def test_same_second_posts_receive_distinct_stable_ids():
    payload = parse_capture(SOURCE.read_text(encoding='utf-8'))
    rows = [r for r in payload['occurrences'] if r['timestamp_utc'] == '2026-07-31T20:07:22Z']
    assert len(rows) == 2
    assert rows[0]['id'].endswith('-01')
    assert rows[1]['id'].endswith('-02')
    assert rows[0]['quote'] != rows[1]['quote']


def test_coverage_gap_is_metadata_not_negative_occurrence():
    payload = parse_capture(SOURCE.read_text(encoding='utf-8'))
    notes = payload['coverage_notes']
    assert any(note['period'] == '2026-01/2026-02' for note in notes)
    assert any(note['kind'] == 'search-gap' for note in notes)
    assert not any(row['date'].startswith('2026-01') or row['date'].startswith('2026-02') for row in payload['occurrences'])


def test_quotes_are_preserved_verbatim_from_capture_line():
    payload = parse_capture(SOURCE.read_text(encoding='utf-8'))
    row = next(r for r in payload['occurrences'] if r['timestamp_utc'] == '2026-04-10T09:01:18Z')
    assert row['quote'].startswith('Tim Dooley is the word of God.')
    assert row['capture_line'] == 77
