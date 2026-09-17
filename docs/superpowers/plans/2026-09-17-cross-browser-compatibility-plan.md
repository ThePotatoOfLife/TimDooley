# Cross-Browser Compatibility Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the public site’s modern cross-browser/mobile robustness without otherwise changing its appearance, content, routes, or intended interactions.

**Architecture:** Preserve the static site architecture. Add narrowly-scoped progressive-enhancement fallbacks in shared CSS and the few browser-API call sites that can fail, then add CI-only Chromium/Firefox/WebKit smoke coverage. No production framework or runtime dependency is introduced.

**Tech Stack:** Static HTML/CSS/JavaScript, Python build/validation scripts, Node source-contract tests, GitHub Actions, Playwright used only in CI/tests.

**Spec:** `docs/superpowers/specs/2026-09-17-cross-browser-compatibility-design.md`

## Global Constraints

- No redesign, copy/content rewrite, route change, information-architecture change, or aesthetic restyling.
- Preserve current desktop appearance and intended interactions where they already work.
- First-class targets: current Chromium family, Firefox, Safari/WebKit, Windows/macOS, iPhone/iPad, Android, phone/tablet portrait and landscape.
- Legacy browsers such as Internet Explorer are out of scope.
- Optional modern APIs must fail safely; core content, links, navigation, scrolling, and reading remain usable.
- Preserve all TTS behavior/fixes from PRs #233, #236, #238, #239, #241, and #243.
- Browser automation is test/CI-only and must not alter the production runtime bundle.

---

### Task 1: Compatibility contract tests

**Files:**
- Create: `scripts/test_browser_compat_contract.mjs`
- Modify: `.github/workflows/quality-checks.yml`

**Interfaces:**
- Consumes: existing public CSS/JS source files.
- Produces: a CI gate that asserts required compatibility fallbacks remain present.

- [ ] **Step 1: Write the failing source-contract test**

The test must assert, at minimum: shared site CSS has overflow/media-safe defaults and safe-area/viewport fallbacks; Great Book does not unconditionally require `IntersectionObserver`; clipboard call sites are guarded; TTS keeps DOM-highlight fallback behavior; standalone TTS does not depend on `color-mix()` as its only usable styling; and mobile fixed controls have viewport-safe bounds.

- [ ] **Step 2: Add the test to repository quality CI**

Run `node scripts/test_browser_compat_contract.mjs` in `.github/workflows/quality-checks.yml`.

- [ ] **Step 3: Verify RED in GitHub Actions**

Expected: the new compatibility test fails on at least one known missing fallback while existing checks continue to execute normally.

---

### Task 2: Shared CSS/mobile compatibility foundation

**Files:**
- Modify: `app/site-system.css`
- Modify: `app/style.css`
- Modify: `app/longform-reader.css`
- Modify: `app/tts-drawer.css`
- Modify: `minimal.css`
- Modify: `great-book/great-book.css` only if a surface-specific mobile fix is required

**Interfaces:**
- Consumes: existing CSS variables and layout classes.
- Produces: fallback-first layout behavior with no intentional visual redesign.

- [ ] **Step 1: Keep the source-contract test failing for the CSS gaps**
- [ ] **Step 2: Add minimal compatibility declarations**

Implement only compatibility-safe rules: `overflow-wrap:anywhere` for long unbroken content where needed; media max sizing; overflow containment for wide tables/code; `min-width:0` for grid/flex children; `100vh` fallback followed by `100dvh`/`100svh` where relevant; safe-area padding for viewport-edge controls; pointer-coarse minimum target sizing only where controls are otherwise difficult to tap; fallback backgrounds before advanced visual effects; and no dependency on `:has()`, blur, or `color-mix()` for core usability.

- [ ] **Step 3: Verify the compatibility test turns green for CSS assertions**
- [ ] **Step 4: Run existing CSS/site shell checks**

---

### Task 3: Great Book and longform browser-API fallbacks

**Files:**
- Modify: `app/great-book-reader.js`
- Modify: `app/great-book-loader.js` only if required
- Test: `scripts/test_browser_compat_contract.mjs`
- Test: existing Great Book/TTS tests

