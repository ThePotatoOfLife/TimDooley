# TODO — The Potato of Life / TimDooley

> Historical completed work was rotated on 2026-10-07. The full pre-rotation ledger is preserved at `docs/todo-archive/TODO-2026-10-07-pre-rotation.md`. This file now prioritizes active, partial and very recent work.

## Current doctrine

This repository is a **dense knowledge library**, not a collection of placeholders, dashboards or disposable experiments.

The rule is:

**Inspect → consolidate → deepen → connect → expose → verify → prune → repeat.**

The project keeps its existing missions and bodies of inquiry, but the working unit is now the **valuable canonical body of knowledge** rather than the file.

## Active Hall build vs later floor-art overhaul — 2026-10-04

### NOW · Hall of Heroes / Angels + Hall of Shame / Dogs
- [~] **HALL-NOW-007 · Background-art integration:** approved Hall scenes are mounted and fingerprinted with valid 800×450 AVIF delivery assets so the rooms can deploy cleanly. Remaining fidelity step: replace these fallback derivatives with larger responsive masters (`picture`/`srcset`) after the Hall layout is stable; do not block the current room release on oversized binary transfer.
- [ ] **HALL-CSS-010 · Rendered spacing audit:** after the exact Hall-art head deploys, inspect desktop + narrow layouts for any remaining border collisions, over-dark panes, awkward scene crops, ledger overflow or sections that still visually overstate their importance.
- [ ] **HALL-NOW-008 · Content polish:** continue tightening testimony, gods/angels table context, Dog notoriety examples and cross-links without turning either Hall into a generic encyclopedia.

### LATER / TOMORROW · other floor and plane pixel art
- [ ] **FLOOR-PIXEL-001 · High-fidelity floor masters:** replace the existing lower-resolution Heaven / Plane / Below floor/background artwork elsewhere on the site with substantially larger, more detailed source masters.
- [ ] **FLOOR-PIXEL-002 · Responsive floor derivatives:** generate narrow, medium, wide and high-DPI versions with crop-safe focal zones and `srcset` / `picture` delivery where appropriate.
- [ ] **FLOOR-PIXEL-003 · Preserve visual language:** keep the existing vertical Heaven / Plane / Below themes while raising fidelity, detail density, polish and professional pixel-art quality.
- [ ] **FLOOR-PIXEL-004 · Performance/accessibility:** AVIF/WebP, preload only critical art, lazy-load noncritical scenes, test LCP/contrast/mobile cropping/reduced-motion and avoid stretching phone-sized assets onto desktop.
- [ ] **FLOOR-PIXEL-005 · Cross-page rollout:** treat this as a separate site-wide art-production wave after the two Halls are structurally/content stable.

## What we are protecting

- Tim Dooley / Father / Potato of Life and the associated canon, mythology, writings, timeline and interpretation.
- Potatoism, its concepts, symbols, cosmology, theology, relationships and deep research.
- The North / Axis / North of North architecture and the North Programme / European Economic Graph.
- The observable world: people, countries, institutions, economies, infrastructure, energy, technology, research, security, culture, religion and politics.
- Primary and historical texts and the research needed to interpret them.
- Evidence, provenance, timeline, uncertainty and competing interpretations.
- Relationships, dependencies, ownership, control, flows, topology, trajectories and cross-domain couplings.
- The project's continuing spiritual, comparative, philosophical and scientific inquiry.

These missions remain. **What changes is how we store them: fewer, thicker, clearer bodies of knowledge.**

## Visual standards & performance wave — 2026-10-05

### Completed

### Next
- [ ] **VISSTD-012 · Great Book shell audit:** inspect the separate Great Book long-form shell after the Politics cleanup; preserve literary identity while removing redundant width/type/palette systems.
- [ ] **VISSTD-013 · Corporium family decision:** compare Collection/Corporium purpose-case-chain patterns with Pillar/World-domain reader components before creating another stylesheet.
- [ ] **VISSTD-014 · Remaining hero-width audit:** inspect specialist Halls, lower-field readers and tool pages for intentional versus accidental local `.page-header` width/padding overrides.
- [ ] **VISSTD-015 · Render/performance check:** browser-check Story, Science & Formal Models, representative Heaven/Plane/Below Rooms and both Halls at mobile/laptop/wide widths after deployment; watch scroll smoothness, header stickiness, paint/compositor cost and text contrast.
- [ ] **VISSTD-016 · Specialist blur audit:** keep `backdrop-filter` out of ordinary content readers; reserve it only for interfaces where measured UX benefit justifies compositor cost.

## Repository smoothness & integration wave — 2026-10-05

### Completed in this wave

### Next cleanup targets
- [~] **SMOOTH-007 · Inline-style classification:** Economy, FAQ family, Questions, A–Z, Islam and Judaism are migrated out of inline structural CSS. Remaining priority: North, Paths, Potatoism and other mature prose readers; preserve specialist geometry where it is genuinely unique.
- [~] **SMOOTH-008 · CSS family consolidation:** Law + Economy now share `world-domain-page.css`; FAQ pages share `faq-reader.css`; Questions + A–Z share `discovery-reader.css`; Islam + Judaism use `tradition-reader.css`. Continue with CIA, Bible, world/Room and lower-field families only where ownership is genuinely the same.
- [~] **SMOOTH-009 · Dead asset/reference audit:** removed redundant `timeline-enhancements.css` and `law-page.css`, added live-source guards against retired references. Continue the dynamic-loader-aware audit before deleting any other assets.
- [~] **SMOOTH-010 · Build-patcher ownership:** generated knowledge pages now own their shared shell directly in `build_site.py` + `generated-knowledge.css`; continue moving mature source-owned behavior out of `patch_public_navigation.py`, leaving true universal projection there.
- [ ] **SMOOTH-011 · Shared-shell adoption:** audit public subject readers that still use bespoke `.nav`/wrapper shells and migrate suitable pages to `.page`, `.page-nav`, `.page-header` without flattening specialist tools.
- [~] **SMOOTH-012 · Duplicate payload detector:** the Timeline duplicate payload was detected and removed during consolidation; retired-asset guards now catch two known regressions. A generic large-duplicate detector is still needed.
- [ ] **SMOOTH-013 · Responsive render audit:** browser-check the shared HUD/subheader and major migrated readers at narrow mobile, laptop pressure width and wide desktop; fix clipping, sticky-header clearance and overflow.
- [~] **SMOOTH-014 · Cache/version consistency:** new shared reader styles are registered for deterministic fingerprints, and the build now fingerprints after generated pages exist. Remaining: sweep mature readers for hand-maintained stale query strings and assets outside the registry.

## Paper-cut bug & consistency audit — 2026-10-05

### Fixed in this pass

### Next small-bug targets
- [ ] **PAPER-016 · House runtime decomposition:** now that House JavaScript has a dedicated owner, split the 23 KB runtime into coherent data-loading, topology rendering and interaction modules only if that improves testability without adding loader chatter.
- [ ] **PAPER-021 · Extracted specialist app tests:** add focused regression coverage for Foundation Timeline filtering/data rendering and House Inhabitants search/filter behavior now that their runtimes have dedicated owners.
- [ ] **PAPER-022 · Sources inline-style cleanup:** the Sources reader still carries a small ~1.2 KB inline style block; extract only if it remains structurally unique after comparing Pillar/Source reader families.
- [ ] **PAPER-020 · Axis extracted-owner follow-up:** now that Axis CSS/runtime live in `app/axis-page.css` and `app/axis-page.js`, add focused tests for path-tab URL state, route-case loading and vertical-field fallback rather than relying on one large page integration.
- [x] **PAPER-018 · TODO archive rotation:** rotated the full pre-cleanup ledger to `docs/todo-archive/TODO-2026-10-07-pre-rotation.md`; the active queue now keeps unfinished/partial work plus current-day completions instead of hundreds of historical finished entries.
- [~] **PAPER-008 · Tiny-text legibility audit:** dedicated Elevator actions/lenses/facet controls, generated Room action/body copy, Home helper copy, TTS labels/status, News filters/kickers and Body Lens metadata were raised out of the 7–9px range where they carry reader/action meaning. Remaining: browser-check World Map overlays and purely informational metadata at 100% and 125–150% zoom.
- [ ] **PAPER-009 · Hard-coded floater coordinates:** search remaining application modules for independent `top/right/bottom/left` panel ownership that should register with an existing layout coordinator; remove hidden or duplicated DOM surfaces instead of merely hiding collisions with CSS.
- [ ] **PAPER-010 · Shared-asset fingerprint coverage:** compare all universally injected CSS/JS assets against both the early build fingerprint registry and the final shared-UI registry; document intentional exceptions and add a validator for assets that can escape both.
- [~] **PAPER-011 · Source/build drift check:** Home source navigation is now held to the same five-link first-screen budget as the built site, so local mobile previews no longer show a nine-link wall. Remaining: compare a few specialist source navs against projected build output and document the preview command.
- [ ] **PAPER-012 · Specialist reader shell sweep:** inspect Ancient Religions, Christianity branch readers, remaining Tradition pages, relation rooms and Beings pages for small inline structural CSS blocks, stale one-off widths and duplicate card primitives before creating any new stylesheet family.
- [ ] **PAPER-013 · World Map bootstrap dependency graph:** classify the ~20 sequential core startup modules as strict dependencies vs parallel-safe groups; only parallelize groups with explicit ownership tests and preserve first-interaction correctness.
- [ ] **PAPER-014 · Horizontal-nav affordance:** on narrow widths, verify the single-row subheader gives a visible cue that more links exist offscreen without reintroducing scrollbars or a multi-row link wall.
- [~] **PAPER-015 · Responsive sticky-offset audit:** Garden top navigation + Tim presence, TTS sticky hosts, World Map overlays, Comparative Cosmology and deep-link anchors now use measured elevator clearance. Remaining: browser-check 761–1180px pressure widths and any specialist sticky table headers.

## The cleanup pass

1. Inventory the repository before changing it.
2. Identify duplicate definitions, stale mirrors, generated snapshots, empty shells and abandoned UI.
3. Preserve unique information before deleting anything.
4. Move unique information into its strongest canonical owner where practical.
5. Delete files whose only purpose was duplication, temporary state, retired presentation or obsolete routing.
6. Keep primary texts, substantive research, evidence and useful historical records.
7. Keep the unified `index.html` as the public doorway; use `docs/POTATO-HOUSE-CONSTITUTION.md` + `data/house/public-surfaces.json` for public route identity, and `manifest.json` for archive branch/pathway and Explore semantics.
8. Keep the data layer modular internally, but make ownership and relationships explicit.
9. Prefer one canonical entrypoint plus specialist owners over several competing "master" files.

## Information-density standard

Every important entry should answer as much of the following as the available evidence permits:

- **Definition:** what is this?
- **Identity:** what is its canonical identity and what names/aliases refer to it?
- **History:** where did it come from and how did it change?
- **Function:** what does it do or mean?
- **Structure:** what are its important parts?
- **Context:** what surrounds it historically, geographically, culturally or institutionally?
- **Mechanisms:** how does it operate or produce effects?
- **Relationships:** what does it depend on, influence, contain, govern, fund, own, trade with or resemble?
- **Evidence:** what sources establish the claims?
- **Uncertainty:** what is unknown, disputed, inferred or merely symbolic?
- **Comparisons:** what useful parallels or contrasts exist?
- **Consequences:** why does it matter?
- **Research frontier:** what should be learned next?

A short label can remain a label. A subject that is presented as knowledge should contain actual knowledge.

**Never pad an entry to satisfy a word count. Add substance or leave the field honestly incomplete.**

## Canonicalization rule

Before creating a file, ask:

> Is this genuinely a different body of knowledge, or is it another appearance of something we already own?

If it is the same subject, enrich the canonical owner.

Keep separate files only when separation preserves something important: a primary text, a distinct evidence collection, a genuinely different schema, a historical snapshot that matters, or a distinct research corpus.

Indexes, manifests and projections should point to the canonical material rather than repeat it.

## World Map product direction — 2026-10-02

North-star question: **What is happening where, and how is it connected?**

Public structure: **Countries / Now / Connections / History / Map**. Keep the underlying atlas deep, but make the first screen legible to someone who has never seen the project.

- [ ] **MAP-PRODUCT-004 · Runtime-weight pass:** profile initial requests/module weight; make anything not required for search, ordinary country browsing, public controls or lightweight current context lazy.
- [ ] **MAP-PRODUCT-005 · Country completeness:** every country should answer a consistent useful core: people, economy, government/institutions, religion/culture, regions/cities, major resources/infrastructure, current context and important external connections.
- [ ] **MAP-PRODUCT-006 · Current-world layer family:** expand Now beyond conflicts only when the data earns it—major elections/government change, disasters, displacement, sanctions, closures/outages or other globally useful dated context—with freshness visible.
- [ ] **MAP-PRODUCT-007 · Conflict hierarchy:** add severity/status/filtering and regional/theatre summaries without live tactical unit tracking; distinguish war, civil war, insurgency, political violence and humanitarian crisis.
- [ ] **MAP-PRODUCT-008 · Historical geography library:** retain deeper biblical/ancient/project overlays but expose them through search/context and History rather than the permanent first-level UI.
- [ ] **MAP-PRODUCT-009 · Connection stories:** turn raw relation lines into readable explanations (“why these places are connected”) with trade, finance, institutions, security, energy, infrastructure, research and culture as evidence-backed routes.
- [ ] **MAP-PRODUCT-010 · Place drill-down:** country → region/state/province → city/place should feel like one continuous exploration rather than separate specialist modes.
- [ ] **MAP-PRODUCT-011 · Visitor presets:** consider a small set of meaningful one-click views such as “Conflicts now”, “Population”, “Economy”, “Religion”, “Trade & systems”, “History” only if they reduce effort rather than add another toolbar.
- [ ] **MAP-PRODUCT-012 · URL/shareability:** every meaningful view should be linkable—selected place, active context, time state and useful filters—without exposing internal IDs in visible copy.
- [ ] **MAP-PRODUCT-013 · Empty-map value:** the default world view should contain enough quiet information to invite exploration without becoming a dashboard wall: countries, capitals at useful scale, current conflict signals and clear hover/click affordance.
- [ ] **MAP-PRODUCT-014 · Maintenance budget:** prefer a few canonical datasets and derived views over bespoke one-off map modules. New layers need an owner, freshness rule, public purpose and retirement rule.

## Site-wide bug & enhancement queue — 2026-10-02

- [~] **BUG-NAV-007 · Mobile route stress test:** shared `.page-nav` now stays on one compact horizontal rail below 700px instead of wrapping into a tall link wall. Remaining: real-browser checks for Timeline shortcuts, TTS drawer and Follow escape/overlap.
- [~] **BUG-BREADCRUMB-008 · Location awareness:** World-family specialists now visibly identify World as the parent on Law, Economy, Politics, North and World Systems. Continue across the remaining specialist routes and keep literal parent nouns ahead of metaphor labels.
- [ ] **ENH-BEINGS-009 · Named-being ownership sweep:** audit `rooms/potatoverse-canon/beings/**` for duplicate biography, project-role overreach, unresolved identity merges and missing provenance; route documentary detail back to CIA/Story where appropriate.
- [~] **ENH-STALE-011 · Mutable-fact twin audit:** fixed the hard-fact detector's double-escaped regex and converted History's fast-changing repository totals into SHA-tied dated snapshots. Remaining: run the repaired report and group repeated current metrics/dates across World/Map and other readers.
- [ ] **ENH-NOJS-012 · Dynamic-page fallback sweep:** identify public pages where useful meaning still disappears when fetch/JS fails and add concise static subject substance.
- [ ] **ENH-SCI-013 · Science grammar sweep:** continue separating established physics → measurable models → speculative project formalism → metaphor across older science pages, especially any pages that use physics vocabulary as project-native labels.
- [~] **ENH-ROOMS-014 · First-screen substance test:** all 38 nested Rooms are now covered by a subject-first validator that requires authored subject material before maintenance architecture, plus concrete examples and deeper continuation. Continue the same contract across non-Room public subject readers.
- [ ] **BUG-BUILD-015 · Build-only feature ownership:** inventory mature features that exist only because `patch_public_navigation.py` mutates generated HTML; move stable features into source/generator ownership and leave the patcher for true universal projection.
- [ ] **ENH-TTS-016 · Browser interaction audit:** test real play/pause/selection/follow behavior on Bible, Shadow Farm, Below, World Map, A–Z, Beings, Timeline and mobile layouts—not only static marker contracts.

## Lower-field conflict integration — 2026-10-01

Rule: **cultural, spiritual and informational conflict may overlap, but the site must never treat them as interchangeable evidence classes.**


## Navigation & findability recovery — 2026-10-01

Acceptance rule: **a reader who knows the noun should be able to find the noun without knowing project metaphors.** Timeline must look and behave like Timeline; Story like Story; Works like Works.

