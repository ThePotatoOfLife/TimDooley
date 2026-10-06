# World Map Context / Visibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one context/visibility runtime that coordinates active country, pins, scale, time and investigation mode, then expose that state through a compact pinned-country context rail and budget-aware automatic relations.

**Architecture:** Preserve existing owners. `3d-context-visibility.js` derives policy only; `3d-country-selection.js` continues to rank/render automatic relations; `3d-pinned-context.js` renders compact retained-country context; `3d-ui-layout.js` owns placement. Bootstrap loads the new runtime after the control-plane foundations and before dependent presentation modules.

**Tech Stack:** Vanilla ES modules/scripts, MapLibre runtime APIs, DOM CustomEvents, existing Python/Node validation scripts.

**Spec:** `docs/superpowers/specs/2026-09-17-world-map-context-visibility-design.md`

## Global Constraints

- No new canonical database in the frontend.
- Do not add a second relation-ranking engine.
- Do not change epistemic types based on selection, zoom or visual overlap.
- Use existing scale/runtime/state owners; no raw zoom thresholds in new modules.
- One deep inspector; pinned countries use compact context only.
- New UI placement must register through `3d-ui-layout.js`.
- No separate prediction/culture map in this wave.

---

### Task 1: Context / Visibility Runtime

**Files:**
- Create: `world-map/3d-context-visibility.js`
- Modify: `world-map/3d-bootstrap.js`
- Test: `scripts/validate_world_map_context_visibility.py`

**Interfaces:**
- Consumes: `window.__potatoAtlasSelection`, `window.__potatoAtlasScale`, `window.__potatoAtlasLayers`, `window.__potatoAtlasTime`, inspector/evidence DOM state when available.
- Produces: `window.__potatoAtlasContextVisibility.current`, `.refresh(reason)`, event `potato-atlas-context-visibility-change`.

- [ ] Add a validator that requires the runtime, bootstrap load order, coalesced refresh, named scale consumption and the context-change event.
- [ ] Add the runtime with derived modes `browse|compare|connections|evidence`, deterministic relation/card budgets and visibility flags.
- [ ] Load it in bootstrap after Scale/Interaction/Inspector/Selection foundations and before pinned presentation consumers.
- [ ] Re-read changed files and verify required interface tokens are present.
- [ ] Commit.

### Task 2: Budget-Aware Automatic Relations

**Files:**
- Modify: `world-map/3d-country-selection.js`
- Extend: `scripts/validate_world_map_context_visibility.py`

**Interfaces:**
- Consumes: orchestrator budget payload `{active,pinned,total}`.
- Produces: `window.__potatoAtlasSelection.setAutomaticRelationBudget(next)` and budget-aware `automaticRelationData()`.

- [ ] Extend validation to require the public budget setter and forbid moving edge ranking out of selection.
- [ ] Replace fixed automatic relation constants with mutable defaults guarded by numeric clamps.
- [ ] Keep ranking/diversity logic unchanged; only budgets vary.
- [ ] Emit relation refresh after a budget change.
- [ ] Re-read changed file and verify backward-compatible selection snapshot fields remain.
- [ ] Commit.

### Task 3: Pinned Context Rail

**Files:**
- Create: `world-map/3d-pinned-context.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `world-map/3d-ui-layout.js`
- Extend: `scripts/validate_world_map_context_visibility.py`

**Interfaces:**
- Consumes: selection pins/activation API, `window.__potatoAtlasActiveView.forCountry(code)`, context visibility budgets.
- Produces: `#atlasPinnedContextRail`, compact country cards, diagnostics counter `pinnedContextCards`.

- [ ] Add `bottom-context` as a layout zone and host.
- [ ] Create a bounded horizontal rail that renders at most the orchestrator card budget while preserving all pins in selection state.
- [ ] Card click activates country; remove control unpins without changing other state.
- [ ] Refresh on pin/selection/layer/time/relation/context events with generation-based stale suppression.
- [ ] Load rail after Active View and UI Layout.
- [ ] Hide the legacy direct selection strip when rail is active without deleting compatibility code.
- [ ] Re-read files and verify mobile scroll/bounded surface rules are present.
- [ ] Commit.

### Task 4: Map-State Diagnostics and Architecture Guard

**Files:**
- Modify: `world-map/3d-map-state.js`
- Modify: `docs/WORLD-MAP-ROADMAP.md`
- Extend: `scripts/validate_world_map_context_visibility.py`

**Interfaces:**
- Consumes: `window.__potatoAtlasContextVisibility.current`.
- Produces: map-state snapshot field `contextVisibility` and roadmap record of the new canonical owner.

- [ ] Add orchestrator snapshot to semantic map-state diagnostics.
- [ ] Record the completed foundation and next extension order in the roadmap.
- [ ] Validator checks map-state snapshot integration and roadmap ownership wording.
- [ ] Re-read changed files and verify no reset path directly mutates orchestrator state.
- [ ] Commit.

### Task 5: Verification

**Files:**
- Read-only verification of all files above.

- [ ] Fetch the validator and inspect every assertion against current branch files.
- [ ] Compare branch against `main`; confirm only intended files changed.
- [ ] Search changed modules for new raw zoom magic numbers, direct country-fill paint ownership, or new canonical-data copies; none should be introduced.
- [ ] Report execution limitation: connector environment cannot run repository Python/Node tests directly unless a workflow/check is available.
- [ ] Keep branch unmerged until verification/review is complete.
