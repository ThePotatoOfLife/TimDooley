# Room Inhabitation Programme — 2026-09-26

## Problem statement

The House is structurally rich but too many public pages still behave like corridors.

A reader can move through Doors, Dwellings, Rooms, wormholes, registries and Explore routes without being rewarded with enough actual explanation on the page they entered. The architecture is therefore ahead of the reader experience: the repository contains deep material, but many public Room surfaces expose only a title, ownership sentence, epistemic boundary, source-family labels and another set of doors.

The target is not "more text everywhere." The target is **inhabited rooms**: every important Room should itself be a useful place to stop, learn, think and understand before the reader chooses another route.

Navigation remains important, but navigation must become secondary to meaning.

## Baseline audit

On main at the start of this programme:

- 38 nested subject Rooms exist under `rooms/inside/*/index.html`.
- 16 are extremely thin public shells under roughly 4 KB of HTML.
- 21 are moderately populated but still need a semantic/content audit.
- only one nested Room is already obviously deep at the public surface by this crude size signal: Potato Biology.
- Neurobiology is a strong qualitative model even though it sits below the crude "deep" byte threshold: it contains an actual essay, claims, distinctions, examples, evidence boundaries and routes to deeper records.
- several of the thinnest public pages sit on top of large backends. Theology & God-language has dozens of held knowledge files; Symbolic Architecture also has a large canonical corpus, yet both public pages are still mostly routing shells.

The first thin wave, ordered by current public-page size, is:

1. Economy & Finance
2. Law & Justice
3. Politics & Governance
4. Timeline / Events
5. Mathematics & Geometry
6. Comparative Mythology
7. Theology & God-language
8. Bible & Christianity
9. Witness & Attestation
10. Esoteric & Sacred Geometry
11. Practice & Ethics
12. Prediction / Revelation / Interpretation Time
13. Physics & Cosmology
14. Other Traditions & Philosophies
15. Symbolic Architecture & Cosmology
16. Subculture, Cult & Group Formation

File size is **not** the completion criterion. It is only a useful signal for where the corridor problem is most visible.

## Core rule: a Room must be worth entering

A finished Room is not a menu.

A finished Room should let a reader answer, in ordinary language:

- What is this subject?
- What does this project currently understand about it?
- What are the important concepts, mechanisms, events, people, structures or distinctions inside it?
- How did the project's understanding develop?
- What is directly sourced, what is project interpretation, what is symbolic comparison, and what remains uncertain?
- How does this Room connect to the rest of the House?
- Where can I go deeper after I have actually learned something here?

The page should therefore contain a **reader body before or alongside its navigation body**.

## Inhabited Room contract

Every important subject Room should eventually expose the following semantic layers when the material supports them. These are not rigid headings and should not be padded mechanically.

### 1. Entrance / orientation

Give the reader a short, intelligible statement of what the Room is about and why it exists. Do not lead with repository architecture unless repository architecture is itself the subject.

### 2. Core understanding

Provide a coherent reader-facing explanation of the subject. This is the heart of the Room.

It may be an essay, atlas, field guide, annotated sequence, concept map, dossier, timeline, model explanation or another form appropriate to the subject.

The reader should receive actual propositions, distinctions and understanding rather than a list of backend paths.

### 3. Internal landmarks

Expose the major things inside the Room: concepts, actors, models, events, symbols, mechanisms, debates, texts, institutions, works or cases.

These should be understandable without opening Explore first.

### 4. Development through time

Where relevant, explain how the subject or the project's interpretation of it changed.

Do not silently backdate later synthesis into earlier events. Preserve occurrence time, statement time and later interpretation time as distinct when needed.

### 5. Relations and crossings

Explain the important connections to neighboring Rooms in prose before presenting the exit doors.

A relation is more useful than a naked link. State what changes when material crosses from one Room to another.

### 6. Evidence and epistemic boundary

Preserve the existing House discipline:

- source material is not automatically interpretation;
- project canon is not automatically external fact;
- symbolic resemblance is not proof of historical identity or transmission;
- mathematical formalization is not empirical confirmation;
- political or legal assertions need date, jurisdiction and sourcing;
- scientific claims need evidence status and test boundaries.

