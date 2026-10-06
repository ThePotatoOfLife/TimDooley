# Site CSS Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify typography, alignment, navigation, page-header rhythm, spacing, colors, focus behavior, and responsive shell rules across the main public Potato of Life pages without destabilizing archive/application surfaces or erasing page-specific character.

**Architecture:** Introduce an opt-in shared foundation at `app/site-system.css`. Migrate major public pages one at a time to explicit `.page-*` shell classes while leaving archive/application layout in its current scoped CSS. Extend the existing namespace audit so shared structural behavior cannot leak back into generic selectors.

**Tech Stack:** Static HTML, CSS, Python validation scripts, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-14-site-css-unification-design.md`

## Global Constraints

- Correction and consistency come before visual enhancement.
- Preserve the current dark editorial identity, information density, green/gold accent language, and serif/sans-serif hierarchy.
- Do not introduce a CSS framework, JavaScript design-system runtime, external font service, or major new dependency.
- Shared structural rules must be scoped through `.page` / `.page-*` primitives; do not add global structural behavior to `.nav`, `.grid`, `.section`, `.card`, `.record`, or `.status`.
- Archive layout remains owned by `app/style.css` under archive/application namespaces.
- `app/layout-guard.css` remains in place during migration.
- Do not force article-width shells onto full-screen map/application surfaces.
- Migrate incrementally and keep page-local CSS until shared behavior is proven stable.

---

## File Structure

### New shared foundation

- Create `app/site-system.css`
  - Owns canonical color tokens, typography stacks, width roles, page shell, navigation rhythm, header rhythm, shared focus behavior, generic page sections, and responsive gutters.
  - Does not own archive grid/sidebar positioning or specialized module layouts.

### Validation

- Modify `scripts/check_css_namespace_collisions.py`
  - Require `app/site-system.css` to exist.
  - Guard against risky global structural selectors inside the new shared stylesheet.
  - Verify migrated primary pages load the shared stylesheet.
- Modify `scripts/audit_web.py` only if required to validate shared stylesheet presence or references. Prefer extending the namespace script when possible.

### Primary public surfaces

- Modify `index.html`
- Modify `tim-dooley/index.html`
- Modify `religion/index.html`
- Modify `philosophy/index.html`
- Modify `philosophy/philosophy.css`
- Modify `science/index.html`
- Modify `science/science-library.css`
- Modify `world/index.html`

### Existing global/application styles

- Modify `app/style.css` only if needed to consume shared tokens safely. Do not change archive layout ownership in the first migration pass.
- Do not remove `app/layout-guard.css`.

---

### Task 1: Add the Shared Site Foundation and Safety Tests

**Files:**
- Create: `app/site-system.css`
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: existing canonical visual values from current public pages and `docs/CSS-NAMESPACE-STANDARD.md`.
- Produces: opt-in `.page`, `.page--reading`, `.page--standard`, `.page--wide`, `.page-nav`, `.page-header`, `.eyebrow`, `.summary`, `.page-section`, `.page-footer` classes and canonical `--site-*` tokens.

- [ ] **Step 1: Add failing validation for the shared stylesheet**

Extend `scripts/check_css_namespace_collisions.py` with:

```python
SITE_SYSTEM = ROOT / "app" / "site-system.css"

if not SITE_SYSTEM.exists():
    errors.append("app/site-system.css is missing")
else:
    site_system = SITE_SYSTEM.read_text(encoding="utf-8")
    for selector in (".nav", ".grid", ".section", ".card", ".record", ".status"):
        for block in re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", site_system):
            if re.search(r"\b(position|top|inset|z-index|display|grid-template-columns|grid-template-rows)\s*:", block):
                errors.append(
                    f"app/site-system.css must not assign structural layout through generic {selector}; use .page-* or a named component"
                )
```

- [ ] **Step 2: Run the namespace check and verify it fails**

Run:

```bash
python scripts/check_css_namespace_collisions.py
```

Expected: FAIL with `app/site-system.css is missing`.

- [ ] **Step 3: Create `app/site-system.css` with canonical opt-in primitives**

Create the shared file with this foundation:

```css
:root {
  --site-bg: #090b09;
  --site-ink: #f4f0e5;
  --site-muted: #9fa79d;
  --site-faint: #727a70;
  --site-line: #30382f;
  --site-green: #b8dc82;
  --site-gold: #d8b56b;
  --site-panel: #0f130f;
  --site-panel-strong: #111611;
  --site-font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --site-font-serif: Georgia, "Times New Roman", serif;
  --site-content-reading: 980px;
  --site-content-standard: 1060px;
  --site-content-wide: 1160px;
  --site-gutter: clamp(16px, 3vw, 24px);
  --site-focus: #e0c17c;
}

