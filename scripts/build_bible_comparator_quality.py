#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from bible_corpus import assemble_relations, assemble_scenes, load_manifest
from bible_duplicate_analysis import candidate_pairs

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'knowledge' / 'indexes' / 'bible-comparator-quality-report.json'


def present(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def research_reasons(row: dict, missing: list[str]) -> list[str]:
    reasons: list[str] = []
    strength = row.get('strength')
    if strength is not None and int(strength or 0) < 4:
        reasons.append('low-strength')
    if any(key in missing for key in ('project_side', 'source_direction')):
        reasons.append('project-evidence-gap')
    if any(key in missing for key in ('bible_refs', 'biblical_sequence')):
        reasons.append('biblical-context-gap')
    if any(key in missing for key in ('counterpressure', 'supported_conclusion')):
        reasons.append('boundary-gap')
    if 'why_it_matters' in missing:
        reasons.append('interpretation-gap')
    if strength is None and row.get('dossier_level') != 'A':
        reasons.append('unscored-provisional')
    return reasons


def assess(row: dict, scene_ids: set[str]) -> dict:
    scene = row.get('scene_context') or {}
    scripture = row.get('scripture_context') or {}
    argument = row.get('relation_argument') or {}
    discovery = row.get('discovery_history') or {}
    linked = [sid for sid in row.get('biblical_scene_ids', []) or [] if sid in scene_ids]
    coverage = {
        'project_side': present(scene.get('summary')) or present(row.get('project_anchor')),
        'exact_wording': present(row.get('exact_wording')) or present(row.get('project_quote')) or present(row.get('quote')),
        'scene': bool(linked),
        'bible_refs': present(row.get('biblical_refs')),
        'literary_context': present(scripture.get('literary_context')),
        'historical_context': present(scripture.get('historical_context')),
        'project_sequence': present(argument.get('project_sequence')),
        'biblical_sequence': present(argument.get('biblical_sequence')),
        'source_direction': present(discovery.get('source_direction')) or present(row.get('source_direction')) or present(row.get('discovery_mode')),
        'counterpressure': present(row.get('mismatch')) or present(row.get('counter_text')) or present(row.get('weaknesses')) or present(row.get('boundary')),
        'supported_conclusion': present(argument.get('maximum_claim')),
        'why_it_matters': present(argument.get('why_it_matters')),
    }
    required = ['project_side','bible_refs','source_direction','counterpressure','supported_conclusion','why_it_matters']
    if int(row.get('strength') or 0) >= 5 or row.get('dossier_level') == 'A':
        required += ['project_sequence','biblical_sequence']
    missing = [key for key in required if not coverage[key]]
    if not missing:
        action = 'retain'
    elif int(row.get('strength') or 0) >= 4:
        action = 'enrich'
    else:
        action = 'research'
    reasons = research_reasons(row, missing) if action == 'research' else []
    return {
        'id': row.get('id'),
        'strength': row.get('strength'),
        'dossier_level': row.get('dossier_level', 'compact'),
        'scene_source_status': scene.get('source_status'),
        'biblical_scene_ids': linked,
        'coverage': coverage,
        'missing': missing,
        'recommended_action': action,
        'research_reasons': reasons,
    }


def build_report(rows: list[dict], scenes: list[dict]) -> dict:
    scene_ids = {scene['id'] for scene in scenes}
    assessments = [assess(row, scene_ids) for row in rows]
    actions = Counter(item['recommended_action'] for item in assessments)
    reason_counts = Counter(reason for item in assessments for reason in item['research_reasons'])
    scene_linked = sum(item['coverage']['scene'] for item in assessments)
    duplicates = candidate_pairs(rows)
    return {
        'id': 'bible-comparator-quality-report',
        'version': '1.2.0',
        'updated': '2026-09-17',
        'purpose': 'Machine-readable quality, enrichment, and duplicate-candidate map for the manifest-defined public Bible comparator corpus.',
        'active_relation_count': len(rows),
        'active_scene_count': len(scenes),
        'relations_with_reusable_scene': scene_linked,
        'action_counts': dict(sorted(actions.items())),
        'research_reason_counts': dict(sorted(reason_counts.items())),
        'duplicate_candidate_count': len(duplicates),
        'duplicate_candidates': duplicates,
        'relations': assessments,
    }


def main() -> int:
    manifest = load_manifest(ROOT)
    rows = assemble_relations(ROOT, manifest)
    report = build_report(rows, assemble_scenes(ROOT, manifest))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Bible comparator quality report: {report['active_relation_count']} relations · {report['active_scene_count']} scenes · {report['action_counts']} · {report['duplicate_candidate_count']} duplicate candidates · research reasons {report['research_reason_counts']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
