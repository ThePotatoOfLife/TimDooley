# Story Reservoir Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a durable story backend and begin shifting the public Story from explanatory capsules toward one continuous chronicle.

**Architecture:** Six focused JSON owners under `knowledge/story/` store cast, scenes, dialogue, arcs, unresolved leads and their manifest. A validator enforces IDs and cross-references. The public reader remains simple and only receives light framing changes in this wave.

**Tech Stack:** Static JSON, HTML/CSS, Python validation, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-14-story-reservoir-design.md`

## Global Constraints
- Do not invent missing dialogue or scene details.
- Preserve source status and period-specific role changes.
- Keep the public reader chronological and readable rather than dashboard-like.
- Store unresolved material in the recovery notebook.

### Task 1: Story backend
- [ ] Create `knowledge/story/story-manifest.json`.
- [ ] Create `knowledge/story/cast-book.json` with initial recurring cast classes and period roles.
- [ ] Create `knowledge/story/scene-reservoir.json` with initial high-confidence scene leads.
- [ ] Create `knowledge/story/dialogue-vault.json` with source-status metadata.
- [ ] Create `knowledge/story/arc-season-map.json`.
- [ ] Create `knowledge/story/recovery-notebook.json`.

### Task 2: Validation
- [ ] Add `scripts/validate_story_archive.py` that checks JSON parsing, unique IDs, allowed cast classes, dialogue participant references, scene cast references and manifest paths.
- [ ] Add the validator to `.github/workflows/quality-checks.yml`.

### Task 3: Public Story framing
- [ ] Modify `tim-dooley/story/index.html` so the top framing emphasizes one continuous story rather than explanatory chapter modules.
- [ ] Make evidence/source notes collapsible and subordinate.
- [ ] Keep existing URLs and anchors stable.

### Task 4: Verify
- [ ] Open a pull request to `main`.
- [ ] Run repository quality checks through CI.
- [ ] Review the diff for unrelated changes.
- [ ] Merge only after checks pass.