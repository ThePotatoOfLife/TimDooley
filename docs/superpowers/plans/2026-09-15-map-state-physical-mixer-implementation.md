# Map State + Physical Mixer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a whole-map reset coordinator and promote the Physical menu into a status-aware opacity mixer without reloading providers or moving the camera.

**Architecture:** Add `3d-map-state.js` as orchestration-only state coordinator. Extend `3d-physical-layers.js` to own generic lifecycle/status/opacity state while each physical controller continues to own its MapLibre paint/source behavior. Keep all UI inside the existing World Bar Physical menu.

**Tech Stack:** Vanilla JavaScript, MapLibre GL JS, JSON manifest metadata, Python contract validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-map-state-physical-mixer-design.md`

## Global Constraints

- Reset must preserve camera center, zoom, bearing, pitch, and projection.
- Reset must clear analytical, Physical, Geography/spatial, selection/pins, relation mode, and non-current Time state through public APIs.
- Physical data providers remain lazy/on-demand and provider failures remain nonfatal.
- Water, Hydrology, Land cover, and Deserts/xeric get one master opacity control; Terrain does not.
- Opacity changes must not refetch providers or recreate sources.
- Failed activation must not enter the Physical active set or survive in `physical=` URL state.
- No polling or `MutationObserver`.
- No new floating UI panel.

---

### Task 1: Contract validators

**Files:**
- Create: `scripts/validate_world_map_map_state.py`
- Modify: `scripts/validate_world_map_ui_layout.py`

**Interfaces:**
- Consumes: approved design contract.
- Produces: failing contract for `__potatoAtlasMapState`, Physical reset/status/opacity APIs, mixer controls, module opacity APIs, and Hydrology status markers.

- [ ] **Step 1: Write the failing validator**

Require:

```python
MAP_STATE = ROOT / "world-map" / "3d-map-state.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
PHYSICAL = ROOT / "world-map" / "3d-physical-layers.js"

for token in (
    "__potatoAtlasMapState", "clearAll", "keepView:true",
    "__potatoAtlasPhysicalLayers", "__potatoAtlasSpatialOverlays",
    "setRelationMode", "mode:'current'", "potato-atlas-map-state-reset",
):
    ...
