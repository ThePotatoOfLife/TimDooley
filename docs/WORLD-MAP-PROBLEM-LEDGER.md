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
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** `data/world-map-scale-contract.json` owns `physical-water-detail`; Water consumes the shared threshold and keeps only cartographic interpolation locally.  
**Guard:** scale-classification validation requires the shared capability marker and rejects return of the old private behavioral gate.

### WM-004 · Hydrology owns private 4 / 5.2 / 6.7 / 8.2 thresholds — P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** the Scale contract owns regional/medium/fine/detailed thresholds and Hydrology consumes them through one `riverRegime()` owner shared by provider filtering and request-key identity.  
**Guard:** scale-classification validation checks every shared hydrology capability marker.

### WM-005 · Remaining raw zoom-magic inventory — P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** behavioral gates live in `data/world-map-scale-contract.json`; `data/world-map-scale-classification.json` classifies remaining values as capability, cartographic interpolation, camera intent or fixture. The core HUD no longer owns private 3/5/7 bands and consumes `scale.bandForZoom()`.  
**Guard:** `scripts/validate_world_map_scale_classification.py` verifies the shared capability consumers and prevents the old HUD classifier from returning.  
**Rule retained:** visual interpolation and camera framing remain local unless they begin governing data/loading/interaction behavior.

### WM-006 · Country visual-channel ownership not fully closed — P1/P2
**Status:** fixed / governed on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** Compositor owns country fill/extrusion color, Country Selection owns outlines, Physical World owns country fill opacity, and the core extrusion controller owns height/visibility. Progressive UI is retired from normal boot. Legacy Lens URLs/API calls now translate into Layer Registry state only; the Lens compatibility adapter owns no country paint, feature-state, legend or control surface.  
**Guard:** visual-channel validation rejects canonical country paint writes from legacy UI/Lens compatibility modules and enforces one owner per channel. Lens ownership regression rejects return of the retired legend/control renderer.  
**Rule retained:** any newly promoted renderer that wants a canonical country channel must declare ownership instead of writing around the compositor.

### WM-007 · Duplicate style/lifecycle writers remain — P2
**Status:** fixed for direct Style Lifecycle ownership on main (2026-09-20).  
**Evidence:** only `3d-style-lifecycle.js` owns the MapLibre `styledata` listener; Render Stack and physical restorers register as participants.  
**Remaining visual-channel conflicts:** tracked separately under WM-006/WM-008 rather than reopening style lifecycle ownership.

### WM-008 · Legacy UI ownership remains split — P2
**Status:** fixed for normal boot on main (2026-09-20).  
**Resolution:** Progressive UI (`3d-ui.js`) and Selection UI (`3d-selection-ui.js`) are rejected from the live bootstrap; World Bar, Country Selection, Compositor, UI Layout and Panel Lifecycle own their former responsibilities. Legacy `3d-lenses.js` remains as source compatibility/reference code but is no longer registered as a live dormant bootstrap module.  
**Guard:** core/browse/inspector validators reject reintroduction of Progressive/Selection UI into normal boot; visual-channel validation prevents legacy UI paint ownership from returning.

### WM-009 · Interaction compatibility marker still exists — P3 until degraded paths retire
**Status:** bounded compatibility debt.  
**Owner:** Interaction Router.  
**Next:** remove only after direct/degraded standalone paths have canonical Router boot and tests.

### WM-010 · Mobile occlusion / keyboard / focus-return audit incomplete — P2
**Status:** fixed / governed for current shared surfaces on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** shared Accessibility owner synchronizes menu ARIA state, Escape closes the active menu and returns focus, opening a map menu closes any already-open sibling without stealing focus, and Inspector Router captures/restores focus across typed inspector transitions. On narrow screens, either World Bar or top-menu expansion suppresses background status, pinned context and inspector surfaces so they cannot compete for pointer/focus space.  
**Guard:** keyboard regression covers Escape/focus and single-open-menu behavior; UI-layout validation requires both mobile menu families in the occlusion policy.

