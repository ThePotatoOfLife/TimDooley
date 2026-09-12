# Placement-First Living Tim Frontend Design

**Date:** 2026-09-12  
**Status:** Approved design direction; implementation pending plan  
**Repository:** `ThePotatoOfLife/TimDooley`

## 1. Purpose

Make the public Potato of Life site feel substantially more like Tim Dooley without turning the site into a larger navigation system, a guided tour, a generic component framework, or a denser encyclopedia.

The project already has the necessary depth in its backend: Tim's questions, public voice, stories, creative work, developmental chronology, religious comparisons, philosophy, science, North Programme, world-repair work, evidence architecture, humor, symbols, transformations and open problems. The public problem is therefore not lack of material. It is **placement**.

The design principle is:

> **Keep the existing structure recognizable. Put each significant piece of material where it belongs best. Promote only the amount that improves understanding.**

The frontend should feel richer semantically, mentally, rhetorically and emotionally while remaining calm, legible and simple.

This design refines the existing five-door public architecture. It does not replace it.

---

## 2. What changed from the earlier design direction

An earlier concept used a shared journey grammar such as:

`question -> encounter -> relation -> transformation -> fruit -> root`

That sequence remains useful as an internal analytical tool, but it must **not** become a public navigation model or a generic UI pattern.

The site already has pages, links, directories, Timeline, Explore, specialist tools and the World Map. Adding another guided sequence on top would make the frontend feel over-designed and would duplicate navigation already present in the project.

The revised rule is therefore:

> **Navigation does navigation. Content does meaning.**

Questions, stories, quotes, transformations, tests, symbols and reflections appear only where they naturally belong. They do not need to lead the reader through a mandatory sequence.

There is no requirement that every page contain the same interaction, the same conceptual stages, or the same Tim symbols.

---

## 3. Core editorial architecture

### 3.1 One natural home

Every significant public-facing idea, story, saying, event, symbol, question, method or programme should have one strongest natural public home.

Examples:

- `A narrow path is a spiral` belongs primarily in Philosophy.
- Tim's long-duration streaming/witness belongs primarily in Tim / Public Witness and secondarily in Timeline.
- Father / Son / Spirit belongs primarily in Religion.
- North-of-North symbolic material belongs primarily in Tim and North.
- empirical North capability, infrastructure and dependency work belongs primarily in North and World Map.
- Vesica geometry belongs primarily on Vesica.
- evidence limits belong primarily in Evidence and source surfaces.

A concept may have contextual appearances elsewhere, but repetition must have a reason.

### 3.2 Contextual appearances are earned

A secondary appearance is justified only when it helps the page explain its own subject.

A page must not repeat a major Tim symbol merely because the symbol is important globally.

For example:

- Science may discuss Door only when a specific model formalizes a state transition or threshold.
- World Map may discuss North only when the distinction between empirical North and project-symbolic North matters.
- Vesica may discuss Father / Son because the geometry uses those centers.
- Tim may mention Father / Son because identity development requires it, but Religion owns the full theological architecture.

### 3.3 Backend importance does not determine frontend size

A concept can be central in the backend and still need only one sentence on a public page.

The public surface should optimize for reader understanding, not for proportional representation of repository volume.

### 3.4 Some material should remain backend-only

Not every interesting record needs public promotion.

Material should remain deep when it is:

- redundant;
- highly technical without public explanatory value;
- too weakly sourced for a prominent surface;
- useful mainly for provenance or research archaeology;
- interpretively narrow;
- better discovered through Explore, Timeline or a specialist tool;
- likely to clutter or distort the page that would host it.

---

## 4. Shared site rules

### 4.1 Preserve the five-door architecture

The homepage keeps exactly five primary public doors:

1. Tim Dooley
2. Religion
3. Philosophy
4. Science
5. World Map

Timeline, North, Vesica, Bible Lab, Explore, Evidence and other specialist surfaces remain secondary/deep routes.

This preserves the existing `frontend-atlas-bridge.json` rule: five simple doors above, one deep archive below.

### 4.2 No generic Living Tim widget

Do not introduce one site-wide component that appears on every page.

There should be no universal:

- quote carousel;
- Tim chatbot;
- symbol strip;
- journey stepper;
- encounter card;
- floating assistant;
- global accordion system;
- generic `question -> answer -> root` widget.

Shared styles and small utilities are acceptable when technically useful, but pages should retain their own editorial identity.

