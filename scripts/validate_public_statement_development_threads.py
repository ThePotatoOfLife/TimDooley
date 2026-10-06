from __future__ import annotations


def _ratio_in_range(value) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return 0.0 <= number <= 1.0


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

        declared_episode_ids = [str(value) for value in thread.get('episode_ids') or []]
        for episode_id in declared_episode_ids:
            if episode_id not in episode_ids:
                errors.append(f'{prefix}: unknown episode {episode_id}')
        declared_relation_ids = [str(value) for value in thread.get('bible_relation_ids') or []]
        for relation_id in declared_relation_ids:
            if relation_id not in relation_ids:
                errors.append(f'{prefix}: unknown Bible relation {relation_id}')

        persistence = thread.get('persistence')
        if not isinstance(persistence, dict):
            errors.append(f'{prefix}: missing persistence metrics')
            continue
        dimensions = persistence.get('dimensions')
        if not isinstance(dimensions, dict):
            errors.append(f'{prefix}: missing persistence dimensions')
            continue
        required_dimensions = {'span', 'recurrence', 'distribution', 'support'}
        missing_dimensions = required_dimensions - set(dimensions)
        if missing_dimensions:
            errors.append(f'{prefix}: missing persistence dimensions {sorted(missing_dimensions)}')
            continue

        span = dimensions['span']
        recurrence = dimensions['recurrence']
        distribution = dimensions['distribution']
        support = dimensions['support']

        if persistence.get('span_days') != span.get('days'):
            errors.append(f'{prefix}: persistence span_days disagrees with span dimension')
        if persistence.get('active_month_count') != len(persistence.get('active_months') or []):
            errors.append(f'{prefix}: active_month_count disagrees with active_months')
        if persistence.get('term_diversity_count') != len(persistence.get('matched_terms') or []):
            errors.append(f'{prefix}: term_diversity_count disagrees with matched_terms')
        if persistence.get('episode_count') != len(declared_episode_ids):
            errors.append(f'{prefix}: episode_count disagrees with episode_ids')
        if persistence.get('bible_relation_count') != len(declared_relation_ids):
            errors.append(f'{prefix}: bible_relation_count disagrees with Bible relation IDs')

        intervals = recurrence.get('interval_days') or []
        expected_reappearances = max(len(attestations) - 1, 0)
        if recurrence.get('reappearance_count') != expected_reappearances:
            errors.append(f'{prefix}: reappearance_count disagrees with attestations')
        if len(intervals) != expected_reappearances:
            errors.append(f'{prefix}: interval_days length disagrees with attestations')
        if intervals and recurrence.get('longest_gap_days') != max(intervals):
            errors.append(f'{prefix}: longest_gap_days disagrees with interval_days')

        monthly_counts = distribution.get('attestations_by_month') or {}
        if sum(int(value) for value in monthly_counts.values()) != len(attestations):
            errors.append(f'{prefix}: monthly attestation counts do not sum to attestation_count')
        if monthly_counts and distribution.get('max_month_attestations') != max(monthly_counts.values()):
            errors.append(f'{prefix}: max_month_attestations disagrees with monthly counts')

        support_count_fields = [
            'episode_attestation_count',
            'bible_attestation_count',
            'second_precision_attestation_count',
        ]
        for field in support_count_fields:
            value = int(support.get(field) or 0)
            if value < 0 or value > len(attestations):
                errors.append(f'{prefix}: support {field} outside attestation bounds')
        for field in ['episode_coverage_ratio', 'bible_attestation_ratio', 'second_precision_ratio']:
            if not _ratio_in_range(support.get(field)):
                errors.append(f'{prefix}: support {field} must be between 0 and 1')
        if not _ratio_in_range(span.get('temporal_coverage_ratio')):
            errors.append(f'{prefix}: temporal_coverage_ratio must be between 0 and 1')
        if not _ratio_in_range(distribution.get('max_month_share')):
            errors.append(f'{prefix}: max_month_share must be between 0 and 1')

        tests = persistence.get('tests') or {}
        passed_count = sum(1 for test in tests.values() if test.get('passed') is True)
        if persistence.get('test_count') != len(tests):
            errors.append(f'{prefix}: test_count disagrees with persistence tests')
        if persistence.get('passed_test_count') != passed_count:
            errors.append(f'{prefix}: passed_test_count disagrees with persistence tests')
        if persistence.get('all_core_tests_passed') is not (passed_count == len(tests)):
            errors.append(f'{prefix}: all_core_tests_passed disagrees with persistence tests')

    for index, gap in enumerate(payload.get('gaps') or []):
        prefix = f'gap[{index}]'
        if gap.get('gap_type') != 'relationship':
            errors.append(f'{prefix}: Development Thread gap_type must be relationship')
        for root_id in gap.get('candidate_root_ids') or []:
            if root_id not in root_ids:
                errors.append(f'{prefix}: unknown candidate root {root_id}')

    return errors