### WM-011 · Reduced-motion behavior incomplete — P2
**Status:** fixed for known user-visible camera consumers on main (2026-09-20).  
**Resolution:** shared Motion policy owns major country/place/subdivision/ADL/Axis transitions plus capital focus and Spatial Overlay fit; reduced-motion CSS and regression coverage exist.  
**Guard:** validator rejects raw `map.easeTo(` / `map.fitBounds(` calls in governed camera consumers outside the Motion owner.

### WM-012 · Color-only semantics remain possible — P2
**Status:** fixed for canonical analytical country layers (2026-09-20).  
**Resolution:** scalar layers use color plus exact numeric/value text; set layers use pattern plus explicit membership text; layer controls expose type/state through accessible labels and the visual-channel validator enforces these redundancies.  
**Remaining:** apply the same review standard to future Evidence/Physical renderers before promotion.

### WM-013 · Active-view accessibility summary incomplete — P2
**Status:** fixed / superseded by current presentation architecture on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** the mixed hover/selection Context Status surface is intentionally retired from Panel Lifecycle. Global analytical state now lives in World Bar's `atlasWorldContext`, a polite atomic status region covering active analytical, Physical, Geography, Evidence, projection, relation and time context; selected-country detail belongs to Country Card/Presentation instead of the global status surface. Identical context markup is not rewritten, reducing repeated live-region announcements.  
**Guard:** context-status regression requires the old mixed surface to stay unloaded and verifies the accessible World Bar successor plus duplicate-announcement suppression.

### WM-014 · Route-geometry behavioral coverage incomplete — P2
**Status:** fixed for current route families / governed on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** relationship chords and symbolic interior routes use the shared wrap-safe longitude kernel; regressions cover dateline crossings in eastern and western world copies; route features carry explicit `geometry_meaning`; stored spatial-overlay lines remain stored/reference geometry rather than being silently converted into schematic chords. Shared Interaction Router tests cover click/hover priority.  
**Future rule:** any surveyed physical-route renderer must preserve source geometry and add its own behavioral test rather than reusing schematic chord semantics.

### WM-015 · Legacy interaction fallback scenarios under-tested — P2
**Status:** fixed / governed on main (2026-09-20), pending exact-head CI confirmation.  
**Resolution:** Country Selection, Spatial Overlays, Places and Subdivisions resolve Router ownership dynamically and promote from bounded fallbacks. Places, Subdivisions, ADL, Mud/Below, Spatial Overlay UI, Axis and Axis Depth resolve Inspector availability dynamically while retaining direct panel fallbacks. Places, Subdivisions and Spatial Overlays restore sources/layers/interaction ownership through the shared Style Lifecycle after style generations.  
**Guard:** dedicated degraded-Inspector regression rejects module-boot Inspector caching and verifies fallback + typed promotion; interaction and Style Lifecycle validators cover Router and style-generation recovery.

### WM-016 · State/subdivision national-context readability — P2
**Status:** substantially fixed.  
**Completed:** canonical USA partition is validator-checked at 50 states + DC including Alaska, Hawaii and DC; narrow-screen labels defer to reduce clutter; the selected subdivision gets a guaranteed overlap-tolerant label; resize behavior and bounded-runtime regressions are enforced.  
**Remaining:** continue visual review in globe mode and dense Northeast cases as style/scale behavior evolves.

### WM-017 · Evidence-layer source refresh contract should be generic — P2
**Status:** fixed on main (2026-09-20).  
**Cause:** ADL owned direct subdivision custom-event and MapLibre sourcedata listeners.  
**Resolution:** the subdivision runtime now owns one source-refresh observer contract; ADL registers through it, and future evidence fills can reuse the same lifecycle hook without owning geography refresh listeners.

### WM-018 · Provider-failure UX is inconsistent across Physical layers — P2
**Status:** fixed; see combined WM-018/019 reliability resolution below.

### WM-019 · Physical layer request budgeting lacks one shared network budget — P2
**Status:** fixed for explicit provider fetches; see combined WM-018/019 reliability resolution below.

