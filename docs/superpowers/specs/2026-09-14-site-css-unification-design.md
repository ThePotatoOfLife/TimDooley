# Site CSS Unification & Visual Overhaul Design

Date: 2026-09-14
Status: Approved direction; implementation pending plan
Repository: `ThePotatoOfLife/TimDooley`

## Purpose

Unify the visual foundation of the Potato of Life site so moving between major pages feels like moving between rooms of one site rather than switching between separate microsites.

The priority is correction and consistency before enhancement. The existing dark editorial identity, dense information design, green/gold accent language, and serif/sans-serif hierarchy should remain recognizable. The overhaul should make the site feel more intentional and greater through typography, alignment, spacing, hierarchy, and shared behavior—not through a radical redesign.

## Current condition

The public site currently contains several overlapping visual systems:

- the archive/explorer shell in `app/style.css`, with a wide 1320px shell and richer application chrome;
- newer main public pages such as Home, Tim Dooley, Religion, Philosophy, Science, and World, each of which independently defines very similar colors, typography, navigation, title scale, page width, and spacing;
- specialized surfaces such as the timeline, Bible comparison tools, science readers, and world map that need shared visual language but not a forced article layout;
- legacy static readers protected by `app/layout-guard.css` while structural class names are progressively namespaced.

The repository already establishes a useful namespace rule in `docs/CSS-NAMESPACE-STANDARD.md`: shared visual classes may be global, archive structure stays archive-scoped, and static reader structure should converge toward explicit `.page-*` classes. This design extends that standard rather than replacing it.

## Design principles

### 1. Migration-first, not redesign-first

No major public surface should lose its existing page-specific stylesheet before the shared system proves equivalent or better. Shared CSS is introduced first; duplicated local rules are removed only after the migrated page is stable.

### 2. Shared foundation, local personality

The site should have one visual grammar and multiple page dialects. Typography, color, page gutters, focus states, navigation rhythm, header hierarchy, and responsive rules should be shared. Philosophy, Science, Religion, World, Archive, Timeline, and Map may keep distinct content layouts and accents where those distinctions communicate function.

### 3. One owner per responsibility

CSS responsibilities should be explicit:

- `app/site-system.css`: site-wide visual tokens and ordinary page shell primitives;
- `app/style.css`: archive/explorer-specific application layout and archive components;
- page-specific stylesheets: only page-specific composition and components;
- `app/layout-guard.css`: temporary compatibility protection for legacy static readers;
- specialized app/module stylesheets: timeline, Bible lab, world map, etc., scoped to their named components.

Generic structural selectors such as `.nav`, `.grid`, `.section`, `.card`, `.record`, or `.status` must not gain new global layout behavior.

### 4. Preserve density

The site should remain information-dense. The overhaul should improve readability through hierarchy and rhythm rather than simply increasing whitespace everywhere.

### 5. Enhancement through restraint

Visual enhancement should come from:

- more deliberate scale relationships;
- consistent vertical rhythm;
- improved title/lead alignment;
- cleaner separators;
- consistent interactive states;
- subtle depth where panels already exist;
- clearer page-family identity;
- better typography at large and small viewport widths.

No glassmorphism-heavy redesign, gratuitous animation, large decorative gradients, oversized cards, or major palette replacement is part of this work.

## Shared visual foundation

Create `app/site-system.css` as the canonical foundation for ordinary public pages.

### Canonical tokens

The shared system should define stable tokens for:

- background;
- primary ink;
- secondary/muted ink;
- faint ink;
- line/border color;
- green accent;
- gold accent;
- panel levels;
- serif and sans-serif font stacks;
- compact, reading, standard, and wide content widths;
- responsive gutters;
- border radii where globally useful;
- focus ring;
- core spacing steps.

Existing repeated values should be reconciled rather than replaced with a new palette. The current common family around `#090b09`, `#f4f0e5`, `#b8dc82`, `#d8b56b`, and `#30382f` is the baseline.

### Typography

Use one canonical body sans-serif stack and one canonical editorial serif stack.

The existing system already relies primarily on system UI for body copy and Georgia for editorial display. Keep that visual character unless a locally available, dependency-free alternative provides a concrete improvement. No external font dependency is required for this migration.

Define shared scale roles rather than hardcoding independent page values:

- display/page title;
- section title;
- card/route title;
- lead/summary;
- body;
- small metadata;
- eyebrow/kicker.

Major page H1s should share baseline behavior while allowing a small number of explicit size variants.

### Width system

Replace arbitrary page-by-page widths with named width roles:

- `--content-reading`: long-form reading surfaces;
- `--content-standard`: ordinary gateways and public pages;
- `--content-wide`: denser dashboards/libraries;
- archive shell retains its own application maximum.

A page should choose a role instead of inventing a new maximum width.

### Page shell primitives

Static/public pages should converge conceptually on:

```html
<main class="page page--standard">
  <nav class="page-nav">...</nav>
  <header class="page-header">
    <p class="eyebrow">...</p>
    <h1>...</h1>
    <p class="summary">...</p>
  </header>
  ...
</main>
```

Not every page must receive identical markup immediately, but the CSS ownership should move toward this model.

Shared primitives should include:

- `.page`;
- `.page--reading`, `.page--standard`, `.page--wide`;
- `.page-nav`;
- `.page-header`;
- `.page-header h1`;
- `.eyebrow` / kicker role;
- `.summary` / lead role;
- `.page-section`;
- `.page-footer`;
- shared focus and link behavior.

### Navigation

The main page navigation should use the same:

- font size;
- gap;
- color states;
- hover/focus behavior;
- wrap behavior;
- vertical offset from the viewport/page top;
- spacing before the page header.

