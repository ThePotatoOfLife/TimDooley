# Unified Site Reader V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make TTS explicit, reliable, and seamless across Bible, Story, Philosophy, Religion, and Tim overview using one shared player and contextual Listen controls.

**Architecture:** Keep `tts-reader.js` as the speech engine and `tts-drawer.js` as the single player UI. Repair `longform-tts-adapter.js` to use the drawer's current `{target,getPayload}` / `setPayload` contract, then add idempotent section-level Listen buttons that point the shared player at the selected story/section. Bible remains specialized.

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

**Files:**
- Modify: `scripts/test_longform_tts_adapter.mjs`
- Modify: `app/longform-tts-adapter.js`

**Interfaces:**
- Consumes: `PotatoTTSDrawer.mount({ target, getPayload, settingsKey })`
- Produces: long-form mount logic that calls `drawer.setPayload(payload)` and never references obsolete `mount/source/updatePayload` names.

- [ ] **Step 1: Extend the failing test**

Add a fake drawer whose `mount()` asserts `options.target` and `options.getPayload`, returns `{setPayload,open,startSection}`, and records calls. Assert that `adapter.mount()` uses this contract and that `refresh()` calls `setPayload`.

- [ ] **Step 2: Run the contract test and verify RED**

Run: `node scripts/test_longform_tts_adapter.mjs`
Expected: FAIL because the adapter currently passes `mount/source` and calls `updatePayload`.

- [ ] **Step 3: Repair the adapter**

Change the drawer call to:

```js
drawer=Drawer.mount({
  target:host,
  getPayload:source,
  settingsKey:config.settingsKey||'potato-tts-settings',
});
```

Replace all `drawer.updatePayload(...)` calls with:

```js
drawer.setPayload(source());
```

and return `refresh:()=>drawer.setPayload(source())`.

- [ ] **Step 4: Run the test and verify GREEN**

Run: `node scripts/test_longform_tts_adapter.mjs`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `fix: align longform TTS with shared drawer API`

---

### Task 2: Add explicit section-level Listen actions

**Files:**
- Modify: `scripts/test_longform_tts_adapter.mjs`
- Modify: `app/longform-tts-adapter.js`
- Modify: `app/tts-drawer.js`
- Modify: `app/tts-drawer.css`

**Interfaces:**
- Produces: `drawer.playSection(sectionId)` on the player API.
- Produces: `button.ptts-inline-listen[data-tts-listen]` injected once per configured readable item.

- [ ] **Step 1: Write failing tests**

Assert the drawer return object exposes `playSection`. Assert the long-form adapter injects one Listen button per item and repeated refresh/mutation does not duplicate it. Assert clicking the button calls `chooseCurrent(item)` and `drawer.playSection('current')`.

- [ ] **Step 2: Run tests and verify RED**

Run:
`node scripts/test_tts_drawer.mjs && node scripts/test_longform_tts_adapter.mjs`
Expected: FAIL because `playSection` and inline Listen controls do not exist.

- [ ] **Step 3: Add `playSection` to drawer**

Implement a method that sets `sectionId` when the requested section exists, updates the scope select and active text, opens the drawer, then invokes the existing `start()` function. Return it from the drawer API.

- [ ] **Step 4: Add idempotent inline buttons**

In the long-form adapter, create `ensureListenButtons()` that iterates `itemSelector` items, skips items already containing `:scope > .ptts-inline-listen`, and appends:

```html
<button type="button" class="ptts-inline-listen" data-tts-listen>🔊 Listen</button>
```

with `aria-label="Listen to this section"`.

The click handler must call `chooseCurrent(item)` followed by `drawer.playSection('current')`.

Call `ensureListenButtons()` on mount and from the MutationObserver.

- [ ] **Step 5: Style the inline action**

Add subdued pill styling to `app/tts-drawer.css`; it should be visible but secondary to headings. Add a stronger hover/focus-visible state.

- [ ] **Step 6: Run tests and verify GREEN**

Run:
`node scripts/test_tts_drawer.mjs && node scripts/test_longform_tts_adapter.mjs`
Expected: PASS.

