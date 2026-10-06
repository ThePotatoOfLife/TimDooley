# World Map Runtime Hardening Wave 2 Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bound World Map runtime growth, remove duplicate runtime ownership, suppress stale async UI, deduplicate hydrology requests, and reduce reconciliation work without removing capabilities or changing geographic fidelity.

**Architecture:** Apply the bounded-partition pattern already proven by subdivisions to Places, then harden the coordination seams around it. Places keeps one global-major source plus one bounded detail source; compact search records are geometry-free; legacy capitals become fallback-only; canonical panel/paint owners remain unique; async UI uses generation/request keys; layout/render work is coalesced; first-inspection enhancement loads are staged across paints.

**Tech Stack:** Browser ES modules, MapLibre GL JS 6.9.0, Node.js fake-DOM/fake-MapLibre regressions, Python 3 builders/validators, GeoJSON, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-world-map-runtime-hardening-wave2-design.md`

## Global Constraints

- Preserve `?country=`, `?place=`, and `?subdivision=` deep links.
- Preserve provenance and `population: null` semantics.
- `world-map/3d-panel-lifecycle.js` remains the only panel `MutationObserver` owner.
- `world-map/3d-physical-layers.js` remains the country fill-opacity owner.
- Do not add polling or a second capital renderer.
- Do not change Wave 1 subdivision budgets or USA/DNK subdivision artifacts.
- Do not remove Physical World layers or fabricate production `data/world-places/` GeoJSON.
- Places budget is exact: 2 MiB per partition, 2 rendered partitions, 6 cached partitions, 8 MiB cache, 5 MiB / 5000-feature global-major maximum.
- Branch remains stacked on Wave 1 exact green head `fb4658667362bb1c6d928568cb6361c4b4c79842`; PR #172 remains untouched.

---

### Task 1: Add the Places runtime/search data contract

**Files:**
- Modify: `scripts/build_world_places.py`
- Modify: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_places_fixture_pipeline.py`

**Interfaces:**
- `PLACES_RUNTIME_BUDGET: dict[str, int]`
- `search_record(feature: dict, partition: str) -> dict`
- Each `countries[ISO3]` descriptor gains `search_records` with exactly `id`, `name`, `aliases`, `country_iso3`, `type`, `capital_status`, `population_rank`, `partition`.

- [ ] **Step 1: Write RED fixture assertions**

Add this exact expected budget to `validate_world_places_fixture_pipeline.py`:

```python
EXPECTED_BUDGET = {
    "partition_max_bytes": 2_097_152,
    "rendered_max_partitions": 2,
    "cache_max_partitions": 6,
    "cache_max_bytes": 8_388_608,
    "global_major_max_bytes": 5_242_880,
    "global_major_max_features": 5_000,
}
```

Assert `index["runtime_budget"] == EXPECTED_BUDGET`, every descriptor byte count equals the emitted country file size and does not exceed `partition_max_bytes`, Copenhagen has id `gn:2618425`, `type == "Capital"`, `capital_status == "national"`, `population_rank == 1_153_615`, and every search record is geometry-free.

- [ ] **Step 2: Prove RED**

```bash
python3 scripts/validate_world_places_fixture_pipeline.py
```

Expected: FAIL because the current generated index lacks `runtime_budget` and `search_records`.

- [ ] **Step 3: Implement the builder contract**

Add:

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
    if capital_status == "national":
        place_type = "Capital"
    elif isinstance(population, int) and 0 < population < 50_000:
        place_type = "Town"
    else:
        place_type = "City"
    return {
        "id": str(props.get("id") or ""),
        "name": str(props.get("name") or ""),
        "aliases": list(props.get("aliases") or []),
        "country_iso3": partition,
        "type": place_type,
        "capital_status": capital_status,
        "population_rank": int(population or 0),
        "partition": partition,
    }