### 4.3 Tim speaks only where Tim is the best voice

The archive narrator remains useful and often clearer.

Direct Tim wording should appear when the wording itself contributes something the archive paraphrase cannot: compression, humor, emotional force, strangeness, historical significance, or distinctive thought structure.

The site must not force Tim's first-person voice into evidence-heavy or technical pages where it weakens clarity.

### 4.4 Provenance-aware voice

Public surfaces must distinguish at minimum:

- **documented Tim wording** — public/first-party wording with strong provenance;
- **recovered Tim wording** — conversation recovery, thought-archive recovery or wording whose public source remains incomplete;
- **project formulation** — Great Book, creative work, archive synthesis or project-derived maxim that is not being claimed as a verbatim public Tim quotation.

Existing granular evidence classes remain canonical in backend owners.

### 4.5 Calm interaction

Interactions should be local and stable.

They must not:

- unexpectedly scroll the page;
- steal focus;
- change browser zoom;
- cause large layout jumps;
- automatically open nested panels;
- alter the World Map camera merely because the reader changed an informational lens;
- introduce hover-only critical content.

On World Map specifically, informational mode changes must not cause camera movement, zoom or refocus unless the user explicitly chooses a map navigation action.

### 4.6 Negative space is a feature

A strong quote, question or strange image may be allowed to stand without immediate over-explanation.

The archive should not surround every Tim formulation with enough taxonomy to eliminate its rhetorical force.

### 4.7 Contrast between surfaces

Different levels of Tim presence are intentional.

- Tim and Philosophy can be highly inhabited.
- Religion can be strongly Timic while remaining comparative.
- North begins symbolically and becomes empirical.
- Science carries Tim's questions but maintains scientific distance.
- World Map primarily embodies Tim's method rather than persona.
- Evidence remains intentionally cool and audit-like.

This contrast makes the whole site feel more alive than repeating the same tone everywhere.

---

## 5. Page-by-page placement contract

## 5.1 Home

### Primary job

Invite the reader into the project without explaining the whole project.

### Keep

- hero;
- short project purpose;
- evidence note;
- exactly five primary doors;
- compact secondary threads;
- Sources and Archive footer routes.

### Change

Refine the wording of each door so the five entries represent different kinds of inquiry, not merely departments.

Home should feel like the threshold to a living archive, but it must remain the simplest page on the site.

### Promote

Only high-compression questions or orientations that help choose a door.

Possible question territory:

- Tim: Who is Tim, and what changed?
- Religion: What is sacred here, and how does it relate to older traditions?
- Philosophy: How does Tim actually think?
- Science: What can be formalized or tested?
- World Map: What becomes visible when relationships matter more than borders?

### Avoid

- Tim timeline detail;
- streaming statistics;
- giant symbol lists;
- theology summaries;
- North membership lists;
- rotating dashboards;
- multiple interactive content blocks.

### Interaction

No new major interaction is required. The five doors are already the interaction.

A single small highlighted question may be considered only if it does not compete with the five doors.

---

## 5.2 Tim Dooley

### Primary job

Let the reader meet Tim as a developing public subject, riddle, identity, witness, builder and later Gardener rather than as a flat biography or list of claims.

### Keep

- current question-led structure;
- Timeline / Public Record / Evidence routes;
- developmental spine;
- identity distinction between Tim/Father and Thomas/Son;
- deeper routes.

### Change

Make the page less dossier-like and more inhabited.

The page should explain what kind of thing Tim is in the archive while allowing actual Tim voice and concrete work to appear where useful.

### Promote

High-value material includes:

- `Tim Dooley is a riddle...` as an archive-reading instruction, with provenance label;
- public witness and streaming as vocation/record rather than statistics alone;
- identity-to-infrastructure pattern: user of Ladder -> Ladder, holder of Axis -> Axis, source-persona -> House/center;
- builder/operator material: archive, systems, maps, models, pages, roads, gardens, world-facing structures;
- mature Gardener/service turn;
- selected direct voice showing cosmic/mundane register switching;
- role synthesis: public person + cultural relation + project theology, kept distinct.

### Natural internal groupings

These are editorial groupings, not necessarily tabs:

- Identity
- Development
- Witness
- Work
- Thought
- Purpose

### Avoid

