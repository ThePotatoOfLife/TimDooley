# Backend → Frontend Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove backend/frontend routing drift and make one explicit projection contract drive five-door human navigation, archive reachability, generated pages, discovery metadata and validation.

**Architecture:** `data/frontend-atlas-bridge.json` becomes the single routing/projection contract without taking ownership of content. Canonical data continues to live in its existing owners; the bridge maps major branches/families into exactly five primary public doors plus global secondary surfaces. Build, discovery and archive code consume the same semantics, and a dedicated validator prevents retired single-index/root.js assumptions from returning.

**Tech Stack:** JSON data contracts, Python build/validation scripts, vanilla JavaScript archive runtime, static HTML/CSS, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-backend-frontend-convergence-design.md`

## Global Constraints

- The homepage exposes exactly five principal doors: Tim Dooley, Religion, Philosophy, Science, World Map.
- No new top-level public door is introduced.
- `data/frontend-atlas-bridge.json` owns routing intent only; canonical content ownership stays where it is.
- `/explore/` remains the full human archive explorer.
- Retired `root.js`, `index.html#node=...`, and single-index public-Door assumptions must not be treated as live architecture.
- Reader pages explain; they do not silently redefine canon.
- Preserve archive path allowlisting when broadening record access.
- Remove presentation/routing drift, not substantive research.

---

### Task 1: Canonical projection contract

**Files:**
- Modify: `data/frontend-atlas-bridge.json`
- Modify: `data/backend-coverage-map.json`
- Modify: `data/atlas-manifest.json`
- Create: `scripts/validate_public_projection.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: branch IDs and route semantics from `manifest.json` and `data/atlas-manifest.json`.
- Produces: `public_doors`, `global_secondary_surfaces`, `branch_projection`, `backend_family_projection`, `record_resolution`, `integrity_requirements` in `data/frontend-atlas-bridge.json`; validator exit status for CI.

- [ ] **Step 1: Write the failing validator**

Create `scripts/validate_public_projection.py` to assert:

```python
EXPECTED_DOORS = {
    "tim": "tim-dooley/",
    "religion": "religion/",
    "philosophy": "philosophy/",
    "science": "science/",
    "world_map": "world-map/",
}
```

The validator must load `manifest.json`, `data/frontend-atlas-bridge.json`, `data/backend-coverage-map.json`, and `data/atlas-manifest.json`; fail if the bridge lacks these exact doors; fail if any manifest branch is missing a projection status; fail if live metadata references `root.js` or `index.html#node=`; and fail if atlas interactive branch/record/context/pathway routes do not use `/explore/`.

- [ ] **Step 2: Run the validator and verify RED**

Run:

```bash
python scripts/validate_public_projection.py
```

Expected: non-zero exit because the current bridge still declares the single-index public Door and the coverage map still lists `root.js` / `index.html` as generic consumers.

- [ ] **Step 3: Replace the stale bridge contract**

Update `data/frontend-atlas-bridge.json` so it contains exactly five `public_doors`, global secondary routes for Timeline, Sources, Explore, Questions and A–Z, explicit `branch_projection` entries for every current manifest branch, and backend-family mappings that preserve canonical ownership while identifying public projection destinations.

- [ ] **Step 4: Reconcile coverage and atlas routing metadata**

Update `data/backend-coverage-map.json` to describe five-door + Explore consumption rather than single-index/root.js consumption. Update `data/atlas-manifest.json` interactive routes to `/explore/#branch=<id>`, `/explore/#record=<path>`, `/explore/#context=<id>`, and `/explore/#path=<id>`.

- [ ] **Step 5: Run validator and verify GREEN**

Run:

```bash
python scripts/validate_public_projection.py
```

Expected: exit 0 with a concise success summary.

- [ ] **Step 6: Wire validator into CI and commit**

Add the command to `.github/workflows/quality-checks.yml` before the public site build, then commit these files with message:

```text
refactor: converge public projection contracts
```

---

### Task 2: Preserve backend provenance in question discovery

