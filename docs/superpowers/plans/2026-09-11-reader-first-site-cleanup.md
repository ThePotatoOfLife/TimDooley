# Reader-First Site Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the public site into one coherent reader-facing publication with five obvious entrances and direct access to substantive material.

**Architecture:** Preserve the deep research/data archive, but remove archive taxonomy and duplicate mini-site structure from the primary reader path. Canonical pages are Home, Tim Dooley, Religion, Philosophy, Science and World Map; specialist URLs remain as deep pages or redirects. Religion gains a direct Jesus ↔ Tim/Son comparison; North becomes subordinate to the World Map.

**Tech Stack:** Static HTML/CSS/JavaScript on GitHub Pages; JSON research records; Python validation scripts.

**Spec:** `docs/superpowers/specs/2026-09-11-reader-first-site-cleanup-design.md`

## Global Constraints

- One subject gets one obvious public entrance.
- Canonical homepage entrances: Tim Dooley, Religion, Philosophy, Science, World Map.
- Assume readers are intelligent; remove hand-holding, repeated definitions, slogans and routing explanations.
- Prefer direct content over routing cards and archive machinery.
- Preserve useful source/data files.
- World Map is the canonical geographical/geopolitical interface; North Axis is subordinate to it.
- Jesus ↔ Tim/Son comparison must be discoverable from Religion and Tim within one click.
- No public-page iframe dependency.

---

### Task 1: Enforce the canonical public shell

**Files:**
- Modify: `index.html`
- Modify: `scripts/validate_site_shell.py`

**Interfaces:**
- Produces: five primary homepage routes: `/tim-dooley/`, `/religion/`, `/philosophy/`, `/science/`, `/world-map/3d.html`.

- [ ] Replace the 13-card homepage gateway wall with five direct subject links.
- [ ] Remove hidden archive-reader bootstrapping from the homepage.
- [ ] Keep only minimal utility links outside the five subjects.
- [ ] Extend site-shell validation to fail if retired public routing markers or archive explorer hooks return to the homepage.
- [ ] Verify the five canonical hrefs are present and the removed gateway hrefs are absent from primary navigation.

### Task 2: Make Religion substantive immediately

**Files:**
- Modify: `religion/index.html`
- Create: `religion/jesus-tim/index.html`
- Source: `knowledge/theology/son-jesus-passion-detention-overlap-atlas.json`

**Interfaces:**
- Produces: `/religion/jesus-tim/` as the canonical reader comparison.

- [ ] Replace Religion's archive-routing grid with direct links to Jesus ↔ Tim/Son, Bible, project theology and comparative/symbol material.
- [ ] Remove `explore/#branch=...` as the way to reach core religion material.
- [ ] Render the existing Jesus/Son atlas into clean two-column comparison rows: Jesus | Tim/Son, with relation and mismatch/boundary underneath.
- [ ] Keep the canonical-Gospel custody/prison correction visible without turning it into a lecture.
- [ ] Link to the comparison from Religion and Tim.

### Task 3: Collapse North into the World Map path

**Files:**
- Modify: `north/index.html`

**Interfaces:**
- Consumes: `world-map/3d.html` as the canonical world interface.
- Produces: a short North page whose primary action is opening the World Map.

- [ ] Remove the North mini-site section wall and local six-link navigation.
- [ ] Preserve only a concise definition of North Axis plus a direct World Map link and a small number of relevant research links.
- [ ] Verify the World Map is the dominant route rather than another explanatory section.

### Task 4: Strip shell clutter from Tim, Philosophy and Science

**Files:**
- Modify: `tim-dooley/index.html`
- Modify: `philosophy/index.html`
- Modify: `science/index.html`

**Interfaces:**
- Produces: three substantive canonical subject pages sharing the same minimal top navigation.

- [ ] Tim: remove jump-pill wall and introductory answer-card duplication; put dossier content first and add direct Jesus comparison route.
- [ ] Philosophy: remove entry-card wall, jump-pill wall, “how to read” lecture and archive-furniture explanation; begin with substantive sayings/arguments.
- [ ] Science: remove dashboard/programme-strip/tutorial shell while preserving the seven models, equations and records below.
- [ ] Keep section-local anchors only where they materially help long-page navigation.

### Task 5: Demote archive utilities and duplicates

**Files:**
- Review: `faq/index.html`, `explore/index.html`, `index-a-z/index.html`, `context/index.html`, `corporium/index.html`, `chronology/index.html`, `tim-dooley/*/index.html`
- Modify only where reader-facing competition remains.

**Interfaces:**
- Produces: archive utilities that remain reachable but no longer compete as main-site entrances.

- [ ] Classify public pages as canonical, useful specialist, archive utility, or redirect candidate.
- [ ] Remove links to archive utilities from primary canonical navigation.
- [ ] Where two public pages perform the same reader job, keep one canonical page and redirect/subordinate the other without deleting source research.

### Task 6: Update discovery and regression checks

**Files:**
- Modify: `sitemap.xml`
- Modify: `llms.txt` if needed
- Modify: `scripts/validate_site_shell.py`

**Interfaces:**
- Produces: machine discovery matching the simplified reader architecture.

- [ ] Add `/religion/jesus-tim/` to the sitemap.
- [ ] Make machine guidance point to canonical reader pages, not obsolete routes.
- [ ] Validate: homepage has five primary entrances; Religion links Jesus comparison; Tim links Jesus comparison; North links World Map; no homepage iframe/archive explorer dependency.
- [ ] Refetch changed files from GitHub and inspect the deployed GitHub Pages routes when deployment is available in the current session.
