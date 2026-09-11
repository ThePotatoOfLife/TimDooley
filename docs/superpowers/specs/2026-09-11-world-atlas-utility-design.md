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

### 4.2 One canonical model, many views

The frontend must not become a second canonical database.

Country identity and country dossier ownership remain in `data/countries/`. Cross-country display runtimes may be generated from the canonical country index, the repository source registry and the same authoritative acquisition definitions used by the country refresh pipeline, but the generated runtimes are explicitly presentation projections.

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

### 5.2 Metric definitions

Cross-country comparable metrics use the existing World Bank WDI indicator definitions already declared in `scripts/refresh_country_atlas.py`:

- population — `SP.POP.TOTL`;
- GDP — `NY.GDP.MKTP.CD`;
- GDP per capita — `NY.GDP.PCAP.CD`;
- GDP per capita PPP — `NY.GDP.PCAP.PP.CD`;
- real GDP growth — `NY.GDP.MKTP.KD.ZG`;
- inflation — `FP.CPI.TOTL.ZG`;
- unemployment — `SL.UEM.TOTL.ZS`;
- labour-force participation — `SL.TLF.CACT.ZS`;
- life expectancy — `SP.DYN.LE00.IN`;
- fertility — `SP.DYN.TFRT.IN`;
- urbanization — `SP.URB.TOTL.IN.ZS`;
- poverty — `SI.POV.NAHC`;
- CO2 emissions per capita — `EN.ATM.CO2E.PC`;
- internet penetration — `IT.NET.USER.ZS`.

Population density is derived at build time from the selected population observation divided by the atlas area value and is labeled `derived`.

Local/national official observations remain visible in country dossiers, but they are not substituted into a cross-country metric when currency, unit, definition or reference basis is incompatible with the metric registry.

### 5.3 Missing data

Missing values are visibly neutral and excluded from ranking. They must not be treated as zero.

### 5.4 Scaling

The runtime snapshot stores metric metadata including a display transform:

- `log1p` for highly skewed magnitude metrics such as GDP and population;
- `linear` for ordinary bounded-range metrics where appropriate;
- `diverging-zero` for signed growth metrics;
- `bounded-percent` for percentage metrics.

The renderer may winsorize the color domain to the 2nd–98th observed percentiles for readability only when the legend states that the display range is clipped. Raw inspector values remain unchanged.

### 5.5 Ranking

When a metric is active, the country inspector may show:

- world rank among countries with data;
- regional rank when region metadata is available;
- percentile.

Ranking is descriptive only and must display coverage, e.g. `12 / 187 countries with data`.

## 6. Feature B — Major Cities

### 6.1 Source and selection rule

The first major-city runtime is generated at build time from Wikidata, not queried live in the browser.

Use Wikidata entity ids as stable source identities and retrieve, where available:

- English/common label;
- country;
- coordinate location;
- population statements with statement date/point-in-time qualifiers;
- administrative territorial entity;
- capital status.

The build output is the union of:

1. all existing national-capital records already represented in `data/world-capitals.geo.json`;
2. Wikidata settlements with a latest available population of at least 500,000;
3. up to the two most populous additional non-capital settlements per canonical ISO3 country when Wikidata supplies a coordinate and population statement.

Duplicate capital/city identities are merged by Wikidata id when available, otherwise by normalized country + name + coordinate proximity.

This produces a globally useful but bounded first city layer while guaranteeing that countries represented by an existing capital do not disappear merely because they lack a very large city.

### 6.2 City record

Each runtime city record contains when available:

- stable id (`wd:<QID>` when Wikidata-backed);
- name;
- country ISO3;
- latitude/longitude;
- population;
- population reference date/year;
- source id/source label;
- capital flag;
- administrative region;
- importance tier;
- minimum zoom;
- aliases when already available from the build source.

### 6.3 Visibility tiers

The build assigns deterministic visibility tiers:

- tier 1 / world zoom: capitals with very high importance and cities >= 5 million;
- tier 2 / regional zoom: cities >= 1 million plus remaining major capitals;
- tier 3 / country zoom: cities >= 500,000 plus per-country top-two additions;
- close zoom: labels may expand while MapLibre collision handling remains enabled.

Exact `minzoom` values are implementation constants documented beside the runtime layer definitions, not data claims.

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

It resolves:

- country common names;
- country official names where available;
- ISO2 / ISO3;
- capital names;
- major-city names;
- runtime aliases.

### 7.2 Result presentation

Suggestions disambiguate type and country, for example:

- `Denmark · Country`
- `Copenhagen · City · Denmark`
- `Georgia · Country`
- `Tbilisi · City · Georgia`

