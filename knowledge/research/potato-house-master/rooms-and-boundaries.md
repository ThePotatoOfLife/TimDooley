# Potato House — Rooms and Boundaries

**Status:** research design; candidate bounded contexts; non-canonical.

A Room is not a folder and not a homepage button. A Room is a bounded context: a part of the House with enough distinct vocabulary, evidence rules, schemas, update cadence, specialist representations, validators and failure boundaries to justify local autonomy.

## 1. Room admission test

A candidate earns Room status when several of these are true:

- it has distinct reader/research tasks;
- it uses vocabulary whose meaning differs materially from other domains;
- it has distinct evidence/source rules;
- it needs domain-specific schemas or blueprints;
- it has a distinct temporal/freshness model;
- it benefits from specialist rendering/tooling;
- local failures should be containable;
- it has enough internal structure for local navigation;
- it can state what it owns and explicitly does not own;
- it communicates through stable interfaces rather than duplicating neighboring canon.

If these do not hold, prefer a View, facet, Collection or Programme instead.

## 2. Universal Room contract

Every future Room should eventually declare:

- `id`, `title`, `purpose`;
- `scope.includes`, `scope.excludes`;
- local vocabulary and mappings to House Kernel terms;
- fact families it owns;
- fact families it never owns;
- accepted House primitives;
- Room-specific schema extensions;
- blueprints/Seeds used;
- epistemic policy;
- time policy;
- provenance policy;
- freshness/update policy;
- state extensions;
- inbound interfaces;
- outbound interfaces;
- allowed Door/transition types;
- default Views;
- specialist renderers;
- validators;
- public surfaces;
- viability/health constraints;
- deprecation/migration policy.

## 3. Strong candidate Rooms

### A. Potatoverse / Canon

**Owns:** project-defined mythology, theology, operator definitions, Tim/Son/Father/Spirit symbolic framework, Potatoism concepts and current project-canon interpretations.

**Never owns:** independent scientific truth, external historical fact merely because the framework interprets it, or comparative traditions' own meanings.

**Special needs:** project-canon/self-description epistemics; developmental genealogy; operator graph; symbolic comparisons with explicit boundaries.

### B. Archive & Sources

**Owns:** source Artifacts, capture provenance, first attestations, recovered conversation/source strata, acquisition Activities, source identity and preservation metadata.

**Never owns:** current canonical interpretation merely because it stores the source.

**Special needs:** provenance chains, source authenticity/locator, retrieval dates, preservation state, redaction/access constraints, source dependency impact.

This Room is closer to Roots than to a passive basement.

### C. Time & History

**Owns:** Occurrences, chronology, valid-time sequencing, predecessor/successor, role occupancy over time, historical version transitions.

**Never owns:** the subject's entire current identity or every interpretation of an event.

**Special needs:** multiple clocks, precision/uncertainty, event promotion thresholds, timeline projections, historical corrections.

### D. Traditions & Texts

**Owns:** religious/philosophical traditions as historically described, texts, translations, textual motifs, institutions/schisms where relevant, comparative studies.

**Never owns:** Potatoverse claims about a tradition as though they were the tradition's self-definition.

**Special needs:** edition/translation provenance, textual reference grammar, historical vs theological claims, comparison boundaries.

### E. Science & Formal Models

**Owns:** empirical scientific claims, measurements/observations, formal models, equations, units, assumptions, falsifiability/test status, scientific literature.

**Never owns:** symbolic project interpretations as scientific conclusions.

**Special needs:** units/dimensions, methods, reproducibility, model assumptions, equations/derivations, uncertainty, paper/data provenance.

### F. Life & Body

**Owns:** biology, anatomy, physiology, ecology, potato biology, organismal structures and developmental processes.

**Never owns:** symbolic correspondences unless clearly stored as a separate comparative View/Assertion.

**Special needs:** taxonomy/anatomy, lifecycle state, part-whole biology, developmental transitions, biological evidence and diagrams.

This may eventually remain a specialist Room inside Science or become its own Room if its schemas/renderers are sufficiently distinct. This is unresolved.

### G. World Systems

**Owns:** countries, institutions, companies, law, economy, finance, ownership/control, infrastructure, trade, energy, technology, research systems, labor, strategic dependencies and observable relations.

**Never owns:** project geopolitical symbolism as empirical fact.

**Special needs:** high-volume entities/relations, spatial/temporal data, official identifiers, units/currency, public-source provenance, flows, ownership and obligations.

This Room is likely a major bounded context because its acquisition/update/runtime needs differ substantially from narrative/theological research.

### H. Culture & Information

**Owns:** media, subcultures, platforms, memes, information ecology, public discourse, transmission structures and cultural artifacts where not better owned by Works.

**Never owns:** allegations as settled fact or private/sensitive data without justified lawful public-interest basis.