- [ ] **Step 7: Commit**

Commit message: `feat: add contextual Listen controls to readable sections`

---

### Task 3: Protect Story disclosure semantics and async story buttons

**Files:**
- Modify: `scripts/test_longform_tts_adapter.mjs`
- Verify: `tim-dooley/story/index.html`

**Interfaces:**
- Story item selector remains `.story-entry`.
- `details.full-story > summary` remains a disclosure element only.

- [ ] **Step 1: Add failing/guard tests**

Assert Story contains `data-tts-item=".story-entry"`. Assert no `summary` or `full-story` selector is registered as a TTS action and no script binds `Hear the full story` to speech. Assert async mutations trigger Listen button injection through adapter behavior tests.

- [ ] **Step 2: Run test**

Run: `node scripts/test_longform_tts_adapter.mjs`
Expected: PASS once Task 2 behavior exists; FAIL if Story disclosure semantics are accidentally wired to TTS.

- [ ] **Step 3: Commit guard if test file changed**

Commit message: `test: protect Story disclosure from autoplay speech`

---

### Task 4: Improve page-level TTS discoverability

**Files:**
- Modify: `app/tts-drawer.css`
- Modify: `traditions/bible/index.html`
- Modify: `philosophy/index.html`
- Modify: `religion/index.html`
- Modify: `tim-dooley/index.html`
- Modify: `tim-dooley/story/index.html`
- Modify: `scripts/test_bible_tts_adapter.mjs`
- Modify: `scripts/test_longform_tts_adapter.mjs`

**Interfaces:**
- Page-level host remains one per page.
- Bible host remains `#bible-tts-drawer`.

- [ ] **Step 1: Add test expectations**

Require the Bible TTS host to sit adjacent to the active reading surface rather than buried above navigation; require long-form page hosts to carry a common `data-tts-primary` marker.

- [ ] **Step 2: Run tests and verify RED**

Run:
`node scripts/test_bible_tts_adapter.mjs && node scripts/test_longform_tts_adapter.mjs`
Expected: FAIL on new placement/marker requirements.

- [ ] **Step 3: Update markup**

Add `data-tts-primary` to the Story, Philosophy, Religion and Tim hosts. Move the Bible host so it is visually associated with `#active-relation` while keeping navigation functional and dependency order unchanged.

- [ ] **Step 4: Enhance trigger styling**

Make `.ptts-trigger` more discoverable with clearer contrast, `font-weight:650`, larger hit target, and `:focus-visible` outline. Keep unused state compact.

- [ ] **Step 5: Run tests and verify GREEN**

Run the two contract tests again.

- [ ] **Step 6: Commit**

Commit message: `feat: make site reader easier to discover`

---

### Task 5: Verify all reader surfaces and repository build

**Files:**
- Modify if needed: `scripts/check_bible_static_dynamic_parity.py`
- Modify if needed: `scripts/validate_reader_surfaces.py`

**Interfaces:**
- Existing Bible build parity must still require TTS assets.
- Existing reader-surface identities must remain unchanged.

- [ ] **Step 1: Run focused TTS contracts**

Run:
```bash
node scripts/test_tts_drawer.mjs
node scripts/test_bible_tts_adapter.mjs
node scripts/test_longform_tts_adapter.mjs
```
Expected: all PASS.

- [ ] **Step 2: Run JavaScript syntax checks**

Run:
```bash
node --check app/tts-reader.js
node --check app/tts-drawer.js
node --check app/bible-tts-adapter.js
node --check app/longform-tts-adapter.js
```
Expected: all exit 0.

- [ ] **Step 3: Run targeted repository validators**

Run:
```bash
python scripts/validate_bible_reader.py
python scripts/validate_reader_surfaces.py
python scripts/stability_audit.py
```
Expected: all PASS.

- [ ] **Step 4: Open PR and let repository quality checks + Pages build run**

Expected: both workflows green before merge.

- [ ] **Step 5: Final review**

Verify changed files are restricted to TTS/shared reader code, readable page integration, tests, and docs.
