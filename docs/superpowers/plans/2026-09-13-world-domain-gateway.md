# World Domain Gateway Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make World the fifth primary public door, add a lightweight `/world/` gateway and `/world-systems/` sibling surface, preserve the World Map as a specialist geographic instrument, and reconcile the existing Politics reader into the World family.

**Architecture:** Keep one relational backend and canonical ownership model. Change only public projection/routing intent: `world` becomes the fifth public domain, while `/world-map/`, `/politics/`, `/north/`, and `/world-systems/` become sibling specialist lenses beneath it. Preserve current World Map runtime behavior and URLs; this implementation changes navigation, projection contracts, discovery, and copy before any deeper map-layer cleanup.

**Tech Stack:** Static HTML/CSS/JavaScript, JSON routing contracts, Python repository validators/build scripts, GitHub Pages, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-13-world-domain-gateway-design.md`

## Global Constraints

- Preserve exactly five homepage primary doors.
- The fifth primary door is `World` and routes to `/world/`.
- Keep `/world-map/`, `/north/`, existing Explore routes, and current World Map runtime behavior stable.
- `/politics/`, `/north/`, `/world-map/`, and `/world-systems/` are specialist siblings beneath World, not new homepage doors.
- `data/frontend-atlas-bridge.json` owns routing intent only; canonical data ownership remains unchanged.
- Unknown/null semantics and observed/inferred/project-interpretive epistemic boundaries remain unchanged.
- Do not remove Axis/North map overlays in this pass.
- Do not build a large World Systems dashboard; first version is a focused gateway/index.
- No automatic viewport movement or new global floating navigation.
- Reconcile the useful Politics reader work from PR #92 onto current `main`; do not merge its stale branch wholesale.

---

## File Structure

### New public surfaces
- `world/index.html` — thin World gateway; four sibling routes plus quiet archive/evidence links.
- `world-systems/index.html` — lightweight systems index grouped by research domain.

### Existing public surfaces
- `index.html` — rename/repoint fifth homepage card to World.
- `world-map/index.html` — clarify Map’s specialist role and add parent/sibling navigation without changing map runtime behavior.
- `north/index.html` — add World-family navigation and parent ownership.
- `politics/index.html` — transplant/reconcile PR #92 reader shell and World-family navigation.
- `politics/parts/part-01.html` through `part-04.html` — preserve PR #92 long-form political content.
- `politics/politics-manifest.json` — preserve ordered Politics reader parts.
- `app/politics-reader.js` — preserve reader assembly, with World-family footer/parent links.
- `app/longform-reader.css` — preserve shared long-form styling from PR #92.
- `knowledge/politics/tim-dooley-politics-geopolitics-compendium.json` — preserve provenance-aware politics ledger from PR #92.

### Routing/discovery contracts
- `data/frontend-atlas-bridge.json` — replace fifth `world_map` public door with `world`, reroute world-facing backend families without moving canonical owners.
- `scripts/validate_public_projection.py` — first-class contract for the new five-door architecture and specialist World routes.
- `scripts/build_discovery.py` — generate discovery navigation using World rather than World Map as the fifth primary door.
- `scripts/validate_reader_surfaces.py` — require World gateway and World-family specialist routes if needed by existing surface contract.
- `scripts/validate_public_navigation.py` — update any literal fifth-door expectations if present.
- `scripts/validate_seo_pipeline.py` / `scripts/validate_discovery_projection.py` — update only if their literal door assertions fail after the routing change.
- `data/backend-coverage-map.json` / `data/atlas-manifest.json` — update routing metadata only where they encode `world_map` as public-domain ownership; do not alter canonical datasets.

---

### Task 1: Lock the World-domain routing contract with failing validation

**Files:**
- Modify: `scripts/validate_public_projection.py`
- Inspect and modify only if literal door assumptions exist: `scripts/validate_public_navigation.py`, `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: `data/frontend-atlas-bridge.json`, `index.html`, the specialist route files.
- Produces: a failing contract requiring the new `world` public door and stable specialist routes.

