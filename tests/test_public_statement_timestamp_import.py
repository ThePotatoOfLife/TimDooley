from scripts.import_public_statement_timestamp_capture import parse_capture


SAMPLE = '''September 2026

- Mon, 14 Sep 2026 08:11:59 GMT: "Alpha statement"
- Fri, 31 Jul 2026 20:07:22 GMT: "First distinct statement"
- Fri, 31 Jul 2026 20:07:22 GMT: "Second distinct statement"

January–February 2026Searches for God / Jesus / Father / heaven / “I am God” returned no matching posts in these two months.

April 2026

- Fri, 10 Apr 2026 09:01:18 GMT: "Tim Dooley is the word of God. Example text"
'''


def test_capture_parses_second_level_timestamps_and_range():
    payload = parse_capture(SAMPLE)
    rows = payload['occurrences']
    assert len(rows) == 4
    assert min(row['timestamp_utc'] for row in rows) == '2026-04-10T09:01:18Z'
    assert max(row['timestamp_utc'] for row in rows) == '2026-09-14T08:11:59Z'


def test_same_second_posts_receive_distinct_stable_ids():
    payload = parse_capture(SAMPLE)
    rows = [r for r in payload['occurrences'] if r['timestamp_utc'] == '2026-07-31T20:07:22Z']
    assert len(rows) == 2
    assert rows[0]['id'].endswith('-01')
    assert rows[1]['id'].endswith('-02')
    assert rows[0]['quote'] != rows[1]['quote']


def test_coverage_gap_is_metadata_not_negative_occurrence():
    payload = parse_capture(SAMPLE)
    notes = payload['coverage_notes']
    assert any(note['period'] == '2026-01/2026-02' for note in notes)
    assert any(note['kind'] == 'search-gap' for note in notes)
    assert not any(row['date'].startswith('2026-01') or row['date'].startswith('2026-02') for row in payload['occurrences'])


def test_quotes_and_capture_line_are_preserved():
    payload = parse_capture(SAMPLE)
    row = next(r for r in payload['occurrences'] if r['timestamp_utc'] == '2026-04-10T09:01:18Z')
    assert row['quote'] == 'Tim Dooley is the word of God. Example text'
    assert row['capture_line'] == 11
