# World Domain Gateway and World Map Responsibility Design

## Status

Approved architectural direction, pending written-spec review before implementation.

## Goal

Keep the public site at exactly five primary doors while changing the fifth door from **World Map** to **World**.

`/world/` becomes a deliberately small gateway into four sibling public lenses:

1. **World Map** — geographic and spatial investigation.
2. **Politics & Geopolitics** — political positions, proposals, chronology, judgments, predictions, questions, and unresolved positions.
3. **North** — North Axis / North Programme interpretation, programme design, and the boundary between symbolic and empirical North.
4. **World Systems** — non-spatial systems such as institutions, economy, finance, ownership, trade, industry, energy, technology, infrastructure, security, labour, capability, dependency, resilience, and related research.

The central architectural correction is:

> **World is the public domain. World Map is one instrument inside that domain.**

The World Map must no longer carry the implicit responsibility to explain every world-facing subject simply because the subject involves countries.

---

## 1. Why this change is needed

The current five-door public architecture routes the fifth door directly to `/world-map/`. At the same time, the internal World and North branches and multiple backend families have grown far beyond cartography. The World Map registry now knows about government, economy, finance, ownership, trade, industry, energy, infrastructure, technology, migration, security, capability, dependency, resilience, programmes, repair, project-symbolic Axis material, and other non-map concepts.

This creates three problems:

1. **Conceptual overload** — “World Map” is forced to mean both a geographic instrument and the project’s entire world-facing knowledge domain.
2. **UI pressure** — material that is politically, institutionally, philosophically, or programmatically important tends to become another map mode, layer, control, or inspector responsibility.
3. **Ownership ambiguity** — it becomes unclear whether the map owns a claim, merely visualizes it, or is being used as a routing surface for material whose real owner lives elsewhere.

The correction should preserve the relational backend while separating public lenses by job.

---

## 2. Public architecture

The homepage keeps exactly five primary doors:

1. Tim Dooley
2. Religion
3. Philosophy
4. Science
5. **World**

The fifth card links to `/world/`, not `/world-map/`.

The homepage should continue to be calm and sparse. It must not list Map, Politics, North, and World Systems as four additional primary doors.

### `/world/` gateway

`/world/` is a lightweight routing surface, not a long-form compendium and not a second archive.

It should answer one question quickly:

> **How do you want to look at the world?**

It presents four strong routes with one-sentence ownership descriptions:

- **World Map** — countries, geography, measurable relationships, memberships, spatial assets, flows, dependencies, comparison, and time.
- **Politics & Geopolitics** — what Tim has said, proposed, questioned, predicted, supported, opposed, or left unresolved politically.
- **North** — symbolic orientation, empirical northern geography, North Programme design, European capability, and their evidence boundaries.
- **World Systems** — institutions and systems that are relational but not inherently geographic: economy, finance, ownership, industry, energy, technology, infrastructure, security, labour, capability, dependency, resilience, and related research.

The gateway may also expose a quiet route to the deep World archive in Explore, but it should not reproduce the archive tree.

---

## 3. Responsibility boundaries

### 3.1 World Map

The World Map owns questions whose primary representation is spatial, geographic, or country-comparative.

Primary jobs:

- where something is;
- which countries or places participate;
- what geographic entities are connected;
- typed cross-border relationships;
- measurable scalar/set overlays;
- flows, routes, infrastructure, and geocoded assets;
- memberships with territorial/country representation;
- comparison between geographic entities;
- dated geographic state where evidence supports it;
- spatial investigation and trace tools.

The Map may visualize political, economic, institutional, or programme data when that data has a legitimate spatial representation. Visualization does **not** make the Map the canonical owner of the underlying concept.

The map should not be responsible for explaining:

- Tim’s political philosophy;
- complete policy programmes;
- ideological positions;
- moral/political judgments;
- political chronology;
- unresolved political positions;
- broad non-spatial institutional analysis;
- sacred or symbolic meaning merely because it is associated with a country;
- general research dossiers that only incidentally mention places.

