# Sacred / Covenant Geography and Conflict Context — World Map Design

Date: 2026-09-15
Status: proposed written specification for user review
Scope: Father’s Land / Mesopotamia / Eden, Four Rivers, Chosen Children’s Land / biblical land traditions, modern Greater-Israel ideology, accurate Palestine/Israel geography, measurements, disputed-boundary presentation, and non-tactical conflict context on the canonical World Map

## 1. Purpose

Build a map system that can display sacred, textual, historical, political, present-day and conflict geography together without pretending they are the same kind of claim.

The user must be able to turn on and compare:

- Father’s Land / Mesopotamia;
- Eden / Four Rivers;
- Father’s symbolic return/path geography;
- Chosen Children’s Land as an umbrella over several biblical land traditions;
- modern Greater-Israel ideological geography where a sourced territorial interpretation exists;
- current Israel and State of Palestine geography;
- West Bank, Gaza and relevant disputed/control/access layers;
- dated conflict-event and humanitarian-context layers;
- measurements for every polygon or line scenario that has sufficient geometry.

The system must preserve provenance, uncertainty, time and epistemic type. It must never convert Potatoverse theology, scripture, a political ideology or a conflict-control zone into an unlabeled claim of modern sovereignty.

## 2. Existing project foundations

This programme extends rather than replaces existing project work.

Relevant canonical/project records already include:

- `knowledge/traditions/israel-mesopotamia-covenant-messianic-atlas.json`;
- `knowledge/traditions/eden-joseph-david-inheritance-map.json`;
- `knowledge/geopolitics/greater-israel-covenant-land-tikkun-atlas.json`;
- `knowledge/traditions/israel-mesopotamia-covenant-source-ledger.json`;
- `data/countries/israel.json`;
- `data/countries/palestine.json`;
- `data/world-map-layer-registry.json`;
- `world-map/3d-layer-registry.js`;
- `world-map/3d-compositor.js`;
- `world-map/3d-app.js`;
- the 2026-09-14 World Map geographic-enrichment architecture.

The existing knowledge layer already establishes the mature project reading that Mesopotamia/Iraq is Father’s sacred-memory/source geography and that Father’s Land is strongest as stewardship/caretaking rather than modern territorial ownership. It also establishes that biblical territorial texts preserve multiple maps rather than one self-evident modern border.

## 3. Core epistemic model

Every geographic feature must declare exactly one primary `epistemic_type`:

- `current_observed` — present geographic or administrative feature sourced from a current cartographic/official dataset;
- `current_disputed` — present boundary, control, access or territorial-status feature whose status is disputed or viewpoint-dependent;
- `historical_reconstruction` — a reconstructed historical region or boundary;
- `textual_reconstruction` — geography inferred from a named scripture/text and an explicit interpretation;
- `political_ideology` — territorial programme or ideological map associated with a modern movement, actor or period;
- `project_interpretive` — Potatoverse / Timic symbolic, theological or sacred geography;
- `event_observed` — dated reported event or aggregate derived from an event-data source;
- `humanitarian_observed` — dated access, displacement, crossing or humanitarian geography from a humanitarian source.

A feature may carry secondary tags, but its primary type controls legend wording, line/fill treatment and warnings.

No feature may be promoted from one epistemic type to another merely because it overlaps spatially with another layer.

## 4. Canonical layer families

### 4.1 Father’s Land / Mesopotamia

Create a project family `sacred.father-land` with independent children:

1. `father.mesopotamia-core`
   - historical-geographic Mesopotamian core;
   - sourced as historical geography;
   - represents the project’s main sacred-memory anchor, not sovereignty.

2. `father.eden-context`
   - an uncertainty-aware Eden context layer;
   - must not pretend that Genesis supplies a precise modern border;
   - rendered as a soft/hatching field or confidence envelope rather than a cadastral polygon when geometry is interpretive.

