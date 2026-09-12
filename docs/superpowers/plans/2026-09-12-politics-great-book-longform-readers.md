# Politics + Great Book Long-Form Readers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a provenance-aware politics compendium and The Great Book of Potato v1.2.0.0 as durable, linkable long-form readers.

**Architecture:** Politics is a static indexed reader assembled from four HTML sections and a machine-readable provenance ledger. The Great Book uses one shell, one manifest with 171 recovered chapter records, and ten ordinary HTML parts loaded into a continuous document while preserving legacy anchors.

**Tech Stack:** Static HTML/CSS/JavaScript, JSON manifests, Python repository validators, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-12-politics-great-book-longform-readers.md`

## Global Constraints
- Preserve Great Book legacy chapter numbers and anchors.
- Treat the source body as primary and the old index as a secondary editorial witness.
- Preserve epistemic distinctions in political material and investigative leads.
- Keep both readers mobile-friendly and linkable without focus/zoom manipulation.

---

### Task 1: Politics reader
**Files:** `politics/index.html`, `politics/politics-manifest.json`, `politics/parts/*.html`, `app/politics-reader.js`, `knowledge/politics/tim-dooley-politics-geopolitics-compendium.json`
- [x] Add indexed reader shell and four ordered content parts.
- [x] Add mode/provenance-aware machine record and explicit unresolved positions.
- [x] Validate section ids and TOC targets.

### Task 2: Great Book v1.2.0.0
**Files:** `great-book/index.html`, `great-book/book-manifest.json`, `great-book/parts/*.html`, `app/great-book-reader.js`
- [x] Recover body headings and produce 171 chapter records.
- [x] Preserve legacy anchors and title aliases.
- [x] Split the continuous edition into ten ordinary HTML parts.
- [x] Render one index/URL namespace in the browser.

### Task 3: Navigation and validation
**Files:** `index.html`, `explore/index.html`, `scripts/validate_longform_readers.py`, `.github/workflows/quality-checks.yml`
- [x] Link both readers from public entry surfaces.
- [x] Add a focused validator for required pages, version, unique anchors, resolvable links and part integrity.
- [ ] Run the full repository CI suite on the pull request and fix integration regressions before merge.
