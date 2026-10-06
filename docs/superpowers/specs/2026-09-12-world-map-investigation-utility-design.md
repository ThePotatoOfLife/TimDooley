# World Map Investigation Utility Design

Date: 2026-09-12
Status: approved direction, design for review before implementation planning

## 1. Goal

Turn the existing World Map from a collection of capable but partly disconnected analytical modules into a coherent investigation tool without reintroducing a large permanent toolbox.

The immediate objective is not to add more visible controls. It is to make already-built capabilities reachable, give them a shared interaction grammar, and deepen them with better canonical data.

This tranche has four linked outcomes:

1. make the existing shortest-path capability genuinely usable from the current compact World Map interface;
2. unify Path, Trace/Connections, Functional Chains, Gateways and Dependency Impact as contextual investigation actions rather than unrelated features;
3. build the previously designed coverage ledger so enrichment work is driven by actual represented evidence and missingness rather than stale counters or intuition;
4. establish the first canonical infrastructure substrate and feed those infrastructure objects into the existing Chain, Gateway and Impact systems where explicit evidence supports the relationship.

The map remains visually compact. New capability should appear primarily in the selected-country card, contextual strips, temporary result panels and clicked physical assets.

---

## 2. Existing capabilities that are already real

This design starts from the current implementation rather than treating old plans as undone work.

Already implemented on current `main`:

- canonical `/world-map/` application;
- North/West/East/South fields;
- institutional groups and scalar Stats layers;
- multi-country selection and comparison;
- selected-country connection previews with relation filtering;
- entity trace / connection exploration;
- system-role context for capabilities, dependencies, builds and gateways;
- empirical gateway/chokepoint points;
- functional-chain explorer with URL persistence and dedicated outline state;
- dependency Impact runtime and two-hop directional tracing;
- shared scalar runtime for population/area and first-class map entities;
- flat/globe projection;
- first-class non-canonical map entities such as Greenland, Antarctica and Kosovo.

The next tranche must reuse these owners rather than duplicate them.

---

## 3. Architectural finding: capability is ahead of discoverability

Several modules exist but are no longer reachable through the current clean interface because they were originally mounted in legacy menus that the World Bar now hides.

The clearest example is Path:

- `world-map/3d-pathfinder.js` already computes shortest represented relationship paths;
- it supports relation-type filtering and URL state;
- it currently mounts its input/button into the old Trace menu;
- the current World Bar deliberately hides that menu.

Time has a similar problem, but Time is not included in this tranche because historical data coverage is not yet broad enough to make a general temporal map mode consistently useful.

The design principle is therefore:

> Promote strong dormant capabilities into contextual interaction, not back into a permanent toolbox.

---

## 4. Investigation grammar

The World Map should answer distinct questions through distinct but related tools.

### 4.1 Connections

Question:

> What does this selected entity connect to in the currently represented relationship graph?

Existing owners:

- selected-country connection preview;
- relation filters;
- entity Trace.

Semantics:

- broad relationship context;
- not necessarily causal;
- not necessarily directional;
- useful for exploring a neighborhood around one entity.

### 4.2 Path

Question:

> How are A and B connected through the currently represented relationship graph?

Semantics:

- shortest represented path under the active relation filter;
- ordinary curated relationships may participate;
- does not imply causality, importance or exclusivity;
- path failure means not represented in the dataset, not no real-world connection.

### 4.3 Impact

Question:

> Who or what explicitly depends on this represented object?

Semantics:

- explicit directional dependency evidence only;
- incoming dependency traversal;
- bounded to direct + second order in the current implementation;
- contextual chains remain separate from causal edges;
- no collapse/risk probability or synthetic score.

### 4.4 Functional chain

Question:

> What countries and systems participate in this represented capability/dependency chain?

Semantics:

- contextual system membership;
- membership is not causal dependency;
- chain context can inform Path or Impact but does not create Impact edges automatically.

### 4.5 Gateway / infrastructure object

Question:

> What real physical or operational node is associated with these countries/systems, and what explicit relationships are represented around it?

Semantics:

- empirical, sourced physical/system object;
- may participate in Chains, Path or Impact according to typed evidence;
- mere geographic adjacency does not imply dependency.

These tools share selection and evidence context, but they must never be collapsed into one ambiguous graph mode.

---

## 5. Path integration

### 5.1 Entry point

Do not restore the old Trace menu.

Add a compact contextual action in the selected-country card:

`Path to…`

Behavior:

1. user selects a country/entity;
2. `Path to…` reveals a compact destination control inside the existing card or a small adjacent contextual surface;
3. destination search uses the same canonical country/entity naming system already available to the map;
4. Enter/click computes the shortest represented relationship path under the current Relations filter;
5. result appears in a temporary investigation panel;
6. clicking a path step activates that entity without destroying the path result;
7. clear closes the path and removes URL state.

No permanent Path item is added to the World Bar.

### 5.2 Runtime/data ownership

Refactor `3d-pathfinder.js` so it does not depend on hidden legacy DOM controls such as `#traceMenu` or `#relationType`.

Preferred inputs:

- active entity from `window.__potatoAtlasSelection`;
- relation mode from the current selection/runtime API;
- canonical relationship graph from the current shared relationship owner;
- canonical country/entity names from the shared runtime where possible.

The module may continue to own shortest-path traversal, but graph loading and naming should use current canonical browser APIs instead of creating another parallel country-name fetch path.

### 5.3 Relation-filter behavior

Path should reuse the same broad relation modes already exposed in the World Bar:

- all;
- money;
- systems;
- institutions;
- project;
- other.

If the underlying relationship vocabulary is more granular, one central mapping from relation type -> relation mode should be reused by both connection preview and Path.

Do not create a second filtering vocabulary.

### 5.4 Result surface

The path result remains bounded and temporary.

Show:

- source;
- destination;
- hop count;
- path entities;
- relationship types per hop;
- active relation filter;
- epistemic boundary.

Boundary text should remain equivalent to:

> This is a shortest path in the represented graph under the active filter, not necessarily the shortest or strongest relationship in the real world.

---

## 6. Common investigation interaction rules

Path, Trace, Chain and Impact should feel related without being merged.

### 6.1 Contextual actions

Use the selected-country/entity card as the main investigation launch point.

Recommended compact action set:

- `Details`
- `Trace connections`
- `Path to…`
- `Impact`

Only show actions whose underlying runtime object exists.

Functional-chain tags remain directly clickable where they already appear.

Gateway/infrastructure popups may expose `Impact` and relevant chain actions contextually.

### 6.2 One temporary specialist surface at a time

Avoid overlapping right/bottom specialist panels.

Introduce a small shared investigation-surface coordinator or event contract so opening Path, Impact, entity Trace or Chain detail can close or demote conflicting temporary panels where necessary.

The coordinator should not own domain logic. It only manages temporary presentation state.

Possible interface:

```js
window.__potatoAtlasInvestigationSurface.open(id, { closeOthers:true })
window.__potatoAtlasInvestigationSurface.close(id)
window.__potatoAtlasInvestigationSurface.active()
```

This is optional if the same behavior can be achieved with a smaller event convention. Do not create a large framework merely for panel arbitration.

### 6.3 URL state

Keep current focused URL parameters:

- `path=...`
- `impact=...`
- `chain=...`

Do not create one giant encoded `investigation=` state object.

Stale/invalid parameters clear cleanly.

### 6.4 Map visual channels

Preserve channel ownership:

- scalar fill -> compositor;
- set/pattern -> compositor;
- selected entity -> selection outline;
- active functional chain -> chain outline;
- impact source/direct/second-order -> impact outline;
- Path -> route/step emphasis without taking over base fill;
- gateways/infrastructure -> point/line geometry according to type.

Do not make analytical tools overwrite one another's base color ownership.

---

## 7. Coverage ledger

### 7.1 Purpose

Create the already-designed generated World Map coverage ledger as an internal truth/maintenance object.

Canonical owners:

```text
scripts/build_world_map_coverage.py
data/world-map-coverage-ledger.json
```

The ledger is generated from canonical records and browser/runtime owners. It is not manually edited country-by-country.

### 7.2 Why it matters to map utility

The map already has sophisticated interfaces, but their usefulness varies because country evidence depth is uneven.

The ledger should answer:

- what does this entity actually have represented?
- which observations are fresh/stale/undated?
- how many sourced relationships exist?
- are there explicit capabilities/dependencies/builds?
- which chains/gateways/impact edges exist?
- which infrastructure domains are represented or missing?
- are duplicate/canonical ownership defects present?

This lets enrichment target holes that materially limit Path, Chain, Gateway and Impact usefulness.

### 7.3 No public score

Do not create:

- completeness percentage displayed as truth;
- geopolitical importance score;
- power score;
- resilience score;
- ranking leaderboard.

Represent dimensions independently.

Allowed states:

- represented;
- partial;
- missing;
- unknown;
- pending-source;
- not-applicable.

### 7.4 Minimum first-version dimensions

For every canonical country and registered map entity where relevant:

- identity/canonical ownership;
- comparable observations;
- observation freshness;
- source/provenance count;
- relationships;
- institutions/groups;
- capabilities;
- dependencies;
- builds/projects;
- functional chains;
- gateways;
- impact graph participation;
- strategic geography;
- ports/logistics;
- energy/resources/grid;
- trade/value chains;
- digital/technology infrastructure;
- infrastructure references.

### 7.5 Operational priority reasons

A maintenance-only sorter may produce ordered reasons such as:

1. integrity defect;
2. gateway/infrastructure hinge with sparse data;
3. multi-chain connector with missing dependencies;
4. Impact node with unresolved concepts;
5. infrastructure domain gap;
6. general descriptive gap.

The output must explain the reason and never masquerade as a geopolitical value ranking.

### 7.6 Public use

Do not add a Coverage menu.

A later quiet card hint may say something equivalent to:

- `Evidence: rich` / `Evidence: limited`
- `Dependencies represented: 4`
- `Infrastructure: partial`

but only if that proves useful and can be expressed without implying completeness of reality.

This tranche should prioritize internal enrichment utility over public coverage decoration.

---

## 8. Infrastructure registry foundation

### 8.1 Purpose

Introduce a canonical empirical infrastructure owner so the map can represent physical and operational nodes rather than forcing infrastructure into duplicated free-text country fields.

Canonical owner:

```text
data/world-map-infrastructure.json
```

This owner does not replace `data/world-map-gateways.json` in the first tranche. Gateways remain the chokepoint/gateway authority while infrastructure records reference them where appropriate.

### 8.2 Initial type vocabulary

First supported types:

- `port`
- `maritime-terminal`
- `strait-associated-terminal`
- `canal-associated-terminal`
- `grid-interconnector`
- `pipeline`
- `lng-terminal`
- `subsea-cable-system`
- `cable-landing`
- `rail-junction`
- `freight-corridor`

The schema should remain forward-compatible with:

- internet exchange;
- refinery/storage interface;
- border/customs node;
- air cargo hub;
- payment interface;
- data gateway;
- industrial/mineral corridor.

### 8.3 Record contract

Each record must have:

```text
id
label
type
countries/entities
location or explicit no-geometry status
systems/chains
gateway_ids when applicable
operator/authority when known
status/observation when applicable
observation period/date when applicable
source
source_url
evidence_class
description
```

Optional typed relationship fields may describe:

- `depends-on`;
- `uses-gateway`;
- `serves`;
- `connects`;
- `alternative-route`;
- `member-of-chain`.

Only explicitly causal relationship types may feed Impact.

### 8.4 First infrastructure wave

Keep the first wave intentionally small and high-leverage.

Seed infrastructure around gateway systems already represented by the map:

#### Turkish Straits

- major Bosporus/Dardanelles associated port/terminal nodes where sourced;
- Turkish Straits gateway linkage;
- Black Sea / Mediterranean / European corridor systems.

#### Suez / Red Sea

- Port Said / Suez / Red Sea terminal context where sourced;
- Suez gateway linkage;
- Egypt and relevant system-chain context.

#### Malacca

- Singapore/Malaysia/Indonesia gateway-adjacent major ports where the evidence is straightforward and current;
- Malacca gateway linkage;
- Southeast Asian shipping/system context.

#### Hormuz

- major Hormuz-facing port/terminal nodes where sourced;
- gateway/system relationships;
- no inferred dependency from proximity alone.

#### Panama

- Balboa / Colón / canal-associated infrastructure where sourced;
- canal gateway linkage and explicit operational relationships.

#### Cape route / Southern Africa

- selected major South African ports relevant to represented rerouting/logistics context;
- Cape route linkage where evidence supports it.

#### Bab el-Mandeb / Djibouti

- Djibouti/Doraleh infrastructure nodes where sourced;
- Red Sea / East African corridor context.

Do not attempt a global port inventory in this tranche.

---

## 9. Infrastructure browser behavior

### 9.1 Contextual rendering

Infrastructure should not become a permanent global visual layer by default.

Render relevant infrastructure contextually when:

- a selected country/entity references the asset;
- an active gateway references the asset;
- an active functional chain includes the asset/system;
- an Impact result contains the asset;
- the user explicitly opens an infrastructure item from contextual information.

This preserves map clarity.

### 9.2 Geometry

Use:

- point geometry for ports/terminals/landings/junctions;
- line geometry only when a sourced route/corridor/interconnector representation is meaningful;
- `no-geometry` when the system record is real but the repository does not yet own defensible geometry.

Approximate coordinates must be marked as visualization anchors and never implied to be navigational precision.

### 9.3 Popup/card content

Compact asset popup should show:

