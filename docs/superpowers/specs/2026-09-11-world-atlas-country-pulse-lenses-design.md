# World Relational Atlas — Country Pulse, Multi-Selection, Lenses and Flows

Date: 2026-09-11
Status: approved design direction, implementation spec pending user review
Starting repository snapshot: `69a4f59262b24ca3ed1cf36effa6dc32b8538846`
Primary surface: `world-map/3d.html`
Related prior spec: `docs/superpowers/specs/2026-09-11-world-atlas-utility-design.md`

## 1. Purpose

Make the World Relational Atlas immediately informative and relational when a user clicks the map.

The core experience should no longer require users to discover a special Compare mode, enable relationship lines, enable interior modules, choose a trace depth, and combine several controls before the map becomes useful.

The map itself becomes the primary interface:

- click a country to select it;
- click additional countries to add them to the working selection;
- click a selected country again to deselect it;
- the most recently selected country is the active country shown in the Country Pulse panel;
- selected countries automatically reveal a restrained, relevance-ranked set of useful relationships;
- one active color lens controls what country fill colors mean;
- connection overlays independently control what kinds of edges/nodes are visible;
- clicking a capital opens a compact national/capital action window;
- clicking an edge, institution, project, city, or facility explains that object or relationship.

The desired feeling is that the user can see a country as a living system: money, trade, debt, energy, institutions, projects, people, religion, alliances, infrastructure, risks and dependencies become visible without turning the interface into a dashboard maze.

## 2. Governing interaction grammar

The interface should be learnable from five rules:

1. **Click country → understand and select the country.**
2. **Click selected country again → remove it from the working set.**
3. **Click capital → understand the machinery of the state / national hub.**
4. **Click connection → understand the relationship.**
5. **Choose Lens → change what country colors mean globally.**

Everything deeper—Trace, Time, Eye/evidence, graph traversal, source inspection, project Axis detail—supports these rules rather than replacing them.

## 3. Selection model

### 3.1 Working selection set

Replace the current mental model of one ordinary selected country plus a separate capped Compare mode with a unified working selection set.

Properties:

- any country polygon click toggles membership;
- no modifier keys are required;
- selection remains visible until toggled off, cleared, or state is reset;
- no arbitrary four-country cap at the core selection layer;
- the implementation may introduce a display-safety limit for simultaneous expanded networks, but selection itself remains conceptually uncapped;
- a compact selection strip shows selected countries and allows direct removal/activation;
- `Clear` removes the whole working set.

### 3.2 Active country

The most recently added or explicitly activated selected country becomes `activeCountry`.

The active country:

- drives the Country Pulse panel;
- gets the strongest outline/emphasis;
- may receive a slightly larger connection budget;
- determines the capital action window context;
- does not erase or hide other selected countries.

If the active country is deselected, the next-most-recent selected country becomes active. If no countries remain, the inspector returns to world mode.

### 3.3 Visual states

At minimum distinguish:

- unselected country;
- selected country;
- active selected country;
- country highlighted by active Lens;
- hovered country.

Lens color and selection state must remain distinguishable. Selection should use outline/emphasis/state treatment rather than replacing the Lens fill color whenever possible.

## 4. Country Pulse

Country Pulse is the default country inspector shown automatically when a country becomes active.

It should be useful in the first screenful without opening modules.

### 4.1 Headline metrics

Prefer a compact top row/grid of high-value sourced metrics:

- population;
- GDP;
- GDP per capita;
- real GDP growth;
- inflation;
- unemployment;
- government debt / GDP when available.

Each displayed metric must preserve value, unit, period and source metadata. Missing values show an honest unavailable state rather than disappearing silently or becoming zero.

### 4.2 Core sections

Country Pulse should progressively expose:

#### Economy / Money
- GDP and GDP/person;
- growth;
- inflation;
- unemployment / labour participation;
- imports / exports / trade balance when available;
- public debt / debt-to-GDP;
- major funding, procurement, investment or banking relationships when available.

#### People
- population;
- density;
- life expectancy;
- fertility;
- urbanization;
- labour/employment;
- migration when available;
- language context;
- religion / unaffiliated composition.

