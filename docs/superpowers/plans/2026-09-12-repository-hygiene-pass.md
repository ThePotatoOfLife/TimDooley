# Repository Hygiene Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce repository and CI clutter without changing canonical product behavior or deleting unique historical evidence.

**Architecture:** Keep four operational workflow classes only: repository quality, Pages deployment, country-data refresh, and explicit Edda import. Move non-canonical historical source strata out of the repository root into the existing legacy archive, rewrite provenance references, and stop shipping `archive/` in the Pages artifact. Add guards so branch-era workflows and root-level legacy strata do not accumulate again.

**Tech Stack:** GitHub Actions, Python build/validation scripts, static HTML/CSS/JavaScript, JSON/Markdown knowledge records.

**Spec:** `docs/PROJECT-STRUCTURE.md`

## Global Constraints

- Do not delete unique historical/source material merely because a newer canonical owner exists.
- `Timeline` remains the only canonical temporal-system name and `/timeline/` the canonical route.
- `archive/` is repository provenance, not a public Pages content root.
- Scheduled data refresh/import workflows remain separate from validation/deployment.
- The quality gate must retain all checks from workflows it supersedes.

---

### Task 1: Consolidate validation workflows

**Files:**
- Create: `.github/workflows/quality-checks.yml`
- Delete: `.github/workflows/atlas-check.yml`
- Delete: `.github/workflows/backend-coverage.yml`
- Delete: `.github/workflows/biblical-syncretism-check.yml`
- Delete: `.github/workflows/css-namespace-check.yml`
- Delete: `.github/workflows/expansion-check.yml`
- Delete: `.github/workflows/faq-backend-check.yml`
- Delete: `.github/workflows/machine-discoverability.yml`
- Delete: `.github/workflows/public-navigation-check.yml`
- Delete: `.github/workflows/root-navigation-ci.yml`
- Delete: `.github/workflows/science-portal-check.yml`
- Keep: `.github/workflows/pages.yml`
- Keep: `.github/workflows/country-refresh.yml`
- Keep: `.github/workflows/import-edda-texts.yml`

**Interfaces:**
- Consumes: existing Python/Node validators.
- Produces: one PR/main quality gate with the same validation coverage but one coherent execution order.

- [ ] **Step 1: Create the consolidated quality workflow**

Run source/static validators first, then build the site once, compile generated reader artifacts once, apply public patches once, and run built-site validators once.

- [ ] **Step 2: Delete superseded validation workflows**

Remove only workflows whose checks are present in the consolidated gate. Remove `root-navigation-ci.yml` as branch-era residue from a superseded navigation branch.

- [ ] **Step 3: Verify workflow inventory**

Expected active workflow files after cleanup: `quality-checks.yml`, `pages.yml`, `country-refresh.yml`, `import-edda-texts.yml`.

### Task 2: Archive root-level legacy source strata

**Files:**
- Move legacy source strata from repository root to `archive/legacy/source-strata/`.
- Modify downstream JSON/Markdown/source references to the new paths.
- Modify: `archive/legacy/README.md`
- Modify: `docs/PROJECT-STRUCTURE.md`

**Interfaces:**
- Consumes: historical documents currently retained for provenance.
- Produces: clean root with explicit legacy ownership and stable rewritten references.

- [ ] **Step 1: Move only files explicitly classified as legacy/source strata**

Candidates: `research.json`, `book-research.json`, `2026-master-framework.json`, `knowledge.json`, `POTATOVERSE-DEEP-RESEARCH.md`, `POTATOVERSE-ALTERNATIVE-RESEARCH.md`, `TIM-DOOLEY-LIFE-AND-MYTH-TIMELINE.md`, `THE-TURNING-APRIL-2025.md`, and `son-timeline.json` where present.

- [ ] **Step 2: Rewrite repository references**

Every exact path reference to a moved root source must point to `archive/legacy/source-strata/<name>`; content semantics remain unchanged.

- [ ] **Step 3: Update archive/structure documentation**

State that the source strata are now archived, not pending at root, and remain provenance-only rather than canonical owners.

### Task 3: Stop deploying repository archive material

**Files:**
- Modify: `scripts/build_site.py`
- Create/modify: repository hygiene validator.

**Interfaces:**
- Consumes: repository source tree.
- Produces: `_site/` without `archive/`, while canonical pages/data continue to build normally.

- [ ] **Step 1: Add `archive` to the build exclusion set**

The public artifact must not contain `_site/archive/`.

- [ ] **Step 2: Add hygiene validation**

Require the four-workflow inventory, reject known legacy source strata at root, and reject `_site/archive/` after a build.

### Task 4: Verify end to end

**Files:**
- Test: consolidated workflow and Pages build.

**Interfaces:**
- Consumes: cleaned repository.
- Produces: evidence that cleanup preserved behavior.

- [ ] **Step 1: Run repository hygiene validation**
Expected: PASS.

- [ ] **Step 2: Run the consolidated quality workflow**
Expected: all source validators, build, Bible, Science, navigation, discovery and shell checks pass.

- [ ] **Step 3: Run Pages deployment**
Expected: successful deployment with `/timeline/`, Bible comparator, Science library and Atlas runtime intact, and no public `archive/` tree.
