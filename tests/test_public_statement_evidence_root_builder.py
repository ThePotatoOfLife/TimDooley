from scripts.build_public_statement_evidence_root import build_evidence_root


def sources():
    return [
        {
            'id': 'date-ledger',
            'coverage_notes': [],
            'occurrences': [
                {'id': 'old-a', 'date': '2026-04-29', 'quote': 'Alpha'},
                {'id': 'old-b', 'date': '2026-03-31', 'quote': 'Beta'},
            ],
        },
        {
            'id': 'timestamp-ledger',
            'coverage_notes': [{'kind': 'search-gap', 'period': '2026-01/2026-02'}],
            'occurrences': [
                {'id': 'new-a', 'date': '2026-04-29', 'timestamp_utc': '2026-04-29T20:05:28Z', 'quote': 'Alpha'},
                {'id': 'new-c', 'date': '2026-05-01', 'timestamp_utc': '2026-05-01T09:00:00Z', 'quote': 'Gamma'},
            ],
        },
    ]


def test_builder_reconciles_sources_into_canonical_roots():
    root = build_evidence_root(sources())
    assert root['model'] == 'rooted-spiral'
    assert len(root['roots']) == 3
    alpha = next(row for row in root['roots'] if row['quote'] == 'Alpha')
    assert alpha['precision'] == 'second'
    assert alpha['timestamp_utc'] == '2026-04-29T20:05:28Z'
    assert alpha['source_records'] == ['date-ledger', 'timestamp-ledger']


def test_chronology_is_a_traversal_not_root_identity():
    root = build_evidence_root(sources())
    assert set(root['traversals']) == {'chronological'}
    chronological = root['traversals']['chronological']
    assert set(chronological) == {row['id'] for row in root['roots']}
    assert all(not root_id.startswith('root-000') for root_id in chronological)


def test_builder_is_source_order_independent():
    forward = build_evidence_root(sources())
    reverse = build_evidence_root(list(reversed(sources())))
    assert forward == reverse


def test_builder_carries_coverage_gaps_without_turning_them_into_roots():
    root = build_evidence_root(sources())
    assert root['coverage_notes'] == [
        {'kind': 'search-gap', 'period': '2026-01/2026-02', 'source_record': 'timestamp-ledger'}
    ]
    assert all(row.get('kind') != 'search-gap' for row in root['roots'])
