# Potato of Life Site House Navigation & Visual Overhaul

**Date:** 2026-09-17  
**Status:** Design specification  
**Scope:** Public website information architecture, navigation, shared visual system, generated-page shelling, and deployment hygiene  
**Repository:** `ThePotatoOfLife/TimDooley`

## 1. Purpose

The public site contains strong material but currently behaves like several generations of websites layered together. The main failure is not merely visual inconsistency. It is that public route identity, page hierarchy, navigation, generated pages, and CSS ownership are only partially centralized.

The redesign will make the project behave as one navigable House without flattening the different kinds of content into one generic page template.

The governing reader model is:

> **One House → five primary Doors → Rooms → local Paths → deep records.**

The visitor should always be able to answer four questions quickly:

1. Where am I in the House?
2. What kind of page am I reading or using?
3. What are the nearest meaningful destinations?
4. How do I go Home, go up one level, or go deeper?

The redesign must preserve the project's existing canonical principle that presentation is a view over canonical owners rather than a second source of truth.

---

## 2. Context discovered during the full-site inventory

The repository currently contains multiple public presentation generations plus generated public pages:

1. **Newer shared-shell readers** using `app/site-system.css`.
2. **Archive/reader-shell pages** using `app/style.css` and `app/reader.css`.
3. **One-off pages** with local `:root`, body, layout, navigation, card, and responsive CSS embedded directly in HTML.
4. **Specialist applications** such as World Map, Bible comparison, Explore, and interactive Timeline surfaces.
5. **Long-form readers** such as the Great Book and other continuous-text works.
6. **Utility tools** such as TTS.
7. **Compatibility redirects** whose only job is preserving old URLs.
8. **Build-generated public families** including `/topics/`, `/context/`, `/records/`, `/questions/`, question-family indexes, and `/index-a-z/`.
9. **Legacy/archive HTML** that should remain preserved in the repository but should not become parallel live public presentation.

The current route and navigation intent is also duplicated across several systems:

- `data/house/public-surfaces.json`
- `data/house/rooms.json`
- `data/frontend-atlas-bridge.json`
- `manifest.json`
- hand-authored page headers
- build generators
- sitemap/SEO machinery
- post-build navigation patchers

These sources do not always agree. The existing `public-surfaces.json` / House resolver should therefore be strengthened rather than replaced by a new navigation database.

---

## 3. Design options considered

### Option A — Patch and standardize the current pages

Migrate more pages onto the existing `site-system.css`, normalize obvious header links, and leave each HTML page responsible for its own navigation.

**Advantages**
- Lowest short-term code risk.
- Smallest visual change.
- Can be applied incrementally.

**Disadvantages**
- Does not solve route-authority duplication.
- Headers can drift again immediately.
- Generated pages remain a separate visual/navigation system.
- Every future page author must remember the same navigation rules manually.
- Great Book and other underexposed routes remain dependent on hand-placed links.

This is rejected as insufficient.

### Option B — Generated House shell + shared visual system (**chosen**)

Keep the static-site architecture and current canonical data owners, but make the House registry the public navigation authority. Build or project a shared House shell onto all appropriate public surfaces while preserving specialized internal layouts where necessary.

**Advantages**
- Solves navigation drift structurally.
- Works with GitHub Pages and the existing build pipeline.
- Preserves specialist tools rather than rewriting them.
- Allows gradual content-shell migration while immediately improving global orientation.
- Lets CI enforce the same rules on future pages.
- Gives generated pages the same public identity as hand-authored pages.

**Disadvantages**
- Requires careful build integration.
- Requires a page-family classification system so full-screen tools are not forced into article geometry.
- Requires migration testing across old reader CSS.

This is the recommended and selected architecture.

### Option C — Replace the public site with a client-side application/router

Move navigation and page rendering into a central SPA or component framework.

**Advantages**
- Strongest component centralization.
- Easy shared navigation state.

**Disadvantages**
- Unnecessary rewrite.
- Risks crawlability and static-reader simplicity.
- Would destabilize mature interactive surfaces.
- Creates a new framework dependency while the repository already has a viable static build system.
- Violates YAGNI for the actual problem.

This is rejected.

---

## 4. Information architecture

### 4.1 The five primary Doors remain permanent

The homepage continues to expose exactly five primary gateways:

1. Tim Dooley
2. Religion
3. Philosophy
4. Science
5. World

