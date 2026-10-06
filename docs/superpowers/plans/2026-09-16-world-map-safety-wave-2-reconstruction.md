# World Map Safety Wave 2 Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruct the still-desired Safety Wave 2 control-plane behavior from PR #191 onto current `main` without replaying stale branch history or reintroducing superseded runtime owners.

**Architecture:** Current `main` is authoritative. The historical branch `world-map-safety-wave-2-2026-09-16` is a source of tested behavior only. Each slice starts with a regression, ports the smallest still-needed runtime change, runs focused validation, then joins the canonical `scripts/validate_world_map_source.py` chain. Single-owner interaction, inspector, tooltip, style-lifecycle, render-stack and scale rules take precedence over historical implementation details.

**Tech Stack:** Vanilla JavaScript ES modules, MapLibre GL JS, Python validation scripts, Node.js regression scripts, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-16-world-map-consolidation-design.md`

## Global Constraints

- Target current `main`; refresh the base SHA before implementation if `main` advances.
- Do not merge PR #191 wholesale and do not replay its 129-commit history.
- Preserve the merged Physical Water zoom-handoff repair and bounded Places/subdivision runtime.
- Keep one primary MapLibre map application.
- Do not add polling or a second DOM `MutationObserver` for map coordination.
- Preserve same-origin browser data loading and lazy specialist loading.
- Preserve missing-data semantics and real-coordinate geography.
- Legacy `__potatoAtlasOverlayHandled` may remain only for consumers that are still genuinely unmigrated.
- Every runtime owner added in this plan must migrate a real consumer in the same task.
- Every task follows RED → minimal GREEN → focused validation → canonical World Map validation → commit.
- No Great Book, Bible, Story, SEO, or unrelated project content belongs in this implementation branch.

---

### Task 1: Reconstruct spatial-overlay interaction arbitration

**Files:**
- Create: `scripts/test_world_map_spatial_interaction_ownership.mjs`
- Create: `scripts/validate_world_map_spatial_interaction.py`
- Modify: `world-map/3d-spatial-overlays.js` around the existing per-layer click bindings and rendered-layer installation
- Modify: `scripts/validate_world_map_interaction_router.py` around interaction-owner contract checks
- Modify: `scripts/validate_world_map_source.py` to invoke the spatial interaction validator after the interaction-router validator

**Interfaces:**
- Consumes: `window.__potatoAtlasInteraction.register(owner, config)` and `.unregister(owner)` from `world-map/3d-interaction-router.js`.
- Produces: one semantic owner named `spatial-overlays`, `objectType:'spatial-overlay'`, click/hover priority `40`, with `featuresAt(event.point)` preserving all overlapping active overlay claims.

- [ ] **Step 1: Add the failing ownership regression**

Create `scripts/test_world_map_spatial_interaction_ownership.mjs` with the source-level assertions already proven on the historical branch:

```js
import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-spatial-overlays.js', import.meta.url), 'utf8');

assert.ok(source.includes('const interaction = window.__potatoAtlasInteraction'));
assert.ok(source.includes('function syncInteractionRegistration()'));
assert.ok(source.includes("interaction.register('spatial-overlays'"));
assert.ok(source.includes("objectType:'spatial-overlay'"));
assert.ok(source.includes('clickPriority:40'));
assert.ok(source.includes("features:featuresAt(event.point)"));
assert.ok(!source.includes("map.on('click', layerId"));

const installIndex = source.indexOf('rendered.set(row.id, { sourceId, layerIds });');
const syncIndex = source.indexOf('syncInteractionRegistration();', installIndex);
assert.ok(installIndex >= 0 && syncIndex > installIndex);

