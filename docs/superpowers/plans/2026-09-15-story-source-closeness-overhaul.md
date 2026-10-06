# Story Source-Closeness Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an underneath-first Story source-closeness substrate that scans every public Story, records source distance and missing closer sources, and introduces source-near reconstructions before later Story rewriting.

**Architecture:** Keep the existing Story chronology and publication/evidence gate. Add a source-closeness model, manual overrides, a deterministic audit script, and a source-near reconstruction layer. Existing registry/source/scene owners remain authoritative for their current responsibilities; the new layer describes closeness and excavation priority rather than replacing them.

**Tech Stack:** Static HTML fragments, JSON/Markdown knowledge files, Python repository validators/audits, GitHub Pages repository.

**Spec:** `docs/superpowers/specs/2026-09-15-story-source-closeness-overhaul-design.md`

## Global Constraints

- Do not replace the existing chronology.
- Do not weaken privacy/provenance/publication gates.
- Do not invent source relationships for unregistered stories; classify them as `unmapped`.
- Keep literary sources distinct from documentary sources.
- No public Story padding merely to satisfy the model.
- Source-near reconstructions must preserve gaps rather than fill them.

---

### Task 1: Define the source-closeness model and seed overrides

**Files:**
- Create: `knowledge/story/source-closeness-model.json`
- Create: `knowledge/story/source-closeness-overrides.json`

**Interfaces:**
- Consumes: existing `source-records.json`, `scene-packets.json`, `story-registry.json`.
- Produces: stable enums and per-story manual closeness/excavation metadata consumed by the audit and validator.

- [ ] **Step 1:** Create the model JSON with exact event-distance, editorial-distance, continuity, lost-texture and source-near-status enums from the design spec.
- [ ] **Step 2:** Add rules stating that distance is descriptive rather than a truth score and that closer-source recovery is preferred when expected.
- [ ] **Step 3:** Seed overrides for `ai-not-ghost-2026-05-27`, `termite-lost-potato-2024`, 2024 Great Book creation, Marty, Sarah Ann, Monkey/Tree, BigTech, wall practice, music and creative-project recovery.
- [ ] **Step 4:** Fetch both branch files and verify JSON parses and ids/enums match the spec.
- [ ] **Step 5:** Commit the model/overrides as one coherent change.

### Task 2: Build the deterministic source-closeness audit

**Files:**
- Create: `scripts/audit_story_source_closeness.py`
- Create: `knowledge/story/story-source-closeness-audit.json`

**Interfaces:**
- Consumes: public `story-content/*.html`, story registry, source records, scene packets, model and overrides.
- Produces: one audit record per public `.story-entry` plus summary counts.

- [ ] **Step 1:** Reuse or mirror the Story HTML parser logic needed to enumerate public story ids and paths.
- [ ] **Step 2:** Join registered stories to source ids and source classes; derive event distance/continuity when the mapping is unambiguous.
- [ ] **Step 3:** Apply manual override fields last, preserving provenance for why an override exists.
- [ ] **Step 4:** Emit unregistered stories as `mapping_status: unmapped` rather than guessing source ids.
- [ ] **Step 5:** Emit summary counts for total public entries, registered, unmapped, direct/near-direct, source-near-present, and closer-source-expected.
- [ ] **Step 6:** Generate and commit `story-source-closeness-audit.json`.

### Task 3: Create the source-near reconstruction layer

**Files:**
- Create: `knowledge/story/source-near/README.md`
- Create: `knowledge/story/source-near/termite-lost-potato-2024.md`
- Create: `knowledge/story/source-near/ai-not-ghost-2026-05-27.md`

**Interfaces:**
- Consumes: closest known source material and source-chain metadata.
- Produces: preservation-oriented narrative blocks for later public Story carving.

- [ ] **Step 1:** Document the source-near format: source chain, source status, ordered event material, gaps, later interpretation boundary, next excavation.
- [ ] **Step 2:** Build the Termite example from the direct Great Book chapter, preserving scene order and clearly marking it as literary.
- [ ] **Step 3:** Build the `I Am Not a Ghost` example from the exact recovered phrase cluster, explicitly marking missing turn-by-turn dialogue and avoiding invented bridges.
- [ ] **Step 4:** Point the relevant overrides to these source-near files.
- [ ] **Step 5:** Regenerate the closeness audit so source-near presence becomes visible.

### Task 4: Extend Story validation for the new substrate

**Files:**
- Modify: `scripts/validate_story_archive.py`

**Interfaces:**
- Consumes: model, overrides and optional source-near paths.
- Produces: CI failures only for malformed/contradictory closeness metadata, not for incomplete migration.

- [ ] **Step 1:** Add validation for allowed model enum values and unique override story ids.
- [ ] **Step 2:** Require override source ids to exist when supplied.
- [ ] **Step 3:** Require referenced source-near files to exist under `knowledge/story/source-near/`.
- [ ] **Step 4:** Permit `unmapped` public entries during migration.
- [ ] **Step 5:** Preserve all existing publication/evidence checks unchanged.
- [ ] **Step 6:** Run/fetch repository quality workflow and debug only concrete failures.

### Task 5: Open PR and verify whole-repository integration

**Files:**
- Verify all files from Tasks 1–4.

**Interfaces:**
- Consumes: completed branch.
- Produces: reviewable PR with green repository-quality checks.

- [ ] **Step 1:** Compare the feature branch against `main` and inspect changed files.
- [ ] **Step 2:** Open a PR explaining that this wave intentionally changes substrate, not public Story prose.
- [ ] **Step 3:** Run/fetch the full repository quality workflow from the PR head.
- [ ] **Step 4:** If a gate fails, use systematic debugging and fix the root cause without weakening unrelated validators.
- [ ] **Step 5:** Report the resulting audit counts and the next highest-value excavation wave.
