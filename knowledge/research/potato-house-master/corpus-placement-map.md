# Potato House — Whole-Corpus Placement Map

**Status:** architecture coverage research; non-canonical until promoted by the permanent House specification.

## Purpose

This document answers the pre-implementation question:

> Can the proposed Potato House architecture provide a legitimate place for every significant class of material in the repository without forcing unlike things into one ontology?

The proof is by **total placement rules**, not by pretending every file is the same kind of object.

## Total coverage invariant

Every repository path must belong to exactly one **repository plane**:

1. **Knowledge House** — durable meaning, identity, claims, events, relations, sources and research.
2. **Governance / Gardener** — schemas, ownership rules, vocabularies, quality constraints, migration/deprecation policy.
3. **Operations / Forge** — builders, importers, acquisition jobs, transforms, validators, audits and deployment workflows.
4. **Presentation / Fruit** — HTML, CSS, JavaScript, maps, readers, timelines, search surfaces and generated machine projections.
5. **Memory / Ash-Archive** — historical snapshots, superseded architectures, legacy pages and preserved prior states.

A path may reference objects in another plane, but its **primary responsibility** must be one plane.

Every durable object inside the Knowledge House must additionally resolve to one or more House roles:

- Subject
- Assertion / Observation / Measurement
- Artifact
- Occurrence
- Relation
- Activity
- Transition
- Context
- Dossier / knowledge product
- Blueprint / Seed
- Programme
- Collection / Guide
- Room membership
- View configuration
- research candidate / unresolved material

If a future file cannot be classified by these rules, that is an architecture defect to investigate rather than an excuse to invent another top-level framework casually.

---

# 1. Root-level project files

| Current family | Placement | Future treatment |
|---|---|---|
| retired 2026 root synthesis | Historical development artifact recoverable through `archive/legacy/README.md` | current ownership lives in dedicated core, science, timeline and world records |
| `THE-TURNING-APRIL-2025.md` | Artifact + Occurrence-related historical/source material | Archive/Time roots; may support Tim/Potatoverse dossiers |
| `TIM-DOOLEY-LIFE-AND-MYTH-TIMELINE.md` | Retained readable timeline/source stratum | Time & History uses it for provenance/early roadmap context; canonical event identity belongs to `data/timeline-events.json` |
| `POTATOVERSE-*-RESEARCH.md` | Research-Lab Artifacts / candidate Assertions | not canonical merely because root-level |
| `book-research.json` | 2024 Great Book source-extraction bridge | preserve as source/provenance artifact; derived durable claims belong in specialist owners |
| `README.md` | Governance/documentation | project entry point, never canonical knowledge merely by location |
| `TODO.md` | Operations/Gardener work queue | not House knowledge unless individual tasks become research records |
| `_config.yml`, `.gitignore` | Operations | repository/build configuration |

Rule: **root location conveys no epistemic or ownership privilege.**

---

# 2. `knowledge/` corpus families

Physical subfolders are historical organization aids, not final ontology. They map to Rooms, facets, Programmes or research strata as follows.

