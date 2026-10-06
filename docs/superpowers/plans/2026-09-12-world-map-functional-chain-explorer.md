# World Map Functional Chain Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** Turn contextual functional-chain tags into an outline-based interactive explorer using the existing shared World Map runtime.

**Architecture:** Add one lightweight explorer module that owns chain feature-state, URL state and a compact contextual strip. Modify the existing country card only enough to expose stable `data-chain-id` actions. Keep all ordinary navigation unchanged.

**Tech Stack:** Vanilla ES modules, MapLibre feature-state, shared generated runtime, Python contract validation.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-functional-chain-explorer-design.md`

## Constraints
- No new permanent menu.
- No fill ownership changes.
- Use `atlasChainMatch` feature-state and a separate line layer.
- Use existing runtime `chain(id)` / `chainsForCountry(code)`.
- Persist only `chain=<id>` in the URL.

### Task 1 — Contract gate
- [ ] Create `scripts/validate_world_map_chain_explorer.py` requiring stable chain IDs in country-card actions, explorer module, feature-state, outline layer, URL persistence and bootstrap integration.
- [ ] Add validator to canonical quality workflow.
- [ ] Open PR and confirm red failure before implementation.

### Task 2 — Country-card action hooks
- [ ] Change functional-chain tags to buttons carrying `data-chain-id`.
- [ ] Preserve compact rendering and descriptions.

### Task 3 — Chain explorer module
- [ ] Create `world-map/3d-chain-explorer.js`.
- [ ] Validate requested URL chain against runtime.
- [ ] Mark/unmark participating ISO3 country features with `atlasChainMatch`.
- [ ] Add `atlas-chain-outline` line layer using feature-state.
- [ ] Add a compact contextual strip with label, systems, epistemic/source note and clear action.
- [ ] Expose `window.__potatoAtlasChainExplorer` with `set`, `toggle`, `clear`, `get`.

### Task 4 — Bootstrap + verification
- [ ] Load explorer after Country Card and System Intelligence.
- [ ] Run exact-head repository quality checks.
- [ ] Merge into main only after green verification, following the established user preference to bake verified side work into main.
