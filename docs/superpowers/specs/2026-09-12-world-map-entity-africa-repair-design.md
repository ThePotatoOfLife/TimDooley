# World Map Entity, Greenland & Africa Repair Design

## Status
Conceptual approach A approved in conversation on 2026-09-12. This document is the implementation contract; no production code should be changed until this written spec is reviewed.

## Goal
Repair two concrete map failures and use the repair to deepen the World Map's regional model:

1. eliminate population labels that can appear over the wrong geography (the observed `145M` North Sea case);
2. make Greenland a first-class map entity without falsely converting the 195-country sovereign-country model into 196 countries;
3. integrate Africa much more deeply through its own regional systems first, then add only defensible North / West / East / South orientations where the evidence or recovered project language is strong enough.

The ordinary map UI must remain shallow. This is primarily a data-authority/runtime repair, not a new toolbox.

---

## 1. Root-cause finding: the `145M` North Sea population label

### Current data flow

`world-map/3d-demography.js` currently builds population labels by combining:

- population value from `world-country-demography.json`; and
- label coordinates from REST Countries `latlng`.

The REST request is intercepted by `world-map/3d-hover.js`, whose fallback path synthesizes country coordinates from map geometry when the same-origin REST snapshot and the remote REST endpoint are unavailable.

The fallback helper `representativePoint(feature)` currently returns the midpoint of a geometry-wide bounding box.

### Failure mechanism

That midpoint algorithm is invalid for geometries crossing the antimeridian or composed of distant parts. A Russia-like geometry can have longitudes near both `-180` and `+180`; a naive min/max midpoint then collapses toward longitude `0`, around northern Europe / the North Sea. Population remains attached to `RUS`, so a roughly 145M label can be rendered at a nonsensical ocean position.

This is the strongest explanation of the observed `145M` North Sea marker and, regardless of whether the deployed incident passed through exactly that fallback path, it is a real architectural defect that can produce that class of error.

### Design decision

Population labels must no longer use a second independent country-coordinate authority.

A population label will be derived from one resolved map entity:

`entity id -> entity geometry -> validated anchor -> entity population`

### Anchor resolution

Introduce one shared map-anchor resolver with this priority:

1. explicit, versioned `label_anchor` from the map-entity registry when one is required;
2. a local primary-capital coordinate only when it belongs to the same entity and is usable as a label anchor;
3. a geometry-derived point-on-surface / representative interior point based on the owning polygon or largest relevant polygon component;
4. no label if no safe anchor can be established.

A geometry-wide bounding-box midpoint is explicitly forbidden as an entity anchor.

For multi-polygons and antimeridian-crossing geometries, the resolver must work per component and choose an interior/representative component rather than averaging global extremes.

### Validation

A dedicated validator must reject:

- population label entries without a resolvable entity id;
- label anchors outside any reasonable ownership/geometry contract;
- use of the old geometry-wide bounding-box midpoint as the population-label fallback;
- a regression fixture where Russia's fallback anchor resolves near longitude zero / the North Sea;
- population-label generation from a population record and an unrelated coordinate record.

The test fixture should explicitly encode the antimeridian case so this bug cannot return under another country's name.

---

## 2. Map entities: preserve 195 countries and add first-class territories

### Existing boundary

`data/countries/index.json` correctly defines the canonical sovereign-country scope as 195 entries: 193 UN Member States + Holy See + State of Palestine.

Greenland is not a sovereign state in that index, but the current geography source contains a `GRL` polygon and several project/empirical datasets already refer to `GRL`. The browser therefore currently has a split state:

- Greenland exists geographically;
- Greenland exists relationally in some datasets;
- Greenland does not receive the same generated runtime treatment as a canonical country.

### Design decision

Do not add Greenland to the 195-country index.

Create a separate first-class map-entity owner:

`data/world-map-entities.json`

This owner contains non-sovereign entities that must behave as meaningful map objects. It complements, rather than replaces, `data/countries/index.json`.

Initial required entity:

```json
{
  "id": "greenland",
  "iso3": "GRL",
  "name": "Greenland",
  "entity_type": "self-governing-territory",
  "sovereignty_context": "Kingdom of Denmark",
  "constitutional_parent": "DNK",
  "capital": "Nuuk",
  "canonical_country": false,
  "label_anchor": [-51.7216, 64.1835],
  "population": {
    "value": 56740,
    "reference_date": "2026-01-01",
    "source": "Statistics Greenland",
    "source_url": "https://stat.gl/publ/en/BE/202601/contents/Population%20estimates.htm"
  }
}
```