| Current knowledge family | Primary House placement | Notes |
|---|---|---|
| `knowledge/core/` | Potatoverse / Canon Room | current project concepts, identity syntheses, root geometry, symbolic grammar; split factual vs project-canon assertions where mixed |
| `knowledge/philosophy/` | Potatoverse/Canon + Research contexts | philosophy dossiers/assertions; some archive epistemics also informs Governance constitution |
| `knowledge/practice/` | Potatoverse/Canon or Collection/Guide | practices are not universal schema; model as Guides/Programmes/Transitions when appropriate |
| `knowledge/cosmology/` | Potatoverse/Canon + Traditions/Science comparative contexts | preserve project canon, scientific and comparative epistemic separation |
| `knowledge/journey/` | Time & History + Potatoverse dossiers | life-development syntheses; Occurrences remain distinct from later interpretation |
| `knowledge/body/` | Life & Body / Science | anatomy/neuro dossiers, symbolic comparisons as separate contextual Assertions |
| `knowledge/biology/` | Life & Body / Science | literal biology; Blueprint-ready biological Subjects, Observations, Occurrences and Relations |
| `knowledge/traditions/` | Traditions & Texts | comparative/theological dossiers, source Artifacts, text Subjects, interpretive Assertions |
| `knowledge/politics/` | World Systems | political Subjects/Relations/Assertions; project political interpretations explicitly typed |
| `knowledge/geopolitics/` | World Systems | countries, alliances, institutions, flows, scenarios; North Programme material may be Programme-owned |
| `knowledge/economics/` | World Systems | finance, trade, debt, ownership, sector flows; use existing Blueprints |
| `knowledge/legal/` | World Systems with Legal facet/Blueprints | laws, obligations, jurisdictions, legal Events/Relations; not necessarily independent Room initially |
| `knowledge/corporium/` | candidate cross-Room Programme/Collection | must be tested before Room promotion; likely consumes World Systems, Culture, Research |
| `knowledge/culture/` | Culture & Information | media, subcultures, platforms, memes, information ecology; claims/evidence remain typed |
| `knowledge/creative/` | Works | original stories, poems, concepts and creative Artifacts; creative status distinct from documentary claim |
| `knowledge/guides/` | Collection/Guide layer | reader/research guides pointing at durable Subjects/Artifacts; should not duplicate owners |
| `knowledge/indexes/` | Governance/derived navigation or curated Collections | each index classified as generated View index or curated Collection; never silent second canon |
| `knowledge/research/` | Research Lab | exploratory Artifacts, hypotheses, architecture research; promotion requires explicit Door |
| `knowledge/schema/` | Governance / Gardener | schema contracts, not content records |

Additional knowledge directories discovered later follow the same test: if they define a distinct bounded context they may support a Room; otherwise they map to an existing Room, facet, Programme, Collection or research layer.

---

# 3. `data/` families

`data/` mixes durable records, registries, schemas, generated datasets and UI configuration. It is therefore explicitly **not one ontology layer**.

| Data family | Placement |
|---|---|
| canonical/current entity records | Knowledge House primitives / Dossiers via adapters |
| country/economic/ownership/flow datasets | World Systems Room using existing Blueprints |
| timeline/event datasets | Occurrences + Time & History indexes |
| relationship/edge/hyperedge datasets | Relation primitives |
| source/evidence ledgers | Artifacts + Provenance |
| claim/observation datasets | Assertions/Observations |
| blueprint registry and blueprint files | Governance Seeds/Blueprint contracts |
| canonical-source-map / ownership maps | Governance authority registry |
| schema files | Governance contracts |
| graph registries / node indexes | derived indexes or compatibility registries; not independent truth unless explicitly designated |
| manifests/navigation maps | View/build configuration; generated where possible |
| runtime/map snapshots | Operations input/cache or generated data, not canon by default |
| migration/deprecation ledgers | Governance / Transition policy |
| diagnostic reports | Gardener health outputs; generated |

Rule: every `data/*.json` family must eventually declare one of: `canonical_input`, `source_artifact`, `governance_contract`, `generated_projection`, `runtime_cache`, `migration_compatibility`, or `historical`.

---

# 4. Blueprints

Existing domain Blueprints are retained and strengthened as **Seeds**.

They define how a family of real records grows correctly while reusing the House Kernel.

Examples already represented in the repository include countries, governance, finance/debt, ownership/control, trade, energy, infrastructure, demography, law, media, research and religion.

Blueprints may define:

- specialist identity fields;
- Room-local vocabulary;
- required time/geography/function fields;
- relation families;
- evidence requirements;
- source acquisition expectations;
- specialist validation;
- preferred public representation.

Blueprints do not own actual facts about instances.

---

# 5. Books, texts and long-form material

| Family | Placement |
|---|---|
| `books/` originals | Works Room Subjects + Artifacts |
| research about books | Research Lab or Traditions/Works Assertions |
| scriptural/public-domain text corpora | Traditions & Texts Artifacts/Subjects |
| translations/editions | Artifacts related to Text Subjects with edition/translation provenance |
| commentary/comparison | Assertions/Dossiers in declared Contexts |

One textual work can have stable identity while editions, translations, files and interpretations remain separate Artifacts/Assertions.

---

# 6. Time and chronology

Current `timeline/`, `chronology/`, timeline JSON and life-history material split into:

- Occurrence identities;
- valid/occurrence time;
- source/publication time;
- recorded/retrieval time;
- interpretation time;
- timeline Views;
- historical Dossiers/Collections.

The public timeline is a **View**, not the owner of the Occurrences.

Later interpretations never silently rewrite the occurrence date.

---

# 7. Public route directories

Current public directories such as Tim, Religion, Philosophy, Science, World, Politics, North, World Map, World Systems, Timeline, Chronology, Traditions/Bible, Learn/Explore and similar routes belong to **Presentation / Fruit**.

They are classified as one of:

- Room landing View;
- Subject compatibility route;
- Programme View;
- specialist Explorer;
- Collection/Guide View;
- deprecated/redirect compatibility Door.

They do not own canonical knowledge simply because users can browse them.

Examples:

- World Map → specialist Explorer/View over World Systems Subjects and Relations.
- Timeline → temporal Explorer/View over Occurrences.
- Bible Comparator → specialist Traditions View.
- North → Programme/public interpretation surface, not universal Room.
- Science landing → Room landing if Science passes final Room contract.
- legacy five-door homepage links → compatibility Views during migration.

---

# 8. `app/` CSS and JavaScript

All frontend CSS/JS belongs to **Presentation / Fruit**.

Subclasses:

- shared shell/design-system component;
- Room-specific component;
- specialist Explorer module;
- compatibility shim;
- deprecated duplicate.

Examples: Bible loaders/readers are Traditions View implementation; timeline JS/CSS is Time View implementation; map modules are World Systems Explorer implementation; generic reader/style files are candidate shared House shell components.

No frontend module owns facts.

Permanent rule: essential meaning/navigation exists in semantic HTML; JS enhances specialist interaction.

---

# 9. `scripts/`

All scripts belong primarily to **Operations / Forge** or **Governance / Gardener**.

Classification by responsibility:

- `build_*` → Forge/build Activities;
- `import_*`, `fetch_*`, acquisition/mining scripts → Root acquisition Activities;
- `normalize_*`, `patch_*`, migration transforms → Forge Transitions, with temporary patches explicitly deprecated;
- `validate_*` → Gardener invariant enforcement;
- `audit_*` → Gardener diagnostics / Swamp detection;
- `analyze_*` → Research/analysis tooling whose outputs are Assertions/diagnostics, not automatically canon;
- SEO/discovery exporters → Presentation projection builders.

Scripts never become evidence merely because they generated an output; generated content retains provenance to inputs and transform version.

---

# 10. `.github/workflows/`

CI/CD workflows belong to **Operations / Forge/Gardener automation**.

Examples:

- Pages workflow → final projection build/deploy Activity;
- quality checks → Gardener health gates;
- country refresh → scheduled acquisition/update Activity for World Systems;
- text import workflows → Archive/Traditions acquisition Activities.

Permanent deployment law:

> the artifact deployed must be the artifact validated; validators do not mutate it after the final gate.

---

# 11. `docs/`

Project documentation belongs to Governance or Memory depending status.

- current architecture/standards/process docs → Governance;
- domain research docs → Research Lab Artifacts;
- superseded architecture docs → Memory/Ash-Archive;
- tool/user guides → Governance/Guide;
- migration plans → Governance/Transition documentation.

Old architecture files such as prior Atlas/layer/navigation schemes are not deleted merely for being superseded; they gain explicit lifecycle status and become provenance for why the current design exists.

---

# 12. `archive/`

Historical snapshots and legacy backlog belong to **Memory / Ash-Archive**.

They preserve:

- prior source states;
- superseded records;
- old site structures;
- migration evidence;
- unique content not yet promoted.

Archive is not Swamp by default.

Archive material can later cross a promotion Door into current knowledge while retaining its historical Artifact identity.

---

# 13. Generated output and caches

Examples include `_site`, generated indexes, runtime snapshots, SEO reports, machine discovery files, compiled catalogs and temporary diagnostic reports.

These are **generated projections/caches**.

Rules:

- rebuildable from durable inputs;
- never the sole owner of unique knowledge;
- provenance includes generator/version and input set where useful;
- safe to delete/rebuild unless explicitly archived as a historical release Artifact.

---

# 14. Media/assets

Images, diagrams, audio, video and other media are either:

- durable creative/source Artifacts;
- derived presentation assets;
- generated/cache assets.

