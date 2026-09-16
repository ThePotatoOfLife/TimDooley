from __future__ import annotations

import json
from pathlib import Path
import re


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


def build_role_mentions(evidence_root: dict, definitions: dict, threads: dict) -> dict:
    timeline = _timeline_roots(evidence_root)
    mentions: list[dict] = []
    root_mentions: dict[str, list[str]] = {}

    for definition in sorted(definitions.get('mentions', []), key=lambda row: str(row.get('id') or '')):
        mention_id = str(definition.get('id') or '').strip()
        if not mention_id:
            continue
        terms = [str(term).strip().lower() for term in definition.get('terms', []) if str(term).strip()]
        attestations: list[dict] = []
        for root in timeline:
            matched = _matched_terms(str(root.get('quote') or ''), terms)
            if not matched:
                continue
            root_id = str(root.get('id') or '')
            timestamp = str(root.get('timestamp_utc') or '')
            date_value = str(root.get('date') or timestamp[:10] or '')
            attestations.append({
                'root_id': root_id,
                'timestamp_utc': timestamp or None,
                'date': date_value,
                'matched_terms': matched,
            })
            root_mentions.setdefault(root_id, []).append(mention_id)

        if not attestations:
            continue
        active_months = sorted({str(row.get('date') or '')[:7] for row in attestations if str(row.get('date') or '')[:7]})
        timestamps = [str(row.get('timestamp_utc')) for row in attestations if row.get('timestamp_utc')]
        mentions.append({
            'id': mention_id,
            'label': str(definition.get('label') or mention_id),
            'terms': sorted(set(terms)),
            'attestation_basis': 'explicit_literal_terms',
            'attestation_count': len(attestations),
            'root_ids': [row['root_id'] for row in attestations],
            'attestations': attestations,
            'first_attestation_utc': timestamps[0] if timestamps else None,
            'last_attestation_utc': timestamps[-1] if timestamps else None,
            'active_months': active_months,
            'actor_assignments': [],
            'interpretive_claims': [],
        })

    root_mentions = {
        root_id: sorted(set(values))
        for root_id, values in sorted(root_mentions.items())
    }

    function_overlap: dict[str, dict] = {}
    for thread in sorted(threads.get('threads', []), key=lambda row: str(row.get('id') or '')):
        thread_id = str(thread.get('id') or '').strip()
        if not thread_id:
            continue
        counts: dict[str, int] = {}
        root_ids = [str(root_id) for root_id in thread.get('root_ids') or []]
        for root_id in root_ids:
            for mention_id in root_mentions.get(root_id, []):
                counts[mention_id] = counts.get(mention_id, 0) + 1
        function_overlap[thread_id] = {
            'root_count': len(root_ids),
            'role_mention_ids': sorted(counts),
            'role_mention_counts': {key: counts[key] for key in sorted(counts)},
        }

    mentions.sort(key=lambda row: (str(row.get('first_attestation_utc') or '9999'), str(row.get('id') or '')))
    return {
        'id': 'public-statement-role-mentions',
        'version': '1.0.0',
        'model': 'literal-dated-role-title-mentions',
        'source_root_id': str(evidence_root.get('id') or ''),
        'source_thread_id': str(threads.get('id') or ''),
        'definition_source_id': str(definitions.get('id') or ''),
        'assignment_policy': 'mentions_do_not_establish_actor_role_assignments',
        'mentions': mentions,
        'root_mentions': root_mentions,
        'function_overlap': function_overlap,
    }


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    root = json.loads((repository_root / 'data/evidence/public-statement-evidence-root.json').read_text(encoding='utf-8'))
    definitions = json.loads((repository_root / 'data/evidence/public-statement-role-mention-definitions.json').read_text(encoding='utf-8'))
    threads = json.loads((repository_root / 'data/evidence/public-statement-development-threads.json').read_text(encoding='utf-8'))
    payload = build_role_mentions(root, definitions, threads)
    output = repository_root / 'data/evidence/public-statement-role-mentions.json'
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"PUBLIC STATEMENT ROLE MENTIONS BUILT ({len(payload['mentions'])} mention classes)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