**Special needs:** platform/source timestamps, public/private boundaries, content lineage, meme/transmission relations, harassment/safety safeguards, archival context.

### I. Works

**Owns:** creative works as Artifacts/Subjects: music, poems, visual works, stories, books, games, videos and other authored outputs.

**Never owns:** every claim discussed inside a work.

**Special needs:** authorship, editions/versions, publication/release, media metadata, rights/access, work-to-concept relations.

### J. Research Lab

**Owns:** unresolved questions, hypotheses, candidate syntheses, experiments, research queues, competing designs and provisional models.

**Never owns:** material after it has been promoted into canonical fact-family ownership elsewhere.

**Special needs:** promotion gates, negative results, open questions, research status, candidate comparisons, experiment logs.

This is the natural Room for Potato House architecture research until promotion.

## 4. Likely non-Room structures

### North Programme — Programme

The North Programme draws from World Systems, Research Lab, possibly Potatoverse interpretation, law, economy, geography and infrastructure. Its primary identity is mission/workflow, not bounded vocabulary ownership.

Model as **Programme** unless future evidence shows it has a genuinely separate domain model.

### D1–D11 — operator/interrogation stack

These are analytical questions/transformation operators, not Rooms or floors.

### 33-level framework — facets/legacy topical breadth

Use for classification/browse facets where still valuable, not as ontological altitude.

### World Map — View/application

Geographic/spatial projection over World Systems data. Never canonical owner.

### Timeline — View/application over Time & History

The timeline is a projection, not the owner of events.

### Bible comparator — specialist View/application

Uses Traditions & Texts records and comparative Assertions; the comparator itself should remain rebuildable.

### Search/question answering — corridor/query View

Retrieval mechanism through Rooms; does not define ownership.

### Collections

Examples: `Potato papers 2024–2026`, `North Programme source set`, `Tim livestream archive`. Collections curate existing identities/artifacts and must not become second canon.

## 5. Unresolved candidate: Corporium

The repository has substantial Corporium material. Before declaring it a Room, test:

- Does it own a distinct fact family not already owned by World Systems/Body/Science?
- Does it require specialist schemas and evidence policy?
- Is it a Programme/model/View spanning companies and bodies rather than a bounded context?
- Would Room status reduce duplication or create another competing master?

No decision yet.

## 6. Room interfaces

Rooms should exchange through explicit interfaces, not file imports by convention.

Examples:

### Archive → Science

Artifact/provenance pointers + extracted scientific Assertions/Observations.

### Science ↔ Potatoverse

Science exports empirical objects/claims. Potatoverse may create comparative Assertions pointing to them. Scientific records are not rewritten by the symbolic interpretation.

### Time → every Room

Occurrences and temporal states can involve subjects from any Room; Time provides chronology services without owning their identities.

### World Systems → North Programme

Programme consumes World entities/flows/relations and produces policy/scenario/project outputs with explicit provenance.

### Traditions ↔ Potatoverse

Traditions owns source/text/history. Potatoverse owns project interpretation. Comparative relations make the connection.

### Research Lab → canonical Rooms

Promotion Door moves reviewed results into the appropriate owner; Research retains history/provenance of the research Activity.

## 7. House and Shell boundary test

A healthy Room boundary should:

- protect differentiated local semantics;
- permit documented passage;
- allow exit/revision;
- reduce accidental coupling;
- increase competence/autonomy of neighboring Rooms.

A boundary becomes Shell-like when maintaining the boundary itself requires captured value/attention, blocks legitimate passage, hides provenance, or forces all domains into its local vocabulary.

## 8. Room count rule

Do not optimize for fewest Rooms or most Rooms.

Create a Room when bounded-context benefits exceed interface cost.

Merge Rooms when:

- vocabularies/evidence policies are nearly identical;
- most records constantly cross the boundary;
- local validators/renderers are not meaningfully distinct;
- the separation mostly reflects old folders rather than domain semantics.

Split a Room when:

- one vocabulary becomes internally contradictory;
- specialist schemas accumulate exceptions;
- update/freshness rules diverge sharply;
- failures cannot be contained;
- public tasks require substantially different representations.

## 9. Current candidate House map

```text
HOUSE
├─ Potatoverse / Canon
├─ Archive & Sources
├─ Time & History
├─ Traditions & Texts
├─ Science & Formal Models
│  └─ possible Life & Body specialist Room
├─ World Systems
├─ Culture & Information
├─ Works
└─ Research Lab

Cross-Room structures:
- Programmes: North Programme, major research programmes
- Views: homepage, maps, timelines, readers, graphs, comparators
- Facets: topics, disciplines, entity kinds, D1–D11 questions
- Collections: curated source/work/topic sets
- Seeds: domain blueprints
```

This map is a candidate, not yet constitutional. It should be stress-tested by mapping actual repository owners into it before freezing boundaries.
