# Canonical Religion / Bible Comparison Engine

**Date:** 2026-09-12  
**Status:** Design specification — awaiting implementation approval  
**Repository:** `ThePotatoOfLife/TimDooley`  
**Branch:** `religion/canonical-comparison-engine-20260912`

## 1. Purpose

Turn the existing Religion and Bible material into one coherent knowledge system rather than continuing to accumulate research-wave files and hand-written public summaries.

This design refines, rather than replaces, `docs/superpowers/specs/2026-09-12-public-knowledge-architecture-design.md`.

The central rule is:

> **Research discovers; canonical owners decide; projections expose.**

The repository already has strong material. The next step is not another independent encyclopedia and not another sequence of first-class waves. The next step is to make the strongest existing owners increasingly complete, structured, cross-linked and machine-readable.

---

## 2. Canonical ownership

### 2.1 Religion public surface

`religion/index.html` owns the broad public orientation to religion in the project.

It explains:

- Potatoism as an evolving religious / philosophical / theological system;
- the project's own account of God / Source / Father / Son / Spirit;
- sacred architecture such as House, Door, Ladder, Axis, Tree, Garden, Throne, North, Stone and Eye;
- religious life, ethics and practice;
- Christianity, Judaism, Islam, Buddhism, Hindu traditions, Daoism, Norse/Germanic traditions, ancient Mediterranean traditions and esotericism;
- how the project performs comparison;
- open questions, disagreements and unresolved areas;
- routes into deeper canonical owners.

It does **not** own detailed verse-by-verse Tim/Son/Jesus relations.

### 2.2 Bible public surface

`traditions/bible/index.html` owns the public Bible comparison laboratory.

It exposes canonical relation records and their supporting evidence, including:

- what Tim / the Son / the project said or did;
- what biblical passage is being compared;
- literary and theological context;
- comparison mechanism;
- discovery history;
- source direction;
- intertextual ancestry inside the Bible;
- prophecy / foresight classification where relevant;
- mismatch / counter-text;
- source owners and provenance;
- related timeline events and relation arcs.

### 2.3 Canonical Bible relation owner

`knowledge/traditions/biblical-syncretism-field.json` remains the canonical registry of Bible ↔ project relations.

It is upgraded so that specialist research files feed it rather than compete with it.

### 2.4 Curated synthesis owner

`knowledge/traditions/biblical-overlap-atlas.json` remains the higher-level curated synthesis of major biblical structures and findings.

The syncretism field owns **individual relation records**.  
The overlap atlas owns **cross-relation synthesis, families, patterns and conclusions**.

### 2.5 Scripture fragment owner

`knowledge/traditions/biblical-passage-fragments.json` remains the public-domain passage-fragment/source layer used by the comparator.

Passage text must not be copied independently into many relation owners unless required for a stable excerpt record.

### 2.6 Broad religion research owner

`docs/RELIGIOUS-SYSTEMS-ATLAS.md` remains the broad research/reference atlas for religious systems, traditions, textual corpora, institutions, ritual, history and comparative methodology.

The public Religion page projects selected material from this and other canonical owners. It should not become a second independent encyclopedia.

### 2.7 Comparative project owner

`knowledge/traditions/comparative-mythology-map.json` remains the project-facing cross-tradition comparison atlas, but future work should increasingly type relations as theological, structural, historical, symbolic, archetypal, textual, functional, contrastive or unresolved rather than treating all resemblance as one class.

### 2.8 Comparative cosmology owner

`data/axis-comparative-cosmologies.json` remains the typed registry for cosmological comparisons such as Jacob's ladder, layered heavens, Yggdrasil and Hermetic above/below relations.

It should remain distinct from the Bible relation field because its unit of comparison is cosmological architecture, not necessarily a Tim/Son event or statement.

---

## 3. Research waves become research history

The existing `biblical-overlap-wave-*` files are valuable research artifacts. They preserve discovery history and specialist reasoning. They are **not** equal-status canonical owners.

### 3.1 Classification

Wave files become one of:

- `research-history`
- `specialist-input`
- `candidate-relations`
- `candidate-synthesis`
- `superseded-research`

They remain in the repository for provenance and research archaeology.

### 3.2 Promotion rule

A discovery from a wave becomes current canonical knowledge only when it is promoted into one of the canonical owners.

Promotion must record, where available:

- originating research file;
- original candidate ID;
- promotion date;
- canonical destination;
- whether wording was preserved, refined, merged or rejected;
- reason for promotion or rejection.

### 3.3 Runtime rule

Public runtime code must not treat raw research waves as peers of canonical owners.

`app/bible-study.js` should consume canonical data only, plus explicitly designated evidence/source ledgers.

