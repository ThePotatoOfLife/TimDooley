# Potato House Public Crystallization Design

Status: approved architectural direction, written-spec review gate

## Goal

Turn the existing Potato House research and constitution into a concrete architecture for a normal, fast, readable public website whose internal data model can keep growing without forcing backend concepts onto visitors.

The public site must remain familiar: a homepage, five major hubs, subject pages, guides/dossiers, specialist explorers, timeline, and sources. The Potato/House/Vesica/Tree logic governs ownership, information flow, maturity, relation, synthesis, and navigation underneath those ordinary pages.

The implementation must make the repository more sophisticated internally while making the public site easier to understand externally.

## Governing principle

The Potato of Life is the hidden organizing grammar of the system, not the required visual interface.

The public website is a projection of durable knowledge. It does not own durable knowledge.

More source material should produce better ownership. Better ownership should produce better synthesis. Better synthesis should produce clearer public pages. Increasing backend complexity must not force increasing homepage complexity.

If adding knowledge makes the homepage harder to understand, the system has failed to metabolize the knowledge.

## Scope

This design defines the architectural direction for making the Potato House operational for public information flow. Its immediate implementation milestone is Wave 1: governance registries, schemas, current-route topology classification, validators, and primary World-routing normalization.

The broader architecture also defines the interfaces later waves must respect:

1. machine-readable Domain Room registry;
2. machine-readable public surface registry;
3. public page projection contract;
4. topology/placement bridge for current major routes;
5. information maturity/crystallization states;
6. validators for ownership, route identity, relation integrity, and homepage/public-shell consistency;
7. normalization of the visible primary navigation around Home, Tim Dooley, Religion, Philosophy, Science, and World;
8. World as the fifth primary public gateway, with World Map, Politics & Geopolitics, North, and World Systems beneath it as lenses;
9. preservation of Explore, Timeline, Sources, and other specialist interfaces as secondary views;
10. a migration path from older manifests/navigation contracts into the new House contracts without deleting provenance-bearing research.

This design deliberately does not require a visual redesign of `index.html` in the first wave.

## Non-goals

The first implementation wave will not:

- replace the static-site architecture with React, a database server, or a CMS;
- make the homepage a graph, tree, Vesica, spatial simulation, or 3D interface;
- mass-move repository files into a new directory tree;
- build a universal numeric truth or altitude score;
- expose backend terms such as Plane, North-of-North, WITHIN, Root, Mountain, or D1-D11 as required public navigation labels;
- delete old architecture documents merely because they are superseded;
- make generated pages canonical owners of knowledge;
- infer that every public hyperlink is a durable Transition record;
- collapse historical, scientific, theological, symbolic, autobiographical, and project-canon evidence classes into one truth status;
- automatically rank homepage content by graph centrality.

## Authority hierarchy

The project needs an explicit authority order so older contracts stop competing with newer ones.

### Whole-project architecture authority

`docs/POTATO-HOUSE-CONSTITUTION.md`

This remains the highest architectural constitution.

### Bounded-context authority

A new machine-readable Domain Room registry owns the list of canonical Rooms and their contracts.

### Public-routing authority

A new public surface registry owns stable public surface identities and routes.

### Knowledge authority

Existing canonical owner files continue to own substantive facts, interpretations, timelines, sources, and specialist material according to their current ownership rules.

### Projection/discovery authority

Generated indexes, manifests, sitemap-like resources, navigation projections, and `manifest.json` may expose the House but must not become substantive knowledge owners.

### Historical/donor authority

Older architecture specifications such as Root Navigation, World/Axis experiments, legacy atlas navigation, and retired homepage contracts remain historical or specialist donors unless explicitly promoted.

## Repository planes

The implementation follows the five repository planes already defined by the Constitution:

