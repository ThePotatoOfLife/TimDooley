# Potato House Six-Wave Roadmap

Status: companion roadmap for `2026-09-13-potato-house-public-crystallization-design.md`; written-spec review gate

## Purpose

This roadmap decomposes the approved Potato House public-crystallization architecture into six sequential implementation waves. It is intentionally broader than the first implementation plan and narrower than the Constitution.

The goal is to see the whole road before changing runtime architecture while still implementing one independently testable subsystem at a time.

The governing rule is:

> **Do not rebuild what already works. Promote, clarify, connect, validate, and retire duplication only after consumers have moved.**

The public result remains a normal website. The sophistication belongs in ownership, metadata, synthesis, routing, provenance, and generated projections underneath it.

## Existing foundation to reuse

The roadmap starts from the repository as it exists on 2026-09-13 rather than from a greenfield design.

Existing assets that remain useful include:

- `docs/POTATO-HOUSE-CONSTITUTION.md` — permanent architecture constitution.
- `data/canonical-source-map.json` — current canonical fact-family ownership map.
- `data/canonical-record-registry.json` — generated inventory of record-like IDs and source paths; discovery aid, not ownership authority.
- `data/repository-spine.json` — internal Spirit/Mind/Matter classification coordinate; not public navigation.
- `manifest.json` — relationship-first branch/pathway map and current archive navigation input.
- `data/frontend-atlas-bridge.json` — current backend-to-frontend projection contract, already using Tim/Religion/Philosophy/Science/World as the five public doors.
- `data/backend-coverage-map.json` — backend owner/consumer/status inventory.
- `data/atlas-manifest.json` — internal backend/data manifest and retired-public-contract ledger.
- `knowledge/indexes/context-graph.json` and other indexes — current contextual navigation layers.
- `app/app.js` / `/explore/` — current fail-closed deep archive reader.
- `scripts/build_site.py` — current static/crawlable page generator.
- `scripts/build_discovery.py` and related discovery/SEO builders.
- existing validators for reader surfaces, public projection, generated navigation, Explore reachability, source-of-truth, architecture, content integrity, public navigation, and final site shell.
- `.github/workflows/quality-checks.yml` — existing exact-head quality workflow into which House checks must integrate rather than compete.

These are donor systems and current contracts. The House architecture may clarify which one owns which concern, but it must not duplicate their useful information under new names without a migration reason.

## Dependency chain

The six waves form one dependency chain:

```text
Wave 1: Governance / route authority
        ↓
Wave 2: Page projection / contextual navigation
        ↓
Wave 3: Crystallization / Gardener readiness
        ↓
Wave 4: Hub convergence
        ↓
Wave 5: Explore + specialist Views
        ↓
Wave 6: Homepage editorial refinement
        ↓
Continuous Gardener loop
```

Each wave must leave the repository deployable and useful. No wave is allowed to require all later waves before the website works.

---

# Wave 1 — Governance Skeleton and Route Authority

## Goal

Give the House a machine-readable governance skeleton without redesigning the public website.

Wave 1 establishes explicit authority for Domain Rooms and public surfaces, classifies current major routes, eliminates remaining primary-navigation drift, and adds validators that make those decisions durable.

## Why this wave comes first

The repository already has substantial content, public hubs, a deep Explorer, canonical ownership maps, generated record indexes and routing bridges. What is still missing is a small constitutional machine contract saying:

- what the ten Domain Rooms are;
- what the stable public surfaces are;
- how major public surfaces relate to Rooms and parent hubs;
- which route is canonical when several historic routes exist;
- which existing manifest/bridge remains authoritative during migration.

Without that, later projection and crystallization work risks inventing another parallel navigation layer.

## Inputs reused

- `docs/POTATO-HOUSE-CONSTITUTION.md`
- `knowledge/research/potato-house-master/rooms-and-boundaries.md`
- `knowledge/research/potato-house-master/corpus-placement-index.json`
- `data/frontend-atlas-bridge.json`
- `data/backend-coverage-map.json`
- `data/atlas-manifest.json`
- `manifest.json`
- existing top-level HTML reader surfaces
- current public and site-shell validators

