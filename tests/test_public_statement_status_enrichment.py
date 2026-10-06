from scripts.enrich_public_statement_evidence_root import enrich_status_ids


def sample_root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'stmt-a', 'date': '2026-09-14', 'timestamp_utc': '2026-09-14T08:11:59Z', 'quote': 'Alpha'},
            {'id': 'stmt-b', 'date': '2026-09-14', 'timestamp_utc': '2026-09-14T07:46:10Z', 'quote': 'Beta'},
            {'id': 'stmt-c', 'date': '2026-09-14', 'timestamp_utc': '2026-09-14T07:46:40Z', 'quote': 'Gamma'},
        ],
    }


def specialist():
    return {
        'id': 'specialist-minute-index',
        'records': [
            {'status_id': '111', 'date': '2026-09-14', 'time_utc': '08:11'},
            {'status_id': '222', 'date': '2026-09-14', 'time_utc': '08:05'},
            {'status_id': '333', 'date': '2026-09-14', 'time_utc': '07:46'},
        ],
    }


def test_unique_minute_match_attaches_status_without_renaming_root():
    enriched = enrich_status_ids(sample_root(), [specialist()])
    alpha = next(row for row in enriched['roots'] if row['quote'] == 'Alpha')
    assert alpha['id'] == 'stmt-a'
    assert alpha['status_id'] == '111'
    assert alpha['external_ids'] == [{'scheme': 'x_status_id', 'value': '111'}]


def test_missing_minute_becomes_typed_evidence_gap():
    enriched = enrich_status_ids(sample_root(), [specialist()])
    gap = next(g for g in enriched['discovery_gaps'] if g['status_id'] == '222')
    assert gap['gap_type'] == 'evidence'
    assert gap['reason'] == 'no_statement_at_minute'
    assert gap['state'] == 'open'


def test_ambiguous_minute_is_not_guessed():
    enriched = enrich_status_ids(sample_root(), [specialist()])
    assert not any(row.get('status_id') == '333' for row in enriched['roots'])
    gap = next(g for g in enriched['discovery_gaps'] if g['status_id'] == '333')
    assert gap['gap_type'] == 'evidence'
    assert gap['reason'] == 'ambiguous_statement_minute'
    assert gap['candidate_root_ids'] == ['stmt-b', 'stmt-c']


def test_status_enrichment_is_source_order_independent():
    forward = enrich_status_ids(sample_root(), [specialist()])
    reverse = enrich_status_ids(sample_root(), [dict(specialist(), records=list(reversed(specialist()['records'])))])
    assert forward == reverse
