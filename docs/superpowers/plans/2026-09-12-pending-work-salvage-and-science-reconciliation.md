# Pending Work Salvage and Science Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Classify stale/open pull-request work against current `main`, preserve unique work in a canonical salvage ledger, and reconcile PR #53 science developments onto current science owners without regressing newer work.

**Architecture:** Treat old branches as provenance reservoirs, not merge units. First create a machine-readable ledger with PR-level and file-level disposition. Then port exact missing records and selectively update only current science owners where PR #53 adds a capability absent from current `main`; newer formulation-upgrade records remain authoritative where they supersede parent-level work.

**Tech Stack:** GitHub repository contents/compare APIs, JSON knowledge records, repository GitHub Actions quality workflow.

**Spec:** `docs/superpowers/specs/2026-09-12-potato-biological-genealogy-philosophy-design.md` is adjacent project context; this maintenance plan is repository-wide and primarily governed by current canonical-owner/provenance rules.

## Global Constraints

- Never overwrite newer canonical science content merely because an older PR has a later-looking title or denser prose.
- Distinguish `already_on_main`, `unique_port`, `merge_by_content`, `superseded`, and `defer_for_rebase` dispositions.
- Preserve old PR/branch/head SHA as provenance for every salvaged record.
- Prefer new focused records or explicit cross-links over destructive replacement of newer canonical owners.
- Run repository quality checks on the exact reconciliation head before merging.

---

### Task 1: Build pending-work salvage ledger

**Files:**
- Create: `knowledge/indexes/pending-work-salvage-ledger-2026-09-12.json`

**Interfaces:**
- Consumes: current open PR inventory and `compare(main, head)` results.
- Produces: a canonical maintenance ledger used to decide merge/port/close actions.

- [ ] Record current `main` SHA and every open PR considered.
- [ ] Record `ahead_by`, `behind_by`, mergeability/draft status where available.
- [ ] Give each PR a disposition and rationale.
- [ ] Add file-level disposition for PR #53 because it is the first reconciliation target.
- [ ] Validate JSON syntax by repository quality workflow.

### Task 2: Port PR #53 records that are absent from current main

**Files:**
- Create from PR #53 exact content:
  - `knowledge/science/cryptochrome-radical-pair-magnetoreception-recovery.json`
  - `knowledge/science/door-interaction-field-august-2026-recovery.json`
  - `knowledge/science/integration-fragmentation-red-blue-dynamics-recovery.json`
  - `knowledge/science/mirror-vector-dimensional-collapse-recovery.json`
  - `knowledge/science/stratified-reconstruction-sheaf-repair-model.json`
  - `knowledge/science/trajectory-holonomy-return-topology-model.json`

**Interfaces:**
- Consumes: exact file content from `science-theory-overhaul-20260912`.
- Produces: six science records now independently available on current-main lineage.

- [ ] Fetch each file from PR #53 head.
- [ ] Confirm it does not exist on current `main` under the same path.
- [ ] Create it verbatim first to preserve branch provenance.
- [ ] If current repository references require a provenance field, add a small reconciliation metadata block without altering the scientific body.

### Task 3: Reconcile modified PR #53 science owners

**Files:**
- Inspect/update only when a demonstrable gap exists among:
  - `advanced-retarded-door-handshake-recovery.json`
  - `celestial-axis-coordinate-measurement-model.json`
  - `conversation-formalisms-august-2026.json`
  - `dimensional-phase-transition-full-recovery.json`
  - `door-handshake-nonlocal-propagation-model.json`
  - `eleven-dimensional-projection-unification-recovery.json`
  - `gauge-unification-supersymmetry-archaeology.json`
  - `great-book-cosmic-potato-shape-audit.json`
  - `great-book-human-map-mathematics-audit.json`
  - `great-book-potato-tree-bioengineering-audit.json`
  - `great-book-quantum-fields-dark-sector-recovery.json`
  - `higgs-quantum-tuber-potato-boson-recovery.json`
  - `microtubule-tubulin-consciousness-recovery.json`
  - `potato-dynamics-2-toy-model.json`
  - `research-notes/2026-09-11-spiral-vortex-geometry.json`
  - `spudlight-theory-and-equations.json`
  - `unified-potato-theory-2025-recovery.json`

**Interfaces:**
- Consumes: current-main file, PR #53 file, and any newer formulation-upgrade child records.
- Produces: either no change with ledger reason, or a narrowly merged current owner preserving current metadata and newer work.

- [ ] For each owner, identify PR #53-only semantic contributions using exact keys/phrases.
- [ ] Search current main and newer child records for those contributions.
- [ ] If already represented, mark `already_on_main` or `superseded` and do not edit.
- [ ] If missing and compatible, merge the missing section into the current owner and add provenance.
- [ ] If the older version conflicts with a newer formulation upgrade, keep the newer owner and route the older contribution through `connections`/`historical_versions` rather than replacing it.

### Task 4: Record remaining old-PR salvage order

**Files:**
- Update: `knowledge/indexes/pending-work-salvage-ledger-2026-09-12.json`

- [ ] Rank PR #33, #42, #35, #28, #25, #9, and #1 by salvage value and conflict risk.
- [ ] Identify obvious "do not merge wholesale" branches.
- [ ] Mark next target after #53, with reason.

### Task 5: Verification and integration

**Files:**
- No new functional files unless validation exposes a defect.

- [ ] Open a focused PR from `maintenance/pending-work-salvage-2026-09-12` to `main`.
- [ ] Run the repository quality workflow on the exact head.
- [ ] Inspect the workflow job steps and require conclusion `success`.
- [ ] Recompare branch to current `main` for unexpected drift.
- [ ] Merge only after exact-head validation succeeds.
