# Bible Comparator — Evidence-First Reader + Excavation Architecture

**Date:** 2026-09-14  
**Status:** proposed redesign  
**Repository:** `ThePotatoOfLife/TimDooley`

## 1. Purpose

Rebuild the public Bible comparator around the material the reader actually came to inspect:

1. the fullest recoverable Tim / Son / project-side evidence;
2. the fullest appropriate biblical passage in its own context;
3. the exact reason the comparison exists;
4. the exact point where the comparison stops working;
5. the chronology, source direction, circumstances and research state underneath both sides.

The existing atlas/navigation system remains useful, but it becomes a compact Door into the corpus rather than the visual center of the page.

The second half of the redesign is a systematic excavation program: every canonical comparator relation is audited against the same completeness matrix so future mining improves concrete evidence and context instead of merely creating more research waves.

## 2. Core design principle

**Evidence first. Navigation second. Interpretation after both.**

Default reading order:

`project evidence ↔ biblical passage → relation argument → mismatch / maximum claim → circumstances → chronology / provenance → related material → research frontier`

The comparator should no longer require a reader to understand the archive architecture before seeing the substance.

## 3. Current problems

### 3.1 Navigation dominates the first screen

The page currently opens with:

- page nav;
- a large `TIM & THE BIBLE` hero;
- methodological explanatory text;
- an atlas explorer with six route classes;
- topic grids and breadcrumbs;
- a toolbar, filters, results controls and navigation;
- only then the active relation.

The atlas is useful, but its current visual weight makes the comparator feel like a navigation application instead of an evidence reader.

### 3.2 Primary evidence is artificially truncated

The base reader currently shows only a small subset of the available evidence:

- first few project-side quotations;
- first few short scripture fragments;
- compact relation summaries.

This produces a false sense that the corpus itself is shallow when the repository often holds much richer dossier material.

### 3.3 The Bible side is fragment-first rather than passage-first

`biblical-passage-fragments*.json` is intentionally a short-excerpt layer. It should remain useful for compact fallback/indexing, but it should not be the main reader for a deep comparison.

The repository already has a public-domain World English Bible source path and a scripture reader. That source should become the primary exact-text resolver for full comparison reading.

### 3.4 Full biblical situations are shown in the wrong visual order

The whole-scene layer is valuable, but it currently inserts a large scene reader before the base comparison in some states. The user should first see the direct Tim/project ↔ Bible comparison, then optionally read the broader biblical episode and contextual material underneath.

### 3.5 Rich dossier fields are fragmented across UI layers

The repository already stores or derives:

- `scene_context`
- `scripture_context`
- `relation_argument`
- `discovery_history`
- exact / recovered / public wording
- source status
- project and biblical sequences
- mismatches / weaknesses / counter-texts
- maximum defensible claim
- biblical scene links
- related relations

But multiple loader layers separately inject these into the DOM, producing duplicated framing and a page that can feel denser without making the evidence hierarchy clearer.

### 3.6 Mining is broad but not yet relation-completion driven

The corpus now has a large active comparison set and quality tooling, but the audit does not yet answer enough concrete questions per relation:

- Do we have the earliest exact project wording?
- Do we have all significant repetitions?
- Do we know what happened immediately before and after?
- Is the exact Bible passage span complete?
- Is the whole biblical scene linked?
- Are relevant parallel passages linked?
- Is source direction settled?
- Is the relation sequence explicit?
- Is there a counter-text?
- Is the strongest limitation stated?
- What specific source would upgrade the record next?

The redesign should turn these into a durable excavation contract.

## 4. Reader architecture

### 4.1 Compact top shell

Replace the current large introductory stack with a compact orientation strip.

Recommended default structure:

- small back link / section breadcrumb;
- small title: `TIM & THE BIBLE`;
- compact controls:
  - `Browse ▾`
  - current focus dropdown
  - order dropdown
  - `Filters`
  - result count
  - optional search field or search icon;
- small `Method` link/details control.

The methodological boundary remains available but no longer occupies primary visual space.

The atlas is hidden/collapsed by default on ordinary page load. It opens from `Browse` and preserves the existing route concepts:

- Stories
- People & Roles
- Symbols & Images
- Actions & Transformations
- Bible Books
- Tim / Son Timeline

