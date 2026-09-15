from scripts.build_public_statement_development_threads import build_development_threads


def sample_root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'root-c', 'timestamp_utc': '2026-05-03T10:00:00Z', 'quote': 'We can build bridges together.'},
            {'id': 'root-a', 'timestamp_utc': '2026-03-01T10:00:00Z', 'quote': 'There is a Door beyond the gate.'},
            {'id': 'root-d', 'timestamp_utc': '2026-06-01T10:00:00Z', 'quote': 'This route is unrelated.'},
            {'id': 'root-b', 'timestamp_utc': '2026-04-01T10:00:00Z', 'quote': 'I am the root and the tree in the garden.'},
        ],
        'traversals': {'chronological': ['root-a', 'root-b', 'root-c', 'root-d']},
    }


def definitions():
    return {
        'id': 'public-statement-development-thread-definitions',
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