#### Connections
- the strongest visible relationships currently rendered for the active country;
- each row is clickable and maps to a visible edge/node where practical;
- relationship type, direction, amount/scale when known, date/period and source should be available.

#### Projects
- major sourced infrastructure, energy, industrial, research, defence/procurement or public programmes;
- spatial projects may be plotted when coordinates are honest;
- nonspatial programmes remain inspector/graph objects.

#### Systems
- energy;
- infrastructure;
- transport/logistics;
- ports/airports/grids/cables/pipelines/power assets as data becomes available;
- strategic dependencies and capabilities.

#### Institutions
- capital;
- central bank;
- parliament/government;
- finance ministry or debt-management institution where available;
- major regulators;
- major banks / exchanges where relevant;
- public intelligence/security organizations where public institutional location data is appropriate.

#### Network position
- what the country depends on;
- who depends on it;
- major institutional memberships;
- major capability chains;
- strongest inbound/outbound relations.

#### Data quality
- coverage/freshness summary;
- last update/observation where meaningful;
- important missing fields;
- source/evidence access through Eye.

### 4.3 More Statistics

Country Pulse exposes a single obvious `More statistics` action opening a larger stats drawer/sheet.

The full stats surface can group metrics into:

- Economy;
- Labour;
- Public finance;
- Trade;
- People / Demography;
- Religion;
- Health;
- Education;
- Energy;
- Environment;
- Digital / Technology;
- Infrastructure;
- Government / Institutions;
- Archive coverage / freshness.

The drawer should use the same canonical/runtime metric registry as map coloring and Compare-like views.

## 5. Automatic connection network

Selecting a country should automatically reveal a useful network. The user must not need to enable `Relations` first.

### 5.1 Default connection budget

At normal world/regional views, show approximately 4–8 high-value connections per selected country, with a slightly larger allowance for the active country.

The exact count is adaptive rather than fixed. The goal is readability, not maximal edge count.

### 5.2 Ranking

Candidate relationships should receive a display/relevance score based on available metadata such as:

`display_score = importance × evidence_quality × freshness × magnitude_signal × contextual_relevance × diversity_weight`

The implementation does not need a single universal mathematical truth score. It needs a deterministic display-priority model.

Suggested factors:

- direct sourced observation > weak inference;
- recent/current relationship > stale relationship where recency matters;
- quantified important flow > tiny or unquantified relation when the active overlay is a flow domain;
- relationship involving a selected country > unrelated background relation;
- diversity bonus prevents one category from consuming every visible slot;
- screen-space penalty reduces overlapping/spaghetti edges.

### 5.3 Diversity rule

Default auto-network should avoid showing six nearly identical trade edges while suppressing debt, energy, projects or institutional relationships.

A practical category budget may reserve or prefer representation across:

- trade / money;
- energy / infrastructure;
- institutions / alliances;
- projects / investment;
- ownership / finance;
- other strategically important relations.

### 5.4 Zoom-aware density

At world zoom:
- strongest country-country and major institutional relationships only.

At regional zoom:
- more trade, energy, infrastructure and alliance detail.

At country zoom:
- capital, cities, institutions, banks, ports, projects and major assets become useful.

At local zoom:
- facilities/buildings dominate; abstract semantic hubs recede.

## 6. Color Lens system

Country fill colors have exactly one primary semantic owner at a time: the active **Lens**.

This avoids mixing multiple incompatible meanings into one fill color.

Top-level Lens choices:

- Neutral / default;
- Metric;
- Alignment / Axis;
- Alliances / institutions;
- Religion;
- Issues / Risk;
- later Archive/Data health.

Selection outlines remain independent of Lens fill.

## 7. Metric Lens

The Metric Lens uses the normalized country metric registry from the utility design.

Initial metrics should include as data permits:

- population;
- population density;
- GDP;
- GDP per capita;
- GDP per capita PPP;
- real GDP growth;
- inflation;
- unemployment;
- labour-force participation;
- life expectancy;
- fertility;
- urbanization;
- poverty;
- CO2 per capita;
- internet penetration;
- government debt / GDP;
- public debt;
- imports;
- exports;
- trade balance;
- energy import dependence;
- later infrastructure/capability measures.

Metric Lens behavior:

- choropleth with explicit legend;
- selected metric promoted in Country Pulse;
- value/unit/period/source visible in inspector;
- missing values render as neutral/unknown;
- selected metric may optionally drive extrusion when mathematically/display appropriate.

## 8. Alignment / Axis Lens

The project North/West/East/South model should be easy to see, but it must remain epistemically separate from empirical alliances.

### 8.1 Modes

Possible Lens submodes:

- Direction / Axis overview;
- North strength / membership class;
- West project alignment;
- East project reference;
- South / exploratory classification;
- overlap / mixed;
- unclassified.

### 8.2 Semantics

Country styling may use a stable family such as:

- North: cool/cyan family;
- West: warm/gold family;
- East: red/orange family;
- South: green family;
- overlap/mixed: distinct blended or patterned treatment;
- unclassified: neutral gray.

Exact colors are visual-design details, but the legend must identify that this is a **project interpretive Lens** unless a specific displayed relation is empirical.

The Lens must not imply sovereignty, annexation, consent, legal bloc membership or objective geopolitical alignment.

### 8.3 Country Pulse integration

When Alignment Lens is active, Country Pulse promotes:

- current project Axis classification;
- version/date;
- rationale/role text;
- empirical alliances that support, complicate or contradict the project reading;
- source/provenance distinction between project interpretation and observed memberships.

## 9. Alliance / Institution Lens

Empirical memberships are kept separate from Axis interpretation.

Initial supported sets may include where canonical/current data exists:

- EU;
- NATO;
- Euro Area;
- Schengen;
- BRICS;
- AUKUS;
- Five Eyes;
- G7;
- G20;
- OECD;
- Nordic / Arctic institutional sets where definitions are explicit;
- later other treaty/organization memberships.

Default interaction:

- choose one alliance/institution;
- members are strongly colored;
- partner/candidate/observer states use clearly different states when supported;
- non-members recede rather than receiving arbitrary competing colors.

A future `Alliance families` overview may combine multiple groups, but the first implementation should favor one chosen set at a time for clarity.

## 10. Religion Lens

Religion is a descriptive demographic Lens, not a geopolitical alignment inference.

### 10.1 Dominant-category view

Countries can be colored by the largest available religious/identity category:

- Christian;
- Muslim;
- Hindu;
- Buddhist;
- Jewish;
- Other religions;
- Religiously unaffiliated.

The legend must state that dominant category does not imply unanimity, political loyalty, behavior or belief intensity.

### 10.2 Selected-category heatmap

The most useful religious Lens is a selected-category gradient.

Choose one:

- Christian share;
- Muslim share;
- Hindu share;
- Buddhist share;
- Jewish share;
- Other religions share;
- Unaffiliated share;
- religious diversity when a defensible measure exists.

The map becomes a percentage choropleth for that category.

### 10.3 Composition detail

Selected countries and capital/country action surfaces may show full composition using the existing sourced bars.

At higher zoom or on selected capitals, a compact stacked composition marker may be considered later, but global world view should not be covered in pies/rings.

## 11. Issues / Risk Lens

This Lens exists to help answer “what pressures or problems are visible?” without turning countries into moral scores.

Candidate metric-based views:

- inflation stress;
- unemployment;
- debt burden;
- energy dependence;
- conflict/security stress where sourced;
- infrastructure pressure;
- climate/environment risk where sourced;
- governance/corruption indicators where methodologically suitable;
- archive/data gaps.

Rules:

- show the underlying indicator and source;
- avoid one universal `bad country` score;
- pair issue states with relevant mechanisms, projects or repair/capacity questions where the project does so explicitly.

## 12. Connection Overlay system

Connection overlays are independent of Lens color.

Top-level choices:

- Auto / major connections;
- Money / funding;
- Trade;
- Debt / finance;
- Energy;
- Infrastructure;
- Projects;
- Institutions;
- Alliances;
- Ownership / control;
- Security;
- None.

The default should be `Auto / major connections` when countries are selected.

Only a small number of overlays should be simultaneously active. The first implementation should prefer one explicit overlay plus the automatic selected-country context.

## 13. Flow and edge semantics

### 13.1 Directional quantitative flows

