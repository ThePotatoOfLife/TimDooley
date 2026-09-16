# Public Rooms Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Culture, History, Politics/Geopolitics, Law, Economy and World Systems directly discoverable from the public homepage while preserving exactly five primary Doors and all existing canonical knowledge ownership.

**Architecture:** Add a presentation-only Rooms layer between the five primary Doors and the Explore/archive layer. New `/rooms/`, `/history/`, `/law/`, and `/economy/` routes are thin guide pages; existing Culture, Politics, World Systems, World Map, North, Timeline and Sources routes remain authoritative human surfaces. House/public-projection registries describe routing only and do not gain knowledge ownership.

**Tech Stack:** Static HTML, JSON route registries, Python validation scripts, GitHub Pages build pipeline.

**Spec:** `docs/superpowers/specs/2026-09-16-public-rooms-navigation-design.md`

## Global Constraints

- Keep `primary_gateway_ids` exactly `tim`, `religion`, `philosophy`, `science`, `world`.
- Keep the homepage primary `.sections` navigation at exactly those five routes and in that order.
- Do not duplicate canonical law, economy, history, culture, politics or world-system data into guide pages.
- New guide pages must link to evidence and/or Explore for deeper inspection.
- Preserve distinctions among documented facts, project interpretation, mythology, political statements and legal claims.
- Use TDD: focused Rooms validation must fail before production navigation changes and pass afterward.

---

### Task 1: Lock the Rooms navigation contract

**Files:**
- Create: `scripts/validate_public_rooms.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: `index.html`, `world/index.html`, `data/house/public-surfaces.json`, `knowledge/research/potato-house-master/public-route-topology.json`, `data/frontend-atlas-bridge.json`
- Produces: one focused command, `python scripts/validate_public_rooms.py`, that fails whenever the Rooms middle-floor contract drifts.

- [ ] **Step 1: Write the failing validator**

Validate all of the following:

```python
EXPECTED_PRIMARY = [
    "tim-dooley/",
    "religion/",
    "philosophy/",
    "science/",
    "world/",
]

REQUIRED_HOME_ROOM_LINKS = {
    "context/culture/": "Culture",
    "history/": "History",
    "politics/": "Politics",
    "law/": "Law",
    "economy/": "Economy",
    "world-systems/": "World Systems",
    "rooms/": "All Rooms",
}

REQUIRED_SURFACES = {
    "rooms": "/rooms/",
    "history": "/history/",
    "law": "/law/",
    "economy": "/economy/",
}
```

The validator must also require the World page to link `../history/`, `../context/culture/`, `../politics/`, `../law/`, `../economy/`, `../world-systems/`, `../world-map/`, `../north/`, and `../context/source-authority/`; require each new source page to exist and contain its reader-surface marker plus links to evidence and Explore; require registry/topology convergence for the four new surface IDs; and require an explicit secondary Rooms projection in `data/frontend-atlas-bridge.json` while keeping exactly five `public_doors`.

- [ ] **Step 2: Run the validator and confirm RED**

Run in CI through a draft PR or locally when available:

```bash
python scripts/validate_public_rooms.py
```

Expected: FAIL because `/rooms/`, `/history/`, `/law/`, `/economy/` and the homepage Rooms corridor do not yet exist.

- [ ] **Step 3: Add the focused validator to the quality workflow**

Add immediately after the Potato House governance validation block:

```yaml
      - name: Validate public Rooms navigation
        run: python scripts/validate_public_rooms.py