```

Also require `reset`, `status`, `setOpacity`, `getOpacity`, `data-physical-opacity`, `Clear physical`, and opacity APIs in Water/Hydrology/Land cover/Deserts. Reject camera-changing reset markers (`jumpTo(`, `flyTo(`, `fitBounds(`, `easeTo(`, `setProjection(`) inside `3d-map-state.js`.

- [ ] **Step 2: Chain the validator into the existing UI validator**

Add `validate_world_map_map_state.py` beside the current Water/Land cover/Deserts/Hydrology validators and execute it as part of the World Map UI architecture gate.

- [ ] **Step 3: Run CI and verify RED**

Expected failure: missing `world-map/3d-map-state.js` and missing new Physical runtime/mixer contract markers. Existing Water/Land cover/Deserts/Hydrology gates should remain green.

- [ ] **Step 4: Commit the failing contract**

Commit only validator changes before production code.

---

### Task 2: Map State coordinator

**Files:**
- Create: `world-map/3d-map-state.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-world-bar.js`

**Interfaces:**
- Consumes: `__potatoAtlasCompositor.reset()`, `__potatoAtlasPhysicalLayers.reset()`, `__potatoAtlasSpatialOverlays.reset()`, `__potatoAtlasSelection.clearAll({keepView:true})`, `__potatoAtlasSelection.setRelationMode('all')`, `__potatoAtlasTime.setState({mode:'current',time:'',time2:''})` when available.
- Produces: `window.__potatoAtlasMapState = { reset, snapshot }` and event `potato-atlas-map-state-reset`.

- [ ] **Step 1: Implement snapshot and isolated reset steps**

Use an ordered array of async steps. Each step is wrapped so failure is appended to `failed` and later steps still execute.

- [ ] **Step 2: Normalize Time without forcing module load**

If `__potatoAtlasTime` exists, call its public API. Otherwise remove only `timeMode`, `time`, `time2`, `timeDate`, and `timeDate2` URL parameters.

- [ ] **Step 3: Bind World Bar × to the coordinator**

Replace direct compositor reset with:

```js
reset.addEventListener('click', () => window.__potatoAtlasMapState?.reset?.());
```

- [ ] **Step 4: Load coordinator through lifecycle**

Load `./3d-map-state.js` after Physical/spatial/selection APIs are available but before ordinary toolbar interaction depends on reset.

- [ ] **Step 5: Run the new validator**

Expected: Map State-specific assertions pass; Physical mixer assertions may still fail until Task 3.

---

### Task 3: Physical runtime state + mixer

**Files:**
- Modify: `world-map/3d-physical-layers.js`
- Modify: `data/world-map-physical-layers.json`

**Interfaces:**
- Produces: `reset()`, `status(id)`, `setOpacity(id,value)`, `getOpacity(id)` and richer Physical menu.
- Consumes controller APIs `enable`, `disable`, optional `setOpacity`, `getOpacity`.

- [ ] **Step 1: Add generic status records**

Initialize one record per manifest entry with `idle`, `active:false`, manifest `default_opacity`, message, and timestamp.

- [ ] **Step 2: Fix activation semantics**

Set `loading` before module activation. If `enable()` throws or returns `false`, keep the layer inactive, set `error`, and normalize URL state. On success, add to active set and mark `active` unless a module already reported a more specific phase.

- [ ] **Step 3: Add runtime opacity API**

Clamp requested opacity to `[0,1]`, call controller `setOpacity`, and update runtime state only after controller success.

- [ ] **Step 4: Add aggregate Physical reset**

Disable active entries, clear active set and `physical=` once, restore runtime opacities to manifest defaults, and emit one aggregate change.

- [ ] **Step 5: Build mixer UI in existing Physical menu**

Rows keep toggle behavior and include state text. Active eligible layers get an accessible range input with `data-physical-opacity`; Terrain does not. Add `Clear physical` footer when active set is non-empty.

- [ ] **Step 6: Consume module status events**

Listen for `potato-atlas-physical-layer-status` from known IDs only and update menu/runtime status.

---

### Task 4: Controller opacity + Hydrology reporting

**Files:**
- Modify: `world-map/3d-physical-water.js`
- Modify: `world-map/3d-physical-hydrology.js`
- Modify: `world-map/3d-physical-land-cover.js`
- Modify: `world-map/3d-physical-deserts.js`

**Interfaces:**
- Each eligible controller produces `setOpacity(value)` and `getOpacity()`.
- Hydrology emits `potato-atlas-physical-layer-status` for `zoom-needed`, `loading`, `active`, `partial`, and `error`.

- [ ] **Step 1: Land cover master opacity**

Replace fixed runtime use of `OPACITY` with mutable clamped state and set `raster-opacity` directly.

- [ ] **Step 2: Hydrology master opacity**

Multiply existing basin fill, basin line, and river line baseline opacities by one mutable master opacity. Emit status on zoom gate, request start, complete, partial, and no-usable-data/error paths.

- [ ] **Step 3: Water master opacity**

Apply one master multiplier to existing lake/river/coastline baseline opacity values across overview/detail tiers without source reload.

- [ ] **Step 4: Deserts/xeric master opacity**

Apply one master multiplier to existing fill/line baseline opacity values without source reload.

- [ ] **Step 5: Run focused validators**

Run Map State/UI architecture, Water, Land cover, Deserts, Hydrology, and Terrain validators.

---

### Task 5: Regression verification

**Files:**
- No production changes unless tests expose a real defect.

**Interfaces:**
- Consumes all completed implementation.
- Produces a verified feature branch ready for review/merge.

- [ ] **Step 1: Run focused map validation suite**

Expected all pass:

```text
validate_world_map_map_state.py
validate_world_map_ui_layout.py
validate_world_map_physical_water.py
validate_world_map_land_cover.py
validate_world_map_deserts.py
validate_world_map_hydrology.py
validate_world_map_terrain.py (if present)
```

- [ ] **Step 2: Run full repository quality checks through PR CI**

Require exact branch head success before claiming implementation complete.

- [ ] **Step 3: Review diff for scope**

Confirm no render-stack refactor, Physical Inspector work, provider migration, tactical tracking, new floating panel, polling, or MutationObserver slipped into this slice.
