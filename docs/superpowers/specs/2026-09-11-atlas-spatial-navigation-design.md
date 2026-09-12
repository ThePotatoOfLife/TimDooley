# World Relational Atlas — Spatial Navigation Design

Date: 2026-09-11
Status: approved interaction direction; implementation not yet started
Scope: 3D World Relational Atlas UI architecture
Branch: `feature/3d-map-relationship-height`

## 1. Purpose

The Atlas has accumulated substantial capability: country observables, relationship tracing, country comparison, empirical networks, project fields, religion/worldview facets, time state, evidence, D1–D11 Axis operators, relation inspection, map-height surfaces, and progressive lazy loading. The current UI exposes too much of the implementation vocabulary directly. Users must understand labels such as Layers, Trace, View, Height, relation type, trace depth, fields, networks, and Axis modules before they can discover the underlying information.

This redesign changes the interaction model without discarding the analytical architecture. The map becomes the organizing surface, and controls are arranged by the meaning of the question being asked.

The stable semantic grammar is:

- **World** — What is there?
- **Relations** — What connects it?
- **Time** — How did it change?
- **Axis** — How are we interpreting or transforming it?
- **Selection context** — What can I do with the thing I just clicked?

Search remains available as a shortcut but is not the primary navigation model.

## 2. Design goals

1. A new user can discover useful features without learning Atlas implementation terms.
2. A returning user can reach any major capability in one to three interactions.
3. New datasets have an obvious semantic home before they are implemented.
4. The normal UI exposes meaning, not rendering mechanics.
5. The map remains visually primary.
6. Advanced analytical depth remains available without cluttering the default state.
7. Active map state is always visible and removable.
8. Lazy loading and current performance boundaries are preserved.
9. Empirical, derived, project-symbolic, and scenario states remain epistemically distinct.
10. The navigation architecture should survive future growth in places, flows, companies, infrastructure, finance, research, treaties, and project lenses without another redesign.

## 3. Core layout

The map occupies the center. Four semantic handles live around it in fixed positions:

- **Top: Axis**
- **Left: World**
- **Right: Relations**
- **Bottom: Time**

A selected object gets a contextual action wheel/dock close to the bottom center or near the selection when space allows.

A small utility cluster in a corner contains only secondary functions:

- Search
- Reset / clear state
- Camera / visual settings
- Optional links / archive navigation

The existing permanent top-level controls `Inspect`, `Layers`, `Trace`, `Time`, `View`, and `More` are removed from the normal interaction path. Their functionality is redistributed into the semantic zones or advanced settings.

## 4. Visual language

Colors communicate semantic families, not quality or rank. Color is a navigation aid rather than a moral or Axis score.

Recommended family palette:

- **World / geography:** muted green
- **Economy / finance:** gold
- **People / society / migration:** violet
- **Infrastructure / technology:** cyan
- **Energy / environment:** teal with restrained warm accents where necessary
- **Relations / networks:** blue
- **Faith / worldview / culture:** warm amber
- **Time / history / change:** purple
- **Evidence / provenance:** neutral white / gray
- **Axis / project-symbolic:** pale icy blue / luminous white

Rules:

- Use family colors consistently across handles, menu tiles, active chips, map legends, and inspector sections.
- Do not give every dataset a unique color.
- Do not use color alone for state; pair it with text, icon, shape, or active outline.
- Up/down Axis symbolism must not be reused to imply empirical value judgments.

## 5. Active-state chips

Any state that materially changes the map is represented by a removable chip near the map edge, preferably under the header/utility region.

Examples:

- `GDP ×`
- `NATO ×`
- `Relations ×`
- `2020 ×`
- `D6 · Spiral ×`

Chips answer the question: **why does the map currently look like this?**

State categories:

- one base surface
- zero or more overlays
- zero or more relation families / network modes
- one time state
- zero or one primary Axis lens, with optional sub-operator state

Clicking `×` deactivates that state. There should be no need for `off` entries inside ordinary selectors.

## 6. World zone

### 6.1 Purpose

World contains things or attributes that can honestly be anchored to places, countries, cities, institutions, or physical objects.

Question: **What is there?**

### 6.2 Interaction form

The left-side World handle opens a drawer. The first level contains large category tiles. Selecting a tile reveals its children in the same drawer rather than opening a separate modal.

Recommended first-level categories:

1. Places
2. People & society
3. Economy
4. Infrastructure
5. Energy & environment
6. Faith & culture
7. Technology & information
8. Institutions & organizations (for entity location, not relational membership)

### 6.3 Initial menu hierarchy

#### Places

- Countries
- Capital cities
- Major cities (future)
- Regions (future)
- Ports (future)
- Airports (future)
- Sacred sites (future)

#### People & society

- Population
- Net migration
- Life expectancy
- Fertility
- Urban population
- Labour-force participation
- Unemployment

#### Economy

- GDP
- GDP / person
- Real GDP growth
- Trade / GDP
- FDI inflow
- Future: debt / GDP
- Future: public debt
- Future: sector composition

#### Infrastructure

- Electricity access
- Future: grid interconnectors
- Future: rail
- Future: roads
- Future: ports / logistics
- Future: submarine cables

#### Energy & environment

- Net energy imports
- Renewable electricity output
- Future: generation mix
- Future: energy production
- Future: emissions / resource indicators using supported current series

#### Faith & culture

- Christian share
- Muslim share
- Hindu share
- Buddhist share
- Jewish share
- Other religions
- Unaffiliated / no religion
- Religious diversity
- Future: directly measured atheism / agnosticism
- Future: religiosity / practice / salience
- Future: languages / culture measures

#### Technology & information

- Internet use
- Future: broadband / mobile
- Future: research intensity
- Future: patents
- Future: data centers / major digital infrastructure

### 6.4 Surface behavior

The user selects the meaning, not the rendering method.

Example:

`World → Economy → GDP`

The Atlas chooses the default visualization. The existing extrusion renderer may remain the default for some numeric country metrics, but `Height` disappears from the normal UI.

A small advanced visual control may offer:

- 3D
- Color
- Both

This belongs in visual settings, not the primary data menu.

## 7. Relations zone

### 7.1 Purpose

Relations contains flows, memberships, dependencies, obligations, connections, ownership, and typed interactions between entities.

Question: **What connects it?**

### 7.2 Interaction form

The right-side Relations handle opens a drawer with relation families.

Recommended first-level categories:

1. Movement
2. Money & ownership
3. Institutions & alliances
4. Infrastructure connections
5. Knowledge & information
6. Culture & society
7. Project relationships

### 7.3 Initial hierarchy

#### Movement

- Country relationships
- Future: bilateral trade
- Future: migration origin → destination
- Future: energy flows
- Future: transport routes

#### Money & ownership

- Future: bilateral investment
- Future: debt / creditor relations
- Future: banking exposure
- Future: ownership / control
- Future: procurement / funding

#### Institutions & alliances

- EU
- NATO
- Nordic cooperation
- Arctic Council
- BRICS
- SCO
- ASEAN
- APEC
- GCC
- MERCOSUR
- SADC
- Pacific Islands Forum
- Future: treaty regimes

#### Infrastructure connections

- Future: electricity interconnectors
- Future: pipelines
- Future: rail corridors
- Future: submarine cables
- Future: shipping corridors

#### Knowledge & information

- Future: research collaboration
- Future: university networks
- Future: patent / technology transfer
- Future: information relay / standards

#### Culture & society

- Future: diaspora
- Future: language ties
- Future: cultural exchange
- Future: directly evidenced social relations

#### Project relationships

- North Axis activation / routing relations
- project symbolic relations
- comparative mythology relations

These remain clearly marked as project interpretation unless separately evidenced empirically.

### 7.4 Trace interaction

`Trace depth` is removed from the normal UI.

Flow:

1. Select a country.
2. Choose `Relations` from the selection context or open a relation family.
3. Immediate connections appear.
4. An `Expand` action appears on the network or contextual control.
5. Each `Expand` adds one further traversal layer.

Advanced settings may expose explicit hop count for debugging or power use, but normal users never need to think in `1 hop / 2 hops / 3 hops` terms.

### 7.5 Relationship selection

Clicking a relation opens a contextual relation inspector with tabs/sections:

- About
- Flow
- History
- Network
- Axis
- Sources

The current D1–D11 projection strip is moved behind the `Axis` section rather than displayed as the first conceptual burden.

## 8. Time zone

### 8.1 Purpose

Time is a bottom rail because it describes sequence, history, transitions, and change across whatever is currently selected.

Question: **How did it change?**

### 8.2 Default state

When active data has no meaningful historical dimension, the Time rail remains compact or hidden.

When selected data contains dated observations, the rail expands contextually.