Navigation content may differ by page family. World may retain a family navigation; specialized tools may have local controls. The requirement is consistent visual grammar, not identical link sets.

### Header rhythm

Ordinary public pages should align the sequence:

`page navigation -> eyebrow/kicker (optional) -> H1 -> lead/summary -> secondary note/method (optional) -> first major section`.

This sequence should use one shared spacing rhythm so moving between Tim, Religion, Philosophy, Science, and World feels stable.

## Page-family behavior

### Home

Keep the current five-door homepage architecture and restrained presentation. Use the shared tokens/typography/gutters, but do not convert it into the archive shell or add unnecessary header chrome.

### Tim Dooley

Preserve its biography/evidence presentation. Normalize page width, navigation, title, lead, section spacing, and cards/routes through shared primitives.

### Religion

Preserve the warmer theological material, Bible laboratory CTA, and green/gold distinctions. Shared shell rules should replace only duplicated global primitives.

### Philosophy

Preserve the slower literary journey, large reflective typography, and stage structure. It should inherit the shared shell but remain the most editorial/literary of the main pages.

### Science

Keep its more compact research-library character. It should inherit shared tokens, nav/header geometry, typography roles, and focus behavior while retaining library controls and result-row density.

### World

Keep its gateway/lens architecture. Normalize shell/nav/title rhythm. World-family subnavigation remains a distinct named component.

### Archive / Explore

Do not force the ordinary static page shell onto the archive. `app/style.css` keeps ownership of application layout, sticky archive navigation, search, explorer grid, and record UI. It should consume shared visual tokens where safe but keep its own layout system.

### Timeline and Bible comparison

Treat as specialized modules. They may inherit shared colors, font stacks, focus styles, and outer shell primitives, but their internal grids, filters, tracks, and interaction states remain module-scoped.

### World map / full-screen apps

Do not force article widths or document-flow headers onto full-screen tools. Share tokens and interaction conventions only where appropriate.

## Migration sequence

Implementation should be incremental and reversible.

1. Add `app/site-system.css` with tokens and opt-in primitives. Do not alter existing pages yet.
2. Add/extend automated checks for namespace safety and accidental reintroduction of generic global structural selectors.
3. Migrate the five primary public surfaces in a controlled order:
   - Home
   - Tim Dooley
   - Religion
   - Philosophy
   - Science
   - World
4. For each page:
   - load `site-system.css` first;
   - adopt explicit `.page-*` classes where practical;
   - keep local CSS intact initially;
   - move only truly shared rules into the shared layer;
   - remove duplicated local base rules after equivalence is verified;
   - verify desktop and mobile layout before moving to the next page.
5. Migrate secondary/static readers opportunistically, prioritizing pages already loading shared app CSS or known to use generic structural names.
6. Reduce `layout-guard.css` responsibility only after legacy collisions are removed; do not delete the guard prematurely.
7. Review archive/explorer tokens and optionally consume shared variables without changing its layout contract.

## Safety strategy

### No destructive first pass

The first implementation pass must not delete existing page-specific CSS wholesale.

### Explicit scoping

Shared structural rules must be scoped beneath `.page` / `.page-*` primitives. Archive structural rules remain under `#archive-explorer`, `#reader`, `.archive-*`, or named module namespaces.

### CSS load order

The intended order for migrated static pages is:

1. shared foundation;
2. page/module stylesheet;
3. only narrowly scoped temporary overrides if required.

This lets page-specific components remain authoritative while the foundation supplies defaults.

### Compatibility guard

`app/layout-guard.css` remains until the risky legacy selectors are materially reduced across the site.

### Reversibility

Each page migration should be a small coherent commit or otherwise independently reviewable change so a page can be reverted without undoing the whole visual system.

## Validation

At minimum, run existing checks including:

```bash
python scripts/check_css_namespace_collisions.py
python scripts/audit_web.py
```

Also inspect or add checks for:

- broken relative stylesheet paths;
- duplicate/conflicting global structural selectors;
- missing viewport metadata on migrated pages;
- focus visibility;
- major overflow at narrow mobile widths;
- page-title and navigation consistency;
- no accidental changes to archive sticky positioning;
- no accidental article shell applied to full-screen map surfaces.

Where existing CI already covers a category, extend it rather than creating redundant scripts.

## Visual acceptance criteria

The migration is successful when:

1. Home, Tim Dooley, Religion, Philosophy, Science, and World clearly look like parts of one site when navigated sequentially.
2. Their navigation baselines, outer gutters, title hierarchy, lead styling, and first-section rhythm are consistent.
3. Page-specific identity remains visible below the shared shell.
4. The archive/explorer still behaves as an application and does not suffer layout regressions.
5. Mobile navigation and content do not overflow or collapse into inconsistent spacing.
6. Shared color/typography values are no longer repeatedly redefined across the major pages.
7. Legacy generic selector collisions are reduced rather than masked with new z-index, negative-margin, or padding hacks.
8. The site feels more polished and deliberate without becoming less dense or substantially more decorative.

## Non-goals

This project does not include:

- changing the information architecture;
- replacing the five-door homepage model;
- redesigning the world map;
- replacing the archive application;
- adding a JavaScript design system/runtime;
- introducing a CSS framework;
- adding an external font service;
- rewriting all legacy pages in one pass;
- decorative animation as a primary enhancement.

## Result

The target state is a site with one durable visual grammar: shared typography, alignment, color, spacing, navigation, headers, focus behavior, and responsive foundations, with each major domain retaining the layout characteristics needed by its content. The visual improvement should feel evolutionary and architectural rather than cosmetic or disruptive.
