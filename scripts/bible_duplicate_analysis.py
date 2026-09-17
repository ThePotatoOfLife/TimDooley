#!/usr/bin/env python3
from __future__ import annotations

import re
from itertools import combinations

STOP = {
    'the','a','an','and','or','of','to','in','on','for','with','is','are','was','were','be','as','at','by','from','that','this','it','into','through','then'
}


def _arr(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _norm(value) -> str:
    return re.sub(r'\s+', ' ', str(value or '').strip().lower())


def _tokens(*values) -> set[str]:
    text = ' '.join(_norm(value) for value in values if value)
    return {token for token in re.findall(r'[a-z0-9]+', text) if len(token) > 2 and token not in STOP}


def _set(values) -> set[str]:
    return {_norm(value) for value in _arr(values) if _norm(value)}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 0.0
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _primary_scene(row: dict) -> str:
    value = _norm(row.get('primary_biblical_scene_id'))
    if value:
        return value
    scenes = _set(row.get('biblical_scene_ids'))
    return sorted(scenes)[0] if scenes else ''


def _date(row: dict) -> str:
    raw = _norm(row.get('date') or row.get('timestamp'))
    match = re.search(r'(?:19|20)\d{2}(?:-\d{2}(?:-\d{2})?)?', raw)
    return match.group(0) if match else raw


def score_pair(left: dict, right: dict):
    if left.get('id') == right.get('id'):
        return None

    same_date = bool(_date(left) and _date(left) == _date(right))
    left_scene, right_scene = _primary_scene(left), _primary_scene(right)
    same_scene = bool(left_scene and left_scene == right_scene)

    bible_overlap = _jaccard(_set(left.get('biblical_refs')), _set(right.get('biblical_refs')))
    motif_overlap = _jaccard(
        _set(_arr(left.get('motifs')) + _arr(left.get('operators')) + _arr(left.get('roles'))),
        _set(_arr(right.get('motifs')) + _arr(right.get('operators')) + _arr(right.get('roles'))),
    )
    text_overlap = _jaccard(
        _tokens(left.get('title'), left.get('project_anchor')),
        _tokens(right.get('title'), right.get('project_anchor')),
    )
    sequence_overlap = _jaccard(
        _tokens(left.get('sequence'), left.get('mechanisms')),
        _tokens(right.get('sequence'), right.get('mechanisms')),
    )
    same_direction = bool(_norm(left.get('source_direction')) and _norm(left.get('source_direction')) == _norm(right.get('source_direction')))
    same_mode = bool(_norm(left.get('discovery_mode')) and _norm(left.get('discovery_mode')) == _norm(right.get('discovery_mode')))

    score = (
        (0.20 if same_date else 0.0)
        + (0.24 if same_scene else 0.0)
        + 0.16 * bible_overlap
        + 0.16 * motif_overlap
        + 0.14 * text_overlap
        + 0.05 * sequence_overlap
        + (0.025 if same_direction else 0.0)
        + (0.025 if same_mode else 0.0)
    )
    score = round(min(1.0, score), 3)

    reasons = []
    if same_date: reasons.append('same project date')
    if same_scene: reasons.append('same primary scene')
    if bible_overlap >= 0.6: reasons.append('strong Bible-reference overlap')
    if motif_overlap >= 0.6: reasons.append('strong motif/operator/role overlap')
    if text_overlap >= 0.6: reasons.append('strong title/project-anchor overlap')
    if sequence_overlap >= 0.6: reasons.append('strong sequence overlap')
    if same_direction: reasons.append('same source direction')
    if same_mode: reasons.append('same discovery mode')

    # Require shared event/scene structure before calling something a merge
    # candidate. Similar vocabulary alone is not enough.
    if score >= 0.90 and same_date and (same_scene or bible_overlap >= 0.8):
        kind = 'exact'
    elif score >= 0.72 and (same_date or same_scene) and (bible_overlap >= 0.45 or motif_overlap >= 0.65):
        kind = 'near'
    elif motif_overlap >= 0.45 or bible_overlap >= 0.45 or text_overlap >= 0.55:
        kind = 'same-motif-distinct'
    else:
        return None

    return {'score': score, 'class': kind, 'reasons': reasons}


def candidate_pairs(rows: list[dict]) -> list[dict]:
    candidates = []
    ordered = sorted(rows, key=lambda row: str(row.get('id') or ''))
    for left, right in combinations(ordered, 2):
        scored = score_pair(left, right)
        if not scored:
            continue
        candidates.append({
            'left_id': left.get('id'),
            'right_id': right.get('id'),
            **scored,
        })
    candidates.sort(key=lambda item: (-item['score'], item['class'], str(item['left_id']), str(item['right_id'])))
    return candidates
