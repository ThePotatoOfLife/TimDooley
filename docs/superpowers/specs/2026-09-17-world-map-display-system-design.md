# World Map Display System — Design

**Date:** 2026-09-17  
**Status:** approved design direction  
**Scope:** World Map hover, current-map context, selected-country presentation, pinned-country comparison, inspector depth, navbar-to-subject interaction, population invariants, and physical-surface ordering.

## 1. Purpose

The World Map already contains the right major subsystems, but ordinary browsing currently repeats the same country facts and analytical answers across several surfaces. Hover, Current Map View, the selected Country Card, the pinned-country rail, and Country Pulse independently decide what to show. This creates duplication, inconsistent hierarchy, and uncertainty about where new information belongs.

This design defines one display grammar for the entire map:

- **the selected country is the persistent subject;**
- **hover is an ephemeral preview subject;**
- **the World Bar / navbar defines the current question or lens;**
- **Current Map View explains the question itself;**
- **the Country Card answers that question for the selected subject while retaining stable country identity;**
- **pins retain other subjects and answer the same question comparatively;**
- **the right inspector provides deeper explanation, provenance, statistics and specialist investigations.**

The goal is not to add another UI. The goal is to make every existing surface own one clear level of information.

## 2. Governing principle

> **Country selection defines the subject. Navbar state defines the question asked of that subject.**

Neither side silently replaces the other.

Changing country selection must not clear analytical/navbar state. Changing navbar state must not change the selected country. Hover must not mutate either.

The system must support states such as:

```text
primary question = Inflation
selected subject = Denmark
hover subject = Germany
pinned subjects = France, Canada
set context = EU, NATO
relation context = Systems
time = Current
physical context = Water, Terrain
projection = Globe
```

All of those may coexist without competing for the same UI role.

## 3. Existing owners preserved

This overhaul must preserve current low-level ownership:

- `world-map/3d-country-selection.js` — active selected country, pins, relation mode and bounded automatic relations;
- `world-map/3d-active-view.js` — analytical answer for a country under current map layers;
- `world-map/3d-context-visibility.js` — derived presentation context, scale and investigation budgets;
- `world-map/3d-layer-registry.js` + compositor — active analytical layers and country visual composition;
- `world-map/3d-interaction-router.js` — semantic hover/click arbitration;
- `world-map/3d-tooltip.js` — transient pointer-attached presentation surface;
- `world-map/3d-inspector-router.js` — persistent right-inspector baseline and child investigations;
- `world-map/3d-ui-layout.js` — screen-zone placement;
- `world-map/3d-render-stack.js` — physical/context/selection render ordering;
- Evidence / Trace / Path / Impact and specialist modules — deep investigation semantics.

The redesign must not create a second selection owner, second layer registry, second country database, or second inspector stack.

## 4. The four subject roles

The display system distinguishes four subject roles.

### 4.1 Preview subject

The country currently under the pointer.

Properties:

- ephemeral;
- disappears on pointer leave;
- never written to URL;
- never changes selection;
- never changes pins;
- never changes inspector baseline;
- never causes automatic relation expansion;
- may request the current analytical answer for that country.

### 4.2 Active subject

The currently selected country.

Properties:

- persistent until another country is selected or active selection is cleared;
- owns the Country Card;
- is the root for automatic relationship context;
- is the baseline subject for the right inspector;
- survives hover changes;
- survives navbar changes.

### 4.3 Retained subjects

Pinned countries.

Properties:

- persistent comparison context;
- lighter than the active subject;
- shown in the pinned rail;
- answer the same primary question as the active country;
- do not each receive a full Country Card or inspector.

### 4.4 Investigation subject

The semantic object currently opened inside the right inspector stack.

It may be the active country itself or a child object such as a connection, infrastructure asset, entity, path, evidence record or chain. The Inspector Router remains the owner of this navigation depth.

## 5. Current Question model

The display system needs one derived Current Question object rather than allowing every surface to reinterpret active buttons independently.

Conceptual shape:

```js
{
  primary: {
    kind: 'scalar' | 'set' | 'none',
    id: 'stat.inflation',
    label: 'Inflation'
  },
  sets: [
    { id:'group.eu', label:'EU' },
    { id:'group.nato', label:'NATO' }
  ],
  relations: {
    mode:'systems',
    label:'Systems'
  },
  physical: [
    { id:'physical.water.base', label:'Water' },
    { id:'physical.terrain', label:'Terrain' }
  ],
  geographies: [],
  time: { mode:'current', time:'', time2:'' },
  projection:'globe',
  investigation:'browse'
}
```