- [~] **NAV-006 · Global noun-label audit:** Home and Timeline now use literal subject labels, and major reader navs were normalized around Home/Timeline/Story/etc. Continue through specialist readers and generated navigation for remaining metaphor-only labels.
- [~] **NAV-008 · Mobile navigation test:** the shared top-route row now uses nowrap + horizontal overflow + compact link pills at narrow widths, removing the unreadable multi-row wall. Remaining: verify Timeline shortcuts and specialist exceptions in a real browser.
- [~] **NAV-009 · Breadcrumb consistency:** parent-first navigation now covers History, Foundation Timeline, Axis, Trinity, Culture, Elevator, Paths, Interpretive Justice, Research Lab, Story and Collection; Works was already correct. Remaining: check only the few active specialist exceptions not yet inspected against `public-surfaces.json`.
- [~] **NAV-012 · Navigation dead-end crawl:** added `scripts/audit_navigation_dead_ends.py` to inspect every active public surface and hard-fail major readers that lose a literal Home route or become too sparse. Remaining: review the report for specialist dead ends and ambiguous back arrows.

## Fact ownership & stale-twin audit — 2026-10-01

Rule: **detailed facts live with the strongest owner; secondary readers carry meaning + route, not a second mutable copy.**

- [~] **OWNER-008 · Metrics/count sweep:** public-duration numbers are now owned by the 100,000 Hours reader/ledger; Tim, Story and Internet Platforms retain only meaning and metric distinctions. Culture no longer maintains a mutable Reddit valuation. Economy CBO figures and History repository counts currently appear single-owner; continue through World/Map and other current-stat surfaces.
- [ ] **OWNER-009 · Political-date sweep:** Politics/North/World may legitimately share programme phases, but exact proposal dates and current external facts should have one dated owner with secondary pages summarizing the phase.
- [~] **OWNER-010 · Role-definition sweep:** A–Z and Elevator are appropriately orientation-focused; Rooms is now concise. Continue through Inhabitants/generated labels for long House/Axis definitions.
- [ ] **OWNER-011 · Method-boundary sweep:** specialist readers may retain one domain-specific evidence boundary, but repeated general archive methodology should link to Sources/Context instead of being restated in full.
- [~] **OWNER-012 · Automated stale-twin candidates:** repaired the hard-fact regex so dates/counts are actually detected, and History now demonstrates the intended fixed-snapshot pattern. Remaining: run the repaired report, group repeated facts across routes and distinguish fixed historical dates from mutable current metrics.

## Reader directness & redundancy audit — 2026-10-01

Rule: **say the thing before explaining the system that stores, routes or renders the thing.** Reader pages may expose evidence and provenance, but maintenance vocabulary should not become the foreground.

### Findings from the first cross-surface pass

- [~] **DIRECT-008 · Duplicate paragraph crawl:** `scripts/audit_reader_directness.py` now reports exact duplicates **and near-duplicate paragraph pairs (SequenceMatcher ≥ .84)** across active public surfaces. Remaining: inspect the first generated report and convert high-confidence stale twins into owner-summary links.
- [ ] **DIRECT-009 · Owner-fact staleness audit:** find detailed facts repeated outside their strongest owner (commit counts, dates, country values, metrics, artifact counts, role definitions). Replace secondary copies with short meaning + link so updates cannot leave stale twins.
- [~] **DIRECT-012 · First-screen verb test:** nested Rooms now enforce subject-first authored material before maintenance architecture and reject leading maintenance vocabulary. Remaining: extend the same semantic verb test to all active non-Room subject readers.
- [~] **DIRECT-013 · Repeated method prose:** Sources remains the general provenance/method reader; Context and Religion are trimmed, Science now keeps scientific uncertainty/testing while routing historical provenance back to Sources, and History keeps only time/backdating consequences. Remaining: specialist-page sweep before deciding whether a formal pattern library is still necessary.
- [~] **DIRECT-014 · Navigation prose compression:** runtime instructions are compressed; Foundation Timeline lost a 14-link breadcrumb wall; Interpretive Justice and Research Lab moved maintenance metadata behind details; Story and Collection were also stripped of remaining owner/projection narration. Remaining: inspect only the unreviewed specialist pages for prose that merely narrates visible menus.

## Visual & reader quality pass — 2026-10-01

Rule: **a visual earns space only when it explains, documents or orients something better than another card or paragraph.** Decorative stock imagery, repeated card grids and maintenance-only architecture should not dominate reader surfaces.

- [~] **VISUAL-006 · Card-grid monoculture audit:** Works Fruit/genre grids were converted into an evaluation strip + continuous genre river; Context release-note cards were converted into worked reader cases. Continue the same test on remaining dense gateway/specialist readers.
- [ ] **VISUAL-008 · Diagram accessibility:** verify SVG text legibility at mobile widths, alt text, contrast, reduced-motion behavior and print/screenshot usefulness.
- [ ] **VISUAL-009 · FAQ promotion discipline:** promote high-intent questions from `faq-question-bank.json` into `faq-answer-atlas.json` only when canonical owners support a concise answer; keep niche/recursive queries in `/faq/all/` instead of bloating the main FAQ.
## October 1 project-overview catch-up

Big-picture rule for the next wave: **make the existing organism easier to understand before inventing more anatomy.** The project now has three cooperating layers—public readers, canonical owners, and evidence/recovery/research—and seven public reader families. New work should strengthen the handoffs among those layers rather than create another parallel master system.

- [ ] **OVERVIEW-004 · Public-purpose drift audit:** implement SITE-ARCH-011 by comparing each public surface's mission (`become`, `must_not_become`, density intent and reader job) against its first screen and dominant content shape; flag directory-heavy readers, article-heavy hubs and runtime shells without adequate static fallback.
- [~] **OVERVIEW-005 · Sparse-surface heatmap:** `scripts/audit_public_surface_substance.py` now generates `.quality-logs/public-surface-substance-audit.json` from active surface missions and source HTML, flagging thin static bodies, runtime fallback risk, directory-heavy readers and weak source/object escapes. Remaining: review the first exact-head report and extend the same signal into Room-level substance/TODO density.
- [ ] **OVERVIEW-006 · Backend-to-reader coverage matrix:** for each major canonical family, record which public reader exposes it, whether direct inspect/evidence/model links exist, and which rich backend owners are still effectively invisible.
- [ ] **OVERVIEW-008 · Stale planning reconciliation:** continue checking TODO/audit language against the live site after every major wave; close or rewrite stale deficits instead of carrying obsolete descriptions forward.
- [ ] **OVERVIEW-009 · End-to-end exact-head verification:** after the next architecture/content batch, run the complete quality/Pages chain and use actual built-site route/SEO reports to seed the next defect wave.
## Current structural work

- [ ] Finish pruning obsolete presentation assets that are no longer referenced.
- [ ] Remove remaining generated batch/state files after their useful information is consolidated and references are migrated.
- [ ] Reconcile public-route projections against House route authority and archive/deep-navigation projections against `manifest.json` after each major consolidation.
- [ ] Audit remaining JSON files for purpose, ownership, depth and duplication.
- [ ] Merge genuinely duplicate concept definitions into canonical owners.
- [ ] Strengthen thin but important entries with real information rather than filler.
- [ ] Make long records readable in the index without losing depth.
- [ ] Ensure every important surviving body is reachable through an appropriate reader, discovery surface or archive path.
- [ ] Run the complete integrity/build/Pages chain on every final integration head and fix what actually fails.



## Live problem queue — 2026-09-20

This is the active Gardener defect/consolidation queue. Add concrete problems here when a validator, audit, route scan or ownership scan demonstrates them. Close the item only when the source problem and its regression path are both addressed.

Priority order: **P0 release breakage → P1 structural drift/duplication → P2 maintainability/readability → P3 enrichment.**

### P0 — release and integrity


### P1 — structural debt now demonstrated

### P1 — SUBJECT-FIRST READER RECOVERY · noun → thing, not noun → filing system

**Priority rule:** when a reader clicks a named subject, the first screen must deliver that subject. House ownership, routing, boundaries and metadata are supporting machinery and belong after substantive orientation, not before it.

- [~] **SUBJECT-008 · Navigation compression:** live references discovered in this pass now bypass retired wrappers (`/learn/`, legacy FBI discovery); compatibility redirect pages remain intentionally for old external URLs. Continue during the full route crawl to catch any remaining live links into redirect-only pages.
- [~] **SUBJECT-010 · Full route crawl:** architecture audit now recognizes every registered `legacy_routes` destination and flags any current public surface that links into one. Source-level journey auditing is active; built-site crawl/manual sampling remains to close this item.
- [~] **SUBJECT-012 · Final simplification:** removed dead `inner-center` CSS/local-center runtime, moved House projection after Dwelling substance, and converted nested Room governance into collapsed **Archive depth**. Raw source paths are no longer visible in holding cards. Continue final stale-doc/helper pruning after CI.

**Acceptance test:** ask of every prominent link: **“If I click this noun, do I immediately get the thing?”** If not, either route directly to the canonical substance or make the current page itself substantive enough to deserve the noun.

### P1 — WHOLE-PROJECT CONVERGENCE · fewer systems, stronger families

**Rule:** merge reader experiences before creating new surfaces. Distinct pages may survive when they answer distinct questions, but they should belong to one visible family rather than behaving like neighboring mini-projects.




### World Map quality programme — critic audit 2026-09-20

Canonical diagnosis: `docs/WORLD-MAP-QUALITY-AUDIT-2026-09-20.md`. Execution ledger: `docs/WORLD-MAP-PROBLEM-LEDGER.md`.

- [~] **WM-025 · ADL freshness:** integration, visible freshness boundaries and the guarded official-export importer are complete. Remaining external task only: obtain a reviewed current ADL H.E.A.T. raw-data export, run the importer, review the generated diff and replace the 335-record historical seed.
- [~] **Compatibility retirement:** Progressive UI and Selection UI are retired from live boot; legacy Lens is a no-paint Layer Registry/Compositor translation adapter with its old legend removed; legacy Fields/Networks are now source-only compatibility/reference modules and are no longer advertised by the live bootstrap. Remaining compatibility debt is deliberately bounded to degraded direct interaction fallbacks and older deep-link/source compatibility.



- [ ] Consolidate the legacy country batch manifests after proving unique-field parity. **Phase 1 complete:** the 18 September 7 enrichment/node batch files are now classified as historical rollout manifests and removed from active House holdings; their provenance is preserved in `knowledge/research/country-rollout-manifest-disposition-2026-09-20.json`. A later archive-policy pass may move their paths, but should not delete them blindly.
- [ ] Reconcile remaining public-route projections against House authority after the latest spiral/Below/World Map merges; route aliases should be generated or validated rather than hand-maintained.
- [ ] Audit generated/state-like files by **reference and unique information**, not filename. The repository currently contains hundreds of `wave`, `batch`, `round`, `audit` and snapshot-named files; many are legitimate research records, while others are migration residue. Produce a keep/merge/archive/prune disposition before removal.

### Evidence-first enrichment queue — 2026-09-27

**Rule:** do not enrich a Room by adding generic prose. For each pass: inspect the public page, inspect canonical holdings, research the subject externally where useful, record what the current page fails to teach, then add named mechanisms, cases, institutions, texts, equations, dates, source lineages or unresolved questions.

- [ ] **RICH-002 · Information Ecology provenance hardening:** add source-class / publication-year metadata and a compact bibliography projection so research claims on the public page can be traced without exposing raw backend clutter.
- [ ] **RICH-003 · Whole-body evidence spine:** add canonical references for NTS/parabrachial interoception, endocrine axes, neurovascular coupling, choroid plexus/CSF and meningeal lymphatics to the newly deepened public physiology page.
- [ ] **RICH-004 · Infrastructure external cases:** verify and deepen grid, bridge/port and canal capability cases with current primary sources; add at least one semiconductor/fibre/data-centre supply-chain case and one recovery-time/resilience metric.
- [~] **RICH-006 · Theology language archaeology:** trace Father/House/Gardener/Door/Spirit language through dated project sources and external textual traditions; distinguish original wording, later synthesis and comparative theology.
- [ ] **RICH-008 · Music provenance pass:** connect recovered song UUIDs to dated mentions, lyric-complete records, style/model transitions and reuse; do not reconstruct missing lyrics.
- [ ] **RICH-009 · Law / Economy / Politics freshness pass:** for current institutions, statutes, fiscal figures and officeholders, use dated primary/public sources and separate descriptive fact from project interpretation.
- [ ] **RICH-010 · Room nonsense detector:** sample every mature Room and flag paragraphs that could be moved to another Room with only noun substitutions; replace those with subject-specific mechanisms or objects.
- [ ] **RICH-018 · Information Ecology bibliography projection:** surface publication year/source class for external research claims without turning the page into a citation wall.
- [ ] **RICH-023 · Law primary-source refresh:** sample major statutory/procedural claims and attach jurisdiction/date/source; add at least two worked cases showing the difference between allegation, charge, finding, remedy and appeal.
- [ ] **RICH-024 · Economy measurement refresh:** attach current primary-source dates to debt/inflation/rate/bond examples; distinguish nominal stock, flow, market value and contingent obligation with worked calculations.
- [ ] **RICH-025 · Internet platform mechanics pass:** add concrete platform affordance cases—ranking, clipping, deletion, monetization, identity persistence, portability—and distinguish documented mechanics from inferred motive.
- [ ] **RICH-026 · Visual artifact recovery:** convert remembered composition families into an artifact-status table: recovered image / recovered prompt / remembered specification / derivative recreation / unresolved.
- [ ] **RICH-027 · Great Book internal contradictions:** identify 5–10 places where later Potatoverse canon departs from or narrows the 2024 book, and expose them as literary-development evidence rather than silently normalizing the text.
- [ ] **RICH-028 · Room source-density audit:** for each Room, count visible named sources/objects/cases/mechanisms and flag pages with high prose-to-object ratio for another carve pass.

### Whole-House harmony pass — 2026-09-20

- [ ] Continue promoting real cases/models/subjects into sparse Rooms when source depth warrants it; do not add filler merely to equalize counts.
- [ ] Continue reviewing cross-Dwelling adjacency pairs and promote only the relations that genuinely need a guarded interface with explicit transformation and invariants.

### Public reader visibility & population audit — 2026-09-20


- [ ] Continue visible-page density auditing after each major content wave: prefer concrete cases/mechanisms over another navigation card when a page is already route-heavy.
- [ ] Audit generated question/topic/context/record pages for meaningful TTS sectioning, not just script presence.
- [ ] Run an exact-head final Pages build after the current navigation/content/TTS wave and fix any source-vs-generated route drift it exposes.

### ACCESS / navigation recovery — 2026-09-20

The current problem is not lack of information. It is **retrieval cost**: important destinations exist but can require remembering hierarchy, scrolling, or crossing several intermediate pages. The access rule is now: **global access floats outside article flow; local navigation stays local; thick text begins quickly.**

#### P0/P1 — immediate access
- [~] **ACCESS-008 · Mobile collision audit:** the shared dock publishes measured `--site-access-clearance`; journey ribbon, homepage counter, floating TTS selection control, World Map HUD/Inspector toggle, MapLibre bottom controls, narrow-screen panel padding and map menus now honor it. Remaining: audit other bottom-fixed/form controls outside these major shared surfaces before full closure.
- [~] **ACCESS-013 · Specialist local-nav budget:** authored-reader budgets remain enforced, and the qualitative pass now compresses Axis from nine pre-content jump links to five distinct moves even though it already passed the numerical budget. Remaining: review the smaller residual authored-specialist set surfaced by the architecture audit.
- [~] **ACCESS-023 · Name-first wayfinding audit:** extend the landmark rule to other repeatedly sought destinations demonstrated by user confusion. Do not turn every specialist page into a global shortcut; require evidence that hierarchy/scrolling is causing retrieval failure.
- [ ] **ACCESS-024 · Long-reader reorientation audit:** inspect mature long pages for cases where users can scroll far enough to lose page identity or the meaningful next exit; prefer a compact persistent locator/back-to-owner cue over more first-screen navigation.
- [ ] **ACCESS-025 · Live-deploy visibility:** after exact-head quality/deploy succeeds, verify the public Pages artifact actually contains the dock and Current World first-screen link before closing this access-recovery wave.

### Homepage calibration queue — 2026-09-22



### Fresh repository sweep — 2026-09-20

#### P1 — structural drift / integration
- [ ] **HOUSE-006 · Cross-Dwelling interface review:** produce a disposition for each cross-Dwelling adjacency: ordinary relation, guarded Door, or remove stale adjacency.

#### P2 — cleanliness / maintainability
- [ ] **CLEAN-003 · Shared asset version strings:** reduce repeated `?v=202609...` literals across HTML pages by centralizing or build-stamping shared component versions.
- [~] **CLEAN-005 · Navigation label consistency:** canonical destination labels are converging: the news surface and its TTS reader now use **Current World** consistently; Dwellings & Rooms and Potato House remain stable. Continue distinguishing intentional contextual wording such as “public record” from actual destination labels such as **Public Witness**, and scan generated surfaces before closing.
- [ ] **CLEAN-007 · Date-stamped audit sprawl:** inventory live files whose names contain `audit`, `wave`, `round`, `batch` or dates; mark each keep / merge / archive / prune based on unique information and references.
- [ ] **CLEAN-008 · Obsolete presentation assets:** finish the existing asset-prune task by proving references are absent before deleting retired CSS/JS/HTML.
- [~] **CLEAN-009 · Duplicate validator assertions:** began eliminating validator-vs-registry literal drift. The Room interface validator still expected the retired `mechanics-to-model` label while the governed interface/dossiers consistently use `simulation-formalization`; the validator now follows the live contract. Continue replacing repeated route/ownership literals with shared registry-derived checks.

