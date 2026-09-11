# Atlas Country Pulse Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn ordinary country clicks into a persistent multi-country working set with an immediately useful Country Pulse, automatic bounded relationships, and a simple Lens system for alignment, alliances, religion, and metrics.

**Architecture:** Keep the existing single MapLibre renderer. `3d-app.js` remains the owner of country-selection state and relationship rendering; `3d-selection-ui.js` becomes the selection-strip surface; new focused modules own Country Pulse enrichment and Lens coloring. Existing Compare/Trace behavior remains temporarily available behind compatibility APIs until the new working-set behavior is verified.

**Tech Stack:** Static HTML, vanilla ES modules, MapLibre GL JS 6.9.0, same-origin JSON runtime snapshots, Python source validators.

**Spec:** `docs/superpowers/specs/2026-09-11-world-atlas-country-pulse-lenses-design.md`

## Global Constraints

- Preserve one MapLibre renderer; do not create another map page or renderer.
- Country selection must be toggle-by-click with no modifier keys.
- Selection outlines remain independent from Lens fill colors.
- Project North/West/East/South alignment remains explicitly interpretive and separate from empirical memberships.
- Religion remains descriptive demographic context and must not imply political loyalty or behavior.
- No fabricated money/trade/debt values or fake coordinates.
- Optional modules/data failures must leave the core country map usable.
- Red/green flow semantics are reserved for sourced direction, not moral good/bad.

---

### Task 1: Lock the new interaction contract in validation

**Files:**
- Modify: `scripts/validate_world_map_3d.py`

**Interfaces:**
- Consumes: existing source files and marker-based validation style.
- Produces: failing checks for `selectedCodes`, active-country selection, auto relations, Country Pulse module, Lens module, and updated selection strip.

- [ ] **Step 1: Write failing source-contract checks**

Add required markers so validation expects:

```python
fail_if_missing(app, (
    "selectedCodes",
    "function toggleCountrySelection",
    "function automaticRelationData",
    "searchParams.set('selected'",
    "activeCode",
), "world-map/3d-app.js", errors)

fail_if_missing(selection_ui, (
    "selection-chip",
    "data-country-code",
    "clearAll",
), "world-map/3d-selection-ui.js", errors)

PULSE = ROOT / "world-map" / "3d-country-pulse.js"
LENSES = ROOT / "world-map" / "3d-lenses.js"
```

Require both files to exist and contain stable public markers:

```python
fail_if_missing(pulse, (
    "Country Pulse",
    "GDP per capita",
    "Inflation",
    "Unemployment",
    "__potatoAtlasCountryPulse",
), "world-map/3d-country-pulse.js", errors)

fail_if_missing(lenses, (
    "__potatoAtlasLenses",
    "Alignment / Axis",
    "Alliances",
    "Religion",
    "potato-atlas-lens-change",
), "world-map/3d-lenses.js", errors)
```

- [ ] **Step 2: Verify RED**

Run in CI-equivalent environment:

```bash
python scripts/validate_world_map_3d.py
```

Expected: FAIL because the new files/functions/markers do not yet exist.

- [ ] **Step 3: Commit the failing contract**

```bash
git add scripts/validate_world_map_3d.py
git commit -m "test: define country pulse atlas contract"
```

---

### Task 2: Replace ordinary single selection with a multi-country working set

**Files:**
- Modify: `world-map/3d-app.js`
- Modify: `world-map/3d-selection-ui.js`

**Interfaces:**
- Produces `window.__potatoAtlasSelection.current` with `{ code, name, selected, selectedCodes, activeCode, compareMode }`.
- Produces `window.__potatoAtlasSelection.toggle(code)`, `.activate(code)`, `.remove(code)`, `.clearAll()`.
- Preserves `window.goCountry(code)` and legacy Compare functions during transition.

- [ ] **Step 1: Add working-set state in `3d-app.js`**

Use:

```js
let selected = null;
let selectedFeature = null;
let selectedCodes = [];
```

Treat `selected` as the active country for compatibility.

- [ ] **Step 2: Implement deterministic toggle semantics**

Add:

```js
async function toggleCountrySelection(code, { fly = false } = {}) {
  const feature = featureByCode(code);
  if (!feature) return;
  if (selectedCodes.includes(code)) {
    selectedCodes = selectedCodes.filter(value => value !== code);
    setState(code, 'selected', false);
    setState(code, 'active', false);
    if (selected === code) selected = selectedCodes.at(-1) || null;
  } else {
    selectedCodes.push(code);
    setState(code, 'selected', true);
    selected = code;
  }
  for (const value of selectedCodes) setState(value, 'active', value === selected);
  selectedFeature = selected ? featureByCode(selected) : null;
  currentCanonical = selected ? await loadCanonical(selected) : null;
  if (fly && selected) fitCodes([selected]);
  updateSpatial();
  updateUrl();
  if (selected) renderCountry(); else renderWorldLanding();
  emitSelectionChange('toggle');
}
```