- [ ] **Step 1: Change the expected public doors in `validate_public_projection.py`**

Replace the current fifth entry:

```python
"world_map": "world-map/",
```

with:

```python
"world": "world/",
```

Add route existence/content assertions equivalent to:

```python
WORLD_SPECIALISTS = {
    "world-map/index.html": "World Map",
    "politics/index.html": "Politics",
    "north/index.html": "North",
    "world-systems/index.html": "World Systems",
}

world_page = (ROOT / "world" / "index.html")
if not world_page.exists():
    fail("World gateway is missing: world/index.html", errors)
else:
    text = world_page.read_text(encoding="utf-8")
    for route in ("../world-map/", "../politics/", "../north/", "../world-systems/"):
        if route not in text:
            fail(f"World gateway must link specialist route {route}", errors)

for relative, label in WORLD_SPECIALISTS.items():
    path = ROOT / relative
    if not path.exists():
        fail(f"World specialist surface is missing: {relative}", errors)
```

Also require that `world-map/` remains a specialist route rather than a public-door key.

- [ ] **Step 2: Run the focused validator and confirm RED**

Run:

```bash
python scripts/validate_public_projection.py
```

Expected: FAIL because `data/frontend-atlas-bridge.json` still exposes `world_map: world-map/`, `/world/` does not exist, and `/world-systems/` does not exist.

- [ ] **Step 3: Inspect companion validators for literal `world_map` / `World Map` door assumptions**

Run:

```bash
grep -R "world_map\|World Map" scripts/validate_public_navigation.py scripts/validate_reader_surfaces.py scripts/validate_seo_pipeline.py scripts/validate_discovery_projection.py
```

Only change assertions that describe the **primary five-door architecture**. Preserve assertions that intentionally refer to the World Map specialist itself.

- [ ] **Step 4: Commit the RED contract**

```bash
git add scripts/validate_public_projection.py scripts/validate_public_navigation.py scripts/validate_reader_surfaces.py scripts/validate_seo_pipeline.py scripts/validate_discovery_projection.py
git commit -m "test: require World gateway public architecture"
```

---

### Task 2: Add the World gateway and World Systems sibling surface

**Files:**
- Create: `world/index.html`
- Create: `world-systems/index.html`
- Modify: `index.html`

**Interfaces:**
- Produces: `/world/` as the fifth public door and `/world-systems/` as a specialist sibling.
- Consumes: existing `/world-map/`, `/north/`, `/explore/`, source/evidence routes; `/politics/` will be added in Task 5.

- [ ] **Step 1: Create `world/index.html` as a thin routing surface**

The page must contain exactly four principal route cards:

```html
<a href="../world-map/"><strong>World Map</strong><span>Countries, geography, measurable relationships, flows, infrastructure and spatial comparison.</span></a>
<a href="../politics/"><strong>Politics &amp; Geopolitics</strong><span>Positions, proposals, political development, predictions, research leads and unresolved questions.</span></a>
<a href="../north/"><strong>North</strong><span>North Axis, North Programme, northern geography, European capability and evidence boundaries.</span></a>
<a href="../world-systems/"><strong>World Systems</strong><span>Institutions, economy, finance, ownership, industry, energy, technology, security, capability and resilience.</span></a>
```

Include a short evidence note and quiet links to `../explore/#branch=world` and `../context/source-authority/`. Do not add a new JavaScript runtime.

- [ ] **Step 2: Create `world-systems/index.html` as a compact grouped index**

Use these eight groups and route each to existing canonical/deep surfaces where possible:

```text
Governance
Economy & Finance
Ownership & Production
Energy & Infrastructure
Technology & Research
Labour & Society
Security & Capability
Dependencies & Resilience
```

Include explicit copy that World Systems explains non-spatial/system structure and links to World Map where geography helps. Do not fabricate dashboards or metrics.

- [ ] **Step 3: Change the homepage fifth card**

In `index.html`, replace the current `world-map/` primary card with:

```html
<a href="world/"><strong>World</strong><span class="purpose">Countries, politics, systems, dependencies and the relationships connecting them.</span><span class="question-previews"><span class="question-preview">How is the world connected?</span><span class="question-preview">Which lens should I use?</span></span></a>
```

Keep five cards total.

- [ ] **Step 4: Run the focused validator**

```bash
python scripts/validate_public_projection.py
```

Expected: still FAIL on the projection JSON and missing Politics route, but the World gateway/systems failures are gone.

- [ ] **Step 5: Commit**

```bash
git add index.html world/index.html world-systems/index.html
git commit -m "feat: add World public gateway"
```

---

### Task 3: Migrate the backend-to-frontend projection contract

**Files:**
- Modify: `data/frontend-atlas-bridge.json`
- Modify only where routing metadata requires it: `data/backend-coverage-map.json`, `data/atlas-manifest.json`

**Interfaces:**
- Produces: `public_doors.world = "world/"` as the only fifth primary door.
- Preserves: canonical owners and specialist deep routes.

- [ ] **Step 1: Replace the fifth public-door key**

Change:

```json
"world_map":"world-map/"
```

to:

```json
"world":"world/"
```

- [ ] **Step 2: Reproject the `north` and `world` branches**

Use:

```json
"north": {
  "primary_door": "world",
  "human_route": "north/",
  "archive_route": "explore/#branch=north",
  "static_topic_route": "topics/north/",
  "related_doors": ["philosophy"]
},
"world": {
  "primary_door": "world",
  "human_route": "world/",
  "archive_route": "explore/#branch=world",
  "static_topic_route": "topics/world/",
  "related_doors": ["science", "philosophy"]
}
```

- [ ] **Step 3: Reproject world-facing backend families without changing canonical owners**

For families currently using `"primary_door":"world_map"`, change only the routing key to `"primary_door":"world"`. Keep map-specific `deep_route:"world-map/"` where the specialist map is still the right detailed surface; otherwise preserve existing Explore routes.

Do **not** rename source files or move canonical data.

- [ ] **Step 4: Update coverage/atlas metadata only if they encode the retired primary door**

Search:

```bash
grep -R '"world_map"\|world-map/' data/backend-coverage-map.json data/atlas-manifest.json
```

Change only statements about **primary public projection**. Keep genuine World Map entry points and specialist routes intact.

- [ ] **Step 5: Run projection validation**

```bash
python scripts/validate_public_projection.py
```

Expected: fail only for Politics if it is not yet present, or PASS if Politics has already been transplanted during execution ordering.

- [ ] **Step 6: Commit**

```bash
git add data/frontend-atlas-bridge.json data/backend-coverage-map.json data/atlas-manifest.json
git commit -m "refactor: make World the fifth public domain"
```

---

### Task 4: Update machine discovery and navigation generation

**Files:**
- Modify: `scripts/build_discovery.py`
- Modify only if required by failing tests: `scripts/validate_discovery_projection.py`, `scripts/validate_seo_pipeline.py`

**Interfaces:**
- Consumes: the five-door public architecture.
- Produces: generated discovery pages/machine indexes that identify World, not World Map, as the fifth primary door.

- [ ] **Step 1: Change `PRIMARY_DOORS` in `scripts/build_discovery.py`**

Replace:

```python
("world_map", "World Map", "/world-map/"),
```

with:

```python
("world", "World", "/world/"),
```

Do not remove references to “world systems” in descriptive discovery copy; those describe content, not route ownership.

- [ ] **Step 2: Run discovery/public validators**

```bash
python scripts/validate_discovery_projection.py
python scripts/validate_seo_pipeline.py
python scripts/validate_public_navigation.py
```

Expected: any failures should point to literal old five-door expectations. Update those expectations to `world -> world/` while keeping Map-specific assertions where they are truly map-specific.

- [ ] **Step 3: Build the site locally**

```bash
python scripts/build_site.py
python scripts/build_discovery.py
```

