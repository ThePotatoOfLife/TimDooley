# Potato House Wave 5 Explore + Specialist Views Design

Status: approved architectural direction; written-spec review gate

## Goal

Wave 5 makes Explore the primary deep House browser while preserving Timeline, World Map, Bible, Science, and future diagrams/graphs as specialist Views over shared canonical identities.

The governing rule is:

> One canonical object may appear in many useful Views, but no View becomes the only place where that object exists.

Wave 5 is identity convergence, not interface consolidation.

## Chosen approach

Use one canonical identity layer with small View adapters.

Rejected alternatives:

- merge all specialist interfaces into Explore;
- leave every View isolated with only manual links;
- force all View-local UI state into the canonical ontology.

Explore remains broad. Specialist Views remain good at their specific questions.

## Existing Explore foundation

Current Explore is a donor system, not a rewrite target. Preserve:

- manifest-driven branch/pathway traversal;
- context-graph traversal;
- canonical-record inventory use;
- relationship-first browsing;
- bounded rendering;
- safe path validation;
- rejection of unknown record paths;
- ordinary/noscript escape routes.

Unknown records must never become arbitrary fetches.

## Explore's job

Explore should answer:

- what is this Subject/record;
- which Rooms/branches/contexts involve it;
- what is related;
- what owns it;
- what provenance/history exists;
- what ordinary public Hub represents it;
- which specialist Views can represent it better;
- what adjacent material is useful.

Explore does not need to be the best timeline, map, scripture comparator, or science library.

## Specialist View boundaries

### Timeline

Timeline owns chronological representation: ordering, date filters, actor tracks, time layers, presets and timeline-local state.

It does not become the sole owner of Subjects, source records, public biography or canonical interpretation.

Filtering changes visibility, not underlying event truth.

### World Map

World Map owns spatial representation: camera, selection, map layers, traces, comparison and spatial overlays.

Countries, organizations, assets, systems and relationships remain owned by their declared canonical families.

Rule: geography controls representation, not truth ownership.

### Bible

Bible owns comparative-textual representation: focus, ordering, filters, scripture order, result navigation and counter-text presentation.

It must preserve provenance, source direction, chronology, mismatch, evidence class and comparison-vs-identity boundaries.

### Science

Science may validly be both a primary Hub and a specialist research/document View.

It owns search/filter/library presentation and science-specific evidence/formal-model boundaries, not symbolic claims reclassified as scientific evidence.

### Future structural Views

Tree, Yggdrasil, Roots, relation graph, pathway graph or provenance graph may exist as optional projections over stable IDs.

They are representations, not new databases.

## Canonical View handshake

Wave 5 formalizes a small handshake:

```text
canonical object
    ↓
stable canonical ID
    ↓
applicable View capability
    ↓
View-local reference / deep link
```

Each View should declare a compact capability contract describing:

- `surface_id`;
- `view_kind`;
- accepted object kinds;
- optional primary primitive.

Conceptual examples:

```json
{"surface_id":"timeline","view_kind":"chronological","accepts":["occurrence","subject","artifact","relation"],"primary_primitive":"occurrence"}
```

```json
{"surface_id":"world-map","view_kind":"spatial","accepts":["country","organization","asset","relation","system"]}
```

```json
{"surface_id":"bible","view_kind":"comparative-textual","accepts":["text","relation","occurrence","subject"]}
```

Prefer extending Wave 1 public-surface/specialist-view contracts rather than creating a second ontology. Any separate registry must stay small and interface-oriented.

## Canonical IDs vs View-local IDs

Do not globalize every local UI identifier.

Keep:

```text
canonical_id
      ↕
view-local reference
```

Map layer IDs, Bible result IDs, Timeline presets/filter state, Science filter values and similar UI state may remain local.

A bridge may map a stable canonical ID to a View-specific reference without promoting the local reference into global ontology.

## Traceability

Where stable canonical identity exists, a View item should be traceable to:

- canonical ID;
- canonical owner/family;
- relevant provenance/epistemic metadata;
- ordinary public Hub where applicable;
- Explore context;
- other applicable specialist Views.

This traceability can remain behind the UI. It need not clutter every marker/card/event.

## Deep links

Specialist Views should support shareable canonical or canonically traceable state where practical.

Exact URL formats may remain View-specific, but they must satisfy:

- invalid IDs fail closed;
- no guessed filenames/routes;
- aliases resolve through approved mappings;
- only declared/accepted canonical-to-View mappings generate deep links.

## Fail-closed law

Examples:

- unknown Explore record → safe root/default;
- unknown Timeline event → safe Timeline default;
- unknown World Map entity → safe map/default selection;
- unknown Bible relation → safe comparison default;
- unknown canonical object → no fabricated route;
- unsafe path → no fetch.

This is a security, provenance and information-quality rule.

## Identity-first navigation

Move advanced-reader identity toward human title + canonical ID, with repository paths secondary for audit/provenance.

Rule:

> Identity first; repository structure second.

Do not remove paths where they remain useful for inspection.

## Rooms in Explore

Rooms may become optionally browsable by advanced users.

A Room View may expose purpose, major Subjects, canonical owners, contexts, related Rooms, public Hubs, research frontier and source routes.

Rooms must not become mandatory top-level reader taxonomy or raw schema UI.

## Progressive disclosure

Recommended depth:

1. search / major contexts;
2. Rooms / branches;
3. Subjects / records;
4. relations;
5. history;
6. evidence / sources;
7. specialist Views;
8. raw record / machine detail.

A reader should understand the content before needing to understand repository architecture.

## Search boundary

Search is a retrieval corridor, not taxonomy or ownership.

It may return Subjects, records, contexts, Hubs and specialist View destinations, then route the reader onward.