1. Knowledge House — durable Subjects, Assertions, Artifacts, Occurrences, Relations, Activities, Transitions, Contexts, Dossiers, Programmes, Collections, and research candidates.
2. Governance / Gardener — constitutions, schemas, registries, ownership rules, health constraints, migration/deprecation rules.
3. Operations / Forge — importers, normalizers, generators, migrations, validators, build and CI scripts.
4. Presentation / Fruit — public HTML, readers, maps, timeline, graphs, search/discovery, JSON-LD, CSS/JS.
5. Memory / Ash-Archive — superseded architecture, historic snapshots, legacy routes, retired generated states, and provenance-bearing residue.

Physical folders are implementation details. They do not define ontology by themselves.

## Domain Rooms

The machine-readable Room registry must encode the ten currently canonical Domain Rooms:

1. Potatoverse / Canon
2. Archive & Sources
3. Time & History
4. Traditions & Texts
5. Science & Formal Models
6. Life & Body
7. World Systems
8. Culture & Information
9. Works
10. Research Lab

A Domain Room is a bounded semantic ownership context, not necessarily a public page or directory.

Each Room contract must support:

- stable `id`;
- public-safe `title`;
- `purpose`;
- inclusion and exclusion rules;
- owned fact families;
- fact families that must never be owned there;
- supported durable primitive kinds;
- schema-extension references where present;
- epistemic policy;
- time policy;
- provenance policy;
- freshness/review policy;
- interfaces to other Rooms;
- allowed public surface types;
- validator references;
- lifecycle/migration status.

The registry is governance metadata. It does not duplicate the Room's substantive content.

## Recursive page/Room language

The project may continue using ordinary-language "room" as a metaphor for any navigable page or bounded information space, while reserving `Domain Room` for the ten canonical governance contexts.

This resolves the apparent contradiction between "every page feels like a room in the House" and "the House has ten canonical Rooms."

The public site can therefore feel like a house without creating thousands of independent governance authorities.

## Public surfaces

The public surface registry must declare stable identities for at least:

- Home `/`
- Tim Dooley `/tim-dooley/`
- Religion `/religion/`
- Philosophy `/philosophy/`
- Science `/science/`
- World `/world/`
- Timeline `/timeline/`
- Explore `/explore/`
- Sources / current canonical sources route
- World Map `/world-map/`
- Politics & Geopolitics `/politics/`
- North `/north/`
- World Systems `/world-systems/`
- Bible / current specialist Bible route if still live

Each public surface record must support:

- `id`;
- `route`;
- `surface_type`;
- `title`;
- `primary_parent` where applicable;
- `primary_room_ids` used by the surface;
- `status`;
- `visibility`;
- `canonical_route`;
- optional compatibility/legacy routes;
- whether the surface is allowed in primary navigation;
- whether the surface is an Explorer/View rather than an owner.

The registry owns route identity and public navigation status only. It does not own the facts shown on those pages.

## Public surface types

The initial public surface grammar is intentionally small:

### Home

Orientation and first choice only.

### Hub

Major entry points such as Tim, Religion, Philosophy, Science, World.

### Subject

A stable identifiable thing: person, place, concept, institution, text, event, biological structure, scientific model, work, etc.

### Guide / Dossier

A curated synthesis spanning multiple Subjects, claims, events, sources, or contexts.

### Explorer

A specialist representation such as World Map, Timeline, Bible comparator, graph/path explorer, search/discovery, or future House explorer.

### Evidence / Source

A provenance/audit surface for evidence lineage, source strength, captures, and claim support.

New public surface types require a demonstrated need. Do not create one merely because a backend object has a different kind.

## Primary public shell

The stable public primary navigation is:

- Home
- Tim
- Religion
- Philosophy
- Science
- World

Secondary global utilities are:

- Timeline
- Explore
- Sources

The five major homepage doors remain:

1. Tim Dooley
2. Religion
3. Philosophy
4. Science
5. World

The root homepage does not expose all ten Domain Rooms, all schema primitives, D1-D11, Spirit/Mind/Matter, World/Axis, or the repository tree.

## World hierarchy

