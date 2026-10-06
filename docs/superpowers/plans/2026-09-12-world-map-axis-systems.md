# World Map Axis & Systems Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved World Map Axis/system architecture: defensible N/W/E/S profiles, current regional institutions, functional chains, reference figures, shared runtime consumption, and a persistent Flat ↔ Globe control without expanding the normal UI into a toolbox.

**Architecture:** Keep the existing layer registry, generated `world-map-data-runtime.json`, compositor, country card, and centered world bar. Add focused canonical owners for project Axis profiles and functional chains, extend the existing institutional-membership owner, project all of them into the current runtime, then make every browser consumer use that same runtime. Axis interpretation remains distinct from observed institutional facts.

**Tech Stack:** Static JSON data, Python build/validation scripts, vanilla ES modules, MapLibre GL JS, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-world-map-axis-systems-design.md`

## Global Constraints

- The fundamental object is the relationship, not the country in isolation.
- North / West / East / South are project-interpretive fields, never sovereignty or legal command.
- Countries may overlap directions and may remain unresolved.
- Missing data is unknown, never zero.
- Real offices and project reference roles remain separate.
- No portraits, crowns, hierarchy trees, subordinate language, or fake command structure in the ordinary map.
- Existing normal top UI remains shallow: Axis buttons, Groups, Religion, Stats, Relations, projection, reset/query state.
- Default map projection is flat/Mercator; `projection=globe` is opt-in and persistent in the URL.
- Every canonical country must resolve to a runtime Axis profile; unresolved is valid.
- TDD: validator first, observe failure, then implement.

---

### Task 1: Add the failing Axis/systems contract validator

**Files:**
- Create: `scripts/validate_world_axis_systems.py`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: repository files directly from `ROOT`.
- Produces: exit code 0 only when Axis source/runtime/UI contracts are all satisfied.

- [ ] **Step 1: Write the validator before production data exists**

The validator must require:

```python
AXES = {"north", "west", "east", "south"}
ROLES = {"primary", "secondary", "bridge", "frontier", "external", "shared", "unresolved"}
CONFIDENCE = {"high", "medium", "low"}
REQUIRED_GROUP_COUNTS = {
    "asean": (11, 11),
    "african-union": (55, 54),
    "sadc": (16, 16),
    "pacific-islands-forum": (18, 14),
    "sco": (10, 10),
    "usmca": (3, 3),
    "mercosur": (5, 5),
    "gcc": (6, 6),
    "arctic-council": (8, 8),
}
```

Validate all of these behaviors:

```python
assert axis_source["default_profile"]["status"] == "unresolved"
assert runtime["country_count"] == 195
assert len(runtime["axis"]["countries"]) == 195
assert set(runtime["axis"]["memberships"]) == AXES
assert runtime["chains"]
assert runtime["reference_figures"]
assert "projection" in world_bar_text
assert "setProjection" in world_bar_text
assert "source_owner" in layer_registry_text
assert "world-axis-profiles.json" not in compositor_text  # compositor consumes runtime, not a second fetch path
```

Also reject `subordinate`, `rules the bloc`, `commands the bloc`, `owns the bloc` in browser-facing Axis copy.

- [ ] **Step 2: Wire it into CI**

Add before the canonical World Map runtime validation:

```yaml
- name: Validate World Map Axis and systems
  run: python scripts/validate_world_axis_systems.py