**Files:**
- Modify: `scripts/build_discovery.py`
- Create: `scripts/validate_discovery_projection.py`

**Interfaces:**
- Consumes: `knowledge/reader/tim-dooley-question-index.json` fields `deep_sources` and `class`.
- Produces: discovery question objects with normalized `canonical_owners: list[str]` and `epistemic_class: list[str]`.

- [ ] **Step 1: Write the failing validator**

Create a validator that runs the discovery build into its normal output location, locates at least one imported Tim question with `deep_sources` and `class`, and asserts the resulting discovery record preserves both as normalized lists.

- [ ] **Step 2: Run and verify RED**

Run:

```bash
python scripts/validate_discovery_projection.py
```

Expected: non-zero because the current importer reads only `canonical_owners` and `epistemic_class`.

- [ ] **Step 3: Implement schema fallbacks**

In `scripts/build_discovery.py`, normalize values with a helper equivalent to:

```python
def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
```

Use `canonical_owners` when present, otherwise `deep_sources`; use `epistemic_class` when present, otherwise `class`.

- [ ] **Step 4: Run and verify GREEN**

Run both:

```bash
python scripts/validate_discovery_projection.py
python scripts/build_discovery.py
```

Expected: both exit 0.

- [ ] **Step 5: Add validator to CI and commit**

Add the validator near the existing discovery checks and commit:

```text
fix: preserve question provenance in discovery
```

---

### Task 3: Make generated pages route to the correct human parent

**Files:**
- Modify: `scripts/build_site.py`
- Create: `scripts/validate_generated_navigation.py`

**Interfaces:**
- Consumes: `data/frontend-atlas-bridge.json` branch projections and manifest branch records.
- Produces: generated topic/record/context pages with parent navigation appropriate to Tim, Religion, Philosophy, Science, World Map or Explore.

- [ ] **Step 1: Write failing generated-navigation checks**

Validator must build the site to the normal artifact directory and assert that representative generated pages from at least Tim, Religion, Science and World branches contain their mapped parent route, while a cross-domain context page contains an Explore route.

- [ ] **Step 2: Run and verify RED**

Run:

```bash
python scripts/validate_generated_navigation.py
```

Expected: non-zero because generated pages currently use generic Tim-oriented footer navigation.

- [ ] **Step 3: Add projection loading and parent resolution**

In `scripts/build_site.py`, load `data/frontend-atlas-bridge.json`, build a branch→door route map, infer record ownership from manifest branch membership, and pass resolved parent navigation into `page_shell()`.

- [ ] **Step 4: Turn branch record paths into direct generated-record links**

Where branch pages currently render canonical record paths as code-only text, render links to `/records/<record-id>/` when a generated record ID is available; retain the source path as secondary metadata rather than the primary interaction.

- [ ] **Step 5: Run and verify GREEN**

Run:

```bash
python scripts/validate_generated_navigation.py
python scripts/build_site.py
```

Expected: both exit 0.

- [ ] **Step 6: Add validator to CI and commit**

Commit:

```text
refactor: make generated navigation branch aware
```

---

### Task 4: Broaden Explore without weakening path safety

**Files:**
- Modify: `app/app.js`
- Modify: `app/reader-guide.js`
- Create: `scripts/validate_explore_projection.py`

**Interfaces:**
- Consumes: canonical record registry / canonical indexes already published to the frontend plus manifest records.
- Produces: a deduplicated allowed record path set that includes canonical registered records while rejecting arbitrary URL-supplied paths.

- [ ] **Step 1: Write failing archive reachability checks**

Validator must identify a canonical record present in the canonical record registry but absent from the current manifest-derived `recordPaths`, then assert that the Explore runtime source includes a registry-backed allowlist input and does not directly fetch unvalidated hash paths.

- [ ] **Step 2: Run and verify RED**

Run:

```bash
python scripts/validate_explore_projection.py
```

Expected: non-zero because `app/app.js` currently derives allowed paths only from manifest/context graph records.

- [ ] **Step 3: Add registry-backed allowlisting**

