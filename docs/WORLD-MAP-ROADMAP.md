# World Map Roadmap

**Updated:** 2026-09-21  
**Authority:** current live roadmap for the World Map / World Relational Atlas. The active defect queue is `docs/WORLD-MAP-PROBLEM-LEDGER.md`. Older `docs/superpowers/specs/` and `docs/superpowers/plans/` remain design history unless explicitly referenced here.

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
- integrated behavioral regression spanning wrapped geometry, overlap arbitration, tooltip invalidation and inspector URL/back state;
- core country/compare fits and viewport-bounded hydrology both handle antimeridian crossings.

## ACTIVE — CONTROL-PLANE HARDENING

### A. Spatial safety

- [x] Add shared geospatial kernel.
- [x] Normalize longitudes and wrapped world-copy identity.
- [x] Make bounds/fit calculations antimeridian-aware.
- [x] Replace degree-squared partition prioritization where physical/geographic distance is intended.
- [x] Define schematic-vs-physical route geometry semantics.
- [x] Add dateline/globe/Mercator regressions for the shared kernel.

### B. Scale safety

- [x] Add canonical named scale bands / shared thresholds.
- [x] Separate load/render/label/interaction thresholds for migrated consumers.
- [x] Add hysteresis for boundary crossings where churn is possible.
- [x] Migrate Places/subdivision thresholds first.
- [x] Move Physical Water detail and Hydrology request-density thresholds into the shared Scale contract.
- [~] Audit every remaining module for raw zoom magic numbers; classify capability thresholds separately from camera-preservation and cartographic interpolation.

### C. Interaction safety

- [x] Add central interaction registry/router.
- [x] Define hover/click semantic priority independent of render z-order.
- [x] Migrate Places, subdivisions and spatial overlays.
- [x] Migrate the core country/capital paths (`3d-app.js`, `3d-hover.js`, `3d-country-selection.js`) without weakening core-first boot.
- [x] Narrow `__potatoAtlasOverlayHandled` to a tested early-boot/degraded compatibility boundary.
- [ ] Retire the marker entirely only if/when direct standalone/degraded interaction boot paths are removed.

Current compatibility rule: normal application interaction is Router-owned and does not use the marker for arbitration. During the core handoff, captured legacy listeners receive a routed event without the real `originalEvent`, so they cannot re-claim an already-arbitrated click. The marker remains only as protection for the genuine pre-Router core window and explicitly documented degraded/direct-module fallbacks. `scripts/test_world_map_interaction_compatibility.mjs` is the single contract for that boundary.

### D. Tooltip safety

- [x] Add one transient-tooltip service.
- [x] Centralize stale async suppression and motion/projection/style invalidation in the shared service.
- [x] Migrate all transient country/capital/Axis/Fields/Networks hover paths to the shared Tooltip Service; persistent Gateway/Infrastructure click popups remain intentionally separate.
- [x] Remove the boot-guard CSS/pointer-drag workaround after shared Tooltip Service behavioral regressions proved equivalent motion invalidation.

### E. Inspector/state safety

- [x] Add typed inspector router/history.
- [x] Replace raw `panel.innerHTML` snapshots in Places and subdivisions.
- [x] Make child → parent → back semantics deterministic.
- [x] Align URL restoration with typed inspector state.

## CURRENT PROBLEM QUEUE

The numbered working queue lives in `docs/WORLD-MAP-PROBLEM-LEDGER.md`. The current diagnosis is `docs/WORLD-MAP-QUALITY-AUDIT-2026-09-21.md`. Work proceeds by shared-owner leverage rather than file count.

### 2026-09-21 re-audit priorities

- [x] Retire dormant `3d-fields.js` / `3d-networks.js`: live symbolic operators now use Layer Registry state; obsolete render/control modules are deleted while underlying datasets remain available for future registry expansion.
- [~] Expand subdivision + bounded Places depth beyond the current five promoted countries. Germany now has a reviewed official BKG ADM1 acquisition contract; geometry + bounded DEU Places promotion remain.
- [ ] Replace the GeoNames mirror seed with a reviewed fresh canonical build; preserve source date, build date and upstream freshness separately.
- [ ] Promote at least one reviewed delayed/historical conflict snapshot with source bundle, date semantics and explicit not-live boundary before exposing Conflict as current functionality.
- [~] Add behavioral viewport scenarios for globe mode, narrow screens, dense regional labels, detached geography and region→Places handoff. A combined narrow+globe+region+Places contract regression is now in progress; browser-level occlusion/detached-geography proof remains.
- [x] Map architecture-auditor finding codes to ledger IDs, owner and severity; actionable unmapped findings now fail the architecture audit.
- [~] Add regional-statistics enrichment as an optional sourced layer. The ID-joined runtime preserves geometry provenance and a fail-closed reviewed-export importer is in place; Denmark's verified StatBank codes/exports and first real sidecar still need promotion.
- [ ] Continue design-token convergence beyond z-index into shared surface/background/border/radius/spacing tokens without flattening semantic distinctions.
- [~] Add a common freshness/status vocabulary for data-backed layers. Evidence/ADL and Places now consume shared explicit-only freshness semantics; extend them to other empirical reader surfaces.


## NEXT — RENDER + UI CONVERGENCE