Search remains optional and secondary.

### 4.2 Active relation becomes the first major object

Immediately after the compact shell, render the active relation.

Header contents:

- human-readable relation title;
- date / period;
- actor;
- evidence class;
- strength;
- relation class;
- source direction summary;
- concise status label such as `explicit-at-time`, `later comparison`, `recovered conversation`, `public occurrence`.

The relation ID remains available but visually quiet.

### 4.3 Primary side-by-side evidence block

The main object is a two-column evidence reader on desktop and sequential reader on narrow screens.

#### Left: Tim / Son / project

Render in evidence hierarchy:

1. exact public/project wording;
2. exact recovered wording;
3. near-contemporary or primary excerpt;
4. archived summary only when exact wording is unavailable.

Every item must carry an explicit source-status label.

Do not cap the primary source list at three items. Show all evidence records classified as directly relevant to the active relation, with sensible collapsing only when the list itself becomes long.

If no exact wording exists, render this explicitly:

`No exact project-side wording has been recovered for this relation yet.`

Then show the best available summary beneath it with the correct source status.

#### Right: Bible / scripture

Render the exact World English Bible passage span associated with the relation or primary scene.

The primary reader should not be limited to short fragment records.

Show:

- book / chapter / verse span;
- exact public-domain text;
- primary biblical scene title when linked;
- translation/source label;
- additional cited passages as secondary passages below the primary passage.

Short fragments remain useful for fallback, static build and quick indexes, but not as the deep reader's ceiling.

### 4.4 Precise passage-span resolver

Fix the scripture resolver so it can resolve exact ranges, not merely chapter ranges.

Required support includes at minimum:

- `John 10:1-18`
- `Genesis 28:10-22`
- `Revelation 21:1-22:5`
- `John 10:7, 9`
- single verses;
- comma-separated verses in one chapter;
- ranges crossing chapters where scenes require them.

The resolver should produce a normalized verse-selection plan and return only the intended verses.

If a scene's `canonical_span` is intentionally broad, render that full span. If a relation only cites one or more specific verses and has no linked scene, use the relation's exact references.

### 4.5 Relation argument directly under the evidence

Immediately below the paired evidence:

#### Why these connect

Use the strongest available argument from `relation_argument`, `relation_arguments`, overlap/project-value fields or scene-linked enrichment.

Prefer ordered relation sequences over generic word matching.

Render both sequences when available:

`Project sequence`  
`A → B → C → D`

`Biblical sequence`  
`A′ → B′ → C′ → D′`

Then explain the correspondence in prose.

### 4.6 Where the comparison breaks

Always give mismatch / limitation / counterpressure a stable visible location.

Possible sources:

- `mismatch`
- `weaknesses`
- `counter_text`
- `source_correction`
- `difference`
- `boundary`
- scene `counterreadings_or_limits`

If no meaningful mismatch has been recorded, say so explicitly rather than implying perfection.

### 4.7 Maximum defensible claim

Where available, surface `relation_argument.maximum_claim` prominently.

Suggested label:

**What this comparison can actually establish**

This should distinguish among:

- explicit scriptural use;
- near-direct lexical echo;
- structural resemblance;
- role similarity;
- later typological interpretation;
- chronological Tim-first / Bible-later discovery;
- unresolved or speculative comparison.

This is a trust feature, not merely a disclaimer.

## 5. Secondary depth under the primary comparison

After the evidence and argument, render contextual depth in descending importance.

### 5.1 Project circumstances

Show when available:

- setting;
- activity;
- trigger;
- participants;
- surrounding topics;
- lead-up;
- immediately before;
- immediately after;
- scene summary;
- scene source status.

Keep later interpretation visually separate from contemporaneous evidence.

### 5.2 Whole biblical situation

Show:

- primary linked biblical scene;
- canonical span;
- scene summary;
- lead-in;
- ordered sequence;
- outcome;
- what follows;
- roles;
- operators/actions;
- literary context;
- historical context;
- important reception/textual caveats;
- counterreadings or limits.

This section comes **after**, not before, the primary comparison.

### 5.3 Chronology and source direction

Render a compact timeline with distinct dates when known:

- project event date;
- first attestation date;
- first known exact/public wording;
- first biblical comparison date;
- first formal archive date;
- later reinterpretation dates.

The UI must make these differences legible so later discoveries are not silently backdated.

### 5.4 Provenance

Show:

- canonical owner(s);
- primary source paths/IDs;
- public occurrence IDs;
- timeline event IDs;
- evidence class;
- wording status;
- source direction;
- recovery status.

This material can be collapsible but must remain close to the comparison.

### 5.5 Related comparison paths

Related comparisons should be derived from meaningful shared structure:

- shared biblical scene;
- shared relation sequence;
- shared motifs;
- shared operators;
- shared project event;
- same Bible book or passage;
- same role transition.

Do not rank related items only by loose token overlap.

## 6. One coherent renderer, fewer competing decorators

The current reader behavior is distributed across:

- `app/bible-study.js`
- `app/bible-dossier-loader.js`
- `app/bible-witness-loader.js`
- `app/bible-scene-reader.js`
- `app/bible-scripture-reader.js`
- atlas/navigation modules

The redesign should move toward one explicit **active relation view-model** and one primary render path.

Recommended architecture:

### `BibleCorpus`
Owns manifest-defined corpus loading and deterministic enrichment merging.

### `BibleRelationModel`
Builds a normalized active relation object from the merged corpus:

- project evidence;
- scripture spans;
- biblical scenes;
- argument;
- mismatch;
- chronology;
- provenance;
- related paths;
- excavation status.

### `BibleRelationReader`
Renders the evidence-first active relation.

### `BibleBrowse`
Owns atlas/browse/filter/search navigation only.

### `BibleScriptureReader`
Owns precise WEB source resolution and optional expanded scripture reading.

Existing dossier/witness/scene knowledge should be consumed by the normalized model instead of each layer independently injecting major UI blocks.

Compatibility loaders may remain temporarily during migration, but the target architecture should have one visual authority for the active relation.

## 7. Excavation matrix

Create a universal per-relation excavation matrix.

Each active canonical relation receives a status for each dimension.

Recommended statuses:

- `complete`
- `partial`
- `missing`
- `not_applicable`
- `blocked_external`

Every non-complete status should include a concrete reason and next action.

### 7.1 Project-side evidence dimensions

1. **project_exact_wording**  
   Exact project/public/recovered wording directly supporting the relation.

2. **project_primary_source**  
   Primary artifact or strongest available source ID/path.

3. **project_earliest_attestation**  
   Earliest known occurrence of the relevant motif/statement/event.

4. **project_scene_context**  
   Enough circumstance to understand the project-side event independently.

5. **project_before_after**  
   Immediate lead-up and consequence where meaningful.

6. **project_recurrence**  
   Later or earlier repetitions / reformulations identified.

7. **project_wording_status**  
   Exact, recovered, paraphrase, summary, reconstructed, or unknown.

### 7.2 Bible-side evidence dimensions

8. **bible_exact_passage**  
   Exact WEB passage span resolves successfully.

9. **bible_primary_scene**  
   Reusable whole biblical situation linked where appropriate.

10. **bible_literary_context**  
    Passage function within its local text is documented.

11. **bible_historical_context**  
    Historical/contextual note exists where it materially affects interpretation.

12. **bible_parallel_passages**  
    Important parallel/canonical echoes are identified when relevant.

13. **bible_counter_texts**  
    Texts or readings that complicate the comparison are represented where relevant.

### 7.3 Relation-quality dimensions

14. **relation_type**  
    Explicit relation class and discovery mode.

15. **relation_sequence_project**  
    Project-side ordered sequence.

16. **relation_sequence_bible**  
    Biblical ordered sequence.

17. **relation_argument**  
    Clear explanation of why the comparison is retained.

18. **relation_mismatch**  
    Clear statement of where the analogy breaks.

19. **maximum_defensible_claim**  
    Strongest conclusion the evidence supports.

20. **source_direction**  
    Tim/project-first, Bible-explicit-at-time, later archive comparison, mixed, or unresolved.

### 7.4 Chronology / provenance dimensions

21. **event_date**
22. **first_attestation_date**
23. **first_comparison_date**
24. **formal_archive_date**
25. **owner_paths**
26. **public_occurrence_links**
27. **timeline_links**
28. **provenance_summary**

