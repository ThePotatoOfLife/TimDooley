# Atlas Spatial Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current implementation-oriented 3D Atlas control shell with the approved spatial semantic navigation system: World on the left, Relations on the right, Time on the bottom, Axis on the top, plus contextual selection actions and removable active-state chips.

**Architecture:** Preserve MapLibre, existing data contracts, current analytical modules, URL state, and the core-first lazy loader. Add one semantic capability registry as the integration boundary, then migrate existing feature modules from ad-hoc DOM injection into registry providers. A new spatial navigation controller renders zone drawers from that registry, while Time, Axis, selection context, chips, and advanced visual settings remain focused adapters over existing domain APIs rather than replacements for them.

**Tech Stack:** Vanilla ES modules/DOM, MapLibre GL 6.9.0, JSON runtime contracts, Python static/runtime validators, GitHub Pages static build.

**Spec:** `docs/superpowers/specs/2026-09-11-atlas-spatial-navigation-design.md`

## Global Constraints

- The stable semantic grammar is: **World — What is there? Relations — What connects it? Time — How did it change? Axis — How are we interpreting or transforming it? Selection context — What can I do with the thing I just clicked?**
- Search remains available as a shortcut but is not the primary navigation model.
- The map remains visually primary.
- The normal UI exposes meaning, not rendering mechanics.
- Active map state is always visible and removable.
- Core-first lazy loading and current diagnostics/deduplication through `window.__potatoAtlasLoadModule` must remain intact.
- Empirical, derived, project-symbolic, and scenario states remain epistemically distinct.
- `Height`, `Trace depth`, generic `Layers`, and similar implementation vocabulary must not remain in the normal interaction path; they may exist only in Advanced Settings or compatibility plumbing.
- D4/world metrics never become Axis height, moral rank, political rank, or project membership.
- No threshold is generated solely from magnitude; no spiral/helix is shown without comparable dated recurrence.
- All controls remain keyboard reachable; color is never the only state cue; Escape closes the active drawer/wheel before clearing map selection.
- Mobile uses side/bottom sheets and a bottom action sheet while preserving the same semantic labels and order.
- Do not rewrite proven data/rendering modules unless the UI integration boundary requires a narrow adapter.

---

## File Structure

### New files

- `world-map/3d-capability-registry.js` — semantic capability registration, activation/deactivation, state slots, availability, and change events.
- `world-map/3d-spatial-navigation.js` — four semantic handles, World/Relations drawers, utility cluster, zone rendering, focus management, responsive sheet behavior.
- `world-map/3d-active-state.js` — active chips derived from capability, time, relation, and Axis state.
- `world-map/3d-time-rail.js` — human-facing bottom Time rail backed by `3d-time.js` state.
- `scripts/validate_atlas_spatial_navigation.py` — static integration contract for the new shell and provider registrations.

### Existing files with focused changes

- `world-map/3d.html` — replace normal top-menu shell with map-centered semantic anchors; retain temporary hidden compatibility controls while migration is incomplete.
- `world-map/3d-bootstrap.js` — load registry and spatial shell automatically after core; promote domain modules from semantic zone events.
- `world-map/3d-ui.js` — retain panel/focus/basemap utilities; remove responsibility for constructing the generic Tools accordion.
- `world-map/3d-selection-ui.js` — replace current Details/Relations/more dock with contextual country action model and mobile action sheet behavior.
- `world-map/3d-app.js` — expose renderer APIs for relations, trace expansion, compare, extrusion/display settings, and reset so semantic UI does not need to click hidden buttons.
- `world-map/3d-metric-dimensions.js` — register country metric surfaces with World categories and expose direct `setSurface()` / `clearSurface()` APIs.
- `world-map/3d-demography-facets.js` — register faith/culture surfaces instead of injecting a selector into Layers.
- `world-map/3d-networks.js` — register institutional/alliance relation modes instead of injecting a network selector.
- `world-map/3d-fields.js` — register project field lenses under Axis instead of injecting a field selector.
- `world-map/3d-axis-depth.js` — render the D1–D11 spine only inside the Axis zone and expose direct dimension state.
- `world-map/3d-axis.js` / `world-map/3d-axis-operators.js` — register North Axis / operator lenses and use the Axis zone host.
- `world-map/3d-time.js` — separate Time state from legacy controls so the new rail can own presentation.
- `world-map/3d-country-dimensions.js` / `world-map/3d-d4-observables.js` — add contextual inspector grouping and `Show on map` affordances using registry IDs.
- `world-map/3d-relation-inspector.js` — move D1–D11 strip behind an Axis section and expose plain-language relation sections first.
- `scripts/validate_world_map_3d.py` — migrate required UI markers from legacy menus to the spatial shell and keep syntax/architecture checks.
- `data/world-map-3d-runtime.json` — document the semantic navigation architecture once the migration is complete.

---

### Task 1: Semantic Capability Registry

**Files:**
- Create: `world-map/3d-capability-registry.js`
- Create: `scripts/validate_atlas_spatial_navigation.py`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `.github/workflows/atlas-check.yml`

