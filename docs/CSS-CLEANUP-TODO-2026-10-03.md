# CSS cleanup work queue — 2026-10-03

Active cleanup queue for the post-unification pass. The goal is one owner per visual responsibility, not one giant stylesheet.

## Completed / verified

- [x] One canonical global foundation in `app/site-system.css`.
- [x] One canonical Heaven / Plane / Below environment renderer in `app/site-elevator.css`.
- [x] Home owns its separate multi-realm scrolling compositor.
- [x] Lower-layer CSS no longer paints a competing underground background.
- [x] Retired SVG realm scenes are removed from production.
- [x] Current main passes Core, World Map, Content and Public Build quality groups.
- [x] Current deployed Pages artifact passes the live smoke test.

## P0 — inline-style migration debt

- [ ] Move the repeated compact tradition-reader CSS into a scoped shared stylesheet.
- [ ] Add a CI guard preventing migrated tradition readers from regaining inline structural CSS.
- [ ] Audit all public HTML files that still contain `<style>`; classify each as legitimate specialized geometry or migration debt.
- [ ] Consolidate repeated relation-room / CIA reader styling.
- [ ] Consolidate repeated science reader styling where an existing science stylesheet already owns the same semantics.
- [ ] Consolidate repeated context / FAQ / theology pane and card fragments.

## P0 — visual regression coverage

- [ ] Add rendered geometry checks for Home and one Heaven, Plane and Below reader.
- [ ] Check 360px, 390px, 768px and desktop widths for horizontal overflow.
- [ ] Guard against clipped headings, pane collisions and bottom-dock overlap.
- [ ] Add a small manual screenshot-review checklist for visual changes semantic validators cannot prove.

## P1 — dead CSS and ownership

- [ ] Remove orphan root-level CSS/JS only after repository-wide reference verification.
- [ ] Generate a stylesheet ownership inventory: foundation, floor, reader, Room, CIA, Bible, map/tool, archive application.
- [ ] Add a validator that flags stylesheets with zero HTML/JS/build references.
- [ ] Continue stripping dead width/padding overrides from pages already migrated to `.page--reading` and `.page--wide`.
- [ ] Review small module stylesheets for consolidation only when they genuinely share an owner.

## P1 — Home / realm polish

- [ ] Review the pale reading shaft against every major Home section.
- [ ] Replace remaining floating text with panes where the art remains too visually busy.
- [ ] Check Heaven / Plane / Below crop at common aspect ratios and during the full scroll pan.
- [ ] Review elevator, journey control, accessibility dock and site counter as one fixed-UI stack.
- [ ] Keep final AVIF realm art as the only environment source.

## Definition of clean

A page is clean when it has a named layout owner, no dead compatibility override, no duplicate environment compositor, no unexplained inline structural CSS, no supported-width overflow, and a validator protecting the architectural rule most likely to regress.