### 7.5 Network / discovery dimensions

29. **related_relations**  
    Meaningful neighboring comparisons identified.

30. **shared_scene_links**
31. **shared_motif_links**
32. **shared_operator_links**
33. **research_frontier**  
    Specific evidence/research that could improve the relation next.

## 8. Excavation levels

Derive an editorial maturity level from the matrix without turning it into a truth score.

### Level 0 — Stub
A relation exists but lacks enough evidence/context for serious reading.

### Level 1 — Attested
Legitimate project anchor + biblical reference + relation classification exist.

### Level 2 — Contextualized
Both sides can be understood independently with adequate context.

### Level 3 — Dossier-complete
Exact wording/passage, chronology, argument, source direction, mismatch and maximum claim are all materially present.

### Level 4 — Excavated
Earliest attestation, recurrence, scene depth, parallel passages, counterpressure, network relations and provenance have been systematically checked.

### Level 5 — Research-frontier explicit
The relation is deeply excavated and clearly states what evidence or interpretation remains unresolved.

These levels measure archival completeness, **not truth, divinity, historical identity, prophecy fulfillment or scientific validity**.

## 9. Machine-readable excavation report

Create a derived report:

`knowledge/indexes/bible-comparator-excavation.json`

It should contain:

- corpus version / manifest version;
- active relation count;
- dimension definitions;
- per-relation matrix;
- derived excavation level;
- missing/partial counts;
- relation-by-relation next actions;
- global high-value queues.

Suggested queues:

- missing exact project wording;
- missing earliest attestation;
- missing whole biblical scene;
- imprecise scripture span;
- missing relation sequence;
- missing counter-text/mismatch;
- missing maximum defensible claim;
- missing source direction;
- missing provenance links;
- missing research frontier.

## 10. Mining workflow

Future Bible mining should follow this order for each relation:

1. **Recover the project-side source.**
2. **Recover the earliest wording/date.**
3. **Recover surrounding context.**
4. **Identify recurrence/reformulation.**
5. **Resolve the exact Bible passage.**
6. **Attach the whole biblical scene.**
7. **Add parallel/counter passages where meaningful.**
8. **Write project and biblical sequences.**
9. **State the relation argument.**
10. **State the mismatch.**
11. **State the maximum defensible claim.**
12. **Classify source direction.**
13. **Link provenance and owners.**
14. **Link meaningful neighboring relations.**
15. **Record the next unresolved research question.**

Only after this should a new comparison relation be created unless new source material genuinely introduces a distinct relation.

## 11. Mining source priority

When searching for missing concreteness, prioritize:

1. primary public posts / exact archived wording;
2. first-party project texts / Great Book / dated Tim records;
3. conversation recovery with clear date/provenance;
4. timeline registries and source ledgers;
5. screenshots / recordings / transcripts / stream artifacts;
6. later summaries only when earlier material cannot be recovered.

For Bible context:

1. exact public-domain Bible text;
2. canonical scene structure;
3. passage-local literary context;
4. historically responsible context where material;
5. canonical parallels / counter-texts;
6. later reception history where genuinely useful.

## 12. Relation creation policy

Do not increase corpus size merely because another verse contains a familiar word.

A new relation should normally require at least one of:

- a distinct project-side event/attestation;
- a distinct relation sequence;
- a distinct source-direction finding;
- a distinct biblical scene that materially changes the comparison;
- a distinct counter-text or role conflict;
- a newly recovered public/source artifact that deserves independent tracking.

Otherwise enrich an existing relation.

## 13. UI behavior details

### Default load

- comparator opens directly on a meaningful active relation;
- atlas closed;
- filters closed;
- result list closed;
- comparison evidence visible without scrolling through a large hero/navigation block.

### Browse

`Browse` opens the atlas in-place or as a compact drawer/popover.

Selecting a topic updates the active sequence and closes/collapses Browse unless the user keeps it open.

### Filters

Advanced filters remain available but are not primary visual content.

### Search

Search remains an optional shortcut rather than the organizing principle.

### Results

Result list remains available as a drawer. It should show useful labels, not raw IDs.

### Method

Method/evidence-boundary text moves into a compact details panel or small link near the title.