Use directional arrows only where direction is meaningful and sourced.

Examples:

- imports/exports;
- investment/funding;
- debt/creditor exposure where data supports the relationship;
- grants/procurement flows;
- electricity/energy physical flows;
- ownership/control direction;
- supplier/customer flows when evidence supports it.

### 13.2 Red / green rule

For the selected-country perspective:

- **green inward** = documented inflow toward the selected/active country;
- **red outward** = documented outflow away from the selected/active country.

The legend must explicitly state that red/green indicates **direction**, not moral quality, success/failure, profit/loss or good/bad.

When the active relation is not naturally an inflow/outflow, use a neutral category color instead.

### 13.3 Thickness and motion

When values are comparable:

- line thickness may encode magnitude;
- restrained animation may encode flow direction;
- animation speed should remain subtle and should not be overloaded as another exact quantitative channel unless explicitly defined;
- users with reduced-motion preference receive a static directional representation.

### 13.4 Evidence states

Possible edge treatment:

- solid = direct/high-confidence sourced relation;
- dashed/dotted = inferred, estimated, incomplete or non-quantified relation;
- confidence/source status is inspectable rather than guessed visually.

Exact line styling should be validated for readability and not imply epistemic precision beyond the source model.

## 14. Capital Action Window

The capital remains a special national interaction anchor, but the default design is a compact floating/bottom action window rather than an always-visible radial wheel.

Clicking the capital should:

- keep/select its country;
- make that country active;
- focus the capital appropriately;
- open a context window with approximately six high-level routes.

Suggested routes:

- Stats;
- People;
- Money;
- Projects;
- Systems;
- Institutions.

Desktop: compact anchored popover/window near the capital when practical.

Mobile: bottom sheet or inspector section; do not rely on a tiny radial target.

### 14.1 Capital / Institutions route

Should progressively reveal real national machinery where sourced:

- parliament;
- head-of-government / executive office;
- central bank;
- finance ministry;
- debt-management office;
- regulators;
- major public financial institutions;
- major banks/exchanges;
- intelligence/security headquarters only when public institutional location data is appropriate.

The existing capital dataset is an orientation anchor, not yet the full institutional graph.

## 15. Real physical nodes and the “living system” effect

The Atlas should increasingly prefer real geocoded objects over abstract decorative semantic dots.

Priority physical node families:

- major cities;
- capitals;
- central banks;
- parliaments/government buildings;
- finance ministries / regulators;
- major banks and exchanges;
- ports;
- airports;
- power plants;
- wind/solar/nuclear facilities;
- grids/interconnectors;
- pipelines;
- subsea cables/landing stations;
- large industrial facilities;
- research institutions;
- major companies/headquarters;
- public intelligence/security institutions where public location data is suitable;
- major sourced projects/facilities.

Visual life should come from meaningful encoding rather than decoration:

- a port emits/receives trade flows;
- a central bank participates in monetary/financial relationships;
- a power plant connects to energy systems;
- a project pulses or carries status only when that state has meaning;
- a bank/company connects to ownership/funding/exposure edges.

Do not animate “smoke” or other effects unless they encode a real sourced quantity. The desired impression of a living system should emerge from actual flows, nodes and state.

## 16. Relationship with current semantic hubs

The current grouped semantic orbit (Society, State, Economy, Systems, Context, Project) remains useful as inspector navigation but should no longer dominate the map after country selection.

Default selected-country map view should prioritize:

1. real country-country edges;
2. real institutions/facilities/projects;
3. major quantitative flows;
4. only then abstract semantic navigation handles when useful.

Detailed semantic modules remain accessible through Country Pulse / deeper inspector routes.

## 17. Relationship with Compare

The current explicit Compare mode should not remain the primary mechanism for multi-country exploration.

Transition strategy:

- first introduce unified multi-country selection;
- preserve old Compare internals temporarily where required for regression safety;
- migrate side-by-side statistical comparison into a view generated from the working selection set;
- remove or demote the separate Compare mode once equivalent behavior is verified.

When multiple countries are selected, a `Compare selected` action may present a table using the same metric registry, but it is optional. Selection itself is not a compare mode.

## 18. Search

Unified country/city search from the utility spec remains valid.