Wave files may be linked from provenance/debug/research-history views, but they must not silently inject live public relations.

---

## 4. Canonical relation contract v2

The canonical Bible relation becomes richer than a motif match.

A conceptual relation can be modeled as:

`R = (Ts, Tp, As, Ap, O, M, H, I, D, C, E)`

where:

- `Ts` — tradition/scripture-side text or source;
- `Tp` — project-side source/event/statement;
- `As` — scripture-side actor/speaker/narrative role;
- `Ap` — project-side actor/role;
- `O` — operator/action/relation verb;
- `M` — comparison mechanism;
- `H` — historical relationship/source-direction status;
- `I` — interpretive/reception layer;
- `D` — differences/counter-fit;
- `C` — chronology/discovery history;
- `E` — evidence/provenance/strength.

The JSON need not literally store this tuple, but the schema should support all of these dimensions.

### 4.1 Required identity fields

- `id`
- `title`
- `actor`
- `date` / `period` where known
- `project_anchor`
- `biblical_refs`
- `relation_class`
- `discovery_mode`
- `strength`

### 4.2 Project-side context

Support:

- `what_happened`
- `exact_wording`
- `paraphrase`
- `speaker`
- `audience`
- `platform_or_setting`
- `project_trigger`
- `understood_then`
- `project_source_ids`
- `project_source_urls`

Exact quotation, recollection, paraphrase and later archive summary must remain distinguishable.

### 4.3 Scripture-side context

Support:

- `scripture_actor`
- `scripture_speaker`
- `scripture_audience`
- `literary_context`
- `genre`
- `canonical_context`
- `historical_context`
- `traditional_interpretations`
- `textual_caveats`

This prevents a verse fragment from being treated as self-interpreting.

### 4.4 Relation mechanism

Allowed initial mechanisms:

- `lexical-direct-phrase`
- `title-or-identity`
- `narrative-sequence`
- `structural-topology`
- `symbolic-analogy`
- `ritual-or-practice`
- `ethical-agreement`
- `ethical-divergence`
- `typology`
- `historical-context-comparison`
- `intertextual-chain`
- `timeline-synchronism`
- `counter-text`

A relation may use multiple mechanisms.

### 4.5 Operator layer

Add an optional controlled `operators` field.

Initial useful operators include:

- `contain`
- `dwell`
- `veil`
- `pass`
- `open`
- `shut`
- `send`
- `indwell`
- `carry`
- `release`
- `root`
- `branch`
- `prune`
- `flow`
- `feed`
- `wash`
- `repair`
- `restore`
- `judge`
- `plant`
- `grow`
- `return`
- `die`
- `rise`
- `remember`
- `inherit`
- `name`
- `house`

The operator layer should improve search and structural comparison without forcing every relation into one verb.

### 4.6 Trigger chain

Support:

- `project_trigger`
- `comparison_trigger`
- `downstream_trigger`

This distinguishes what originally happened from what later made the relation interesting and what new research the relation subsequently opened.

### 4.7 Meaning and mismatch

Support:

- `relation_arguments`
- `project_consequence`
- `biblical_relevance`
- `weaknesses`
- `counter_text`
- `source_correction`
- `alternative_explanations`
- `unresolved_questions`

Every high-strength relation should ideally have at least one explicit limit or mismatch field unless the comparison is purely lexical and self-limiting.

---

## 5. Biblical intertextuality

A major relation may have an internal biblical ancestry rather than a single isolated verse.

Examples of the form:

`Genesis 28 → John 1 → Potatoverse Ladder/Door`

`Isaiah 22 → Revelation 3 → Potatoverse Key/House/Door`

`Exodus veil → Hebrews veil/flesh → Son/Vessel/Door`

### 5.1 Intertext contract

Support an optional `intertext_chain` array with entries such as:

- reference;
- role in chain;
- relation to previous text (`quotes`, `alludes-to`, `reworks`, `echoes`, `typological-use`, `later-reception`);
- confidence;
- source note.

### 5.2 Method rule

Do not assume direct literary dependence merely because two texts share an image or structure.

Possible source-direction statuses should distinguish:

- direct quotation;
- explicit allusion;
- probable literary reuse;
- shared scriptural tradition;
- conventional type-scene;
- broad structural resemblance;
- uncertain.

---

## 6. Four context layers

Important religious comparisons should be able to expose four separate layers:

1. **Text** — what the source says.
2. **Immediate context** — speaker, audience, genre, narrative/literary setting.
3. **Tradition / reception** — historical Jewish, Christian, Islamic, patristic, rabbinic, mystical, academic or other interpretation where relevant.
4. **Potatoverse interpretation** — why the project compares itself to the source and what conclusion it draws.

