# Literature Library + Great Book Reader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a durable Literature library and a complete continuous reader for The Great Book of Potato v1.2.0.0, with a linked 171-chapter index, stable chapter URLs, and a download action.

**Architecture:** Add `/literature/` as the collection route and `/literature/great-book/` as a reader shell. The Great Book remains split into ten static HTML parts described by a JSON manifest; client-side JavaScript assembles those parts into one continuous reading surface and builds the chapter index from manifest metadata. A focused repository validator enforces completeness, anchor stability, navigation exposure, and non-invasive reader behavior.

**Tech Stack:** Static HTML/CSS/JavaScript, JSON manifest, Python repository validators, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-13-literature-great-book-reader-design.md`

## Global Constraints

- Public route family is `/literature/`.
- Great Book public route is `/literature/great-book/`.
- Edition string is exactly `v1.2.0.0` in reader-facing presentation and `1.2.0.0` in manifest metadata.
- Manifest contains exactly 171 chapter records and 10 content parts.
- Preserve legacy chapter anchors and Chapter 20 → `chapter-65-5` redirect.
- Reading must not change browser zoom or programmatically focus chapter elements.
- No search engine, account system, pagination mode, or fake page-turn UI in this release.

---

### Task 1: Completeness Validator

**Files:**
- Create: `scripts/validate_literature_reader.py`

**Interfaces:**
- Consumes: `literature/great-book/book-manifest.json`, content parts, reader shell, home/archive HTML.
- Produces: zero exit status only when the complete Literature/Great Book contract is satisfied.

- [ ] **Step 1: Write the validator before the feature files exist**

Implement checks for route files, version, 171 chapters, 10 existing part files, unique manifest anchors, exactly-one occurrence of every chapter anchor across content parts, valid legacy Chapter 20 redirect, download artifact presence, home/archive Literature links, and absence of zoom/focus-changing APIs in `app/great-book-reader.js`.

- [ ] **Step 2: Run validator to verify it fails**

Run: `python scripts/validate_literature_reader.py`
Expected: FAIL because Literature reader files do not yet exist.

- [ ] **Step 3: Commit the failing contract**

Commit message: `test: define Literature reader contract`

### Task 2: Publish Book Data and Reader Shell

**Files:**
- Create: `literature/great-book/book-manifest.json`
- Create: `literature/great-book/parts/part-01.html` through `part-10.html`
- Create: `literature/great-book/index.html`
- Create: `app/great-book-reader.js`
- Create: `app/literature-reader.css`

**Interfaces:**
- Consumes: recovered v1.2.0.0 manifest and ten generated HTML parts.
- Produces: continuous reader DOM, linked chapter index, stable chapter hash navigation.

- [ ] **Step 1: Add the recovered manifest and ten ordinary HTML parts**

Copy the reviewed generated v1.2.0.0 build without renumbering chapters or rewriting body claims.

- [ ] **Step 2: Add reader shell and presentation CSS**

Provide title, edition/status metadata, index navigation, reading body, and compact sticky/inline navigation without page-turn effects.

- [ ] **Step 3: Add reader loader**

Fetch `book-manifest.json`, render all manifest index links, fetch the ten parts in manifest order, append them to one continuous article, insert previous/index/next/back-to-top chapter controls, and resolve the initial URL hash only after all parts are present.

- [ ] **Step 4: Run focused validator**

Run: `python scripts/validate_literature_reader.py`
Expected: still FAIL only on library/download/navigation requirements not yet implemented.

- [ ] **Step 5: Commit reader core**

Commit message: `feat: publish Great Book continuous reader`

### Task 3: Literature Library, Download, and Discovery

**Files:**
- Create: `literature/index.html`
- Create: `literature/great-book/The-Great-Book-of-Potato-v1.2.0.0-reader-build.zip`
- Modify: `index.html`
- Modify: `explore/index.html`

**Interfaces:**
- Consumes: completed Great Book reader.
- Produces: discoverable Literature collection route with Read/Download actions from library and reader.

- [ ] **Step 1: Add Literature library landing page**

Create a compact collection page whose first work card is The Great Book of Potato, with Read and Download actions and space for future works without predefining a larger schema.

- [ ] **Step 2: Add download artifact**

Publish the complete v1.2.0.0 reader build ZIP beside the reader and link it from both the work card and reader header.

- [ ] **Step 3: Expose Literature from public navigation**

Add Literature to homepage secondary threads and archive noscript/footer discovery without replacing the five primary homepage sections.

- [ ] **Step 4: Run focused validator**

Run: `python scripts/validate_literature_reader.py`
Expected: PASS.

- [ ] **Step 5: Commit library/discovery**

Commit message: `feat: add Literature library and Great Book download`

### Task 4: Repository-Wide Verification

**Files:**
- Modify only files required by existing repository audits if a real compatibility issue is found.

**Interfaces:**
- Consumes: complete feature branch.
- Produces: evidence that the feature integrates without regressions.

- [ ] **Step 1: Run JavaScript syntax and focused validation**

Run repository JS syntax checks plus `python scripts/validate_literature_reader.py`.
Expected: PASS.

- [ ] **Step 2: Run the repository quality workflow locally where supported**

Run the same validation/build scripts used by `.github/workflows` for source-of-truth, navigation, metadata, stability, machine discovery, and public-site build.
Expected: PASS.

- [ ] **Step 3: Push the branch and open/update a pull request**

PR title: `Add Literature library and Great Book reader`

- [ ] **Step 4: Verify GitHub Actions at the exact PR head**

Expected: repository quality workflow completes successfully for the current head SHA before completion is claimed.