console.log('WORLD MAP SPATIAL INTERACTION OWNERSHIP REGRESSION PASSED');
```

Create `scripts/validate_world_map_spatial_interaction.py` to execute that Node regression with `subprocess.run(..., check=False)` and return non-zero on failure.

- [ ] **Step 2: Run RED**

Run:

```bash
node scripts/test_world_map_spatial_interaction_ownership.mjs
python scripts/validate_world_map_spatial_interaction.py
```

Expected: failure because current `main` still binds spatial-overlay interaction per rendered layer rather than through one router owner.

- [ ] **Step 3: Port the minimal shared-owner implementation**

In `world-map/3d-spatial-overlays.js`, add:

```js
const interaction = window.__potatoAtlasInteraction;

function syncInteractionRegistration() {
  if (!interaction?.register) return false;
  const layers = [...rendered.values()]
    .flatMap(state => state.layerIds || [])
    .filter(layerId => map.getLayer(layerId));
  if (!layers.length) {
    interaction.unregister?.('spatial-overlays');
    return false;
  }
  interaction.register('spatial-overlays', {
    layers,
    objectType:'spatial-overlay',
    clickPriority:40,
    hoverPriority:40,
    cursor:'pointer',
    onClick:event => emit('feature-click', {
      point:event.point,
      lngLat:event.lngLat,
      features:featuresAt(event.point),
    }),
  });
  return true;
}
```

After `rendered.set(row.id, { sourceId, layerIds });`, call `syncInteractionRegistration()`. Keep a direct-binding fallback only when the shared router is unavailable; the normal routed path must not install parallel per-layer click listeners.

- [ ] **Step 4: Join the validator chain and run GREEN**

Run:

```bash
node --check world-map/3d-spatial-overlays.js
node scripts/test_world_map_spatial_interaction_ownership.mjs
python scripts/validate_world_map_spatial_interaction.py
python scripts/validate_world_map_interaction_router.py
python scripts/validate_world_map_source.py
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/test_world_map_spatial_interaction_ownership.mjs \
        scripts/validate_world_map_spatial_interaction.py \
        scripts/validate_world_map_interaction_router.py \
        scripts/validate_world_map_source.py \
        world-map/3d-spatial-overlays.js
git commit -m "fix(world-map): centralize spatial overlay interaction"
```

---

### Task 2: Migrate Places to canonical scale and interaction ownership

**Files:**
- Create: `scripts/test_world_map_places_interaction_ownership.mjs`
- Create: `scripts/test_world_map_place_label_density.mjs`
- Modify: `world-map/3d-places.js` around layer installation, label layout, click binding, and initialization
- Modify: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_map_scale_contract.py`

**Interfaces:**
- Consumes: `window.__potatoAtlasInteraction`, `window.__potatoAtlasScale.ready`, `scale.threshold('places-detail', kind)`.
- Produces: one `places` interaction owner at priority `80`; detail render/label thresholds owned by the shared scale runtime; deterministic label ordering by national-capital status then population.

- [ ] **Step 1: Add RED regressions**

`test_world_map_places_interaction_ownership.mjs` must assert these source contracts:

```js
assert.ok(source.includes('const interaction = window.__potatoAtlasInteraction'));
assert.ok(source.includes("interaction.register('places'"));
assert.ok(source.includes("objectType:'place'"));
assert.ok(source.includes('clickPriority:80'));
assert.ok(source.includes('enabled:() => visible'));
assert.ok(source.includes('function bindFallbackLayerEvents()'));
```

