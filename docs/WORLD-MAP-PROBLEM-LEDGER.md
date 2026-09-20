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
**Status:** fixed for direct Style Lifecycle ownership on main (2026-09-20).  
**Evidence:** only `3d-style-lifecycle.js` owns the MapLibre `styledata` listener; Render Stack and physical restorers register as participants.  
**Remaining visual-channel conflicts:** tracked separately under WM-006/WM-008 rather than reopening style lifecycle ownership.

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
**Status:** fixed for known user-visible camera consumers on main (2026-09-20).  
**Resolution:** shared Motion policy owns major country/place/subdivision/ADL/Axis transitions plus capital focus and Spatial Overlay fit; reduced-motion CSS and regression coverage exist.  
**Guard:** validator rejects raw `map.easeTo(` / `map.fitBounds(` calls in governed camera consumers outside the Motion owner.

### WM-012 · Color-only semantics remain possible — P2
**Status:** open.  
**Risk:** analytical/evidence differences may rely too heavily on hue.  
**Next:** add textual/shape/pattern redundancy and accessibility checks.

### WM-013 · Active-view accessibility summary incomplete — P2
**Status:** partially fixed.  
**Completed:** Context Status is a polite live region and reports selected/preview country, population, active analytical answer, investigation mode, scale band, pins and time.  
**Remaining:** explicitly summarize active Physical / Geography / Evidence layer identities and verify announcement noise/ordering.

### WM-014 · Route-geometry behavioral coverage incomplete — P2
**Status:** open.  
**Scope:** physical routes vs relationship chords vs symbolic routes; globe/dateline behavior; selection/hover priority.

### WM-015 · Legacy interaction fallback scenarios under-tested — P2
**Status:** partially fixed (2026-09-20).  
**Completed:** late-Router promotion now converges Gateways, Infrastructure, Places and Subdivisions from removable direct fallbacks into canonical Router ownership; validators require dynamic Router lookup, explicit unbind and `potato-atlas-interaction-ready` promotion.  
**Remaining matrix:** no Inspector, delayed optional modules, Router replacement/reload, and style reload during active interaction.

### WM-016 · State/subdivision national-context readability — P2
**Status:** partially fixed.  
**Current:** borders can appear earlier without early hit targets; labels still use canonical label threshold.  
**Next:** validate Alaska/Hawaii/DC, globe mode, dense Northeast labels and low-width screens.

### WM-017 · Evidence-layer source refresh contract should be generic — P2
**Status:** fixed on main (2026-09-20).  
**Cause:** ADL owned direct subdivision custom-event and MapLibre sourcedata listeners.  
**Resolution:** the subdivision runtime now owns one source-refresh observer contract; ADL registers through it, and future evidence fills can reuse the same lifecycle hook without owning geography refresh listeners.

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


### WM-021 · URL state ownership is fragmented — P1
**Status:** open.  
**Evidence:** more than twenty World Map runtime modules directly call `history.replaceState`.  
**Risk:** unrelated modules can preserve/delete each other's parameters; reset/hydration compatibility rules are distributed; URL races become load-order dependent.  
**Owner target:** one URL State service / transaction owner.  
**Solution:** namespaced parameter ownership, atomic patch API, hydration registration, diagnostics, and a validator forbidding direct URL mutation outside the owner plus explicitly bounded compatibility bridges.

### WM-022 · Specialist inspectors bypass typed Inspector Router — P1
**Status:** open.  
**Evidence:** ADL, Axis, Axis Depth, Mud/Below and Spatial Overlay UI write `panel.innerHTML` directly; Places and Subdivisions already use typed Inspector nodes.  
**Risk:** visible panel, `inspect=` URL path, parent/back history and focus semantics can disagree.  
**Owner target:** Inspector Router.  
**Solution:** migrate each specialist surface to typed inspector nodes; raw panel writes occur only inside the active node's render callback.

### WM-023 · Degraded interaction fallback can become permanent by boot order — P1
**Status:** fixed on main (2026-09-20).  
**Cause:** Spatial Overlays and Country Selection captured the Router once and could leave direct listeners installed forever.  
**Resolution:** both resolve Router ownership dynamically, listen for `potato-atlas-interaction-ready`, remove degraded listeners with `map.off`, and promote to canonical Router registrations.  
**Guard:** interaction validator/regression requires the ready listener and teardown markers.

### WM-024 · Canonical subdivision evidence integration lacks generic search/badge projection — P2
**Status:** open.  
**Completed:** subdivisions now expose generic evidence-provider and source-refresh observer contracts; ADL is the first provider.  
**Gap:** search/results and subdivision lists do not expose provider availability/count context, so evidence is discoverable mainly after selection.  
**Solution:** generic provider badges/summaries in subdivision search/inspector surfaces without hard-coding ADL.

### WM-025 · ADL state evidence is structurally integrated but snapshot freshness is historical — P2
**Status:** open data-quality task.  
**Current:** 335-record historical `Extremist murders` seed, 2005–2023; source/methodology boundary is explicit and official CSV importer exists.  
**Risk:** polished interaction can be mistaken for current monthly ADL coverage.  
**Solution:** persistent stale/snapshot-age indicator, reviewed official CSV replacement when available, and keep ADL/FBI methodologies separate.

## Work order

1. **State/control ownership wave** — WM-021/022/023.
2. **Scale ownership wave** — WM-003/004/005.
3. **Render/visual ownership wave** — WM-006/008/014.
4. **Accessibility/mobile/motion wave** — WM-010/011/012/013/016.
5. **Physical provider reliability wave** — WM-018/019.
6. **Evidence/subdivision projection wave** — WM-024/025.
7. **Compatibility + audit retirement** — WM-009/015/020 and remaining legacy surfaces.

## Completion rule

A problem is not complete because code changed. Close it only when:
- canonical ownership is explicit;
- regression/validator coverage exists;
- exact-head CI proves the relevant subsystem;
- any compatibility behavior is documented;
- the live roadmap and this ledger agree.
