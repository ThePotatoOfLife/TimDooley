# World Map Runtime Hardening Wave 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bound World Map runtime growth, eliminate duplicate ownership, suppress stale async UI, deduplicate hydrology requests, and reduce reconciliation work without removing map capabilities or changing geographic data fidelity.

**Architecture:** Extend the bounded-runtime pattern already used by subdivisions into Places, then harden the neighboring coordination seams that can still accumulate work: search, hover/capital fallback, legacy UI ownership, hydrology, render ordering, layout refresh, and first-inspection promotion. Each subsystem keeps its current public API where possible; the changes add explicit budgets, deterministic eviction, single-owner contracts, generation/request guards, coalesced scheduling, and diagnostics rather than introducing a parallel map architecture.

**Tech Stack:** Browser ES modules, MapLibre GL JS 6.9.0, Node.js regression harnesses with fake DOM/MapLibre objects, Python 3 validators/build scripts, GeoJSON, GitHub Actions repository quality checks.

**Spec:** `docs/superpowers/specs/2026-09-15-world-map-runtime-hardening-wave2-design.md`

## Global Constraints

- Preserve user-visible World Map capabilities and data fidelity.
- Preserve deep-link semantics for `?country=`, `?place=`, and `?subdivision=`.
- Preserve the canonical `#panel` inspection surface.
- Preserve provenance and missing-value semantics; missing population remains `null`, never numeric zero.
- `world-map/3d-panel-lifecycle.js` remains the single canonical panel `MutationObserver` owner.
- `world-map/3d-physical-layers.js` remains the canonical country surface opacity owner.
- Do not add polling, a second DOM `MutationObserver`, or a second capital rendering owner.
- Do not change Wave 1 subdivision runtime budgets, USA/DNK subdivision geometry, or subdivision provenance.
- Do not remove Physical World layers or aggressively unload every hidden physical source in this wave.
- Do not fabricate or commit production `data/world-places/` GeoJSON in this wave.
- Places runtime budget values are exact: `partition_max_bytes=2097152`, `rendered_max_partitions=2`, `cache_max_partitions=6`, `cache_max_bytes=8388608`, `global_major_max_bytes=5242880`, `global_major_max_features=5000`.
- The Wave 2 branch is stacked on exact green Wave 1 head `fb4658667362bb1c6d928568cb6361c4b4c79842`; keep PR #172 unchanged.

---

## File structure and ownership map

**Places contract/data generation**
- `scripts/build_world_places.py` owns generated index shape, runtime budgets, partition descriptors, and compact geometry-free place search records.
- `scripts/validate_world_places.py` owns static/data contract enforcement and launches focused runtime regressions.
- `scripts/validate_world_places_fixture_pipeline.py` proves builder → generated fixture data → validator end to end.

**Places/search runtime**
- `world-map/3d-places.js` owns major-place data, bounded partition cache, shared detail source, place lookup/focus, place search records, and Places diagnostics.
- `world-map/3d-search.js` owns unified country/subdivision/place ranking and the UI request-generation guard.

**Hover/capital compatibility**
- `world-map/3d-hover.js` owns country hover and legacy capitals only as a fallback when Places reports unusable major data.

**Canonical UI ownership**
- `world-map/3d-panel-lifecycle.js` stays unchanged as the single live panel observer.
- `world-map/3d-ui.js` keeps unique compatibility controls/styling but consumes canonical lifecycle events and no longer owns country fill opacity.
- `world-map/3d-ui-layout.js` owns placement and one coalesced refresh scheduler.

**Physical request coordination**
- `world-map/3d-physical-hydrology.js` owns viewport request keys, abort/dedup counters, and regional HydroBASINS/HydroRIVERS refreshes.

**Render/bootstrap coordination**
- `world-map/3d-render-stack.js` owns semantic layer ordering with one style-order snapshot per reconciliation.
- `world-map/3d-bootstrap.js` owns staged first-inspection module promotion.
- `scripts/validate_world_map_browse_performance.py`, `scripts/validate_world_map_render_stack.py`, `scripts/validate_world_map_ui_layout.py`, `scripts/validate_world_map_hydrology.py`, and `scripts/validate_world_map_3d.py` enforce the migrated architecture.

---

### Task 1: Make the Places data contract carry exact runtime budgets and geometry-free search records

**Files:**
- Modify: `scripts/build_world_places.py`
- Modify: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_places_fixture_pipeline.py`

**Interfaces:**
- Consumes: existing normalized place feature properties from `normalize_place()` and existing per-country partition generation in `build_outputs()`.
- Produces: index top-level `runtime_budget: dict[str, int]`; each `countries[ISO3]` descriptor gains `search_records: list[dict]` with fields `id`, `name`, `aliases`, `country_iso3`, `type`, `capital_status`, `population_rank`, `partition`.
- Produces helper signature: `def search_record(feature: dict, partition: str) -> dict`.

- [ ] **Step 1: Add failing fixture-contract assertions**

Extend `validate_world_places_fixture_pipeline.py` after loading `index`:

```python
EXPECTED_BUDGET = {
    "partition_max_bytes": 2_097_152,
    "rendered_max_partitions": 2,
    "cache_max_partitions": 6,
    "cache_max_bytes": 8_388_608,
    "global_major_max_bytes": 5_242_880,
    "global_major_max_features": 5_000,
}

