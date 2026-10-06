# Science Paper Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `/science/` into the single clean public library for all substantial science records, with searchable abstracts, compact field/type filters, full generated readable documents, and downloadable canonical source JSON.

**Architecture:** Extend the existing `scripts/build_science_catalog.py` pipeline rather than creating a second science database. `knowledge/science/**/*.json` remains canonical; the build derives deterministic document metadata, qualifies substantial records, patches `/science/` with a complete abstract library, and generates `/science/papers/<slug>/` pages. The public Pages workflow must run this generator before validation/deployment.

**Tech Stack:** Static HTML/CSS/vanilla JS, Python 3 build scripts, GitHub Pages, JSON source records.

**Spec:** `docs/superpowers/specs/2026-09-11-science-paper-library-design.md`

## Global Constraints

- `/science/` is the only canonical public Science hub.
- `knowledge/science/**/*.json` remains the canonical source layer; do not create a second paper database.
- Subject fields are multi-valued filters, not sub-sites.
- Document type is independent from scientific field.
- Every qualifying item must open a full readable generated document.
- Every generated document must expose its canonical JSON source and GitHub source.
- Formatting must preserve scientific/epistemic status and must not upgrade speculation into validated science.
- New qualifying science records must appear automatically on rebuild.
- Main library is a continuous row list, not a card wall.

---

### Task 1: Add a regression contract for the Science portal

**Files:**
- Create: `scripts/validate_science_portal.py`
- Modify: `.github/workflows/atlas-check.yml`

**Interfaces:**
- Consumes: source `science/index.html`, `scripts/build_science_catalog.py`, and built `_site/science/...` output.
- Produces: one validator that fails when the hub loses search/filter/list semantics, when generated papers are missing, or when raw JSON/source controls disappear.

- [ ] **Step 1: Write the failing validator**

Require source markers:

```python
SOURCE_MARKERS = (
    'id="science-search"',
    'id="science-field"',
    'id="science-type"',
    'id="science-results"',
    '<!-- SCIENCE_CATALOG_STATIC -->',
    'science-library.css',
    'science-library.js',
)
```

Require builder markers:

```python
BUILDER_MARKERS = (
    'classify_fields',
    'classify_document_type',
    'qualifies_for_library',
    'render_paper_page',
    'PAPERS_DIR',
    'Download source JSON',
    'View source on GitHub',
)
```

When `_site/science/catalog.json` exists, parse it and require:

```python
assert payload['qualifying_count'] >= 10
assert payload['papers']
for paper in payload['papers']:
    assert paper['slug']
    assert paper['abstract']
    assert paper['fields']
    assert paper['document_type']
    assert (SITE / 'science' / 'papers' / paper['slug'] / 'index.html').exists()
```

Require at least one generated paper page to contain `Abstract`, `Download source JSON`, `View source on GitHub`, and its canonical `knowledge/science/` path.

- [ ] **Step 2: Run validator before implementation**

Run after a normal site build:

```bash
python scripts/build_site.py
python scripts/validate_science_portal.py
```

Expected: FAIL because the current `/science/` source does not expose the paper-library contract and generated paper pages do not exist.

- [ ] **Step 3: Add validator to the integrity workflow after science compilation**

Insert:

```yaml
      - name: Validate science paper library
        run: python scripts/validate_science_portal.py
```

after `Compile complete science catalog`.

- [ ] **Step 4: Commit**

```bash
git add scripts/validate_science_portal.py .github/workflows/atlas-check.yml
git commit -m "test: protect science paper library"
```

---

### Task 2: Replace the static seven-model Science page with the portal shell

**Files:**
- Modify: `science/index.html`
- Create: `science/science-library.css`
- Create: `science/science-library.js`

**Interfaces:**
- Consumes: static cards injected at `<!-- SCIENCE_CATALOG_STATIC -->` by the build script.
- Produces: stable DOM IDs used by the validator and client-side filter code.

- [ ] **Step 1: Replace `science/index.html` with the approved low-clutter shell**

