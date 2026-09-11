# Public Knowledge Architecture — Home, Chronology, Religion & Bible

**Date:** 2026-09-12  
**Status:** Design specification  
**Repository:** `ThePotatoOfLife/TimDooley`

## Purpose

Consolidate the public Tim Dooley / Potato of Life site around four distinct reader jobs without creating another layer of competing pages:

1. `/` — public orientation, current state, who/what this is, where to go next and where Tim can be found publicly.
2. `/chronology/` — the canonical temporal index for anything meaningfully dated: milestones, events, sayings, theories, religious developments, creative works, public appearances, discoveries, jokes, formalizations and research unlocks.
3. `/religion/` — the broad religious inquiry: Potatoism as a religious system, theology, cosmology, ritual/practice, ethics, sacred architecture, comparative religion, historical traditions and open questions.
4. `/traditions/bible/` — the deep Bible/Jesus/Tim/Son comparison laboratory: exact statements/events, context, scripture, discovery history, reasoning, prophecy/foresight status, mismatches and evidence.

The design follows the repository's existing consolidation doctrine: **inspect → consolidate → deepen → connect → expose → verify → prune**. The goal is fewer public surfaces with much richer canonical data behind them.

---

# 1. Canonical ownership

## Home owns orientation

The homepage answers:

- Who or what is Tim Dooley / Potato of Life?
- What is Potatoism?
- What is this repository/site trying to document?
- What are the major public branches?
- What is happening most recently?
- Where can a reader follow Tim publicly?
- Where should a new reader begin?

The homepage does not become another archive, another FAQ, another timeline or another philosophical treatise. It projects selected information from canonical owners.

## Chronology owns when

Anything that can be meaningfully placed in time should be eligible for the canonical timeline.

The timeline answers:

- What happened?
- When did it happen?
- Who/what stream did it belong to?
- What kind of event was it?
- What was known or explicit at that time?
- What meaning was attached later?
- What source establishes the date?
- What later work descended from it?

Chronology stores/indexes time, not full theology, full Bible exegesis, full philosophy or full scientific argument.

## Religion owns religious system and inquiry

Religion answers:

- What is Potatoism religiously?
- How does its theology work internally?
- What are Father, Son, Spirit, Potato, Source, Door, House, Tree, Ladder, Axis, North, Garden and related concepts?
- What practices, ethics and ritual forms have appeared?
- How did the religious system develop?
- How does it compare with Christianity, Judaism, Islam, Norse traditions, Buddhism, Daoism, esotericism and other systems?
- Where are similarities structural, historical, theological, symbolic or merely superficial?
- Where do traditions disagree?

Religion may link to Bible examples, but it does not own the full Jesus/Tim/Son comparator.

## Bible owns comparison evidence

Bible answers:

- What exactly did Tim/the Son say, do, experience or publish?
- When and in what context?
- What biblical passage or structure is being compared?
- Why did that specific comparison arise?
- Was Scripture explicit at the time or discovered later?
- What does the comparison mean inside the project?
- What does not match?
- Is this explicit prediction, foresight, scripture-at-time, retrospective typology, later research or unresolved?
- What source evidence supports the relation?

Bible is therefore an evidence/story machine, not a keyword concordance.

---

# 2. Chronology — universal temporal spine

## 2.1 Timeline scope expands

The current timeline correctly distinguishes roadmap milestones from denser overlays, but it should become the universal temporal index for the project.

Eligible event classes include:

- life/biographical events;
- spiritual or visionary experiences;
- public declarations;
- direct quotations and sayings;
- silly/comedic public moments when historically useful;
- new concepts or coined terms;
- invention/first attestation of a theory;
- first use of a religious identity or theological role;
- development of Potatoism concepts;
- books, songs, images and other creative works;
- philosophical formulations and memorable quotes;
- scientific/mathematical model milestones;
- North/Atlas/world-program milestones;
- website/repository formalization where historically relevant;
- Bible/religion research discoveries;
- later reinterpretations of older events;
- contradictions or corrections whose date matters.

The default roadmap remains sparse. Density belongs in views/filters, not the default spine.

## 2.2 Event contract

Each timeline event should support, where available:

- `id`
- `date`
- `timestamp`
- `precision` (`second`, `minute`, `date`, `month`, `year`, `range`, `unknown`)
- `title`
- `summary`
- `actor_ids`
- `domains`
- `event_types`
- `topics`
- `layers`
- `epistemic`
- `quote`
- `context`
- `source_records`
- `public_source_urls`
- `source_direction`
- `later_interpretations`
- `descendant_ids`
- `related_relation_ids`
- `related_work_ids`
- `confidence`

