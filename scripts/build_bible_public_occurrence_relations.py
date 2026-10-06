#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

RELATION_STRENGTH = {
    'near-direct-scriptural-phrase': 5,
    'explicit-scriptural-title-or-figure': 5,
    'explicit-biblical-vocabulary-at-time': 5,
    'explicit-Christian-vocabulary-at-time': 4,
    'explicit-at-time': 4,
    'mixed-explicit-scriptural-vocabulary': 4,
    'mixed-explicit-and-later': 4,
    'later-structural-comparator': 3,
    'project-conflation-requiring-correction': 2,
}


def human_join(items: list[str]) -> str:
    clean = [str(item).strip() for item in items if str(item).strip()]
    if not clean:
        return 'the cited biblical material'
    if len(clean) == 1:
        return clean[0]
    if len(clean) == 2:
        return f'{clean[0]} and {clean[1]}'
    return f"{', '.join(clean[:-1])}, and {clean[-1]}"


def build_reader_reading(refs: list[str], significance: str, mismatch: str | None = None) -> str:
    opening = f"The closest biblical neighbors are {human_join(refs)}."
    parts = [opening, str(significance or '').strip()]
    if mismatch:
        parts.append(str(mismatch).strip())
    return ' '.join(part for part in parts if part)


def build_relations(occurrence_index: dict, source_ledger: dict) -> list[dict]:
    sources = {
        str(row.get('id')): row
        for row in source_ledger.get('occurrences', [])
        if row.get('id')
    }
    rows: list[dict] = []
    for occurrence in occurrence_index.get('occurrences', []):
        source_id = str(occurrence.get('source_id') or '').strip()
        source = sources.get(source_id)
        if not source or not source.get('quote'):
            continue
        refs = [str(ref) for ref in occurrence.get('biblical_texts', []) if ref]
        relation_class = str(occurrence.get('biblical_relation') or 'comparative').strip()
        motifs = [str(m) for m in occurrence.get('timic_motifs', []) if m]
        mismatch = occurrence.get('mismatch')
        row = {
            'id': f'public-x-bible-{source_id}',
            'project_concept': ' · '.join(motifs) or 'Public Tim/Bible occurrence',
            'project_expression': source['quote'],
            'exact_wording': source['quote'],
            'date': occurrence.get('date') or source.get('date'),
            'source_direction': 'project_to_bible',
            'relation_type': relation_class.replace('-', '_'),
            'strength': RELATION_STRENGTH.get(relation_class, 3),
            'biblical_refs': refs,
            'reader_reading': build_reader_reading(refs, occurrence.get('significance', ''), mismatch),
            'analysis': occurrence.get('significance', ''),
            'occurrence_ids': [source_id],
            'source_refs': [
                'knowledge/traditions/rational-potato-x-biblical-reference-occurrence-index-2024-2026.json',
                'data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json',
            ],
            'evidence_class': 'P0-public-occurrence',
            'provenance_note': 'Exact wording is joined from the curated public X occurrence ledger by source_id; the Bible mapping remains owned by the occurrence-level biblical index.',
        }
        if source.get('source_url'):
            row['source_url'] = source['source_url']
        if source.get('status_id'):
            row['status_id'] = str(source['status_id'])
        if mismatch:
            row['counterpoint'] = str(mismatch)
        if occurrence.get('existing_overlap_id'):
            row['related_relation_ids'] = [str(occurrence['existing_overlap_id'])]
        rows.append(row)
    return rows


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    occurrence_path = root / 'knowledge' / 'traditions' / 'rational-potato-x-biblical-reference-occurrence-index-2024-2026.json'
    source_path = root / 'data' / 'evidence' / 'rational-potato-x-occurrence-ledger-2024-2026.json'
    output_path = root / 'knowledge' / 'traditions' / 'public-x-biblical-occurrence-relations.json'
    occurrence_index = json.loads(occurrence_path.read_text(encoding='utf-8'))
    source_ledger = json.loads(source_path.read_text(encoding='utf-8'))
    relations = build_relations(occurrence_index, source_ledger)
    payload = {
        'id': 'public-x-biblical-occurrence-relations',
        'version': '1.0.0',
        'updated': '2026-09-14',
        'purpose': 'Reader-facing Tim-first relation projection of the curated public X/Twitter biblical occurrence index. Exact Tim wording is preserved from the evidence ledger; biblical comparison remains directional and does not establish supernatural identity.',
        'source_owners': [str(occurrence_path.relative_to(root)), str(source_path.relative_to(root))],
        'relations': relations,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'PUBLIC X BIBLE RELATIONS BUILT ({len(relations)} relations)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
