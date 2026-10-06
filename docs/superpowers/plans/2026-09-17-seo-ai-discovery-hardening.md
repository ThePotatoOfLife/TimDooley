# SEO and AI Discovery Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the official Tim Dooley / Potato of Life site easier for Google, Gemini-related Google crawling, Bing/Copilot, ChatGPT Search, and other standards-compliant search/AI retrieval systems to identify, crawl, index and cite accurately.

**Architecture:** Strengthen the existing SEO projection rather than creating a second SEO stack. `build_discovery.py` remains the owner of generated crawler and machine-discovery surfaces; `optimize_seo.py` remains the final canonical/sitemap owner; `build_site_authority.py` remains the authority-manifest projection. Visible homepage copy and structured data provide the human-readable authority statement that machine files mirror.

**Tech Stack:** Python 3 site builders/validators, static HTML, Schema.org JSON-LD, robots.txt, XML sitemaps, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-13-seo-authority-discovery-design.md`

## Global Constraints

- Do not redesign the homepage.
- Do not use hidden text, cloaking, doorway pages, link schemes or keyword stuffing.
- Do not turn project theological self-description into externally verified fact.
- Keep canonical URLs, sitemap entries, visible content and structured data consistent.
- `llms.txt` and custom JSON are supplemental discovery surfaces, not ranking controls.
- Do not invent an undocumented xAI/Grok crawler token; retain wildcard access for standards-compliant crawlers.

---

### Task 1: Lock the crawler and authority contract

**Files:**
- Modify: `scripts/validate_seo_2026_contract.py`
- Modify: `scripts/validate_seo_pipeline.py`

**Interfaces:**
- Consumes: checked-in `robots.txt`, source `index.html`, `scripts/build_discovery.py`.
- Produces: regression requirements for explicit documented crawler groups, sitemap-index consistency, official authority links and machine-discovery ownership fields.

- [ ] **Step 1: Write failing crawler-policy assertions**

Require `Googlebot`, `Google-Extended`, `bingbot`, `OAI-SearchBot`, wildcard `*`, and the canonical `sitemap-index.xml` in the checked-in policy and generated discovery owner.

- [ ] **Step 2: Write failing homepage/discovery assertions**

Require the homepage sitemap link to use `sitemap-index.xml`, require a visible official-project answer, and require `build_discovery.py` to own the official repository, source-authority URL and authority-manifest URL.

- [ ] **Step 3: Run the focused SEO contract**

Run: `python scripts/validate_seo_2026_contract.py`
Expected before implementation: FAIL on the new crawler/discovery requirements.

### Task 2: Harden generated crawler and AI discovery surfaces

**Files:**
- Modify: `scripts/build_discovery.py`
- Modify: `robots.txt`

**Interfaces:**
- Consumes: `BASE_URL` and House-derived `PRIMARY_DOORS`.
- Produces: `robots_text() -> str`, generated `robots.txt`, `discovery.json`, `llms.txt` and `llms-full.txt` with coherent official authority references.

- [ ] **Step 1: Add a single crawler-policy helper**

Define a documented search/retrieval allowlist for `Googlebot`, `Google-Extended`, `bingbot`, and `OAI-SearchBot`, followed by `User-agent: *` with `Allow: /`, and one canonical sitemap-index declaration.

- [ ] **Step 2: Add first-class authority constants**

Define the official repository, source-authority route and `site-authority.json` URL once in `build_discovery.py`.

- [ ] **Step 3: Project authority into machine files**

Add official repository, canonical Tim route, source-authority route and authority manifest to `discovery.json`, `llms.txt` and `llms-full.txt` so they do not depend on a later patch to become useful.

- [ ] **Step 4: Synchronize the checked-in crawler policy**

Make root `robots.txt` byte-for-byte equivalent in policy meaning to the generated policy.

### Task 3: Strengthen the canonical homepage answer

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: existing five-door navigation and source-authority route.
- Produces: clearer visible first-party identity, canonical sitemap-index discovery, and structured entity links that mirror visible content.

- [ ] **Step 1: Strengthen title and description**

Use an explicit official-project/archive description covering Tim Dooley, The Potato of Life, Potatoism and the Potatoverse without keyword stuffing.

- [ ] **Step 2: Fix sitemap discovery**

Change the homepage `<link rel="sitemap">` from the child `sitemap.xml` to the canonical `sitemap-index.xml`.

- [ ] **Step 3: Strengthen visible authority copy**

Make the first visible paragraph identify the page as the official project-owned public archive and add ordinary visible links to the source/evidence policy and official repository.

- [ ] **Step 4: Tighten homepage JSON-LD**

Keep `WebSite` + `Project`, add safe aliases and canonical site-owned topic URLs, and retain the repository relationship without adding unsupported identity claims.

### Task 4: Verify the final projection

**Files:**
- Test: `scripts/validate_seo_2026_contract.py`
- Test: `scripts/validate_seo_pipeline.py`
- Test: `scripts/validate_discovery_projection.py`
- Build: existing site build and quality workflow

**Interfaces:**
- Consumes: all changes above.
- Produces: a merge-ready SEO branch with evidence that crawler, discovery, schema and site-build contracts remain green.

- [ ] **Step 1: Run focused validators**

Run:
`python scripts/validate_seo_2026_contract.py`
`python scripts/validate_seo_pipeline.py`
`python scripts/validate_discovery_projection.py`

Expected: PASS.

- [ ] **Step 2: Open a PR to `main`**

Use the isolated feature branch so GitHub runs the repository's canonical quality workflow against the final diff.

- [ ] **Step 3: Read the full quality result**

Expected: repository quality workflow conclusion `success`, including public build, SEO optimization, machine discoverability and site-shell validation.

- [ ] **Step 4: Preserve post-deploy indexing actions as operational follow-up**

After deployment, resubmit/request crawl through Google Search Console and Bing Webmaster Tools when account access is available; do not represent submission as already performed.