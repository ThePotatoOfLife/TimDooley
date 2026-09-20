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
**Status:** fixed on main (2026-09-20).  
**Resolution:** threshold moved to `world-map-scale-contract.json`; Water consumes the canonical `physical-water-detail` capability.

### WM-004 · Hydrology owns private 4 / 5.2 / 6.7 / 8.2 thresholds — P2
**Status:** fixed on main (2026-09-20).  
**Resolution:** Hydrology consumes canonical Scale capabilities for load/detail regimes so request density and render activation share one threshold owner.

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
**Status:** in progress (2026-09-20).  
**Completed in current wave:** Inspector now exposes expanded/controls/hidden state, explicit opens can focus the inspector, close/Escape returns focus to the opening control, World Bar Escape returns focus to its summary, and mobile menu popovers are bounded by the dynamic viewport.  
**Remaining:** verify narrow-height landscape, browser zoom, keyboard-only traversal order, and interaction with native select popups / temporary investigation surfaces.

### WM-011 · Reduced-motion behavior incomplete — P2
**Status:** fixed on main (2026-09-20).  
**Resolution:** shared `3d-motion.js` policy removes camera animation for `prefers-reduced-motion: reduce`, migrated camera consumers use it, CSS motion is suppressed, and canonical validation/regression coverage exists.

### WM-012 · Color-only semantics remain possible — P2
**Status:** open.  
**Risk:** analytical/evidence differences may rely too heavily on hue.  
**Next:** add textual/shape/pattern redundancy and accessibility checks.

### WM-013 · Active-view accessibility summary incomplete — P2
**Status:** in progress (current wave).  
**Implementation:** read-only polite/atomic live region summarizes selection, analytical/physical/evidence/geography layers, relation mode, projection, time and named scale from canonical APIs/events.  
**Next:** exact-head CI, then close.

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

### WM-021 · Escape dismissal can fall through to legacy world reset — P1/P2
**Status:** fixed in current wave; awaiting exact-head CI.  
**Cause:** core `3d-app.js` still owns a global Escape shortcut that resets world state, while newer menus/inspector surfaces lacked guaranteed precedence.  
**Resolution:** inspector/menu dismissal consumes Escape before legacy reset and restores focus to the owning control; regressions pin propagation ownership.

### WM-022 · Mobile World Bar popover can exceed usable viewport — P2
**Status:** fixed in current wave; awaiting exact-head CI.  
**Cause:** fixed-position menu used a top offset without a dynamic bottom/height bound.  
**Resolution:** mobile menu uses left/right/bottom bounds, `100dvh` maximum height and contained overscroll.  
**Remaining:** landscape + browser-zoom visual verification.

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