if index.get("runtime_budget") != EXPECTED_BUDGET:
    errors.append(f"fixture runtime budget mismatch: {index.get('runtime_budget')}")

dnk_descriptor = countries.get("DNK") or {}
dnk_search = dnk_descriptor.get("search_records") or []
by_search_id = {row.get("id"): row for row in dnk_search}
if by_search_id.get("gn:2618425") != {
    "id": "gn:2618425",
    "name": "Copenhagen",
    "aliases": by_search_id.get("gn:2618425", {}).get("aliases", []),
    "country_iso3": "DNK",
    "type": "Capital",
    "capital_status": "national",
    "population_rank": 1_153_615,
    "partition": "DNK",
}:
    errors.append("Copenhagen search record lost identity/type/rank/partition semantics")
```

Also assert every fixture partition descriptor `bytes` equals the generated file size and is `<= EXPECTED_BUDGET["partition_max_bytes"]`.

- [ ] **Step 2: Run the fixture pipeline and verify RED**

Run:

```bash
python3 scripts/validate_world_places_fixture_pipeline.py
```

Expected: FAIL because `runtime_budget` and `search_records` are absent.

- [ ] **Step 3: Implement the builder contract and validator**

In `build_world_places.py`, add:

```python
PLACES_RUNTIME_BUDGET = {
    "partition_max_bytes": 2_097_152,
    "rendered_max_partitions": 2,
    "cache_max_partitions": 6,
    "cache_max_bytes": 8_388_608,
    "global_major_max_bytes": 5_242_880,
    "global_major_max_features": 5_000,
}


def search_record(feature: dict, partition: str) -> dict:
    props = feature.get("properties") or {}
    population = props.get("population")
    capital_status = str(props.get("capital_status") or "none")
    kind = "Capital" if capital_status == "national" else (
        "Town" if isinstance(population, int) and 0 < population < 50_000 else "City"
    )
    return {
        "id": str(props.get("id") or ""),
        "name": str(props.get("name") or ""),
        "aliases": list(props.get("aliases") or []),
        "country_iso3": partition,
        "type": kind,
        "capital_status": capital_status,
        "population_rank": int(population or 0),
        "partition": partition,
    }
```

When writing each country descriptor, include exact file bytes and `search_records=[search_record(feature, iso3) for feature in rows]`. Add `"runtime_budget": PLACES_RUNTIME_BUDGET` to the top-level index.

In `validate_world_places.py`, define the same expected budget constants and enforce:

```python
if index.get("runtime_budget") != EXPECTED_RUNTIME_BUDGET:
    errors.append("Places runtime_budget does not match the canonical Wave 2 budget")

if major_path.stat().st_size > EXPECTED_RUNTIME_BUDGET["global_major_max_bytes"]:
    errors.append("global-major file budget exceeded")
if len(features) > EXPECTED_RUNTIME_BUDGET["global_major_max_features"]:
    errors.append("global-major feature budget exceeded")
```

For each country descriptor, verify `bytes == path.stat().st_size`, `bytes <= partition_max_bytes`, and validate every search record has the exact fields above, a stable id/name/country/partition, list aliases, supported type, supported capital status, and non-negative integer `population_rank`.

- [ ] **Step 4: Run the data contract tests and verify GREEN**

Run:

```bash
python3 scripts/validate_world_places_fixture_pipeline.py
python3 scripts/validate_world_places.py --runtime-only
```

Expected: both PASS; fixture output preserves Copenhagen/Berlin identities and null population semantics.

- [ ] **Step 5: Commit the contract**

```bash
git add scripts/build_world_places.py scripts/validate_world_places.py scripts/validate_world_places_fixture_pipeline.py
git commit -m "World Map: budget Places data contract"
```

---

### Task 2: Bound Places partition memory and the shared detail source

**Files:**
- Create: `scripts/test_world_map_places_bounded_runtime.mjs`
- Modify: `world-map/3d-places.js`
- Modify: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_map_browse_performance.py`

**Interfaces:**
- Consumes: `indexPayload.runtime_budget` and country descriptors from Task 1.
- Produces: `window.__potatoAtlasPlaces.status()` fields `renderedPartitions`, `renderedBytes`, `cachedPartitions`, `cacheBytes`, `cacheHits`, `cacheMisses`, `cacheEvictions`, `budget`.
- Keeps public methods `ready`, `setVisible`, `focus`, `current`, `search`, `clear`, `status`, `loadCountry`.
- Internal maps: `majorFeatureById`, `partitionFeatureById`, `partitionByFeatureId`, `partitionCache`.