**Interfaces:**
- Produces `window.__potatoAtlasCapabilities.register(descriptor)`.
- Produces `window.__potatoAtlasCapabilities.unregister(id)`.
- Produces `window.__potatoAtlasCapabilities.list({zone?, category?})`.
- Produces `window.__potatoAtlasCapabilities.activate(id, context?)` and `.deactivate(id, context?)`.
- Produces `window.__potatoAtlasCapabilities.get(id)` and `.getActiveState()`.
- Dispatches `potato-atlas-capability-registry-change` after registration/unregistration.
- Dispatches `potato-atlas-capability-change` after activation/deactivation with `{id, active, descriptor, state}`.
- Registry descriptors require `id`, `name`, `zone`, `category`, `kind`, `colorFamily`, `description`, `activate`, `deactivate`, `getState`; optional `stateSlot`, `lazyModule`, `epistemicLayer`, `timeSupport`, `availability`.

- [ ] **Step 1: Write the failing spatial-navigation validator for the registry contract**

Create `scripts/validate_atlas_spatial_navigation.py` with checks that initially fail because the registry does not exist:

```python
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "world-map" / "3d-capability-registry.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"

errors = []
if not REGISTRY.exists():
    errors.append("missing world-map/3d-capability-registry.js")
else:
    text = REGISTRY.read_text(encoding="utf-8")
    for marker in (
        "window.__potatoAtlasCapabilities",
        "function register",
        "function activate",
        "function deactivate",
        "potato-atlas-capability-change",
        "potato-atlas-capability-registry-change",
        "baseSurface",
        "relationModes",
        "axisLens",
    ):
        if marker not in text:
            errors.append(f"capability registry missing marker: {marker}")

bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
if "3d-capability-registry.js" not in bootstrap:
    errors.append("bootstrap does not load semantic capability registry")

for error in errors:
    print("ERROR:", error)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Run the validator and confirm it fails**

Run:

```bash
python scripts/validate_atlas_spatial_navigation.py
```

Expected: FAIL with `missing world-map/3d-capability-registry.js`.

- [ ] **Step 3: Implement the registry with state-slot semantics**

Implement a focused module shaped like:

```js
const descriptors = new Map();
const active = {
  baseSurface: null,
  worldOverlays: new Set(),
  relationModes: new Set(),
  axisLens: null,
};

const VALID_ZONES = new Set(['world','relations','time','axis','settings']);

function register(descriptor) {
  if (!descriptor?.id || !descriptor?.name || !VALID_ZONES.has(descriptor.zone)) {
    throw new Error('Invalid Atlas capability descriptor');
  }
  descriptors.set(descriptor.id, Object.freeze({...descriptor}));
  window.dispatchEvent(new CustomEvent('potato-atlas-capability-registry-change', {
    detail:{type:'register', id:descriptor.id, descriptor:descriptors.get(descriptor.id)}
  }));
  return descriptors.get(descriptor.id);
}

async function activate(id, context={}) {
  const descriptor = descriptors.get(id);
  if (!descriptor) throw new Error(`Unknown Atlas capability: ${id}`);
  const availability = typeof descriptor.availability === 'function'
    ? descriptor.availability(context)
    : {available:true};
  if (availability?.available === false) return {ok:false, reason:availability.reason || 'Unavailable'};

  if (descriptor.stateSlot === 'baseSurface' && active.baseSurface && active.baseSurface !== id) {
    await deactivate(active.baseSurface, context);
  }
  if (descriptor.stateSlot === 'axisLens' && active.axisLens && active.axisLens !== id) {
    await deactivate(active.axisLens, context);
  }
  await descriptor.activate(context);
  setActive(descriptor, true);
  emitChange(descriptor, true);
  return {ok:true};
}
```

Rules:

- one `baseSurface` at a time;
- one `axisLens` at a time;
- multiple `worldOverlays` / `relationModes` may coexist;
- registry never decides empirical truth or rendering values;
- `getActiveState()` returns serializable arrays/IDs, never raw Sets.

- [ ] **Step 4: Load the registry automatically before optional semantic modules**

In `3d-bootstrap.js`, after core map readiness and before UI providers register capabilities:

```js
await loadAfterPaint('Capability registry', './3d-capability-registry.js');
```

Record it in diagnostics exactly like other modules.

- [ ] **Step 5: Add the new validator to Atlas CI**

Add after `Validate 3D world atlas runtime`:

```yaml
- name: Validate Atlas spatial navigation
  run: python scripts/validate_atlas_spatial_navigation.py
```

- [ ] **Step 6: Run focused validation**

Run:

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
```

Expected: both PASS.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-capability-registry.js world-map/3d-bootstrap.js scripts/validate_atlas_spatial_navigation.py .github/workflows/atlas-check.yml
git commit -m "feat: add Atlas semantic capability registry"
```

---

### Task 2: Four-Zone Spatial Shell

**Files:**
- Create: `world-map/3d-spatial-navigation.js`
- Modify: `world-map/3d.html`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `world-map/3d-ui.js`
- Modify: `scripts/validate_atlas_spatial_navigation.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Produces DOM hosts `#atlasWorldZone`, `#atlasRelationsZone`, `#atlasTimeZone`, `#atlasAxisZone`.
- Produces drawer hosts `#atlasWorldDrawer`, `#atlasRelationsDrawer`.
- Produces utility host `#atlasUtilities` and settings trigger `#atlasSettingsTrigger`.
- Produces `window.__potatoAtlasSpatialUI.openZone(zone)`, `.closeZone(zone?)`, `.renderZone(zone)`, `.getOpenZone()`.
- Consumes registry `list()` and registry-change events.

- [ ] **Step 1: Extend the validator with failing shell assertions**

Add checks:

```python
HTML = ROOT / "world-map" / "3d.html"
SPATIAL = ROOT / "world-map" / "3d-spatial-navigation.js"
html = HTML.read_text(encoding="utf-8")

for marker in ('id="atlasWorldZone"','id="atlasRelationsZone"','id="atlasTimeZone"','id="atlasAxisZone"','id="atlasUtilities"'):
    if marker not in html:
        errors.append(f"spatial shell missing marker: {marker}")

if not SPATIAL.exists():
    errors.append("missing world-map/3d-spatial-navigation.js")
```

Also fail if the normal visible shell still contains summaries named `Layers`, `Trace`, `View`, or `More` outside `#atlasCompatibilityControls`.

- [ ] **Step 2: Run validator and confirm failure**

```bash
python scripts/validate_atlas_spatial_navigation.py
```

Expected: FAIL on missing zone markers/module.

- [ ] **Step 3: Restructure `3d.html` around the map**

Keep the map, status node, panel, datalist, and compatibility IDs. Replace the visible menu strip with:

```html
<header class="atlas-utility-bar">
  <div class="brand"><b>World Relational Atlas · 3D</b></div>
  <div id="atlasUtilities" class="atlas-utilities">
    <input id="search" list="country-list" placeholder="Find country…" aria-label="Find country">
    <datalist id="country-list"></datalist>
    <button id="atlasReset" title="Clear active Atlas state">Reset</button>
    <button id="atlasSettingsTrigger" aria-expanded="false">Settings</button>
  </div>
</header>

<div class="mapwrap">
  <div id="map" class="map"></div>
  <button id="atlasAxisZone" class="atlas-zone atlas-zone-axis">Axis</button>
  <button id="atlasWorldZone" class="atlas-zone atlas-zone-world">World</button>
  <button id="atlasRelationsZone" class="atlas-zone atlas-zone-relations">Relations</button>
  <button id="atlasTimeZone" class="atlas-zone atlas-zone-time">Time</button>
  <aside id="atlasWorldDrawer" class="atlas-zone-drawer" hidden></aside>
  <aside id="atlasRelationsDrawer" class="atlas-zone-drawer" hidden></aside>
  ...existing map/status/HUD nodes...
</div>
```

Retain current core-owned elements (`height`, `compare`, `interior`, `relations`, `relationType`, `traceDepth`, `fit`, `tilt`, `globe`, `world`, `timeMode`, `timeDate`, `timeDate2`, `timeNow`, menu hosts) inside:

```html
<div id="atlasCompatibilityControls" hidden aria-hidden="true">...</div>
```

until their direct consumers are migrated in later tasks.

- [ ] **Step 4: Implement the spatial controller**

`3d-spatial-navigation.js` must:

- render World/Relations category tiles from registry descriptors;
- keep only one large drawer open;
- close drawer on Escape before clearing selection;
- preserve linear DOM order for keyboard users;
- mark unavailable capabilities disabled with a readable reason;
- render human names/descriptions, not internal IDs;
- never import domain modules directly; request them through `window.__potatoAtlasLoadModule` only when a registered descriptor declares a `lazyModule` and activation needs it.

Create category rendering helpers:

```js
function descriptorsFor(zone) {
  return window.__potatoAtlasCapabilities
    .list({zone})
    .sort((a,b) => (a.order ?? 999) - (b.order ?? 999) || a.name.localeCompare(b.name));
}

function renderCategory(zone, category, descriptors) { /* tiles + child buttons */ }
function openZone(zone) { /* world/relations drawer or dispatch to time/axis host */ }
function closeZone(zone=null) { /* focus-safe close */ }
```

- [ ] **Step 5: Reduce `3d-ui.js` to utility/panel ownership**

Keep:

- `setPanel()`;
- focus-mode state for Advanced Settings;
- basemap attachment utility;
- no body-wide observer;
- no startup polling.

Remove normal-path construction of `atlasToolsMenu` and nested generic menus. Compatibility controls remain hidden and functional during migration.

- [ ] **Step 6: Bootstrap the new shell automatically**

After registry and progressive UI:

```js
await loadAfterPaint('Spatial navigation', './3d-spatial-navigation.js');
```

- [ ] **Step 7: Run validators**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
```

Expected: PASS; core compatibility markers still exist but visible generic menu markers are gone.

- [ ] **Step 8: Commit**

```bash
git add world-map/3d.html world-map/3d-spatial-navigation.js world-map/3d-bootstrap.js world-map/3d-ui.js scripts/validate_atlas_spatial_navigation.py scripts/validate_world_map_3d.py
git commit -m "feat: add four-zone Atlas navigation shell"
```

---

### Task 3: Migrate World Capabilities

**Files:**
- Modify: `world-map/3d-metric-dimensions.js`
- Modify: `world-map/3d-demography-facets.js`
- Modify: `world-map/3d-selection-ui.js`
- Modify: `world-map/3d-hover.js` only if a direct capital visibility API is missing
- Modify: `world-map/3d-bootstrap.js`
- Modify: `scripts/validate_atlas_spatial_navigation.py`

**Interfaces:**
- `window.__potatoAtlasMetricDimensions.setSurface(metricId)` and `.clearSurface()`.
- `window.__potatoAtlasDemographyFacets.set(key)` already exists and becomes registry-backed.
- `window.__potatoAtlasCapitals.setVisible(boolean)` remains the Places provider.
- World descriptors use `zone:'world'` and semantic categories exactly matching the spec.

- [ ] **Step 1: Add failing provider assertions**

Validator must require source markers for registrations:

```python
WORLD_PROVIDER_MARKERS = {
    "3d-metric-dimensions.js": ("zone:'world'", "category:'Economy'", "gdp", "internet_penetration", "renewable_electricity"),
    "3d-demography-facets.js": ("zone:'world'", "category:'Faith & culture'", "christian", "unaffiliated", "diversity"),
    "3d-selection-ui.js": ("category:'Places'", "capitals"),
}
```

Run and confirm failure.

- [ ] **Step 2: Give metric dimensions direct semantic APIs**

Refactor the existing Height selector adapter so semantic activation no longer depends on changing `#height` manually:

```js
function setSurface(metricId) {
  if (!D4_SURFACES[metricId]) return false;
  activeSemanticSurface = metricId;
  ensureExtrusionVisible();
  setD4Height(metricId);
  updateNote();
  return true;
}

function clearSurface() {
  activeSemanticSurface = null;
  restoreCoreFlatMode();
}
```

Register each supported D4 surface with human categories:

- Population → People & society
- GDP / GDP/person / growth / trade / FDI / unemployment / labour participation → Economy or People & society as specified
- life expectancy / fertility / urbanization / migration → People & society
- electricity access → Infrastructure
- net energy imports / renewable electricity → Energy & environment
- internet use → Technology & information

Each descriptor uses `stateSlot:'baseSurface'`, World family color, source/time metadata, and `activate:()=>setSurface(metricId)`.

- [ ] **Step 3: Register faith/culture facets**

Stop inserting `#religionFacetView` into a visible Layers menu. Keep it only as a compatibility element if needed during transition.

For each `FACETS` entry register:

```js
capabilities.register({
  id:`world:faith:${key}`,
  name:facet.label,
  zone:'world',
  category:'Faith & culture',
  kind:'surface',
  stateSlot:'baseSurface',
  colorFamily:'faith',
  description:'2020 religious identity composition',
  epistemicLayer:'empirical/derived',
  timeSupport:{type:'snapshot', year:2020},
  activate:()=>applyFacet(map,data,key),
  deactivate:()=>applyFacet(map,data,'off'),
  getState:()=>({active:activeFacet===key, facet:key}),
});
```

- [ ] **Step 4: Register capitals as World → Places**

Use the existing capitals API rather than another top-level button:

```js
capabilities.register({
  id:'world:places:capitals',
  name:'Capital cities',
  zone:'world',
  category:'Places',
  kind:'place',
  stateSlot:'worldOverlays',
  colorFamily:'world',
  description:'Show capital-city points and labels',
  activate:()=>window.__potatoAtlasCapitals?.setVisible(true),
  deactivate:()=>window.__potatoAtlasCapitals?.setVisible(false),
  getState:()=>({active:window.__potatoAtlasCapitals?.visible!==false}),
});
```

- [ ] **Step 5: Promote World providers when World opens**

Change bootstrap zone promotion so opening World requests only World providers:

```js
window.addEventListener('potato-atlas-zone-open', event => {
  if (event.detail?.zone !== 'world') return;
  Promise.all([
    loadAfterPaint('Metric dimensions','./3d-metric-dimensions.js'),
    loadAfterPaint('Demography facets','./3d-demography-facets.js'),
  ]);
});
```

Do not eagerly load Networks or Axis providers.

- [ ] **Step 6: Validate semantic World paths**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_country_observables.py || true
```

The last command requires a built `_site`; if unavailable in the source checkout, rely on the Atlas CI build for that validator.

Expected static checks: PASS.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-metric-dimensions.js world-map/3d-demography-facets.js world-map/3d-selection-ui.js world-map/3d-hover.js world-map/3d-bootstrap.js scripts/validate_atlas_spatial_navigation.py
git commit -m "feat: migrate World data into semantic navigation"
```

---

### Task 4: Relations Zone, Context Actions, and Expand

**Files:**
- Modify: `world-map/3d-app.js`
- Modify: `world-map/3d-networks.js`
- Modify: `world-map/3d-selection-ui.js`
- Modify: `world-map/3d-spatial-navigation.js`
- Modify: `scripts/validate_atlas_spatial_navigation.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Produce `window.__potatoAtlasRelations = {setVisible, setType, getType, expand, collapseToImmediate, getDepth, getVisible}`.
- Produce `window.__potatoAtlasCompare = {startWithCurrent, addCountry, removeCountry, clear, finish, getCodes, isActive}` while keeping legacy global functions temporarily.
- Network providers register under `zone:'relations'`, `category:'Institutions & alliances'`, `stateSlot:'relationModes'`.
- Country selection context exposes `Overview`, `Relations`, `Compare`, `Change`, `Sources`, plus secondary `Focus`.

- [ ] **Step 1: Add failing assertions for direct relation APIs and semantic network registration**

Require markers:

```python
for marker in ("window.__potatoAtlasRelations", "expand()", "collapseToImmediate", "window.__potatoAtlasCompare"):
    if marker not in app:
        errors.append(f"3d-app relation API missing: {marker}")
if "zone:'relations'" not in networks or "category:'Institutions & alliances'" not in networks:
    errors.append("empirical networks are not registered under Relations")
