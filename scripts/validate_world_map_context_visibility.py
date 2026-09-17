#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'world-map' / '3d-context-policy.js'
CONTEXT = ROOT / 'world-map' / '3d-context-visibility.js'
STATUS = ROOT / 'world-map' / '3d-context-status.js'
SELECTION = ROOT / 'world-map' / '3d-country-selection.js'
PINNED = ROOT / 'world-map' / '3d-pinned-context.js'
LAYOUT_POLICY = ROOT / 'world-map' / '3d-ui-layout-policy.js'
LAYOUT = ROOT / 'world-map' / '3d-ui-layout.js'
PANEL = ROOT / 'world-map' / '3d-panel-lifecycle.js'
STATE = ROOT / 'world-map' / '3d-map-state.js'
TIME_POLICY = ROOT / 'world-map' / '3d-time-policy.js'
TIME = ROOT / 'world-map' / '3d-time.js'
INVESTIGATION = ROOT / 'world-map' / '3d-investigation-surface.js'
EVIDENCE = ROOT / 'world-map' / '3d-evidence.js'
POLICY_TEST = ROOT / 'scripts' / 'test_world_map_context_policy.mjs'
UI_BUDGET_TEST = ROOT / 'scripts' / 'test_world_map_ui_surface_budget.mjs'
STATUS_TEST = ROOT / 'scripts' / 'test_world_map_context_status.mjs'
PINNED_TEST = ROOT / 'scripts' / 'test_world_map_pinned_context_contract.mjs'
TIME_TEST = ROOT / 'scripts' / 'test_world_map_time_policy.mjs'
INVESTIGATION_TEST = ROOT / 'scripts' / 'test_world_map_investigation_contract.mjs'
RESET_TEST = ROOT / 'scripts' / 'test_world_map_reset_context_contract.mjs'

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
status = text(STATUS)
selection = text(SELECTION)
pinned = text(PINNED)
layout_policy = text(LAYOUT_POLICY)
layout = text(LAYOUT)
panel = text(PANEL)
state = text(STATE)
time_policy = text(TIME_POLICY)
time_runtime = text(TIME)
investigation = text(INVESTIGATION)
evidence = text(EVIDENCE)
policy_test = text(POLICY_TEST)
ui_budget_test = text(UI_BUDGET_TEST)
status_test = text(STATUS_TEST)
pinned_test = text(PINNED_TEST)
time_test = text(TIME_TEST)
investigation_test = text(INVESTIGATION_TEST)
reset_test = text(RESET_TEST)

for token in (
    'contextScaleBand',
    'contextInvestigationMode',
    'contextBudgets',
    'contextVisibility',
    'scale.transition',
):
    require(policy, token, '3d-context-policy.js')

for token in (
    "from './3d-context-policy.js'",
    'contextInvestigationMode',
    'window.__potatoAtlasContextVisibility',
    'potato-atlas-context-visibility-change',
    'potato-atlas-working-selection-change',
    'potato-atlas-pin-change',
    'atlas-time-change',
    'stableScaleBand',
    'investigationId',
    'budgets',
    'epistemic',
    'window.__potatoAtlasLayers',
    'window.__potatoAtlasScale',
):
    require(context, token, '3d-context-visibility.js')

require(context, 'queueMicrotask', '3d-context-visibility.js')
require(context, 'refreshSerial', '3d-context-visibility.js')
require(context, 'selection.setAutomaticRelationBudget', '3d-context-visibility.js')
require(context, 'api.active()', '3d-context-visibility.js')

for token in (
    'atlasContextStatus',
    'Current view',
    "zone:'left-status'",
    'context.question?.investigation',
    'context.scaleBand',
    'context.pinnedCountries',
    'context.time',
):
    require(status, token, '3d-context-status.js')

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

for token in ('selectVisibleSurfaceIds', 'normalizedBudget'):
    require(layout_policy, token, '3d-ui-layout-policy.js')