- [ ] **Step 1: Write the bounded-runtime regression**

Create a fake DOM/MapLibre harness modeled on `scripts/test_world_map_subdivision_bounded_runtime.mjs`. Feed synthetic major data plus USA/DNK/FIN country partitions and a test budget with `cache_max_partitions: 2` and `rendered_max_partitions: 2`.

Key assertions:

```js
await window.__potatoAtlasPlaces.loadCountry('USA');
await window.__potatoAtlasPlaces.loadCountry('DNK');
assert.equal(await window.__potatoAtlasPlaces.focus('gn:dnk-selected', { country:'DNK', fit:false }), true);
await window.__potatoAtlasPlaces.loadCountry('FIN');

const status = window.__potatoAtlasPlaces.status();
assert.ok(status.cachedPartitions.length <= 2);
assert.ok(status.cachedPartitions.includes('DNK'), 'selected place partition must survive LRU pressure');
assert.ok(status.renderedPartitions.length <= 2);
assert.ok(status.cacheEvictions >= 1);
assert.equal(typeof status.cacheBytes, 'number');
assert.equal(typeof status.renderedBytes, 'number');

const detail = sources.get('atlas-places-detail')?.data;
const detailCountries = new Set((detail?.features || []).map(f => f.properties.country_iso3));
assert.ok(detailCountries.size <= 2, 'shared detail source must stay bounded');

assert.equal(window.__potatoAtlasPlaces.__testFindFeature?.('gn:usa-evicted') ?? null, null);
assert.ok(window.__potatoAtlasPlaces.current(), 'selected feature must remain available');
assert.ok(window.__potatoAtlasPlaces.search('Majorville').length > 0, 'global-major index must survive partition eviction');
```

Expose `__testFindFeature` only when the module URL contains `bounded-runtime-regression=1`, or assert eviction through `search()`/`focus()` if keeping test-only API out of production is cleaner.

- [ ] **Step 2: Run the regression and verify RED**

Run:

```bash
node scripts/test_world_map_places_bounded_runtime.mjs
```

Expected: FAIL because the current runtime retains all partitions and reports no budget/cache diagnostics.

- [ ] **Step 3: Implement deterministic Places LRU and bounded rendering**

In `3d-places.js`, replace the unbounded `loadedCountries`/single feature map model with:

```js
const DEFAULT_RUNTIME_BUDGET = Object.freeze({
  partition_max_bytes: 2_097_152,
  rendered_max_partitions: 2,
  cache_max_partitions: 6,
  cache_max_bytes: 8_388_608,
  global_major_max_bytes: 5_242_880,
  global_major_max_features: 5_000,
});

const majorFeatureById = new Map();
const partitionFeatureById = new Map();
const partitionByFeatureId = new Map();
const partitionCache = new Map();
let useClock = 0;
let activeCountry = null;
let deepLinkCountry = new URL(location.href).searchParams.get('country')?.toUpperCase() || null;
let cacheHits = 0;
let cacheMisses = 0;
let cacheEvictions = 0;
```

Implement exact helpers:

```js
function runtimeBudget() { /* merge only finite positive index values over defaults */ }
function touchPartition(code) { /* increment useClock and record lastUsed */ }
function selectedPartition() { return selectedId ? partitionByFeatureId.get(selectedId) || null : null; }
function protectedPartitions(extra = null) { /* selected, activeCountry, deepLinkCountry, extra */ }
function evictPartition(code) { /* remove partition feature ids, partition map entry, diagnostics */ }
function enforceCacheBudget(extraProtected = null) { /* LRU until count and bytes fit */ }
function renderedPartitionCodes() { /* relevance order: selected, active, deep link, recency; slice budget */ }
function syncDetailSource() { /* compose only rendered partition records into DETAIL_SOURCE */ }
```

`loadCountry(code)` increments hit/miss diagnostics, validates descriptor byte size against `partition_max_bytes`, stores `{code, descriptor, data, bytes, lastUsed}`, indexes its features into the partition maps, sets `activeCountry=code`, enforces cache budget with the newly loaded code temporarily protected, then calls `syncDetailSource()`.

`findFeature(id)` resolves `majorFeatureById` first, then `partitionFeatureById`. `clear()` removes selection protection and re-runs cache enforcement/sync. `status()` returns the exact diagnostics contract from the spec and mirrors it into `window.__potatoAtlasDiagnostics.places` when diagnostics exist.

- [ ] **Step 4: Wire validators and verify GREEN**

Add `scripts/test_world_map_places_bounded_runtime.mjs` execution to `validate_world_places.py --runtime-only`. Extend `validate_world_map_browse_performance.py` to require `cacheEvictions`, `renderedPartitions`, the shared `atlas-places-detail` source, and reject an all-history detail-source loop pattern.

