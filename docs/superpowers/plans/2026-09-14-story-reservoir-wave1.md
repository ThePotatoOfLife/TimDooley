# Story Reservoir Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a durable Story-authoring backend and begin shifting the public Story from explanatory capsules toward one continuous chronicle.

**Implemented architecture:** Wave 1 uses focused canonical owners rather than forcing raw conversation-style containers through the repository: `knowledge/story/cast-book.json`, `knowledge/story/arc-season-map.json`, `knowledge/indexes/story-recovery-priorities.json`, the existing `knowledge/indexes/conversation-recovery-inventory.json`, and `knowledge/story/AUTHORING-GUIDE.md`. `scripts/validate_story_archive.py` validates cast/arc integrity now and already understands optional future scene/dialogue/manifest owners if those are safely added later.

**Tech Stack:** Static JSON, HTML/CSS, Python validation, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-14-story-reservoir-design.md`

## Global Constraints
- Do not invent missing dialogue or scene details.
- Preserve source status and period-specific role changes.
- Keep the public reader chronological and readable rather than dashboard-like.
- Keep unresolved material in explicit recovery priorities.
- Treat Great Book literary characters, real people, collective Tim/project labels and created beings as distinct cast classes.

### Task 1: Story backend
- [x] Create `knowledge/story/cast-book.json` with recurring cast classes and period roles.
- [x] Create `knowledge/story/arc-season-map.json` with overlapping arcs rather than rigid eras.
- [x] Create `knowledge/indexes/story-recovery-priorities.json` for unresolved characters, dialogue and scene leads.
- [x] Keep `knowledge/indexes/conversation-recovery-inventory.json` as the current conversation-source ledger.
- [x] Add `knowledge/story/AUTHORING-GUIDE.md` so scene-first storytelling is part of the project workflow.
- [ ] Add richer standalone scene/dialogue owners later only when repository safety and source separation make that appropriate.

### Task 2: Validation
- [x] Add `scripts/validate_story_archive.py` for unique IDs, cast classes and arc references, with optional support for future scene/dialogue/manifest owners.
- [x] Add `scripts/test_story_archive_validator.py` and confirm the contract red→green during implementation.
- [ ] Wire the Story-specific validator directly into global CI later through a small safe integration path; current full repository CI already validates the new files through existing hygiene/content/site checks.

### Task 3: Public Story framing
- [x] Modify `tim-dooley/story/index.html` so the top framing emphasizes one continuous story rather than explanatory chapter modules.
- [x] Turn the old card-grid chapter selector into a quiet chronological re-entry map.
- [x] Make source notes collapsible and subordinate.
- [x] Keep existing URLs and anchors stable.
- [x] Add more lived 2024 texture without inventing documentary scenes from Great Book fiction.

### Task 4: Verify
- [x] Open pull request #130 to `main`.
- [x] Run repository quality checks through CI.
- [x] Confirm all 77 repository checks pass on the implemented Story reader/backend state.
- [ ] Review final diff once more after this documentation cleanup.
- [ ] Integrate only after the latest commit is green.