- duplicating the Religion page's full Father/Son theology;
- duplicating the Timeline;
- turning every Tim title into a card;
- forcing all creative work onto the page;
- presenting recovered wording as verified public quotation.

### Interaction

Prefer ordinary links and small local selectors only where they genuinely improve reading. A compact optional lens switch is acceptable if it changes content in-place and does not move the reader.

---

## 5.3 Religion

### Primary job

Explain Potatoism as religion/theology and place it in serious comparison with older traditions without flattening those traditions into Potatoism.

### Keep

- strong Bible Lab handoff;
- evidence/comparison boundaries;
- Christianity, Judaism, Islam and broader comparative routes;
- question-led format.

### Change

Give the page a more coherent theological center instead of feeling mainly like a list of traditions.

### Promote

- Potatoism: what kind of religious system it is and how it developed;
- God / ultimate reality;
- Father / Son / Spirit;
- Source and manifestation;
- sacred architecture: House, Door, Ladder, Tree, Garden, Axis, Throne, North, Stone, Eye where relevant;
- religious life: cultivation, care, repair, nourishment, service, washing/release, community;
- open disagreements and non-equivalences with Christianity, Judaism, Islam and other traditions.

### Natural subcategories

- Potatoism
- God / Ultimate Reality
- Father / Son / Spirit
- Sacred Architecture
- Religious Life
- Traditions
- Open Questions / Disagreements

These should be concise sections or anchors, not a second mega-navigation.

### Avoid

- full verse-by-verse Bible relations;
- treating every tradition as having the same God category;
- long motif inventories;
- duplicated Vesica deep dive;
- implying comparison proves identity or historical dependence.

### Interaction

Keep the existing Bible Lab as the main deeper interaction. Religion itself should remain primarily readable prose and links.

---

## 5.4 Philosophy

### Primary job

Be the strongest place for encountering how Tim thinks.

### Keep

- inquiry questions;
- sayings;
- recurring ideas;
- Potato Method;
- open questions.

### Change

Reduce homogeneity. Instead of a long sequence of similar quotation blocks, mix forms naturally: saying, question, small story, contradiction, observation, parable, principle.

### Promote

- questioning the floor / another level;
- narrow path / spiral;
- relation before isolation;
- Mud -> Soil;
- Root / shadow / frame-change material;
- reader-as-soil;
- power -> responsibility;
- humor as method;
- absurdity as epistemic pressure-release;
- selected creative/parable material such as the banana argument where provenance and context support it;
- Sisyphus / Ring -> Spiral as a philosophical diagnostic;
- center ethic and Gardener ethic.

### Natural subcategories

- Truth
- Relation
- Identity
- Transformation
- Power
- Humor / Absurdity

These categories guide curation. They do not need to become visible navigation if the page reads better without them.

### Avoid

- turning Philosophy into a glossary;
- reproducing all Tim quotes;
- over-explaining every line immediately;
- using scientific equations as philosophical decoration;
- duplicating Religion's theology.

### Interaction

A restrained `Chew on it` disclosure is appropriate for selected items where it preserves the initial rhetorical impact before revealing the archive interpretation.

No nested accordion architecture.

---

## 5.5 Science

### Primary job

Show what the project can formalize, test, compare or reject scientifically.

### Keep

- searchable science library;
- field and document-type filters;
- strong model/analogy/metaphor distinctions;
- falsifiability and provenance discipline;
- full science documents.

### Change

Reveal the originating question when it improves understanding of why a scientific model exists.

### Promote

- actual Tim-originated or Tim-attributed scientific questions where provenance supports them;
- formalization questions;
- recovered equations with explicit provenance class;
- model assumptions;
- testability and failure conditions;
- distinctions between established equations, archive-derived models and symbolic analogies.

### Natural classifications

Scientific status is more useful than a Timic symbolic taxonomy:

- established result / established science context;
- formal model;
- mathematical analogy;
- testable hypothesis;
- speculative/open problem.

### Avoid

- making Science more mystical;
- presenting theology relabeled as physics;
- repeating Tim symbols unless the scientific document actually formalizes them;
- new controls that duplicate the existing library filters.

### Interaction

Where data supports it, science results may show a compact origin block:

- motivating question;
- formal object;
- scientific status;
- test / unresolved work.

This should be part of the document/result presentation, not another global toolbar.

---

## 5.6 World Map

### Primary job

Apply relationship-first thinking to countries, systems, capabilities, dependencies, time and repair.