World is the fifth primary public hub.

Under World, the canonical sibling lenses are:

- World Map
- Politics & Geopolitics
- North
- World Systems

World Map is a geographic Explorer, not the parent of North, Politics, or World Systems.

Primary navigation on Tim, Religion, Philosophy, Science, and other top-level hubs must link to World, not bypass it by linking directly to World Map.

Specialist pages may still link directly to World Map when the map itself is the relevant destination.

## Normal public page contract

The public page grammar must remain ordinary and reader-facing.

A compatible Subject or Hub page may render some subset of:

1. identity / title;
2. concise explanation or synthesis;
3. broader context;
4. related topics;
5. components, branches, applications, or consequences;
6. history/change;
7. evidence/sources;
8. other contexts;
9. specialist views;
10. next/deeper reading.

The UI labels should use ordinary language.

Internal directional semantics translate as follows:

- HERE / Plane → current page;
- WITHIN / Domain Room → category/context;
- UP / Mountain / North → broader context / larger synthesis;
- DOWN / Roots → history / evidence / sources / dependencies;
- OUT / Tree → parts / applications / consequences / branches;
- ACROSS / Road → related subjects;
- THROUGH / Door → ordinary link/continue/explore transition;
- STATE → status, maturity, evidence, lifecycle, freshness.

These are mapping rules for the engine, not required public labels.

## Door semantics for the web

Every ordinary hyperlink may be treated metaphorically as a local Door because it moves a reader into another information space.

The durable knowledge graph must distinguish that navigation metaphor from a stored `Transition` primitive.

A durable Transition record is required only when the underlying represented state/context actually changes in a meaningful modeled way.

Therefore:

- every Transition may be rendered through a link;
- not every link creates a Transition object.

This prevents the system from bloating merely because the public site contains many links.

## Identity address vs functional address

The House must allow an entity or concept to have a stable identity while participating in multiple functional projections.

Examples:

- Tim Dooley remains one stable Subject while Father, Gardener, House, Axis, Center, Seat, Peak-orientation, streamer, writer, and other roles are typed roles/relations rather than duplicate Tim identities.
- Son/Thomas may retain an embodied identity/history while Son/Jesus-as-Door is represented as a threshold/mediation function in a theological or symbolic projection.
- Denmark remains one geographic/political identity while appearing in World, North, economics, culture, timeline, and biography views.

Public URLs must prefer stable identity over mutable taxonomy.

## Information lifecycle and crystallization

The House needs a practical maturity model so raw material can accumulate without immediately becoming public canon.

The canonical first implementation uses these ordered states:

1. `raw` — unprocessed bulk material;
2. `captured` — material preserved with provenance;
3. `normalized` — stable object/claim/event identity or candidate identity has been established;
4. `reviewed` — ownership, epistemic class, and important contradictions have been checked;
5. `canonical` — accepted durable owner/record inside the House;
6. `synthesized` — multiple durable records have been combined into an understandable higher-level interpretation/dossier;
7. `publishable` — clear enough, sourced/typed enough, and context-safe enough for an ordinary public page;
8. `featured` — intentionally curated for prominent discovery such as a hub or homepage path.

Not every object should reach every stage.

An archived source may remain `captured` or `normalized` forever and still be valuable.

A public homepage item should almost always draw from `publishable` or `featured` material rather than raw research.

## Crystallization readiness

The architecture must support a machine-readable readiness record or generated readiness report with boolean or enumerated checks for:

- identity readiness;
- canonical ownership readiness;
- provenance/source readiness;
- epistemic classification readiness;
- contradiction/review readiness;
- synthesis readiness;
- public route readiness;
- stale/review-due status;
- homepage/hub candidacy as an editorial signal only.

Readiness is not truth ranking.

No single numeric score should decide whether a claim is true or whether a page belongs on the homepage.

Editorial prominence remains curated.

The first implementation plan does not need to implement the readiness report; it must only avoid schema or lifecycle choices that would block Wave 3.