These are the stable top-level public domains. The redesign must not turn Rooms, World Map, Great Book, Timeline, Politics, or any specialist route into additional primary Doors.

### 4.2 Rooms remain the middle floor

Rooms are subject neighborhoods and cross-domain public corridors. They reduce pressure on the five Doors without competing with them.

Examples include:

- Culture
- History
- Politics
- Law
- Economy
- World Systems
- Sources / Evidence
- other bounded contexts already represented in `data/house/rooms.json`

The Rooms hub should be generated from room/surface metadata rather than maintained as an unrelated hand-coded directory.

### 4.3 Paths are ways of traversing material

Paths are not additional top-level domains. They are reader journeys across the House.

Important Paths include:

- Story
- Timeline
- Great Book
- Collection
- Works
- Bible comparison
- World Map
- question discovery

The site should make the distinction visible:

- **Door:** where a subject belongs.
- **Room:** a bounded neighborhood of related subjects.
- **Path:** a way of moving through material.
- **Depth:** records, sources, questions, A–Z, and archive exploration.

### 4.4 Depth/discovery layer

Deep discovery surfaces remain quieter than primary navigation:

- Explore
- Questions
- A–Z
- Sources / Context
- generated Topics
- generated Contexts
- generated Records

These should be easy to reach but should not dominate every header.

---

## 5. Global navigation architecture

### 5.1 Layer 1 — Permanent House bar

Every real visitor-facing content surface receives a form of the House identity layer.

On normal desktop reader pages the conceptual structure is:

**Potato of Life** | **Tim · Religion · Philosophy · Science · World** | **Book · Rooms · Explore · Find**

Rules:

- The Potato of Life brand always links Home.
- The five Doors are visually primary.
- Book, Rooms, Explore, and Find are visually secondary.
- The bar must stay concise; Questions, A–Z, Sources, Timeline, and other secondary links belong behind contextual navigation or discovery rather than all appearing at once.
- The current primary Door should be visually identifiable without becoming loud.

`Find` may route to Questions/A–Z/search discovery depending on final implementation, but it should not introduce a new search backend requirement merely for visual completeness.

### 5.2 Layer 2 — Breadcrumb / context trail

Normal public readers receive a compact context trail below the House bar.

Examples:

- Home / Tim Dooley / Public Witness
- Home / Religion / Bible
- Home / World / North
- Home / Science / Axis & 11D

The breadcrumb owns parentage. This removes the need for each local nav to invent a different “back” strategy.

### 5.3 Layer 3 — Local family navigation

A page may then expose its nearest siblings, based on metadata rather than arbitrary hand-authored lists.

Examples:

**Tim family**  
Overview · Story · Timeline · 100,000 Hours · Public Witness · Evidence · Works

**Religion family**  
Overview · Bible · Sacred Symbols · Traditions · Practice · Sources

**World family**  
Overview · Map · Politics · Economy · Law · North · Systems

Local navigation is contextual, not global. It must not repeat the full House bar.

### 5.4 Layer 4 — Page-specific controls

Controls for the actual surface remain owned by that surface.

Examples:

- Great Book: chapters, search, progress, TTS.
- Bible: comparison focus, filters, traversal.
- World Map: layers, search, inspector, selected geography.
- Timeline: date/lens/filter controls.
- TTS tool: playback/editor controls.

Global navigation and application controls must not be visually conflated.

### 5.5 Layer 5 — Continue exploring

Normal editorial pages receive a quiet end-of-page relation block generated from navigation metadata.

It should answer:

- **Up** — parent surface
- **Beside** — nearby sibling surfaces
- **Across** — useful cross-domain relation
- **Deeper** — Explore / Sources / records when relevant

This replaces arbitrary footer link piles.

### 5.6 Global footer

One uniform lightweight footer provides stable discovery and project routes. It must not repeat the entire site map.

Likely stable entries:

- Questions
- A–Z
- Sources
- Explore
- accessibility/tooling route if needed

---

## 6. Route authority

### 6.1 `public-surfaces.json` becomes comprehensive public-surface authority

Do not create another navigation database.

Extend the existing surface registry so durable human-facing surfaces can declare enough metadata for shell generation.

Each durable surface should be able to express:

- `id`
- `title`
- `canonical_route`
- `primary_parent`
- `surface_type`
- `shell_type`
- `visibility`
- `navigation_group`
- `rooms`
- `indexability`
- optional legacy aliases / redirect routes

