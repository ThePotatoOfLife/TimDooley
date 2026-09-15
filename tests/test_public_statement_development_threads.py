from scripts.build_public_statement_development_threads import build_development_threads


def sample_root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'root-c', 'timestamp_utc': '2026-05-03T10:00:00Z', 'precision': 'second', 'quote': 'We can build bridges together.'},
            {'id': 'root-a', 'timestamp_utc': '2026-03-01T10:00:00Z', 'precision': 'second', 'quote': 'There is a Door beyond the gate.'},
            {'id': 'root-d', 'timestamp_utc': '2026-06-01T10:00:00Z', 'precision': 'second', 'quote': 'This route is unrelated.'},
            {'id': 'root-b', 'timestamp_utc': '2026-04-01T10:00:00Z', 'precision': 'second', 'quote': 'I am the root and the tree in the garden.'},
        ],
        'traversals': {'chronological': ['root-a', 'root-b', 'root-c', 'root-d']},
    }


def definitions():
    return {
        'id': 'public-statement-development-thread-definitions',
        'persistence_policy': {
            'minimum_active_months': 3,
            'minimum_span_days': 90,
            'minimum_term_diversity': 2,
            'minimum_episode_count': 2,
        },
        'threads': [
            {
                'id': 'threshold-door-gate',
                'label': 'Threshold / Door / Gate',
                'status': 'candidate',
                'terms': ['door', 'gate', 'portal', 'drain'],
                'minimum_attestations': 1,
            },
            {
                'id': 'growth-seed-root-tree-garden',
                'label': 'Growth / Seed / Root / Tree / Garden',
                'status': 'candidate',
                'terms': ['seed', 'root', 'tree', 'garden'],
                'minimum_attestations': 1,
            },
            {
                'id': 'repair-participation',
                'label': 'Repair / Participation',
                'status': 'candidate',
                'terms': ['repair', 'fix', 'build', 'bridge', 'together'],
                'minimum_attestations': 1,
            },
        ],
    }


def sample_episodes():
    return {
        'episodes': [
            {'id': 'episode-one', 'member_root_ids': ['root-a', 'root-b']},
            {'id': 'episode-two', 'member_root_ids': ['root-c']},
        ]
    }


def sample_bible_projection():
    return {
        'root_relations': {
            'root-a': ['rel-door'],
            'root-b': ['rel-tree'],
            'root-c': ['rel-repair'],
        }
    }


def persistent_root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'p1', 'timestamp_utc': '2026-01-01T10:00:00Z', 'date': '2026-01-01', 'precision': 'second', 'quote': 'The door and gate are here.'},
            {'id': 'p2', 'timestamp_utc': '2026-03-15T10:00:00Z', 'date': '2026-03-15', 'precision': 'second', 'quote': 'Walk through the door.'},
            {'id': 'p3', 'timestamp_utc': '2026-06-10T10:00:00Z', 'date': '2026-06-10', 'precision': 'date', 'quote': 'The gate is also a portal.'},
        ],
        'traversals': {'chronological': ['p1', 'p2', 'p3']},
    }


def persistent_definitions():
    return {
        'id': 'public-statement-development-thread-definitions',
        'persistence_policy': {
            'minimum_active_months': 3,
            'minimum_span_days': 90,
            'minimum_term_diversity': 3,
            'minimum_episode_count': 2,
        },
        'threads': [
            {
                'id': 'threshold-door-gate',
                'label': 'Threshold / Door / Gate',
                'status': 'candidate',
                'terms': ['door', 'gate', 'portal'],
                'minimum_attestations': 2,
            },
        ],
    }


def persistent_episodes():
    return {
        'episodes': [
            {'id': 'episode-early', 'member_root_ids': ['p1']},
            {'id': 'episode-late', 'member_root_ids': ['p2', 'p3']},
        ]
    }


def persistent_bible_projection():
    return {
        'root_relations': {
            'p1': ['rel-early'],
            'p3': ['rel-late'],
        }
    }


