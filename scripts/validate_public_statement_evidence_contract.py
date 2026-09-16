#!/usr/bin/env python3
"""Stdlib-only contract smoke test for the public-statement Evidence Root subsystem."""
from __future__ import annotations

from scripts.public_statement_evidence_root import reconcile_records
from scripts.build_public_statement_evidence_root import build_evidence_root
from scripts.enrich_public_statement_evidence_root import enrich_status_ids
from scripts.import_public_statement_timestamp_capture import parse_capture
from scripts.validate_public_statement_evidence_root import validate_evidence_root
from scripts.build_public_statement_episodes import build_episodes
from scripts.build_public_statement_role_mentions import build_role_mentions
from scripts.build_public_statement_development_threads import build_development_threads


def validate_contract() -> list[str]:
    errors: list[str] = []

    rows = [
        {'id': 'a', 'date': '2026-04-29', 'quote': 'Alpha', 'source_record': 'date-ledger', 'source_occurrence_id': 'a'},
        {'id': 'b', 'date': '2026-04-29', 'timestamp_utc': '2026-04-29T20:05:28Z', 'quote': 'Alpha', 'source_record': 'timestamp-ledger', 'source_occurrence_id': 'b'},
    ]
    reconciled = reconcile_records(rows)
    if len(reconciled) != 1 or reconciled[0].get('precision') != 'second':
        errors.append('reconciliation must prefer precise duplicate evidence without duplicating the root')
    if reconciled and reconciled[0].get('source_records') != ['date-ledger', 'timestamp-ledger']:
        errors.append('reconciliation must preserve both contributing source records')

    sources = [
        {'id': 'date-ledger', 'coverage_notes': [], 'occurrences': [{'id': 'old-a', 'date': '2026-04-29', 'quote': 'Alpha'}]},
        {'id': 'timestamp-ledger', 'coverage_notes': [], 'occurrences': [{'id': 'new-a', 'date': '2026-04-29', 'timestamp_utc': '2026-04-29T20:05:28Z', 'quote': 'Alpha'}]},
    ]
    root = build_evidence_root(sources)
    if root.get('model') != 'rooted-spiral' or len(root.get('roots', [])) != 1:
        errors.append('builder must produce one rooted-spiral statement root for duplicate source observations')

    capture = '- Mon, 14 Sep 2026 08:11:59 GMT: "Alpha statement"\n'
    captured = parse_capture(capture)
    if captured.get('occurrences', [{}])[0].get('timestamp_utc') != '2026-09-14T08:11:59Z':
        errors.append('timestamp capture must preserve second-level UTC precision')

    validation_fixture = {
        'id': 'public-statement-evidence-root',
        'model': 'rooted-spiral',
        'source_owners': ['source-a'],
        'roots': [{
            'id': 'stmt-a', 'kind': 'statement', 'ring': 0,
            'date': '2026-09-14', 'timestamp_utc': '2026-09-14T08:11:59Z',
            'precision': 'second', 'quote': 'Alpha', 'source_records': ['source-a'],
            'provenance': [{'id': 'a'}],
        }],
        'coverage_notes': [],
        'traversals': {'chronological': ['stmt-a']},
        'discovery_gaps': [],
        'reconciliation': {'merged_groups': 0, 'unresolved': []},
    }
    errors.extend(f'root validator: {error}' for error in validate_evidence_root(validation_fixture))

    status_root = {
        'id': 'public-statement-evidence-root',
        'roots': [{'id': 'stmt-a', 'date': '2026-09-14', 'timestamp_utc': '2026-09-14T08:11:59Z', 'quote': 'Alpha'}],
    }
    specialist = {'id': 'status-index', 'records': [{'status_id': '111', 'date': '2026-09-14', 'time_utc': '08:11'}]}
    enriched = enrich_status_ids(status_root, [specialist])
    if enriched.get('roots', [{}])[0].get('status_id') != '111':
        errors.append('status enrichment must attach an unambiguous minute-level status identifier')

    episode_root = {
        'id': 'public-statement-evidence-root',
        'roots': [
            {'id': 'r1', 'timestamp_utc': '2026-03-01T10:00:00Z', 'date': '2026-03-01', 'quote': 'The Father stands at the door.'},
            {'id': 'r2', 'timestamp_utc': '2026-04-01T10:00:00Z', 'date': '2026-04-01', 'quote': 'The gate remains a door.'},
        ],
        'traversals': {'chronological': ['r1', 'r2']},
    }
    episode_defs = {'id': 'episode-defs', 'episodes': [{
        'id': 'e1', 'label': 'Bounded episode', 'status': 'candidate',
        'start_utc': '2026-03-01T10:00:00Z', 'end_utc': '2026-04-01T10:00:00Z',
        'minimum_members': 2, 'evidence_basis': 'bounded sequence',
    }]}
    episodes = build_episodes(episode_root, episode_defs)
    if episodes.get('episodes', [{}])[0].get('member_root_ids') != ['r1', 'r2']:
        errors.append('episode builder must preserve chronological root membership')

    thread_defs = {
        'id': 'thread-defs',
        'persistence_policy': {'minimum_active_months': 2, 'minimum_span_days': 1, 'minimum_term_diversity': 1, 'minimum_episode_count': 1},
        'threads': [{'id': 'threshold-door-gate', 'label': 'Threshold / Door / Gate', 'status': 'candidate', 'terms': ['door', 'gate'], 'minimum_attestations': 1}],
    }
    threads = build_development_threads(episode_root, thread_defs, episodes, {'root_relations': {}})
    if not threads.get('threads') or threads['threads'][0].get('interpretive_claims') != []:
        errors.append('development threads must remain evidence-derived candidates without interpretive promotion')

    role_defs = {'id': 'role-defs', 'mentions': [{'id': 'father', 'terms': ['father']}]}
    roles = build_role_mentions(episode_root, role_defs, threads)
    father = next((row for row in roles.get('mentions', []) if row.get('id') == 'father'), {})
    if father.get('root_ids') != ['r1'] or father.get('actor_assignments') != []:
        errors.append('role mentions must remain literal observations without actor assignment')

    return errors


def main() -> int:
    errors = validate_contract()
    if errors:
        print('PUBLIC STATEMENT EVIDENCE CONTRACT FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print('PUBLIC STATEMENT EVIDENCE CONTRACT PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
