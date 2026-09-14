# Story Diary Stream Wave 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current 13-section explanatory Story surface with a diary-like chronological stream of many rich Main Story / Side Story episodes, while preserving source hygiene underneath the prose.

**Architecture:** A single canonical story-stream data file owns episode order and the only public classification (`main` or `side`). The public Story page renders one continuous scroll with subtle date/title/meta typography and no cards. Episode prose may remain raw, long, dialogic, repetitive or unresolved; validation protects structure and provenance, not literary polish.

**Tech Stack:** JSON, static HTML/CSS/JavaScript, Python validation, existing GitHub Pages build/quality checks.

**Spec:** `knowledge/story/AUTHORING-GUIDE.md` plus the user-approved diary-stream requirements from 2026-09-14.

## Global Constraints
- Public story classification is only `main` or `side`.
- Story count is open-ended; do not target an arbitrary fixed total.
- All episodes appear in one chronological scroll.
- Date and title are visually subtle; prose is the dominant element.
- Rich/long stories are preferred when the material supports them.
- Rawness, uneven length, profanity, spelling, repetition and unresolved endings are allowed.
- Validation checks structure, chronology, IDs, references and quote/source status; it must not score prose quality.
- Never invent missing dialogue or physical scene details.
- Serious allegations remain attributed to Tim/project sources unless independently established.

### Task 1: Canonical story-stream schema and first large population
- [ ] Create `knowledge/story/story-stream.json`.
- [ ] Populate a broad first wave from material already in the repository.
- [ ] Modify `knowledge/story/AUTHORING-GUIDE.md` with diary/rawness rules.

### Task 2: Story-stream validator
- [ ] Add tests for invalid type, duplicate ID and reversed chronology.
- [ ] Update `scripts/validate_story_archive.py` to validate the stream without literary-quality scoring.

### Task 3: Diary-style public reader
- [ ] Create `app/story-stream.js`.
- [ ] Modify `tim-dooley/story/index.html` into a continuous stream with subtle date/title/type markers and collapsed source notes.

### Task 4: Verification and integration
- [ ] Run Story tests.
- [ ] Run repository quality checks.
- [ ] Open focused PR and merge only after fresh CI succeeds.