```

Write `runtime_budget` at index top level and `search_records=[search_record(feature, iso3) for feature in rows]` in each country descriptor.

- [ ] **Step 4: Enforce the contract in `validate_world_places.py`**

Reject any budget mismatch, any partition file over 2 MiB, descriptor/file byte mismatch, global-major over 5 MiB or 5000 features, any search record with geometry, missing/extra required fields, unsupported `type`/`capital_status`, negative/non-integer `population_rank`, or country/partition mismatch.

- [ ] **Step 5: Prove GREEN and commit**

```bash
python3 scripts/validate_world_places_fixture_pipeline.py
python3 scripts/validate_world_places.py --runtime-only
git add scripts/build_world_places.py scripts/validate_world_places.py scripts/validate_world_places_fixture_pipeline.py
git commit -m "World Map: budget Places data contract"
```

---

### Task 2: Bound Places cache, indexes, and rendered partitions

**Files:**
- Create: `scripts/test_world_map_places_bounded_runtime.mjs`
- Modify: `world-map/3d-places.js`
- Modify: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_map_browse_performance.py`

**Interfaces:**
- Public API stays `ready`, `setVisible`, `focus`, `current`, `search`, `clear`, `status`, `loadCountry`.
- `status()` gains `renderedPartitions`, `renderedBytes`, `cachedPartitions`, `cacheBytes`, `cacheHits`, `cacheMisses`, `cacheEvictions`, `budget`.

- [ ] **Step 1: Write RED bounded-runtime regression**

Model the harness on `scripts/test_world_map_subdivision_bounded_runtime.mjs`. Use USA/DNK/FIN fixture partitions, a test cache limit of 2, select a DNK place, then load FIN. Assert cache/render count and byte budgets, DNK protection, at least one eviction, one shared `atlas-places-detail` source, removal of evicted feature ids, and survival of global-major lookup/search.

- [ ] **Step 2: Prove RED**

```bash
node scripts/test_world_map_places_bounded_runtime.mjs
```

Expected: FAIL because `loadedCountries` and `featureById` currently grow with visit history.

- [ ] **Step 3: Implement exact bounded state**

