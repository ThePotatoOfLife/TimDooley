# Sacred / Covenant Map Overlays Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the first working Sacred / Covenant Geography slice on the canonical World Map: independently toggleable and overlapping sacred/textual/current layers, correct Palestine entity handling, source/status metadata, and a safe non-tactical conflict-context contract.

**Architecture:** Keep `world-map/3d-app.js` as the country-renderer owner and keep analytical `layers=` state untouched. Add a focused spatial-overlay registry/runtime that owns `overlays=` URL state, loads repository-owned GeoJSON lazily, renders deterministic stacked MapLibre layers, and reports every overlapping feature to the inspector rather than merging meanings. Current Israel/Palestine geography is handled as a source-aware spatial layer and canonical entity alias, while future OCHA/ACLED feeds plug into the same contract without live unit tracking.

**Tech Stack:** Static GitHub Pages, vanilla JavaScript ES modules, MapLibre GL JS 6.9, GeoJSON/WGS84, Python repository validators, JSON manifests.

**Spec:** `docs/superpowers/specs/2026-09-15-sacred-covenant-geography-conflict-layers-design.md`

## Global Constraints

- Sacred/project, textual, historical, political-ideological, current-observed, disputed, humanitarian and conflict-event geography remain explicitly distinct.
- Multiple spatial overlays may overlap; overlap is intentional and must enumerate all active meanings rather than collapse them.
- `layers=` remains the analytical registry contract; spatial scenarios use `overlays=`.
- `PSE` is one canonical State of Palestine entity whose geometry may contain disconnected West Bank and Gaza components.
- No real-time or near-real-time tracking of individual tanks, aircraft, troops, units or operational routes.
- Conflict context must be delayed/aggregated, dated, source-attributed and analytical.
- Uncertain ancient geography must expose confidence/status notes instead of invented precision.
- Current/disputed boundary rendering must expose source/viewpoint semantics rather than claim a single politically neutral truth.

---

### Task 1: Canonical spatial-overlay contract and validation

**Files:**
- Create: `data/world-map-spatial-overlays.json`
- Create: `data/world-map-spatial/sacred-covenant-foundation.geojson`
- Create: `scripts/validate_world_map_spatial_overlays.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: project concepts from the design spec and existing Mesopotamia/Eden/Israel/Palestine knowledge records.
- Produces: manifest records keyed by `id`; GeoJSON features keyed by stable `feature_id`; validator enforcing epistemic/source/confidence/geometry contracts.

- [ ] **Step 1: Write the failing validator**

Validator must fail when any overlay lacks `id`, `label`, `family`, `epistemic_type`, `geometry_owner`, `feature_ids`, `source_ids`, `confidence`, `measurable`, or `visual.legend_class`; when an `epistemic_type` is outside the spec enum; when a referenced GeoJSON file or feature is missing; or when a GeoJSON feature lacks `feature_id`, `overlay_id`, `epistemic_type`, `source_ids`, `geometry_version`, `confidence`, `status_note`, and `measurement_policy`.

- [ ] **Step 2: Run the validator and confirm failure**

Run: `python scripts/validate_world_map_spatial_overlays.py`

Expected: non-zero exit because the manifest/GeoJSON owners do not yet exist.

- [ ] **Step 3: Add the foundation manifest and GeoJSON**

Initial overlay ids:

```text
father.mesopotamia-core
father.eden-context
father.four-rivers.tigris
father.four-rivers.euphrates
father.return-path
biblical.dan-to-beersheba
biblical.numbers-34
biblical.genesis-15
biblical.ezekiel-47
current.palestine
current.israel
conflict.context
```

Only features with supportable geometry are marked `availability: "current"`; scenario stubs that still need a sourced reconstruction remain `availability: "planned"` and are not activatable.

- [ ] **Step 4: Re-run validator**

Run: `python scripts/validate_world_map_spatial_overlays.py`

Expected: PASS.

- [ ] **Step 5: Wire validator into quality checks**

Add `python scripts/validate_world_map_spatial_overlays.py` beside the existing World Map validators.

- [ ] **Step 6: Commit**

```bash
git add data/world-map-spatial-overlays.json data/world-map-spatial/sacred-covenant-foundation.geojson scripts/validate_world_map_spatial_overlays.py .github/workflows/quality-checks.yml
git commit -m "feat(world-map): define spatial overlay contract"
```

### Task 2: Spatial overlay runtime with overlap-preserving rendering

**Files:**
- Create: `world-map/3d-spatial-overlays.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Consumes: `window.__potatoAtlasMap`, `data/world-map-spatial-overlays.json`, repository GeoJSON owners, URL parameter `overlays`.
- Produces: `window.__potatoAtlasSpatialOverlays` with `ready`, `entries()`, `active()`, `isActive(id)`, `activate(id)`, `deactivate(id)`, `toggle(id)`, `reset()`, `fit(id)`, and `featuresAt(point)`.