## New durable contracts

Recommended family:

```text
data/house/rooms.json
data/house/public-surfaces.json
schemas/house-room-registry.schema.json
schemas/house-public-surface-registry.schema.json
knowledge/research/potato-house-master/public-route-topology.json
```

Exact paths may adjust to repository conventions during the Wave 1 implementation plan, but responsibilities must remain separate.

### `rooms.json`

Owns only Domain Room governance identity and contract references.

It must not become a content database.

### `public-surfaces.json`

Owns stable public surface IDs, canonical routes, surface type, public parent, primary Room references, visibility/navigation status and compatibility routes.

It must not own the prose or facts rendered at those routes.

### Route topology ledger

Research/bridge-level mapping of current major public surfaces to canonical surface ID, Room participation, parent Hub, specialist-view status and migration state.

It is a migration aid, not a new knowledge owner.

## Migration relationship to existing projection files

`data/frontend-atlas-bridge.json` remains live during Wave 1.

Wave 1 must not abruptly replace it because `build_site.py`, public projection validation and generated navigation already rely on it.

The new public-surface registry becomes the clearer route-identity authority. Existing bridge data continues as the branch/backend-family projection and compatibility contract until a later wave can derive or validate it against the new registry.

`manifest.json` remains the relationship/pathway archive map.

`data/repository-spine.json` remains an independent internal classification coordinate.

`data/canonical-source-map.json` remains ownership authority for existing data families.

## Public changes

Minimal.

The current homepage remains visually and structurally stable.

Normalize peer navigation on current primary hubs so the fifth peer is **World**, not **World Map**. Specialist/contextual links to the World Map remain valid where the map itself is intended.

Known examples at the design snapshot include Tim, Religion, Philosophy and Science top navigation.

## Validators

Add a focused House-governance validator rather than duplicating all existing public validators.

It should prove:

- Room registry schema validity;
- exactly ten canonical Domain Room IDs;
- public-surface registry schema validity;
- unique public-surface IDs and canonical routes;
- all Room references resolve;
- five primary public Hubs are Tim, Religion, Philosophy, Science and World;
- World Map is a specialist View under World, not the fifth peer;
- current major routes have topology entries;
- compatibility routes do not collide with current canonical routes;
- no Explorer/View is declared a canonical substantive knowledge owner;
- current primary hub nav links to World as a peer;
- existing bridge/manifest relationships remain covered rather than silently orphaned.

Integrate this into `quality-checks.yml` before the public build/projection gates.

## Exit criteria

Wave 1 is complete when:

- all ten Rooms have machine-readable governance records;
- all current major public surfaces have stable IDs/routes;
- the primary public shell is consistent;
- current bridge/manifest contracts have explicit migration roles;
- House governance validation passes;
- existing public/build/discovery validators still pass;
- homepage behavior remains reader-first and essentially unchanged;
- later waves can reference stable surface and Room IDs without inventing them again.

## Explicitly deferred

No automatic Related/History/Sources rendering.

No crystallization scoring/report.

No mass subject migration.

No Explore redesign.

No homepage redesign.

---

# Wave 2 — Public Projection Foundation

## Goal

Create one deterministic, reference-based page-context projection that can answer ordinary navigation questions without making the page itself a knowledge owner.

The first useful projection questions are:

- What larger context is this part of?
- What is related?
- What history matters?
- What evidence/source route supports it?
- What specialist View exists?
- Where can the reader go next?

## Architectural rule

Wave 2 generates navigation/context **from canonical references**. It does not generate the main explanatory prose and does not invent facts.

A projection is disposable output.

## Inputs reused

- Wave 1 Room registry
- Wave 1 Public Surface registry
- route topology ledger
- `data/canonical-source-map.json`
- `data/canonical-record-registry.json`
- `manifest.json` branch relations/pathways
- `knowledge/indexes/context-graph.json`
- `data/frontend-atlas-bridge.json`
- existing `data-projection-surface` reader sections
- `scripts/build_site.py`

