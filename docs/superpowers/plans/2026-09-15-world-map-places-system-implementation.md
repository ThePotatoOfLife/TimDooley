# World Map Places System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a scale-aware global Places system with capitals, major cities and towns, lazy country detail, typed right-panel inspection, unified country/place search, and correct integration with subdivision and map-state behavior.

**Architecture:** Generate same-origin GeoNames-backed place snapshots at build time, merge the existing capital snapshot, load only a bounded global-major layer initially, and fetch country detail partitions on demand. `world-map/3d-places.js` owns place rendering/selection/inspection; `world-map/3d-search.js` owns mixed country/place search; existing country, subdivision, infrastructure, render-stack and map-state owners remain authoritative for their domains.

**Tech Stack:** Python 3 build/validation scripts, GeoJSON/JSON snapshots, MapLibre GL JS 6.9, browser ES modules, existing GitHub Actions repository-quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-15-world-map-places-system-design.md`

## Global Constraints

- No live GeoNames or Wikidata browser dependency.
- GeoNames attribution must remain visible and its CC BY 4.0 license preserved.
- Population observation period, source modification date and dataset refresh date must remain distinct.
- Missing population is unknown, never numeric zero.
- The existing capital snapshot must converge into Places rather than render duplicate capital markers.
- Initial global geometry must remain bounded; country detail loads lazily.
- Place selection must not mutate the analytical country working set.
- Existing sacred/spatial/infrastructure click handling keeps precedence over country fallback.
- No new `MutationObserver`, `setInterval` or polling in Places/Search.
- Subdivision statistics should use the canonical right inspector rather than keep a competing floating card.
- Existing country/entity ownership, Physical ownership and infrastructure ownership remain unchanged.

---

### Task 1: Lock the RED Places contract

**Files:**
- Create: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_map_ui_layout.py`
- Test: `scripts/validate_world_places.py`

**Interfaces:**
- Consumes: approved spec paths and existing World Map files.
- Produces: one validator that later tasks must satisfy and that runs through the current UI-layout/repository-quality validation chain.

- [ ] **Step 1: Write the failing validator**

Require these artifacts/tokens before any production implementation exists:

```python
ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data/world-places/index.json"
MAJOR = ROOT / "data/world-places/global-major.geo.json"
PLACES = ROOT / "world-map/3d-places.js"
SEARCH = ROOT / "world-map/3d-search.js"
MAP_STATE = ROOT / "world-map/3d-map-state.js"
SUBDIVISIONS = ROOT / "world-map/3d-subdivisions.js"

required_places_tokens = (
    "__potatoAtlasPlaces",
    "atlas-places-major-points",
    "atlas-places-major-labels",
    "atlas-places-detail-points",
    "atlas-places-detail-labels",
    "context-network",
    "place=",
    "__potatoAtlasOverlayHandled",
    "Open country",
)
required_search_tokens = (
    "__potatoAtlasSearch",
    "Country",
    "Capital",
    "City",
    "Town",
)
```

Validate data when present:

```python
assert index["license"] == "CC BY 4.0"
assert "GeoNames" in index["attribution"]
assert major["type"] == "FeatureCollection"
assert len(major["features"]) <= 5000
assert MAJOR.stat().st_size <= 5 * 1024 * 1024
```

Per feature require stable id/name/country/point coordinates and reject `population == 0` when the record marks population unknown.

Also require `3d-subdivisions.js` to render through `#panel` and reject creation of `atlasSubdivisionCard`.

- [ ] **Step 2: Chain the validator into current World Map CI**

In `scripts/validate_world_map_ui_layout.py`, run `validate_world_places.py` after render-stack/map-state validation so a failure appears at the existing World Map UI-layout gate.

- [ ] **Step 3: Push the validator-only head and verify RED**

Expected repository-quality result: failure at `Validate World Map UI layout`; all earlier unrelated steps remain green.

- [ ] **Step 4: Commit**

```bash
git add scripts/validate_world_places.py scripts/validate_world_map_ui_layout.py
git commit -m "test(world-map): define places system contract"
```

---

### Task 2: Build the GeoNames + capital snapshot pipeline

**Files:**
- Create: `scripts/build_world_places.py`
- Create: `tests/fixtures/world-places/geonames-cities-sample.txt`
- Create: `tests/fixtures/world-places/capitals-sample.geo.json`
- Test/Modify: `scripts/validate_world_places.py`

**Interfaces:**
- Consumes: GeoNames `cities5000` tab-separated records and existing `data/world-capitals.geo.json`.
- Produces: normalized place records and generated `index.json`, `global-major.geo.json`, country GeoJSON partitions.

