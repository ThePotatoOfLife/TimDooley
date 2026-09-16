from scripts.build_public_statement_role_mentions import build_role_mentions


def _root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'r1', 'timestamp_utc': '2026-03-01T10:00:00Z', 'date': '2026-03-01', 'quote': 'I am the Father and my son is the Messiah.'},
            {'id': 'r2', 'timestamp_utc': '2026-04-01T10:00:00Z', 'date': '2026-04-01', 'quote': 'Jesus is the door. Odin is the father.'},
            {'id': 'r3', 'timestamp_utc': '2026-05-01T10:00:00Z', 'date': '2026-05-01', 'quote': 'The kingdom grows. This is not a king statement.'},
        ],
        'traversals': {'chronological': ['r1', 'r2', 'r3']},
    }


def _definitions():
    return {
        'id': 'public-statement-role-mention-definitions',
        'mentions': [
            {'id': 'father', 'terms': ['father', 'father in heaven']},
            {'id': 'son', 'terms': ['son', 'my son']},
            {'id': 'messiah', 'terms': ['messiah', 'moshiach']},
            {'id': 'king', 'terms': ['king', 'king of kings']},
            {'id': 'jesus-christ', 'terms': ['jesus', 'jesus christ', 'christ']},
            {'id': 'odin', 'terms': ['odin']},
        ],
    }


def _threads():
    return {
        'id': 'public-statement-development-threads',
        'threads': [
            {'id': 'threshold-door-gate', 'root_ids': ['r2']},
            {'id': 'growth-seed-root-tree-garden', 'root_ids': ['r3']},
        ],
    }


def test_mentions_are_literal_observations_not_role_assignments():
    payload = build_role_mentions(_root(), _definitions(), _threads())
    father = next(row for row in payload['mentions'] if row['id'] == 'father')
    assert father['root_ids'] == ['r1', 'r2']
    assert [row['matched_terms'] for row in father['attestations']] == [['father'], ['father']]
    assert father['actor_assignments'] == []
    assert father['interpretive_claims'] == []
    assert payload['assignment_policy'] == 'mentions_do_not_establish_actor_role_assignments'


def test_role_words_use_word_boundaries():
    payload = build_role_mentions(_root(), _definitions(), _threads())
    king = next(row for row in payload['mentions'] if row['id'] == 'king')
    assert king['root_ids'] == ['r3']
    assert king['attestations'][0]['matched_terms'] == ['king']


def test_root_index_records_co_mentions_without_inference():
    payload = build_role_mentions(_root(), _definitions(), _threads())
    assert payload['root_mentions']['r1'] == ['father', 'messiah', 'son']
    assert payload['root_mentions']['r2'] == ['father', 'jesus-christ', 'odin']
    assert payload['root_mentions']['r3'] == ['king']


def test_function_overlap_is_reference_only():
    payload = build_role_mentions(_root(), _definitions(), _threads())
    threshold = payload['function_overlap']['threshold-door-gate']
    assert threshold == {
        'root_count': 1,
        'role_mention_ids': ['father', 'jesus-christ', 'odin'],
        'role_mention_counts': {'father': 1, 'jesus-christ': 1, 'odin': 1},
    }
    growth = payload['function_overlap']['growth-seed-root-tree-garden']
    assert growth == {
        'root_count': 1,
        'role_mention_ids': ['king'],
        'role_mention_counts': {'king': 1},
    }


def test_mention_timeline_is_dated_and_deterministic():
    payload = build_role_mentions(_root(), _definitions(), _threads())
    father = next(row for row in payload['mentions'] if row['id'] == 'father')
    assert father['first_attestation_utc'] == '2026-03-01T10:00:00Z'
    assert father['last_attestation_utc'] == '2026-04-01T10:00:00Z'
    assert father['active_months'] == ['2026-03', '2026-04']
    assert father['attestation_count'] == 2
