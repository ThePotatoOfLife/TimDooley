from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re


def _timeline_roots(evidence_root: dict) -> list[dict]:
    by_id = {str(row.get('id')): row for row in evidence_root.get('roots', []) if row.get('id')}
    timeline = (evidence_root.get('traversals') or {}).get('chronological') or []
    ordered = [by_id[root_id] for root_id in timeline if root_id in by_id]
    seen = {str(row.get('id')) for row in ordered}
    extras = sorted(
        (row for root_id, row in by_id.items() if root_id not in seen),
        key=lambda row: (str(row.get('timestamp_utc') or row.get('date') or ''), str(row.get('id') or '')),
    )
    return ordered + extras


def _term_pattern(term: str) -> re.Pattern[str]:
    parts = [re.escape(part) for part in str(term).strip().lower().split() if part]
    body = r'\s+'.join(parts)
    return re.compile(rf'(?<!\w){body}(?!\w)', re.IGNORECASE)


def _matched_terms(quote: str, terms: list[str]) -> list[str]:
    text = str(quote or '')
    matched = {
        str(term).strip().lower()
        for term in terms
        if str(term).strip() and _term_pattern(str(term)).search(text)
    }
    return sorted(matched)


def _episode_ids(root_ids: set[str], episodes: dict) -> list[str]:
    values = []
    for episode in episodes.get('episodes', []):
        members = {str(value) for value in episode.get('member_root_ids') or []}
        if root_ids & members:
            values.append(str(episode.get('id')))
    return sorted(value for value in values if value)


def _episode_root_ids(root_ids: set[str], episodes: dict) -> set[str]:
    covered: set[str] = set()
    for episode in episodes.get('episodes', []):
        members = {str(value) for value in episode.get('member_root_ids') or []}
        covered.update(root_ids & members)
    return covered


def _bible_relation_ids(root_ids: set[str], bible_projection: dict) -> list[str]:
    values: set[str] = set()
    root_relations = bible_projection.get('root_relations') or {}
    for root_id in root_ids:
        values.update(str(value) for value in root_relations.get(root_id, []) if value)
    return sorted(values)


def _persistence_metrics(
    attestations: list[dict],
    root_ids: set[str],
    episode_ids: list[str],
    episodes: dict,
    bible_relation_ids: list[str],
    bible_projection: dict,
    policy: dict,
) -> dict:
    attestation_dates = sorted(
        {
            str(row.get('date') or str(row.get('timestamp_utc') or '')[:10])
            for row in attestations
            if str(row.get('date') or str(row.get('timestamp_utc') or '')[:10])
        }
    )
    parsed_dates = [date.fromisoformat(value) for value in attestation_dates]
    span_days = (parsed_dates[-1] - parsed_dates[0]).days if len(parsed_dates) >= 2 else 0
    active_months = sorted({value[:7] for value in attestation_dates if len(value) >= 7})
    matched_terms = sorted(
        {
            str(term).strip().lower()
            for row in attestations
            for term in row.get('matched_terms') or []
            if str(term).strip()
        }
    )
    covered_roots = _episode_root_ids(root_ids, episodes)
    root_relations = bible_projection.get('root_relations') or {}
    bible_attestation_count = sum(1 for root_id in root_ids if root_relations.get(root_id))
    attestation_count = len(attestations)

    thresholds = {
        'cross_episode': int(policy.get('minimum_episode_count') or 0),
        'long_span': int(policy.get('minimum_span_days') or 0),
        'multi_month': int(policy.get('minimum_active_months') or 0),
        'term_diversity': int(policy.get('minimum_term_diversity') or 0),
    }
    observed = {
        'cross_episode': len(episode_ids),
        'long_span': span_days,
        'multi_month': len(active_months),
        'term_diversity': len(matched_terms),
    }
    tests = {
        key: {
            'observed': observed[key],
            'threshold': thresholds[key],
            'passed': observed[key] >= thresholds[key],
        }
        for key in sorted(observed)
    }
    passed_test_count = sum(1 for test in tests.values() if test['passed'])

    return {
        'span_days': span_days,
        'active_months': active_months,
        'active_month_count': len(active_months),
        'matched_terms': matched_terms,
        'term_diversity_count': len(matched_terms),
        'episode_count': len(episode_ids),
        'episode_attestation_count': len(covered_roots),
        'episode_coverage_ratio': len(covered_roots) / attestation_count if attestation_count else 0.0,
        'bible_relation_count': len(bible_relation_ids),
        'bible_attestation_count': bible_attestation_count,
        'bible_attestation_ratio': bible_attestation_count / attestation_count if attestation_count else 0.0,
        'tests': tests,
        'passed_test_count': passed_test_count,
        'test_count': len(tests),
        'all_core_tests_passed': passed_test_count == len(tests),
    }


