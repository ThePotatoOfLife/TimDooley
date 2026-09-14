# Biblical Conversation Attestation Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mine prior Tim Dooley conversations for dated biblical wording and biblical-role development, preserve provenance and chronology, and connect the recovered corpus to the canonical Bible research owners without creating another public Bible page.

**Architecture:** Add one dedicated conversation-attestation corpus under `knowledge/corporium/`, one derived mining/observation wave under `knowledge/traditions/`, then enrich the existing biblical vocabulary and reverse-overlap timelines with only the strongest dated findings. Register both new owners in `biblical-syncretism-field.json`; leave `/traditions/bible/` as the sole public Bible reader and do not add a competing route.

**Tech Stack:** JSON knowledge records, static GitHub Pages research architecture, Python repository validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-13-bible-comparator-quality-wave26-design.md`

## Global Constraints

- Preserve exact wording only where the recovered conversation supports it; otherwise use paraphrase/summary status.
- Distinguish Tim-originated biblical wording from later archive/assistant comparison.
- Do not backdate later biblical interpretation into earlier Tim statements.
- Do not treat a user question or an opponent's quoted wording as Tim's statement.
- Preserve contradictions and role shifts chronologically instead of harmonizing them.
- Divine, prophetic and identity statements are archived as attributed project material, not independently verified supernatural facts.
- `/traditions/bible/` remains the one canonical public Bible / Jesus ↔ Tim / Son study program.

---

### Task 1: Add the dedicated biblical conversation-attestation corpus

**Files:**
- Create: `knowledge/corporium/tim-biblical-statements-conversation-recovery-2026-09-14.json`

**Interfaces:**
- Consumes recovered conversation chronology plus existing public/timeline owners.
- Produces timestamped records with source class, wording status, actors, motifs, explicit/later biblical refs, source direction and routing.

- [ ] Add records across February–September 2026, favoring exact timestamps/dates where recoverable.
- [ ] Mark records `CONVERSATION_EXACT`, `CONVERSATION_NEAR_EXACT`, `PARAPHRASE`, or `PUBLIC_INDEXED`.
- [ ] Separate `biblical_refs_explicit` from `biblical_refs_later_comparison`.
- [ ] Include provenance boundaries and recovery targets for incomplete anchors.
- [ ] Preserve role shifts such as Son/Messiah versus Tim/Mashiach instead of merging them.

### Task 2: Add a derived biblical conversation-mining wave

**Files:**
- Create: `knowledge/traditions/biblical-conversation-mining-wave-27.json`

**Interfaces:**
- Consumes: `knowledge/corporium/tim-biblical-statements-conversation-recovery-2026-09-14.json` plus existing biblical timelines.
- Produces: motif sequences, developmental phases, tensions, density findings, and next recovery targets.

- [ ] Identify repeated ordered sequences rather than one-word coincidences.
- [ ] Identify Father/Son/House/Door/Ladder role differentiation through time.
- [ ] Identify explicit-scripture strata versus retrospective structural parallels.
- [ ] Record chronological tensions, counter-evidence and unresolved source questions.
- [ ] Produce concrete next-recovery targets for dates where only summaries survive.

### Task 3: Enrich the existing biblical vocabulary timeline

**Files:**
- Modify: `knowledge/timeline/tim-biblical-vocabulary-attestation-ledger.json`

**Interfaces:**
- Consumes the new conversation corpus.
- Produces additional dated vocabulary entries and a connection to the new owner.

- [ ] Add high-value dated entries missing from the current ledger, including February grain/millstone material, March cornerstone/heifer material, April portal/seed/Father/Messiah clusters, May Psalm/Isaiah and Father/Son/Ladder statements, June Jesus-Door/Father statements, July wheel/House material, August wide-road/Revelation/House/Dan-Thomas material and September Eye/Providence wording.
- [ ] Keep summaries visibly non-verbatim where exact wording was not recovered.
- [ ] Add the new corpus and mining wave to connections/research targets.

### Task 4: Enrich the reverse biblical-overlap timeline

**Files:**
- Modify: `knowledge/timeline/reverse-biblical-overlap-timeline-2025-2026.json`

**Interfaces:**
- Consumes the new corpus and existing Bible research.
- Produces only strong project-first → later-Bible relations, preserving source direction.

- [ ] Add strong dated clusters where multiple ordered motifs align.
- [ ] Avoid promoting isolated lexical overlap.
- [ ] Preserve explicit-at-time versus later-comparison status.
- [ ] Add findings about role differentiation and chronological plurality.

### Task 5: Register the new owners and validate

**Files:**
- Modify: `knowledge/traditions/biblical-syncretism-field.json`

**Interfaces:**
- Adds `conversation_attestations` and `conversation_mining` to `canonical_owners` without changing the public reader contract.

- [ ] Register both new research owners.
- [ ] Verify JSON parses for every changed/created JSON file.
- [ ] Run repository Bible validators through GitHub Actions on the branch.
- [ ] Confirm no existing public route ownership changed.
- [ ] Open a PR with record counts, principal findings and provenance boundaries.