Examples:

- GDP → year selector / timeline
- religion composition → `2020 snapshot`
- a treaty → entry / exit dates
- a multi-year relation → series timeline
- a D6-capable relation → cycle / spiral controls

### 8.3 Modes

Human-facing modes:

- Current
- At a date
- Compare dates
- Play through time
- Events / thresholds

The implementation may retain `current`, `as_of`, and `changed_between`, but those names do not need to be the user-facing vocabulary.

### 8.4 D3 / D5 / D6 emergence

Time is the natural bridge for the existing dimension model:

- **D3** — provenance, earlier observations, path dependence, source history
- **D5** — explicit event / threshold / gate markers
- **D6** — comparable change, recurrence, cycles, spiral / helix where justified

No threshold is generated solely from magnitude.

No spiral is shown unless comparable dated recurrence exists.

## 9. Axis zone

### 9.1 Purpose

Axis contains project lenses and analytical operators applied to the underlying World / Relations / Time state.

Question: **How are we interpreting or transforming what is already there?**

### 9.2 Interaction form

The top Axis handle opens a vertical curved spine or ladder, not a generic dropdown.

Human name first, dimension label second:

- North of North — D11
- Crown / Integration — D10
- Relay — D9
- Garden / Rooms — D8
- Tree / Generativity — D7
- Spiral / Change — D6
- Door / Threshold — D5
- World — D4
- Roots / Provenance — D3
- Swamp / Capture — D2
- Closure / Collapse — D1

D4 is visibly the middle real-world anchor.

The vertical navigator appears only when Axis is activated. It should not permanently compete with ordinary map navigation.

### 9.3 Axis sub-lenses

The Axis zone may also expose:

- North Axis
- North / West / East / South / Center fields
- Evidence
- Dependency
- Resilience
- Flow
- future analytical operators

These are lenses over existing state, not parallel datasets.

### 9.4 North semantics

Project North Axis and empirical northern geography/institutions remain distinct.

The project chain involving Tim / Throne → Son / vessel in Denmark → Denmark → Greenland → North Gate → North of North stays project canon. It must not silently replace empirical constitutional, geographic, cultural, or institutional relations.

## 10. Selection context wheel / dock

### 10.1 Principle

Actions belong to the selected object wherever possible. A user should not have to search the global navigation for actions that only make sense after selection.

### 10.2 Country selection

When a country is selected, show five primary actions:

- Overview
- Relations
- Compare
- Change
- Sources

Optional secondary action:

- Focus

`Details` is replaced by `Overview`.

`Connections` / `Relations` is unified under the same word used by the right-side zone.

### 10.3 Relationship selection

- About
- Flow
- History
- Network
- Axis
- Sources

### 10.4 City / place selection (future)

- About
- Economy
- Infrastructure
- Relations
- Country
- Sources

### 10.5 Interaction shape

Desktop:

- Prefer a compact semicircular / radial wheel if it remains legible and keyboard-accessible.
- If the wheel becomes visually noisy, use a curved segmented dock that preserves the same spatial metaphor.

Mobile:

- Replace radial positioning with a bottom action sheet using the same action order and labels.

Accessibility and touch targets take precedence over decorative geometry.

## 11. Inspector architecture

The inspector becomes contextual, not globally toggled.

Selecting a meaningful object automatically opens the inspector unless the user has explicitly pinned it closed for the session.

### Country inspector

Sections:

1. Overview
2. People & society
3. Economy
4. Infrastructure & energy
5. Faith & culture
6. Relations
7. Change
8. Sources
9. Axis (when a project/analytical lens is active)

The initial Overview should show a small useful summary, not every metric at once.

Each metric may expose `Show on map`.

Example:

`Internet use — 98% — 2024 — Show on map`

This creates natural feature discovery inside the information itself.

### Relationship inspector

Starts with plain-language facts and relation types before advanced Axis interpretation.

The current D1–D11 strip remains available inside the Axis section.

## 12. Compare

Compare is contextual rather than a permanent header button.

Flow:

1. Select Denmark.
2. Choose `Compare`.
3. Prompt: `Compare Denmark with…`
4. Click Germany.
5. Comparison inspector appears.
6. `+ Add country` allows up to the existing four-country maximum.

The D4 comparison vector remains the data source.

Comparison should group measurements by human domain rather than implementation module.

## 13. Search

Search stays available as a compact utility shortcut.

