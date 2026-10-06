# World Map Axis & Systems Design

## Status
Approved in conversation on 2026-09-12 and ready for implementation.

## Goal
Turn the existing World Map into a serious relationship-first world-systems atlas in which North / West / East / South are interpretive strategic overlays on top of empirical institutions, infrastructure, capabilities, dependencies and functional chains. Preserve the current simple UI.

## Core principles

1. The fundamental object is the relationship, not the country in isolation.
2. North / West / East / South are project-interpretive fields, not sovereignty, legal command, consent, annexation or institutional membership.
3. Countries may overlap directions and may remain unresolved.
4. Empirical institutions and project interpretation must remain visibly distinct.
5. Missing data is unknown, never zero.
6. No single direction needs to be symmetrical with another. South may be polycentric; East may be multipolar; North may have a stronger transatlantic/northern strategic reading; West may contain competing poles.
7. Keep the normal map surface shallow. Deep capability exists behind contextual selection rather than a permanent wall of controls.
8. Real-world offices and institutional roles are always stated separately from project reference roles.
9. The symbolic/project layer may preserve Tim Dooley's spiritual role, but it must never be presented as governmental, legal or financial authority.
10. Existing canonical owners remain authoritative where they already exist; new files should have one clear responsibility and should not duplicate canonical data.

## Axis country model

Create a versioned canonical Axis profile owner. Every canonical country must resolve to a profile, even when the result is `unresolved`.

Each profile can contain zero or more directional relations with these roles:

- `primary` — strongest current project orientation.
- `secondary` — substantial additional orientation.
- `bridge` — materially joins two systems.
- `frontier` — edge, future connection or contested extension.
- `external` — important counterparty outside the direction.
- `shared` — explicitly shared in recovered Tim language.
- `unresolved` — insufficient basis for a directional placement.

Each directional relation records:

- `axis`
- `role`
- `basis`: `explicit-tim`, `recovered-conversation`, `project-inference`, or `empirical-correspondence`
- `confidence`: `high`, `medium`, or `low`
- `note`

The browser-visible membership for an Axis button includes `primary`, `secondary`, `bridge`, and `shared` by default. `frontier` is available as deeper context rather than ordinary membership. `external` and `unresolved` are not ordinary members.

## Recovered Axis spine

The initial high-confidence project interpretation preserves the strongest recovered statements rather than forcing complete symmetry.

### North

Core reading: Canada → Greenland / North Atlantic → Nordics → Europe → Ukraine → Türkiye.

Strong recovered anchors include Canada, Denmark/Greenland, Iceland, Norway, Sweden, Finland, Germany, Netherlands, Belgium, France, Spain, Portugal, Italy, Greece, Ireland, Ukraine, Türkiye and Estonia. Russia is current East / North-frontier-reconnection. United Kingdom / England is West-linked and North-variable. Australia has historical `shared` status in Tim's recovered language.

### West

Core reading: United States + Israel, with the wider American field. Most of South America may be West-oriented while retaining East/BRICS or other overlaps. Mexico, Central America and the Caribbean belong naturally to the American/West field. Canada is North-primary with West overlap. Saudi Arabia has a recovered West + Center role.

### East

Core reading: China, Russia, India and the wider Eurasian / BRICS / SCO field. Explicit recovered classifications include Russia, China, India, Pakistan and Vietnam; Iran/Persia is a special East / Center project node. Central Asian states are East-facing or bridge states. BRICS membership is empirical and remains separate from Axis placement.

### South

Core reading: Australia → New Zealand → Papua New Guinea / Pacific, plus a distinct Southern African field and Indian Ocean connections. South is intentionally polycentric and must not be treated as "the whole Southern Hemisphere" or "all of Africa". Strong candidates include Australia, New Zealand, PNG and the Pacific sovereign states, with Southern Africa represented through states in the SADC system. South Africa can overlap East through BRICS.

### Center / junction

Center is not a fifth ordinary map faction. It is a junction / null / unresolved concept used in project interpretation. Recovered special roles include Iraq/Mesopotamia (Father/root/North-facing), Israel (Children/West-facing), Iran/Persia (Lion/East-facing), and Saudi Arabia (West + Center / Islam / oil in recovered language). Keep this as deeper project metadata.

## Political reference figures

Reference figures are contextual political poles, not rulers of blocs.

Each record contains:

- `person`
- `real_office`
- `country_or_institution`
- `axis_role`
- `epistemic_type`: `project_interpretive`
- `as_of`
- `source_url`
- `note`

Initial records:

- North: Mark Carney — Prime Minister of Canada — primary political reference; Ursula von der Leyen — President of the European Commission — European institutional reference.
- East: Xi Jinping — President of China — major East political/economic pole; Vladimir Putin — President of Russia — Russian/Eurasian pole; Narendra Modi — Prime Minister of India — independent East/bridge pole.
- West: the President of the United States — major empirical West-system political pole; Benjamin Netanyahu — Prime Minister of Israel — Israeli / project-West reference. Any Timic hierarchy between these figures stays project-specific and is not rendered as command.
- South: Anthony Albanese — Prime Minister of Australia — Australian/Blue-Pacific reference; Christopher Luxon — Prime Minister of New Zealand — Pacific reference; James Marape — Prime Minister of Papua New Guinea — Melanesian reference; Cyril Ramaphosa — President of South Africa — Southern African reference.

