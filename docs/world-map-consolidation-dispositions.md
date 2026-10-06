# World Map Consolidation Dispositions

**Updated:** 2026-09-16  
**Purpose:** record what was reconstructed from stale World Map work, what is now canonical on `main`, what was deliberately not merged, and what remains compatibility work.

## Governing rule

**Salvage behavior, contracts, data and verified fixes — not stale branch history.**

Old branches are evidence and source material. Current `main` is authoritative. A historical implementation is ported only when current `main` does not already contain an equal or stronger owner, and every reconstructed slice receives a current-main regression and exact-head CI proof before merge.

## Historical Safety Wave 2 — PR #191

Disposition: **source branch only; do not merge wholesale.**

The branch mixed useful control-plane work with stale assumptions and code that could regress fixes already established on current `main`. The clearest example was historical physical-water code that restored a native detail-layer `minZoom`; current `main` intentionally keeps native water detail `minZoom` at zero and lets the shared scale runtime own the handoff, preventing the previously observed transient blank/artifact gap while zooming.

### Reconstructed and canonical

- Spatial-overlay interaction arbitration and router ownership.
- Places interaction ownership, scale ownership and deterministic label-density behavior.
- Typed Inspector Router/history and canonical inspector URL state.
- Places/subdivision migration away from raw panel snapshots.
- Shared Style Lifecycle for Render Stack and migrated physical layers.
- Runtime telemetry for source/layer counts, style restoration, interaction diagnostics and tooltip lifecycle state.
- Integrated behavioral scenario spanning wrapped geography, semantic overlap priority, tooltip invalidation/stale suppression and inspector URL/back behavior.

### Verified merge sequence

- PR #196 — spatial-overlay + Places interaction/scale reconstruction. Merged to `main` in the first reconstruction phase.
- PR #194 — typed Inspector/state safety. Merge commit `9377ce1120cdfd46f182a5fff387f95bf5873acf`; merge-result repository workflow `35087527032` passed.
- PR #197 — centralized Style Lifecycle. Merge commit `5c56e567c17848d817a21b588d117e29cf854f50`; exact-head repository workflow `35088128054` passed.
- PR #200 — event-driven runtime telemetry + integrated behavioral scenario. RED head `c0626ebc553ab5c8381828fc79c9024ac96fdd31` failed at the canonical World Map runtime gate in run `35092286561`; GREEN head `af45a70366f4d7305f2b6e8acf22a3a2092759b6` passed the entire repository workflow in run `35092475710`; merge commit `c3fd10bd763203e268933471a80ecfc53c62a792`.

## Compatibility marker — `__potatoAtlasOverlayHandled`

Disposition: **still live; bounded retirement only.**

Current default-branch inventory shows four distinct categories.

### 1. Canonical compatibility owner

`world-map/3d-interaction-router.js` sets the marker when a routed winner claims the overlay interaction. This intentionally protects still-unmigrated legacy handlers from handling the same browser event.

### 2. Genuine remaining early-boot consumers

These still use the marker as part of active behavior and therefore block global retirement:

- `world-map/3d-app.js` — core country-polygon path exists before the optional control-plane modules are fully loaded.
- `world-map/3d-hover.js` — capital/country transient interaction is imported during core boot, before the later optional module sequence.
- `world-map/3d-country-selection.js` — country selection remains coupled to the early/core country-click path.

These paths need a dedicated migration that preserves core-first availability. Reordering or deleting their guard without a regression would risk duplicate selections/clicks during boot or degraded-module conditions.

### 3. Migrated modules with degraded fallback boundaries

Places, subdivisions and spatial overlays use the shared Interaction Router on normal boots but retain direct-listener fallback code for a degraded environment in which the router is unavailable. The marker may remain inside those fallback branches until the core interaction migration makes the compatibility boundary unnecessary.

### 4. Validators/documentation

Several validators still mention the marker because they protect current compatibility behavior. They should be rewritten only when the associated production consumer migrates; validators must not force obsolete architecture after the production boundary disappears.

## Deferred from Safety Wave 2

The following remain separate work rather than justification for merging PR #191:

- physical-vs-schematic route geometry semantics;
- remaining raw zoom-magic audit outside migrated Places/subdivision ownership;
- migration of core country/capital interaction paths;
- remaining tooltip consumers outside the shared service;
- visual-channel matrix and country fill/pattern/outline/height ownership;
- broader accessibility/mobile/focus/reduced-motion hardening;
- compatibility retirement for older UI/lens surfaces.

## Architecture auditor — historical PR #188

Disposition: **compare before porting.**

Current `main` already runs an architecture-auditor test, audit, artifact upload and audit gate as part of repository quality checks. Therefore PR #188 must not be merged or copied wholesale. Any remaining #188 capability should first be compared against the current audit contract and only distinct, stronger behavior should be reconstructed.

## Permanent safety notes

- Preserve the physical-water zoom handoff fix; do not restore historical native detail `minZoom` ownership.
- Do not add duplicate global `styledata` owners when Style Lifecycle can own restoration.
- Do not add polling for runtime telemetry; consume lifecycle events or expose on-demand state.
- Do not remove an interaction compatibility marker until every affected click path has a tested canonical owner.
- Do not treat passing a subsystem test as merge evidence; use the exact PR head and the full repository quality workflow before claiming completion.