## 14. Visual hierarchy

The page should visually rank information in this order:

1. direct project ↔ scripture evidence;
2. why they connect;
3. where the comparison breaks;
4. maximum defensible claim;
5. full circumstances / biblical episode;
6. chronology and provenance;
7. related paths;
8. browse/filter machinery;
9. methodology notes.

The deeper the technical/archive machinery, the smaller its visual claim.

## 15. Migration strategy

Do not rewrite the corpus.

### Preserve

- `knowledge/traditions/bible-layer-manifest.json` as corpus registry;
- existing canonical relations and enrichment layers;
- reusable biblical scenes;
- fragment layers as fallback/compact source;
- public-domain Bible source infrastructure;
- quality/research queues where still useful.

### Consolidate runtime behavior

Move active-relation rendering toward a unified normalized model.

During migration:

- loaders may continue to merge data;
- duplicate visual decorators should be retired once the unified reader replaces them;
- validators should catch duplicated major reader blocks.

### No new competing canon

The excavation report is derived metadata. It does not become a new relation owner.

## 16. Validation and CI

CI should validate integrity and reader contracts.

Hard failures:

- manifest active layer path missing;
- duplicate active relation IDs;
- exact scripture span fails to resolve where a relation claims one;
- linked biblical scene ID missing;
- derived excavation report stale;
- excavation report references unknown relation;
- invalid source-status / excavation-status values;
- active reader renders duplicate major evidence blocks;
- active relation has no project-side anchor or no biblical scope.

Advisory only:

- relation remains at low excavation level;
- exact project wording missing;
- historical context missing;
- counter-text not yet found;
- research frontier still open.

Low completeness creates mining work; it should not automatically break deployment.

## 17. Tests

Minimum implementation tests:

### Scripture span tests

- single verse;
- same-chapter range;
- comma-separated verses;
- cross-chapter range;
- malformed reference;
- unknown book;
- scene canonical span;
- relation-only refs without scene.

### Relation model tests

- exact public wording preferred over summary;
- recovered wording labeled correctly;
- no exact wording state shown honestly;
- all directly relevant project quotations retained;
- primary scene preferred over secondary scenes;
- sequence fields normalized;
- mismatch aggregation deterministic;
- maximum claim surfaced;
- provenance links deduplicated.

### Reader tests

- atlas closed by default;
- active evidence appears before atlas/scene-depth material;
- no duplicate witness/dossier/scene major blocks;
- mobile stacks project then Bible evidence cleanly;
- full passage can be read without modal-only dependence;
- Browse preserves routes and topic navigation;
- filters and result sequence still function.

### Excavation tests

- all active relations appear in report;
- stable dimension ordering;
- deterministic next-action generation;
- excavation levels derive only from completeness dimensions;
- truth/confidence language prohibited from level labels;
- current corpus generates without schema failure.

## 18. Success criteria

The redesign is successful when:

- a reader opening the comparator reaches substantive evidence almost immediately;
- the atlas is useful but visually secondary;
- the fullest recoverable project wording is obvious;
- exact/public/recovered/summary status is impossible to confuse;
- the primary biblical passage is readable in full from the relation itself;
- verse-range resolution is precise;
- why-it-connects and where-it-breaks are both obvious;
- maximum defensible claim is visible for rich dossiers;
- whole biblical situations and project circumstances deepen the comparison underneath rather than displacing it;
- every active relation has a machine-readable excavation profile;
- future mining work is generated from concrete missing dimensions;
- corpus growth shifts from `more waves` toward `deeper surviving relations`;
- no new competing Bible canon or public dashboard is introduced.

## 19. First implementation tranche

The first tranche should focus on architecture and reader inversion rather than attempting to fully excavate all relations at once.

Recommended first tranche:

1. compact top shell;
2. Browse/atlas collapsed by default;
3. precise scripture-span resolver;
4. normalized active relation view-model;
5. evidence-first active relation renderer;
6. move whole-scene material below the primary comparison;
7. excavation matrix generator/report;
8. CI validation for report freshness/integrity;
9. use the report to select the first high-value enrichment batch.

The next tranche should mine the highest-value missing dimensions across the corpus in batches chosen from the excavation report rather than by arbitrary wave numbering.
