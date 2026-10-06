# World Map Hover / Water Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ordinary country browsing coherent across map view, hover, selection and pins; guarantee population stays visible for the current country subject; and remove the globe water-fold artifact without weakening water detail.

**Architecture:** Preserve the existing ownership model. `3d-interaction-router.js` remains the semantic hit-test owner and gains a read-only current-hover snapshot; `3d-context-status.js` becomes the lightweight presentation adapter that temporarily previews a hovered country while selection remains persistent; `3d-country-card.js` remains the deep selected-country surface. Water stops feeding the world-spanning Natural Earth ocean polygon into a globe fill; instead it draws a seam-safe ocean base below the canonical country geometry while retaining Natural Earth coastline/lake/river detail and the existing 110m→50m regional detail switch.

**Tech Stack:** MapLibre GL JS 6.9, browser ES modules, Node contract tests, Python repository validators.

**Spec:** `docs/superpowers/specs/2026-09-17-world-map-context-visibility-design.md`

## Global Constraints

- Do not create a second canonical selection owner or inspector.
- Hover is ephemeral and must never mutate country selection, pins, URL state, automatic relations, Evidence, Trace or Path state.
- Click/tap remains the act that commits a country selection.
- Population is always present in the visible country-subject summary; unknown values render explicitly as `—`, never by removing the field.
- Current Map View remains the stable question; hover/selection only change the subject answering that question.
- Physical water remains lazy/on-demand, Natural Earth detail remains pinned to `ca96624a56bd078437bca8184e78163e5039ad19`, and provider failure stays nonfatal.
- Do not use a raw world-spanning ocean GeoJSON fill in globe projection.
- Preserve centralized Render Stack, Style Lifecycle and Interaction Router ownership.

---

### Task 1: Make hover identity readable and stable

**Files:**
- Modify: `world-map/3d-interaction-router.js`
- Modify: `scripts/test_world_map_interaction_router.mjs`

**Interfaces:**
- Produces: `window.__potatoAtlasInteraction.currentHover()` returning `null` or `{ key, owner, objectType, layerId, feature }`.
- Preserves: existing `register`, `unregister`, `resolve`, `dispatch`, `clearHover`, `state`, `diagnostics` APIs.

- [ ] **Step 1: Write the failing regression**

Add a hover registration whose country features expose `iso3` but no generic `id`. Dispatch hover over `DNK`, then `DEU`, and assert `currentHover().feature.properties.iso3` changes to `DEU`. Assert `clearHover()` returns the snapshot to `null`.

- [ ] **Step 2: Run the focused test and confirm RED**

Run: `node scripts/test_world_map_interaction_router.mjs`

Expected before implementation: failure because `currentHover` is undefined and the current key fallback cannot distinguish id-less country features.

- [ ] **Step 3: Implement semantic feature identity and read-only hover state**

Use feature identity precedence `feature.id → properties.id → iso3/cca3/ISO_A3/code → name/NAME/ADMIN`, update `activeHover` on every resolved hover, and expose:

```js
function currentHover() {
  if (!activeHover) return null;
  const { key, owner, winner } = activeHover;
  return { key, owner, objectType:winner.objectType, layerId:winner.layerId, feature:winner.feature };
}
```

Do not expose mutable router internals other than the already-returned feature object.

- [ ] **Step 4: Re-run the focused test and confirm GREEN**

Run: `node scripts/test_world_map_interaction_router.mjs`

Expected: PASS.

### Task 2: Couple Current Map View, hover and selection without conflating state

**Files:**
- Modify: `world-map/3d-context-status.js`
- Modify: `scripts/test_world_map_context_status.mjs`

**Interfaces:**
- Consumes: `__potatoAtlasInteraction.currentHover()`, `__potatoAtlasSelection.current`, `__potatoAtlasSelection.countryName(code)`, `__potatoAtlasDataRuntime.populationObservation(code)`, `__potatoAtlasActiveView.forCountry(code)`, `__potatoAtlasContextVisibility.current`.
- Produces: one compact status surface with three presentation modes: `Preview`, `Selected`, `Current view`.

- [ ] **Step 1: Write contract assertions first**

Require the status module to contain the markers `currentHover`, `Population`, `Preview`, `Selected`, `potato-atlas-interaction-state`, and `__potatoAtlasActiveView` while preserving the existing context/time/pin markers.