### 7.3 Navigation

Selecting a country preserves the current country-selection behavior.

Selecting a city:

1. flies/fits to the city at the tier-appropriate zoom;
2. selects/highlights the city;
3. opens the city inspector;
4. records URL state with the stable city id.

Country and city URL state must not fight each other. A city may imply its parent country for context without turning the country into the primary selection.

## 8. Feature D — Metric-Aware Compare

### 8.1 Preserve current Compare

Compare remains limited to four countries and keeps deterministic add/remove/exit behavior.

### 8.2 Metric selection

Compare gains a compact metric checklist sourced from the same metric registry as the map.

Default comparison metrics are:

- population;
- GDP;
- GDP per capita;
- real GDP growth;
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

The table may visually emphasize extrema but must use neutral labels such as `highest`/`lowest`, never `best`/`worst` unless a metric has an explicit normative direction in the registry. Version 1 uses neutral direction for all metrics.

### 8.4 Relationship comparison

Relationship overlap/intersection remains separate from statistical comparison in the Analyze section so the Compare panel does not mix distinct analytical jobs.

## 9. Data architecture

### 9.1 Country metric runtime

Add:

`data/world-country-metrics.json`

It is generated by:

`scripts/build_world_country_metrics.py`

The builder uses:

1. `data/countries/index.json` as the sovereign-state identity set;
2. the WDI indicator definitions already used by `scripts/refresh_country_atlas.py` for cross-country comparable observations;
3. same-origin country facts for area when deriving density;
4. canonical country records only as compatible-value/provenance enrichment, never to force incompatible local-currency or differently defined values into a global comparison.

External acquisition happens only during the build/refresh process. The browser reads the committed same-origin runtime.

Shape:

```json
{
  "version": "1.0.0",
  "generated_at": "...",
  "metrics": {
    "gdp": {
      "label": "GDP",
      "indicator": "NY.GDP.MKTP.CD",
      "unit": "current USD",
      "transform": "log1p",
      "direction": "neutral"
    }
  },
  "countries": {
    "DNK": {
      "gdp": {
        "value": 0,
        "unit": "current USD",
        "period": "2025",
        "source": "World Bank WDI",
        "source_id": "NY.GDP.MKTP.CD"
      }
    }
  }
}
```

The example value `0` is schema illustration only; the builder never substitutes zero for missing observations.

### 9.2 City runtime

Add:

`data/world-cities.geo.json`

Generated by:

`scripts/build_world_cities.py`

This is a presentation runtime, not the canonical owner of city knowledge.

### 9.3 Metric registry

The `metrics` object in `data/world-country-metrics.json` is the single runtime registry used by:

- map coloring;
- legend;
- hover;
- country inspector;
- Compare;
- optional selected-metric extrusion.

Do not duplicate metric lists independently across modules.

## 10. Runtime modules

Use the following separation:

- `world-map/3d-metrics.js` — metric registry consumption, choropleth state, legend, hover/inspector augmentation, selected-metric API;
- `world-map/3d-places.js` — major-city source/layers, city selection, city inspector, city URL state;
- `world-map/3d-search.js` — unified searchable index over countries + cities;
- `world-map/3d-compare-metrics.js` — metric selection/rendering inside Compare;
- existing `3d-ui.js` — only integrates compact controls and summaries;
- existing `3d-app.js` — remains owner of core renderer and country selection, with only small integration hooks where required.

If implementation proves that two new modules are inseparable because they share one lifecycle and public API, they may be merged, but the responsibilities above remain the required boundaries.

## 11. Shared browser APIs

Expose small stable APIs rather than reaching into module internals.

Required contracts:

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

Events follow the existing custom-event style:

- `potato-atlas-metric-change`;
- `potato-atlas-place-selection-change`;
- `potato-atlas-places-ready`.

## 12. URL state

Add:

- `metric=<metric-id>`;
- `city=<stable-city-id>`.

Existing country, compare, relation, trace depth, path and time parameters remain intact.

Unknown/retired metric or city ids fail safely and return to neutral state rather than breaking boot.

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

The UI does not need literal top-level tabs named Explore/Compare/Investigate in this slice. This is the conceptual grouping that guides control placement.

## 14. Performance

### 14.1 Initial load

Country geometry and existing core boot remain first priority.

Metrics and cities load after core readiness. Unified search triggers city-runtime loading on first focus/input if the places module has not already loaded it.

### 14.2 City volume

