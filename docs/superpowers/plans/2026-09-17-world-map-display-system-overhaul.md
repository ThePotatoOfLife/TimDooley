# World Map Display System Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate World Map hover, Current Map View, selected-country card, pinned-country comparison and inspector depth into one predictable subject/question display system.

**Architecture:** Preserve the existing selection, analytical-view, interaction, inspector, layout and render-stack owners. Add one shared country-presentation adapter that normalizes identity, population and the current analytical answer; make every ordinary country surface consume it at a different disclosure depth. Remove the mixed country-preview role from `3d-context-status.js`, make `atlasWorldContext` global-only, restructure the Country Card into a permanent header/current-answer plus Overview/Context/Connections tabs, and protect the ocean-below-terrain ordering contract.

**Tech Stack:** MapLibre GL JS 6.9, browser ES modules, Node contract/regression tests, Python repository validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-17-world-map-display-system-design.md`

## Global Constraints

- Country selection defines the persistent subject; navbar state defines the question/lens.
- Hover is ephemeral and must never mutate selection, pins, URL, inspector, automatic relations, Evidence, Trace, Path or camera.
- Current Map View is global question/context only; it must not display a country-specific value.
- The upper-left Country Card remains the one ordinary persistent country information surface.
- Population exists on hover, selected-card, pinned-card and deep country summary surfaces; missing population renders `—`, never `0` and never disappears.
- One shared presentation path owns population fallback, current analytical answer, missing-value formatting and source/period normalization.
- Physical Water/Terrain/Geography context must not displace the primary scalar/set analytical question.
- Preserve one Selection owner, one Interaction Router, one Inspector Router, one Context Visibility owner, one UI Layout coordinator and one Render Stack.
- Preserve the seam-safe ocean geometry fix. Ocean base must remain below land mask, terrain hillshade and canonical country fill.

---

### Task 1: Protect the new display ownership contract

**Files:**
- Create: `scripts/test_world_map_display_system_contract.mjs`
- Modify: `scripts/test_world_map_context_ci_contract.mjs`
- Modify: `.github/workflows/quality-checks.yml`
- Modify: `scripts/validate_world_map_context_visibility.py`
- Modify: `scripts/validate_world_map_ui_shell.py`

**Interfaces:**
- Consumes: current source text for `3d-hover.js`, `3d-world-bar.js`, `3d-country-card.js`, `3d-pinned-context.js`, `3d-country-pulse.js`, `3d-panel-lifecycle.js`, and the future `3d-country-presentation.js`.
- Produces: CI-enforced ownership contract requiring one shared country-presentation adapter, minimal tooltip, global-only Current Map View, three Country Card tabs, presentation-backed pins, and no runtime load of mixed `3d-context-status.js`.

- [ ] **Step 1: Write the failing display-system test**

Create `scripts/test_world_map_display_system_contract.mjs` with assertions equivalent to:

```js
import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const read = path => fs.readFileSync(new URL(path, root), 'utf8');

const presentation = read('world-map/3d-country-presentation.js');
const hover = read('world-map/3d-hover.js');
const worldBar = read('world-map/3d-world-bar.js');
const card = read('world-map/3d-country-card.js');
const pins = read('world-map/3d-pinned-context.js');
const pulse = read('world-map/3d-country-pulse.js');
const panel = read('world-map/3d-panel-lifecycle.js');