The body must contain:

```html
<h1>SCIENCE</h1>
<p class="science-lede">Papers, mathematical formulations, scientific audits and research programmes developed throughout the Potato of Life project.</p>
<div class="science-controls">
  <label class="science-search-wrap">Search
    <input id="science-search" type="search" placeholder="Search titles, abstracts, equations, concepts…">
  </label>
  <label>Field<select id="science-field"><option value="all">All fields</option></select></label>
  <label>Document type<select id="science-type"><option value="all">All document types</option></select></label>
</div>
<div class="science-count" id="science-count" aria-live="polite"></div>
<section class="science-results" id="science-results">
<!-- SCIENCE_CATALOG_STATIC -->
</section>
```

Use the existing five-section navigation and canonical metadata.

- [ ] **Step 2: Add low-eye-load CSS**

The desktop document row must use:

```css
.science-record{display:grid;grid-template-columns:150px minmax(0,1fr) 150px;gap:22px;padding:28px 3px;border-bottom:1px solid var(--science-line)}
```

Use continuous rows, visible abstracts, restrained chips, one optional equation line, and vertical stacking on narrow screens. Do not add a dashboard or category card wall.

- [ ] **Step 3: Add client-side filtering**

`science-library.js` must:

```js
const rows=[...document.querySelectorAll('.science-record')];
```

Populate unique field/type options from row `data-fields` and `data-type`, then apply:

```js
const visible = matchesSearch && matchesField && matchesType;
row.hidden = !visible;
```

Update `#science-count` with the current result count. Default view shows all rows.

- [ ] **Step 4: Commit**

```bash
git add science/index.html science/science-library.css science/science-library.js
git commit -m "feat: make science a paper library portal"
```

---

### Task 3: Extend the science catalog into deterministic document metadata

**Files:**
- Modify: `scripts/build_science_catalog.py`

**Interfaces:**
- Produces each record with:

```python
{
  'file': str,
  'slug': str,
  'title': str,
  'abstract': str,
  'status': str,
  'maturity': str,
  'updated': str,
  'fields': list[str],
  'document_type': str,
  'equations': list[str],
  'findings': list[str],
  'keywords': list[str],
  'qualifies': bool,
}
```

- [ ] **Step 1: Add deterministic field classification**

Implement `classify_fields(path: Path, data: dict) -> list[str]` using explicit token dictionaries over filename/title/status/known topic/domain strings. Initial canonical display labels:

```python
FIELD_RULES = {
    'Physics': (...),
    'Cosmology & Astronomy': (...),
    'Quantum Science': (...),
    'Neuroscience': (...),
    'Biology': (...),
    'Chemistry': (...),
    'Psychology': (...),
    'Information Science': (...),
    'Mathematics & Formal Systems': (...),
}
```

A record may receive multiple fields. If none match, use `Cross-disciplinary` rather than guessing one narrow discipline.

- [ ] **Step 2: Add deterministic document-type classification**

Implement `classify_document_type(path: Path, data: dict) -> str` with precedence:

1. explicit `document_type` if valid;
2. recovery/archaeology wording -> `Recovery / Archaeology`;
3. audit wording -> `Scientific Audit`;
4. programme/program wording -> `Research Programme`;
5. framework/formalism/toy-model/formulation-upgrade wording -> `Formal Note / Framework`;
6. theory/model with substantial model content -> `Theory / Paper`;
7. fallback -> `Research Record`.

- [ ] **Step 3: Add qualification rules**

Implement `qualifies_for_library(path: Path, data: dict, record: dict) -> bool`.

Reject obvious administrative records when filename/status/title includes `index`, `ledger`, `registry`, `inventory`, `router`, or `source-ledger`, unless the record also contains a substantive `abstract` and at least two scientific-content groups.

Count scientific-content groups among keys matching:

```python
('research_question','model','equation','formula','formal','method','finding','result','observable','test','falsification','failure','reference','experiment','mechanism','dynamics','derivation')
```