```

- [ ] **Step 2: Refactor core relation/trace state behind an API**

Keep existing `showRelations`, `relationType`, `traceDepth`, `updateSpatial()`, caps and URL persistence, but expose semantic methods instead of requiring DOM clicks:

```js
window.__potatoAtlasRelations = {
  setVisible(visible) { showRelations=Boolean(visible); syncRelations(); },
  setType(type='all') { relationType=validRelationType(type); syncRelations(); updateUrl(); },
  getType:()=>relationType,
  getVisible:()=>showRelations,
  getDepth:()=>traceDepth,
  expand() {
    traceDepth=Math.min(TRACE_MAX_DEPTH, traceDepth+1);
    syncRelations();
    updateUrl();
    return traceDepth;
  },
  collapseToImmediate() { traceDepth=1; syncRelations(); updateUrl(); },
};
```

`Expand` is disabled at depth 3 with a readable `Maximum expansion reached` state.

- [ ] **Step 3: Expose Compare as a contextual API**

Wrap current compare functions without changing the four-country cap:

```js
window.__potatoAtlasCompare = {
  startWithCurrent: window.addCurrentToCompare,
  addCountry: toggleCompareCountry,
  removeCountry: removeComparedCountry,
  clear: window.clearCompare,
  finish: window.leaveCompare,
  getCodes:()=>[...compareCodes],
  isActive:()=>compareMode,
};
```

Preserve `compare` URL restoration.

- [ ] **Step 4: Register networks semantically**

For each empirical network register a Relations capability. Activating one calls `applyNetwork(map, registry, id)`; deactivation calls `off`. Remove the visible injected `empiricalNetworkView` selector from normal UI.

- [ ] **Step 5: Replace country selection dock with contextual action model**

Desktop DOM order:

```text
Overview → Relations → Compare → Change → Sources → Focus
```

Use a segmented curved dock first; do not implement inaccessible free-positioned radial buttons. CSS may visually arc the segments, but DOM order remains linear.

Behavior:

- Overview opens country inspector.
- Relations loads relation providers, enables immediate relations, and opens Relations drawer.
- Compare enters contextual compare mode.
- Change opens Time zone and requests the Time module.
- Sources opens Evidence/source section.
- Focus fits country polygon.

Mobile renders the same actions in a bottom action sheet.

- [ ] **Step 6: Add `Expand` to relation context**

When relations are visible for a selected root, render one contextual `Expand connections` action. It calls `window.__potatoAtlasRelations.expand()` and changes its helper copy from `Immediate connections` → `Expanded 2 levels` → `Expanded 3 levels`.

The normal UI never says `hop` or `Trace depth`.

- [ ] **Step 7: Run validators**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_pathfinder.py
python scripts/validate_world_map_entity_trace.py
```

Expected: PASS; BFS/cycle caps remain unchanged.

- [ ] **Step 8: Commit**

```bash
git add world-map/3d-app.js world-map/3d-networks.js world-map/3d-selection-ui.js world-map/3d-spatial-navigation.js scripts/validate_atlas_spatial_navigation.py scripts/validate_world_map_3d.py
git commit -m "feat: make Relations contextual and expandable"
```

---

### Task 5: Active-State Chips and Unified Semantic State

**Files:**
- Create: `world-map/3d-active-state.js`
- Modify: `world-map/3d.html`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `world-map/3d-capability-registry.js`
- Modify: `world-map/3d-spatial-navigation.js`
- Modify: `scripts/validate_atlas_spatial_navigation.py`

**Interfaces:**
- Produce `#atlasActiveState` chip container.
- Produce `window.__potatoAtlasActiveState.refresh()` and `.clearAll()`.
- Chips consume registry state plus `__potatoAtlasTime`, `__potatoAtlasRelations`, and `__potatoAxisDepth` when present.

- [ ] **Step 1: Add failing chip assertions**

Require:

```python
for marker in ('id="atlasActiveState"', '3d-active-state.js'):
    if marker not in html + bootstrap:
        errors.append(f"active-state UI missing: {marker}")
```

- [ ] **Step 2: Add chip host to map shell**

```html
<div id="atlasActiveState" class="atlas-active-state" aria-live="polite"></div>
```

Position beneath utility bar on desktop and above Time rail/action sheet on mobile.

- [ ] **Step 3: Implement chip rendering**

`3d-active-state.js` listens to:

- `potato-atlas-capability-change`
- `atlas-time-change`
- `potato-atlas-relations-change`
- `atlas-axis-dimension-change`
- selection/compare state changes

Chip model:

```js
{id, label, family, remove()}
```

Examples:

- `GDP ×`
- `NATO ×`
- `Relations ×`
- `At 2020-01-01 ×`
- `D6 · Spiral ×`

Removing a chip calls the owning semantic API, never manipulates MapLibre layers directly.

- [ ] **Step 4: Add Clear all semantics**

`clearAll()`:

1. deactivates base surface;
2. deactivates world overlays;
3. disables relation modes;
4. returns time to Current;
5. returns Axis to D4 / no lens;
6. keeps current country selection unless user explicitly presses Reset World.

This distinction prevents `clear visual state` from unexpectedly losing selection.

- [ ] **Step 5: Bootstrap after spatial navigation**

```js
await loadAfterPaint('Active state', './3d-active-state.js');
```

