# World Map Browse-First Interaction and Performance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ordinary country clicking browse-first, move retained multi-country state to explicit pins, connect map overlays directly to country statistics, and reduce duplicate UI/render work without removing Atlas capabilities.

**Architecture:** Keep the existing registry/compositor/map runtime as authoritative. Refactor country interaction into active browse state plus explicit pins, add a small active-view adapter for presentation, then migrate the compact card/inspector to that adapter. Consolidate scalar painting under the compositor and replace repeated DOM observation with explicit render lifecycle events where safe.

**Tech Stack:** Static ES modules/JavaScript, MapLibre GL, Python validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-browse-performance-design.md`

## Global Constraints

- Ordinary country clicks replace the active country; they do not mutate retained pins.
- Re-clicking the active country does not deselect it.
- Pins are deliberate retained comparison/investigation state.
- Automatic relations follow the active country in browse mode.
- No routine click, pin, overlay, statistics, or compare-preparation action automatically moves the camera.
- Unknown observations remain unknown/null, never synthetic zero.
- The compositor remains the single country-fill owner.
- Preserve existing Compare, Path, Trace, Impact, Chain, Gateway, Infrastructure and registered-entity behavior.
- Preserve empirical / sourced / inferred / project-interpretive epistemic distinctions.
- Avoid unrelated refactors.

---

### Task 1: Define the browse-first validator contract

**Files:**
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Consumes: World Map JavaScript source markers.
- Produces: a failing semantic contract until browse/pin state, lifecycle events, active-view context, and single-owner scalar rendering exist.

- [ ] Add required markers for `pinnedCodes`, `togglePinnedCountry`, `potato-atlas-pin-change`, browse-only `activateCountry`, `potato-atlas-country-card-rendered`, `__potatoAtlasActiveView`, and explicit `Color:`/Map-view presentation.
- [ ] Remove validator assumptions that `selectedCodes` is the ordinary persistent click state.
- [ ] Add regression checks rejecting ordinary click -> `toggleCountrySelection(code)` and scalar bridge full repaint ownership.
- [ ] Run the validator in CI through a PR and confirm RED before production changes.
- [ ] Commit the failing contract.

### Task 2: Convert working selection to Browse + Pins

**Files:**
- Modify: `world-map/3d-country-selection.js`

**Interfaces:**
- Produces: `activeCode`, `pinnedCodes`, `pin(code)`, `unpin(code)`, `togglePinnedCountry(code)`, `isPinned(code)`, `potato-atlas-pin-change`.
- Preserves: `window.__potatoAtlasSelection`, `potato-atlas-selection-change`, legacy URL recovery.

- [ ] Replace persistent `selectedCodes` click semantics with `pinnedCodes` plus independent active country.
- [ ] Make normal polygon click call `activateCountry(code)` only; Shift-click toggles a pin.
- [ ] Render the retained strip from pins only and rename its copy to `pinned`.
- [ ] Serialize `pins=` for new URLs while accepting legacy `selected=` and `compare=` on restore.
- [ ] Make automatic relations use `[activeCode]` in normal browse mode.
- [ ] Keep `window.goCountry` browse-first and no-auto-fly.
- [ ] Emit selection and pin events with distinct semantics.
- [ ] Commit and verify syntax/validator progress.

### Task 3: Add shared active-view context

**Files:**
- Create: `world-map/3d-active-view.js`
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**
- Produces: `window.__potatoAtlasActiveView.current`, `forCountry(code)`, `refresh(reason)`, `potato-atlas-active-view-change`.
- Consumes: layer registry, compositor composition, runtime metric observations, active selection/pins, relation mode.

- [ ] Read the active scalar/set composition from existing runtime objects rather than duplicating state.
- [ ] Resolve exact country observation, formatted value, unit, period, source/coverage and set membership where available.
- [ ] Preserve explicit unknown state.
- [ ] Load after compositor/selection and before card presentation.
- [ ] Refresh on layer, composition, selection, pin and relation-mode changes.
- [ ] Commit and verify syntax.

### Task 4: Connect map color to the country card and statistics

**Files:**
- Modify: `world-map/3d-country-card.js`
- Modify: `world-map/3d-country-pulse.js`

**Interfaces:**
- Consumes: `window.__potatoAtlasActiveView`, pin API.
- Produces: Map-view block, Statistics action, Pin/Unpin action, card/inspector lifecycle events.

- [ ] Promote active overlay to a clear `Map color` / `Map view` block near the card header.
- [ ] Show exact value, unit, period and concise source/coverage; explicit unknown when unavailable.
- [ ] Add Pin/Unpin and Statistics actions without removing current investigation actions.
- [ ] Make Statistics open/focus the existing inspector/Country Pulse rather than another floating window.
- [ ] Highlight the active map metric first in Country Pulse where it maps to a statistic.
- [ ] Dispatch `potato-atlas-country-card-rendered` and `potato-atlas-inspector-rendered` once per render.
- [ ] Commit and verify syntax/validators.

### Task 5: Improve overlay discoverability

**Files:**
- Modify: `world-map/3d-world-bar.js`

**Interfaces:**
- Consumes: active-view/composition state.
- Produces: explicit active overlay text such as `Color: GDP / person` without adding a second toolbar.

- [ ] Keep existing Stats/Groups/Religion controls.
- [ ] Make active scalar wording visually explain that it controls map color.
- [ ] Keep lower-left context passive and compact.
- [ ] Do not add camera behavior.
- [ ] Commit and verify syntax.

### Task 6: Consolidate scalar rendering ownership

**Files:**
- Modify: `world-map/3d-compositor.js`
- Modify: `world-map/3d-scalar-runtime-bridge.js`

**Interfaces:**
- Compositor owns feature-state batches and fill paint.
- Scalar bridge becomes compatibility/read adapter only.

- [ ] Move entity-aware population/area state application into the compositor path.
- [ ] Ensure one composition event produces one scalar repaint batch.
- [ ] Remove bridge listeners that repaint again on both layer and composition changes.
- [ ] Keep compatibility APIs needed by other modules.
- [ ] Add diagnostic counters for scalar compositions/state batches.
- [ ] Commit and verify syntax/validators.

### Task 7: Reduce repeated DOM enhancement work

**Files:**
- Modify where safe: `world-map/3d-gateways.js`, `world-map/3d-chain-explorer.js`, `world-map/3d-impact-actions.js`, `world-map/3d-country-dimensions.js`, `world-map/3d-evidence.js`, `world-map/3d-ui.js`.

**Interfaces:**
- Consumes: card/inspector lifecycle events.
- Produces: bounded enhancement passes, with MutationObserver only as fallback where necessary.

- [ ] Convert country-card enhancers to listen primarily for `potato-atlas-country-card-rendered`.
- [ ] Convert inspector enhancers to explicit inspector/selection events where safe.
- [ ] Keep narrow observers only for legacy/core DOM paths that cannot emit events yet.
- [ ] Count enhancement passes in diagnostics.
- [ ] Commit and verify syntax/validators.

### Task 8: Make specialist modules genuinely lazy where safe

**Files:**
- Modify: `world-map/3d-bootstrap.js`
- Create only if needed: `world-map/3d-specialist-loader.js`

**Interfaces:**
- Visible actions remain callable before implementation modules are loaded.
- Specialist modules load once on first relevant use/context.

- [ ] Remove Gateway/Chain/Infrastructure/Impact implementations from the core-to-interactive critical path where safe.
- [ ] Add one-shot lazy delegates for visible actions/events.
- [ ] Preserve current public entry points after module load.
- [ ] Count specialist lazy loads in diagnostics.
- [ ] Commit and verify syntax/validators.

### Task 9: Full verification and PR

**Files:**
- Any validator adjustments strictly required by final implementation.

**Interfaces:**
- Produces: green PR checks at exact feature head.

- [ ] Run/inspect JavaScript syntax checks for every changed JS file.
- [ ] Run/inspect `scripts/validate_world_map_3d.py` and all World Map quality validators via PR CI.
- [ ] Check diff for accidental data/camera behavior changes.
- [ ] Confirm normal browse, pin semantics, active overlay continuity, and legacy URL markers statically/through available tests.
- [ ] Open PR to `main` and verify exact-head Repository quality checks are green before completion claims.
