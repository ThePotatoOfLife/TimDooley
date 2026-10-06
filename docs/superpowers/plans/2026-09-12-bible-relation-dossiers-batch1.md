# Bible Relation Dossiers Batch 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore early Son/Jesus chronology and Thomas/Twin depth as scene-aware canonical Bible dossiers and project those dossiers through the focused Bible comparator.

**Architecture:** Keep `knowledge/traditions/biblical-syncretism-field.json` as canonical relation owner. Enrich selected rows with typed scene context, relation arguments, discovery history and mismatch; add exact WEB fragments in the existing fragment owner; strengthen validation; render the richer fields in the existing single-relation UI without changing navigation or viewport behavior.

**Tech Stack:** JSON canonical data, Python validators/builders, vanilla JavaScript/CSS public reader.

**Spec:** `docs/superpowers/specs/2026-09-12-bible-relation-dossiers-enrichment-design.md`

## Global Constraints

- Never invent documentary scene detail.
- Distinguish exact, recovered, adjacent-context, date-only and unknown scene provenance.
- Preserve evidence classes and chronological source direction.
- High-strength identity-sensitive relations require a meaningful mismatch/maximum-claim boundary.
- Keep one active relation at a time and never reintroduce automatic viewport scrolling.
- Research discovers; canonical owners decide; projections expose.

---

### Task 1: Add dossier density validation

**Files:**
- Modify: `scripts/check_biblical_syncretism_field.py`
- Modify: `scripts/validate_bible_reader.py`

**Interfaces:**
- Consumes: relation rows with optional `dossier_level`, `scene_context`, `relation_argument`, `discovery_history`, `mechanisms`, `wording_status`, `mismatch`/`weaknesses`.
- Produces: validation failures when Level-A records are skeletal or scene provenance is internally inconsistent.

- [ ] Add validator expectations first so the current branch fails for missing Level-A dossier markers.
- [ ] Verify the failure is caused by missing dossier data/UI markers rather than unrelated syntax.
- [ ] Implement scene-status and Level-A density validation.
- [ ] Preserve existing fragment coverage, owner-path and relation-class checks.

### Task 2: Restore early Son/Jesus chronology and Thomas/Twin dossiers

**Files:**
- Modify: `knowledge/traditions/biblical-syncretism-field.json`

**Interfaces:**
- Consumes: `knowledge/theology/son-jesus-longitudinal-christology-atlas.json`, `knowledge/timeline/son-jesus-martyr-prehistory.json`, `knowledge/traditions/thomas-twin-of-christ.json`, countertext atlas and timeline recoveries.
- Produces: Level-A canonical relation dossiers covering 2011, 2016, 2017/2018, 2019/20 and mature Thomas/Twin development.

- [ ] Add a 2011 Tree-ordeal relation with later Christian Tree/Cross/Ladder comparison and explicit Odin/Yggdrasil priority boundary.
- [ ] Add 2016 accusation/custody/prison relation and separate prison-among-offenders/recognition relation where analytically distinct.
- [ ] Add enemy-love vs reciprocity as first-class countertext.
- [ ] Add 2017/2018 Jesus/crucifixion declaration dossier preserving date uncertainty and source status.
- [ ] Add 2019/20 meme-crucifixion/burial/hidden interval dossier with symbolic-vs-physical boundary.
- [ ] Add a mature Thomas/Twin dossier built around Twin → co-dying → Way → wounds → recognition, with later Thomasine reception clearly separated from canonical John.

### Task 3: Expand exact WEB fragment coverage

**Files:**
- Modify: `knowledge/traditions/biblical-passage-fragments.json`

**Interfaces:**
- Consumes: promoted dossier `biblical_refs`.
- Produces: exact public-domain side-by-side text for new dossiers.

- [ ] Add John 11:16, John 14:5-6 and John 20:24-29 fragments.
- [ ] Add Matthew 5:39-44/Luke 6:27-29 enemy-love fragment coverage.
- [ ] Add Isaiah 53 / Passion-adjacent coverage only where a promoted relation actually cites it.
- [ ] Add Hebrews 13:12-14 or other required passage fragments if used by the batch.

### Task 4: Project dossier context into the focused reader

**Files:**
- Modify: `app/bible-study.js`
- Modify: `app/bible-study.css`
- Modify: `scripts/validate_bible_reader.py`

**Interfaces:**
- Consumes: `scene_context`, `what_happened`, `wording_status`, `relation_argument`, `discovery_history`, scripture context fields and mismatch/maximum claim.
- Produces: narrative front-face and progressive details while keeping the existing single-active-relation state machine.

- [ ] Make search text include scene, relation argument and discovery fields.
- [ ] Add front-face “What was happening” scene summary when available.
- [ ] Render a substantial argument rather than truncating to generic relation metadata.
- [ ] Add disclosures for Circumstances & sequence, Bible in context, and Discovery history.
- [ ] Preserve Evidence & chronology, Sources & provenance and Related comparisons.
- [ ] Keep all selection handlers free of `scrollIntoView`.

### Task 5: Validate and finish

**Files:**
- Verify all files changed above.

**Interfaces:**
- Produces: a merge-ready feature branch with canonical data and reader behavior aligned.

- [ ] Run `python scripts/check_biblical_syncretism_field.py`.
- [ ] Run `python scripts/validate_bible_reader.py`.
- [ ] Run JavaScript syntax validation used by repository workflow.
- [ ] Open a pull request to `main`.
- [ ] Run/inspect the repository quality workflow for the exact head commit.
- [ ] Merge only after the relevant workflow is green.
