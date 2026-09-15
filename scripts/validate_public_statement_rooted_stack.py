from __future__ import annotations

import json
from pathlib import Path

try:
    from scripts.build_public_statement_bible_projection import build_bible_projection
    from scripts.build_public_statement_development_threads import build_development_threads
    from scripts.build_public_statement_discovery_frontier import build_discovery_frontier
    from scripts.build_public_statement_episodes import build_episodes
    from scripts.build_public_statement_evidence_root import build_evidence_root
    from scripts.enrich_public_statement_evidence_root import enrich_status_ids
    from scripts.validate_public_statement_bible_projection import validate_bible_projection
    from scripts.validate_public_statement_development_threads import validate_development_threads
    from scripts.validate_public_statement_evidence_root import validate_evidence_root
    from scripts.validate_public_statement_episodes import validate_episodes
except ModuleNotFoundError:
    from build_public_statement_bible_projection import build_bible_projection
    from build_public_statement_development_threads import build_development_threads
    from build_public_statement_discovery_frontier import build_discovery_frontier
    from build_public_statement_episodes import build_episodes
    from build_public_statement_evidence_root import build_evidence_root
    from enrich_public_statement_evidence_root import enrich_status_ids
    from validate_public_statement_bible_projection import validate_bible_projection
    from validate_public_statement_development_threads import validate_development_threads
    from validate_public_statement_evidence_root import validate_evidence_root
    from validate_public_statement_episodes import validate_episodes


def validate_built_stack(
    root: dict,
    frontier: dict,
    episodes: dict,
    projection: dict,
    threads: dict | None = None,
) -> list[str]:
    errors: list[str] = []
    root_id = str(root.get('id') or '')
    if frontier.get('source_root_id') != root_id:
        errors.append('frontier source_root_id does not match Evidence Root')
    if episodes.get('source_root_id') != root_id:
        errors.append('episodes source_root_id does not match Evidence Root')
    if projection.get('source_root_id') != root_id:
        errors.append('Bible projection source_root_id does not match Evidence Root')
    if projection.get('source_episode_id') != episodes.get('id'):
        errors.append('Bible projection source_episode_id does not match Episode layer')
    if threads is not None:
        if threads.get('source_root_id') != root_id:
            errors.append('Development Threads source_root_id does not match Evidence Root')
        if threads.get('source_episode_id') != episodes.get('id'):
            errors.append('Development Threads source_episode_id does not match Episode layer')
        if threads.get('source_bible_projection_id') != projection.get('id'):
            errors.append('Development Threads source_bible_projection_id does not match Bible projection')

    open_gap_ids = sorted(
        str(gap.get('id'))
        for gap in frontier.get('gaps', [])
        if gap.get('state') == 'open' and gap.get('id')
    )
    queue_gap_ids = sorted(str(item.get('gap_id')) for item in frontier.get('work_queue', []) if item.get('gap_id'))
    if open_gap_ids != queue_gap_ids:
        errors.append('frontier work_queue must reference every open gap exactly once')
    if int((frontier.get('summary') or {}).get('open_total') or 0) != len(open_gap_ids):
        errors.append('frontier summary open_total does not match open gaps')

    root_ids = {str(row.get('id')) for row in root.get('roots', []) if row.get('id')}
    for episode in episodes.get('episodes', []):
        for member in episode.get('member_root_ids', []):
            if member not in root_ids:
                errors.append(f"episode {episode.get('id')} references unknown Root {member}")
    return errors


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def audit_repository(repository_root: Path) -> list[str]:
    evidence_paths = [
        repository_root / 'data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json',
        repository_root / 'data/evidence/rational-potato-x-timestamped-ledger-2025-2026.json',
    ]
    specialist_paths = [
        repository_root / 'knowledge/traditions/september-2026-x-biblical-overlap-01-10.json',
        repository_root / 'knowledge/traditions/september-2026-x-biblical-overlap-11-20.json',
    ]
    relation_paths = [
        repository_root / 'knowledge/traditions/public-x-biblical-occurrence-relations-01-09.json',
        repository_root / 'knowledge/traditions/public-x-biblical-occurrence-relations-10-18.json',
        repository_root / 'knowledge/traditions/public-x-biblical-occurrence-relations-19-27.json',
    ]
    episode_definitions_path = repository_root / 'data/evidence/public-statement-episode-definitions.json'
    thread_definitions_path = repository_root / 'data/evidence/public-statement-development-thread-definitions.json'

    required = [
        *evidence_paths,
        *specialist_paths,
        *relation_paths,
        episode_definitions_path,
        thread_definitions_path,
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        return [f"missing rooted-stack source: {path.relative_to(repository_root)}" for path in missing]

    root = build_evidence_root([_load(path) for path in evidence_paths])
    root = enrich_status_ids(root, [_load(path) for path in specialist_paths])
    frontier = build_discovery_frontier(root)
    episodes = build_episodes(root, _load(episode_definitions_path))
    relations = [_load(path) for path in relation_paths]
    projection = build_bible_projection(root, episodes, relations)
    threads = build_development_threads(
        root,
        _load(thread_definitions_path),
        episodes,
        projection,
    )

    errors = validate_evidence_root(root)
    root_ids = {str(row.get('id')) for row in root.get('roots', []) if row.get('id')}
    errors.extend(validate_episodes(episodes, root_ids))
    episode_ids = {str(row.get('id')) for row in episodes.get('episodes', []) if row.get('id')}
    relation_ids = {
        str(row.get('id'))
        for payload in relations
        for row in payload.get('relations', [])
        if row.get('id')
    }
    errors.extend(validate_bible_projection(projection, root_ids, episode_ids, relation_ids))
    errors.extend(validate_development_threads(threads, root_ids, episode_ids, relation_ids))
    errors.extend(validate_built_stack(root, frontier, episodes, projection, threads))
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = audit_repository(root)
    if errors:
        print('PUBLIC STATEMENT ROOTED STACK AUDIT FAILED')
        for error in errors:
            print(' -', error)
        return 1
    print('PUBLIC STATEMENT ROOTED STACK AUDIT PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