- label;
- type;
- countries/entities;
- linked gateway/chain/system;
- operator/authority if known;
- latest relevant observation/status;
- source/provenance;
- contextual investigation actions such as Impact if an explicit impact node exists.

No extra permanent infrastructure dashboard.

---

## 10. Chain integration

Functional chains remain contextual system objects.

Infrastructure can enrich chains through explicit references:

```text
chain -> infrastructure ids
infrastructure -> chain ids
```

The runtime should be able to answer:

```js
infrastructureForChain(chainId)
infrastructureForEntity(code)
infrastructure(id)
```

when those records exist.

Activating a chain may contextually reveal a bounded number of linked infrastructure nodes without changing base country fill.

Chain membership alone must not create a causal Impact edge.

---

## 11. Gateway integration

`data/world-map-gateways.json` remains the first-class gateway/chokepoint owner.

Infrastructure records may reference `gateway_ids`.

Browser behavior:

- selecting/clicking a gateway can reveal associated infrastructure;
- selecting a country can show its gateway + infrastructure context;
- gateway popup can expose explicit infrastructure relationships;
- existing gateway transit observations remain gateway-owned rather than copied into every terminal record.

This avoids duplicate factual ownership.

---

## 12. Impact integration

The existing Impact engine must be reused.

Extend supported node kinds as infrastructure records become available, for example:

```text
port:<id>
terminal:<id>
interconnector:<id>
pipeline:<id>
cable:<id>
rail:<id>
```

Only explicit dependency semantics enter the causal graph.

Allowed examples:

```text
country -> depends-on -> port
system -> uses-gateway -> gateway
industrial corridor -> depends-on -> grid-interconnector
terminal -> member-of-chain -> chain        # contextual, not causal
cable-landing -> member-of-system -> cable  # contextual unless dependency is explicit
```

Do not infer Impact edges from:

- physical proximity;
- country association;
- chain membership;
- shared group membership;
- ordinary relationship adjacency;
- phrases such as "important" or "strategic" without a dependency statement.

The existing boundary remains:

> represented dependencies, not a forecast of real-world failure.

---

## 13. Path integration with infrastructure

Path v1 in this tranche should remain entity-focused unless infrastructure graph semantics are sufficiently explicit during implementation.

Preferred sequence:

1. first make country/entity Path usable with current relationships;
2. introduce infrastructure records;
3. allow infrastructure nodes in Path only where typed non-causal/casual graph semantics are explicit and the UX remains understandable.

Do not block the Path repair on full infrastructure graph support.

---

## 14. Evidence and sourcing rules

Infrastructure is empirical data and requires source discipline.

Preferred sources by asset class include official authorities, operators, intergovernmental/agency datasets and other primary institutional sources.

Each first-wave record must have at least one explicit source URL.

Dated observations must carry date/period.

Do not present stale point values as current merely because they exist in an old country record.

When exact geometry, capacity, operator or relationship semantics are not available, mark unknown rather than infer.

Project Axis classifications remain separate from infrastructure evidence.

---

## 15. Time and D1–D11 are deliberately deferred

### 15.1 Time

The current Time module is technically real but still depends heavily on sparse historical owners, especially recovered North snapshots.

Do not promote Time into the clean ordinary interface in this tranche.

Instead, the new infrastructure and coverage schema should preserve dates/periods so future Time work has more useful state to operate on.

### 15.2 D1–D11 Axis depth

Do not activate the large existing `3d-axis-depth.js` vertical navigator in the ordinary map.

Reasons:

- it introduces a large persistent visual surface;
- it mixes symbolic navigation with ordinary geography;
- it would reverse the recent simplification of the interface.

Useful symbolic material can later be surfaced contextually through a compact Axis explanation rather than a 476px permanent navigator.

---

## 16. TDD and validation

Implementation must be test-first.

### 16.1 Path utility validator

Require:

- Path entry point exists in selected-country card;
- no dependency on hidden `#traceMenu`;
- no dependency on old `#relationType` DOM as source of truth;
- Path reads active selection and relation mode from current APIs;
- result is URL-persisted with `path`;
- invalid/stale path state clears;
- boundary text distinguishes represented graph from real-world completeness;
- no permanent Path item is added to World Bar.

Regression fixture:

```text
A --money--> B --systems--> C
A --institutions--> D --institutions--> C
```

Assertions should prove active relation mode changes the available path.

### 16.2 Investigation-surface validator

Require temporary specialist surfaces to avoid obvious overlap/conflict.

If a coordinator is implemented, validate Path/Impact/Trace registration and close behavior.

