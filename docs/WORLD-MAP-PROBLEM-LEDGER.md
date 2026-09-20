# World Map Problem Ledger

**Updated:** 2026-09-20  
**Authority:** active defect / architecture queue for the World Map.  
**Rule:** fix the highest-leverage shared owner first; do not patch the same symptom independently in multiple modules.

## Severity model

- **P0** — map unusable / corrupt state / serious data or interaction failure.
- **P1** — visible feature disappears, wrong layer wins, state/lifecycle race, broken navigation, repeated requests.
- **P2** — architectural duplication likely to create future regressions, accessibility failure, mobile occlusion, inconsistent semantics.
- **P3** — polish, wording, cleanup, compatibility retirement after parity is proven.

## Active queue

### WM-001 · Shared subdivision retention can be released by the wrong overlay — P1
**Status:** fixed on main (2026-09-20).  
**Cause:** U.S. subdivision retention used one Set instead of owner-aware leases.  
**Resolution:** owner-aware retain/release; ADL and project overlays cannot evict each other.

### WM-002 · ADL feature-state can disappear after subdivision source refresh — P1
**Status:** fixed on main (2026-09-20).  
**Cause:** shared GeoJSON source replacement invalidated rendered feature-state timing.  
**Resolution:** source-change lifecycle + ADL repaint; load de-duplication; regression coverage.

### WM-003 · Physical Water owns a private 3.4 detail threshold — P2
**Status:** in progress in this wave.  
**Risk:** drift from canonical scale semantics; duplicated lifecycle thresholds.  
**Owner:** Scale runtime.  
**Resolution:** move threshold to `world-map-scale-contract.json`; Water consumes `physical-water-detail`.

### WM-004 · Hydrology owns private 4 / 5.2 / 6.7 / 8.2 thresholds — P2
**Status:** in progress in this wave.  
**Risk:** request density, cache identity and render activation can diverge.  
**Owner:** Scale runtime + Hydrology.  
**Resolution:** canonical capabilities + one `riverRegime()` owner shared by query threshold and request-key regime.

### WM-005 · Remaining raw zoom-magic inventory — P2
**Status:** open.  
**Known candidates:** core HUD mode bands, capitals label thresholds, Axis camera thresholds, specialist layers.  
**Rule:** distinguish capability thresholds from camera-preservation math before migrating.  
**Next:** inventory every raw threshold and classify: capability / cartographic interpolation / camera intent / test fixture.

### WM-006 · Country visual-channel ownership not fully closed — P1/P2
**Status:** partially fixed (2026-09-20).  
**Risk:** country fill/pattern/outline/height writers can override each other or restore in the wrong order.  
**Owner:** compositor + country selection + Physical World + core extrusion controller.  
**Completed:** explicit owner map added; Progressive UI no longer writes canonical country fill/extrusion/outline paint.  
**Next:** migrate or retire the dormant legacy Lens repaint path, then audit remaining variable/dynamic paint writers.

### WM-007 · Duplicate style/lifecycle writers remain — P2
**Status:** open.  
**Risk:** style reloads can recreate layers in conflicting order.  
**Owner:** Style Lifecycle.  
**Next:** drain auditor findings and forbid new global style writers outside approved owners.

### WM-008 · Legacy UI ownership remains split — P2
**Status:** open.  
**Candidates:** `3d-ui.js`, `3d-selection-ui.js`, old Lens ownership.  
**Risk:** duplicate controls/state synchronization and hidden compatibility behavior.  
**Next:** prove parity against World Bar / selection / compositor, then retire one surface at a time.

### WM-009 · Interaction compatibility marker still exists — P3 until degraded paths retire
**Status:** bounded compatibility debt.  
**Owner:** Interaction Router.  
**Next:** remove only after direct/degraded standalone paths have canonical Router boot and tests.

### WM-010 · Mobile occlusion / keyboard / focus-return audit incomplete — P2
**Status:** open.  
**Risks:** controls can overlap, menus can lose focus, inspector transitions can strand keyboard users.  
**Next:** add keyboard navigation, focus return, small-viewport occlusion and modal/menu regressions.

### WM-011 · Reduced-motion behavior incomplete — P2
**Status:** fixed (2026-09-20).  
**Risk addressed:** camera `easeTo` / `fitBounds` transitions previously ignored user motion preferences.  
**Resolution:** shared `3d-motion.js` policy now removes animation under `prefers-reduced-motion: reduce`; core, Places, subdivisions, ADL/Mud focus, Axis navigation and symbolic operators consume it; decorative shell transitions are also suppressed; canonical runtime validation includes a behavioral regression.

### WM-012 · Color-only semantics remain possible — P2
**Status:** open.  
**Risk:** analytical/evidence differences may rely too heavily on hue.  
**Next:** add textual/shape/pattern redundancy and accessibility checks.