Add:

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
let cacheHits = 0;
let cacheMisses = 0;
let cacheEvictions = 0;
```

Implement budget normalization exactly as:

```js
function runtimeBudget() {
  const raw = indexPayload?.runtime_budget || {};
  return Object.fromEntries(Object.entries(DEFAULT_RUNTIME_BUDGET).map(([key, fallback]) => {
    const value = Number(raw[key]);
    return [key, Number.isFinite(value) && value > 0 ? value : fallback];
  }));
}
```

Implement touch/protection/eviction exactly around partition records `{code, descriptor, data, bytes, lastUsed}`:

```js
function touchPartition(code) {
  const state = partitionCache.get(code);
  if (!state) return null;
  state.lastUsed = ++useClock;
  return state;
}
function selectedPartition() {
  return selectedId ? partitionByFeatureId.get(selectedId) || null : null;
}
function protectedPartitions(extra = null) {
  return new Set([selectedPartition(), activeCountry, extra].filter(Boolean));
}
function evictPartition(code) {
  const state = partitionCache.get(code);
  if (!state) return false;
  for (const feature of state.data?.features || []) {
    const id = String(feature?.properties?.id || '');
    if (id) {
      partitionFeatureById.delete(id);
      partitionByFeatureId.delete(id);
    }
  }
  partitionCache.delete(code);
  cacheEvictions += 1;
  return true;
}
function cacheBytes() {
  return [...partitionCache.values()].reduce((sum, state) => sum + Number(state.bytes || 0), 0);
}
function enforceCacheBudget(extraProtected = null) {
  const budget = runtimeBudget();
  const protectedCodes = protectedPartitions(extraProtected);
  while (partitionCache.size > budget.cache_max_partitions || cacheBytes() > budget.cache_max_bytes) {
    const victim = [...partitionCache.values()]
      .filter(state => !protectedCodes.has(state.code))
      .sort((a, b) => a.lastUsed - b.lastUsed || a.code.localeCompare(b.code))[0];
    if (!victim) break;
    evictPartition(victim.code);
  }
}
```

`renderedPartitionCodes()` must return unique cached codes in order: selected partition, active country, then descending `lastUsed`; stop when adding the next partition would exceed either `rendered_max_partitions` or `cache_max_bytes`, and also reject a partition whose own bytes exceed `partition_max_bytes`. `syncDetailSource()` concatenates only those rendered partition feature arrays into the one `atlas-places-detail` source.

`loadCountry(code)` increments cache hits on resident partitions and misses before fetch, validates descriptor bytes against `partition_max_bytes`, stores/indexes one partition, sets `activeCountry`, enforces cache budget with the new code protected for that pass, then syncs the detail source. `findFeature()` checks `majorFeatureById` first and `partitionFeatureById` second. `clear()` clears selected protection and resyncs/enforces.

- [ ] **Step 4: Wire focused validation and prove GREEN**

```bash
node scripts/test_world_map_places_bounded_runtime.mjs
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_browse_performance.py
```

- [ ] **Step 5: Commit**

```bash
git add world-map/3d-places.js scripts/test_world_map_places_bounded_runtime.mjs scripts/validate_world_places.py scripts/validate_world_map_browse_performance.py
git commit -m "World Map: bound Places runtime cost"
```

---

### Task 3: Search compact records and suppress stale suggestion renders

**Files:**
- Create: `scripts/test_world_map_search_generation.mjs`
- Modify: `world-map/3d-places.js`
- Modify: `world-map/3d-search.js`
- Modify: `scripts/validate_world_places.py`

**Interfaces:**
- Search result shape: `{id, name, country, type, partition, feature}`; `feature` is resident GeoJSON or `null`.
- Diagnostics: `window.__potatoAtlasDiagnostics.search = {generation, staleRenderSuppressions}`.

- [ ] **Step 1: Write RED deferred-query regression**

Trigger input `de`, then `denmark`; resolve the newer logical search before the older one; assert only the newest result set remains rendered. Feed a geometry-free place result and assert focusing it calls `__potatoAtlasPlaces.focus(id,{country,feature:null,fit:true})` so geometry loads only on focus.

- [ ] **Step 2: Prove RED**

```bash
node scripts/test_world_map_search_generation.mjs
```

- [ ] **Step 3: Implement compact search merge and generation guard**

Build compact records once from `indexPayload.countries[*].search_records`. Merge them by stable id with global-major and cached partition records, preferring resident features when present. Preserve current exact/prefix/contains name/alias scoring and the caller limit.

In `3d-search.js` add:

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

The input listener invokes `searchAndRenderInput(event.target.value)`. Preserve the existing capturing Enter handler and `stopImmediatePropagation()` before awaiting submit.

- [ ] **Step 4: Prove GREEN and commit**

```bash
node scripts/test_world_map_search_generation.mjs
node scripts/test_world_map_subdivision_search.mjs
python3 scripts/validate_world_places.py --runtime-only
git add world-map/3d-places.js world-map/3d-search.js scripts/test_world_map_search_generation.mjs scripts/validate_world_places.py
git commit -m "World Map: harden async place search"
```

---

### Task 4: Make legacy capitals fallback-only and race-proof country hover

**Files:**
- Create: `scripts/test_world_map_hover_capital_ownership.mjs`
- Modify: `world-map/3d-hover.js`
- Modify: `scripts/validate_world_places.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Places is always promoted by `3d-panel-lifecycle.js`; therefore the fallback decision uses `potato-atlas-places-ready` and needs no timer/polling path.
- Hover diagnostics: `window.__potatoAtlasDiagnostics.hover = {generation, staleSuppressions}`.

- [ ] **Step 1: Write RED ownership/race regression**

Case A: dispatch Places-ready with `majorCount:3,error:null`; assert `capital-cities` source/layers are never created. Case B: dispatch Places-ready with `majorCount:0,error:'snapshot unavailable'`; flush promises; assert legacy source/layers initialize. For hover, fire USA then DNK mousemoves with deferred scalar promises, resolve DNK first then USA, and assert popup remains DNK. Fire mouseleave before another deferred result resolves and assert it stays closed.

- [ ] **Step 2: Prove RED**

```bash
node scripts/test_world_map_hover_capital_ownership.mjs
```

- [ ] **Step 3: Implement one owner and hover generations**

Do not call `installCapitalsWhenUseful()` directly from `install()`. Bind the country hover immediately and listen once for Places readiness:

