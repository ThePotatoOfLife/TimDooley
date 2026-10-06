from scripts.build_public_statement_episodes import build_episodes


def sample_root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'a', 'timestamp_utc': '2026-09-13T16:58:53Z', 'quote': 'A'},
            {'id': 'b', 'timestamp_utc': '2026-09-13T17:01:32Z', 'quote': 'B'},
            {'id': 'c', 'timestamp_utc': '2026-09-14T08:11:59Z', 'quote': 'C'},
            {'id': 'd', 'timestamp_utc': '2026-09-15T08:17:46Z', 'quote': 'D'},
        ],
        'traversals': {'chronological': ['a', 'b', 'c', 'd']},
    }


def definitions():
    return {
        'id': 'public-statement-episode-definitions',
        'episodes': [
            {
                'id': 'episode-sep13-14',
                'label': 'September 13–14 public-statement burst',
                'status': 'candidate',
                'start_utc': '2026-09-13T16:58:53Z',
                'end_utc': '2026-09-14T08:11:59Z',
                'minimum_members': 3,
                'evidence_basis': 'Bounded high-density statement sequence.',
            }
        ],
    }


def test_episode_membership_uses_root_timestamps_and_timeline_order():
    payload = build_episodes(sample_root(), definitions())
    episode = payload['episodes'][0]
    assert episode['member_root_ids'] == ['a', 'b', 'c']
    assert episode['member_count'] == 3


def test_episode_excludes_roots_outside_bounds():
    payload = build_episodes(sample_root(), definitions())
    assert 'd' not in payload['episodes'][0]['member_root_ids']


def test_episode_remains_candidate_without_interpretive_promotion():
    payload = build_episodes(sample_root(), definitions())
    episode = payload['episodes'][0]
    assert episode['status'] == 'candidate'
    assert episode['relation_ids'] == []
    assert episode['interpretive_claims'] == []


def test_episode_fails_closed_when_minimum_members_not_met():
    defs = definitions()
    defs['episodes'][0]['minimum_members'] = 4
    payload = build_episodes(sample_root(), defs)
    assert payload['episodes'] == []
    assert payload['gaps'][0]['reason'] == 'minimum_members_not_met'
    assert payload['gaps'][0]['candidate_root_ids'] == ['a', 'b', 'c']


def test_episode_build_is_definition_order_independent():
    defs = definitions()
    second = dict(defs['episodes'][0], id='episode-second', label='Second', start_utc='2026-09-15T08:17:46Z', end_utc='2026-09-15T08:17:46Z', minimum_members=1)
    forward = dict(defs, episodes=[defs['episodes'][0], second])
    reverse = dict(defs, episodes=[second, defs['episodes'][0]])
    assert build_episodes(sample_root(), forward) == build_episodes(sample_root(), reverse)