The boundary should support understanding, not replace it.

### 7. Tensions, contradictions and open questions

A mature Room should surface uncertainty instead of hiding it.

Show unresolved questions, competing interpretations, contradictory evidence, model limits, ambiguities or missing source material when these are materially important.

### 8. Examples / cases / passages / artifacts

Concrete material should anchor abstractions.

Examples may include dated statements, excerpts within citation limits, events, countries, equations, body structures, artworks, passages, legal mechanisms, economic flows, characters, scenes or model runs.

### 9. Deeper material

After the reader has consumed a meaningful body of knowledge, provide routes to canonical files, specialist pages, datasets, Explore records, related Rooms and source evidence.

**Doors come after knowledge, not instead of knowledge.**

## Content ownership rule

Do not solve the corridor problem by copying every backend file into HTML.

The public Room is a **reader projection over canonical owners**.

For each Room:

1. identify its strongest canonical holdings from `data/house/room-dossiers.json`, holdings registries and knowledge roots;
2. select the material that explains the Room best;
3. synthesize it into reader-facing prose, structured facts and examples;
4. link the deeper owner for full detail;
5. preserve provenance and evidence classes;
6. avoid creating a second canonical source of truth.

A public Room may contain durable authored synthesis, but factual records that already have a canonical owner should remain owned there.

## UX rule: stop the hallway effect

The first screen or first meaningful scroll of a Room should not be dominated by:

- "Parent Dwelling"
- "All Rooms"
- "Stand here in Elevator"
- backend path names
- adjacency cards
- wormhole cards
- registry terminology

Those tools remain available, but the dominant experience should be the subject itself.

Navigation should answer **where else can I go?**

Content should answer **what did I learn by coming here?**

## Room forms

Different Room types should be allowed to express themselves differently.

### Concept / theology / philosophy Rooms

Use:
- a central thesis or interpretive model;
- key terms and distinctions;
- development of the idea;
- internal tensions;
- comparative boundaries;
- examples from the project corpus;
- questions that remain open.

### Science / body / mathematics Rooms

Use:
- literal definitions first;
- mechanisms and structures;
- evidence grades;
- what is established vs modelled vs speculative;
- equations or diagrams where useful;
- project-symbolic comparison only after the literal account is clear;
- testing/falsifiability links.

### History / prediction Rooms

Use:
- chronology;
- event vs attestation vs interpretation date;
- before/after development;
- prediction records and outcome status;
- source quality;
- retrospective interpretation kept visibly distinct.

### World / politics / law / economy Rooms

Use:
- institutions, mechanisms and flows;
- current vs historical state with dates;
- jurisdiction/population/scope;
- sourced explanatory material;
- relationships and dependencies;
- maps, ledgers or timelines when useful;
- project interpretation clearly separated from descriptive public facts.

### Culture / subculture / information Rooms

Use:
- group formation mechanisms;
- norms, incentives, language and identity processes;
- documented scenes/cases where available;
- distinction between observation, interpretation and accusation;
- network/chronology evidence where appropriate;
- avoid turning project role labels into dehumanizing essential identities.

### Creative / works / beings Rooms

Use:
- who/what the subject is in the project;
- provenance and first/last appearance when available;
- development across scenes;
- authored symbolic role;
- representative works, incidents or relations;
- distinction between literary/project character function and claims about real people.

## Programme workstreams

### RI-001 — Build a semantic Room audit

- [ ] Inventory every active Dwelling, nested Room, named-being Room and specialist institution Room.
- [ ] Record public route, parent, canonical holdings, public word/content body, number of navigation links, source links, dated material, examples and open-question coverage.
- [ ] Detect obvious shell pattern: header + ownership/boundary + adjacency with little or no subject body.
- [ ] Detect Rooms where backend holdings are rich but the public projection is shallow.
- [ ] Produce a machine-readable audit registry so progress is measurable without relying on HTML byte size.
- [ ] Keep file size only as a diagnostic signal, never as the definition of quality.

