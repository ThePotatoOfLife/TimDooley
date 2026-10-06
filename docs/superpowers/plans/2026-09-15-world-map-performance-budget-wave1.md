# World Map Performance Budget Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bound World Map subdivision artifact/runtime cost and replace per-country MapLibre sources/layers with one shared subdivision rendering surface without changing selection, deep-link, inspector, search, or geography behavior.

**Architecture:** Keep independent same-origin country GeoJSON partitions, but attach exact byte metadata and a common runtime budget to the subdivision index. `3d-subdivisions.js` becomes a bounded cache/reconciler: it loads raw partition FeatureCollections into an LRU cache and composes only the highest-priority relevant partitions into one shared GeoJSON source with one hit, one line, and one label layer. Selection and deep links resolve full raw features from the cache so nested provenance/population objects remain intact.

**Tech Stack:** Browser ES modules, MapLibre GL JS runtime API, Node `.mjs` regression tests with fake map objects, Python repository validators, static GeoJSON/JSON artifacts, GitHub Actions repository-quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-15-world-map-performance-budget-wave1-design.md`

## Global Constraints

- Keep `data/world-subdivisions/USA.geo.json` and `data/world-subdivisions/DNK.geo.json` byte-for-byte unchanged.
- Preserve `?subdivision=`, `window.__potatoAtlasSubdivisions.select()`, canonical `#panel`, one-shot deep-link fitting, and country-opening behavior.
- Use one shared source `atlas-subdivisions-active` and exactly three shared layers: `atlas-subdivision-hit`, `atlas-subdivision-line`, `atlas-subdivision-label`.
- Keep subdivision search geometry-free through index `search_records`.
- Runtime budget values: `partition_max_bytes=1500000`, `rendered_max_bytes=3000000`, `rendered_max_partitions=4`, `cache_max_bytes=6000000`, `cache_max_partitions=8`.
- No polling and no additional `MutationObserver`.
- Missing population remains unknown; never coerce it to zero.
- Every behavior change follows RED → GREEN → refactor.

---

### Task 1: Make subdivision artifact budgets executable

**Files:**
- Modify: `scripts/validate_world_map_subdivisions.py`
- Modify: `data/world-subdivisions/index.json`

**Interfaces:**
- Consumes: existing subdivision partition descriptors and files under `data/world-subdivisions/`.
- Produces: top-level `runtime_budget` plus descriptor `bytes`; validator contract used by later runtime code.

- [ ] **Step 1: Write the failing validator assertions**

Add constants and checks to `scripts/validate_world_map_subdivisions.py`:

```python
EXPECTED_RUNTIME_BUDGET = {
    "partition_max_bytes": 1_500_000,
    "rendered_max_bytes": 3_000_000,
    "rendered_max_partitions": 4,
    "cache_max_bytes": 6_000_000,
    "cache_max_partitions": 8,
}

budget = index.get("runtime_budget")
if budget != EXPECTED_RUNTIME_BUDGET:
    errors.append(f"subdivision runtime budget mismatch: {budget!r}")

for partition, descriptor in partitions.items():
    path = ROOT / "data" / "world-subdivisions" / str(descriptor.get("path") or "")
    if not path.exists():
        errors.append(f"{partition}: partition path is missing")
        continue
    actual_bytes = path.stat().st_size
    if descriptor.get("bytes") != actual_bytes:
        errors.append(f"{partition}: descriptor bytes must equal {actual_bytes}")
    if actual_bytes > EXPECTED_RUNTIME_BUDGET["partition_max_bytes"]:
        errors.append(f"{partition}: partition exceeds hard byte budget")
```

- [ ] **Step 2: Run the validator and verify RED**

Run: `python scripts/validate_world_map_subdivisions.py`

Expected: FAIL because `runtime_budget` and descriptor `bytes` are absent.

- [ ] **Step 3: Add measured metadata to the index**

Update `data/world-subdivisions/index.json` without touching the GeoJSON files:

```json
"runtime_budget": {
  "partition_max_bytes": 1500000,
  "rendered_max_bytes": 3000000,
  "rendered_max_partitions": 4,
  "cache_max_bytes": 6000000,
  "cache_max_partitions": 8
}
```

