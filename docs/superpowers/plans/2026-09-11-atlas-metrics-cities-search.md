# Atlas Metrics, Cities and Unified Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the merged World Relational Atlas substantially more useful for ordinary exploration by adding one sourced cross-country metric registry, a bounded major-city runtime, unified country/city search, and metric-aware legacy Compare.

**Architecture:** Preserve the single MapLibre renderer and the newly merged working-selection/Country-Pulse/Lens architecture. Build compact same-origin presentation snapshots from authoritative acquisition inputs; runtime modules consume those snapshots without becoming canonical databases. Optional snapshot failures leave the neutral country map, country search, Trace, Time and Eye usable.

**Tech Stack:** Python 3 build scripts, World Bank WDI API, Wikidata Query Service, static JSON/GeoJSON snapshots, vanilla ES modules, MapLibre GL JS 6.9.0, GitHub Pages build pipeline.

**Spec:** `docs/superpowers/specs/2026-09-11-world-atlas-utility-design.md`

## Global Constraints

- Keep one MapLibre renderer; do not create a second map page or application state tree.
- Country identity remains canonical in `data/countries/`; generated metric/city files are presentation runtimes.
- Every displayed metric carries value, unit, period, source and display-transform metadata.
- Missing metric values remain missing/neutral; never substitute zero.
- Plot only real sourced city coordinates; do not spatialize nonspatial concepts.
- Country fill still has one semantic owner at a time through the existing Lens system.
- Metric and city snapshots are same-origin browser inputs; external APIs are build/acquisition inputs only.
- City runtime must stay below 5,000 features and 5 MB uncompressed.
- Historical Time mode must not project current metric values backward as historical truth.
- Existing capital behavior, working selection, Path, Trace, Eye and URL state must keep working.

---

### Task 1: Lock the metrics/cities/search contract before implementation

**Files:**
- Modify: `scripts/validate_world_map_3d.py`
- Create: `scripts/validate_world_map_metrics.py`
- Create: `scripts/validate_world_cities.py`

**Interfaces:**
- Metrics validator consumes `data/world-country-metrics.json` when present and validates the registry/country-observation shape.
- Cities validator consumes `data/world-cities.geo.json` when present and validates identity, coordinates, canonical ISO3 routing, uniqueness and volume limits.
- Main 3D validator requires runtime modules `3d-metrics.js`, `3d-places.js`, `3d-search.js`, and `3d-compare-metrics.js` plus their public APIs/events.

- [ ] **Step 1: Add failing 3D source-contract markers**

Require these files/APIs from `scripts/validate_world_map_3d.py`:

```python
METRICS = ROOT / "world-map" / "3d-metrics.js"
PLACES = ROOT / "world-map" / "3d-places.js"
SEARCH = ROOT / "world-map" / "3d-search.js"
COMPARE_METRICS = ROOT / "world-map" / "3d-compare-metrics.js"

fail_if_missing(metrics, (
    "__potatoAtlasMetrics", "setMetric", "forCountry", "potato-atlas-metric-change", "metric="
), "world-map/3d-metrics.js", errors)
fail_if_missing(places, (
    "__potatoAtlasPlaces", "major-cities", "potato-atlas-place-selection-change", "city="
), "world-map/3d-places.js", errors)
fail_if_missing(search_js, (
    "__potatoAtlasSearch", "find(query)", "select(result)", "City"
), "world-map/3d-search.js", errors)
fail_if_missing(compare_metrics, (
    "atlas-compare-metrics", "GDP per capita", "Life expectancy"
), "world-map/3d-compare-metrics.js", errors)
```

- [ ] **Step 2: Add focused metric validator**

Implement `scripts/validate_world_map_metrics.py` so it exits non-zero when:

```python
assert len(set(payload["metrics"])) == len(payload["metrics"])
for iso3, row in payload["countries"].items():
    assert iso3 in canonical_codes
    for metric_id, obs in row.items():
        assert metric_id in payload["metrics"]
        assert isinstance(obs.get("value"), (int, float))
        assert math.isfinite(float(obs["value"]))
        assert obs.get("period") not in (None, "")
        assert obs.get("source") not in (None, "")
```

Also require population and GDP coverage >=150 countries and reject any observation whose `source_id` conflicts with the metric registry indicator.

- [ ] **Step 3: Add focused city validator**