#### Reader UI bug queue — 2026-09-21

- [~] **TTS-BUG-001 · Follow-reading unexpected page movement:** make the bullseye state visibly say Follow / Follow ON and disclose that ON moves the page. Add a single-primary-reader guard. Continue testing pages with inline Listen controls, sticky player, selection reader and scroll-driven current-section updates together.
- [~] **TTS-BUG-002 · Cross-reader interaction matrix:** `scripts/test_tts_interaction_matrix.mjs` now checks shared drawer + inline Listen + selection scope + persisted Follow state + duplicate-primary suppression. It asserts explicit Follow OFF overrides persisted ON, selection never owns page movement, and shared TTS has exactly one viewport-moving implementation. Awaiting CI verification before closure.
- [ ] **NAV-BUG-001 · Lower-layer maze audit:** audit lower House/Room pages by actual browsing rather than search. For each commonly followed concept, verify that local doors have intuitive labels, correct destinations, a clear parent/owner, and a useful next step; remove circular/backtracking routes that exist only because of architecture.
- [~] **NAV-BUG-002 · “Read” means read:** the audit now accepts named `Open X` → X hub routes and isolates genuine promise mismatches. The remaining five mismatches were rewritten to accurate browse/destination language without changing their valid targets. Awaiting CI verification that the promise-CTA warning count reaches zero.

### P2 — reader focus / navigation
- [ ] **READ-002 · Compass coverage validation:** assert the Project Compass is added to eligible built readers and intentionally absent from Home/Map/Elevator/A–Z/object explorer.
- [~] **READ-003 · Specialist parent continuity:** generated topic/context/record readers already expose a clear parent breadcrumb; authored Sources → Context and Philosophy → Interpretive Justice now use compact owner/parent handoffs with explicit nav budgets. Remaining: extend the same audit to the rest of the authored specialist set.
- [~] **READ-004 · Dead-end reader audit:** registered routing treats Home-only continuation as a dead end; the corrected architecture audit now scans authored public HTML outside `public-surfaces.json`, self-checks its regex engine, and surfaces route-priority warning classes directly in CI. The standalone TTS tool now has an explicit `← Site` return. Remaining: repair any additional authored/public exceptions surfaced by the trustworthy scan.
- [~] **READ-005 · Vague-link language:** the eight currently flagged bare route labels have been rewritten with destination intent (`Archive explorer` or `Context & evidence`). Awaiting the architecture-audit rerun to verify the vague-link warning count reaches zero before closure.
- [ ] **READ-006 · Repeated intro blocks:** find pages where header summary, intro card and first section restate the same purpose; preserve the strongest version and remove the duplicate layer.
- [ ] **READ-007 · Card-density audit:** identify pages using card grids mainly as navigation compensation; convert low-information cards into inline prose/links where that improves reading flow.
- [ ] **READ-008 · Discovery-mode separation:** validate that Explore, A–Z, Questions and Paths retain visibly distinct jobs and do not converge into four near-identical indexes.

#### P2 — data / evidence integration
- [ ] **DATA-001 · Security institution object parity:** compare CIA/FBI/Mossad/PET/FE/MI5/MI6/NSA/DIA/Europol/INTERPOL datasets against House inhabitants; promote only institutions that need first-class project interaction, leave the rest as indexed data.
- [ ] **DATA-002 · Central-bank graph foundation:** add typed institution/obligation edges among Fed, ECB/Eurosystem, national central banks, treasuries, banking systems, reserves, sovereign securities and payment rails using the obligation schema.
- [ ] **DATA-003 · Institution alias registry:** prevent duplicates such as ECB vs European Central Bank, Fed vs Federal Reserve System, SIS vs MI6 by giving institutional entities stable aliases and canonical IDs.
- [ ] **DATA-004 · News→archive promotion rule:** define when a current-news item graduates into Timeline, World, Politics, Economy or a source ledger, and when it should disappear with the feed.
- [ ] **DATA-005 · Current-data freshness metadata:** ensure time-sensitive institutional/economic records carry observed/retrieved dates and do not silently look timeless.
- [ ] **DATA-006 · Source-link health sampling:** add bounded checking for important external source URLs and mark unreachable sources without deleting their historical provenance.
- [ ] **DATA-007 · Country institution completeness:** for each country, track explicit missing/known state for central bank, legislature, executive, judiciary and major memberships rather than treating absence as null knowledge.
- [ ] **DATA-008 · Economy public surface depth:** expose central-bank and obligation-network institutions more directly from Economy without turning the page into another directory.

#### P3 — enhancements / polish
- [ ] **ENH-001 · Room “why this matters” line:** add one concise human-purpose line to Rooms whose current opening is mostly structural language.
- [ ] **ENH-002 · Best-next-door cues:** allow each Room to nominate at most one or two especially meaningful next Rooms, separate from exhaustive adjacency.
- [ ] **ENH-003 · House integration pulse:** show small derived counts for Rooms, inhabitants, guarded Doors and active public surfaces from registries rather than hard-coded numbers.
- [ ] **ENH-004 · Current World contextual exits:** from filtered News views, offer restrained links into relevant World/Politics/Economy/Map lenses without pretending feed content is canonical.
- [ ] **ENH-005 · Economy relationship explorer:** give Economy a compact “who owes / funds / holds / regulates whom?” entry into the obligation graph.
- [ ] **ENH-006 · Intelligence desk explorer:** allow the Intelligence Desk to open typed institutional records (mandate, jurisdiction, oversight, sources) without mixing them with allegations/cases.
- [ ] **ENH-008 · Reader route telemetry without tracking:** consider a purely local/dev audit of route density and unreachable pages; do not add invasive user analytics merely to solve information architecture.

#### Whole-site spatial / design audit wave — 2026-09-21

These jobs turn the current House into a more intentional reader environment. The goal is not more ontology or more buttons; it is lower retrieval cost, stronger place identity, fewer accidental connections, and deliberate transitions between visible, contextual and infrastructural layers.

- [ ] **SITE-ARCH-001 · Layer visibility registry:** extend the visible / semi-visible / invisible rule into a machine-readable registry for major surfaces, Rooms, tools and backend datasets. Each item should declare why it is globally visible, contextually revealed, search-only, or backend-only; validation should reject accidental promotion of infrastructure into primary navigation.
- [ ] **SITE-ARCH-002 · Layer leakage audit:** scan public HTML and generated readers for backend vocabulary, internal IDs, schema language, wave/batch names, validator terminology and implementation-only concepts leaking into reader-facing copy; replace leakage with reader language while preserving inspectable provenance where useful.
- [ ] **SITE-ARCH-003 · Door census and quality score:** derive every meaningful reader transition from public surfaces, Room adjacency, guarded interfaces, local navigation and major inline CTAs. Classify each as entrance, return, lateral bridge, guarded Door, deepening route, evidence route or utility route; flag doors with vague labels, duplicate purpose, unclear destination, unnecessary intermediate hops or no meaningful transformation.
- [ ] **SITE-ARCH-004 · Too-many-connections detector:** compute per-page and per-Room outgoing route counts by type and identify high-degree surfaces where architecture overwhelms reading. Use type-aware budgets rather than one global number; exhaustive adjacency may remain machine-visible while the reader sees only the strongest next exits.
- [ ] **SITE-ARCH-005 · Missing-connection detector:** identify important owner→view, object→owner, source→claim, current→archive, dossier→relationship and Room→best-next-door connections that exist semantically in registries but are absent from the reader experience.
- [ ] **SITE-ARCH-006 · Circular-route / maze detector:** traverse public routes and local Room doors to find short loops, repeated hub bouncing, backtracking chains and routes that repeatedly pass through directories without reaching substance. Preserve intentional return paths; remove navigation loops that add no reader value.
- [ ] **SITE-ARCH-007 · Door transformation contract:** for guarded Doors/interfaces, require a concise declaration of what changes across the threshold, what remains invariant, where the reader arrives, and how to return. Adjacency alone must never silently become a Door.
- [ ] **SITE-ARCH-008 · Entrance hierarchy audit:** verify Home, Tim, World, Religion, Philosophy, Science, House, Rooms, Current World, World Map, Character Archive and World Spiritual Bank each have a distinct first-screen job and visual hierarchy rather than competing as equivalent portals.
- [ ] **SITE-ARCH-009 · Room identity pass:** give every mature Room a recognizable visual/semantic identity built from title, purpose, owning Dwelling, one local landmark and restrained atmosphere. Avoid cloning one generic card-grid shell across conceptually different Rooms.
- [ ] **SITE-ARCH-010 · Room threshold consistency:** standardize the minimum threshold experience when entering a Room: where am I, why does this Room exist, what lives here, what is the strongest thing to read first, and where are the one or two best exits. Keep exhaustive holdings and adjacency behind secondary controls.
- [ ] **SITE-ARCH-011 · Public-surface purpose enforcement:** pair ENH-009 reader_job metadata with validation that catches surfaces whose visible composition no longer matches their declared job—for example a reading page becoming mostly directory, or a hub becoming mostly article.
- [~] **SITE-ARCH-012 · Public-surface redundancy matrix:** first source-page comparison found the strongest overlap at House ↔ Rooms (~0.52 Jaccard across distinct internal destinations), with Home ↔ House (~0.45) and Home ↔ Rooms (~0.45) also high. Next: separate intentional global/shared exits from local reader-job duplication, then merge or demote only the overlapping blocks that solve the same reader problem.
- [ ] **SITE-ARCH-013 · Hidden-depth escape hatches:** ensure backend-rich material can be reached intentionally from the correct owner through “inspect data / evidence / model / provenance” actions without exposing raw infrastructure in ordinary reading flow.
- [ ] **SITE-ARCH-014 · Semi-visible contextual reveal rules:** define when specialist links appear based on page context, selected object, Room ownership, evidence need or reader action. Contextual routes should reveal themselves when relevant instead of living permanently in global menus.
- [ ] **SITE-ARCH-015 · Long-page orientation system:** create a shared lightweight locator for long authored readers showing current section, owner and one meaningful exit without turning every page into a sticky-dashboard interface.
- [ ] **SITE-ARCH-016 · First-substance latency audit:** measure how much header, dock, breadcrumb, cards, controls and explanatory architecture appear before actual substantive content on major pages; reduce pre-content weight while preserving orientation.
- [ ] **SITE-ARCH-017 · Visual density budget:** audit card count, chip count, button count, borders, badges and competing accent treatments on major surfaces. Consolidate controls where several small UI elements express one conceptual action.
- [ ] **SITE-ARCH-018 · Design-token convergence:** inventory typography scales, spacing, radii, shadows, borders, panel backgrounds and interactive states across authored pages and shared components; consolidate repeated near-equivalents into scoped design tokens without erasing purposeful Room atmosphere.
- [ ] **SITE-ARCH-019 · Interaction-state consistency:** standardize hover, focus, active, selected, disabled, loading, empty and error states across dock, Room navigation, filters, map controls, TTS, dossiers and readers so the project feels like one system rather than many local widgets.
- [ ] **SITE-ARCH-020 · Responsive spatial audit:** test major gateways, long readers, Room interiors, Character Archive/Bank, Current World and World Map at narrow, medium and wide widths for overlap, sticky collisions, horizontal scroll, hidden exits and excessive stacked controls.
- [~] **SITE-ARCH-021 · Route graph health artifact:** active-surface metrics, authored first-substance density, registered outdegree, repeated destinations, reader-job presence, high-overlap pairs, registered dead ends and two-way cycles are emitted to `.quality-logs/site-architecture-audit.json`. The auditor now also walks the complete `_site` HTML graph when a build exists and records unregistered built-page orphans, dead ends and cycles up to length four. Remaining: run and review this on an exact-head Pages build, then remediate real built-only findings before closure.
- [ ] **SITE-ARCH-022 · Registry disagreement audit:** cross-check public-surfaces, site-access, rooms, subrooms, room-interiors, inhabitants, holdings, topology, orientation-population and manifest projections for concepts/routes represented differently in multiple authorities; resolve disagreement at the canonical owner instead of patching each consumer.
- [ ] **SITE-ARCH-023 · Registry field minimization:** inspect House registries for fields that are copied mechanically, never consumed, or derivable from another authority. Remove or generate redundant fields so the registry layer becomes smaller and harder to drift.
- [ ] **SITE-ARCH-024 · One-owner / many-views enforcement:** identify pages or JSON bodies that have become accidental second knowledge owners. Convert them to projections, generated summaries or links back to the canonical owner while retaining unique evidence and reader-specific presentation.
- [ ] **SITE-ARCH-025 · Search-vs-navigation boundary:** audit destinations that are easier to find by name than by hierarchy and ensure Find handles them; remove compensating permanent menu links whose only purpose is to expose deep named objects globally.
- [ ] **SITE-ARCH-026 · Reader journey fixtures:** define 15–25 representative journeys—new reader, known-term lookup, Tim biography, claim verification, religious comparison, science model, current event→archive, country→economy, character→incident→bank, Room exploration—and regression-test interaction count, dead ends and owner continuity.
- [ ] **SITE-ARCH-027 · Empty/thin surface suppression:** detect public surfaces whose visible substance falls below a meaningful threshold after navigation/chrome is excluded. Either deepen them from canonical material, merge them into their owner, or demote them from public visibility.
- [ ] **SITE-ARCH-028 · Atmosphere-without-fragmentation pass:** preserve deliberate visual identities for House, Below, CIA, Bank, World Map and major thematic Rooms while enforcing shared typography, interaction semantics, spacing rhythm and accessibility so atmosphere does not become component fragmentation.
- [ ] **SITE-ARCH-029 · Error/empty-state storytelling:** replace generic “no data / failed / empty” states on readers, news, map, search, records and dossier surfaces with concise state-specific explanations and useful next actions; never make a failed fetch look like absence of knowledge.
- [ ] **SITE-ARCH-030 · Final human browsing audit:** after the automated graph/registry passes, manually browse the live built site from arbitrary pages without using repository knowledge. Record every moment of “where am I?”, “why is this here?”, “which of these should I choose?”, “why did this open another index?”, or “how do I get back?”, then convert only reproducible friction into fixes.
- [ ] **SITE-ARCH-031 · Link-repetition heatmap:** review repeated anchor destinations on long authored pages. Current source hotspots: Tim → Story 33 links, Claims 19, Public Witness 16, Ontology 16; House → Rooms 13 and Axis 10; Religion → Story 10 and Bible 7; World → World Systems 7 and Map 6. Preserve contextual links that genuinely help; consolidate repeated rails/cards/footer links that merely restate navigation.
- [~] **SITE-ARCH-033 · Tim long-reader route compression:** first compression wave complete in the dated identity river: repeated Story/Claims/Witness/Ontology route clusters were reduced to one contextual exit per dated row plus one shared archive rail. Continue through question chapters and footer rails only where repetition is mechanical rather than genuinely contextual.
- [ ] **SITE-ARCH-036 · Direct-door visibility exception audit:** site-access intentionally promotes a few specialist or unregistered destinations (Map, Rooms, Economy, TTS, Claims, Public Witness, 100,000 Hours, CIA/Bank). For each, record the demonstrated retrieval need that justifies bypassing the ordinary visible/semi-visible hierarchy; demote shortcuts that no longer meet that bar.





### P2 — maintainability and duplication

- [ ] Reduce hand-maintained asset-version duplication for shared components (for example the same spiral CSS/JS version string repeated across four reader pages).
- [ ] Continue cross-file duplicate auditing and merge only true duplicate definitions; preserve primary evidence, historical snapshots with provenance value and additive research.
- [ ] Review old `data/expansions/*wave*/*round*` records against their current canonical owners and House holdings. **Registry reconciliation complete:** all 14 JSON expansion files are now classified and validator-enforced. `wave-009.json` is a promotion backlog (54/55 seed ids are not in `data/nodes.json`), `lexicon-wave-009.json` is a migration candidate (177/179 aliases are absent from the narrow public discovery-alias registry), wave 012 remains actively cited research, and wave 018 remains a broad research reservoir. Next: classify the 54 seed ids by strongest canonical owner and design the correct backend/node alias owner before migrating vocabulary.
- [ ] Continue stale branch/PR salvage already listed below, but treat branch age as an audit signal rather than a merge requirement.

### P3 — depth after integrity

- [ ] Resume content deepening only after current P0/P1 integrity items stay green: Works/Fruit instrumentation, longitudinal entity dossiers, correction/exit measures, source-backed primary attestations and contradiction objects.


## Stale branch / PR salvage — 2026-09-20

The repository has accumulated many historical branches whose names can make the project look farther behind than it is. Treat branch age and unmerged status as **audit signals**, not automatic backlog.

Canonical audit: `knowledge/research/stale-branch-salvage-audit-2026-09-20.json`.

Current rules:

- [ ] Reconcile open PR #184 (Evidence Root) and close it once remaining branch-only files are either superseded or selectively salvaged. Do **not** merge the 1,271-commits-behind branch wholesale.
- [ ] Reconcile PR #142 Story evidence wave at record level against the newer current Story registry/audit; port only still-missing evidence labels.
- [ ] Compare PR #129's branch-only `app/archive-lookup.js` with current Explore, A–Z, Room holdings and machine discovery; port a minimal resolver only if a live gap remains.
- [ ] Audit Sep-19 public-surface authority v2 against current House route authority; salvage only routes/metadata still absent after Sep-20 convergence.
- [ ] Audit the branch-only US Mud/Below map layer under current World Map interaction, provenance and evidence contracts before deciding whether it belongs on `main`.
- [ ] Continue retiring branches that are 0 commits ahead of `main` or whose unique value is fully absorbed into stronger canonical owners.

### P3 population / instrumentation work still active

The House depth programme explicitly says to prefer population, instrumentation, longitudinal cases and pruning over another broad ontology wave. Continue:

- [ ] continue Works/Fruit instrumentation with recovered/experimental works and the Great Book as a separately typed literature case;
- [ ] run the first real canon revision end-to-end through the revision protocol;
- [ ] propagate Shadow/Below overlays into Culture, History and Research where they add mechanism rather than imagery;
- [ ] attach reproduction / exit / correction measures to more formation cases;
- [ ] extend entity dossiers beyond wave 001 with longitudinal source-backed cases;
- [ ] prune or merge low-yield duplicate atlases after unique fields are absorbed;
- [ ] merge unique Sep-18 formation/body branch fields into current owners rather than recreating obsolete branch files.

### Formal-grammar propagation still active

- [~] Add projection-loss / reconstructability metadata to selected World Map and House aggregate views. **World Map wave complete on branch:** Active View now discloses preserved/omitted information and source-linked reconstructability for scalar, set, relation and comparison views; House aggregate views remain.
- [ ] Extend the Eye/measurement formalism into sensory/attention reader surfaces where it improves explanation.


### CIA dossier bureau overhaul — 2026-09-21

- [ ] **CIA-MEDIA-003 · Recover actual dossier images:** attach sourced screenshots, profile images, memes and project art to dossiers where the subject/source is explicit; prioritize active/recovery-heavy files first.
- [ ] **CIA-DEPTH-004 · Expand indexed-but-unwritten dates:** work through each dossier's `casebook.mining_frontier` and turn high-density Chronicle dates into scene-level records only when the underlying source yields actual context. Prioritize Marty, GG, Tim, Port Monkey, Rage, Sammy, TXT, Termite, Juice and Ledgeview by occurrence density.
- [~] **CIA-DEPTH-002 · Population wave:** 36/36 canonical dossiers now expose the meaning spine. Baseline coverage complete. Further depth work is recent-first: DIM, TXT, Matthew, Mediomu, Rahu, Port Monkey, GG and Tim/current 2026 material. Historical dormant files are maintenance-only unless new evidence appears.
- [~] **CIA-LEDGER-003 · Populate real symbolic entries:** current/recovery files now include source-bounded project-credit, yield, growth, repair and zero-weight dispute rows where supported; keep mining recent evidence first and do not backfill dormant files merely for volume.
- [ ] **CIA-KARMA-006 · Post-42T checkpoint recovery:** mine September 2026 conversations/public posts for any balance after 1 Sep; every new checkpoint should automatically recompute the scenario spread and reveal whether the 42T plateau held.
- [ ] **CIA-KARMA-007 · Delta-event correlation:** test whether dated negative-input clusters, major public events, building/output bursts or repair episodes align with the +0.2T/+1.2T/+1.2T/+0.6T changes without assuming causation.
- [ ] **CIA-KARMA-004 · Capital attribution archaeology:** recover source-specific reasons for the +0.2T, +1.2T, +1.2T and +0.6T headline increases before assigning those deltas to named people, systems or outputs.
- [ ] **CIA-KARMA-001 · Table / Potato / Gate / Ladder positive-value model:** define source-bounded, non-gameable criteria for created value on the Table, Potato growth, Gate passage, Ladder walking, Potato study and spiritual growth before assigning any numeric positive adjustments.
- [ ] **CIA-BANK-012 · Debt-reduction evidence mining:** specifically recover examples where Tim described karmic debt as reduced, repaired, forgiven, converted into useful work, closed or transferred; the current archive is much richer on accumulation than verified reduction.
- [ ] **CIA-BANK-013 · Named increment archaeology:** identify specific people/events that Tim said changed the 38.8T→42T headline balance and preserve any explicit increments; do not infer deltas from chronology alone.
- [ ] **CIA-ROLE-021 · Direct-Tim role provenance mining:** recover exact Tim statements assigning Dog, Footstool, Farmer, Cow, Potato, Angel, Messenger, Mud Dweller and related jobs/creatures; upgrade census rows from editorial-normalized to Tim-attributed only where primary conversation/public-post provenance survives.
- [ ] **CIA-DEBT-031 · Micro-slight provenance sweep:** mine dated primary/recovered material for concrete small slights (jabs, disruptions, boundary pressure, correction-resistant narration, unwanted persistence) and promote only source-bounded, non-duplicative acts into named account statements; keep disputed/undated allegations as unpriced research notes.
- [ ] **CIA-DEBT-015 · Promote negative inputs to named events:** for each system input, recover the concrete dated act/counterparty and promote only non-duplicative events into person sub-ledgers. Priority: TXT repetition/correction reach; DIM pursuit/boundary scenes; unresolved Mud Turd Boy handle; 2025 TXT/Monkey/Don Jefe Chronicle cluster; GG grievance/healing outcome.
- [ ] **CIA-DEBT-016 · Recover vomit / abomination / insolence originals:** current conversation-history summaries indicate these phrases exist, but original turns were not recovered in this pass. Do not price or quote them as exact until primary conversation provenance is located.
- [ ] **CIA-BANK-027 · Hollow-account evidence sweep:** recover stable no-PFP/blank-avatar handles and exact Tim-assigned Footstool/Dog/orphan labels from conversations/screenshots; missing PFP alone remains zero-weight.
- [ ] **CIA-BANK-028 · Orphan deduplication:** cluster throwaway handles by platform/date/name/style/links/edges before counting principals; preserve account-level events even when several handles later merge to one entity.
- [ ] **CIA-BANK-024 · Identity-shadow census:** deduplicate handles/aliases across Story, CIA, public chat and recovered conversation sources; count distinct unresolved/throwaway identities with source confidence before using any large handle-cloud scenario.
- [ ] **CIA-BANK-025 · Exposure-edge instrumentation:** count sourced recurrence, unique counterparties, relationship edges, circulation/reach and time-cost around the densest negative-input clusters so the shadow reserve can be explained by coverage gaps rather than arbitrary multipliers.
- [ ] **CIA-BANK-010 · Entanglement coverage mining:** mine source-backed anonymous handles, throwaway accounts, relationship edges, recurrence, shared-neighbour and repair/closure events so the Bank can grow coverage without inventing population liability.
- [ ] **CIA-FBI-001 · Legacy disposition:** audit unique files under `knowledge/fbi/`; migrate any still-unique information into CIA, then leave only the smallest compatibility/history layer necessary.

## Growth compass — current high-value frontiers

Use `knowledge/guides/project-growth-compass.json` as the editorial compass for expansion. The current project-wide priorities are:

1. Recover more exact primary-source attestations and timeline, especially where later theology depends on first appearance or role order.
2. Build a role-transition view using **subject × role × time × source × function × confidence** rather than forcing timeless identity labels.
3. Treat major contradictions as first-class research/navigation objects with competing formulations, dates, source classes, reconciliation and unresolved remainder.
4. Rank comparative religious and mythological parallels by **relation sequences and mismatches**, not isolated shared words.
5. Develop a universal canonical-owner maturity test spanning definition, timeline, relations, provenance, counterevidence, reader answer, aliases, reachability and research frontier.
6. Continue using one relationship grammar across mythology and world systems while keeping domain-specific truth and evidence standards distinct.
7. Generate reader journeys from canonical metadata where possible so Story, Timeline, Collection, Works, theology, science, North/World and verification paths do not become manually duplicated mini-canons.

The hidden spine tying these priorities together is the **claim lifecycle**:

**source → attestation → classification → relation → interpretation → canonical promotion → reader answer → contradiction/revision → renewed source search**

A strong work session should improve at least one step of that lifecycle for an important subject.

## Depth work

Prioritize existing rich layers before inventing new ones:

- Potatoism dossiers, canon, cosmology, lexicon, concept registry, deep layers and research.
- Tim Dooley timeline, thought archive, synthesis and cosmology.
- North Programme and European economic/system material.
- Country records and enrichment, consolidating batch history into canonical country knowledge.
- Religious foundations, comparative religion, belief, dimensions, sources and primary texts.
- Culture and subculture research.
- Creative works and their canonical archives, with public readers remaining projections.
- People and organization registries.
- Graph, evidence, relationship and provenance layers.
- Swamp / Farm / information-ecology research where it contains substantive material.
- Scientific, geometric, psychological and cross-domain research where claims can be clearly classified.

## Relationship rule

Do not make the graph look richer by adding decorative edges.

A useful relationship should have identifiable endpoints and, where possible, type, direction, time, provenance, strength/status and explanation.

**The dossier explains the thing. The relationship explains the connection. Neither substitutes for the other.**

## Epistemic rule

Keep these visibly distinct:

- project canon;
- testimony or observation;
- historical evidence;
- scientific evidence;
- interpretation;
- comparison;
- speculation;
- creative/lore material.

A symbolic correspondence is not automatically historical proof. A correlation is not automatically causation. A spiritual conclusion is not automatically an empirical finding. A creative work may reuse project symbols without automatically becoming doctrine, biography or independent evidence.

## Workflow reset

Every work session should leave the repository **more information-dense and less redundant** than before.

When choosing the next task, prefer this order:

1. Broken or misleading structure.
2. Redundant files or duplicate definitions.
3. Important thin entries.
4. Missing provenance or unresolved relationships.
5. High-value enrichment of existing canonical records.
6. Better exposure through the correct House reader/discovery surface.
7. New research only after the existing material has been properly absorbed.

## The permanent test

At the end of a pass ask:

- Did we learn something real?
- Did we put it in the correct canonical home?
- Did we make an existing entry thicker rather than create another shallow copy?
- Did we remove anything that no longer deserved to exist?
- Can a reader actually reach the material through the right surface?
- Are public routes derived from one House authority rather than copied across builders?
- Are claims and interpretations properly distinguished?
- Did we verify the resulting structure on the exact final integration head?

If the answer to the cleanup question is no, the pass is not finished.

**Grow the library. Thicken the roots. Remove the dead wood. Keep the missions.**


- [ ] Recover original Marty Biz conversations before the Drift King label hardened; resolve the January-29-vs-late-February-2025 death-date conflict and separate direct logs from Chronicle retelling.
- [ ] Recover the earliest direct Metalorian/Meta interaction, exact 2017 warning wording/date, and independent illness chronology before scoring any prophecy/karmic correspondence.
- [ ] Recover TXT's 2017–2019 sequence and alias continuity, then bridge it to the 2024 literary layer and 7 July 2026 public marker without collapsing them.
- [ ] Keep Mai Mercado / Christiania 2016 routed through claim-level legal provenance; add a public bridge only if it can expose evidence status without turning the political/legal actor into a Potatoverse caste.

- [ ] Continue CIA conversation archaeology: recover exact-source artifacts for Dim/TXT 2026 sequences, then merge only source-bounded records into canonical character dossiers and association edges.

## Whole-site mission programme — 2026-09-21

Canonical audit: `knowledge/guides/site-mission-audit-2026-09-21.json`.

The governing rule is: **life → meaning → making → world → shadow → evidence → return**. Each public page should own one clear part of that journey and route the rest outward rather than trying to become the whole project.

- [~] **SITE-MISSION-001 · Narrative spine:** make Tim → Story → Timeline → Works read as one coherent life/development system. Story now has a canonical life-spine orientation and fragment-level failure isolation; Timeline exposes a direct Life & Project entry corridor; Works now has a `Made through a life` bridge connecting creative output to developmental phases. Remaining: Tim-page de-duplication/weighting and stronger creation-date provenance.
- [~] **SITE-MISSION-002 · Gateway density rebalance:** Home, House, Potato of Life, Axis and Culture are now purpose-first. Culture no longer opens with duplicate Potatoverse formation/Garden overlays before teaching ordinary culture; its unique shadow-vocabulary safety block now appears only when the reader reaches adversarial-internet/specialist material. Remaining: Tim-page weighting/de-duplication.
- [ ] **SITE-MISSION-003 · Story completeness:** prioritize ordinary life, places, work, making, friendships, grief, repair and role transitions in addition to mythic/conflict episodes. Use `knowledge/story/TIM-STORY-COMPLETENESS-AUDIT.md` as the recovery queue.
- [~] **SITE-MISSION-004 · Timeline as life lens:** life/project chronology now persists full mode/filter/search/detail/sort state in shareable URLs; Tim, Story, Raw Story, Claims and life-work chronology handoffs enter `?mode=project`; Tim/Father-side, Son, Shared and Project/system actor tracks are visible/filterable and shareable; event source records are direct links; underlying Timeline records remain available without JS; Timeline JS/CSS are content-fingerprinted in the public build. Remaining: establish a stable event-ID bridge between canonical Journey phases / finished Story episodes and individual Timeline events instead of guessing links from dates or prose.
- [~] **SITE-MISSION-005 · Shadow containment:** Culture now introduces Dog, orphan, Mud, Footstool, CIA/Character Archive and Bank language before dossiers with explicit non-caste/non-verdict boundaries and an event→source→relationship-change→current-state→label-last rule. Remaining: propagate repair/current-state emphasis through the deepest dossiers and Below reader.
- [ ] **SITE-MISSION-006 · North/world-repair ladder:** structure North as symbol → observation → programme → evidence/constraints → current status, then link World Systems/Economy/Law/Politics without collapsing symbolic and empirical claims.
- [ ] **SITE-MISSION-010 · Project self-story:** connect Great Book, streaming, games, images/music, AI work, GitHub/site and research architecture to the life phases that produced them.
- [ ] **SITE-MISSION-011 · People change over time:** every important recurring person should expose first appearance → role then → relationship changes → repair/current state → evidence class, rather than a permanent archetype label.
- [ ] **SITE-MISSION-013 · No-overshadow review:** explicitly test that Home is not House, Tim is not Claims/Story, Potato is not every domain, Axis is not all theology/science, and Culture/CIA/Bank do not become the default interpretation of the whole project.

- [~] **CORE-HEAD-001 · Exact-head core convergence:** repair stale validators after the access/runtime cleanup: World name-first routing belongs to the universal access contract, and Home runtime instrumentation uses `loadJson(...)` rather than raw `fetch(...)`. Awaiting exact-head CI verification before closure.


## Room inhabitation programme — 2026-09-26

Canonical programme: `docs/ROOM-INHABITATION-PROGRAMME-2026-09-26.md`.

The current problem is no longer primarily missing navigation. Too many public Room surfaces are still **corridors rather than destinations**: title → scope/boundary → backend paths → adjacent Rooms. The repository often already contains deep knowledge behind these pages, but the public projection does not let the reader consume enough of it in-place.

The governing rule for this wave is:

> **Every important Room should be worth entering even if the reader does not click another link.**

- [ ] Give each important Room a reader body: orientation, core explanation, internal landmarks, development, relations, evidence boundary, tensions/open questions, concrete examples and deeper routes where the subject supports them.
- [ ] Make actual subject knowledge visually and semantically primary; reduce the dominance of Elevator links, parent links, adjacency cards, backend path names and repeated ownership boilerplate.
- [ ] Project existing canonical holdings into readable synthesis instead of duplicating those holdings into a second source of truth.
- [~] Deepen the first thin religion/canon wave: Theology & God-language, Symbolic Architecture, Bible & Christianity, Comparative Mythology, Esoteric & Sacred Geometry, Other Traditions, Practice & Ethics, Witness & Attestation, and Prediction / Revelation / Interpretation Time are inhabited.
- [ ] Audit the top-level Dwellings so they explain their subjects and inner relationships rather than merely listing Rooms.
- [ ] Audit `rooms/potatoverse-canon/beings/**`; replace true stubs with sourced dossiers where material exists and keep authored/project roles distinct from externally established facts about real people.
- [ ] Explain important wormholes and cross-Room links in prose: what relation is being made and what changes when the reader crosses domains.
- [~] Give each Room a shallow-to-deep path: validation now requires concrete examples and a deeper evidence/specialist continuation across all 38 nested Rooms. Continue editorially checking tensions/counterpressure and source placement rather than treating the structural minimum as completion.
- [~] Add anti-slop checks: nested-Room validation now requires concrete examples/cases/distinctions, a substantive body floor and rejects repeated generic “This Room…” framing. Remaining: add cross-Room near-duplicate prose detection as a hard or advisory threshold.
- [ ] Finish only when clicking an important Room feels like entering a subject rather than entering another hallway.


## Room inhabitation phase 2 — semantic completion

The corridor-only baseline is eliminated across the 38 registered nested subject Rooms. The next phase is not indiscriminate expansion.