def bursty_root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'b1', 'timestamp_utc': '2026-01-01T10:00:00Z', 'date': '2026-01-01', 'precision': 'second', 'quote': 'door'},
            {'id': 'b2', 'timestamp_utc': '2026-01-02T10:00:00Z', 'date': '2026-01-02', 'precision': 'second', 'quote': 'door'},
            {'id': 'b3', 'timestamp_utc': '2026-01-03T10:00:00Z', 'date': '2026-01-03', 'precision': 'second', 'quote': 'door'},
            {'id': 'b4', 'timestamp_utc': '2026-01-04T10:00:00Z', 'date': '2026-01-04', 'precision': 'second', 'quote': 'gate'},
            {'id': 'b5', 'timestamp_utc': '2026-01-05T10:00:00Z', 'date': '2026-01-05', 'precision': 'second', 'quote': 'gate'},
            {'id': 'b6', 'timestamp_utc': '2026-06-10T10:00:00Z', 'date': '2026-06-10', 'precision': 'second', 'quote': 'portal'},
        ],
        'traversals': {'chronological': ['b1', 'b2', 'b3', 'b4', 'b5', 'b6']},
    }


def bursty_episodes():
    return {'episodes': [{'id': 'episode-burst', 'member_root_ids': ['b1', 'b2', 'b3', 'b4', 'b5']}, {'id': 'episode-late', 'member_root_ids': ['b6']}]}


def empty_projection():
    return {'root_relations': {}}


def test_thread_membership_requires_explicit_literal_terms():
    payload = build_development_threads(sample_root(), definitions(), sample_episodes(), sample_bible_projection())
    growth = next(t for t in payload['threads'] if t['id'] == 'growth-seed-root-tree-garden')
    assert growth['root_ids'] == ['root-b']
    assert growth['attestations'][0]['matched_terms'] == ['garden', 'root', 'tree']
    assert 'root-d' not in growth['root_ids']


def test_word_boundary_prevents_root_matching_route():
    payload = build_development_threads(sample_root(), definitions(), sample_episodes(), sample_bible_projection())
    all_members = {rid for thread in payload['threads'] for rid in thread['root_ids']}
    assert 'root-d' not in all_members


def test_attestations_follow_existing_timeline_traversal():
    payload = build_development_threads(sample_root(), definitions(), sample_episodes(), sample_bible_projection())
    assert [t['first_attestation_utc'] for t in payload['threads']] == sorted(
        t['first_attestation_utc'] for t in payload['threads']
    )
    threshold = next(t for t in payload['threads'] if t['id'] == 'threshold-door-gate')
    assert [a['root_id'] for a in threshold['attestations']] == ['root-a']


def test_threads_attach_episode_and_bible_references_without_copying_interpretation():
    payload = build_development_threads(sample_root(), definitions(), sample_episodes(), sample_bible_projection())
    repair = next(t for t in payload['threads'] if t['id'] == 'repair-participation')
    assert repair['episode_ids'] == ['episode-two']
    assert repair['bible_relation_ids'] == ['rel-repair']
    assert repair['interpretive_claims'] == []


def test_insufficient_thread_fails_closed_to_development_gap():
    defs = definitions()
    defs['threads'][0]['minimum_attestations'] = 2
    payload = build_development_threads(sample_root(), defs, sample_episodes(), sample_bible_projection())
    assert not any(t['id'] == 'threshold-door-gate' for t in payload['threads'])
    gap = next(g for g in payload['gaps'] if g['thread_id'] == 'threshold-door-gate')
    assert gap['gap_type'] == 'relationship'
    assert gap['reason'] == 'minimum_attestations_not_met'


def test_definition_order_does_not_change_output():
    defs = definitions()
    reverse = dict(defs, threads=list(reversed(defs['threads'])))
    forward_payload = build_development_threads(sample_root(), defs, sample_episodes(), sample_bible_projection())
    reverse_payload = build_development_threads(sample_root(), reverse, sample_episodes(), sample_bible_projection())
    assert forward_payload == reverse_payload