It is not the primary navigation model.

Search may eventually discover:

- countries / cities / entities
- datasets / surfaces
- networks
- relation families
- project lenses

But every search result must also have a browsable home in World, Relations, Time, or Axis.

If a capability can only be discovered by search, the navigation design is incomplete.

## 14. Advanced settings

A small settings / display control contains implementation-level choices normal users should not need.

Candidate contents:

- 3D / color / both
- basemap
- globe / planar projection
- tilt
- label density
- map focus mode
- explicit hop limit
- module orbit / semantic interior hubs
- debug / diagnostics

The existing `Height`, `Trace depth`, `Focus mode`, `Toggle tilt`, `Toggle globe`, and `Load OSM basemap` concepts move here where appropriate.

## 15. Unified capability registry

The redesign requires a UI-facing registry so lazy modules stop injecting ad hoc controls into arbitrary menus.

Each capability registers a semantic descriptor:

```js
{
  id,
  name,
  zone,                 // world | relations | time | axis | settings
  category,
  subcategory,
  kind,                 // surface | overlay | relation | place | lens | action
  colorFamily,
  description,
  availability,
  active,
  activate(context),
  deactivate(context),
  getState(),
  lazyModule,
  epistemicLayer,
  timeSupport
}
```

This registry is the main long-term integration point.

A future feature should not manually append a control to `#layersMenu` or `#viewMenu`. It registers once and the semantic UI decides where it appears.

## 16. State model

The UI should expose a small composable state model:

```text
selection
baseSurface
worldOverlays[]
relationModes[]
timeState
axisLens
axisDimension
visualSettings
```

Rules:

- activating a new base surface replaces the prior base surface
- overlays may coexist when visually compatible
- relation modes may coexist only when the renderer can distinguish them
- time state filters/suppresses incompatible undated/current-only surfaces
- Axis state never overwrites empirical values
- removable chips mirror active semantic state
- URL state remains bookmarkable

## 17. Lazy loading

The existing core-first bootstrap remains a design constraint.

Semantic handles should load modules only when needed:

- open World → promote World registry providers
- open Relations → promote relation/network providers
- activate Time → promote time module
- activate Axis → promote Axis modules
- select country → promote country inspector enrichments

The new registry should preserve the existing loader diagnostics and deduplication rather than bypassing `window.__potatoAtlasLoadModule`.

## 18. Migration from existing controls

Existing capability → new home:

- `Layers` → removed; capabilities redistributed into World / Relations / Axis
- `Trace` → Relations + `Expand`
- `Compare` → country contextual action
- `Inspect` → automatic contextual inspector
- `Time` → bottom contextual Time rail
- `View` → semantic surfaces plus advanced visual settings
- `Height` → hidden rendering method; user selects meaning
- `relationType` → Relations family/subcategory
- `traceDepth` → Expand interaction; advanced hop limit in settings
- `axisFieldView` → Axis / project field lens
- `empiricalNetworkView` → Relations / institutions & alliances
- `religionFacetView` → World / faith & culture
- `capitals` → World / places
- `interior` module orbit → Advanced settings
- `Focus mode` → Advanced visual settings
- `basemap` → Advanced visual settings
- D1–D11 navigator → Axis vertical spine, only when active

Compatibility IDs may remain temporarily so existing modules continue to function during migration. They should not remain the long-term UI API.

## 19. Roadmap alignment

This architecture intentionally anticipates likely future datasets.

### Future World additions

- cities
- ports
- airports
- rail hubs
- pipelines
- power plants
- submarine cables
- companies
- banks
- universities
- churches / mosques / temples / sacred sites
- military bases where appropriate and publicly sourced
- satellites / digital infrastructure where appropriate

### Future Relations additions

- bilateral trade
- bilateral investment
- debt / creditor exposure
- supply chains
- energy flows
- migration origin → destination
- ownership chains
- procurement / funding
- research collaboration
- patent / technology transfer
- arms transfers
- treaty relations
- transport routes
- Internet / AS connectivity

### Future Time additions

- historical borders
- treaty accession / withdrawal
- debt maturity
- policy thresholds
- wars / conflicts
- elections where relevant
- economic cycles
- religious composition change
- demographic transitions

### Future Axis additions

- dependency
- resilience
- counterfactual removal
- relay / bottleneck analysis
- threshold operators
- recurrence / spiral history
- Tree / generativity
- Rooms / higher-order composition
- Mountain / system integration
- D11 objective comparison