### Keep

- map-first architecture;
- compact top navigation;
- search;
- compare;
- inspector;
- typed relationship lines;
- time controls;
- current map camera behavior;
- distinction between empirical and project-symbolic layers.

### Change

Improve the inspector's conceptual questions so a country is understood as a system of relationships rather than a profile card.

### Promote

- `map relationships, not isolated entities`;
- country-state/capability questions;
- dependencies and reciprocal capabilities;
- coupled capability;
- historical change in relationships;
- resilience;
- mechanism-first repair;
- North Programme intervention discipline;
- non-intervention as a legitimate conclusion.

### Natural investigation categories

- Capabilities
- Dependencies
- Relationships
- Trajectory
- Repair

These belong in the inspector context, not the top toolbar.

### Avoid

- constant Potatoverse symbolism;
- turning the map into a North Axis propaganda surface;
- adding a permanent question menu;
- putting policy conclusions ahead of evidence;
- camera movement from informational mode changes.

### Interaction

Changing conceptual inspector views must update only the inspector content. Camera movement occurs only from explicit map navigation actions.

---

## 5.7 Timeline

### Primary job

Show development through time while preserving what happened, what was understood then, what was interpreted later and what later grew from an event.

### Keep

- actor tracks;
- evidence layers;
- Bible/research/creative lenses;
- search;
- year filtering;
- detailed cards;
- source direction;
- URL-shareable state.

### Change

Make major turning points more legible as transformations rather than adding more event volume.

### Promote

- first attestations of major concepts;
- Tim/Son role changes;
- 2011 Tree ordeal;
- 2019/2020 death/Potato corridor;
- 2024 Great Book/Potato development;
- April 2025 turning;
- 2025–2026 Father/House/Axis development;
- North emergence;
- public witness milestones;
- transition from conflict/survival toward building/repair;
- unresolved chronology explicitly marked as unresolved.

### Natural lenses

Potential additional lens/preset only if supported cleanly by existing data:

- Transformations
- First appearances

Existing roadmap/public/Bible/research/creative lenses remain.

### Avoid

- duplicating the Tim page in every event;
- backdating later interpretations;
- treating every symbol appearance as a turning point;
- expanding low-value event detail.

### Interaction

Important event cards may expose compact fields such as contemporaneous meaning, later interpretation and downstream consequence when the canonical event data supports those distinctions.

---

## 5.8 North

### Primary job

Bridge sacred/symbolic North and the empirical North Programme without confusing them.

### Keep

- strong NORTH AXIS identity;
- World Map CTA;
- Programme link;
- membership history/data routes.

### Change

Substantially enrich the page's meaning while keeping it short.

The current North page is too thin relative to the importance of North in the project.

### Promote

- North as symbolic orientation;
- North-of-North / Axis / Seat development;
- the transition from symbolic orientation to empirical research geography;
- Denmark / Greenland anchoring;
- northern/eastern/western European relationship corridor;
- capability/dependency study;
- world-repair programme;
- explicit statement that the North Programme is a research/policy framework, not an existing alliance or government.

### Natural sections

- Meaning
- Geography
- Programme
- Evidence / Map

### Avoid

- giant country lists on the landing page;
- treating project membership as real diplomatic membership;
- mixing symbolic sovereignty with empirical political authority;
- duplicating the World Map inspector.

### Interaction

No complex interaction is necessary. This page should gain richness primarily through better prose and carefully chosen links.

---

## 5.9 Vesica

### Primary job

Explain the geometry and its strongest comparative meaning without losing historical/scientific boundaries.

### Keep

Most of the current page.

Its existing density is justified because it is a specialist deep page and already maintains important boundaries.

### Change

Improve the opening orientation and navigability, not the conceptual volume.

### Promote

One central question more clearly:

> How can two centers remain distinct while participating in one shared field?

This explains why the geometry matters to the project.

### Natural anchors

- Geometry
- Father / Son
- Mandorla / Christianity
- Source / Manifestation
- Body symbolism
- Research boundaries

### Avoid

- new symbolic families;
- turning Vesica into the master explanation of Potatoism;
- universal-secret claims;
- more large diagrams unless a clear reader problem requires them.

### Interaction

Simple anchor navigation is enough.

---

## 5.10 Bible Lab

### Primary job

Let the reader investigate one Bible/project relation at a time with context, chronology, evidence and mismatch visible.