```js
function placesCanOwnCapitals(detail = {}) {
  return Number(detail.majorCount || 0) > 0 && !detail.error;
}
window.addEventListener('potato-atlas-places-ready', event => {
  if (!placesCanOwnCapitals(event.detail || {})) void installCapitalsWhenUseful();
});
```

Keep the legacy capital constants, dataset, source/layer construction, and `window.__potatoAtlasCapitals` API for the fallback path.

Add `let hoverGeneration = 0; let staleHoverSuppressions = 0;`. On country mousemove increment and capture generation before awaiting `countryHtml`; render only if captured generation still equals current generation. On mouseleave increment generation before removing popup. Mirror counters to diagnostics.

- [ ] **Step 4: Migrate validator expectations and prove GREEN**

`validate_world_map_3d.py` must require Places-ready fallback markers rather than eager capital installation. `validate_world_places.py --runtime-only` launches the Node regression.

```bash
node scripts/test_world_map_hover_capital_ownership.mjs
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_3d.py
```

- [ ] **Step 5: Commit**

```bash
git add world-map/3d-hover.js scripts/test_world_map_hover_capital_ownership.mjs scripts/validate_world_places.py scripts/validate_world_map_3d.py
git commit -m "World Map: converge capital and hover ownership"
```

---

### Task 5: Consolidate UI lifecycle/paint ownership and coalesce layout refresh

**Files:**
- Create: `scripts/test_world_map_ui_layout_coalescing.mjs`
- Modify: `world-map/3d-ui.js`
- Modify: `world-map/3d-ui-layout.js`
- Modify: `scripts/validate_world_map_ui_layout.py`
- Modify: `scripts/validate_world_map_browse_performance.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- `3d-ui.js` consumes `potato-atlas-panel-rendered`; it does not observe `#panel`.
- `3d-ui-layout.js` exposes existing `refresh()` and uses one internal `scheduleRefresh()` microtask for mutations.

- [ ] **Step 1: Write RED coalescing/ownership regression**

Register three surfaces synchronously in a fake DOM and assert one `potato-atlas-ui-layout-change` after the microtask. Add static validator rejection for `new MutationObserver(` in `3d-ui.js` and for any `countries-fill` `fill-opacity` mutation from that file.

- [ ] **Step 2: Prove RED**

```bash
node scripts/test_world_map_ui_layout_coalescing.mjs
python3 scripts/validate_world_map_browse_performance.py
```

- [ ] **Step 3: Migrate `3d-ui.js`**

Delete its private panel lifecycle key/scheduler/observer. Keep its unique controls and styling. Subscribe to `potato-atlas-panel-rendered` to run the existing panel-open compatibility decision once per lifecycle event. Remove only `countries-fill` opacity ownership from surface tuning; keep non-conflicting styling.

- [ ] **Step 4: Implement non-recursive layout scheduling**

Add:

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

`register`, `unregister`, and `setVisible` mutate state then call `scheduleRefresh()`. During `refresh()`, set `refreshing=true`, adopt known surfaces through a private registration helper that does not schedule another refresh, perform placement once, clear `refreshing` in `finally`, increment `__potatoAtlasDiagnostics.uiLayoutRefreshes`, and emit one layout-change event.

- [ ] **Step 5: Update old validator ownership assumptions, prove GREEN, commit**

Change `validate_world_map_3d.py` from requiring `MutationObserver` in `3d-ui.js` to requiring `potato-atlas-panel-rendered` and rejecting a UI observer. Keep the existing exact-one-observer assertion on `3d-panel-lifecycle.js`.

```bash
node scripts/test_world_map_ui_layout_coalescing.mjs
python3 scripts/validate_world_map_ui_layout.py
python3 scripts/validate_world_map_browse_performance.py
python3 scripts/validate_world_map_3d.py
git add world-map/3d-ui.js world-map/3d-ui-layout.js scripts/test_world_map_ui_layout_coalescing.mjs scripts/validate_world_map_ui_layout.py scripts/validate_world_map_browse_performance.py scripts/validate_world_map_3d.py
git commit -m "World Map: consolidate UI runtime ownership"
```