The first city snapshot remains direct GeoJSON. If the generated feature count exceeds 5,000 or the uncompressed committed file exceeds 5 MB, the build must fail with an instruction to tighten the selection rule or migrate places to vector tiles/partitioned packages rather than silently shipping an oversized runtime.

### 14.3 Rendering

Use MapLibre filters, minzoom and symbol collision handling instead of large DOM marker sets.

## 15. Error handling and resilience

- failure to load metrics leaves the neutral country map fully usable;
- failure to load cities leaves country search and existing capital/country functions usable;
- city/metric modules surface a nonfatal unavailable state rather than silently corrupting selection;
- all new browser data uses same-origin generated snapshots;
- external APIs are build/acquisition inputs, not mandatory browser dependencies.

## 16. Provenance and epistemic boundaries

Metric and city values require explicit source/period metadata.

Derived values such as density and ranks are labeled derived.

The map distinguishes:

- observed/sourced country statistics;
- derived display statistics;
- project classifications;
- graph relationships;
- symbolic/Axis navigation.

Metric color is never reused to imply project alignment or evidence quality.

## 17. Accessibility and usability

- search suggestions remain keyboard accessible;
- metric selector has a readable label/title;
- choropleth does not rely on color alone: inspector + legend text always expose the numeric value;
- city points use MapLibre hit-testing with an adequate circle radius independent of visible point radius;
- mobile keeps the existing bottom inspector behavior;
- no city labels overwhelm the map at world zoom.

## 18. Validation strategy

Extend existing validation rather than creating disconnected checks.

### 18.1 Build/data validation

Add validators that verify:

- every metric id is unique;
- every present metric observation has a finite numeric value;
- every observation has period/source metadata or an explicit unknown marker;
- metric source ids match declared registry definitions where applicable;
- city coordinates are finite and within geographic bounds;
- city ids are unique;
- city ISO3 codes resolve to the canonical country index;
- capital flags do not create contradictory duplicate city identities;
- city runtime stays under the volume limits in section 14.2.

### 18.2 Runtime/source validation

Extend `scripts/validate_world_map_3d.py` and add focused data validators as needed to assert:

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
10. exit Compare and confirm city/metric state is not accidentally cleared;
11. switch Time mode and ensure current-only metrics are not falsely presented as historical values;
12. verify mobile inspector remains usable;
13. run the existing path/entity-trace/map validators and confirm no regression.

## 19. Time interaction

The existing conservative Time contract takes precedence over visual convenience.

Version 1 metric behavior:

- in Current mode, show the latest acquired comparable observation and its period;
- in historical modes, do not project current metric colors backward;
- if a historical observation selector has not yet been implemented for the metric runtime, the choropleth becomes neutral and the legend states `Historical metric view unavailable`; country dossier history may still expose preserved observations separately.

Version 1 city behavior:

- city coordinates may remain visible as present-day geographic context;
- current population values are hidden from historical-mode hover unless their observation period is explicitly presented as modern context;
- the UI must not imply current population values describe the selected historical date.

## 20. Implementation order

Implement in small verified slices:

### Slice 1 — Metric runtime and neutral registry

- add `scripts/build_world_country_metrics.py`;
- generate `data/world-country-metrics.json`;
- add `world-map/3d-metrics.js`;
- add metric selector + legend;
- pilot population, GDP and life expectancy;
- validate.

### Slice 2 — Full first metric set

- add the remaining declared WDI metrics;
- add density derivation;
- add ranking/coverage metadata;
- add selected-metric extrusion where appropriate;
- validate.

### Slice 3 — Major cities runtime

- add `scripts/build_world_cities.py`;
- generate `data/world-cities.geo.json` using section 6.1;
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

Additions:

- `docs/superpowers/specs/2026-09-11-world-atlas-utility-design.md`
- `scripts/build_world_country_metrics.py`
- `scripts/build_world_cities.py`
- `data/world-country-metrics.json`
- `data/world-cities.geo.json`
- `world-map/3d-metrics.js`
- `world-map/3d-places.js`
- `world-map/3d-search.js`
- `world-map/3d-compare-metrics.js`
- focused validation scripts where data-contract checks are clearer outside the existing validator.

Modifications:

- `world-map/3d.html`
- `world-map/3d-bootstrap.js`
- `world-map/3d-ui.js`
- small hooks in `world-map/3d-app.js` and/or `3d-hover.js` where unavoidable;
- `scripts/validate_world_map_3d.py`
- `data/world-map-3d-runtime.json` after each implemented capability.

The implementation should reduce this list when existing APIs make a file unnecessary; it must not increase coupling merely to match the list.

## 22. Success criteria

The expansion is successful when a new user can:

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