Add explicit activate/remove/clear helpers without requiring compare mode.

- [ ] **Step 3: Persist working selection in URL**

Use `selected=DNK,DEU,FRA` and retain `country=FRA` as active-country compatibility. Parse legacy `country=` and `compare=` into the working set when `selected=` is absent.

- [ ] **Step 4: Keep selected outlines independent of fill**

Update country paint expressions so `active` controls the strongest outline, `selected` controls secondary outline/state, and Lens modules remain free to own fill color later.

- [ ] **Step 5: Replace selection dock with chips**

`3d-selection-ui.js` renders one button per selected country:

```html
<button class="selection-chip active" data-country-code="DNK">Denmark ×</button>
```

Clicking an inactive chip activates it; its ×/remove action removes it. Add a compact `Clear` action. Do not require the inspector to be closed for the strip to exist.

- [ ] **Step 6: Verify GREEN**

Run:

```bash
python scripts/validate_world_map_3d.py
```

Expected: selection-related contract checks pass; later Pulse/Lens checks may still fail until their tasks land.

- [ ] **Step 7: Commit**

```bash
git add world-map/3d-app.js world-map/3d-selection-ui.js
git commit -m "feat: add persistent multi-country atlas selection"
```

---

### Task 3: Make relationships appear automatically on selection

**Files:**
- Modify: `world-map/3d-app.js`

**Interfaces:**
- Produces `automaticRelationData(codes)` as bounded GeoJSON for ordinary selected-country context.
- Existing explicit Trace still uses recursive `traceRelationData(selected)` when the user asks for deeper traversal.

- [ ] **Step 1: Define a deterministic immediate-edge budget**

Add constants:

```js
const AUTO_EDGES_ACTIVE = 8;
const AUTO_EDGES_OTHER = 4;
const AUTO_EDGES_TOTAL = 28;
```

- [ ] **Step 2: Rank immediate curated relationships without inventing values**

Use a stable category priority and evidence/layer signal:

```js
const AUTO_TYPE_PRIORITY = ['trade','energy','infrastructure','fiscal','economic','security','alliance','constitutional','culture'];
```

Score only display priority. Do not call it truth/confidence.

- [ ] **Step 3: Build automatic relation GeoJSON**

For each selected country, choose up to the per-country budget, deduplicate shared edges, cap the total, and emit properties including `root`, `types`, `layer`, and serialized raw edge.

- [ ] **Step 4: Wire ordinary selection to automatic edges**

`updateSpatial()` should set the `relations` source to:

```js
showRelations && selected
  ? traceRelationData(selected)
  : automaticRelationData(selectedCodes)
```

This means relationships appear by default after selection while explicit Trace remains available.

- [ ] **Step 5: Make auto edges visibly calmer than explicit Trace**

Use `mode: 'auto'` on features and a thinner/softer paint rule for automatic edges.

- [ ] **Step 6: Verify and commit**

Run `python scripts/validate_world_map_3d.py`, then commit:

```bash
git add world-map/3d-app.js
git commit -m "feat: reveal bounded country connections automatically"
```

---

### Task 4: Add a useful Country Pulse without waiting for a new backend database

