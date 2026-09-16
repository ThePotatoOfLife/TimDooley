# World Map Roadmap

**Updated:** 2026-09-16  
**Authority:** current live roadmap for the World Map / World Relational Atlas. Older `docs/superpowers/specs/` and `docs/superpowers/plans/` remain design history unless explicitly referenced here.

## Vision

The World Map should become a stable relational instrument rather than a growing collection of overlays. It should make geography, relationships, time, evidence, capability, infrastructure and project context understandable without confusing unlike kinds of claim.

The quality target is not maximum visible density. It is maximum useful structure with explicit ownership, provenance, scale, interaction and mathematical meaning.

## Governing architecture

See `docs/superpowers/specs/2026-09-16-world-map-control-plane-design.md` and `docs/superpowers/specs/2026-09-16-world-map-consolidation-design.md`.

The active direction is:

`canonical data → active view → geospatial/scale/render/interaction/inspector control plane → MapLibre presentation`

The reconstruction rule is:

**Salvage behavior, contracts, data and verified fixes — not stale branch history.**

## DONE / FOUNDATION

These capabilities are established enough to build on:

- one primary World Map public surface;
- canonical country geometry and country records;
- persistent country selection / active country;
- layer registry and compositor foundation;
- render-stack ordering;
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
- browse/performance regressions for known hover, panel, cache and overlap failures;
- shared geospatial kernel with normalized longitude/wrapped identity and antimeridian-safe bounds;
- shared scale runtime with named thresholds and hysteresis, used by Places and subdivisions;
- central Interaction Router with semantic click/hover priority;
- router ownership for Places, subdivisions and spatial overlays;
- typed Inspector Router and canonical inspector URL path with deterministic child/back semantics;
- shared Style Lifecycle for Render Stack and physical layer restoration;
- event-driven runtime telemetry for map/style/interaction/tooltip state;
- integrated behavioral regression spanning wrapped geometry, overlap arbitration, tooltip invalidation and inspector URL/back state.

## ACTIVE — CONTROL-PLANE HARDENING

### A. Spatial safety

- [x] Add shared geospatial kernel.
- [x] Normalize longitudes and wrapped world-copy identity.
- [x] Make bounds/fit calculations antimeridian-aware.
- [ ] Replace degree-squared partition prioritization where physical/geographic distance is intended.
- [ ] Define schematic-vs-physical route geometry semantics.
- [x] Add dateline/globe/Mercator regressions for the shared kernel.

### B. Scale safety

- [x] Add canonical named scale bands / shared thresholds.
- [x] Separate load/render/label/interaction thresholds for migrated consumers.
- [x] Add hysteresis for boundary crossings where churn is possible.
- [x] Migrate Places/subdivision thresholds first.
- [ ] Audit every remaining module for raw zoom magic numbers.

### C. Interaction safety

- [x] Add central interaction registry/router.
- [x] Define hover/click semantic priority independent of render z-order.
- [x] Migrate Places, subdivisions and spatial overlays.
- [ ] Migrate the remaining core country/capital paths (`3d-app.js`, `3d-hover.js`, `3d-country-selection.js`) without weakening core-first boot.
- [ ] Retire `__potatoAtlasOverlayHandled` only after those remaining early-boot consumers have a tested canonical owner.

Current compatibility rule: the marker is still live protection against duplicate early-boot country/capital clicks. Router-owned consumers may retain it only inside degraded fallback paths until the core path is migrated.

### D. Tooltip safety

- [x] Add one transient-tooltip service.
- [x] Centralize stale async suppression and motion/projection/style invalidation in the shared service.
- [ ] Migrate every remaining country hover, Axis, Fields, Networks and infrastructure tooltip path.
- [ ] Remove the boot-guard CSS workaround only after behavioral regressions prove equivalent behavior.

### E. Inspector/state safety

- [x] Add typed inspector router/history.
- [x] Replace raw `panel.innerHTML` snapshots in Places and subdivisions.
- [x] Make child → parent → back semantics deterministic.
- [x] Align URL restoration with typed inspector state.

## NEXT — RENDER + UI CONVERGENCE

- [ ] Add visual-channel compatibility matrix.
- [ ] Audit every writer of country fill/pattern/outline/height.
- [x] Centralize style-generation restoration for Render Stack and migrated physical layers.
- [ ] Drain remaining duplicate style/lifecycle writers discovered by the architecture auditor.
- [ ] Consolidate global UI design tokens, z-index bands and common surfaces.
- [ ] Make top-level controls increasingly question-oriented: Browse / Compare / Connections / Evidence / Time / View.
- [ ] Audit mobile occlusion, keyboard access, focus return, color-only semantics and reduced motion.
- [ ] Add concise accessible active-view summaries.

## NEXT — VERIFICATION + OBSERVABILITY

- [x] Add real behavioral scenario tests for drag/projection/wrap/overlap/inspector transitions.
- [x] Track active source/layer counts and style restoration work.
- [x] Track interaction registry size, dispatch counts and tooltip generation/stale suppression.
- [x] Retain bounded Places/subdivision cache diagnostics.
- [x] Publish and enforce the World Map architecture audit in CI.
- [ ] Expand scenarios toward route geometry, remaining legacy interaction consumers and accessibility behavior.

## COMPATIBILITY RETIREMENT

Drain only after unique behavior is preserved and tested:

- [ ] `world-map/3d-ui.js`
- [ ] `world-map/3d-selection-ui.js`
- [ ] old Lens ownership after registry/compositor parity
- [ ] old Atlas naming/routing remnants
- [ ] remaining duplicated style/lifecycle ownership not yet under Style Lifecycle
- [ ] `__potatoAtlasOverlayHandled` after core country/capital interaction migration
- [ ] stale generated/retired map artifacts already represented by canonical owners

See `docs/world-map-consolidation-dispositions.md` for the branch-by-branch reconstruction record and compatibility classification.

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