---

### Task 6: Deduplicate hydrology refreshes by stable request key

**Files:**
- Create: `scripts/test_world_map_hydrology_dedup.mjs`
- Modify: `world-map/3d-physical-hydrology.js`
- Modify: `scripts/validate_world_map_hydrology.py`

**Interfaces:**
- `roundedEnvelope(precision = 2) -> [west,south,east,north]`
- `requestKey() -> string | null`
- Diagnostics: `{requestCount,deduplicatedRefreshes,abortedRequests,requestKey}`.

- [ ] **Step 1: Write RED request regression**

Enable at zoom 6 with stable bounds; first refresh causes basin+river pair. Repeat identical refresh and assert no extra HTTP calls. Change bounds by more than rounding precision, refresh, and assert one new pair. Assert dedupe/abort/request-cycle counters.

- [ ] **Step 2: Prove RED**

```bash
node scripts/test_world_map_hydrology_dedup.mjs
```

- [ ] **Step 3: Implement exact key semantics**

`roundedEnvelope(2)` returns the four current bounds rounded with `Number(value.toFixed(2))`. `requestKey()` returns `null` below `MIN_ZOOM`; otherwise it returns:

```js
JSON.stringify({
  envelope: roundedEnvelope(2),
  riverThreshold: riverThreshold(),
  zoomRegime: Math.floor(map.getZoom()),
})
```

Track `inFlightRequestKey`, `completedRequestKey`, `requestCount`, `deduplicatedRefreshes`, `abortedRequests`. Before aborting/creating a controller, return early when the key matches either in-flight or completed. Increment `abortedRequests` only when a different key replaces a live controller. Increment `requestCount` once per basin+river cycle. Set completed key only if serial/key are still current. Clear in-flight key on completion/disable.

- [ ] **Step 4: Prove GREEN and commit**

```bash
node scripts/test_world_map_hydrology_dedup.mjs
python3 scripts/validate_world_map_hydrology.py
python3 scripts/validate_world_map_ui_layout.py
git add world-map/3d-physical-hydrology.js scripts/test_world_map_hydrology_dedup.mjs scripts/validate_world_map_hydrology.py
git commit -m "World Map: deduplicate hydrology requests"
```

---

### Task 7: Reconcile render order with one style snapshot

**Files:**
- Create: `scripts/test_world_map_render_stack_reconcile.mjs`
- Modify: `world-map/3d-render-stack.js`
- Modify: `scripts/validate_world_map_render_stack.py`

**Interfaces:**
- Public render-stack API remains unchanged.
- Reconcile diagnostics/event detail gains `styleSnapshots` and `moveCount`.

- [ ] **Step 1: Write RED one-snapshot regression**

Fake style/layers, count `map.getStyle()` calls, record `moveLayer()` operations, call `reconcile('regression')`, and assert one style snapshot plus unchanged semantic slot ordering.

- [ ] **Step 2: Prove RED**

```bash
node scripts/test_world_map_render_stack_reconcile.mjs
```

- [ ] **Step 3: Implement mutable local ordering**

At reconciliation start call `styleOrder()` once. Pass the resulting array into every move helper. After each successful `moveLayer(layerId,beforeId)`, remove `layerId` from the local array and splice it immediately before `beforeId` (or append if no before id). All adjacency/index checks use this local array. Do not call `styleOrder()` inside per-layer loops. Preserve canonical semantic slots and priorities.

- [ ] **Step 4: Prove GREEN and commit**

```bash
node scripts/test_world_map_render_stack_reconcile.mjs
python3 scripts/validate_world_map_render_stack.py
python3 scripts/validate_world_map_ui_layout.py
git add world-map/3d-render-stack.js scripts/test_world_map_render_stack_reconcile.mjs scripts/validate_world_map_render_stack.py
git commit -m "World Map: reduce render stack reconciliation work"
```

---

### Task 8: Stage first-inspection promotion across paints

**Files:**
- Modify: `world-map/3d-bootstrap.js`
- Modify: `scripts/validate_world_map_browse_performance.py`