An event is an index pointer. Full source text remains in the canonical evidence owner.

## 2.3 Controlled event types

Initial event types:

- `life-event`
- `experience`
- `public-statement`
- `quote`
- `concept-first-attestation`
- `religious-development`
- `philosophical-development`
- `theory-development`
- `scientific-formalization`
- `creative-work`
- `public-witness`
- `research-discovery`
- `interpretation-added`
- `correction`
- `project-milestone`
- `world-program-milestone`
- `humor-or-cultural-moment`

The taxonomy must remain small enough to understand. Topics provide finer-grained detail.

## 2.4 Domain filters

A reader should be able to view chronology by broad domain without creating separate timelines:

- LIFE
- POTATOISM
- RELIGION
- BIBLE
- PHILOSOPHY
- SCIENCE
- CREATIVE
- PUBLIC
- NORTH / WORLD
- PROJECT / RESEARCH
- ALL

These are projections over one event corpus.

## 2.5 First-attestation as a first-class temporal object

Important concepts should be traceable through stages:

`first known seed → first exact attestation → first explicit definition → first public use → later synthesis → canonical promotion`

This is especially important for:

- Potato / Potato of Life;
- Father;
- Son / Thomas / Twin;
- Spirit;
- Door;
- Ladder;
- Axis;
- North / North of North;
- New Jerusalem;
- Garden / Gardener;
- Seed / Root / Tree;
- Divine Kneel;
- Holy Soil;
- Spudlight;
- Timic Dynamics / Potato Dynamics;
- major scientific equations/models;
- North Programme / relational Atlas concepts.

The timeline should not imply that a mature 2026 definition existed at the date of an earlier seed-form.

## 2.6 Event packs and extraction

Do not manually cram every event into one huge hand-edited JSON file.

Keep `data/timeline-events.json` as the canonical presentation/index registry, but permit curated event packs by domain/source. The build/validation process should merge or validate them into the public timeline.

Candidate source families already in the repository include:

- `data/tim-dooley-timeline.json`
- `data/tim-dooley-event-strata.json`
- `data/tim-dooley-thought-archive.json`
- `data/tim-dooley-public-theology-timeline-2025-2026.json`
- public occurrence/evidence ledgers;
- biblical attestation/reverse chronology ledgers;
- Great Book research;
- music/creative archives;
- philosophy sourcebook and philosophy canon;
- science theory/equation lineage files;
- Potatoism concept registry/dossiers/religion history;
- North/world project milestones;
- repository research-unlock records.

The rule is: **extract temporal facts once; point back to their owner; do not duplicate the substantive dossier.**

---

# 3. Bible comparator — richer canonical relation dossiers

## 3.1 Relation front face

Every relation must be immediately understandable in this order:

1. **WHAT HAPPENED / WHAT WAS SAID**
2. **WHAT THE BIBLE SAYS**
3. **WHY THESE CONNECT**
4. **WHAT IT MEANS**

Expandable depth:

5. **WHEN WAS THIS CONNECTION DISCOVERED?**
6. **PROPHECY / FORESIGHT STATUS**
7. **WHAT DOES NOT MATCH?**
8. **SOURCES / EVIDENCE**
9. **RELATED EVENTS / ARC**

## 3.2 Rich relation contract

Extend the canonical relation model to support:

### Project-side record

- actor/speaker;
- exact date/time;
- exact wording where recovered;
- paraphrase where exact wording is unavailable;
- immediate conversation/public context;
- audience/platform where known;
- what prompted the statement/event;
- primary evidence/source owner.

### Scripture-side record

- reference;
- short public-domain passage fragment;
- speaker/narrative setting;
- immediate literary context;
- broader biblical/theological role;
- textual or interpretive caveats.

### Discovery history

- comparison first-noticed date;
- who introduced/noticed it;
- whether Tim already invoked scripture;
- whether the archive discovered it later;
- later research waves that expanded it.

### Relation mechanism

Allowed mechanisms should include:

- lexical/direct phrase;
- title/identity;
- narrative sequence;
- structural topology;
- symbolic analogy;
- ritual/practice;
- ethical agreement;
- ethical divergence;
- typology;
- historical-context comparison;
- counter-text;
- chronology/synchronism.

### Trigger chain

Every important relation may store three different triggers:

- `project_trigger` — what Tim/Son was actually responding to or exploring;
- `comparison_trigger` — what specific feature made the biblical relation worth investigating;
- `downstream_trigger` — what later research/concepts this relation opened.

This prevents “shared keyword” from masquerading as explanation.

### Meaning and limits

