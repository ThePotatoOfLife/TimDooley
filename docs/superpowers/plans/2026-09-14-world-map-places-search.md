# World Map Places + Unified Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current country-first World Map into a scale-aware place atlas by adding a bounded sourced city runtime, a unified Places layer, and one search surface for countries, subdivisions, capitals, and major cities.

**Architecture:** Keep the existing MapLibre renderer and country-selection model. Add a generated same-origin city snapshot, a focused lazy `3d-places.js` browser module, and a small pure search core consumed by `3d-search.js`; search may activate existing country/subdivision/place APIs but does not become another spatial data owner. Existing capital rendering is retained only as compatibility input until Places takes over its visual job without duplicate markers.

**Tech Stack:** Python 3 builders/validators, ES modules, vanilla JavaScript, MapLibre GL 6.9, committed GeoJSON/JSON runtimes, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-14-world-map-geographic-enrichment-design.md`

## Global Constraints

- One MapLibre renderer; no second map application.
- Canonical country facts stay in canonical country/entity owners; browser files are projections.
- Browser browsing uses same-origin snapshots; external city APIs are acquisition-time inputs only.
- Missing population is unknown, never numeric zero.
- Only real geographic entities receive coordinates.
- Zoom creates detail; ordinary map browsing must not gain a new toolbar of toggles.
- Initial city runtime remains bounded to at most 5,000 features and 5 MB uncompressed.
- Country selection remains the primary working-set state; subdivision/city selection must not silently mutate it.
- Search results must disambiguate type and parent context.
- Optional Places/Search failure must leave the core country map usable.

---

### Task 1: Pure search contract — RED then GREEN

**Files:**
- Create: `scripts/test_world_map_search.mjs`
- Create: `world-map/3d-search-core.js`

**Interfaces:**
- Produces: `normalizeSearchText(value) -> string`
- Produces: `buildSearchRecords({countries, subdivisions, places}) -> SearchRecord[]`
- Produces: `rankSearchRecords(records, query, limit=12) -> SearchRecord[]`
- `SearchRecord = {id,type,name,parent,code,aliases,display,payload}` where `type` is `country|subdivision|city`.

- [ ] **Step 1: Write the failing Node test**

```js
import assert from 'node:assert/strict';
import {buildSearchRecords, rankSearchRecords} from '../world-map/3d-search-core.js';