`test_world_map_place_label_density.mjs` must assert that both major and detail labels use `text-variable-anchor`, `text-radial-offset`, `text-padding`, `text-allow-overlap:false`, and that the major label layer uses `symbol-sort-key` prioritizing national capitals and larger population.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_places_interaction_ownership.mjs
node scripts/test_world_map_place_label_density.mjs
```

Expected: at least the interaction and shared-scale assertions fail on current `main`.

- [ ] **Step 3: Port only the modern ownership changes**

At the top of `3d-places.js`:

```js
const interaction = window.__potatoAtlasInteraction;
```

Add shared scale resolution:

```js
async function scaleRuntime() {
  const scale = await window.__potatoAtlasScale?.ready;
  if (!scale?.threshold || !scale?.bandThreshold) {
    throw new Error('World Map Scale runtime unavailable to Places.');
  }
  return scale;
}
```

Make `installLayers()` async, obtain:

```js
const PLACE_DETAIL_RENDER_ZOOM = scale.threshold('places-detail', 'render');
const PLACE_DETAIL_LABEL_ZOOM = scale.threshold('places-detail', 'label');
```

Use those values for detail-layer `minzoom` and interpolation starts instead of raw `4.2` / `5.0` ownership.

Add the router owner:

```js
function syncInteractionRegistration() {
  if (!interaction?.register) return false;
  interaction.register('places', {
    layers:[MAJOR_POINTS, DETAIL_POINTS],
    objectType:'place',
    clickPriority:80,
    hoverPriority:80,
    cursor:'pointer',
    enabled:() => visible,
    onClick:(event, feature) => {
      const id = feature?.properties?.id;
      if (id) focus(id, {feature, fit:false});
    },
  });
  return true;
}
```

Keep the legacy direct layer listeners only in `bindFallbackLayerEvents()` and use them only if router registration fails.

Apply the label-density layout proven in PR #191:

```js
'symbol-sort-key':['+',
  ['case',['boolean',['get','is_national_capital'],false],0,1000000000],
  ['-',1000000000,['coalesce',['to-number',['get','population']],0]]
],
'text-variable-anchor':['top','bottom','left','right'],
'text-radial-offset':1.05,
'text-padding':['interpolate',['linear'],['zoom'],1.2,5,6,2],
'text-optional':true,
'text-allow-overlap':false
```

Await `installLayers()` during initialization so shared scale thresholds are available before layer creation.

- [ ] **Step 4: Run GREEN**

```bash
node --check world-map/3d-places.js
node scripts/test_world_map_places_interaction_ownership.mjs
node scripts/test_world_map_place_label_density.mjs
python scripts/validate_world_places.py
python scripts/validate_world_map_scale_contract.py
python scripts/validate_world_map_source.py
```

Expected: all pass without changing Places runtime budgets or adding a second capital renderer.

- [ ] **Step 5: Commit**

```bash
git add world-map/3d-places.js \
        scripts/test_world_map_places_interaction_ownership.mjs \
        scripts/test_world_map_place_label_density.mjs \
        scripts/validate_world_places.py \
        scripts/validate_world_map_scale_contract.py
git commit -m "refactor(world-map): migrate Places interaction and scale ownership"
```

---

### Task 3: Add typed Inspector Router and deterministic URL state

**Files:**
- Create: `world-map/3d-inspector-router.js`
- Create: `world-map/3d-inspector-url.js`
- Create: `scripts/test_world_map_inspector_router.mjs`
- Create: `scripts/test_world_map_inspector_url.mjs`
- Create: `scripts/test_world_map_inspector_consumers.mjs`
- Create: `scripts/validate_world_map_inspector_router.py`
- Modify: `world-map/3d-bootstrap.js` so Inspector Router and URL bridge load before Places/subdivision consumers
- Modify: `world-map/3d-places.js` around `panelSnapshot`, `renderInspector`, `focus`, and `clear`
- Modify: `world-map/3d-subdivisions.js` around inspector capture/restore and selection
- Modify: `scripts/validate_world_map_source.py`

**Interfaces:**
- Produces `window.__potatoAtlasInspector` with `setBaseline(node)`, `open(node)`, `back()`, `reset(node?)`, `current()`, `state()`.
- Produces `window.__potatoAtlasInspectorUrl` with canonical `inspect=` path plus legacy `country`, `subdivision`, `place` compatibility mirroring.
- Inspector node shape: `{ type, id, owner, parent?, render?, restore? }`.

- [ ] **Step 1: Write router and URL RED tests**

The router test must exercise this sequence:

```js
router.setBaseline({type:'country', id:'DNK', owner:'country', restore:()=>events.push('country')});
router.open({type:'subdivision', id:'DK-83', owner:'subdivisions', parent:{type:'country',id:'DNK'}, render:()=>events.push('subdivision')});
router.open({type:'place', id:'gn:2618425', owner:'places', parent:{type:'subdivision',id:'DK-83'}, render:()=>events.push('place')});
assert.equal(router.state().depth, 3);
assert.equal(router.current().type, 'place');
assert.equal(router.back(), true);
assert.equal(router.current().type, 'subdivision');
```

The URL test must prove:

```js
assert.equal(
  encodeInspectorPath([{type:'country',id:'DNK'},{type:'place',id:'gn:2618425'}]),
  'country:DNK/place:gn%3A2618425'
);
assert.deepEqual(
  decodeInspectorPath('country:DNK/subdivision:DK-83/place:gn%3A2618425').map(x => x.type),
  ['country','subdivision','place']
);
```

The consumer test must reject `panelSnapshot` ownership in Places/subdivisions and require `window.__potatoAtlasInspector` consumption.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_inspector_router.mjs
node scripts/test_world_map_inspector_url.mjs
node scripts/test_world_map_inspector_consumers.mjs
```