* { box-sizing: border-box; }

html { background: var(--site-bg); }

body {
  margin: 0;
  background: var(--site-bg);
  color: var(--site-ink);
  font-family: var(--site-font-sans);
  font-size: 16px;
  line-height: 1.64;
}

a {
  color: var(--site-green);
  text-underline-offset: 3px;
}

a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
[tabindex]:focus-visible {
  outline: 3px solid var(--site-focus);
  outline-offset: 3px;
}

.page {
  width: min(100%, calc(var(--site-content-standard) + (2 * var(--site-gutter))));
  margin-inline: auto;
  padding: 38px var(--site-gutter) 100px;
}

.page--reading {
  width: min(100%, calc(var(--site-content-reading) + (2 * var(--site-gutter))));
}

.page--wide {
  width: min(100%, calc(var(--site-content-wide) + (2 * var(--site-gutter))));
}

.page-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin: 0 0 52px;
  font-size: 14px;
}

.page-nav a {
  color: var(--site-muted);
  text-decoration: none;
}

.page-nav a:hover,
.page-nav a:focus-visible,
.page-nav a[aria-current="page"] {
  color: var(--site-green);
}

.page-header {
  margin: 0 0 38px;
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--site-green);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.page-header h1 {
  margin: 0 0 20px;
  font-family: var(--site-font-serif);
  font-size: clamp(54px, 9vw, 104px);
  font-weight: 400;
  letter-spacing: -.06em;
  line-height: .86;
}

.summary {
  max-width: 900px;
  margin: 0;
  color: #d9ddd5;
  font-family: var(--site-font-serif);
  font-size: clamp(20px, 2.3vw, 23px);
  line-height: 1.52;
}

.page-section {
  border-top: 1px solid var(--site-line);
}

.page-footer {
  margin-top: 38px;
  padding-top: 18px;
  border-top: 1px solid var(--site-line);
  color: var(--site-muted);
  font-size: 13px;
}

@media (max-width: 700px) {
  .page {
    padding-top: 30px;
    padding-bottom: 76px;
  }

  .page-nav {
    margin-bottom: 38px;
  }

  .page-header {
    margin-bottom: 30px;
  }
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto !important; }
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
```

- [ ] **Step 4: Run the namespace test**

Run:

```bash
python scripts/check_css_namespace_collisions.py
```

Expected: PASS, with only pre-existing warnings if any.

- [ ] **Step 5: Commit the foundation**

```bash
git add app/site-system.css scripts/check_css_namespace_collisions.py
git commit -m "style: add shared site visual foundation"
```

---

### Task 2: Migrate the Homepage Without Changing Its Five-Door Structure

**Files:**
- Modify: `index.html`
- Test: `scripts/check_css_namespace_collisions.py`, `scripts/audit_web.py`

**Interfaces:**
- Consumes: `app/site-system.css` tokens and typography.
- Produces: homepage using the shared visual foundation while retaining its existing five-door information architecture.

- [ ] **Step 1: Add a test requiring the homepage to load the shared stylesheet**

Add to `scripts/check_css_namespace_collisions.py`:

```python
PRIMARY_MIGRATED_PAGES = [ROOT / "index.html"]
for page in PRIMARY_MIGRATED_PAGES:
    text = page.read_text(encoding="utf-8", errors="ignore")
    if "app/site-system.css" not in text:
        errors.append(f"{page.relative_to(ROOT)} must load app/site-system.css")
```

- [ ] **Step 2: Run validation and verify it fails**

```bash
python scripts/check_css_namespace_collisions.py
```

Expected: FAIL because `index.html` does not yet load `app/site-system.css`.

- [ ] **Step 3: Load the shared CSS before homepage-local styles**

Add inside `<head>` before the existing `<style>` block:

```html
<link rel="stylesheet" href="app/site-system.css?v=20260914a">
```

Change:

```html
<body><main data-reader-surface="home">
```

to:

```html
<body><main class="page page--standard home-page" data-reader-surface="home">
```

Keep the five door links and their content unchanged.

- [ ] **Step 4: Remove duplicated homepage base declarations but preserve homepage-specific composition**

From the inline homepage CSS, remove/rewrite only rules now owned by `site-system.css`:

- root color definitions;
- `*{box-sizing:border-box}`;
- body margin/background/color/font;
- main width/margins/gutters;

Keep homepage-specific `h1`, `.project-purpose`, `.evidence-note`, `.sections`, `.secondary-threads`, and footer composition. Rebase their colors to `var(--site-*)` tokens where direct duplication exists.

- [ ] **Step 5: Run integrity tests**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
```