### Keep

- current one-relation-at-a-time browser;
- focus selector;
- order selector;
- search;
- optional filters/results;
- previous/next/random;
- structural arcs;
- evidence/source-direction discipline.

### Change

Improve the internal reading order of a relation rather than expanding outer controls.

### Promote

For high-value relations:

- what happened / what was said;
- scripture;
- why the comparison exists;
- project interpretation;
- literary/theological context;
- discovery date/history;
- source direction;
- mismatch/counter-text;
- alternative explanation;
- provenance.

### Avoid

- another taxonomy layer;
- another persistent toolbar;
- giant all-relations pages;
- presenting later recognition as earlier prophecy.

### Interaction

Keep the front of a relation readable. Deeper context can remain a compact disclosure.

---

## 5.11 Explore

### Primary job

Carry the archive depth that should not burden the public landing pages.

### Keep

- branch navigation;
- archive search;
- relationship-first graph;
- record reader;
- contextual constellations;
- pathways;
- source records.

### Change

Make it easier to follow a concept through its mutations and relations instead of only browsing by branch/file-like structure.

### Promote

- concept histories;
- typed relationships;
- thought archive;
- transformation/mutation sequences;
- source provenance;
- creative/story records where relevant;
- consequences and downstream relations.

### Natural entry modes

Potential reader modes, if implementation remains simple:

- Concepts
- Questions
- Stories / Works
- Relations
- Sources

These must all resolve into the same underlying archive rather than becoming separate databases.

### Avoid

- rebuilding the homepage inside Explore;
- another competing root taxonomy;
- exposing raw repository organization as the public conceptual model.

### Interaction

A selected concept may expose a compact `Follow this thought` view showing origin, mutation, relations and evidence, but only if this can be built from canonical data without duplicating content.

---

## 5.12 Evidence

### Primary job

Audit claims.

### Keep

- distinction between documentary, public/history, function, comparison, prophecy/foresight, relational evidence and metaphysical inference;
- explicit evidentiary limits;
- routes to stronger evidence.

### Change

Make claim/evidence reach even clearer and reduce any temptation to narrativize the page.

### Promote

- source authority;
- exact primary wording;
- recovered-vs-public distinction;
- uncertainty;
- chronology gaps;
- misses and counter-evidence where applicable;
- external verification requirements;
- domain-specific source authority.

### Natural evidence classes

- Documentary
- Historical
- Functional
- Comparative
- Predictive
- Metaphysical

### Avoid

- emotional Tim voice;
- mythology as interface decoration;
- arguments that treat heterogeneous evidence as one proof score;
- hiding gaps because they weaken the narrative.

### Interaction

If filtering is useful, a simple evidence-class selector is enough. The core unit should read approximately:

- claim;
- what supports it;
- what the evidence does not establish;
- what stronger evidence would look like;
- sources.

---

## 6. Placement decision process

When reviewing backend material for promotion, use this order:

1. **What is this material actually about?**
2. **Which public page owns that subject most strongly?**
3. **Does the page already communicate the idea adequately?**
4. **If promoted, what is the smallest form that materially improves the page?**
5. **Does Tim's own wording improve the result, or is archive prose clearer?**
6. **What provenance label is required?**
7. **Does another page genuinely need a contextual appearance?**
8. **Would promotion create repetition, taxonomy noise or conceptual flattening?**
9. **Should the material remain discoverable only in Explore/Timeline/specialist tools?**

The default answer to secondary placement is **no unless useful**.

---

## 7. Subcategory rule

Subcategories are page-local.

Do not force one global taxonomy onto the five doors or specialist pages.

Examples:

- Tim can use Identity / Development / Witness / Work / Thought / Purpose.
- Religion can use Potatoism / God / Father-Son-Spirit / Sacred Architecture / Religious Life / Traditions.
- Philosophy can use Truth / Relation / Identity / Transformation / Power / Humor.
- Science should prefer actual scientific fields and scientific-status classes.
- World Map should prefer capabilities, dependencies, relations, trajectory and repair.
- Evidence should prefer evidence classes.

A subcategory exists only when it improves navigation, comprehension or curation. It must not be created simply because the backend contains enough material to fill one.

---

## 8. Voice-intensity rule

Suggested relative intensity:

- Home: low
- Tim: very high
- Religion: medium-high
- Philosophy: very high
- Science: medium and tightly bounded
- World Map: low persona / high method
- Timeline: medium-high where sourced
- North: medium-high symbolic opening, low empirical programme
- Vesica: medium-low
- Bible Lab: medium, source-dependent
- Explore: low-medium
- Evidence: very low

These are editorial guides, not automatic quotas.

---

## 9. Interaction rule

Use ordinary hyperlinks first.

Add interaction only when it solves a real reading problem.

Preferred interaction forms:

- small in-place selector;
- simple disclosure for secondary explanation;
- anchor navigation;
- existing specialist-tool controls;
- stable inspector mode switch.

Avoid:

- nested accordions;
- automatic carousels;
- hover-only meaning;
- popovers for ordinary prose;
- modal navigation;
- global guided-tour controls;
- duplicated filter systems;
- page re-centering or map camera movement caused by informational selection.

---

## 10. Data and ownership

No new canonical Tim database should be created for this work.

Existing canonical owners remain authoritative.

The existing `data/frontend-atlas-bridge.json` remains the high-level routing/projection contract.

If implementation benefits from a small placement manifest, it must contain only curation metadata such as:

- source owner;
- public home;
- optional contextual surfaces;
- presentation/provenance hint;
- deep route.

It must not duplicate full canonical content.

If the pages can be maintained cleanly without such a manifest, prefer direct page curation plus validation rather than adding infrastructure for its own sake.

---

## 11. Validation requirements

Future implementation should extend reader-surface validation without making exact prose canonical.

Durable checks should include:

- homepage still has exactly five primary doors;
- public pages retain existing `data-reader-surface` identities;
- no page exposes raw backend file paths as primary navigation;
- Tim/Father vs Thomas/Son distinction remains present where required;
- direct/recovered/project voice is not visually flattened;
- World Map informational controls do not call camera-fit/zoom functions unless explicitly map-navigational;
- North clearly distinguishes symbolic/project geography from real alliance/government status;
- Science preserves model/analogy/metaphor/evidence boundaries;
- Bible Lab continues consuming canonical Bible relations rather than raw research waves;
- Evidence continues expressing uncertainty and limits;
- deeper routes remain available to Explore/Timeline/specialist pages;
- JavaScript enhancement has a readable no-JS/default state wherever practical.

Tests should validate semantics and structure rather than exact paragraph wording.

---

## 12. Implementation order

Implementation should proceed in editorial waves rather than rewriting all public pages in one pass.

### Wave 1 — establish the voice and placement standard

- Tim
- Philosophy

These pages have the highest Tim voice and will reveal whether the richer treatment feels alive rather than cluttered.

### Wave 2 — theology and world-facing transition

- Religion
- North

These pages test whether symbolic Tim material can remain rich while making clear transitions into comparative religion and empirical programme work.

### Wave 3 — disciplined application

- Science
- World Map

These pages require the greatest restraint and test whether Timic questions/method can be visible without weakening scientific or empirical credibility.

### Wave 4 — developmental/deep tools

- Timeline
- Explore

These receive richer concept histories and transformation context only where existing canonical data supports it.

### Wave 5 — light-touch refinements

- Home
- Vesica
- Bible Lab
- Evidence

These pages are already structurally strong and should receive only targeted improvements.

---

## 13. Success criteria

The design succeeds when:

- the site remains immediately recognizable to an existing reader;
- the five-door public structure is unchanged;
- pages feel less generic and more specifically Tim Dooley;
- a reader encounters Tim's actual questions, voice, stories, development and work in the places where they matter;
- the same symbols are not mechanically repeated across all pages;
- philosophy feels more lived and strange without becoming chaotic;
- religion feels more theological and comparative without becoming an encyclopedia;
- science feels more connected to its motivating questions without becoming pseudo-scientific;
- World Map feels more like relationship/capability/repair thinking without becoming ideological clutter;
- North becomes meaningfully connected to the larger project while preserving empirical boundaries;
- Timeline better shows development rather than simply accumulating events;
- Evidence becomes clearer rather than more rhetorical;
- backend depth remains available without forcing all of it into the public layer;
- interaction remains calm and stable;
- no major addition exists merely because it was possible to add it.

The final standard is:

> **The frontend should feel like the richest possible expression of Tim that still feels simple.**

And the pruning test is:

> **If a piece of material is important but does not improve the page where it is placed, move it deeper rather than making the page carry it.**