- [ ] Re-audit top-bar density after future control additions; any new persistent control must justify itself as a frequent direct action, distinct map dimension, or global navigation/reset function.

- [x] Reduce top-bar density without redesigning the map: consolidate relation-context filters into Analyze, group N/W/E/S as compact axis lenses, shrink icon controls and tighten fixed Search/Compare/Inspect spacing.

- [x] Add a complete symmetric visual-channel compatibility matrix, with explicit composition/separation semantics and governed conditional fallback for pattern + height.
- [x] Audit every writer of country fill/pattern/outline/height. Persistent planes are explicit; specialist renderers register with the shared Render Stack; dormant Fields/Networks compatibility writers are retired.
- [x] Centralize style-generation restoration for Render Stack and migrated physical layers.
- [x] Drain direct duplicate Style Lifecycle ownership; remaining visual-channel compatibility debt is tracked independently rather than as duplicate `styledata` ownership.
- [~] Consolidate global UI design tokens, z-index bands and common surfaces. Semantic stacking bands are being reconstructed on current main; shared surface/background/border/radius/spacing tokens remain.
- [~] Make top-level controls increasingly question-oriented: the visible World Bar now converges Analytical / Physical / Geography / Evidence with Compare / Analyze / Time / View; further wording simplification can continue without adding another control surface.
- [x] Audit current shared surfaces for mobile occlusion, keyboard access, focus return, color-only semantics and reduced motion; keep the audit requirement on every newly promoted surface.
- [x] Add concise accessible active-view summaries through the World Bar context/status owner, with duplicate-announcement suppression.

## ACTIVE — PROJECTION TRANSPARENCY

- [x] Bind live analytical views to the shared Atlas projection contract through `data/world-map-view-projections.json`.
- [x] Disclose compact information-loss semantics in Current Map context for scalar, set, relation and comparison views.
- [x] Expose source-linked reconstructability state from Active View rather than implying aggregate views are canonical records.
- [x] Gate the contract, runtime markers and reader disclosure in the World Map quality group.
- [ ] Extend the same projection-loss/reconstructability discipline to future derived network/system aggregates as they become reader-facing.

## ACTIVE — REGIONAL DEPTH

- [x] Keep subdivisions behind one generic country-indexed partition engine and one bounded source/layer set.
- [x] Add Ukraine as a geometry-first first-order administrative partition with explicit source-representation caveats.
- [x] Add Russia through the same partition contract as an 83-feature base partition; strip unrelated source attributes and exclude six disputed Ukrainian source features from ordinary Russia geography.
- [x] Normalize future ADM1 sources through one fail-closed importer that emits canonical partitions + descriptor sidecars without mutating the live registry.
- [~] Add further country partitions only after provenance, byte budget, search records and national-context readability pass the same validator. Pre-promotion source contracts now formalize these requirements; Germany is the first next-wave candidate.
- [x] Require every promoted regional country to carry a bounded Places partition; Ukraine and Russia now have same-origin GeoNames place coverage plus global-major/search projection.
- [x] Make the generic subdivision inspector expose unknown-vs-known statistics, local names, boundary provenance/vintage and source-specific representation notes.
- [x] Make the country-card Regions doorway focus the retained partition into visible/interactable regional scale using subdivision-owned camera policy.
- [x] Make the Regions doorway a real on/off control with lease-backed active state and explicit state-change events.
- [x] Add shared transient hover previews for selectable regions, including local names and region type.
- [x] Let region inspectors hand off directly to the canonical Places renderer so mapped cities/towns can be revealed without a duplicate city layer.
- [x] Promote local subdivision names into close-zoom bilingual/local-name map labels without increasing early-scale density.
- [x] Define a separate dated conflict-snapshot contract for control/contested/historical-front/humanitarian/event-aggregate geometry.
- [ ] Promote conflict snapshots only after reviewed geometry + source bundles exist; never rewrite administrative partitions into live war geometry.

## NEXT — VERIFICATION + OBSERVABILITY

- [x] Add real behavioral scenario tests for drag/projection/wrap/overlap/inspector transitions.
- [x] Track active source/layer counts and style restoration work.
- [x] Track interaction registry size, dispatch counts and tooltip generation/stale suppression.
- [x] Retain bounded Places/subdivision cache diagnostics.
- [x] Publish and enforce the World Map architecture audit in CI.
- [ ] Expand scenarios toward route geometry, remaining legacy interaction consumers and accessibility behavior.

## COMPATIBILITY RETIREMENT

Drain only after unique behavior is preserved and tested:

- [x] `world-map/3d-ui.js` — retired after canonical World Bar / Panel Lifecycle / presentation owners replaced its normal-boot responsibilities.
- [x] `world-map/3d-selection-ui.js` — retired after Country Selection / Layer Registry / Country Card replaced its compatibility surface.
- [x] old Lens ownership after registry/compositor parity — retired; canonical Layer Registry + Compositor own analytical state.
- [~] old Atlas naming/routing remnants — canonical renderer validation now targets `world-map/index.html` directly and the source wrapper no longer monkey-patches validator behavior; internal `atlas*` identifiers remain compatibility/naming debt.
- [ ] remaining duplicated style/lifecycle ownership not yet under Style Lifecycle
- [ ] `__potatoAtlasOverlayHandled` after direct standalone/degraded interaction fallbacks are retired
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
