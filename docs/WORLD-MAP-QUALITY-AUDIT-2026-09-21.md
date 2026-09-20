# World Map Quality Audit — 2026-09-21

**Scope:** current World Map mainline after Progressive/Selection UI and Lens retirement, plus green-but-not-yet-merged map PRs noted separately.  
**Base main commit at audit start:** `d925744db6446acfce94c9735157c11431625e7e`.  
**Authority:** current diagnosis. Execution remains in `docs/WORLD-MAP-PROBLEM-LEDGER.md`; architecture direction remains in `docs/WORLD-MAP-ROADMAP.md`.

## Executive assessment

The World Map is now **strong in control-plane ownership and weak mainly in breadth, freshness, final compatibility retirement and combined-behavior proof**.

Major architectural defects from the 2026-09-20 audit have been closed or substantially narrowed:
- URL mutation is owned by `3d-url-state.js`; direct browser-history writes are rejected outside the owner.
- Places, Subdivisions, ADL, Mud/Below, Axis, Axis Depth and Spatial Overlay inspection now enter the typed Inspector Router; raw panel HTML is renderer detail inside typed nodes or degraded fallback.
- User-visible camera movement is routed through the shared Motion owner; repository search found raw `map.easeTo` / `map.fitBounds` only inside `3d-motion.js`.
- Interaction boot-order fallback promotion is governed; remaining `__potatoAtlasOverlayHandled` usage is a bounded degraded compatibility boundary, not normal arbitration.
- Physical layers share provider phase/status and the request-budget owner.
- Progressive UI and Selection UI are deleted; Lens compatibility is deleted on main.
- Visual-channel compatibility is now a complete governed 9×9 matrix.

Green PRs not counted as merged at this audit instant:
- PR #366 — semantic UI layering bands.
- PR #367 — canonical route/validator ownership cleanup.

## Current status matrix

| Area | Status | Current reality | Remaining work |
|---|---|---|---|
| Core geography | GOOD | canonical countries, antimeridian-safe fits, compare/selection | expand first-order regional coverage |
| URL/state | GOOD | one URL State owner with namespaced claims/patches | keep retired compatibility params from returning |
| Inspector | GOOD | typed nodes cover current specialist inspectors | broaden browser-level back/focus scenarios |
| Interaction | GOOD / COMPAT | Router owns normal interaction | retire degraded marker only with standalone fallback retirement |
| Motion | GOOD | raw user-visible camera calls centralized | maintain validator coverage |
| Render/style | GOOD | Render Stack + Style Lifecycle + visual matrix | retire dormant Fields/Networks assumptions |
| Scale | GOOD / MONITORED | behavioral thresholds classified/shared | keep future additions classified |
| UI convergence | GOOD / IN PROGRESS | World Bar/UI Layout primary; legacy UI removed | shared surface tokens; semantic z-index PR pending |
| Subdivisions | GOOD / SPARSE | USA, CAN, DNK, UKR, RUS through generic engine | expand countries; add combined viewport scenarios |
| Places | GOOD / STALE-SEED | bounded 4,591-place seed, 95 global-major features | fresh reproducible build and broader country depth |
| Conflict/history | CONTRACT ONLY | strong schema and separation rules | no reviewed snapshot geometry committed |
| Evidence | GOOD / MIXED FRESHNESS | ADL integration/provenance strong | ADL current export + cross-layer freshness vocabulary |
| Physical world | GOOD | common status + request budget | continue real-provider degradation scenarios |
| Accessibility | GOOD / NEEDS COMBINED PROOF | focus/keyboard/reduced-motion contracts exist | narrow-screen/globe/region combined scenarios |
| Observability | GOOD / SPLIT QUEUE | telemetry + architecture auditor + grouped CI | map finding codes to ledger IDs/owners |
| Compatibility | IMPROVING | UI/Selection/Lens retired | Fields/Networks + bounded interaction marker remain |

## Verified open defects / gaps

### A. Dead compatibility source: Fields / Networks
`3d-fields.js` and `3d-networks.js` are absent from current bootstrap/import paths but still carry control injection, URL/time/tooltip logic and validator/data-contract references. They are a retirement candidate, not yet a safe mass deletion. See WM-045.

### B. Regional coverage is intentionally sparse
Only five first-order country partitions are committed: USA, CAN, DNK, UKR and RUS. The engine is generic; coverage is not. See WM-046.

### C. Place freshness is not known exactly
The detailed Places system uses a pinned GeoNames `cities15000` mirror seed. The exact upstream refresh date is unknown, and detailed partitions currently align with the same five promoted regional countries. See WM-047.

### D. Conflict/history has no real snapshot data yet
The conflict contract is `active-schema-dormant-data`. No reviewed historical/delayed geometry is committed, so the Time + Inspector + conflict-render path is not yet exercised end-to-end. See WM-048.

### E. Combined browsing scenarios are under-tested
Strong unit/regression coverage exists, but globe projection + narrow viewport + dense region labels + detached geography + region→Places has no single end-to-end scenario. See WM-049.

### F. Auditor findings do not become work items automatically
Architecture diagnostics and the ledger remain separate systems. Recurring finding types should resolve to owner, severity and ledger ID. See WM-050.

### G. Regional statistics are uneven by design, but can be enriched
Geometry-first partitions correctly preserve unknown statistics. An optional sourced statistics join would make regional inspection richer without contaminating boundary provenance. See WM-051.

### H. UI token convergence is incomplete
Layering bands are being centralized, but common menu/panel/context/control surfaces still repeat local CSS literals. See WM-052.

### I. Freshness semantics vary by data family
ADL, Places, empirical relationship data and physical providers communicate recency/status differently. Readers need a shared vocabulary that preserves those differences instead of flattening them. See WM-053.

## Things checked and *not* re-opened as bugs

- Raw `panel.innerHTML` is not itself a defect when it is the render callback of a typed Inspector node. Current ADL/Mud/Axis/Axis Depth/Spatial/Places/Subdivision paths are Router-aware.
- Raw `map.easeTo` / `map.fitBounds` calls were not found outside the Motion owner in current main.
- Raw MapLibre `minzoom` values are not automatically behavioral-scale bugs; many are classified cartographic/presentation values.
- More runtime modules are not automatically a problem; duplicate ownership is the criterion.
- Unknown regional population/area values must remain unknown until a sourced enrichment exists.

## Recommended next work order

1. Merge already-green semantic-layering and canonical-route PRs if still clean after current-main reconciliation.
2. Retire Fields/Networks compatibility with parity regressions.
3. Add architecture-auditor → ledger mapping.
4. Add the combined globe/mobile/regional browser scenario.
5. Build fresh reproducible Places ingestion and promote the next regional country wave.
6. Ingest one reviewed delayed/historical conflict snapshot.
7. Add optional sourced regional statistics.
8. Finish common surface/freshness UI vocabulary.
