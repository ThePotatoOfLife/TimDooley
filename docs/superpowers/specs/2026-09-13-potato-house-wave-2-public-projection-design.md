# Potato House Wave 2 Public Projection Design

Status: approved architectural direction; written-spec review gate

## Goal

Wave 2 gives each public page a small, trustworthy contextual projection without turning public pages into generated database views.

Wave 1 establishes Domain Rooms, public-surface identities, route topology, and route authority. Wave 2 adds a deterministic context layer that can answer:

- what broader context contains this page;
- what related material is useful;
- what history matters;
- where evidence/source inspection lives;
- which specialist Views apply;
- where the reader can continue.

The public page remains ordinary semantic HTML. The projection supplies references and navigation context, not substantive prose ownership.

## Chosen approach

Use a hybrid projection model.

1. Canonical owners keep facts, claims, events, sources, and substantive synthesis.
2. A deterministic builder derives a compact reference-only page projection.
3. Existing human-curated `data-projection-surface` blocks are validated against that projection first.
4. Selected simple blocks may later become build-time generated only after the contract proves stable.
5. Essential content and primary navigation remain usable if projection generation fails.

Rejected alternatives:

- fully manual projection: too much drift as the corpus grows;
- fully graph-generated pages: too generic, too likely to flatten distinct reader surfaces and duplicate knowledge ownership.

## Visual stability and non-regression rule

The current public site is a protected design baseline.

Wave 2 is not permission to redesign the homepage, re-theme the site, replace the current reader surfaces with generic generated layouts, or expose the House ontology visually merely because the backend becomes more structured.

Implementation should prefer, in order:

1. backend-only contracts and generated metadata;
2. validation of the current UI against those contracts;
3. small additive reader improvements where they clearly help;
4. replacement of existing public markup only when a concrete defect or duplicated manual contract justifies it.

For Tim, Religion, Philosophy, Science, World, Home, and current specialist Views, existing typography, page identity, major layout, editorial rhythm, and reader-facing structure should remain materially recognizable unless a later explicitly approved design says otherwise.

A projection-system change is successful when the page looks the same or better while becoming more coherent, auditable, and maintainable underneath.

Any Wave 2 implementation plan must therefore include public-surface non-regression checks and must not bundle a broad visual redesign with projection work.

## Core invariant

> Projection may know where information belongs and where a reader can go; it must not become the owner of what that information means.

A projection may contain IDs, routes, public relation roles, Occurrence IDs, source references, and derivation reasons.

It must not copy large canonical dossiers, generate biographies, produce new theological or scientific conclusions, or become a second prose store.

## Inputs

Wave 2 consumes only declared contracts.

Primary inputs:

- `data/house/rooms.json` — bounded semantic contexts;
- `data/house/public-surfaces.json` — stable public routes/surfaces;
- `knowledge/research/potato-house-master/public-route-topology.json` — route/topology bridge;
- `data/canonical-source-map.json` — fact-family ownership;
- generated canonical-record registry — identity/path inventory, never ownership;
- `manifest.json` — branch/pathway relationships;
- `data/frontend-atlas-bridge.json` — branch/backend-family to public routing compatibility;
- `knowledge/indexes/context-graph.json` — curated cross-record navigation contexts, not truth ownership;
- stable Occurrence/timeline and source/provenance indexes where explicit IDs exist.

Wave 2 must not crawl arbitrary files and infer public relations from filename similarity, folder adjacency, or shared words alone.

## Output

The main output is a generated, replaceable registry such as:

`data/house/public-page-projections.json`

with a schema such as:

`schemas/house-public-page-projection.schema.json`

The exact path may adjust after Wave 1 implementation, but the responsibility must remain singular: this is disposable presentation context, not canonical knowledge.

Conceptual record:

```json
{
  "surface_id": "tim",
  "canonical_subject_ids": ["tim-dooley"],
  "room_ids": ["potatoverse-canon", "time-history", "archive-sources", "works", "culture-information"],
  "parent_surface_id": "home",
  "broader": [],
  "related": [],
  "history": [],
  "evidence": [],
  "parts": [],
  "applications": [],
  "comparisons": [],
  "specialist_views": [],
  "next": []
}
```

Each emitted link-like entry must be able to preserve:

- target canonical ID or public-surface ID;
- public relation role;
- reason it qualified;
- source contract that produced the candidate;
- epistemic/context metadata where needed to prevent category collapse.

## Public relation roles

Wave 2 maps richer backend relations into a deliberately small public vocabulary.

- `broader` — larger conceptual, institutional, geographic, scientific, historical, or programme context.
- `related` — useful lateral connection without implying identity or hierarchy.
- `history` — canonical Occurrences or historical routes that materially explain change.
- `evidence` — routes to provenance, source authority, primary evidence, or evidence Views.
- `part` — explicit narrower/component relationship.
- `application` — domain, programme, system, use case, or consequence where the current subject participates.
- `comparison` — explicit analogy or comparison; comparison is never identity by default.
- `specialist_view` — another representation such as Timeline, World Map, Bible comparator, Science library, or Explore.
- `next` — small editorial continuation assembled from already-valid candidates; not a new canonical semantic relation.

