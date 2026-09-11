# World Relational Atlas — Utility-First Expansion Design

Date: 2026-09-11
Status: approved direction, implementation design
Scope: first major usability/value expansion of `world-map/3d.html`

## 1. Goal

Increase the practical value of the 3D World Relational Atlas without redesigning the shell again or flooding it with controls.

The first implementation slice will make the atlas useful for ordinary exploration before deeper graph analysis by adding four tightly related capabilities:

1. a sourced metric explorer for countries;
2. a major-cities layer beyond capitals;
3. unified country/city search;
4. metric-aware country comparison.

The existing map-first, progressive-disclosure interface remains the governing interaction model.

## 2. Non-goals

This slice does not:

- replace MapLibre or create a second renderer;
- redesign the entire navigation shell;
- add fake coordinates for nonspatial concepts;
- add every city in the world at once;
- build the full institution/company/infrastructure graph yet;
- build scenario simulation;
- introduce graph-derived geographic coordinates;
- collapse unlike evidence into a single truth score;
- treat extrusion height as rank, value, sovereignty, holiness or importance.

Those remain later layers once the core map is more useful.

## 3. Existing foundations to preserve

The current atlas already provides:

- country polygons and representative country hubs;
- country search;
- capital-city points and labels;
- sourced population/religion presentation;
- country dimensions/profile cards;
- Compare for up to four countries;
- recursive country Trace;
- shortest-known Path;
- Time state;
- Eye/evidence inspector;
- URL state;
- progressive disclosure through the compact Tools surface;
- validators for map, path, entity trace and mathematical calibration.

The new work extends these systems rather than duplicating them.

## 4. Design principles

### 4.1 Map first

Opening the page should still look like a map, not a dashboard.

Persistent controls remain sparse. New controls belong in the existing Tools hierarchy unless they are part of search itself.

### 4.2 One canonical value, many views

The map must consume canonical country observations and generated runtime snapshots rather than invent a separate statistics database.

### 4.3 Every displayed metric carries context

A metric is not complete without:

- name;
- value;
- unit;
- observation/reference year or period;
- source;
- scaling/normalization method when used for color or height.

### 4.4 Honest spatialization

Countries, cities and other real places may be plotted when their coordinates are sourced. Nonspatial concepts remain cards, graph nodes or analytical transitions.

### 4.5 Progressive density

Cities and labels appear by zoom and importance. The world view should remain legible.

### 4.6 Small incremental modules

Prefer new focused modules and generated runtime snapshots over growing `3d-app.js` or `3d-ui.js` into monoliths.

## 5. Feature A — Metric Explorer

### 5.1 User experience

Add one `Metric` selector inside the Map section of Tools.

Initial choices:

- None / neutral map;
- Population;
- Population density;
- GDP;
- GDP per capita;
- GDP per capita PPP;
- Real GDP growth;
- Inflation;
- Unemployment;
- Labour-force participation;
- Life expectancy;
- Fertility;
- Urbanization;
- Poverty where available;
- CO2 emissions per capita;
- Internet penetration.

A metric selection does three things:

1. colors country polygons by the selected metric;
2. updates a compact map legend;
3. adds the selected metric, value, unit, year/period and source to country hover/inspection.

The existing View > Height control remains separate. Where a metric is safe for extrusion, Height gains a `Selected metric` option rather than duplicating every metric name.

### 5.2 Missing data

Missing values are visibly neutral and excluded from ranking. They must not be treated as zero.

### 5.3 Scaling

The runtime snapshot stores metric metadata including a recommended transform:

- linear;
- log1p;
- diverging around zero;
- bounded percent.

The renderer may winsorize display ranges only when the legend discloses that behavior. Raw values in the inspector remain unchanged.

### 5.4 Ranking

When a metric is active, the country inspector may show:

- world rank among countries with data;
- regional rank when region metadata is available;
- percentile.

Ranking is descriptive only and must display coverage, e.g. `12 / 187 countries with data`.

## 6. Feature B — Major Cities

### 6.1 Scope

Capitals remain a distinct semantic flag but become one subset of a broader places layer.

