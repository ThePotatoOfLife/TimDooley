from __future__ import annotations

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


def _bible_relation_ids(root_ids: set[str], bible_projection: dict) -> list[str]:
    values: set[str] = set()
    root_relations = bible_projection.get('root_relations') or {}
    for root_id in root_ids:
        values.update(str(value) for value in root_relations.get(root_id, []) if value)
    return sorted(values)


def build_development_threads(
    evidence_root: dict,
    definitions: dict,
    episodes: dict,
    bible_projection: dict,
) -> dict:
    timeline = _timeline_roots(evidence_root)
    threads: list[dict] = []
    gaps: list[dict] = []

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
            'episode_ids': _episode_ids(root_set, episodes),
            'bible_relation_ids': _bible_relation_ids(root_set, bible_projection),
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
        'version': '1.0.0',
        'model': 'rooted-spiral-development-threads',
        'source_root_id': str(evidence_root.get('id') or ''),
        'definition_source_id': str(definitions.get('id') or ''),
        'source_episode_id': str(episodes.get('id') or ''),
        'source_bible_projection_id': str(bible_projection.get('id') or ''),
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