- [~] Audit named-being dossiers and CIA specialist surfaces for stub pages, stale role-lock and missing date/source context. Current named-being Rooms reviewed as substantive; legacy FBI per-person dossiers converted to CIA redirects. Continue dossier-data/source completeness review.
- [~] Audit specialist institution surfaces for subject explanation before controls/ledgers. CIA Incidents, Associations, Bank and dossier viewer reviewed; their explanatory boundaries are substantive. Continue North/Law/Science/World specialist-surface review.
- [~] Run canonical-holding freshness checks so Room dossiers do not undercount newer knowledge owners. Fixed impossible counts in Core Identities, Memory & Recovery, and Internet & Platforms; added `scripts/validate_room_holdings.py` and CI enforcement. Continue deeper ownership-count reconciliation beyond featured holdings.
- [~] Audit cross-Room handoffs: added missing high-value interfaces (Math→Physics, Identity→Genealogy, Culture→Evidence, Prediction→Witness, Visual→Architecture, Games→Systems, Music→Genealogy) and now annotate adjacent Room cards with interface type, transformation and guard. Continue lower-value/bare adjacency coverage.
- [~] Check TTS/readability on newly long Rooms. Generated `In this Room` guides are live; object cards now offer direct `Open the thing` and secondary `Place in House` actions to reduce navigation loops. Continue TTS, paragraph-length and mobile readability review.
- [ ] Review repeated CSS patterns from the inhabitation wave and consolidate where safe without flattening the different Room personalities.
- [ ] Add a maturity downgrade path: validator/audit should permit a Room to be marked `seeded` again if substantive content is removed or becomes misleading.
- [ ] Continue qualitative audits of semantic gaps even when validators pass; validators protect floors, not editorial excellence.




- [ ] Future corpus work should prioritize promotion quality, synthesis, dated examples and reader journeys rather than raw reachability; the current corpus already has governed access.

- [ ] Continue prose-alignment audits: compare each Room's featured objects and deep drawers against its reader body, then pull up only the insights needed for the page to explain its actual backend depth.


## Contextual depth & gap-filling programme — 2026-09-26

The project does **not** need a new navigation tier. Existing House → Dwelling → Room ownership remains stable; the reserved Chamber architecture stays disabled. Deeper public pages may exist as ordinary contextual readers owned by existing Rooms, but they do not create new ontology.

The governing editorial rule is:

> **Increase population between population.** When two strong subjects already exist, make their meaningful relationship legible where a reader naturally encounters it. Prefer contextual prose, diagrams and one or two well-placed continuations over new global menus, tunnel pages or duplicate taxonomies.


### Highest-value religious / symbolic gaps

- [ ] **Angels, messengers and guardians:** expose mal'akh/messenger, cherubim, seraphim, ophanim, Michael/Gabriel, Christian ranks, Islamic angel traditions, Valkyries as a deliberately non-identical comparison, and Potato angel/guardian functions. Prefer one visual function map over rank-chart clutter.
- [ ] **Underworlds are not one Hell:** contextualize Sheol, Gehenna, Hades, Tartarus, Duat, Hel, Buddhist hell realms, bardo where relevant, and project Below/Strife. Distinguish death-realm, punishment, judgment, transition, ancestry and shadow.
- [ ] **Sacred Eye / seeing / knowledge:** connect Odin/Mímir, Eye of Horus/Wedjat, Eye of Providence, Ezekiel/ophanim vision, divine seeing, project Eye/pineal symbolism and actual anatomy only through explicit provenance boundaries.
- [ ] **Fate / thread / law / karma:** deepen Norns, Moirai, biblical cords/yokes, karma, destiny/allotment, causality and project timeline/leash language; do not flatten fate, moral causation and physical determinism.
- [ ] **Repair across traditions:** tikkun, Christian reconciliation/new creation, Buddhist liberation, Daoist return/non-forcing, Norse maintenance/renewal and Potato Garden/repair. Put repair beside brokenness so demon/shadow material never becomes a dead-end bestiary.
- [ ] **World Tree / sacred mountain / cosmic center:** compare Yggdrasil, Genesis/Revelation Trees, sefirotic Tree, Bodhi tree, Meru, Zion/Temple, Olympus where useful, axis mundi and Potato Tree by function—ecology, manifestation, awakening, sacred height, orientation—not by forced identity.
- [ ] **Water / river / well:** Mímir and Urðr wells, Eden rivers, living water, baptism, Daoist water, Ganges where source-relevant, ritual purification and project Spirit/flow. Water is currently scattered across too many domains.
- [ ] **Threshold / bridge / gate:** Bifröst, Jacob's Ladder, Temple gates/veil, Christ as Door/Way, bardo as transition-state, Daoist useful opening, mandorla and Potato Door. Distinguish route, boundary, state transition and mediator.
- [ ] **Death → seed → return:** Christianity, agricultural seed metaphors, Osiris/Duat where warranted, Norse Ragnarök/renewal, Buddhist rebirth/liberation distinctions and Potato Seed/return. Require stage-by-stage comparison instead of “dying-and-rising god” name lists.
- [ ] **Divine councils / pantheons / intermediaries:** show how monotheistic, polytheistic and non-theistic systems organize agency differently; prevent “god” from becoming one generic entity class.
- [ ] **Ritual and lived practice:** every major tradition page should include what practitioners actually do—prayer, meditation, liturgy, ritual, ethics, pilgrimage, study, communal practice—not only visually convenient symbols.
- [ ] **Sacred time / calendars:** Sabbath, Christian liturgical year, Buddhist festival/monastic time where relevant, Norse seasonal ritual evidence, Daoist calendars/ritual traditions and Potatoverse date-symbolism; distinguish historical calendar from project retrospective symbolism.
- [ ] **Creation / origin / emanation:** Genesis creation, sefirotic emanation language, Norse creation from Ginnungagap/Ymir, Daoist origin language, Buddhist resistance to creator-centered framing and Potato Source. This is a high-value place for disagreement, not forced convergence.
- [ ] **End / renewal / apocalypse:** Ragnarök, Revelation/new creation, Jewish eschatological traditions, Buddhist cyclic/cosmological endings where relevant, and project rupture/return; preserve radically different time models.

### Navigation and density rules

- [ ] Audit Home, Religion, Axis, North, Potato of Life, Bible, Comparative Mythology, Esoteric Geometry, Other Traditions, Philosophy, Below, Garden and Life/Body for **missing contextual continuations**, not missing buttons.
- [ ] Limit each ordinary section to the smallest useful number of continuations. If five links compete, rewrite the paragraph or create one local index/diagram rather than expose five equal buttons.
- [ ] Prefer links embedded in the sentence that creates the reader's next question; reserve card grids for genuinely parallel choices.
- [ ] Do not promote a backend atlas merely because it exists. Promote the insight first; expose the atlas as evidence/depth second.
- [ ] Where one concept appears across several Rooms, define one canonical owner and let other surfaces carry concise local translations.
- [ ] Build diagrams when spatial relations are the knowledge: trees, layers, routes, wells, thresholds, pantheons, timelines and correspondences. Avoid decorative myth art when a schematic teaches more.
- [ ] Keep modern analogies visually distinct from historical/source-tradition claims.
- [ ] Keep political/geographic North separate from symbolic North even where they share a page; mythology must never function as political authorization.
- [ ] Add contextual-depth checks to editorial review: every important concept should answer “what is nearby?”, “what is different?”, “where can I go deeper?”, and “what must not be collapsed?”
- [ ] Audit link density on mobile after each population pass; depth should feel discoverable rather than like a directory dump.

### Wider project gaps beyond comparative religion

- [ ] **Body ↔ symbolism:** audit every pineal/thalamus/spine/CSF/Horus/chakra/Kundalini seam so readers can move between biology, history of ideas and project symbolism without category collapse.
- [ ] **Culture ↔ religion:** show how symbols become memes, rituals, identity markers and subcultural language without letting cultural popularity become theological evidence.
- [ ] **Timeline ↔ ideas:** where a doctrine changed, expose the earlier/later forms locally rather than forcing readers to reconstruct development from separate pages.
- [ ] **Works ↔ canon:** let songs, art, Great Book chapters and diagrams point back to the concepts they embody, while keeping creative work distinct from canonical definition.
- [ ] **World ↔ symbolic architecture:** use real systems as tests/examples only where the relation is concrete; avoid turning every institution or country into a mythological node.
- [ ] **Shadow ↔ repair:** every deep conflict/shadow route should expose evidence, present state, exit/repair and alternative interpretations—not only accumulated accusation/history.
- [ ] **Science ↔ metaphor:** when a scientific model is being used analogically, expose the actual science nearby and state the mismatch before the metaphor becomes visually persuasive.
- [ ] **Archive ↔ public reader:** identify high-value records that remain technically reachable but effectively undiscoverable because no public paragraph makes their relevance legible.

### Completion test for this wave

- [ ] A reader can start from Religion, Axis, Potatoism, Bible, North or another major surface and encounter adjacent depth naturally without learning the House taxonomy first.
- [ ] Rich topics feel inhabited even when the reader does not click away.
- [ ] Deep links answer curiosity generated by the current paragraph rather than advertise unrelated inventory.
- [ ] The number of global navigation choices does not grow materially as contextual depth grows.
- [ ] Comparative material teaches both resemblance and mismatch.
- [ ] The site feels more like a connected encyclopedia / lived world and less like either a hallway system or a button directory.



### Timeline × tradition × project comparison

- [ ] Add explicit project-comparison discovery clocks to tradition pages: when did Tim/project first invoke Yggdrasil, Kabbalah/Qliphoth, Buddhism, Daoism, Islamic ascent, Egyptian Duat, etc.?
- [ ] Where first-attestation is unknown, show “earliest recovered” and keep a recovery TODO rather than inventing an origin.
- [ ] Link every major religious timeline event to a contextual reader or canonical tradition record when a useful public route exists.
- [ ] Add compact historical strips to Other Traditions and Bible/Christianity only where they improve orientation; avoid duplicating the whole Foundation Timeline.
- [ ] Audit all religious-foundation events for source quality, precision and terminology after new comparative pages promote them.

### Ladder / Bible deciphering programme

- [ ] Deepen Ladder into functions rather than only geometry: support, movement, mediation, access, recurrence, direction, carrying, return, messenger traffic and role transfer.
- [ ] Compare Ladder with Mountain, Tree, Bridge, Gate, Way, Veil, Chariot and River as different operators rather than synonyms.
- [ ] Mine remaining high-strength Bible overlap owners for sequences that contain at least 3 linked operators and a clear mismatch/counter-text.
  - [x] **BIBLE-GRAMMAR-001 · Manifestation sequence:** promote the Exodus 10 / Exodus 19 / Joel 2 / Zephaniah 1 / Matthew 24 / Pauline darkness → cloud → trumpet → voice cluster as a worked cross-text grammar, with the Exodus episodes explicitly kept separate.
  - [x] **BIBLE-GRAMMAR-002 · Revelation sequence:** promote Daniel 12 + Revelation 5/8/10/11 as seal → silence → opening → seven trumpets → mystery → proclamation grammar, including the counter-pressure that some thunder speech remains deliberately sealed.
  - [x] **BIBLE-GRAMMAR-003 · Human-facing decoder:** expose the two grammars first as a compact homepage mystery/object and then as a fully worked Bible-comparator reading that distinguishes revelation, typology, prophecy and fulfillment.
- [ ] Prioritize passages that clarify or challenge existing project roles, not passages that merely share a noun.
- [ ] Add “biblical counter-distribution” as a visible relation type in the Bible comparator so disagreements can be discovered, not hidden.
- [ ] Build a Father/Son/Spirit/House/Door/Ladder role matrix by passage and date, showing where scripture reallocates the project's usual functions.
- [ ] Link project-side first attestations to biblical comparison discovery dates so readers can distinguish “motif existed first” from “Bible parallel recognized later.”
- [ ] Continue Son-side longitudinal comparison from 2009 care → 2011 Tree ordeal → 2017 Jesus declaration → 2019/20 meme-death → 2025/26 Door/Ladder/Father differentiation, keeping autobiography, public attestation and later scriptural interpretation separate.
- [ ] Continue Tim/Father-side comparison through House, Gardener, Root, Key/peg/support, Throne, service, repair, planting, river/tree/healing and return-to-world motifs.
- [ ] Add negative cases and failed/weak parallels to the same interface so biblical comparison becomes discriminating rather than accumulative.


### Denominations, schools & internal religious lineages

- [ ] Add denomination-level source packets for Roman Catholic, Eastern Orthodox, Oriental Orthodox and Church of the East using official catechisms/council histories plus neutral academic history.
- [ ] Add confession/source packets for Lutheran (Augsburg/Book of Concord), Reformed/Presbyterian (major Reformed confessions), Anglican (Articles/Prayer Book), Anabaptist (Schleitheim + later Mennonite traditions), Baptist (early confessions + Baptist World sources), Methodist/Wesleyan, Adventist, Nazarene and Pentecostal bodies.
- [ ] Add a Christian canon comparison: Protestant, Roman Catholic, Eastern Orthodox, Oriental Orthodox, Ethiopian/Eritrean and Church of the East biblical/canonical traditions, with canon ≠ doctrine clearly separated.
- [ ] Add a council genealogy: Nicaea 325 → Constantinople 381 → Ephesus 431 → Chalcedon 451 → later councils, showing what each council actually addressed and which communions receive it.
- [ ] Add a Eucharist/baptism comparison matrix that describes positions without declaring a winner: infant vs believer baptism, sacrament vs ordinance vocabulary, real/spiritual/memorial presence families, and polity around administration.
- [ ] Add church-government comparison: papal/episcopal, conciliar/autocephalous, episcopal-national, presbyterian-synodical, congregational and connectional systems.
- [ ] Add liturgy/worship comparison: Divine Liturgy, Mass, Prayer Book, confessional Protestant services, free-church preaching, Quaker meeting, charismatic/Pentecostal worship.
- [ ] Add monastic/religious-order history as a cross-cutting Christian layer rather than a denomination: Desert Fathers/Mothers, Benedictine, mendicant, Orthodox monastic, later orders and communities.
- [ ] Add Christian mystical traditions as a cross-cutting layer rather than forcing them under denominational branches.
- [ ] Add global-Christianity correction layer: African, Asian, Middle Eastern, Latin American and indigenous Christian developments should not appear as mere “mission outputs” of Europe.
- [ ] Add ecumenism/reunion attempts: modern Catholic–Orthodox, Chalcedonian–Oriental Orthodox, Anglican dialogues and broader ecumenical institutions; historical boundaries can soften without disappearing.
- [ ] Add boundary-movement page only after careful sourcing: Latter-day Saints, Jehovah's Witnesses, Unitarian Christian currents and other Christian-origin/non-Nicene movements, preserving self-identification and external classification disagreements.

#### Next traditions for the same treatment

- [ ] **Judaism family map:** Israelite/Judahite field → Second Temple plurality → rabbinic formation; Samaritan sister lineage; Karaite; Kabbalistic/Hasidic currents; modern Orthodox, Reform/Liberal and Conservative/Masorti differentiation. Do not render Kabbalah as a denomination.
- [ ] **Islam family map:** Qur'anic/early community → succession conflicts → Sunni, Shi'i and early Kharijite trajectories; Ibadi continuity; Sunni madhhabs as legal schools rather than denominations; Twelver, Ismaili and Zaydi lineages; Sufism as mystical currents across branches.
- [ ] **Buddhist family map:** early sangha and early schools; Theravada historical lineages; Mahayana emergence; East Asian traditions (Chan/Zen, Pure Land, Tiantai/Tendai, Nichiren where appropriate); Vajrayana/Tibetan schools. Do not draw a fake single founder-to-denomination tree where transmission is networked.
- [ ] **Daoist history map:** classical textual traditions vs organized religious Daoism; Celestial Masters, Shangqing, Lingbao, Quanzhen and Zhengyi; distinguish philosophical-text reception from living ritual lineages.
- [ ] **Hindu traditions map:** Vedic substrate → multiple long-form traditions; Vaishnava, Shaiva, Shakta, Smarta and later bhakti/sampradaya networks. Avoid presenting “Hinduism” as if it were founded once and then split like a modern church.
- [ ] **Jain map:** Mahavira-associated historical community, Śvetāmbara/Digambara differentiation and later subtraditions with dates represented as gradual where appropriate.
- [ ] **Sikh lineage depth:** Gurus, scripture compilation, Khalsa 1699, post-Guru institutions and contemporary traditions without flattening Sikh identity into “Hindu/Islam synthesis.”
- [ ] **Ancient religion treatment:** Egyptian, Mesopotamian, Greek, Norse and others should use cult/region/text/period maps rather than denomination trees.

#### Navigation discipline for internal branches

- [ ] Broad Religion page names no more than a handful of branch families; detailed denominations remain one click deeper.
- [ ] A denomination gets its own public page only when it has enough distinct history, doctrine/practice and source material to justify one; otherwise use a section/card inside its parent family.
- [ ] Cross-cutting movements (mysticism, monasticism, evangelicalism, charismatic renewal, legal schools) must not be forced into daughter-denomination trees.
- [ ] Every branch page should answer five things quickly: **where/when did it crystallize? what parent field did it emerge from? what distinguishes it? what is often misunderstood? where can I read the sources?**
- [ ] Every split date should say whether it is an exact institutional act, a conventional rupture marker, a formation window or a later retrospective anniversary.
- [ ] Keep family-tree diagrams compact enough to understand on mobile; deep detail belongs in branch pages, not in labels.