const records = buildSearchRecords({
  countries:[{iso3:'GEO',name:'Georgia'},{iso3:'USA',name:'United States'}],
  subdivisions:[{id:'US-CA',name:'California',code:'CA',parent:'United States'}],
  places:[{id:'wd:Q65',name:'Los Angeles',iso3:'USA',admin_region:'California',aliases:['LA']}],
});
assert.equal(rankSearchRecords(records,'Georgia')[0].id,'GEO');
assert.equal(rankSearchRecords(records,'CA')[0].id,'US-CA');
assert.equal(rankSearchRecords(records,'LA')[0].id,'wd:Q65');
assert.match(rankSearchRecords(records,'Los Angeles')[0].display,/City.*California.*United States/);
assert.deepEqual(rankSearchRecords(records,'not-a-place'),[]);
console.log('WORLD MAP SEARCH CORE PASSED');
```

- [ ] **Step 2: Run RED**

Run: `node scripts/test_world_map_search.mjs`
Expected: FAIL because `world-map/3d-search-core.js` does not exist.

- [ ] **Step 3: Implement the minimal pure search core**

Use normalized case-folded tokens, exact id/code/name/alias priority, prefix priority next, substring last, deterministic tie-breaking by type then display name. Do not perform fuzzy edit-distance matching in this wave.

- [ ] **Step 4: Run GREEN**

Run: `node scripts/test_world_map_search.mjs`
Expected: `WORLD MAP SEARCH CORE PASSED`.

- [ ] **Step 5: Commit**

```bash
git add scripts/test_world_map_search.mjs world-map/3d-search-core.js
git commit -m "test: define unified World Map search contract"
```

### Task 2: Bounded major-city runtime

**Files:**
- Create: `scripts/test_world_cities_builder.py`
- Create: `scripts/build_world_cities.py`
- Create: `scripts/validate_world_cities.py`
- Generate: `data/world-cities.geo.json`

**Interfaces:**
- Builder consumes `data/countries/index.json` and `data/world-capitals.geo.json`.
- Optional acquisition input: Wikidata SPARQL during refresh/build only.
- Runtime is a GeoJSON FeatureCollection with stable `properties.id`, `name`, `iso3`, `capital`, `source`, `coordinate_source`, `tier`, `minimum_zoom`, and optional `population`, `population_period`, `population_source`, `admin_region`, `aliases`.

- [ ] **Step 1: Write failing builder tests**

Test a temporary fixture path and monkeypatch the acquisition function so tests do not require network. Assert: 195-country identity validation, capital fallback survives acquisition failure, duplicate IDs fail, noncanonical ISO3 fails, negative/zero-as-missing population is rejected, and output exceeds neither 5,000 features nor 5 MB.

- [ ] **Step 2: Run RED**

Run: `python -m unittest scripts.test_world_cities_builder -v`
Expected: FAIL because builder module does not exist.

- [ ] **Step 3: Implement builder fresh against current main contracts**

Selection policy:
1. all represented national capitals from committed capital snapshot;
2. sourced settlements with population >= 500,000;
3. up to two additional highest-population non-capital settlements per canonical country;
4. merge a Wikidata settlement into an existing capital when country + normalized name or very-close coordinates identify the same place;
5. prefer latest dated population statement; preserve missing dates as missing.

- [ ] **Step 4: Run unit tests GREEN**

Run: `python -m unittest scripts.test_world_cities_builder -v`
Expected: PASS.

- [ ] **Step 5: Generate and validate snapshot**

Run:
```bash
python scripts/build_world_cities.py
python scripts/validate_world_cities.py
```
Expected: valid FeatureCollection, <= 5,000 features, <= 5 MB; acquisition failure is recorded but capitals still yield a valid runtime.

- [ ] **Step 6: Commit**

```bash
git add scripts/test_world_cities_builder.py scripts/build_world_cities.py scripts/validate_world_cities.py data/world-cities.geo.json
git commit -m "feat: add bounded sourced World Map city runtime"
```

### Task 3: Places browser module

**Files:**
- Create: `scripts/validate_world_map_places.py`
- Create: `world-map/3d-places.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-hover.js`

**Interfaces:**
- Produces `window.__potatoAtlasPlaces = {ready, select(id, options), clear(), records(), get selected()}`.
- Emits `potato-atlas-place-select` and `potato-atlas-places-ready`.
- Deep link: `?place=<stable-id>`.
- `3d-hover.js` keeps capital compatibility API but yields capital visual ownership to Places once Places is ready, preventing duplicate capital points.

- [ ] **Step 1: Write the failing structural validator**

Validator must fail until it finds: the city runtime, `3d-places.js`, stable layer ids, `minimum_zoom`-driven visibility, place deep-link handling, place inspector, public API, and lifecycle lazy-load wiring.

- [ ] **Step 2: Run RED**

Run: `python scripts/validate_world_map_places.py`
Expected: FAIL because Places module/wiring is absent.

- [ ] **Step 3: Implement Places module**

Add one GeoJSON source and bounded point/label layers. Use `minimum_zoom` via MapLibre expressions; do not create one layer per city tier. Clicking a place fits/eases to the real coordinates, opens a compact inspector, sets `place=`, and does not change country working selection. Capital styling may differ from non-capital styling within the same source.

- [ ] **Step 4: Add lazy lifecycle wiring**

Load Places when the map reaches regional scale, when `place=` is present, or when Search requests it. Failure remains nonfatal.

- [ ] **Step 5: Remove duplicate capital visuals after Places readiness**

Keep the old capital API/data for compatibility and country-focus helpers, but hide its point/label layers when Places reports ready.

- [ ] **Step 6: Run GREEN**

Run:
```bash
python scripts/validate_world_map_places.py
python scripts/validate_world_map_3d.py
```
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate_world_map_places.py world-map/3d-places.js world-map/3d-panel-lifecycle.js world-map/3d-hover.js
git commit -m "feat: add progressive World Map places layer"
```

### Task 4: Unified country / subdivision / city search