The distinction is explicit. An original artwork is a Works Artifact; a resized thumbnail is a generated projection.

---

# 15. Old organizing systems

No useful prior architecture is discarded; each is assigned a role.

| Prior system | Future role |
|---|---|
| Spirit / Mind / Matter | cross-cutting concept scheme/facets; not physical storage roots |
| 33-level framework | legacy facet/breadth scheme and research Artifact |
| D1–D11 | interrogation/operator stack |
| World / Axis | major analytical/View distinction; World = observable systems, Axis = transformation/orientation operators |
| five homepage doors | compatibility/public Views, not ontology |
| experimental Atlas | engineering donor + historical architecture Artifact; its Node ontology is not constitutional |
| Tree / World Tree | connective/generative structural comparator, not file hierarchy |
| North Axis | selected orientation / Programme depending context, not truth ranking |

---

# 16. Specialist applications

Specialist applications are **Explorers** consuming House data:

- World Map;
- Bible Comparator;
- Timeline Explorer;
- graph/path finder;
- science equation/model tools;
- future ownership/finance/network explorers;
- House Inspector/Gardener diagnostics.

Each Explorer declares:

- input primitive types;
- Rooms/Blueprints consumed;
- projection/loss contract;
- whether it writes any durable state;
- accessibility fallback;
- performance budget.

An Explorer does not become another truth store.

---

# 17. Programmes, Collections, Guides and Questions

These cross Rooms without requiring new ownership trees.

- **Programme** — coordinated mission/workflow (for example North Programme).
- **Collection** — curated references to existing durable objects.
- **Guide** — ordered explanatory route through existing objects.
- **Question** — temporary retrieval/synthesis corridor; becomes durable only if explicitly promoted as a research Subject/Assertion/Programme.

---

# 18. Swamp placement

Swamp is not a folder. It is a diagnostic condition that can occur in any plane:

- Knowledge: duplicate ownership, unresolved contradictions, vague relations.
- Governance: competing constitutions or schemas.
- Operations: circular build mutation, patches undoing one another.
- Presentation: duplicated content ownership, inaccessible graph-only navigation.
- Memory: old material with no classification/promotion/retirement path.

Therefore Swamp is recorded as health findings and remediation work, not as a dumping directory.

---

# 19. Coverage gates before implementation

The architecture is not implementation-ready until all of these are true:

1. every top-level repository family matches one repository plane;
2. every `knowledge/` family maps to a candidate Room/context or explicit cross-Room role;
3. every durable JSON/Markdown knowledge family maps to at least one House primitive/composition;
4. every public route is classified as Subject, Room, Programme, Collection, Explorer or compatibility View;
5. every schema/registry is classified as canonical contract, Room extension, generated projection or legacy contract;
6. every major script family has an operational/Gardener responsibility;
7. every legacy architecture has a preservation/deprecation role;
8. no current specialist application requires owning duplicate truth;
9. at least one representative real example from every major family can normalize without bespoke exceptions;
10. remaining exceptions are explicitly listed as architecture defects rather than silently ignored.

Only after these gates pass should implementation begin.

---

# 20. Current conclusion

The proposed House **can represent the known repository as a whole**, provided it is understood as a layered project architecture rather than one knowledge graph.

The finite placement model is:

```text
PROJECT
├── Knowledge House
│   ├── Kernel primitives
│   ├── Rooms
│   ├── Blueprints / Seeds
│   ├── Programmes / Collections / Guides
│   └── Research candidates
├── Governance / Gardener
│   ├── schemas
│   ├── vocabularies
│   ├── source-of-truth maps
│   ├── health constraints
│   └── migration/deprecation contracts
├── Operations / Forge
│   ├── acquisition
│   ├── normalization
│   ├── generation
│   ├── validation/auditing
│   └── deployment
├── Presentation / Fruit
│   ├── Subject pages
│   ├── Room pages
│   ├── Explorers
│   ├── search/discovery
│   └── machine projections
└── Memory / Ash-Archive
    ├── historical snapshots
    ├── superseded architectures
    ├── legacy routes
    └── preserved prior states
```

This is the current whole-project placement hypothesis to be tested by the permanent design specification and representative-record normalization before implementation begins.