- [ ] **Step 1: Add fixture records and failing builder assertions**

Fixture must include at least:

```text
Copenhagen / DK / populated place / population
Aarhus / DK / populated place / population
Berlin / DE / national capital
Springfield-like duplicate-name examples in different parents
one record with population 0 to verify unknown handling
```

Write a focused builder test mode or pure helper assertions covering normalization, ISO2→ISO3 mapping, stable `gn:<id>` ids and deduplication.

- [ ] **Step 2: Implement parser and normalized record builder**

Core helpers:

```python
def parse_geonames_line(line: str) -> dict: ...
def normalize_place(row: dict, iso2_to_iso3: dict[str, str]) -> dict: ...
def merge_capitals(places: list[dict], capitals: dict) -> list[dict]: ...
def importance_tier(place: dict) -> int: ...
def build_outputs(places: list[dict], out_dir: Path) -> None: ...
```

Population rule:

```python
population_raw = int(row["population"] or 0)
record["population"] = population_raw if population_raw > 0 else None
record["population_period"] = None
```

Do not manufacture an observation year.

- [ ] **Step 3: Merge existing capitals without duplicates**

Match in this order:

```text
explicit shared source id/QID when present
country + normalized name + coordinate proximity
otherwise retain capital as a distinct compatibility record
```

A merged record must retain `is_national_capital=true` and capital provenance.

- [ ] **Step 4: Generate bounded global-major selection**

Selection:

```python
is_major = (
    place["is_national_capital"]
    or (place["population"] is not None and place["population"] >= 500_000)
    or place["importance_tier"] == 1
)
```

Add up to two high-population places per ISO3 when needed for useful coverage while preserving the 5,000-feature/5-MB hard gate.

- [ ] **Step 5: Generate country partitions and index metadata**

Index shape:

```json
{
  "schema_version": "1.0.0",
  "source": "GeoNames cities5000",
  "license": "CC BY 4.0",
  "attribution": "GeoNames",
  "generated_at": "...",
  "global_major": {"path": "global-major.geo.json", "count": 0, "bytes": 0},
  "countries": {
    "DNK": {"path": "countries/DNK.geo.json", "count": 0, "bytes": 0}
  }
}
```

- [ ] **Step 6: Run fixture validation GREEN and commit builder**

```bash
python scripts/build_world_places.py --fixture tests/fixtures/world-places --output /tmp/world-places-fixture
python scripts/validate_world_places.py --data-dir /tmp/world-places-fixture --allow-runtime-missing
```

Expected: builder/data portion passes while runtime requirements still fail.

```bash
git add scripts/build_world_places.py scripts/validate_world_places.py tests/fixtures/world-places
git commit -m "feat(world-map): add places snapshot builder"
```

---

### Task 3: Commit a bounded generated Places baseline

**Files:**
- Create: `data/world-places/index.json`
- Create: `data/world-places/global-major.geo.json`
- Create: selected `data/world-places/countries/<ISO3>.geo.json`
- Modify: source/provenance documentation only if required by repository conventions.

**Interfaces:**
- Consumes: Task 2 builder.
- Produces: same-origin browser data for Task 4.

- [ ] **Step 1: Acquire the current GeoNames `cities5000` snapshot and source metadata**

Record download/source date separately from row-level population periods.

- [ ] **Step 2: Generate the global-major file and an initial useful partition set**

First checked-in partition wave should include Denmark plus a coherent Europe/North-Atlantic/North-Axis test set, for example:

```text
DNK NOR SWE FIN ISL DEU NLD BEL FRA GBR IRL
CAN POL CZE AUT CHE ITA ESP PRT GRC TUR UKR
```

The builder remains capable of generating all countries; CI validates partition metadata. Do not create hundreds of files manually in this PR.

- [ ] **Step 3: Validate provenance, counts and budgets**

Run:

```bash
python scripts/validate_world_places.py --data-only
```

Expected: PASS for data contract and hard budgets.

- [ ] **Step 4: Commit generated baseline**

```bash
git add data/world-places
git commit -m "data(world-map): add bounded global places baseline"
```

---

### Task 4: Replace capital-only rendering with the Places runtime

**Files:**
- Create: `world-map/3d-places.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-hover.js`
- Modify: `scripts/validate_world_places.py`

**Interfaces:**
- Consumes: `data/world-places/index.json`, `global-major.geo.json`, country partitions, `window.__potatoAtlasRenderStack`, `window.goCountry` or existing country selection API.
- Produces: `window.__potatoAtlasPlaces` API and MapLibre place layers.

- [ ] **Step 1: Add runtime-focused failing assertions**

Validator requires:

