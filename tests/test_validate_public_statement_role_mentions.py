from scripts.validate_public_statement_role_mentions import validate_role_mentions


def valid_payload():
    return {
        'id': 'public-statement-role-mentions',
        'model': 'literal-dated-role-title-mentions',
        'assignment_policy': 'mentions_do_not_establish_actor_role_assignments',
        'mentions': [
            {
                'id': 'father',
                'attestation_basis': 'explicit_literal_terms',
                'terms': ['father'],
                'attestation_count': 1,
                'root_ids': ['r1'],
                'attestations': [{'root_id': 'r1', 'matched_terms': ['father']}],
                'actor_assignments': [],
                'interpretive_claims': [],
            }
        ],
        'root_mentions': {'r1': ['father']},
        'function_overlap': {
            'source-house-dwelling': {
                'root_count': 1,
                'role_mention_ids': ['father'],
                'role_mention_counts': {'father': 1},
            }
        },
    }


def threads():
    return {'threads': [{'id': 'source-house-dwelling', 'root_ids': ['r1']}]}


def test_valid_role_mentions_pass():
    assert validate_role_mentions(valid_payload(), {'r1'}, threads()) == []


def test_role_mentions_reject_actor_assignment_and_interpretation():
    payload = valid_payload()
    payload['mentions'][0]['actor_assignments'] = [{'actor': 'someone', 'role': 'father'}]
    payload['mentions'][0]['interpretive_claims'] = ['identity claim']
    errors = validate_role_mentions(payload, {'r1'}, threads())
    assert any('actor assignments' in error for error in errors)
    assert any('interpretive claims' in error for error in errors)


def test_role_mentions_require_resolved_roots_and_exact_indexes():
    payload = valid_payload()
    payload['mentions'][0]['root_ids'] = ['missing']
    payload['mentions'][0]['attestations'] = [{'root_id': 'missing', 'matched_terms': ['father']}]
    errors = validate_role_mentions(payload, {'r1'}, threads())
    assert any('unknown Root missing' in error for error in errors)
    assert any('root_mentions index does not match' in error for error in errors)


def test_function_overlap_must_be_recomputable_from_thread_membership():
    payload = valid_payload()
    payload['function_overlap']['source-house-dwelling']['role_mention_counts'] = {'father': 2}
    errors = validate_role_mentions(payload, {'r1'}, threads())
    assert any('function_overlap[source-house-dwelling]' in error for error in errors)
