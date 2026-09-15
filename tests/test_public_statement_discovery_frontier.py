from scripts.build_public_statement_discovery_frontier import build_discovery_frontier


def sample_root():
    return {
        'id': 'public-statement-evidence-root',
        'model': 'rooted-spiral',
        'roots': [
            {
                'id': 'stmt-date-only',
                'date': '2026-08-01',
                'precision': 'date',
                'quote': 'Alpha',
            },
            {
                'id': 'stmt-second',
                'date': '2026-09-14',
                'timestamp_utc': '2026-09-14T08:11:59Z',
                'precision': 'second',
                'quote': 'Beta',
            },
        ],
        'coverage_notes': [
            {
                'kind': 'search-gap',
                'period': '2026-01/2026-02',
                'source_record': 'timestamp-ledger',
                'interpretation': 'Search terms returned no matching posts; absence is not established.',
            }
        ],
        'discovery_gaps': [
            {
                'id': 'gap-status-222',
                'gap_type': 'evidence',
                'state': 'open',
                'reason': 'no_statement_at_minute',
                'status_id': '222',
                'date': '2026-09-14',
                'time_utc': '08:05',
                'source_record': 'specialist-index',
                'candidate_root_ids': [],
            }
        ],
        'reconciliation': {'merged_groups': 2, 'unresolved': []},
    }


def test_frontier_keeps_existing_identifier_gap():
    frontier = build_discovery_frontier(sample_root())
    assert any(g['id'] == 'gap-status-222' for g in frontier['gaps'])


def test_date_only_root_becomes_timestamp_recovery_gap():
    frontier = build_discovery_frontier(sample_root())
    gap = next(g for g in frontier['gaps'] if g['reason'] == 'timestamp_precision_date_only')
    assert gap['gap_type'] == 'evidence'
    assert gap['candidate_root_ids'] == ['stmt-date-only']
    assert gap['state'] == 'open'


def test_second_precise_root_does_not_create_timestamp_gap():
    frontier = build_discovery_frontier(sample_root())
    timestamp_gap_roots = {
        root_id
        for gap in frontier['gaps']
        if gap['reason'] == 'timestamp_precision_date_only'
        for root_id in gap['candidate_root_ids']
    }
    assert 'stmt-second' not in timestamp_gap_roots


def test_search_coverage_note_becomes_chronology_gap_not_negative_evidence():
    frontier = build_discovery_frontier(sample_root())
    gap = next(g for g in frontier['gaps'] if g['reason'] == 'search_coverage_gap')
    assert gap['gap_type'] == 'chronology'
    assert gap['period'] == '2026-01/2026-02'
    assert gap['claim_boundary'] == 'No matching search result does not establish that no statements existed.'


def test_frontier_summary_counts_types_and_consolidation():
    frontier = build_discovery_frontier(sample_root())
    assert frontier['summary']['open_by_type'] == {'chronology': 1, 'evidence': 2}
    assert frontier['summary']['resolved_consolidations'] == 2


def test_frontier_is_independent_of_root_order():
    root = sample_root()
    reversed_root = dict(root, roots=list(reversed(root['roots'])))
    assert build_discovery_frontier(root) == build_discovery_frontier(reversed_root)