Implement `scripts/validate_world_cities.py` so every feature has unique `id`, canonical `iso3`, finite longitude/latitude in bounds, name/source/provenance, `minimum_zoom`, and no contradictory duplicate stable ids. Reject >5,000 features or source file size >5 MB.

- [ ] **Step 4: Verify RED**

Run:

```bash
python scripts/validate_world_map_3d.py
```

Expected: FAIL because the four runtime modules do not exist yet.

- [ ] **Step 5: Commit the failing contracts**

```bash
git add scripts/validate_world_map_3d.py scripts/validate_world_map_metrics.py scripts/validate_world_cities.py
git commit -m "test: define atlas metrics cities search contract"
```

---

### Task 2: Generate one harmonized country-metric runtime

**Files:**
- Create: `scripts/build_world_country_metrics.py`
- Generate at deploy/source refresh: `data/world-country-metrics.json`
- Modify: `scripts/build_world_demography.py`

**Interfaces:**
- Builder exports `build(out_path: Path) -> dict` and `main() -> int`.
- Browser payload shape:

```json
{
  "version": "1.0.0",
  "metrics": {
    "gdp": {"label":"GDP","indicator":"NY.GDP.MKTP.CD","unit":"current USD","transform":"log1p","direction":"neutral"}
  },
  "countries": {
    "DNK": {"gdp":{"value":1,"unit":"current USD","period":2025,"source":"World Bank WDI","source_id":"NY.GDP.MKTP.CD"}}
  }
}
```

- [ ] **Step 1: Reuse the existing WDI indicator definitions**

Import `INDICATORS` and acquisition helpers from `scripts/refresh_country_atlas.py` rather than redefining indicator ids independently.

- [ ] **Step 2: Define the runtime registry**

Registry entries cover:

```python
METRICS = {
    "population": ("Population", "people", "log1p"),
    "gdp": ("GDP", "current USD", "log1p"),
    "gdp_per_capita": ("GDP per capita", "current USD / person", "log1p"),
    "gdp_per_capita_ppp": ("GDP per capita PPP", "current international $ / person", "log1p"),
    "real_growth": ("Real GDP growth", "percent", "diverging-zero"),
    "inflation": ("Inflation", "percent", "diverging-zero"),
    "unemployment": ("Unemployment", "percent of labour force", "bounded-percent"),
    "labour_force_participation": ("Labour-force participation", "percent age 15+", "bounded-percent"),
    "life_expectancy": ("Life expectancy", "years", "linear"),
    "fertility": ("Fertility", "births / woman", "linear"),
    "urbanization": ("Urbanization", "percent of population", "bounded-percent"),
    "poverty": ("National poverty headcount", "percent", "bounded-percent"),
    "co2_emissions": ("CO₂ emissions per capita", "t CO₂ / person", "log1p"),
    "internet_penetration": ("Internet penetration", "percent of population", "bounded-percent"),
}
```

- [ ] **Step 3: Acquire one latest comparable observation per ISO3/metric**

Use the World Bank helper with the same `mrv=5` latest-non-null rule as the country refresh. Store source as `World Bank WDI`, `source_id` as the indicator id and period as the returned year.

- [ ] **Step 4: Derive population density only from compatible inputs**

After country-facts generation, derive `population_density` as sourced population / atlas `area_km2`, mark `derived: true`, source `World Bank WDI population + atlas area snapshot`, and preserve both component periods/source fields.

- [ ] **Step 5: Add deterministic coverage/domain metadata**

For each metric store `coverage`, observed min/max and 2nd/98th percentile display domain. Raw values remain unchanged.

- [ ] **Step 6: Make the existing demography build emit metrics beside its output**

When `ATLAS_DEMOGRAPHY_OUT=_site/data/world-country-demography.json`, call the metrics builder with `_site/data/world-country-metrics.json`. If WDI acquisition fails, log the failure and fall back to compatible canonical WDI-shaped observations; refuse to fabricate missing values.

- [ ] **Step 7: Validate and commit**

Run the metric validator against a generated snapshot in CI/build context, then commit builder + integration.

---

### Task 3: Turn the foundation Metric Lens into the real registry-driven Metric Explorer

