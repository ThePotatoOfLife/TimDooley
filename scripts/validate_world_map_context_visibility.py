#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / 'world-map' / '3d-context-visibility.js'
SELECTION = ROOT / 'world-map' / '3d-country-selection.js'
PINNED = ROOT / 'world-map' / '3d-pinned-context.js'
LAYOUT = ROOT / 'world-map' / '3d-ui-layout.js'
PANEL = ROOT / 'world-map' / '3d-panel-lifecycle.js'
STATE = ROOT / 'world-map' / '3d-map-state.js'

errors = []

def text(path):
    if not path.exists():
        errors.append(f'missing {path.relative_to(ROOT)}')
        return ''
    return path.read_text(encoding='utf-8')

def require(haystack, needle, owner):
    if needle not in haystack:
        errors.append(f'{owner} missing required token: {needle}')

context = text(CONTEXT)
selection = text(SELECTION)
pinned = text(PINNED)
layout = text(LAYOUT)
panel = text(PANEL)
state = text(STATE)

for token in (
    'window.__potatoAtlasContextVisibility',
    'potato-atlas-context-visibility-change',
    'potato-atlas-working-selection-change',
    'potato-atlas-pin-change',
    'atlas-time-change',
    "investigation:'browse'" if False else "return 'browse'",
    'scaleBand',
    'budgets',
    'epistemic',
):
    require(context, token, '3d-context-visibility.js')

require(context, 'queueMicrotask', '3d-context-visibility.js')
require(context, 'refreshSerial', '3d-context-visibility.js')
require(context, 'selection.setAutomaticRelationBudget', '3d-context-visibility.js')

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
    'window.__potatoAtlasActiveView',
    'staleSuppressions',
):
    require(pinned, token, '3d-pinned-context.js')

for token in (
    "loadModule?.('Context Visibility', './3d-context-visibility.js')",
    "loadModule?.('Pinned Context', './3d-pinned-context.js')",
):
    require(panel, token, '3d-panel-lifecycle.js')

require(state, 'contextVisibility: window.__potatoAtlasContextVisibility?.current || null', '3d-map-state.js')
require(state, "window.__potatoAtlasContextVisibility?.refresh?.('map-state-reset')", '3d-map-state.js')

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