Qualify when an abstract/substantive summary exists and at least one scientific-content group exists, or when two or more scientific-content groups exist with a substantial purpose/summary.

- [ ] **Step 4: Add normalized keywords**

Collect short explicit `topics`, `concepts`, `keywords`, `motifs`, `named_frameworks`, and connection names for search only. Cap generated search keywords to avoid giant HTML attributes.

- [ ] **Step 5: Run Python syntax check**

```bash
python -m py_compile scripts/build_science_catalog.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_science_catalog.py
git commit -m "feat: classify science library records"
```

---

### Task 4: Generate full readable paper/document pages

**Files:**
- Modify: `scripts/build_science_catalog.py`
- Create: `science/science-paper.css`

**Interfaces:**
- Consumes: normalized records from Task 3 and original JSON dictionaries.
- Produces: `_site/science/papers/<slug>/index.html` for every qualifying record.

- [ ] **Step 1: Add paper output constants**

```python
PAPERS_DIR = OUT / 'papers'
GITHUB_BLOB_BASE = 'https://github.com/ThePotatoOfLife/TimDooley/blob/main/knowledge/science/'
```

- [ ] **Step 2: Implement semantic section rendering**

Add helpers:

```python
def humanize_key(key: str) -> str: ...
def render_value(value, depth=0) -> str: ...
def render_semantic_sections(data: dict) -> str: ...
```

Use preferred key groups for abstract/question/context/model/equations/findings/tests/limits/open-work/lineage/references, then render remaining substantive keys once. Avoid rendering administrative keys (`id`, `title`, `version`, `updated`, `status`, `maturity`, `abstract`) twice.

- [ ] **Step 3: Render equations distinctly**

Strings under equation/formula/action/lagrangian/operator/dynamics/formalism keys should render in `<pre class="paper-equation"><code>...</code></pre>` rather than ordinary prose.

- [ ] **Step 4: Implement `render_paper_page`**

Each page includes:

```html
<a href="../../">← Science</a>
<h1>...</h1>
<p class="paper-abstract">...</p>
<a class="source-action" href="../../../knowledge/science/...json" download>Download source JSON</a>
<a class="source-action" href="https://github.com/ThePotatoOfLife/TimDooley/blob/main/knowledge/science/...json">View source on GitHub</a>
```

Display document type, fields, status/maturity, update date, and canonical source path without letting metadata dominate the page.

- [ ] **Step 5: Add paper stylesheet**

Optimize for long reading: max-width around 900px, readable serif headings, monospaced equations with horizontal overflow, nested section hierarchy, references and source controls at the end.

- [ ] **Step 6: Build and inspect representative outputs**

Run:

```bash
python scripts/build_site.py
python scripts/build_science_catalog.py
```

Inspect generated pages for:

- UPT;
- microtubules/tubulin;
- one formulation-upgrade record;
- one recovery/archaeology record.

Confirm they render materially different section sets without empty fake headings.

- [ ] **Step 7: Commit**

```bash
git add scripts/build_science_catalog.py science/science-paper.css
git commit -m "feat: generate readable science papers"
```

---

### Task 5: Build the complete abstract library from qualifying records

**Files:**
- Modify: `scripts/build_science_catalog.py`

**Interfaces:**
- Produces: injected `.science-record` rows, `_site/science/catalog.json`, and filter metadata used by `science-library.js`.

- [ ] **Step 1: Replace legacy catalog-card rendering with science-record rows**

For each qualifying record render:

```html
<article class="science-record" data-fields="Physics|Quantum Science" data-type="Theory / Paper" data-search="...">
  <div class="science-record-meta">...</div>
  <div class="science-record-body">
    <h2>...</h2>
    <p class="science-abstract">...</p>
    <code class="science-equation-preview">...</code>
  </div>
  <div class="science-record-actions">
    <a href="./papers/<slug>/">Read full paper →</a>
    <a href="../knowledge/science/<file>" download>Download source JSON</a>
  </div>
</article>
```

