# World Map Places System Design

Date: 2026-09-15
Status: approved direction, written specification for review
Branch: `design/world-map-places-system`
Stack base: `fix/world-map-land-cover-provider` at `ce3896bb05107082e7d8039f5c920bcbf4478885`

## 1. Purpose

Complete the missing geographic-resolution layer of the World Map so the atlas becomes useful below country scale without becoming a cluttered pin map.

The first implementation turns the existing capital-only rendering into a scale-aware Places system with:

1. capitals, major cities, regional cities and towns;
2. progressive label density by zoom and importance;
3. country-partitioned same-origin place data;
4. unified country/place search;
5. a typed place inspector in the existing right inspector;
6. place statistics with explicit source/date semantics;
7. a stable path toward subdivisions, institutions, infrastructure and smaller settlements.

The intended geographic hierarchy is:

```text
world
  -> country
    -> subdivision
      -> place
        -> institution / infrastructure / real asset
```

This work extends the existing renderer and country model. It does not create another map application, another country database, or another permanent floating panel.

## 2. Existing foundations to preserve

Current World Map already provides:

- one MapLibre renderer;
- country polygons and country selection;
- an existing `#panel` right inspector;
- a single top search input;
- `data/world-capitals.geo.json`;
- capital points/labels and `window.__potatoAtlasCapitals`;
- country hover and country cards;
- shared UI-layout coordination;
- shared render-stack coordination;
- map-state reset coordination;
- Physical layers;
- infrastructure, Trace, Time, Compare and evidence tooling.

The Places implementation must converge with these owners rather than duplicate them.

## 3. Source strategy

### 3.1 Global place backbone: GeoNames downloads

Use the GeoNames downloadable gazetteer as the first global populated-place backbone.

Initial acquisition input:

```text
cities5000.zip
```

GeoNames currently defines `cities5000` as cities with population above 5,000 or first-order administrative seats. This gives useful global town coverage while remaining small enough to partition and validate.

GeoNames data is CC BY 4.0 and must retain attribution.

The browser must not call GeoNames web services during ordinary browsing. Acquisition happens in a build/refresh script and produces repository-owned browser snapshots.

### 3.2 Capital compatibility

Merge the existing `data/world-capitals.geo.json` records into the generated place model so every currently represented national capital remains represented even when the GeoNames threshold/source differs.

Do not leave the old capital points rendered underneath a duplicate city point.

### 3.3 Optional Wikidata enrichment

Wikidata may be queried during refresh/build for bounded enrichment such as:

- stable QID where confidently matched;
- population statements with explicit point-in-time qualifiers;
- aliases;
- selected administrative relationships.

Wikidata is enrichment, not the runtime backbone. The browser must not depend on WDQS, and a refresh must still be able to produce a useful GeoNames-only snapshot when enrichment is unavailable.

### 3.4 Population semantics

GeoNames supplies a population field but does not guarantee an observation/reference year per row.

Therefore:

- never display the GeoNames snapshot/download date as if it were the population observation year;
- preserve `population_period = null` when no defensible period is available;
- show the source as GeoNames and, separately, the dataset refresh date;
- when Wikidata or another explicit observation source supplies a selected population statement with a point-in-time qualifier, preserve that period and source distinctly;
- missing population is unknown, never zero.

## 4. Generated data architecture

Recommended build outputs:

```text
data/world-places/index.json
data/world-places/global-major.geo.json
data/world-places/countries/AAA.geo.json
...
```

The builder is:

```text
scripts/build_world_places.py
```

The validator is:

```text
scripts/validate_world_places.py
```

### 4.1 `index.json`

The index is small and always safe to load. It contains:

- schema version;
- generated timestamp;
- source snapshot identifiers;
- attribution/license text;
- total place count;
- global-major count;
- per-country counts;
- per-country file paths/sizes;
- coverage notes;
- optional enrichment status.

### 4.2 `global-major.geo.json`

This is the only global place geometry loaded initially.

It contains the union of:

- all represented national capitals;
- places with selected population >= 500,000 when population is available;
- up to two additional high-population places per canonical country when needed for useful coverage;
- explicit high-importance administrative seats required by the capital compatibility layer.

The target remains bounded enough for direct GeoJSON. The implementation validator should enforce a practical feature/file-size budget rather than allowing silent growth.

### 4.3 Country partitions

`countries/<ISO3>.geo.json` contains the selected GeoNames `cities5000` populated places for that country plus merged capital records.

Country partitions load only when useful:

- the user reaches country/subnational zoom;
- the user searches for a place inside that country;
- a direct `place=` URL requires that partition.

Only the required country partition should be fetched for close-scale browsing.

### 4.4 Future density packs

The runtime contract must be able to accept denser later sources without changing the Places API:

```text
cities5000   -> first global town layer
cities1000   -> later close-scale town expansion
cities500    -> later high-detail/local expansion
```

Do not include `cities1000` or `cities500` in the first implementation unless measurements prove the first partition strategy insufficient.

