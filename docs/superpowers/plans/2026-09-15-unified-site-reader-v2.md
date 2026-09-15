# Unified Site Reader V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make TTS explicit, reliable, and seamless across Bible, Story, Philosophy, Religion, and Tim overview using one shared player and contextual Listen controls.

**Architecture:** Keep `tts-reader.js` as the speech engine and `tts-drawer.js` as the single player UI. Repair `longform-tts-adapter.js` to use the drawer's current `{target,getPayload}` / `setPayload` contract, add idempotent section-level Listen buttons, add explicit selection reading, and keep Bible specialized.

**Tech Stack:** Static HTML/CSS/JavaScript, Web Speech API, Node contract tests, Python repository validators, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-15-unified-site-reader-v2-design.md`

## Global Constraints

- No autoplay.
- `Hear the full story` remains a content disclosure only and must never start speech.
- One player instance per readable page.
- Voice, speed and volume share the existing site-wide settings key.
- Maps, catalogs, filters and navigation remain silent.
- Bible keeps a contextual adapter rather than becoming a whole-DOM reader.
- All changes stay on `feat/unified-site-reader-v2` until verification is green.

---

### Task 1: Lock the current drawer API into the long-form contract

**Files:** `scripts/test_longform_tts_adapter.mjs`, `app/longform-tts-adapter.js`

**Interfaces:** Consumes `PotatoTTSDrawer.mount({ target, getPayload, settingsKey })`; produces long-form mount logic that calls `drawer.setPayload(payload)` and never references obsolete `mount/source/updatePayload` names.

- [x] Write the regression contract for `target/getPayload/setPayload`.
- [x] Repair the adapter and use the shared `potato-tts-settings` key.
- [x] Verify the focused contract.

---

### Task 2: Add explicit section-level Listen actions

**Files:** `scripts/test_longform_tts_adapter.mjs`, `app/longform-tts-adapter.js`, `app/tts-drawer.js`, `app/tts-drawer.css`

**Interfaces:** Produces `drawer.playSection(sectionId)` and one idempotent `button.ptts-inline-listen[data-tts-listen]` per readable item.

- [x] Add `playSection(sectionId)` to the player API.
- [x] Add idempotent inline Listen buttons.
- [x] Keep TTS controls out of spoken text.
- [x] Style contextual Listen controls and focus states.

---

### Task 3: Protect Story disclosure semantics and async story buttons

**Files:** `scripts/test_longform_tts_adapter.mjs`, `tim-dooley/story/index.html`

- [x] Guard `.story-entry` as the TTS unit.
- [x] Guard `Hear the full story` / `summary` from speech actions.
- [x] Ensure MutationObserver adds Listen controls to async story entries without duplicates.

---

### Task 4: Improve page-level TTS discoverability

**Files:** `app/tts-drawer.css`, `app/bible-tts-adapter.js`, long-form reader pages and contracts.

- [x] Strengthen the page-level trigger and focus state.
- [x] Mark the shared player host as the primary reader surface.
- [x] Add a contextual Listen action to the active Bible comparison.
- [x] Keep Bible on the specialized payload model.

---

### Task 5: Verify reader surfaces and repository build

- [x] Run focused TTS contracts.
- [x] Run JavaScript syntax checks through repository CI.
- [x] Run reader/Bible/stability validators through repository CI.
- [x] Run full public-site build and Bible parity checks.
- [x] Confirm the full repository quality suite is green.

---

### Task 6: Add explicit Read Selection interaction

**Files:**
- Modify: `app/tts-drawer.js`
- Modify: `app/longform-tts-adapter.js`
- Modify: `app/bible-tts-adapter.js`
- Modify: `app/tts-drawer.css`
- Modify: `scripts/test_tts_drawer.mjs`
- Modify: `scripts/test_longform_tts_adapter.mjs`
- Modify: `scripts/test_bible_tts_adapter.mjs`

**Interfaces:**
- Produces: `PotatoTTSDrawer.mountSelectionAction({ container, drawer, getPayload })`.
- Selection action calls `drawer.setPayload(getPayload())` then `drawer.playSection('selection')` only after a user click.
- Bible payload exposes `selection` only when selected text belongs to the active relation.

- [ ] **Step 1: Write the failing selection contract**

Require a shared selection-action helper, `.ptts-selection-listen`, and `playSection('selection')`. Require Bible payload/source to expose a selection scope when active-relation text is selected.

- [ ] **Step 2: Verify RED**

Run:
```bash
node scripts/test_tts_drawer.mjs
node scripts/test_longform_tts_adapter.mjs
node scripts/test_bible_tts_adapter.mjs
```
Expected: FAIL because the selection action does not exist yet.

- [ ] **Step 3: Implement the shared selection action**

Create a transient fixed-position button near `Selection.getRangeAt(0).getBoundingClientRect()`. On `pointerdown`, prevent default so the browser selection remains intact. On click, refresh the payload and call `drawer.playSection('selection')`. Hide the button when selection is empty/outside the configured container, on scroll, or on Escape.

- [ ] **Step 4: Wire long-form and Bible adapters**

Long-form already emits a `selection` payload section; mount the shared action against the configured readable root. Extend Bible's contextual source to append `{id:'selection',label:'Selection',text:selectedText}` only for selection inside `#active-relation`.

- [ ] **Step 5: Style selection action**

Add a small elevated pill with clear hover/focus states and safe viewport clamping.

- [ ] **Step 6: Verify GREEN and commit**

Run the three focused contracts. Commit message: `feat: add explicit read-selection actions`.

---

### Task 7: Keep the active reader visible and mark the spoken section

**Files:**
- Modify: `app/tts-drawer.js`
- Modify: `app/longform-tts-adapter.js`
- Modify: `app/tts-drawer.css`
- Modify: `scripts/test_tts_drawer.mjs`
- Modify: `scripts/test_longform_tts_adapter.mjs`

**Interfaces:**
- Drawer accepts optional `onEvent(event)` and includes `sectionId` in forwarded speech events.
- Long-form adapter applies `.ptts-reading-active` only while `sectionId==='current'` is speaking.

- [ ] **Step 1: Write failing event/state contracts**

Require the drawer source to call an optional event hook and require the long-form adapter to add/remove `.ptts-reading-active` on start/complete/stop/error.

- [ ] **Step 2: Verify RED**

Run focused drawer + long-form tests.

- [ ] **Step 3: Forward speech events**

After internal drawer event handling, call `options.onEvent?.({...event,sectionId})`.

- [ ] **Step 4: Add active-reading state**

When a `current` section starts/chunks/boundaries, add `.ptts-reading-active` to the selected item. Remove it on complete/stop/error or when another item is chosen.

- [ ] **Step 5: Make primary player sticky while scrolling**

Use `[data-tts-primary]` as the stable hook. Keep the collapsed trigger compact, and make the primary host sticky near the viewport top while scrolling without covering page content.

- [ ] **Step 6: Verify GREEN and commit**

Run focused contracts. Commit message: `feat: keep reading context visible during speech`.

---

### Task 8: Final verification

- [ ] Run all three focused TTS contracts.
- [ ] Confirm PR changed files stay inside shared TTS code/tests/docs and intended adapters.
- [ ] Run the full Repository quality checks on the exact final head.
- [ ] Do not merge until the exact final head is green.