Expected: both commands exit 0 and generated navigation contains World as the fifth primary door.

- [ ] **Step 4: Commit**

```bash
git add scripts/build_discovery.py scripts/validate_discovery_projection.py scripts/validate_seo_pipeline.py scripts/validate_public_navigation.py
git commit -m "build: project World through discovery surfaces"
```

---

### Task 5: Transplant and reconcile the Politics reader from PR #92

**Files:**
- Create from PR #92 content: `app/longform-reader.css`
- Create from PR #92 content: `app/politics-reader.js`
- Create from PR #92 content: `politics/index.html`
- Create from PR #92 content: `politics/politics-manifest.json`
- Create from PR #92 content: `politics/parts/part-01.html`
- Create from PR #92 content: `politics/parts/part-02.html`
- Create from PR #92 content: `politics/parts/part-03.html`
- Create from PR #92 content: `politics/parts/part-04.html`
- Create from PR #92 content: `knowledge/politics/tim-dooley-politics-geopolitics-compendium.json`
- Do **not** transplant PR #92’s homepage/Explore edits unchanged.

**Interfaces:**
- Produces: `/politics/` sibling lens beneath World.
- Preserves: PR #92 provenance/mode ledger and explicit unresolved positions.

- [ ] **Step 1: Copy only the durable Politics files from PR #92 head `70c9f8bb707b8560a7342d54273b7bc59c01a62f`**

Fetch each exact file from that ref and write it onto the fresh feature branch. Exclude the PR’s `index.html` and `explore/index.html` patches because their “Other threads” integration is superseded by the World gateway architecture.

- [ ] **Step 2: Reconcile Politics navigation with World parent ownership**

In `politics/index.html`, include local family navigation:

```html
<nav aria-label="World sections">
  <a href="../world/">World</a>
  <a href="../world-map/">Map</a>
  <a aria-current="page" href="./">Politics</a>
  <a href="../north/">North</a>
  <a href="../world-systems/">Systems</a>
</nav>
```

Keep the Politics TOC and provenance-aware reader body unchanged except for navigation/parent copy needed by the new architecture.

- [ ] **Step 3: Reconcile the Politics reader footer**

In `app/politics-reader.js`, ensure the assembled footer includes `../world/` as the parent domain and retains links to the canonical machine record and Explore. Do not introduce automatic zoom/focus behavior; hash scrolling remains limited to explicit deep-link load behavior already defined by the reader.

- [ ] **Step 4: Run syntax and route checks**

```bash
node --check app/politics-reader.js
python scripts/validate_public_projection.py
```

Expected: PASS for syntax; projection validator should now see all four World specialist routes.

- [ ] **Step 5: Commit**

```bash
git add app/longform-reader.css app/politics-reader.js politics knowledge/politics/tim-dooley-politics-geopolitics-compendium.json
git commit -m "feat: add Politics as a World sibling"
```

---

### Task 6: Add local World-family navigation without rewriting specialist runtimes

**Files:**
- Modify: `north/index.html`
- Modify: `world-map/index.html`
- Modify: `world-systems/index.html`
- Modify: `world/index.html`
- Modify: `politics/index.html`

**Interfaces:**
- Produces: coherent local family navigation `World · Map · Politics · North · Systems`.
- Preserves: specialized World Map application header and all runtime script/bootstrap behavior.

- [ ] **Step 1: Add family navigation to static World-family pages**

Use the same five labels and relative routes on World, Politics, North, and World Systems. Mark the current page with `aria-current="page"`.

- [ ] **Step 2: Add a compact parent/sibling affordance to `world-map/index.html`**

Do not replace the Map application header. Add a minimal menu group or links that provide:

```text
World · Politics · North · Systems
```

Keep existing Home access if useful. Do not alter map controls, camera handlers, bootstrap order, layer registry, compositor, or inspector behavior in this task.

- [ ] **Step 3: Tighten World Map copy**

Change identity copy only where needed so it reads as a spatial/geographic specialist, e.g.:

```text
Map first · countries, geography, spatial relationships, flows, time and evidence
```

and make any broad “World” wording clearly describe map investigation rather than overall public-domain ownership.

- [ ] **Step 4: Run World Map and reader validators**

```bash
python scripts/validate_world_map_browse_performance.py
python scripts/validate_world_map_runtime.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_projection.py
```

Expected: PASS. A failure in a World Map runtime contract means the navigation edit touched more than intended and must be narrowed.

- [ ] **Step 5: Commit**

```bash
git add world/index.html world-systems/index.html politics/index.html north/index.html world-map/index.html
git commit -m "ux: connect World sibling surfaces"
```

---

### Task 7: Integrate the design/spec history and retire the stale Politics PR path

**Files:**
- Add to feature branch: `docs/superpowers/specs/2026-09-13-world-domain-gateway-design.md`
- Add to feature branch: `docs/superpowers/plans/2026-09-13-world-domain-gateway.md`
- PR metadata: supersede/close PR #92 after its durable files are verified on the new branch.

**Interfaces:**
- Produces: one current-main-based implementation branch containing design history and Politics content.

- [ ] **Step 1: Bring the approved spec and plan commits from the design branch into the feature branch**

Preserve both files at their canonical paths.

- [ ] **Step 2: Compare the new branch’s Politics files to PR #92**

The only intended semantic differences should be World-family navigation and parent-domain integration. The political compendium and four content parts should remain substantively preserved.

- [ ] **Step 3: Mark PR #92 superseded only after the new branch contains its durable Politics work**

Update/close PR #92 with a concise explanation that its Politics reader has been reconciled into the World-domain implementation on current main; do not discard its provenance history.

- [ ] **Step 4: Commit any documentation-only reconciliation**

```bash
git add docs/superpowers/specs/2026-09-13-world-domain-gateway-design.md docs/superpowers/plans/2026-09-13-world-domain-gateway.md
git commit -m "docs: preserve World gateway design and plan"
```

---

### Task 8: Run the exact-head repository gate and merge to main

**Files:**
- No intentional source changes unless validation exposes a concrete defect.

**Interfaces:**
- Consumes: complete feature branch.
- Produces: verified merge to `main`.

- [ ] **Step 1: Refresh against current `main` before the final gate**

Fetch current `main`. If it advanced, compare changed paths. Merge/reconcile current main into the feature branch before final CI; never merge a stale exact head.

- [ ] **Step 2: Run focused local validators where possible**

```bash
python scripts/validate_public_projection.py
python scripts/validate_public_navigation.py
python scripts/validate_reader_surfaces.py
python scripts/validate_discovery_projection.py
python scripts/validate_seo_pipeline.py
python scripts/validate_world_map_browse_performance.py
python scripts/validate_world_map_runtime.py
python scripts/build_site.py
python scripts/build_discovery.py
```

All must exit 0.

- [ ] **Step 3: Open a PR from the feature branch to `main` and wait for the repository quality workflow on the exact head**

Required result: all substantive quality-check steps pass. Expected policy/enforcement skips may remain skipped if that is the repository’s established workflow behavior.

- [ ] **Step 4: Review changed files and PR threads**

Confirm:

- only intended World-domain, Politics, routing/discovery, validation, and design/plan files changed;
- no World Map runtime owner was accidentally rewritten;
- no unresolved review thread remains;
- the branch is not behind `main`.

- [ ] **Step 5: Merge with exact-head protection**

Merge only the exact verified PR head. After merge, fetch `main` and confirm its tree contains the verified feature tree plus any deliberate merge-parent history.

- [ ] **Step 6: Post-merge verification**

Confirm on `main`:

- homepage has five doors with World fifth;
- `/world/` exists and links Map, Politics, North, Systems;
- `/world-map/` remains reachable and runtime contracts are unchanged;
- `/politics/`, `/north/`, `/world-systems/` are reachable;
- projection/discovery validators pass on the merged tree.
