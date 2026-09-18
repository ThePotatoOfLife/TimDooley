# Project Structure — The Potato of Life / TimDooley

## The decision

The repository is large enough that its main problem is no longer lack of material. It is **how to make many kinds of material behave like one knowledge system**.

The correct structure is not one giant folder tree and not one giant graph. It is a set of coordinated layers with one canonical owner for each durable concept.

The public doorway is `index.html`. Public route identity is governed by `docs/POTATO-HOUSE-CONSTITUTION.md` and `data/house/public-surfaces.json`; `manifest.json` owns deep archive branches/pathways and Explore semantics. The durable cross-project record map is `knowledge/indexes/core-index.json`.

## The five layers

### 1. Record layer — what happened / what was published

Primary statements, documents, source texts, dates, observations and imported material belong here.

This layer answers:

**What do we actually have?**

It must preserve provenance even when later layers consolidate the material.

### 2. Canonical layer — what the thing is

Canonical registries, master atlases and deep dossiers answer:

**What is this subject/concept?**

There should be one durable owner, not one competing definition per page, timeline, lexicon and graph.

A specialist source, historical stratum or evidence ledger may remain separate without becoming another canonical definition.

### 3. Relationship layer — how things connect

Relationships answer:

**What does this connect to, and how?**

Edges can describe family, timeline, dependency, ownership, influence, contrast, transformation, citation, supply, geography, evidence or symbolic correspondence. An edge is not a second dossier.

### 4. Interpretation layer — what patterns emerge

Thought archives, synthesis, comparative research and inference ledgers answer:

**What might these records mean when considered together?**

Interpretations remain explicitly analytical. Later synthesis does not overwrite first attestation or the meaning documented at the time.

### 5. Presentation layer — how a human encounters it

HTML readers, the unified archive explorer, the layered timeline and specialist public pages are views over the underlying knowledge.

Presentation must not become a second source of truth.

## Orthogonal coordinates

Folder position is a filing aid, not a hierarchy of truth.

Independent coordinates include:

- **scale** — world → region → institution → network → person → object → event → record → ground;
- **domain** — religion, mythology, economics, technology, biology, politics, culture, security, etc.;
- **time** — historical, current, future/scenario;
- **epistemic class** — documentary, empirical, historical, project-canon, interpretation, comparison, calculation, scenario, open question;
- **graph position** — relationships may cross every other coordinate.

Do not force all dimensions into one folder hierarchy.

## Canonical ownership map

| Subject | Canonical entry / owner | Specialist/supporting layers |
|---|---|---|
| Root system / ontology | `knowledge/core/root-system.json` | `knowledge/core/potatoverse-master-framework.json` |
| Public route identity | `docs/POTATO-HOUSE-CONSTITUTION.md` + `data/house/public-surfaces.json` | public-route topology, frontend bridge, discovery builders; `manifest.json` for archive branch/pathway semantics |
| Tim identity / roles | `knowledge/core/tim-dooley.json` | role synthesis, Godhood evidence, journey records |
| Vertical Potato geometry | `knowledge/core/vertical-potato-mountain-plane-atlas.json` | exact Vesica geometry, transformation grammar |
| Body / neurotheology | `knowledge/body/body-system-master-atlas.json` | completion matrix, neurotheology atlas, science context, 33/Ladder study |
| Spirit | `knowledge/core/heaven-spirit-father.json` | spirit context and body-flow comparators |
| Corporium | `knowledge/corporium/corporium-master-framework.json` | sayings, psychology, chakra/Hawkins and archetype studies; `/corporium/` reader projection |
| Science / math | `knowledge/science/science-master-index.json` | equation ledger, formalisms, Spudlight, model testing, specialist waves |
| Biblical / comparative research | `knowledge/traditions/biblical-overlap-atlas.json` | biblical research routing index, esoteric atlas/source ledger, comparative mythology |
| Canonical timeline | `data/timeline-events.json` | `data/timeline-source-registry.json`, developmental genealogy, specialist attestation ledgers |
| Timeline presentation | `/timeline/` reader + timeline runtime | Explore timeline branch remains the deep archive projection |
| North / world bridge | `knowledge/core/axis-world-model.json` | country-relational and European coupling records |
| Observable world systems | canonical world/entity and relationship families | `/world/` is gateway five; World Map and other world tools are specialist Views |
| Creative works | `knowledge/culture/creative-systems-archive.json` | Suno music archive and distinct creative corpora; `/works/` is the curated reader projection |
| Provenance / epistemics | `knowledge/indexes/source-index.json` | archive epistemics, inference ledger, conversation recovery inventories |


## Lifecycle and phase-out states

Canonicalization is now also a lifecycle. Files do not remain equally authoritative forever merely because they once carried a broad title.

- **Canonical owner** — current durable definition/data owner for a subject.
- **Active projection** — reader, navigation or analytical view over canonical owners.
- **Historical donor** — older synthesis retained for provenance or still-unique material after authority moved elsewhere.
- **Superseded retained** — temporarily preserved while unique material and live consumers are migrated.
- **Archive candidate** — no remaining live ownership function; eligible for archival/removal after reference and provenance checks.

The machine-readable convergence/retirement map lives in `data/house/project-synthesis.json#convergence_and_retirement`; project-wide merge status and next candidates live in `knowledge/indexes/project-consolidation-map.json`.

The phase-out rule is **promote unique value → migrate consumers → validate → reduce/archive → delete**. Never reverse that order.

