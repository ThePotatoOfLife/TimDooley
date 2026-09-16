from scripts.build_public_statement_bible_projection import build_bible_projection


def sample_root():
    return {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'root-a', 'source_occurrence_ids': ['old-a'], 'quote': 'A'},
            {'id': 'root-b', 'source_occurrence_ids': ['old-b'], 'quote': 'B'},
        ],
    }


def sample_episodes():
    return {
        'id': 'public-statement-episodes',
        'episodes': [
            {'id': 'episode-one', 'member_root_ids': ['root-a', 'root-b']},
        ],
    }


def relation_sources():
    return [
        {
            'id': 'relations-one',
            'relations': [
                {'id': 'rel-a', 'occurrence_ids': ['old-a']},
                {'id': 'rel-shared', 'occurrence_ids': ['old-a', 'old-b']},
                {'id': 'rel-orphan', 'occurrence_ids': ['missing']},
            ],
        }
    ]


def test_relations_join_to_roots_by_occurrence_id_only():
    projection = build_bible_projection(sample_root(), sample_episodes(), relation_sources())
    assert projection['root_relations']['root-a'] == ['rel-a', 'rel-shared']
    assert projection['root_relations']['root-b'] == ['rel-shared']


def test_episode_relations_are_member_inheritance_not_sequence_claims():
    projection = build_bible_projection(sample_root(), sample_episodes(), relation_sources())
    episode = projection['episode_relations']['episode-one']
    assert episode['relation_ids'] == ['rel-a', 'rel-shared']
    assert episode['inheritance'] == 'member_union'
    assert episode['sequence_relation_ids'] == []


def test_unmatched_relation_stays_visible_as_projection_gap():
    projection = build_bible_projection(sample_root(), sample_episodes(), relation_sources())
    gap = projection['gaps'][0]
    assert gap['relation_id'] == 'rel-orphan'
    assert gap['reason'] == 'unresolved_occurrence_reference'
    assert gap['occurrence_ids'] == ['missing']


def test_projection_does_not_copy_relation_interpretation():
    sources = relation_sources()
    sources[0]['relations'][0]['analysis'] = 'Interpretive text owned elsewhere.'
    sources[0]['relations'][0]['biblical_refs'] = ['Example 1:1']
    projection = build_bible_projection(sample_root(), sample_episodes(), sources)
    serialized = str(projection)
    assert 'Interpretive text owned elsewhere.' not in serialized
    assert 'Example 1:1' not in serialized


def test_projection_is_relation_source_order_independent():
    first = relation_sources()[0]
    second = {'id': 'relations-two', 'relations': [{'id': 'rel-b', 'occurrence_ids': ['old-b']}]}
    forward = build_bible_projection(sample_root(), sample_episodes(), [first, second])
    reverse = build_bible_projection(sample_root(), sample_episodes(), [second, first])
    assert forward == reverse
