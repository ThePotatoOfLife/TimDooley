# World Relational Atlas — Expanded Composable Registry Design

Date: 2026-09-11
Status: approved design; implementation target
Primary surface: `world-map/3d.html`

## Goal

Turn the 3D World Relational Atlas into a visual query engine with a tiny ordinary UI and a large internal registry. New statistics, organizations, project fields, relation families, physical assets and derived capability layers should normally enter through registry data rather than bespoke controls.

## Product rule

**Simple surface, deep engine.** The map should expose only the controls useful to the current question while retaining a much richer internal vocabulary.

## Canonical inputs

The registry must unify, not duplicate, the mature taxonomies already in the repository:

- `data/domain-coupling.json` — real-world domains and typed relationships;
- `data/indicator-catalog.json` — measurable country/system indicators;
- `knowledge/core/country-relational-method.json` — country capability/dependency blueprint, resilience and functional chains;
- `data/world-relational-map.json` — project Axis and empirical memberships;
- `data/world-country-demography.json` — population/religion runtime;
- `data/map-layer-placement-matrix.json` — rules for spatial vs relational vs contextual rendering;
- canonical country dossiers under `data/countries/`.

The browser registry is a presentation projection over these canonical owners, not a replacement database.

## Visual channels

Every registry entry declares a preferred visual channel:

- `fill` — one scalar/ordered country field at a time;
- `pattern` — categorical/set membership and overlap;
- `outline` — selection only;
- `line` — typed relations and flows;
- `point` — real geocoded places/assets;
- `height` — optional scalar, used sparingly;
- `card` — contextual nonspatial information;
- `timeline` — dated state/history;
- `scene` — nonspatial graph/Axis/specialist representation.

No layer may silently steal a channel from an incompatible semantic type.

## Registry families

### Orientation / project fields
North, West, East, South, geographic North/Arctic, project North, future versioned project fields.

### Institutions & groups
NATO, EU, BRICS, USMCA, ASEAN, African Union, MERCOSUR, GCC, SCO, AUKUS, Five Eyes, G7, G20, OECD, Schengen, Euro Area, Arctic Council, Nordic Council and future explicit organizations.

### People & demography
Population, growth, density, median age, fertility, life expectancy, urbanization and other compatible population indicators.

### Religion & belief
Christian, Muslim, Hindu, Buddhist, Jewish, other religions, unaffiliated, dominant composition and defensible diversity measures. Religion remains demographic context and never implies loyalty or behavior.

### Government & law
Political system, constitutional form, executive, legislature, courts, regulatory jurisdiction and institutional membership. Mostly contextual/card or point data rather than polygon moral ranking.

### Economy & public finance
GDP, GDP/person, PPP/person, growth, productivity, inflation, unemployment, revenue, spending, fiscal balance, debt, debt/GDP and public investment.

### Finance & capital
Central banks, banking, FDI, credit, pensions, capital markets and funding networks.

### Companies & ownership
Major companies, state-owned firms, parent/child structures, beneficial ownership and control relations.

### Trade & value chains
Exports, imports, concentration, suppliers/customers, routes, product chains and input-output dependencies.

### Industry
Manufacturing, pharmaceuticals, aerospace/defence, semiconductors, food, machinery, chemicals and other strategic sectors.

### Energy
Generation mix, import dependence, grids, interconnectors, nuclear, renewables, storage, oil/gas and cross-border flows.

### Materials & resources
Critical minerals, agriculture, water, fisheries, forestry and strategic material dependencies.

### Infrastructure
Ports, airports, rail, roads, pipelines, cables, grids, telecoms, water and logistics corridors.

### Technology & digital
AI/compute, cloud, telecoms, cyber, robotics, software, digital government and critical technology dependencies.

### Research & innovation
Universities, R&D spending, researchers, patents, research networks and knowledge flows.

### Labour & skills
Employment, participation, wages, skills, shortage occupations and labour mobility.

### Migration & diaspora
Stocks, flows, origins/destinations and skills movement.

### Health & education
Spending, capacity, outcomes, institutions, education expenditure and skills formation.

### Environment & climate
Emissions, climate exposure, land/water indicators and infrastructure/environment interactions.

### Security & defence
Alliances, defence spending, industrial base, cyber, forces and strategic geography.

### Capability
Derived relational layers describing what a country/system can produce, enable or provide.

### Dependency
Strategic imports, supplier concentration, foreign capital dependence, external security dependence and chokepoints.

### Resilience
Redundancy, substitutability, storage, diversity, recovery capacity and efficiency-vs-resilience tradeoffs.