The first city release should target a manageable globally useful set instead of every settlement. A build-time city snapshot should include major cities selected by a transparent rule such as:

- national capitals;
- large urban populations;
- strategic ports/economic centers already referenced by the repository;
- a per-country minimum so smaller countries are not invisible.

The exact source-selection script may begin with a public structured source that supplies stable place identity, coordinates, country and population/date metadata. The generated snapshot is committed same-origin for resilient browser use.

### 6.2 City record

Each runtime city record should contain when available:

- stable id;
- name;
- country ISO3;
- latitude/longitude;
- population;
- population reference date/year;
- source;
- capital flag;
- administrative region;
- importance tier;
- minimum zoom;
- aliases where useful.

### 6.3 Visibility tiers

Recommended behavior:

- world zoom: only top global cities / major capitals;
- regional zoom: major cities;
- country zoom: additional selected cities;
- close zoom: labels may expand while still avoiding overlap.

This preserves map readability and browser performance.

### 6.4 City inspection

Clicking a city opens an inspector containing:

- city name;
- country;
- population + date/source;
- capital status;
- administrative region if available;
- coordinates/provenance;
- `Open country` action.

Later slices can attach ports, companies, institutions and infrastructure to the city.

## 7. Feature C — Unified Search

### 7.1 Search model

The existing top search input becomes a unified place search.

It should resolve:

- country common names;
- country official names where available;
- ISO2 / ISO3;
- capital names;
- major-city names;
- supported aliases.

### 7.2 Result presentation

Suggestions should disambiguate type and country, for example:

- `Denmark · Country`
- `Copenhagen · City · Denmark`
- `Georgia · Country`
- `Tbilisi · City · Georgia`

### 7.3 Navigation

Selecting a country preserves the current country-selection behavior.

Selecting a city:

1. flies/fits to the city at an appropriate zoom;
2. selects/highlights the city;
3. opens the city inspector;
4. records URL state with a stable city id.

Country and city URL state must not fight each other. A city may imply its parent country for context without turning the country into the primary selection.

## 8. Feature D — Metric-Aware Compare

### 8.1 Preserve current Compare

Compare remains limited to four countries and keeps deterministic add/remove/exit behavior.

### 8.2 Metric selection

Compare gains a compact metric checklist sourced from the same metric registry as the map.

Default comparison metrics should be a small useful set, for example:

- population;
- GDP;
- GDP per capita;
- real growth;
- unemployment;
- life expectancy.

Users can change the set without altering the underlying country selection.

### 8.3 Table behavior

Each metric row shows:

- value;
- unit;
- period;
- source cue;
- missing state when unavailable.

Optional derived display may include best/highest/lowest emphasis only when direction is neutral or explicit. The UI must not imply that higher is always better.

### 8.4 Relationship comparison

Relationship overlap/intersection is intentionally separate from statistical comparison. It can remain in the Analyze section so the Compare panel does not become conceptually mixed.

## 9. Data architecture

### 9.1 Country metric runtime

Add a generated same-origin runtime snapshot, tentatively:

`data/world-country-metrics.json`

It should be derived from canonical `data/countries/*.json` observations and contain only normalized display/runtime fields.

Suggested shape:

```json
{
  "version": "1.0.0",
  "generated_at": "...",
  "metrics": {
    "gdp": {
      "label": "GDP",
      "unit_family": "currency",
      "display_unit": "current USD",
      "transform": "log1p",
      "direction": "neutral"
    }
  },
  "countries": {
    "DNK": {
      "gdp": {
        "value": 0,
        "unit": "...",
        "period": "...",
        "source": "..."
      }
    }
  }
}
```

The build step must normalize schema variants already present in country records without overwriting the canonical records.

### 9.2 City runtime

Add a generated same-origin snapshot, tentatively:

`data/world-cities.geo.json`

This is a presentation runtime, not the canonical owner of city knowledge.

### 9.3 Metric registry

Metric display rules should live in one registry used by:

- map coloring;
- legend;
- hover;
- country inspector;
- Compare;
- optional extrusion.

Do not duplicate metric lists independently across modules.

## 10. Runtime modules

Prefer the following separation:

- `world-map/3d-metrics.js` — metric registry consumption, choropleth state, legend, hover/inspector augmentation, selected-metric API;
- `world-map/3d-places.js` — major-city source/layers, city selection, city inspector, city URL state;
- `world-map/3d-search.js` — unified searchable index over countries + cities;
- `world-map/3d-compare-metrics.js` — metric selection/rendering inside Compare;
- existing `3d-ui.js` — only integrates compact controls and summaries;
- existing `3d-app.js` — remains owner of core renderer and country selection, with only small integration hooks where required.

If inspection shows a smaller reuse path, modules may be merged, but no new file should combine unrelated concerns merely to reduce file count.

## 11. Shared browser APIs

Expose small stable APIs rather than reaching into module internals.

Tentative contracts:

- `window.__potatoAtlasMetrics`
  - `setMetric(id)`
  - `getMetric()`
  - `forCountry(iso3)`
  - `registry`
- `window.__potatoAtlasPlaces`
  - `focus(id)`
  - `get(id)`
  - `forCountry(iso3)`
  - `visible`
- `window.__potatoAtlasSearch`
  - `find(query)`
  - `select(result)`

Events should follow the existing custom-event style:

- `potato-atlas-metric-change`;
- `potato-atlas-place-selection-change`;
- `potato-atlas-places-ready`.

## 12. URL state

Add stable URL parameters only where they make a view reproducible:

- `metric=<metric-id>`;
- `city=<stable-city-id>`.

Existing country, compare, relation, trace depth, path and time parameters remain intact.

Unknown/retired metric or city ids should fail safely and return to neutral state rather than breaking boot.

## 13. Interaction hierarchy

The map should read as three ordinary user verbs:

### Explore

- search country/city;
- choose metric;
- toggle cities/places;
- select a map feature;
- inspect basic sourced facts.

### Compare

- select up to four countries;
- choose comparison metrics;
- view sourced side-by-side values.

### Investigate

- Trace;
- Path;
- relation filters;
- Time;
- Eye/evidence;
- provenance and later entity traversal.

The UI does not need literal top-level tabs named Explore/Compare/Investigate in this slice. This is the conceptual grouping that should guide control placement.

## 14. Performance

### 14.1 Initial load

Country geometry and existing core boot remain first priority.

Metrics and cities should load lazily after core readiness or when their controls/search need them.

### 14.2 City volume

The first city snapshot must remain small enough for direct GeoJSON use. If later expansion crosses a practical threshold, migrate high-volume places to vector tiles or partitioned packages rather than shipping the entire global city corpus on each visit.

### 14.3 Rendering

Use MapLibre filters, minzoom and symbol collision handling instead of creating large DOM marker sets.

## 15. Error handling and resilience

- failure to load metrics must leave the neutral country map fully usable;
- failure to load cities must leave country search and capital/country functions usable;
- city/metric modules must surface a nonfatal unavailable state rather than silently corrupting selection;
- all new browser data should prefer same-origin generated snapshots;
- external APIs remain build/acquisition inputs, not mandatory browser dependencies.

## 16. Provenance and epistemic boundaries

Metric and city values need explicit source/period metadata.

Derived values such as density and ranks must be labeled derived.

The map must distinguish:

- observed/sourced country statistics;
- derived display statistics;
- project classifications;
- graph relationships;
- symbolic/Axis navigation.

Metric color must never be reused to imply project alignment or evidence quality.

## 17. Accessibility and usability

- search suggestions must remain keyboard accessible;
- metric selector must have a readable label/title;
- choropleth must not rely on color alone: inspector + legend text always expose the numeric value;
- city points require sufficient hit targets at relevant zooms;
- mobile keeps the existing bottom inspector behavior;
- no city labels should overwhelm the map at world zoom.

## 18. Validation strategy

Extend existing validation rather than creating disconnected checks.

### 18.1 Build/data validation

Add validators that verify:

- every metric id is unique;
- every metric observation has a finite numeric value when present;
- every observation has period/source metadata or an explicit unknown marker;
- city coordinates are finite and within geographic bounds;
- city ids are unique;
- city ISO3 codes resolve to the canonical country index;
- capital flags do not create contradictory duplicate city identities.