### 3.2 Politics & Geopolitics

Politics owns questions of:

- what Tim has said or accepted politically;
- political chronology and development;
- governance philosophy;
- political economy;
- civil liberties;
- immigration/citizenship positions;
- geopolitical judgments and predictions;
- policy proposals;
- support/opposition ledgers;
- political research leads;
- distinctions between explicit position, proposal, question, prediction, satire, mythology, and archive synthesis;
- negative space and unresolved positions.

Politics can link to the Map for geographic evidence or spatial exploration.

### 3.3 North

North remains a specialist bridge because it contains multiple non-equivalent meanings that must remain explicit:

- project-symbolic North / North-of-North;
- conceptual geography;
- empirical northern and European relationships;
- North Programme research and policy design;
- repair/intervention methodology.

North owns the explanation of why a North concept or programme exists and what it means. The Map may show the geography or membership relevant to a specific North view.

### 3.4 World Systems

World Systems owns non-spatial or only partially spatial system structure, especially:

- state and governance architecture;
- public finance and debt;
- banking and capital;
- company ownership/control;
- production and industry;
- trade and value chains;
- energy systems;
- infrastructure systems;
- technology and digital capability;
- research and innovation;
- labour and skills;
- migration systems where the primary object is a system rather than a map;
- security and defence-industrial systems;
- capability and dependency;
- resilience;
- procurement and projects;
- evidence-backed intervention/repair analysis.

The first public World Systems surface should be an index/gateway into canonical owners and high-value investigations, not an attempt to render every backend dataset at once.

---

## 4. Shared backend, multiple lenses

This design does **not** split the relational backend into four silos.

The project keeps one evidence-governed relational backend with canonical owners. Different public surfaces are projections over the same relationships.

Example:

- NATO membership is stored once in its canonical source.
- The Map can render NATO geographically.
- World Systems can explain NATO as an institutional/security system where relevant.
- Politics can discuss Tim’s views about NATO.
- North can discuss NATO where it materially affects North Programme analysis.

No surface should duplicate the underlying fact as a second canonical truth.

Core rule:

> **One fact / relationship owner; many legitimate views.**

---

## 5. Routing and projection contract

`data/frontend-atlas-bridge.json` remains the public routing contract, but its fifth primary door changes semantically from `world_map` to `world`.

Target public doors:

- `tim` -> `tim-dooley/`
- `religion` -> `religion/`
- `philosophy` -> `philosophy/`
- `science` -> `science/`
- `world` -> `world/`

The existing `/world-map/` route remains stable and is not redirected away.

The `north` and `world` archive branches should project primarily through the World door while preserving their specialist routes:

- `north` human specialist route: `/north/`
- `world` human gateway route: `/world/`
- map specialist route: `/world-map/`
- politics specialist route: `/politics/`
- systems specialist route: `/world-systems/`

Backend families that currently name `world_map` as their primary public door should generally move to `world` unless they are specifically map-only presentation contracts. Their `deep_route` should continue to point to the most appropriate specialist surface.

The routing bridge owns **routing intent only**. Canonical content ownership remains in source files.

---

## 6. World Map simplification strategy

Do not remove useful Map capabilities merely because a new World gateway exists.

Implementation should proceed in this order:

1. Establish `/world/` and change public routing ownership.
2. Preserve all existing World Map URLs and current validated runtime behavior.
3. Add clear sibling navigation between World, Map, Politics, North, and World Systems.
4. Audit Map controls/layers by responsibility.
5. Move or demote only those Map responsibilities that are clearly non-spatial and now have a better owner.

### Project-symbolic Axis material

The first pass should **not delete** Axis/North overlays from the Map.

Instead:

- North becomes the explanatory owner of symbolic/programmatic North;
- the Map remains a possible visualization surface;
- project-symbolic layers should not silently define the Map’s overall identity;
- future cleanup may demote deeper Axis navigation into a specialist pathway if it continues to compete with ordinary geographic use.

This avoids a risky simultaneous rewrite of map rendering and public architecture.

---

## 7. Politics PR reconciliation

