# Story Refinery / All Stories Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture every recoverable story candidate, distinguish tellable episodes from stubs, deepen published entries with an inline full-story layer, and steadily expand the chronological Story without inventing connective tissue.

**Architecture:** Keep `tim-dooley/story/` as one chronological reader. Add an exhaustive backend reservoir under `knowledge/story/`, preserve `story-content/` as the public story fragments, and add an optional inline `details.full-story` narrative layer inside entries. Recovery records remain source-aware; only complete episodes graduate to MAIN/SIDE Story.

**Tech Stack:** Static HTML/CSS/JavaScript, Markdown/JSON knowledge files, existing GitHub Pages structure.

**Spec:** `docs/superpowers/specs/2026-09-14-story-refinery-all-stories-design.md`

## Global Constraints
- Public labels remain only `MAIN STORY` and `SIDE STORY`.
- Do not manufacture dialogue, chronology, motives or reactions.
- Keep biography, public evidence, recovered conversation, memory, Great Book literature and assistant-created literature distinct.
- A concept is not a Story unless an episode can be narrated.
- The Story reader remains one chronological river.
- Full narratives expand inline; detailed provenance stays quiet underneath.

---

### Task 1: Create the exhaustive story reservoir

**Files:**
- Create: `knowledge/story/ALL-STORY-RESERVOIR.md`

**Interfaces:**
- Consumes: `knowledge/story/DIARY-STORY-LEDGER.md`, `knowledge/indexes/story-recovery-priorities.json`, conversation archaeology records, Great Book chapter manifests, recent conversation recovery.
- Produces: one durable list of published, ready, partial and stub story candidates.

- [ ] **Step 1:** Seed the reservoir with the current 104 diary-ledger entries.
- [ ] **Step 2:** Add the 100 recovered candidates numbered 105–204 from the September 14 recovery pass.
- [ ] **Step 3:** Add newly recovered early-biography and Great Book episode candidates discovered after that pass.
- [ ] **Step 4:** Mark each candidate with readiness and source class rather than publishing all candidates automatically.
- [ ] **Step 5:** Commit the reservoir separately.

### Task 2: Restore the first pre-2020 complete-story wave

**Files:**
- Create: `story-content/pre-2020-restored.html`
- Modify: `tim-dooley/story/index.html`

**Interfaces:**
- Consumes: early biography/timeline records and story publication gate.
- Produces: chronologically sortable `.story-entry` elements with stable IDs and full-story layers.

- [ ] **Step 1:** Draft only episodes with enough sequence to tell honestly.
- [ ] **Step 2:** Give each entry a date/year, MAIN/SIDE classification, compact Story layer and `details.full-story` narrative.
- [ ] **Step 3:** Add quiet provenance notes identifying autobiography/project testimony/literary source status.
- [ ] **Step 4:** Add the new fragment to the reader file list.
- [ ] **Step 5:** Verify the stream still sorts correctly by `time[datetime]` and existing entries remain present.
- [ ] **Step 6:** Commit the pre-2020 wave separately.

### Task 3: Add inline full-story reader support

**Files:**
- Modify: `tim-dooley/story/index.html`

**Interfaces:**
- Consumes: optional `details.full-story` blocks inside story fragments.
- Produces: readable expandable second narrative layer without requiring separate pages.

- [ ] **Step 1:** Add restrained styles for `.full-story`, summary text and open state.
- [ ] **Step 2:** Ensure entries without a full-story block still render exactly as before.
- [ ] **Step 3:** Keep source notes visually quieter than the full narrative.
- [ ] **Step 4:** Verify mobile and desktop HTML remains valid and readable.
- [ ] **Step 5:** Commit the reader-depth support separately.

### Task 4: Audit the existing 104 manuscript stories for narrative depth

**Files:**
- Modify: `knowledge/story/ALL-STORY-RESERVOIR.md`
- Modify individual `story-content/*.html` only when a source-backed full episode is recoverable.

**Interfaces:**
- Consumes: all current Story entries plus their source owners.
- Produces: per-entry readiness state: `published-deep`, `published-shallow`, `partial`, or `stub`.

- [ ] **Step 1:** Walk every current Story entry.
- [ ] **Step 2:** Mark explanation-only entries as `published-shallow` rather than pretending they are complete.
- [ ] **Step 3:** Recover full narrative for entries where source material is already sufficient.
- [ ] **Step 4:** Move unresolved missing details into explicit recovery notes.
- [ ] **Step 5:** Commit each coherent restoration wave rather than one giant rewrite.

### Task 5: Mine old and recent conversations systematically

**Files:**
- Modify: `knowledge/story/ALL-STORY-RESERVOIR.md`
- Modify: `knowledge/indexes/story-recovery-priorities.json` when a genuinely new high-value recovery target appears.

**Interfaces:**
- Consumes: conversation archaeology waves, memory recovery, recent GitHub-building conversations and public-post records.
- Produces: additional story candidates with dates/windows and source classification.

- [ ] **Step 1:** Revisit all conversation-archaeology waves, not only the latest Story-specific records.
- [ ] **Step 2:** Mine recent September repository-building sessions as life/project stories where they contain actual sequences and decisions.
- [ ] **Step 3:** Reject concept-only fragments from the Story reservoir unless they are tied to a concrete episode.
- [ ] **Step 4:** Promote complete episodes into later Story waves.
- [ ] **Step 5:** Keep unresolved candidate wording as stubs rather than synthesized prose.

### Task 6: Mine Great Book narrative chapters as literary side stories

**Files:**
- Modify: `knowledge/story/ALL-STORY-RESERVOIR.md`
- Create later `story-content/gb-*.html` fragments only for complete literary episodes.

**Interfaces:**
- Consumes: 167 Great Book body chapters.
- Produces: literary-story candidates clearly separated from documentary biography.

- [ ] **Step 1:** Identify chapters that actually narrate scenes rather than teach concepts.
- [ ] **Step 2:** Preserve authored dialogue as Great Book dialogue, not documentary transcript.
- [ ] **Step 3:** Add complete literary stories to the reservoir with `GREAT_BOOK_LITERARY` source class.
- [ ] **Step 4:** Publish the strongest complete episodes as SIDE STORY entries where they enrich the chronological 2024 creative-life layer.

### Task 7: Verification

**Files:**
- Verify all changed Story/knowledge files.

- [ ] **Step 1:** Fetch the branch versions of changed files and confirm expected content exists.
- [ ] **Step 2:** Check every new `.story-entry` has a unique id, `data-story-type`, and a sortable `time datetime`.
- [ ] **Step 3:** Confirm no complete source-sensitive allegation is rewritten as independent fact.
- [ ] **Step 4:** Confirm the reader references every new story fragment exactly once.
- [ ] **Step 5:** Compare branch against `main` before integration and report the exact commits/files changed.