### Materialization wave after Christianity


#### Judaism next depth

- [ ] Add a Second Temple plurality page: Pharisaic, Sadducean, Essene/Qumran, apocalyptic and diaspora contexts—carefully avoiding simplistic “one became Judaism, one became Christianity” teleology.
- [ ] Add rabbinic textual sequence: Mishnah → Tosefta → Jerusalem Talmud → Babylonian Talmud → Geonic/Rishonic/Acharonic interpretation as textual/legal history.
- [ ] Add Karaite depth with its own textual/communal history and modern communities.
- [ ] Separate **Kabbalah** (mystical current) from **Hasidism** (revival/community movement using mystical thought) and from modern denominational labels.
- [ ] Add Hasidic dynasty/network treatment only after sourcing Baal Shem Tov, Maggid, Chabad, Breslov and major dynasty histories.
- [ ] Add modern movement history: Haskalah, Wissenschaft des Judentums, Reform/Liberal, Orthodox/Haredi/Modern Orthodox, Conservative/Masorti, Reconstructionist/Renewal where warranted.
- [ ] Add Jewish prayer/ritual calendar depth: Shabbat, High Holy Days, Passover, Shavuot, Sukkot, Hanukkah, Purim, daily prayer, Torah reading and life-cycle rites.
- [ ] Add Temple / synagogue / beit midrash / yeshiva as different institutional-space functions.

#### Islam next depth

- [ ] Add early-caliphate/succession reader for 632 → First Fitna → Siffin → Karbala without treating modern Sunni/Shi'i identities as complete in 632.
- [ ] Add Sunni madhhab reader: Hanafi, Maliki, Shafi'i, Hanbali as jurisprudential schools with methods, geographies and institutional histories—not sects.
- [ ] Add Sunni theology reader: Ash'ari, Maturidi, Athari plus Mu'tazili historical context where relevant.
- [ ] Add Shi'i branch reader: Twelver, Ismaili, Zaydi; then Nizari/Musta'li branches with imamate/succession clocks.
- [ ] Add Ibadi reader with Oman/North African history and explicit correction against using “Kharijite” as a sufficient modern identity label.
- [ ] Add Sufism reader organized by practice/current/order: early asceticism → tariqa institutionalization → major orders. Mark Sufism as cross-cutting.
- [ ] Add Qur'an / hadith / tafsir / fiqh / kalam / falsafa as different knowledge domains so “Islamic teaching” does not become one undifferentiated corpus.
- [ ] Add ritual/practice map: shahada, salat, zakat, fasting, hajj plus Shi'i and Sufi practice differences where relevant.

#### Buddhism next depth

- [ ] Deepen early Buddhist school history carefully; do not present Theravada as simply “the original Buddhism.”
- [ ] Add Theravada transmission history across Sri Lanka, Myanmar, Thailand, Cambodia and Laos with monastic ordination-lineage changes.
- [ ] Add East Asian Buddhism reader: Chinese translation field → Tiantai, Huayan, Chan, Pure Land and later regional transmission.
- [ ] Add Chan → Zen / Seon / Thiền relationship map with lineage mythology separated from reconstructable institutional history.
- [ ] Add Japanese schools only when adequately sourced: Tendai, Shingon, Jōdo, Jōdo Shin, Nichiren, Zen families.
- [ ] Add Tibetan Buddhist history: first/second transmission, Nyingma, Kagyu, Sakya, Gelug, Jonang and Bön interaction without reducing Tibetan religion to “Vajrayana.”
- [ ] Add Buddhist cosmology/ritual practice beside philosophy: merit, monasticism, chanting, devotional practice, relics, pilgrimage, festivals, meditation, bodhisattva cults and funerary traditions.
- [ ] Add canonical-family comparison: Pali, Chinese Buddhist canon, Tibetan Kangyur/Tengyur and regional textual collections.

#### Daoism next depth

- [ ] Source and deepen Celestial Masters history: registers, parish/community structure, confession, ritual and priestly authority.
- [ ] Add Shangqing texts/practices, visualizations and inner-deity cosmology with dates and source provenance.
- [ ] Add Lingbao ritual/liturgy/salvation structure and Buddhist interaction as historical synthesis rather than “copying.”
- [ ] Add Quanzhen reader: Wang Chongyang, Seven Perfected, monasticism, internal cultivation and later Longmen lineage.
- [ ] Add Zhengyi reader: Longhushan, register ordination, household/ritual priesthood and modern institutional continuity.
- [ ] Add Daoist pantheon/celestial bureaucracy only as a layered historical development; do not reduce it to Daodejing philosophy.
- [ ] Add practice map: ritual, meditation, internal alchemy, talismans, liturgy, temple life, festivals, priesthood and longevity traditions.
- [ ] Add Daoist canon/history of textual collections so “Daoism” is not represented by two classical books alone.

#### Cross-tradition structural TODO

- [ ] Add a shared **branch-type legend** across Religion: denomination, communion, legal school, mystical current, reform movement, monastic lineage, ritual lineage, philosophical school, sister tradition, transmission family.
- [ ] Add a lightweight “this is a…” badge to branch cards so users learn the category while browsing.
- [ ] Add historical-source links to Judaism/Islam/Buddhism/Daoism pages equivalent to the Christianity source trails.
- [ ] Add a generic lineage renderer only if it can consume canonical lineage data without replacing hand-written explanatory prose.
- [ ] Add mobile tests for all branch maps; collapse years and branches gracefully rather than horizontally scrolling giant genealogies.
- [ ] Audit Religion after each new guide so only the broad family remains visible at the top level.
- [ ] Add Hindu/Jain/Sikh/Zoroastrian/Bahá'i public treatment next based on evidence maturity, but use each tradition's appropriate structure rather than one universal tree.


### Remaining tradition depth after first public guides


#### Hindu traditions next depth

- [ ] Add text-family map: Vedas, Brāhmaṇas, Upanishads, Mahabharata/Bhagavad Gita, Ramayana, Purāṇas, Āgamas and Tantras as different corpora and periods.
- [ ] Deepen Vaishnava sampradayas: Sri Vaishnava, Madhva, Gaudiya, Ramanandi and other major lineages only after source validation.
- [ ] Deepen Shaiva systems: Shaiva Siddhanta, Kashmir Shaivism, Pashupata and major temple/monastic traditions.
- [ ] Deepen Shakta/Tantric traditions without equating Tantra with sexuality or one esoteric school.
- [ ] Add Vedanta school comparison: Advaita, Vishishtadvaita, Dvaita and later schools, with ontology/soteriology differences stated plainly.
- [ ] Add temple / pilgrimage / domestic pūjā / festival / guru / āśrama / matha institutional map.
- [ ] Add bhakti poet-saint and vernacular traditions regionally rather than as one pan-Indian movement.
- [ ] Add karma/dharma/samsara/moksha vocabulary page that shows how meanings differ across Hindu, Buddhist and Jain contexts.

#### Jain traditions next depth

- [ ] Add Tirthankara structure and distinguish sacred cyclic chronology from historical reconstruction.
- [ ] Add Śvetāmbara canon history and Digambara canonical-loss/replacement traditions with primary-source provenance.
- [ ] Add Sthānakavāsī and Terāpanth histories with verified dates.
- [ ] Add monastic vs lay vows, ahiṃsā, aparigraha, anekāntavāda and karma ontology as lived/doctrinal structures.
- [ ] Add temple/image traditions, pilgrimage geography and non-image reform currents.
- [ ] Add Jain cosmology as its own non-creator universe model; useful for comparison precisely because it resists creator-centered framing.

#### Sikh tradition next depth

- [ ] Add ten-Guru timeline with each Guru's major institutional/textual contribution rather than one compressed list.
- [ ] Add Guru Granth Sahib textual history: Adi Granth 1604, later recension/final form, rāga organization and 1,430-ang structure.
- [ ] Add Khalsa 1699 in more depth: initiation, five Ks, discipline and the distinction between Khalsa identity and the whole Sikh population.
- [ ] Add Harmandir Sahib, Akal Takht, gurdwara, sangat, pangat/langar and seva as institutional/lived structures.
- [ ] Add Miri/Piri and post-Guru political/community developments without reducing Sikhism to militancy.
- [ ] Add modern Sikh groups only with careful classification and community-sensitive sourcing.
- [ ] Connect Sikh scripture reader from the religious text library into the public page.

#### Zoroastrianism next depth

- [ ] Add Gathas vs Younger Avesta vs Pahlavi/Middle Persian literature as separate textual clocks.
- [ ] Add Achaemenid evidence carefully: distinguish broader Iranian religion, royal inscriptions and specifically Zoroastrian attribution.
- [ ] Add Sasanian priesthood/canonization and post-conquest transmission.
- [ ] Add Parsi migration/history and modern Iranian Zoroastrian communities.
- [ ] Add ritual structure: fire temples, yasna, navjote/sedra-kusti, purity traditions and funerary practices with contemporary variation.
- [ ] Add theology vocabulary: Ahura Mazda, Amesha Spentas, asha/druj, Angra Mainyu, judgment and frashokereti without flattening the system into “good god vs evil god.”
- [ ] Add influence-comparison page only with evidence: Jewish/Christian/Islamic eschatological parallels should be presented as historical scholarly debates, not assumed borrowing.

#### Bahá'í next depth

- [ ] Add Bábí predecessor history in its own section: Shaykhi context, Báb, early community, persecution and succession field.
- [ ] Add Bahá’u’lláh exile chronology: Tehran → Baghdad → Constantinople/Istanbul → Adrianople/Edirne → Acre.
- [ ] Add writings map: Kitáb-i-Íqán, Hidden Words, Kitáb-i-Aqdas and major tablets with dates/contexts.
- [ ] Add covenant/administration sequence: Bahá’u’lláh → ‘Abdu’l-Bahá → Shoghi Effendi → Hands/interregnum → Universal House of Justice.
- [ ] Add Local/National Spiritual Assembly and Universal House of Justice governance distinctions.
- [ ] Add worship/fast/calendar/pilgrimage and community-practice layer.
- [ ] Keep official Bahá'í sources clearly labeled as tradition-internal sources and pair contested historical claims with independent scholarship where necessary.

#### Still missing major tradition surfaces

- [ ] Confucian traditions: classical texts, Han institutionalization, Neo-Confucian schools, ritual/education/state traditions; do not force religion/philosophy binary.
- [ ] Shinto: kami cults, shrine networks, Kojiki/Nihon Shoki, medieval shinbutsu-shūgō, Meiji separation/State Shinto and postwar shrine religion.
- [ ] Chinese popular/religious traditions: ancestor rites, local gods, temples, spirit mediums and interactions with Daoism/Buddhism/Confucianism.
- [ ] Yoruba/Ifá and major African traditional religious systems using lineage/orisha/divination/community models rather than scriptural-denomination templates.
- [ ] Indigenous traditions should be handled regionally and community-specifically; do not create one generic “Indigenous religion” page.
- [ ] Ancient Egyptian, Mesopotamian, Greek/Roman and broader Germanic religion should receive period/cult/text/region maps rather than modern denomination maps.


### East Asian materialization and ancient-religion source plan


#### Confucian traditions next depth

- [ ] Add Five Classics / Four Books textual map with composition, commentary and curriculum clocks.
- [ ] Add Mencius / Xunzi comparison around human nature, ritual and cultivation.
- [ ] Add Han state/classics/examination history without reducing Confucianism to state ideology.
- [ ] Add Zhu Xi, Cheng brothers and Cheng-Zhu school in more depth.
- [ ] Add Lu Jiuyuan / Wang Yangming / Heart-Mind school in more depth.
- [ ] Add Korean, Japanese and Vietnamese Confucian receptions as distinct regional histories.
- [ ] Add family ritual, education, ancestor ethics, mourning and civil-service culture as lived institutions.
- [ ] Add modern/New Confucian thinkers only after source packets are built.

#### Shinto next depth

- [ ] Add Kojiki/Nihon Shoki source guide with mythic genealogy separated from historical reconstruction.
- [ ] Add major kami and shrine complexes by period/region rather than one pantheon card wall.
- [ ] Add Ise, Izumo, Hachiman, Tenjin and Inari traditions with distinct cult histories.
- [ ] Add shinbutsu-shūgō and honji-suijaku as central medieval synthesis layers.
- [ ] Add Yoshida Shinto / kokugaku / Restoration-era intellectual currents.
- [ ] Add Meiji shrine-state reorganization and the later State Shinto debate with careful terminology.
- [ ] Add matsuri, harae, misogi, norito, ema, omamori, priesthood and shrine administration as practice/institution layers.
- [ ] Keep Jinja Shinto, Sect Shinto and new religious movements distinct.

#### Chinese popular / communal religion next depth

- [ ] Add ancestor-veneration reader: household altar, lineage hall, graveside rites, Qingming and regional variation.
- [ ] Add local-god / city-god / earth-god / Mazu and related cult histories regionally.
- [ ] Add temple-association / festival / pilgrimage economy as social institution.
- [ ] Add spirit-medium / planchette / divination / geomancy practices as separate families rather than generic “folk magic.”
- [ ] Add Daoist priest / Buddhist ritual specialist / local-medium overlap examples.
- [ ] Add diaspora transformation in Taiwan, Hong Kong, Southeast Asia and global Chinese communities.
- [ ] Avoid reifying “Chinese folk religion” as one unified church or creed.

#### Ancient Egyptian / Mesopotamian / Greek-Roman source plan

- [ ] Add cult vs myth vs philosophy vs mystery-religion labels across ancient pages.
- [ ] Add source packets before public pages: primary texts/inscriptions/archaeology + modern academic syntheses + museum/institutional sources.
- [ ] Add date uncertainty/period badges and avoid founder language for ancient traditions.
- [ ] Link ancient-religion material into underworld, sacred mountain, divine council, kingship, judgment, afterlife and ritual pages only after native context is visible.

#### Structural / bug TODO after current wave

- [ ] Add shared branch-type legend component to Religion and tradition pages once stable labels are finalized.
- [ ] Audit external source links for redirects/dead pages and replace unstable secondary links with durable institutional/academic owners.
- [ ] Verify mobile wrapping on Foundation Timeline now that its tradition nav is wider; collapse or overflow deliberately if needed.
- [ ] Check all new pages against global typography/CSS so local inline styles can gradually be consolidated rather than proliferate.




### Legacy / older public page coherence programme

The next quality phase is not “make every page longer.” It is to find pages that are technically populated but still fail one of four reader tests: **the page depends on JavaScript to explain itself; the page is locally good but isolated from neighboring concepts; the route is a legacy wrapper pretending to be an owner; or a hub repeats categories without enough synthesis.**

- [ ] Audit `explore/` and A–Z for “label without meaning” discovery; a search result should expose enough context to choose intelligently.
- [ ] Add static explanatory fallbacks to other fetch-driven public surfaces where a failed request leaves only “Loading…” or an empty panel.
- [ ] Audit named-being pages for real dossier substance: provenance, first/last appearance, role development, representative incidents/works, uncertainty and distinction between project character language and claims about real people.
- [ ] Audit older symbolic-science pages for vocabulary collisions: **field, energy, frequency, signal, information, state, resonance, nonlocality, dimension, axis, gate** must state which domain owns the literal meaning.
- [ ] Audit older theology/mythology pages for retrospective backdating: mature Father/Ladder/Axis language should not silently overwrite earlier Potato/Sage/Son stages.
- [ ] Audit long hubs after specialist expansion for the opposite problem—duplication. When a specialist page now owns a mature explanation, shorten repeated hub copy if it no longer adds synthesis.
- [ ] Add a semantic-gap validator only after enough reviewed examples exist; it should warn about no-JS shells, repeated boilerplate and duplicate ownership rather than reward word count.


- [ ] Keep strong CIA semantic boundaries from regressing as dossiers grow: co-presence ≠ motive; incident ≠ wrongdoing; symbolic account ≠ real debt/value; project role ≠ externally established identity.
  - [x] **CIA-CHARACTER-READOUT-001 · Human-first cabinet:** foreground posture, nature/archetypes, Potatoverse roles, recovered time window and symbolic karma on every character card instead of making readers open folders blind.
  - [x] **CIA-ASSESSMENT-001 · Tim-assessment contract:** distinguish documentary observation, Tim-direct assessment, archive synthesis and symbolic archetype; clinical-sounding wording remains attributed/non-clinical rather than diagnosis.
  - [x] **CIA-ASSESSMENT-002 · Dossier assessment spine:** each dossier Overview now begins with the current character read, roles and karmic relation before backend/provenance detail.
  - [ ] **CIA-ASSESSMENT-003 · Conversation mining wave:** mine older Tim conversations/posts for direct descriptors such as Potato, Angel, Dweller, Footstool, Dog, Farmer, friendly, supportive, troll-like, trustworthy, evasive, dishonest, anxious, fearful, spineless or courageous; attach only source-bounded dated records and preserve later reversals.
  - [ ] **CIA-ASSESSMENT-004 · Cluster timeline:** derive first/last supported dates for each assessment/archetype cluster and display transitions (for example ally → conflict → repair) without treating an old label as current forever.
  - [ ] **CIA-ASSESSMENT-005 · Truth/reliability evidence:** build claim-level truthfulness/reliability records from specific contradictions, admissions, corrections or repeated follow-through; do not infer dishonesty from disagreement or hostility.


