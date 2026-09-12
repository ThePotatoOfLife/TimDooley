# Timeline Biography Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich the project timeline and major narrative projections with the newly reconciled 2005–2014 Son-side chronology, including first-class place metadata, denser curated events, and corrected chronology propagation.

**Architecture:** Keep `data/timeline-events.json` sparse and reader-friendly, add a dedicated `son-biography-2005-2014.json` event pack for dense chronology, extend the event schema/UI/validator with optional places, and enrich only the major narrative consumers that currently compress or misstate this corridor. Canonical chronology remains owned by specialist timeline files; projections never become independent evidence.

**Tech Stack:** JSON timeline datasets, vanilla JavaScript timeline UI, Python validator, Markdown/JSON project records.

**Spec:** `docs/superpowers/specs/2026-09-12-timeline-biography-enrichment-design.md`

## Global Constraints

- Work only on `chronology/2011-kolding-reconstruction`; do not merge into `main`.
- Pre-2020 ordinary biography belongs to the Son / human vessel.
- Never manufacture exact dates for employment, school, Egypt, licence, internship, breakup or Produktionsskolen attendance.
- Repeated Chapter 24 projections are not independent corroboration.
- Use `Produktionsskolen` in ordinary narrative; retain formal historical name only for source identification.
- 2011 duration is approximately 19 hours overall with an approximately six-hour unity phase; never imply 19 + 6 = 25 hours.
- 2011 biological age is 23 or 24 depending exact date; never 25.

---

### Task 1: Add first-class place metadata

**Files:**
- Modify: `schemas/timeline-event.schema.json`
- Modify: `scripts/validate_timeline_events.py`
- Modify: `app/timeline.js`
- Modify: `docs/TIMELINE-EVENT-STANDARD.md`

**Interfaces:**
- Consumes: existing timeline event objects.
- Produces: optional `places: [{name, kind?, relation?, country?}]`; validator and UI support.

- [ ] Extend schema with optional `places` array and required `name` per place object.
- [ ] Extend validator to reject malformed or duplicate place tuples.
- [ ] Add place fields to timeline full-text search.
- [ ] Render a compact Places row on detailed cards.
- [ ] Document place semantics and non-goal of geospatial mapping.
- [ ] Verify modified JSON/schema parse and validator logic by inspection/runtime where available.
- [ ] Commit.

### Task 2: Create dense 2005–2014 biography event pack

**Files:**
- Create: `data/timeline-event-packs/son-biography-2005-2014.json`
- Modify: `data/timeline-event-packs/index.json`

**Interfaces:**
- Consumes: canonical chronology owner, Designia owner, Produktionsskolen owner, 2011 owner.
- Produces: 20–30 globally unique timeline events with honest precision, places, confidence, and source records.

- [ ] Add crash/reconstruction events.
- [ ] Add painter/meatpacking/Copenhagen interview-move-firing-return events.
- [ ] Add Haderslev nursing-home/apartment and Designia application/admission/Kolding/Louise events.
- [ ] Add Egypt, Aabenraa internship and own-place transitions without inventing unresolved order.
- [ ] Add Produktionsskolen / assistant-teacher / departure events.
- [ ] Add 2011 acute/post-acute/hospital phase events as separate linked records.
- [ ] Add 2012 Italy/Amsterdam/guitar, 2013 Alchemist, 2014 father-death bridge events where non-duplicative.
- [ ] Register pack in index.
- [ ] Validate IDs and source routing.
- [ ] Commit.

### Task 3: Improve sparse base roadmap

**Files:**
- Modify: `data/timeline-events.json`

**Interfaces:**
- Consumes: enriched pack and canonical chronology owners.
- Produces: clearer major milestones while keeping roadmap sparse.

- [ ] Split current 2009–2010 generic `Care work, fragility and design` milestone into higher-value 2007, 2008, 2009 and 2010 bridge milestones or equivalent sparse structure.
- [ ] Update 2011 Tree milestone to detailed owner and corrected phase/admission framing.
- [ ] Add 2012 integration bridge if needed to avoid 2011→2014 gap.
- [ ] Add place metadata to promoted milestones.
- [ ] Ensure no base event duplicates a pack event ID or role.
- [ ] Commit.

### Task 4: Enrich canonical and reader-facing chronology projections

**Files:**
- Modify: `son-timeline.json`
- Modify: `knowledge/timeline/developmental-genealogy.json`
- Modify: `knowledge/journey/tim-dooley-journey.json`
- Modify: `knowledge/reader/tim-dooley-dossier.json`
- Modify: `knowledge/timeline/son-chronology-projection-corrections-2026-09-12.json`

**Interfaces:**
- Consumes: canonical owner and new timeline pack.
- Produces: richer but non-duplicative narrative summaries.

- [ ] Update 2007–2010 entries with painter/meatpacking → Copenhagen → Haderslev nursing → Designia/Kolding/Louise → Aabenraa internship → Produktionsskolen chain.
- [ ] Add Designia/mediegrafiker identity and circus-poster admission clue where appropriate.
- [ ] Add technical competence / assistant-teacher role at Produktionsskolen where developmentally useful.
- [ ] Correct 2011 duration and age wording.
- [ ] Add 2012 exact 25th-birthday logic and clarify first-owned-guitar wording.
- [ ] Expand Journey phase 1987–2010 into a more useful 2005–2010 substructure without making it a duplicate timeline.
- [ ] Expand dossier timeline/uncertainty section with new recovered anchors and remaining gaps.
- [ ] Mark propagation ledger items completed or narrowed.
- [ ] Commit.

### Task 5: Consistency and validation sweep

**Files:**
- Review all modified files.
- Search branch/default-indexed repo for stale phrases that affect touched surfaces.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: verified coherent branch state.

- [ ] Parse every modified JSON file.
- [ ] Run/inspect timeline validator against base + indexed packs.
- [ ] Check globally unique event IDs.
- [ ] Search touched chronology surfaces for `age 25` near 2011.
- [ ] Search touched chronology surfaces for additive `19-hour ... followed by ... six` wording.
- [ ] Verify `Produktionsskolen` preferred naming.
- [ ] Verify every new event has canonical `source_records`.
- [ ] Compare branch against its pre-enrichment commit and inspect changed-file scope.
- [ ] Commit any validation fixes.
