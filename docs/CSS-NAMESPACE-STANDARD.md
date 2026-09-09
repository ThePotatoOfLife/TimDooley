# CSS Namespace & Page-Shell Standard

The site has two distinct presentation systems:

1. **Global/archive shell** — homepage header, archive explorer, branch reader, timeline module.
2. **Static reader pages** — chronology, context, science, Corporium, FAQ, theology, etc.

They must not share structural class names in ways that change positioning or layout.

## Permanent ownership rules

### Global/theme classes
Allowed globally because they are intentionally site-wide:

- `.eyebrow`
- `.summary`
- typography/colors/tokens
- `.top`, `.topin`, `.brand`, `.footer`

### Archive-explorer structural classes
New archive-only layout rules must be scoped beneath one of:

- `#archive-explorer`
- `#reader`
- `.archive-*`
- `.tl-*` for timeline components

Do **not** add new global sticky/absolute/grid rules to generic names such as:

- `.nav`
- `.grid`
- `.section`
- `.record`
- `.status`
- `.card`

Legacy uses still exist. `app/layout-guard.css` protects static pages while they are progressively migrated.

### Static reader-page structural classes
Prefer:

- `.page-nav`
- `.page-header`
- `.page-grid`
- `.page-section`
- `.page-card`

A static reader page should have this conceptual order:

```html
<main class="page">
  <nav class="page-nav">...</nav>
  <header class="page-header">
    <div class="eyebrow">...</div>
    <h1>...</h1>
    <p class="summary">...</p>
  </header>
  ...
</main>
```

The page navigation and page header are normal document-flow layers. They are not sticky unless a dedicated named component explicitly opts into sticky behavior.

## Compatibility guard

`app/reader.css` imports `app/layout-guard.css`.

The guard neutralizes the historical archive `.nav { position: sticky; top: 92px; }` behavior inside static `.page` / `.wrap` readers. It also prevents generic archive-grid defaults from creating large accidental bottom spacing on page-local grids.

This is intentionally a compatibility layer, not permission to keep creating generic structural selectors.

## Automated check

Run:

```bash
python scripts/check_css_namespace_collisions.py
```

The check verifies:

- the layout guard exists;
- reader.css loads it;
- static pages that combine `app/style.css` with legacy `.nav` are protected;
- additional risky global structural rules are surfaced for review.

CI runs the same check.

## Migration policy

When editing an older static page:

1. Change its top navigation from `class="nav"` to `class="page-nav"` (or temporarily use both if local CSS still targets `.nav`).
2. Keep the eyebrow/title/summary inside a `.page-header` when practical.
3. Rename page-local structural `.grid`, `.section`, `.card` classes when they conflict with shared app styles.
4. Never fix a collision by adding arbitrary `z-index`, negative margins, or duplicated top padding. Fix ownership/scope instead.

The goal is **one visual layer per responsibility**: site shell, page navigation, page intro, page content, optional module. No two layers should occupy the same coordinates by accident.
