from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path


def _ordered_roots(evidence_root: dict) -> list[dict]:
    by_id = {str(row.get('id')): row for row in evidence_root.get('roots', []) if row.get('id')}
    timeline = (evidence_root.get('traversals') or {}).get('chronological') or []
    ordered = [by_id[root_id] for root_id in timeline if root_id in by_id]
    seen = {str(row.get('id')) for row in ordered}
    extras = sorted(
        (row for root_id, row in by_id.items() if root_id not in seen),
        key=lambda row: (str(row.get('timestamp_utc') or ''), str(row.get('id') or '')),
    )
    return ordered + extras


def _within(timestamp: str, start: str, end: str) -> bool:
    return bool(timestamp) and start <= timestamp <= end


def build_episodes(evidence_root: dict, definitions: dict) -> dict:
    roots = _ordered_roots(evidence_root)
    episodes: list[dict] = []
    gaps: list[dict] = []

    for definition in sorted(definitions.get('episodes', []), key=lambda row: str(row.get('id') or '')):
        episode_id = str(definition.get('id') or '').strip()
        start = str(definition.get('start_utc') or '').strip()
        end = str(definition.get('end_utc') or '').strip()
        minimum = int(definition.get('minimum_members') or 1)
        if not episode_id or not start or not end or start > end:
            gaps.append({
                'id': f'gap-episode-definition-{episode_id or "unknown"}',
                'gap_type': 'consolidation',
                'state': 'open',
                'reason': 'invalid_episode_definition',
                'episode_id': episode_id,
                'candidate_root_ids': [],
            })
            continue

        members = [
            str(root['id'])
            for root in roots
            if _within(str(root.get('timestamp_utc') or ''), start, end)
        ]
        if len(members) < minimum:
            gaps.append({
                'id': f'gap-episode-members-{episode_id}',
                'gap_type': 'consolidation',
                'state': 'open',
                'reason': 'minimum_members_not_met',
                'episode_id': episode_id,
                'required_members': minimum,
                'observed_members': len(members),
                'candidate_root_ids': members,
            })
            continue

        episode = deepcopy(definition)
        episode['member_root_ids'] = members
        episode['member_count'] = len(members)
        episode.setdefault('status', 'candidate')
        episode['relation_ids'] = list(episode.get('relation_ids') or [])
        episode['interpretive_claims'] = list(episode.get('interpretive_claims') or [])
        episodes.append(episode)

    return {
        'id': 'public-statement-episodes',
        'version': '1.0.0',
        'model': 'rooted-spiral-episodes',
        'source_root_id': str(evidence_root.get('id') or ''),
        'definition_source_id': str(definitions.get('id') or ''),
        'episodes': episodes,
        'gaps': sorted(gaps, key=lambda row: str(row.get('id') or '')),
    }


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    root_path = repository_root / 'data' / 'evidence' / 'public-statement-evidence-root.json'
    definition_path = repository_root / 'data' / 'evidence' / 'public-statement-episode-definitions.json'
    output_path = repository_root / 'data' / 'evidence' / 'public-statement-episodes.json'
    evidence_root = json.loads(root_path.read_text(encoding='utf-8'))
    definitions = json.loads(definition_path.read_text(encoding='utf-8'))
    payload = build_episodes(evidence_root, definitions)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(
        'PUBLIC STATEMENT EPISODES BUILT '
        f"({len(payload['episodes'])} episodes; {len(payload['gaps'])} gaps)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