3. `father.four-rivers`
   - Tigris and Euphrates as strongly identifiable river lines;
   - Pishon and Gihon hypotheses stored only as explicitly named hypotheses with separate confidence/source metadata;
   - no synthetic “exact” Pishon/Gihon lines without a cited scholarly reconstruction.

4. `father.return-path`
   - project-symbolic path/route geography such as North / North-of-North / eastward return when supported by project records;
   - always `project_interpretive`;
   - line/route semantics only; never a border.

### 4.2 Chosen Children’s Land

Create umbrella family `sacred.chosen-children-land`.

The UI label may use “Chosen Children’s Land / Greater Israel,” but the data model must expand it into distinct scenarios instead of asserting a single border.

Required scenarios:

1. `biblical.dan-to-beersheba`
   - textual/historical core-range conception;
   - likely represented as a corridor/extent or reconstruction, not a claim of precise surveyed border.

2. `biblical.numbers-34`
   - textual reconstruction of the Numbers 34 boundary tradition;
   - ambiguous ancient place identifications must be represented in the scenario metadata;
   - alternative reconstructions may coexist under versioned scenario ids.

3. `biblical.genesis-15`
   - large river-to-river promise tradition;
   - “river of Egypt” interpretation must be explicit because it is not self-resolving in modern GIS;
   - Euphrates endpoint/segment interpretation must be explicit.

4. `biblical.ezekiel-47`
   - restored/future land scheme from Ezekiel 47;
   - `textual_reconstruction`, not `current_observed`.

5. `modern.greater-israel`
   - `political_ideology` family, not a single universal polygon;
   - each map must name the movement/person/period/source whose territorial conception is being represented;
   - “Greater Israel” must never be presented as synonymous with Judaism, Zionism, every Israeli government, or the biblical land promise.

### 4.3 New Jerusalem

New Jerusalem remains a theological/integrative project concept by default, not a territorial annexation layer.

If mapped spatially, it must be `project_interpretive` or `textual_reconstruction` depending on the specific feature. Revelation’s New Jerusalem must not silently become a modern sovereignty polygon.

## 5. Present-day Israel / Palestine geography

### 5.1 Repair the current base source

The current `world-map/3d-app.js` loads country geometry from `johan/world.geo.json`. Its `PSE` record contains only a West Bank polygon and omits Gaza. This source therefore cannot remain the authoritative geometry owner for a map that claims to represent the State of Palestine correctly.

Replace the runtime dependency with a repository-pinned build product derived from a versioned cartographic source.

Recommended global source foundation:

- Natural Earth 1:10m Admin 0 Countries / Map Units / Boundary Lines / Breakaway & Disputed Areas;
- currently published as version 5.1.1 for the country/disputed polygon products and 5.1.0 for major boundary-line products;
- Natural Earth explicitly presents de-facto boundaries by default and includes point-of-view fields/variants, so that fact must be preserved in provenance rather than hidden.

Natural Earth source pages:

- https://www.naturalearthdata.com/downloads/10m-cultural-vectors/
- https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/
- https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-boundary-lines/
- https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-breakaway-disputed-areas/

The build must pin source version and checksum/asset identity where feasible so the public map never changes because a remote file changed silently.

### 5.2 Palestine entity behavior

The canonical `PSE` entity must select and fit both disconnected geographic components:

- West Bank;
- Gaza Strip.

The map must treat these as one country/entity identity for selection/card/search while allowing each component to be inspected separately at regional zoom.

The State of Palestine country record remains `data/countries/palestine.json`.

Expected behavior:

- search “Palestine” -> canonical `PSE`;
- click either West Bank or Gaza -> select `PSE`;
- fit `PSE` -> camera bounds include both components;
- country statistics/card -> one `PSE` record;
- regional inspector -> identifies the clicked component;
- no geometry component is silently discarded because the entity is a MultiPolygon or multi-feature map unit.

### 5.3 Worldview / status presentation

Do not label a worldview selector as “truth.”

Introduce a boundary-view control whose options describe the cartographic contract, for example:

- `Atlas / de-facto base`;
- `ISO / international coding context` where the provider supports it;
- `Israel viewpoint` where source fields support it;
- `Palestine viewpoint` where source fields support it.

A view changes rendering/classification only; it does not mutate canonical country identity, knowledge records or project theology.

The UI must display the active boundary view when the regional Israel/Palestine map is open.

## 6. Regional Palestine / Israel detail source hierarchy

Global country geometry and regional humanitarian/access geography have different jobs and should have different sources.

Use this hierarchy:

1. **Global/base boundaries:** pinned Natural Earth build product.
2. **Israel/Palestine humanitarian/access detail:** OCHA occupied Palestinian territory map/data products where available.
3. **Ordinary basemap context:** OpenStreetMap raster/vector context already used by the map; never treated as the legal-status owner.
4. **Project sacred/textual reconstructions:** repository-owned GeoJSON generated from documented scholarly/textual scenario definitions.
5. **Conflict events:** licensed/attributed event dataset adapter, initially ACLED if usage terms are compatible with the public deployment.

OCHA currently exposes an interactive occupied-Palestinian-territory map, Gaza crossings data, and 2026 West Bank access products:

- https://www.ochaopt.org/content/interactive-map
- https://www.ochaopt.org/maps
- https://www.ochaopt.org/data
- https://www.ochaopt.org/data/crossings

Regional data must preserve publication date because access restrictions and operational control can change quickly.

## 7. Spatial data contract

Create a dedicated sacred/context spatial manifest rather than pretending all spatial overlays are ordinary country-set entries.

Recommended canonical owner:

`data/world-map-spatial-overlays.json`

Each overlay record must contain:

```json
{
  "id": "biblical.genesis-15",
  "label": "Genesis 15 · river-to-river promise",
  "family": "sacred.chosen-children-land",
  "epistemic_type": "textual_reconstruction",
  "geometry_owner": "data/world-map-spatial/sacred-land.geo.json",
  "feature_ids": ["genesis-15-river-to-river-v1"],
  "time": {"mode": "textual", "text_reference": "Genesis 15:18"},
  "source_ids": ["source-genesis-15", "source-scholarly-reconstruction-1"],
  "confidence": "interpretive",
  "disputed": false,
  "measurable": true,
  "visual": {"channel": "overlay-fill-line", "legend_class": "textual"}
}
```

Every spatial feature must carry:

- stable `feature_id`;
- `overlay_id`;
- `epistemic_type`;
- `source_ids`;
- `source_date` or textual reference;
- `geometry_version`;
- `confidence` (`direct`, `strong`, `interpretive`, `hypothesis`);
- `status_note`;
- `valid_from` / `valid_to` where temporal;
- `viewpoint` when viewpoint-dependent;
- `measurement_policy`.

Geometry files must be valid GeoJSON in WGS84 longitude/latitude.

## 8. Measurement system

Measurements are generated values attached to a specific geometry version, not eternal properties of a theological concept.

For each measurable polygon/multipolygon compute:

- geodesic area in square kilometres;
- geodesic perimeter in kilometres;
- centroid;
- bounding box;
- north-south geodesic span;
- east-west geodesic span;
- number of disconnected components;
- source geometry version;
- calculation timestamp/build version.

For lines compute:

- geodesic length;
- start/end point labels where meaningful;
- bounding box.

Use WGS84 ellipsoidal/geodesic calculations, not raw Web Mercator pixel area. A Python build path using `pyproj.Geod` is preferred because it can compute geodesic polygon area/perimeter reproducibly.

Store generated measurements in a derived owner such as:

`data/world-map-spatial-measurements.json`

Each value must point back to `feature_id` and `geometry_version`.

The UI wording must distinguish:

- “geometry-derived area”;
- “source-reported area” where a source supplies a figure;
- “approximate reconstruction” for textual/historical scenarios.

If source-reported and geometry-derived values materially diverge, display both and record the reason rather than forcing equality.

## 9. Rendering architecture