Search selection should obey the same interaction rules as map clicks:

- selecting a country adds/activates it rather than secretly entering another mode;
- selecting a city focuses the city and exposes its country context;
- selecting a capital may open the Capital Action Window;
- URL state remains reproducible.

## 19. Data architecture

### 19.1 Metric runtime

Use/generated from canonical country observations:

`data/world-country-metrics.json`

This remains the shared source for:

- Country Pulse headline stats;
- full stats drawer;
- Metric Lens;
- metric-aware selected-country comparison;
- hover/legend values;
- optional extrusion.

### 19.2 Selection / pulse runtime

A generated or runtime-composed `Country Pulse` projection should combine canonical sources without becoming a second owner of truth.

Conceptual shape:

```json
{
  "country": "DNK",
  "headline_metrics": ["population", "gdp", "gdp_per_capita", "growth", "inflation", "unemployment", "debt_gdp"],
  "candidate_connections": [
    {
      "from": "DNK",
      "to": "DEU",
      "type": "trade",
      "direction": "outbound",
      "value": null,
      "unit": null,
      "period": null,
      "source": null,
      "confidence": "unknown",
      "spatial_class": "country-country",
      "display_score": null
    }
  ]
}
```

`display_score` is a runtime/display field, not a canonical truth claim.

### 19.3 Entity runtime

Physical/institutional expansion should converge toward a reusable entity schema with:

- canonical id;
- name;
- type/subtype;
- country;
- coordinates and precision;
- spatial confidence/provenance;
- validity period;
- owner/source dataset;
- relationships;
- display importance.

Do not create parallel entity identities when a canonical project ID already exists.

## 20. State and URL

New state concepts:

- `selected=<ISO3,ISO3,...>` or equivalent stable encoding;
- `active=<ISO3>` when useful;
- `lens=<lens-id>`;
- Lens submode/metric/religion/alliance as stable ids;
- `overlay=<overlay-id>`;
- existing Time/Evidence state remains independent.

Legacy `country=` and `compare=` parameters should be migrated carefully with backward-compatible parsing during transition.

Unknown ids fail safely to default/neutral states.

## 21. UI shell

Persistent top-level map controls should remain sparse.

Recommended ordinary controls:

- Search;
- Lens;
- Connections;
- selected-country strip / Clear;
- existing compact Tools for advanced functions.

Country Pulse remains the main contextual inspector.

Advanced tools such as Time, Eye, detailed Trace, Path, Axis specialist operations and future graph scenes remain under progressive disclosure.

Do not add separate persistent buttons for every dataset.

## 22. Mobile

Mobile interaction should preserve the same grammar:

- tap polygon to add/remove;
- active country appears in bottom inspector;
- selected-country chips scroll/wrap compactly;
- Lens and Connections are simple selectors/sheets;
- capital action routes appear as a bottom sheet, not a precision radial menu;
- no feature depends on hover.

## 23. Accessibility

- all Lens/overlay meanings have text legends;
- color is never the sole carrier of selected state;
- religion/metric values remain numerically inspectable;
- red/green flow direction also uses arrowheads and text so color-vision deficiencies do not destroy meaning;
- keyboard-accessible country/search selection remains possible;
- reduced-motion preference disables or minimizes flow animation;
- selection strip controls use real buttons and visible focus states.

## 24. Error handling

- map core must boot if metrics fail;
- map core must boot if entity/place snapshots fail;
- unavailable Lens data shows a neutral/no-data state rather than breaking selection;
- connection ranking must tolerate missing amount/date/confidence fields;
- an unavailable overlay must not erase the working selection;
- failed optional data modules surface a concise nonfatal message in the relevant panel.

## 25. Implementation slices

The work is intentionally staged so the map improves visibly after each slice.

### Slice A — Unified multi-country selection

- replace default single-selection toggle behavior with working selection set;
- active-country concept;
- selection strip;
- click again to deselect;
- preserve old Compare temporarily behind compatibility boundary;
- URL migration/backward parsing;
- tests.

### Slice B — Country Pulse headline stats

- consume normalized metric runtime;
- replace module-count-first panel with useful headline metrics;
- promote religion composition and key demographic/economic sections;
- More Statistics drawer;
- tests for missing values/source metadata.