The existing Politics & Geopolitics reader work should be preserved, but reconciled with this architecture before merge.

Required changes to that work:

- treat `/politics/` as a World sibling, not merely an “Other thread” attached to the homepage;
- link Politics back to `/world/` as its parent public domain;
- keep `/world-map/` links only where spatial investigation is useful;
- preserve the provenance-aware political mode ledger and unresolved-position section;
- avoid making Politics a sixth homepage door;
- refresh the branch onto current `main` before final verification.

The politics compendium remains a canonical political reader/data owner; the World gateway only routes to it.

---

## 8. World Systems first version

`/world-systems/` should begin small.

It should not attempt to become a dashboard containing every system at launch.

Recommended first version:

- short explanation of relationship-first systems research;
- grouped routes for Governance, Economy & Finance, Ownership & Production, Energy & Infrastructure, Technology & Research, Labour & Society, Security & Capability, Dependencies & Resilience;
- links into high-value canonical/Explore investigations;
- explicit evidence boundary;
- link to the World Map when a system has a spatial view;
- link to Politics when the user moves from observed systems to Tim’s policy or political interpretation.

The surface may later evolve into a richer systems browser, but only if concrete user needs justify it.

---

## 9. Navigation model

The World family should feel related without creating a heavy site-wide navigation bar.

Preferred local navigation on World-family pages:

`World · Map · Politics · North · Systems`

Rules:

- local, stable, no automatic viewport movement;
- current surface indicated quietly;
- no floating global widget;
- no duplicated giant menu;
- existing site-native visual language retained.

The Map can keep its specialized application header; a compact `World` parent link or local family link is sufficient.

---

## 10. Validation and compatibility

Implementation must preserve:

- exactly five homepage primary doors;
- existing `/world-map/` URLs;
- existing `/north/` URLs;
- existing Explore branch routes;
- canonical data ownership;
- unknown/null semantics;
- epistemic separation between observed, inferred, and project-interpretive material;
- stable Map camera behavior from the browse-first redesign;
- current World Map runtime contracts unless intentionally revised with new tests.

Validation should be updated so it asserts:

1. the fifth homepage door is World and routes to `/world/`;
2. `/world/` exposes the four sibling lenses;
3. the projection contract has exactly five public doors and uses `world` rather than `world_map` as the fifth primary public domain;
4. World Map remains a valid specialist route;
5. Politics and North remain secondary/specialist routes rather than new homepage doors;
6. World Systems exists and is reachable through World;
7. no routing change silently changes canonical backend ownership;
8. discovery/sitemap/build outputs include the new World surfaces without inventing a parallel navigation hierarchy.

---

## 11. Implementation boundaries

### In scope for the first implementation

- `/world/` gateway;
- homepage fifth-door rename/re-route;
- `frontend-atlas-bridge.json` projection migration;
- build/discovery/validation updates required by that migration;
- `/world-systems/` first lightweight surface;
- local World-family navigation;
- reconciliation of the open Politics reader work with the World domain;
- targeted copy changes on the Map that clarify it is a geographic/spatial instrument rather than the whole World domain.

### Not in scope for the first implementation

- rewriting the World Map runtime;
- deleting existing map layers wholesale;
- redesigning the relational backend;
- moving canonical datasets merely to match frontend routes;
- building a giant World Systems dashboard;
- making Politics a sixth homepage door;
- collapsing North into Politics or the Map;
- changing the meaning of evidence/provenance classes;
- broad unrelated frontend refactors.

---

## 12. Success criteria

The design is successful when a visitor can answer these routing questions intuitively:

- “I want to inspect countries and geographic relationships.” -> **World Map**
- “I want to understand Tim’s politics.” -> **Politics & Geopolitics**
- “I want to understand North and the North Programme.” -> **North**
- “I want to understand economic/institutional/technical systems without forcing them onto a globe.” -> **World Systems**
- “I’m not sure which one I need.” -> **World**

And the World Map itself should feel more focused because it no longer has to serve as the conceptual homepage for every world-facing idea.