**Files:**
- Create: `world-map/3d-metrics.js`
- Modify: `world-map/3d-lenses.js`
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**
- `window.__potatoAtlasMetrics.setMetric(id)`
- `window.__potatoAtlasMetrics.getMetric()`
- `window.__potatoAtlasMetrics.forCountry(iso3)`
- `window.__potatoAtlasMetrics.registry`
- event `potato-atlas-metric-change`

- [ ] **Step 1: Load `../data/world-country-metrics.json` non-fatally**

Failure leaves the current neutral/population/area Lens behavior usable.

- [ ] **Step 2: Add metric values to the country source through feature state**

For the selected metric set `metricValue` and `metricHas` on canonical ISO3 polygon features. Do not mutate geometry or canonical records.

- [ ] **Step 3: Generate MapLibre expressions from registry transform/domain**

Support `log1p`, `linear`, `bounded-percent` and `diverging-zero`; missing values use the neutral unknown fill. Legend text always shows metric name, unit, coverage, observation-period rule and clipping/domain method.

- [ ] **Step 4: Replace duplicated Metric options in `3d-lenses.js`**

When Lens family `metric` is chosen, populate options from `__potatoAtlasMetrics.registry`; selecting an option delegates to `setMetric` and the Lens module remains the sole fill owner.

- [ ] **Step 5: Add inspector/Pulse augmentation**

When a metric is active, append one compact selected-metric row to Country Pulse with value, unit, period, source, world rank and coverage. Never label rank as best/worst.

- [ ] **Step 6: Respect Time mode**

On non-current `atlas-time-change`, neutralize metric fill and show `Historical metric view unavailable`; restore current metric state when Time returns to current.

- [ ] **Step 7: Persist `metric=<id>` and verify**

Unknown ids fall back safely. Run 3D + metric validators and commit.

---

### Task 4: Generate a bounded major-city runtime

**Files:**
- Create: `scripts/build_world_cities.py`
- Generate at deploy/source refresh: `data/world-cities.geo.json`
- Modify: `scripts/build_world_demography.py`

**Interfaces:**
- Builder exports `build(out_path: Path) -> dict` and `main() -> int`.
- Output is GeoJSON FeatureCollection with feature properties:

```json
{"id":"wd:Q60","name":"New York City","iso3":"USA","population":0,"population_period":"2020","source":"Wikidata","source_id":"Q60","capital":false,"minimum_zoom":3.8,"tier":2}
```

The example population `0` is schema illustration only; missing population remains absent.

- [ ] **Step 1: Start with the committed `data/world-capitals.geo.json` baseline**

Every canonical capital point remains available even if Wikidata acquisition fails. Preserve its source string and mark `capital: true` only when the current capital runtime identifies it as primary/current.

- [ ] **Step 2: Acquire Wikidata settlements in one bounded query**

Query settlements with country ISO3, coordinate and population; retrieve enough high-population rows to include all >=500,000 inhabitants and a candidate pool for per-country top-two additions. Use stable `wd:QID` ids and English labels. Network failure must leave the capital baseline rather than fail the entire map build.

- [ ] **Step 3: Deduplicate and choose bounded features**

Union capitals + all >=500k settlements + up to two highest-population additional non-capitals per canonical ISO3 from the acquired candidate pool. Merge obvious capital duplicates by country/name/coordinate proximity when a Wikidata id is unavailable.

- [ ] **Step 4: Assign visibility tiers**

Use deterministic `minimum_zoom`: very large cities/capitals at regional zoom, >=1m at intermediate zoom, >=500k/top-two at country zoom. These thresholds are display rules, not data claims.

- [ ] **Step 5: Enforce limits and validate**

Reject >5,000 features, >5 MB output, out-of-range coordinates, unknown canonical ISO3 and duplicate stable ids. Commit builder/integration.

---

### Task 5: Render and inspect major cities without clutter

**Files:**
- Create: `world-map/3d-places.js`
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**
- `window.__potatoAtlasPlaces.focus(id)`
- `window.__potatoAtlasPlaces.get(id)`
- `window.__potatoAtlasPlaces.forCountry(iso3)`
- `window.__potatoAtlasPlaces.visible`
- event `potato-atlas-places-ready`
- event `potato-atlas-place-selection-change`

- [ ] **Step 1: Load city GeoJSON after core readiness**

Failure keeps the existing capital layer and country map usable.

- [ ] **Step 2: Add MapLibre sources/layers**