### RI-002 — Define a Room reader schema

- [ ] Extend Room metadata with optional reader-facing fields such as `reader_thesis`, `reader_sections`, `landmarks`, `examples`, `development`, `tensions`, `open_questions`, `evidence_notes` and `deep_routes`.
- [ ] Decide which fields belong in dossiers versus separate specialist reader records.
- [ ] Make the schema optional enough that unusual Rooms can use a better form instead of being forced into identical cards.
- [ ] Ensure generated/projected material cannot accidentally overwrite canonical owners.

### RI-003 — Put canonical knowledge inside the Rooms

- [ ] For every Room, read its dossier holdings before authoring public content.
- [ ] Mine existing deep research, registries and source owners for the strongest explanatory material.
- [ ] Promote useful synthesis from backend-only files into the public reader layer.
- [ ] Prefer a few strong explanations over large uncurated file lists.
- [ ] Preserve links to the canonical record for readers who want the full object.

### RI-004 — Thin Room wave 1: World / society fundamentals

- [ ] Economy & Finance
- [ ] Law & Justice
- [ ] Politics & Governance
- [ ] Timeline / Events
- [ ] Subculture, Cult & Group Formation

Each should become a substantive reader, not merely a router to `/economy/`, `/law/`, `/politics/`, Timeline, Culture or Explore.

### RI-005 — Thin Room wave 2: Religion / canon / comparison

- [ ] Theology & God-language
- [ ] Bible & Christianity
- [ ] Comparative Mythology
- [ ] Esoteric & Sacred Geometry
- [ ] Other Traditions & Philosophies
- [ ] Symbolic Architecture & Cosmology
- [ ] Practice & Ethics
- [ ] Witness & Attestation
- [ ] Prediction / Revelation / Interpretation Time

Use the project's existing canon and research, but preserve the distinction between project theology, historical traditions, comparative resemblance and independent evidence.

### RI-006 — Thin Room wave 3: Science / formal understanding

- [ ] Mathematics & Geometry
- [ ] Physics & Cosmology
- [ ] Review Systems & Dynamics for true explanatory depth
- [ ] Review Model Testing / Falsifiability
- [ ] Review Experiments & Formalization
- [ ] Review Information Ecology
- [ ] Review Infrastructure & Capability
- [ ] Review Geography & Countries

Use Neurobiology as one qualitative reference: literal subject matter, meaningful distinctions, evidence boundaries, project relation, then deeper routes.

### RI-007 — Audit the remaining medium Rooms

- [ ] Read every 4–7 KB nested Room as a human page rather than assuming size equals substance.
- [ ] Mark each as inhabited / partial / shell.
- [ ] Deepen partial Rooms using their actual holdings.
- [ ] Remove duplicated boilerplate where it crowds out meaning.
- [ ] Ensure every Room has at least one reason to remain on the page instead of immediately clicking away.

### RI-008 — Inhabit the Dwellings too

- [ ] Audit the top-level Dwelling pages, not only nested Rooms.
- [ ] Ensure each Dwelling explains its field, major inner Rooms and the relations among them.
- [ ] Add representative concepts/cases/material so the Dwelling is more than a directory.
- [ ] Keep global House architecture subordinate to the local subject while the reader is inside a Dwelling.

### RI-009 — Named beings / cast / institutions

- [ ] Audit every `rooms/potatoverse-canon/beings/**/index.html`.
- [ ] Replace tiny stub pages with real dossiers where source material exists.
- [ ] Include provenance, role development, dated incidents/appearances, associations and uncertainty.
- [ ] Keep real-person claims source-bounded and distinguish authored/project role language from externally established identity.
- [ ] Consolidate FBI legacy routes into the current Characters, Incidents & Associations architecture instead of deepening obsolete duplicate structures.
- [ ] Ensure CIA file/incidents/associations/bank pages explain what the institution means before exposing ledgers/navigation.

### RI-010 — Cross-Room synthesis