### WM-013 · Active-view accessibility summary incomplete — P2
**Status:** open.  
**Next:** concise live region describing active analytical/physical/evidence/geography layers, selection, scale and time.

### WM-014 · Route-geometry behavioral coverage incomplete — P2
**Status:** open.  
**Scope:** physical routes vs relationship chords vs symbolic routes; globe/dateline behavior; selection/hover priority.

### WM-015 · Legacy interaction fallback scenarios under-tested — P2
**Status:** open.  
**Next:** explicit degraded-boot test matrix: no Router, no Inspector, delayed optional modules, style reload during interaction.

### WM-016 · State/subdivision national-context readability — P2
**Status:** partially fixed.  
**Current:** borders can appear earlier without early hit targets; labels still use canonical label threshold.  
**Next:** validate Alaska/Hawaii/DC, globe mode, dense Northeast labels and low-width screens.

### WM-017 · Evidence-layer source refresh contract should be generic — P2
**Status:** open.  
**Observation:** ADL now listens to subdivision-source lifecycle directly.  
**Next:** consider a generic source-refresh hook/adapter contract so future evidence fills do not reinvent repaint logic.

### WM-018 · Provider-failure UX is inconsistent across Physical layers — P2
**Status:** open.  
**Next:** common status/error/degraded-state contract for Terrain, Water, Hydrology, Land Cover and Aridity.

### WM-019 · Physical layer request budgeting lacks one shared network budget — P2
**Status:** open.  
**Risk:** multiple physical providers can be enabled together and independently issue expensive requests.  
**Next:** global bounded request/concurrency budget and telemetry.

### WM-020 · Architecture audit should emit actionable queue IDs — P3
**Status:** open.  
**Next:** map recurring audit findings to this ledger and include remediation owner + severity.

### WM-021 · Path route geometry disclosure drift — P2
**Status:** fixed (2026-09-20).  
**Cause:** Path described shortest represented graph paths but did not explicitly say rendered graph lines are not surveyed physical routes.  
**Resolution:** canonical Path disclosure now states that map lines are schematic relationship chords, not surveyed transport, cable, pipeline, border, or physical route geometry; the route-semantics regression pins the wording.

### WM-022 · Gateway has duplicate / bypassed click ownership — P1/P2
**Status:** in progress.  
**Cause:** System Gateway points bind a direct MapLibre click after the Interaction Router is available, while Impact Actions adds another direct click on the same layer.  
**Risk:** one pointer action can trigger multiple semantic owners and bypass overlap priority.  
**Next:** one Router-owned Gateway click; Impact reacts to the semantic gateway-change event.

### WM-023 · Infrastructure points bypass semantic interaction priority — P2
**Status:** in progress.  
**Cause:** Infrastructure binds direct hover/click listeners during normal app boots.  
**Risk:** overlap with Places/subdivisions/other contextual points depends on listener/render order instead of semantic priority.  
**Next:** register Infrastructure with the Interaction Router and retain direct handlers only as a degraded standalone fallback.

### WM-024 · Architecture auditor style-restorer contract is stale — P2
**Status:** open.  
**Observed:** audit reports the central `3d-style-lifecycle.js` as unapproved while flagging Render Stack and four physical modules as stale restorers.  
**Cause:** audit contract still describes pre-centralization `styledata` ownership.  
**Next:** move approved ownership to the central Style Lifecycle and classify registered restore participants separately from direct `styledata` listeners.

### WM-025 · Shared singleton APIs still look like multiple assigners — P2
**Status:** open.  
**Observed:** `__potatoAtlasGeo`, `__potatoAtlasStyleLifecycle`, and `__potatoAtlasTooltip` trigger multi-assigner warnings.  
**Next:** distinguish guarded get-or-create singleton publication from competing mutation; converge any genuine duplicate assignment.

### WM-026 · Evidence-layer URL state has multiple writers — P2
**Status:** open.  
**Observed:** architecture audit reports multiple writers for `url:evidenceLayer`.  
**Next:** identify canonical URL-state owner and convert other writers to request/event APIs or document intentional shared ownership with one normalization path.

## Work order

1. **Scale ownership wave** — WM-003/004/005.
2. **Render ownership wave** — WM-006/007/017.
3. **Interaction/degraded runtime wave** — WM-009/014/015.
4. **Accessibility/mobile/motion wave** — WM-010/011/012/013/016.
5. **Physical provider reliability wave** — WM-018/019.
6. **Compatibility retirement** — WM-008/020 and remaining legacy surfaces.

## Completion rule

A problem is not complete because code changed. Close it only when:
- canonical ownership is explicit;
- regression/validator coverage exists;
- exact-head CI proves the relevant subsystem;
- any compatibility behavior is documented;
- the live roadmap and this ledger agree.
