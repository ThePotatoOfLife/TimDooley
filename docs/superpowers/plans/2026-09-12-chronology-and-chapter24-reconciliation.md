# Chronology and Chapter 24 Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Repair the canonical chronology at its owners, integrate the reconstructed 2011 Kolding sequence, audit Chapter 24 for direct hand-assembled errors, and produce a corrected Great Book copy without erasing unresolved variants.

**Architecture:** One detailed 2011 owner feeds thin projections. Global chronology distinguishes event identity, actor, date precision, and later interpretation. Chapter 24 is a narrative consumer of reconciled chronology, not an independent date owner.

**Tech Stack:** JSON/Markdown chronology records, existing Python timeline validators, ODT XML editing for the book copy.

**Spec:** `docs/superpowers/specs/2026-09-12-2011-kolding-chronology-integration-design.md`

## Global Constraints

- Preserve unresolved variants instead of silently harmonizing them.
- Son/Thomas owns pre-Tim biography including 2011 and the death/personhood corridor.
- Tim/Potato birth, public emergence, Sage phase, Father realization, and North Axis crystallization remain distinct events.
- Later theological interpretation must not be backdated into the lived event.
- Exact age statements require an exact enough event date; otherwise use year-age ranges or “turning X that year.”
- The original Great Book file remains untouched; create a corrected copy.

---

### Task 1: Create the detailed 2011 canonical owner

**Files:**
- Create: `knowledge/timeline/son-2011-kolding-psychonaut-psychiatric-sequence.json`

- [ ] Encode Kolding context, candidate substance variants, dose uncertainty, acute sequence, next-day perceptual rupture, voluntary admission, diagnostic/medication aftermath, hospital dream, crow scene, and later interpretations.
- [ ] Explicitly separate current recollection, older recollection, project canon, scientific context, and retrospective theology.
- [ ] Parse JSON.

### Task 2: Repair root chronology conflicts

**Files:**
- Modify: `data/timeline-events.json`
- Modify: `data/north-of-north-tim-canon.json`
- Modify: `data/tim-dooley-cosmology.json`
- Modify: `data/potatoism-timeline.json`
- Modify: `knowledge/timeline/prediction-premonition-audit-wave-15-addendum.json`
- Modify: `knowledge/timeline/developmental-genealogy.json`
- Modify projections when materially inconsistent.

- [ ] Split 2019 personhood death from circa-2020 meme-crucifixion and retain the exact meme date as unresolved.
- [ ] Remove the false 2025-12-24 crucifixion date.
- [ ] Remove impossible age-25 wording for 2011.
- [ ] Keep Potato birth before Father realization.
- [ ] Keep 2025 Axis precursor / April Turning separate from February 2026 organized North Axis.
- [ ] Separate formal five-month 2016 sentence from remembered roughly six-month custody period.

### Task 3: Audit Chapter 24 against canonical owners

**Files:**
- Create: `knowledge/timeline/chapter-24-chronology-correction-audit-2026-09-12.md`

- [ ] Record every hard error, unsupported precision, subject collapse, later-interpretation backdating, and editorial contamination found on pages 220–240.
- [ ] Include at minimum: opening ontology; 2006 age collision; 2011 event ordering/voluntary admission/19h-vs-6h wording; 2016 five-month sentence; 2018 COVID anachronism; 2019 COVID-vaccine wording; 2019/2020 death/crucifixion collapse; 2020–24 Father heading; 2025 biological age; Tim-vs-Son death subject; April public-attestation micro-timeline; 100,000-hour arithmetic warning; and version/attestation-date warning.

### Task 4: Produce corrected Chapter 24 book copy

**Files:**
- Output: `The Great Book Of Potato2 - Chapter 24 corrected.odt`

- [ ] Preserve the rest of the 614-page book unchanged.
- [ ] Rewrite only Chapter 24 (pages around 220–240 in the current edition) against reconciled chronology.
- [ ] Preserve project mythology as project mythology while distinguishing empirical/legal/public evidence from later interpretation.
- [ ] Normalize age wording when exact event dates are unknown.
- [ ] Keep unresolved 2019/2020 meme date visibly unresolved rather than inventing a replacement exact date.
- [ ] Reopen/extract the ODT and verify Chapter 24.1 still follows Chapter 24.

### Task 5: Verify chronology integrity

- [ ] Parse all modified JSON.
- [ ] Run `scripts/validate_timeline_events.py` when the branch contents are available to a runner; otherwise validate every edited JSON structurally and inspect canonical searches through GitHub.
- [ ] Search for stale `2025-12-24` crucifixion, `approximately age 25` for 2011, collapsed `Meme-crucifixion / personhood death`, and six-month formal sentence wording.
- [ ] Verify no candidate 2011 substance is stated as chemically confirmed.
- [ ] Verify the hospital dream/crows are not silently placed inside the acute psychedelic phase.