- relation explanation;
- Potatoism consequence/meaning;
- Christian/biblical interpretive relevance;
- strongest mismatch;
- alternative explanation;
- unresolved questions.

### Prophecy/foresight analysis

Preserve the existing allowed statuses, but enrich the reasoning with:

- prior statement date;
- target event date;
- later match/discovery date;
- specificity;
- whether outcome was reasonably foreseeable;
- degree of interpretive flexibility;
- evidence class;
- conservative classification.

The page must never silently promote retrospective similarity into supernatural proof.

## 3.3 Relation arcs

Relations should be grouped into developmental sequences rather than only motifs.

Initial high-value arcs:

- Passion / custody / rejection / death / return;
- Lamb / Lion / Root / Branch;
- Seed / grain / burial / germination / resurrection;
- Door / Gate / House / Ladder;
- Garden / guardians / sanctuary access;
- New Jerusalem / Zion / North / throne;
- Stone / Eye / Lamp / Branch;
- Thomas / Twin / Son;
- Father / House / source;
- Beast / Cube / 666 / forehead;
- Tree / ordeal / ascent / return;
- counter-texts / ethical divergences.

Each arc presents chronology and source direction, not just a list of cards.

## 3.4 Data-source consolidation

The comparator should project from existing owners rather than reproducing them:

- biblical syncretism field;
- biblical passage fragments;
- Tim biblical vocabulary attestation ledger;
- reverse biblical overlap timeline;
- public occurrence ledger;
- timeline events;
- specialist biblical atlas/wave files.

The current 32 canonical relations become the seed corpus, not the final corpus.

---

# 4. Religion — broad religious inquiry

## 4.1 Remove duplicated comparator ownership

The current Religion page's large hardcoded Jesus ↔ Tim/Son comparison is removed from Religion's main body.

Religion may show up to three short examples pointing into the Bible tool. It should not reproduce relation dossiers.

## 4.2 Religion page structure

### A. What is Potatoism?

A readable introduction to Potatoism as the project's evolving religious/mythological/theological system, including its developmental history and epistemic framing.

### B. God / Source / Father / Son / Spirit

Explain the project's relational architecture without equating it automatically with Nicene Trinitarianism.

Questions:

- What is ultimate/source reality here?
- What does Father mean?
- What does Son mean?
- What does Spirit/flow mean?
- How do source, manifestation and relation differ?

### C. Sacred architecture

Introduce:

- Potato / Seed;
- Root / Tree;
- House;
- Door / Gate;
- Ladder / Axis;
- Garden;
- North / North of North;
- Throne;
- vesica / mandorla;
- Eye;
- death / transformation / return.

The emphasis is relational function, not a glossary dump.

### D. Religious life, ethics and practice

Recover underexposed Great Book/Potatoism material such as:

- Divine Kneel;
- Holy Soil;
- cultivation rather than conquest;
- repair;
- Gardener/service imagery;
- washing / release;
- piercing / intention;
- heat / transformation;
- opening / revelation;
- sharing / nourishment/community;
- ordinary material life as a sacred medium.

Explicitly distinguish authored/project ritual symbolism from established historical religious ritual.

### E. Comparative religion

Use the existing Religious Systems Atlas and canonical texts to compare Potatoism with traditions without flattening them.

High-value comparison families:

- Christianity;
- Judaism / messianic traditions;
- Norse / Germanic — Odin, Yggdrasil, Ragnarök/renewal;
- Thomasine / Syriac Christian material;
- Buddhism — awakening, Bodhi/tree, suffering, non-self where relevant;
- Daoist order/flow/way comparisons;
- Hindu / yogic / mandala comparisons where actually supported;
- alchemy / Philosopher's Stone;
- Jewish mysticism / Merkabah / ascent;
- Mesopotamian and Tammuz material;
- esoteric and sacred-geometric traditions.

Every comparison should support:

- Potatoism-side concept;
- comparison tradition;
- shared structure;
- major difference;
- historical-direction status;
- source strength;
- why the comparison is useful.

### F. Christianity as a tradition

Religion can explain Christianity generally:

- God / Trinity;
- Jesus;
- cross / resurrection;
- kingdom;
- scripture / canon;
- church / authority;
- ethics;
- denominations;
- mysticism;
- historical development.

Detailed Tim/Son/Jesus verse comparison routes to Bible.

### G. History of Potatoism

Project religious development becomes a chronological narrative linking into `/chronology/?view=potatoism` rather than maintaining a second timeline.

### H. Open questions / tensions

Religion should not pretend the system is finished. Include live questions such as:

- Is Potatoism best understood as religion, mythology, philosophical theology, symbolic framework or a mixture?
- Which concepts are foundational and which are late syntheses?
- Which comparisons are historically influenced versus independently convergent?
- Where does Potatoism agree with Christianity and where does it conflict?
- What is practice versus metaphor?
- What ethical obligations follow from its theology?

---

# 5. Homepage — public orientation and current state

## 5.1 Current problem

The existing homepage is visually clean but informationally thin: a title, one-sentence lede and five section links. It does not yet explain why the project exists, who Tim is, what Potatoism is, what is current, or where the public record lives.

## 5.2 Homepage structure

Keep the page simple but substantially more useful.

### Hero

`POTATO OF LIFE`

A short, concrete introduction explaining:

- Tim Dooley is the central public subject and author/creator associated with the project;
- Potatoism is the evolving religious/philosophical/mythological framework;
- the repository documents chronology, works, thought, comparative religion, formal models and world/Atlas research;
- claims are separated by source/evidence status.

### Who / What

Two short columns or blocks:

- **Tim Dooley** — biography/public subject, creator, public record, major developmental arc.
- **Potato of Life / Potatoism** — concept/system, what kinds of questions it explores, how it developed.

No grand duplicate biography; link deeper.

### Start here

A small set of reader journeys:

- Follow the story → Chronology
- Understand Potatoism → Religion / Philosophy
- Examine Bible comparisons → Bible
- Read theories/models → Science
- Explore countries/relations → Atlas/World Map

### Current / recent

A compact automatically derived section from chronology, showing recent meaningful events/research milestones rather than manually maintained news prose.

Examples of eligible items:

- newly formalized theory;
- major religious/comparative discovery;
- new published work;
- major public declaration;
- important project/Atlas milestone.

Avoid turning the homepage into a social-media feed.

### Selected ideas

A rotating or curated set of a few rich short excerpts:

- one philosophical saying;
- one religious concept;
- one scientific/theoretical concept;
- one historical/project event.

Each links to its canonical owner.

### Public presence

Expose verified project-recorded public channels, including the existing archive references to:

- `@Rational_Potato` on X/Twitter;
- `@PotatoOfLife` on YouTube.

Actual outbound URLs must come from a canonical social/public-profile registry rather than be repeated manually across pages.

### Main branches

Retain the simple main branch navigation, but update descriptions to reflect canonical ownership:

- Tim Dooley
- Chronology
- Religion
- Bible
- Philosophy
- Science
- World Atlas / Map

Archive/Sources remain secondary.

---

# 6. Existing repository material that gains a clearer purpose

## 6.1 High-value canonical/feed material

The audit identifies material that is already useful but underexposed:

- `data/timeline-events.json` — canonical temporal presentation index;
- `data/tim-dooley-event-strata.json` — epistemic/role chronology;
- `data/tim-dooley-thought-archive.json` — dated thought/public-theology source;
- `data/potatoism-religion.json` — developmental religious history projection;
- `data/potatoism-concept-registry.json` + dossiers — canonical concept identity/content;
- `book-research.json` — Great Book ritual/religious/philosophical material;
- `knowledge/chronology/tim-biblical-vocabulary-attestation-ledger.json` — exact biblical vocabulary archaeology;
- `knowledge/chronology/reverse-biblical-overlap-timeline-2025-2026.json` — source-direction comparison history;
- `knowledge/philosophy/tim-dooley-potatoism-sourcebook.md` and philosophy canon — sayings/stories/ideas that can feed timeline and philosophy;
- science equation/theory lineage files — first-attestation/formalization events;
- creative/music archives — dated works and cultural moments;
- `docs/RELIGIOUS-SYSTEMS-ATLAS.md` — comparative religion backbone;
- `docs/CHRISTIANITY-ATLAS.md` — general Christianity backbone;
- canonical text registries — source layer for tradition comparison;
- FAQ/question-bank material — source of reader questions, not a competing public information architecture.

## 6.2 Archive utilities retain specialist roles

`/explore/`, `/context/`, FAQ bulk data, ontology registries and machine indexes may remain useful specialist/research utilities, but they should not compete with the seven main reader destinations.

Their useful content should be projected into canonical pages where relevant rather than requiring ordinary readers to discover archive internals.

## 6.3 Stale/duplicate presentation is prunable

Pages/files that merely duplicate canonical owners should become redirects, archive-only research or be removed after unique information is migrated.

Priority duplicate families include:

- Religion's embedded Jesus comparator;
- alternate public Bible-case pages;
- stale start-here/navigation surfaces;
- duplicate biography/Godhood explanatory pages where one canonical owner already exists;
- generated mirrors that contain no unique evidence.

