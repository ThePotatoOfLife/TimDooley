from copy import deepcopy

from scripts.validate_public_statement_evidence_root import validate_evidence_root


def valid_payload():
    return {
        'id': 'public-statement-evidence-root',
        'model': 'rooted-spiral',
        'source_owners': ['source-a'],
        'roots': [
            {
                'id': 'stmt-a',
                'kind': 'statement',
                'ring': 0,
                'date': '2026-09-14',
                'timestamp_utc': '2026-09-14T08:11:59Z',
                'precision': 'second',
                'quote': 'Alpha',
                'source_records': ['source-a'],
                'provenance': [{'id': 'a'}],
                'status_id': '111',
                'external_ids': [{'scheme': 'x_status_id', 'value': '111'}],
            },
            {
                'id': 'stmt-b',
                'kind': 'statement',
                'ring': 0,
                'date': '2026-09-15',
                'timestamp_utc': '2026-09-15T08:20:48Z',
                'precision': 'second',
                'quote': 'Beta',
                'source_records': ['source-a'],
                'provenance': [{'id': 'b'}],
            },
        ],
        'coverage_notes': [],
        'traversals': {'chronological': ['stmt-a', 'stmt-b']},
        'discovery_gaps': [
            {
                'id': 'gap-status-222',
                'gap_type': 'evidence',
                'state': 'open',
                'reason': 'no_statement_at_minute',
                'status_id': '222',
                'candidate_root_ids': [],
            }
        ],
        'reconciliation': {'merged_groups': 0, 'unresolved': []},
    }


def test_valid_root_passes():
    assert validate_evidence_root(valid_payload()) == []


def test_duplicate_status_ids_fail():
    payload = valid_payload()
    payload['roots'][1]['status_id'] = '111'
    assert any('duplicate status_id' in error for error in validate_evidence_root(payload))


def test_chronology_must_reference_every_root_exactly_once():
    payload = valid_payload()
    payload['traversals']['chronological'] = ['stmt-a']
    assert any('chronological traversal' in error for error in validate_evidence_root(payload))


def test_root_requires_provenance_and_ring_zero():
    payload = valid_payload()
    payload['roots'][0]['provenance'] = []
    payload['roots'][0]['ring'] = 1
    errors = validate_evidence_root(payload)
    assert any('provenance' in error for error in errors)
    assert any('ring 0' in error for error in errors)


def test_gap_type_must_be_known_and_candidates_must_exist():
    payload = valid_payload()
    payload['discovery_gaps'][0]['gap_type'] = 'mystery'
    payload['discovery_gaps'][0]['candidate_root_ids'] = ['missing-root']
    errors = validate_evidence_root(payload)
    assert any('invalid gap_type' in error for error in errors)
    assert any('unknown candidate root' in error for error in errors)


def test_external_status_identifier_must_match_status_field():
    payload = valid_payload()
    payload['roots'][0]['external_ids'][0]['value'] = '999'
    assert any('external x_status_id' in error for error in validate_evidence_root(payload))