The exact anchor is a display anchor, not a claim that Greenland's population is concentrated at one point. It is intentionally distinct from a centroid calculation and should be labelled as such in metadata.

### Runtime model

The generated World Map runtime gains an `entities` plane:

```json
{
  "countries": 195,
  "territories": {...},
  "by_id": {...},
  "renderable_entity_count": ...
}
```

Country analytics remain keyed to the sovereign-country index. Entity-aware browser functions resolve both country and territory ids where appropriate.

Required runtime APIs include:

- `entity(code)`
- `entityName(code)`
- `entityType(code)`
- `populationObservation(code)`
- `labelAnchor(code)`

Existing `members(id)` and Axis functions remain country-compatible and gain explicit territory handling rather than silently dropping `GRL`.

### Greenland behavior

Greenland must become:

- selectable by clicking its polygon;
- inspectable in the upper-left card;
- nameable as Greenland rather than an anonymous territory/map polygon;
- population-labelled from Statistics Greenland;
- a North anchor in the project Axis runtime;
- part of Arctic and North Atlantic functional-chain context;
- related to Denmark through an explicit constitutional/Kingdom edge;
- able to carry sourced empirical memberships/participation where territory representation differs from sovereign-state membership.

The card must state the entity type clearly. It must not call Greenland a sovereign country.

### Faroe Islands

Faroe Islands should use the same entity architecture when the canonical geometry/rendering source can represent them reliably. `FRO` must not block the Greenland fix. If the current polygon source lacks a usable Faroe geometry, keep FRO in the entity registry as `render_status: pending-geometry` rather than inventing a polygon.

---

## 3. Africa-first integration model

### Principle

Africa should become richer as Africa before N/E/S/W is used as an external strategic reading.

The directional model must not reduce African states to appendages of Europe, the United States, China, Russia, Australia, or any other external pole.

### Empirical African regional systems

Create a focused canonical owner:

`data/world-africa-regional-systems.json`

It records African regional systems, memberships, provenance, current status, and overlaps.

The African Union recognises eight Regional Economic Communities (RECs) as pillars/building blocks of continental integration:

- Arab Maghreb Union (AMU/UMA)
- COMESA
- CEN-SAD
- East African Community (EAC)
- ECCAS
- ECOWAS
- IGAD
- SADC

Source: African Union, `https://au.int/en/recs`.

The first implementation should fully encode at minimum:

- AU
- EAC
- SADC
- ECOWAS current membership
- the three Sahel states that left ECOWAS, represented explicitly as former/current-transition relations rather than stale members
- the remaining AU-recognised RECs where current official membership can be sourced cleanly in the same wave

EAC current partner-state spine is eight states: Burundi, DRC, Kenya, Rwanda, Somalia, South Sudan, Uganda and Tanzania. Source: `https://www.eac.int/eac-partner-states`.

SADC current membership is 16 states: Angola, Botswana, Comoros, DRC, Eswatini, Lesotho, Madagascar, Malawi, Mauritius, Mozambique, Namibia, Seychelles, South Africa, Tanzania, Zambia and Zimbabwe. Source: `https://www.sadc.int/member-states`.

ECOWAS current membership must reflect the effective 29 January 2025 withdrawal of Burkina Faso, Mali and Niger. The current ECOWAS member list is Benin, Cabo Verde, Côte d’Ivoire, The Gambia, Ghana, Guinea, Guinea-Bissau, Liberia, Nigeria, Sierra Leone, Senegal and Togo. Sources: `https://www.ecowas.int/burkina-faso-mali-and-nigers-withdrawal-from-ecowas-is-now-a-reality/` and `https://www.ecowas.int/creation-history/`.

### Browser behavior

African regional systems are contextual empirical structures. They do not become a new permanent top-bar category wall.

They should be available through:

- country-card membership/context;
- relationship lines/context;
- functional-chain exploration;
- the existing Groups surface only where the menu can remain usable;
- an Africa regional context API for future analysis.

Overlapping REC memberships are expected and should be visible rather than normalized away.

### African functional chains

Extend the chain model with high-value African relationship structures where the data supports them, including:

- East African integration
- Southern African development/industrial system (existing Southern African chain deepened)
- West African integration / ECOWAS current system
- Sahel transition system
- North African / Mediterranean interface
- African continental integration / AfCFTA scaffold