```text
__potatoAtlasPlaces
ready / setVisible / focus / current / search / clear / status
atlas-places-major-points
atlas-places-major-labels
atlas-places-detail-points
atlas-places-detail-labels
context-network registration
no MutationObserver / setInterval
```

- [ ] **Step 2: Load Places lazily from panel lifecycle**

`3d-panel-lifecycle.js` should load Places after Render Stack / Map State are available. Load immediately for `?place=` deep links; otherwise global-major can initialize after ordinary map boot without blocking the country map.

- [ ] **Step 3: Implement global-major source/layers**

Use one source for global-major and register place layers with the render stack:

```js
stack?.register?.('atlas-places-major-points', {
  slot:'context-network', priority:30, owner:'places'
});
stack?.register?.('atlas-places-major-labels', {
  slot:'context-network', priority:31, owner:'places'
});
```

Capital styling is an expression on the same source, not a duplicate capital layer.

- [ ] **Step 4: Implement lazy country partition loading**

Maintain:

```js
const loadedCountries = new Map();
async function loadCountry(iso3) { ... }
```

Only fetch a partition when country-scale camera/search/deep-link requires it. Install/update detail GeoJSON from loaded partitions; do not fetch all descriptors on boot.

- [ ] **Step 5: Converge legacy capital rendering**

Refactor `3d-hover.js` so it no longer adds `capital-cities`, `capital-city-major-labels`, or `capital-city-labels` when Places is available. Keep `window.__potatoAtlasCapitals` as a compatibility façade delegating visibility/focus to Places where necessary.

- [ ] **Step 6: Implement click precedence and hover**

On place click:

```js
if (event.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
```

Country polygon fallback must not fire from the same click.

- [ ] **Step 7: Run validator and syntax checks, then commit**

```bash
node --check world-map/3d-places.js
node --check world-map/3d-hover.js
python scripts/validate_world_places.py
```

Expected: data/runtime sections pass; search/inspector integration may still fail.

```bash
git add world-map/3d-places.js world-map/3d-panel-lifecycle.js world-map/3d-hover.js scripts/validate_world_places.py
git commit -m "feat(world-map): render scale-aware places"
```

---

### Task 5: Route Place and Subdivision statistics into the canonical right inspector

**Files:**
- Modify: `world-map/3d-places.js`
- Modify: `world-map/3d-subdivisions.js`
- Modify: `world-map/3d-panel-lifecycle.js` only if lifecycle key needs typed-context support
- Modify: `scripts/validate_world_places.py`

**Interfaces:**
- Consumes: existing `#panel`, existing country selection API, `window.__potatoAtlasSubdivisions`.
- Produces: typed Place/Subdivision panel contexts with no extra floating inspector.

- [ ] **Step 1: Add failing UI contract**

Reject:

```text
atlasSubdivisionCard
position:absolute subdivision inspector creation
```

Require the Place renderer to target `document.getElementById('panel')`, use an eyebrow containing `Place`, and include `Open country`.

Require subdivision selection to use the same panel and an eyebrow containing `Subdivision`.

- [ ] **Step 2: Implement Place inspector**

Render only available facts:

```text
Place
Copenhagen
Capital · Denmark
Population: 1,xxxxxx
Population period: — (when unknown)
Administrative region: ...
Coordinates: ...
Source: GeoNames
Dataset refreshed: ...
Open country
```

Never label dataset refresh as population year.

- [ ] **Step 3: Migrate subdivision inspector from floating card to `#panel`**

Remove `installInspector()` DOM card creation and render the existing subdivision fields in `#panel` instead. Preserve selection URL, source data and `clear()` behavior.

- [ ] **Step 4: Preserve explicit country transition**

`Open country` calls the existing country-selection function. Merely selecting a place/subdivision must not change compare/Trace working sets.

- [ ] **Step 5: Update panel lifecycle key if needed**

Include `place` and `subdivision` URL/context state so enhancement passes can distinguish typed inspector renders without adding another observer.

- [ ] **Step 6: Test and commit**

```bash
node --check world-map/3d-places.js
node --check world-map/3d-subdivisions.js
python scripts/validate_world_places.py
```

```bash
git add world-map/3d-places.js world-map/3d-subdivisions.js world-map/3d-panel-lifecycle.js scripts/validate_world_places.py
git commit -m "feat(world-map): route place and subdivision stats to inspector"
```

---

### Task 6: Add unified country/place search and stable URL restoration

**Files:**
- Create: `world-map/3d-search.js`
- Modify: `world-map/3d-panel-lifecycle.js` or bootstrap loader for Search
- Modify: `world-map/3d-map-state.js`
- Modify: existing country-search binding file only where necessary to delegate to `__potatoAtlasSearch`
- Modify: `scripts/validate_world_places.py`

