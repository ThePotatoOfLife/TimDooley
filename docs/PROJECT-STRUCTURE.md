# Project Structure — The Potato of Life / TimDooley

## The decision

The repository has become large enough that its main problem is no longer lack of material. It is **how to make many kinds of material behave like one knowledge system**.

The correct structure is therefore not one giant folder tree and not one giant graph. It is a set of coordinated layers with one canonical owner for each durable concept.

## The five layers

### 1. Record layer — what happened / what was published

Primary statements, documents, source texts, dates, observations and imported material belong here.

This layer answers:

**What do we actually have?**

It must preserve provenance even when later layers consolidate the material.

### 2. Canonical layer — what the thing is

The canonical registries and deep dossiers answer:

**What is this subject/concept?**

For recurring Potatoism concepts, `data/potatoism-concept-registry.json` owns identity and aliases. `data/potatoism-dossiers.json` owns substantial readable explanation.

There should be one identity, not one identity per page, timeline, lexicon and graph.

### 3. Relationship layer — how things connect

Relationships answer:

**What does this connect to, and how?**

Edges can describe family, chronology, dependency, ownership, influence, contrast, transformation, citation, supply, geography, evidence or symbolic correspondence. An edge is not a second dossier.

### 4. Interpretation layer — what patterns emerge

Thought archives, synthesis, higher reflections and comparative research answer:

**What might these records mean when considered together?**

This is where the new Tim Dooley Thought Archive and Thought Synthesis belong. Interpretations remain explicitly analytical.

### 5. Presentation layer — how a human encounters it

HTML pages, the Repository, Timeline, Scroll, concept pages and navigation are views over the underlying knowledge.

Presentation must not become a second source of truth.

## Orthogonal coordinates

The repository's `Spirit → Mind → Matter` root is a **filing coordinate**, not a hierarchy of truth.

Other coordinates remain independent:

- **scale** — world → region → institution → network → person → object → event → record → ground;
- **domain** — religion, mythology, economics, technology, biology, politics, culture, security, etc.; 
- **time** — historical, current, future/scenario;
- **epistemic class** — documentary, empirical, historical, project-canon, interpretation, comparison, calculation, scenario, open question;
- **graph position** — relationships may cross every other coordinate.

Do not force all of these dimensions into one folder hierarchy.

## Canonical ownership map

| Subject | Owner | Other layers do |
|---|---|---|
| Potatoism identity | `data/potatoism-concept-registry.json` | reference / enrich |
| Potatoism deep explanation | `data/potatoism-dossiers.json` | cite / project |
| Tim chronology | `data/tim-dooley-timeline.json` | thought archive references |
| Tim cosmology | `data/tim-dooley-cosmology.json` | research and reflections reference |
| Raw Tim thought trajectory | `data/tim-dooley-thought-archive.json` | preserve dated extraction |
| Cross-cutting thought interpretation | `data/tim-dooley-thought-synthesis.json` | generate hypotheses |
| Potato biology | potato property/research layers | compare to symbolism |
| Religious comparison | source/religion research layers | never overwrite historical identity |
| Planetary interpretation | planetary cosmology layer | preserve astronomical facts separately |
| World entities | canonical world/entity families | graph and research enrich |
| Relationships | relationship/graph layers | never create identity |
| Public navigation | HTML | render existing knowledge |

## Consolidation rules

### Keep

Keep a file when it contains a distinct body of evidence, a distinct temporal record, a distinct ontology, a distinct source collection, or a distinct presentation function.

### Merge

Merge when two files:

- define the same concept;
- repeat substantially the same explanation;
- exist only because an earlier navigation system needed another copy;
- can be represented as occurrences of one canonical record;
- or contain research that clearly belongs in an existing dossier.

Before deleting a legacy file, extract every unique fact, source, date and relationship into its canonical owner.

### Archive instead of destroy

If a legacy research document is useful as historical provenance but duplicates the canonical layer, keep it temporarily as an archive/source and make its status explicit. Once all unique material has been migrated and the source has no independent archival value, deletion becomes safe.

## Current consolidation candidates

The repository visibly contains several older top-level research documents alongside newer machine-readable layers. In particular:

- `POTATOVERSE-DEEP-RESEARCH.md` overlaps substantially with `data/potatoverse-deep-research.json` and the canonical Potatoism research/dossier layers.
- `TIM-DOOLEY-LIFE-AND-MYTH-TIMELINE.md` overlaps with `data/tim-dooley-timeline.json` and `data/tim-dooley-cosmology.json`.
- Older alternative-research documents should be retained only where they contain unique provenance or unresolved research that has not yet migrated.

**Do not delete these automatically.** The next consolidation pass should diff each document against its machine-readable successor, migrate unique information, then either turn the document into a concise archival pointer or remove it.

## Generated index rule

`data/repository-index.json` is a generated projection, not a hand-maintained knowledge store. The build workflow explicitly generates it before auditing and deployment. Therefore its absence from the source branch is not itself a data-loss condition.

The real failure condition is:

**build cannot generate it → deployment continues anyway → Repository silently appears empty.**

The project should therefore keep the build fail-closed and surface the exact generation error. `repository.html` already uses an explicit error state instead of silently rendering an empty tree.

## The public reading architecture

The public experience should increasingly offer four ways into the same knowledge:

1. **Repository** — find a subject.
2. **Timeline / Thought** — understand development through time.
3. **Dossier / Book** — understand a subject deeply.
4. **Graph / Atlas** — understand relationships and systems.

The Continuous Scroll should eventually synthesize those views into a coherent reading path rather than duplicating their content.

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

That is the project's real architecture.