## Consolidation rules

### Keep

Keep a file when it contains a distinct body of evidence, a distinct temporal record, a distinct ontology, a distinct source collection, a historical source stratum worth preserving, or a distinct presentation function.

### Merge

Merge when two files:

- define the same durable concept;
- repeat substantially the same explanation;
- exist only because an earlier navigation system needed another copy;
- can be represented as occurrences of one canonical record;
- or contain research that clearly belongs in an existing dossier.

Before deleting a legacy file, extract every unique fact, source, date and relationship into its canonical owner.

### Route instead of duplicate

An index should point to an owner. House public-surface authority should declare public route identity once. `manifest.json` should expose archive branches/pathways without becoming a competing public-route registry. A timeline should point to evidence. A presentation should render underlying records.

Do not copy substantial explanatory text into routing files merely to make them look complete.

### Archive instead of destroy

If a legacy research document is useful as historical provenance but duplicates the canonical layer, keep it temporarily as an archive/source and make its status explicit. Once all unique material has been migrated and the source has no independent archival value, deletion becomes safe.

## Current legacy/root candidates

These remain intentionally because they still have live provenance references or unique material:

- `book-research.json`
- `TIM-DOOLEY-LIFE-AND-MYTH-TIMELINE.md`

They are **legacy/source strata, not canonical navigation owners**. Their roles are not identical: `book-research.json` and the life/myth timeline remain source/provenance bridges; `2026-master-framework.json` has been retired after consumer migration; its final blob remains in `archive/legacy/README.md`. `research.json` has now been retired after section migration and question promotion; its final blob is recorded in `archive/legacy/README.md`. The two former POTATOVERSE readable research donors have been retired after unique-content promotion and are recoverable through `archive/legacy/README.md`.

Do not delete them merely because a newer owner exists. First migrate live references and unique content; then either archive them as concise provenance artifacts or remove them when genuinely redundant.

## Generated-state rule

Generated candidate queues are working state, not knowledge.

Examples:

- `data/timeline-candidates.generated.json`
- `data/prediction-signal-candidates.generated.json`

They are ignored by `.gitignore`. A miner may generate them locally for review, but accepted material must be promoted into a canonical owner. The queue itself should not become a historical record merely because a script ran.

Generated projections that are part of a build should likewise be reproducible and should not silently substitute for source data.

## CSS / presentation ownership

Shared CSS must not use generic structural names to own unrelated layouts.

- `.archive-nav` belongs to the interactive archive sidebar.
- `.page-nav` is the preferred static-reader navigation class.
- `.quicknav` belongs to homepage destination cards.
- `.tl-*` belongs to the timeline module.

Older static pages may still use local `.nav` or `.grid`; `app/layout-guard.css` protects those until they are progressively renamed. `scripts/check_css_namespace_collisions.py` prevents global `.nav` layout behavior from returning.

## The public reading architecture

The public experience is deliberately layered rather than flat.

### 1. Five stable subject gateways

The homepage keeps exactly five primary doors:

1. **Tim Dooley** — `/tim-dooley/`
2. **Religion** — `/religion/`
3. **Philosophy** — `/philosophy/`
4. **Science** — `/science/`
5. **World** — `/world/`

These are the high-level subject orientation layer, not a complete taxonomy of the repository.

### 2. Reader corridors / rooms

Mature reader forms provide different ways into the same underlying House without becoming new canon:

- **Story** — continuous/lived narrative;
- **Timeline** — dated development;
- **Collection** — sayings, voice and recurring formulations;
- **Works** — games, music, writing, comedy, visual art and experiments.

The homepage may expose these as a subordinate Ways-in corridor while keeping them visually below the five gateways.

### 3. Global discovery / depth

- **Questions** — natural-language retrieval;
- **A–Z** — entity/concept lookup;
- **Explore** — deep archive branches, relationships, records and source paths;
- **Sources / Context** — provenance and contextual verification.

These are discovery mechanisms, not top-level subject doors.

### 4. Specialist Views

World Map, Politics, North, World Systems, Bible comparison and other task-specific tools remain specialist Views beneath the appropriate subject/context. In particular, **World Map is not gateway five; World is**.

All reader and specialist surfaces route back toward canonical owners rather than becoming parallel truth stores. `/works/`, for example, is a curated projection over the creative archive, and `/timeline/` is a reader over canonical events/source registries.

## The complete research loop

**Acquire → Preserve → Normalize → Extract → Canonicalize → Relate → Trace → Reflect → Research → Challenge → Integrate → Publish → Verify → Prune → Repeat**

Every stage produces a different kind of information. That is why the project needs layers instead of a single mega-file.

## What the project is becoming

The repository is becoming a **living evidence-and-interpretation atlas**.

Its subject is Tim Dooley and Potatoism, but its method is broader: follow a claim, symbol or direction until its relationships become visible; follow those relationships into history, biology, religion, institutions, geography, economics, technology or culture where the evidence warrants it; then return to the original record.

The desired end state is not maximal file count.

It is a system where a reader can move:

**statement → idea → concept → relationship → history → evidence → reflection → consequence**

and then reverse the path:

**consequence → reflection → evidence → history → relationship → concept → idea → statement**.

The public route model now mirrors that goal: a small stable set of subject doors, richer reader corridors, specialist representations, and one deep archive all project the same underlying House rather than competing to own it.