## Proposed output contract

A generated projection registry such as:

```text
data/house/public-page-projections.json
```

with a schema such as:

```text
schemas/house-public-page-projection.schema.json
```

A projection record should be small and reference-oriented:

```json
{
  "surface_id": "tim",
  "canonical_subject_ids": ["tim-dooley"],
  "room_ids": ["potatoverse-canon", "time-history", "works"],
  "parent_surface_id": "home",
  "broader": [],
  "related": [],
  "history_refs": [],
  "source_refs": [],
  "specialist_surface_ids": ["timeline", "explore"],
  "next_surface_ids": []
}
```

The exact relationship fields may be richer where evidence exists, but the first implementation should remain narrow.

## Builder

Create one deterministic builder rather than hand-maintaining projection JSON.

Conceptually:

```text
scripts/build_public_page_projections.py
```

It should read current House/public/manifest/context contracts and emit reference records.

If a relation cannot be resolved safely, omit or mark it unresolved; never guess.

## First proof surfaces

Prove the model on two deliberately different surfaces:

1. **Tim Dooley** — person/history/works/project identity with mixed evidence classes.
2. **Science** — library/hub with formal models, documents and strict analogy/evidence boundaries.

A later Subject proof can use thalamus, Denmark or another acceptance object once Subject-page generation is ready.

## Relationship to existing manual projection sections

Current hubs already contain compact `data-projection-surface` blocks.

Wave 2 should first validate that these human-curated blocks are consistent with generated projection data.

Only after that contract proves useful should rendering move toward build-time generation.

This avoids converting nuanced reader pages into generic templates prematurely.

## Public changes

Small and ordinary.

Possible generated or validated blocks use labels such as:

- Broader context
- Related
- History
- Sources
- Explore further

Backend labels such as UP/DOWN/ACROSS/THROUGH remain implementation vocabulary.

Semantic HTML remains complete without JavaScript.

## Validators

Prove:

- every projection references known public surfaces/Rooms/canonical IDs where applicable;
- generated projections contain references rather than copied canonical records;
- no projection becomes a canonical owner;
- unresolved references fail closed;
- Tim and Science projection blocks match the generated contract;
- generated static topic/record pages can still route to the right human parent;
- optional projection failure does not remove primary semantic navigation.

## Exit criteria

Wave 2 is complete when:

- one deterministic projection builder exists;
- two radically different reader surfaces successfully consume or validate against it;
- canonical owners remain unchanged;
- generated projection data can be deleted/rebuilt without information loss;
- the model is demonstrably useful enough to expand to Subject pages without another universal schema rewrite.

---

# Wave 3 — Crystallization and Gardener Readiness

## Goal

Turn the project's informal sense of "bulk → idea → canon → synthesis → public" into an auditable workflow.

This wave gives the Gardener a queue: what is mature, what is blocked, what is stale, and what would create the most useful next public improvement.

It does **not** create a numeric truth score.

## Lifecycle vocabulary

Use the approved lifecycle:

```text
raw
→ captured
→ normalized
→ reviewed
→ canonical
→ synthesized
→ publishable
→ featured
```

Not every object must advance through all states.

## Inputs reused

- `data/canonical-source-map.json`
- generated canonical-record inventory
- repository/source-of-truth audits
- Wave 1 Room/surface registries
- Wave 2 projections
- provenance/epistemic metadata already present in domain records
- research frontier and project workflow files
- duplicate/orphan/coverage audits

## New policy and report contracts

Recommended separation:

```text
data/house/crystallization-policy.json
scripts/build_crystallization_report.py
```

Generated output:

```text
data/house/crystallization-report.json
```

The policy defines states and readiness dimensions.

The report is generated and replaceable.

## Readiness dimensions

Use explicit checks rather than one scalar score:

- identity resolved;
- canonical owner resolved;
- Room/context resolved;
- provenance sufficient for the claim class;
- epistemic class explicit;
- contradiction/dispute state handled where relevant;
- synthesis owner exists where needed;
- public parent/surface resolved;
- public copy safe/clear enough where a public projection exists;
- review/freshness state;
- blocking reason(s).

Editorial prominence remains human-curated.

## Representative acceptance set

Use the twelve-object acceptance set from the umbrella design:

- Tim Dooley;
- Son / Jesus / Door;
- April 2025 Turning;
- Yggdrasil;
- John 10;
- thalamus;
- Denmark;
- one company;
- one scientific equation/model;
- one creative work;
- Tree of Strife;
- one raw source Artifact.

The point is not to force identical schemas. The point is to prove the House can tell what each object is, where it belongs, what owns it, what state it is in and what prevents or enables public use.

## Gardener queue

Generate actionable categories such as:

- publishable but no public route;
- synthesis exists but ownership unresolved;
- important canonical record missing provenance;
- public page exists but source lineage weak;
- duplicate owner conflict;
- stale high-value public synthesis;
- raw/captured material with strong likely merge target;
- projection route exists but canonical ID missing.

No automated promotion occurs solely because a check passes.

## Public changes

Normally none.

This is primarily an internal maintenance/intelligence wave.

At most, existing pages may gain better source/status metadata once a record is explicitly promoted.

## Validators

Prove:

- lifecycle values are from the approved vocabulary;
- report references known records/owners/surfaces;
- generated readiness does not overwrite source records;
- no numeric truth rank controls publication;
- the twelve acceptance objects have explicit results or explicit justified non-applicability;
- generated report is deterministic enough for CI comparison/invariants without snapshotting the whole file.

## Exit criteria

Wave 3 is complete when the project can answer, for representative material:

> What is this, who owns it, how mature is it, what supports it, where could it appear publicly, and what specifically blocks the next step?

That is the operational meaning of crystallization.

---

# Wave 4 — Hub Convergence

## Goal

Make the five major public Hubs consume the same route/projection authority while preserving their distinct editorial voice and specialist functions.

The result should feel more coherent to readers without making every page look identical.

## Hubs

- Tim Dooley
- Religion
- Philosophy
- Science
- World

## Architectural rule

Shared structure should be generated or validated.

Domain-specific prose and meaningful page forms remain curated.

For example:

- Tim can remain biographical/developmental;
- Religion can remain comparative/theological;
- Philosophy can remain a reader journey;
- Science can remain a searchable research library;
- World can remain a gateway into specialist lenses.

Do not flatten these into a universal card grid merely because they share metadata.

## Inputs reused

- Wave 1 public-surface/Room registries
- Wave 2 public projections
- Wave 3 readiness output
- current reader-first HTML
- existing `validate_reader_surfaces.py`
- current frontend bridge
- static build tooling

## Shared shell responsibilities

Promote the following into one source of route truth where practical:

- primary Hub navigation;
- current-surface identity;
- parent/global utility routes;
- compact deeper navigation data;
- machine metadata for surface/Room/canonical references.

Prefer build-time generation or validation over runtime JavaScript for essential navigation.

## Reusable public information blocks

Where the data supports them, use ordinary sections:

- Related
- Broader context
- History
- Sources & evidence
- Explore further

Blocks should only appear when meaningful.

No empty universal scaffolding.

## Migration of existing contracts

By this point, enough consumers may use the House surface/projection contracts that parts of `frontend-atlas-bridge.json` can become generated compatibility output rather than unique authority.

Do this only after inspecting consumers.

`manifest.json` may likewise retain pathways/branch semantics while route identity comes from the public-surface registry.

Do not retire either merely for conceptual neatness.

## Public changes

Visible coherence improves:

- primary navigation stops drifting;
- deeper links become consistently named;
- common metadata/related sections behave similarly;
- domain-specific content remains intact.

## Validators

Extend existing reader-surface tests to prove:

- every Hub resolves through the public-surface registry;
- shared nav uses canonical routes;
- projection blocks reference valid projection records;
- static semantic HTML still contains essential navigation;
- main editorial content was not replaced by raw generated backend fields;
- no Hub duplicates canonical data solely to satisfy the renderer.

## Exit criteria

Wave 4 is complete when:

- all five Hubs share one route authority;
- common navigation/context data is generated or validated from the House;
- reader-specific content remains high quality;
- legacy route definitions are no longer unique authorities where migration is complete;
- all existing page/build/discovery gates remain green.

---

# Wave 5 — Explore and Specialist Views

## Goal

Let advanced users see more of the hidden organism without moving that complexity onto the homepage.

Explore becomes the main deep House browser. Specialist interfaces remain specialized Views over the same canonical IDs.

## Existing system to preserve

`/explore/` already loads the manifest, context graph and canonical-record inventory, and it already rejects unknown record paths before fetching.

That fail-closed behavior must survive.

Wave 5 enriches Explore; it does not discard it for a new graph app.

## Explore capabilities

Progressively support:

- browse by Domain Room;
- Subject/record lookup;
- branch/pathway browsing;
- typed relation browsing;
- provenance/source browsing;
- history/Occurrence browsing;
- search as temporary corridor;
- optional topology projections such as Tree/Yggdrasil/Roots;
- developer/maintenance House-health views where appropriate.

The exact interface should use progressive disclosure rather than display every graph simultaneously.

## Donor ideas

Useful ideas from older root/spatial navigation work can be promoted here:

- current path;
- expandable tree;
- dossier-in-place;
- persistent state;
- breadcrumb/context awareness;
- relation-aware traversal.

Those ideas are Explore UX donors, not root-homepage authority.

## Specialist Views remain distinct

Do not merge these into Explore merely because they share IDs:

- Timeline — chronological View over Occurrences;
- World Map — geographic/spatial View over World Systems;
- Bible comparator — textual/comparative Traditions View;
- Science library — research/document View;
- future diagrams/graphs — task-specific representations.

A specialist View earns existence when its representation matches the question better than a generic dossier.

## Canonical traceability requirement

Where underlying canonical identity exists, a View item should be traceable back to:

- stable canonical ID;
- owner/source path or owner family;
- relevant epistemic/provenance metadata;
- other public surfaces if available.

The View itself never becomes the only owner.

## Technical evolution

If `app/app.js` becomes too large to reason about safely, split modules by responsibility while preserving the same public contract.

Do not perform a framework rewrite solely for modularity.

## Validators

Prove:

- Explore Room/record references resolve through approved registries;
- requested record paths remain fail-closed;
- specialist View records trace to canonical IDs where available;
- Timeline still does not own Occurrence truth;
- World Map still does not own country/system truth;
- Bible comparator retains source/mismatch boundaries;
- optional topology projections can fail without blocking normal record reading;
- no repository file tree leaks into public navigation as a required mental model.

## Exit criteria

Wave 5 is complete when a curious/research reader can traverse the archive deeply by context, relation, history and evidence while the top-level website remains simple.

---

# Wave 6 — Homepage Editorial Refinement

## Goal

Refine the homepage only after its destinations, route authority, projections and maturity workflow are stable.

The current homepage is already close to the target and may require only restrained changes.

## Governing rule

The homepage is an editorial threshold, not the visualization of the entire House.

More backend sophistication should make the homepage easier, not denser.

## Stable anatomy

Keep:

1. project identity / hero;
2. concise project purpose and evidence boundary;
3. exactly five major gateways: Tim Dooley, Religion, Philosophy, Science, World;
4. a very small set of optional curated "Start here" paths if they add real value;
5. quiet access to Explore/Sources and, if useful after testing, Timeline;
6. footer/machine-discovery metadata.

## Editorial path selection

A Start-here path may be suggested by Wave 3 readiness but must be intentionally curated.

Examples might include:

- Who is Tim Dooley?
- What is the Potato of Life?
- How is the world connected?

Do not select homepage material merely because a node has high graph degree or because a file is large.

## What does not belong on the homepage

