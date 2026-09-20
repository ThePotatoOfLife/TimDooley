# World Map Quality Audit — 2026-09-20

**Scope:** current `main` World Relational Atlas / `world-map/`.
**Purpose:** critic-level assessment of what works, what is degraded, what is broken, why it fails, and the standard required before the map should be considered clean.
**Relationship to other docs:** this document is the quality diagnosis; `docs/WORLD-MAP-PROBLEM-LEDGER.md` is the numbered execution queue; `docs/WORLD-MAP-ROADMAP.md` is the architectural direction.

## Intended standard

The map is considered **beyond clean** when:

1. every semantic responsibility has one canonical runtime owner;
2. every consumer reads that owner rather than republishing or shadowing it;
3. URL state has one mutation contract and deterministic hydration/reset semantics;
4. interaction priority is Router-owned on normal boots and degraded listeners cannot become permanent by boot order;
5. camera movement goes through the shared Motion policy and respects reduced-motion preferences;
6. Inspector content participates in typed history/back/URL/focus semantics rather than replacing panel HTML ad hoc;
7. Style Lifecycle is the only style-reload owner and Render Stack is the only semantic z-order owner;
8. scale thresholds that change behavior are named capabilities, not scattered zoom magic numbers;
9. evidence attaches to canonical geographic objects and preserves source/methodology/missing-data boundaries;
10. physical providers expose common loading/partial/degraded/error states and share bounded request budgets;
11. mobile, keyboard, focus, live-region and non-color semantics are regression-tested;
12. performance is bounded by explicit source/layer/cache/request budgets;
13. compatibility surfaces are temporary, measurable and removable;
14. every important failure is observable through compact diagnostics and maps to an actionable ledger ID.

## Executive assessment

The map is **architecturally strong but not yet converged**.

The strongest parts are the canonical country layer, geospatial kernel, scale foundation, Render Stack, Style Lifecycle, Tooltip Service, typed Inspector foundation, lazy subdivision partitions, evidence provenance boundaries, bounded Places/subdivision caching, context policy, and grouped CI.

The remaining problems are mostly coordination debt:
- too many modules can still mutate browser URL state directly;
- some modules still bypass the Inspector Router;
- a few camera and interaction paths bypass their shared owners;
- legacy UI/Lens/Fields/Networks compatibility remains live;
- behavioral scale thresholds are not fully centralized;
- accessibility/mobile/color semantics are incompletely proven;
- physical-provider reliability and request budgeting remain fragmented;
- data depth is uneven (subdivisions only USA/CAN/DNK; ADL snapshot is historical).

## Status matrix

| Area | Status | What works | What does not meet standard |
|---|---|---|---|
| Core geography | GOOD | canonical country geometry/selection, antimeridian kernel, compare/fit foundations | some legacy country interaction fallback remains |
| Render/style ownership | GOOD / DEGRADED | one Style Lifecycle; Render Stack; explicit visual channels | country visual-channel audit not fully closed; dormant legacy writers remain |
| Interaction | DEGRADED | central Interaction Router and semantic priority | boot-order fallbacks can become permanent in some modules; compatibility marker remains |
| Camera/motion | DEGRADED | shared Motion policy exists and major consumers migrated | Hover capital focus and Spatial Overlay fit still bypass Motion |
| URL state | BROKEN ARCHITECTURALLY | state can be restored and reset | 20+ modules call `history.replaceState` directly; ownership/race semantics remain distributed |
| Inspector/navigation | DEGRADED | typed Inspector works for Places/Subdivisions | ADL, Axis, Axis Depth, Mud/Below, Spatial Overlay UI bypass typed history and write panel directly |
| Scale semantics | DEGRADED | named shared scale bands/capabilities; Places/Subdivisions/ADL migrated | raw behavior thresholds remain in Water/Hydrology/Axis/core/specialists; classification incomplete |
| Subdivisions | GOOD / INCOMPLETE | USA 51/51, Canada 13/13, Denmark 5/5; bounded generic partition engine | national-context/readability edge cases incomplete; world coverage intentionally sparse |
| Evidence | GOOD / STALE DATA | generic evidence coordinator; evidence-provider attachment to subdivisions; ADL attribution/methodology | committed ADL seed is historical, not current monthly export; future comparison layer absent |
| Physical world | DEGRADED | lazy modules, per-layer status and opacity | provider error vocabulary inconsistent; no shared cross-provider network/concurrency budget |
| Accessibility | DEGRADED | Context Status uses live region; shared reduced-motion policy exists | incomplete focus return, keyboard/menu regression, color redundancy, small-screen occlusion testing |
| UI convergence | DEGRADED | UI Layout owns placement budgets; World Bar is primary | `3d-ui.js`, `3d-selection-ui.js`, Lens/Fields/Networks compatibility still inject styles/controls |
| Observability/testing | GOOD / DEGRADED | 100+ map validators/tests, architecture auditor, runtime telemetry, grouped CI | audit findings do not map directly to queue IDs; some behavior remains static-marker tested |
| Performance | GOOD / DEGRADED | lazy specialist loading, bounded subdivision/Places caches, context budgets | physical providers have no one request budget; total runtime module count remains high |
| Data semantics | GOOD | provenance/missing-data guardrails are strong | uneven country/subdivision/evidence freshness and depth must stay explicit |

## Proven defects and risks

### 1. Decentralized URL mutation — HIGH
More than twenty runtime modules call `history.replaceState` directly. The map has a whole-map state coordinator, but not a canonical URL mutation owner.

