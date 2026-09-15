# Reader Residency Wave 001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Tim, Collection, Works, Timeline, Religion, Science and World more inhabited by projecting already-owned material into the right readers with provenance-aware routing.

**Architecture:** Add one non-canonical residency map that controls which existing source/canonical records may be projected into which reader surfaces. Reader pages gain compact surface-specific sections carrying `data-residency-id` markers; a validator proves every projection maps to real owners and respects source-class boundaries. Story is not modified in this wave because active Story restoration work already exists.

**Tech Stack:** Static HTML, JSON, Python validation, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-reader-residency-wave-001-design.md`

## Global Constraints

- Keep exactly five homepage primary gateways unchanged.
- Do not modify `tim-dooley/story/index.html` or `story-content/` in this wave.
- Do not create a new canonical fact owner; `knowledge/guides/reader-residency-map.json` has `knowledge_owner:false`.
- Memory-summary material must never be rendered as verified quotation.
- Use only URL parameters already supported by `app/timeline.js`.
- Preserve Philosophy Spiral Reader architecture.
- Run the full repository quality workflow on the exact final PR head before merge.

---

### Task 1: Residency contract and RED validator

**Files:**
- Create: `scripts/validate_reader_residency.py`
- Modify: `.github/workflows/quality-checks.yml`
- Later create: `knowledge/guides/reader-residency-map.json`

**Interfaces:**
- Consumes: reader HTML files and the future residency map.
- Produces: one executable validation contract used by CI.

- [ ] **Step 1: Write the failing validator**
  - Require `knowledge/guides/reader-residency-map.json`.
  - Require the ten IDs from the spec.
  - Check owner-path existence, target-surface vocabulary, `knowledge_owner:false`, memory-summary quotation rules, timeline query parameters, and reader markers.
  - The seven required reader files are:
    - `tim-dooley/index.html`
    - `corporium/index.html`
    - `works/index.html`
    - `timeline/index.html`
    - `religion/index.html`
    - `science/index.html`
    - `world/index.html`
- [ ] **Step 2: Add `python scripts/validate_reader_residency.py` to `quality-checks.yml` beside reader/House projection validators.**
- [ ] **Step 3: Commit RED and confirm Actions fails because the residency map/markers do not yet exist.**

### Task 2: Create the residency map

**Files:**
- Create: `knowledge/guides/reader-residency-map.json`

**Interfaces:**
- Produces ten residency records keyed by stable `id`.

- [ ] **Step 1: Add exactly ten residency records:**
  - `tim-making-things`
  - `ordinary-absurd-tim`
  - `builder-gardener-service`
  - `information-architecture-feb-2026`
  - `spiritual-bank-mar-2026`
  - `ontology-reversal-mar-apr-2026`
  - `not-a-ghost-repair-may-2026`
  - `north-vocabulary-evolution`
  - `door-root-mud-sprout`
  - `creative-objects-navigation`
- [ ] **Step 2: Point each record only to existing owner paths and define target surfaces.**
- [ ] **Step 3: Add timeline queries using supported parameters only.**
- [ ] **Step 4: Run/observe validator; expected failure now moves from missing map to missing reader markers.**

### Task 3: Inhabit Tim and Collection

**Files:**
- Modify: `tim-dooley/index.html`
- Modify: `corporium/index.html`

**Interfaces:**
- Consumes residency IDs from Task 2.
- Produces human-readable projections with exact `data-residency-id` markers.

- [ ] **Step 1: Add Tim `Tim in motion` section** with Making, Voice, Builder/Gardener and Repair facets.
- [ ] **Step 2: Add links to Works, Collection, Story, Timeline and evidence/deep routes where appropriate.**
- [ ] **Step 3: Add Collection `Voice trails` section before Ladder/anatomy material.**
- [ ] **Step 4: Add five source-classed trails: mundane/divine inversion, North vocabulary, build→service, Door/Root/Mud/Sprout, Ghost→repair.**
- [ ] **Step 5: Ensure memory-summary material is paraphrased, not quoted.**
- [ ] **Step 6: Verify residency validator failures now concern only remaining surfaces.**

### Task 4: Inhabit Works and Timeline

**Files:**
- Modify: `works/index.html`
- Modify: `timeline/index.html`

**Interfaces:**
- Works projects creative owners; Timeline links into existing runtime state.

- [ ] **Step 1: Add Works `Making timeline`** covering 2024 Great Book, 2025 music/AI/streaming, 2026 games/maps/archive/site-building.
- [ ] **Step 2: Add stable archive/Story/Explore links from existing Works cards where a strongest existing route exists; do not invent missing artifact pages.**
- [ ] **Step 3: Add Timeline `Follow a development` corridor above the explorer with six links:** information architecture, spiritual bank, ontology reversal, Not-a-Ghost/repair, North vocabulary, Builder→Gardener→service.
- [ ] **Step 4: Use only supported `tl_q`, `tl_from`, `tl_to`, `tl_layers`, `tl_actors`, `tl_epistemic`, `tl_detail`, `tl_exact`, `tl_sort`, `tl_event` parameters.**
- [ ] **Step 5: Verify validator failures now concern only Religion/Science/World.**

### Task 5: Inhabit Religion, Science and World

**Files:**
- Modify: `religion/index.html`
- Modify: `science/index.html`
- Modify: `world/index.html`

**Interfaces:**
- Produces three compact developmental/process sections.

- [ ] **Step 1: Religion — add `Theology changed over time`** for Mar 8 → Apr 9 → Apr 14 → mature Father/Ladder + Son/Door formulation, explicitly as project development.
- [ ] **Step 2: Science — add `How a Tim question becomes a model`** with the six-stage process from raw observation/metaphor to testable claim/non-scientific boundary and document/audit.
- [ ] **Step 3: World — add `From symbolic North to relational systems`** separating symbolic North, country/capability mapping, North Programme/European system-building, and empirical World views.
- [ ] **Step 4: Run the residency validator and require PASS.**

### Task 6: Integration review and merge

**Files:**
- No new production files unless verification reveals a scoped defect.

- [ ] **Step 1: Open draft PR with scope and Story non-collision note.**
- [ ] **Step 2: Inspect changed-file list and diff for accidental Story/homepage/Philosophy edits.**
- [ ] **Step 3: Run full Repository quality checks on the exact final head.**
- [ ] **Step 4: If `main` moves, verify the GitHub PR merge ref or rebase/merge as needed and rerun exact-head integration checks.**
- [ ] **Step 5: Mark ready and merge with expected-head SHA guard only after green CI and clean review.**