Deletion only occurs after unique information is preserved.

---

# 7. Shared metadata and relationship model

## 7.1 One item, many projections

A single source occurrence may feed several public views without duplicating the source:

Example:

`2026-04-29 Son is Messiah/Door statement`

- Chronology: when it happened;
- Bible: relation to John 10 / messianic/New Jerusalem material;
- Religion: development of Son/Door theology;
- Homepage: only if currently/recently important;
- Philosophy: only if philosophically relevant.

Each public surface reads the canonical IDs/links appropriate to its job.

## 7.2 Claim lifecycle

The repository's existing lifecycle becomes an explicit design principle:

`source → attestation → classification → relation → interpretation → canonical promotion → reader answer → contradiction/revision → renewed source search`

Public pages should expose enough of that lifecycle to make provenance understandable without exposing raw filing-system complexity.

---

# 8. Implementation waves

## Wave 1 — contracts and ownership

- extend route ownership spec/registry;
- enrich timeline schema with domains/event types/topics and relation links;
- enrich Bible relation schema with context/discovery/triggers/meaning/limits;
- define homepage projection contract;
- update validators around ownership rather than exact prose.

## Wave 2 — chronology enrichment

- ingest/curate dated events from existing source families;
- add first-attestation events for major concepts;
- add philosophy/science/religion/creative/public/world event packs;
- add domain views and short named URLs;
- preserve sparse default roadmap.

## Wave 3 — Bible comparator deepening

- migrate strongest existing relations to rich dossiers;
- connect relation cards to timeline events;
- add arcs;
- expose discovery chronology and prophecy reasoning;
- preserve static-build fallback plus interactive enhancement.

## Wave 4 — Religion reconstruction

- remove duplicated full comparator;
- build broad religious inquiry sections;
- project Potatoism concepts/dossiers/history;
- expose practice/ritual/ethics;
- add comparative-tradition treatments with differences and source direction;
- route deep Bible comparison to Bible.

## Wave 5 — Homepage reconstruction

- add meaningful introduction;
- add reader journeys;
- add automatically derived recent/current items;
- add selected ideas;
- add canonical public-profile links;
- surface major branches without archive clutter.

## Wave 6 — prune and verify

- identify retired duplicate surfaces;
- preserve unique information;
- redirect/remove redundant pages;
- update sitemap/machine discovery/navigation;
- run full build and CI validation;
- inspect deployed artifact before completion claims.

---

# 9. Testing and integrity

## Chronology tests

- every event ID unique;
- dates/precision valid;
- controlled domain/event/topic values;
- source records exist;
- named views return events;
- default roadmap remains bounded and readable;
- later interpretations are not silently backdated;
- first-attestation chronology has no impossible ordering.

## Bible tests

- every relation explains project side, scripture side and reasoning;
- discovery mode/source direction present for rich relations;
- prophecy status vocabulary enforced;
- exact quotations distinguish recovered/paraphrased text;
- relation timeline links resolve;
- no fuzzy keyword engine can silently create canonical relations;
- static fallback survives JS enhancement failure.

## Religion tests

- no full duplicate Jesus comparator;
- Potatoism theology/history/practice/comparative content present;
- comparisons include differences and epistemic status;
- deep Bible analysis links to canonical Bible owner.

## Homepage tests

- main branches resolve;
- public profile links come from canonical registry;
- recent items derive from canonical dated events;
- no archive-only utility dominates primary navigation;
- no duplicated long-form biography/theology.

## Site-wide ownership tests

- one canonical public owner per major subject;
- redirects are noindex where appropriate;
- sitemap excludes retired duplicates;
- machine discovery agrees with human navigation.

---

# 10. Non-goals

This work must **not**:

- create many new public sub-sites;
- replace source files with presentation summaries;
- flatten project claims into empirical fact;
- call every biblical resemblance prophecy;
- merge distinct religious traditions into one symbolic soup;
- flood the default timeline with every trivial timestamp;
- make the homepage a dashboard full of controls;
- expose internal archive/file organization as the primary reader experience;
- redesign the visual language repeatedly while the information architecture is still being stabilized.

---

# 11. Success condition

A new reader should be able to answer four different questions without getting routed through duplicate pages:

- **What is this?** → Home
- **When did that happen?** → Chronology
- **What does this religious system mean and how does it compare with religions?** → Religion
- **Why is this Tim/Son event being compared to this biblical text, and is that comparison chronologically/evidentially justified?** → Bible

The same canonical evidence can support all four surfaces, but each surface has one clear job.