for (const token of ['__potatoAtlasCountryPresentation','forCountry','Population','currentQuestion']) {
  assert.ok(presentation.includes(token), `country presentation missing ${token}`);
}
assert.ok(hover.includes('__potatoAtlasCountryPresentation'), 'hover must consume shared country presentation');
for (const forbidden of ['Capital:', 'Area:', 'Currency:']) {
  assert.ok(!hover.includes(forbidden), `ordinary country hover must stay minimal: ${forbidden}`);
}
assert.ok(!worldBar.includes('<span>Active</span>'), 'Current Map View must not expose selected-country identity');
assert.ok(worldBar.includes('select a country'), 'relationship context without a subject needs an explicit orientation state');
for (const tab of ['overview','context','connections']) {
  assert.ok(card.includes(`data-country-tab="${tab}"`), `Country Card missing ${tab} tab`);
}
assert.ok(card.includes('__potatoAtlasCountryPresentation'), 'Country Card must consume shared country presentation');
assert.ok(pins.includes('__potatoAtlasCountryPresentation'), 'pins must consume shared country presentation');
assert.ok(!pins.includes('function populationObservation'), 'pins must not own a second population resolver');
assert.ok(!panel.includes("'Context Status', './3d-context-status.js'"), 'mixed context-status surface must not load');
assert.ok(!pulse.includes('activeMapViewHtml(view)'), 'deep Country Pulse must not repeat the Country Card current-map answer');
```

- [ ] **Step 2: Replace old context-status CI assertions**

Update `test_world_map_context_ci_contract.mjs` and the context-control-plane workflow step so they require:

```text
node scripts/test_world_map_display_system_contract.mjs
```

and no longer require `node scripts/test_world_map_context_status.mjs`.

- [ ] **Step 3: Update static validators to the new ownership model**

`validate_world_map_context_visibility.py` must stop requiring `3d-context-status.js` and instead require:

```text
world-map/3d-country-presentation.js
__potatoAtlasCountryPresentation
./3d-country-presentation.js
./3d-pinned-context.js
```

It must also reject a panel lifecycle that loads `./3d-context-status.js`.

`validate_world_map_ui_shell.py` must replace old flattened-card requirements such as `Pinned comparison`, `comparisonRows`, `populationObservation`, and `Map color` with:

```text
Current map
Overview
Context
Connections
data-country-tab
__potatoAtlasCountryPresentation
```

- [ ] **Step 4: Verify RED in GitHub Actions**

Open a draft PR from `world-map-display-system-overhaul-2026-09-17` to `main` after committing these tests.

Expected: Repository quality checks fail because `3d-country-presentation.js` does not yet exist, Country Card has no three-tab contract, pins still resolve population independently, Current Map View still exposes `Active`, and panel lifecycle still loads Context Status.

---

### Task 2: Add the shared Country Presentation adapter

**Files:**
- Create: `world-map/3d-country-presentation.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `scripts/test_world_map_display_system_contract.mjs`

**Interfaces:**
- Consumes: `window.__potatoAtlasActiveView.forCountry(code)`, `window.__potatoAtlasDataRuntime.populationObservation(code)`, `areaObservation(code)`, `window.__potatoAtlasSelection.countryName(code)`, `window.__potatoAtlasSelection.current`, optional `window.__potatoAtlasDemography`, and `../data/world-country-facts.json` as identity fallback.
- Produces:

```js
window.__potatoAtlasCountryPresentation = {
  forCountry(code, options?),
  currentQuestion(),
  formatPopulation(value),
  formatArea(value),
}
```

`forCountry()` returns normalized `{ code, identity, population, answer, memberships, relation, active, pinned }`.

- [ ] **Step 1: Extend the failing contract with null-population and Population-layer dedupe expectations**

Require source markers for an explicit null guard:

```js
if (value == null || value === '') return '—';
```

and an answer property that can identify `stat.population` so renderers can deduplicate it.

- [ ] **Step 2: Implement the minimal shared adapter**

Create a focused module with helpers equivalent to:

```js
function formatPopulation(value) {
  if (value == null || value === '') return '—';
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { notation:'compact', maximumFractionDigits:1 }).format(number);
}

async function forCountry(code) {
  code = String(code || '').toUpperCase();
  const selection = window.__potatoAtlasSelection;
  const runtime = window.__potatoAtlasDataRuntime;
  const activeView = window.__potatoAtlasActiveView;
  const [populationCell, areaCell, view] = await Promise.all([
    runtime?.populationObservation?.(code) || null,
    runtime?.areaObservation?.(code) || null,
    activeView?.forCountry?.(code) || null,
  ]);
  const fallbackPopulation = window.__potatoAtlasDemography?.countries?.[code]?.population?.value ?? null;
  const populationValue = populationCell?.value ?? fallbackPopulation;
  return {
    code,
    identity:{
      name:selection?.countryName?.(code) || code,
      area:{ value:areaCell?.value ?? null, display:formatArea(areaCell?.value) },
    },
    population:{ value:populationValue, display:formatPopulation(populationValue), period:populationCell?.period || '', source:populationCell?.source || '' },
    answer:normalizeAnswer(view),
    memberships:view?.memberships || null,
    relation:{ mode:view?.relationMode || selection?.getRelationMode?.() || 'all', count:selection?.connectionsFor?.(code, 64)?.length || 0 },
    active:code === selection?.current?.activeCode,
    pinned:selection?.isPinned?.(code) === true,
  };
}
```

Load country facts once only if needed for capital/identity fallback. Do not create another canonical database.

- [ ] **Step 3: Derive `currentQuestion()` from existing owners**

Return the primary scalar/set state plus supporting relation/time/projection/investigation context. Scalar takes precedence over sets; relations/physical/geography/time/projection never become the scalar answer.

- [ ] **Step 4: Load the adapter after Active View and before World Bar/Country Card**

Update bootstrap order:

```js
await loadAfterPaint('Active View', './3d-active-view.js');
await loadAfterPaint('Country Presentation', './3d-country-presentation.js');
await loadAfterPaint('World Bar', './3d-world-bar.js');
await loadAfterPaint('Country Card', './3d-country-card.js');
```

- [ ] **Step 5: Verify adapter syntax and source contract**

Run through CI / local-equivalent checks:

```bash
node --check world-map/3d-country-presentation.js
node scripts/test_world_map_display_system_contract.mjs
```

Expected: adapter assertions pass; later surface assertions remain RED until migrated.

---

### Task 3: Make hover minimal and Current Map View global-only