def build_development_threads(
    evidence_root: dict,
    definitions: dict,
    episodes: dict,
    bible_projection: dict,
) -> dict:
    timeline = _timeline_roots(evidence_root)
    threads: list[dict] = []
    gaps: list[dict] = []
    persistence_policy = dict(definitions.get('persistence_policy') or {})

    for definition in sorted(definitions.get('threads', []), key=lambda row: str(row.get('id') or '')):
        thread_id = str(definition.get('id') or '').strip()
        terms = [str(term).strip().lower() for term in definition.get('terms', []) if str(term).strip()]
        minimum = int(definition.get('minimum_attestations') or 1)
        attestations = []
        for root in timeline:
            matched = _matched_terms(str(root.get('quote') or ''), terms)
            if not matched:
                continue
            timestamp = str(root.get('timestamp_utc') or '')
            attestations.append({
                'root_id': str(root.get('id')),
                'timestamp_utc': timestamp or None,
                'date': str(root.get('date') or timestamp[:10] or ''),
                'matched_terms': matched,
            })

        root_ids = [row['root_id'] for row in attestations]
        if len(attestations) < minimum:
            gaps.append({
                'id': f'gap-development-thread-{thread_id or "unknown"}',
                'gap_type': 'relationship',
                'state': 'open',
                'reason': 'minimum_attestations_not_met',
                'thread_id': thread_id,
                'required_attestations': minimum,
                'observed_attestations': len(attestations),
                'candidate_root_ids': root_ids,
            })
            continue

        root_set = set(root_ids)
        dated = [row for row in attestations if row.get('timestamp_utc')]
        first = dated[0]['timestamp_utc'] if dated else None
        last = dated[-1]['timestamp_utc'] if dated else None
        episode_ids = _episode_ids(root_set, episodes)
        bible_relation_ids = _bible_relation_ids(root_set, bible_projection)
        persistence = _persistence_metrics(
            attestations,
            root_set,
            episode_ids,
            episodes,
            bible_relation_ids,
            bible_projection,
            persistence_policy,
        )
        threads.append({
            'id': thread_id,
            'label': str(definition.get('label') or thread_id),
            'status': str(definition.get('status') or 'candidate'),
            'scope': str(definition.get('scope') or ''),
            'attestation_basis': 'explicit_literal_terms',
            'terms': sorted(set(terms)),
            'attestation_count': len(attestations),
            'root_ids': root_ids,
            'attestations': attestations,
            'first_attestation_utc': first,
            'last_attestation_utc': last,
            'episode_ids': episode_ids,
            'bible_relation_ids': bible_relation_ids,
            'persistence': persistence,
            'actor_assignments': [],
            'interpretive_claims': [],
        })

    threads.sort(
        key=lambda row: (
            str(row.get('first_attestation_utc') or '9999'),
            str(row.get('id') or ''),
        )
    )
    gaps.sort(key=lambda row: str(row.get('id') or ''))
    return {
        'id': 'public-statement-development-threads',
        'version': '1.1.0',
        'model': 'rooted-spiral-development-threads',
        'source_root_id': str(evidence_root.get('id') or ''),
        'definition_source_id': str(definitions.get('id') or ''),
        'source_episode_id': str(episodes.get('id') or ''),
        'source_bible_projection_id': str(bible_projection.get('id') or ''),
        'persistence_policy': persistence_policy,
        'threads': threads,
        'gaps': gaps,
    }


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    root = json.loads((repository_root / 'data/evidence/public-statement-evidence-root.json').read_text(encoding='utf-8'))
    definitions = json.loads((repository_root / 'data/evidence/public-statement-development-thread-definitions.json').read_text(encoding='utf-8'))
    episodes = json.loads((repository_root / 'data/evidence/public-statement-episodes.json').read_text(encoding='utf-8'))
    bible_projection = json.loads((repository_root / 'data/evidence/public-statement-bible-projection.json').read_text(encoding='utf-8'))
    payload = build_development_threads(root, definitions, episodes, bible_projection)
    output = repository_root / 'data/evidence/public-statement-development-threads.json'
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(
        'PUBLIC STATEMENT DEVELOPMENT THREADS BUILT '
        f"({len(payload['threads'])} threads; {len(payload['gaps'])} gaps)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
