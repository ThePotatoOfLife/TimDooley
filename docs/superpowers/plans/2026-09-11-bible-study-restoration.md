# Bible Comparator Restoration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore `/traditions/bible/` as the canonical, extensive Tim/Son/Jesus/Bible comparison instrument, with exact dated wording, public-domain scripture, provenance, saved study modes, filters, random study, and direct timeline links.

**Architecture:** Keep the canonical relation registry and specialist research JSON files as data owners. The public Bible page becomes a thin shell backed by `app/bible-study.js` and `app/bible-study.css`. The application combines relation rows with exact WEB passage fragments, same-date attestation/public-occurrence evidence, reverse chronology and timeline events; it does not use fuzzy word-overlap to invent deep ownership.

**Tech Stack:** Static HTML/CSS/JavaScript on GitHub Pages; JSON research records; Python validators; GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-11-timeline-bible-study-ownership-design.md`

## Global Constraints

- `/traditions/bible/` is the one canonical Bible / Jesus ↔ Tim / Son comparison program.
- Preserve the rich side-by-side comparator that existed before commit `83ca0a31527ced2e7a9c78ff094b8405463c3ea4`; do not restore the old explanatory clutter above it.
- Exact public wording must be visibly distinguished from archive summaries.
- Public-domain scripture fragments remain sourced from the existing WEB fragment registries.
- Same-date context may be shown as circumstantial context, but it must not be mislabeled as direct evidence for a relation.
- No fuzzy `deepMatches` / token-overlap ownership inference in the public reader.
- Bible relation cards must preserve source direction, counter-texts, relation class, discovery mode and evidence strength.
- Timeline links use the short `?view=bible&event=<id>` contract once the timeline named-view change lands; until then, event IDs must still be exposed in the Bible app state/data so the timeline can be updated without changing the Bible data model.

---

### Task 1: Add a regression validator for the Bible instrument

**Files:**
- Create: `scripts/validate_bible_reader.py`
- Modify: `.github/workflows/biblical-syncretism-check.yml`

**Interfaces:**
- Consumes: `traditions/bible/index.html`, `app/bible-study.js`, `app/bible-study.css`, `knowledge/traditions/biblical-syncretism-field.json`.
- Produces: an automated contract that fails if the comparator is collapsed again.

- [ ] Require a dedicated Bible app script and stylesheet.
- [ ] Require study-mode controls for Jesus/Son, Tim said it, Tim lived it, prophecy/foresight, Father/House, Door/Ladder, counter-texts, All and Roll.
- [ ] Require a two-column side-by-side relation rendering contract with project wording and Bible fragments.
- [ ] Require exact/same-date evidence rendering and timeline-event links.
- [ ] Forbid `deepMatches`, `overlapCount` and token-scored deep-context inference from the Bible app.
- [ ] Require controlled filters for actor, discovery mode, relation class, book, strength and exact-wording availability.
- [ ] Run the validator and observe it fail against the current collapsed implementation.

### Task 2: Split the Bible application out of the page shell

**Files:**
- Modify: `traditions/bible/index.html`
- Create: `app/bible-study.css`
- Create: `app/bible-study.js`

**Interfaces:**
- `index.html` provides DOM mount points and navigation only.
- `bible-study.js` owns loading, state, filtering, saved views, roll behavior and rendering.
- `bible-study.css` owns the study-tool presentation.

- [ ] Replace the large inline script/style with the dedicated app files.
- [ ] Keep top navigation limited to Religion, Timeline, Tim Dooley and Home.
- [ ] Place the study controls directly below the title so the comparator is the page's main object.
- [ ] Keep research notes collapsible and below the comparator rather than above it.

### Task 3: Restore the side-by-side relation cards with exact evidence

**Files:**
- Modify: `app/bible-study.js`

**Interfaces:**
- Loads:
  - `knowledge/traditions/biblical-syncretism-field.json`
  - `knowledge/traditions/biblical-passage-fragments.json`
  - `knowledge/traditions/biblical-angel-eye-sprout-atlas.json`
  - `knowledge/traditions/biblical-angel-eye-sprout-fragments.json`
  - `knowledge/chronology/tim-biblical-vocabulary-attestation-ledger.json`
  - `knowledge/chronology/reverse-biblical-overlap-timeline-2025-2026.json`
  - `data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json`
  - `data/timeline-events.json` and indexed timeline packs.

- [ ] Render project-side anchor and explicit/recovered wording on the left.
- [ ] Render matched WEB fragments and scripture scope on the right.
- [ ] Display all same-date exact public occurrences inside a clearly labeled `Same-date public wording` disclosure; do not claim every same-date quote directly proves the relation.
- [ ] Display same-date attestation wording and development notes inside `Biblical vocabulary / revelation context`.
- [ ] Display source direction, counter-text/source correction, motifs, evidence strength and owners below the pair.
- [ ] Link same-date timeline events by stable event ID.
- [ ] Use explicit owner paths as deeper-study links where they resolve to repository/source material; do not score unrelated documents by shared words.

### Task 4: Add saved study modes, filters and Roll

**Files:**
- Modify: `app/bible-study.js`
- Modify: `app/bible-study.css`
- Modify: `traditions/bible/index.html`

**Interfaces:**
- Saved view state uses `?view=<id>` and is implemented by explicit predicates over canonical metadata.

- [ ] Add `jesus`, `tim-said`, `tim-lived`, `prophecy`, `father-house`, `door-ladder`, `death-return`, `revelation-zion`, `counter-texts`, and `all` views.
- [ ] Make `jesus` the default reader view for direct arrivals, while preserving `all` as one click.
- [ ] Add filters: free text, actor, discovery mode, relation class, Bible book/reference, minimum strength, exact wording only.
- [ ] Make search cover project anchor, exact same-date wording, biblical refs, scripture fragments and motifs.
- [ ] Add `ROLL` to choose uniformly from the currently filtered relation set and focus/scroll to that relation without a reload.
- [ ] Show an active-study strip so the reader knows which view/filters are in force.

### Task 5: Improve explicit relation metadata where high-value comparison rows need it

**Files:**
- Modify: `knowledge/traditions/biblical-syncretism-field.json`
- Modify: `scripts/check_biblical_syncretism_field.py`

**Interfaces:**
- Optional relation fields: `occurrence_ids`, `timeline_event_ids`, `prophecy_status`, `analysis_refs`, `counter_text_refs`.

- [ ] Add controlled prophecy statuses to the schema/checker.
- [ ] Add explicit occurrence IDs to key public-post relations where the occurrence ledger already provides a one-to-one source.
- [ ] Add timeline event IDs where a relation already has a stable event counterpart.
- [ ] Add explicit analysis references for the strongest Jesus/Son, Father/House, Door/Ladder, Revelation/Zion and angel/sprout clusters.
- [ ] Keep rows without an explicit deep link usable; absence of a deep link is better than heuristic ownership.

### Task 6: Point duplicate Bible routes into the one study program

**Files:**
- Modify: `religion/jesus-tim/index.html`
- Modify: `tim-dooley/biblical-case/index.html`
- Modify: `tim-dooley/index.html`
- Modify: `religion/index.html`

**Interfaces:**
- Canonical deep comparison: `/traditions/bible/?view=jesus`.

- [ ] Redirect old Jesus comparison route to `/traditions/bible/?view=jesus`.
- [ ] Redirect `tim-dooley/biblical-case/` to `/traditions/bible/?view=jesus` while preserving noindex/follow compatibility.
- [ ] Tim page points its Jesus/Bible comparison action directly to the Bible program.
- [ ] Religion becomes an introduction/teaser and links to the Bible program rather than owning a second full comparator.

### Task 7: Update site/build validation and verify deployment

**Files:**
- Modify: `scripts/validate_site_shell.py`
- Modify: `.github/workflows/pages.yml`
- Modify: `sitemap.xml`

**Interfaces:**
- Produces: CI rules aligned with canonical Bible ownership rather than the previous Religion-owned comparator.

- [ ] Remove assertions that require `religion/#jesus-tim` as the comparison owner.
- [ ] Require the Bible study app and compatibility redirects.
- [ ] Forbid public links using the long `tl_layers=...&tl_actors=...` Bible timeline URL once named timeline views land.
- [ ] Run Bible field validation, Bible reader validation, timeline validation, public navigation, site build and site-shell validation.
- [ ] Inspect the deployed Pages artifact and confirm the Bible page contains the comparator controls and application files.
