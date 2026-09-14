# World Map Geographic Enrichment Design

Date: 2026-09-14
Status: approved architecture
Scope: population completeness, subnational geography, major cities/search, physical terrain, and the next value-producing World Map expansion sequence

## 1. Purpose

This design consolidates the next World Map expansion after a fresh scan of the current renderer, runtime builders, validators, data owners, earlier approved map specifications, and historical map branches.

It is intentionally an integration design rather than a new parallel roadmap. The repository already contains a strong World Map substrate. The next wave should deepen geographic resolution and data completeness while preserving the existing map-first interface and current ownership boundaries.

The first programme has four linked outcomes:

1. make population coverage complete and testable for all 195 canonical sovereign-country records;
2. add a generic subnational geography contract, implemented first with United States states and the District of Columbia;
3. complete the previously designed major-cities/place layer and unify country, subdivision and city search;
4. add an optional physical-terrain context layer with hillshade and real elevation without disturbing analytical overlays.

The broader objective is a scale-aware map:

```text
world
  -> countries
    -> subdivisions
      -> cities
        -> institutions / infrastructure / real assets
```

with physical geography underneath and analytical/project layers above it:

```text
physical Earth
  -> administrative geography
    -> places / assets
      -> empirical statistics and relationships
        -> project-interpretive Axis / specialist analysis
```

## 2. Scan conclusions

### 2.1 Preserve the current renderer

The active World Map already has one MapLibre renderer, one country selection model, one layer registry/compositor, one entity runtime, one empirical infrastructure registry, and one lazy specialist-module system.

Do not introduce a second renderer, a second country model, a second metric database, a second infrastructure registry, or a separate USA-only application.

The current renderer already recognizes four view scales: world, regional, country and subnational. Subnational is therefore a missing data/runtime capability inside an existing navigation model, not a reason to create another map.

### 2.2 Population architecture is mostly repaired, but completeness is not enforced

Current main already contains shared scalar resolution for population and area. Population resolution prefers a valid canonical observation, then a compatible canonical top-level population value, then a generated fallback, then unknown. Missing data is not supposed to become numeric zero.

The remaining defect is the quality gate. The map validates the 195-country identity set and representative population cases, but it does not currently require a valid resolved population for every canonical sovereign record.

The demography builder also has a weaker coverage floor than the intended public invariant. This wave should turn population completeness into an explicit contract rather than an assumption.

### 2.3 Cities were designed before, but the implementation was never integrated

The approved 2026-09-11 utility-first design already defines a bounded major-city runtime, zoom-aware labels, city inspection and unified country/city search.

Current main has a real capital-city layer but no `world-cities.geo.json`, no complete places module and no unified city search.

Historical branch `atlas-metrics-cities-search` contains useful never-integrated acquisition/validation work for a Wikidata-backed city snapshot. The branch is far behind current main and must not be merged. Its builder logic and tests are archaeology to adapt into current architecture.

### 2.4 Subnational geography is genuinely missing

No current subdivision/admin-1 runtime or layer was found. The correct solution is a generic subdivision contract with country-partitioned geometry. The United States is the first implementation, not a permanent special case.

### 2.5 Terrain is genuinely missing

No current terrain, hillshade, DEM or land-cover implementation was found. MapLibre 6.9 already supports raster-DEM hillshade and 3D terrain, so this can be an optional lazy extension of the current renderer.

### 2.6 Coverage and infrastructure owners already exist

The coverage builder/validator and empirical infrastructure registry already exist. They should be extended, not replaced.

Infrastructure is already typed, geocoded, sourced and connected to the investigation/Impact architecture. Later place enrichment should attach real institutions and infrastructure to the same relational map rather than create decorative pin collections.

## 3. Governing principles

### 3.1 Simple surface, deep engine

The ordinary map must stay readable. New geographic capability appears progressively by zoom or one compact existing control. The top bar does not become a GIS dashboard.

### 3.2 One owner per fact class

Canonical country facts remain in canonical country/entity owners. Generated browser runtimes are projections. Subdivision and city snapshots must declare their source and acquisition provenance and must not become duplicate authorities for country-level facts.

### 3.3 Same-origin browser data where practical

Countries, subdivisions, cities and their metadata should load from repository/deployment snapshots rather than require public APIs during ordinary browsing.

External services are acquisition inputs, not mandatory browser dependencies, except physical terrain tiles where vendoring global DEM data is intentionally out of scope.

### 3.4 Missing is unknown, never zero

No population, area, city population or subdivision statistic may become `0` merely because acquisition or resolution failed.

### 3.5 Honest coordinates and geometry

Only real geographic entities receive real map coordinates/polygons. Semantic concepts, treaties, scripture, abstractions and project ideas remain in cards, graphs, Axis scenes or other nonspatial representations.

### 3.6 Zoom creates detail; controls do not create clutter

Administrative detail and places appear when the camera scale makes them useful. A user should not need to turn on ten switches merely to discover that California or Los Angeles exists.

### 3.7 Analytical layers remain above geographic context

Terrain, water, hillshade and administrative subdivisions are context. Population, religion, memberships, Axis patterns, selected-country outlines, relations, infrastructure and evidence layers retain their current semantic jobs.

