# World Map Place Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing World Map search into one place resolver for countries, supported subdivisions, and the populated places already present in the map while preserving fast initial load and current analytical semantics.

**Architecture:** Keep country selection owned by `3d-country-selection.js`, subdivision ownership in `3d-subdivisions.js`, and existing populated-place display ownership in `3d-hover.js`. Cross-class routing lives in focused `3d-place-search.js`, which reuses the existing header input rather than editing the giant core app. The established `validate_world_map_source.py` gate owns validation integration, so no new workflow is added.

**Tech Stack:** Vanilla JavaScript, MapLibre GL JS 6.9.0, Python source validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-14-world-map-place-search-design.md`

## Global Constraints
- Reuse the existing search input; do not add a second toolbar/search box.
- Do not add a new GitHub Actions workflow.
- Avoid changing `3d-app.js` unless a real integration blocker requires it.
- Country search/selection must remain functional if optional subdivision/place data fails.
- Subdivision data remains owned by `3d-subdivisions.js`.
- Reuse `data/world-capitals.geo.json`; do not create a duplicate city dataset or renderer for this slice.
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

- [x] **Step 4: Run focused and repository validation**

The first implementation head (`0782b374…`) completed the full Repository quality checks successfully in run #963.

- [x] **Step 5: Review first independently usable slice**

Self-review reduced the integration surface: no `3d-app.js`, `index.html`, or workflow edit was required. Validation remains folded into the canonical World Map source gate.

---

### Task 2: Search the existing populated-place layer

**Files:**
- Modify: `world-map/3d-place-search.js`
- Modify: `scripts/validate_world_map_place_search.py`
- Modify: this design/plan documentation only to record the discovered ownership boundary.

**Interfaces:**
- Consumes: existing `data/world-capitals.geo.json` features (`iso3`, `name`, `country`, `scalerank`, `primary`, source, Point geometry) already loaded/rendered by `3d-hover.js`.
- Produces: city search results, stable `CITY-<ISO3>-<slug>` navigation IDs, `?place=` deep links, and one transient selection marker/label for the chosen place.

- [x] **Step 1: Scan before adding city data**

Found that `3d-hover.js` and `data/world-capitals.geo.json` already provide 150+ pinned Natural Earth populated places, including primary capitals and selected non-primary cities. Cancelled the proposed duplicate city builder/dataset.

- [x] **Step 2: Write the failing city contract**

Extended the focused validator to require the existing snapshot, at least 150 valid features, broad primary-capital coverage, selected non-primary places, exact city search/focus behavior, `?place=` ownership, and a visible searched-place marker.

- [x] **Step 3: Confirm RED in the canonical gate**

Repository quality run #966 reached `Validate canonical World Map runtime` after all earlier checks passed, then failed on the deliberately unmet city contract.

- [x] **Step 4: Implement existing-data city search**

Reused `world-capitals.geo.json` without changing the existing renderer. Added lazy city lookup, datalist enrichment, exact/prefix matching, parent-country activation, coordinate focus, `?place=CITY-…` restoration, and a transient selection marker/label that also makes indexed non-primary cities visible when selected.

- [x] **Step 5: Harden selection-state ownership**

Added cleanup so a later direct country or subdivision selection removes a stale city marker/deep link, while city focus can retain its parent-country context. The focused validator now runs `node --check` on both new/modified JavaScript modules.

- [ ] **Step 6: Require a fresh green quality run on the exact final head**

Do not merge or claim completion until the current branch head passes the full repository quality workflow.

---

### Task 3: Future populated-place expansion only if justified

Do not automatically introduce a broader city dataset. First evaluate real search misses and whether the existing pinned Natural Earth 1:110m places are materially insufficient. If expansion is justified later, extend the canonical place source deliberately rather than layering a parallel geocoder or duplicate renderer on top of it.
