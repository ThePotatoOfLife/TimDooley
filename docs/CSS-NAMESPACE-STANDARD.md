# CSS Namespace & Page-Shell Standard

The site has two distinct presentation systems:

1. **Global/archive shell** — archive explorer, branch reader, timeline module, and application-like surfaces.
2. **Static/public reader pages** — Home, Tim Dooley, Religion, Philosophy, Science, World, context readers, FAQ, theology, etc.

They share a visual language but must not share structural class names in ways that accidentally change positioning or layout.

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

Page-specific stylesheets should define only composition and components unique to that surface. The shared file owns ordinary-page typography, colors, width roles, responsive gutters, focus treatment, navigation rhythm, and header rhythm.

Load order for migrated public pages is:

1. `app/site-system.css`;
2. page/module stylesheet;
3. narrowly scoped page-specific overrides only where the surface genuinely differs.

The six primary public surfaces—Home, Tim Dooley, Religion, Philosophy, Science, and World—use this shared foundation. Their content layouts remain intentionally different beneath the common shell.

The archive is a deliberate exception. `app/style.css` retains its slightly different application palette, wider shell, sticky navigation, search, explorer grid, and record-reader behavior. Do not import or alias shared tokens into the archive merely for numerical uniformity unless the resulting change is proven layout-neutral and visually appropriate.

## Permanent ownership rules

### Global/theme classes
Allowed globally because they are intentionally site-wide:

- `.eyebrow`
- `.summary`
- `.page*` shell classes from `app/site-system.css`
- typography/colors/tokens
- archive-owned `.top`, `.topin`, `.brand`, `.footer` where used by that application shell

### Archive-explorer structural classes
The archive sidebar is explicitly `.archive-nav`.

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

Legacy generic uses still exist on some static pages. `app/layout-guard.css` protects those pages while they are progressively migrated.

### Static reader-page structural classes
Prefer explicit `.page-*` names rather than generic structural names:

- `.page-nav`
- `.page-header`
- `.page-grid`
- `.page-section`
- `.page-card`

A static reader page should have this conceptual order:

```html
<main class="page page--standard">
  <nav class="page-nav">...</nav>
  <header class="page-header">
    <div class="eyebrow">...</div>
    <h1>...</h1>
    <p class="summary">...</p>
  </header>
  ...
</main>
```

Choose `.page--reading` for long-form/literary surfaces and `.page--wide` for denser libraries. Ordinary gateways use `.page--standard`.

The page navigation and page header are normal document-flow layers. They are not sticky unless a dedicated named component explicitly opts into sticky behavior.

## Specialized surfaces

Timeline, Bible comparison, archive/explorer, and World Map/full-screen tools may consume shared visual values where safe, but their internal tracks, grids, controls, sticky behavior, and full-screen geometry remain module-owned.

Never force `.page` article-width behavior onto a full-screen map or application surface merely to make the CSS look more uniform.

## Compatibility guard

`app/reader.css` imports `app/layout-guard.css`.

The guard exists only for older static readers that still use local `.nav` / `.grid` names. The active archive sidebar does not depend on it; `.archive-nav` is owned directly by `app/style.css`.

This is a compatibility layer, not permission to keep creating generic structural selectors.

## Automated check

Run:

```bash
python scripts/check_css_namespace_collisions.py
```

The check verifies:

- the layout guard exists;
- `reader.css` loads it;
- `app/site-system.css` exists and does not own layout through risky generic selectors;
- all six migrated primary pages retain their required shared-shell markers;
- migrated local styles do not silently recreate the canonical palette in local `:root` blocks;
- the homepage archive uses `.archive-nav` if an archive explorer is present;
- `app/style.css` does not reintroduce global `.nav` layout behavior;
- static pages that combine shared app CSS with legacy `.nav` are protected;
- other risky global structural selectors are surfaced for review.

CI runs the same check.

## Migration policy

When editing an older static page:

1. Load `app/site-system.css` before its page-specific stylesheet.
2. Put the outer document in `.page` plus the appropriate width role.
3. Change its top navigation from `class="nav"` to `class="page-nav"` (or temporarily use both if local CSS still targets `.nav`).
4. Keep eyebrow/title/summary material inside `.page-header` when practical.
5. Remove local `:root`, body, width/gutter, generic nav, and H1 rules only after the shared equivalent is proven stable.
6. Rename page-local structural `.grid`, `.section`, `.card` classes when they conflict with shared app styles.
7. Keep meaningful page personality below the shell; consistency does not require flattening every component into the same layout.
8. Never fix a collision by adding arbitrary `z-index`, negative margins, or duplicated top padding. Fix ownership/scope instead.

The goal is **one visual layer per responsibility**: shared static-page foundation, page navigation, page intro, page-specific content, optional module, and separate application shells where needed. No two layers should occupy the same coordinates by accident.
