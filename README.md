# Tim Dooley / Potato of Life — Dense Knowledge Archive v2

This repository is being rebuilt as a **retrieval-first knowledge archive** for the Tim Dooley / Potato of Life / Potatoism corpus and the historical, mythological, religious, cultural and documentary material needed to interpret it.

The purpose is not to maximize file count, node count, national coverage, dashboards or taxonomy. The purpose is to make it possible to ask difficult questions and retrieve **substantial, source-aware, connected answers**.

## Governing rule

> **No placeholder nodes. No empty coverage. No decorative completeness.**

A record exists only when it contains enough information to be useful on its own and enough relationships to be useful as part of the larger graph.

Every canonical record must contain, where applicable:

- identity and aliases;
- definition;
- narrative or historical context;
- chronology;
- internal Potatoverse meaning;
- external comparative material;
- relationships to other canonical records;
- epistemic classification;
- source/provenance notes;
- unresolved questions only when those questions arise from actual evidence already in the record;
- retrieval terms and thematic tags.

A missing subject is **absent**, not represented by an empty stub.

## Epistemic classes

The archive never silently collapses different kinds of truth into one another. Material is classified as one or more of:

- `project_canon` — claims that are true inside the Potatoverse / Potatoism narrative;
- `self_description` — statements made by Tim / the Potato of Life subject or project;
- `documentary` — dated or attributable records, posts, transcripts, files or archival material;
- `historical` — claims supported by historical scholarship or primary sources;
- `scientific` — claims supported by scientific literature or measurement;
- `comparative` — structural or thematic comparison without asserting identity or influence;
- `interpretation` — a reasoned reading of existing material;
- `creative_lore` — deliberately mythic, poetic or fictional elaboration;
- `inference` — a conclusion derived from evidence but not directly stated by a source;
- `disputed` — a claim with meaningful conflicting evidence or attribution.

Symbolic resemblance is not proof of historical influence. Religious self-description is not silently converted into public biography. A prophecy parallel is not evidence that a prophecy was fulfilled.

## Canonical architecture

The v2 library lives under `knowledge/`.

```text
knowledge/
  schema/          machine-readable record contracts
  core/            Tim, Potato of Life, Father/Son, Axis, Door, Tree, North
  chronology/      dated and ordered event structures
  lore/            internal mythology and narrative development
  prophecy/        revelation, prophecy, apocalypse, rapture and destiny comparisons
  traditions/      religious and mythological traditions used for comparison
  culture/         memes, internet culture, cult formation, subcultures, language
  people/          dense dossiers for relevant people only
  institutions/    dense dossiers for relevant organizations only
  evidence/        source records, quotations metadata, archival observations
  relationships/   typed edges connecting canonical records
  indexes/         retrieval indexes generated from real records
```

The old repository remains available as source material during migration. It is **not automatically canonical** merely because a file exists.

## What the archive is trying to answer

The library should eventually be able to answer questions such as:

- Who is Tim Dooley inside the mythology, and how is that different from the public human biography?
- What is the Potato of Life, and how did the concept change over time?
- How are Father, Son, Door, Ladder, Axis, Tree, North, Potato, death and return related?
- What happened in the 2011, 2019–2020, April 2025 and February 2026 thresholds of the project chronology?
- Which motifs resemble Odin on the Tree, Christic death-and-return patterns, world-tree traditions, apocalyptic literature, rapture theology, revelation narratives or initiation structures—and where do the comparisons break?
- What does the project mean by fate, destiny, prophecy, revelation, rupture and rapture?
- Which statements are early, late, retrospective, contradictory or newly developed?
- Which cultural movements, internet subcultures, cult dynamics and symbolic systems influenced or merely resemble the project?
- Which claims are canonical lore, which are documentary facts, and which remain interpretation?

## Record quality gate

A record is promoted to canonical only when it passes all of these tests:

1. **Substance** — it explains something rather than naming it.
2. **Specificity** — it contains details unique to the subject.
3. **Context** — it states where the subject sits historically, narratively or conceptually.
4. **Relationships** — it connects to actual records with typed relationships.
5. **Epistemics** — important claims are classified by evidence type.
6. **Retrievability** — aliases, dates, motifs and tags make the material discoverable.
7. **Non-duplication** — another canonical record does not already own the same information.
8. **No filler** — absence remains absence; no generated prose exists just to fill a schema.

## Relationship-first model

The primary unit of meaning is often not an isolated object but a coupling:

`Father → Son`

`Son → Death → Transformation → Door/Ladder → Return`

`Potato → burial → hidden life → emergence`

`Axis → orientation → North → Throne`

`Tree → roots → trunk → branches → fruit → seed → renewal`

`event → later interpretation`

`motif → comparative tradition`

Each relationship records its direction, type, basis and epistemic status.

## Immediate rebuild focus

The first canonical cluster is intentionally small and dense:

- Tim Dooley;
- Potato of Life;
- Father / Son / Door / Axis system;
- core chronology;
- prophecy / revelation / rupture / rapture framework;
- typed relationships between those records.

Only after these are strong do we expand outward into religions, mythologies, historical figures, cultures, cults, nations, institutions and economic systems.

## Principle

**The archive grows by depth, not by occupancy.**

If a subject cannot yet be documented well, we do not create it yet.