This is derived state. It does not own underlying layer, time, projection or selection state.

### 5.1 Primary question

Only one item receives the primary country-answer position.

Priority:

1. active scalar analytical layer, when one exists;
2. active set query when no scalar exists;
3. otherwise neutral country browsing.

Relationship mode, physical layers, geography overlays, projection and time are supporting context. They do not displace a scalar/set primary question merely because they are active.

### 5.2 Supporting context

Supporting context can coexist with the primary question:

- active sets;
- relation filter;
- geography overlays;
- physical layers;
- time mode/window;
- projection;
- investigation mode.

Supporting context is shown only on surfaces where it is meaningful.

## 6. Shared Country Presentation adapter

All country-subject surfaces must consume one shared presentation adapter rather than independently resolving population, current-map answers or missing-value semantics.

Preferred responsibility extension: build on `3d-active-view.js` or a focused sibling presentation module that consumes Active View and the canonical data runtime.

Conceptual API:

```js
await CountryPresentation.forCountry('DNK')
```

Conceptual result:

```js
{
  code:'DNK',
  identity:{
    name:'Denmark',
    officialName:'Kingdom of Denmark',
    capital:'Copenhagen',
    area:{ value:42947, unit:'km²' }
  },
  population:{
    value:6000000,
    display:'6.0M',
    period:'2025',
    source:'...'
  },
  answer:{
    kind:'scalar',
    id:'stat.inflation',
    label:'Inflation',
    status:'current',
    display:'1.7%',
    period:'2025',
    source:'World Bank'
  },
  sets:{...},
  relation:{ mode:'systems', count:8 },
  active:true,
  pinned:false
}
```

The shared adapter owns presentation normalization only. Canonical data remains in existing runtimes/files.

### 6.1 Shared invariants

The adapter defines:

- one population fallback path;
- one current analytical-answer resolver;
- one missing-value representation;
- one period/source interpretation;
- one number-formatting policy for shared summary values;
- one country-name/code resolution path.

No ordinary country surface may separately reinvent those rules.

## 7. Population invariant

Population is a permanent country-orientation field.

For every country subject surface:

- hover preview — Population field exists;
- selected Country Card — Population field exists;
- pinned card — Population field exists;
- deep country inspector summary — Population field exists.

If unavailable:

```text
Population · —
```

Never coerce `null`, `undefined` or empty string to zero. Never silently omit the field.

When Population itself is the primary analytical layer, the UI must deduplicate rather than show two identical population values. The permanent population field remains, and the current-answer treatment may attach source/period/emphasis to that same field.

## 8. Surface ownership

### 8.1 Tooltip / Hover — identify and preview

Hover is deliberately minimal.

Neutral browsing:

```text
Denmark
Population · 6.0M
```

A small optional secondary identity line may show capital or area only if the layout remains genuinely minimal and no analytical question is active.

Scalar active:

```text
Denmark
Inflation · 1.7%
Population · 6.0M
```

Set query active:

```text
Denmark
Matches · EU yes · NATO yes
Population · 6.0M
```

Relationship mode active without scalar/set primary question:

```text
Denmark
Systems · 8 represented connections
Population · 6.0M
```

Hover must not show government, general GDP, memberships unrelated to active sets, chains, project interpretation, evidence detail, multiple generic statistics, actions or deep relation lists.

The shared Tooltip service is the only ordinary country-hover surface. The separate context-status surface must not also become a competing country preview.

### 8.2 Current Map View — explain the question

Current Map View is global context, not a country surface.

It answers:

> What is the map currently asking/showing?

It may show:

- primary scalar label;
- scalar source owner / epistemic type / coverage / period;
- active set labels and ANY/ALL logic;
- current relation filter;
- active time mode/window;
- projection;
- active supporting geographies;
- physical context summary when useful;
- investigation mode when not ordinary browse.

It must not show the selected country's current value, population or country identity.

When a relationship mode needs a subject but no country is selected, Current Map View should explicitly orient the user, for example:

```text
Systems connections · select a country
```

rather than appearing broken or silently empty.

### 8.3 Selected Country Card — persistent ordinary country workspace

The upper-left Country Card remains the single ordinary persistent country information surface.

It has three layers:

1. permanent orientation header;
2. permanent Current Map Answer block;
3. tabbed secondary content.

#### Permanent header

Always visible:

- flag when available;
- country name;
- ISO3 code;
- capital;
- population;
- pin state/action.

#### Permanent Current Map Answer

Always visible when a primary question exists.

Scalar example:

```text
CURRENT MAP
Inflation
1.7%
2025 · World Bank
```

Set example:

```text
CURRENT MAP
EU + NATO · ANY
Matches
EU yes · NATO yes
```

Neutral browsing does not render an empty Current Map box.

#### Tabs

Exactly three ordinary tabs:

- **Overview**
- **Context**
- **Connections**

No additional top-level tabs are introduced in this wave.

### 8.4 Overview tab

Purpose:

> What kind of country is this?

Stable baseline, largely independent of navbar state.

Target content:

- population;
- GDP;
- GDP per capita when available;
- growth;
- inflation;
- unemployment;
- area;
- capital;
- concise government/system identity.

The Overview tab should not become a full dossier. Detailed statistics belong in the inspector.

### 8.5 Context tab

Purpose:

> What do the things currently active on the map mean for this country?

Context is conditional. Empty sections are not rendered.

Possible sections:

- active set memberships;
- active set query result;
- time state when non-default or analytically relevant;
- current geography overlays only when country-specific context exists;
- relevant functional chains surfaced by active context;
- clearly typed project/Axis interpretation when active/relevant;
- active physical context only when it changes country-specific interpretation; ordinary Water/Terrain toggles do not create meaningless country rows.

Context must not become a dump of every globally active button.

### 8.6 Connections tab

Purpose:

> What are the strongest represented relationships from this country under the current relation filter?

Behavior:

- show bounded strongest relationships;
- respect `all`, `money`, `systems`, `institutions`, `project`, `other`;
- show partner name and compact relation type summary;
- show represented connection count when available;
- provide promotion to full Trace / specialist investigation;
- do not render the whole graph in the card.

### 8.7 Country Card actions

Actions remain outside tab content so they do not move around:

- Pin / Unpin;
- Statistics;
- More Data;
- Trace;
- Path;
- Impact.

The exact visual density may be refined, but these remain navigation/investigation actions rather than information sections.

### 8.8 Pinned Context Rail — retained comparison subjects

Each pin answers the same primary question as the selected country.

Scalar example:

```text
Germany
Inflation · 2.1%
Population · 83.5M
```

Set example:

```text
Germany
EU · Member
Population · 83.5M
```

Neutral example:

```text
Germany
Population · 83.5M
```

Pinned cards do not show government, capital, chains, generic memberships or deep relation lists. Clicking a pin activates that country without unpinning it.

### 8.9 Right Inspector — explanation and depth

The inspector is deeper than the Country Card.

Its country baseline may include:

- Country Pulse;
- complete/expanded statistics;
- demography;
- economy;
- infrastructure;
- energy;
- institutions;
- memberships;
- provenance and source coverage;
- history/time detail;
- deeper relationship sections.

Child investigations include Evidence, Trace, Path, Impact, entity detail, infrastructure detail and other specialist modules through the existing Inspector Router.

Country Pulse should evolve toward inspector-depth material and should not simply repeat the Country Card's first screen.

## 9. Navbar behavior classes

Every World Bar control belongs to a display class.

### 9.1 Scalar controls

Examples: Population, GDP, GDP per capita, Inflation, Unemployment, religion percentage.

Effects:

- country fill/color becomes primary analytical question;
- hover shows scalar answer + population;
- Country Card Current Map Answer shows scalar answer;
- pins compare scalar answer + population;
- inspector may expose source/history/deeper statistics.

### 9.2 Set controls

Examples: EU, NATO, Schengen, G20, Axis sets.

Effects:

- map highlights set membership/query;
- hover shows membership answer + population;
- Country Card Current Map Answer shows match/outside state;
- Context tab lists active set memberships;
- pins show comparable membership answer + population.

### 9.3 Relationship controls

Examples: All, Money, Systems, Institutions, Project, Other.

Effects:

- filter bounded automatic relationships from selected country;
- no selected country => Current Map View explicitly asks user to select one;
- hover remains minimal and does not expand relations;
- Country Card Connections tab reflects current filter;
- Trace remains the deep graph surface.

### 9.4 Geography/context overlays

Examples: basin extents, historical/scriptural geographies, project geographies.

Effects:

- remain geographic context on the map;
- Current Map View lists them as supporting context when appropriate;
- Country Card Context tab mentions them only when a country-specific relation/intersection/context is available;
- they do not become generic country metrics merely because they are active.

### 9.5 Physical controls

Examples: Water, Terrain, land-cover context.

Effects:

- physical map context only;
- may be summarized in Current Map View if useful;
- never replace the primary analytical question;
- never create arbitrary Country Card rows unless a future physical-country analysis explicitly provides a country-specific answer.

### 9.6 Time and projection

Time and projection modify context, not subject identity.

