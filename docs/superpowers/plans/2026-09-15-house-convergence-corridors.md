# House Convergence Corridors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Converge public route authority, expose mature reader forms beneath the five fixed homepage gateways, add a real Works reader, and remove route drift across House governance, frontend projection, discovery builders, and operating docs.

**Architecture:** Keep the five primary gateways unchanged. Expand `data/house/public-surfaces.json` and its topology ledger to register mature secondary/subordinate surfaces, route branches to their strongest readers, make discovery builders consume House authority, and expose a compact homepage `Ways in` corridor. Public pages remain projections; canonical knowledge stays in existing owners.

**Tech Stack:** Static HTML/CSS, JSON, Python 3 standard library, repository validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-house-convergence-corridors-design.md`

## Global Constraints

- Exactly five primary gateway IDs remain `tim`, `religion`, `philosophy`, `science`, `world` in that order.
- Exactly five primary routes remain `/tim-dooley/`, `/religion/`, `/philosophy/`, `/science/`, `/world/`.
- World Map remains specialist under World.
- Domain Rooms are not homepage labels.
- Story, Collection, Works, Timeline, Questions, A–Z, Explore, Sources, and Context are projections/readers, not canonical knowledge owners.
- Static semantic HTML must remain sufficient for essential navigation.
- No mass folder moves, framework rewrite, or sixth homepage gateway.
- Full repository quality checks and final built-site validation must pass before merge.

---

### Task 1: Make House public-surface authority extensible and complete

**Files:**
- Modify: `schemas/house-public-surface-registry.schema.json`
- Modify: `data/house/public-surfaces.json`
- Modify: `knowledge/research/potato-house-master/public-route-topology.json`
- Modify: `scripts/validate_house_governance.py`

**Interfaces:**
- Consumes: ten Room IDs from `data/house/rooms.json`.
- Produces: registered public surface IDs/routes consumed by frontend/discovery code; exact one-record-per-active-surface topology invariant.

- [ ] **Step 1: Write the failing governance assertions**

Extend `scripts/validate_house_governance.py` with constants:

```python
REQUIRED_SURFACES = {
    "story": "/tim-dooley/story/",
    "collection": "/corporium/",
    "works": "/works/",
    "questions": "/questions/",
    "index-a-z": "/index-a-z/",
    "context": "/context/",
}
GENERATED_SURFACES = {"questions", "index-a-z"}
TOPOLOGY = ROOT/'knowledge/research/potato-house-master/public-route-topology.json'
```

Add checks that every required surface exists, `secondary_global_ids` resolve to registered IDs, and every active surface has exactly one topology record with matching route/type/Room IDs.

- [ ] **Step 2: Run the validator and verify RED**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: FAIL because the six required surfaces/topology records do not yet all exist and topology currently omits at least Culture.

- [ ] **Step 3: Remove the fixed surface ceiling**

In `schemas/house-public-surface-registry.schema.json`, retain `minItems: 15` but remove `maxItems: 15` from `surfaces`.

- [ ] **Step 4: Register the new surfaces**

Update `data/house/public-surfaces.json`:

```json
"secondary_global_ids": ["timeline","explore","sources","questions","index-a-z","context"]
```

Add records:

```json
{"id":"story","route":"/tim-dooley/story/","canonical_route":"/tim-dooley/story/","surface_type":"guide","title":"Story","primary_parent":"tim","primary_room_ids":["potatoverse-canon","time-history","archive-sources","works","culture-information"],"status":"active","visibility":"specialist","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
{"id":"collection","route":"/corporium/","canonical_route":"/corporium/","surface_type":"guide","title":"Collection","primary_parent":"tim","primary_room_ids":["potatoverse-canon","culture-information","life-body","science-formal-models","archive-sources"],"status":"active","visibility":"specialist","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
{"id":"works","route":"/works/","canonical_route":"/works/","surface_type":"guide","title":"Works","primary_parent":"tim","primary_room_ids":["works","culture-information","archive-sources","time-history"],"status":"active","visibility":"specialist","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
{"id":"questions","route":"/questions/","canonical_route":"/questions/","surface_type":"explorer","title":"Questions","primary_parent":"home","primary_room_ids":["potatoverse-canon","archive-sources","time-history","traditions-texts","science-formal-models","life-body","world-systems","culture-information","works","research-lab"],"status":"active","visibility":"secondary","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
{"id":"index-a-z","route":"/index-a-z/","canonical_route":"/index-a-z/","surface_type":"explorer","title":"A–Z","primary_parent":"home","primary_room_ids":["potatoverse-canon","archive-sources","time-history","traditions-texts","science-formal-models","life-body","world-systems","culture-information","works","research-lab"],"status":"active","visibility":"secondary","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
{"id":"context","route":"/context/","canonical_route":"/context/","surface_type":"guide","title":"Context & Evidence","primary_parent":"home","primary_room_ids":["archive-sources","potatoverse-canon","time-history","traditions-texts","science-formal-models","life-body","world-systems","culture-information","works","research-lab"],"status":"active","visibility":"secondary","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
```

- [ ] **Step 5: Synchronize topology**

Add topology rows for all six new surfaces and the existing `culture` surface. Match registry route/type/Rooms exactly. Use `primary_hub_id="tim"` for Story/Collection/Works; `null` for Questions/A–Z/Context; `culture` may remain `null`/home-context as current registry defines.

- [ ] **Step 6: Run governance validation and verify GREEN**

Run:

```bash
python scripts/validate_house_governance.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add schemas/house-public-surface-registry.schema.json data/house/public-surfaces.json knowledge/research/potato-house-master/public-route-topology.json scripts/validate_house_governance.py
git commit -m "architecture: register mature reader surfaces"
```

---

### Task 2: Route mature branches to their strongest public readers

**Files:**
- Modify: `data/frontend-atlas-bridge.json`
- Modify: `scripts/validate_public_projection.py`

**Interfaces:**
- Consumes: public route authority from Task 1.
- Produces: branch-level human-route intent while retaining Explore archive routes.

- [ ] **Step 1: Add failing projection assertions**

Add checks:

```python
if projection.get("timeline", {}).get("global_route") != "timeline/": ...
if projection.get("corporium", {}).get("human_route") != "corporium/": ...
if projection.get("works", {}).get("human_route") != "works/": ...
if bridge.get("backend_family_projection", {}).get("culture", {}).get("global_route") != "context/culture/": ...
```

- [ ] **Step 2: Run RED**

```bash
python scripts/validate_public_projection.py
```

Expected: FAIL on the stale routes.

- [ ] **Step 3: Correct bridge routes**

Change only public/human routes:

```json
"timeline":{"global_route":"timeline/","archive_route":"explore/#branch=timeline",...}
"corporium":{"primary_door":"philosophy","human_route":"corporium/","archive_route":"explore/#branch=corporium",...}
"works":{"primary_door":"tim","human_route":"works/","archive_route":"explore/#branch=works",...}
```

and:

```json
"culture":{"global_route":"context/culture/",...}
```

- [ ] **Step 4: Run GREEN**

```bash
python scripts/validate_public_projection.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data/frontend-atlas-bridge.json scripts/validate_public_projection.py
git commit -m "architecture: route branches to mature readers"
```

---

### Task 3: Add the Works public reader

**Files:**
- Create: `works/index.html`
- Modify: `scripts/validate_reader_surfaces.py` or the nearest existing static-reader validator if appropriate after inspection.

**Interfaces:**
- Consumes: canonical creative archive at `knowledge/culture/creative-systems-archive.json` and registered `/works/` route from Task 1.
- Produces: human-curated Works projection; no new substantive owner.

- [ ] **Step 1: Add a failing reader contract**

Require source HTML `works/index.html` and semantic markers/text proving:

```text
reader surface: works
Play & Simulation
Writing & Performance
Music & Sound
Visual & Symbolic Art
Recovered & Experimental Works
creative work does not automatically become doctrine/evidence
```

Also require links to `../tim-dooley/`, `../tim-dooley/story/`, `../corporium/`, `../explore/#branch=works`, and `../context/source-authority/`.

- [ ] **Step 2: Run RED**

Run the focused reader validator. Expected: FAIL because `/works/` does not yet exist.

- [ ] **Step 3: Create `works/index.html`**

Use the existing site system stylesheet and a simple reader layout. Include:

```html
<body><main class="page page--reading" data-reader-surface="works">
```

Use five genre sections from the design. Explain representative existing works without copying the full JSON archive. Add a concise evidence boundary explaining Works is a presentation over existing creative owners.

- [ ] **Step 4: Run GREEN**

Run the focused reader validator. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add works/index.html scripts/validate_reader_surfaces.py
git commit -m "feat: add Works reader"
```

---

### Task 4: Replace generic homepage threads with the Ways-in corridor

**Files:**
- Modify: `index.html`
- Modify: existing homepage validator found by repository inspection; if no focused validator exists, extend the nearest public/home shell validator rather than creating a redundant framework.

**Interfaces:**
- Consumes: Story, Timeline, Collection, Works routes.
- Produces: subordinate homepage discovery corridor without changing primary gateway count.

- [ ] **Step 1: Write failing homepage assertions**

Require exactly five primary `.sections > a` routes in canonical order and require the subordinate corridor to contain:

```text
Story -> tim-dooley/story/
Timeline -> timeline/
Collection -> corporium/
Works -> works/
```

Require footer links to:

```text
questions/
index-a-z/
explore/
context/source-authority/
tools/tts/
```

- [ ] **Step 2: Run RED**

Expected: FAIL because Home still contains `Other threads` and lacks the new corridor/utilities.

- [ ] **Step 3: Update homepage HTML/CSS**

Rename `.secondary-threads` to a neutral subordinate style or reuse it while changing semantics. Replace:

```html
<strong>Other threads</strong> ...
```

with:

```html
<strong>Ways in</strong>
<a href="tim-dooley/story/">Story</a>
<a href="timeline/">Timeline</a>
<a href="corporium/">Collection</a>
<a href="works/">Works</a>
```

Update footer with Questions and A–Z while preserving Sources, Explore/Archive, TTS.

- [ ] **Step 4: Run GREEN**

Run focused homepage validation. Expected: PASS and still exactly five primary gateways.

- [ ] **Step 5: Commit**

```bash
git add index.html scripts/<homepage-validator>.py
git commit -m "feat: add homepage ways-in corridor"
```

---

### Task 5: Make discovery builders consume House route authority

**Files:**
- Create: `scripts/house_public_surfaces.py`
- Modify: `scripts/build_discovery.py`
- Modify: `scripts/build_site_authority.py`
- Modify: `scripts/validate_seo_pipeline.py` or existing discovery/authority validator after inspection.

**Interfaces:**
- Produces:

```python
load_public_surfaces(root: Path) -> dict
primary_gateway_rows(root: Path) -> list[dict]
```

Each gateway row contains `id`, `title`, `route`, `canonical_route`.

- [ ] **Step 1: Write failing authority-source assertions**

Validator must reject independent `PRIMARY_DOORS = (...)` and `PRIMARY_ROUTES = {...}` literals in the two builders and require import/use of `primary_gateway_rows`.

- [ ] **Step 2: Run RED**

Expected: FAIL because both builders currently hard-code five routes.

- [ ] **Step 3: Implement resolver**

`scripts/house_public_surfaces.py` loads `data/house/public-surfaces.json`, verifies exact primary ID order and returns registered rows. Fail with `ValueError` on missing/malformed authority.

- [ ] **Step 4: Refactor `build_discovery.py`**

Replace static `PRIMARY_DOORS` with:

```python
from house_public_surfaces import primary_gateway_rows
PRIMARY_DOORS = tuple(
    (row["id"], row["title"], row["canonical_route"])
    for row in primary_gateway_rows(ROOT)
)
```

Retain generated Questions/A–Z/deep discovery behavior.

- [ ] **Step 5: Refactor `build_site_authority.py`**

Build `PRIMARY_ROUTES` from `primary_gateway_rows(ROOT)` and preserve exact output shape.

- [ ] **Step 6: Run focused tests GREEN**

Run SEO/discovery/authority validators. Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/house_public_surfaces.py scripts/build_discovery.py scripts/build_site_authority.py scripts/validate_seo_pipeline.py
git commit -m "refactor: derive discovery routes from House authority"
```

---

### Task 6: Reconcile current operating documentation

**Files:**
- Modify: `docs/PROJECT-OPERATING-MAP.md`
- Modify: `docs/PROJECT-STRUCTURE.md`
- Modify: `TODO.md`

**Interfaces:**
- Consumes: final authority model implemented by Tasks 1–5.
- Produces: non-stale orientation for future maintainers.

- [ ] **Step 1: Update route authority language**

State that:

```text
docs/POTATO-HOUSE-CONSTITUTION.md = architecture constitution
data/house/public-surfaces.json = public route/surface identity authority
manifest.json = archive branch/pathway/deep Explore relationship map
```

- [ ] **Step 2: Correct fifth gateway and workspace language**

Replace stale statements naming World Map as fifth primary door. Remove statements that describe an old consolidation branch as the active implementation workspace; `main` is deployment base and feature work uses isolated branches.

- [ ] **Step 3: Add mature reader forms**

Document Story, Timeline, Collection, Works, Questions, A–Z, Explore, Sources as public reading/discovery forms beneath the five gateways.

- [ ] **Step 4: Run docs/content validators**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/PROJECT-OPERATING-MAP.md docs/PROJECT-STRUCTURE.md TODO.md
git commit -m "docs: align operating map with House authority"
```

---

### Task 7: Full integration verification and review

**Files:** no planned content changes unless verification exposes a defect.

**Interfaces:** verifies the entire convergence wave.

- [ ] **Step 1: Run focused validators**

```bash
python scripts/validate_house_governance.py
python scripts/validate_public_projection.py
python scripts/validate_reader_surfaces.py
python scripts/validate_seo_pipeline.py
```

Include any existing homepage/world/discovery validators identified during implementation.

- [ ] **Step 2: Run the complete repository quality workflow**

Use the repository's existing GitHub Actions quality workflow on the exact branch head. Require all jobs/steps to pass, including full build, content integrity, source/route audits, SEO, machine discovery, and final `_site` shell validation.

- [ ] **Step 3: Review the PR diff**

Confirm:

- no sixth primary gateway;
- no canonical creative content duplicated into Works;
- no stale route tables remain in discovery builders;
- no unintended route or Room changes;
- only current operating docs are normalized; historical specs remain historical.

- [ ] **Step 4: Promote PR and merge only after exact-head green verification**

Use expected head SHA during merge.
