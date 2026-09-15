# World Map Render Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace optional-layer load-order-dependent z-order with a deterministic semantic render-stack coordinator used by Physical, spatial overlays, and infrastructure.

**Architecture:** Add `world-map/3d-render-stack.js` as a small always-on ordering service that registers `{layerId, slot, priority, owner}` metadata and reconciles actual MapLibre order with `map.moveLayer()`. Existing modules retain source/data/visibility/click ownership and only register their rendered layers; the service never removes layers or changes paint/source semantics.

**Tech Stack:** JavaScript ES modules, MapLibre GL JS, Python repository validators, GitHub Actions repository quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-15-world-map-render-stack-design.md`

## Global Constraints

- Work from the exact PR #156 green head plus the approved render-stack spec.
- TDD is mandatory: validator RED before production code.
- No synthetic/invisible anchor layers.
- No MutationObserver, setInterval, or polling loops.
- No new map UI or user-defined z-order controls.
- No provider/data/source migrations.
- Preserve Physical mixer status/opacity/reset behavior.
- Preserve spatial-overlay epistemic classifications and click/reset behavior.
- Preserve infrastructure context and Impact behavior.
- Never merge directly to `main` during implementation.

---

### Task 1: Add the RED render-stack architecture validator

**Files:**
- Create: `scripts/validate_world_map_render_stack.py`
- Modify: `scripts/validate_world_map_ui_layout.py`

**Interfaces:**
- Consumes: existing repository file layout and module names.
- Produces: one validator that fails until the coordinator, lifecycle loader, and module registrations exist.

- [ ] **Step 1: Write the failing validator**

The validator must require:

```python
RENDER_STACK = ROOT / "world-map" / "3d-render-stack.js"
PHYSICAL_MODULES = {
    "terrain": ROOT / "world-map" / "3d-physical-terrain.js",
    "water": ROOT / "world-map" / "3d-physical-water.js",
    "hydrology": ROOT / "world-map" / "3d-physical-hydrology.js",
    "land-cover": ROOT / "world-map" / "3d-physical-land-cover.js",
    "deserts": ROOT / "world-map" / "3d-physical-deserts.js",
}
SPATIAL = ROOT / "world-map" / "3d-spatial-overlays.js"
INFRASTRUCTURE = ROOT / "world-map" / "3d-infrastructure.js"
PANEL = ROOT / "world-map" / "3d-panel-lifecycle.js"
```

Require coordinator markers:

```python
for token in (
    "__potatoAtlasRenderStack", "register", "unregister", "reconcile",
    "state", "slotOrder", "physical-surface", "physical-line",
    "geography-context", "context-network", "selection-emphasis",
    "moveLayer", "potato-atlas-render-stack-change",
):
    ...
```

Reject coordinator tokens:

```python
for forbidden in ("MutationObserver", "setInterval", "removeLayer(", "removeSource(", "setPaintProperty("):
    ...
```

Require lifecycle ordering:

```python
render_index = lifecycle.index("./3d-render-stack.js")
physical_index = lifecycle.index("./3d-physical-layers.js")
if render_index > physical_index:
    errors.append("Render Stack must load before Physical World")