Set `partitions.USA.bytes` to `389005` and `partitions.DNK.bytes` to `551315`.

- [ ] **Step 4: Re-run the validator and verify GREEN**

Run: `python scripts/validate_world_map_subdivisions.py`

Expected: PASS with all existing USA/Denmark provenance and regression checks still green.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_world_map_subdivisions.py data/world-subdivisions/index.json
git commit -m "World Map: validate subdivision artifact budgets"
```

### Task 2: Lock the fixed-cost render contract with a failing regression

**Files:**
- Create: `scripts/test_world_map_subdivision_bounded_runtime.mjs`
- Modify: `scripts/validate_world_map_subdivisions.py`

**Interfaces:**
- Consumes: `window.__potatoAtlasSubdivisions`, fake MapLibre map surface, budgeted index descriptors.
- Produces: executable regression proving one shared source/three shared layers and compatibility across USA + Denmark.

- [ ] **Step 1: Write the failing Node regression**

Create a fake map test that:

```js
await import(new URL('../world-map/3d-subdivisions.js?bounded-runtime-regression=1', import.meta.url));
await window.__potatoAtlasSubdivisions.loadPartition('USA');
await window.__potatoAtlasSubdivisions.loadPartition('DNK');

assert.deepEqual([...sources.keys()], ['atlas-subdivisions-active']);
assert.deepEqual(
  [...layers.keys()].filter(id => id.startsWith('atlas-subdivision')).sort(),
  ['atlas-subdivision-hit', 'atlas-subdivision-label', 'atlas-subdivision-line']
);
assert.equal(await window.__potatoAtlasSubdivisions.select('US-CA', {fit:false}), true);
assert.equal(await window.__potatoAtlasSubdivisions.select('DK-1083', {fit:false}), true);
```

The fixtures must include full raw nested `population`/provenance objects and assert the selection event receives those objects unchanged.

- [ ] **Step 2: Register the regression in the Python validator**

Add `BOUNDED_RUNTIME_REGRESSION` to required files and execute it alongside freeze and multi-country regressions.

- [ ] **Step 3: Run and verify RED**

Run: `node scripts/test_world_map_subdivision_bounded_runtime.mjs`

Expected: FAIL because current code creates `atlas-subdivisions-USA`, `atlas-subdivisions-DNK` and six country-specific layers.

- [ ] **Step 4: Commit the RED test**

```bash
git add scripts/test_world_map_subdivision_bounded_runtime.mjs scripts/validate_world_map_subdivisions.py
git commit -m "test(world-map): require bounded subdivision rendering"
```

### Task 3: Implement one shared subdivision rendering surface

**Files:**
- Modify: `world-map/3d-subdivisions.js`

**Interfaces:**
- Consumes: index `runtime_budget`, descriptor `bytes`, independent FeatureCollections.
- Produces: `loadPartition(partition)`, `select(id, options)`, `clear()`, `loadedPartitions()`, `status()` with fixed shared source/layers.

- [ ] **Step 1: Replace per-partition IDs with shared IDs**

Use exactly:

```js
const SOURCE_ID = 'atlas-subdivisions-active';
const HIT_ID = 'atlas-subdivision-hit';
const LINE_ID = 'atlas-subdivision-line';
const LABEL_ID = 'atlas-subdivision-label';
```

Delete `SOURCE_PREFIX`, `LINE_PREFIX`, `HIT_PREFIX`, `LABEL_PREFIX` and the four partition-specific ID helper functions.

- [ ] **Step 2: Separate raw cache loading from rendering**

Represent cache state as:

```js
const cache = new Map();
let useClock = 0;
let activePartitions = [];
let activeBytes = 0;