**Files:**
- Create: `scripts/validate_world_map_search.py`
- Create: `world-map/3d-search.js`
- Modify: `world-map/index.html`
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**
- Produces `window.__potatoAtlasSearch = {ready, query(text, limit), activate(record), refreshSuggestions(text)}`.
- Consumes `window.goCountry(code)`, `window.__potatoAtlasSubdivisions.select(id)`, `window.__potatoAtlasPlaces.select(id)`.
- Existing input remains `#search`; existing datalist remains `#country-list` for compatibility but becomes a mixed place suggestion list.

- [ ] **Step 1: Write failing search integration validator**

Assert that the placeholder/ARIA copy says places rather than countries, bootstrap loads Search, Search imports the pure search core, exact search activation dispatches by type, search can request Subdivisions/Places lazy modules, and the old core Enter handler is neutralized through capture-phase handling rather than deleting country compatibility logic from `3d-app.js`.

- [ ] **Step 2: Run RED**

Run: `python scripts/validate_world_map_search.py`
Expected: FAIL because unified search controller is absent.

- [ ] **Step 3: Implement controller**

On first focus/input, load city runtime and implemented subdivision partition metadata, build mixed records, and populate at most 12 suggestions. Capture Enter before the legacy core handler; when a unified match exists call `stopImmediatePropagation()` and activate it. If no unified match exists, allow the legacy country handler to run unchanged.

- [ ] **Step 4: Update search copy**

`placeholder="Find country, state or city…"` and `aria-label="Find country, subdivision or city"`.

- [ ] **Step 5: Run GREEN**

Run:
```bash
node scripts/test_world_map_search.mjs
python scripts/validate_world_map_search.py
python scripts/validate_world_map_places.py
python scripts/validate_world_map_subdivisions.py
python scripts/validate_world_map_3d.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_world_map_search.py world-map/3d-search.js world-map/index.html world-map/3d-bootstrap.js
git commit -m "feat: unify World Map country subdivision and city search"
```

### Task 5: Runtime contract, deployment checks, and regression gate

**Files:**
- Modify: `data/world-map-3d-runtime.json`
- Modify: `.github/workflows/quality-checks.yml` if the new validators are not already discovered automatically.
- Modify: `.github/workflows/pages.yml` only if generated/runtime copy rules require explicit inclusion.

**Interfaces:**
- Runtime contract records Places and Search as implemented, city/subdivision deep links, and the transition from capital-only to unified Places.

- [ ] **Step 1: Write/extend validator assertions first**

Require runtime status to declare `places` and `unified_search`, and require deployment workflows to ship `data/world-cities.geo.json` and both browser modules.

- [ ] **Step 2: Run RED**

Run the focused validators and confirm they fail on missing runtime/workflow declarations.

- [ ] **Step 3: Update runtime/workflow declarations minimally**

Do not rewrite unrelated roadmap text; remove only next-priority statements made obsolete by this implementation.

- [ ] **Step 4: Run the full local quality slice**

```bash
node scripts/test_world_map_search.mjs
python -m unittest scripts.test_world_cities_builder -v
python scripts/validate_world_cities.py
python scripts/validate_world_map_places.py
python scripts/validate_world_map_search.py
python scripts/validate_world_map_subdivisions.py
python scripts/validate_world_map_3d.py
python scripts/validate_site_shell.py
```
Expected: all PASS with no warnings treated as validation failures.

- [ ] **Step 5: Commit**

```bash
git add data/world-map-3d-runtime.json .github/workflows/quality-checks.yml .github/workflows/pages.yml
git commit -m "docs: register World Map places and unified search runtime"
```

### Task 6: Branch verification and PR gate

- [ ] **Step 1: Compare feature branch to current `main`** and verify only intended map/runtime/docs files changed.
- [ ] **Step 2: Confirm `main` did not advance underneath the branch; if it did, rebase/reconcile before review.**
- [ ] **Step 3: Open a PR rather than merging historical `atlas-metrics-cities-search`.**
- [ ] **Step 4: Require Pages + repository quality checks to pass on the PR/head SHA before merge.**
- [ ] **Step 5: Perform a final manual browser smoke check:** country search, California search, Los Angeles search, city click, city deep link, subdivision deep link, terrain toggle, ordinary country selection, and no duplicate capital markers.