- [ ] **Step 6: Validate**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-active-state.js world-map/3d.html world-map/3d-bootstrap.js world-map/3d-capability-registry.js world-map/3d-spatial-navigation.js scripts/validate_atlas_spatial_navigation.py
git commit -m "feat: show removable Atlas active-state chips"
```

---

### Task 6: Contextual Time Rail

**Files:**
- Create: `world-map/3d-time-rail.js`
- Modify: `world-map/3d-time.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `world-map/3d-spatial-navigation.js`
- Modify: `scripts/validate_atlas_spatial_navigation.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- `window.__potatoAtlasTime.getState()` remains stable.
- `window.__potatoAtlasTime.setState({mode,time,time2})` must work without legacy DOM controls.
- Add `window.__potatoAtlasTime.getAvailabilityContext()` returning at minimum `{mode, supportsHistorical, reason?}` when data context can report it.
- Produce `#atlasTimeRail` with Current / At a date / Compare dates, and reserved `Play` / `Events` affordances only when capability support exists.

- [ ] **Step 1: Add failing Time rail assertions**

Require `3d-time-rail.js`, `atlasTimeRail`, user-facing labels `Current`, `At a date`, `Compare dates`, and absence of visible `changed_between` vocabulary.

- [ ] **Step 2: Decouple `3d-time.js` from legacy controls**

Move state ownership into module variables:

```js
let currentState = urlState();

function setState(next) {
  currentState = normalizeState(next);
  setUrl(currentState);
  dispatch(currentState);
  return {...currentState};
}

window.__potatoAtlasTime = {
  getState:()=>({...currentState}),
  setState,
};
```

Legacy `timeMode/timeDate/timeDate2` listeners may remain temporarily as compatibility adapters, but are no longer required for `setState()`.

- [ ] **Step 3: Implement Time rail presentation**

The compact bottom handle says `Time` in Current mode. Opening it shows:

- Current
- At a date
- Compare dates

When a selected capability has `timeSupport:{type:'snapshot',year:2020}`, show `2020 snapshot` read-only context instead of implying a continuous historical series.

When a capability is current-only, keep Time available but explain that historical rendering is unavailable.

- [ ] **Step 4: Make Change contextual action open the rail**

`selection-ui` Change action should dispatch/open Time; it must not create a second Time UI.

- [ ] **Step 5: Preserve historical suppression semantics**

Verify `3d-fields.js`, `3d-networks.js`, religion facets, and metric surfaces continue disabling current-only visualizations in incompatible historical modes.

- [ ] **Step 6: Validate**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
```

Expected: PASS; legacy time contract markers and URL state remain intact.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-time-rail.js world-map/3d-time.js world-map/3d-bootstrap.js world-map/3d-spatial-navigation.js scripts/validate_atlas_spatial_navigation.py scripts/validate_world_map_3d.py
git commit -m "feat: replace Time menu with contextual rail"
```

---

### Task 7: Axis Zone and Vertical Spine

**Files:**
- Modify: `world-map/3d-axis-depth.js`
- Modify: `world-map/3d-fields.js`
- Modify: `world-map/3d-axis.js`
- Modify: `world-map/3d-axis-operators.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `world-map/3d-spatial-navigation.js`
- Modify: `scripts/validate_atlas_spatial_navigation.py`

**Interfaces:**
- `window.__potatoAxisDepth.setDimension(number)` remains stable.
- Axis navigator mounts under `#atlasAxisZonePanel` and is absent/hidden until Axis opens.
- Axis descriptor IDs use `axis:dimension:D1` … `axis:dimension:D11`, `axis:fields:north`, etc.
- Axis primary lens uses `stateSlot:'axisLens'` when appropriate.

- [ ] **Step 1: Add failing Axis semantic assertions**

Require human-first labels and Axis host:

```python
for label in ('North of North','Crown / Integration','Relay','Garden / Rooms','Tree / Generativity','Spiral / Change','Door / Threshold','World','Roots / Provenance','Swamp / Capture','Closure / Collapse'):
    if label not in axis_depth:
        errors.append(f"Axis human label missing: {label}")
```

Also reject a permanently visible `axisDepthNavigator` outside the Axis panel.

- [ ] **Step 2: Mount Axis navigator contextually**

Replace fixed `right:12px; top:62px` ownership with a root supplied by spatial navigation:

```js
const host = document.getElementById('atlasAxisZonePanel');
host.appendChild(root);
```

The curved/spiral geometry remains, but label order becomes `Human name` first and `D#` second.

- [ ] **Step 3: Register dimensions and project fields**

Each D level is a semantic Axis capability whose activation calls `setDimension(n)`.

Fields register as Axis lenses:

- North
- West
- East
- South
- Center
- BRICS remains empirical and should not be misclassified as project Axis; move BRICS to Relations → Institutions & alliances if it is already represented there, and remove duplicate field navigation.

- [ ] **Step 4: Register North Axis / operators**

`3d-axis.js` registers North Axis as project lens; `3d-axis-operators.js` attaches operator detail to current Axis selection instead of another floating HUD competing with the map.

- [ ] **Step 5: Keep D4 as real-world anchor**

Opening Axis defaults to current dimension; if no Axis state exists, highlight `World — D4`. Closing Axis does not alter current data surfaces.