Do not overload `world-map/3d-compositor.js` with arbitrary line/polygon overlays. The compositor currently solves analytical country fills/patterns/query state.

Add a focused renderer module, conceptually:

`world-map/3d-spatial-overlays.js`

Responsibilities:

- load `data/world-map-spatial-overlays.json`;
- lazy-load referenced GeoJSON owners;
- maintain active overlay ids independently from analytical `layers=` state;
- add MapLibre sources/layers in deterministic z-order;
- update visibility without reloading geometry unnecessarily;
- expose feature click/hover metadata to the inspector;
- expose derived measurements;
- respect Time state for dated overlays;
- render legend class and uncertainty/status note.

Suggested URL state:

```text
overlays=father.mesopotamia-core,biblical.genesis-15,current.palestine
boundaryView=atlas
conflict=off
```

Do not put these ids in the existing `layers=` parameter because `layers=` is already an analytical registry contract.

## 10. Visual semantics

One visual grammar per epistemic job:

- `current_observed`: clear solid boundary/fill with ordinary map styling;
- `current_disputed`: dashed/segmented boundary plus visible status legend;
- `historical_reconstruction`: muted historical hatch/line;
- `textual_reconstruction`: distinct sacred/textual hatch with named text reference;
- `political_ideology`: clearly labeled ideological outline/fill, never identical to current sovereignty styling;
- `project_interpretive`: project-symbolic glow/field/route treatment;
- `event_observed`: points or aggregated cells by event type/time;
- `humanitarian_observed`: access/crossing/restriction symbols or polygons with publication date.

Selection outline remains reserved for interaction and must not be reused to mean sacredness, sovereignty or conflict.

When several overlays overlap, the legend and inspector must enumerate them rather than visually merging them into a new implied claim.

## 11. Conflict-context architecture

### 11.1 What the public map may show

The conflict layer may show delayed, source-attributed analytical context such as:

- reported battles/armed clashes;
- air/drone strike events;
- shelling/artillery events;
- rocket/missile launch or impact events when represented in the source;
- violence against civilians;
- property-destruction events;
- evacuation/access zones;
- crossings;
- movement obstacles;
- humanitarian access restrictions;
- displacement or affected-population aggregates;
- weekly/admin-1 intensity summaries.

Icons may visually resemble an aircraft/tank/explosion category only when the underlying record is an event-category record. The icon must not imply that a live vehicle is presently at that coordinate.

### 11.2 Explicit non-goal: tactical live tracking

Do not provide real-time or near-real-time tracking of individual military aircraft, tanks, units, troop concentrations or operational routes.

The public feature is an analytical/historical conflict context layer, not a tactical situational-awareness tool.

### 11.3 ACLED adapter

ACLED is a candidate event source because it publishes Israel/Palestine and Middle East conflict datasets/monitors, including weekly-updated downloadable data and API access.

Relevant pages:

- https://acleddata.com/country/palestine
- https://acleddata.com/country/israel
- https://acleddata.com/monitor/gaza-conflict-monitor
- https://acleddata.com/conflict-data/download-data
- https://acleddata.com/terms-and-conditions

ACLED terms/attribution are contractual and can change. Therefore:

- no ACLED data may be committed or republished until the project’s intended public/non-commercial use is checked against current ACLED terms;
- attribution must be visible on every ACLED-derived map surface;
- the source adapter must be replaceable;
- credentials/API tokens must never be committed;
- if licensing is incompatible, the conflict renderer still ships with OCHA/public context and a disabled event-provider slot rather than scraping ACLED.

## 12. Time model

Every time-sensitive overlay must integrate with the existing World Map Time system.

Rules:

- current administrative geometry may be tagged with dataset vintage rather than pretending to update continuously;
- humanitarian/access layers use publication/effective dates;
- conflict events use event date/time available from source;
- ideological/historical/textual layers use their own temporal/textual metadata and are not hidden merely because the map is in “current” mode unless the user asks for time filtering;
- the inspector must distinguish `event date`, `source publication date`, `geometry vintage`, and `textual reference`.