Generated individual question/record pages do not need one handcrafted row each. Instead, their **families/generators** receive a defined shell type and routing contract.

### 6.2 Existing authorities retain their proper responsibilities

- `public-surfaces.json`: public route identity and navigation placement.
- `rooms.json`: bounded-context / room semantics.
- `frontend-atlas-bridge.json`: backend-to-public projection intent.
- `manifest.json`: deep archive branch structure and pathways.
- canonical records: content truth and provenance.

No file should duplicate another file's responsibility merely for convenience.

### 6.3 Builders consume route authority

Hard-coded primary-door arrays and legacy fifth-door references must be removed or derived from the House resolver wherever practical.

Builders and validators should consume the same route authority instead of carrying parallel definitions.

---

## 7. Great Book treatment

The Great Book becomes a first-class public **Path / primary work**, not a sixth Door.

Required outcomes:

1. Register `/great-book/` in public surface authority.
2. Make it permanently discoverable from the House bar as **Book**.
3. Feature it prominently on the homepage in a Library / Read section.
4. Integrate its top-level reader chrome with the House identity layer without damaging the long-form reader.
5. Preserve its chapter navigation, search, TTS, numbering, and continuous-reader behavior.
6. Replace the root `great-book.html` publishing stub with a compatibility redirect to `/great-book/`.
7. Include Great Book in Works/Library relationships and relevant Timeline/Path surfaces without duplicating its content.

A new sixth gateway is explicitly not part of this design.

---

## 8. Homepage redesign

The homepage should become an orientation surface rather than a dense list of everything.

Recommended order:

1. **Project identity / short purpose**
2. **Five Doors** — visually dominant
3. **Library / Ways through** — Great Book, Story, Timeline, Collection, Works
4. **Rooms** — compact subject corridors
5. **Find anything** — Questions, A–Z, Explore, Sources
6. lightweight footer

The homepage should avoid exposing backend branch taxonomy or presenting every specialist page as a peer.

The existing dark editorial identity remains, but the hierarchy becomes calmer and more spatially obvious.

---

## 9. Visual system v2

### 9.1 Direction

Preserve the recognizable dark green / warm gold editorial identity, but redesign it substantially.

The target is:

- darker, quieter background field
- less border noise
- more whitespace
- clearer hierarchy
- fewer pill-shaped elements used as generic decoration
- stronger distinction between navigation, metadata, prose, cards, controls, and evidence notes
- restrained use of green as navigational/living accent
- gold reserved for emphasis, thresholds, important reader affordances, and selected state

The redesign should feel intentional and archival rather than dashboard-heavy.

### 9.2 Shared tokens

`app/site-system.css` becomes the central public design-token and shell layer rather than remaining a minimal partial foundation.

Token categories should include:

- background layers
- text hierarchy
- muted/faint text
- line/border hierarchy
- green/gold accents
- danger/warning/status colors only where semantically necessary
- reading, standard, wide, and tool widths
- spacing scale
- radius scale
- shadow/elevation scale
- font stacks
- text sizes / fluid title sizes
- focus treatment
- header heights
- motion duration/easing

### 9.3 Public shell primitives

New or expanded namespaced primitives should cover responsibilities rather than individual pages, for example:

- `.site-shell`
- `.site-housebar`
- `.site-brand`
- `.site-primary-nav`
- `.site-secondary-nav`
- `.site-breadcrumbs`
- `.site-local-nav`
- `.site-related`
- `.site-footer`
- `.page`
- `.page--reading`
- `.page--standard`
- `.page--wide`
- `.page-header`
- `.page-section`
- `.reader-note`
- `.reader-card`
- `.reader-grid`

Exact class names may change during implementation, but responsibilities must remain separate.

### 9.4 Page character remains possible

The shared system owns:

- background
- typography baseline
- site navigation
- widths/gutters
- heading rhythm
- focus behavior
- responsive shell
- common cards/notes
- footer and related routes

A page-specific stylesheet may still own meaningful content presentation such as:

- Bible comparison panes
- scientific equations
- Timeline tracks
- Great Book chapter reader
- World Map panels
- specialist visualizations

Page-specific CSS must not redefine global body, root tokens, global nav, or generic structural selectors unless explicitly scoped to a specialist shell.

---

## 10. Shell types

The redesign deliberately uses several shells rather than one universal geometry.

### 10.1 Editorial / reading shell

For gateways, Rooms, dossiers, essays, FAQ, sources, philosophy, science readers, history/law/economy, and similar pages.