- [ ] **Step 2: Run the status test and confirm RED**

Run: `node scripts/test_world_map_context_status.mjs`

Expected before implementation: missing hover/presentation markers.

- [ ] **Step 3: Implement the presentation adapter**

Resolve subject precedence as:

```text
hovered country > selected country > no country subject
```

For a country subject always show `Population · <value or —>`. When an analytical scalar is active, also show the active-view label/value/source/period; when set-membership is active, show Matches/Outside plus compact membership labels. Keep mode/scale/pins/time/relation metadata in a secondary context line. Hover renders `Preview · <country>` and never invokes a selection mutator. Mouse leave restores `Selected · <country>` or the neutral `Current view` summary.

Use a render generation counter so slow population/active-view responses cannot overwrite a newer hover subject.

- [ ] **Step 4: Re-run the status test and confirm GREEN**

Run: `node scripts/test_world_map_context_status.mjs`

Expected: PASS.

### Task 3: Remove the polar/antimeridian ocean fold

**Files:**
- Modify: `world-map/3d-physical-water.js`
- Modify: `data/world-map-physical-layers.json`
- Modify: `scripts/validate_world_map_physical_water.py`

**Interfaces:**
- Preserves controller: `window.__potatoAtlasPhysicalWater` with `enable`, `disable`, `toggle`, `setOpacity`, `getOpacity`, `detailInstalled`.
- Preserves detail threshold: `DETAIL_ZOOM = 3.4` for coastline/lakes/rivers.
- Produces seam-safe base source/layers: `atlas-physical-water-ocean-grid` and `atlas-physical-water-land-mask`.

- [ ] **Step 1: Make the validator reject raw global ocean fills**

Require the seam-safe base markers and reject active source loading of `ne_110m_ocean.geojson` / `ne_50m_ocean.geojson`. Keep Natural Earth 110m/50m requirements for coastline, lakes and rivers.

- [ ] **Step 2: Run the water validator and confirm RED**

Run: `python scripts/validate_world_map_physical_water.py`

Expected before implementation: failure because the current module still loads Natural Earth ocean polygons directly.

- [ ] **Step 3: Implement the seam-safe ocean base**

Create a small in-memory FeatureCollection of longitude/latitude rectangles that do not cross the antimeridian or touch ±90°, add it as a GeoJSON source with `buffer:0`, and render it below country fill through the `physical-surface` Render Stack slot. Add a land-mask fill referencing the canonical `countries` source with the ordinary map background color so country tint compositing stays unchanged. Keep Natural Earth lake fills, lake lines, river lines and coastline lines above the country fill through existing water/line slots.

Overview/detail switching at zoom 3.4 changes only Natural Earth detail line/fill geometry; the ocean base remains stable at all zooms.

- [ ] **Step 4: Update provenance copy precisely**

Change the Water manifest description to state that ocean color is a seam-safe globe base clipped by canonical country geometry while Natural Earth provides 1:110m/1:50m coastline/lake/river detail. Keep the pinned Natural Earth commit and attribution.

- [ ] **Step 5: Re-run the validator and syntax checks**

Run: `python scripts/validate_world_map_physical_water.py`

Expected: PASS, including `node --check world-map/3d-physical-water.js` when Node is present.

### Task 4: Integration verification

**Files:**
- Modify only if a regression proves an integration contract needs updating.

- [ ] **Step 1: Run focused regressions**

```bash
node scripts/test_world_map_interaction_router.mjs
node scripts/test_world_map_context_status.mjs
python scripts/validate_world_map_physical_water.py
python scripts/validate_world_map_context_visibility.py
python scripts/validate_world_map_render_stack.py
python scripts/validate_world_map_style_lifecycle.py
python scripts/validate_world_map_ui_shell.py
```

Expected: all PASS.

- [ ] **Step 2: Run the canonical World Map validator**

Run: `python scripts/validate_world_map_3d.py`

Expected: PASS.

- [ ] **Step 3: Review the diff for ownership drift**

Confirm there is still one selection owner, one Interaction Router, one Context / Visibility Orchestrator, one Render Stack, no hover-triggered URL or relation mutation, and no raw global ocean polygon fill.

- [ ] **Step 4: Open a focused PR from `world-map-hover-water-polish-2026-09-17` to `main`**

PR summary must call out the browse-state contract, population invariant, semantic hover-key fix, and the polar/antimeridian water root cause.