### 18.2 Runtime/source validation

Extend `scripts/validate_world_map_3d.py` or add focused validators to assert:

- the new modules are boot-reachable;
- required public APIs/events exist;
- URL parameters are supported;
- Tools contains one metric control and one places/cities control;
- old capital-city behavior remains compatible;
- neutral map boot does not require metrics/cities.

### 18.3 Regression cases

At minimum test:

1. load neutral map with all optional snapshots present;
2. load neutral map with metrics unavailable;
3. load neutral map with cities unavailable;
4. search/select a country;
5. search/select a city;
6. select GDP and verify legend/state;
7. select a metric with missing values and verify neutral missing styling;
8. compare two to four countries with mixed metric coverage;
9. reload URL with `metric=` and `city=`;
10. exit Compare and confirm city/metric state is not accidentally cleared unless designed to be;
11. switch Time mode and ensure selected current-only metrics are not falsely presented as historical values;
12. verify mobile inspector remains usable.

## 19. Time interaction

The existing conservative Time contract takes precedence over visual convenience.

Version 1 metric behavior:

- in Current mode, show the latest canonical observation and its period;
- in historical modes, only show a metric as historical when an observation valid for/requested near that time can be selected honestly from preserved history;
- otherwise mark the metric unavailable/unknown for that historical state rather than projecting the current number backward.

City coordinates may remain visible in historical mode only as present-day location context unless the city record itself has historical validity data. The UI should not imply current population values are historical.

## 20. Implementation order

Implement in small verified slices:

### Slice 1 — Metric runtime and neutral registry

- build normalized metric snapshot;
- add metric registry/module;
- add metric selector + legend;
- add population/GDP/life-expectancy pilot metrics;
- validate.

### Slice 2 — Full first metric set

- add remaining supported World Bank/canonical observations;
- add ranking/coverage metadata;
- add selected-metric extrusion where appropriate;
- validate.

### Slice 3 — Major cities runtime

- build city snapshot;
- add zoom-tiered points/labels;
- city inspector and country handoff;
- validate.

### Slice 4 — Unified search

- replace country-only suggestion source with country + city search index;
- preserve country search behavior;
- add `city=` URL state;
- validate.

### Slice 5 — Compare metrics

- share metric registry with Compare;
- user-selected metric rows;
- source/period cues;
- mixed-coverage behavior;
- validate.

Only after these slices are stable should work proceed to real institutions, companies, ports, grids, cables, power plants and entity-aware graph traversal.

## 21. Files expected to change

Likely additions:

- `docs/superpowers/specs/2026-09-11-world-atlas-utility-design.md`
- `scripts/build_world_country_metrics.py`
- `data/world-country-metrics.json`
- city acquisition/build script under `scripts/`
- `data/world-cities.geo.json`
- `world-map/3d-metrics.js`
- `world-map/3d-places.js`
- `world-map/3d-search.js`
- `world-map/3d-compare-metrics.js`
- focused validation scripts if needed.

Likely modifications:

- `world-map/3d.html`
- `world-map/3d-bootstrap.js`
- `world-map/3d-ui.js`
- small hooks in `world-map/3d-app.js` and/or `3d-hover.js` where unavoidable;
- `scripts/validate_world_map_3d.py`
- `data/world-map-3d-runtime.json` after each implemented capability.

Exact files may be reduced during implementation if existing hooks make a smaller solution possible.

## 22. Success criteria

The first expansion is successful when a new user can:

1. type a country or major city and reach it immediately;
2. switch the world map to a sourced statistical metric and understand the legend without opening documentation;
3. click a country and see the active statistic with unit, date and source;
4. click a city and understand what/where it is and return to the country context;
5. compare up to four countries on selected sourced metrics;
6. use the page on desktop or mobile without the top bar becoming materially more cluttered;
7. reload a shared metric/city URL and recover the same state;
8. distinguish missing data from zero;
9. distinguish current observations from historical Time state;
10. continue using Trace, Path, Eye, Axis and existing capital functions without regression.

The map should feel more useful, not merely more complicated.