for token in (
    "from './3d-ui-layout-policy.js'",
    "'bottom-context'",
    'atlasUIBottomContext',
    'refreshBottomContext',
    'pinned-context',
    'applyLeftStatusBudget',
    'data-layout-suppressed',
    'statusSurfaceBudget',
    'statusSurfacesSuppressed',
    'potato-atlas-context-visibility-change',
):
    require(layout, token, '3d-ui-layout.js')
for token in (
    'selectVisibleSurfaceIds',
    'highest-priority visible surfaces',
):
    require(ui_budget_test, token, 'test_world_map_ui_surface_budget.mjs')

for token in (
    'atlasPinnedContextRail',
    'window.__potatoAtlasPinnedContext',
    "zone:'bottom-context'",
    'potato-atlas-active-view-change',
    'atlas-pinned-overflow',
    'staleSuppressions',
    'Promise.all',
    'collapse()',
):
    require(pinned, token, '3d-pinned-context.js')

if 'setTimeout' in pinned:
    errors.append('3d-pinned-context.js must not poll for Active View with setTimeout')

for module_path in (
    './3d-context-visibility.js',
    './3d-context-status.js',
    './3d-pinned-context.js',
):
    require(panel, module_path, '3d-panel-lifecycle.js')

for token in (
    'contextVisibility: window.__potatoAtlasContextVisibility?.current || null',
    "window.__potatoAtlasContextVisibility?.refresh?.('map-state-reset')",
    "runStep('investigation'",
    '__potatoAtlasInvestigationSurface?.closeActive',
    "runStep('compare'",
    'window.leaveCompare?.()',
    "runStep('pinned-context'",
    '__potatoAtlasPinnedContext?.collapse',
):
    require(state, token, '3d-map-state.js')

for token in (
    'normalizeTimeState',
    'describeTimeWindow',
    'reordered-range',
    'missing-range-end',
    'validIsoDate',
):
    require(time_policy, token, '3d-time-policy.js')
for token in (
    "from './3d-time-policy.js'",
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
    'contextInvestigationMode',
    "contextScaleBand(fakeScale, 'region', 5.1)",
    'compare mode should grant pinned countries a larger relation budget',
    'narrow screens should keep the pinned rail bounded',
    'local browse should prioritize physical/local context over abstract global lines',
):
    require(policy_test, token, 'test_world_map_context_policy.mjs')
for token in ('Current view', './3d-context-status.js'):
    require(status_test, token, 'test_world_map_context_status.mjs')
for token in (
    'Promise\\.all',
    'pinned context must stay event-driven instead of polling',
    'pinned context should explain hidden overflow',
):
    require(pinned_test, token, 'test_world_map_pinned_context_contract.mjs')
for token in ("reversed.issue, 'reordered-range'", 'invalid-date', 'missing-range-end'):
    require(time_test, token, 'test_world_map_time_policy.mjs')
for token in (
    'Escape should close the active investigation surface centrally',
    'Evidence must register with the shared investigation surface',
    'context visibility must consume the actual investigation API',
):
    require(investigation_test, token, 'test_world_map_investigation_contract.mjs')
for token in (
    'map reset should explicitly close temporary investigations',
    'map reset should explicitly leave Compare mode',
    'map reset should reset transient pinned-context presentation state',
):
    require(reset_test, token, 'test_world_map_reset_context_contract.mjs')

# New context modules may query map zoom only through the shared scale API.
for owner, source in [('3d-context-visibility.js', context), ('3d-pinned-context.js', pinned), ('3d-context-status.js', status)]:
    for bad in ('getZoom() >', 'getZoom() >=', 'getZoom() <', 'getZoom() <='):
        if bad in source:
            errors.append(f'{owner} introduces raw zoom threshold: {bad}')

# Context presentation must never become a country-fill owner.
for owner, source in [('3d-context-visibility.js', context), ('3d-pinned-context.js', pinned), ('3d-context-status.js', status), ('3d-ui-layout.js', layout)]:
    if "setPaintProperty('countries-fill'" in source or 'setFeatureState({ source: \'countries\'' in source:
        errors.append(f'{owner} must not own country analytical/selection paint')

if errors:
    print('World Map context visibility validation FAILED')
    for error in errors:
        print(f'- {error}')
    sys.exit(1)

print('World Map context visibility validation passed')
