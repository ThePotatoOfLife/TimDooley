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

- [x] Remove orphan root-level CSS/JS only after repository-wide reference verification.
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


## P0 — realm readability pass (added after room audit)

- [x] Give realm-backed public pages a default pane surface for direct child sections/articles/asides/details.
- [x] Give top-level boundary/note/warning/lede blocks a readable pane instead of floating them over realm art.
- [x] Pane nested Room long-form blocks and their repeated room-run sections.
- [x] Add soft, mist and paper pane tokens so contrast can vary without inventing new page-local palettes.
- [x] Reduce default realm over-zoom by keeping the 1086px source closer to native scale.
- [x] Add a mild saturation/contrast lift to restore edge separation without blur or a duplicate art layer.
- [ ] Audit pages where a specialized layout should opt out with `.surface-clear` rather than inheriting a generic pane.
- [ ] Find direct text nodes or wrapperless prose that still escape the default pane selectors.
- [ ] Review any sections that now become double-paned because both module CSS and the global realm contract add surfaces.
- [x] Give Home major reading sections a faint outer pane while keeping stronger inner panes.
- [ ] Decide whether future realm assets should be exported above 1086×1448 so 1440p/4K displays can stay truly native-sharp.


## Cleanup batch log

- [x] Removed duplicated Room base CSS from Music & Sound, Internet & Platforms, Research Programmes, Information Ecology and Neurobiology.
- [x] Music & Sound no longer carries any inline stylesheet.
- [x] Removed orphan legacy `simple.css`, `root.css`, and `portal.css` after zero-reference verification.
- [ ] Move the remaining page-specific nested-Room blocks into shared module owners when two or more rooms repeat the same component family.
- [ ] Re-run the inline-style census after GitHub code search catches up with these commits.


## Geometry bug fixes

- [x] Fix `.dwelling-reflection` panes being visibly shorter/narrower than neighboring Room panes.
- [x] Remove old `max-width` caps from top-level `.room-essay` and `.room-ledger` surfaces so pane width follows the Room column.
- [ ] Audit remaining pane classes for fixed-width/max-width values that constrain the surface rather than only the prose measure.


## Homepage naked-component fixes

- [x] Wrap the “Five pieces of the project that can be inspected directly” link cluster in one coherent pane.
- [x] Replace its old border-top / border-bottom rule language with individual cards so stray 1px lines do not read as visual artifacts.
- [ ] Audit other homepage nav/list clusters that still rely on divider-only styling over realm art.
- [ ] Prefer framed groups + card surfaces over isolated rules whenever the background is visible behind interactive text.


## Sub-header / page-nav pass

- [x] Keep the sub-header floating and visually subtle rather than converting it into a dock or heavy card.
- [x] Normalize generated `.page-nav` menus so Home is always the leftmost anchor on non-home pages.
- [x] Preserve authored local links after Home instead of replacing page-specific navigation.
- [x] Project up to 3 governed child Rooms on top-level Dwelling pages.
- [x] Project up to 2 governed adjacent Rooms inside nested Room pages.
- [x] Use `data/house/subrooms.json` as the Room-link source instead of hard-coding a second navigation ontology.
- [x] Add CI checks for Home-first order, duplicate targets and Room-link caps.
- [x] Re-apply the navigation normalizer after special public-page rewrites so exceptions cannot undo the contract.
- [ ] Audit pages without `.page-nav` and decide which genuinely need the subtle sub-header versus intentionally specialized navigation.
- [ ] Review Room-link labels for clarity and shorten only where the full governed title is too long for the line.
- [ ] Audit whether any useful governed backend Room still lacks a public route before projecting it into navigation.
- [ ] Check mobile wrapping so the sub-header remains a clean compact line/group rather than becoming button soup.


## Orphan / legacy cleanup batch

- [x] Remove all remaining root-level CSS/JS browser assets after reference and DOM-target verification.
- [x] Add a CI guard preventing new root-level CSS/JS assets from reappearing.
- [x] Migrate FAQ and Shadow Farm onto the shared `.page-nav` contract while retaining their local `.nav` compatibility class.
- [ ] Migrate remaining intentional specialist navigation classes only when they already load `site-system.css` and can preserve local behavior.
- [ ] Continue reducing inline CSS on older public readers such as Vesica without flattening their unique diagrams.


## Cross-Room harmonization pass

- [x] Consolidate Economy, Law and Politics styling into `app/world-room.css`.
- [x] Remove their inconsistent 860/880/920px whole-pane caps; keep prose measure inside a full-width pane instead.
- [x] Consolidate Games and Visual Art specialist styling into `app/works-room.css`.
- [x] Replace divider-only specialist registries with pane-backed shared components.
- [x] Add a reusable `.room-synthesis` component for contribution / boundary / next-handoff summaries.
- [x] Add House synthesis to Games, Visual Art, Economy and Whole-body Physiology where the local page was strong but the larger contribution was implicit.
- [ ] Apply `.room-synthesis` only to specialist Rooms where it adds a real cross-domain handoff; do not stamp it mechanically onto every page.
- [ ] Continue grouping inline CSS by semantic family rather than page-by-page cleanup.
- [ ] Review remaining rich specialist Rooms for “good local essay, weak House handoff” rather than adding generic closing prose.


## Specialist Room primitive cleanup

- [x] Centralize shared `.room-reader`, `.rule`, `.case` and `.deep-links` behavior in `app/room-interior.css`.
- [x] Remove duplicated copies from Math & Geometry, Timeline Events, Other Traditions, Practice & Ethics, Canon Identities and Bible & Christianity.
- [x] Remove legacy max-width caps from those specialist reader panes; constrain prose rather than the pane surface.
- [ ] Continue moving only repeated primitives upward; keep genuinely semantic grids/components with their owning module.
- [ ] Re-run the nested-Room inline-style census after indexing catches up and choose the next family-level owner from actual remaining duplication.


## Pane coverage audit — 2026-10-03

- [x] Convert shared Dwelling Reflection from a transparent left-rule treatment into a full readable pane.
- [x] Pane shared topology context instead of leaving it between two divider rules.
- [x] Pane Room Language and specialist Room reader surfaces.
- [x] Pane major Tim reader sections, riddles, thresholds and raw-call surfaces.
- [x] Pane History, Economy, Law, Context, North and Timeline long-form reader blocks.
- [x] Pane World purpose/path surfaces, Potato threshold callouts, Corporium purpose and News orientation.
- [x] Pane major Rooms-directory architecture sections and replace border-only Dwelling tiles with real cards.
- [x] Pane comparative-cosmology section rules and modern-comparison cards.
- [ ] Audit specialist tradition pages for divider-only long-form sections that still sit directly over realm art.
- [ ] Audit figures/diagrams that technically have a border but insufficient contrast against the realm background.
- [ ] Audit generated/app surfaces (Bible tools, map panels, search drawers, timeline controls) for transparent text containers that need a local pane owner.
- [ ] Preserve true structural separators inside tables/timelines; do not convert every 1px rule into a card.
- [ ] Add visual spot-checks at mobile and desktop widths for double-pane cases and excessive nesting.
