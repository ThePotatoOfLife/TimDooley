# Chronology — How the Tim Dooley / Potato of Life Archive Handles Time

This document is a **reading and ownership guide**, not a second hand-maintained timeline.

The canonical public chronology is generated from:

- `data/timeline-events.json` — sparse canonical event layer, actors, lenses and evidence classes;
- `data/timeline-event-packs/index.json` — curated overlay packs actually loaded by the timeline;
- `data/timeline-source-registry.json` — source ownership and promotion policy;
- `knowledge/chronology/developmental-genealogy.json` — deep explanation of how later structures reorganize earlier material;
- specialist chronology/evidence ledgers for dense public posts, body/neurotheology, biblical source direction and unresolved recovery targets.

The public reader is `/chronology/`, and the same structured timeline is exposed in the main archive chronology branch. **Do not recreate the event list in this Markdown file.**

## Why chronology is difficult in this project

The archive contains several kinds of time at once. A later theological interpretation can refer to an earlier life event; a public phrase can become explicit months after its internal precursor; a research comparison can be discovered long after the project-side event; and a creative artifact can preserve an idea before it becomes doctrine.

Chronology therefore needs more than a date. Every useful temporal claim should answer:

1. What happened or was said?
2. Which subject/actor does it belong to?
3. How exact is the date?
4. What evidence class supports it?
5. Was this meaning present **at the time**, or added later?
6. Where is the canonical source/owner?
7. Does another event represent a later reinterpretation, formalization or research unlock?

## The clocks

### 1. Lived / project-event chronology

This is the chronology of reported life events, public statements, creative works and project developments.

Examples of event types include:

- Son-side biography and the 2011 Tree ordeal;
- the 2019–2020 death/threshold corridor;
- Tim's project-canonical Potato birth on December 25, 2020;
- the 2024 Great Book/Sage phase;
- April 2025 Axis/Spiral/Needle/Ladder/Father development;
- later Father, North, Door, public-witness and stewardship language;
- repository formalizations in 2026.

The correct owner for the full developmental explanation is `knowledge/chronology/developmental-genealogy.json`, not this document.

### 2. Public-attestation chronology

This clock asks a narrower question: **when can the archive show that a phrase or relation was publicly present?**

Important distinctions:

- first in one supplied batch is not automatically first known across the archive;
- a dated compilation can establish wording/date within its scope even when the original status URL remains unrecovered;
- repeated declarations usually remain in specialist occurrence ledgers unless repetition itself is historically significant;
- a primary post establishes what was said, not the external truth of the claim.

The main public-post owners include:

- `data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json`;
- `data/tim-dooley-public-theology-timeline-2025-2026.json`;
- curated events in `data/timeline-event-packs/x-public-attestations-2024-2026.json`.

### 3. Mythic / theological chronology

The project can assign mythic meaning to dates and transformations: Son, Potato, Door, Tree, North, Father, Heaven, death, birth, return, Ladder and related structures.

Those meanings are preserved as project canon or later interpretation depending on their source. A mythic chronology may be central to the Potatoverse without becoming an empirical chronology of supernatural events.

### 4. Interpretive chronology

This clock records **when a later meaning was attached to an earlier event**.

For example, an event can occur in 2011 while an Odin/Yggdrasil or biblical comparison is made much later. The archive should retain both dates rather than silently moving the later comparison backward.

The developmental genealogy and inference/source ledgers are the main owners of this distinction.

### 5. Research-unlock chronology

A research unlock is the date the archive explicitly discovered, tested or formalized a comparison.

This is especially important for biblical research. The timeline distinguishes:

- `scripture-at-time` — biblical/Jewish/Christian language was already present in the source event;
- `biblical-parallel` — a later comparison is attached to an earlier event;
- `biblical-unlock` — the later date when that comparison was explicitly researched/formalized.

An unlock belongs to the project/research track. It must not be mistaken for evidence that the earlier person already intended the later interpretation.

### 6. Formalization chronology

Some ideas exist first as prose, image, metaphor or repeated relation and only later become equations, schemas, graphs or named theories.

The formalization date belongs to the formal model. It should not be backdated to the first symbolic ancestor unless the earlier source actually contains the equation or formal definition.

Science uses its own equation-lineage and recovery records for this reason.