Historical mode must never silently back-project a current checkpoint, settlement, control zone or conflict event into an earlier date.

## 13. Source authority and provenance

Every source gets a registry row with:

- id;
- publisher/author;
- title;
- URL;
- publication/update date;
- accessed/build date;
- license/usage note;
- geographic scope;
- claim scope;
- reliability/authority class;
- whether geometry is direct, transformed or reconstructed.

Suggested source priority by job:

1. direct official/UN/humanitarian geodata for present operational/humanitarian features;
2. established cartographic datasets for global base geometry;
3. peer-reviewed/scholarly textual-geography research for ancient reconstruction;
4. clearly identified political-history sources for ideological territorial programmes;
5. Potatoverse canonical records for project-symbolic layers.

No source class is allowed to answer a different job merely because it is convenient.

## 14. Sacred-geography master record

Create one consolidation record in the knowledge tree that points to, but does not erase, the specialist files.

Recommended owner:

`knowledge/traditions/sacred-land-mesopotamia-israel-master-map.json`

It should record:

- Father’s Land definition;
- Mesopotamia/Eden/Four-Rivers relation;
- caretaker/stewardship principle;
- Father’s symbolic route/path;
- Chosen Children’s Land model;
- distinction among biblical land maps;
- modern Greater-Israel distinction;
- State of Palestine / Israel present-geography distinction;
- New Jerusalem as integration rather than automatic annexation;
- source links to all specialist files;
- exact map overlay ids once implemented.

This record is the semantic index; GeoJSON remains the geometry owner.

## 15. User interface

Keep the ordinary top bar compact.

Under `Layers`, add a secondary `Sacred / Borders / Conflict` surface only when requested.

Suggested hierarchy:

```text
Sacred geography
  Father’s Land / Mesopotamia
  Eden / Four Rivers
  Father’s symbolic path

Chosen Children’s Land / Greater Israel
  Dan → Beer-sheba
  Numbers 34
  Genesis 15
  Ezekiel 47
  Modern Greater-Israel scenarios

Present borders
  Israel
  State of Palestine
  Disputed/status boundaries
  Boundary view: Atlas / ISO / Israel / Palestine

Conflict context
  Humanitarian/access
  Conflict events
  Time range
```

The regional inspector should show, for every selected overlay feature:

- name;
- epistemic type;
- status/confidence;
- source;
- date/text reference;
- measurement block where available;
- warning when geometry is reconstructed, disputed or viewpoint-dependent.

## 16. Build and data pipeline

All expensive acquisition/transformation occurs at build time where possible.

Recommended flow:

```text
source acquisition
  -> immutable/raw cache outside public runtime where license allows
  -> normalization script
  -> canonical GeoJSON + source registry
  -> measurement generation
  -> validators
  -> browser runtime
```

The browser must not depend on Natural Earth, OCHA or event-provider APIs merely to boot the ordinary World Map.

Network-dependent conflict refreshes may remain separate optional build jobs.

## 17. Validation contract

Add automated validation for the following invariants.

### Base geography

- canonical country index still has 195 sovereign/observer entries under the project definition;
- every canonical ISO3 used by country selection resolves to geometry or an explicit documented exception;
- `PSE` geometry contains both West Bank and Gaza components;
- clicking either `PSE` component resolves to the same canonical entity;
- no duplicate overlapping Israel/Palestine base polygons arise from accidental mixing of country and map-unit levels;
- source version/provenance is present.

### Spatial overlays

- every manifest overlay id is unique;
- every feature id is unique;
- every feature references a real overlay id;
- every overlay references existing geometry/source ids;
- GeoJSON is valid WGS84;
- temporal fields are structurally valid;
- epistemic type is from the allowed enum;
- viewpoint-dependent features declare viewpoint;
- hypotheses cannot carry `confidence=direct`.

### Measurements