- [ ] **Step 6: Validate**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
python scripts/validate_atlas_view_contracts.py
python scripts/validate_atlas_math_calibration.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-axis-depth.js world-map/3d-fields.js world-map/3d-axis.js world-map/3d-axis-operators.js world-map/3d-bootstrap.js world-map/3d-spatial-navigation.js scripts/validate_atlas_spatial_navigation.py
git commit -m "feat: make Axis a contextual vertical lens"
```

---

### Task 8: Contextual Inspectors and “Show on map” Discovery

**Files:**
- Modify: `world-map/3d-country-dimensions.js`
- Modify: `world-map/3d-d4-observables.js`
- Modify: `world-map/3d-evidence.js`
- Modify: `world-map/3d-relation-inspector.js`
- Modify: `world-map/3d-selection-ui.js`
- Modify: `scripts/validate_atlas_spatial_navigation.py`

**Interfaces:**
- Country inspector sections: Overview, People & society, Economy, Infrastructure & energy, Faith & culture, Relations, Change, Sources, conditional Axis.
- Metric rows use `data-atlas-capability="<registry-id>"` for Show on map.
- Relation inspector sections: About, Flow, History, Network, Axis, Sources.

- [ ] **Step 1: Add failing inspector assertions**

Require country/relation section labels and `Show on map` markers. Reject D1–D11 strip as the first visible relation content before `About`.

- [ ] **Step 2: Make country Overview concise**

Do not dump all 16 D4 metrics into the first viewport. Overview should surface a compact sample such as population, GDP/person, life expectancy, trade/GDP, electricity access, internet use, with section navigation to the full grouped vector.

- [ ] **Step 3: Add `Show on map` actions to supported metrics**

For each D4 metric with a registered surface:

```html
<button class="show-on-map" data-atlas-capability="world:economy:gdp">Show on map</button>
```

Click handler:

```js
const id = button.dataset.atlasCapability;
await window.__potatoAtlasCapabilities.activate(id,{source:'inspector'});
```

This must open no extra generic menu.

- [ ] **Step 4: Route Sources to Evidence**

Country Sources action opens existing Eye/evidence content inside the inspector section instead of requiring a separate global Eye control.

The evidence module remains independent and source-aware; only its presentation host changes.

- [ ] **Step 5: Reorder relation inspector**

Default to About with plain relation facts. Keep family inference and boundary notes. Move the current 11-button projection strip into Axis section only.

Axis section must preserve the explicit/family-supported/conditional/unmodeled distinction.

- [ ] **Step 6: Validate**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_entity_trace.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-country-dimensions.js world-map/3d-d4-observables.js world-map/3d-evidence.js world-map/3d-relation-inspector.js world-map/3d-selection-ui.js scripts/validate_atlas_spatial_navigation.py
git commit -m "feat: make Atlas inspectors contextual and discoverable"
```

---

### Task 9: Advanced Settings and Legacy-Control Retirement

**Files:**
- Modify: `world-map/3d-spatial-navigation.js`
- Modify: `world-map/3d-ui.js`
- Modify: `world-map/3d-app.js`
- Modify: `world-map/3d.html`
- Modify: `scripts/validate_atlas_spatial_navigation.py`
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Produce `#atlasSettingsPanel`.
- Produce `window.__potatoAtlasVisual = {setDisplayMode, setTilted, setProjection, resetCamera, setFocusMode, setHopLimit, getState}` or equivalent focused adapters over current core behavior.
- Normal path contains no visible `Height`, `Trace depth`, `Layers`, `View`, or `Inspect` controls.

- [ ] **Step 1: Add failing retirement assertions**

Validator should parse visible shell separately from `#atlasCompatibilityControls` and reject:

```python
FORBIDDEN_VISIBLE_COPY = ("Layers", "Trace depth", "Height ·", "Inspect", "View")
```

Require settings copy for:

- Display: 3D / color / both
- Basemap
- Globe / planar
- Tilt
- Focus mode
- Advanced hop limit
- Module orbit

- [ ] **Step 2: Expose direct visual APIs from core/UI**

Stop using hidden button clicks for normal settings. Wrap current behavior:

```js
window.__potatoAtlasVisual = {
  setDisplayMode(mode) { /* flat/color, 3d, both */ },
  setTilted(on) { map.easeTo({pitch:on ? 55 : 0, duration:500}); },
  setProjection(mode) { map.setProjection({type:mode === 'globe' ? 'globe' : 'mercator'}); },
  resetCamera:()=>resetWorld(false),
  setFocusMode:on=>window.__potatoAtlasUI?.setFocus?.(on),
  getState() { return {...}; },
};
```

Advanced hop limit may update the existing trace cap preference but may never exceed `TRACE_MAX_DEPTH = 3` until the renderer contract changes.

- [ ] **Step 3: Build compact settings panel**

Use semantic labels and grouped controls. Do not expose raw renderer IDs or implementation file names.

- [ ] **Step 4: Remove legacy controls that no longer have direct consumers**

Before deleting each compatibility node, search source for its DOM ID. Only remove when no module relies on it. If a compatibility ID remains necessary, keep it hidden and document the remaining owner in a comment.

