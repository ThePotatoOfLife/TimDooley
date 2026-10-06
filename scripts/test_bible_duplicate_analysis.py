#!/usr/bin/env python3
from bible_duplicate_analysis import score_pair


def row(**overrides):
    base = {
        'id':'a',
        'title':'Door and the Way',
        'date':'2026-01-01',
        'project_anchor':'Tim says the Son is the Door.',
        'biblical_refs':['John 10:9'],
        'primary_biblical_scene_id':'john-door-shepherd',
        'biblical_scene_ids':['john-door-shepherd'],
        'motifs':['door','way'],
        'operators':['open','pass'],
        'roles':['son','door'],
        'source_direction':'project first, later biblical comparison',
        'discovery_mode':'tim-explicit',
        'sequence':'door -> entry -> life',
    }
    base.update(overrides)
    return base


left = row(id='left')
exact = row(id='exact', title='The Door and Way')
near = row(
    id='near',
    title='Door, gate and passage',
    project_anchor='Tim says the Son is the Door and passage to the Father.',
    biblical_refs=['John 10:7-10'],
    motifs=['door','gate','way'],
)
distinct = row(
    id='distinct',
    date='2025-09-30',
    title='Return and recognition',
    project_anchor='A later return claim is compared to recognition after resurrection.',
    biblical_refs=['John 20:24-29'],
    primary_biblical_scene_id='john-thomas-wounds-recognition',
    biblical_scene_ids=['john-thomas-wounds-recognition'],
    motifs=['return','recognition'],
    operators=['rise','recognize'],
    roles=['witness'],
    sequence='return -> recognition',
)

exact_score = score_pair(left, exact)
assert exact_score is not None
assert exact_score['class'] == 'exact'
assert exact_score['score'] >= 0.90

near_score = score_pair(left, near)
assert near_score is not None
assert near_score['class'] in {'near','exact'}
assert near_score['score'] >= 0.72

# Sharing a broad theological area is not enough to collapse distinct
# project events and distinct biblical scenes into one relation.
distinct_score = score_pair(left, distinct)
assert distinct_score is None or distinct_score['class'] == 'same-motif-distinct'

# Determinism: order changes output ids but not class/score/reasons.
reverse = score_pair(exact, left)
assert reverse is not None
assert reverse['class'] == exact_score['class']
assert reverse['score'] == exact_score['score']
assert reverse['reasons'] == exact_score['reasons']

print('bible duplicate analysis: ok')