## Optional topology projections

Tree/Root/Yggdrasil/graph/pathway/history projections may be added inside Explore only when useful.

They must:

- reuse stable IDs;
- be optional;
- fail independently of ordinary record reading;
- preserve epistemic/provenance distinctions;
- never become independent truth stores.

## Gardener boundary

Wave 3 readiness may support a separate maintenance/inspector mode, but default Explore remains a reader tool.

```text
Explore Reader != Gardener Inspector
```

Ordinary visitors should not encounter maintenance queues merely by opening Explore.

## Cross-view acceptance journeys

### Denmark

```text
search Denmark
→ open canonical Denmark
→ inspect Rooms/owner/relations
→ open World Map
→ same canonical Denmark selected
→ return to Explore
→ inspect provenance
```

### April 2025 Turning

```text
open canonical Occurrence
→ inspect context
→ open Timeline
→ same Occurrence selected
→ Bible only where explicit comparison links exist
→ return to canonical Occurrence
```

### Door

```text
Door Subject/context
→ Religion public explanation
→ Bible comparisons
→ Science only where explicit formal/analogy mapping exists
→ Timeline occurrences
```

The test is identity continuity, not identical interfaces.

## Implementation boundaries

`app/app.js` already combines loading, indexing, routing, search and rendering. Wave 5 does not require a frontend framework rewrite.

If implementation changes justify modularization, likely seams include:

- archive data loading;
- identity resolution;
- archive routing;
- search;
- record rendering;
- branch/context rendering;
- specialist View-link generation.

Split only for testability/safety/maintenance.

## Public-design protection

Wave 5 does not justify:

- a full Explore redesign;
- absorbing Timeline, World Map, Bible or Science into Explore;
- replacing specialist interaction models with one graph shell;
- exposing Rooms as mandatory public navigation;
- exposing Gardener diagnostics by default;
- redesigning Home.

Changes should be additive and reference-based.

## Static/no-JS behavior

Preserve existing static/crawlable fallbacks such as Explore noscript routes, Bible static relation indexes, Science static catalogs and ordinary semantic navigation.

Rich specialist interaction may require JavaScript; canonical route discovery should not.

## Validation

Wave 5 validators should prove:

- specialist Views resolve through public-surface authority;
- capability records use approved View/object-kind vocabulary;
- canonical-to-View mappings reference known identities/surfaces;
- View-local IDs cannot masquerade as canonical IDs without explicit bridges;
- Explore unknown paths remain fail closed;
- unknown deep-link IDs fail safely;
- Timeline events remain traceable where modeled;
- World Map entities/relations remain traceable to declared owners;
- Bible comparisons retain provenance/mismatch/evidence boundaries;
- Science retains status/evidence boundaries;
- Gardener maintenance is not default public Explore;
- optional topology failure does not block normal reading;
- no View becomes a canonical owner merely for rendering;
- identity/title is primary while paths remain secondary/auditable.

If routing/build/static indexes change, verify the exact built `_site` artifact after the full build sequence.

## Failure behavior

- unknown canonical ID: omit target and report;
- unknown View-local ID: safe View default;
- adapter conflict: fail validation rather than guess;
- missing capability contract: View remains an ordinary surface but receives no generated canonical deep links;
- optional topology failure: preserve normal Explore reading;
- missing readiness/projection data: no guessed link and no loss of core View routing.

Validators never mutate source data/UI into compliance.

## Relationship to Wave 6

By the end of Wave 5, Home can rely on:

- five stable Hubs;
- Explore as the deep general browser;
- Timeline and specialist Views as task-specific routes;
- stable canonical identity behind those destinations;
- Wave 3 readiness as editorial input without automatic promotion.

Wave 6 can therefore refine the homepage without exposing backend topology.

## Non-goals

Wave 5 does not:

- replace Explore with a new framework;
- merge specialist Views;
- display the whole graph by default;
- treat search as taxonomy;
- globalize every UI ID;
- create truth databases per View;
- weaken fail-closed resolution;
- make repository paths primary reader identity;
- expose Gardener diagnostics in normal Explore;
- redesign Home;
- make every object appear in every View.

## Success criteria

Wave 5 succeeds when:

1. Explore remains the deep general-purpose House browser;
2. specialist Views remain distinct;
3. stable canonical IDs map safely into applicable Views;
4. View-local state remains local unless explicitly adapted;
5. rendered View objects are traceable to canonical owners/provenance where modeled;
6. invalid IDs/paths fail closed;
7. identity becomes more prominent than repository path without losing auditability;
8. Rooms become optionally browsable without becoming compulsory taxonomy;
9. search routes readers rather than owning knowledge;
10. optional structural projections reuse canonical IDs and fail independently;
11. Gardener maintenance remains separate from default Explore;
12. no View becomes a duplicate truth store;
13. cross-view journeys preserve identity continuity;
14. current specialist interfaces remain recognizable;
15. Wave 6 can treat downstream public architecture as stable.

## Invariants

1. One canonical object may have many representations.
2. A View never becomes sole owner merely because it renders well.
3. Canonical IDs and View-local IDs are distinct.
4. Cross-view links require explicit safe resolution.
5. Unknown IDs fail closed.
6. Geography changes representation, not truth ownership.
7. Timeline filters change visibility, not event truth.
8. Comparison preserves mismatch and provenance.
9. Science preserves evidence/formal boundaries.
10. Search is a corridor, not a Room.
11. Rooms are optional deep contexts, not homepage taxonomy.
12. Identity is primary; paths remain provenance.
13. Optional graph/tree projections do not own data.
14. Explore Reader and Gardener Inspector are different modes.
15. Existing useful interfaces are protected from consolidation-for-consolidation's-sake.