The purpose of the architecture is that none of these additions should require new top-level navigation categories.

## 20. Error handling and conflicting states

- If a module fails to load, the semantic item remains visible but reports `Unavailable` rather than disappearing silently.
- If a current-only layer conflicts with historical mode, keep its menu item visible but disabled with a clear reason.
- If two surfaces cannot coexist, activating the new one replaces the old one and updates chips.
- If a relation mode requires missing data, show the conceptual option only when the module can explain why it is unavailable; otherwise omit it until meaningful.
- Unknown data remains unknown, never zero.
- Project-symbolic lenses remain labeled as project interpretation.

## 21. Accessibility and input

- All controls must be keyboard reachable.
- Radial controls must have a linear DOM order matching visual order.
- Every color family also has a text/icon identity.
- Minimum touch targets should remain usable on mobile.
- Drawers must not trap focus unexpectedly.
- Escape closes the active drawer/wheel before clearing map selection.
- Screen-reader labels should use human-facing names, not internal IDs.

## 22. Responsive behavior

Desktop:

- World left drawer
- Relations right drawer
- Axis top vertical/curved navigator
- Time bottom rail
- contextual selection wheel/dock near bottom center
- contextual inspector floats on the right only when needed

Mobile / narrow screens:

- semantic handles remain at edges
- drawers become bottom/side sheets
- context wheel becomes bottom action sheet
- Time becomes a compact bottom rail above the action sheet
- inspector becomes a swipeable bottom sheet
- only one large sheet is open at once

## 23. Implementation boundaries

This redesign should primarily change UI orchestration, not rewrite proven data/rendering modules.

Preserve:

- MapLibre geographic core
- current data contracts
- country D4 observable runtime
- demography/religion runtime
- empirical network runtime
- curated relationship renderer
- relationship inspector logic
- time contracts
- Axis contracts
- bootstrap lazy-loader / diagnostics
- URL state where possible

Refactor/adapt:

- `3d.html`
- `3d-ui.js`
- `3d-selection-ui.js`
- control injection in Fields / Networks / Demography Facets / Metric Dimensions / Axis modules
- state summaries / chips
- inspector navigation shell

Add:

- semantic capability registry
- spatial zone UI controller
- active-state chip controller
- contextual Time rail
- contextual selection action model

## 24. Validation strategy

### Static validation

- no orphaned existing feature after migration
- every registered capability has a semantic zone/category
- no duplicate active control for the same capability
- no normal-path controls expose removed implementation vocabulary (`Height`, `Trace depth`, generic `Layers`) unless inside advanced settings
- Pages build parity for new UI modules

### Runtime validation

Smoke paths:

1. World → Economy → GDP
2. World → Faith & culture → Christian share
3. Relations → Institutions → NATO
4. select Denmark → Relations → expand once
5. select Denmark → Compare → Germany
6. select country → Overview → Show on map for one D4 metric
7. Time with a D4 metric
8. Axis → D6 Spiral
9. Axis → project North field
10. clear each active chip and verify state disappears
11. bookmark/reload representative states
12. mobile narrow-layout interaction

### Performance validation

- core map remains interactive before optional semantic modules load
- opening one zone does not eagerly load unrelated zones
- failed optional module does not block other zones
- no duplicate module imports caused by multiple navigation paths

## 25. Success criteria

The redesign succeeds when:

1. A user can reach GDP, NATO, religion composition, country relations, historical state, and Axis D6 without knowing any implementation terminology.
2. The user can always tell why the map looks different by reading active chips.
3. Selecting a country reveals its likely actions without requiring a global-menu search.
4. New features can be added through the registry without inventing another top-level button.
5. The default map is visually calmer than the current UI while exposing more capability contextually.
6. The Atlas can grow substantially without another navigation redesign.

## 26. Non-goals

This redesign does not:

- merge empirical and project-symbolic truth layers
- turn Axis height into a country score
- redesign the canonical data model
- replace MapLibre
- remove search entirely
- force all future data to use the same visual encoding
- expose every advanced control by default

## 27. Final interaction law

The enduring rule is:

> **Thing → World · Connection → Relations · Change → Time · Interpretation → Axis · Action → Selection context**

If a future feature does not fit that rule cleanly, first ask whether it is actually a rendering/debug option that belongs in Advanced Settings, or whether the feature itself has been modeled ambiguously.