## 5. Place record contract

Each place record contains when available:

```text
id                     stable browser id, preferably gn:<geonameid>
name
ascii_name
aliases[]
country_iso3
country_iso2
admin1_code
admin2_code
admin1_name             when resolved during build
admin2_name             when resolved during build
feature_class
feature_code
coordinates             WGS84 point geometry
population
population_period       nullable
population_source
population_source_id    nullable
capital_status           national / admin / none
is_national_capital
source                   GeoNames / existing capital snapshot / enrichment
source_record_id
source_modified_date     when provided by source
dataset_refresh_date
wikidata_id              nullable
importance_tier
min_zoom
```

No field is invented merely to fill a card.

## 6. Runtime architecture

Create a focused Places module:

```text
world-map/3d-places.js
```

Public API:

```js
window.__potatoAtlasPlaces = {
  ready,
  visible,
  setVisible(value),
  focus(id, options?),
  current(),
  search(query, options?),
  clear(),
  status(),
};
```

Responsibilities:

- load the small place index;
- load `global-major.geo.json` on first Places activation/boot when useful;
- load country partitions lazily;
- own place MapLibre source/layers;
- own place hover/click behavior;
- own place selection state;
- render the place inspector;
- expose search records to unified search;
- deduplicate legacy capital rendering.

It does not own country facts, country selection, subdivision geometry, infrastructure data, Physical data or analytical metrics.

## 7. Rendering and progressive density

### 7.1 One Places layer family

Replace the separate capital-only visual family with one coherent Places family.

Suggested MapLibre layers:

```text
atlas-places-major-points
atlas-places-major-labels
atlas-places-detail-points
atlas-places-detail-labels
atlas-place-selection
```

All visual layers register with the shared render stack in `context-network` or a future specifically approved place slot. Do not rely on script load order.

### 7.2 Visibility tiers

Approximate first-pass behavior:

- world scale: globally major cities + highest-importance capitals;
- regional scale: remaining global-major places;
- country scale: load one country partition and show larger towns/admin seats;
- close scale: reveal more of the loaded country partition as collision rules permit.

Exact `minzoom` thresholds are presentation constants, not claims about settlement importance.

MapLibre label collision remains enabled. Place labels must never use `text-allow-overlap: true` globally.

### 7.3 Visual hierarchy

National capitals remain visually distinguishable from ordinary cities/towns, but difference must be subtle rather than a second duplicate layer.

Selected place receives a focused highlight that sits above ordinary place points but below modal/evidence UI.

## 8. Place inspector

Use the existing canonical right inspector `#panel`.

Selecting a place temporarily changes the inspector context to `Place` without changing the analytical country working set.

The Place inspector shows only sourced/derived fields that are actually available:

- name;
- type/status (capital, administrative seat, populated place);
- country;
- administrative region(s);
- population;
- population observation period when known;
- source and source-record identity;
- dataset refresh/source modified date separately from observation date;
- coordinates;
- GeoNames/Wikidata identity where available;
- `Open country` action;
- later hooks for subdivision, infrastructure and institutions.

The panel heading/eyebrow must make the entity type obvious so city statistics are not mistaken for country statistics.

### 8.1 Selection precedence

Map click precedence remains:

1. explicit specialist/sacred/spatial overlay that already handles the event;
2. selected infrastructure/real asset when its layer handles the event;
3. place point;
4. country polygon fallback.

A place click must mark the original map event as handled so it does not immediately trigger the country polygon click underneath.

### 8.2 Country selection remains orthogonal

Selecting Copenhagen may imply Denmark as parent context, but it must not silently mutate the selected/compare/Trace country working set.

`Open country` explicitly invokes the existing country-selection API.

## 9. Unified search

Create/refine one search module around the existing top search input:

```text
world-map/3d-search.js
```

Search resolves, in one suggestion list:

- country common/official names;
- ISO2/ISO3;
- national capitals;
- major cities;
- loaded country-partition towns;
- place aliases;
- subdivisions once that programme lands.

Result labels disambiguate type and parent context:

```text
Georgia · Country
Copenhagen · Capital · Denmark
Aarhus · City · Denmark
Odense · City · Denmark
Los Angeles · City · California · United States
```

Selecting a place:

1. resolves/loads its country partition if needed;
2. flies to the place;
3. highlights it;
4. opens the Place inspector;
5. writes stable URL state.

Country selection preserves existing behavior.

## 10. URL and reset state

Add orthogonal state:

```text
place=<stable-place-id>
```

Existing country/compare/time/physical state remains independent.

Whole-map reset clears place focus and place partition focus without deleting cached browser data or changing the camera beyond the existing reset contract.

Invalid/missing place ids fail safely and do not break boot.

## 11. Statistics routing

The broader rule is that statistics render in the inspector belonging to the selected entity type.

### Country

Country metrics stay in existing country card/dimensions/evidence surfaces.

### Place

Place-scoped facts stay in Place inspector:

- place population;
- local administrative context;
- place/source identity;
- later city economic/demographic facts only when a real place-level source exists.

