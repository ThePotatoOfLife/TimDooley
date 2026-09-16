from scripts.validate_public_statement_episodes import validate_episodes


def valid_payload():
    return {
        'id': 'public-statement-episodes',
        'model': 'rooted-spiral-episodes',
        'source_root_id': 'public-statement-evidence-root',
        'episodes': [
            {
                'id': 'episode-a',
                'label': 'Neutral sequence',
                'status': 'candidate',
                'start_utc': '2026-09-13T16:58:53Z',
                'end_utc': '2026-09-14T08:11:59Z',
                'minimum_members': 2,
                'member_count': 2,
                'member_root_ids': ['a', 'b'],
                'relation_ids': [],
                'interpretive_claims': [],
            }
        ],
        'gaps': [],
    }


def test_valid_candidate_episode_passes():
    assert validate_episodes(valid_payload(), {'a', 'b'}) == []


def test_episode_members_must_resolve_to_roots():
    payload = valid_payload()
    payload['episodes'][0]['member_root_ids'].append('missing')
    payload['episodes'][0]['member_count'] = 3
    assert any('unknown root' in e for e in validate_episodes(payload, {'a', 'b'}))


def test_member_count_and_minimum_are_enforced():
    payload = valid_payload()
    payload['episodes'][0]['member_count'] = 99
    errors = validate_episodes(payload, {'a', 'b'})
    assert any('member_count' in e for e in errors)

    payload = valid_payload()
    payload['episodes'][0]['minimum_members'] = 3
    errors = validate_episodes(payload, {'a', 'b'})
    assert any('minimum_members' in e for e in errors)


def test_candidate_episode_cannot_ship_interpretive_claims():
    payload = valid_payload()
    payload['episodes'][0]['interpretive_claims'] = ['Unsupported conclusion']
    assert any('candidate episode' in e for e in validate_episodes(payload, {'a', 'b'}))


def test_episode_bounds_must_be_ordered():
    payload = valid_payload()
    payload['episodes'][0]['start_utc'] = '2026-09-15T00:00:00Z'
    assert any('invalid bounds' in e for e in validate_episodes(payload, {'a', 'b'}))