def test_persistence_metrics_measure_long_range_recurrence_and_reference_coverage():
    payload = build_development_threads(
        persistent_root(),
        persistent_definitions(),
        persistent_episodes(),
        persistent_bible_projection(),
    )
    thread = payload['threads'][0]
    persistence = thread['persistence']

    assert persistence['span_days'] == 160
    assert persistence['active_months'] == ['2026-01', '2026-03', '2026-06']
    assert persistence['active_month_count'] == 3
    assert persistence['matched_terms'] == ['door', 'gate', 'portal']
    assert persistence['term_diversity_count'] == 3
    assert persistence['episode_count'] == 2
    assert persistence['episode_coverage_ratio'] == 1.0
    assert persistence['bible_relation_count'] == 2
    assert persistence['bible_attestation_count'] == 2
    assert persistence['bible_attestation_ratio'] == 2 / 3


def test_persistence_dimensions_separate_span_recurrence_distribution_and_support():
    payload = build_development_threads(
        persistent_root(),
        persistent_definitions(),
        persistent_episodes(),
        persistent_bible_projection(),
    )
    dimensions = payload['threads'][0]['persistence']['dimensions']

    assert dimensions['span'] == {
        'days': 160,
        'active_month_count': 3,
        'month_span_count': 6,
        'temporal_coverage_ratio': 0.5,
    }
    assert dimensions['recurrence'] == {
        'reappearance_count': 2,
        'interval_days': [73, 87],
        'longest_gap_days': 87,
        'median_gap_days': 80.0,
    }
    assert dimensions['distribution'] == {
        'attestations_by_month': {'2026-01': 1, '2026-03': 1, '2026-06': 1},
        'max_month_attestations': 1,
        'max_month_share': 1 / 3,
    }
    assert dimensions['support'] == {
        'episode_count': 2,
        'episode_attestation_count': 3,
        'episode_coverage_ratio': 1.0,
        'bible_relation_count': 2,
        'bible_attestation_count': 2,
        'bible_attestation_ratio': 2 / 3,
        'second_precision_attestation_count': 2,
        'second_precision_ratio': 2 / 3,
    }


def test_bursty_thread_is_visible_as_concentrated_even_with_long_span():
    defs = persistent_definitions()
    payload = build_development_threads(bursty_root(), defs, bursty_episodes(), empty_projection())
    persistence = payload['threads'][0]['persistence']

    assert persistence['span_days'] == 160
    assert persistence['dimensions']['span']['month_span_count'] == 6
    assert persistence['dimensions']['span']['temporal_coverage_ratio'] == 2 / 6
    assert persistence['dimensions']['distribution']['attestations_by_month'] == {'2026-01': 5, '2026-06': 1}
    assert persistence['dimensions']['distribution']['max_month_attestations'] == 5
    assert persistence['dimensions']['distribution']['max_month_share'] == 5 / 6
    assert persistence['dimensions']['recurrence']['longest_gap_days'] == 156


def test_persistence_tests_use_declared_policy_without_promoting_candidate_status():
    payload = build_development_threads(
        persistent_root(),
        persistent_definitions(),
        persistent_episodes(),
        persistent_bible_projection(),
    )
    thread = payload['threads'][0]
    tests = thread['persistence']['tests']

    assert tests == {
        'cross_episode': {'observed': 2, 'threshold': 2, 'passed': True},
        'long_span': {'observed': 160, 'threshold': 90, 'passed': True},
        'multi_month': {'observed': 3, 'threshold': 3, 'passed': True},
        'term_diversity': {'observed': 3, 'threshold': 3, 'passed': True},
    }
    assert thread['persistence']['passed_test_count'] == 4
    assert thread['persistence']['test_count'] == 4
    assert thread['persistence']['all_core_tests_passed'] is True
    assert thread['status'] == 'candidate'
    assert thread['interpretive_claims'] == []


def test_persistence_policy_thresholds_can_fail_without_removing_the_thread():
    defs = persistent_definitions()
    defs['persistence_policy']['minimum_active_months'] = 4
    defs['persistence_policy']['minimum_span_days'] = 200
    defs['persistence_policy']['minimum_term_diversity'] = 4
    defs['persistence_policy']['minimum_episode_count'] = 3

    payload = build_development_threads(
        persistent_root(),
        defs,
        persistent_episodes(),
        persistent_bible_projection(),
    )
    thread = payload['threads'][0]

    assert thread['persistence']['passed_test_count'] == 0
    assert thread['persistence']['all_core_tests_passed'] is False
    assert thread['status'] == 'candidate'
    assert thread['root_ids'] == ['p1', 'p2', 'p3']
