# World Map Roadmap

**Updated:** 2026-09-16  
**Authority:** current live roadmap for the World Map / World Relational Atlas. Older `docs/superpowers/specs/` and `docs/superpowers/plans/` remain design history unless explicitly referenced here.

## Vision

The World Map should become a stable relational instrument rather than a growing collection of overlays. It should make geography, relationships, time, evidence, capability, infrastructure and project context understandable without confusing unlike kinds of claim.

The quality target is not maximum visible density. It is maximum useful structure with explicit ownership, provenance, scale, interaction and mathematical meaning.

## Governing architecture

See `docs/superpowers/specs/2026-09-16-world-map-control-plane-design.md`.

The active direction is:

`canonical data → active view → geospatial/scale/render/interaction/inspector control plane → MapLibre presentation`

## DONE / FOUNDATION

These capabilities are established enough to build on:

- one primary World Map public surface;
- canonical country geometry and country records;
- persistent country selection / active country;
- layer registry and compositor foundation;
- render-stack ordering;
- centralized style-generation restoration and generation diagnostics;
- active-view model;
- current/as-of/compare-date time foundation;
- evidence/Eye inspection;
- relationship Trace and Path foundations;
- scale-aware Places with bounded runtime budgets;
- lazy bounded subdivision rendering;
- physical-world layer system;
- independent epistemically typed spatial overlays;
- investigation-surface arbitration;
- panel lifecycle ownership;
- progressive/lazy specialist loading;
- mathematical calibration separating geography, topology, hierarchy, time and gated flow;
- viewport-safe UI padding so map camera state accounts for the desktop inspector;
- deterministic collision priority and adaptive placement for place labels;
- browse/performance regressions for known hover, panel, cache, overlap and occlusion failures.

## ACTIVE — CONTROL-PLANE HARDENING

### A. Spatial safety

- [x] Add shared geospatial kernel.
- [ ] Normalize longitudes and wrapped world-copy identity. *(longitude normalization is live; canonical world-copy identity remains to be completed)*
- [x] Make bounds/fit calculations antimeridian-aware for the migrated subdivision/geospatial paths.
- [x] Replace degree-squared subdivision partition prioritization where physical/geographic distance is intended.
- [ ] Define schematic-vs-physical route geometry semantics.
- [ ] Add complete dateline/globe/Mercator regressions. *(dateline regressions exist; projection coverage remains incomplete)*

### B. Scale safety

- [x] Add canonical named scale bands.
- [x] Separate load/render/label/interaction thresholds in the scale contract.
- [x] Add hysteresis for boundary crossings where churn is possible.
- [x] Finish migrating Places/subdivision load/render/label thresholds, including MapLibre layer `minzoom` ownership.
- [ ] Audit every remaining module for raw zoom magic numbers.

### C. Interaction safety

- [x] Add central interaction registry/router.
- [x] Define hover/click semantic priority independent of render z-order.
- [ ] Finish migrating active targets. *(Places 80, Gateways 75, Infrastructure 70, subdivisions 60 and spatial overlays 40 are centralized; country/Axis compatibility paths remain)*
- [ ] Retire `__potatoAtlasOverlayHandled` after all relevant targets migrate.

### D. Tooltip safety

- [x] Add one transient-tooltip service.
- [x] Centralize stale async suppression and drag/zoom/rotate/pitch/projection invalidation.
- [x] Migrate country/capital hover, Axis, Fields and Networks to the shared transient owner.
- [x] Remove the boot-guard pointer/CSS workaround after behavioral regressions prove equivalent behavior.

### E. Inspector/state safety

- [x] Add typed inspector router/history.
- [x] Replace raw `panel.innerHTML` snapshots in Places and subdivisions.
- [x] Make child → parent → back semantics deterministic.
- [ ] Align full URL restoration/hydration with typed inspector state.

## NEXT — RENDER + UI CONVERGENCE

- [ ] Add visual-channel compatibility matrix.
- [ ] Audit every writer of country fill/pattern/outline/height.
- [x] Centralize style-generation restoration. *(Style Lifecycle owns the single active `styledata` listener; physical restorers run before Render Stack reconciliation.)*
- [ ] Consolidate global UI design tokens, z-index bands and common surfaces. *(Inspector width and map-safe camera padding are centralized; broader token convergence remains.)*
- [x] Bound World Bar dropdown height/scroll ownership and keep map camera fits clear of the desktop inspector.
- [x] Add deterministic place-label collision priority, flexible anchors and scale-aware collision spacing.
- [ ] Make top-level controls increasingly question-oriented: Browse / Compare / Connections / Evidence / Time / View.
- [ ] Audit mobile occlusion, keyboard access, focus return, color-only semantics and reduced motion. *(mobile inspector/menu occlusion now has bounded layout rules; accessibility work remains)*
- [ ] Add concise accessible active-view summaries.

## NEXT — VERIFICATION + OBSERVABILITY

- [ ] Add real behavioral scenario tests for drag/zoom/projection/wrap/overlap/inspector transitions.
- [ ] Track active source/layer counts and style restoration work. *(Style Lifecycle generation/restore counters now exist; source/layer count telemetry remains.)*
- [ ] Track interaction registry size and tooltip generation/stale suppression.
- [x] Retain bounded Places/subdivision cache diagnostics.
- [ ] Publish useful backend/map audit artifacts in CI rather than creating disposable repository state.

## COMPATIBILITY RETIREMENT

Drain only after unique behavior is preserved and tested:

- [ ] `world-map/3d-ui.js`
- [ ] `world-map/3d-selection-ui.js`
- [ ] old Lens ownership after registry/compositor parity
- [ ] old Atlas naming/routing remnants
- [x] duplicated styledata/lifecycle ownership
- [ ] stale generated/retired map artifacts already represented by canonical owners

## DATA EXPANSION AFTER CONTROL-PLANE STABILITY

Use the same relationship-first method for:

1. economy and public finance;
2. trade/value chains;
3. energy/resources/interconnectors;
4. infrastructure and logistics;
5. companies, ownership and control;
6. technology, research and skills;
7. institutions, procurement and funding;
8. dependency, capability and resilience;
9. dated flows and transitions.

Every new data family must expose identity, geography where honest, ownership/control, function, relationships, date/period, source, confidence/status and missing-data semantics.

## RESEARCH READY / NOT DEFAULT EARTH GEOGRAPHY

These are valid future mathematical views once their input requirements exist:

- spectral layouts for dense non-geographic relationship graphs;
- hyperbolic hierarchy for Tree/Rooms-like structures;
- Hodge-style decomposition for directed quantitative flows with compatible quantities, units and reference periods;
- scenario/programme views only after observed-state, time and evidence separation is robust.

## PERMANENT GUARDRAILS

- Geography uses real coordinates.
- Zoom is camera scale, not ontology.
- Graph distance is represented relationship distance, not moral or geopolitical distance.
- Axis depth is analytical/project navigation, not physical altitude or extra-dimensional geography.
- Symbolic/project geography is explicitly typed and never silently becomes sovereignty or surveyed terrain.
- Missing data remains missing.
- Repetition is not corroboration.
- Visual overlap does not merge unlike claims.
- World copies may repeat visually; canonical entities do not.
- Compatibility code is removed only after unique behavior has a tested canonical owner.
