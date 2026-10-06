from __future__ import annotations


def validate_role_mentions(payload: dict, root_ids: set[str], threads: dict) -> list[str]:
    errors: list[str] = []
    if payload.get('id') != 'public-statement-role-mentions':
        errors.append('role mention payload id must be public-statement-role-mentions')
    if payload.get('model') != 'literal-dated-role-title-mentions':
        errors.append('role mention model must be literal-dated-role-title-mentions')
    if payload.get('assignment_policy') != 'mentions_do_not_establish_actor_role_assignments':
        errors.append('role mention assignment policy must forbid inferred actor-role assignments')

    mention_ids: set[str] = set()
    derived_root_mentions: dict[str, set[str]] = {}
    for index, mention in enumerate(payload.get('mentions') or []):
        prefix = f'mention[{index}]'
        mention_id = str(mention.get('id') or '').strip()
        if not mention_id:
            errors.append(f'{prefix}: missing id')
            continue
        if mention_id in mention_ids:
            errors.append(f'{prefix}: duplicate id {mention_id}')
        mention_ids.add(mention_id)
        if mention.get('attestation_basis') != 'explicit_literal_terms':
            errors.append(f'{prefix}: attestation_basis must be explicit_literal_terms')
        terms = {str(term).strip().lower() for term in mention.get('terms') or [] if str(term).strip()}
        if not terms:
            errors.append(f'{prefix}: terms must be non-empty')
        if mention.get('actor_assignments'):
            errors.append(f'{prefix}: role mention observations cannot contain actor assignments')
        if mention.get('interpretive_claims'):
            errors.append(f'{prefix}: role mention observations cannot contain interpretive claims')

        members = [str(root_id) for root_id in mention.get('root_ids') or []]
        attestations = mention.get('attestations') or []
        if len(members) != len(set(members)):
            errors.append(f'{prefix}: duplicate root member')
        if mention.get('attestation_count') != len(attestations):
            errors.append(f'{prefix}: attestation_count does not match attestations')
        if [str(row.get('root_id') or '') for row in attestations] != members:
            errors.append(f'{prefix}: attestations do not match root_ids')
        for root_id in members:
            if root_id not in root_ids:
                errors.append(f'{prefix}: unknown Root {root_id}')
            derived_root_mentions.setdefault(root_id, set()).add(mention_id)
        for row_index, attestation in enumerate(attestations):
            matched = [str(term).strip().lower() for term in attestation.get('matched_terms') or []]
            if not matched:
                errors.append(f'{prefix}.attestation[{row_index}]: matched_terms must be non-empty')
            for term in matched:
                if term not in terms:
                    errors.append(f'{prefix}.attestation[{row_index}]: undeclared matched term {term}')

    actual_root_mentions = {
        str(root_id): sorted(str(value) for value in values)
        for root_id, values in (payload.get('root_mentions') or {}).items()
    }
    expected_root_mentions = {
        root_id: sorted(values)
        for root_id, values in sorted(derived_root_mentions.items())
    }
    if actual_root_mentions != expected_root_mentions:
        errors.append('root_mentions index does not match mention attestations')

    thread_map = {
        str(thread.get('id')): [str(root_id) for root_id in thread.get('root_ids') or []]
        for thread in threads.get('threads', [])
        if thread.get('id')
    }
    overlap = payload.get('function_overlap') or {}
    if set(overlap) != set(thread_map):
        errors.append('function_overlap keys must match Development Thread ids exactly')
    for thread_id, members in thread_map.items():
        counts: dict[str, int] = {}
        for root_id in members:
            for mention_id in actual_root_mentions.get(root_id, []):
                counts[mention_id] = counts.get(mention_id, 0) + 1
        expected = {
            'root_count': len(members),
            'role_mention_ids': sorted(counts),
            'role_mention_counts': {key: counts[key] for key in sorted(counts)},
        }
        if overlap.get(thread_id) != expected:
            errors.append(f'function_overlap[{thread_id}] does not match Root/thread evidence')

    return errors