Run:

```bash
node scripts/test_world_map_places_bounded_runtime.mjs
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_browse_performance.py
```

Expected: all PASS; existing subdivision guards stay unchanged.

- [ ] **Step 5: Commit bounded Places runtime**

```bash
git add world-map/3d-places.js scripts/test_world_map_places_bounded_runtime.mjs scripts/validate_world_places.py scripts/validate_world_map_browse_performance.py
git commit -m "World Map: bound Places runtime cost"
```

---

### Task 3: Make place search geometry-free and suppress stale suggestion renders

**Files:**
- Create: `scripts/test_world_map_search_generation.mjs`
- Modify: `world-map/3d-places.js`
- Modify: `world-map/3d-search.js`
- Modify: `scripts/validate_world_places.py`

**Interfaces:**
- Consumes: Task 1 `countries[*].search_records` and Task 2 bounded feature maps.
- Produces: place search results `{id, name, country, type, partition, feature}` where `feature` is either a currently resident feature or `null`.
- Produces search diagnostics under `window.__potatoAtlasDiagnostics.search = {generation, staleRenderSuppressions}`.

- [ ] **Step 1: Write a deferred-promise search generation regression**

Create `scripts/test_world_map_search_generation.mjs` with a fake `#search`, fake datalist, and deferred country/subdivision index fetches. Trigger input `"de"`, then `"denmark"`, resolve the newer logical search first and the older search second, and assert the rendered datalist still contains only the newest result set.

Also feed a geometry-free place search record and assert focusing it delegates to:

```js
window.__potatoAtlasPlaces.focus(result.id, {
  country: result.country,
  feature: null,
  fit: true,
});
```

- [ ] **Step 2: Run the regression and verify RED**

```bash
node scripts/test_world_map_search_generation.mjs
```

Expected: FAIL because older async input completions can still call `renderSuggestions()`.

- [ ] **Step 3: Implement search-record lookup and UI generation guards**

In `3d-places.js`, build a deduplicated geometry-free search array from `indexPayload.countries[*].search_records`. `search(query,{limit})` merges major features, cached feature records, and compact search records by stable id; it ranks exact/prefix/contains name/alias matches and returns the resident `feature` when available, otherwise `null` plus `partition/country`.

In `3d-search.js`, add:

```js
let inputGeneration = 0;
let staleRenderSuppressions = 0;

async function searchAndRenderInput(value) {
  const generation = ++inputGeneration;
  const results = await search(value, {limit:10});
  if (generation !== inputGeneration) {
    staleRenderSuppressions += 1;
    syncSearchDiagnostics();
    return results;
  }
  renderSuggestions(results);
  syncSearchDiagnostics();
  return results;
}
```

Use `searchAndRenderInput(event.target.value)` in the input listener. Keep the existing capturing Enter handler and `event.stopImmediatePropagation()` before awaiting `submit()`.

- [ ] **Step 4: Verify search behavior and runtime contracts**

```bash
node scripts/test_world_map_search_generation.mjs
node scripts/test_world_map_subdivision_search.mjs
python3 scripts/validate_world_places.py --runtime-only
```

Expected: all PASS; subdivision search/focus continues delegating to `__potatoAtlasSubdivisions.select()`.

- [ ] **Step 5: Commit search hardening**

```bash
git add world-map/3d-places.js world-map/3d-search.js scripts/test_world_map_search_generation.mjs scripts/validate_world_places.py
git commit -m "World Map: harden async place search"
```

---

### Task 4: Converge capital ownership and suppress stale country hover

**Files:**
- Create: `scripts/test_world_map_hover_capital_ownership.mjs`
- Modify: `world-map/3d-hover.js`
- Modify: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Consumes: `potato-atlas-places-ready` and `window.__potatoAtlasPlaces.status()`.
- Produces: legacy `window.__potatoAtlasCapitals` only when Places reports `majorCount === 0` or a data error; Places remains primary when `majorCount > 0` and no error.
- Produces hover diagnostics `window.__potatoAtlasDiagnostics.hover = {generation, staleSuppressions}`.

- [ ] **Step 1: Write ownership and hover race regressions**

The Node harness should cover two startup cases:

```js
// Healthy Places: no legacy capital source/layers.
dispatchEvent(new CustomEvent('potato-atlas-places-ready', {
  detail:{majorCount:3, error:null}
}));
assert.equal(sources.has('capital-cities'), false);

// Places unavailable: fallback is installed.
dispatchEvent(new CustomEvent('potato-atlas-places-ready', {
  detail:{majorCount:0, error:'snapshot unavailable'}
}));
await flushPromises();
assert.equal(sources.has('capital-cities'), true);
```

For hover, make `countryHtml()` depend on deferred scalar promises. Fire USA mousemove then DNK mousemove; resolve DNK first and USA second. Assert the popup remains DNK. Fire mouseleave before a deferred hover resolves and assert the late result does not reopen the popup.

