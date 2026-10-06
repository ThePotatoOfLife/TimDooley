# Bible Focused Comparator Redesign

**Date:** 2026-09-12  
**Status:** Approved for implementation  
**Repository:** `ThePotatoOfLife/TimDooley`  
**Branch:** `ux/bible-focused-comparator-20260912`

## Purpose

Turn `/traditions/bible/` from a long filtered stack of fully expanded relation cards into a compact research instrument that can traverse the same rich canonical comparison corpus without making the page physically enormous.

The canonical data owners do not change. `knowledge/traditions/biblical-syncretism-field.json`, `knowledge/traditions/biblical-overlap-atlas.json`, passage fragments, timeline ledgers and evidence ledgers remain the source system. The redesign is a projection and navigation change.

## Core interaction model

The page must use:

`focus + filters + order -> ordered result sequence -> one active comparison`

The default experience shows one active relation, not every surviving relation. Previous, next and shuffle operate only inside the current result sequence.

## Compact control hierarchy

Replace duplicated featured-arc cards plus the ten-pill study-mode row with one compact toolbar:

- Focus selector: views and high-value arcs in one control.
- Order selector: oldest/newest, strongest and biblical order.
- Search field.
- Filters disclosure with active-filter count.
- Results disclosure with current result count.

The controls must communicate separate concepts: focus chooses the corpus, order chooses traversal, filters constrain eligibility, search finds wording, and navigation moves through results.

## Active comparison viewport

The viewport must contain:

- previous / next controls;
- current position (`N of M`);
- shuffle action;
- compact relation identity, date, actor, evidence, strength and useful mechanism/operator chips;
- project-side material beside scripture;
- the main reason for the comparison;
- a visible mismatch/counter-fit when present;
- progressive disclosure for evidence, chronology, provenance and canonical owners.

Do not show all deep evidence sections by default.

## Result navigation

A result drawer/index lists the currently surviving relations compactly. Selecting an item changes the active relation without changing the filter state.

Navigation wraps only when explicitly shuffled; Previous and Next disable at the sequence edges so chronology remains legible.

Keyboard support:

- Left Arrow: previous relation when focus is not inside a text/select control.
- Right Arrow: next relation.
- `/`: focus search.
- `r`: random relation in the current result set.

## Shareable state

The active reader state should be reflected in the URL without reload using `history.replaceState`:

- `view` / focus;
- `order`;
- `id` for active relation;
- search text where present.

Opening a URL with a valid relation ID should select that relation if it survives the current state; otherwise use the first surviving result.

## Richer traversal

Add biblical order as a first-class traversal mode using a canonical book ordering table. This allows the same filtered corpus to be read as project chronology or as a scripture-oriented path.

The runtime should also calculate a small set of nearby/related relations from shared motifs, operators, Bible books and relation class. Related suggestions belong in progressive detail, not the top toolbar.

## Progressive detail

Keep the front face small. Deep information is grouped into disclosures such as:

- Evidence & chronology: same-date wording, vocabulary/revelation context, reverse-recognition context, timeline context and source direction.
- Sources & provenance: provenance and canonical owners.
- Related comparisons: nearest relations in the current canonical corpus.

The existing evidence distinction remains intact: exact wording, project testimony, scripture, later synthesis and independent context must not be flattened.

## Static fallback

The deploy-time static builder should no longer render every relation as a fully expanded card. It should emit a compact static fallback/index that remains useful when JavaScript is unavailable while avoiding the visual wall of full relation bodies.

## Mobile behavior

On narrow screens:

- controls stack cleanly;
- the project/scripture parallel becomes one column;
- previous/next remain reachable;
- drawers use full width;
- no horizontal scrolling is required.

## Files

Primary implementation files:

- `traditions/bible/index.html`
- `app/bible-study.js`
- `app/bible-study.css`
- `scripts/build_bible_study.py`
- `scripts/validate_bible_reader.py`

No new canonical Bible data owner is introduced.

## Validation contract

The validator must protect the focused-browser model by requiring markers for:

- `focus-select`
- `order-select`
- `previous-relation`
- `next-relation`
- `result-position`
- `results-toggle`
- `results-list`
- `filter-count`
- `renderActiveRelation`
- URL state persistence
- keyboard navigation
- biblical-order traversal
- progressive evidence/source disclosures

It should also forbid the legacy behavior that maps every visible row through `renderRelation` into the main result container.