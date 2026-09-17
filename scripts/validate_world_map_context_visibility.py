#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'world-map' / '3d-context-policy.js'
CONTEXT = ROOT / 'world-map' / '3d-context-visibility.js'
SELECTION = ROOT / 'world-map' / '3d-country-selection.js'
PINNED = ROOT / 'world-map' / '3d-pinned-context.js'
LAYOUT = ROOT / 'world-map' / '3d-ui-layout.js'
PANEL = ROOT / 'world-map' / '3d-panel-lifecycle.js'
STATE = ROOT / 'world-map' / '3d-map-state.js'
TIME_POLICY = ROOT / 'world-map' / '3d-time-policy.js'
TIME = ROOT / 'world-map' / '3d-time.js'
INVESTIGATION = ROOT / 'world-map' / '3d-investigation-surface.js'
EVIDENCE = ROOT / 'world-map' / '3d-evidence.js'
POLICY_TEST = ROOT / 'scripts' / 'test_world_map_context_policy.mjs'
TIME_TEST = ROOT / 'scripts' / 'test_world_map_time_policy.mjs'
INVESTIGATION_TEST = ROOT / 'scripts' / 'test_world_map_investigation_contract.mjs'

errors = []

def text(path):
    if not path.exists():
        errors.append(f'missing {path.relative_to(ROOT)}')
        return ''
    return path.read_text(encoding='utf-8')

def require(haystack, needle, owner):
    if needle not in haystack:
        errors.append(f'{owner} missing required token: {needle}')

policy = text(POLICY)
context = text(CONTEXT)
selection = text(SELECTION)
pinned = text(PINNED)
layout = text(LAYOUT)
panel = text(PANEL)
state = text(STATE)
time_policy = text(TIME_POLICY)
time_runtime = text(TIME)
investigation = text(INVESTIGATION)
evidence = text(EVIDENCE)
policy_test = text(POLICY_TEST)
time_test = text(TIME_TEST)
investigation_test = text(INVESTIGATION_TEST)

for token in (
    'contextScaleBand',
    'contextBudgets',
    'contextVisibility',
    'scale.transition',
):
    require(policy, token, '3d-context-policy.js')

for token in (
    "import { contextScaleBand, contextBudgets, contextVisibility } from './3d-context-policy.js'",
    'window.__potatoAtlasContextVisibility',
    'potato-atlas-context-visibility-change',
    'potato-atlas-working-selection-change',
    'potato-atlas-pin-change',
    'atlas-time-change',
    "return 'browse'",
    'stableScaleBand',
    'investigationId',
    'budgets',
    'epistemic',
):
    require(context, token, '3d-context-visibility.js')

require(context, 'queueMicrotask', '3d-context-visibility.js')
require(context, 'refreshSerial', '3d-context-visibility.js')
require(context, 'selection.setAutomaticRelationBudget', '3d-context-visibility.js')
require(context, 'api.active()', '3d-context-visibility.js')

for token in (
    'setAutomaticRelationBudget',
    'getAutomaticRelationBudget',
    'automaticRelationBudget',
    'rankedEdges',
    'relationBucket',
):
    require(selection, token, '3d-country-selection.js')

for forbidden in ('const AUTO_EDGES_ACTIVE =', 'const AUTO_EDGES_OTHER =', 'const AUTO_EDGES_TOTAL ='):
    if forbidden in selection:
        errors.append(f'3d-country-selection.js still owns fixed auto-relation constant: {forbidden}')

for token in (
    "'bottom-context'",
    'atlasUIBottomContext',
    'refreshBottomContext',
    'pinned-context',
):
    require(layout, token, '3d-ui-layout.js')

for token in (
    'atlasPinnedContextRail',
    'window.__potatoAtlasPinnedContext',
    "zone:'bottom-context'",
    'potato-atlas-active-view-change',
    'atlas-pinned-overflow',
    'staleSuppressions',
):
    require(pinned, token, '3d-pinned-context.js')

if 'setTimeout' in pinned:
    errors.append('3d-pinned-context.js must not poll for Active View with setTimeout')

for token in (
    "loadModule?.('Context Visibility', './3d-context-visibility.js')",
    "loadModule?.('Pinned Context', './3d-pinned-context.js')",
):
    require(panel, token, '3d-panel-lifecycle.js')

require(state, 'contextVisibility: window.__potatoAtlasContextVisibility?.current || null', '3d-map-state.js')
require(state, "window.__potatoAtlasContextVisibility?.refresh?.('map-state-reset')", '3d-map-state.js')

for token in (
    'normalizeTimeState',
    'describeTimeWindow',
    'reordered-range',
    'missing-range-end',
    'validIsoDate',
):
    require(time_policy, token, '3d-time-policy.js')
for token in (
    "import { normalizeTimeState, describeTimeWindow } from './3d-time-policy.js'",
    'Time needs attention',
    'Comparison window',
    'describe(){return describeTimeWindow',
):
    require(time_runtime, token, '3d-time.js')

for token in (
    'get current()',
    'isActive',
    'closeActive',
    "event.key !== 'Escape'",
):
    require(investigation, token, '3d-investigation-surface.js')
for token in (
    "register('evidence'",
    ".open('evidence')",
    ".close('evidence')",
):
    require(evidence, token, '3d-evidence.js')

for token in (
    "contextScaleBand(fakeScale, 'region', 5.1)",
    'compare mode should grant pinned countries a larger relation budget',
    'narrow screens should keep the pinned rail bounded',
    'local browse should prioritize physical/local context over abstract global lines',
):
    require(policy_test, token, 'test_world_map_context_policy.mjs')
for token in (
    'reversed ranges should normalize chronologically',
    'invalid-date',
    'missing-range-end',
):
    require(time_test, token, 'test_world_map_time_policy.mjs')
for token in (
    'Escape should close the active investigation surface centrally',
    'Evidence must register with the shared investigation surface',
    'context visibility must consume the actual investigation API',
):
    require(investigation_test, token, 'test_world_map_investigation_contract.mjs')

# New modules may query map zoom only through the shared scale API. Direct numeric
# map.getZoom() threshold comparisons here would recreate the raw-zoom problem.
for owner, source in [('3d-context-visibility.js', context), ('3d-pinned-context.js', pinned)]:
    for bad in ('getZoom() >', 'getZoom() >=', 'getZoom() <', 'getZoom() <='):
        if bad in source:
            errors.append(f'{owner} introduces raw zoom threshold: {bad}')

# Context and pinned presentation must never become country-fill owners.
for owner, source in [('3d-context-visibility.js', context), ('3d-pinned-context.js', pinned)]:
    if "setPaintProperty('countries-fill'" in source or 'setFeatureState({ source: \'countries\'' in source:
        errors.append(f'{owner} must not own country analytical/selection paint')

if errors:
    print('World Map context visibility validation FAILED')
    for error in errors:
        print(f'- {error}')
    sys.exit(1)

print('World Map context visibility validation passed')