Receives full House bar, breadcrumb, optional local family nav, reader content, related routes, footer.

### 10.2 Long-form shell

For Great Book, Politics where appropriate, primary text readers, and continuous works.

Receives compact House identity and breadcrumb, then gives vertical space to reading controls and text.

### 10.3 Specialist application shell

For World Map, Bible comparison, Explore, complex Timeline modes, and similar app-like interfaces.

Receives:

- shared tokens
- compact brand/Home escape
- current domain / context indicator
- optional expandable House navigation

Does **not** receive article-width constraints, large editorial headers, or normal page footer geometry if that interferes with the tool.

### 10.4 Utility shell

For TTS and similar focused tools.

Receives a tiny stable House/Home control and shared tokens where safe. Tool controls retain priority.

### 10.5 Redirect shell

Compatibility redirects remain minimal and `noindex`. They do not receive decorative site chrome.

### 10.6 Diagnostic shell

Technical diagnostics remain `noindex`, intentionally separate from public navigation, and may use local functional styling.

---

## 11. Generated public pages

Generated pages must stop looking like a parallel site.

The shared generators for:

- Topics
- Contexts
- Records
- Questions
- question-family indexes
- A–Z

should emit the same design tokens and appropriate House shell as hand-authored content.

Generated pages should derive parent/context navigation from House/branch metadata.

Generated content may remain visually simpler than curated readers, but it must not duplicate its own embedded root theme or primary-door list.

This is a template-family migration, not a page-by-page manual edit.

---

## 12. Legacy/archive deployment hygiene

Historical files belong in the repository but not in the current public presentation layer.

The deployment/build scope must align with the source web audit's stated intent that `archive/` is historical, not public presentation.

Required rule:

> **Preserve archive in git; do not copy legacy archive HTML into the live Pages artifact unless a specific archival-public route is intentionally registered.**

This prevents obsolete Religion, Bible, Map, and other legacy interfaces from surviving as discoverable duplicate HTML.

Compatibility aliases needed by users should exist as explicit redirects outside the legacy archive rather than by publishing the old page itself.

---

## 13. Responsive behavior

### Desktop

- Full House bar visible.
- Five Doors fit as the primary central nav.
- Secondary actions remain visually quieter.
- Breadcrumb/local family row stays compact.

### Tablet

- House bar may wrap only in controlled ways.
- Secondary actions may collapse behind a native disclosure/menu.
- Local family navigation can become horizontally scrollable or compactly wrapped.

### Mobile

- Brand/Home remains always visible.
- A single accessible navigation disclosure reveals the five Doors and secondary actions.
- Breadcrumb is shortened to meaningful hierarchy rather than overflow.
- Local sibling nav becomes horizontal-scroll or disclosure based on family size.
- Content width and typography remain optimized for reading.

The mobile implementation should prefer progressive/native HTML controls over a large JavaScript navigation dependency.

---

## 14. Accessibility and interaction rules

- Visible keyboard focus must be consistent across all shells.
- Navigation must work without JavaScript where practical.
- Active/current navigation state should use `aria-current` when appropriate.
- Color alone must not communicate current state.
- Touch targets should be large enough on mobile.
- Reduced-motion preferences must be respected.
- Existing TTS functionality must survive shell migration.
- Heading structure must remain semantic after visual changes.
- Specialist apps must preserve existing keyboard/control contracts.

---

## 15. Performance and dependency rules

- No new front-end framework is required.
- No external design system is required.
- Prefer shared static CSS and lightweight build-time generation.
- Do not add a JavaScript dependency merely to render global navigation if build-time HTML can do it.
- Preserve static crawlability.
- Keep application-specific vendor/runtime dependencies isolated to those applications.

---

## 16. Error and fallback behavior

Navigation generation must fail safely.

If a durable public surface lacks required registry metadata, validation should fail in CI rather than silently emit an orphan page.

Generated pages with unknown parentage should fall back to:

1. Home
2. Explore
3. the nearest known branch/domain

but the validator should still report the missing mapping so fallback does not become permanent architecture.

A broken optional related link should not prevent page rendering, but canonical parent/Home routes are mandatory.

---

## 17. Validation and tests

The implementation plan must include automated checks for at least the following:

### 17.1 Surface authority

- Exactly five primary Doors in the canonical order.
- Every registered active human-facing surface resolves to an existing or generated route.
- Great Book is registered and discoverable.
- Specialist surfaces declare an appropriate shell type.