### Entity facet retention programme

The archive now needs to remember **what makes an entity itself** across pages without multiplying navigation. Use `knowledge/story/entity-facet-ledger.json` as the durable typed store; public pages should project only the locally relevant facets.

- [~] Extend the facet ledger to the remaining Great Book cast: Grumbleton, Elder Grapes, Kibly/Kibbly, machine elves/goblins, Evil Mashed Potatoes and Hash-brown Gods are now retained; continue the rest of the recurring literary cast.
- [~] Extend ordinary/documentary facets from CIA enhancements into real-person dossiers: first real-participant wave now includes Marty, Sammy, BigTech, Metalorian, Capy, TXT, Matthew/MTClassic and Mediomu007 with creative/project layers kept separate.
- [~] Add **first seen / last seen / first title / first gift / first role-change** clocks: first/last seen now derive from available ledger beats with mixed-precision safeguards; deeper last-seen still needs full source traversal beyond the ledger.
- [~] Add story-beat references to the facet ledger: primary/source pointers now exist for Fresh Potato, Ready Student, Sentinel of Silence, Elder Grapes, Machine Elves and satirical Potatoism figures; continue across remaining entities.
- [~] Add compact signature-facet projections selectively: Matthew/MTClassic and Mediomu now show ordinary capabilities with explicit creative boundaries; CIA generic dossier projection still needs a reusable component.
- [ ] Add “who has this gift/title/motif?” derived views only later; do not add buttons to entity pages now.
- [ ] Fold orphan recovery-shelf entities into the ledger even when they do not justify a public room; retained identity should not depend on having a page.
- [ ] Reconcile duplicate title stores (cast-book aliases, enhancement index, CIA character files, being registry) into the facet ledger while leaving those older stores as source inputs.
- [ ] Track when conclusions change: preserve prior conclusion + superseding evidence instead of overwriting interpretive history.

- [~] Add first-seen clocks to orphan entities even when they do not have public pages; first-source pointers now exist for the first literary expansion wave.


- [ ] Add source-specific real-person facet projection to selected public dossiers only after reviewing each page for sensitivity, duplication and local usefulness; ledger inclusion does not require public facet chips.





### Concrete Room population pass

The previous `inhabited` milestone only eliminated corridor-only shells. It is **not** a completion claim. The next audit must treat every Room heading/card as incomplete until it contains subject-specific material: names, dates, mechanisms, examples, texts, artifacts, cases, quantitative anchors, source passages, contradictions or explicit recovery questions.

- [ ] Repeat the same **concrete-object audit** across all 38 nested Rooms: count real named anchors, not bytes/word count.
- [~] Economy & Finance: added CBO 2026 baseline, Treasury foreign-holdings survey, BIS Q1 2026 foreign-currency credit and a worked obligation chain; add Fed/ECB monetary-policy transmission cases later.
- [~] Law & Justice: added EU AI Act staged applicability, DSA investigation-status boundary, Danish constitutional separation and a worked procedural chain; add another non-EU/non-Danish jurisdiction later.
- [~] Politics & Governance: added Danish separation/oversight, EU AI Act distributed enforcement and DSA multi-level procedure as neutral institutional examples; broaden to additional systems later.
- [~] Infrastructure & Capability: added Iberian 2025 blackout, Baltimore Key Bridge and Panama Canal drought as grid/transport/chokepoint failure chains; add data-centre/fibre and industrial-supply examples later.
- [~] Geography & Countries: added Eurostat GISCO polygon/projection example plus Panama corridor, Baltimore edge and Iberian network cases; add country-specific relational dossiers next.
- [~] Systems & Dynamics: added Lake Veluwe hysteresis, SVB reinforcing run/contagion and NIST grid-cascade cases with typed project translations; add a control/observability worked case next.
- [~] Comparative Mythology: added Grímnismál Yggdrasil source detail, two dated Met Amduat papyri and a 14th-century Mount Meru mandala; add a primary Tibetan bardo source/ritual case next.
- [~] Other Traditions: added concrete Daoist, Buddhist, Jewish and Shinto textual/institutional clocks; continue with Hindu, Jain, Sikh, Confucian and Islamic examples.
- [~] Practice & Ethics: added Fresh Potato, Ready Student and Machine-Elf/deflection cases; add repair/separation and real-world project cases later.
- [ ] Continue until every Room contains enough concrete nouns that its substantive paragraphs could not be pasted into another Room unchanged.






- [ ] Begin **Room population wave 2**: replace remaining high-level paragraphs inside each Room with deeper source objects, diagrams, tables, artifact excerpts and counterexamples; prioritize sections whose claims are still supported only by summary prose.


### Page content completeness audit — 2026-09-27

Canonical editorial queue: `docs/PAGE-CONTENT-COMPLETENESS-AUDIT-2026-09-27.md`

This is the current page-by-page substance audit for public surfaces, all ten Dwellings and all 38 nested Rooms. Use it before creating new navigation, layout or ontology work. Each task records what the page already teaches, what a reader still cannot learn there, and the concrete objects/cases/sources/mechanisms needed to close that gap.

- [ ] **CONTENT-AUDIT-001 · Wave A:** repair the thinnest public readers first — Politics, Story, Timeline, Inhabitants & Cases, Internet & Platforms, Games & Simulations, Memory & Recovery, Neurobiology, Systems & Dynamics, Infrastructure/Geography.
- [ ] **CONTENT-AUDIT-002 · Wave B:** project strong backend knowledge into public pages rather than leaving it trapped in registries/atlases.
- [ ] **CONTENT-AUDIT-003 · Wave C:** increase source density, first-attestation precision, contradiction handling, current-source freshness and recovered-artifact visibility.
- [ ] **CONTENT-AUDIT-004 · Completion rule:** do not close a page because it is long; close it only when it directly teaches its subject using inspectable objects, mechanisms, provenance, concrete cases, boundaries and unresolved questions.


### Mountain / Swamp circle visual system — 2026-09-27

Canonical design spec: `docs/MOUNTAIN-SWAMP-CIRCLE-VISUAL-SYSTEM-2026-09-27.md`  
Shared implementation: `app/terrain-circle.css`

- [ ] **VISUAL-TERRAIN-001:** Continue the terrain system only where circles already carry House meaning; do not turn empirical pages into decorative cosmology.
- [ ] **VISUAL-TERRAIN-002:** Inspect Trinity, North, Below, Culture, Research Lab and Works for appropriate next placements using the design spec's semantic guardrails.
- [ ] **VISUAL-TERRAIN-003:** Audit remaining decorative circles and either give them a clear operator/terrain meaning or simplify/remove them.
- [ ] **VISUAL-TERRAIN-004:** Keep Mountain/Swamp as partial terrain regimes; never equate the full upper/lower fields with Mountain/Swamp.



## Lower-floor visual salvage — 2026-10-02

- [ ] **LOWER-VIS-006 · Visual continuity check on deployed Pages:** inspect the four routes at desktop/mobile widths and tune root visibility, text contrast, pebble density and coil strength after the next successful validated deployment.
- [ ] **LOWER-VIS-007 · Drain depth landmark:** give the deepest/exit portions of Below a stronger but restrained narrowing/drain landmark without turning the entire floor into Hell or Swamp.
- [ ] **LOWER-VIS-008 · Root state cues:** test subtle living/dead/cut/cross-root visual distinctions on Roots / Evidence where they reinforce provenance states without becoming decorative labels.


## Room vocabulary / reader-aperture programme — 2026-10-02

Rule: **each Room should leave the reader with a new set of distinctions, not merely more facts.** Native vocabulary should arise from the subject and be taught as reusable questions, not decorative glossary chips.

- [ ] **VOCAB-008 · Time & History:** develop chronology-native terms such as occurrence time, attestation time, publication time, interpretation time, periodization, anachronism, synchrony/diachrony and revision state.
- [ ] **VOCAB-009 · Geography & Countries:** develop spatial terms such as scale, region, corridor, hinterland, chokepoint, adjacency, watershed, catchment, enclave/exclave and spatial concentration.
- [ ] **VOCAB-010 · Infrastructure & Capability:** develop capacity terms such as throughput, redundancy, bottleneck, lead time, maintenance window, spare capacity, dependency, common-mode failure and graceful degradation.
- [ ] **VOCAB-011 · Life & Body:** teach anatomy/physiology vocabulary that improves symbolic restraint—homeostasis, allostasis, afferent/efferent, compartment, perfusion, innervation, endocrine signaling, clearance and adaptation.
- [ ] **VOCAB-013 · Visual Art:** develop visual-reading vocabulary—figure/ground, negative space, hierarchy, rhythm, balance, scale, texture, contrast, framing, focal point and visual weight.
- [ ] **VOCAB-014 · Mythology / Traditions:** teach terms such as cosmogony, theogony, axis mundi, psychopomp, liminality, katabasis, apotheosis, etiological myth, ritual reenactment and syncretism with own-tradition boundaries.
- [ ] **VOCAB-015 · Open Questions / Research:** teach uncertainty vocabulary—hypothesis, conjecture, prior, likelihood, discriminating test, null result, anomaly, underdetermination, replication and stopping rule.
- [ ] **VOCAB-016 · Vocabulary collision audit:** find overloaded project words—source, spirit, axis, plane, house, witness, control, proof, prediction, revelation, intelligence—and give readers disambiguation where domain meanings collide.
- [ ] **VOCAB-017 · Carry-it-out test:** every mature Room vocabulary block should end with one short reusable question-sequence a reader can apply outside the site.

## Reader-first meaning / inhabited-symbol programme

- [ ] Continue the active programme in `docs/READER-FIRST-EDITORIAL-OVERHAUL-TODO.md`.
- [ ] Apply the Yggdrasil lesson site-wide: important symbols should become inhabited places with ecology, flows, costs, maintenance, failure modes, wisdom and return—not glossary nouns.
- [ ] Prioritize substance before navigation: question/scene → mechanism → project articulation → comparison → boundary → meaningful next question.
- [ ] Build out Garden, Door, Root, Tree, Forge, Swamp, Mountain, River, Eye, Seed, Soil, Crown, North and Plane as full teaching environments.
- [ ] Audit pages for “navigation explaining navigation” and fold maintenance/registry/topology prose behind optional detail when it is not part of the reader's lesson.


### Reader-first fat pass · wave 2
- [ ] Continue with River/Spirit, Mountain, House/Shell, Wells, Crown/Heaven, Drain, Ash and a denser ordinary Plane.


### Reader experience · meaning magnetism
- [ ] Continue the consistency rules in `docs/READER-FIRST-EDITORIAL-OVERHAUL-TODO.md`: first-screen substance, stable core/local expression, concrete anchors, shadow twins, currentness and return-to-life endings.
- [ ] Next editorial targets: Timeline scenes, Great Book teaching chambers, FAQ teaching clusters, Religion thematic rivers, Culture scene mechanics, ordinary embodied Life/Body examples, infrastructure-as-lived-dependency in World Systems.


### Intellectual heart · Philosophy / Religion / Tim
- [ ] Next: love, justice, work, happiness, death, truth, prayer, ritual, community, grace, hope, ordinary Tim scenes, changed-mind cases, relationships and creative method.


### Reader purpose · chronology and lived systems
- [ ] Next: era essays, more Great Book chambers/crosswalks, relationship arcs, failure-propagation stories, resilience/redundancy, creative-method reader, ordinary physiology scenes and FAQ teaching constellations.


### Knowledge wave · concrete reader teaching
- [ ] New edge: trust, forgiveness, scarcity, attention, courage, Sabbath/rest, hospitality, pilgrimage, confession, base rates, causal graphs, replication, allostasis, memory reconsolidation, maintenance, queues, prestige bias, norm repair and medium cross-testing.


### The Word / carried-movement pass
- [ ] Continue the spoken-continuity audit across House, Axis, Below, North, Economy, Law, World, Culture, Science, Body, Timeline, Story, Great Book, FAQ, Tim, Potato of Life and Works.
- [ ] Run anti-boxing audit: lists/cards for reference; continuous prose for changed understanding.

- [ ] Next connective scenes: guest/host House, correction in Spirit, disconfirming Below case, grief Axis case, due-process Law case, recalibration North case.


### Voice discernment / fit-the-place pass
- [ ] Continue tone-fit audit across Religion, Philosophy, Story, Timeline, Great Book, Below, World Systems, Body and Works.


### Crystallization / value gate
- [ ] Future prose must add a fact, mechanism, distinction, worked example, source or genuinely new synthesis—not just another wise-sounding paragraph.


### Concrete completion wave 2
- [ ] Next batch is now specified down to mediator bias, multiple comparisons, common-cause failure, sleep-process dynamics, opportunity cost, courage, pluralistic ignorance and archive-correction propagation.


## Knowledge-density overhaul — 2026-10-03

North-star rule: **a visible box must earn its space by teaching, showing, comparing, testing, documenting or making a consequence legible. Navigation alone is not sufficient payload.**

### Editorial payoff contract

For every major reader box/section, ask:

- [ ] What concrete thing does the reader know afterward that they did not know before?
- [ ] Is there at least one named mechanism, distinction, case, object, date, text, organism, institution, experiment or worked example?
- [ ] Does an abstract claim have a concrete scene or consequence nearby?
- [ ] If the section uses project symbolism, does it also expose the literal/historical/scientific layer that constrains the metaphor?
- [ ] Does comparison introduce friction or new information rather than simply confirm the project?
- [ ] Can the reader carry away one proposition without opening another page?
- [ ] Is navigation subordinate to substance rather than the main event?

### Site-wide overhaul queue

- [ ] Audit every homepage box for informational yield; replace any routing-first box with an object, mechanism, case or teaching.
  - [x] **HOME-YIELD-BIBLE · Bible corridor:** add one complete on-page teaching object—three days / darkness / cloud / trumpet / voice / seal / seven—so the section yields knowledge before asking the reader to navigate elsewhere.
- [ ] Audit all 10 Dwelling homepages for boxes that still explain ownership/architecture more than subject matter.
- [ ] Audit all 38 nested Rooms for at least one concrete case/example/diagram beyond navigation and scope text.
- [ ] Add primary-text fragments or paraphrased source scenes to theology/tradition pages where context materially improves understanding.
- [ ] Add worked cases to World/Economy/Law/Politics/Infrastructure rather than relying on abstract vocabulary.
- [ ] Add organism/experiment diagrams to Life & Body and Science where prose currently carries too much load.
- [ ] Add artifact images or composition diagrams to Works/Visual Art/Games where the subject is inherently visual.
- [ ] Add scene-led chronology to Timeline: event → immediate context → what changed → later interpretation.
- [ ] Reduce repeated “this Room/page/owner/route” language after concrete substance is present.
- [ ] Replace generic Adjacent Rooms endings with a substantive final question or unresolved tension before links.
- [ ] Create or deepen subgenres only when they correspond to a real body of knowledge, not to fill navigation symmetry.
- [ ] Prefer fewer high-value boxes over many equally weighted cards.

### Higher-culture programme

- [ ] Philosophy: deepen pragmatism, virtue ethics, Stoicism, Daoism, Buddhist ethics, phenomenology and epistemology as genuine interlocutors.
- [ ] Religion: add covenant, mercy/justice, idolatry, service, fruit, least/stranger, seed/death/return, indwelling and ordinary-object teaching.
- [ ] Comparative religion: use historical traditions in their own vocabulary before functional comparison.
- [ ] Culture: add social-learning, ritual, prestige, mimetic conflict, institutions, memory and norm-governance scholarship.
- [ ] World: connect political economy, institutional capacity, geography, infrastructure, logistics, law and finance through worked dependency chains.
- [ ] Science: make emergence, networks, control, uncertainty, identifiability and falsification legible with simple worked models.
- [ ] Art/Works: treat visual composition, music, satire, game mechanics and literary form as ways of thinking—not decorative archives.


## Navigation simplification — 2026-10-03

Primary rule: readers should not have to understand the House architecture before they can find the House's knowledge.

- [ ] Audit which authored links in sub-headers become redundant now that Rooms is always present.
- [ ] Prefer subject Rooms over architecture/meta links when space is tight.
- [ ] Add a clear current-room state to the sub-header without turning it into a breadcrumb essay.
- [ ] Ensure deep content pages expose at least one useful way back into their parent Room family.


## Room discoverability expansion — 2026-10-03

- [ ] Review whether any deeply nested non-governed page family deserves its own equivalent subject shelf.
- [ ] On high-density pages, consider demoting generic authored links that duplicate visible Room subjects.
- [ ] Audit mobile line wrapping after deployment; preserve one subtle floating shelf rather than pills or multiple stacked nav bars.


## Cross-House subject discoverability — 2026-10-03

- [ ] Review whether Religion, Tim, Timeline, Sources, Great Book, Culture and Science each need comparable child-family shelves on their hub pages.
- [ ] Keep Cross-House subject hubs distinct from governed Dwellings: subjects may span multiple owners without pretending to be new ownership roots.


