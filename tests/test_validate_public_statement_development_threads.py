from scripts.validate_public_statement_development_threads import validate_development_threads


def valid_payload():
    return {
        'id': 'public-statement-development-threads',
        'model': 'rooted-spiral-development-threads',
        'source_root_id': 'public-statement-evidence-root',
        'source_episode_id': 'public-statement-episodes',
        'source_bible_projection_id': 'public-statement-bible-projection',
        'threads': [
            {
                'id': 'threshold-door-gate',
                'status': 'candidate',
                'attestation_basis': 'explicit_literal_terms',
                'terms': ['door', 'gate'],
                'attestation_count': 2,
                'root_ids': ['a', 'b'],
                'attestations': [
                    {'root_id': 'a', 'matched_terms': ['door']},
                    {'root_id': 'b', 'matched_terms': ['gate']},
                ],
                'episode_ids': ['episode-a'],
                'bible_relation_ids': ['rel-a'],
                'actor_assignments': [],
                'interpretive_claims': [],
                'persistence': {
                    'span_days': 90,
                    'active_months': ['2026-01', '2026-04'],
                    'active_month_count': 2,
                    'matched_terms': ['door', 'gate'],
                    'term_diversity_count': 2,
                    'episode_count': 1,
                    'episode_coverage_ratio': 1.0,
                    'bible_relation_count': 1,
                    'bible_attestation_count': 1,
                    'bible_attestation_ratio': 0.5,
                    'tests': {
                        'cross_episode': {'observed': 1, 'threshold': 2, 'passed': False},
                        'long_span': {'observed': 90, 'threshold': 90, 'passed': True},
                        'multi_month': {'observed': 2, 'threshold': 3, 'passed': False},
                        'term_diversity': {'observed': 2, 'threshold': 2, 'passed': True},
                    },
                    'passed_test_count': 2,
                    'test_count': 4,
                    'all_core_tests_passed': False,
                    'dimensions': {
                        'span': {
                            'days': 90,
                            'active_month_count': 2,
                            'month_span_count': 4,
                            'temporal_coverage_ratio': 0.5,
                        },
                        'recurrence': {
                            'reappearance_count': 1,
                            'interval_days': [90],
                            'longest_gap_days': 90,
                            'median_gap_days': 90.0,
                        },
                        'distribution': {
                            'attestations_by_month': {'2026-01': 1, '2026-04': 1},
                            'max_month_attestations': 1,
                            'max_month_share': 0.5,
                        },
                        'support': {
                            'episode_count': 1,
                            'episode_attestation_count': 2,
                            'episode_coverage_ratio': 1.0,
                            'bible_relation_count': 1,
                            'bible_attestation_count': 1,
                            'bible_attestation_ratio': 0.5,
                            'second_precision_attestation_count': 2,
                            'second_precision_ratio': 1.0,
                        },
                    },
                },
            }
        ],
        'gaps': [],
    }


def test_valid_candidate_thread_passes():
    assert validate_development_threads(valid_payload(), {'a', 'b'}, {'episode-a'}, {'rel-a'}) == []


def test_thread_roots_and_attestations_must_resolve():
    payload = valid_payload()
    payload['threads'][0]['root_ids'].append('missing')
    payload['threads'][0]['attestation_count'] = 3
    errors = validate_development_threads(payload, {'a', 'b'}, {'episode-a'}, {'rel-a'})
    assert any('unknown root' in error for error in errors)
    assert any('attestations do not match root_ids' in error for error in errors)


def test_matched_terms_must_be_declared_terms():
    payload = valid_payload()
    payload['threads'][0]['attestations'][0]['matched_terms'] = ['portal']
    assert any('undeclared matched term' in error for error in validate_development_threads(payload, {'a', 'b'}, {'episode-a'}, {'rel-a'}))


def test_candidate_thread_cannot_contain_interpretive_claims_or_actor_assignments():
    payload = valid_payload()
    payload['threads'][0]['interpretive_claims'] = ['Unsupported conclusion']
    payload['threads'][0]['actor_assignments'] = [{'actor': 'x'}]
    errors = validate_development_threads(payload, {'a', 'b'}, {'episode-a'}, {'rel-a'})
    assert any('interpretive claims' in error for error in errors)
    assert any('actor assignments' in error for error in errors)


def test_episode_and_bible_references_must_exist():
    payload = valid_payload()
    payload['threads'][0]['episode_ids'] = ['missing-episode']
    payload['threads'][0]['bible_relation_ids'] = ['missing-rel']
    errors = validate_development_threads(payload, {'a', 'b'}, {'episode-a'}, {'rel-a'})
    assert any('unknown episode' in error for error in errors)
    assert any('unknown Bible relation' in error for error in errors)
