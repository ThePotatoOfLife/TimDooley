# World Map Multi-Country Subdivisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generalize the existing subdivision runtime to country-indexed partitions and land Denmark's five official-source regions as the second production partition.

**Architecture:** Keep `world-map/3d-subdivisions.js` as the sole subdivision renderer and use `data/world-subdivisions/index.json` as the routing registry. Resolve deep links and viewport relevance from descriptor metadata, preserving lazy loading, the canonical `#panel` inspector, URL state, and existing MapLibre layer ownership.

**Tech Stack:** Browser JavaScript, MapLibre GL JS, GeoJSON, Python validators, Node regression tests, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-world-map-multi-country-subdivisions-design.md`

## Global Constraints

- Do not add a second map, second inspector, or eager all-world subdivision payload.
- Keep subdivision data same-origin and partitioned by country.
- Preserve one-shot deep-link camera intent; persistent selection must never trigger repeated `fitBounds` on `moveend`.
- Missing Denmark population remains unknown, never numeric zero.
- Preserve official DAWA/Dataforsyningen provenance for Denmark.
- Exact-head Repository quality checks are required before merge to `main`.

---

### Task 1: Generic subdivision runtime regression

**Files:**
- Create: `scripts/test_world_map_subdivision_multi_country.mjs`
- Modify: `scripts/validate_world_map_subdivisions.py`

**Interfaces:**
- Consumes: `window.__potatoAtlasSubdivisions`, `data/world-subdivisions/index.json` descriptor contract.
- Produces: executable regression proving `DK-*` routes to the `DNK` partition and camera intent remains one-shot.

- [ ] **Step 1: Write the failing test**

Create a fake index with USA and DNK descriptors, a fake Denmark region feature `DK-1083`, start at `?subdivision=DK-1083`, and assert that importing `3d-subdivisions.js` fetches `DNK.geo.json`, fits exactly once, and a subsequent `moveend` leaves the fit count at one.

- [ ] **Step 2: Run test to verify it fails**

Run: `node scripts/test_world_map_subdivision_multi_country.mjs`
Expected: FAIL because the current runtime only recognizes `US-` and `USA_BOUNDS`.

- [ ] **Step 3: Register the regression in the canonical validator**

Add the new Node regression beside `test_world_map_subdivision_freeze.mjs` in `scripts/validate_world_map_subdivisions.py` so future repository-quality runs execute both.

- [ ] **Step 4: Commit the red test**

Commit message: `test(world-map): require multi-country subdivisions`

### Task 2: Generalize the runtime

**Files:**
- Modify: `world-map/3d-subdivisions.js`

**Interfaces:**
- Consumes: index descriptors containing `path`, `id_prefix`, and `viewport_bounds`.
- Produces: generic `partitionForId(id)`, generic relevance loading, generic `select(id)`.

- [ ] **Step 1: Replace USA-only routing minimally**

Load the index once, find descriptors by `id_prefix`, evaluate `viewport_bounds`, and call `loadPartition(partition)` for deep-link or viewport-relevant descriptors. Keep the current fallback for USA only as compatibility when the descriptor is missing.

- [ ] **Step 2: Preserve one-shot camera semantics**

Use `pendingDeepLinkId` only for the initial deep-link fit. After the target feature is found, clear the pending id before selecting so the resulting `moveend` cannot refit.

- [ ] **Step 3: Make `select(id)` generic**

Resolve the partition through index metadata rather than `id.startsWith('US-')`.

- [ ] **Step 4: Run the focused regressions**

Run:
`node scripts/test_world_map_subdivision_freeze.mjs`
`node scripts/test_world_map_subdivision_multi_country.mjs`
Expected: both PASS.

- [ ] **Step 5: Commit**

Commit message: `feat(world-map): generalize subdivision partitions`

### Task 3: Land Denmark data and index metadata

**Files:**
- Create by existing Git blob: `data/world-subdivisions/DNK.geo.json`
- Modify: `data/world-subdivisions/index.json`
- Modify: `scripts/validate_world_map_subdivisions.py`

**Interfaces:**
- Consumes: immutable blob `40fa7231bcd23b3d042adfc85c29fdd851ebab80` from the earlier proven map branch.
- Produces: registered `DNK` descriptor and validated five-region production partition.

- [ ] **Step 1: Attach the exact Denmark blob**

Create the new branch tree entry for `data/world-subdivisions/DNK.geo.json` with blob SHA `40fa7231bcd23b3d042adfc85c29fdd851ebab80`, preserving bytes and provenance.

- [ ] **Step 2: Extend the index**

Add `id_prefix: "US-"` and `viewport_bounds` to USA if absent, then add DNK with path `DNK.geo.json`, feature count 5, admin level 1, status `implemented-geometry-first`, source `Danish Agency for Climate Data (DAWA/Dataforsyningen)`, population status `unknown-not-zero`, id prefix `DK-`, parent name `Denmark`, Denmark viewport bounds, and five lightweight search records.

- [ ] **Step 3: Extend data validation**

Require DNK descriptor count 5, GeoJSON feature count 5, unique `DK-*` ids, subdivision type `region`, geometry source/provenance, and no invented numeric population value.

- [ ] **Step 4: Run canonical subdivision validation**

Run: `python scripts/validate_world_map_subdivisions.py`
Expected: PASS with USA 51/51 and Denmark 5/5.

- [ ] **Step 5: Commit**

Commit message: `data(world-map): add Denmark regions`

### Task 4: Repository verification and merge

**Files:**
- No production files beyond Tasks 1-3.

**Interfaces:**
- Consumes: exact PR head SHA.
- Produces: verified merge on `main`.

- [ ] **Step 1: Open the PR against current `main`**

Describe the generic runtime, Denmark provenance, regression coverage, and bounded lazy-loading behavior.

- [ ] **Step 2: Run exact-head Repository quality checks**

Require the full workflow to complete with conclusion `success`, including canonical World Map runtime, UI shell/layout, spatial overlays, Palestine geometry, pathfinder, investigation utility, and Trace.

- [ ] **Step 3: Merge with expected head SHA**

Merge only the verified PR head and then fetch `main` to confirm the merge commit.
