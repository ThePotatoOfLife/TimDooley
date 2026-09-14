#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from bible_corpus import assemble_fragments, assemble_relations, assemble_scenes, load_manifest

PROMOTABLE_SEPTEMBER_CLASSES = {
    'direct', 'direct_cluster', 'direct_motif', 'strong', 'thematic', 'tension'
}

BOOK_RE = re.compile(r'^((?:[1-3]\s+)?[A-Za-z]+(?:\s+(?:of\s+)?[A-Za-z]+)*)\s+\d')


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def book_from_ref(reference: object) -> str | None:
    text = str(reference or '').strip()
    if not text or text.lower().startswith('generic '):
        return None
    match = BOOK_RE.match(text)
    if match:
        return match.group(1)
    return None


def relation_refs(row: dict) -> list[str]:
    refs = []
    for key in ('biblical_refs', 'biblical_texts', 'texts'):
        refs.extend(str(item) for item in as_list(row.get(key)) if item)
    return list(dict.fromkeys(refs))


def exact_wording(row: dict) -> bool:
    return any(bool(row.get(key)) for key in ('exact_wording', 'project_quote', 'quote', 'tim_quote'))


def public_x_source(row: dict) -> bool:
    url = str(row.get('source_url') or '')
    if 'x.com/' in url or 'twitter.com/' in url:
        return True
    discovery = str(row.get('discovery_mode') or '').lower()
    if discovery == 'public-occurrence':
        return True
    owners = ' '.join(str(v) for v in as_list(row.get('owners'))).lower()
    return 'rational-potato-x' in owners or bool(row.get('occurrence_ids'))


def expressive_reading(row: dict) -> bool:
    return any(bool(row.get(key)) for key in ('reader_reading', 'expressive_reading', 'reading', 'reader_narrative'))


def occurrence_rows(data: dict) -> list[dict]:
    return list(data.get('records') or data.get('occurrences') or [])


def occurrence_key(row: dict) -> str | None:
    for key in ('status_id', 'status', 'source_id', 'id'):
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def build_report(root: Path, manifest: dict, september: dict, public_x: dict) -> dict:
    relations = assemble_relations(root, manifest)
    scenes = assemble_scenes(root, manifest)
    fragments = assemble_fragments(root, manifest)

    book_counts: Counter[str] = Counter()
    source_direction_counts: Counter[str] = Counter()
    relation_type_counts: Counter[str] = Counter()
    strength_counts: Counter[str] = Counter()

    for row in relations:
        for reference in relation_refs(row):
            book = book_from_ref(reference)
            if book:
                book_counts[book] += 1
        if row.get('source_direction'):
            source_direction_counts[str(row['source_direction'])] += 1
        relation_type = row.get('relation_type') or row.get('relation_class') or row.get('classification')
        if relation_type:
            relation_type_counts[str(relation_type)] += 1
        if row.get('strength') is not None:
            strength_counts[str(row['strength'])] += 1

    september_rows = occurrence_rows(september)
    september_classes = Counter(str(row.get('class') or 'unclassified') for row in september_rows)

    public_rows = occurrence_rows(public_x)
    public_keys = [key for row in public_rows if (key := occurrence_key(row))]
    key_counts = Counter(public_keys)
    duplicate_keys = sorted(key for key, count in key_counts.items() if count > 1)

    promoted_keys = set()
    for row in relations:
        promoted_keys.update(str(v) for v in as_list(row.get('occurrence_ids')) if v)
        for key in ('status_id', 'status'):
            if row.get(key):
                promoted_keys.add(str(row[key]))

    september_keys = {occurrence_key(row) for row in september_rows if occurrence_key(row)}
    september_promoted = sorted(september_keys & promoted_keys)
    promotable_rows = [
        row for row in september_rows
        if str(row.get('class') or '').lower() in PROMOTABLE_SEPTEMBER_CLASSES
    ]
    promotable_keys = {occurrence_key(row) for row in promotable_rows if occurrence_key(row)}

    report = {
        'id': 'bible-comparator-coverage-report',
        'version': '1.0.0',
        'purpose': 'Deterministic census of the active manifest corpus, public X occurrence coverage, September 2026 review coverage, and reader-facing expressive depth.',
        'active_relation_count': len(relations),
        'active_scene_count': len(scenes),
        'active_fragment_count': len(fragments),
        'relations_with_exact_wording': sum(1 for row in relations if exact_wording(row)),
        'relations_with_public_x_source': sum(1 for row in relations if public_x_source(row)),
        'expressive_reading_count': sum(1 for row in relations if expressive_reading(row)),
        'september_status_count': len(september_rows),
        'september_class_counts': dict(sorted(september_classes.items())),
        'september_promotable_count': len(promotable_rows),
        'september_promoted_count': len(september_promoted),
        'september_promoted_ids': september_promoted,
        'september_promotable_unpromoted_ids': sorted(promotable_keys - promoted_keys),
        'public_x_occurrence_count': len(public_rows),
        'public_x_unique_status_count': len(set(public_keys)),
        'public_x_duplicate_status_ids': duplicate_keys,
        'bible_book_counts': dict(sorted(book_counts.items(), key=lambda item: (-item[1], item[0]))),
        'source_direction_counts': dict(sorted(source_direction_counts.items())),
        'relation_type_counts': dict(sorted(relation_type_counts.items())),
        'strength_counts': dict(sorted(strength_counts.items(), key=lambda item: item[0])),
    }
    if relations:
        report['exact_wording_rate'] = round(report['relations_with_exact_wording'] / len(relations), 4)
        report['public_x_source_rate'] = round(report['relations_with_public_x_source'] / len(relations), 4)
        report['expressive_reading_rate'] = round(report['expressive_reading_count'] / len(relations), 4)
    else:
        report['exact_wording_rate'] = 0.0
        report['public_x_source_rate'] = 0.0
        report['expressive_reading_rate'] = 0.0
    return report


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = load_manifest(root)
    september = load_json(root / 'knowledge' / 'traditions' / 'september-2026-x-overlap-all-75.json')
    public_x = load_json(root / 'knowledge' / 'traditions' / 'rational-potato-x-biblical-reference-occurrence-index-2024-2026.json')
    report = build_report(root, manifest, september, public_x)
    output = root / 'knowledge' / 'indexes' / 'bible-comparator-coverage-report.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(
        'BIBLE COMPARATOR COVERAGE BUILT '
        f"({report['active_relation_count']} relations, {report['active_scene_count']} scenes, "
        f"{report['september_status_count']} September statuses)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
