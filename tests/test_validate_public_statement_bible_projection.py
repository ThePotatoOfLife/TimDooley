from scripts.validate_public_statement_bible_projection import validate_bible_projection


def valid_projection():
    return {
        'id': 'public-statement-bible-projection',
        'model': 'rooted-reference-projection',
        'root_relations': {'root-a': ['rel-a']},
        'episode_relations': {
            'episode-a': {
                'relation_ids': ['rel-a'],
                'inheritance': 'member_union',
                'sequence_relation_ids': [],
            }
        },
        'gaps': [
            {
                'id': 'gap-bible-projection-rel-b',
                'gap_type': 'comparator',
                'state': 'open',
                'reason': 'unresolved_occurrence_reference',
                'relation_id': 'rel-b',
                'candidate_root_ids': [],
            }
        ],
    }


def test_valid_reference_projection_passes():
    assert validate_bible_projection(valid_projection(), {'root-a'}, {'episode-a'}, {'rel-a', 'rel-b'}) == []


def test_unknown_root_and_episode_fail():
    payload = valid_projection()
    payload['root_relations']['missing-root'] = ['rel-a']
    payload['episode_relations']['missing-episode'] = payload['episode_relations']['episode-a']
    errors = validate_bible_projection(payload, {'root-a'}, {'episode-a'}, {'rel-a', 'rel-b'})
    assert any('unknown root' in e for e in errors)
    assert any('unknown episode' in e for e in errors)


def test_unknown_relation_reference_fails():
    payload = valid_projection()
    payload['root_relations']['root-a'] = ['missing-rel']
    assert any('unknown relation' in e for e in validate_bible_projection(payload, {'root-a'}, {'episode-a'}, {'rel-a', 'rel-b'}))


def test_member_inheritance_cannot_masquerade_as_sequence_relation():
    payload = valid_projection()
    payload['episode_relations']['episode-a']['sequence_relation_ids'] = ['rel-a']
    assert any('sequence_relation_ids' in e for e in validate_bible_projection(payload, {'root-a'}, {'episode-a'}, {'rel-a', 'rel-b'}))
