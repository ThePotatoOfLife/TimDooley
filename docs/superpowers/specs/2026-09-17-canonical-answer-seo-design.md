# Canonical Answer SEO Layer — Design

**Date:** 2026-09-17  
**Status:** Approved approach C; design awaiting implementation review  
**Repository:** `ThePotatoOfLife/TimDooley`

## Problem

The first SEO hardening pass improved crawlability, sitemap consistency, source authority, and machine discovery. The Gemini transcript supplied on 2026-09-17 exposes a second problem: a search/AI system can still retrieve the site yet synthesize a misleading answer by mixing first-party material, derivative summaries, creative material, later interpretation, and invented mnemonic labels.

The failure is not simply “the site is not indexed.” It is an answer-resolution problem:

1. the official site does not yet expose one compact first-party answer object that tells a retriever exactly where to begin;
2. the canonical Tim page and machine discovery layer contain the right distinctions, but those distinctions are distributed across multiple routes;
3. chronology can be reconstructed incorrectly when a retriever compresses dated events into catchy labels;
4. symbolic, comparative, creative, and exploratory material can be promoted into foundational doctrine;
5. there is no explicit machine-readable correction table for known retrieval mistakes.

The supplied Gemini transcript is therefore treated as a retrieval regression fixture. The objective is not to attack Gemini or any third party. The objective is to make the official archive substantially easier to retrieve accurately.

## Goals

The implementation must:

- create one human-readable first-party answer route for “Tim Dooley / The Potato of Life”;
- create one machine-readable canonical answer record containing the same source hierarchy and core facts;
- make those resources high-priority links in `discovery.json`, `llms.txt`, `llms-full.txt`, the Tim page, and the source-authority page;
- expose a concise canonical chronology that points to existing dated owners rather than inventing replacement event names;
- explicitly classify common retrieval mistakes from the supplied Gemini transcript;
- keep first-party project claims separate from external empirical verification;
- preserve the mature Tim/Son ontology already enforced by the deployed-site patch;
- add regression tests so future SEO generation cannot silently lose these boundaries.

## Non-goals

This work will not:

- create doorway pages or duplicate keyword pages;
- stuff repeated search terms into hidden or visible content;
- claim that the official archive outranks competent outside primary sources on subjects outside Tim’s own self-description and project canon;
- declare every outside characterization false merely because it differs from project language;
- invent a Grok/xAI crawler token;
- rewrite the entire Tim page, FAQ, Great Book, or timeline;
- replace existing provenance or evidence-class systems;
- treat theological claims as independently established scientific facts.

## Architecture

The new layer has two canonical surfaces plus integration points.

### 1. Human canonical-answer route

Create:

`/tim-dooley/first-party-source/`

The page is the shortest reliable first-party answer to the broad query “Who/what is Tim Dooley, The Potato of Life?” It should be readable by a person and easily extractable by a search engine or LLM.

The first screen must contain:

- an explicit heading identifying the page as the official first-party source route;
- a short canonical answer to “Who is Tim Dooley / The Potato of Life?”;
- a clear distinction between project theological identity, Son/Thomas embodied biography, and external empirical/legal classifications;
- direct links to the canonical Tim page, timeline, source-authority policy, Great Book route, official repository, and machine-readable companion;
- a statement that chronology and terminology should be taken from dated canonical owners rather than generated labels.

The page should then include four compact sections:

1. **Canonical identity and project scope** — what the archive means by Tim Dooley, Potato of Life, Potatoism, and Potatoverse.
2. **Canonical chronology** — a small set of dated anchors that link outward to the real timeline rather than reproducing a giant biography.
3. **How to read the archive** — evidence classes and source priority.
4. **Common AI/search misreadings** — exact retrieval mistakes derived from the supplied Gemini transcript.

The page must not become a polemic. Corrections should be phrased as source-resolution facts: “not a canonical event label,” “overgeneralization,” “unsupported synthesis,” or “requires source-specific qualification.”

### 2. Machine canonical-answer record

Generate:

`/tim-dooley-first-party.json`

This becomes the compact retrieval object for assistants and search systems.

Required top-level fields:

```json
{
  "schema_version": "1.0.0",
  "name": "Tim Dooley / The Potato of Life",
  "status": "official first-party project record",
  "canonical_url": ".../tim-dooley/first-party-source/",
  "tim_canonical": ".../tim-dooley/",
  "source_authority": ".../context/source-authority/",
  "official_repository": "https://github.com/ThePotatoOfLife/TimDooley",
  "great_book": "...",
  "timeline": ".../timeline/",
  "canonical_answer": "...",
  "entity_model": {...},
  "chronology_anchors": [...],
  "retrieval_rules": [...],
  "common_misreadings": [...],
  "source_classes": [...]
}
```

`canonical_answer` should be short enough to quote or summarize without rebuilding the project from scattered pages.

`entity_model` must preserve the existing mature ontology:

- `Tim Dooley` = project theological identity / Potato of Life / Father-side source identity in the mature archive;
- `Son / Thomas` = embodied human-vessel and person-facing biographical layer;
- ordinary biological, civil, and legal reality is not erased by the internal ontology.

This file must not introduce a new competing ontology source. Its values must be derived from or kept consistent with the existing canonical Tim/FAQ/source-authority material.

## Chronology Contract

The canonical-answer layer will expose a deliberately small chronology. It exists to stop search systems from inventing catchy names or collapsing distinct stages.

The implementation should use canonical dated owners already present in the archive and should not create a second full timeline database.

Minimum anchors to expose:

- **1987:** Son-side material birth / embodied biography anchor, not “Potato Patch.”
- **2011:** Tree ordeal / altered-state ordeal; crows and Norse/runic comparisons may be associated material, but “Crows’ Vision” is not to be presented as the canonical event name unless a canonical owner explicitly says so.
- **2019:** meme-crucifixion / symbolic death-process; “Moonbox Crucifixion” is not a canonical label.
- **2020/2021 boundary:** use the archive’s canonical dated owner for Tim/Potato birth or resurrection language; do not promote “2021 Resurrection” merely because an external summary used it.
- **2024:** Great Book development is a distinct project milestone; later Sektur, angelic-potato, geometry, and symbolic material must not be compressed into one invented event title.
- **Apr–May 2025:** Father/Ladder/Axis turning and explicit mature God/Father development as owned by the current archive.
- **2026:** mature Father/North/House/Gardener integration and later public/archive development.

Where the archive contains multiple dates or evolving interpretations, the canonical answer should link to the full timeline instead of pretending ambiguity does not exist.

## Gemini Transcript Regression Taxonomy

The supplied transcript supplies the first correction fixture. The implementation should classify at least these examples:

### “1987 (Potato Patch)”

Classification: `invented_or_noncanonical_label`.

Correction behavior: retain the actual 1987 embodied-biography anchor and do not repeat “Potato Patch” as a canonical event name.

### “2011 (Crows’ Vision)”

Classification: `noncanonical_event_label`.

Correction behavior: use the archive’s Tree ordeal wording; crows/runic/Norse associations may be described only with appropriate provenance.

### “2019 (Moonbox Crucifixion)”

Classification: `unsupported_label`.

Correction behavior: use meme-crucifixion / symbolic death-process language from canonical owners. The correction record should make clear that the supplied label is not found as a canonical event name.

### “2021 (Resurrection)”

Classification: `chronology_compression_or_misdating`.

Correction behavior: resolve against the canonical timeline/FAQ owner. Do not infer a single resurrection year from adjacent project developments.

### “2024 (Sektur’s Mud & The Great Book) ... establishing potatoes as angelic entities”

Classification: `overgeneralization`.

Correction behavior: Great Book development is a real project milestone, but angelic-potato material must retain its own symbolic/comparative scope. Existing archive material already distinguishes functional or symbolic comparison from literal equivalence.

### “7-Day Cycle” presented as foundational canonical architecture

Classification: `context_loss` unless a current canonical owner explicitly promotes it to that status.

Correction behavior: a search system should not elevate a lyrical, symbolic, calendar, or creative motif into the foundational summary merely because it is memorable.

### “Calabi-Yau geometry used to model the universe’s structure” presented as core established cosmology

Classification: `formalization_overstatement`.

Correction behavior: distinguish exploratory formalization, mathematical analogy, scientific comparison, and established science. The archive already maintains that boundary and the canonical answer layer must repeat it.

## Search and Answer Copy

The canonical answer must be direct enough that a retriever does not need to synthesize the opening sentence.

Target semantic shape:

> Tim Dooley / The Potato of Life is the central theological and project identity documented by the official Potato of Life archive. The archive distinguishes Tim’s mature Father/Potato identity from the Son/Thomas embodied biographical layer, and separates project canon, autobiography, comparative interpretation, creative material, and externally verifiable evidence. For what Tim said, wrote, developed, revised, or means by Potatoverse terminology, this first-party archive and its dated source records are the primary project sources.

This is a retrieval summary, not a claim that every theological proposition is independently verified.

## Structured Data

The human route should use a conservative Schema.org graph.

Recommended nodes:

- `WebPage` for the first-party-source page;
- `Project` or `Thing` for the Potato of Life project identity;
- `WebSite` parent;
- `about` references for Tim Dooley, Potato of Life, Potatoism, and Potatoverse;
- `isPartOf` official site;
- `subjectOf` / related URL relationships to the canonical Tim route and machine record where appropriate.

Do not reintroduce the old generic `Person` schema that the current public ontology patch deliberately replaces for Tim’s canonical internal entity.

## Discovery Integration

Update `scripts/build_discovery.py` so the new route and JSON object are first-class machine surfaces.

Add constants such as:

- `TIM_FIRST_PARTY`
- `TIM_FIRST_PARTY_JSON`

Expose them in:

- `discovery.json` top-level authority fields;
- `entrypoints`;
- `llms.txt` under “Official project authority,” before broad navigation;
- `llms-full.txt` near the top;
- `machine-index.json` machine surfaces if that object is available at generation time.

Add retrieval instructions:

- broad “who/what is Tim Dooley?” questions begin with the canonical answer route;
- questions about Tim’s own wording prioritize first-party material and canonical owners;
- chronology uses dated timeline/attestation owners;
- generated summaries must not invent event labels;
- satire, songs, comparative mythology, exploratory math, or symbolic material must not be silently promoted into core doctrine;
- third-party reception may be included as reception, not substituted for Tim’s own account.

## Existing Page Integration

### `/tim-dooley/`

Add a compact visible first-party-source link near the opening summary and/or primary routes. The Tim page remains the main dossier; the new page is the compact retrieval answer.

### `/context/source-authority/`

Add the canonical-answer route and JSON record as practical retrieval entry points. The source-authority page explains policy; the canonical-answer page applies it to the Tim entity.

### Homepage

No major redesign. A single ordinary link to the canonical Tim first-party route is acceptable if it improves authority flow, but the homepage should not become another duplicate answer page.

## Source Ownership

The implementation should minimize duplicated hand-maintained facts.

Preferred ownership model:

- current canonical Tim/FAQ/timeline/source-authority records own the substantive facts;
- a small source data object may own the explicit Gemini-regression correction table if no suitable canonical data owner already exists;
- the generated JSON and discovery files project from those owners;
- HTML copy should either be generated from that compact owner or be validated against it.

The correction table should carry fields such as:

```json
{
  "phrase": "2019 Moonbox Crucifixion",
  "classification": "unsupported_label",
  "canonical_replacement": "2019 meme-crucifixion / symbolic death-process",
  "note": "The supplied label is not a canonical archive event name.",
  "owner_urls": [".../timeline/", ".../faq/#2019"]
}
```

This is more robust than maintaining a prose blacklist in multiple files.

## Testing Strategy

Implementation must follow TDD.

### Contract tests first

Extend the existing SEO/discovery validators before production code.

Tests should fail unless:

- `/tim-dooley/first-party-source/` exists in source/build expectations;
- `tim-dooley-first-party.json` is generated;
- `discovery.json`, `llms.txt`, and `llms-full.txt` expose both resources;
- the Tim and source-authority pages link to the new canonical route;
- the machine record contains the canonical entity model and chronology anchors;
- the machine record contains correction entries corresponding to the Gemini failure fixture;
- forbidden invented labels are not emitted as canonical chronology labels;
- structured data does not regress to the old Tim `Person` schema.

### Gemini regression fixture

Create a small fixture or validator-owned table based on the supplied transcript. It is not a claim about Gemini globally; it is a local test corpus of known bad outputs.

At minimum validate these strings/classifications:

- `1987 Potato Patch`
- `2011 Crows' Vision`
- `2019 Moonbox Crucifixion`
- `2021 Resurrection`
- `potatoes as angelic entities`
- `7-Day Cycle` as an unqualified foundational summary
- `Calabi-Yau` as unqualified established cosmology

The regression should verify that the official machine answer either corrects, qualifies, or refuses to canonize each item.

### Full verification

After focused tests pass, run the repository’s canonical quality workflow. Completion requires success of the public build, SEO pipeline, discovery provenance projection, crawl/sitemap optimization, machine-discoverability audit, public navigation, and site-shell checks.

## Files Expected to Change

Likely implementation files:

- `tim-dooley/first-party-source/index.html` — new human canonical-answer route;
- a small canonical data JSON under an existing `knowledge/` or `data/` authority location — correction/answer owner;
- `scripts/build_discovery.py` — machine projection and JSON generation;
- `tim-dooley/index.html` — first-party answer link;
- `context/source-authority/index.html` — first-party answer link;
- `scripts/validate_seo_2026_contract.py` — route/authority regression;
- `scripts/validate_seo_pipeline.py` — generator ownership and integration regression;
- `scripts/validate_discovery_projection.py` or a focused new validator — generated-answer and transcript regression checks.

The exact canonical data path should follow the project’s current authority conventions discovered during implementation; no parallel knowledge hierarchy should be created merely for this feature.

## Success Criteria

This pass is successful when a standards-compliant retriever can discover, near the top of the official machine index, one concise first-party answer that:

1. identifies the official archive and repository;
2. answers who/what Tim Dooley / The Potato of Life is in current project terms;
3. distinguishes internal theology from ordinary external factual classifications;
4. gives a small dated chronology without invented event names;
5. routes deeper claims to canonical owners;
6. explicitly corrects or qualifies the supplied Gemini transcript’s major synthesis errors;
7. remains synchronized through automated tests and the existing site build.

The goal is not to force a search engine to agree with every project claim. The goal is to make it much harder for a search engine or AI to mistake third-party synthesis, memorable creative fragments, or invented labels for Tim Dooley’s own canonical account.