**Interfaces:**
- Consumes: existing `loadSlot`, current-chapter publication, and TTS preparation contracts.
- Produces: eager/scroll-safe behavior when `IntersectionObserver` is missing without changing normal observed behavior.

- [ ] **Step 1: Add/confirm failing test for missing `IntersectionObserver` fallback**
- [ ] **Step 2: Implement minimal feature detection**

If `IntersectionObserver` is unavailable, eagerly load the currently required slots (or all chapter slots if necessary for correctness), preserve current chapter publication in a deterministic fallback, and do not throw.

- [ ] **Step 3: Run Great Book/TTS regression tests**

---

### Task 4: Clipboard and TTS progressive enhancement

**Files:**
- Modify: `app/timeline.js`
- Modify: `tools/tts/index.html`
- Modify: `app/tts-reader.js` / `app/tts-drawer.js` only if an actual unsupported-API crash is identified
- Test: `scripts/test_browser_compat_contract.mjs`
- Test: existing TTS regression suite

**Interfaces:**
- Produces: no-throw copy behavior and no regression to TTS follow/highlight semantics.

- [ ] **Step 1: Add/confirm failing tests for clipboard and optional speech/highlight APIs**
- [ ] **Step 2: Guard clipboard calls**

Use `navigator.clipboard?.writeText` only when available; otherwise preserve the already-visible URL/text and avoid throwing. Do not add new UI copy unless necessary.

- [ ] **Step 3: Preserve TTS DOM/range fallback and unsupported-speech handling**
- [ ] **Step 4: Run the full existing TTS suite**

---

### Task 5: Special-surface compatibility audit

**Files:**
- Modify only public World Map/runtime files that have an identified compatibility failure.
- Modify only public timeline/minimal layout files that have an identified viewport failure.
- Test: `scripts/test_browser_compat_contract.mjs`

**Interfaces:**
- Produces: stable fallback/no-throw states without changing map data, political boundaries, layer semantics, or visual design.

- [ ] **Step 1: Test for required capability guards**
- [ ] **Step 2: Add minimal guards/fallbacks where tests expose a gap**
- [ ] **Step 3: Run existing World Map validation suite relevant to changed files**

---

### Task 6: Real browser smoke matrix

**Files:**
- Create: `tests/browser/compat.spec.mjs`
- Create: `playwright.compat.config.mjs`
- Create or modify: `.github/workflows/browser-compat.yml`

**Interfaces:**
- Consumes: built `_site` artifact served by a local HTTP server.
- Produces: CI-only Chromium, Firefox, and WebKit smoke coverage at desktop, phone, and tablet viewport profiles.

- [ ] **Step 1: Add browser smoke tests**

Cover homepage, Great Book, standalone TTS, representative longform page, timeline, and World Map shell. Assert no uncaught page errors, core content visible, primary controls reachable, and no whole-document horizontal overflow on standard content pages. Mock speech synthesis only for deterministic TTS UI-state checks.

- [ ] **Step 2: Configure Chromium/Firefox/WebKit projects and representative desktop/mobile viewports**
- [ ] **Step 3: Add CI workflow that builds `_site`, starts a local server, installs Playwright browsers, and runs the compatibility spec**
- [ ] **Step 4: Verify all projects green**

---

### Task 7: Final regression and no-redesign review

**Files:**
- No new production scope unless a verification failure requires a fix.

**Interfaces:**
- Produces: merge-ready branch with compatibility-only diff.

- [ ] **Step 1: Run the complete compatibility contract and browser matrix**
- [ ] **Step 2: Run existing TTS, Great Book, site shell, and relevant World Map checks**
- [ ] **Step 3: Compare branch to `main` and inspect every changed production file**

Reject unrelated content, copy, visual, route, data, or architecture changes.

- [ ] **Step 4: Verify branch is up to date with `main`**
- [ ] **Step 5: Create/update PR with exact compatibility scope and test evidence**
- [ ] **Step 6: Merge only when required checks are green**