## Raw → evidence → canon → synthesis → public data flow

The operational flow is:

`external/raw material → capture → Artifact/source → extraction → Assertion/Occurrence/Subject/Relation candidate → normalization → canonical owner → synthesis/Dossier → public projection → static page`.

Each step must preserve provenance links wherever the source material supports them.

Generated public pages are replaceable projections. Removing a generated page must never delete the canonical underlying knowledge.

## Public page projection contract

A page projection is a query/selection contract over House knowledge.

It may reference:

- canonical Subject ID;
- summary/synthesis owner;
- Domain Rooms involved;
- broader-context IDs;
- narrower/component IDs;
- related IDs;
- Occurrence IDs;
- evidence/source refs;
- specialist View refs;
- primary parent Hub;
- preferred next/deeper routes.

The projection must reference canonical IDs rather than copy complete durable records merely to simplify rendering.

A generated navigation projection may be disposable and rebuilt whenever the House changes.

Wave 1 needs only the route/topology fields required to classify existing major public surfaces. It does not need to build a general page-rendering engine.

## Initial page projection example

Conceptual example only:

```json
{
  "subject": "thalamus",
  "surface": "subject-thalamus",
  "parent": "science",
  "rooms": ["life-body", "science-formal-models"],
  "broader": ["diencephalon", "brain", "nervous-system"],
  "related": ["cortex", "hypothalamus", "pineal"],
  "history": [],
  "sources": ["artifact:..."],
  "specialist_views": ["potatoverse-thalamus-comparison"],
  "next": ["brain", "pineal"]
}
```

The corresponding public page may simply render sections such as "Overview", "Part of", "Related", "History", "Sources", and "Explore further".

## Topology ledger

The existing corpus placement work answers where repository material belongs.

A new topology ledger must answer how major durable/public objects connect.

The research-stage topology ledger must cover at least the following fields where applicable:

- stable identity;
- canonical owner;
- primary Domain Room;
- additional Domain Rooms used by Views;
- public surfaces;
- primary Hub;
- broader context;
- related identities;
- components/branches/applications;
- root/provenance dependencies;
- history/Occurrence IDs;
- specialist Views;
- compatibility/legacy routes;
- migration status.

The topology ledger is not itself a new content owner.

Its durable pieces should later become registries or generated indexes once proven.

Wave 1 topology scope is intentionally limited to current major public routes and their relationship to Domain Rooms, primary Hub, canonical route, surface type, and migration status. Deeper subject-level topology belongs to Wave 2 and later.

## Representative-object acceptance set

Before mass migration, the architecture must successfully normalize a deliberately diverse acceptance set:

1. Tim Dooley — person/public subject with many roles and mixed source classes;
2. Son / Jesus / Door — identity plus symbolic/theological transition function;
3. April 2025 Turning — historical/project Occurrence and synthesis anchor;
4. Yggdrasil — comparative mythological concept;
5. John 10 — textual source/comparative theological anchor;
6. thalamus — biological/anatomical Subject with symbolic comparison;
7. Denmark — country/geographic/institutional Subject;
8. one company — real-world organization inside World Systems;
9. one scientific equation/model — formal object with evidence/model boundaries;
10. one creative work — Works surface object;
11. Tree of Strife — project synthesis/model;
12. one raw source Artifact — evidence/provenance object not necessarily public-facing.

For every acceptance object, the system must eventually be able to identify or explicitly decline:

- identity;
- owner;
- Domain Room;
- epistemic state;
- time coordinates where relevant;
- provenance/source lineage;
- typed relations;
- public destination or explicit backend-only status;
- broader context;
- related material.

The full acceptance set is a precondition for mass subject migration, not a requirement for Wave 1 governance-skeleton completion.

If one object requires a new universal architecture merely to fit, investigate the modeling error before extending the universal kernel.

## Homepage contract

The homepage is editorial navigation, not a catalogue and not a generated dump of high-centrality nodes.