Expected: both PASS.

- [ ] **Step 6: Commit homepage migration**

```bash
git add index.html scripts/check_css_namespace_collisions.py
git commit -m "style: migrate homepage to shared site system"
```

---

### Task 3: Migrate Tim Dooley to the Shared Page Shell

**Files:**
- Modify: `tim-dooley/index.html`
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: `.page`, `.page--reading`, `.page-nav`, `.page-header`, `.summary`.
- Produces: Tim page with shared navigation/header alignment and unchanged biography/evidence content layout.

- [ ] **Step 1: Extend the migrated-page validation list**

Change the validation list to:

```python
PRIMARY_MIGRATED_PAGES = [
    ROOT / "index.html",
    ROOT / "tim-dooley" / "index.html",
]
```

Run the check and confirm it fails for Tim Dooley.

- [ ] **Step 2: Load `site-system.css`**

Add:

```html
<link rel="stylesheet" href="../app/site-system.css?v=20260914a">
```

before the local `<style>` block.

- [ ] **Step 3: Adopt explicit shell markup**

Change the outer main and first page elements to:

```html
<body><main class="page page--reading tim-page" data-reader-surface="tim">
<nav class="page-nav" aria-label="Primary">...</nav>
<header class="page-header">
  <h1>TIM<br>DOOLEY</h1>
  <p class="summary lead">...</p>
</header>
```

Close the header immediately after the lead paragraph.

- [ ] **Step 4: Remove local base CSS now owned by the shared foundation**

Remove local declarations for root shared colors, `*`, body, `.wrap`, generic `nav`, generic nav anchors, and base H1/lead rules. Keep the content-specific classes (`.questions`, `.question-stub`, `.primary`, `.sequence`, `.reading-frame`, `.work`, `.deep`) and convert repeated colors to `var(--site-*)` where safe.

- [ ] **Step 5: Validate**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tim-dooley/index.html scripts/check_css_namespace_collisions.py
git commit -m "style: unify Tim Dooley page shell"
```

---

### Task 4: Migrate Religion While Preserving Its Warm Theological Components

**Files:**
- Modify: `religion/index.html`
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: shared standard page shell.
- Produces: Religion page with uniform nav/header geometry while retaining theology core and Bible-lab CTA styling.

- [ ] **Step 1: Add Religion to `PRIMARY_MIGRATED_PAGES` and verify the test fails**

Add:

```python
ROOT / "religion" / "index.html",
```

Run the namespace test and confirm failure.

- [ ] **Step 2: Load shared CSS and adopt the standard shell**

Add:

```html
<link rel="stylesheet" href="../app/site-system.css?v=20260914a">
```

Change main/nav/title/lead markup to:

```html
<main class="page page--standard religion-page" data-reader-surface="religion">
<nav class="page-nav" aria-label="Primary">...</nav>
<header class="page-header">
  <h1>RELIGION</h1>
  <p class="summary lead">...</p>
  <p class="method">...</p>
</header>
```

- [ ] **Step 3: Strip only duplicated shell CSS**

Remove root/body/wrap/nav/H1/lead declarations from Religion's inline CSS. Keep `.method`, `.theology-core`, `.core-line`, `.bible-lab-cta`, `.lab-families`, `.question-stub`, `.minor`, `.boundary`, and page-specific responsive layouts.

- [ ] **Step 4: Normalize shared values to tokens**

Use `var(--site-green)`, `var(--site-gold)`, `var(--site-muted)`, `var(--site-line)`, and `var(--site-font-serif)` where values are purely shared visual language. Do not flatten the CTA's warmer local background.

- [ ] **Step 5: Validate and commit**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
git add religion/index.html scripts/check_css_namespace_collisions.py
git commit -m "style: unify religion page shell"
```

---

### Task 5: Migrate Philosophy Without Flattening Its Literary Rhythm

**Files:**
- Modify: `philosophy/index.html`
- Modify: `philosophy/philosophy.css`
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: shared reading-width shell and page navigation.
- Produces: Philosophy retains threshold/journey typography while its outer shell aligns with the rest of the site.

- [ ] **Step 1: Add Philosophy to the migrated-page validator and verify failure**

Add:

```python
ROOT / "philosophy" / "index.html",
```

- [ ] **Step 2: Load shared CSS before page CSS**

```html
<link rel="stylesheet" href="../app/site-system.css?v=20260914a">
<link rel="stylesheet" href="./philosophy.css">
```

- [ ] **Step 3: Adopt `.page` and `.page-nav` without forcing the threshold into generic summary typography**

Use:

```html
<main class="page page--reading philosophy-page" data-reader-surface="philosophy">
<nav class="page-nav" aria-label="Primary">...</nav>
<header class="page-header philosophy-header">
  <h1>PHILOSOPHY</h1>
  <div class="threshold">...</div>
</header>
```

This keeps the philosophy-specific challenge/root-rule hierarchy intact.

- [ ] **Step 4: Remove duplicated base CSS from `philosophy.css`**

Delete local root/shared color declarations, global box-sizing, body shell, `.wrap`, generic nav, generic nav anchor, and global H1 rules. Keep `.threshold`, `.ownership`, `.journey`, `.movement`, `.reflection`, `.philosophy-story`, `.chew`, `.tool-line`, `.deep-source`, `.deep`.

- [ ] **Step 5: Convert shared repeated visual values to tokens**

Examples:

```css
color: var(--site-green);
color: var(--site-gold);
border-color: var(--site-line);
font-family: var(--site-font-serif);
```

- [ ] **Step 6: Validate and commit**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
git add philosophy/index.html philosophy/philosophy.css scripts/check_css_namespace_collisions.py
git commit -m "style: unify philosophy page shell"
```

---

### Task 6: Migrate Science While Preserving Research-Library Density

**Files:**
- Modify: `science/index.html`
- Modify: `science/science-library.css`
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: shared wide page shell and common header/nav typography.
- Produces: Science remains a dense research library with standardized outer geometry.

- [ ] **Step 1: Add Science to the migrated-page validator and verify failure**

Add:

```python
ROOT / "science" / "index.html",
```

- [ ] **Step 2: Load shared CSS before `science-library.css`**

```html
<link rel="stylesheet" href="../app/site-system.css?v=20260914a">
<link rel="stylesheet" href="./science-library.css?v=20260911a">
```

- [ ] **Step 3: Adopt the wide shell and shared navigation/header classes**

Change outer markup to:

```html
<main class="page page--wide science-page" data-reader-surface="science">
<nav class="page-nav science-nav" aria-label="Primary">...</nav>
<header class="page-header science-hero">
  <p class="eyebrow science-kicker">Research library</p>
  <h1>SCIENCE</h1>
  <p class="summary science-lede">...</p>
</header>
```

- [ ] **Step 4: Remove duplicated foundation rules from `science-library.css`**

Remove `:root` shared color declarations, global `*`, `html`, `body`, `.science-page` width/gutters, `.science-nav` base flex/gap/margin, `.science-nav a` base shared state, and duplicate hero H1/lede typography where the shared classes already provide equivalent behavior.

Keep science-specific control grids, record rows, field/status metadata, results, empty state, footnote, and science-specific breakpoints.

- [ ] **Step 5: Preserve compact research behavior**

If the shared `.summary` is visually too large for Science, define a narrow modifier only under `.science-hero .science-lede`, e.g.:

```css
.science-hero .science-lede {
  max-width: 850px;
  font-size: clamp(20px, 2.3vw, 25px);
}
```

Do not override the global shell itself.

- [ ] **Step 6: Validate and commit**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
git add science/index.html science/science-library.css scripts/check_css_namespace_collisions.py
git commit -m "style: unify science page shell"
```

---

### Task 7: Migrate World and Preserve Its Family Navigation

**Files:**
- Modify: `world/index.html`
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: shared standard shell.
- Produces: World route family remains distinct while using site-wide type/spacing/token rules.

- [ ] **Step 1: Add World to the migrated-page validator and verify failure**

Add:

```python
ROOT / "world" / "index.html",
```

- [ ] **Step 2: Load shared CSS**

```html
<link rel="stylesheet" href="../app/site-system.css?v=20260914a">
```

- [ ] **Step 3: Adopt the standard shell and explicit named family navigation**

Use:

```html
<main class="page page--standard world-page" data-reader-surface="world">
<nav class="page-nav world-family" aria-label="World sections">...</nav>
<header class="page-header">
  <h1>WORLD</h1>
  <p class="summary lead">...</p>
  <p class="note">...</p>
</header>
```

- [ ] **Step 4: Remove duplicated shell CSS and retain lens routes**

Delete root/body/wrap and duplicated nav/H1/lead shell declarations. Retain `.world-family` only for World-specific differences not already owned by `.page-nav`, plus `.note`, `.routes`, `.deep`, and route responsive behavior.