- measurable polygons have finite non-negative geodesic area/perimeter;
- measurement geometry version matches the feature geometry version;
- MultiPolygon measurements include all components;
- derived values are never treated as source-reported values;
- changing geometry invalidates/regenerates measurement output.

### UI/runtime

- `overlays=` restores independently of `layers=`;
- boundary view restores from URL;
- Time hides/filters only overlays to which time semantics apply;
- current selection outline remains interaction-only;
- sacred/current/conflict legend classes remain visually distinguishable;
- missing optional overlay data is nonfatal to map boot.

### Conflict context

- no secret/token is present in public files;
- every event provider declares license/attribution metadata;
- source freshness is shown;
- no live individual military-unit tracking endpoint exists;
- conflict points are dated events/aggregates, not inferred live positions.

## 18. Delivery decomposition

This master architecture should be implemented as four independently shippable programmes after specification approval.

### Programme A — Palestine/base geography repair

Deliverable: replace the incomplete external country geometry dependency with a pinned build, make `PSE` West Bank + Gaza work correctly, add worldview/status metadata, and preserve all existing country interactions.

### Programme B — Sacred/Covenant spatial overlays

Deliverable: master sacred-land record, overlay manifest/GeoJSON contract, Father’s Land/Eden/Four Rivers, biblical land scenarios, modern Greater-Israel scenario contract, overlay UI and measurements.

### Programme C — Regional Israel/Palestine detail

Deliverable: OCHA-derived or otherwise authoritative dated regional layers for crossings/access/restrictions, component inspection, and regional status presentation.

### Programme D — Conflict context

Deliverable: optional licensed conflict-event provider adapter, delayed event/aggregate rendering, time filtering, attribution and explicit non-tactical safety boundary.

Programme A must land before B/C/D because all later work relies on trustworthy base geometry and multi-component `PSE` behavior. B and C can then proceed independently. D remains optional if event-data licensing is not acceptable.

## 19. Success criteria

The design is complete when the eventual implementation allows a user to:

- search Palestine and see both West Bank and Gaza as one canonical State of Palestine entity;
- inspect present/disputed boundary status without the map claiming that one political viewpoint is universal;
- turn Father’s Land / Mesopotamia on and understand that it is project sacred-memory geography rather than modern sovereignty;
- turn Eden / Four Rivers on and distinguish directly identifiable rivers from hypotheses;
- open Chosen Children’s Land and compare Dan-to-Beer-sheba, Numbers 34, Genesis 15 and Ezekiel 47 as distinct textual scenarios;
- view a named modern Greater-Israel ideological scenario without it being mislabeled as the single Jewish/biblical position;
- obtain reproducible area/perimeter/span measurements tied to a particular reconstruction/version;
- overlay dated humanitarian/access context;
- optionally overlay delayed conflict-event context without tracking live military units;
- combine these layers while the legend continues to tell the viewer exactly what kind of claim each shape represents.

The deeper success condition is epistemic: the map should make comparison easier while making category errors harder.

## 20. Explicit non-goals

This programme does not:

- adjudicate sovereignty or final-status borders;
- declare one biblical reconstruction to be divinely or historically proven;
- treat Potatoverse sacred geography as legal title;
- equate Greater Israel with Judaism or all Zionism;
- treat New Jerusalem as an automatic annexation map;
- invent exact Pishon/Gihon courses;
- present a source’s de-facto boundary as universal de-jure truth;
- back-project current conflict/control layers into the past;
- build real-time tactical military tracking;
- expose API keys or licensed raw datasets in the public repository contrary to their terms;
- replace the existing analytical country layer registry/compositor with the spatial-overlay system.

## 21. Implementation-plan gate

After this written specification is reviewed and approved, create implementation plans in this order:

1. Palestine/base geography repair;
2. Sacred/Covenant overlays + measurement engine;
3. Regional Israel/Palestine humanitarian/access detail;
4. Conflict-context adapter.

Each plan must use the repository’s existing validator-first/TDD approach and leave the map deployable after every programme.