Expected: modules are missing and/or consumer assertions fail.

- [ ] **Step 3: Implement the typed router**

Create `3d-inspector-router.js` with the PR #191 behavior: normalize `type/id/owner`, keep a stack, invoke `render`/`restore`, emit `potato-atlas-inspector-change`, and expose the six methods above. Reject nodes missing `type`, `id`, or `owner`.

The critical open/back semantics are:

```js
function open(node) {
  const next = normalizeNode(node);
  if (!stack.length) throw new Error('inspector baseline must be set before opening a child node');
  const existingIndex = stack.findIndex(row => row.type === next.type && row.id === next.id && row.owner === next.owner);
  if (existingIndex >= 0) stack = stack.slice(0, existingIndex);
  else if (next.parent) {
    const parentIndex = stack.map((row, index) => ({ row, index }))
      .filter(({row}) => row.type === next.parent.type && row.id === next.parent.id)
      .at(-1)?.index;
    if (Number.isInteger(parentIndex)) stack = stack.slice(0, parentIndex + 1);
  }
  stack.push(next);
  invoke(next);
  snapshot('open');
  return true;
}
```

- [ ] **Step 4: Implement canonical inspector URL encoding**

Create `3d-inspector-url.js` using ordered types `country → subdivision → place`. `inspect=` is canonical; legacy query params remain mirrored for backward compatibility. Invalid ordering or malformed encoding must decode to `[]`, not partial state.

- [ ] **Step 5: Migrate Places and subdivisions away from raw panel snapshots**

Delete Places `panelSnapshot`, `captureInspector()`, and `restoreInspector()` ownership. Use a country baseline and child nodes:

```js
function countryBaseline(code) {
  const id = String(code || '').toUpperCase();
  return {
    type:'country', id, owner:'country',
    restore:() => { if (id && window.goCountry) window.goCountry(id); },
  };
}
```

Places open as `type:'place', owner:'places'`; subdivisions open as `type:'subdivision', owner:'subdivisions'`; `clear()` calls Inspector Router `back()` when the current child belongs to that subsystem.

Load the router and URL bridge in `3d-bootstrap.js` before consumer modules.

- [ ] **Step 6: Run GREEN**

```bash
node --check world-map/3d-inspector-router.js
node --check world-map/3d-inspector-url.js
node --check world-map/3d-places.js
node --check world-map/3d-subdivisions.js
node scripts/test_world_map_inspector_router.mjs
node scripts/test_world_map_inspector_url.mjs
node scripts/test_world_map_inspector_consumers.mjs
python scripts/validate_world_map_inspector_router.py
python scripts/validate_world_map_source.py
```

Expected: all pass and existing `?country=`, `?subdivision=`, `?place=` links remain restorable.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-inspector-router.js world-map/3d-inspector-url.js \
        world-map/3d-bootstrap.js world-map/3d-places.js world-map/3d-subdivisions.js \
        scripts/test_world_map_inspector_router.mjs scripts/test_world_map_inspector_url.mjs \
        scripts/test_world_map_inspector_consumers.mjs scripts/validate_world_map_inspector_router.py \
        scripts/validate_world_map_source.py