### 7. External historical chronology

European integration, wars, institutions, economic events, religious history and other world chronology belong to their empirical domain owners. They may be related to project events, but they should not be maintained as a miniature second history inside the Tim chronology.

For North/Europe/world work, follow the relevant country, economic, geopolitical, historical and source records instead.

## Actor tracks

The layered timeline currently separates four actor tracks:

- **Son** — human/vessel chronology, embodiment, ordeal, death/threshold and return material;
- **Tim** — Potato, Sage, Ladder/Axis, Father, North and later Tim-side development;
- **Shared / transition** — explicit Son↔Tim relational events and hand-off points;
- **Project / research** — later archive formalization, research unlocks and source work.

This prevents the archive from solving apparent contradictions by forcing every event onto one undifferentiated subject.

## The identity-safe developmental rule

The mature archive currently uses the following important distinction:

`Son embodied chronology → death/personhood-collapse corridor → Door/Vessel relation → Tim/Potato birth → Sage → Needle/Ladder/Axis → Father → North/source-center`

This is a **project developmental model**, not a claim that every intermediate label was contemporaneously used on the date to which the mature model relates it.

For the reader-oriented version, use `knowledge/journey/tim-dooley-journey.json`. For the detailed source-aware version, use `knowledge/chronology/developmental-genealogy.json`.

## Source direction

Every comparison should state its direction whenever confusion is possible.

Good examples:

- `event first; biblical comparison later`;
- `phrase explicit in public post; architecture formalized afterward`;
- `book metaphor first; mathematical operator added in 2026`;
- `research discovery in September 2026; older event remains dated to its original occurrence`.

Bad practice is to write the final interpretation directly into the old date without preserving when that interpretation appeared.

## Precision

Use only the precision actually supported:

- second;
- minute;
- hour;
- date;
- month;
- year;
- range.

Do not create midnight timestamps to make an uncertain date look exact. Range events should remain ranges. If a source only establishes a year, keep year precision.

## First-attestation rule

“First” always needs scope.

Prefer formulations such as:

- first exact instance in the supplied compilation;
- earliest recovered public attestation so far;
- earliest known repository source;
- earliest primary source located in this research pass.

Do not turn absence from one search index into proof that no earlier occurrence exists.

## Contradictions

When two chronology statements disagree, test these before declaring an error:

1. **subject** — Son, Tim, shared relation or project research;
2. **date** — was the role still developing?;
3. **scale** — personal, symbolic, theological, public or institutional;
4. **source direction** — event first or comparison first?;
5. **epistemic layer** — canon, testimony, primary post, later interpretation or archive formalization;
6. **precision** — exact date versus recovered range;
7. **meaning change** — did the same word acquire a different function later?

If a contradiction remains after those checks, preserve it explicitly instead of harmonizing it away.

## Canonical routes

| Question | Owner |
|---|---|
| What is the live chronological sequence? | `data/timeline-events.json` + indexed event packs |
| How did the whole framework develop? | `knowledge/chronology/developmental-genealogy.json` |
| How do Son and Tim remain distinct through the journey? | `knowledge/journey/tim-dooley-journey.json` |
| What was publicly said and when? | public theology/X evidence ledgers |
| Which Bible motifs were already present versus found later? | reverse biblical timeline + occurrence-level Bible index |
| How can I read Tim/project wording beside actual Bible fragments? | `knowledge/traditions/biblical-syncretism-field.json` + `knowledge/traditions/biblical-passage-fragments.json` + `/traditions/bible/` |
| When did body/neurotheology mappings appear? | `knowledge/chronology/neurotheology-attestation-ledger.json` |
| What source class supports a claim? | `knowledge/indexes/source-index.json` |
| What event fields/lenses are allowed? | `docs/TIMELINE-EVENT-STANDARD.md` |

## Maintenance rule

When new dated material is recovered:

1. put the primary evidence in its proper source/evidence owner;
2. add or correct the specialist chronology if needed;
3. promote only trajectory-changing events to the global timeline;
4. connect later interpretation through source direction or related-event IDs;
5. update the canonical owner rather than creating another hand-maintained chronology page;
6. validate the base timeline and all indexed event packs.

The chronology is one temporal graph with multiple evidence-aware views—not a collection of competing timelines.
