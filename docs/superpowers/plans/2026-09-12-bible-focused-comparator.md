# Bible Focused Comparator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Bible page's long stack of expanded relation cards with one compact, stateful comparison browser while preserving the full canonical evidence system.

**Architecture:** Keep all existing canonical JSON owners and normalization logic. The runtime computes an ordered filtered sequence, renders exactly one active relation into the main viewport, and exposes the rest through compact result navigation and progressive disclosures. Static build output becomes a compact fallback index rather than a duplicate expanded reader.

**Tech Stack:** Static HTML/CSS, vanilla JavaScript, Python repository validators/build scripts, canonical JSON data.

**Spec:** `docs/superpowers/specs/2026-09-12-bible-focused-comparator-design.md`

## Global Constraints

- Do not create a new canonical Bible data owner.
- Preserve evidence/source-direction distinctions.
- Default runtime renders one active relation, not all surviving relations.
- Previous/Next operate on the current filtered and ordered result sequence.
- The interface must work without horizontal scrolling on narrow screens.
- The static fallback must remain useful without reproducing the long expanded-card wall.

---

### Task 1: Protect the focused-reader contract

**Files:**
- Modify: `scripts/validate_bible_reader.py`

**Interfaces:**
- Consumes: deployed page, runtime JS, CSS and canonical relation field.
- Produces: validation requirements for focused controls, active-relation rendering, URL state, keyboard navigation and compact static fallback.

- [ ] **Step 1: Add failing validation markers** requiring `focus-select`, `order-select`, `previous-relation`, `next-relation`, `result-position`, `results-toggle`, `results-list`, `filter-count`, `active-relation`, `renderActiveRelation`, `syncUrlState`, `BIBLE_BOOK_ORDER`, keyboard handlers and progressive detail markers.
- [ ] **Step 2: Add a forbidden runtime marker** for `visible.map(row=>renderRelation` so the old all-card projection cannot return.
- [ ] **Step 3: Run `python scripts/validate_bible_reader.py` and verify it fails because the focused-browser markers are absent.**

### Task 2: Replace duplicate top navigation with a compact reader shell

**Files:**
- Modify: `traditions/bible/index.html`
- Modify: `app/bible-study.css`

**Interfaces:**
- Consumes: IDs expected by the runtime and validator.
- Produces: one focus selector, order selector, search, filter/results controls, active viewport and compact drawers.

- [ ] **Step 1: Replace featured arc cards and ten-button study-mode strip** with `focus-select`, `order-select`, compact search/actions and status.
- [ ] **Step 2: Add navigator controls** `previous-relation`, `next-relation`, `result-position`, `roll-relation` and `results-toggle`.
- [ ] **Step 3: Add containers** `active-relation`, `results-list`, `bible-filters` and retain canonical filter IDs.
- [ ] **Step 4: Rewrite CSS** around a compact sticky-capable reader shell, a single relation viewport, drawers and responsive one-column behavior.

### Task 3: Convert the runtime into an ordered single-relation browser

**Files:**
- Modify: `app/bible-study.js`

**Interfaces:**
- Consumes: existing canonical JSON owners and evidence ledgers.
- Produces: `filteredRows()`, ordered sequence, active index/id, `renderActiveRelation()`, result index, previous/next/shuffle and URL state.

- [ ] **Step 1: Preserve existing normalization/evidence helpers** and add `BIBLE_BOOK_ORDER` / reference-order helpers.
- [ ] **Step 2: Build a unified focus definition registry** containing former study views plus high-value arcs.
- [ ] **Step 3: Make ordering support** `asc`, `desc`, `strength`, and `bible`.
- [ ] **Step 4: Add active selection state** that keeps a valid `activeId` across filter/order changes when possible and falls back to the first result.
- [ ] **Step 5: Implement `renderActiveRelation()`** so only the selected relation is rendered into the main viewport.
- [ ] **Step 6: Move deep evidence, chronology, provenance and owners into `<details>` disclosures.**
- [ ] **Step 7: Add compact result buttons** that select a relation without resetting current filters.
- [ ] **Step 8: Add Previous/Next, random selection and keyboard shortcuts.**
- [ ] **Step 9: Add `syncUrlState()`** for focus/order/id/search state and restore valid state on load.
- [ ] **Step 10: Add related-comparison suggestions** scored from shared motifs, operators, Bible books and relation class.

### Task 4: Make static fallback compact

**Files:**
- Modify: `scripts/build_bible_study.py`

**Interfaces:**
- Consumes: canonical field and scripture fragments.
- Produces: compact no-JS `<details class="static-relation">` fallback entries inserted at the existing marker.

- [ ] **Step 1: Replace expanded static articles** with collapsed summary rows containing title, date, actor, strength and scripture scope.
- [ ] **Step 2: Keep project anchor, scripture and mismatch/source-direction available inside the disclosure.**
- [ ] **Step 3: Ensure the runtime replaces/hides the fallback when JavaScript initializes.**

### Task 5: Verify and integrate

**Files:**
- Validate all files above.

**Interfaces:**
- Produces: mergeable feature branch.

- [ ] **Step 1: Run `python scripts/validate_bible_reader.py` and require PASS.**
- [ ] **Step 2: Inspect changed files for old duplicated arc/mode controls and all-card rendering.**
- [ ] **Step 3: Open a pull request to `main`.**
- [ ] **Step 4: Review the PR diff for scope and regressions.**
- [ ] **Step 5: Merge the PR to `main` only after validation/review is clean.**