git commit -m "feat(world-map): add typed inspector routing"
```

---

### Task 4: Centralize style-generation restoration

**Files:**
- Create: `world-map/3d-style-lifecycle.js`
- Create: `scripts/test_world_map_style_lifecycle.mjs`
- Create: `scripts/validate_world_map_style_lifecycle.py`
- Modify: `world-map/3d-bootstrap.js` to load Style Lifecycle before physical/style-owning consumers
- Modify: `world-map/3d-physical-water.js`
- Modify: `world-map/3d-physical-land-cover.js`
- Modify: `world-map/3d-physical-hydrology.js`
- Modify: `world-map/3d-physical-deserts.js`
- Modify: `world-map/3d-render-stack.js`
- Modify: `scripts/validate_world_map_source.py`

**Interfaces:**
- Produces `window.__potatoAtlasStyleLifecycle.register(owner,{priority,restore})`, `.unregister(owner)`, `.schedule(reason)`, `.state()`.
- Physical restorers run before final Render Stack reconciliation.
- Exactly one active global `styledata` lifecycle owner remains after migration.

- [ ] **Step 1: Add the RED lifecycle regression**

Test a fake map and deterministic queue:

```js
const callbacks = {};
const queue = [];
const map = { on:(name, fn)=>{ callbacks[name]=fn; } };
const lifecycle = createStyleLifecycle(map, { queue:fn=>queue.push(fn), emit:()=>{} });
const order = [];
lifecycle.register('water', {priority:10, restore:()=>order.push('water')});
lifecycle.register('render-stack', {priority:1000, restore:()=>order.push('render-stack')});
callbacks.styledata();
callbacks.styledata();
assert.equal(queue.length, 1);
queue.shift()();
assert.deepEqual(order, ['water','render-stack']);
assert.equal(lifecycle.state().generation, 1);
assert.equal(lifecycle.state().styleEvents, 2);
```

Also source-scan migrated physical modules and fail if they still own independent `map.on('styledata'` listeners.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_style_lifecycle.mjs
```

Expected: module missing and duplicate style listeners still present.

- [ ] **Step 3: Implement Style Lifecycle**

Create the 102-line bounded service proven in PR #191: registration map, numeric priority sort, one coalesced microtask per burst, generation counter, restore/error list, one `styledata` listener, and `potato-atlas-style-generation` event.

Critical scheduler:

```js
function schedule(reason = 'styledata') {
  lastReason = reason;
  if (scheduled) return false;
  scheduled = true;
  enqueue(() => {
    scheduled = false;
    run(lastReason);
  });
  return true;
}
```

- [ ] **Step 4: Migrate real consumers and remove duplicate ownership**

Each physical module registers an idempotent restore callback instead of attaching its own global `styledata` listener. Register Render Stack with a later priority so physical sources/layers exist before final semantic reordering.

Do not alter the water `syncScaleDetail()` ownership introduced by PR #193.

- [ ] **Step 5: Run GREEN**

```bash
node --check world-map/3d-style-lifecycle.js
node scripts/test_world_map_style_lifecycle.mjs
python scripts/validate_world_map_style_lifecycle.py
python scripts/validate_world_map_render_stack.py
python scripts/validate_world_map_physical_water.py
python scripts/validate_world_map_source.py
```

Expected: all pass; source scan shows one active global style lifecycle owner.

- [ ] **Step 6: Commit**

```bash
git add world-map/3d-style-lifecycle.js world-map/3d-bootstrap.js \
        world-map/3d-physical-water.js world-map/3d-physical-land-cover.js \
        world-map/3d-physical-hydrology.js world-map/3d-physical-deserts.js \
        world-map/3d-render-stack.js scripts/test_world_map_style_lifecycle.mjs \
        scripts/validate_world_map_style_lifecycle.py scripts/validate_world_map_source.py
git commit -m "refactor(world-map): centralize style restoration lifecycle"
```

---

### Task 5: Add runtime telemetry and one integrated control-plane scenario

**Files:**
- Create: `world-map/3d-runtime-telemetry.js`
- Create: `scripts/test_world_map_runtime_telemetry.mjs`
- Create: `scripts/validate_world_map_runtime_telemetry.py`
- Create: `scripts/test_world_map_behavioral_scenario.mjs`
- Create: `scripts/validate_world_map_behavioral_scenarios.py`
- Modify: `world-map/3d-interaction-router.js` to expose `diagnostics()` and publish lightweight counters
- Modify: `world-map/3d-bootstrap.js` to load telemetry after control-plane owners exist
- Modify: `scripts/validate_world_map_source.py`

**Interfaces:**
- Interaction Router adds `diagnostics()` returning registration/enabled/click-owner/hover-owner/layer counts plus dispatch counters.
- Runtime telemetry consumes existing custom events; it must not poll.
- Integrated scenario covers antimeridian/wrapped identity, semantic interaction priority, inspector back/URL behavior, and stale tooltip invalidation using existing control-plane APIs.

- [ ] **Step 1: Add RED telemetry tests**

Extend the router regression to expect:

```js
const d = router.diagnostics();
assert.equal(typeof d.registrationCount, 'number');
assert.equal(typeof d.clickDispatches, 'number');
assert.equal(typeof d.hoverDispatches, 'number');
```

The telemetry test must reject `setInterval` / recursive `setTimeout` polling and assert subscriptions to existing lifecycle custom events.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_runtime_telemetry.mjs
node scripts/test_world_map_behavioral_scenario.mjs
```

Expected: telemetry module/diagnostics are absent.

- [ ] **Step 3: Add bounded router diagnostics**

In `3d-interaction-router.js`, add counters and:

```js
function diagnostics() {
  const rows = [...registrations.values()];
  const zoom = Number(map.getZoom?.());
  const enabledRows = rows.filter(row => row.enabled({ kind:'diagnostics', zoom }));
  return {
    registrationCount:rows.length,
    enabledCount:enabledRows.length,
    clickOwnerCount:activeRegistrations('click').length,
    hoverOwnerCount:activeRegistrations('hover').length,
    layerCount:new Set(rows.flatMap(row => row.layers)).size,
    activeHoverOwner:activeHover?.owner || null,
    clickDispatches,
    hoverDispatches,
  };
}
```

Publish only on register/unregister/dispatch/hover-clear events; do not poll.

- [ ] **Step 4: Implement event-driven runtime telemetry and integrated scenario**

The telemetry module aggregates current source/layer counts from MapLibre plus diagnostics already emitted by Interaction Router, Style Lifecycle, Tooltip, Places and subdivisions. Use custom-event listeners and on-demand snapshots only.

The behavioral scenario script imports pure/helper modules where available and uses fakes for map/router/inspector transitions. It must not depend on a live browser or remote network.

- [ ] **Step 5: Run GREEN**

```bash
node --check world-map/3d-interaction-router.js
node --check world-map/3d-runtime-telemetry.js
node scripts/test_world_map_runtime_telemetry.mjs
node scripts/test_world_map_behavioral_scenario.mjs
python scripts/validate_world_map_runtime_telemetry.py
python scripts/validate_world_map_behavioral_scenarios.py
python scripts/validate_world_map_source.py
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add world-map/3d-interaction-router.js world-map/3d-runtime-telemetry.js world-map/3d-bootstrap.js \
        scripts/test_world_map_runtime_telemetry.mjs scripts/validate_world_map_runtime_telemetry.py \
        scripts/test_world_map_behavioral_scenario.mjs scripts/validate_world_map_behavioral_scenarios.py \
        scripts/validate_world_map_source.py
git commit -m "feat(world-map): add control-plane runtime telemetry"
```

---

### Task 6: Reconcile legacy interaction compatibility and finish exact-head verification

**Files:**
- Modify only if required by the regression outcome: `world-map/3d-app.js`, `world-map/3d-country-selection.js`, `world-map/3d-hover.js`, `world-map/3d-gateways.js`, `world-map/3d-infrastructure.js`, `world-map/3d-axis.js`
- Modify: `scripts/validate_world_map_3d.py`
- Modify: `scripts/validate_world_map_interaction_router.py`
- Modify: `docs/WORLD-MAP-ROADMAP.md`
- Create: `docs/world-map-consolidation-dispositions.md` with the #191 disposition only for this plan

**Interfaces:**
- `__potatoAtlasOverlayHandled` remains only where an unmigrated compatibility consumer still needs it.
- The validator expresses the architecture, not an obsolete implementation marker.
- Roadmap checkboxes may move only when exact-head validation proves the behavior is on the integration branch.

- [ ] **Step 1: Inventory the marker on the reconstructed branch**

Run:

```bash
git grep -n '__potatoAtlasOverlayHandled' -- world-map scripts
```

Classify every occurrence as router-owned compatibility, active legacy consumer, regression fixture, or obsolete requirement.

- [ ] **Step 2: Write the failing compatibility regression before deleting any remaining marker**

For each runtime consumer selected for migration, add a source assertion proving it now registers with `window.__potatoAtlasInteraction` and no longer directly claims the marker. Do not globally assert zero marker occurrences until all consumers are migrated.

- [ ] **Step 3: Remove obsolete validator requirements first, then migrate any bounded remaining consumer**

If `scripts/validate_world_map_3d.py` still requires the marker in `3d-app.js`, replace that requirement with checks for the actual central interaction owner/module chain. Do not add the marker back merely to satisfy the validator.

- [ ] **Step 4: Run the full World Map gate locally**

```bash
node --check world-map/*.js
python scripts/validate_world_map_source.py
python scripts/validate_world_map_ui_shell.py
python scripts/validate_world_map_ui_layout.py
python scripts/validate_world_map_spatial_overlays.py
python scripts/validate_world_map_physical_water.py
```

Expected: all available focused World Map gates pass.

- [ ] **Step 5: Update roadmap and disposition record**

In `docs/world-map-consolidation-dispositions.md`, record:

```text
PR/branch: #191 / world-map-safety-wave-2-2026-09-16
Disposition: reconstructed, not merged wholesale
Integrated: <list only capabilities actually present on the branch>
Superseded: <list only capabilities current main already had more strongly>
Remaining: <list only work intentionally deferred>
Verification: exact reconstruction branch SHA + local focused gate + GitHub Actions run/conclusion
```

Use concrete values from the finished branch; do not mark roadmap items complete before verification.

- [ ] **Step 6: Commit documentation**

```bash
git add scripts/validate_world_map_3d.py scripts/validate_world_map_interaction_router.py \
        docs/WORLD-MAP-ROADMAP.md docs/world-map-consolidation-dispositions.md \
        world-map/3d-app.js world-map/3d-country-selection.js world-map/3d-hover.js \
        world-map/3d-gateways.js world-map/3d-infrastructure.js world-map/3d-axis.js
git commit -m "chore(world-map): reconcile safety wave 2 compatibility"
```

- [ ] **Step 7: Push and inspect exact-head CI**

Push the reconstruction branch, open/update its PR against `main`, then inspect the Repository quality checks run attached to the exact head SHA. If the canonical World Map runtime step fails, inspect the job log, fix only the demonstrated regression, rerun focused tests, and push another bounded commit.

Do not claim Safety Wave 2 integrated until the exact branch head is green or any remaining unrelated repository failure is explicitly distinguished from a passing World Map gate.

---

## Deferred to separate plans

The following are intentionally outside this implementation plan and require their own plan after Safety Wave 2 is integrated:

- porting PR #188 World Map architecture auditor;
- full archaeology/disposition sweep of every historical map branch;
- route-geometry physical-vs-schematic semantics;
- visual-channel compatibility matrix and country-style writer convergence;
- broader accessibility and legacy UI retirement;
- new economic/geopolitical data expansion.