- changing time never changes selected/hovered/pinned country;
- changing projection never changes selected/hovered/pinned country;
- Current Map View owns their global presentation;
- country answers consume the time state when the underlying domain supports it.

## 10. Interaction state machine

### 10.1 Hover only

No selected country:

- tooltip follows hover subject;
- Country Card hidden;
- Current Map View remains global;
- pins remain if they exist;
- inspector baseline is not replaced by hover.

### 10.2 Click country

- clicked country becomes active subject;
- Country Card opens/updates;
- automatic relations re-root to active subject;
- right inspector baseline becomes/refreshes country baseline when appropriate;
- navbar state remains unchanged.

### 10.3 Hover another country while one is selected

- tooltip shows hovered country;
- Country Card remains selected country;
- selected outline remains selected country;
- pins unchanged;
- URL unchanged;
- inspector unchanged.

### 10.4 Change scalar/set layer with country selected

- selected country remains selected;
- map composition changes;
- tooltip answer changes for whatever is hovered;
- Country Card Current Map Answer changes;
- Context tab updates active memberships/context;
- pins update comparison answer;
- Overview remains stable.

### 10.5 Change relation mode with country selected

- selected country remains selected;
- automatic relationships re-filter;
- Connections tab updates;
- Current Map View updates relation context;
- scalar/set primary answer remains primary if one is active.

### 10.6 Pin country

- active subject may also be pinned;
- pinned rail appears/updates;
- pinning alone does not create a second deep inspector;
- pinning does not change navbar state.

### 10.7 Activate pinned country

- clicked pin becomes active subject;
- remains pinned;
- Country Card and inspector baseline switch to that country;
- other pins remain retained.

## 11. Duplication rules

### 11.1 Population

One shared population presentation value. Displayed wherever required, but not independently resolved.

### 11.2 Current analytical answer

One shared country answer. Hover, Country Card and pins may render it at different density but may not recalculate it separately.

### 11.3 Current Map View

Global question/context only. Country-specific answer forbidden.

### 11.4 Country Card vs Country Pulse

Country Card = ordinary answer/navigation.  
Country Pulse / inspector = depth, provenance and expanded material.

### 11.5 Context status

`3d-context-status.js` in its current mixed role should not remain a second country-preview/current-view surface.

Preferred outcome:

- pointer country preview belongs to Tooltip;
- global current map context belongs to `atlasWorldContext` / World Bar context;
- selected country belongs to Country Card.

The module may be removed, folded into existing owners, or reduced to non-country diagnostics if a residual role is still necessary. It must not duplicate country preview or selected-country answer.

## 12. Presentation profiles

The shared adapter may expose explicit profiles or equivalent selectors:

- `preview` — name, population, current answer;
- `selected` — identity, population, current answer, baseline summary;
- `pinned` — name, population, current answer;
- `deep` — full normalized summary metadata for inspector consumers.

Profiles control disclosure only. They do not create different facts.

## 13. Missing data and async behavior

- missing values render as `—` or `Unknown` according to semantic type;
- null numeric values must never coerce to zero;
- stale hover responses must never overwrite a newer hovered country;
- stale selected-country responses must never overwrite a newer selected country;
- pin updates must use generation/serial suppression;
- one failing optional source must not remove the entire country surface;
- source/period metadata must remain attached to the answer that produced it.

## 14. Mobile behavior

The same semantic hierarchy survives narrow screens.

- hover is irrelevant on touch-only interaction and must not be required for access to information;
- tap selects country and opens/updates the Country Card or mobile equivalent;
- the Country Card tabs remain available;
- pinned rail remains horizontally scrollable and bounded;
- expanded right inspector / bottom sheet may suppress nonessential pinned-card metadata but not the pinned set itself;
- Current Map View remains compact and must not cover primary controls.

No separate mobile ontology is introduced.

## 15. Physical-surface render-order invariant

The water fix is now part of the display-system contract because physical context must remain visually subordinate to canonical land/country presentation.

Required broad order:

```text
ocean base
land mask
terrain hillshade
country analytical surface
lake / river / coastline detail
country boundaries / selection emphasis
```

Implementation-specific nuance:

- ocean base and land mask remain in `physical-surface` below `countries-fill`;
- terrain hillshade remains a later `physical-surface` layer than ocean/land mask;
- lakes may use `physical-water` above country fill for legibility;
- rivers/coastlines use physical linework below canonical country boundary;
- the raw ocean base must never be registered into `physical-water`, which would place the global ocean surface above country fill.

Tests must protect this registration/order contract.

## 16. Surface matrix

