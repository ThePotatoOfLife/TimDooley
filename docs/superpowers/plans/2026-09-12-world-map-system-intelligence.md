# World Map System Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose evidence-backed capability, dependency, builds, resilience context and gateway/chokepoint data through the existing World Map runtime and country-card workflow without adding another permanent control surface.

**Architecture:** Extend the existing generated runtime with a normalized `systems` object for every canonical country plus a sourced gateway owner. Keep gateway visualization contextual to country selection. Reuse the existing registry/runtime/card/bootstrap architecture; do not create a parallel application state or synthetic scores.

**Tech Stack:** Static JSON, Python runtime generator/validators, vanilla ES modules, MapLibre GL JS, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-system-intelligence-design.md`

## Global Constraints

- No capability, power, alignment or resilience score.
- Missing evidence remains unknown.
- Legacy unsourced strategic prose is not promoted merely because it is detailed.
- Capability/build/dependency extraction uses explicit canonical fields only.
- Gateway observations remain dated and sourced.
- No new ordinary top-level map menu.
- All 195 canonical countries receive runtime `systems` context.

---

### Task 1: Add failing system-intelligence validator

**Files:**
- Create: `scripts/validate_world_map_system_intelligence.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Requires `data/world-map-gateways.json`, generated runtime `systems`, browser runtime API, country-card consumption, contextual gateway module and registry ownership.

- [ ] Write validator requiring 195 country `systems` records, no `*_score` fields, gateway provenance/map anchors, runtime coverage, registry entries, card consumption, and bootstrap/module integration.
- [ ] Wire `python scripts/validate_world_map_system_intelligence.py` immediately after the Axis/systems validator.
- [ ] Commit and observe CI fail because production pieces are absent.

### Task 2: Add empirical gateway owner

**Files:**
- Create: `data/world-map-gateways.json`

**Interfaces:**
- Produces `gateways` keyed by stable IDs with `coordinates`, `countries`, `systems`, `observation`, `description`, `epistemic_type`.

- [ ] Add Malacca, Hormuz, Suez/SUMED, Bab el-Mandeb, Danish Straits, Turkish Straits, Panama Canal and Cape of Good Hope route.
- [ ] Use dated EIA transit observations for the common maritime chokepoint dataset and authoritative Panama metadata where required.
- [ ] Mark coordinates `approximate-center` and explicitly unsuitable for navigation.

### Task 3: Extend generated runtime

**Files:**
- Modify: `scripts/build_world_map_runtime.py`
- Modify: `scripts/validate_world_map_data_runtime.py`

**Interfaces:**
- Runtime country shape gains:
```json
"systems": {
  "capabilities": [],
  "dependencies": [],
  "builds": [],
  "chains": [],
  "gateways": [],
  "resilience": {"evidence_domains": [], "score": null, "policy": "no aggregate score inferred"}
}
```
- Top-level runtime gains `gateways` and `system_coverage`.

- [ ] Extract capabilities from explicit canonical country strategic-asset/value-chain fields.
- [ ] Extract dependencies only from explicit typed dependency relationships/fields.
- [ ] Extract builds from sourced observations whose keys contain project/build/tender/expansion/planned/new-offshore/new_* semantics.
- [ ] Join chain IDs and gateway IDs by ISO3.
- [ ] Add coverage counts for capabilities/dependencies/builds/chains/gateways.
- [ ] Add validator assertions proving 195-system coverage and no synthetic score.

### Task 4: Expose runtime API and registry contracts

**Files:**
- Modify: `world-map/3d-compositor.js`
- Modify: `data/world-map-layer-registry.json`

**Interfaces:**
- Add runtime API methods:
```js
systemContext(code)
gatewaysForCountry(code)
gateway(id)
systemCoverage()
```
- Contextual registry entries become current and runtime-owned.

- [ ] Add the four runtime API functions.
- [ ] Promote `derived.capability`, `derived.dependency`, `derived.resilience` to current runtime-backed contextual entries.
- [ ] Add `derived.builds` and `gateway.context` as current contextual entries.
- [ ] Keep every entry `ordinary:false`.

### Task 5: Surface system role in country card

**Files:**
- Modify: `world-map/3d-country-card.js`

**Interfaces:**
- Consumes `systemContext(code)` and `gatewaysForCountry(code)`.

- [ ] Fetch system context alongside axis/membership/comparison context.
- [ ] Render a compact `System role` section only when evidence exists.
- [ ] Show up to 3 capabilities, 2 dependencies, 2 builds and 2 gateways with `+N` overflow tags.
- [ ] Do not render aggregate resilience as a score.

### Task 6: Add contextual gateway point module

**Files:**
- Create: `world-map/3d-gateways.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `.github/workflows/quality-checks.yml` JS syntax step

**Interfaces:**
- Module listens to `potato-atlas-working-selection-change` and reads `window.__potatoAtlasDataRuntime`.
- Owns a GeoJSON source/layer pair and popup behavior.

- [ ] Add contextual GeoJSON source and circle/symbol layers.
- [ ] On country selection show only directly associated gateways; on clear selection show none.
- [ ] Popup displays label, type, latest observation value/unit/period and source.
- [ ] Load module after Country Card in ordinary bootstrap; no toolbar control.
- [ ] Add `node --check world-map/3d-gateways.js` to CI.

### Task 7: Verify, open PR, and report

**Files:**
- No planned production changes except fixes revealed by verification.

- [ ] Confirm the red validator run exists from Task 1.
- [ ] Confirm exact-head full quality suite is green.
- [ ] Open PR to `main` summarizing system intelligence, gateway context and evidence boundaries.
- [ ] Report branch head SHA and CI run number; do not merge without explicit user instruction.