- [ ] **Step 1: Extend the World Map validator with runtime markers**

Require `3d-spatial-overlays.js`, `overlays`, `__potatoAtlasSpatialOverlays`, `queryRenderedFeatures`, `epistemic_type`, and explicit deterministic z-order markers.

- [ ] **Step 2: Run validator and confirm failure**

Run: `python scripts/validate_world_map_3d.py`

Expected: FAIL on missing spatial-overlay runtime.

- [ ] **Step 3: Implement manifest loading and URL state**

`3d-spatial-overlays.js` loads the manifest once, restores comma-separated `overlays=`, rejects non-current ids, and persists only active ids without touching `layers=`.

- [ ] **Step 4: Implement deterministic MapLibre rendering**

Render independent source/layer pairs by epistemic class. Use separate fill, line and symbol channels, stable z-order, and per-feature metadata. Never union or dissolve active polygons merely because they overlap.

- [ ] **Step 5: Implement overlap inspection**

`featuresAt(point)` uses MapLibre rendered-feature queries across active spatial layers and returns all distinct matching features ordered by display z-order. This is the mechanism that makes overlapping Father/Eden/biblical/current/disputed layers a feature rather than a bug.

- [ ] **Step 6: Load the module from bootstrap after the core map becomes interactive**

Add `Spatial Overlays` as a loaded core enhancement after the analytical layer registry/compositor and before specialist inspection modules.

- [ ] **Step 7: Re-run validator**

Run: `python scripts/validate_world_map_3d.py`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add world-map/3d-spatial-overlays.js world-map/3d-bootstrap.js scripts/validate_world_map_3d.py
git commit -m "feat(world-map): render overlapping spatial overlays"
```

### Task 3: Sacred geography controls and inspector semantics

**Files:**
- Modify: `world-map/index.html`
- Create: `world-map/3d-spatial-overlay-ui.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `scripts/validate_world_map_ui_shell.py`

**Interfaces:**
- Consumes: `window.__potatoAtlasSpatialOverlays` and its change events.
- Produces: Layers-menu spatial controls, active-overlay badges, overlap inspector cards, and boundary-view placeholder state.

- [ ] **Step 1: Add failing UI-shell expectations**

Require a `Sacred / territorial overlays` section, `atlasSpatialOverlayHost`, and UI markers for `Father’s Land`, `Eden`, `Chosen Children’s Land`, `State of Palestine`, `Israel`, and `Boundary view`.

- [ ] **Step 2: Run validator and confirm failure**

Run: `python scripts/validate_world_map_ui_shell.py`

Expected: FAIL on missing spatial overlay controls.

- [ ] **Step 3: Add stable host to Layers menu**

Keep the existing top-level shell and one-level-deep menu structure; add a host inside `layersMenu` rather than another top-level menu.

- [ ] **Step 4: Implement grouped toggles**

Groups:

```text
Father’s Land / Eden
Chosen Children’s Land / biblical scenarios
Current Israel / Palestine
Conflict context
```

Planned/unavailable scenarios render disabled with a clear status note. Active overlays can coexist without mutual exclusion.

- [ ] **Step 5: Implement overlap inspector**

Clicking an active spatial feature shows every active feature at that point with label, epistemic type, confidence, source ids, status note, textual reference/date and geometry version. The UI must explicitly say when several overlays overlap.

- [ ] **Step 6: Add boundary-view state shell**

Expose `Atlas / de-facto base` now and reserve disabled/source-dependent options for `ISO`, `Israel viewpoint`, and `Palestine viewpoint` until their geometry owners are pinned. Store state in `boundaryView=` without mutating country identity.

- [ ] **Step 7: Re-run UI validator**

Run: `python scripts/validate_world_map_ui_shell.py`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add world-map/index.html world-map/3d-spatial-overlay-ui.js world-map/3d-bootstrap.js scripts/validate_world_map_ui_shell.py
git commit -m "feat(world-map): add sacred geography overlay controls"
```

### Task 4: Correct Palestine selection and disconnected component handling

**Files:**
- Modify: `world-map/3d-app.js`
- Modify: `world-map/3d-geometry-aliases.js`
- Modify: `data/world-map-spatial-overlays.json`
- Modify/Create: `data/world-map-spatial/palestine-current.geojson`
- Create: `scripts/validate_world_map_palestine.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: canonical country code `PSE`, repository-owned West Bank + Gaza geometry, existing country selection bridge.
- Produces: search/click/focus behavior in which both components resolve to one `PSE` entity while component metadata remains inspectable.

- [ ] **Step 1: Write failing Palestine validator**