- [ ] **Step 2: Run the regression and verify RED**

```bash
node scripts/test_world_map_hover_capital_ownership.mjs
```

Expected: FAIL because capitals currently install eagerly and hover has no generation guard.

- [ ] **Step 3: Implement fallback-only capitals and hover generations**

Change `install()` so it binds country hover immediately but does not call `installCapitalsWhenUseful()` directly. Add:

```js
function placesCanOwnCapitals(detail = {}) {
  const status = window.__potatoAtlasPlaces?.status?.() || detail || {};
  return Number(status.majorCount || 0) > 0 && !status.error;
}

window.addEventListener('potato-atlas-places-ready', event => {
  if (!placesCanOwnCapitals(event.detail || {})) void installCapitalsWhenUseful();
});
```

Add one monotonic `hoverGeneration`; increment on each mousemove and mouseleave. Capture the generation and country code before awaiting `countryHtml()`, and call `showPopup()` only if the generation still matches.

Do not remove the fallback capital dataset/constants/layers/API; their unique compatibility path must remain available when Places data is absent.

Update `validate_world_map_3d.py` so it requires the fallback markers and the Places-ready ownership gate rather than assuming eager capital installation. Update `validate_world_places.py` to execute the new Node regression.

- [ ] **Step 4: Verify capital fallback and core 3D contracts**

```bash
node scripts/test_world_map_hover_capital_ownership.mjs
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_3d.py
```

Expected: PASS in both healthy-Places and no-Places fixture cases.

- [ ] **Step 5: Commit capital/hover ownership**

```bash
git add world-map/3d-hover.js scripts/test_world_map_hover_capital_ownership.mjs scripts/validate_world_places.py scripts/validate_world_map_3d.py
git commit -m "World Map: converge capital and hover ownership"
```

---

### Task 5: Remove duplicate legacy UI ownership and coalesce UI layout refreshes

**Files:**
- Create: `scripts/test_world_map_ui_layout_coalescing.mjs`
- Modify: `world-map/3d-ui.js`
- Modify: `world-map/3d-ui-layout.js`
- Modify: `scripts/validate_world_map_ui_layout.py`
- Modify: `scripts/validate_world_map_browse_performance.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Consumes: canonical `potato-atlas-panel-rendered` events and `window.__potatoAtlasPanelLifecycle`.
- Produces: `window.__potatoAtlasUILayout.refresh()` as explicit synchronous refresh; `register()`, `unregister()`, and `setVisible()` schedule one coalesced microtask refresh.
- Produces diagnostics `window.__potatoAtlasDiagnostics.uiLayoutRefreshes`.

- [ ] **Step 1: Write layout coalescing and ownership regressions**

Create a fake DOM harness that imports `3d-ui-layout.js`, creates the known `#panel`, `#atlasWorldContext`, and `#atlasTimeState` surfaces, and counts `potato-atlas-ui-layout-change` events.

Assert that registering three surfaces synchronously emits one coalesced event after a microtask and that each surface ends in the correct host/order.

Add static assertions in the same test or Python validators:

```python
if "new MutationObserver(" in ui:
    errors.append("world-map/3d-ui.js must consume the canonical panel lifecycle instead of observing #panel")
if "setPaintProperty('countries-fill','fill-opacity'" in ui.replace(" ", ""):
    errors.append("legacy UI must not own countries-fill opacity")
```

- [ ] **Step 2: Run focused validators and verify RED**

```bash
node scripts/test_world_map_ui_layout_coalescing.mjs
python3 scripts/validate_world_map_browse_performance.py
```

Expected: at least one FAIL because `3d-ui.js` still constructs its own observer and `register()` still recursively calls `refresh()`.

- [ ] **Step 3: Migrate `3d-ui.js` to canonical lifecycle consumption**

Remove its local `panelLifecycleKey`, observer state, `publishPanelLifecycle`, `schedulePanelLifecycle`, and `new MutationObserver(...)` block. Replace that behavior with:

```js
window.addEventListener('potato-atlas-panel-rendered', () => {
  if (!panel) return;
  const signature = panel.textContent || '';
  if (signature === lastSignature) return;
  lastSignature = signature;
  if (!app?.classList.contains('ui-focus')) {
    const passiveSelection = /Canonical country|Territory \/ map polygon|World Relational Atlas/.test(signature);
    const isLanding = /Explore the world/.test(signature);
    if (!isLanding && !passiveSelection) setPanel(true, {persist:false});
  }
});
```

Keep unique menu controls, styling, keyboard behavior, and `window.__potatoAtlasUI`. In `tuneMapSurface()`, preserve non-conflicting color/line styling but remove direct `countries-fill` opacity assignment so `3d-physical-layers.js` is the sole opacity owner.

- [ ] **Step 4: Coalesce layout refresh scheduling and migrate validators**

