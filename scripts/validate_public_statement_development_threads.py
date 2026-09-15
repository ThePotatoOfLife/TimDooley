from __future__ import annotations


def validate_development_threads(
    payload: dict,
    root_ids: set[str],
    episode_ids: set[str],
    relation_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    if payload.get('id') != 'public-statement-development-threads':
        errors.append('thread payload id must be public-statement-development-threads')
    if payload.get('model') != 'rooted-spiral-development-threads':
        errors.append('thread payload model must be rooted-spiral-development-threads')

    seen: set[str] = set()
    for index, thread in enumerate(payload.get('threads') or []):
        prefix = f'thread[{index}]'
        thread_id = str(thread.get('id') or '').strip()
        if not thread_id:
            errors.append(f'{prefix}: missing id')
        elif thread_id in seen:
            errors.append(f'{prefix}: duplicate id {thread_id}')
        else:
            seen.add(thread_id)

        if thread.get('attestation_basis') != 'explicit_literal_terms':
            errors.append(f'{prefix}: attestation_basis must be explicit_literal_terms')
        terms = {str(term).strip().lower() for term in thread.get('terms') or [] if str(term).strip()}
        if not terms:
            errors.append(f'{prefix}: terms must be non-empty')

        members = [str(root_id) for root_id in thread.get('root_ids') or []]
        if len(members) != len(set(members)):
            errors.append(f'{prefix}: duplicate root member')
        for root_id in members:
            if root_id not in root_ids:
                errors.append(f'{prefix}: unknown root {root_id}')

        attestations = thread.get('attestations') or []
        attestation_ids = [str(row.get('root_id') or '') for row in attestations]
        if attestation_ids != members:
            errors.append(f'{prefix}: attestations do not match root_ids')
        if thread.get('attestation_count') != len(attestations):
            errors.append(f'{prefix}: attestation_count does not match attestations')
        for row_index, attestation in enumerate(attestations):
            matched = [str(term).strip().lower() for term in attestation.get('matched_terms') or []]
            if not matched:
                errors.append(f'{prefix}.attestation[{row_index}]: matched_terms must be non-empty')
            for term in matched:
                if term not in terms:
                    errors.append(f'{prefix}.attestation[{row_index}]: undeclared matched term {term}')

        status = str(thread.get('status') or '')
        if status not in {'candidate', 'tested', 'consolidated', 'rejected'}:
            errors.append(f'{prefix}: invalid status {status!r}')
        if status == 'candidate' and thread.get('interpretive_claims'):
            errors.append(f'{prefix}: candidate thread cannot contain interpretive claims')
        if status == 'candidate' and thread.get('actor_assignments'):
            errors.append(f'{prefix}: candidate thread cannot contain actor assignments')

        for episode_id in thread.get('episode_ids') or []:
            if episode_id not in episode_ids:
                errors.append(f'{prefix}: unknown episode {episode_id}')
        for relation_id in thread.get('bible_relation_ids') or []:
            if relation_id not in relation_ids:
                errors.append(f'{prefix}: unknown Bible relation {relation_id}')

    for index, gap in enumerate(payload.get('gaps') or []):
        prefix = f'gap[{index}]'
        if gap.get('gap_type') != 'relationship':
            errors.append(f'{prefix}: Development Thread gap_type must be relationship')
        for root_id in gap.get('candidate_root_ids') or []:
            if root_id not in root_ids:
                errors.append(f'{prefix}: unknown candidate root {root_id}')

    return errors