```

- [ ] **Step 3: Commit the red test gate**

Commit message:

```text
test(world-map): define axis and systems contract
```

- [ ] **Step 4: Verify RED through GitHub Actions**

Expected: the new step fails because `data/world-axis-profiles.json`, `data/world-system-chains.json`, runtime Axis/chains/reference data, and the new projection control do not exist yet.

---

### Task 2: Add canonical Axis profiles, reference figures, regional groups, and functional chains

**Files:**
- Create: `data/world-axis-profiles.json`
- Create: `data/world-system-chains.json`
- Modify: `data/world-institution-memberships.json`

**Interfaces:**
- Produces: `profiles`, `axes`, `reference_figures`, `center_junction`, `chains`, and expanded official `groups`.
- Later tasks consume these exact keys.

- [ ] **Step 1: Create `world-axis-profiles.json`**

Required shape:

```json
{
  "version": "1.0.0",
  "updated": "2026-09-12",
  "epistemic_type": "project_interpretive",
  "default_profile": {"status": "unresolved", "orientations": []},
  "axes": {
    "north": {"label": "North", "color": "#79D6FF"},
    "west": {"label": "West", "color": "#14558A"},
    "east": {"label": "East", "color": "#C94F32"},
    "south": {"label": "South", "color": "#E8C84A"}
  },
  "profiles": {},
  "reference_figures": [],
  "center_junction": {}
}
```

Encode only defensible recovered classifications. Use `unresolved` rather than forcing ambiguous countries. Strong coverage must include:

- North spine: CAN, DNK, ISL, NOR, SWE, FIN, DEU, NLD, BEL, FRA, ESP, PRT, ITA, GRC, IRL, EST, UKR, TUR.
- North variable/frontier/shared cases: GBR, RUS, AUS.
- West American field: USA, MEX, Central America, Caribbean sovereign states, all sovereign South American states; CAN as overlap; ISR; SAU project overlap.
- East explicit/recovered: CHN, RUS, IND, PAK, VNM, IRN, MNG, PRK, AFG, LAO, KHM, MMR, Central Asian sovereign states; BRICS members/partners only where the project reading is explicitly preserved as secondary/bridge rather than inferred as ideological unity.
- South: AUS, NZL, PNG, Pacific sovereign states, and defensible Southern African / Indian Ocean states; ZAF may carry South primary + East secondary.
- Center junction metadata: IRQ, ISR, IRN, SAU.

Reference figures must include real office, project Axis role, as-of date, and source URL for Carney, von der Leyen, Xi, Putin, Modi, the U.S. President, Netanyahu, Albanese, Luxon, Marape and Ramaphosa. Tim Dooley's spiritual role belongs only in a `project_cosmology` metadata block with an explicit non-governmental boundary.

- [ ] **Step 2: Extend `world-institution-memberships.json`**

Add:

```text
ASEAN — 11 canonical country members
African Union — official 55; 54 canonical-195 polygons + SADR/Western Sahara metadata
SADC — 16
Pacific Islands Forum — official 18; 14 canonical-195 country polygons + Cook Islands/Niue/French Polynesia/New Caledonia metadata
SCO — 10
USMCA — 3
MERCOSUR — 5 current states parties; Venezuela recorded separately as suspended
GCC — 6
Arctic Council — 8 states
```

Every group records `as_of`, `source`, `source_url`, `members`, and when necessary `non_canonical_members` / `suspended_members` / `official_member_count`.

- [ ] **Step 3: Create `world-system-chains.json`**

Seed IDs:

```text
arctic
north-atlantic
baltic
northern-energy
european-industrial
eastern-security
european-strategic-autonomy
eurasian-interface
blue-pacific
southern-african
```

Each entry has `label`, `epistemic_type`, `members`, `systems`, `description`, `source_note`, and optional `gateways`.

Do not expose these as ordinary top-bar controls yet.

- [ ] **Step 4: Commit canonical data**

Commit message:

```text
data(world-map): add axis profiles and world-system chains
```

---

### Task 3: Project Axis, groups, reference figures, and chains into the existing runtime

**Files:**
- Modify: `scripts/build_world_map_runtime.py`
- Modify: `scripts/validate_world_map_data_runtime.py`
- Generated/updated by build: `data/world-map-data-runtime.json`

**Interfaces:**
- Produces runtime keys:

```python
runtime["axis"] = {
    "axes": {...},
    "memberships": {"north": [...], "west": [...], "east": [...], "south": [...]},
    "countries": {"ISO3": {...}}
}
runtime["reference_figures"] = [...]
runtime["chains"] = {...}
```

- [ ] **Step 1: Extend generator tests/contracts before generator implementation**

Add assertions to `validate_world_map_data_runtime.py` requiring the runtime keys above and expanded group membership metadata.

- [ ] **Step 2: Build all 195 runtime Axis country profiles**

Algorithm:

```python
for canonical_country in countries:
    code = canonical_country["iso3"]
    source = profiles.get(code, default_profile)
    runtime_axis_countries[code] = normalized_profile(source)