In `3d-ui-layout.js`, add:

```js
let refreshScheduled = false;
let refreshing = false;

function scheduleRefresh() {
  if (refreshScheduled) return;
  refreshScheduled = true;
  queueMicrotask(() => {
    refreshScheduled = false;
    refresh();
  });
}
```

`register()`, `unregister()`, and `setVisible()` mutate state then call `scheduleRefresh()`. `refresh()` guards `refreshing`, adopts known surfaces without recursively triggering a synchronous refresh, performs placement once, increments `uiLayoutRefreshes`, then emits one layout-change event.

Update `validate_world_map_3d.py`: replace the old required `MutationObserver` marker for UI with `potato-atlas-panel-rendered` and reject a UI observer. Update `validate_world_map_ui_layout.py` and `validate_world_map_browse_performance.py` to enforce `scheduleRefresh`, one canonical observer in `3d-panel-lifecycle.js`, no observer in `3d-ui.js`, and no legacy fill-opacity owner.

- [ ] **Step 5: Verify and commit canonical UI ownership**

Run:

```bash
node scripts/test_world_map_ui_layout_coalescing.mjs
python3 scripts/validate_world_map_ui_layout.py
python3 scripts/validate_world_map_browse_performance.py
python3 scripts/validate_world_map_3d.py
```

Expected: all PASS.

Commit:

```bash
git add world-map/3d-ui.js world-map/3d-ui-layout.js scripts/test_world_map_ui_layout_coalescing.mjs scripts/validate_world_map_ui_layout.py scripts/validate_world_map_browse_performance.py scripts/validate_world_map_3d.py
git commit -m "World Map: consolidate UI runtime ownership"
```

---

### Task 6: Deduplicate hydrology viewport requests

**Files:**
- Create: `scripts/test_world_map_hydrology_dedup.mjs`
- Modify: `world-map/3d-physical-hydrology.js`
- Modify: `scripts/validate_world_map_hydrology.py`

**Interfaces:**
- Produces helper signatures `function requestKey()` and `function roundedEnvelope(precision = 2)` or equivalent stable-key helpers.
- Produces hydrology diagnostics `{requestCount, deduplicatedRefreshes, abortedRequests, requestKey}` under `window.__potatoAtlasDiagnostics.hydrology`.
- Keeps `window.__potatoAtlasHydrology.refresh`, `enable`, `disable`, `toggle`, `setOpacity`, `getOpacity`.

- [ ] **Step 1: Write duplicate/scope-change request regression**

Build a fake map at zoom 6 with stable bounds and a fetch spy. After `enable()`, wait for the first basin+river pair, call `refresh()` again with identical bounds, and assert fetch count remains two. Change bounds materially, call `refresh()`, and assert fetch count becomes four.

Also assert diagnostics:

```js
assert.equal(status.requestCount, 2, 'two refresh cycles should start after one deduplicated repeat');
assert.ok(status.deduplicatedRefreshes >= 1);
assert.ok(status.abortedRequests >= 0);
```

Use request cycle count rather than raw HTTP count if the diagnostics count one basin+river pair as one request cycle.

- [ ] **Step 2: Run the regression and verify RED**

```bash
node scripts/test_world_map_hydrology_dedup.mjs
```

Expected: FAIL because identical refreshes currently start another pair.

- [ ] **Step 3: Implement stable request keys and counters**

Add state:

```js
let inFlightRequestKey = null;
let completedRequestKey = null;
let requestCount = 0;
let deduplicatedRefreshes = 0;
let abortedRequests = 0;
```

Build the key from rounded west/south/east/north coordinates, the `riverThreshold()`, and a zoom regime label. Before aborting/creating a controller:

```js
const key = requestKey();
if (key && (key === inFlightRequestKey || key === completedRequestKey)) {
  deduplicatedRefreshes += 1;
  syncHydrologyDiagnostics(key);
  return;
}
```

When a materially different request replaces an in-flight controller, increment `abortedRequests`. Set `completedRequestKey` only when the request cycle is still current. Reset `inFlightRequestKey` on completion/disable. Preserve minimum zoom and error behavior.

- [ ] **Step 4: Verify hydrology contract**

```bash
node scripts/test_world_map_hydrology_dedup.mjs
python3 scripts/validate_world_map_hydrology.py
python3 scripts/validate_world_map_ui_layout.py
```

Expected: all PASS; hydrology remains on-demand, viewport-bounded, and sacred-overlay independent.

- [ ] **Step 5: Commit request deduplication**

```bash
git add world-map/3d-physical-hydrology.js scripts/test_world_map_hydrology_dedup.mjs scripts/validate_world_map_hydrology.py
git commit -m "World Map: deduplicate hydrology requests"
```

---

### Task 7: Reconcile render order with one style snapshot per pass

**Files:**
- Create: `scripts/test_world_map_render_stack_reconcile.mjs`
- Modify: `world-map/3d-render-stack.js`
- Modify: `scripts/validate_world_map_render_stack.py`

