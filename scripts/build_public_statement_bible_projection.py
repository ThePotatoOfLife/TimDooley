from __future__ import annotations

import json
from pathlib import Path


def build_bible_projection(evidence_root: dict, episodes: dict, relation_sources: list[dict]) -> dict:
    occurrence_to_roots: dict[str, set[str]] = {}
    for root in evidence_root.get('roots', []):
        root_id = str(root.get('id') or '').strip()
        if not root_id:
            continue
        for occurrence_id in root.get('source_occurrence_ids') or []:
            occurrence_to_roots.setdefault(str(occurrence_id), set()).add(root_id)

    root_relations: dict[str, set[str]] = {
        str(root.get('id')): set()
        for root in evidence_root.get('roots', [])
        if root.get('id')
    }
    gaps: list[dict] = []
    source_ids: list[str] = []

    for source in sorted(relation_sources, key=lambda row: str(row.get('id') or '')):
        source_id = str(source.get('id') or '').strip()
        if source_id:
            source_ids.append(source_id)
        for relation in sorted(source.get('relations', []), key=lambda row: str(row.get('id') or '')):
            relation_id = str(relation.get('id') or '').strip()
            occurrence_ids = [str(value) for value in relation.get('occurrence_ids') or [] if value]
            matched_roots: set[str] = set()
            for occurrence_id in occurrence_ids:
                matched_roots.update(occurrence_to_roots.get(occurrence_id, set()))
            if not matched_roots:
                gaps.append({
                    'id': f'gap-bible-projection-{relation_id or "unknown"}',
                    'gap_type': 'comparator',
                    'state': 'open',
                    'reason': 'unresolved_occurrence_reference',
                    'relation_id': relation_id,
                    'relation_source_id': source_id,
                    'occurrence_ids': occurrence_ids,
                    'candidate_root_ids': [],
                })
                continue
            for root_id in matched_roots:
                root_relations.setdefault(root_id, set()).add(relation_id)

    root_index = {
        root_id: sorted(relation_ids)
        for root_id, relation_ids in sorted(root_relations.items())
        if relation_ids
    }

    episode_index: dict[str, dict] = {}
    for episode in sorted(episodes.get('episodes', []), key=lambda row: str(row.get('id') or '')):
        episode_id = str(episode.get('id') or '').strip()
        if not episode_id:
            continue
        inherited: set[str] = set()
        for root_id in episode.get('member_root_ids') or []:
            inherited.update(root_index.get(str(root_id), []))
        episode_index[episode_id] = {
            'relation_ids': sorted(inherited),
            'inheritance': 'member_union',
            'sequence_relation_ids': [],
        }

    gaps.sort(key=lambda row: (row['relation_source_id'], row['relation_id']))
    return {
        'id': 'public-statement-bible-projection',
        'version': '1.0.0',
        'model': 'rooted-reference-projection',
        'source_root_id': str(evidence_root.get('id') or ''),
        'source_episode_id': str(episodes.get('id') or ''),
        'relation_source_ids': sorted(set(source_ids)),
        'root_relations': root_index,
        'episode_relations': episode_index,
        'gaps': gaps,
        'ownership_rule': 'Bible relation interpretation remains owned by the relation source files; this projection stores references only.',
    }


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    root_path = repository_root / 'data' / 'evidence' / 'public-statement-evidence-root.json'
    episode_path = repository_root / 'data' / 'evidence' / 'public-statement-episodes.json'
    output_path = repository_root / 'data' / 'evidence' / 'public-statement-bible-projection.json'
    relation_paths = [
        repository_root / 'knowledge' / 'traditions' / 'public-x-biblical-occurrence-relations-01-09.json',
        repository_root / 'knowledge' / 'traditions' / 'public-x-biblical-occurrence-relations-10-18.json',
        repository_root / 'knowledge' / 'traditions' / 'public-x-biblical-occurrence-relations-19-27.json',
    ]
    evidence_root = json.loads(root_path.read_text(encoding='utf-8'))
    episodes = json.loads(episode_path.read_text(encoding='utf-8'))
    relation_sources = [json.loads(path.read_text(encoding='utf-8')) for path in relation_paths]
    payload = build_bible_projection(evidence_root, episodes, relation_sources)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(
        'PUBLIC STATEMENT BIBLE PROJECTION BUILT '
        f"({len(payload['root_relations'])} roots linked; {len(payload['gaps'])} gaps)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