- [ ] **Step 5: Validate**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
```

Expected: PASS and no forbidden normal-path copy.

- [ ] **Step 6: Commit**

```bash
git add world-map/3d-spatial-navigation.js world-map/3d-ui.js world-map/3d-app.js world-map/3d.html scripts/validate_atlas_spatial_navigation.py scripts/validate_world_map_3d.py
git commit -m "feat: retire legacy Atlas controls into settings"
```

---

### Task 10: Responsive, Accessibility, Runtime Contract, and Full Regression Gate

**Files:**
- Modify: `world-map/3d-spatial-navigation.js`
- Modify: `world-map/3d-selection-ui.js`
- Modify: `world-map/3d.html`
- Modify: `scripts/validate_atlas_spatial_navigation.py`
- Modify: `scripts/validate_site_shell.py`
- Modify: `data/world-map-3d-runtime.json`
- Modify: `.github/workflows/atlas-check.yml` only if final validation ordering needs adjustment

**Interfaces:**
- Desktop: side drawers, top Axis spine, bottom Time rail, curved selection dock.
- Narrow viewport: drawers become sheets, selection dock becomes bottom action sheet, one large sheet open at once.
- Escape order: close active drawer/sheet → close contextual panel → clear/reset selection only on subsequent Escape.

- [ ] **Step 1: Add failing accessibility/responsive contract checks**

Validator must require:

```python
for marker in (
    "aria-expanded",
    "aria-controls",
    "aria-live",
    "@media(max-width:900px)",
    "Escape",
    "atlas-bottom-sheet",
):
    if marker not in spatial_text + html + selection_text:
        errors.append(f"responsive/accessibility marker missing: {marker}")
```

Also check every zone button has a human-facing `aria-label` and each drawer has a labeled heading.

- [ ] **Step 2: Implement keyboard/focus behavior**

Rules:

- Enter/Space opens focused zone handle.
- Escape closes open zone first.
- Closing a drawer returns focus to its handle.
- Tab order follows World drawer category order / selection action order.
- no focus trap unless a mobile sheet is modal; if modal, release focus on close.

- [ ] **Step 3: Implement narrow-screen sheets**

At `max-width:900px`:

- World/Relations become bottom or side sheets;
- selection context becomes bottom action sheet;
- Time rail sits above selection sheet;
- Axis opens a full-height but narrow scrollable spine sheet;
- only one large sheet is open.

- [ ] **Step 4: Update built-site parity validation**

`validate_site_shell.py` must confirm the new modules are copied to `_site/world-map/` and `3d.html` references the versioned bootstrap path normally.

- [ ] **Step 5: Update runtime architecture contract**

In `data/world-map-3d-runtime.json`, document:

- semantic capability registry;
- World / Relations / Time / Axis spatial navigation;
- contextual selection actions;
- active-state chips;
- advanced settings ownership;
- legacy generic menus retired from normal path;
- lazy provider promotion preserved.

Do not change empirical or Axis data contracts.

- [ ] **Step 6: Run the complete local validation suite**

```bash
python scripts/validate_atlas_spatial_navigation.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_pathfinder.py
python scripts/validate_world_map_entity_trace.py
python scripts/validate_atlas_view_contracts.py
python scripts/validate_atlas_math_calibration.py
python scripts/build_site.py
ATLAS_DEMOGRAPHY_OUT=_site/data/world-country-demography.json python scripts/build_world_demography.py
ATLAS_D4_OUT=_site/data/world-country-observables.json python scripts/build_world_country_observables.py
python scripts/validate_world_country_observables.py
python scripts/validate_site_shell.py
```

Expected: every command PASS. If the external World Bank build is unavailable, do not waive its gate; use CI diagnostics to identify acquisition failures exactly as the current D4 pipeline does.

- [ ] **Step 7: Manual smoke test the approved interaction paths**

Verify in a browser:

```text
World → Economy → GDP
World → Faith & culture → Christian share
Relations → Institutions & alliances → NATO
Select Denmark → Relations → Expand
Select Denmark → Compare → Germany
Country Overview → Internet use → Show on map
Time with GDP active
Axis → Spiral / Change — D6
Axis → North project field
Remove every active chip one-by-one
Reload bookmarked country + relation + time + Axis states
Repeat core selection/zone actions under 900px width
```

Expected: no normal-path user needs `Layers`, `Height`, `Trace depth`, or implementation terminology.

- [ ] **Step 8: Run branch CI and inspect every check**

Push the task commit, then verify:

- Atlas integrity check
- Atlas expansion check
- Machine discoverability
- CSS namespace check

All must be green before calling the redesign complete.

- [ ] **Step 9: Commit final contract updates**

```bash
git add world-map/3d-spatial-navigation.js world-map/3d-selection-ui.js world-map/3d.html scripts/validate_atlas_spatial_navigation.py scripts/validate_site_shell.py data/world-map-3d-runtime.json .github/workflows/atlas-check.yml
git commit -m "feat: complete spatial Atlas navigation migration"
```

---

## Self-Review Results

- **Spec coverage:** Every approved design section has an implementation owner: semantic zones (Tasks 2–7), colors/categories (Tasks 2–3), active chips (Task 5), World (Task 3), Relations/Expand (Task 4), Time rail (Task 6), Axis spine (Task 7), contextual actions/inspectors/Compare (Tasks 4 and 8), search as utility (Task 2), Advanced Settings (Task 9), capability registry/state/lazy loading (Tasks 1–7), error states (Tasks 1–3), accessibility/responsive behavior (Task 10), migration/validation/runtime documentation (Tasks 9–10).
- **Placeholder scan:** No TBD/TODO/“implement later” instructions are used as plan steps. Future datasets remain future scope from the approved spec and are not implementation dependencies.
- **Type consistency:** Registry IDs and APIs are stable across tasks: `__potatoAtlasCapabilities`, `__potatoAtlasRelations`, `__potatoAtlasCompare`, `__potatoAtlasTime`, `__potatoAxisDepth`, `__potatoAtlasSpatialUI`, `__potatoAtlasActiveState`, and `__potatoAtlasVisual`. `stateSlot` values remain `baseSurface`, `worldOverlays`, `relationModes`, and `axisLens` throughout.
