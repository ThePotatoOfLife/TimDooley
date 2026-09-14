# Focused Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove live routing fossils from the current five-door + Explore architecture without redesigning the site or creating another competing maintenance layer.

**Architecture:** Keep `data/frontend-atlas-bridge.json` as the routing-intent owner and `data/canonical-record-registry.json` as the generated ID/source inventory. Add one `Explore` ID lookup route so graph tools can resolve canonical IDs through existing source records; migrate live emitters and selected active metadata away from retired `index.html#node=...` links. Extend the existing projection validator and operating map rather than adding parallel guards or maintenance documents.

**Tech Stack:** Static HTML/CSS/JavaScript, JSON routing contracts, Python validators, GitHub Actions.

**Spec:** User-approved focused hygiene scope from 2026-09-14 repository audit.

## Global Constraints

- Preserve exactly five homepage doors: Tim Dooley, Religion, Philosophy, Science, World.
- World Map remains a specialist surface beneath World.
- Deep interactive navigation belongs to `/explore/`; do not revive the retired root node reader.
- Do not create a second routing registry or a second maintenance roadmap.
- Preserve canonical content owners and epistemic boundaries.
- Prefer truthful metadata removal/migration over decorative additions.

---

### Task 1: Make stale deep links test-visible

**Files:**
- Modify: `scripts/validate_public_projection.py`

**Interfaces:**
- Consumes: `data/frontend-atlas-bridge.json`, `data/atlas-manifest.json`, current runtime files and active routing metadata.
- Produces: failing assertions for missing `lookup` routing and surviving retired live routes.

- [ ] Add `lookup: explore/#lookup=<id>` to the expected interactive contract.
- [ ] Assert `app/app.js` handles `#lookup=` through the canonical record registry.
- [ ] Assert standalone Timeline no longer emits `../#record=`.
- [ ] Assert World Map Entity Trace no longer emits or consumes `index.html#node=` routes.
- [ ] Assert selected active metadata (`global-graph-bridge`, belief backend/registry, religious layer map, country fallback) contains no retired node routes.
- [ ] Push the validator-only change and confirm the PR quality workflow fails for the intended missing behavior.

### Task 2: Add one canonical ID resolver to Explore

**Files:**
- Modify: `app/app.js`
- Modify: `data/frontend-atlas-bridge.json`
- Modify: `data/atlas-manifest.json`

**Interfaces:**
- Consumes: `canonicalRecordRegistry.records[]` where each record has `id` and `occurrences[].source`.
- Produces: `explore/#lookup=<id>`; one unique safe source opens directly, multiple safe sources render explicit choices, unknown IDs return to a clear lookup result without guessing.

- [ ] Index canonical registry rows by ID while building Explore indexes.
- [ ] Add lookup rendering and hash handling without changing existing branch/record/context/path routes.
- [ ] Add the lookup route to both canonical routing contracts.
- [ ] Keep direct record loading allowlisted through existing `recordPaths` logic.

### Task 3: Migrate live emitters and active metadata

**Files:**
- Modify: `app/timeline.js`
- Modify: `world-map/3d-entity-trace.js`
- Modify: `data/global-graph-bridge.json`
- Modify: `data/belief-backend.json`
- Modify: `data/belief-registry.json`
- Modify: `data/religious-layer-map.json`
- Modify: `data/country-fallback.json`
- Modify: `scripts/build_site.py`

**Interfaces:**
- Consumes: `explore/#record=<path>` for source-file links and `explore/#lookup=<id>` for entity-ID links.
- Produces: no live runtime or selected active metadata dependency on `index.html#node=...`.

- [ ] Point standalone Timeline source links at `../explore/#record=<path>`.
- [ ] Make Entity Trace construct archive links from the canonical lookup route instead of bridge-local legacy routes.
- [ ] Migrate graph/belief/religion/country routing metadata to Explore/World-era routes while preserving data ownership.
- [ ] Replace the stale `world_map` primary-door build label with `world`.

### Task 4: Align operator guidance and preserve deferred options

**Files:**
- Modify: `docs/PROJECT-OPERATING-MAP.md`
- Modify: `TODO.md`

**Interfaces:**
- Produces: current operator guidance plus a compact future-hygiene queue in existing docs.

- [ ] Correct the fifth-door wording to World and remove the obsolete consolidation-branch instruction.
- [ ] Record that `_site` discovery files are generated projections; absence from source is not automatically a defect.
- [ ] Add a short deferred hygiene section covering: broader fossilized metadata audit, historical branch/PR pruning, optional branch/ruleset protections, and legacy source-strata retirement only after provenance migration.
- [ ] Do not create another maintenance note.

### Task 5: Verify and retire superseded PR state

**Files:** no product file required.

**Interfaces:**
- Consumes: GitHub Actions, current `main`, PR #121.
- Produces: green focused-hygiene PR and closed superseded research PR.

- [ ] Confirm all substantive PR #121 research/index files already exist on current `main` through later integration.
- [ ] Close PR #121 as superseded/absorbed rather than merging its historical branch.
- [ ] Run/observe Repository quality checks on the focused-hygiene PR.
- [ ] Review the final diff for accidental scope growth and retired-route remnants.
- [ ] Merge only after the green gate; otherwise leave the focused branch isolated for repair.

## Self-review

- Spec coverage: live Timeline and Entity Trace links, canonical ID resolver, active metadata migration, operator drift, future options, PR #121 retirement, and CI validation are all owned by tasks above.
- Placeholder scan: no TBD/TODO/implement-later placeholders are used; deferred work is explicitly bounded as future hygiene rather than part of this implementation.
- Type consistency: lookup uses an entity/record ID string; record loading continues to use an allowlisted source path string.