Country GDP, debt or national unemployment must not be displayed as if they were city statistics merely because a city is selected.

### Subdivision

Future subdivision inspector owns subdivision population, area, density, capital and source fields.

### Physical feature

Physical inspection remains a separate future inspector context for basin/river/ecoregion attributes.

This typed ownership prevents the right panel from becoming a mixed bag of unrelated scales.

## 12. Subdivision integration

Places must be subdivision-ready even though the first Places implementation does not require global subdivision geometry.

Place records preserve `admin1_code`/`admin2_code` and resolved names where possible.

When the generic subdivision programme lands:

- place records may attach to stable subdivision ids;
- search can resolve country -> subdivision -> place;
- `Open region` can appear in the Place inspector;
- country partitions remain valid.

No country-specific renderer special case is introduced.

## 13. Infrastructure and institution integration

Places are future geographic parents for real assets, not decorative endpoints.

Later records may connect:

```text
place -> airport
place -> port
place -> rail hub
place -> university
place -> company HQ
place -> government institution
place -> power plant / energy asset
```

These links belong in the relational graph/infrastructure owners. The Places dataset must not duplicate those asset facts.

## 14. Performance and failure behavior

- no live GeoNames/Wikidata dependency in ordinary browsing;
- initial global geometry remains bounded;
- country town partitions are lazy;
- do not load every country partition on boot;
- loaded partitions may be cached in memory for the session;
- provider/build refresh failure must not break the existing country map;
- malformed country partition fails locally and leaves global-major places usable;
- unknown population remains unknown;
- labels rely on collision management rather than manual DOM overlays;
- no MutationObserver/setInterval/polling added by Places.

If a single country `cities5000` partition proves too large in practice, split that country by admin1 in a later measured optimization rather than pre-optimizing every country.

## 15. Attribution and provenance

GeoNames attribution must be visible in map/source attribution or Places inspector/source surface.

Generated metadata preserves:

- GeoNames dataset/download date;
- builder generation timestamp;
- source license;
- source record id;
- source modified date where supplied;
- enrichment provenance separately.

Do not conflate dataset refresh date, source modification date and population observation period.

## 16. Coverage ledger

Extend the existing World Map coverage ledger instead of creating a second quality database.

Add descriptive fields such as:

```text
places_global_major_count
places_country_detail_count
places_population_count
places_population_period_known_count
places_capital_coverage
places_refresh_date
places_partition_status
```

These are maintenance/coverage measures, not national importance scores.

## 17. Testing and validation

Add focused validation for:

### Build/data

- index and global-major snapshot exist;
- every place has stable id, name, country and valid WGS84 point;
- no numeric zero is used as a missing population sentinel;
- capital compatibility coverage remains above current baseline;
- duplicate capital/city identities are merged;
- every generated country partition has matching index metadata;
- GeoNames attribution/license is present;
- global-major file/feature budget is enforced.

### Runtime

- Places API exists;
- initial browser load does not fetch all country partitions;
- country partition fetch is lazy;
- place layers use shared render-stack registration;
- place click marks event handled;
- place selection does not mutate analytical country working set;
- `Open country` uses existing country selection;
- place inspector distinguishes observation period from refresh date;
- reset clears place selection;
- no polling/DOM observers.

### Search

- country results still work;
- city/town results work;
- ambiguous names show parent/type context;
- direct `place=` restoration works;
- invalid ids fail safely.

### Regression

Run all existing World Map validators, especially UI layout, render stack, map state, infrastructure, spatial overlays, Physical layers, canonical runtime and repository-quality checks.

## 18. Implementation sequence

1. RED contract for generated Places data and runtime.
2. GeoNames/capital builder + validator.
3. Commit a bounded generated global-major snapshot and country partitions.
4. Add `3d-places.js` with progressive density and capital convergence.
5. Add Place inspector + URL/reset behavior.
6. Add unified country/place search.
7. Extend coverage ledger.
8. Verify exact-head Repository quality.
9. Keep this work stacked on the current World Map PR chain until the lower map stack is merged/rebased and reverified.

## 19. Explicit non-goals for first implementation

- every village/hamlet on Earth;
- live geocoding API calls;
- browser-side WDQS queries;
- global admin-1 polygons in the initial Places PR;
- city GDP/unemployment estimates without real place-level sources;
- arbitrary user z-order;
- replacing MapLibre;
- replacing the country/entity canonical model;
- turning places into a second infrastructure registry;
- loading `cities500` globally on first boot.

## 20. Follow-on map programme

After Places is working, highest-value follow-ons are:

1. generic subdivisions, country-partitioned, with the United States/Denmark/Europe as early implementations;
2. Physical Inspector for basin/river/ecoregion clicks;
3. place-to-infrastructure relational linking;
4. denser `cities1000`/`cities500` close-scale packs where useful;
5. local/subnational sourced statistics;
6. coverage/freshness dashboard in the existing maintenance tooling, not the ordinary map surface.
