# Final Gap Salvage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote only genuinely missing, still-current knowledge or infrastructure from leftover historical branches into current `main` without reintroducing stale runtime or duplicate canonical owners.

**Architecture:** Work from a fresh branch cut from current `main`. Compare a small set of high-value historical branches against current `main`, classify each delta as already present, unique-and-current, superseded, or archive-only, then port only unique-and-current assets. Keep canonical ownership and current reader/runtime architecture unchanged unless a missing asset clearly belongs there.

**Tech Stack:** GitHub repository contents API, existing JSON/Markdown knowledge architecture, repository quality checks.

**Spec:** `TODO.md`, `knowledge/guides/project-growth-compass.json`, and `knowledge/indexes/pending-work-salvage-ledger-2026-09-12.json`.

## Global Constraints

- Never merge a stale branch wholesale.
- Preserve one canonical owner per durable concept.
- Do not promote generated snapshots, obsolete UI, or duplicate reader surfaces.
- Preserve provenance and explicit epistemic class.
- Verify the exact branch head before merging to `main`.

---

### Task 1: Inventory residual branch deltas

**Files:**
- Modify only this plan if audit notes need correction.

**Interfaces:**
- Consumes: current `main` and historical branch refs.
- Produces: a classified shortlist of salvage candidates.

- [ ] Compare the highest-value remaining historical branches to current `main`.
- [ ] Reject files already present or superseded on `main`.
- [ ] Select only additive files or narrowly reconcilable knowledge that remains absent.

### Task 2: Port missing canonical knowledge

**Files:**
- Create only exact missing knowledge/research records proven absent from `main`.
- Modify existing canonical indexes only when required for discoverability.

**Interfaces:**
- Consumes: Task 1 shortlist.
- Produces: current-main-native records with preserved provenance.

- [ ] Fetch source branch versions of selected files.
- [ ] Create them on `maintenance/final-gap-salvage-2026-09-12`.
- [ ] Avoid importing stale page/runtime copies.

### Task 3: Repair stale maintenance state

**Files:**
- Modify: `knowledge/indexes/pending-work-salvage-ledger-2026-09-12.json` only if its live-state claims are stale.

**Interfaces:**
- Consumes: actual current PR state and completed salvage status.
- Produces: an accurate provenance/resolution ledger rather than a false live backlog.

- [ ] Reconcile live PR count/status with the ledger.
- [ ] Preserve historical PR information while marking it resolved/archival.

### Task 4: Verify and integrate

**Files:** none beyond Tasks 1–3.

**Interfaces:**
- Consumes: exact salvage branch head.
- Produces: verified PR and merged `main` if checks pass.

- [ ] Compare salvage branch against `main` and inspect changed files.
- [ ] Open a PR.
- [ ] Run repository quality checks on the exact head.
- [ ] Merge only if checks pass.
- [ ] Fetch `main` again and report the exact resulting SHA.