Use `Read full document →` for non-paper document types.

- [ ] **Step 2: Write catalog JSON with both raw and public counts**

```python
payload = {
    'generated': date.today().isoformat(),
    'source_directory': 'knowledge/science/',
    'record_count': len(records),
    'qualifying_count': len(papers),
    'fields': sorted(...),
    'document_types': sorted(...),
    'papers': papers,
}
```

Do not expose a second canonical copy of full paper content in the catalog; metadata only.

- [ ] **Step 3: Patch the source hub marker**

`patch_science_page()` must replace exactly one `<!-- SCIENCE_CATALOG_STATIC -->` in `_site/science/index.html` and fail loudly if it is missing.

- [ ] **Step 4: Generate a secondary `/science/catalog/` only as a noindex/raw metadata utility or retire its old card-wall role**

Prefer a simple redirect/noindex utility pointing back to `/science/` because the main hub now contains the complete library.

- [ ] **Step 5: Run the portal validator**

```bash
python scripts/build_site.py
python scripts/build_science_catalog.py
python scripts/validate_science_portal.py
```

Expected: `SCIENCE PORTAL VALIDATION PASSED`.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_science_catalog.py
git commit -m "feat: publish complete science abstract library"
```

---

### Task 6: Make GitHub Pages deploy the science library

**Files:**
- Modify: `.github/workflows/pages.yml`

**Interfaces:**
- Consumes: `scripts/build_science_catalog.py` and `scripts/validate_science_portal.py`.
- Produces: deployed `_site/science/` with generated papers.

- [ ] **Step 1: Add science compilation after site build**

Immediately after `Build Pages artifact` add:

```yaml
      - name: Compile complete science paper library
        run: python scripts/build_science_catalog.py

      - name: Validate science paper library
        run: python scripts/validate_science_portal.py
```

- [ ] **Step 2: Strengthen canonical-reader verification**

Require:

```bash
test -f _site/science/catalog.json
grep -q 'id="science-search"' _site/science/index.html
grep -q 'class="science-record"' _site/science/index.html
```

and verify with Python that `qualifying_count >= 10` and every catalog slug has a generated `science/papers/<slug>/index.html`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/pages.yml
git commit -m "ci: deploy generated science paper library"
```

---

### Task 7: Final verification and integration

**Files:**
- No new production files unless verification reveals a defect.

**Interfaces:**
- Verifies all previous tasks together.

- [ ] **Step 1: Run local/static verification**

```bash
python -m py_compile scripts/build_science_catalog.py scripts/validate_science_portal.py
python scripts/build_site.py
python scripts/build_science_catalog.py
python scripts/validate_science_portal.py
python scripts/validate_site_shell.py
```

Expected: all pass.

- [ ] **Step 2: Check generated library scale**

Inspect `_site/science/catalog.json` and report:

- total science records discovered;
- qualifying public documents;
- field counts;
- document-type counts;
- generated paper-page count.

This catches accidental under-filtering or a page flooded by administrative records.

- [ ] **Step 3: Verify representative source links**

For at least three generated paper pages, confirm relative `Download source JSON` paths resolve inside `_site/knowledge/science/` and GitHub source URLs point at the same repository-relative path.

- [ ] **Step 4: Open pull request and wait for CI**

Create a PR from `science-paper-library` to `main`. Confirm `Atlas integrity check` passes before merge.

- [ ] **Step 5: Merge/fast-forward only after green checks, then inspect Pages workflow**

After integration to `main`, confirm the Pages run executes `Compile complete science paper library`, `Validate science paper library`, site-shell validation, artifact upload and deployment successfully.

- [ ] **Step 6: Verify the live page**

Open `https://thepotatooflife.github.io/TimDooley/science/` and confirm:

- the abstract library is visible;
- search works;
- field/type filters work;
- representative full paper links open;
- source JSON downloads/opens correctly;
- no giant category/card wall has reappeared.