**Interfaces:**
- Keeps public `window.__potatoAtlasRenderStack = {register, unregister, reconcile, state, slotOrder}`.
- `reconcile(reason)` additionally reports `styleSnapshots` and `moveCount` in the returned/event detail diagnostics.

- [ ] **Step 1: Write the style-snapshot regression**

Fake a style containing country fill/line/hubs/labels plus registered physical/context layers. Count calls to `map.getStyle()` and record `moveLayer()` operations.

Assert:

```js
const result = window.__potatoAtlasRenderStack.reconcile('regression');
assert.equal(getStyleCalls, 1, 'one reconciliation must snapshot style order once');
assert.deepEqual(finalSemanticOrder, expectedSemanticOrder);
assert.equal(result.moveCount, moves.length);
```

Expected semantic relationships: physical-surface below country fill; physical-water/line/geography/context below country line; selection-emphasis below country hubs/labels.

- [ ] **Step 2: Run and verify RED**

```bash
node scripts/test_world_map_render_stack_reconcile.mjs
```

Expected: FAIL because current `moveRegion()` repeatedly calls `styleOrder()`.

- [ ] **Step 3: Implement a mutable local order snapshot**

At the start of `reconcile()`:

```js
const order = styleOrder();
let styleSnapshots = 1;
```

Pass `order` into `moveRegion()`. After a successful `map.moveLayer(layerId, beforeId)`, update the local `order` array by removing `layerId` and splicing it before `beforeId`. Use local `indexOf()` values for adjacency decisions; never rebuild style order inside the loop.

Add `moveCount:moved.length` and `styleSnapshots` to reconcile result/event detail and retain existing `reconcileCount`/`lastReason` behavior.

- [ ] **Step 4: Verify render semantics**

```bash
node scripts/test_world_map_render_stack_reconcile.mjs
python3 scripts/validate_world_map_render_stack.py
python3 scripts/validate_world_map_ui_layout.py
```

Expected: all PASS and exactly one style snapshot in the focused regression.

- [ ] **Step 5: Commit render-stack optimization**

```bash
git add world-map/3d-render-stack.js scripts/test_world_map_render_stack_reconcile.mjs scripts/validate_world_map_render_stack.py
git commit -m "World Map: reduce render stack reconciliation work"
```

---

### Task 8: Stage first-inspection enhancement promotion

**Files:**
- Modify: `world-map/3d-bootstrap.js`
- Modify: `scripts/validate_world_map_browse_performance.py`

**Interfaces:**
- Keeps `loadAfterPaint(label,path)` and `loadSpecialist(label,path)` public internal semantics.
- Introduces internal functions `loadInspectionBasics()`, `loadInspectionContext()`, `loadInspectionDeep()` used by `promoteInspection()`.

- [ ] **Step 1: Add a failing structural regression to the browse-performance validator**

Require these exact function markers and ordering:

```python
for token in (
    "async function loadInspectionBasics()",
    "async function loadInspectionContext()",
    "async function loadInspectionDeep()",
    "await loadInspectionBasics();",
    "await nextPaint();",
    "await loadInspectionContext();",
    "await nextPaint();",
    "await loadInspectionDeep();",
):
    require(bootstrap, token, "world-map/3d-bootstrap.js", errors)
```

Also ensure `Infrastructure Context`, `Impact Trace`, and `Impact Actions` occur inside the deep function, not in the context `Promise.all` containing `System Intelligence` and `Functional Chains`.

- [ ] **Step 2: Run the validator and verify RED**

```bash
python3 scripts/validate_world_map_browse_performance.py
```

Expected: FAIL because promotion is currently two broad groups plus Impact Actions.

- [ ] **Step 3: Split the promotion into three paint-separated groups**

Use:

```js
async function loadInspectionBasics() {
  await Promise.all([
    loadAfterPaint('Demography', './3d-demography.js'),
    loadAfterPaint('Country Pulse', './3d-country-pulse.js'),
    loadAfterPaint('Evidence', './3d-evidence.js'),
  ]);
}

async function loadInspectionContext() {
  await Promise.all([
    loadSpecialist('System Intelligence', './3d-gateways.js'),
    loadSpecialist('Functional Chains', './3d-chain-explorer.js'),
  ]);
}

async function loadInspectionDeep() {
  await Promise.all([
    loadSpecialist('Infrastructure Context', './3d-infrastructure.js'),
    loadSpecialist('Impact Trace', './3d-impact-trace.js'),
  ]);
  await loadSpecialist('Impact Actions', './3d-impact-actions.js');
}

async function promoteInspection() {
  await loadInspectionBasics();
  await nextPaint();
  await loadInspectionContext();
  await nextPaint();
  await loadInspectionDeep();
}
```

This keeps existing module APIs and explicit shared-loader access intact while flattening the first-inspection burst.