**Interfaces:**
- New internal functions: `loadInspectionBasics()`, `loadInspectionContext()`, `loadInspectionDeep()`.

- [ ] **Step 1: Write RED structural assertions**

Require those three function names, require `promoteInspection()` to call basics → `nextPaint()` → context → `nextPaint()` → deep, and assert Infrastructure/Impact modules are not in the context group.

- [ ] **Step 2: Prove RED**

```bash
python3 scripts/validate_world_map_browse_performance.py
```

- [ ] **Step 3: Implement exact promotion sequence**

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

- [ ] **Step 4: Prove GREEN and commit**

```bash
python3 scripts/validate_world_map_browse_performance.py
python3 scripts/validate_world_map_3d.py
node --check world-map/3d-bootstrap.js
git add world-map/3d-bootstrap.js scripts/validate_world_map_browse_performance.py
git commit -m "World Map: stage inspection enhancements"
```

---

### Task 9: Integrated exact-head verification

**Files:**
- Modify validators only if a focused regression is not yet launched by its canonical validator.
- Verify unchanged: `data/world-subdivisions/USA.geo.json`, `data/world-subdivisions/DNK.geo.json`.

- [ ] **Step 1: Run all focused Wave 2 regressions**

```bash
python3 scripts/validate_world_places_fixture_pipeline.py
node scripts/test_world_map_places_bounded_runtime.mjs
node scripts/test_world_map_search_generation.mjs
node scripts/test_world_map_hover_capital_ownership.mjs
node scripts/test_world_map_ui_layout_coalescing.mjs
node scripts/test_world_map_hydrology_dedup.mjs
node scripts/test_world_map_render_stack_reconcile.mjs
```

- [ ] **Step 2: Run affected architecture validators**

```bash
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_hydrology.py
python3 scripts/validate_world_map_render_stack.py
python3 scripts/validate_world_map_ui_layout.py
python3 scripts/validate_world_map_browse_performance.py
python3 scripts/validate_world_map_3d.py
python3 scripts/validate_world_map_ownership.py
```

- [ ] **Step 3: Re-run Wave 1 regressions unchanged**

```bash
node scripts/test_world_map_subdivision_bounded_runtime.mjs
node scripts/test_world_map_subdivision_freeze.mjs
node scripts/test_world_map_subdivision_multi_country.mjs
node scripts/test_world_map_subdivision_search.mjs
python3 scripts/validate_world_map_subdivisions.py
```

- [ ] **Step 4: Prove protected subdivision artifacts are unchanged**

```bash
git diff --exit-code fb4658667362bb1c6d928568cb6361c4b4c79842 -- data/world-subdivisions/USA.geo.json data/world-subdivisions/DNK.geo.json
```

Expected: exit 0.

- [ ] **Step 5: Push exact implementation head and require exact-head GitHub Actions success**

Record branch SHA. Inspect `Repository quality checks` for that exact SHA. Completion evidence requires `status=completed` and `conclusion=success`; an older run is not evidence.

- [ ] **Step 6: Commit validator wiring only if Step 1/2 exposes missing wiring**

If wiring changes were required:

```bash
git add scripts/validate_world_places.py scripts/validate_world_map_browse_performance.py scripts/validate_world_map_ui_layout.py
git commit -m "test(world-map): enforce runtime hardening contracts"
```

If no wiring changed, do not create an empty commit.

## Self-review result

- Spec coverage: all nine approved Wave 2 areas have an implementing task; Physical Water/desert aggressive unloading remains intentionally outside scope.
- Placeholder scan: no `TBD`, `TODO`, comment-only implementation stubs, or unspecified error-handling steps remain in this execution plan.
- Interface consistency: budget names, diagnostics names, public APIs, helper signatures, layer/source ids, and generation/request counters are consistent across tasks.
- Compatibility check: Places is unconditionally promoted by `3d-panel-lifecycle.js`, so capital fallback can safely wait for `potato-atlas-places-ready` without polling or a timer.
- Validator migration: the old `validate_world_map_3d.py` assumption that `3d-ui.js` must contain a `MutationObserver` is explicitly migrated in Task 5 rather than silently weakened.