The validator requires the current Palestine owner to contain at least two disconnected named components (`West Bank`, `Gaza Strip`) whose canonical entity is `PSE`, and requires runtime source markers showing that `PSE` geometry can be replaced/augmented by repository-owned geometry.

- [ ] **Step 2: Run validator and confirm failure**

Run: `python scripts/validate_world_map_palestine.py`

Expected: FAIL because the legacy remote world source still supplies a one-component `PSE` polygon.

- [ ] **Step 3: Pin a source-attributed Palestine geometry owner**

Store West Bank + Gaza as one repository-controlled FeatureCollection/MultiPolygon contract with source/version/viewpoint metadata. Do not silently call it a universally neutral legal boundary; expose the active cartographic contract.

- [ ] **Step 4: Patch country geometry after legacy load**

Until the full global Natural Earth build replaces `johan/world.geo.json`, replace the legacy `PSE` feature at runtime from the pinned repository geometry. Preserve `PSE` country statistics/card identity and component names in feature metadata.

- [ ] **Step 5: Make geometry bounds handle all components**

`fitCodes(['PSE'])` must encompass both West Bank and Gaza. Clicking either component resolves to `PSE`; overlay inspection still reports which component was clicked.

- [ ] **Step 6: Re-run validators**

Run:

```bash
python scripts/validate_world_map_palestine.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_ui_shell.py
```

Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-app.js world-map/3d-geometry-aliases.js data/world-map-spatial-overlays.json data/world-map-spatial/palestine-current.geojson scripts/validate_world_map_palestine.py .github/workflows/quality-checks.yml
git commit -m "fix(world-map): represent Palestine as West Bank and Gaza"
```

### Task 5: Measurement metadata and safe conflict-context scaffold

**Files:**
- Create: `scripts/build_world_map_spatial_measurements.py`
- Create: `data/world-map-spatial-measurements.json`
- Modify: `data/world-map-spatial-overlays.json`
- Modify: `world-map/3d-spatial-overlay-ui.js`
- Modify: `scripts/validate_world_map_spatial_overlays.py`

**Interfaces:**
- Consumes: measurable WGS84 polygon/line features.
- Produces: feature-id/version keyed derived measurements and conflict-context availability/status metadata.

- [ ] **Step 1: Add validator expectations for measurements**

For every `measurable: true` current overlay feature, require a derived record keyed by `feature_id` + `geometry_version` containing bounding box, component count and either polygon area/perimeter or line length.

- [ ] **Step 2: Run validator and confirm failure**

Run: `python scripts/validate_world_map_spatial_overlays.py`

Expected: FAIL because measurement output is absent.

- [ ] **Step 3: Implement reproducible measurement build**

Use standard-library haversine/spherical calculations if `pyproj` is unavailable in CI; record the method explicitly. The build must never present approximate reconstructed polygons as scripture-supplied exact measurements.

- [ ] **Step 4: Generate and display measurements**

Inspector wording distinguishes `geometry-derived`, `approximate reconstruction`, and `source-reported` values.

- [ ] **Step 5: Add conflict-context scaffold without tactical tracking**

`conflict.context` remains unavailable until a dated/licensed adapter is added, but its manifest/UI contract lists allowed event/humanitarian categories and explicitly forbids live individual unit/vehicle tracking.

- [ ] **Step 6: Re-run validator**

Run: `python scripts/validate_world_map_spatial_overlays.py`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/build_world_map_spatial_measurements.py data/world-map-spatial-measurements.json data/world-map-spatial-overlays.json world-map/3d-spatial-overlay-ui.js scripts/validate_world_map_spatial_overlays.py
git commit -m "feat(world-map): add spatial measurements and conflict scaffold"
```

### Task 6: Full regression verification, PR and merge to main

**Files:**
- Modify only if validation exposes regressions.

**Interfaces:**
- Consumes: all tasks above.
- Produces: reviewed, CI-green merge into `main`.

- [ ] **Step 1: Run the targeted validator suite**

```bash
python scripts/validate_world_map_spatial_overlays.py
python scripts/validate_world_map_palestine.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_ui_shell.py
```

- [ ] **Step 2: Run repository quality checks available in GitHub Actions**

Confirm no existing World Map, schema or Pages validator regresses.

- [ ] **Step 3: Inspect final diff for epistemic collisions**

Verify that no sacred/textual/ideological feature uses current-sovereignty styling or wording; verify overlapping overlays remain independently queryable.

- [ ] **Step 4: Open PR against `main`**

PR body summarizes the working slice, current limitations, source/version provenance, safety boundary for conflict context, and the follow-up global Natural Earth build.

- [ ] **Step 5: Merge only after green checks**

Use squash or repository-standard merge method, then verify the resulting `main` SHA and Pages workflow status.