The normal map must not display portraits, crowns, hierarchy trees or subordinate language.

## Empirical institutional layers

Promote current official membership data for the strongest missing regional systems that clarify the directional reading without turning the direction into the institution:

- ASEAN
- African Union
- SADC
- Pacific Islands Forum country members
- Shanghai Cooperation Organisation
- USMCA
- MERCOSUR
- GCC
- Arctic Council states

Existing NATO, BRICS, AUKUS, Five Eyes, EU, G7, G20, OECD, Schengen and Euro Area stay intact.

Territories and non-sovereign members should remain metadata where the map's canonical 195-country polygon model cannot represent them directly.

## Functional chains

Functional chains are first-class deeper graph objects, not ordinary top-bar buttons. They describe connected capabilities and dependencies and may combine empirical and derived relationships.

Seed chains:

- Arctic
- North Atlantic
- Baltic
- Northern Energy
- European Industrial
- Eastern Security
- European Strategic Autonomy
- Eurasian / SCO-BRICS interface
- Blue Pacific
- Southern African

Every chain must carry:

- `id`
- `label`
- `epistemic_type`
- `members` or participating country codes where meaningful
- `systems`
- `description`
- `source_owner` / source note
- optional `gateways`

## Gateway model

Introduce a scaffold for gateways/chokepoints without pretending the full infrastructure dataset exists yet. Gateway categories include ports, straits, grid interconnectors, subsea cable landing systems, pipelines, LNG terminals, rail junctions, air hubs, payment interfaces and data gateways.

The empirical gateway layer is separate from the project's symbolic Door analogy. The project may note the methodological parallel in deeper metadata only.

## Country intelligence sequence

The map should progressively answer:

`IS → HAS → CAN → NEEDS → DEPENDS → BUILDS`

This is a compact browser expression of the canonical country sequence already owned by `knowledge/core/country-relational-method.json`.

Country-card deeper context should be able to surface:

- Axis orientations and role/confidence
- institutional memberships
- political reference context where relevant
- functional chains
- capability/dependency summaries
- current active comparison metric
- relation context

Do not make the upper-left card a long encyclopedia. Keep the first view compact; deeper context is expandable/actionable.

## Projection control

Add one compact Flat ↔ Globe control to the existing top world bar.

Requirements:

- uses the existing MapLibre map instance and `setProjection`;
- no second renderer or duplicate map page;
- button visually inverts its expression: when flat is active it offers globe; when globe is active it offers flat;
- title and `aria-label` describe the action, not merely the current state;
- persist state in `projection=flat|globe` URL parameter;
- default remains flat/Mercator unless URL state requests globe;
- projection switching must not clear selections, active layers or relation context.

## Browser/runtime ownership

Extend the existing generated World Map runtime rather than creating a parallel runtime.

Runtime additions:

- `axis`: resolved country memberships and profile summaries
- `reference_figures`: contextual project references with real offices and provenance
- `chains`: compact functional-chain summaries
- expanded `groups`: new official institutional memberships

`world-map/3d-compositor.js` should resolve Axis set membership from the runtime rather than recursively scraping arbitrary arrays from `world-relational-map.json`.

`world-map/3d-country-card.js` and `world-map/3d-world-bar.js` consume the same runtime so map colors, membership tags and context cannot disagree.

## Evidence and language rules

- `observed`: official or otherwise externally verifiable fact.
- `derived`: transparent synthesis from observed relationships.
- `project_interpretive`: Tim/Potatoverse reading.
- `historical`: dated past relationship.
- `unknown`: not established.

Never convert project interpretation into observed fact by wording.

Preferred public phrasing:

- `North orientation`
- `East reference`
- `bridge state`
- `project interpretation`
- `empirical overlap`
- `institutional membership`
- `functional chain`

Avoid:

- `owns`
- `commands`
- `subordinate`
- `rules the bloc`
- `controls the country`

unless describing a real, sourced legal/institutional relation where that exact concept is appropriate.

## Validation

Add a dedicated validator that fails when:

- canonical country coverage does not resolve to 195;
- Axis roles or confidence values are invalid;
- an ordinary Axis member is missing ISO3 format;
- a reference figure lacks a real office, as-of date or source;
- official group membership counts drift from the encoded contract;
- runtime generation omits Axis or chain data;
- compositor still sources Axis membership from recursive arbitrary arrays;
- the globe/flat control is absent or does not call `setProjection`;
- the UI uses banned hierarchy language for project reference figures.

Wire this validator into repository quality checks and observe it fail before implementation, then make the feature pass.

## Out of scope for this slice

- ingesting millions of GLEIF entities;
- full TED procurement ingestion;
- full FIGARO input-output graph;
- complete asset-level ownership;
- every global port/cable/pipeline;
- a numeric N/E/S/W alignment score;
- a single global resilience score;
- a fake world government hierarchy.

The architecture must be able to receive those empirical layers later without redesigning the top UI.