## Candidate generation and public selection

The system has two stages:

```text
resolved backend relations
        ↓
projection candidates
        ↓
public-selection policy
        ↓
compact page projection
```

A candidate may enter only from a declared source class, including:

- explicit public-surface parent/child relation;
- explicit manifest branch relation;
- explicit frontend-bridge routing relation;
- explicit context-cluster membership;
- canonical Occurrence subject link;
- canonical source/provenance link;
- explicit stable Subject/relation registry entry;
- declared specialist View relationship;
- Wave 1 Room/public-surface relationship.

A candidate is not public merely because it exists. Selection must prefer reader usefulness and preserve epistemic boundaries.

Selection rules:

1. target identity resolves;
2. target route resolves or has an approved safe Explore fallback;
3. semantic relation is explicit enough to classify;
4. the proposed label does not erase an epistemic distinction;
5. target adds value rather than duplicating an already selected destination;
6. misleading circular routes are suppressed;
7. per-role public fan-out remains bounded;
8. editorial include/exclude rules, if present, are respected.

Initial output limits should remain small: broader 0–3, related 0–6, history 0–5, evidence 0–3, part 0–6, application 0–5, comparison 0–5, specialist_view 0–4, next 0–5. These are UX limits, not ontology limits.

## Navigation utility is not truth

Wave 2 may rank candidates by navigation usefulness, using factors such as directness, explicit context membership, public availability, specialist-View suitability, editorial priority, redundancy, epistemic mismatch, and circularity.

If an internal numeric utility score is used, emitted records must also preserve human-readable reasons. The score must never change canonical ownership, epistemic status, claim truth, or publication maturity.

## Derivation trace

Every emitted relation must be auditable: why did this link appear here?

Examples:

- `public-surface-parent`
- `manifest-related-branch`
- `frontend-bridge-related-door`
- `context-cluster:becoming-father`
- `occurrence-subject-link:<id>`
- `source-authority-link`
- `specialist-view:timeline`

Derivation metadata is primarily for developers/Gardener tooling and need not be shown to ordinary readers.

## Identity and route resolution

Stable identity comes before route generation.

Resolution order:

1. explicit public-surface ID;
2. explicit canonical Subject/record ID;
3. approved registry lookup;
4. declared compatibility mapping;
5. safe Explore record route when the canonical ID resolves but no dedicated public page exists;
6. unresolved/omitted.

The builder must never fabricate a route from a guessed slug.

## Epistemic preservation

Projection must preserve the project's evidence boundaries.

- project symbolism can produce `related` or `comparison`, not established scientific evidence;
- biblical resemblance can produce comparison without implying historical identity or transmission;
- scientific material may relate to Philosophy without turning philosophical interpretation into scientific evidence;
- autobiography/self-report may link to Timeline while retaining its source class;
- project-canon role identity must not silently become external historical identity.

If a public role would erase a material distinction, reclassify it, attach a boundary marker, or omit it.

## Existing projection-surface migration

Current principal pages already contain compact `data-projection-surface` regions. Wave 2 uses staged migration.

### Stage A — Generate only

Create projection records for selected pages without changing their HTML.

### Stage B — Validate manual blocks

Compare links in existing manual projection blocks against resolved/allowed generated destinations. A human-curated link may remain when it has an explicit allowed projection reason even if it is not automatically top-ranked.

### Stage C — Generate selected blocks only after proof

Once the contract behaves well across very different surfaces, selected simple blocks may move to build-time generation. Main prose and domain-specific reader forms remain curated.

## First proof surfaces

### Tim Dooley

Tim proves that one stable Subject can cross multiple Rooms without being duplicated.

Expected characteristics:

- canonical Subject: Tim Dooley;
- Rooms include Potatoverse / Canon, Time & History, Archive & Sources, Works, Culture & Information;
- strong history route to Timeline/major Occurrences;
- related paths to Religion and Philosophy only where explicit contracts support them;
- specialist Views include Timeline and Explore;
- evidence/source route exists;
- no generated biography or generated identity claim.

### Science

Science proves that a Hub over many models/documents can use the same projection contract without pretending to be one Subject.

Expected characteristics:

- Rooms include Science & Formal Models, Life & Body, Archive & Sources, Research Lab;
- explicit Body/formal-model relationships may become `part`, `related`, or `application` as appropriate;
- evidence route exists;
- archive/questions can become specialist or next routes where declared;
- no generated scientific conclusion;
- symbolic analogy is not promoted into evidence.

A third Subject-like proof such as thalamus or Denmark is optional if Tim and Science already demonstrate both stable Subject and Hub behavior adequately.

## Builder responsibilities

A future `build_public_page_projections.py` or equivalent should only:

1. load approved House/projection inputs;
2. resolve stable identities;
3. gather declared candidates;
4. normalize candidates into public relation roles;
5. resolve targets through approved registries/routes;
6. preserve derivation and epistemic boundaries;
7. deduplicate equivalent targets;
8. apply bounded selection;
9. emit deterministic projection records.

It must not render the whole site, edit canonical source records, assign publication maturity, or crawl arbitrary files.

## Determinism