Public pages must not collapse layer 4 into layer 1 or present the project's reading as though it were the historical tradition's own doctrine.

---

## 7. Evidence and epistemic classes

The engine should preserve the repository's evidence discipline while allowing strong project claims to be stated directly in their canonical layer.

Initial evidence classes:

- exact public wording;
- primary project document;
- contemporary public record;
- autobiographical testimony;
- recovered conversation memory;
- later project interpretation;
- canonical Potatoist theology;
- independent historical source;
- academic/scholarly source;
- scripture/textual source;
- structural comparison;
- unresolved / research candidate.

A relation can combine several evidence classes.

The engine should explain what each item supports rather than treating a pile of heterogeneous evidence as one undifferentiated proof score.

---

## 8. Prophecy / foresight handling

Keep the existing distinction between retrospective parallel, scripture-at-time, warning/foresight and explicit prediction.

Where relevant, support:

- prior statement date;
- target event date;
- later discovery date;
- wording specificity;
- outcome foreseeability;
- interpretive flexibility;
- evidence class;
- conservative classification;
- alternative explanation.

A later resemblance must not silently become an earlier prophecy.

---

## 9. Relation arcs

Individual relations should be groupable into developmental arcs.

Initial high-value arcs:

- Passion / custody / rejection / death / return;
- Lamb / Lion / Root / Branch;
- Seed / grain / burial / germination / resurrection;
- Door / Gate / House / Ladder;
- Garden / guardians / sanctuary access;
- Father / House / Source;
- Spirit / flow / indwelling;
- Temple / presence / non-containment;
- New Jerusalem / Zion / throne / North;
- Stone / Eye / Lamp / Branch;
- Thomas / Twin / witness / doubt;
- Tree / ordeal / ascent / return;
- Beast / Cube / 666 / forehead;
- care / repair / feeding / washing / cultivation;
- counter-texts / ethical divergence.

An arc should expose chronology and source direction rather than only grouping by keyword.

---

## 10. Cross-tradition comparison contract

Religion comparison must not assume that every tradition contains the same category called `God`.

Each comparison should support:

- `project_concept`
- `tradition`
- `tradition_concept`
- `concept_type`
- `shared_structure`
- `major_difference`
- `historical_direction_status`
- `source_strength`
- `why_useful`
- `canonical_sources`
- `research_sources`

Useful `concept_type` values include:

- `ultimate-reality`
- `creator-god`
- `deity`
- `divine-person`
- `cosmic-principle`
- `prophet`
- `messiah`
- `sage`
- `buddha`
- `bodhisattva`
- `angelic-being`
- `spirit`
- `sacred-place`
- `ritual`
- `cosmology`
- `textual-structure`
- `ethical-principle`
- `institution`

This should build on, not duplicate, the vocabulary already developed in `RELIGIOUS-SYSTEMS-ATLAS.md`.

---

## 11. Public Religion page redesign

`religion/index.html` should remain compact enough to read but become substantially more representative of the knowledge behind it.

Recommended sections:

1. **Potatoism** — what kind of system this is and how it developed.
2. **God / Ultimate Reality** — the project's own ontology and the fact that different traditions use non-equivalent categories.
3. **Father / Son / Spirit** — internal architecture and Christian comparison without automatic doctrinal identity.
4. **Sacred Architecture** — Potato, Seed, Root, Tree, House, Door, Ladder, Axis, Garden, Throne, North, Eye, Stone, death/return.
5. **Religious Life** — cultivation, care, repair, nourishment, Divine Kneel, Holy Soil, washing, release, transformation, community.
6. **Scripture and Texts** — Bible, Qur'an, Dao De Jing, Buddhist textual traditions, Hindu corpora, Norse sources, esoteric texts.
7. **Traditions** — Christianity, Judaism, Islam, Buddhism, Hindu traditions, Daoism, Norse/Germanic, ancient Mediterranean, esoteric traditions.
8. **Comparison Lab** — explanation of relation types, source direction, mismatches and evidence.
9. **Open Questions** — where Potatoism agrees, differs, synthesizes or remains unresolved.

Detailed Bible comparisons route to `/traditions/bible/`.

---

## 12. Bible UI redesign

Preserve the useful existing filters and views.

Add or refine views such as:

- `GOD / PRESENCE`
- `EMBODIMENT / VESSEL`
- `HOUSE / TEMPLE`
- `SPIRIT / FLOW`
- `GARDEN / CARE`
- `ROOT / TREE`
- `TEXT REUSE / INTERTEXT`
- `COUNTER-FITS`

Add an operator filter when canonical data supports it.

### 12.1 Relation-card reading order

Each major card should aim to expose:

1. What happened / what was said.
2. Scripture beside it.
3. Why these connect.
4. What it means in the project.
5. Biblical literary context.
6. Intertextual ancestry where relevant.
7. When the comparison was discovered.
8. Source direction.
9. Prophecy / foresight status where relevant.
10. What does not match.
11. Alternative explanation.
12. Sources / owners / provenance.
13. Related events and arc.

The front face should remain readable; deeper sections can be expandable.

---

## 13. Build/runtime consolidation

### 13.1 Static builder

`scripts/build_bible_study.py` already correctly treats the canonical field as the source for static relation rendering. Extend it rather than creating a second builder.

### 13.2 Browser runtime

Refactor `app/bible-study.js` so canonical public relations come from:

- `biblical-syncretism-field.json`;
- `biblical-passage-fragments.json`;
- canonical attestations/evidence ledgers;
- canonical timeline owners;
- explicitly designated theology owners where needed.

Remove direct wave-file ingestion from canonical runtime composition.

### 13.3 Promotion registry

Prefer a compact promotion/index object rather than another giant store. It may live in an existing manifest/index if that is cleaner.

It should answer:

- which files are canonical;
- which are research history;
- which research files promoted which relations/findings;
- which files are public runtime inputs;
- which are background scholarly/reference inputs.

Do not create a redundant registry if `knowledge/indexes/core-index.json`, `manifest.json` or another existing owner can cleanly hold these declarations.

---

## 14. Machine discovery and SEO

Update machine/discovery routes only after canonical ownership is stabilized.

Requirements:

- Religion and Bible public URLs remain canonical.
- Machine routes should point to the same current owners readers see.
- Research waves should not rank as preferred answers when a promoted owner exists.
- Search terms can include questions such as God, Jesus, Father, Son, Spirit, Bible parallels, Christianity, Judaism, Islam, Buddhism, Daoism and comparative religion without manufacturing thin keyword pages.
- `llms.txt`, manifests and indexes should describe the distinction between project theology, scripture, historical interpretation, external scholarship and comparison.

---

## 15. Validation requirements

Implementation should add or extend validation for:

- valid JSON;
- unique relation IDs;
- no duplicate canonical relation IDs across owners;
- every runtime Bible relation originates from a canonical owner;
- no raw research-wave file is treated as a canonical runtime relation source;
- referenced passage IDs / refs resolve where expected;
- controlled relation mechanisms are valid;
- operator values are valid when controlled;
- source owners resolve to repository paths where applicable;
- public links from Religion to Bible and major tradition routes remain valid;
- browser/static relation counts are consistent where they are meant to be;
- generated site builds successfully;
- existing reader-surface validators still pass.

---

## 16. Migration sequence

Implementation should proceed in this order:

1. Inventory current canonical/runtime/research inputs.
2. Add explicit owner/research-history classification.
3. Extend relation schema in backward-compatible form.
4. Promote the strongest existing wave findings into canonical owners where not already promoted.
5. Add intertext, operator, context and mismatch fields to high-value relations first.
6. Refactor runtime to stop directly ingesting research waves.
7. Enhance the Bible UI to expose the richer canonical fields.
8. Enrich the Religion public page from existing owners.
9. Update machine/discovery routing.
10. Build and validate the full site.
11. Audit for duplication and prune obsolete public/runtime paths without deleting useful research history.

---

## 17. Non-goals

This work does **not**:

- delete research waves merely because they are no longer canonical;
- create one universal claim that all religions teach the same thing;
- turn structural resemblance into historical dependence;
- turn later parallels into prior prophecy;
- treat all traditions' ultimate-reality concepts as equivalent to `God`;
- create dozens of thin SEO pages;
- create another independent religion encyclopedia competing with existing owners;
- require every relation to be fully researched before the engine can ship.

The system should support progressive enrichment: high-value relations become deep first, while simpler records remain valid and searchable.

---

## 18. Success criteria

The design succeeds when:

1. A researcher can tell which file owns a religious claim or relation.
2. A research wave can contribute discoveries without becoming permanent competing canon.
3. The Bible page can explain **why** two things are compared, not merely that they share a motif.
4. Strong relations expose context, chronology, intertextual ancestry, mismatch and provenance.
5. The Religion page reflects the real breadth of the repository without duplicating specialist owners.
6. Different religious traditions remain meaningfully distinct even when compared.
7. Canonical data drives static output, runtime UI and machine discovery consistently.
8. New research can be promoted through a repeatable pipeline instead of creating another ad hoc layer.

## 19. Implementation principle

The project should increasingly behave like a knowledge graph with editorial promotion:

`research discovery → candidate relation → contextualization → comparison test → canonical promotion → public projection → machine discovery → later refinement`

That pipeline is the core of the Canonical Religion / Bible Comparison Engine.