```

Require Physical registrations with slot strings, spatial `geography-context`, and infrastructure `context-network`.

- [ ] **Step 2: Chain it into UI-layout validation**

Add:

```python
RENDER_STACK_VALIDATOR = ROOT / "scripts" / "validate_world_map_render_stack.py"
```

Include it in required paths and validator subprocesses before the existing map-state/Physical checks.

- [ ] **Step 3: Run validation and prove RED**

Run in CI through the feature PR. Expected failure: missing `world-map/3d-render-stack.js` and missing registration/lifecycle markers.

- [ ] **Step 4: Commit the RED test**

Commit message:

```text
test(world-map): require shared render stack contract
```

---

### Task 2: Add the render-stack coordinator and lifecycle loading

**Files:**
- Create: `world-map/3d-render-stack.js`
- Modify: `world-map/3d-panel-lifecycle.js`

**Interfaces:**
- Produces:
  - `register(layerId, {slot, priority=0, owner=''}) -> boolean`
  - `unregister(layerId) -> boolean`
  - `reconcile(reason='manual') -> object`
  - `state() -> {entries,lastReason,reconcileCount}`
  - `slotOrder() -> string[]`

- [ ] **Step 1: Implement declared slots and registry**

Use:

```js
const SLOT_ORDER = Object.freeze([
  'physical-surface',
  'physical-line',
  'geography-context',
  'context-network',
  'selection-emphasis',
]);
const entries = new Map();
```

Validate slots, normalize priority to finite number, and schedule reconciliation once per turn with `queueMicrotask`.

- [ ] **Step 2: Implement deterministic sort and anchor resolution**

Sort within each slot by:

```js
(a, b) => a.priority - b.priority || a.layerId.localeCompare(b.layerId)
```

Anchor regions:

```js
physical-surface -> before countries-fill
physical-line + geography-context + context-network -> before countries-line
selection-emphasis -> before country-hubs, else country-labels
```

If an anchor or registered layer is absent, skip nonfatally.

- [ ] **Step 3: Implement minimal move reconciliation**

Read current style order from:

```js
map.getStyle()?.layers?.map(layer => layer.id) || []
```

Only call `map.moveLayer(layerId, beforeId)` when current placement is not already desired. Catch per-layer move failures and continue.

- [ ] **Step 4: Emit diagnostics**

After each pass:

```js
window.dispatchEvent(new CustomEvent('potato-atlas-render-stack-change', {
  detail:{ reason, moved, registered:entries.size, missing }
}));
```

- [ ] **Step 5: Add lifecycle triggers**

Register one-shot reconciliation for `styledata` and `potato-atlas-module-ready`. Do not poll.

- [ ] **Step 6: Load coordinator before Physical World**

In `3d-panel-lifecycle.js`, ensure startup sequence contains:

```text
UI Layout -> Render Stack -> Map State -> Physical World
```

- [ ] **Step 7: Run focused validator**

Expected: coordinator/lifecycle checks pass; migration checks still fail.

- [ ] **Step 8: Commit**

```text
feat(world-map): add shared render stack coordinator
```

---

### Task 3: Migrate Physical modules to semantic stack registration

**Files:**
- Modify: `world-map/3d-physical-terrain.js`
- Modify: `world-map/3d-physical-water.js`
- Modify: `world-map/3d-physical-hydrology.js`
- Modify: `world-map/3d-physical-land-cover.js`
- Modify: `world-map/3d-physical-deserts.js`
- Modify validators: `scripts/validate_world_map_terrain.py`, `scripts/validate_world_map_physical_water.py`, `scripts/validate_world_map_hydrology.py`, `scripts/validate_world_map_land_cover.py`, `scripts/validate_world_map_deserts.py`

**Interfaces:**
- Consumes `window.__potatoAtlasRenderStack?.register?.(...)`.
- Keeps every existing public controller API unchanged.

- [ ] **Step 1: Add one local registration helper per module**

Pattern:

```js
const renderStack = () => window.__potatoAtlasRenderStack;
function registerLayer(layerId, slot, priority) {
  renderStack()?.register?.(layerId, { slot, priority, owner:'physical.water.base' });
}
```

Use the correct owner for each module.

- [ ] **Step 2: Register Terrain**

Hillshade:

```js
slot:'physical-surface', priority:10
```

- [ ] **Step 3: Register Land cover**

Raster:

```js
slot:'physical-surface', priority:20
```

- [ ] **Step 4: Register Water**

Lake fills in `physical-surface` priority `30`.
Coast/lake/river line layers in `physical-line` priorities `20..29` in stable visual order.

- [ ] **Step 5: Register Deserts/xeric**

Fill:

```js
physical-surface / 40
```

Boundary:

```js
physical-line / 40
```

- [ ] **Step 6: Register Hydrology**

Basin fill:

```js
physical-surface / 50
```

Basin boundary:

```js
physical-line / 50
```

Rivers:

```js
physical-line / 60
```

- [ ] **Step 7: Preserve style reload behavior**

After a module recreates missing layers, call its registration helper again or `renderStack()?.reconcile?.('style-restore')`.

- [ ] **Step 8: Update dedicated validators**

Replace ordering assertions that depend on `countries-fill`/`countries-line` with assertions for `__potatoAtlasRenderStack`, expected slot names, and relevant priority markers. Do not weaken provider/status/opacity checks.

- [ ] **Step 9: Run focused Physical validators**

Run each dedicated validator and the shared render-stack validator; expected PASS.

- [ ] **Step 10: Commit**

```text
refactor(world-map): register Physical layers with render stack
```

---

### Task 4: Migrate spatial overlays and infrastructure

**Files:**
- Modify: `world-map/3d-spatial-overlays.js`
- Modify: `world-map/3d-infrastructure.js`
- Modify any existing dedicated validators for these modules if they encode old insertion anchors.

**Interfaces:**
- Spatial rendered layers register in `geography-context`.
- Infrastructure point layer registers in `context-network`.

- [ ] **Step 1: Add spatial registration helper**

Register each created overlay layer with owner `spatial-overlays` and:

```js
slot:'geography-context'
priority:100 + localOrder
```

Derive `localOrder` deterministically from the overlay's own layer sequence, not activation time or epistemic classification.

- [ ] **Step 2: Retire direct label anchor as primary contract**

Allow a fallback `beforeId` only if render-stack is unavailable during partial boot; always register after layer creation.

- [ ] **Step 3: Register infrastructure points**

After ensuring `atlas-infrastructure-points`:

```js
window.__potatoAtlasRenderStack?.register?.('atlas-infrastructure-points', {
  slot:'context-network', priority:20, owner:'infrastructure'
});
```

- [ ] **Step 4: Preserve click/inspector/reset behavior**

Do not alter spatial click claiming, overlay reset, infrastructure popups, source data, or Impact calls.

- [ ] **Step 5: Run render-stack and existing spatial/infrastructure validators**

Expected PASS.

- [ ] **Step 6: Commit**

```text
refactor(world-map): order contextual layers through render stack
```

---

### Task 5: Full verification and stacked PR

**Files:**
- No production changes unless verification exposes a real defect.

**Interfaces:**
- Produces one reviewable stacked PR with exact-head CI evidence.

- [ ] **Step 1: Run/trigger full repository quality on exact feature head**

Required World Map steps must be green, including UI layout, map state, Physical modules, spatial overlays, and infrastructure.

- [ ] **Step 2: Inspect any failure before patching**

If CI fails, fetch the failing job steps/logs and fix only the demonstrated defect. Add/adjust a regression test first when behavior changes.

- [ ] **Step 3: Re-run exact-head verification**

Record exact feature SHA and workflow run number/ID with `conclusion: success`.

- [ ] **Step 4: Open stacked PR**

Base branch:

```text
feat/map-state-physical-mixer
```

Head branch:

```text
feat/world-map-render-stack
```

PR description must state it is intentionally stacked on #156 and should not merge to `main` independently unless rebased/retargeted and reverified.

- [ ] **Step 5: Stop before merge**

Report exact tested head, PR number, and CI status. Do not merge without a separate user instruction.
