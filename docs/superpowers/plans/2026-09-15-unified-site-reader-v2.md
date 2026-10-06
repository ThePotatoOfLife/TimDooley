# Unified Site Reader V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make TTS explicit, reliable, and seamless across the project's real reading surfaces while keeping maps, catalogs, filters, navigation and other operational UI quiet.

**Architecture:** Keep `tts-reader.js` as the speech engine and `tts-drawer.js` as the single player UI. Use `longform-tts-adapter.js` for declarative reading surfaces, keep Bible specialized through `bible-tts-adapter.js`, and use a generated-artifact projection only for legacy source pages that are unsafe to rewrite directly.

**Tech Stack:** Static HTML/CSS/JavaScript, Web Speech API, CSS Custom Highlight API, Node contract tests, Python repository validators, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-15-unified-site-reader-v2-design.md`

## Global Constraints

- No autoplay.
- `Hear the full story` remains a content disclosure only and must never start speech.
- One player instance per readable page.
- Voice, speed and volume share the existing site-wide settings key.
- Maps, catalogs, filters and navigation remain silent unless they expose a meaningful readable object.
- Bible keeps a contextual adapter rather than becoming a whole-DOM reader.
- Actual-page highlighting must not rewrite or wrap article text.
- Legacy source strata stay byte-stable when a generated-artifact projection can safely supply the capability.
- All changes stay on `feat/unified-site-reader-v2` until exact-head verification is green.

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

### Task 5: Establish the first full repository verification gate

- [x] Run focused TTS contracts.
- [x] Run JavaScript syntax checks through repository CI.
- [x] Run reader/Bible/stability validators through repository CI.
- [x] Run full public-site build and Bible parity checks.
- [x] Confirm the full repository quality suite is green.

---

### Task 6: Add explicit Read Selection interaction

**Files:** `app/tts-drawer.js`, `app/longform-tts-adapter.js`, `app/bible-tts-adapter.js`, `app/tts-drawer.css`, TTS contracts.

**Interfaces:**
- `PotatoTTSDrawer.mountSelectionAction({ container, drawer, getPayload })`.
- Selection action refreshes payload and calls `drawer.playSection('selection')` only after a user click.
- Bible exposes `selection` only when selected text belongs to the active relation.

- [x] Write and verify the failing selection contract.
- [x] Implement the transient `🔊 Read selection` action.
- [x] Preserve selection on pointer interaction and hide on invalid/outside state.
- [x] Wire long-form and Bible adapters.
- [x] Style the selection action with viewport-safe positioning and focus treatment.
- [x] Verify through the focused contracts and repository gate.

---

### Task 7: Keep reading context visible

**Files:** `app/tts-drawer.js`, `app/longform-tts-adapter.js`, `app/bible-tts-adapter.js`, `app/tts-drawer.css`, TTS contracts.

**Interfaces:** Drawer forwards speech events with `sectionId`; adapters consume those events to mark current readable context.

- [x] Write and verify event/state contracts.
- [x] Forward speech events through `options.onEvent`.
- [x] Add/remove `.ptts-reading-active` for spoken sections/relations.
- [x] Keep the primary player sticky while scrolling.
- [x] Clear active state on completion, stop, error and context changes.
- [x] Verify through the repository gate.

---

### Task 8: Highlight the actual spoken word in page text

**Files:** `app/tts-drawer.js`, `app/longform-tts-adapter.js`, `app/bible-tts-adapter.js`, `app/tts-drawer.css`, TTS contracts.

**Interfaces:** Shared non-mutating page highlighter maps normalized speech offsets back to DOM text ranges and renders them through the CSS Custom Highlight API.

- [x] Add normalized speech-text → DOM text-node mapping.
- [x] Add a shared `createPageHighlighter(...)` primitive.
- [x] Map long-form `current` and `all` scopes back to their actual page regions.
- [x] Map Bible Project / Scripture / Why / Both boundaries back to printed regions.
- [x] Leave synthetic spoken labels unhighlighted rather than fabricating DOM targets.
- [x] Add the shared highlight styling and clear it on terminal/context events.
- [x] Verify without rewriting or wrapping article markup.

---

### Task 9: Roll the shared reader across mature prose surfaces

**Files:** reader pages and `scripts/test_longform_tts_adapter.mjs`.

- [x] Story: Whole story / Current entry / Selection + per-entry Listen.
- [x] Philosophy: Whole journey / Current movement / Selection + per-movement Listen.
- [x] Religion: Whole page / Current section / Selection + contextual Listen.
- [x] Tim overview: Whole overview / Current section / Selection + contextual Listen.
- [x] North: Whole North reader / Current section / Selection + per-section Listen.
- [x] Culture: Whole culture reader / Selection only; no card-level button clutter.
- [x] Keep World Systems quiet because it is an index/gateway rather than a continuous reader.
- [x] Keep Great Book quiet while its public route remains a restoration notice rather than the validated chapter reader.

---

### Task 10: Make TTS a first-class repository contract

**Files:** `scripts/validate_reader_surfaces.py`, TTS Node contracts.

- [x] Execute all three TTS Node contracts from the required reader-surface validator.
- [x] Catch and repair brittle contract assertions discovered by the new gate.
- [x] Verify the TTS behavioral suite inside normal repository CI.

---

### Task 11: Integrate the legacy Shadow/Farm deep reader without rewriting source

**Files:** `scripts/patch_public_navigation.py`, `scripts/test_longform_tts_adapter.mjs`, `scripts/site_shell_contract.py`.

**Architecture:** `shadow-farm/index.html` remains legacy source. The public post-build projection injects one whole-reader + selection TTS host into `_site/shadow-farm/index.html` after source copying.

- [x] Write a failing pure projection contract and verify RED.
- [x] Move ownership to the existing public generated-artifact projection pass rather than creating a second build path.
- [x] Add an idempotent `inject_legacy_tts_reader(...)` helper.
- [x] Register only `shadow-farm/index.html` for the legacy projection.
- [x] Keep the legacy source page untouched.
- [x] Add shared CSS and engine → drawer → adapter dependency order.
- [x] Keep Shadow/Farm to Whole deep reader / Selection; no `data-tts-item` UI confetti.
- [x] Add a built-site shell assertion for the generated Shadow/Farm reader.

---

### Task 12: Merge-readiness verification

- [ ] Confirm all three TTS contracts pass on the exact final head.
- [ ] Confirm the full Repository quality checks pass on the exact final head.
- [ ] Confirm built Shadow/Farm projection passes the site-shell contract.
- [ ] Confirm PR #162 is current with `main` and mergeable.
- [ ] Review final changed-file scope and PR description.
- [ ] Do not merge until the user explicitly approves go-live / merge.