```

- [ ] **Step 4: Commit the RED contract**

```bash
git add scripts/validate_public_rooms.py .github/workflows/quality-checks.yml
git commit -m "test: define public Rooms navigation contract"
```

### Task 2: Add the homepage Rooms corridor and Rooms directory

**Files:**
- Modify: `index.html`
- Create: `rooms/index.html`

**Interfaces:**
- Consumes: the existing five `.sections` Doors and mature specialist routes.
- Produces: a distinct `rooms-corridor` on Home and a human-readable `/rooms/` middle-floor directory.

- [ ] **Step 1: Add the smallest homepage corridor that satisfies the validator**

Keep `.sections` untouched. Add a separate section after it with heading `Explore the Rooms` and links to Culture & Society, History & Time, Politics & Geopolitics, Law & Justice, Economy & Finance, World Systems, Sources & Evidence and All Rooms.

- [ ] **Step 2: Create `rooms/index.html`**

Use `app/site-system.css`; identify the page with `data-reader-surface="rooms"`; explain that Rooms cross-cut the five Doors and do not own canonical facts. Link at minimum to Culture, History, Politics, Law, Economy, World Systems, World Map, North, Sources, Timeline, Works, Bible Comparison, Science, Home and Explore.

- [ ] **Step 3: Run focused validation**

```bash
python scripts/validate_public_rooms.py
```

Expected: still FAIL only for missing History/Law/Economy pages and registry/projection wiring.

- [ ] **Step 4: Commit**

```bash
git add index.html rooms/index.html
git commit -m "feat: expose public Rooms directory"
```

### Task 3: Add thin History, Law and Economy guide pages

**Files:**
- Create: `history/index.html`
- Create: `law/index.html`
- Create: `economy/index.html`

**Interfaces:**
- Produces stable human routes only; no canonical data copies.

- [ ] **Step 1: Create History & Time guide**

Use `data-reader-surface="history"`. Route to Timeline, Explore, Politics, Culture, Religion/Bible and Sources. Include explicit text separating historical occurrence, later interpretation and project mythology.

- [ ] **Step 2: Create Law & Justice guide**

Use `data-reader-surface="law"`. Cover constitutions/legislation; rights/duties/prohibitions; ministries/regulators/courts/prosecutors/ombudsmen; enforcement/jurisprudence; constitutional review/treaties/cross-border law; evidence/procedure/due process/accountability. Link World Systems, Politics, Interpretive Justice, Explore and Sources. State that project claims and reconstructions are not automatically established legal findings.

- [ ] **Step 3: Create Economy & Finance guide**

Use `data-reader-surface="economy"`. Cover public finance/debt; banking/capital markets; ownership/production; trade/value chains; energy/infrastructure; labour/skills; dependencies/resilience; North/European systems. Link World Systems, World Map, North, Explore and Sources. State that missing values remain unknown and the guide does not create synthetic scores.

- [ ] **Step 4: Run focused validation**

```bash
python scripts/validate_public_rooms.py
```

Expected: remaining failures are registry/projection and World gateway wiring only.

- [ ] **Step 5: Commit**

```bash
git add history/index.html law/index.html economy/index.html
git commit -m "feat: add History Law and Economy guide rooms"
```

### Task 4: Register the new surfaces and projection map

**Files:**
- Modify: `data/house/public-surfaces.json`
- Modify: `knowledge/research/potato-house-master/public-route-topology.json`
- Modify: `data/frontend-atlas-bridge.json`
- Modify: `scripts/validate_house_governance.py`

**Interfaces:**
- Produces registered active route identities for `rooms`, `history`, `law`, `economy` while leaving knowledge ownership false.

- [ ] **Step 1: Register the four active public surfaces**

Add:

```json
{"id":"rooms","route":"/rooms/","canonical_route":"/rooms/","surface_type":"guide","title":"Rooms","primary_parent":"home","primary_room_ids":["potatoverse-canon","archive-sources","time-history","traditions-texts","science-formal-models","life-body","world-systems","culture-information","works","research-lab"],"status":"active","visibility":"secondary","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
```

```json
{"id":"history","route":"/history/","canonical_route":"/history/","surface_type":"guide","title":"History & Time","primary_parent":"home","primary_room_ids":["time-history","archive-sources","culture-information","world-systems"],"status":"active","visibility":"specialist","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
```

```json
{"id":"law","route":"/law/","canonical_route":"/law/","surface_type":"guide","title":"Law & Justice","primary_parent":"world","primary_room_ids":["world-systems","archive-sources","culture-information","research-lab"],"status":"active","visibility":"specialist","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
```

```json
{"id":"economy","route":"/economy/","canonical_route":"/economy/","surface_type":"guide","title":"Economy & Finance","primary_parent":"world","primary_room_ids":["world-systems","archive-sources","research-lab"],"status":"active","visibility":"specialist","primary_navigation":false,"is_view":true,"knowledge_owner":false,"legacy_routes":[]}
```

Add `rooms` to `secondary_global_ids`.

- [ ] **Step 2: Add matching topology rows in the same active-surface order**

Each topology row must mirror canonical route, surface type and room IDs; `rooms` and `history` use `primary_hub_id:null`; `law` and `economy` use `primary_hub_id:"world"`; all are current and have no compatibility routes.

- [ ] **Step 3: Extend the frontend projection contract**

Add a `public_rooms` object without changing `public_doors`:

```json
"public_rooms": {
  "culture":"context/culture/",
  "history":"history/",
  "politics":"politics/",
  "law":"law/",
  "economy":"economy/",
  "world_systems":"world-systems/",
  "sources":"context/source-authority/",
  "rooms":"rooms/"
}
```

Add an integrity requirement stating that Rooms are secondary subject corridors and never additional primary Doors.

- [ ] **Step 4: Extend House governance requirements**

Add `rooms`, `history`, `law`, `economy` with the exact canonical routes to `REQUIRED_SURFACES`, and extend `HOME_CORRIDOR` with the Rooms markers while leaving the primary gateway-route assertion unchanged.

- [ ] **Step 5: Run focused and House validators**

```bash
python scripts/validate_public_rooms.py
python scripts/validate_house_governance.py
python scripts/validate_house_topology.py
python scripts/validate_house_compatibility.py
python scripts/validate_public_projection.py
```

Expected: Rooms/House/projection checks pass; World gateway may remain the last focused failure until Task 5.

- [ ] **Step 6: Commit**

```bash
git add data/house/public-surfaces.json knowledge/research/potato-house-master/public-route-topology.json data/frontend-atlas-bridge.json scripts/validate_house_governance.py
git commit -m "feat: register public Rooms projection"
```

### Task 5: Expand World as a subject gateway

**Files:**
- Modify: `world/index.html`
- Modify: `world-systems/index.html`

**Interfaces:**
- Produces direct World-level navigation into Law, Economy, Culture and History alongside existing Map, Politics, North and Systems.

- [ ] **Step 1: Expand World lenses**

Keep World as the fifth Door. Add visible routes for Law & Justice, Economy & Finance, Culture & Society, History & Time and Sources & Evidence. Preserve the existing Map, Politics, North and World Systems routes.

- [ ] **Step 2: Improve World Systems exits**

Route Governance toward `/law/`, Economy & Finance toward `/economy/`, Labour & Society toward `/context/culture/`, while retaining Explore links for deeper record-level browsing.

- [ ] **Step 3: Run focused validator**

```bash
python scripts/validate_public_rooms.py
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add world/index.html world-systems/index.html
git commit -m "feat: connect World to public subject rooms"
```

### Task 6: Verify build and full repository quality

**Files:**
- No production changes unless a validator exposes a real compatibility issue.

**Interfaces:**
- Produces exact-head evidence for merge readiness.

- [ ] **Step 1: Run focused validations**

```bash
python scripts/validate_public_rooms.py
python scripts/validate_house_governance.py
python scripts/validate_house_topology.py
python scripts/validate_house_compatibility.py
python scripts/validate_house_world_routing.py
python scripts/validate_public_projection.py
python scripts/validate_generated_navigation.py
```

- [ ] **Step 2: Build and validate public output**

```bash
python scripts/build_site.py
python scripts/validate_public_navigation.py
python scripts/validate_site_shell.py
```

Confirm `_site/rooms/index.html`, `_site/history/index.html`, `_site/law/index.html`, and `_site/economy/index.html` exist.

- [ ] **Step 3: Push exact head through the full GitHub Actions `Repository quality checks` workflow**

Require all workflow steps to pass on the final PR head SHA. Do not rely on earlier runs.

- [ ] **Step 4: Compare PR head against current `main` before merge**

If `main` advanced, reconcile the branch with the new `main` and rerun full verification on the new exact head.

- [ ] **Step 5: Merge only with `expected_head_sha` set to the verified final head**

Use a normal merge commit unless repository state requires otherwise.