## 4. Programme A — Population completeness and scalar integrity

### 4.1 Public invariant

For the canonical sovereign-country plane:

```text
country_count = 195
resolved_population_count = 195
missing_population_count = 0
```

This does not mean every country must have the same observation year. It means every canonical sovereign must have one valid, sourced population observation selected by the shared resolution policy.

Territories and non-sovereign first-class map entities remain a separate entity plane and do not inflate the 195-country invariant.

### 4.2 Resolution order

Population resolution remains:

1. valid canonical `observations.population`;
2. compatible canonical top-level/legacy population field with preserved source/date semantics;
3. generated UN World Population Prospects fallback;
4. unknown only for noncanonical/unresolved entities where no defensible value exists.

The demography builder and World Map runtime must share this policy rather than implementing subtly different population authority chains.

### 4.3 Global fallback

UN World Population Prospects 2024 remains the global completion source for canonical sovereigns when a compatible local/canonical observation is absent. It is a build/acquisition source, not a live browser dependency.

The selected cell must preserve at least:

```text
value
unit = persons
period / reference year
source
source URL or source identifier
resolution tier (canonical observation / canonical compatible / global fallback)
```

### 4.4 Validators

Strengthen World Map validation to fail when:

- canonical country count is not 195;
- any canonical ISO3 has no resolved population;
- any missing population is represented as numeric zero;
- population cells lack value/unit/period/source;
- two conflicting scalar paths expose different resolved population values to card, hover and population layer.

The coverage ledger gains an explicit population-completeness dimension derived from the generated runtime.

### 4.5 Non-goals

This slice does not require every country to have current GDP, debt, religion, infrastructure or every other metric. Population is selected first because it is foundational to ordinary geographic browsing and can defensibly reach complete sovereign coverage.

## 5. Programme B — Generic subdivisions, United States first

### 5.1 Architecture

Add one generic subdivision contract, not a USA-specific renderer.

Recommended source/runtime structure:

```text
data/world-subdivisions/index.json
data/world-subdivisions/USA.geo.json
```

The index describes available country partitions and source vintages. Individual country partitions keep initial load bounded and let future countries be added independently.

A focused browser module owns the layer:

```text
world-map/3d-subdivisions.js
```

It loads only when the camera reaches the subnational scale or a subdivision search result explicitly requests a subdivision.

### 5.2 First United States dataset

Use official U.S. Census Bureau geography as the acquisition authority for the first partition.

Geometry source: 2025 TIGER/Line State and Equivalent Entity geography, with legal boundaries/names as of 2025-01-01.

Population source: Census Vintage 2025 state population estimates, using the July 1, 2025 estimate and preserving its vintage/reference date.

The ordinary first layer presents:

- the 50 states;
- District of Columbia as a district/federal district, not mislabeled as a state.

Puerto Rico and other U.S. territories may be present in source acquisition but must retain explicit territory/equivalent typing. They must not be silently counted among the 50 states.

### 5.3 Subdivision record contract

Each subdivision should expose when available:

```text
id                    stable namespaced id, e.g. US-CA
name
short code / postal code
parent ISO3
subdivision type
geometry
capital
population observation
area observation
derived density (only when both population and compatible area exist)
source geometry
source population
reference dates/vintages
```

Density is explicitly derived and never canonical.

### 5.4 Interaction

At world/regional scale, state borders remain absent.

As the user zooms into the United States, subdivision outlines and labels progressively appear. They should be subordinate to country boundaries and should not overwhelm active analytical fills.

Clicking a subdivision opens a compact subdivision inspector with:

- identity/type;
- parent country;
- capital;
- population + reference date;
- area;
- derived density where valid;
- source/provenance;
- `Open country` action;
- later, related cities/assets.

Selecting a subdivision must not mutate the parent country's canonical selection state unless the user explicitly opens/selects the parent country.

### 5.5 URL state

Use stable URL state such as:

```text
subdivision=US-CA
```

Unknown/retired subdivision ids fail safely.

### 5.6 Generalization

The contract must be able to accept later partitions for Canada, Germany, Denmark, Australia, India and other countries without changing the renderer API.

Different countries use different administrative systems. The runtime therefore uses generic `subdivision_type` rather than pretending every admin-1 unit is a “state.”

### 5.7 Performance

Do not ship all global admin-1 geometry in the initial bundle.

Country partitions are loaded on demand. Geometry may be simplified for web display while preserving source vintage/provenance. Simplification is a presentation transform, never a new boundary authority.

## 6. Programme C — Major cities and unified place search

### 6.1 Recover, do not merge, the historical implementation

Adapt the useful acquisition and validation logic from historical branch `atlas-metrics-cities-search` into current main architecture. Do not merge that branch wholesale and do not restore its old metric/runtime assumptions.

The current capital layer remains useful input and compatibility infrastructure.

### 6.2 Generated city snapshot

Create/refine:

```text
scripts/build_world_cities.py
data/world-cities.geo.json
scripts/validate_world_cities.py
```

The city snapshot is a same-origin browser runtime generated intentionally from acquisition sources. External Wikidata requests happen during refresh/acquisition, not ordinary browsing.