| Information | Hover | Current Map View | Country Card header/current | Overview | Context | Connections | Pins | Inspector |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Country identity | minimal | no | yes | yes | inherited | inherited | yes | yes |
| Population | always | no | always | yes | no duplicate | no | always | always |
| Primary scalar answer | yes | question only | yes | no duplicate | metadata if relevant | no | yes | deep/source/history |
| Set answer | yes | query only | yes | no | yes | no | yes | deep |
| Generic baseline metrics | no | no | concise | yes | no | no | no | expanded |
| Relation filter | no/compact count only | yes | compact context | no | optional context | yes | no | yes |
| Strong relation list | no | no | no | no | no | bounded | no | expanded |
| Physical layers | no | supporting context | no | no | only if country-specific | no | no | specialist if needed |
| Geography overlays | no | supporting context | no | no | only if country-specific | no | no | deep if inspected |
| Time/projection | no | yes | answer metadata only | no | when relevant | no | no | deep/history |
| Actions | no | no | persistent | no | no | Trace promotion | activate/unpin | specialist actions |

## 17. Testing contract

Add behavioral/runtime tests for at least:

1. hover country with no selection → minimal preview only;
2. hover country while another country is selected → preview changes, selected Country Card does not;
3. scalar layer active → hover/card/pins all receive the same normalized answer;
4. set query active → hover/card/pins receive consistent membership answer;
5. navbar scalar change → subject preserved, answers update;
6. relation-mode change → subject preserved, Connections tab updates;
7. physical-layer change → primary analytical answer not displaced;
8. no selected country + relationship mode → Current Map View shows a select-country orientation state;
9. population field exists on hover/card/pins/deep summary;
10. null population never renders zero;
11. Population layer deduplicates permanent population/current-answer presentation;
12. Overview content remains stable across layer changes;
13. Context tab does not render empty sections;
14. pin activation changes active subject without unpinning;
15. hover never mutates URL, selection, pins, inspector or relations;
16. stale hover async result cannot overwrite a newer hover;
17. stale Country Card async result cannot overwrite a newer selection;
18. current-map context contains no country-specific value;
19. context-status mixed ownership is removed/reduced;
20. ocean base remains below land mask, terrain hillshade and country fill according to render-stack contract.

Repository validators should also continue to enforce one ordinary Country Card, one UI Layout coordinator, one Context Visibility orchestrator, one Inspector Router, one Render Stack and one Interaction Router.

## 18. Migration approach

This should be implemented as a consolidation rather than a parallel rewrite.

1. protect the desired contract with failing tests;
2. extend/create the shared Country Presentation adapter;
3. move hover to the minimal shared presentation profile;
4. make Current Map View global-only;
5. remove/reduce mixed `3d-context-status.js` behavior;
6. restructure Country Card into permanent header + Current Map Answer + Overview/Context/Connections tabs;
7. migrate pins to the shared adapter;
8. migrate Country Pulse/inspector baseline away from first-screen duplication and toward depth;
9. add explicit handling for neutral/scalar/set/relation/physical/geography/time combinations;
10. add population invariants;
11. add physical render-order regression;
12. run targeted World Map suites and full repository quality checks;
13. perform a final duplication/ownership audit before integration.

## 19. Non-goals

This wave does not:

- redesign the World Bar visual style from scratch;
- create a second country inspector;
- create a separate Compare application;
- rewrite canonical country data;
- expand every specialist dataset;
- redesign Evidence, Trace, Path or Impact internals;
- create full generic hover support for every non-country object;
- change project/Axis epistemic semantics;
- change the physical-water geometry fix except to protect ordering.

## 20. Future extensibility

The same display grammar should later support non-country objects.

A generic presentation subject may eventually expose:

```text
country
place
infrastructure
institution
relationship
gateway
spatial geography
Axis/project object
```

Each object can then provide `preview`, `selected` and `deep` disclosures without inventing independent UI rules.

This future direction must not delay the country display overhaul.

## 21. Definition of success

The overhaul succeeds when a user can:

1. turn analytical/context buttons on and off;
2. hover rapidly across countries;
3. select one country;
4. pin several others;
5. change scalar/set/relation/time/projection state;
6. open deeper investigations;

and always understand, without duplication or ambiguity:

- **what question the map is asking;**
- **which country is merely being previewed;**
- **which country is selected;**
- **which countries are retained for comparison;**
- **where to look for ordinary country facts;**
- **where to look for active-context meaning;**
- **where to look for relationships;**
- **where to go for deeper evidence and investigation.**

The interface should feel like one coherent information system rather than several individually useful modules competing for attention.
