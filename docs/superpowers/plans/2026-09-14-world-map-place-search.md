# World Map Place Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing World Map search into one place resolver for countries, supported subdivisions, and a compact later city layer while preserving fast initial load and current analytical semantics.

**Architecture:** Keep country selection owned by `3d-country-selection.js`, subdivision ownership in `3d-subdivisions.js`, and cross-class routing in a focused `3d-place-search.js`. The new controller reuses the existing header input rather than editing the giant core app. Optional city data stays same-origin and lazy-loaded. The established `validate_world_map_source.py` gate owns validation integration, so no new workflow is added.

**Tech Stack:** Vanilla JavaScript, MapLibre GL JS 6.9.0, Python source validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-14-world-map-place-search-design.md`

## Global Constraints
- Reuse the existing search input; do not add a second toolbar/search box.
- Do not add a new GitHub Actions workflow.
- Avoid changing `3d-app.js` unless a real integration blocker requires it.
- Country search/selection must remain functional if optional subdivision/city modules fail.
- Subdivision data remains owned by `3d-subdivisions.js`.
- Geographic context stays outside the analytical layer registry.
- No live browser geocoder.

---

### Task 1: Unified country + subdivision search contract

**Files:**
- Create: `scripts/validate_world_map_place_search.py`
- Create: `world-map/3d-place-search.js`
- Modify: `scripts/validate_world_map_source.py`
- Modify: `world-map/3d-subdivisions.js`
- Modify: `world-map/3d-panel-lifecycle.js`

**Interfaces:**
- Consumes: `window.__potatoAtlasSelection.activate(code, options)` and `window.__potatoAtlasSubdivisions.select(id, options)`.
- Produces: `window.__potatoAtlasPlaceSearch.submit(query)` and `window.__potatoAtlasSubdivisions.search(query)`.

- [x] **Step 1: Write failing source validator**

Defined the focused place-search contract before the implementation existed.

- [x] **Step 2: Run validator and confirm failure**

Observed expected RED result: `PLACE SEARCH CONTRACT FAILED: world-map/3d-place-search.js must exist`.

- [x] **Step 3: Implement minimal country + subdivision resolver**

Added normalized subdivision lookup, focused place-search orchestration, runtime `Find place…` copy, capture-phase Enter routing, country selection through the canonical selection API, and subdivision loading only when needed.

- [ ] **Step 4: Run focused and repository validation**

Run through the PR quality gate and inspect any failure. Required source checks:
```bash
python scripts/validate_world_map_place_search.py
python scripts/validate_world_map_source.py
node --check world-map/3d-place-search.js
node --check world-map/3d-subdivisions.js
```
Expected: PASS.

- [ ] **Step 5: Commit/review first independently usable slice**

Review the PR diff for ownership/performance regressions before beginning city data.

---

### Task 2: Compact pinned city layer

**Files:**
- Create: `scripts/build_world_places.py`
- Create: `scripts/test_build_world_places.py`
- Create: `data/world-places.geo.json`
- Modify: `world-map/3d-place-search.js`
- Modify: `scripts/validate_world_map_place_search.py`
- Modify: `scripts/validate_world_map_source.py` only if another focused contract hook is required.

**Interfaces:**
- Consumes: Natural Earth v5.1.2 populated-place fields (`ne_id`, `name`, `adm0_a3`, `adm1name`, `adm0cap`, `scalerank`, `min_zoom`, `pop_max`, point geometry).
- Produces: compact same-origin GeoJSON with stable `NE-<ne_id>` IDs and contextual place metadata.

- [ ] **Step 1: Write failing builder tests**

Test that admin-0 capitals are retained, ordinary `scalerank <= 4` cities are retained, lower-priority small places and scientific stations are excluded, IDs are stable, and source metadata is preserved.

- [ ] **Step 2: Run builder tests and confirm failure**

Run: `python scripts/test_build_world_places.py`
Expected: FAIL because builder functions do not exist yet.

- [ ] **Step 3: Implement builder and checked-in snapshot**

Normalize only display/navigation fields; keep Natural Earth population explicitly labeled as an estimate and do not couple it to canonical country demography.

- [ ] **Step 4: Extend renderer/search**

Lazy-load `data/world-places.geo.json`, render scale-ranked city dots/labels, route search selections to a city inspector, and persist `?place=NE-…`.

- [ ] **Step 5: Run focused and repository checks**

Run builder tests, place validator, JS syntax, existing subdivision validator, and repository quality checks. Confirm the initial map path does not require the city snapshot.

- [ ] **Step 6: Commit**

Commit the city layer only after the first search slice remains green.