function touch(state) {
  state.lastUsed = ++useClock;
  return state;
}
```

`loadPartition()` fetches/validates the raw FeatureCollection, stores `{descriptor, data, bytes, lastUsed}`, and returns it. It must not create country-specific sources or layers.

- [ ] **Step 3: Install one shared source/layer set exactly once**

Create `installSharedLayers()` that adds `atlas-subdivisions-active` with an empty FeatureCollection and the three shared layers using the current paint/layout expressions. Bind mouse events once to `HIT_ID`.

The click handler resolves `event.features[0].properties.id`, finds its owning partition with `partitionForId(index, id)`, then calls `featureById(partition, id)` so selection receives the full raw feature rather than MapLibre's flattened rendered copy.

- [ ] **Step 4: Add deterministic relevance ordering**

Implement helpers:

```js
function descriptorCenter(bounds) {
  return bounds ? [(bounds.west + bounds.east) / 2, (bounds.south + bounds.north) / 2] : null;
}

function squaredDistanceToMapCenter(bounds) {
  const center = descriptorCenter(bounds);
  const mapCenter = map.getCenter?.();
  if (!center || !mapCenter) return Number.POSITIVE_INFINITY;
  const dx = center[0] - Number(mapCenter.lng);
  const dy = center[1] - Number(mapCenter.lat);
  return dx * dx + dy * dy;
}
```

Rank pending-deep-link partition first, selected partition second, then viewport-overlapping partitions by squared center distance and partition id.

- [ ] **Step 5: Compose the active FeatureCollection atomically**

Implement `reconcileActive(index)` that loads/adopts candidates until adding the next partition would exceed either `rendered_max_partitions` or `rendered_max_bytes`; mandatory selected/deep-link entries rank first. Build one merged `FeatureCollection` and call `source.setData(merged)` once per reconciliation. Update `activePartitions` and `activeBytes` only after the merged collection is ready.

- [ ] **Step 6: Preserve deep-link one-shot behavior**

`ensureRelevantPartitions()` obtains the index, calls `reconcileActive(index)`, and only then consumes `pendingDeepLinkId`. Clear the pending value before `selectSubdivision(..., {fit:true})` exactly as the existing freeze fix requires.

- [ ] **Step 7: Run fixed-cost + legacy regressions and verify GREEN**

Run:

```bash
node scripts/test_world_map_subdivision_bounded_runtime.mjs
node scripts/test_world_map_subdivision_freeze.mjs
node scripts/test_world_map_subdivision_multi_country.mjs
python scripts/validate_world_map_subdivisions.py
```

Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add world-map/3d-subdivisions.js
git commit -m "World Map: use fixed-cost subdivision rendering"
```

### Task 4: Add bounded LRU cache and diagnostics

**Files:**
- Modify: `scripts/test_world_map_subdivision_bounded_runtime.mjs`
- Modify: `world-map/3d-subdivisions.js`
- Modify: `scripts/validate_world_map_subdivisions.py`

**Interfaces:**
- Consumes: cache states from Task 3 and index runtime budget.
- Produces: deterministic eviction plus `window.__potatoAtlasSubdivisions.status()` diagnostics.

- [ ] **Step 1: Extend the regression to force eviction and verify RED**

Use synthetic index entries with small `bytes` values and a test budget such as `cache_max_partitions:2`. Load three non-protected partitions, reconcile so only the two newest/relevant remain, then assert:

```js
const status = window.__potatoAtlasSubdivisions.status();
assert.ok(status.cachedPartitions.length <= 2);
assert.ok(status.cacheEvictions >= 1);
assert.equal(typeof status.cacheHits, 'number');
assert.equal(typeof status.cacheMisses, 'number');
assert.ok(status.renderedPartitions.length <= status.budget.rendered_max_partitions);
```

Also select one partition before loading the third and assert that selected partition is never evicted.

- [ ] **Step 2: Run and verify RED**

Run: `node scripts/test_world_map_subdivision_bounded_runtime.mjs`

Expected: FAIL because `status()`/eviction counters do not yet exist.

- [ ] **Step 3: Implement LRU eviction**

Add counters `cacheHits`, `cacheMisses`, `cacheEvictions`. A cache hit calls `touch(state)` and increments hits; a fetch increments misses only once the partition is not cached.

Implement `enforceCacheBudget(index)`:

```js
const protectedIds = new Set(activePartitions);
const selectedPartition = partitionForId(index, selectedId);
const pendingPartition = partitionForId(index, pendingDeepLinkId);
if (selectedPartition) protectedIds.add(selectedPartition);
if (pendingPartition) protectedIds.add(pendingPartition);

const evictable = [...cache.entries()]
  .filter(([partition]) => !protectedIds.has(partition))
  .sort((a, b) => a[1].lastUsed - b[1].lastUsed || a[0].localeCompare(b[0]));
```

Delete oldest entries until both byte and count limits pass or no unprotected entries remain.

- [ ] **Step 4: Expose diagnostics**

Add:

```js
status() {
  return {
    selected: selectedId,
    renderedPartitions: [...activePartitions],
    renderedBytes: activeBytes,
    cachedPartitions: [...cache.keys()],
    cacheBytes: [...cache.values()].reduce((sum, state) => sum + state.bytes, 0),
    cacheHits,
    cacheMisses,
    cacheEvictions,
    budget: {...runtimeBudget},
  };
}
```

Mirror cumulative counters into `window.__potatoAtlasDiagnostics.subdivisions` when that diagnostics object exists.

- [ ] **Step 5: Re-run all subdivision regressions and validator**

Run the four commands from Task 3 Step 7.

Expected: all PASS and the bounded regression proves at least one eviction.

- [ ] **Step 6: Commit**

```bash
git add scripts/test_world_map_subdivision_bounded_runtime.mjs world-map/3d-subdivisions.js scripts/validate_world_map_subdivisions.py
git commit -m "World Map: bound subdivision partition cache"
```

### Task 5: Integrate with repository performance guardrails and verify exact head

**Files:**
- Modify: `scripts/validate_world_map_browse_performance.py`

**Interfaces:**
- Consumes: fixed source/layer IDs, bounded cache diagnostics, existing lazy-bootstrap performance validator.
- Produces: repository-level architecture guard preventing regression to per-partition style growth.

- [ ] **Step 1: Add a failing static architecture assertion**

Require the subdivision module to contain the four budget/cache markers and shared IDs, and reject the old per-partition source/layer prefixes:

```python
for token in (
    "atlas-subdivisions-active",
    "atlas-subdivision-hit",
    "atlas-subdivision-line",
    "atlas-subdivision-label",
    "cacheEvictions",
    "renderedPartitions",
):
    if token not in subdivisions:
        errors.append(f"bounded subdivision runtime missing marker: {token}")

for forbidden in ("SOURCE_PREFIX", "LINE_PREFIX", "HIT_PREFIX", "LABEL_PREFIX"):
    if forbidden in subdivisions:
        errors.append(f"subdivision runtime retains unbounded per-partition marker: {forbidden}")
```

- [ ] **Step 2: Run validator to prove the assertion is meaningful**

Before Task 3 implementation this assertion fails; after Tasks 3–4 it must pass. If the implementation is already present when this task is reached, validate the guard by temporarily evaluating it against the parent/RED commit or by confirming the dedicated bounded runtime regression already failed on the old architecture in Task 2.

- [ ] **Step 3: Run focused verification**

Run:

```bash
python scripts/validate_world_map_browse_performance.py
python scripts/validate_world_map_subdivisions.py
node scripts/test_world_map_subdivision_bounded_runtime.mjs
```

Expected: PASS.

- [ ] **Step 4: Run the repository-quality workflow on the exact branch head**

Push/open the PR and wait for the full `Repository quality` workflow associated with the exact head SHA. Inspect failed job logs if any; do not merge on partial or stale success.

- [ ] **Step 5: Review the diff against the spec**

Confirm:

- USA/DNK GeoJSON SHAs are unchanged.
- no extra source/layer per partition remains;
- no new polling/observer exists;
- deep-link/search/public API contracts are preserved;
- cache/status implementation does not leak cache details into the URL/state model.

- [ ] **Step 6: Commit any final validator-only change**

```bash
git add scripts/validate_world_map_browse_performance.py
git commit -m "World Map: enforce bounded subdivision performance"
```

- [ ] **Step 7: Merge only after exact-head full CI success**

Use the PR head SHA as the expected head at merge. After merge, fetch `main` and verify the resulting main SHA/parents before reporting completion.