Use one GeoJSON source plus circle hit layer and symbol label layers; filter with per-feature `minimum_zoom`/tier and MapLibre collision handling. Avoid DOM markers.

- [ ] **Step 3: Add a single `Major cities` control through `__potatoAtlasLayerRegistry`**

Do not add a new permanent top-bar button.

- [ ] **Step 4: Add city inspector and URL state**

Clicking a city opens name, country, population + period/source, capital flag, coordinate provenance and `Open country`; persist `city=<stable-id>` without forcing country selection.

- [ ] **Step 5: Restore city URL safely and verify**

Unknown ids clear `city=` without breaking boot. Run city + 3D validators and commit.

---

### Task 6: Replace country-only search with unified country/city search

**Files:**
- Create: `world-map/3d-search.js`
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**
- `window.__potatoAtlasSearch.find(query)` returns ranked `{type,id,label,detail}` records.
- `window.__potatoAtlasSearch.select(result)` routes countries to `window.goCountry(iso3)` and cities to `__potatoAtlasPlaces.focus(id)`.

- [ ] **Step 1: Build the search index from canonical countries + loaded places**

Index country names/official names/ISO2/ISO3 and city name/country/aliases.

- [ ] **Step 2: Reuse the existing top search input**

Replace its datalist options with disambiguated labels such as `Denmark · Country` and `Copenhagen · City · Denmark`. Do not create a second search box.

- [ ] **Step 3: Intercept Enter only when unified search resolves a result**

Use a capture-phase listener so city selection prevents the legacy country-only handler; unresolved queries fall through to legacy behavior.

- [ ] **Step 4: Keep keyboard/mobile behavior**

`/` still focuses search; Enter selects; city focus uses a readable zoom and opens the normal inspector.

- [ ] **Step 5: Verify and commit**

Run main 3D validator plus city validator.

---

### Task 7: Make legacy Compare consume the same metric registry

**Files:**
- Create: `world-map/3d-compare-metrics.js`
- Modify: `world-map/3d-bootstrap.js`

**Interfaces:**
- Reads current legacy `compare=` countries and `__potatoAtlasMetrics.registry`.
- Injects `.atlas-compare-metrics` into the Compare inspector without changing the four-country cap.

- [ ] **Step 1: Default to population, GDP, GDP per capita, growth, unemployment and life expectancy**

All values come from `__potatoAtlasMetrics.forCountry(iso3)`.

- [ ] **Step 2: Add a compact metric chooser**

Changing rows does not change country membership or active Lens.

- [ ] **Step 3: Render value, unit, period and source cue for every cell**

Use `—` for missing data; optional highest/lowest emphasis is descriptive only.

- [ ] **Step 4: Re-render when Compare or metric runtime changes**

Observe panel/URL changes using the existing mutation/event style without body-wide observers.

- [ ] **Step 5: Verify and commit**

Run 3D + metric validators.

---

### Task 8: Final integration, runtime contract and deployment verification

**Files:**
- Modify: `data/world-map-3d-runtime.json`
- Modify: `scripts/validate_site_shell.py` only if build parity needs explicit new-file assertions.

**Interfaces:**
- Runtime contract becomes the source of truth for metrics/cities/search/Compare ownership and future entity growth.

- [ ] **Step 1: Update runtime contract**

Document the metric registry, places/cities module, unified search, metric-aware Compare, URL parameters, Time boundary and next physical-node priority.

- [ ] **Step 2: Run source validators**

```bash
python scripts/validate_world_map_metrics.py
python scripts/validate_world_cities.py
python scripts/validate_world_map_3d.py
python scripts/validate_world_map_pathfinder.py
python scripts/validate_world_map_entity_trace.py
```

Expected: all Atlas-specific checks pass.

- [ ] **Step 3: Run PR CI**

Require Atlas expansion and Public navigation to pass; require every Atlas/source/structure/content step inside Atlas integrity to pass. If the known repository-wide web-audit enforcement still fails only on its pre-existing broken-route baseline with zero generated-route regressions, report it separately rather than weakening the audit.

- [ ] **Step 4: Review the PR diff for async selection/search races and stale URL state**

Specifically test that rapid city/country search changes cannot paint or inspect the previous result after a newer selection becomes active.

- [ ] **Step 5: Merge only the verified head**

Use expected-head SHA protection and squash the implementation after review.
