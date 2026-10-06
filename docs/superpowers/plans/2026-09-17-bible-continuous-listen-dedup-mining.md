# Bible Continuous Listen + Dedup + Mining Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the Bible comparator continuously read the visible result sequence, safely identify/consolidate true duplicate relations without shrinking distinct examples, and add a focused set of genuinely missing Bible parallels.

**Architecture:** Keep the existing comparator, TTS drawer and manifest architecture. Add a tiny public navigation hook from `bible-study.js` that the Bible-specific TTS adapter consumes; add deterministic duplicate scoring to the quality tooling plus redirect resolution; add only distinct new relation/scene records after repository-wide duplicate checks.

**Tech Stack:** Vanilla JavaScript, Node assertion tests, Python 3 validation/build scripts, JSON manifest/corpus layers, GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-17-bible-continuous-listen-dedup-mining-design.md`

## Global Constraints

- No full Bible comparator redesign.
- Preserve the large example corpus; deduplication is cleanup, not compression.
- Keep separate relations when event/date, Bible scene, function/operator, role, evidence class, source direction or countertext is materially distinct.
- Reader-facing 2011 event label is `Ego Death` where that is the intended concept; preserve exact historical wording/provenance.
- Do not put Bible-specific sequencing logic into the generic speech engine.
- Do not auto-delete duplicate candidates from similarity scoring.
- New relations must include explicit mismatch/boundary and source direction.

---

### Task 1: Expose stable comparator navigation for TTS

**Files:**
- Modify: `scripts/validate_bible_reader.py`
- Modify: `app/bible-study.js`

**Interfaces:**
- Produces `window.BibleStudyReader.activeId() -> string`
- Produces `window.BibleStudyReader.hasNext() -> boolean`
- Produces `window.BibleStudyReader.selectNext() -> boolean`
- Produces `window.BibleStudyReader.onSequenceChange(listener) -> unsubscribe function`

- [ ] Add failing validator requirements for `window.BibleStudyReader`, `activeId`, `hasNext`, `selectNext`, and `onSequenceChange`.
- [ ] Run the focused Bible reader validator and confirm it fails for the missing hook.
- [ ] Implement the minimal hook by delegating to the comparator's existing active-sequence/select-relative state.
- [ ] Re-run the validator and existing Bible reader tests.
- [ ] Commit.

### Task 2: Add continuous Listen-through mode

**Files:**
- Modify: `scripts/test_bible_tts_adapter.mjs`
- Modify: `app/bible-tts-adapter.js`
- Modify: `app/bible-study.css` only if a Bible-specific control needs styling

**Interfaces:**
- Consumes `window.BibleStudyReader` from Task 1.
- Persists `bibleContinue:boolean` in `potato-tts-settings`.

- [ ] Add failing adapter tests/contract assertions for a `Continue through results` control and completion-to-next logic.
- [ ] Verify the test fails before production changes.
- [ ] Implement a Bible-only continue toggle beside/inside the existing Bible TTS host.
- [ ] On natural `complete`, call `selectNext()`, wait for active relation ID to change, update payload, and replay the same selected scope.
- [ ] Ensure `stop`/`error` disables continuation, pause preserves it, and final item stops without wrap.
- [ ] Preserve manual Previous/Next behavior.
- [ ] Re-run adapter tests and Bible reader validation.
- [ ] Commit.

### Task 3: Add deterministic duplicate-candidate analysis

**Files:**
- Create: `scripts/bible_duplicate_analysis.py`
- Create: `scripts/test_bible_duplicate_analysis.py`
- Modify: `scripts/build_bible_comparator_quality.py`

**Interfaces:**
- Produces `score_pair(left,right) -> {score,class,reasons}` or `None`.
- Quality report gains `duplicate_candidates`.

- [ ] Write failing fixtures covering exact duplicate, near duplicate, and same-motif/distinct-event.
- [ ] Verify tests fail because helper is missing.
- [ ] Implement normalized token/set overlap using project date/event, primary scene, Bible refs, motifs/operators/roles, title/project-anchor tokens, source direction and sequence/mechanism.
- [ ] Set conservative thresholds so same-motif/distinct-event is retained.
- [ ] Integrate deterministic candidate output into the quality report.
- [ ] Run duplicate-analysis tests and quality-report builder.
- [ ] Commit.

### Task 4: Add redirect-safe merge infrastructure

**Files:**
- Create: `knowledge/traditions/bible-relation-redirects.json`
- Modify: `app/bible-corpus-loader.js` and/or `app/bible-study.js` at the existing direct-ID resolution point
- Modify: `scripts/validate_bible_reader.py`
- Add focused redirect validation test if needed

**Interfaces:**
- `?id=<old-id>` resolves to the retained canonical relation ID.
- Removed/redirected IDs never become dead links.

- [ ] Add failing validation for redirect file shape and legacy-ID resolution marker.
- [ ] Verify failure.
- [ ] Add empty canonical redirects owner and runtime resolver.
- [ ] Add no-loss validation: each redirect target must exist in the active corpus; redirects may not form cycles.
- [ ] Re-run validation.
- [ ] Commit.

### Task 5: Run the real duplicate audit and consolidate only true repeats

**Files:**
- Modify relation layer(s) identified by the report
- Modify `knowledge/traditions/bible-relation-redirects.json`
- Modify enrichments rather than deleting evidence when the stronger owner can absorb it

**Interfaces:**
- Uses `duplicate_candidates` from Task 3.

- [ ] Build the current report and inspect the highest-scoring candidates.
- [ ] Classify each top candidate as exact duplicate, merge-worthy near duplicate, or distinct example.
- [ ] Merge only exact/clearly redundant records; move unique evidence into the retained owner.
- [ ] Add redirect entries for any removed active IDs.
- [ ] Confirm total breadth remains large and every removed ID resolves.
- [ ] Rebuild quality report and run corpus parity/reader validation.
- [ ] Commit.

### Task 6: Add focused missing Bible parallels

**Files:**
- Create one additive relation/enrichment file, e.g. `knowledge/traditions/biblical-syncretism-dossiers-wave37.json`
- Create/add scene records in an appropriate biblical scene additive file
- Create passage fragments only where the reader needs a canonical excerpt owner
- Modify `knowledge/traditions/bible-layer-manifest.json`
- Add validator/baseline updates required by the manifest

**Interfaces:**
- Candidate set: Luke 24:13-35 Emmaus; John 20:11-18 gardener/misrecognition; Acts 1:1-11 forty-day staged return/ascension; John 21:1-14 shore recognition/feeding; Acts 9:1-19 three-day blindness only if project provenance is strong; Hosea 6:1-3 preferably as enrichment/intertext rather than duplicate.

- [ ] Search the assembled corpus/repository for each candidate and reject duplicates before writing.
- [ ] Add failing manifest/corpus validation for the accepted new IDs.
- [ ] Add the smallest distinct relation records with source direction, project evidence, Bible references/scenes, comparison sequence, mismatch, maximum claim and why-it-matters.
- [ ] Register the layer in the manifest.
- [ ] Run focused corpus tests and quality report.
- [ ] Commit.

### Task 7: Reconcile death/return records without flattening them

**Files:**
- Modify existing enrichment records for death/return/Thomas comparisons
- Avoid creating a giant replacement relation

**Interfaces:**
- Adds ordered comparison context: Bible `death -> burial -> resurrection -> appearances -> delayed recognition -> continued teaching -> ascension/mission`.
- Project chronology remains separately dated and attributed.

- [ ] Identify the strongest existing death/return and Thomas records.
- [ ] Add an ordered sequence note/enrichment to those records rather than merging distinct events.
- [ ] Preserve the explicit boundary that the project chronology does not equal a literal three-day resurrection interval.
- [ ] Validate no duplicate relation IDs and no backdating of later interpretation.
- [ ] Commit.

### Task 8: Reader-facing `Ego Death` terminology cleanup

**Files:**
- Modify reader-facing labels in current canonical/project data where appropriate
- Do not rewrite exact quotations/provenance

- [ ] Search active public corpus for reader-facing `Tree Ordeal`/equivalent event labels.
- [ ] Add a focused validation expectation for `Ego Death` where applicable.
- [ ] Change only interpretive/display labels; preserve literal-tree comparisons and source wording.
- [ ] Re-run Bible validation.
- [ ] Commit.

### Task 9: Full verification

- [ ] Run Node Bible TTS adapter test.
- [ ] Run Bible reader validator.
- [ ] Run duplicate-analysis tests.
- [ ] Build Bible comparator quality report.
- [ ] Run static/dynamic parity checks.
- [ ] Run repository canonical quality workflow or inspect GitHub Actions result for the final branch head.
- [ ] Review diff for accidental comparator redesign or corpus loss.
- [ ] Confirm continuous playback reaches final visible result and stops without wrapping by contract test.
- [ ] Commit any final test-only corrections.