**Failure mode:** one module can unintentionally preserve/delete another subsystem's parameter; hydration/reset knowledge is duplicated; compatibility parameters survive unpredictably.

**Solution:** introduce one URL State service with namespaced ownership, atomic patching, hydration registration, and diagnostics. Migrate domains incrementally. Direct `history.replaceState` becomes forbidden outside the URL owner and explicitly bounded compatibility adapters.

### 2. Inspector bypass — HIGH
Places and Subdivisions use the typed Inspector Router. ADL, Axis, Axis Depth, Mud/Below and Spatial Overlay UI still replace `panel.innerHTML` directly.

**Failure mode:** back/history semantics, canonical `inspect=` path, focus restoration, and parent/child navigation can disagree with what the user sees.

**Solution:** each specialist registers typed inspector nodes and renders through the Router. Raw panel writes are allowed only inside a node render callback owned by the current Inspector state.

### 3. Interaction boot-order split ownership — HIGH
Spatial Overlays and Country Selection capture `window.__potatoAtlasInteraction` at module initialization and retain fallback direct MapLibre listeners when Router ownership is unavailable at that moment.

**Failure mode:** a temporary degraded boot can become permanent split ownership; interaction priority becomes dependent on load order.

**Solution:** normal application modules must await/resolve the Router before binding. Genuine standalone degraded mode needs a removable fallback registration that is explicitly torn down when the Router appears.

### 4. Residual motion-policy bypass — MEDIUM
Major camera consumers use `3d-motion.js`, but capital focus in Hover still calls `map.easeTo` directly and Spatial Overlay fit still calls `map.fitBounds` directly.

**Failure mode:** reduced-motion preference is not respected consistently.

**Solution:** route every user-visible camera transition through Motion; validator scans should forbid raw camera calls outside the Motion owner and explicitly classified internal MapLibre setup.

### 5. Scale magic not fully classified — MEDIUM
Raw zoom tests/minzoom values remain in physical, Axis, core, ADL/Places presentation and lifecycle code.

**Failure mode:** request density, interaction activation and rendering can cross thresholds at different zooms.

**Solution:** inventory every raw threshold and classify it as behavior capability, cartographic interpolation, camera intent or fixture. Only capability thresholds move to Scale contract; interpolation/camera values remain local but documented.

### 6. Inspector/layout focus semantics incomplete — MEDIUM
UI Layout controls position, but opening/closing inspector/menu surfaces does not yet have complete focus-return behavior.

**Failure mode:** keyboard users can be stranded after a panel/menu closes; mobile overlays can hide the focused control.

**Solution:** focus origin token on open, deterministic focus return on close/back, Escape semantics per surface, automated narrow-viewport keyboard scenarios.

### 7. Color-only semantics possible — MEDIUM
Analytical/evidence layers can communicate intensity/membership primarily through color.

**Failure mode:** low-vision/color-deficient users may not distinguish evidence/analytical states.

**Solution:** require textual legend values plus pattern/shape/stroke redundancy for semantically important states; add contrast/color-independence validator.

### 8. Physical provider reliability not unified — MEDIUM
Physical Layers owns a common high-level phase record, but individual providers still expose provider-specific partial/error/request behavior.

**Failure mode:** inconsistent messages and repeated expensive requests when several physical layers are active.

**Solution:** common provider result schema + one request/concurrency budget + abort/de-dupe/cache telemetry shared by Terrain/Water/Hydrology/Land Cover/Aridity.

### 9. Legacy UI/compatibility surface remains large — MEDIUM
`3d-ui.js`, `3d-selection-ui.js`, `3d-lenses.js`, `3d-fields.js`, and `3d-networks.js` remain live compatibility participants.

**Failure mode:** styles, controls, URL parameters and interactions can be owned twice; visual cleanup becomes harder because old assumptions remain executable.

**Solution:** feature-by-feature parity matrix, then retire one compatibility owner at a time with regressions. Do not mass-delete.

### 10. Evidence freshness is not equivalent to evidence integration — MEDIUM
ADL is structurally integrated with canonical U.S. subdivisions and now uses geometry-independent state aggregates, but the committed snapshot is historical.

**Failure mode:** users may assume a technically polished layer is current.

**Solution:** make snapshot vintage/status visually persistent; add stale-age indicator; replace with reviewed official CSV when available; keep ADL and FBI methodologies separate.

### 11. Subdivision coverage/readability uneven — LOW/MEDIUM
USA, Canada and Denmark work through the generic engine, but Alaska/Hawaii/DC, dense Northeast labels, globe mode and narrow screens are not fully regression-tested.

**Solution:** viewport/label scenarios and a generic partition quality checklist before adding more countries.

### 12. Audit-to-workflow bridge incomplete — LOW
Architecture auditor reports findings but does not map recurring findings to ledger IDs/owners.

**Solution:** finding code → ledger ID → owner → severity mapping; grouped CI summary links directly to remediation.

## What should not be “fixed”

- 74 runtime modules are not automatically a bug; duplicate ownership is.
- symbolic/project geography should not be forced into ordinary sovereignty/geography.
- missing data should not be filled with guesses.
- ADL and FBI datasets should not be merged into one score.
- camera interpolation numbers are not automatically scale-contract thresholds.
- compatibility should not be deleted until canonical parity is proven.

## Recommended work order

1. URL ownership + interaction boot-order.
2. Inspector convergence.
3. residual Motion + scale classification.
4. visual-channel/style/legacy writer retirement.
5. accessibility/mobile/color semantics.
6. provider reliability/request budget.
7. subdivision/evidence data expansion and freshness.
8. audit-to-ledger automation and final compatibility retirement.
