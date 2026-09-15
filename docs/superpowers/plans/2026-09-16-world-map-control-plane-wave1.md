# World Map Control Plane Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the first shared World Map control-plane mechanics: antimeridian-safe spatial math, named scale bands, interaction ownership and one transient-tooltip owner.

**Architecture:** Add small dependency-light runtime modules loaded by the existing bootstrap. Start with pure functions so mathematical behavior is testable outside MapLibre, then introduce coordination APIs that domain modules can adopt incrementally. Existing fallbacks remain until migrations are behaviorally proven.

**Tech Stack:** Browser ES modules, MapLibre GL JS 6.9.0, Node.js regressions, Python validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-16-world-map-control-plane-design.md`

## Global Constraints

- Do not modify Great Book files.
- Do not create a second map renderer.
- Preserve current URL parameters and current public behavior unless a task explicitly migrates an owner.
- Keep existing compatibility behavior until the replacement is tested.
- Geography remains geographic; nonspatial mathematical layouts remain nonspatial.
- Wrapped visual world copies must resolve to one canonical semantic object.
- No production behavior change without a failing regression first.

---

### Task 1: Add the shared geospatial kernel

**Files:**
- Create: `world-map/3d-geo-kernel.js`
- Create: `scripts/test_world_map_geo_kernel.mjs`
- Create: `scripts/validate_world_map_geo_kernel.py`
- Modify: `data/world-map-3d-runtime.json`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Produces `window.__potatoAtlasGeo` and ES exports:
  - `normalizeLongitude(lng)`
  - `shortestLongitudeDelta(fromLng, toLng)`
  - `unwrapLongitude(lng, referenceLng)`
  - `minimalLongitudeInterval(longitudes, referenceLng?)`
  - `antimeridianAwareBounds(points, referenceLng?)`
  - `haversineDistanceKm(a, b)`

- [ ] **Step 1: Write the failing pure-function regression**

Assert at minimum:

```js
assert.equal(normalizeLongitude(190), -170);
assert.equal(normalizeLongitude(-190), 170);
assert.equal(shortestLongitudeDelta(170, -170), 20);
assert.equal(shortestLongitudeDelta(-170, 170), -20);
assert.equal(unwrapLongitude(-170, 170), 190);
assert.equal(unwrapLongitude(170, -170), -190);

const bounds = antimeridianAwareBounds([[170, -10], [-170, 15]]);
assert.equal(bounds.west, 170);
assert.equal(bounds.east, 190);
assert.equal(bounds.crossesAntimeridian, true);
assert.equal(bounds.spanLongitude, 20);

const distance = haversineDistanceKm([179, 0], [-179, 0]);
assert.ok(distance > 200 && distance < 225);
```

Also assert invalid/non-finite coordinate input is rejected or ignored according to the documented function contract rather than producing `NaN` bounds.

- [ ] **Step 2: Run RED**

Run:

```bash
node scripts/test_world_map_geo_kernel.mjs
```

Expected: FAIL because `world-map/3d-geo-kernel.js` does not exist yet.

- [ ] **Step 3: Implement the minimum kernel**

Use normalized longitude arithmetic rather than map-projection APIs. `minimalLongitudeInterval` sorts canonical longitudes, finds the largest circular gap, and uses the complementary arc as the smallest interval. Preserve an optional reference longitude by shifting the chosen interval by multiples of 360 until its center is nearest the reference.

Use the haversine formula with Earth mean radius `6371.0088 km`.

Expose the same frozen API on `window.__potatoAtlasGeo` when `window` exists.

- [ ] **Step 4: Run GREEN**

```bash
node scripts/test_world_map_geo_kernel.mjs
python3 scripts/validate_world_map_geo_kernel.py
```

Expected: PASS.

- [ ] **Step 5: Wire CI and runtime documentation**

Add `python scripts/validate_world_map_geo_kernel.py` alongside other World Map validation steps. Add a `geospatial_kernel` entry to `data/world-map-3d-runtime.json` documenting normalized identity, antimeridian-aware bounds and mean-Earth haversine prioritization.

- [ ] **Step 6: Commit**

```bash
git add world-map/3d-geo-kernel.js scripts/test_world_map_geo_kernel.mjs scripts/validate_world_map_geo_kernel.py data/world-map-3d-runtime.json .github/workflows/quality-checks.yml
git commit -m "World Map: add antimeridian-safe geospatial kernel"
```

---

### Task 2: Migrate subdivision spatial prioritization to the kernel

**Files:**
- Create: `scripts/test_world_map_subdivision_wrap_math.mjs`
- Modify: `world-map/3d-subdivisions.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `scripts/validate_world_map_subdivisions.py`

