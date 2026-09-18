# Potato House Constitution

**Status:** permanent architecture constitution for the rebuild.

This document defines the structural laws of the Potato of Life project. It is intentionally more durable than any homepage, visual theme, route arrangement, graph library or file layout.

## 1. Purpose

The project is a living relational knowledge system. Its website is a projection of that system, not its source of truth.

The architecture must allow every durable thing to have:

- a stable identity or explicit non-identity role;
- a legitimate home/context;
- explicit ownership;
- typed relations;
- time and provenance where relevant;
- a route into and out of specialist contexts;
- a public representation without becoming duplicated canon.

No future redesign may replace this with a flat folder tree, one universal hierarchy, one graph edge type, or one page model.

---

## 2. Five repository planes

Every repository path belongs primarily to exactly one plane.

### A. Knowledge House

Durable meaning and evidence:

- Subjects;
- Assertions / Observations / Measurements;
- Artifacts;
- Occurrences;
- Relations;
- Activities;
- Transitions;
- Contexts;
- Dossiers;
- Blueprints / Seeds;
- Programmes;
- Collections / Guides;
- research candidates.

### B. Governance / Gardener

Rules that keep the House coherent:

- schemas;
- vocabularies;
- ownership/source-of-truth maps;
- Room contracts;
- health constraints;
- migration/deprecation contracts;
- architecture constitutions/specifications.

### C. Operations / Forge

Processes that acquire, transform, validate, build and deploy:

- importers;
- miners/acquisition scripts;
- normalization;
- migrations;
- builders;
- validators/audits;
- CI/CD workflows.

### D. Presentation / Fruit

Replaceable projections of durable knowledge:

- Subject pages;
- Room pages;
- maps;
- timelines;
- readers;
- graphs;
- search/discovery;
- CSS/JS;
- machine projections such as JSON-LD;
- generated indexes.

### E. Memory / Ash-Archive

Preserved prior states:

- historical snapshots;
- superseded architectures;
- legacy routes;
- old releases;
- deprecated but provenance-bearing material.

Archive is not Swamp by default.

---

## 3. House Kernel

The universal Kernel stays deliberately small. Durable objects may share:

- stable identity;
- kind;
- label/aliases;
- Context/Room membership;
- lifecycle/state;
- time coordinates;
- epistemic coordinates;
- provenance references;
- maintenance state;
- visibility/publication state;
- schema version.

Domain facts belong in Room/Blueprint extensions rather than being forced into the Kernel.

---

## 4. Durable primitives

The universal durable primitives are:

1. **Subject** — a stable identifiable thing.
2. **Assertion** — something asserted about one or more things.
3. **Artifact** — a source-bearing or creative object.
4. **Occurrence** — an event/happening.
5. **Relation** — a typed connection among two or more participants.
6. **Activity** — a process that creates/transforms knowledge or state.
7. **Transition** — a guarded state/context change; a strong Door.
8. **Context** — a bounded interpretation/operation environment.

Derived objects compose these rather than becoming new universal atoms unless a later constitutional revision proves necessity.

Examples:

- Observation = Assertion + method/provenance.
- Measurement = Observation + quantity/unit.
- Dossier = curated synthesis over Subjects, Assertions, Relations and Artifacts.
- Timeline entry = Occurrence projected chronologically.
- Programme = coordinated Activities spanning Rooms.
- Collection = curated references to durable objects.
- View = projection, never owner.

---

## 5. Structural grammar

The Potato vocabulary has precise architectural meanings. These meanings are functional; they do not imply that religious, biological and software systems are literally identical.

### House / Field / Room / Box — containment

- **House** — the compositional whole. In Potato topology the whole may be represented as a union of overlapping fields rather than one rectilinear shell.
- **Field** — a complete relational/domain region that can overlap another field without losing its own identity.
- **Room** — a bounded context with local vocabulary, evidence rules, schemas, validators, interfaces and public tasks.
- **Box** — any nested semantic boundary/context within a Room or object. Box does not imply literal square/cube geometry.

