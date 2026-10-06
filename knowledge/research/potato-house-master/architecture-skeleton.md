# Potato House — Architecture Skeleton

**Status:** research design; non-canonical.

This file defines the smallest current candidate skeleton that the whole project can populate without forcing every domain into one schema or one navigation tree.

## 1. Five layers

### Layer A — House Kernel

Shared coordinates that almost every durable object can use:

- stable identity;
- state/lifecycle;
- context;
- time;
- epistemic state;
- provenance pointer;
- maintenance state;
- visibility/publication state.

The Kernel must stay small. Domain-specific facts do not belong here merely because they are important.

### Layer B — Durable Primitives

Current candidate primitives:

1. **Subject** — enduring identity: person, place, organization, concept, object, work, system, biological structure, text, etc.
2. **Assertion** — something asserted about one or more Subjects/Relations/Occurrences.
3. **Artifact** — source-bearing object: file, post, dataset, document, image, recording, text, publication.
4. **Occurrence** — event/happening with participants and time.
5. **Relation** — typed connection among two or more participants.
6. **Activity** — process that creates/transforms knowledge: capture, extraction, translation, normalization, synthesis, publication, migration.
7. **Transition** — Door: guarded state change.
8. **Context** — environment/bounded interpretation space in which vocabulary and rules apply.

Derived/specialized objects should normally compose these rather than create new universal atoms.

Examples:

- Observation = Assertion + method/measurement/provenance.
- Measurement = Observation + quantity/unit.
- Dossier = curated compressed View/product over Subjects + Assertions + Relations + Artifacts.
- Timeline entry = Occurrence projected into chronological View.
- Claim dossier = Assertions + argument/evidence graph.
- Programme = mission/workflow spanning Rooms.
- Collection = curated grouping, not owner.

## 2. Graph family

The House must not pretend one graph answers every question.

`G = {T_N, E_B, E_R, E_P, E_T, E_A, E_D, E_F, E_build}`

- `T_N` — selected North orientation tree/arborescence.
- `E_B` — additional broader-context/part-of/classification relations.
- `E_R` — semantic Roads: influence, comparison, membership, ownership, dependence, etc.
- `E_P` — provenance/derivation Roots.
- `E_T` — temporal/version/predecessor/successor relations.
- `E_A` — argument graph: support, attack, qualify, contradict.
- `E_D` — Door/state-transition graph.
- `E_F` — quantitative/typed flows where valid: money, energy, goods, attention, authority, care, data, people.
- `E_build` — implementation dependency/rebuild graph.

These are semantic layers; they do not require separate databases.

## 3. Four verticalities

Do not collapse every up/down relation into one altitude.

1. **Resolution** — detail ↔ abstraction.
2. **Composition** — component ↔ larger system.
3. **Provenance** — consequence/current state ↔ source/antecedent.
4. **Orientation** — subject ↔ selected North criterion/context.

A source may be deep in provenance but concrete in abstraction. A nation may be high in composition but not epistemically superior to a measurement. Altitude never determines truth.

## 4. Direction grammar

### Up

- Mountain: compress/integrate many into fewer.
- Compose: component → system.
- North: move toward selected orientation.
- North-of-North: examine the criterion by which orientation was chosen.

### Down

- Decompose: system → components.
- Root: trace provenance/cause/dependency.
- Expand: Tree → cases/branches/applications.
- Enter: Room/subject → internal detail.

### Sideways

- semantic Roads;
- comparison;
- context switching;
- peer relations;
- cross-Room interfaces.

The UI may make several of these look like navigation, but the backend must retain the distinction.

## 5. Tree family

The word Tree currently names several different functions. Keep them separate:

- **World Tree / Yggdrasil comparator** — connective scaffold/topology across differentiated regions.
- **Tree operator** — differentiation/generation: fewer → many.
- **Tree of Life** — viable/generative/healing regime and fruit.
- **Tree of Knowledge** — epistemic branching resource; knowledge can feed different downstream regimes.
- **Tree of Strife** — project-defined recurrent destructive/low-exit branching regime.
- **Roots of Strife** — conditions/incentives feeding that regime.
- **Roots of Ash** — residue after rupture that may become Mud, Archive, Forge input or Soil.

Connectivity, generativity and viability are independent dimensions.

## 6. State model

Identity must not encode role/state. Use orthogonal state coordinates where possible:

- lifecycle: latent | active | mature | senescing | historical;
- maintenance: healthy | review_due | wounded | repairing | stale | deprecated | historical;
- publication: internal | candidate | public | withdrawn;
- ownership: raw | specialist | canonical | derived;
- dispute: uncontested | contested | contradicted | unresolved;
- visibility: public | partial | internal | unknown;
- research: unresearched | queued | active | reviewed | closed;
- viability: viable | constrained | blocked | unknown.

Rooms may extend these but should not replace common meanings silently.

## 7. Time model

At minimum distinguish where material:

- valid/occurrence time — when it happened/applied;
- publication time — when a source was published;
- recorded/retrieved time — when the archive captured it;
- interpretation time — when a later interpretation was formed;
- review time — when it was last checked;
- system transaction/version time — when repository state changed.

Do not backdate later interpretation into earlier occurrence.

## 8. Epistemic coordinates

Do not overload one `epistemic_class` field with several different questions.

Candidate coordinates:

### Claim class

scientific | historical | documentary | self_description | project_canon | comparative | interpretation | creative

### Evidence basis

observed | measured | disclosed | documented | estimated | inferred | alleged | scenario | unknown

### Dispute state

uncontested | contested | contradicted | unresolved

### Confidence

high | medium | low | unknown, or justified quantitative uncertainty where valid.

### Source class

primary | official | academic | archival | journalistic | conversation | project | technical | statistical | other

Navigation, symbolic altitude and epistemic strength remain independent.

## 9. Provenance / Root model

A source link alone is insufficient. Target chain:

`external Artifact → capture Activity → archived Artifact → extraction Activity → Assertion/Observation → normalization Activity → canonical knowledge → synthesis Activity → Dossier/View`

The future system should be able to answer:

- Which assertions depend on this Artifact?
- Which Dossiers/Views depend on those assertions?
- Which outputs require re-review if a source changes?

## 10. Relation primitive

Long-term candidate relation shape:

- stable relation ID;
- 2+ participants with roles;
- relation type;
- directionality;
- context;
- time;
- epistemic/evidence state;
- provenance;
- state extensions: boundary, passage, memory, visibility, bond, flow, obligation, agency, recurrence, transformation, fruit, closure.

This generalizes the strong existing pairwise/hyperedge schemas rather than discarding them. Pairwise algorithmic projections may be generated from higher-order relations and should declare information loss.

## 11. Door / Transition primitive

A Door is a guarded transition, not merely a link.

Required conceptual fields:

- identity;
- affected subject(s);
- source state/context;
- guard/preconditions;
- trigger;
- transition Activity;
- destination state/context;
- preserved invariants;
- generated provenance;
- reversibility;
- rollback/return path;
- time/evidence.

Links/buttons may expose Doors; they do not define them.

## 12. Room / View / Facet / Programme / Collection / Seed

- **Room** — bounded context with local vocabulary, schemas, evidence rules, validators and interfaces.
- **View** — task-specific lossy projection; never owner.
- **Facet** — cross-cutting classification/filter.
- **Programme** — mission/workflow spanning multiple Rooms.
- **Collection** — curated grouping of existing identities/artifacts.
- **Blueprint / Seed** — reusable generative contract for a record family.
- **Path / Ladder** — ordered sequence of navigation steps and/or Doors.

Never use these names interchangeably.

## 13. Universal ownership law

Replace the coarse rule `one concept → one file` with:

> **One stable identity authority, and one explicit authority for each fact family in each bounded context.**

Historical strata, evidence collections and specialist datasets may survive separately when they own distinct provenance or function. Projections may never become shadow canon.

## 14. Safety and liveness

House health has two dimensions.

### Safety

Important bad states do not occur:

- no broken JSON/routes;
- no duplicate canonical fact-family owner;
- no unresolved required endpoints;
- no silent project-canon/empirical collapse;
- no validator mutation of deployed artifacts;
- no invalid source/provenance claims.

### Liveness

Important processes can still progress:

- research can become canonical;
- deprecated systems can retire;
- unresolved contradictions can reach explicit stable state;
- Rooms can evolve schemas;
- new Views can be added without identity rewrites;
- sources can trigger selective re-review;
- useful material can become reachable.

A system can be syntactically clean and still be Swamp if liveness collapses.

## 15. Constitutional distinction

The future constitution should define **semantics and invariants**, not force one physical storage layout. JSON files, indexes and generated pages are implementation choices below the constitutional layer.