**Interfaces:**
- Consumes `window.__potatoAtlasGeo`.
- `3d-panel-lifecycle.js` loads Geo Kernel before subdivisions may be promoted.

- [ ] **Step 1: Write RED regression**

Extract/test the partition-priority helper behavior with viewport/map center near `179°E`. A partition descriptor centered at `179°W` must rank as geographically near, not ~358 degrees away. Also verify viewport overlap can represent descriptors whose unwrapped east longitude is greater than 180.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_subdivision_wrap_math.mjs
```

Expected: FAIL because subdivisions currently use raw longitude/latitude degree differences and non-wrapped overlap comparisons.

- [ ] **Step 3: Implement minimum migration**

Use Geo Kernel longitude unwrapping for descriptor center and map-center comparison. Use haversine distance for ranking. Convert viewport and descriptor longitudes into a common unwrapped frame before intersection tests.

Do not change cache budgets or subdivision visibility thresholds in this task.

- [ ] **Step 4: Run GREEN**

```bash
node scripts/test_world_map_subdivision_wrap_math.mjs
python3 scripts/validate_world_map_subdivisions.py
```

- [ ] **Step 5: Commit**

```bash
git add world-map/3d-subdivisions.js world-map/3d-panel-lifecycle.js scripts/test_world_map_subdivision_wrap_math.mjs scripts/validate_world_map_subdivisions.py
git commit -m "World Map: make subdivision spatial math wrap-safe"
```

---

### Task 3: Add named scale bands and hysteresis

**Files:**
- Create: `world-map/3d-scale.js`
- Create: `scripts/test_world_map_scale_contract.mjs`
- Create: `data/world-map-scale-contract.json`
- Create: `scripts/validate_world_map_scale_contract.py`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-places.js`
- Modify: `world-map/3d-subdivisions.js`

**Interfaces:**
- Produces `window.__potatoAtlasScale`:
  - `bandForZoom(zoom)`
  - `atLeast(band, zoom?)`
  - `threshold(capability, phase)`
  - `transition(previousBand, zoom)` with contract-defined hysteresis

- [ ] **Step 1: Write RED tests for named boundaries and hysteresis**

The test must prove that zoom jitter immediately around a boundary does not repeatedly toggle bands and that Places/subdivision thresholds are read from the contract rather than duplicated magic numbers.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_scale_contract.mjs
```

- [ ] **Step 3: Implement scale runtime and migrate the first consumers**

Keep current visible behavior approximately stable: subdivisions begin in the regional/country transition near existing 3.4 semantics; detailed Places near existing 4.2 semantics; labels remain separately controlled. The improvement is ownership and hysteresis, not a visual redesign.

- [ ] **Step 4: Run GREEN**

```bash
node scripts/test_world_map_scale_contract.mjs
python3 scripts/validate_world_map_scale_contract.py
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_subdivisions.py
```

- [ ] **Step 5: Commit**

```bash
git add world-map/3d-scale.js data/world-map-scale-contract.json scripts/test_world_map_scale_contract.mjs scripts/validate_world_map_scale_contract.py world-map/3d-panel-lifecycle.js world-map/3d-places.js world-map/3d-subdivisions.js
git commit -m "World Map: centralize scale thresholds"
```

---

### Task 4: Add interaction arbitration without migrating every domain module

**Files:**
- Create: `world-map/3d-interaction-router.js`
- Create: `scripts/test_world_map_interaction_router.mjs`
- Create: `scripts/validate_world_map_interaction_router.py`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-places.js`
- Modify: `world-map/3d-subdivisions.js`
- Modify: `world-map/3d-spatial-overlays.js`

**Interfaces:**
- Produces `window.__potatoAtlasInteraction`:
  - `register(owner, config)`
  - `unregister(owner)`
  - `resolve(point, kind)`
  - `state()`

- [ ] **Step 1: Write RED semantic-priority regression**