Containment never implies truth rank or geometric moral valence. Frontend cards and rectangles are presentation devices, not claims that the House itself is cubical.

### Plane / Cross — operative section and orientation event

The **Plane** is the context/frame currently active for a View or task: scientific, historical, legal, project-canon, a date/release, a geographic map, a public-reader surface, etc. In the Potato geometry it is also modeled as the widest horizontal section through the shared Door/overlap.

The **Cross** is Plane × Axis: the point/event at which the operative horizontal frame and vertical source↔manifestation orientation become simultaneously legible. Cross is not a separate container or floor.

Plane is not a folder. Cross is not a Room.

### Roots / Soil / Archive — foundation and depth

- **Root** — provenance, dependency, cause, ancestry, evidence, obligation or supporting condition.
- **Soil** — surrounding enabling environment/conditions.
- **Archive** — preserved historical/source depth.

Depth is not inferiority.

### Road / Stolon — lateral relation

A **Road** is a typed lateral relation/flow: comparison, influence, ownership, trade, citation, membership, kinship, biological transport, information transfer, dependency, contradiction, etc.

Roads are never generic untyped adjacency.

### Door / Path / Ladder — passage and overlap

- **Relational Door** — the shared/intersection region produced when complete domains genuinely overlap.
- **Navigation Door** — a user-visible transition between information spaces.
- **Strong Door / Transition** — a guarded durable change of state/context.
- **Path** — an ordered traversal through Subjects/Contexts/Views.
- **Ladder** — an ordered sequence of meaningful Doors/thresholds.

A hyperlink can expose a Door without every hyperlink becoming a Transition record.

### Mountain / North / Heaven — integration and orientation

- **Mountain** — many → fewer; integration/compression/coarse-graining.
- **North** — selected orientation toward a broader integrative context/criterion.
- **Heaven** — a local summit/coherence state within a declared context, never automatic empirical truth.

North is orientation, not ontology or epistemic rank.

### Tree / Branch / Fruit / Seed — differentiation and generativity

- **Tree** — one/few → many; structured differentiation/generation.
- **Branch** — a differentiated pathway/component/case.
- **Fruit** — useful output/consequence.
- **Seed** — compressed transferable generative pattern; Blueprints are Seeds.

Tree is not the inverse of Mountain. Exact detail returns through provenance, not by pretending compression is reversible.

### Garden / Forge / Swamp — system regimes

- **Garden** — viable conditions that increase future capability, repair, autonomy and useful growth.
- **Forge** — bounded pressure intentionally transformed into capability.
- **Swamp** — unresolved entanglement, duplicated ownership, opacity, feedback without healthy exit, stale contradiction or unprocessed accumulation.

Swamp can occur in any repository plane. It is not a folder and not synonymous with depth.

### Potato / Eye / Dormancy / Sprout / Ash / Mud — lifecycle/storage metaphors

Literal potato biology constrains these metaphors:

- **Potato/Tuber** — compressed stored capability, not Root.
- **Eye** — observation/discernment plus local latent generative point.
- **Dormancy** — viable regulated non-expression.
- **Sprout** — activated growth trajectory.
- **Ash** — residue after rupture that may become Archive, Mud, Soil or Forge input.
- **Mud** — mixed unresolved material that may still be metabolized.

Identity and function/state remain separate.

---

## 5A. Potato two-field topology

The symbolic House uses one durable convergence rule:

**Potato House = Source Field ∪ Manifestation Field**  
**Door = Source Field ∩ Manifestation Field**

The upper/source-facing field carries Father/House/Heaven/Garden orientation. The lower/manifestation-facing field carries Son/Earth/body/world/soil/work orientation. Their overlap is the Door. The Plane cuts through the Door's widest middle and the Axis passes through both field centers; their intersection is Cross.