**Files:**
- Modify: `world-map/3d-hover.js`
- Modify: `world-map/3d-world-bar.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `scripts/test_world_map_hover_artifacts.mjs`
- Modify: `scripts/test_world_map_display_system_contract.mjs`

**Interfaces:**
- Hover consumes `__potatoAtlasCountryPresentation.forCountry(code)` when available and preserves the existing shared Tooltip generation/race API.
- Current Map View consumes global layer/query/selection context but never a country-specific value.

- [ ] **Step 1: Add failing minimal-hover assertions**

Require `countryHtml()` to render only country identity, current answer and Population, and explicitly reject ordinary hover strings `Capital:`, `Area:`, `Currency:` and generic region rows.

Preserve the existing race test proving newest hover wins and mouseleave invalidates late async work.

- [ ] **Step 2: Rewrite `countryHtml()` around Country Presentation**

When presentation is ready:

```text
Country name
[current scalar/set/relation answer when meaningful]
Population · value
```

When the adapter is not yet loaded during early boot, render name + `Population · —` instead of independently fetching/formatting country facts. This keeps boot non-blocking without creating a second presentation truth.

- [ ] **Step 3: Remove selected-country data from Current Map View**

Delete the `Active` country row and any country-specific answer. Keep scalar metadata, set query, coverage, pins count, relation mode, projection and time.

If relation mode is filtered while there is no active country, add:

```text
Connections · Systems · select a country
```

or equivalent explicit orientation copy.

- [ ] **Step 4: Stop loading mixed Context Status**

Remove:

```js
await window.__potatoAtlasLoadModule?.('Context Status', './3d-context-status.js');
```

from `3d-panel-lifecycle.js`. Leave the old file unexecuted for compatibility history unless a later cleanup proves safe to delete it.

- [ ] **Step 5: Verify hover/global-context GREEN**

```bash
node scripts/test_world_map_hover_artifacts.mjs
python scripts/validate_world_map_tooltip.py
node scripts/test_world_map_display_system_contract.mjs
```

Expected: hover/current-view/context-status ownership assertions pass; Country Card/pin/Pulse assertions may still be pending until later tasks.

---

### Task 4: Restructure the selected Country Card

**Files:**
- Modify: `world-map/3d-country-card.js`
- Modify: `scripts/validate_world_map_ui_shell.py`
- Modify: `scripts/test_world_map_display_system_contract.mjs`

**Interfaces:**
- Consumes: `__potatoAtlasCountryPresentation.forCountry(code)`, canonical country dossier data for Overview-only detail, Active View membership context, existing selection connection APIs and existing actions.
- Produces: one upper-left card with permanent header + optional Current Map Answer + exactly three tabs (`overview`, `context`, `connections`).

- [ ] **Step 1: Add failing tab and hierarchy assertions**

Require:

```text
data-country-tab="overview"
data-country-tab="context"
data-country-tab="connections"
atlas-country-current-answer
atlas-country-tab-panel
Population
__potatoAtlasCountryPresentation
```

Reject the old top-level `Pinned comparison` section.

- [ ] **Step 2: Add stable tab state**

Maintain `activeTab = 'overview'`. Preserve the chosen tab across rerenders of the same country; reset to `overview` when active country changes.

- [ ] **Step 3: Build the permanent header from shared presentation**

Always show name/code, capital when available, Population, pin state and close control. Population comes from `presentation.population`, not a card-local population resolver.

- [ ] **Step 4: Build the Current Map Answer block**

Scalar: label/value/source/period. Set: match state + compact membership labels. Neutral: no empty box.

When primary answer is `stat.population`, do not render a second numeric Population value; enrich the permanent population row with current source/period metadata instead.

- [ ] **Step 5: Build Overview tab**

Stable baseline:

```text
Population
GDP
GDP per capita
Growth
Inflation
Unemployment
Area
Capital
Government/system identity
```

Use dossier observations for non-shared metrics. Do not add deep source lists or full dossier sections.

- [ ] **Step 6: Build Context tab**

Render only meaningful active context: active set memberships/query, non-default time context, relevant Axis/project/functional-chain context already available for the country. Omit empty sections and do not add ordinary Water/Terrain rows.

- [ ] **Step 7: Build Connections tab**

Render bounded strongest relationships from `selection.connectionsFor(code, 4)` under the current relation mode, plus represented count and promotion to Trace. Keep full network exploration out of the card.

- [ ] **Step 8: Keep actions outside tabs**

Preserve Pin, Statistics, More data, Trace, Path and Impact actions in a stable footer.

- [ ] **Step 9: Verify Country Card contract**

```bash
node --check world-map/3d-country-card.js
python scripts/validate_world_map_ui_shell.py
node scripts/test_world_map_display_system_contract.mjs
```

Expected: Country Card slice GREEN.

---

### Task 5: Migrate pinned countries to the shared presentation truth

**Files:**
- Modify: `world-map/3d-pinned-context.js`
- Modify: `scripts/test_world_map_pinned_context_contract.mjs`

**Interfaces:**
- Consumes: `window.__potatoAtlasCountryPresentation.forCountry(code)`.
- Preserves: pinned rail overflow/expand/collapse behavior, activation/unpin behavior, serial stale suppression, bottom-context UI Layout registration.

- [ ] **Step 1: Change the pinned contract to require shared presentation**

Require `__potatoAtlasCountryPresentation` and reject local `function populationObservation` / direct `__potatoAtlasDataRuntime?.populationObservation` calls.

- [ ] **Step 2: Replace `resolveView()` with `resolvePresentation()`**

Resolve visible pins in parallel:

```js
const rows = await Promise.all(visiblePins.map(code =>
  window.__potatoAtlasCountryPresentation?.forCountry?.(code).catch(() => null)
));
```

Keep the existing render serial guard.

- [ ] **Step 3: Render only retained comparison information**

Each card shows:

```text
Country
current primary answer when one exists
Population · value
compact source/period only when useful
```

No government/capital/chains/generic memberships.

- [ ] **Step 4: Verify pinned GREEN**

```bash
node scripts/test_world_map_pinned_context_contract.mjs
node scripts/test_world_map_display_system_contract.mjs
```

Expected: PASS.

---

### Task 6: Make Country Pulse an inspector-depth surface

**Files:**
- Modify: `world-map/3d-country-pulse.js`
- Modify: `scripts/test_world_map_display_system_contract.mjs`

**Interfaces:**
- Preserves: `window.__potatoAtlasCountryPulse.render()`, full statistics, demography/religion context, systems/capabilities, projects, institutions, provenance/coverage and deeper relationship sections.
- Removes: duplicated `Current map color/view` first-screen answer that belongs to Country Card.

- [ ] **Step 1: Add the failing no-duplicate assertion**

Reject `activeMapViewHtml(view)` and `Current map color` in Country Pulse.

- [ ] **Step 2: Remove the duplicated current-map answer**

Country Pulse should begin with sourced/deeper country material rather than repeating the Country Card's Current Map block.

- [ ] **Step 3: Preserve the deep population invariant**

Population remains in the sourced headline/deep stats summary. If practical without widening scope, consume the shared presentation Population value; otherwise guarantee the deep summary remains sourced and consistent with the shared runtime.

- [ ] **Step 4: Verify inspector-depth contract**

```bash
node --check world-map/3d-country-pulse.js
node scripts/test_world_map_display_system_contract.mjs
```

Expected: PASS.

---

### Task 7: Protect physical ordering and verify the integrated system

**Files:**
- Modify: `scripts/validate_world_map_physical_water.py`
- Modify: `scripts/validate_world_map_render_stack.py` only if needed for shared ordering assertions.
- Verify all changed World Map files and repository workflow.

**Interfaces:**
- Preserves: current seam-safe ocean mesh, Natural Earth coastline/lake/river detail, Water controller API and Terrain DEM behavior.
- Enforces: ocean base `physical-surface` priority 8; land mask `physical-surface` priority 9; terrain hillshade `physical-surface` priority 10; ocean base never registered in `physical-water`.

- [ ] **Step 1: Add explicit render-order assertions**

The water validator must require source markers equivalent to:

```text
BASE_LAYERS.oceanBase ... slot:'physical-surface', priority:8
BASE_LAYERS.landMask ... slot:'physical-surface', priority:9
```

and terrain validator/render-stack validator must require hillshade `slot:'physical-surface', priority:10`.

Reject registration of `BASE_LAYERS.oceanBase` into `physical-water`.

- [ ] **Step 2: Run focused World Map checks**

```bash
node scripts/test_world_map_display_system_contract.mjs
node scripts/test_world_map_hover_artifacts.mjs
node scripts/test_world_map_pinned_context_contract.mjs
node scripts/test_world_map_interaction_router.mjs
python scripts/validate_world_map_tooltip.py
python scripts/validate_world_map_context_visibility.py
python scripts/validate_world_map_ui_shell.py
python scripts/validate_world_map_physical_water.py
python scripts/validate_world_map_render_stack.py
python scripts/validate_world_map_source.py
```

Expected: all PASS.

- [ ] **Step 3: Run full repository quality checks on the exact branch head**

Use the draft PR's `Repository quality checks` workflow. Do not claim completion until the exact final SHA has a completed `success` run.

- [ ] **Step 4: Final ownership audit**

Confirm:

```text
one country selection owner
one shared country presentation adapter
one tooltip hover surface
one global Current Map View
one ordinary Country Card
one pinned comparison rail
one inspector stack
one Render Stack
```

Confirm hover cannot mutate selection/pins/URL/relations/inspector and no country-specific value appears in Current Map View.

- [ ] **Step 5: Update the draft PR summary with verification evidence**

Document the subject/question model, minimal hover, three-tab Country Card, shared presentation adapter, population invariant, removal of mixed context-status ownership, inspector-depth distinction and protected water/terrain order.