- [ ] **Step 4: Verify bootstrap/lazy architecture**

```bash
python3 scripts/validate_world_map_browse_performance.py
python3 scripts/validate_world_map_3d.py
node --check world-map/3d-bootstrap.js
```

Expected: all PASS.

- [ ] **Step 5: Commit staged promotion**

```bash
git add world-map/3d-bootstrap.js scripts/validate_world_map_browse_performance.py
git commit -m "World Map: stage inspection enhancements"
```

---

### Task 9: Run the integrated hardening gate and preserve Wave 1 invariants

**Files:**
- Modify only if test-run wiring is missing: `scripts/validate_world_places.py`, `scripts/validate_world_map_browse_performance.py`, `scripts/validate_world_map_ui_layout.py`
- Verify unchanged: `world-map/3d-subdivisions.js`, `data/world-subdivisions/USA.geo.json`, `data/world-subdivisions/DNK.geo.json`

**Interfaces:**
- Produces no new runtime API. This task proves the combined branch remains compatible with the approved design and Wave 1.

- [ ] **Step 1: Run every focused Wave 2 regression**

```bash
python3 scripts/validate_world_places_fixture_pipeline.py
node scripts/test_world_map_places_bounded_runtime.mjs
node scripts/test_world_map_search_generation.mjs
node scripts/test_world_map_hover_capital_ownership.mjs
node scripts/test_world_map_ui_layout_coalescing.mjs
node scripts/test_world_map_hydrology_dedup.mjs
node scripts/test_world_map_render_stack_reconcile.mjs
```

Expected: all PASS.

- [ ] **Step 2: Run all affected architecture validators**

```bash
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_hydrology.py
python3 scripts/validate_world_map_render_stack.py
python3 scripts/validate_world_map_ui_layout.py
python3 scripts/validate_world_map_browse_performance.py
python3 scripts/validate_world_map_3d.py
python3 scripts/validate_world_map_ownership.py
```

Expected: all PASS.

- [ ] **Step 3: Re-run Wave 1 subdivision regressions unchanged**

```bash
node scripts/test_world_map_subdivision_bounded_runtime.mjs
node scripts/test_world_map_subdivision_freeze.mjs
node scripts/test_world_map_subdivision_multi_country.mjs
node scripts/test_world_map_subdivision_search.mjs
python3 scripts/validate_world_map_subdivisions.py
```

Expected: all PASS; subdivision runtime remains one shared source/three layers with the existing Wave 1 budget contract.

- [ ] **Step 4: Verify subdivision data artifacts are untouched relative to Wave 1 base**

```bash
git diff --exit-code fb4658667362bb1c6d928568cb6361c4b4c79842 -- data/world-subdivisions/USA.geo.json data/world-subdivisions/DNK.geo.json
```

Expected: exit 0 with no diff.

- [ ] **Step 5: Run repository quality checks on the exact branch head**

Push the exact implementation head and inspect the GitHub Actions `Repository quality checks` run for that same SHA. The accepted result is `status=completed` and `conclusion=success`; do not substitute an older successful run or a run from another SHA.

Record the exact head SHA and workflow run id in the completion report.

- [ ] **Step 6: Commit only integration-wiring changes if Step 1 or 2 exposed missing validator wiring**

If the focused tests were not already launched by their canonical validators, add that wiring and commit exactly those validator files:

```bash
git add scripts/validate_world_places.py scripts/validate_world_map_browse_performance.py scripts/validate_world_map_ui_layout.py
git commit -m "test(world-map): enforce runtime hardening contracts"
```

If no wiring changes are needed, leave the working tree unchanged and do not create an empty commit.

---

## Final implementation review checklist

Before declaring implementation complete, verify all of the following from the exact implementation head:

- Places cache and rendered detail partitions are bounded by both count and bytes.
- Selected place partition survives LRU pressure; evicted partition features leave the partition feature index.
- Global-major place lookup/search remains available after partition eviction.
- Geometry-free search records can resolve to geometry only when focused.
- Older async search results cannot overwrite newer suggestions.
- Older async hover results cannot overwrite the current hover or reopen after mouseleave.
- Healthy Places prevents legacy `capital-cities` source/layers from being created; unavailable Places still gets the legacy fallback.
- `3d-ui.js` contains no `MutationObserver` and does not set `countries-fill` opacity.
- `3d-panel-lifecycle.js` remains the single active panel observer.
- UI layout registrations coalesce into one scheduled refresh/event per microtask burst.
- Repeated identical hydrology request keys do not issue another basin/river pair; changed viewport keys do.
- Render stack takes one style-order snapshot per reconciliation and preserves semantic z-order.
- First country inspection promotes basic, context, and deep modules in separate paint stages.
- No production Places GeoJSON was added.
- USA/DNK subdivision geometry and Wave 1 runtime contract are unchanged.
- Exact-head repository quality checks succeed before merge.