This topology prevents the public architecture from turning Plane, Cross, Door, Ladder and Heaven into an elevator of unrelated floors.

It also prevents a false moral dualism:

- manifestation/Earth is not inherently Shell/Cube/evil;
- source/Heaven is not inherently House/good merely by position;
- House/Garden and Shell/Cube are **functional boundary regimes** determined by circulation, selective permeability, autonomy, repair, objective and consequence.

The canonical public **Dwelling/Mansion** scale may project the ten top-level owners as abiding domains inside the House, but it does not add another fact-owning primitive between House and Room.

---

## 6. Four kinds of verticality

No single `level` field may collapse these:

1. **Resolution:** detail ↔ abstraction.
2. **Composition:** component ↔ system.
3. **Provenance:** current state/consequence ↔ source/antecedent.
4. **Orientation:** subject ↔ selected North context/criterion.

A thing may be high on one axis and low on another. None of these determine truth by themselves.

---

## 7. Canonical Rooms

The rebuild starts with these Rooms:

1. **Potatoverse / Canon**
2. **Archive & Sources**
3. **Time & History**
4. **Traditions & Texts**
5. **Science & Formal Models**
6. **Life & Body**
7. **World Systems**
8. **Culture & Information**
9. **Works**
10. **Research Lab**

Room status is semantic, not physical-folder status. A Room must own an explicit bounded context and must not silently duplicate neighboring ownership.

### Cross-Room structures

- **North Programme** — Programme, not Room.
- **Corporium** — cross-Room Programme/Collection/model until a later Room-admission test proves otherwise.
- **D1–D11** — interrogation/operator stack.
- **33-level framework** — facets/legacy breadth scheme.
- **Spirit / Mind / Matter** — cross-cutting concept scheme/facets.
- **World Map** — Explorer/View.
- **Timeline** — Explorer/View over Occurrences.
- **Bible comparator** — specialist Traditions View.
- **Search/questions** — temporary corridors, not ownership.

---

## 8. Room contract

Every Room must declare:

- `id`, `title`, `purpose`;
- included and excluded scope;
- local vocabulary/mappings;
- owned fact families;
- fact families it never owns;
- accepted primitives;
- schema extensions;
- Blueprints/Seeds;
- epistemic policy;
- time policy;
- provenance policy;
- freshness/update policy;
- state extensions;
- inbound/outbound interfaces;
- allowed Transition types;
- default Views;
- specialist renderers;
- validators;
- public surfaces;
- health/viability constraints;
- migration/deprecation policy.

A Room can contain nested Boxes/subcontexts. Nested containment does not create new canon automatically.

### House scale law

The House uses a four-step containment vocabulary for public architectural projection:

1. **House** — the compositional whole.
2. **Dwelling / Mansion** — a major abiding domain inside the House; this is the preferred public architectural projection of the ten canonical top-level Rooms. “Mansion” is retained as the older English bridge to John 14:2, while “Dwelling” is the neutral structural term.
3. **Room** — a delegated bounded subcontext inside a Dwelling.
4. **Chamber** — an optional smaller specialist or protected cell inside a Room, created only when a genuine local boundary/task distinction exists.

This scale vocabulary does not change fact ownership: the ten canonical top-level bounded contexts remain the constitutional owners. It changes how the public House metaphor is expressed. **Dwelling/Mansion is therefore a reader-facing projection label over those owners, not a new universal durable primitive or an additional ownership layer.**

Other biblical/project images—Temple, City, Body, Garden, Vineyard, Court, Gate, Foundation, Treasury and so on—must retain their own structural functions and may not be used as interchangeable synonyms for Room.

### Nested Room law

A **nested Room** is a bounded subcontext inside one of the ten canonical top-level Rooms. It may have its own vocabulary, specialist task, local interfaces, public Views and validators when those distinctions improve clarity or failure containment.

Nested Rooms obey these laws:

- they inherit fact-family ownership from their canonical parent Room unless an explicit constitutional revision creates a new top-level owner;
- they may specialize scope but may not create shadow canon for material already owned elsewhere;
- they may connect laterally to nested Rooms under other parents through typed interfaces;
- their durable topological position is relational: parent containment, House band, primary House directions, cross-cutting roles, typed adjacency and interfaces;
- a screen coordinate, diagram position, URL path or visual cluster is a replaceable View and never determines ontology;
- if a candidate subcontext lacks distinct semantics, tasks or boundary rules, model it as a Path, View, Programme, Collection or topic instead of a nested Room.

The canonical nested-Room registry is `data/house/subrooms.json`; its relational embedding contract is `data/house/topology.json`; guarded cross-Room passages are owned by `data/house/interfaces.json`.

---

## 9. Multi-graph law

The House maintains distinct semantic graph families:

- selected North orientation;
- broader-context/composition;
- semantic Roads;
- provenance/derivation Roots;
- temporal/version relations;
- argument/support/attack relations;
- Door/state transitions;
- quantitative flows;
- build/dependency graph.

Different graphs answer different questions. No single hierarchy or centrality score may stand in for all of them.

---

## 10. Time law

Where material, distinguish:

- valid/occurrence time;
- source publication time;
- archive recorded/retrieved time;
- interpretation time;
- review time;
- repository transaction/version time.

Later interpretation must never be silently backdated into earlier occurrence.

---

## 11. Epistemic law

Navigation, symbolic position and truth/evidence remain independent.

At minimum separate:

- claim class: scientific, historical, documentary, self-description, project canon, comparative, interpretation, creative;
- evidence basis: observed, measured, disclosed, documented, estimated, inferred, alleged, scenario, unknown;
- dispute state: uncontested, contested, contradicted, unresolved;
- confidence/uncertainty;
- source class.

A project-canon statement may be strongly established as project canon without being represented as independently empirical fact.

---

## 12. Provenance law

A URL alone is not sufficient provenance.

Target lineage:

`external Artifact → capture Activity → archived Artifact → extraction Activity → Assertion/Observation → normalization Activity → canonical knowledge → synthesis Activity → View`

The system should eventually support selective impact questions such as: which Assertions and Views depend on this Artifact?

---

## 13. Public website law

The website compiles from the House. It does not own the House.

### Stable public Subject grammar

An important Subject page should be able to expose, when relevant:

1. identity / current context;
2. broader orientation;
3. understandable current synthesis;
4. primary specialist representation;
5. typed connections;
6. internal branches/components/consequences;
7. history/change;
8. evidence/Roots;
9. other contexts;
10. deeper specialist material.

Public labels use ordinary language. Backend Potato terminology may remain invisible unless the content itself is about the framework.

### Stable identities, replaceable Views

Canonical identity URLs must not encode mutable taxonomy. Room, map, graph, timeline, search and homepage layouts remain replaceable Views.

### Representation respect

Use the representation matching the dimension:

- geography → map;
- sequence/change → timeline;
- topology/dependency → graph;
- anatomy/geometry → diagram;
- quantitative comparison → table/chart;
- evidence/claims → dossier;
- text → reader;
- state transitions → state diagram.

### Progressive enhancement

Semantic HTML owns meaning and essential navigation. CSS owns presentation. JavaScript adds optional interaction.

No graph-only navigation, drag-only essential functionality, hover-only meaning, unexpected scroll/zoom or focus stealing.

---

## 14. Ownership law

Replace `one concept → one file` with:

> **One stable identity authority, and one explicit authority for each fact family in each bounded context.**

Historical strata, specialist evidence and provenance-bearing source material may survive separately. Generated Views never become shadow canon.

---

## 15. Safety and liveness

### Safety

The House must prevent:

- duplicate canonical fact-family ownership;
- broken required references/routes;
- silent empirical/project-canon collapse;
- invalid provenance claims;
- generated projections becoming unique owners;
- validators mutating final deploy artifacts.