- giant House graph;
- visible Room registry;
- raw metadata dashboard;
- D1-D11 controls;
- full Vesica explanation unless editorially chosen as content;
- repository directory tree;
- dozens of topic cards;
- automatic "most connected" content;
- backend lifecycle labels.

## Machine/discovery integration

Homepage structured data, machine index and discovery files should consume stable public surface IDs/routes rather than maintain another independent list.

The visible page remains hand-readable semantic HTML.

## Testing

Test:

- exactly five gateway routes;
- natural questions remain clear;
- no backend terminology leaks into primary navigation;
- mobile layout remains readable;
- machine index/sitemap/JSON-LD agree with current canonical surfaces;
- all curated Start-here routes are publishable and resolve;
- built artifact matches source contract after all post-build patches.

## Exit criteria

Wave 6 is complete when a first-time visitor can understand the major choices almost immediately, every choice leads into a stable mature destination, and the homepage is no more complicated than it was before the House became richer.

---

# Continuous Gardener Loop After Wave 6

The six waves create architecture; they do not finish the knowledge project.

Afterward, ordinary growth follows a continuous loop:

```text
capture source / new material
→ classify and preserve provenance
→ resolve identity and owner
→ normalize
→ connect typed relations
→ synthesize where useful
→ evaluate readiness
→ project into public surfaces when warranted
→ validate exact built artifact
→ review / prune / archive superseded projections
→ repeat
```

## Rules for future growth

A new source does not go directly to the homepage.

A new public page gets a stable surface/Subject identity and resolves to canonical ownership.

A new specialist View references canon rather than copying it.

A generated projection may be deleted and rebuilt.

Old material may become Archive/Ash without being deleted when provenance remains valuable.

Research can remain research indefinitely without being treated as failed content.

A contradiction becomes typed data rather than silently overwritten.

## Practical House-health / Swamp signals

Periodic health reports should surface:

- duplicate ownership;
- orphan records;
- stale or conflicting canonical summaries;
- dead routes;
- public pages with missing owner/source references;
- important publishable material with no intentional public route;
- research material accidentally presented as established fact;
- generated Views that became unique owners;
- compatibility contracts with no remaining consumer but no retirement decision;
- opaque blocks that cannot explain why they are not promotable.

Swamp is unresolved entanglement, not simply a large archive.

---

# Cross-Wave Non-Negotiables

Every wave must preserve these laws:

1. The public site remains a normal semantic website.
2. The House owns knowledge; public pages project it.
3. Stable identities survive View and taxonomy changes.
4. `data/canonical-source-map.json` remains existing ownership authority unless a deliberate migration replaces a specific family contract.
5. The canonical-record registry remains an inventory/discovery aid unless explicitly promoted by a later approved design; it does not silently become ownership authority.
6. Domain Rooms do not replace `repository-spine.json`; they answer a different bounded-context/ownership question.
7. World is the fifth primary Hub; World Map is a specialist View.
8. Explore is the deep interactive reader; no second competing root reader is introduced.
9. Timeline, map, Bible and graph Views remain distinct representations when their dimensions differ.
10. Project canon, autobiography, interpretation, comparative research, historical evidence and scientific evidence remain epistemically typed.
11. No single hierarchy, centrality score, level number or readiness number becomes a proxy for truth.
12. Semantic HTML owns essential meaning/navigation; JavaScript enhances.
13. Migration is additive-first and reversible until consumers have moved.
14. CI validates the exact deploy artifact, not merely source files.
15. Increasing backend complexity should result in equal or lower public cognitive load.

# Review and implementation boundary

This roadmap works out all six waves at architectural level.

It is **not** one implementation plan and is not approval to execute all six waves in one batch.

After written-spec approval:

- create a detailed implementation plan for Wave 1 only;
- implement and verify Wave 1;
- inspect the new repository state;
- write/approve the next wave's implementation design/plan at the appropriate level of change;
- continue sequentially.

This preserves the full destination while preventing later-wave assumptions from overriding evidence learned during earlier implementation.