Provide overlapping fake rendered features representing country, subdivision, place and spatial overlay. Assert place wins ordinary click, subdivision wins when no place exists, and registered priority rather than MapLibre render order determines the result.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_interaction_router.mjs
```

- [ ] **Step 3: Implement router and migrate bounded consumers**

Migrate Places, subdivisions and spatial overlays first. Keep `__potatoAtlasOverlayHandled` as fallback for yet-unmigrated country/legacy handlers. Do not remove it in this task.

- [ ] **Step 4: Run GREEN**

```bash
node scripts/test_world_map_interaction_router.mjs
python3 scripts/validate_world_map_interaction_router.py
python3 scripts/validate_world_map_3d.py
```

- [ ] **Step 5: Commit**

```bash
git add world-map/3d-interaction-router.js world-map/3d-places.js world-map/3d-subdivisions.js world-map/3d-spatial-overlays.js scripts/test_world_map_interaction_router.mjs scripts/validate_world_map_interaction_router.py world-map/3d-panel-lifecycle.js
git commit -m "World Map: centralize interaction priority"
```

---

### Task 5: Add one transient-tooltip owner and migrate country hover first

**Files:**
- Create: `world-map/3d-tooltip.js`
- Create: `scripts/test_world_map_tooltip_lifecycle.mjs`
- Create: `scripts/validate_world_map_tooltip.py`
- Modify: `world-map/3d-hover.js`
- Modify: `world-map/3d-panel-lifecycle.js`
- Modify: `world-map/3d-boot-guard.js`

**Interfaces:**
- Produces `window.__potatoAtlasTooltip`:
  - `show(owner, lngLat, html, generation?)`
  - `clear(owner?)`
  - `invalidate(reason)`
  - `nextGeneration(owner)`
  - `state()`

- [ ] **Step 1: Write RED lifecycle regression**

Assert a transient tooltip is cleared/invalidated by drag start, zoom start and projection change; an older async generation cannot reopen or move the tooltip; persistent click-owned popups are outside this service.

- [ ] **Step 2: Run RED**

```bash
node scripts/test_world_map_tooltip_lifecycle.mjs
```

- [ ] **Step 3: Implement service and migrate country hover**

Country hover must stop owning its own transient MapLibre Popup. Keep the boot-guard drag CSS fallback for other hover modules until they migrate.

- [ ] **Step 4: Run GREEN**

```bash
node scripts/test_world_map_tooltip_lifecycle.mjs
node scripts/test_world_map_hover_artifacts.mjs
python3 scripts/validate_world_map_tooltip.py
python3 scripts/validate_world_map_browse_performance.py
```

- [ ] **Step 5: Commit**

```bash
git add world-map/3d-tooltip.js world-map/3d-hover.js world-map/3d-panel-lifecycle.js world-map/3d-boot-guard.js scripts/test_world_map_tooltip_lifecycle.mjs scripts/validate_world_map_tooltip.py
git commit -m "World Map: centralize transient country hover"
```

---

### Task 6: Wave verification and roadmap update

**Files:**
- Modify: `docs/WORLD-MAP-ROADMAP.md`
- Modify as needed: `scripts/validate_world_map_source.py`

- [ ] **Step 1: Run the focused World Map suite**

```bash
python3 scripts/validate_world_map_geo_kernel.py
python3 scripts/validate_world_map_scale_contract.py
python3 scripts/validate_world_map_interaction_router.py
python3 scripts/validate_world_map_tooltip.py
python3 scripts/validate_world_map_subdivisions.py
python3 scripts/validate_world_places.py --runtime-only
python3 scripts/validate_world_map_3d.py
python3 scripts/validate_world_map_source.py
python3 scripts/validate_world_map_browse_performance.py
python3 scripts/stability_audit.py
```

- [ ] **Step 2: Update roadmap checkboxes only for behavior actually proven green**

Do not mark later Inspector Router/style/UI convergence work complete.

- [ ] **Step 3: Review branch diff for accidental Great Book/content changes**

Expected: no Great Book chapter payload changes.

- [ ] **Step 4: Commit final roadmap/validator convergence**

```bash
git add docs/WORLD-MAP-ROADMAP.md scripts/validate_world_map_source.py
git commit -m "World Map: record control-plane wave 1"
```