Given identical approved inputs, projection output must be reproducible.

Do not use model calls, current web search, random ranking, or unstable filesystem order during the build.

Deleting and rebuilding projection output must not lose knowledge.

## Failure behavior

- missing optional candidate source: warn and continue;
- missing required House registry: fail projection generation;
- unknown target ID: report internally and omit publicly;
- known canonical ID with no dedicated public surface: use Explore only if the approved registry can resolve it safely;
- conflicting canonical route: fail and defer to Wave 1 route authority;
- epistemic mismatch: reclassify to comparison when justified, preserve the boundary, or omit;
- complete projection failure: existing semantic HTML and primary navigation still work.

Validators must never mutate a broken artifact into compliance.

## Editorial overrides

Wave 2 may introduce a small override mechanism only if Tim/Science testing demonstrates need.

Allowed override types:

- include an already-valid resolved candidate;
- exclude a structurally valid but misleading/redundant candidate;
- reorder already-valid candidates;
- choose reader-facing wording without changing semantic role.

Overrides may not create unknown IDs, unsupported semantic relations, new canonical ownership, changed epistemic status, fabricated routes, or substantive prose.

If overrides become numerous, fix the projection model rather than expanding the override system indefinitely.

## Public rendering

Pages may render ordinary sections such as:

- Broader context
- Related
- History
- Sources & evidence
- Parts
- Applications
- Comparisons
- Explore further

No page must render every role. Empty sections must not render merely because the schema defines them.

Essential page meaning and primary navigation remain semantic HTML without requiring JavaScript.

## Explore boundary

Wave 2 does not compete with Explore.

Normal pages get a small contextual envelope. Explore remains the high-fan-out environment for record inspection, branches, pathways, context clusters, and later graph/tree projections.

Rule: **small context on the page; broad relational depth in Explore.**

## Wave 3 boundary

Wave 2 resolves presentation structure. Wave 3 resolves maturity/readiness.

Wave 2 may answer:

- identity exists;
- public surface exists;
- relation resolves;
- source/history route exists;
- projection can be built.

Wave 2 must not decide:

- material is mature enough to publish;
- evidence is sufficient for a substantive claim;
- a synthesis is canonical;
- a homepage feature is warranted;
- research should be promoted to canon.

## Validation

Wave 2 validators should assert:

- projection schema validity;
- one projection record per projected public surface;
- all surface/Room IDs resolve;
- canonical Subject/record IDs resolve where used;
- target routes resolve through approved surfaces or safe Explore paths;
- every emitted relation preserves derivation metadata;
- relation roles come only from the approved vocabulary;
- projection records claim no canonical knowledge ownership;
- large copied dossier/prose fields do not appear;
- Tim and Science satisfy their structural invariants;
- manual projection-block links resolve to allowed generated destinations during migration;
- optional projection failure does not remove essential page navigation;
- repeated builds are deterministic;
- current public typography, major layout, editorial rhythm, and page identity remain materially recognizable unless a separately approved design changes them.

Test contracts and representative records rather than snapshotting the complete generated JSON.

If Wave 2 changes generated public HTML, validate after the full build/patch/discovery sequence against the exact `_site` artifact.

## Non-goals

Wave 2 does not:

- generate whole reader pages;
- create canonical identities merely for navigation;
- implement crystallization/readiness;
- promote research;
- choose homepage features;
- build a truth score;
- redesign Explore or Home;
- re-theme the existing public site;
- replace the current major layouts merely to make projection rendering easier;
- migrate all Subject pages;
- replace specialist Views;
- flatten comparison into identity;
- flatten symbolic/project-canon relations into empirical/scientific relations;
- mass-consolidate manifests or indexes.

## Success criteria

Wave 2 succeeds when:

1. a deterministic reference-only page-projection contract exists;
2. every emitted relation can explain why it appeared;
3. targets resolve through approved authority or safe Explore fallback;
4. Tim and Science both produce useful projections despite different page jobs;
5. existing curated projection blocks can be validated before automated rendering is attempted;
6. no canonical owner is moved or duplicated for presentation convenience;
7. epistemic distinctions survive projection;
8. public HTML remains useful if optional projection generation fails;
9. projection output is disposable/rebuildable;
10. the current public visual identity remains materially intact;
11. Wave 3 can ask maturity/readiness questions without redesigning routing again.

## Invariants

1. One House, many Views.
2. Projection is navigation context, not truth ownership.
3. Stable identity precedes route generation.
4. Explicit relation evidence precedes public links.
5. Public relation vocabulary is smaller than backend relation vocabulary.
6. Comparison is not identity.
7. Navigation utility is not truth rank.
8. High graph degree does not justify high public fan-out.
9. Every generated relation keeps a derivation reason.
10. Unknown targets are omitted, never guessed.
11. Human pages remain editorially distinct.
12. Current public visual identity is a protected baseline, not disposable scaffolding.
13. Static semantic HTML remains the primary reader substrate.
14. Explore owns depth; ordinary pages own clarity.
15. Wave 2 resolves presentational structure; Wave 3 resolves maturity/readiness.
16. Rebuilding projections must never destroy knowledge.