If event-only coordination is chosen, validate the equivalent behavior rather than requiring a specific abstraction.

### 16.3 Coverage validator

Require:

- exactly 195 canonical sovereign countries;
- registered map entities represented separately;
- duplicate-ISO3 detection;
- actual-content counts outrank stale stored counters;
- missing is not zero;
- no aggregate geopolitical/completion score;
- coverage includes systems/gateway/impact/infrastructure participation;
- generated ledger can be reproduced deterministically.

### 16.4 Infrastructure validator

Require:

- unique IDs;
- supported type vocabulary;
- countries/entities use valid canonical/registered codes;
- each record has provenance/source URL;
- location/no-geometry policy is explicit;
- approximate coordinates are labeled;
- gateway and chain references resolve;
- causal relationship types are explicitly distinguished from contextual ones;
- no contextual association automatically becomes an Impact dependency.

### 16.5 Runtime/browser validator

Require shared runtime APIs for infrastructure/context as implemented.

Require browser rendering to be contextual and not introduce a new permanent top-bar Infrastructure control.

Require Impact to accept explicitly represented infrastructure nodes without changing depth/score guardrails.

### 16.6 Exact-head gate

The full repository quality workflow must pass on the exact final PR head before merge.

After merge, exact-`main` quality and Pages deployment must also pass before claiming the utility wave is live.

---

## 17. Implementation decomposition

This design should be implemented in sequential, reviewable slices on one feature branch or a very small sequence of dependent PRs.

Recommended order:

### Slice 1 — Path utility

- failing Path utility validator;
- refactor pathfinder to current APIs;
- contextual Path entry point;
- modern result state and URL behavior;
- full regression check.

### Slice 2 — investigation surface coherence

- coordinate Path / Impact / Trace / Chain temporary surfaces;
- preserve individual module ownership;
- prevent obvious UI collisions;
- no new top-level controls.

### Slice 3 — coverage ledger

- revive/adapt archived coverage-builder ideas only where they match current owners;
- generate ledger from current canonical data/runtime;
- integrate into build/quality pipeline;
- do not expose public score.

### Slice 4 — infrastructure registry foundation

- add canonical schema/owner;
- add validator;
- seed a small first-wave set around existing gateways;
- include sources, dates, geometry policy and typed relationships.

### Slice 5 — runtime + contextual infrastructure

- project infrastructure records into the shared runtime;
- expose bounded entity/gateway/chain lookups;
- render only contextually;
- add compact asset popup.

### Slice 6 — Chain/Gateway/Impact integration

- connect explicit infrastructure references to Chain and Gateway context;
- extend Impact graph only with explicit causal relations;
- verify no automatic dependency inference.

### Slice 7 — final integrated verification

- full World Map validators;
- full repository quality workflow;
- public build;
- exact-main merge verification;
- Pages deployment verification.

---

## 18. Non-goals

This tranche does not include:

- global exhaustive infrastructure ingestion;
- live AIS/shipping telemetry;
- full company/beneficial-ownership graph;
- complete procurement/TED ingestion;
- complete FIGARO supply-use ingestion;
- probabilistic disruption simulation;
- synthetic risk/resilience/power scores;
- general arbitrary-depth graph explorer;
- a new permanent Infrastructure/Coverage/Investigation top-level menu;
- promotion of Time to ordinary UI;
- promotion of the large D1–D11 Axis depth navigator;
- automatic Axis classification from empirical infrastructure or institutions.

---

## 19. Success criteria

The tranche succeeds when a normal user can select a country and naturally move through increasingly deep questions without hunting through hidden menus:

```text
What is this country?
    ↓
What does it connect to?
    ↓
How does it connect to another country?       [Path]
    ↓
What system/functional chains is it part of?  [Chain]
    ↓
What gateways/infrastructure matter here?     [Gateway / Infrastructure]
    ↓
Who explicitly depends on this represented object? [Impact]
```

At the same time, the repository gains an internal coverage ledger that tells future enrichment work where these answers are still weak.

The measure of success is not number of controls or records. It is whether the same compact World Map can answer materially better relational questions with correctly owned, sourced and epistemically separated data.

---

## 20. Self-review

- No new permanent toolbox is introduced.
- Existing modules are reused rather than duplicated.
- Path, Connections, Chain and Impact remain semantically distinct.
- Coverage is internal/descriptive rather than a public score.
- Infrastructure has a canonical owner and does not duplicate gateway authority.
- Explicit causality is required before infrastructure enters Impact.
- Time and D1–D11 are intentionally deferred.
- The tranche is decomposable into sequential TDD slices.
- Missing evidence remains unknown rather than inferred.