### 17.2 Navigation

- Every indexable normal public page exposes a Home path through the House brand.
- Every indexable normal public page has a valid parent/context relation unless explicitly global.
- No duplicate hrefs inside generated nav blocks.
- No stale `/#branch=` routing where `/explore/#branch=` is required.
- Generated pages consume the same primary-door authority.

### 17.3 CSS ownership

- Public editorial pages load the shared site system.
- New/updated reader pages do not redefine unscoped global `:root`, `body`, or generic navigation layout when the shared shell owns them.
- Archive `app/style.css` is not accidentally made the global base for migrated public editorial pages.
- Specialist pages remain exempt only through explicit classification.

### 17.4 Deployment hygiene

- `archive/` HTML does not appear in `_site` unless explicitly whitelisted.
- redirect pages remain `noindex`.
- diagnostics remain `noindex`.
- the old `great-book.html` route redirects to `/great-book/`.

### 17.5 Regression suites

Preserve and run the existing reader, TTS, Bible, Timeline, World Map, House governance, SEO, and navigation validation suites. New shell tests must augment them rather than replacing semantic/content validators.

---

## 18. Migration strategy

The visual/navigation overhaul should be implemented in controlled stages so the public site remains usable throughout.

### Stage 1 — Authority and shell foundation

- strengthen `public-surfaces.json`
- add shell-type/navigation metadata
- centralize public route resolution helpers
- expand shared CSS tokens/primitives
- build shell renderer/projector
- add validation before broad migration

### Stage 2 — Homepage and primary Doors

Migrate:

- Home
- Tim
- Religion
- Philosophy
- Science
- World

These establish the canonical appearance.

### Stage 3 — Great Book and global Paths

Migrate/promote:

- Great Book
- Story
- Timeline
- Collection
- Works
- Rooms

### Stage 4 — Rooms and major specialists

Migrate House chrome and context on:

- Culture
- History
- Politics
- Law
- Economy
- World Systems
- Sources
- North
- Bible
- World Map

Specialists keep their internal layouts.

### Stage 5 — deep reader families

Migrate repeated page families such as:

- Tim deep dossiers
- Science deep readers
- Context/Collection readers
- FAQ/practice/standalone readers
- primary text readers

Prefer family/template changes over isolated one-off edits.

### Stage 6 — generated output

Update generators for Topics, Contexts, Records, Questions, A–Z and related generated pages.

### Stage 7 — deployment cleanup and final CSS consolidation

- stop deploying archival HTML
- replace obsolete compatibility stubs with redirects
- remove duplicated old global CSS rules after migrated surfaces prove stable
- run complete build and validation suite

---

## 19. Success criteria

The redesign is successful when:

1. A visitor can reach Home from every real public surface without hunting for a page-specific link.
2. The five Doors remain stable everywhere.
3. A visitor can tell the parent/domain of any normal page at a glance.
4. Great Book is permanently visible as a major work without becoming a sixth primary Door.
5. Rooms are meaningful middle-level navigation rather than a manually curated miscellaneous link grid.
6. Old pages no longer look like separate websites simply because they were created at different times.
7. Specialist applications still feel purpose-built and are not damaged by article-shell assumptions.
8. Generated pages look and navigate like part of the same House.
9. Legacy archive HTML does not leak into the public artifact as duplicate presentation.
10. Future public pages cannot silently omit Home/context navigation or invent a new primary navigation scheme without failing validation.
11. The site has fewer CSS ownership conflicts and substantially less repeated global styling.
12. The visual language is recognizably Potato of Life but cleaner, quieter, more spacious, and easier to understand.

---

## 20. Explicit non-goals

This project does **not**:

- rewrite canonical content records
- change the five-Door constitution
- replace the archive explorer backend
- convert the site into a SPA
- merge specialist tools into a single generic layout
- redesign World Map internals unrelated to House chrome
- alter theological, scientific, historical, or political content merely for visual consistency
- delete historical material from git
- introduce a new navigation ontology that competes with the existing House model

---

## 21. Final architectural decision

The site will remain a static, crawlable, multi-surface knowledge system. The overhaul will centralize **public orientation**, not centralize every piece of content rendering.

The permanent rule is:

> **The House owns orientation. The page family owns presentation. Canonical records own truth.**

That division gives the site one coherent identity without destroying the specialized forms that make the archive useful.