### Functional chains
Arctic, North Atlantic, Baltic, Northern Energy, European Industrial, Eastern Security, European Strategic Autonomy and future explicit multi-country capability chains.

### Projects & procurement
Tenders, contracts, grants, programmes and infrastructure projects.

### Evidence / archive health
Coverage, freshness, source class, confidence, contradiction count, unresolved research and last verification.

### Time / history
Past membership, leadership, borders/status, reforms, wars, institutional change and role occupancy.

### Programme / intervention / repair
North Programme and other proposed interventions, plus documented repair/closure state. These remain separate from empirical observations.

## Entry schema

Each runtime entry has, where applicable:

- `id` — stable identifier;
- `label`;
- `family`;
- `kind` — `set`, `scalar`, `composition`, `network`, `flow`, `place`, `derived`, `context`, `timeline`;
- `visual_channel`;
- `epistemic_type` — `observed`, `derived`, `project_interpretive`, `scenario`, `contextual`;
- `map_priority` — ordinary, contextual, advanced, specialist;
- `queryable`;
- `color` / palette metadata;
- `unit`, `transform`, `direction` for scalar entries;
- `source_owner`;
- `period` / version metadata;
- `requires` and `derived_from`;
- `compatible_with` / exclusions when needed;
- `spatiality` — polygon, point, route, relation, nonspatial;
- `roles` for member/partner/candidate/observer-type sets;
- `notes` / epistemic boundary text.

## Relationship vocabulary

The query/edge engine should preserve typed relations rather than generic connection lines. Initial normalized relation verbs include:

`funds`, `owns`, `controls`, `depends-on`, `supplies`, `trades-with`, `employs`, `regulates`, `represents`, `practices`, `influences`, `connects`, `flows-through`, `competes-with`, `cooperates-with`, `located-in`, `historical-predecessor-of`, `textual-context-for`, `participates-in`.

These map into higher UI relation families such as trade, ownership, funding, debt/finance, procurement, energy, infrastructure, security, research/technology, labour/migration, institutional/political and strategic dependency.

## Country analytical sequence

The registry and country card should progressively support:

`what it is → what it has → what it can do → what it needs → who depends on it → what it depends on → what it can only do with others → what others can only do with it → what it is building → where it is going`

This is the main route from encyclopedia-style country facts toward capability topology.

## Query semantics

- one scalar fill may be active at a time;
- multiple set/pattern layers may be active;
- 1–3 set memberships may render as deterministic stripes/patterns;
- >3 categorical layers collapse to overlap intensity/count plus exact membership in card;
- selection is always outline/emphasis, never semantic fill;
- when 2+ queryable layers are active, expose `ANY | ALL`;
- scalar thresholds are supported by the engine even if the first UI only exposes simple activation;
- aggregate summaries must report coverage and never convert missing to zero.

## Ordinary UI

Target persistent surface:

`Search | N | W | E | S | Groups ▾ | Religion ▾ | Stats ▾ | Relations ▾ | Reset`

No persistent Tools hierarchy for ordinary use. Time, Evidence, deep Trace and Axis specialist controls remain available contextually or through secondary access.

## Country card

One compact country card should normally show identity, flag, capital, population, GDP, GDP/person, government/leader/head of state where sourced, important memberships, Axis class, religion summary and freshness. It promotes active-layer information so it explains the current map question.

## Spatial honesty

The placement matrix remains authoritative: real countries, cities, institutions, infrastructure, routes and geographically meaningful flows can render on Earth; abstract theology, formal-science analogy, symbolic Door/Tree/Swamp states and other nonspatial concepts open as cards/scenes/graphs rather than fake map pins.

## First implementation slice

1. Add a canonical browser-facing registry JSON generated manually from existing canonical owners for the first slice.
2. Add a `3d-layer-registry.js` loader/API.
3. Add a `3d-compositor.js` state/composition API supporting one scalar + multiple sets.
4. Add a small registry-driven `3d-world-bar.js` with N/W/E/S, Groups, Religion, Stats, Relations, ANY/ALL and Reset.
5. Retire ordinary loading of `3d-lenses.js` so it cannot fight the compositor for country fill.
6. Add validation that checks schema/channel rules and bootstrap integration.
7. Preserve all current deeper modules behind existing compatibility surfaces until the compact replacement proves stable.

## Success criteria

- adding a new supported layer normally means adding registry data, not another bespoke menu;
- North + NATO + EU can coexist without flattening into one category;
- a scalar such as GDP/person can coexist with set membership and selection;
- ordinary map UI is smaller than the current Tools surface;
- missing or failed optional registry data leaves core geography usable;
- observed facts, derived data and project interpretation remain visibly distinct.