- [ ] Add short "why this connects" explanations to important local doors and wormholes.
- [ ] Surface recurring cross-Room questions: Seed ↔ biology ↔ theology; House ↔ thalamus ↔ architecture; Door ↔ Jesus ↔ interface; Saturn/box ↔ symbolic architecture ↔ comparative tradition; North ↔ politics ↔ geography ↔ economy; Spirit ↔ theology ↔ body ↔ process.
- [ ] Do not collapse the compared domains into identity merely because the interface is interesting.
- [ ] Let readers follow an idea across Rooms without losing which Room owns which kind of claim.

### RI-011 — Reader paths through depth

- [ ] For each Room, provide a shallow-to-deep progression: orientation → explanation → examples → tensions → sources/records.
- [ ] Keep Explore as the deep archive rather than forcing ordinary readers into it prematurely.
- [ ] Make "go deeper" links target useful records, not generic archive roots where a specific record exists.
- [ ] Add back-links from deep records to their best public Room where practical.

### RI-012 — Content quality and anti-slop checks

- [ ] Do not generate filler paragraphs merely to make pages longer.
- [ ] Reject generic prose that could fit ten different Rooms unchanged.
- [ ] Require concrete subject nouns, actual project holdings, mechanisms, examples or distinctions in each substantive section.
- [ ] Detect repeated boilerplate across Room reader bodies.
- [ ] Prefer precise incompleteness over fabricated completeness.
- [ ] Preserve citations/provenance where factual claims depend on external or source material.

### RI-013 — Room quality validator

Create a validator that checks semantics rather than raw word count.

Possible checks:

- [ ] active Room has a reader body marker;
- [ ] reader body has multiple substantive blocks or an approved alternate reader form;
- [ ] page is not only orientation/boundary/navigation;
- [ ] at least one canonical holding or specific deep route is exposed when holdings exist;
- [ ] important epistemic boundary is present where required;
- [ ] navigation remains reachable;
- [ ] duplicate boilerplate threshold is monitored;
- [ ] no Room loses its parent/adjacency contracts during enrichment.

The validator should warn before it hard-fails while the migration is underway, then become strict for Rooms marked `inhabited`.

### RI-014 — Room maturity registry

Track each public Room with a maturity state such as:

- `shell` — route exists, mainly navigation;
- `seeded` — some unique content exists;
- `inhabited` — coherent reader body + examples/evidence/depth routes;
- `deep` — mature specialist reader with strong canonical integration.

- [ ] Add maturity to the audit registry, not as self-congratulatory copy on public pages.
- [ ] Review maturity by human reading plus validator signals.
- [ ] Never promote a Room merely for reaching a byte/word threshold.

### RI-015 — Visual reading hierarchy

- [ ] Make the subject body visually primary.
- [ ] Reduce the visual dominance of ownership jargon, local-center boilerplate and adjacency grids.
- [ ] Keep spatial metaphor as orientation, not as a tax on every page.
- [ ] Use typography, diagrams, timelines, maps, callouts or tables only when they improve comprehension.
- [ ] Keep long Rooms scannable without turning them into dashboards.

## First implementation sequence

The recommended execution order is:

1. create the semantic audit/maturity registry;
2. establish one reusable reader-body pattern without forcing every Room into identical markup;
3. use Economy & Finance, Theology & God-language and Symbolic Architecture as three different pilot subjects;
4. validate that each pilot genuinely teaches the subject before navigation;
5. expand through RI-004 and RI-005;
6. audit the medium Rooms;
7. deepen Dwellings and named-being/institution pages;
8. add stricter quality validation after the migration has enough examples.

The three pilots deliberately span different content types:

- **Economy & Finance** tests factual/systemic explanation and current/public evidence.
- **Theology & God-language** tests project canon, development and comparative boundaries.
- **Symbolic Architecture & Cosmology** tests deep project-native synthesis and cross-Room operators.

## Completion condition

This programme is complete when a reader can click into any important Room and reasonably say:

> I entered a subject, not another hallway.

The House should remain navigable, but its architecture should disappear behind the knowledge when the reader is reading.