**Files:**
- Create: `world-map/3d-country-pulse.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `world-map/3d-app.js` only for a small canonical-record API hook.

**Interfaces:**
- `window.__potatoAtlasCountryRecords.get(code)` returns the lazy-loaded canonical record.
- `window.__potatoAtlasCountryPulse.render()` enriches the active-country inspector.
- Consumes `window.__potatoAtlasSelection.current`, `window.__potatoAtlasDemography`, and canonical country records.

- [ ] **Step 1: Expose canonical country records safely**

Add:

```js
window.__potatoAtlasCountryRecords = {
  get: loadCanonical,
  peek(code) { return cache.get(code) || null; }
};
```

- [ ] **Step 2: Create metric-normalization helpers**

The Pulse must understand both refreshed WDI observations and enriched country sections.

Examples:

```js
function metric(record, id) {
  const obs = record?.observations?.[id];
  if (obs && typeof obs === 'object' && Number.isFinite(Number(obs.value))) {
    return { value:Number(obs.value), period:obs.year || obs.reference_period, source:obs.source, indicator:obs.indicator };
  }
  if (id === 'gdp' && Number.isFinite(Number(record?.economy?.gdp_current_usd_trillion))) {
    return { value:Number(record.economy.gdp_current_usd_trillion) * 1e12, period:record.economy.gdp_year, source:record.economy.source, unit:'USD' };
  }
  // equivalent explicit fallbacks for gdp_per_capita, real_growth, inflation, unemployment
  return null;
}
```

- [ ] **Step 3: Render headline metrics first**

Country Pulse should visibly show, where available:

- Population;
- GDP;
- GDP per capita;
- Growth;
- Inflation;
- Unemployment;
- Debt/GDP only when a correctly defined series exists.

Each card carries period/source text; unavailable metrics render `—` rather than disappearing.

- [ ] **Step 4: Add readable Economy, People, Connections and Projects/System summaries**

Use existing country fields such as `trade_and_value_chains`, `energy_and_resources`, `political_system`, `security_and_external_relations`, `relationships`, and `research_queue`. Do not dump raw JSON.

- [ ] **Step 5: Promote religion composition**

If demography is loaded, reuse its data and render religion near the top. Do not duplicate the existing card if `3d-demography.js` already inserted one.

- [ ] **Step 6: Load Pulse on first country interaction**

In bootstrap `promoteInspection`, load `3d-country-pulse.js` alongside Demography and Evidence.

- [ ] **Step 7: Verify and commit**

Run `python scripts/validate_world_map_3d.py`, then commit:

```bash
git add world-map/3d-country-pulse.js world-map/3d-bootstrap.js world-map/3d-app.js
git commit -m "feat: add sourced country pulse inspector"
```

---

### Task 5: Add the first Lens framework

**Files:**
- Create: `world-map/3d-lenses.js`
- Modify: `world-map/3d-bootstrap.js`
- Modify: `world-map/3d.html` only if a static top-level Lens host is cleaner than dynamic injection.

**Interfaces:**
- `window.__potatoAtlasLenses.setLens(id, option)`
- `window.__potatoAtlasLenses.getState()`
- Event: `potato-atlas-lens-change`

- [ ] **Step 1: Install one simple top-level Lens selector**

Initial Lens families:

```text
Neutral
Alignment / Axis
Alliances
Religion
Metric · Population
Metric · Area
```

Do not add separate permanent buttons per dataset.

- [ ] **Step 2: Alignment / Axis coloring**

Fetch `../data/world-relational-map.json`. Derive country categories from `project_axis.north`, `.west`, `.east`, `.south`. Apply fill colors through `map.setPaintProperty('countries-fill', 'fill-color', expression)` while preserving selection outline separately.

The legend must say `Project interpretation`.

- [ ] **Step 3: Empirical alliance coloring**

Support at least NATO, BRICS, AUKUS and Five Eyes from `empirical_memberships`. Member states receive the active color; partners use a secondary state when the dataset supplies partners; others recede.

- [ ] **Step 4: Religion coloring**

Load `world-country-demography.json` lazily. Support:

- dominant category;
- Christian share;
- Muslim share;
- Hindu share;
- Buddhist share;
- Jewish share;
- Other religions share;
- Unaffiliated share.

Use a legend and percentage gradient. Religion Lens text must state that composition does not imply loyalty/behavior.

- [ ] **Step 5: Lightweight metric Lens**

Use country feature properties for Population and Area immediately. The full WDI metric registry remains a later data-normalization task from the utility spec.

- [ ] **Step 6: URL persistence**

Persist `lens=` and `lensOption=`. Unknown ids return to Neutral safely.

- [ ] **Step 7: Verify and commit**

Run `python scripts/validate_world_map_3d.py`, then commit:

```bash
git add world-map/3d-lenses.js world-map/3d-bootstrap.js world-map/3d.html
git commit -m "feat: add atlas alignment alliance religion lenses"
```

---

### Task 6: Update runtime contract and run full verification

**Files:**
- Modify: `data/world-map-3d-runtime.json`
- Modify: `scripts/validate_site_shell.py` only if built-site checks require the new modules to be declared.

**Interfaces:**
- Runtime contract documents working selection, Country Pulse, automatic relations, and Lens framework as implemented.

- [ ] **Step 1: Update runtime architecture/status**

Document:

- working multi-country selection set;
- active country;
- automatic bounded relationship context;
- Country Pulse;
- Lens module and supported initial Lens families;
- legacy Compare retained as compatibility during transition.

- [ ] **Step 2: Run all source validators**

```bash
python scripts/validate_atlas_view_contracts.py
python scripts/validate_atlas_math_calibration.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_pathfinder.py
python scripts/validate_world_map_entity_trace.py
```

Expected: all PASS.

- [ ] **Step 3: Build and validate the site**

```bash
python scripts/build_site.py
python scripts/validate_site_shell.py
```

Expected: PASS or only already-known non-blocking diagnostics explicitly documented by the validator.

- [ ] **Step 4: Commit**

```bash
git add data/world-map-3d-runtime.json scripts/validate_site_shell.py
git commit -m "docs: record country pulse atlas runtime"
```

- [ ] **Step 5: Open PR and merge only after checks are green**

PR title:

```text
Make the World Atlas informative on click
```

PR body should summarize the selection model, Country Pulse, automatic connections, initial lenses, compatibility boundary, and validators run.