```

Ordinary Axis memberships include only roles:

```python
{"primary", "secondary", "bridge", "shared"}
```

Do not include `frontier`, `external`, or `unresolved` in ordinary polygon membership.

- [ ] **Step 3: Project canonical group metadata and chains**

Keep current metric behavior unchanged. Carry through official member counts and non-canonical members as metadata while `members` remains renderable ISO3 polygons.

- [ ] **Step 4: Build runtime and commit**

Commit message:

```text
feat(world-map): project axis and chains into runtime
```

---

### Task 4: Make registry and compositor consume runtime Axis membership

**Files:**
- Modify: `data/world-map-layer-registry.json`
- Modify: `world-map/3d-compositor.js`

**Interfaces:**
- `window.__potatoAtlasDataRuntime.members(id)` continues serving empirical groups.
- Add:

```js
axisMembers(axisId)
axisProfile(code)
referenceFigures(axisId)
chainsForCountry(code)
chain(chainId)
```

- [ ] **Step 1: Promote new official group entries**

Promote planned group entries where present and add new entries for SADC, Pacific Islands Forum and Arctic Council. Keep them in the single existing `Groups` menu.

- [ ] **Step 2: Point Axis entries to runtime-backed ownership**

Each Axis registry entry must carry:

```json
"source_owner": "data/world-map-data-runtime.json",
"runtime_axis": "north"
```

and equivalents for west/east/south.

- [ ] **Step 3: Replace recursive Axis scraping in compositor**

`membershipFor(entry)` resolves `entry.runtime_axis` from runtime `axis.memberships` and no longer recursively collects arbitrary arrays from `world-relational-map.json` for Axis layers.

- [ ] **Step 4: Expose the compact runtime API**

Add the five functions above to `window.__potatoAtlasDataRuntime`.

- [ ] **Step 5: Commit**

Commit message:

```text
feat(world-map): render axis from canonical runtime
```

---

### Task 5: Enrich the country card without turning it into an encyclopedia

**Files:**
- Modify: `world-map/3d-country-card.js`

**Interfaces:**
- Consumes: `axisProfile(code)`, `chainsForCountry(code)`, existing membership/metric runtime APIs.

- [ ] **Step 1: Add compact orientation summary**

For the active country, render at most the first three orientations in the compact card using language such as:

```text
North · primary
West · secondary
East · bridge
```

When none exist, show nothing rather than `Unresolved` as a noisy badge.

- [ ] **Step 2: Add compact functional-chain context**

Show at most two relevant chain labels in the deeper/context section, with `+N` when more exist.

- [ ] **Step 3: Keep reference figures contextual**

Only surface a reference figure when the selected country's Axis context makes it directly relevant. Display real office first and project role second. No hierarchy language.

- [ ] **Step 4: Commit**

Commit message:

```text
feat(world-map): add axis and chain country context
```

---

### Task 6: Add the persistent Flat ↔ Globe inversion control

**Files:**
- Modify: `world-map/3d-world-bar.js`
- Modify if required by shell contract: `scripts/validate_world_map_ui.py`

**Interfaces:**
- URL parameter: `projection=flat|globe`
- Browser API:

```js
window.__potatoAtlasProjection = {
  get(),
  set(mode),
  toggle()
}
```

- [ ] **Step 1: Parse projection state**

Use:

```js
const url = new URL(location.href);
let projectionMode = url.searchParams.get('projection') === 'globe' ? 'globe' : 'flat';
```

- [ ] **Step 2: Apply projection to the existing map**

Use:

```js
map.setProjection({ type: projectionMode === 'globe' ? 'globe' : 'mercator' });
```

Do not create a second map instance.

- [ ] **Step 3: Add one button to the centered bar**

Use a single compact control with an action-oriented title/aria label. When flat is active the control offers Globe; when globe is active it offers Flat. Update its visual state/icon/text on each toggle.

- [ ] **Step 4: Persist without disturbing existing layer/query URL state**

Use `history.replaceState` with the current URL and only change the `projection` parameter.

- [ ] **Step 5: Commit**

Commit message:

```text
feat(world-map): add flat globe projection toggle
```

---

### Task 7: Green verification, build, and PR integration

**Files:**
- Modify only if verification reveals contract drift.

**Interfaces:**
- Exact branch head must pass repository quality checks.

- [ ] **Step 1: Run/observe Axis validator GREEN**

Expected: `Validate World Map Axis and systems` passes.

- [ ] **Step 2: Verify existing World Map contracts remain green**

Expected passing steps include:

```text
Validate World Map data runtime
Validate canonical World Map runtime
Validate World Map UI shell
Validate JavaScript syntax
Build public site
```

- [ ] **Step 3: Confirm PR #51 still targets `main` and remains mergeable**

If concurrent changes moved `main`, verify mergeability and do not overwrite unrelated work.

- [ ] **Step 4: Update PR #51 description**

Add the Axis/systems, expanded institutions, functional chains, and Flat/Globe implementation to the PR summary.

- [ ] **Step 5: Report exact head SHA and exact CI result**

Do not claim completion from local reasoning alone.
