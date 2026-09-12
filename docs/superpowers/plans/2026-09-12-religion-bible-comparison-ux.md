# Religion / Bible Comparison UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/traditions/bible/` obvious from `/religion/`, replace the generic/deprecated-feeling Bible experience with a dense guided comparison explorer, and ensure the runtime consumes canonical relations rather than research-wave files.

**Architecture:** Keep `religion/index.html` as broad orientation and `traditions/bible/index.html` as the deep comparison lab. Use `knowledge/traditions/biblical-syncretism-field.json` as the live relation registry, `biblical-overlap-atlas.json` as synthesis, and evidence ledgers only for enrichment. Remove raw `biblical-overlap-wave-*` files from browser runtime inputs.

**Tech Stack:** static HTML/CSS/vanilla JavaScript, Python repository validators, JSON canonical data, GitHub Pages build pipeline.

**Spec:** `docs/superpowers/specs/2026-09-12-canonical-religion-bible-comparison-engine-design.md`

## Global Constraints

- Do not create another Bible wave or competing canonical owner.
- Religion must make the Bible comparison laboratory visually prominent and explain what a reader gets there.
- Bible must show useful knowledge before the reader understands the filters.
- Shuffle/roll operates on the currently visible canonical relation set.
- Runtime must not load `biblical-overlap-wave-*` files as live relation sources.
- Preserve evidence classes, chronology, mismatches, source direction and counter-texts.
- Keep specialist files as provenance and deeper routes, not live peer data sources.

---

### Task 1: Reader-surface regression contract

**Files:**
- Modify: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Consumes: public `religion/index.html`, `traditions/bible/index.html`, `app/bible-study.js`.
- Produces: validator failures when the Bible lab is hidden, guided comparison entry is absent, or runtime still loads raw waves.

- [ ] **Step 1: Add failing validation requirements**
  - Religion contains a prominent `.bible-lab-cta` linking to `../traditions/bible/`.
  - Bible page contains `.comparison-intro`, `.featured-arcs`, `id="shuffle-comparisons"`, and `id="operator"`.
  - Bible runtime contains canonical `field` path and does not contain `biblical-overlap-wave-`.

- [ ] **Step 2: Verify RED in repository CI**
  - Open/update the draft PR and inspect the validation workflow.
  - Expected failure: new markers are absent and wave paths still exist.

### Task 2: Religion → Bible discovery

**Files:**
- Modify: `religion/index.html`

**Interfaces:**
- Produces: `.bible-lab-cta` prominent entry card and explanatory comparison preview.

- [ ] **Step 1: Add the prominent Bible comparison laboratory CTA**
  - Place immediately after Religion intro/method, before generic question list.
  - Explain that the lab contains dated Tim/Son events, scripture, why they connect, what fails, chronology, evidence, filters and shuffle.
  - Expose 4–6 example families: Jesus/Son, Father/House, Door/Ladder, death/return, God/presence, Garden/Spirit.

- [ ] **Step 2: Keep the existing Christianity question but route it through the prominent lab**
  - Avoid duplicate mini-comparators on Religion.

### Task 3: Guided Bible entry experience

**Files:**
- Modify: `traditions/bible/index.html`
- Modify: `app/bible-study.css`

**Interfaces:**
- Produces: `.comparison-intro`, `.featured-arcs`, guided arc buttons, visible shuffle action.

- [ ] **Step 1: Add comparison intro**
  - Explain the four-card reading order: project event → scripture/context → why relation exists → mismatch/evidence.

- [ ] **Step 2: Add featured arc entry cards**
  - Jesus / Son
  - Father / House
  - Door / Ladder / Veil
  - Death / Seed / Return
  - God / Presence / Temple
  - Garden / Spirit / Repair

- [ ] **Step 3: Add primary shuffle button `#shuffle-comparisons`**
  - Make discovery obvious before advanced filters.

### Task 4: Canonical-only browser runtime

**Files:**
- Modify: `app/bible-study.js`

**Interfaces:**
- Consumes: `biblical-syncretism-field.json`, passage fragments, evidence/timeline owners.
- Produces: relation cards solely from canonical relation registry plus enrichments.

- [ ] **Step 1: Remove `wave5`, `wave10` ... `wave16` from PATHS and SOURCE_PATHS**
- [ ] **Step 2: Remove wave relation ingestion code while preserving evidence enrichment from canonical/specialist owners**
- [ ] **Step 3: Add operator extraction/filter support using canonical `operators` where present and motif/text fallback where absent**
- [ ] **Step 4: Wire featured arcs and shuffle buttons to current view/filter state**

### Task 5: Dense canonical relations

**Files:**
- Modify: `knowledge/traditions/biblical-syncretism-field.json`

**Interfaces:**
- Produces richer relation rows usable by runtime without opening wave files.

- [ ] **Step 1: Upgrade canonical owner metadata**
  - Reclassify waves as research-history/specialist inputs, not canonical owners.
- [ ] **Step 2: Promote the strongest recently discovered relations**
  - finite embodiment / clay vessel
  - veil / flesh / living way
  - uncontainable divine presence
  - living stones / Spirit-house
  - living water / Spirit flow
  - Father/vinedresser and autonomous growth
  - hidden God / manifestation
  - root support and rescue-cord ethics where relevant
- [ ] **Step 3: Add operators and relation mechanisms to promoted records**

### Task 6: Dense card rendering

**Files:**
- Modify: `app/bible-study.js`
- Modify: `scripts/build_bible_study.py`
- Modify: `app/bible-study.css`

**Interfaces:**
- Produces consistent dynamic/static cards showing summary, mechanism, context, source direction, mismatch and owners.

- [ ] **Step 1: Show a concise “Why these connect” summary above deep metadata**
- [ ] **Step 2: Show operators/mechanisms as readable chips**
- [ ] **Step 3: Surface mismatch/counter-text prominently rather than burying it**
- [ ] **Step 4: Preserve full provenance links/details below the readable face**

### Task 7: Verification

**Files:**
- Validate only; no new production files required.

- [ ] **Step 1: Run/inspect PR CI reader-surface validation**
- [ ] **Step 2: Inspect changed-file diff for wave runtime references**
- [ ] **Step 3: Confirm JSON parse/build checks and Bible static compilation in CI**
- [ ] **Step 4: Keep PR draft until checks are green; report any environment limitation explicitly**