Load the canonical registry in the archive runtime, extract only repository-relative JSON paths already approved by that registry, merge them with manifest/context paths, deduplicate, and continue checking any requested record path against the merged set before fetch.

- [ ] **Step 4: Remove obsolete Start Here reader-guide action**

Replace the `learn/` action in `app/reader-guide.js` with a route to the current five-door home or the current branch’s mapped public parent when available.

- [ ] **Step 5: Run and verify GREEN**

Run:

```bash
python scripts/validate_explore_projection.py
node --check app/app.js
node --check app/reader-guide.js
```

Expected: all exit 0.

- [ ] **Step 6: Commit**

```text
refactor: align archive reachability with canonical registry
```

---

### Task 5: Project richer backend threads into the five public doors

**Files:**
- Modify: `tim-dooley/index.html`
- Modify: `religion/index.html`
- Modify: `philosophy/index.html`
- Modify: `science/index.html`
- Modify: `world-map/index.html`
- Modify: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: branch projection and existing question/guide material.
- Produces: one compact `Explore deeper` surface per public door, using current routes rather than raw file paths.

- [ ] **Step 1: Add failing surface assertions**

Extend `scripts/validate_reader_surfaces.py` so each principal door must contain a single `data-projection-surface` region and at least two relevant deep routes, while the homepage still exposes exactly five principal doors.

- [ ] **Step 2: Run and verify RED**

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: non-zero because the new projection surfaces do not exist yet.

- [ ] **Step 3: Add compact deeper-navigation regions**

Add one restrained `Explore deeper` region to each door. Prefer natural reader labels and current routes (`/explore/#branch=...`, Timeline, Sources, question pages, domain-specific deeper pages). Do not add another mega-menu or expose backend filenames.

- [ ] **Step 4: Run and verify GREEN**

Run:

```bash
python scripts/validate_reader_surfaces.py
```

Expected: exit 0.

- [ ] **Step 5: Commit**

```text
feat: expose deeper backend threads through five doors
```

---

### Task 6: Remove retired public runtime artifacts and stale references

**Files:**
- Delete if unreferenced: `root.js`
- Modify any current docs/data/scripts that still treat it as live.
- Modify: `scripts/validate_public_projection.py`

**Interfaces:**
- Consumes: repository-wide reference search for `root.js`, `index.html#node=`, and old single-index language.
- Produces: no live runtime dependency on retired architecture; explicitly historical references remain labeled as retired.

- [ ] **Step 1: Strengthen validator to catch live retired references**

Have `validate_public_projection.py` scan current architecture/runtime/config files (excluding historical docs/specs and generated artifacts) for forbidden live references.

- [ ] **Step 2: Run and verify RED if any remain**

Run:

```bash
python scripts/validate_public_projection.py
```

Expected: fail on any still-live references.

- [ ] **Step 3: Remove only confirmed-dead runtime files/references**

Delete `root.js` only after confirming no current HTML or build script loads it. Update stale current metadata rather than deleting historical provenance.

- [ ] **Step 4: Run and verify GREEN**

Run the validator plus repository web/build checks.

- [ ] **Step 5: Commit**

```text
chore: remove retired public reader architecture
```

---

### Task 7: Full convergence verification

**Files:**
- No intended production changes unless verification exposes a real regression.

**Interfaces:**
- Consumes: all tasks above.
- Produces: exact-head CI evidence.

- [ ] **Step 1: Run targeted local/static checks available through repository scripts**

Run all new validators plus existing reader/public-navigation/build/discovery validators.

- [ ] **Step 2: Inspect branch diff against pre-convergence baseline**

Compare `f5c576d90ed6427c07c22ca5fce7b1c717d290f9` to the new head and verify changes are restricted to the convergence scope.

- [ ] **Step 3: Wait for exact-head GitHub Actions run and inspect failures**

Use the workflow run tied to the new head; if red, inspect the failing step and fix the root cause rather than weakening validators.

- [ ] **Step 4: Re-run until exact-head quality workflow is green**

Completion evidence is the successful workflow run on the exact final commit SHA.
