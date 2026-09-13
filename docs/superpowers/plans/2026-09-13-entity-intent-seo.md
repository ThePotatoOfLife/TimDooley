# Entity + Intent SEO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the existing site-wide SEO build understand page intent, emit typed structured data and stronger metadata, add restrained topical links, and audit semantic SEO quality across all indexable pages.

**Architecture:** Add `scripts/seo_strategy.py` as a pure route/content classification layer. Keep `scripts/optimize_seo.py` as the final projection step; it imports the strategy and applies metadata/schema/link decisions to `_site`. Add a dedicated strategy validator before changing production behavior, then extend the existing SEO pipeline validator and report.

**Tech Stack:** Python 3 standard library, static HTML, JSON-LD, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-13-entity-intent-seo-design.md`

## Global Constraints

- Preserve self-canonical URLs and current noindex behavior.
- Do not create keyword landing pages.
- Do not encode spiritual, theological or biographical claims as external factual schema properties.
- Preserve strong hand-written metadata; replace only weak/generic metadata.
- Internal SEO links must come from an explicit route map, not keyword scraping.
- No JavaScript dependency for SEO metadata or structured data.
- Missing social images are warnings, not build failures.

---

### Task 1: Strategy contract test

**Files:**
- Create: `scripts/validate_seo_strategy.py`

- [ ] Require route classifications for home, Tim profile, Bible, North, science, science paper, timeline, source authority, question and record pages.
- [ ] Require intent title/description helpers, schema-type decisions, entity topics and related-route decisions.
- [ ] Require conservative schema rules: ProfilePage may describe Tim as page subject, but must not encode spiritual claims or unsupported `sameAs` values.
- [ ] Verify current repository fails because `scripts/seo_strategy.py` does not yet exist.

### Task 2: SEO strategy module

**Files:**
- Create: `scripts/seo_strategy.py`

- [ ] Implement `classify_route(route)`.
- [ ] Implement `metadata_for(route, current_title, current_description)` that preserves good curated copy and improves weak/generic copy.
- [ ] Implement `schema_profile(route)` returning primary schema type and neutral topic/entity labels.
- [ ] Implement `related_routes(route)` from an explicit relationship map.
- [ ] Keep module pure: no filesystem mutation.

### Task 3: Integrate strategy into final optimizer

**Files:**
- Modify: `scripts/optimize_seo.py`

- [ ] Import strategy helpers.
- [ ] Apply intent metadata to weak/generic pages while preserving strong hand-written copy.
- [ ] Replace generic WebPage-only fallback with intent-aware primary JSON-LD plus existing WebSite/Breadcrumb graph.
- [ ] Add `about`, `mainEntity` and `isPartOf` conservatively.
- [ ] Add build-time related-context block only when an equivalent block is absent.
- [ ] Add social image metadata only when a stable site-owned image can be found.

### Task 4: Semantic SEO diagnostics

**Files:**
- Modify: `scripts/optimize_seo.py`
- Modify: `scripts/validate_seo_pipeline.py`

- [ ] Report intent coverage, primary schema type coverage, generic metadata count, related-context coverage and social-image coverage.
- [ ] Fail on missing intent classification for indexable canonical pages.
- [ ] Keep social-image absence as warning-only.
- [ ] Require `seo_strategy.py` and `validate_seo_strategy.py` in pipeline validation.

### Task 5: CI integration and verification

**Files:**
- Modify: `.github/workflows/pages.yml` only if needed to invoke strategy validation explicitly.
- Modify: `.github/workflows/quality-checks.yml` only if needed.

- [ ] Run strategy validation before build SEO optimization.
- [ ] Fetch final repository files from `main` and syntax-check exact contents.
- [ ] Inspect workflow/commit status.
- [ ] Confirm no change to the five-door homepage navigation or noindex redirect helpers.