### WM-020 · Architecture audit should emit actionable queue IDs — P3
**Status:** fixed on main (2026-09-20).  
**Resolution:** recurring architecture-audit finding codes now project to owning `WM-xxx` queue IDs plus remediation owner in both JSON reports and console output.  
**Guard:** `scripts/test_world_map_auditor.py` verifies queue projection for ownership collisions.


### WM-021 · URL state ownership is fragmented — P1
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** `3d-url-state.js` is the sole direct `history.replaceState` owner. Domain/specialist state and the formerly coupled selection/Inspector family now use shared parameter claims and atomic patches; Places, Subdivisions and map-reset fallbacks no longer bypass ownership.  
**Guard:** `validate_world_map_url_state.py` scans every live `world-map/*.js` file and rejects direct history writers outside the canonical owner; URL regression covers shared-owner overlapping claims.  
**Compatibility:** legacy `selected=` remains read-compatible but is cleared by the working-selection owner on writes.

### WM-022 · Specialist inspectors bypass typed Inspector Router — P1
**Status:** fixed for known main-panel specialist surfaces on main (2026-09-20).  
**Resolution:** Places, Subdivisions, ADL dataset/state/incident evidence, Mud/Below, Spatial Overlay inspection, Axis and Axis Depth all project through typed Inspector nodes. Raw panel HTML remains an implementation detail inside node render callbacks rather than owning semantic history.  
**Accessibility:** Inspector open/back already focuses rendered headings and restores the invoking control.  
**Guard:** Inspector URL and router validators cover the migrated node types and hierarchy.

### WM-023 · Degraded interaction fallback can become permanent by boot order — P1
**Status:** fixed on main (2026-09-20).  
**Cause:** Spatial Overlays, Country Selection, Places and Subdivisions could capture Router availability too early and leave direct listeners installed forever.  
**Resolution:** all four resolve Router ownership dynamically, listen for `potato-atlas-interaction-ready`, remove degraded listeners with `map.off`, and promote to canonical Router registrations.  
**Guard:** interaction validator/regression requires the ready listener and teardown markers.

### WM-024 · Canonical subdivision evidence integration lacks generic search/badge projection — P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** subdivision runtime exposes provider-agnostic `evidenceSummaries(id)`; inspector cards and unified subdivision search consume the generic summaries. Search displays active evidence count context without naming or depending on ADL.  
**Guard:** `validate_world_map_subdivision_evidence_projection.py` requires the generic provider/search bridge and explicitly rejects ADL hard-coding in unified search.

### WM-025 · ADL state evidence is structurally integrated but snapshot freshness is historical — P2
**Status:** UI/currentness boundary fixed; external data refresh remains open.  
**Current:** 335-record historical `Extremist murders` seed, 2005–2023; the Evidence menu declares `historical-snapshot`, active controls compute snapshot age from the latest record (2023-10-11), and state/dataset inspectors repeat the freshness boundary.  
**Guard:** ADL validation requires `snapshotFreshness()`, a persistent `data-adl-freshness` control warning and the explicit phrase that this is not current monthly ADL coverage.  
**Remaining:** replace the historical seed with a reviewed official CSV export when available; keep ADL/FBI methodologies separate.

### WM-018/019 · Physical provider status + request reliability — P1/P2
**Status:** fixed / governed on main (2026-09-20).  
**Resolution:** Terrain, Water, Hydrology, Land Cover and Aridity report a common `potato-atlas-physical-layer-status` schema into the Physical mixer, which records provider, phase, attempts, retryability, last success and last error. `3d-request-budget.js` owns explicit provider-request concurrency, in-flight de-duplication, abort handling, short-lived cache and telemetry; Hydrology is the first explicit-fetch consumer.  
**Scope boundary:** MapLibre-managed raster/vector/tile source scheduling remains under MapLibre and is not wrapped in a second scheduler.  
**Guard:** `validate_world_map_physical_provider_reliability.py` + `test_world_map_request_budget.mjs` run in the World Map quality group.

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