The first bounded selection remains close to the previously approved design:

1. all represented national capitals;
2. settlements with latest available population >= 500,000 when sourced coordinates and population exist;
3. up to two additional high-population non-capital settlements per canonical country when defensible.

A later source/coverage pass may use GeoNames or another documented acquisition fallback to repair gaps, but one city identity must have one selected runtime record and explicit provenance.

### 6.3 City record contract

Each city record contains when available:

```text
stable id
name
aliases
country ISO3
parent subdivision id when resolved
coordinates
population
population reference date/year
population source
coordinate source
capital flag
administrative region
visibility tier
minimum zoom
```

### 6.4 Visibility tiers

Preserve the bounded progressive-density model:

- world scale: globally major cities / high-importance capitals;
- regional scale: million-plus cities and remaining important capitals;
- country scale: 500k-plus cities and bounded per-country additions;
- close scale: more labels as collision rules permit.

MapLibre symbol collision handling stays enabled. The goal is useful geographic texture, not maximum label count.

### 6.5 One places layer, not duplicate capitals

City work must converge with current capital rendering rather than stack a second marker on every capital.

The places module may ingest the existing capital snapshot and the generated city snapshot into one browser-facing place index while preserving the capital source/provenance fields.

Recommended module:

```text
world-map/3d-places.js
```

It owns place source/layers, place visibility, city selection and the place inspector.

### 6.6 Unified search

Replace country-only discovery with a single search index capable of resolving:

- country common/official names;
- ISO2/ISO3;
- subdivision names/codes;
- capital names;
- major city names and aliases.

Recommended module:

```text
world-map/3d-search.js
```

Suggestions disambiguate type and parent context, for example:

```text
Georgia · Country
California · State · United States
Los Angeles · City · California · United States
Tbilisi · City · Georgia
```

Selecting a city flies to the city, highlights it and opens its inspector. Selecting a subdivision flies/fits to the subdivision and opens its inspector. Selecting a country preserves current country-selection behavior.

### 6.7 Performance budget

The initial city runtime should remain bounded. Retain the earlier safety gate of approximately 5,000 features / 5 MB uncompressed unless measurement during implementation demonstrates a better threshold.

If the place runtime outgrows direct GeoJSON, migrate deliberately to partitioned/vector-tile delivery rather than silently shipping an unbounded file.

## 7. Programme D — Physical terrain and relief

### 7.1 User experience

Add one quiet physical-terrain control under the existing Layers/View hierarchy. Do not add a permanent toolbar of physical toggles.

Initial states can remain conceptually simple:

```text
Terrain off
Terrain on
```

When enabled:

- physical base context becomes more visible;
- DEM-based hillshade is added below administrative/analytical layers;
- real elevation is enabled for pitched/tilted views where supported;
- water remains ordinary physical context;
- analytical country fills, patterns, outlines, relationships and points remain readable above it.

### 7.2 Runtime boundary

Recommended focused lazy module:

```text
world-map/3d-physical-terrain.js
```

It is loaded only on first terrain activation.

MapLibre `raster-dem`, hillshade and `setTerrain()` are the implementation primitives. The terrain-provider endpoint is configuration, not a semantic data owner.

### 7.3 Failure mode

Terrain failure is nonfatal.

If the DEM provider is unavailable:

- remove/disable terrain state;
- retain the ordinary country map and analytical layers;
- surface a compact unavailable status if the user explicitly requested terrain;
- never block World Map boot.

### 7.4 URL/preference state

Terrain state may persist through a compact URL parameter such as:

```text
terrain=1
```

It must not alter analytical layer state.

### 7.5 Land cover is a later sourced layer

Do not treat generic green basemap pixels as a claim of current forest/grass coverage.

A later physical-Earth wave may add separately sourced forests, grasslands, deserts/bare land, permanent ice/snow, wetlands, hydrography, bathymetry/relief and climate/environmental surfaces. Those require explicit source/date/resolution contracts and should not be smuggled into the first terrain toggle.

## 8. Interaction and layer ordering

The desired conceptual render order is:

```text
background / water / physical basemap
terrain / hillshade
country polygons / analytical scalar fill
subdivision boundaries and labels at close zoom
categorical analytical patterns
selection / query outlines
relationship lines
cities / capitals / infrastructure / real assets
specialist overlays / evidence UI
```

Exact MapLibre insertion points may vary with current layer ids, but the semantic priority must remain stable.

Subdivision boundaries must not become a new analytical fill owner. Terrain must not repaint population/religion/Axis color. Cities must not compete with infrastructure for meaning through identical symbols without a legend/visual distinction.

## 9. State model

Country selection remains the primary working-set state. Subdivision selection, place selection and terrain are orthogonal view/context states. The URL should preserve each without mutating the analytical `layers=` state.

## 10. Implementation sequence

1. Population completeness and validator strengthening.
2. Generic subdivision contract + U.S. partition.
3. Places/cities runtime + unified search.
4. Physical terrain toggle.
5. Later sourced land-cover/environment and additional subdivision countries.

Each slice must ship independently with validators and must leave the current map useful if later slices are absent.