### Slice C — Automatic network

- selected country automatically renders top relevant relations;
- remove requirement to manually toggle relations for ordinary use;
- deterministic ranking/diversity/clutter cap;
- active-country connection list synchronized with visible edges;
- tests for bounded edge counts and deterministic ranking.

### Slice D — Lens framework

- one country-fill Lens owner;
- Neutral;
- Metric;
- Alignment/Axis;
- Alliances;
- Religion;
- legend contract;
- selection styling independent from fill;
- URL persistence.

### Slice E — Religion and alliance polish

- dominant religion;
- selected religion gradient;
- alliance membership highlighting;
- Country Pulse context adaptation;
- epistemic labels.

### Slice F — Connection overlays and directional flows

- Auto;
- Trade;
- Money/Funding;
- Debt/Finance;
- Energy;
- Infrastructure;
- Projects;
- Institutions;
- Ownership;
- Security;
- arrows, direction, magnitude and evidence styling where supported;
- no fake flow values.

### Slice G — Capital Action Window

- capital click keeps/activates country;
- Stats / People / Money / Projects / Systems / Institutions routes;
- desktop anchored popover + mobile bottom-sheet behavior;
- no mandatory radial wheel.

### Slice H — Real entity/facility expansion

- central banks;
- government institutions;
- major banks/exchanges;
- ports/airports;
- energy assets;
- major projects;
- companies/research institutions;
- public security/intelligence institutions where public location data is appropriate;
- entity-aware Trace integration.

## 26. Validation / regression requirements

At minimum verify:

1. neutral world map boots with no selected countries;
2. clicking one country selects and activates it;
3. clicking a second country keeps the first selected and activates the second;
4. clicking a selected country removes it;
5. active country falls back deterministically after removal;
6. selection state survives Lens changes;
7. Lens fill does not erase selected/active visibility;
8. default country selection automatically shows a bounded useful network;
9. connection count remains bounded with many selected countries;
10. edge ranking is deterministic for identical data/state;
11. Country Pulse shows GDP/inflation/unemployment/etc. when available and honest missing states otherwise;
12. religion composition is visible without opening a hidden semantic module;
13. Metric Lens values display period/source metadata;
14. Alignment Lens is visibly labeled project-interpretive;
15. Alliance Lens uses empirical membership data independently of Alignment;
16. selected-religion heatmap uses percentage values and a legend;
17. red/green directional flows also use arrows/text semantics;
18. reduced-motion mode remains understandable;
19. capital click opens action context and does not accidentally deselect the country;
20. old `country=`/`compare=` URLs migrate safely during transition;
21. optional metric/entity failures leave the core map usable;
22. mobile supports all primary tap interactions.

## 27. Success criteria

The redesign succeeds when a new user can do the following without instructions:

- click several countries and see them remain selected;
- click one again and remove it;
- learn useful facts about the active country immediately;
- see interesting relationships appear automatically;
- switch the entire map between inflation, unemployment, religion, alliances and project alignment using one obvious Lens control;
- understand what visible colors mean from the legend;
- click a capital and reach national institutions/stats/projects without learning a specialist control scheme;
- click a connection and understand its type/direction/value/date/source where available;
- obtain a much richer sense of how a country functions without turning on seven different hidden controls.

## 28. Non-goals for the first implementation cycle

- no attempt to ingest every bank, city, project, facility or bond globally at once;
- no fake coordinates for abstract concepts;
- no universal moral ranking of countries;
- no inference of political loyalty from religion;
- no conversion of project Axis categories into empirical alliance claims;
- no fabricated trade/debt/financial amounts;
- no highly animated decorative effects that do not encode data;
- no full removal of old Compare/Trace internals until the replacement behavior is verified;
- no second map renderer.

## 29. Canonical product principle

The Atlas should be **quiet until the user asks a question, then immediately informative**.

Country selection is the primary question.

Lens changes the meaning of country color.

Connections reveal relationships.

Country Pulse explains the active country.

Capital click exposes national machinery.

Time and Eye explain when and how well we know it.

The complexity belongs in the data model and ranking logic, not in the number of controls the user must discover.