A chain may be empirical, derived, or mixed, but its epistemic type must be explicit.

---

## 4. Selective African Axis orientations

### Rule

REC membership alone never determines an Axis orientation.

An orientation requires one or more of:

- explicit/recovered Tim project language;
- unusually strong external institutional/security/economic correspondence;
- an already-established project pattern such as BRICS-as-East or Southern-African-South;
- a carefully documented bridge/frontier relationship.

Use `bridge`, `secondary`, or `frontier` when a clean primary classification would overstate the case.

Leave countries unresolved when the directional reading is weak.

### Required profile refinements

#### South Africa — retain

- South `primary`, high confidence.
- East `secondary`, high confidence, preserving BRICS overlap.

#### Egypt — deepen

- East `secondary`, preserving BRICS/project correspondence.
- West `bridge` or `secondary` with empirical basis, because Egypt is a designated U.S. Major Non-NATO Ally.
- Regional note: Mediterranean / North African / Middle Eastern junction.

#### Ethiopia — retain/deepen

- East `secondary` through the project BRICS reading.
- African institutional identity remains primary context; do not portray Ethiopia as simply an East satellite.

#### Nigeria

- East `bridge`, not primary, where BRICS partner status/project-East correspondence is represented.
- ECOWAS / West African regional role remains the stronger African structural context.

#### Uganda

- East `bridge`, not primary, where BRICS partner correspondence is represented.
- EAC and East African context remain first-class.

#### Morocco

- North `bridge`, medium/high confidence, based on the unusually dense Euro-Mediterranean and EU strategic relationship plus recovered North-horizon language.
- West `secondary` or `bridge` as empirical correspondence through U.S. security alignment/MNNA status.
- Do not label Morocco North-primary unless stronger project evidence is recovered later.

EU-Morocco source basis includes the 29 January 2026 Association Council description of a longstanding, multidimensional and privileged strategic partnership: `https://www.consilium.europa.eu/en/press/press-releases/2026/01/29/communique-conjoint-de-la-haute-representante-kaja-kallas-et-du-ministre-des-affaires-etrangeres-du-maroc-nasser-bourita-suite-a-la-tenue-du-quinzieme-conseil-d-association-ue-maroc/`.

#### Tunisia

- North `bridge`, medium confidence, based on Euro-Mediterranean integration.
- West `secondary` empirical correspondence may be encoded from U.S. MNNA status.

#### Algeria

- North `frontier` or `bridge`, low/medium confidence.
- Do not make Algeria North-primary; preserve strategic autonomy and ambiguity.

#### Kenya

- West `secondary` or `bridge`, empirical correspondence through current U.S. MNNA status.
- EAC remains the stronger regional structure.

The current U.S. MNNA list includes Egypt, Kenya, Morocco and Tunisia. Source: `https://samm.dsca.mil/glossary/major-non-nato-allies`.

#### Tanzania

- South `secondary` or `bridge`, medium confidence through Southern African system participation.
- Explicitly retain EAC overlap; Tanzania is a model case for multi-system membership.

#### Angola

- South `secondary`, medium confidence through the Southern African system, without implying subordination to South Africa.

#### DRC

- Do not force a single Axis.
- Represent DRC as an EAC + SADC multi-regional bridge in empirical systems.
- Any later Axis placement requires stronger evidence.

### Countries deliberately left unresolved

Most African states should remain without a directional orientation until there is a defensible reason to add one. Language, colonial history, geography, or one trade relationship is not sufficient by itself.

---

## 5. Entity-aware selection and relation model

The current selection controller accepts countries known through the 195-country name index or REST runtime. This must become entity-aware.

### Resolver

Introduce one shared resolver concept:

```js
resolveMapEntity(code) -> {
  code,
  name,
  entityType,
  canonicalCountry,
  geometryAvailable,
  population,
  anchor,
  parentRelations,
  axisProfile,
  systems
}
```

Country selection, hover, card, demography labels, chains, gateways and relation context should use this resolver rather than each module independently deciding whether a code is a country.

### Compatibility

Existing country APIs remain valid for the 195 sovereign records.

No existing module is required to treat every territory as a country. Entity-aware modules explicitly opt into the broader resolver.

---

## 6. Data/runtime ownership

### Canonical owners