Its long-term anatomy is:

1. identity/hero;
2. five major gateways;
3. a very small "Start here" or recommended-path area if useful;
4. secondary Explore/Timeline/Sources access;
5. concise evidence boundary;
6. footer.

The first implementation wave does not need to redesign the homepage markup to match this anatomy if the current page already satisfies the five-gateway contract.

Homepage cards and paths must be intentionally selected from publishable/featured material.

## Hub contracts

### Tim Dooley

Primary job: biography, chronology, identity development, public record, works, mission/ideas, related concepts, and evidence boundaries.

Consumes chiefly from Potatoverse / Canon, Time & History, Archive & Sources, Works, Culture & Information, and relevant Traditions material.

### Religion

Primary job: explain Potatoism and compare it carefully with Christianity/Bible, Judaism, Islam, Norse and other traditions while preserving historical distinctions.

Consumes chiefly from Potatoverse / Canon, Traditions & Texts, Time & History, and Archive & Sources.

### Philosophy

Primary job: teach useful ideas through a coherent intellectual path rather than expose the backend ontology.

It is primarily a cross-Room interpretive/public guide, not automatically a separate governance Room.

### Science

Primary job: distinguish formalizable/testable models from analogy, symbolism, and speculation.

Consumes chiefly from Science & Formal Models, Life & Body, Archive & Sources, and Research Lab.

### World

Primary job: apply relationship-first thinking to observable real-world systems.

Consumes chiefly from World Systems, Time & History, Archive & Sources, Culture & Information, Research Lab, and relevant Programmes such as North.

## Explore contract

`/explore/` is the correct future home for deeper House-navigation interfaces.

It may progressively expose:

- browsing by Domain Room;
- Subject lookup;
- relation browsing;
- source/provenance browsing;
- timeline/history browsing;
- graph projection;
- Tree/Yggdrasil/Root projections;
- House health/inspector functions appropriate for public or developer audiences.

Old Root Navigation interaction ideas such as progressive disclosure, current path, expandable tree, dossier-in-place, and state persistence should be treated as Explore UX donors rather than root-homepage authority.

## Timeline contract

Timeline is a View over canonical Occurrences.

Occurrences own event facts. Timeline HTML/JSON does not become the canonical event owner.

The same Occurrence may appear on Tim, Religion, World, a Subject page, and Timeline without duplication of canonical event identity.

## World Map contract

World Map is a geographic View over World Systems knowledge.

A map feature should trace back to durable Subject/Relation/Occurrence IDs where the underlying data supports those concepts.

Geographic rendering never becomes the sole owner of country, company, infrastructure, political, economic, or programme facts.

## Search contract

Search is retrieval, not taxonomy.

Search results may cross all Domain Rooms and public surfaces, but a query must not create a new permanent ownership hierarchy.

Search should eventually return users to stable Subject, Hub, Guide, Explorer, or Evidence surfaces.

## Metadata policy

Public pages may carry machine metadata for:

- canonical ID;
- public surface ID;
- Room/context IDs;
- canonical owner path/ID;
- epistemic class/status;
- publication status;
- review/freshness state;
- relation IDs;
- source count or source refs where suitable;
- JSON-LD identity.

This metadata should remain mostly invisible in normal reading mode.

It exists for validation, discovery, related-navigation generation, machine readability, and maintenance.

## Existing manifest migration

`manifest.json`, `data/frontend-atlas-bridge.json`, `data/atlas-manifest.json`, discovery indexes, and other route/catalog files must not be deleted or redefined blindly.

The implementation plan must first inspect their current consumers.

Migration rule:

1. establish the new Room and Public Surface registries;
2. map current route/branch data into them;
3. validate equivalence/coverage where required;
4. update consumers to use the new authority or generated compatibility projection;
5. downgrade legacy manifests to compatibility/discovery roles only after they no longer contain unique authority;
6. preserve historical versions or architecture rationale where provenance matters.