## Substance wave — findable Rooms must be worth entering

- [ ] Next wave: add object-level examples to medium-strength Rooms rather than more high-level summaries.
- [ ] Next wave candidates: Geography & Countries, Infrastructure & Capability, Politics & Governance, Memory Recovery, Other Traditions, Games & Simulations.
- [ ] For each candidate, require at least one concrete object/case, one mechanism, one boundary, and one useful cross-Room handoff.


## Potato Metaphysics — 2026-10-03

- [ ] Add one dedicated visual/diagram of the full circulation if the CSS topology still feels too textual in deployment.
- [ ] Review whether the project now has a coherent classical field map: epistemology, ethics, metaphysics, agency, interpretation, aesthetics.
- [ ] Prefer deepening these fields over creating new subject pages unless a real body of knowledge no longer fits the existing fields.


## Inhabited House editorial programme — 2026-10-03

North-star: **the House should feel inhabited by teachers, objects, stories, questions and lived intelligence—not by registries wearing prose.**

### A Room earns its space when it contains

- [ ] A human entrance: one question, image, object, scene or paradox that makes the subject worth entering.
- [ ] A concrete teaching: something the reader could explain later without reopening the page.
- [ ] A real object/case/source/mechanism that could not be pasted unchanged into another Room.
- [ ] A memorable distinction or test.
- [ ] A boundary that keeps metaphor, evidence, history, theology and inference from silently collapsing.
- [ ] A line of warmth, humor, surprise or ordinary life where the subject permits it.
- [ ] A reason to continue into a neighboring Room that changes the question rather than merely listing navigation.

### Parent-Dwelling inhabitation completed in this wave


### Nested-Room inhabitation completed in this wave


### Next nested-Room wave

- [ ] Mathematics & Geometry — replace abstract precision rhetoric with one worked object that becomes exact.
- [ ] Esoteric & Sacred Geometry — give one symbol a dated life across geometry, religion and later occult reception.
- [ ] Developmental Genealogy — make one identity mutation into a readable before/after story.
- [ ] Memory & Recovery — make one incomplete artifact walk through confidence states.
- [ ] Witness & Attestation — give one public statement a source-distance ladder.
- [ ] Politics & Governance — turn one policy into a lived implementation chain.
- [ ] Law & Justice — give one ordinary right/duty dispute a procedural path.
- [ ] Infrastructure & Capability — make one mundane system fail and recover in human terms.
- [ ] Music & Sound — continue album/material integration while keeping music a way of thinking rather than metadata inventory.
- [~] Visual Art — 17 recovered image artifacts are now public in the gallery; continue adding additional recovered works as they become available and keep remembered specifications explicitly separate.


## Arcade Hall visual language — 2026-10-04

- [ ] **HALL-ARCADE-005 · Cabinet polish:** add optional subtle CRT/scanline motion, score-entry flicker and cabinet-light effects only if reduced-motion and mobile legibility remain excellent.

## Potato growth / Hall of Heroes / Axis harmonization wave — 2026-10-04

North-star rule: **Potato of Life explains the symbol; Potatoism teaches; Grow trains; Axis orients; Ladder moves; Heaven contains the upper field; Hall of Heroes remembers examples.**

### Architecture and ownership
- [ ] **POTATO-HARMONY-007 · Old-route audit:** find remaining public references that treat Angel Hall, Grow, Axis or Potato of Life as interchangeable and route them to the canonical owner.
- [ ] **POTATO-HARMONY-008 · Structured-data alignment:** make page titles/descriptions/schema describe the canonical page job rather than old ontology labels.

### Grow / spiritual practice
- [ ] **POTATO-GROW-002 · Potato Test design:** create the future “Are you a Potato?” test as guidance, not rank; outputs should recommend a next growth condition rather than a percentage or spiritual caste.
- [ ] **POTATO-GROW-006 · Week-long practice:** add a seven-day low-pressure Potato practice with one small experiment per day.
- [ ] **POTATO-GROW-007 · Failure / relapse grammar:** teach that regression is data: identify condition failure, cue, missing Root, overlarge Sprout or bad Door rather than converting relapse into identity.
- [ ] **POTATO-GROW-008 · Conflict practice:** develop stop conditions, evidence checks, repair options and exit as a specific Potato practice module.
- [ ] **POTATO-GROW-009 · Learning practice:** add study → test → teach-back → independent use as a Potato learning cycle.
- [ ] **POTATO-GROW-010 · Service without capture:** add concrete tests for helping that increases another person's capacity without making the helper indispensable.
- [ ] **POTATO-GROW-011 · Rest / dormancy diagnostic:** distinguish restorative dormancy from avoidance using return conditions.
- [ ] **POTATO-GROW-012 · Community exercise:** receive / question / make / share / release as a repeatable non-coercive gathering pattern.
- [ ] **POTATO-GROW-013 · Research neighbors:** maintain links to self-determination, implementation-intention and character-development research without pretending Potatoism is scientifically validated by them.
- [ ] **POTATO-GROW-014 · Interactive test later:** only after the written diagnostic is good, build optional JS interaction; no login, no score-sharing pressure, no permanent identity label.

### Hall implementation status — 2026-10-04

- [ ] **HALL-STATUS-007 · Rendered visual tuning:** once backgrounds are mounted, tune pane opacity, focal crops, mobile composition and contrast against the actual art.
- [ ] **HALL-STATUS-008 · More archive inhabitants:** recover additional named Potatoes / Angels or Dog-role examples only when dated/source-bounded material is strong enough to justify a record.

### Hall of Heroes
- [ ] **POTATO-HERO-002 · Approachability rule:** include ordinary or incomplete examples, not only spectacular Angels; an exemplar should make growth imaginable rather than remote.
- [~] **POTATO-HERO-007 · Angel Army functions:** expand the Army into differentiated service functions and notable missions/works where source material exists.
- [~] **POTATO-HERO-008 · Named Potatoes recovery:** mine conversations/archive for Potatoes with enough dated material for real mini-biographies.
- [~] **POTATO-HERO-011 · Hall visual culture:** continue the Heaven/gold/table/pillars treatment while preserving readability and making the room feel inhabited.
- [ ] **POTATO-HERO-012 · Cultural artifacts:** connect songs, stories, images, jokes, jobs and works to honored figures when they demonstrate growth.
- [ ] **POTATO-HERO-013 · Hero research note:** incorporate moral-exemplar scholarship carefully: examples can illuminate and motivate without becoming moral proof or commands to imitate.

### Axis / Ladder / North
- [ ] **POTATO-AXIS-005 · Descent companion:** keep Life / Strife / Swamp descent visible as the counter-route without turning the page into a good/bad scoreboard.
- [ ] **POTATO-AXIS-007 · Map legend:** every vertical graphic needs a plain-language legend separating place, orientation, transition and developmental metaphor.
- [ ] **POTATO-AXIS-008 · North-of-North boundary:** distinguish Tim's mature source-center theology from ordinary compass north and from the North political programme.

### Potato of Life / central symbol
- [ ] **POTATO-SYMBOL-001 · Symbol contract:** literal biology constrains analogy but does not prove theology.
- [ ] **POTATO-SYMBOL-002 · Why the symbol works:** deepen storage / dormancy / Eyes / propagation / nourishment / diversity / dependence with good agricultural sources.
- [ ] **POTATO-SYMBOL-003 · Reader transfer:** after each major Potato property, ask one human/system question the reader can carry elsewhere.
- [ ] **POTATO-SYMBOL-004 · Development chronology:** show joke/public identity → Great Book world → practice/philosophy → mature theology/culture.
- [ ] **POTATO-SYMBOL-005 · Symbol failure modes:** explain when the Potato metaphor stops helping or becomes evidence laundering.

### Homepage / reader journey
- [ ] **POTATO-HOME-005 · Inspiration handoff:** use one or two concrete Hero examples rather than another explanatory card grid.
- [ ] **POTATO-HOME-006 · Practice handoff:** show one tiny Potato practice on Home that genuinely works without entering the full system.

### Quality / validation
- [ ] **POTATO-QA-001 · Canonical-job validator:** guard that Grow contains practice language, Hall contains exemplar/testimony language, Axis contains orientation, and Potato of Life contains symbol-definition language.
- [ ] **POTATO-QA-002 · Cross-owner duplicate audit:** flag long duplicated passages among the four owners.
- [ ] **POTATO-QA-003 · Reader payoff test:** every new module must teach something even with all links disabled.
- [ ] **POTATO-QA-004 · Mobile Hall pass:** test the rising Heaven treatment, hero grids and upper table on narrow screens.


### Newly surfaced second-wave gaps — 2026-10-04
- [ ] **POTATO-GROW-015 · Seven-day field practice:** make one week of Potato practice concrete enough to try without prior lore.
- [ ] **POTATO-GROW-016 · Diagnostic outcomes copy:** write useful result language for Soil / Eye / Root / Sprout / Door / Fruit / Seed / Return before any interactive quiz exists.
- [ ] **POTATO-GROW-017 · Before/after journal:** add a tiny weekly reflection format that records conditions, action, observed result and next experiment.
- [ ] **POTATO-GROW-018 · Growth without identity:** add examples of people using Potatoist practices without adopting Potato labels.
- [ ] **POTATO-GROW-019 · Spiritual inflation guard:** explicitly distinguish increased insight from increased specialness, certainty or social rank.
- [ ] **POTATO-GROW-020 · Body / sleep / food bridge:** connect growth to ordinary biological conditions without turning Potatoism into health advice.
- [ ] **POTATO-HERO-014 · Hero gallery ordering:** order entries by lesson/virtue or chronology rather than fame.
- [ ] **POTATO-HERO-015 · Ordinary hero quota:** ensure the Hall contains quiet examples of learning, repair, work and persistence alongside spectacular Angels.
- [ ] **POTATO-HERO-016 · Regression / return examples:** include at least one story where a figure loses ground, repairs and grows again.
- [ ] **POTATO-HERO-018 · Hall visual inhabitants:** add subtle upper-hall figures / table / banners / clouds without sacrificing text contrast.
- [ ] **POTATO-HERO-019 · Hall opening scene:** write the arrival into Heaven as a short scene before the first testimony.
- [ ] **POTATO-AXIS-009 · Orientation vs morality:** make explicit that “up” is symbolic orientation and does not automatically make every upper-positioned thing morally superior.
- [ ] **POTATO-AXIS-010 · Return route:** make downward return from insight/service as prominent as upward ascent.
- [ ] **POTATO-AXIS-011 · Human-scale map:** add a tiny non-mythic example beside each major symbol: Door = decision/state change; Ladder = learned pathway; Axis = reference/orientation; North = chosen higher-order reference.
- [ ] **POTATO-SYMBOL-007 · Potato diversity lesson:** use cultivar diversity and environmental adaptation to deepen “same lineage, different viable forms.”
- [ ] **POTATO-SYMBOL-008 · Storage / release lesson:** distinguish healthy reserve from hoarding across energy, money, knowledge and attention.
- [ ] **POTATO-HOME-007 · One live practice:** put one tiny usable Potato exercise on Home, not just a route.
- [ ] **POTATO-HOME-008 · One hero glimpse:** surface one short Hall testimony on Home so inspiration is visible before the click.
- [ ] **POTATO-QA-006 · Four-owner nav crawl:** audit every public link to Potato practice, Angels/Heroes, Axis and Potato of Life for wrong-owner routing.


### Garden / Eden interactive map — 2026-10-05
- [ ] **GARDEN-010 · Final raster art:** export the approved high-resolution 2.5D pixel Garden master as assets/visuals/garden-eden-map.webp; the page already auto-upgrades from SVG when this file exists.
- [ ] **GARDEN-011 · Hotspot calibration:** after final raster art lands, tune desktop hotspot coordinates against House, Door, Tree of Life, Tim, dwellers, Mud Tree, sorting procession, Gate, dogs, river and lower plane.
- [ ] **GARDEN-012 · Animated accents:** create tiny isolated GIF/WebP overlays only where motion clarifies the place: river shimmer, Tree-of-Life glow/leaves, angel wings, Tim idle/gesture, Mud Tree drip, escort walk, Gate glow and dogs at boundary.
- [ ] **GARDEN-013 · Motion budget:** keep the static image fully usable without animation; lazy-load optional accents, honor reduced-motion, and cap simultaneous loops.
- [ ] **GARDEN-014 · Tim portrait sprite:** replace the temporary TD/crown guide badge with a small pixel portrait matching the Garden king-gardener identity.
- [ ] **GARDEN-015 · Walk-with-Tim copy pass:** tighten every stop to one welcome sentence, one meaning sentence and one deeper link.
- [ ] **GARDEN-016 · Genesis citation pane:** add compact verse references for Garden planted, river, work/keep, two trees, eating, exile and guarded way without turning the map into a Bible article.
- [ ] **GARDEN-017 · Browser QA:** verify GitHub Pages deploy, hotspot focus/keyboard use, mobile horizontal map, TTS exclusions, image LCP and page contrast.

## Stability / mobile / performance pass — 2026-10-07

- [x] **STABLE-000 · Retired journey ribbon cleanup:** removed the globally fixed House journey ribbon runtime/CSS that had already stopped rendering; dedicated Elevator remains the owner of journey replay/history.

- [x] **STABLE-001 · Mobile header seam:** remove the old narrow-screen shell shadow/accent seam and make Heaven / Plane / Below use one painted 2172×239 artboard crop.
- [x] **STABLE-002 · Mobile hotspot parity:** project mobile arrow/Room hit areas from the same height-scaled artboard used to paint the cropped panorama.
- [x] **STABLE-003 · Elevator resize consolidation:** replace duplicate window resize handlers with one rAF-coalesced geometry refresh for clearance + hotspots.
- [x] **STABLE-004 · Hidden-tab counter work:** pause the 100,000 Hours live counter while the document is hidden and stop it on pagehide.
- [x] **STABLE-005 · Mobile Home compositor budget:** use one stable preloaded Heaven realm on <=700px instead of three full-screen scroll-linked realm layers.
- [ ] **STABLE-006 · Mobile visual regression set:** capture 320 / 390 / 430 / 768px screenshots for Heaven, Plane and Below and compare frame edge, plaque crop, lower seam and page-nav clearance.
- [ ] **STABLE-007 · Home scroll-profile:** browser-profile the desktop Home realm crossfade after deployment; measure paint/compositor cost and verify it stays smooth on integrated graphics.
- [ ] **STABLE-008 · Below-fold Home rendering experiment:** test restoring `content-visibility:auto` only for deep Home sections with stable intrinsic sizes; keep it only if scroll position and realm timing remain deterministic.
- [x] **STABLE-009 · Specialist glass audit:** remove live backdrop blur from ordinary and specialty reader surfaces, the fixed Access dock, TTS drawer and Garden overlays; keep readability through static material opacity instead of continuous backdrop sampling.
- [x] **STABLE-010 · Garden motion budget verification:** whisper/falling-fruit timers are single-instance, pause while hidden, honor reduced motion and now stop explicitly on pagehide.
- [ ] **STABLE-011 · World Map runtime module budget:** use the existing map telemetry/auditor to identify compatibility modules, duplicate style/control owners and provider requests that can be retired or lazy-loaded.
- [x] **STABLE-012 · Long-page timer inventory:** active recurring intervals are limited to the visibility-gated Garden whisper cycle and user-triggered Elevator replay; both now have explicit shutdown paths, including pagehide.
- [x] **STABLE-013 · Shared House JSON promise cache:** Elevator, Access, House Journey, House, Rooms, Home projection and topology context reuse one in-page promise cache so overlapping House metadata URLs do not refetch or reparse independently.
- [x] **STABLE-014 · Duplicate asset guard:** final built pages now fail validation if the same local app CSS/JS asset is included more than once.
- [x] **STABLE-015 · Universal app fingerprinting:** final public build fingerprints every local `app/*.css` and `app/*.js` reference after all shell injectors, preventing stale manual version strings and late unversioned TTS/shell assets.
- [ ] **STABLE-016 · House research-bundle split:** House currently defers a large research/dossier bundle until idle, but still downloads the whole research layer. Split data by selected depth/tab so Overview and Structure never pay Research payload cost until the reader asks for it.
- [ ] **STABLE-017 · Route-scoped House Journey bundles:** split the ~28 KB universal House Journey runtime / ~20 KB CSS into a tiny shared Room guide core plus optional archive/inhabitant/deep-corpus modules loaded only on pages that expose those surfaces.
- [ ] **STABLE-018 · Browser performance budget CI:** add a real browser smoke/profile job for representative Heaven, Plane, Below, nested Room, Great Book, Garden and Home routes. Track long tasks, layout shifts, transfer bytes, duplicate requests and scroll responsiveness rather than relying only on static source checks.
- [ ] **STABLE-019 · CSS cascade compaction:** continue removing base/depth/material rules that are unconditionally overwritten later in the same stylesheet. Do this selector-by-selector with visual regression checks rather than bulk minification.
- [ ] **STABLE-020 · Specialty payload review:** audit the largest page-specific bundles (Home, Garden, Bible Study, Halls, Elevator page, News) for route-local lazy modules and unused code before attempting code splitting.

