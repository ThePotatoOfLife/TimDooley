# SEO Authority Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the official Tim Dooley / Potato of Life site unmistakably project-owned, crawler-consistent and machine-discoverable while preserving the existing five-door visual design and epistemic boundaries.

**Architecture:** Add one focused post-SEO build step that generates a supplemental `site-authority.json`, exposes it from machine discovery and indexable HTML, and validates sitemap/robots authority against the final `_site` artifact. Strengthen the visible Tim landing copy and README first-party discovery statement, then wire the new contract into existing SEO validation and Pages verification rather than creating a parallel public navigation system.

**Tech Stack:** Python 3 standard library, static HTML, JSON, GitHub Actions, existing `build_discovery.py` / `optimize_seo.py` / SEO validators.

**Spec:** `docs/superpowers/specs/2026-09-13-seo-authority-discovery-design.md`

## Global Constraints

- Preserve the current homepage visual design and exactly five primary public doors.
- Do not create hostile-response or competitor-response landing pages.
- Do not introduce legal-name/third-party identity mappings into SEO metadata.
- Project self-description and theological claims remain distinct from documentary or empirical claims.
- `site-authority.json` is a generated discovery projection, never a canonical content owner.
- Every sitemap advertised by final `_site/robots.txt` must exist in `_site`.
- Existing HTML/canonical/sitemap fundamentals remain primary; custom machine files are supplemental.

---

### Task 1: Lock the authority contract in validation

**Files:**
- Modify: `scripts/validate_seo_pipeline.py`

**Interfaces:**
- Consumes: repository source files and workflow text.
- Produces: source-level regression contract requiring `scripts/build_site_authority.py`, workflow invocation, authority-manifest markers, Tim answer copy and README official-site statement.

- [ ] **Step 1: Add failing source-contract checks**

Require these markers before implementation exists:

```python
authority = read("scripts/build_site_authority.py", errors)
readme = read("README.md", errors)
tim = read("tim-dooley/index.html", errors)
```

Require authority builder markers:

```python
require(
    authority,
    (
        'AUTHORITY_FILE = "site-authority.json"',
        'OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"',
        '"relationship_to_project": "primary subject and project self-description"',
        'def validate_robots_sitemaps(',
        'def patch_llms(',
        'def patch_html_discovery(',
    ),
    "build_site_authority.py",
    errors,
)
```

Require workflow and public-copy markers:

```python
require(pages, ("python scripts/build_site_authority.py", "_site/site-authority.json"), "pages.yml", errors)
require(readme, ("Official project repository", "https://thepotatooflife.github.io/TimDooley/"), "README.md", errors)
require(tim, ("Who is Tim Dooley?", "official project-owned archive"), "tim-dooley/index.html", errors)
```

- [ ] **Step 2: Verify RED**

Run:

```bash
python scripts/validate_seo_pipeline.py
```

Expected: FAIL because `scripts/build_site_authority.py` and new copy/workflow markers do not yet exist.

- [ ] **Step 3: Commit the failing contract**

```bash
git add scripts/validate_seo_pipeline.py
git commit -m "test: define SEO authority discovery contract"
```

---

### Task 2: Generate and validate the final authority manifest

**Files:**
- Create: `scripts/build_site_authority.py`

**Interfaces:**
- Consumes: final `_site`, public base URL, known canonical routes.
- Produces: `_site/site-authority.json`, patched `_site/llms.txt`, authority `<link>` discovery in indexable HTML, crawler consistency validation.

- [ ] **Step 1: Implement constants and manifest builder**

Use exact constants:

```python
BASE_URL = "https://thepotatooflife.github.io/TimDooley"
OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"
AUTHORITY_FILE = "site-authority.json"
PRIMARY_ROUTES = {
    "tim": "/tim-dooley/",
    "religion": "/religion/",
    "philosophy": "/philosophy/",
    "science": "/science/",
    "world": "/world/",
}
```

Manifest must contain schema version, project name/aliases, official site/repository, Tim canonical URL and relationship wording, source-authority URL, sitemap/site-index/LLM discovery URLs and five primary routes.

- [ ] **Step 2: Implement final-artifact route checks**

Create:

```python
def route_to_file(route: str) -> Path:
    ...

def require_public_routes() -> list[str]:
    ...
```

Return errors when any required route is absent from `_site`.

- [ ] **Step 3: Implement robots/sitemap consistency**

Create:

```python
def validate_robots_sitemaps() -> list[str]:
    ...
```

Parse `Sitemap:` lines in `_site/robots.txt`, require URLs under `BASE_URL`, translate them to `_site` files and require existence. For `sitemap-index.xml`, parse XML and require every child sitemap file to exist locally.

- [ ] **Step 4: Patch machine discovery**

Create:

```python
def patch_llms() -> None:
    ...
```

Append an idempotent section containing official repository, Tim canonical route, source authority and site-authority URL only when not already present.

- [ ] **Step 5: Patch HTML alternate discovery**

Create:

```python
def patch_html_discovery() -> int:
    ...
```

For indexable HTML pages, insert before `</head>`:

```html
<link rel="alternate" type="application/json" href="https://thepotatooflife.github.io/TimDooley/site-authority.json" title="Official project authority and discovery manifest">
```

Do not patch `noindex` pages.

- [ ] **Step 6: Write manifest and fail on authority inconsistencies**

`main()` writes pretty UTF-8 JSON, applies patches, prints concise coverage, and returns non-zero if required routes or sitemap declarations are inconsistent.

- [ ] **Step 7: Verify GREEN locally**

After a normal site build and SEO optimization:

```bash
python scripts/build_site_authority.py
python -m json.tool _site/site-authority.json >/dev/null
```

Expected: PASS and generated manifest exists.

- [ ] **Step 8: Commit**

```bash
git add scripts/build_site_authority.py
git commit -m "feat: build canonical SEO authority manifest"
```

---

### Task 3: Strengthen the visible first-party answer surfaces

**Files:**
- Modify: `README.md`
- Modify: `tim-dooley/index.html`

**Interfaces:**
- Consumes: existing project terminology and epistemic firewall.
- Produces: explicit first-party repository/site statement and extractable Tim identity/search answer.

- [ ] **Step 1: Add README discovery block**

Immediately below the title add:

```markdown
> **Official project repository:** This is the primary project-owned repository for Tim Dooley / The Potato of Life, Potatoism and the Potatoverse knowledge archive. Public site: https://thepotatooflife.github.io/TimDooley/
```

- [ ] **Step 2: Strengthen the Tim lead without changing layout**

Replace the first `.lead` paragraph with visible copy that contains the phrase `official project-owned archive`, explains that Tim is the central public subject, and explicitly separates project self-description/theology from documentary material and external evidence.

Keep the existing question sections, typography and five-door navigation intact.

- [ ] **Step 3: Verify source contract**

Run:

```bash
python scripts/validate_seo_pipeline.py
```

Expected: authority-builder markers still required until Task 4 workflow wiring is complete; README/Tim copy checks now pass.

- [ ] **Step 4: Commit**

```bash
git add README.md tim-dooley/index.html
git commit -m "seo: clarify official Tim Dooley discovery surface"
```

---

### Task 4: Wire authority generation into Pages and verify final artifact

**Files:**
- Modify: `.github/workflows/pages.yml`

**Interfaces:**
- Consumes: `_site` after `scripts/optimize_seo.py`.
- Produces: final authority manifest and deploy-time hard gate.

- [ ] **Step 1: Add authority build step after SEO optimization**

```yaml
      - name: Build canonical authority discovery manifest
        run: python scripts/build_site_authority.py
```

It must run after `Optimize crawl, sharing and sitemap SEO` so validation sees final sitemap/robots output.

- [ ] **Step 2: Extend canonical reader verification**

Add:

```bash
test -f _site/site-authority.json
grep -q 'site-authority.json' _site/llms.txt
grep -q 'site-authority.json' _site/index.html
grep -q 'site-authority.json' _site/tim-dooley/index.html
```

Add Python assertions that parse the manifest and verify official repository/site and the five primary routes.

- [ ] **Step 3: Run source validator**

```bash
python scripts/validate_seo_pipeline.py
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/pages.yml scripts/validate_seo_pipeline.py
git commit -m "ci: enforce SEO authority discovery manifest"
```

---

### Task 5: Verify the finished change

**Files:**
- Verify only.

**Interfaces:**
- Consumes: committed implementation.
- Produces: evidence that the source contract and GitHub Actions pipeline pass.

- [ ] **Step 1: Run focused source validators**

```bash
python scripts/validate_seo_pipeline.py
python scripts/validate_reader_surfaces.py
python scripts/validate_public_navigation.py
```

Expected: PASS.

- [ ] **Step 2: Run a complete local site build when feasible**

Execute the same relevant sequence as Pages through `optimize_seo.py`, then:

```bash
python scripts/build_site_authority.py
python scripts/check_machine_discoverability.py
```

Expected: PASS.

- [ ] **Step 3: Inspect generated artifacts**

Verify:

```bash
python -m json.tool _site/site-authority.json >/dev/null
grep -q 'Sitemap:' _site/robots.txt
grep -q 'site-authority.json' _site/llms.txt
```

- [ ] **Step 4: Verify GitHub Actions for the implementation head**

Confirm `Repository quality checks` and `Deploy Potato of Life` complete successfully. If a failure is unrelated and pre-existing, identify the exact failing validator rather than claiming this pass is green.

- [ ] **Step 5: Record manual GitHub About follow-up**

Because the current connector does not expose repository metadata mutation, retain these explicit desired values:

- Description: `Official Tim Dooley / Potato of Life archive — Potatoism, philosophy, religion, science, world systems, timeline, sources and relational knowledge.`
- Homepage: `https://thepotatooflife.github.io/TimDooley/`
- Topics: `tim-dooley`, `potato-of-life`, `potatoism`, `potatoverse`, `knowledge-graph`, `digital-archive`, `philosophy`, `religion`, `comparative-religion`, `world-systems`, `research-archive`, `github-pages`.