`manifest.json` should converge toward generated discovery/compatibility rather than remain the whole-site constitutional source.

## House health / practical Swamp detection

The operational layer should eventually generate health findings for:

- orphan canonical Subjects;
- duplicate canonical ownership;
- public pages with no declared public-surface identity;
- dead or bypassing public routes;
- duplicated summaries that disagree;
- claims with missing source lineage where provenance is required;
- stale reviewed material;
- backend-only important material with no intentional public route;
- public pages relying on research-only material without appropriate labeling;
- global navigation bypassing World for primary-hub routing;
- generated files masquerading as owners;
- unresolved legacy navigation contracts.

This is the practical engineering interpretation of Swamp: unresolved entanglement, duplicate ownership, opacity, stale contradiction, blocked exit, and accumulated material that cannot yet participate cleanly in the current House.

## Validation requirements

The first-wave validators must fail when:

- a Room registry entry has a duplicate ID;
- a public surface has a duplicate ID or canonical route;
- a primary public route points to a missing surface;
- the five homepage gateways differ from Tim Dooley, Religion, Philosophy, Science, World;
- primary navigation on major hubs uses World Map instead of World as the fifth peer;
- a public surface references an unknown Room ID;
- an Explorer/View is marked as the canonical knowledge owner for its represented facts;
- a topology record references an unknown public surface or canonical identity where validation is possible;
- compatibility/legacy routes conflict with a canonical current route;
- generated output is required but its generator or source contract is missing;
- schema validation fails for the new registries.

Later-wave validators should add ownership/provenance/public-readiness checks as the corresponding registries become authoritative.

## Error handling and degradation

The site is static-first.

If optional navigation projection data fails to load, the page must retain its primary semantic HTML, heading structure, body content, and primary navigation.

JavaScript enhancement must not be required to discover the five major hubs.

Generated related/history/source blocks should fail closed: omit a broken optional block rather than fabricate a route or duplicate knowledge.

A validator should catch broken required registry references before deployment.

## Initial file family

The implementation plan should determine exact final paths by following existing repository conventions, but the intended responsibilities are:

- one canonical Room registry;
- one canonical public surface registry;
- schemas for those registries;
- one topology research/bridge index for current major routes;
- one crystallization/readiness model or generated report contract for a later wave;
- validator(s) for registry and public-shell integrity;
- shared navigation/projection helper(s) only when a concrete current consumer justifies them;
- updates to current top-level Hub markup/navigation only where necessary to use World consistently;
- documentation updates marking older whole-site navigation specs as superseded, historical, or Explore-specific where appropriate.

Avoid a giant `house.json` that combines governance, knowledge, routing, and generated projections in one file.

## Implementation waves

### Wave 1 — Governance skeleton

Deliver working machine-readable Room and Public Surface registries plus schemas and validators.

Classify all current major public routes.

Normalize primary World routing.

The visible homepage should remain functionally stable.

### Wave 2 — Public projection foundation

Create the smallest reusable projection/navigation contract that can feed ordinary public sections such as Broader context, Related, History, Sources, and Explore further.

Prove it first on Tim, then one radically different surface such as Science or a Subject page.

### Wave 3 — Crystallization/readiness

Add maturity/readiness records or generated reports so the project can distinguish bulk, evidence, canonical knowledge, synthesis, publishable material, and featured/editorial material.

Use this to create a Gardener work queue rather than exposing the internal score publicly.

### Wave 4 — Hub convergence

Convert Tim, Religion, Philosophy, Science, and World to consume shared public-surface/projection contracts while retaining semantic static HTML.

Reduce duplicate route and ownership definitions as each hub migrates.

### Wave 5 — Explore and specialist Views

Re-scope the strongest older root/tree/spatial-navigation ideas into Explore and specialist Views.

Ensure Timeline, World Map, Bible comparator, and future graph projections share canonical IDs rather than duplicate canon.