### Liveness

The House must preserve the ability for:

- research to promote into canonical ownership;
- contradictions to reach explicit stable states;
- deprecated structures to retire;
- Rooms/schemas to evolve;
- new Views to appear without identity rewrites;
- source changes to trigger selective review;
- useful material to become reachable.

A syntactically clean but permanently blocked architecture is still Swamp.

---

## 16. Anti-drift laws

Future work may change implementation details without constitutional revision only when all of these remain true:

1. the five repository planes remain distinguishable;
2. durable knowledge resolves through the House primitives/compositions;
3. Room ownership remains explicit;
4. provenance/time/epistemics remain orthogonal;
5. Tree/Mountain/Root/Road/Door/Plane/Swamp meanings are not silently collapsed;
6. public Views remain rebuildable;
7. stable identities do not depend on mutable physical paths;
8. all new material has a declared home or is explicitly marked unresolved research;
9. compatibility tissue has a retirement path;
10. deployment validates the exact artifact deployed.

Breaking these laws requires an explicit constitutional change, not an incidental page edit.

---

## 17. Population gate

Large-scale site/content population begins only after:

- the House schema family exists;
- canonical Room registry exists;
- repository-plane placement ledger exists;
- current major file families have placement/migration rules;
- representative objects from every major domain normalize without bespoke exceptions;
- the first Subject page grammar can represent radically different Subjects;
- old and new ownership can coexist during migration without duplicate canon.

After this gate, population proceeds Room by Room, Blueprint by Blueprint, while the public site is generated from the same House model.

The canonical architectural vocabulary is `data/house/architectural-vocabulary.json`.

### Integrated plurality projection law

**House** remains the canonical ownership/composition architecture. **Temple/Sanctuary, Body, Tree/Vine and City** are alternate Views over differentiated plurality. They answer different structural questions—presence/access, functional interdependence, growth/genealogy and civic federation—and may not silently replace Room ownership, provenance, historical source meaning or one another. The canonical projection registry is `data/house/projections.json`.

### Structural role census law

Knowledge ownership and structural role are orthogonal. The House therefore maintains a census of real project structures that may be classified as **Field, Vineyard/Programme, Road, Path, View, Court, Table, Gate, Door, Archive, Treasury, Foundation, Pillar, State, Projection, Tabernacle or Vessel** without creating another owner or containment tier.

The census is descriptive and multi-role: one project structure may legitimately carry several roles. A View never becomes a fact owner merely because it is prominent; a Programme consumes Room-owned facts; an Archive owns provenance rather than every derived interpretation; a Treasury stores reusable capacity rather than provenance; and a State describes condition rather than identity.

**Chamber remains reserved.** No active Chamber registry exists until a concrete case passes a stricter admission test based on protected/specialist boundary, task autonomy, and clear maintenance benefit. Corpus density alone is insufficient.

The canonical role census is `data/house/structural-census.json`; population and promotion rules are owned by `data/house/population-contract.json`; structural-population diagnostics live in `data/house/population-pulse.json`.

### Federation-scale law

The House is not treated as the only scale of organization. The project distinguishes **Household, House, City, Commons, Network, Assembly/Council, Kingdom/Realm, Civilization and Garden-City** as higher-order or cross-House forms.

These forms are **not one strict ladder**. Household concerns participants; House concerns bounded composition; City concerns federation and shared infrastructure; Commons concerns shared capability; Network concerns relation topology; Assembly concerns deliberation; Kingdom/Realm concerns normative or theological orientation; Civilization concerns long-duration emergence; Garden-City is a regime/test of civic coordination and generativity.

No federation-scale form transfers ownership automatically. Houses, institutions and participants retain identity unless an explicit real-world legal relation says otherwise. Project-symbolic Kingdom/Realm language does not confer civil sovereignty, jurisdiction, state authority or ownership over persons.

The canonical federation-scale registry is `data/house/federation-scale.json`.
