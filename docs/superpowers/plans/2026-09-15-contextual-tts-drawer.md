# Contextual TTS Drawer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable three-state text-to-speech drawer and prove it inside the Bible comparator.

**Architecture:** Keep `app/tts-reader.js` as the speech core. Add a reusable drawer module and stylesheet, then a Bible-specific adapter that converts the active comparison into structured reading scopes. The standalone `/tools/tts/` page remains unchanged as the full reader.

**Tech Stack:** Vanilla HTML/CSS/JavaScript, Web Speech API, Node.js contract tests.

**Spec:** `docs/superpowers/specs/2026-09-15-contextual-tts-drawer-design.md`

## Global Constraints

- Work only on `feat/tts-tool-v6`; do not modify `main` directly.
- Preserve the focused Bible comparator interaction model.
- Embedded TTS must not add a second full editor.
- Active relation changes stop stale playback and refresh the drawer payload.
- Exact word highlighting uses Web Speech boundary events only; do not fake timing.

---

### Task 1: Reusable drawer contract

**Files:**
- Create: `app/tts-drawer.js`
- Create: `app/tts-drawer.css`
- Test: `scripts/test_tts_drawer.mjs`

**Interfaces:**
- Consumes: `PotatoTTS.TTSEngine`, `PotatoTTS.chooseVoice`, `PotatoTTS.voiceIdentity`.
- Produces: `PotatoTTSDrawer.mount()`, `normalizePayload()`, `resolveSection()`, `buildReadingText()`, `renderFocusedText()`.

- [x] **Step 1: Write the failing contract test** for payload normalization, scope resolution, `mount`, and focus slicing.
- [x] **Step 2: Run the test and confirm it fails because the module is absent.**
- [x] **Step 3: Implement the minimal reusable drawer.**
- [x] **Step 4: Run the contract test and confirm it passes.**

### Task 2: Bible adapter

**Files:**
- Create: `app/bible-tts-adapter.js`
- Test: `scripts/test_bible_tts_adapter.mjs`

**Interfaces:**
- Consumes: rendered `.relation` markup inside `#active-relation`.
- Produces: `buildBiblePayload()`, `extractRelation()`, `mount()`.

- [x] **Step 1: Write the failing reading-order test** for Both / Project / Scripture / Why.
- [x] **Step 2: Run the test and confirm it fails because the adapter is absent.**
- [x] **Step 3: Implement payload extraction and MutationObserver refresh.**
- [x] **Step 4: Run both contract tests and confirm they pass.**

### Task 3: Comparator integration

**Files:**
- Modify: `traditions/bible/index.html`
- Modify: `scripts/validate_bible_reader.py`

**Interfaces:**
- Loads: `app/tts-reader.js`, `app/tts-drawer.js`, `app/bible-tts-adapter.js`, `app/tts-drawer.css`.

- [ ] **Step 1: Add failing validator markers** for the drawer assets.
- [ ] **Step 2: Run the validator and confirm the new markers fail.**
- [ ] **Step 3: Load the drawer CSS and scripts from the Bible comparator.**
- [ ] **Step 4: Run validator and Node contract tests.**

### Task 4: Branch verification

- [ ] **Step 1: Compare `main...feat/tts-tool-v6` and review the exact changed-file set.**
- [ ] **Step 2: Run or inspect repository checks for the branch head.**
- [ ] **Step 3: Update PR #157 description to include the embedded Bible reader.**
