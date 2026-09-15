from scripts.validate_public_statement_rooted_stack import validate_built_stack


def test_valid_built_stack_passes():
    root = {
        'id': 'public-statement-evidence-root',
        'roots': [{'id': 'a'}, {'id': 'b'}],
        'traversals': {'chronological': ['a', 'b']},
    }
    frontier = {
        'id': 'public-statement-discovery-frontier',
        'source_root_id': 'public-statement-evidence-root',
        'gaps': [{'id': 'g1', 'state': 'open'}],
        'work_queue': [{'gap_id': 'g1'}],
        'summary': {'open_total': 1},
    }
    episodes = {
        'id': 'public-statement-episodes',
        'source_root_id': 'public-statement-evidence-root',
        'episodes': [{'id': 'e1', 'member_root_ids': ['a', 'b']}],
        'gaps': [],
    }
    projection = {
        'id': 'public-statement-bible-projection',
        'source_root_id': 'public-statement-evidence-root',
        'source_episode_id': 'public-statement-episodes',
        'root_relations': {'a': ['r1']},
        'episode_relations': {'e1': {'relation_ids': ['r1'], 'inheritance': 'member_union', 'sequence_relation_ids': []}},
        'gaps': [],
    }
    assert validate_built_stack(root, frontier, episodes, projection) == []


def test_frontier_queue_must_cover_every_open_gap_once():
    root = {'id': 'public-statement-evidence-root', 'roots': [], 'traversals': {'chronological': []}}
    frontier = {
        'id': 'public-statement-discovery-frontier',
        'source_root_id': root['id'],
        'gaps': [{'id': 'g1', 'state': 'open'}, {'id': 'g2', 'state': 'open'}],
        'work_queue': [{'gap_id': 'g1'}],
        'summary': {'open_total': 2},
    }
    episodes = {'id': 'public-statement-episodes', 'source_root_id': root['id'], 'episodes': [], 'gaps': []}
    projection = {'id': 'public-statement-bible-projection', 'source_root_id': root['id'], 'source_episode_id': episodes['id'], 'root_relations': {}, 'episode_relations': {}, 'gaps': []}
    assert any('work_queue' in error for error in validate_built_stack(root, frontier, episodes, projection))


def test_episode_and_projection_must_point_back_to_same_root():
    root = {'id': 'public-statement-evidence-root', 'roots': [], 'traversals': {'chronological': []}}
    frontier = {'id': 'public-statement-discovery-frontier', 'source_root_id': root['id'], 'gaps': [], 'work_queue': [], 'summary': {'open_total': 0}}
    episodes = {'id': 'public-statement-episodes', 'source_root_id': 'wrong-root', 'episodes': [], 'gaps': []}
    projection = {'id': 'public-statement-bible-projection', 'source_root_id': root['id'], 'source_episode_id': episodes['id'], 'root_relations': {}, 'episode_relations': {}, 'gaps': []}
    assert any('source_root_id' in error for error in validate_built_stack(root, frontier, episodes, projection))