**Interfaces:**
- Consumes: existing top `#search`, existing country lookup/navigation, `window.__potatoAtlasPlaces.search/focus`, `window.__potatoAtlasSubdivisions` when loaded.
- Produces: `window.__potatoAtlasSearch` and stable `place=<id>` restore/reset behavior.

- [ ] **Step 1: Add failing search/state assertions**

Require:

```js
window.__potatoAtlasSearch = { search, select, refresh };
```

Validator checks result type labels and `place` clearing in map state.

- [ ] **Step 2: Build a merged in-memory suggestion index**

Country records remain sourced from existing country owners. Place records come from global-major plus loaded partitions. Do not copy country metrics into place records.

Each suggestion has:

```js
{ type:'country'|'place'|'subdivision', id, label, parentLabel, score }
```

- [ ] **Step 3: Render disambiguated suggestions**

Examples:

```text
Georgia · Country
Copenhagen · Capital · Denmark
Aarhus · City · Denmark
```

Use the existing search surface; do not add another permanent search box.

- [ ] **Step 4: Select a place without mutating country working set**

Place selection calls:

```js
await window.__potatoAtlasPlaces.focus(id, { openInspector:true, fly:true });
```

and writes `place=<id>`.

- [ ] **Step 5: Restore deep links**

At module readiness, resolve `place=`. If the id is not in global-major, use index metadata/id lookup to identify/load the country partition. Invalid ids clear/fail quietly without breaking map boot.

- [ ] **Step 6: Extend whole-map reset**

In `3d-map-state.js` add:

```js
await runStep('places', async () => window.__potatoAtlasPlaces?.clear?.(), cleared, failed);
await runStep('subdivision', async () => window.__potatoAtlasSubdivisions?.clear?.(), cleared, failed);
```

When modules are unloaded, delete `place`/`subdivision` URL params directly so reset semantics do not depend on optional modules being loaded.

- [ ] **Step 7: Test and commit**

```bash
node --check world-map/3d-search.js
node --check world-map/3d-map-state.js
python scripts/validate_world_places.py
```

```bash
git add world-map/3d-search.js world-map/3d-map-state.js world-map/3d-panel-lifecycle.js scripts/validate_world_places.py
git commit -m "feat(world-map): unify country and place search"
```

---

### Task 7: Coverage/freshness integration and full repository verification

**Files:**
- Modify: existing World Map coverage builder/ledger files discovered by `scripts/build_world_map_coverage.py` / validator
- Modify: `scripts/validate_world_places.py`
- Modify: docs/spec metadata only if implementation decisions differ materially.

**Interfaces:**
- Consumes: generated Places index and existing coverage ledger.
- Produces: maintenance-level place coverage/freshness fields and exact-head green CI evidence.

- [ ] **Step 1: Add coverage fields from `index.json`**

At minimum:

```text
places_global_major_count
places_country_detail_count
places_population_count
places_population_period_known_count
places_capital_coverage
places_refresh_date
places_partition_status
```

These are descriptive coverage metrics only.

- [ ] **Step 2: Run focused validators**

```bash
python scripts/validate_world_places.py
python scripts/validate_world_map_ui_layout.py
python scripts/validate_world_map_3d.py
```

Expected: PASS.

- [ ] **Step 3: Run/trigger full Repository quality on exact head**

Verify the exact commit SHA, not merely the PR merge candidate. Confirm syntax, canonical runtime, UI shell/layout, render stack, map state, infrastructure, spatial overlays and Physical validators all remain green.

- [ ] **Step 4: Open/retarget stacked PR**

Base the Places implementation on the current Land Cover head (`fix/world-map-land-cover-provider`) until lower World Map PRs merge. Record RED and GREEN run numbers and exact SHAs in the PR description.

- [ ] **Step 5: Commit any final coverage integration**

```bash
git add scripts data/world-map* docs/superpowers/specs/2026-09-15-world-map-places-system-design.md
git commit -m "feat(world-map): integrate places coverage metadata"
```

## Self-review result

- Spec coverage: source strategy, bounded global layer, country partitions, place contract, render stack, typed inspector, unified search, URL/reset, subdivision compatibility, infrastructure hooks, performance, provenance and coverage all map to explicit tasks.
- Placeholder scan: no implementation `TODO`/`TBD` steps remain.
- Interface consistency: runtime API is consistently `window.__potatoAtlasPlaces`; search API is `window.__potatoAtlasSearch`; place URL parameter is consistently `place`; subdivision API remains `window.__potatoAtlasSubdivisions`.