### Wave 6 — Homepage refinement

Only after destinations and contracts are stable, refine the root homepage if needed.

Keep it simple even if the House behind it becomes much richer.

## Implementation-plan decomposition

This document is an umbrella design. The next implementation plan must cover Wave 1 only.

Wave 1 is one independently testable subsystem: governance registries plus route topology and validation. It should finish with the existing public homepage intact and with a stable machine-readable contract that later work can consume.

Waves 2–6 are architectural direction, not permission to batch all remaining work into the first plan. Each later wave must be planned from the actual repository state produced by the prior wave. If a later wave changes public behavior or introduces a new subsystem, it receives the appropriate design/approval gate before implementation.

## Test strategy

The Wave 1 implementation plan must use test-first changes where practical and repository-appropriate.

Wave 1 tests must cover:

- schema validation for Room registry;
- schema validation for Public Surface registry;
- uniqueness of IDs/routes;
- exact five-homepage-gateway contract;
- primary-nav World route on major hubs;
- public-surface-to-Room reference integrity;
- topology reference integrity for the initial route set;
- static HTML fallback / critical links where existing site-shell tests support this;
- build/deploy artifact validation on the exact generated output where current workflow supports it.

Representative-object normalization belongs to later waves and should not block Wave 1 once the governance contracts are correct.

Do not use tests merely to snapshot large generated files. Prefer contract assertions that explain architectural intent.

## Migration strategy

Migration must be additive-first and reversible.

1. add registries and validators without deleting existing manifests;
2. map current public routes;
3. update one consumer at a time;
4. keep compatibility output while old consumers still exist;
5. verify no unique authority remains in a legacy contract before downgrading/removing it;
6. preserve historically meaningful files in Memory/Ash-Archive or clearly mark them superseded;
7. avoid mass renames/moves until ownership and projection contracts prove stable.

## Success criteria

The first implementation milestone succeeds when:

- the ten canonical Domain Rooms exist in a machine-readable registry;
- all major current public surfaces have stable machine-readable identities and canonical routes;
- Home, Tim, Religion, Philosophy, Science, World form one consistent primary shell;
- World Map, Politics, North, and World Systems are correctly represented as World lenses rather than primary peers of the five homepage hubs;
- schema/route validators pass;
- current homepage behavior remains reader-first and does not expose backend architecture;
- the topology ledger can describe the current major route set without creating duplicate canonical owners;
- older manifest/navigation contracts have explicit migration status instead of competing silently;
- the next implementation wave can build projection/navigation blocks without redesigning the ontology again.

The broader architecture succeeds when a new visitor can understand where to go in seconds, a curious reader can traverse the project deeply, a researcher can trace claims to evidence, a developer can identify ownership, and backend complexity continues to produce simpler rather than more confusing public presentation.

## Design invariants

These rules must survive implementation details:

1. One House, many Views.
2. Stable identities must not depend on mutable public taxonomy.
3. Public pages are projections, never sole owners of durable knowledge.
4. Domain Rooms govern bounded semantic ownership; they are not required public menu items.
5. The five primary homepage gateways remain Tim Dooley, Religion, Philosophy, Science, World.
6. World is the fifth Hub; World Map is a specialist Explorer under World.
7. Every ordinary link may function as a navigation Door without becoming a durable Transition object.
8. Historical provenance is preserved when architecture/content is superseded.
9. Archive/Root/Soil are not equivalent to Swamp; unresolved entanglement is what makes material Swamp-like.
10. Metadata and Potato terminology may remain hidden when ordinary reader language is clearer.
11. Generated projections may be deleted and rebuilt without destroying canonical knowledge.
12. No automatic centrality/readiness metric is allowed to stand in for truth or editorial judgment.
13. Semantic HTML owns the public meaning and critical navigation; JavaScript is enhancement.
14. The first implementation wave changes governance and routing contracts before attempting a large homepage redesign.
15. The system should become easier to read as it becomes richer internally.