- `data/countries/index.json` — sovereign-country identity, stays at 195.
- `data/world-map-entities.json` — non-sovereign first-class map entities.
- `data/world-axis-profiles.json` — project directional interpretation for countries and supported territories.
- `data/world-africa-regional-systems.json` — African regional-system memberships and current/historical status.
- `data/world-institution-memberships.json` — existing global institutional groups; may reference African systems where appropriate but must not duplicate their detailed status history.
- `data/world-system-chains.json` — functional-chain summaries.
- `data/world-map-data-runtime.json` — generated browser projection of the above.

### No duplicated authority

Greenland population is owned once in the entity registry (or a dedicated territory observation owner if implementation reveals a better existing observation boundary) and projected into runtime/demography.

African REC membership is owned once in the Africa regional-systems owner and projected outward. Do not separately maintain divergent EAC/SADC/ECOWAS lists in several JSON files.

---

## 7. UI behavior

### Greenland

Clicking Greenland should feel almost identical to clicking a country, with one important difference: the card header clearly says something equivalent to:

`Self-governing territory · GRL`

rather than `Canonical country`.

The card may show:

- Greenland
- population and reference date/source
- capital Nuuk
- Kingdom/constitutional relation to Denmark
- North orientation
- Arctic / North Atlantic chains
- available empirical groups/relations

### Population labels

Population labels remain quiet map annotations. They should not look like free-floating entity nodes detached from polygons.

At minimum:

- label placement is entity-owned;
- hover/click can identify the owning entity;
- labels for tiny populations may use K rather than M;
- labels may be suppressed where collision/zoom rules make them misleading.

### Africa

No Africa-specific permanent toolbox.

When an African country is selected, its card can expose:

- AU / REC memberships
- overlapping regional systems
- selective Axis orientation when present
- relevant functional chains
- external bridge relationships

The map should make overlap legible without implying that one external Axis explains the country.

---

## 8. Validation and TDD requirements

Create a dedicated validator before implementation and observe it fail.

It must require all of the following:

### Entity integrity

- sovereign-country count remains exactly 195;
- `GRL` exists as a non-country map entity;
- `GRL` has population source/date, capital, constitutional parent and label anchor;
- `GRL` is selectable/runtime-resolvable;
- `GRL` has North and Arctic/North Atlantic context;
- no code path describes Greenland as a sovereign country.

### Population-anchor integrity

- demography population labels no longer depend on REST `latlng` as the authoritative placement source;
- no geometry-wide bounding-box midpoint fallback is accepted;
- antimeridian regression fixture passes;
- population and anchor resolve through the same entity id.

### Africa integrity

- AU REC owner exists with provenance;
- EAC has 8 current partner states;
- SADC has 16 current member states;
- ECOWAS current list excludes Burkina Faso, Mali and Niger and records the withdrawal date/status rather than deleting history;
- African REC overlap is preserved;
- DRC can simultaneously resolve to EAC and SADC;
- Tanzania can simultaneously resolve to EAC and SADC;
- no Axis assignment is automatically inferred from REC membership;
- new African Axis records carry `basis`, `confidence`, `role`, and explanatory note.

### Browser/runtime integrity

- entity resolver exists;
- selection accepts `GRL`;
- country-card equivalent displays entity type;
- runtime projects territory and Africa-system context;
- ordinary top bar does not gain an Africa/territory tools explosion.

---

## 9. Implementation order

1. Red validator for entity/population/Africa contracts.
2. Add map-entity owner with Greenland.
3. Replace population coordinate authority with entity-owned anchor resolver and antimeridian-safe geometry fallback.
4. Extend runtime generator to project territories/entities.
5. Make selection/hover/card/runtime entity-aware for Greenland.
6. Add Africa regional-systems owner and current REC memberships.
7. Project African systems into runtime/card/relations/chains.
8. Add only the approved selective African Axis refinements.
9. Run full repository quality suite, verify exact branch head, open/update PR, then merge only when exact-head CI is green.

---

## 10. Out of scope for this wave

- converting every ISO dependency/territory into a first-class map entity;
- redefining Greenland as a sovereign state;
- a fifth Africa Axis;
- forcing all African states into N/E/S/W;
- a synthetic Africa alignment score;
- a synthetic geopolitical loyalty score;
- full AfCFTA trade-flow ingestion;
- every African infrastructure corridor;
- moving population dots by hand as a visual patch.

The architecture should make those future additions possible without reopening the basic country/entity distinction again.