- [ ] **Step 5: Validate and commit**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
git add world/index.html scripts/check_css_namespace_collisions.py
git commit -m "style: unify world page shell"
```

---

### Task 8: Add Cross-Page Consistency Checks

**Files:**
- Modify: `scripts/check_css_namespace_collisions.py`

**Interfaces:**
- Consumes: all six migrated primary surfaces.
- Produces: durable CI protection against regression to isolated page shells.

- [ ] **Step 1: Add exact required shell markers for migrated pages**

Define:

```python
MIGRATED_SHELL_REQUIREMENTS = {
    ROOT / "index.html": ("site-system.css", 'class="page ',),
    ROOT / "tim-dooley" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "religion" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "philosophy" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "science" / "index.html": ("site-system.css", "page-nav", "page-header"),
    ROOT / "world" / "index.html": ("site-system.css", "page-nav", "page-header"),
}

for page, markers in MIGRATED_SHELL_REQUIREMENTS.items():
    text = page.read_text(encoding="utf-8", errors="ignore")
    for marker in markers:
        if marker not in text:
            errors.append(f"{page.relative_to(ROOT)} missing shared shell marker: {marker}")
```

- [ ] **Step 2: Add a duplicate-token warning for migrated page CSS**

For local CSS associated with migrated pages, warn when it redefines the canonical palette literals in a `:root` block:

```python
CANONICAL_TOKEN_LITERALS = ("#090b09", "#f4f0e5", "#b8dc82", "#d8b56b", "#30382f")
```

Only inspect `:root{...}` / `:root {...}` blocks so legitimate component colors are not falsely flagged.

- [ ] **Step 3: Run full checks**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add scripts/check_css_namespace_collisions.py
git commit -m "test: guard shared page shell consistency"
```

---

### Task 9: Review Archive Token Compatibility Without Changing Layout

**Files:**
- Modify: `app/style.css` only if the change is mechanical and layout-neutral.

**Interfaces:**
- Consumes: canonical `--site-*` tokens.
- Produces: reduced palette drift between archive and public pages, with archive layout unchanged.

- [ ] **Step 1: Compare archive token values to the shared system**

Inspect the top-level variables in `app/style.css`. If values are equivalent or close enough to map safely, add aliases such as:

```css
:root {
  --bg: var(--site-bg, #080a08);
  --ink: var(--site-ink, #f4f0e5);
  --muted: var(--site-muted, #a8ada3);
  --line: var(--site-line, #2b322b);
  --green: var(--site-green, #a8ce72);
  --gold: var(--site-gold, #d8b56b);
}
```

Only do this if the archive's visual contrast remains acceptable. If archive-specific values are materially intentional, leave them unchanged and document that distinction instead.

- [ ] **Step 2: Do not alter archive structural selectors**

No changes to `.grid`, `.archive-nav`, `.top`, `.topin`, sticky behavior, reader dimensions, or archive responsive breakpoints are part of this task.

- [ ] **Step 3: Validate**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
```

Expected: PASS.

- [ ] **Step 4: Commit only if a safe token-only change was made**

```bash
git add app/style.css
git commit -m "style: align archive palette tokens"
```

If no safe token-only change is justified, make no commit for this task.

---

### Task 10: Final Regression Sweep and Documentation Update

**Files:**
- Modify: `docs/CSS-NAMESPACE-STANDARD.md`
- Test: full web/CSS checks

**Interfaces:**
- Consumes: completed shared foundation and migrated primary surfaces.
- Produces: documented permanent ownership rules for future CSS work.

- [ ] **Step 1: Update the CSS standard**

Add a section documenting:

```markdown
## Shared visual foundation

`app/site-system.css` owns site-wide visual tokens and opt-in static-page shell primitives.

Static/public pages should prefer:

- `.page`
- `.page--reading`
- `.page--standard`
- `.page--wide`
- `.page-nav`
- `.page-header`
- `.eyebrow`
- `.summary`
- `.page-section`
- `.page-footer`

Page-specific stylesheets should define only composition/components unique to that surface. Archive/application structural behavior remains outside this file.
```

- [ ] **Step 2: Run all CSS/web integrity checks**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
```

Expected: PASS.

- [ ] **Step 3: Inspect source diffs for forbidden migration patterns**

Run:

```bash
git diff --check
```

Expected: no whitespace errors.

Then inspect the migration diff and confirm:

- no new generic global `.nav`, `.grid`, `.section`, `.card`, `.record`, `.status` structural ownership;
- no new negative-margin/z-index hacks used to fake header alignment;
- no archive sticky/navigation behavior removed;
- no full-screen map page was given `.page` article width;
- all six primary pages load `site-system.css`.

- [ ] **Step 4: Commit documentation**

```bash
git add docs/CSS-NAMESPACE-STANDARD.md
git commit -m "docs: codify shared site visual system"
```

- [ ] **Step 5: Final verification**

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
git status --short
```

Expected: both checks PASS and working tree is clean.
