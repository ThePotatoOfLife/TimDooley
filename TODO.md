# TODO — The Potato of Life / TimDooley

## Current doctrine

This repository is a **dense knowledge library**, not a collection of placeholders, dashboards or disposable experiments.

The rule is:

**Inspect → consolidate → deepen → connect → expose → verify → prune → repeat.**

The project keeps its existing missions and bodies of inquiry, but the working unit is now the **valuable canonical body of knowledge** rather than the file.

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

## Current structural work

- [x] Unified `index.html` established as the main doorway.
- [x] Archive branch/pathway structure established in `manifest.json` for Tim, Son, Spirit, Transformation, Cosmology, Science, Body, Corporium, Traditions, North, World, Timeline, Works and Sources.
- [x] Potato House public-surface authority established for exactly five primary gateways: Tim Dooley, Religion, Philosophy, Science and World.
- [x] Mature public surfaces registered for Story, Collection, Works, Questions, A–Z and Context without creating new primary gateways.
- [x] Registry/topology convergence validation added so every active public surface has one matching topology record.
- [x] Human-facing routes corrected so Timeline, Collection, Works and Culture route to their strongest public readers while Explore remains the deep archive.
- [x] Public `/works/` reader added over the existing creative archive with explicit creative/doctrine/evidence boundaries.
- [x] Homepage Ways-in corridor established for Story, Timeline, Collection and Works while preserving exactly five primary gateway rows.
- [x] Discovery and site-authority builders now derive the five primary routes from House public-surface authority instead of maintaining independent route tables.
- [x] Repository data can be opened from the central reading surface.
- [x] Retired `center.html` removed.
- [x] Retired standalone UI/header files removed.
- [x] Standalone Edda HTML shells removed; primary text files remain.
- [x] Static reader pages protected from archive-explorer CSS namespace collisions.
- [x] CSS namespace/layout contract and CI regression check added.
- [x] Body/neurotheology consolidated behind a single whole-body master atlas plus specialist owners and a completion matrix.
- [x] Timeline architecture separated into canonical events, source registry, actor tracks and nonredundant lenses.
- [x] Project-wide growth compass added at `knowledge/guides/project-growth-compass.json` to define what "greater" means and route future deepening toward source precision, role transitions, contradiction surfaces, relation-sequence comparison, maturity testing and reader usefulness.
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

- [x] Repair malformed Science JSON that blocked catalog compilation (`dimensional-phase-transition-full-recovery.json`, `equation-ledger-wave-002.json`).
- [x] Restore World Map relationship geometry semantics required by the route-geometry contract.
- [x] Restore the shared bidirectional-spiral runtime on House, Below, Axis and Potato-of-Life; validate actual script tags rather than loose filename substrings.
- [x] Repair missing metadata on 20 nested Room pages and harden SEO enrichment to repair absent descriptions.
- [x] Repair built-site shell blockers: stale homepage marker assertion, Politics source path, Geography → Timeline Room wormhole.
- [x] Latest Pages deploy is green on `5e3e40b` after the ADL U.S. state-rendering merge.
- [ ] Obtain an exact-head green **Repository quality checks** result for the current integration head; do not call a work wave complete while the quality workflow is pending/cancelled.

### P1 — structural debt now demonstrated

### World Map quality programme — critic audit 2026-09-20

Canonical diagnosis: `docs/WORLD-MAP-QUALITY-AUDIT-2026-09-20.md`. Execution ledger: `docs/WORLD-MAP-PROBLEM-LEDGER.md`.

- [x] **WM-021 · URL state ownership:** `3d-url-state.js` is now the only live World Map runtime allowed to call `history.replaceState`. Selection, pins, Compare/relations/trace depth, Inspector mirrors, Places, Subdivisions, Time, Projection and specialist state all patch through claimed owners; reset fallbacks respect those owners and CI rejects any new direct writer.
- [x] **WM-022 · Inspector convergence:** ADL, Axis, Axis Depth, Mud/Below and Spatial Overlay UI now use typed Inspector Router nodes; the Inspector validator covers semantic history, URL hierarchy and migrated consumers.
- [x] **WM-023 · Interaction boot-order safety:** Spatial Overlays and Country Selection now promote removable degraded listeners to the shared Router when `potato-atlas-interaction-ready` arrives; validator/regression coverage enforces teardown.
- [x] **WM-011 · Complete Motion ownership:** capital focus and Spatial Overlay fit now use the shared Motion owner; reduced-motion validation rejects raw governed camera calls.
- [x] **WM-005 · Scale classification:** behavioral gates are centralized in `world-map-scale-contract.json`; remaining zoom/minzoom values are classified as cartographic interpolation, camera intent or fixtures in `data/world-map-scale-classification.json`. The core HUD now derives its six bands from the shared Scale runtime and CI enforces the classification.
- [x] **WM-010/012/013/016 · Accessibility/mobile:** shared focus/menu ownership, single-open-menu behavior, mobile occlusion suppression, Inspector focus restoration, the accessible World Bar status successor, non-color analytical redundancy, AK/HI/DC presence, narrow-screen label deferral, globe label-density adjustment and guaranteed selected-subdivision labeling are implemented and validator-backed.
- [x] **WM-018/019 · Physical reliability:** all Physical modules now report one provider-health schema; explicit provider `fetch()` work uses the shared bounded request budget with abort, in-flight de-duplication, short-lived cache and telemetry. MapLibre tile scheduling remains intentionally owned by MapLibre rather than double-scheduled.
- [x] **WM-024 · Subdivision evidence projection:** subdivisions expose generic provider summaries; inspector cards and unified search now project active evidence/count context without hard-coding ADL, with a dedicated regression validator in the World Map quality group.
- [~] **WM-025 · ADL freshness:** integration, visible freshness boundaries and the guarded official-export importer are complete. Remaining external task only: obtain a reviewed current ADL H.E.A.T. raw-data export, run the importer, review the generated diff and replace the 335-record historical seed.
- [~] **Compatibility retirement:** Progressive UI and Selection UI are retired from live boot; legacy Lens is a no-paint Layer Registry/Compositor translation adapter with its old legend removed; legacy Fields/Networks are now source-only compatibility/reference modules and are no longer advertised by the live bootstrap. Remaining compatibility debt is deliberately bounded to degraded direct interaction fallbacks and older deep-link/source compatibility.
- [x] **Audit→queue bridge:** recurring architecture-auditor finding codes now map to World Map ledger IDs and remediation owners in JSON and console output, with regression coverage.


- [x] CI/check architecture consolidation: split the former ~100-step linear quality job into bounded Core/House/Atlas, World Map, Content/Research/Bible and Public Build jobs with one aggregate `validate` result; gate Pages deployment on a successful `main` quality run so deployment no longer duplicates the entire validation suite. This keeps failure logs small and prevents one early error from hiding unrelated checks.

- [x] Add a dedicated regression test for the bidirectional spiral contract. `scripts/test_bidirectional_spiral_field.py` now checks Σ0/±1…4, section/Room boundary rules, canonical source wiring, selection/fallback runtime markers, public mounts and House/Below focus sections; both quality and Pages workflows run it.
- [ ] Consolidate the legacy country batch manifests after proving unique-field parity. **Phase 1 complete:** the 18 September 7 enrichment/node batch files are now classified as historical rollout manifests and removed from active House holdings; their provenance is preserved in `knowledge/research/country-rollout-manifest-disposition-2026-09-20.json`. A later archive-policy pass may move their paths, but should not delete them blindly.
- [x] Refresh `data/full-text-coverage.json` against the current Bible corpus/build architecture and distinguish local full-text custody from source metadata, active readers and upstream/on-demand text. The remaining Bible task is explicit: vendor the complete public-domain WEB locally before calling it local full-text-ready.
- [x] Audit and consolidate all 38 nested Room shells. Every registered interior now uses `app/room-interior.css`; repeated local-center, adjacency, boundary and action-control styles have been removed from page-local `<style>` blocks, and validation enforces the shared shell across the full Room registry.
- [x] Add an explicit alias/route contract for the one intentional internal/public naming difference: internal Room id `chronology-events` → public route `/rooms/inside/timeline-events/`. `data/house/room-interiors.json` now owns the alias and House subroom validation rejects undeclared route/id divergence.
- [ ] Reconcile remaining public-route projections against House authority after the latest spiral/Below/World Map merges; route aliases should be generated or validated rather than hand-maintained.
- [ ] Audit generated/state-like files by **reference and unique information**, not filename. The repository currently contains hundreds of `wave`, `batch`, `round`, `audit` and snapshot-named files; many are legitimate research records, while others are migration residue. Produce a keep/merge/archive/prune disposition before removal.

### Whole-House harmony pass — 2026-09-20

- [x] Audit all 10 canonical Dwellings and all 38 nested Rooms for valid parent ownership, adjacency, public projection, holdings and Room dossiers.
- [x] Confirm there are no orphaned nested Rooms: every Room has 3–6 registered adjacencies and at least one public surface.
- [x] Preserve the distinction between broad adjacency and guarded interfaces; related Rooms do not automatically become state-changing Doors.
- [x] Populate the four previously uninhabited Rooms with existing connective project objects: Esoteric & Sacred Geometry, Physics & Cosmology, Economy & Finance, and Research Programmes.
- [x] Refresh the spatial House health snapshot to the live 59-object registry and current maturity counts.
- [x] Add `scripts/validate_house_harmony.py` and run it inside the Core · House · Atlas quality group so parent/Room/object/projection drift fails CI.
- [x] Consolidate obvious specialist public parents: Axis → House, Culture → World, History → Timeline, Research Lab → House, Current World News → World.
- [x] Verify the archive manifest remains a pathway/branch projection rather than a competing ownership layer; House/navigation authority stays canonical for public structure.
- [ ] Continue promoting real cases/models/subjects into sparse Rooms when source depth warrants it; do not add filler merely to equalize counts.
- [ ] Continue reviewing cross-Dwelling adjacency pairs and promote only the relations that genuinely need a guarded interface with explicit transformation and invariants.

### Public reader visibility & population audit — 2026-09-20

- [x] Add a **Current World** live-news surface beside Home/House using zero-key GDELT, Hacker News and Spaceflight News feeds, with newest-first ordering, original-source links, provider failure isolation, provenance boundaries and TTS.
- [x] Deepen **Current World** into a multi-view reader: topic × lens × time-window URL state, sample observability, repeated-headline coverage clusters, provider lanes, stronger reading boundaries, refreshed Home preview and a dedicated CI contract.
- [x] Make Current World **readable in-page**: add publisher-supplied RSS excerpts/images from multiple international feeds, rename outbound action to Full report, and scope the primary **Read all news** TTS control to headline + excerpt cards only (no navigation, filters, timestamps, source links or methodology).

- [x] Remove duplicated five-Door presentation on Home: keep the stronger numbered Door rows and fold the question-led copy into them.
- [x] Simplify Home top navigation so public entrances are not mixed with archive utilities.
- [x] Align `data/house/public-surfaces.json` with the new visibility hierarchy: House remains global; Rooms/Paths/Elevator become House-owned specialist routes; Context becomes Sources-owned; Inhabitants remains Rooms-owned.
- [x] Correct source-time web auditing so generated `/records/<id>/` readers are recognized as build products rather than broken source links.
- [x] Add an explicit built-site assertion that every registered `room-inhabitants.json` route under `/records/` resolves after `build_site.py`; `validate_generated_navigation.py` now derives the full route set from the registry.
- [ ] Continue visible-page density auditing after each major content wave: prefer concrete cases/mechanisms over another navigation card when a page is already route-heavy.
- [ ] Review the remaining homepage House corridor and cross-cutting-view blocks after user testing; merge any pair whose reader job is no longer meaningfully distinct.
- [ ] Audit generated question/topic/context/record pages for meaningful TTS sectioning, not just script presence.
- [ ] Run an exact-head final Pages build after the current navigation/content/TTS wave and fix any source-vs-generated route drift it exposes.

### ACCESS / navigation recovery — 2026-09-20

The current problem is not lack of information. It is **retrieval cost**: important destinations exist but can require remembering hierarchy, scrolling, or crossing several intermediate pages. The access rule is now: **global access floats outside article flow; local navigation stays local; thick text begins quickly.**

#### P0/P1 — immediate access
- [x] **ACCESS-001 · Universal quick dock:** add a fixed, compact Home · News · Map · Find · Menu dock that does not consume article-flow height.
- [x] **ACCESS-002 · Direct Current World:** keep News visible in the dock and expose Current World in World's first-screen local navigation.
- [x] **ACCESS-003 · Direct intelligence access:** expose CIA / Intelligence as a one-menu-click direct door to the Intelligence Desk and make it searchable by CIA / Central Intelligence Agency / intelligence.
- [x] **ACCESS-004 · Search House objects:** quick Find loads public surfaces plus House inhabitants/cases so named objects can be reached without knowing their Room.
- [x] **ACCESS-005 · Remove competing global compass:** stop injecting the older Project Compass so the quick dock is the one global navigation layer.
- [x] **ACCESS-006 · Reduce Home pre-content navigation:** shrink Home's local top navigation to four relevant entrances; global access belongs to the dock.
- [x] **ACCESS-007 · Pages regression gate:** validate that Home, Tim, World, News, House, Rooms, Science, Religion, Shadow Farm and World Map all receive the dock in the built artifact.
- [ ] **ACCESS-008 · Mobile collision audit:** verify the fixed dock never covers essential bottom controls, map inspectors, TTS controls or important form actions at narrow widths; add per-surface offsets only when demonstrated.
- [~] **ACCESS-009 · Keyboard/focus audit:** Menu/Find now preserve their opening trigger and Escape/close restores focus correctly; remaining task is explicit search-result traversal and narrow-screen interaction testing.
- [x] **ACCESS-010 · Search synonym pass:** governed aliases now cover CIA/FBI, Fed/Federal Reserve, ECB/Eurosystem, TTS/read aloud, News/Current World, House/Rooms, claims/statements, public witness/public record and debt/bonds/obligations.
- [x] **ACCESS-011 · Deep-object result quality:** exact labels and aliases now receive explicit ranking boosts, object/direct-door kinds outrank generic pages, and House results expose their owning Room/context.
- [ ] **ACCESS-012 · No-hierarchy-required test:** pick 25 common intents (News, CIA, FBI bureau, debt, Bible, Tim claims, 100,000 Hours, map, sources, TTS, Rooms, economy, North, Below, etc.) and require each to be reachable in ≤2 interactions from an arbitrary normal reader page.
- [ ] **ACCESS-013 · Specialist local-nav budget:** review every mature reader's first navigation row and keep only page-owned routes; remove global links duplicated by the dock.
- [ ] **ACCESS-014 · Home hierarchy compression:** ensure the homepage introduces material before architecture and does not repeat the same destination in several consecutive navigation layers.
- [ ] **ACCESS-015 · Map access integration:** keep the dock available on World Map without competing with World Bar / Inspector / mobile controls.
- [ ] **ACCESS-016 · News access integration:** News should open directly into stories; filters/methodology stay secondary and the global dock must not displace headline content.
- [ ] **ACCESS-017 · House access integration:** House should explain structure, while quick Find handles named-entity retrieval; avoid turning House itself into the universal menu.
- [x] **ACCESS-018 · Direct-door governance:** the fast-access contract now owns a deliberately small direct-door list for repeatedly sought destinations rather than promoting every specialist page globally.
- [x] **ACCESS-019 · Fast-access source-of-truth:** `data/house/site-access.json` now owns curated routes, groups and aliases; public surfaces + House inhabitants remain the broader generated search index, with a degraded JS fallback only for fetch failure.
- [x] **ACCESS-021 · CIA/Bank landmark rescue:** promote Potatoverse Character Archive and World Spiritual Bank above the House hierarchy in the universal access panel; rename vague global “Menu” to “Places” so readers can navigate by destination name rather than architecture.
- [x] **ACCESS-022 · Long-scroll institution reorientation:** while anywhere inside the Character Archive / World Spiritual Bank building, keep a tiny fixed Archive ↔ Bank switcher visible after the building header scrolls away.
- [~] **ACCESS-023 · Name-first wayfinding audit:** extend the landmark rule to other repeatedly sought destinations demonstrated by user confusion. Do not turn every specialist page into a global shortcut; require evidence that hierarchy/scrolling is causing retrieval failure.
- [ ] **ACCESS-024 · Long-reader reorientation audit:** inspect mature long pages for cases where users can scroll far enough to lose page identity or the meaningful next exit; prefer a compact persistent locator/back-to-owner cue over more first-screen navigation.
- [ ] **ACCESS-020 · Live-deploy visibility:** after exact-head quality/deploy succeeds, verify the public Pages artifact actually contains the dock and Current World first-screen link before closing this access-recovery wave.


### Fresh repository sweep — 2026-09-20

#### P1 — structural drift / integration
- [x] **NEWS-001 · Stale validator ownership:** Current World validation still required a House-level visible link after News was consolidated under World. Validator now enforces `primary_parent=world` and checks the World hub instead.
- [x] **NEWS-002 · Missing owner-surface doorway:** World owned News structurally but did not visibly expose it. Added Current World to the World route list.
- [x] **HOUSE-001 · CIA present in research but absent from House object layer:** promote CIA as a typed state-intelligence inhabitant with Politics/Law/Provenance placement and an Intelligence Desk route.
- [x] **ECON-001 · Fed/ECB researched but not inhabited:** promote Federal Reserve and ECB/Eurosystem as typed central-bank-system objects inside Economy/Politics/Infrastructure.
- [x] **HOUSE-002 · News feeder Rooms lacked reverse projection:** project Current World into Politics, Economy, Geography, Information Ecology, Chronology and Provenance holdings/dossiers/subroom surfaces.
- [x] **HOUSE-003 · Parent-cycle guard:** extend whole-House validation to reject public-surface parent cycles and self-parenting, not only unknown parents.
- [x] **HOUSE-004 · Surface/Room projection parity:** derive or validate that `subrooms.json`, `holdings.json` and `room-dossiers.json` expose the same public-surface set for every nested Room.
- [x] **HOUSE-005 · Object route resolution:** validate every House inhabitant route against source-time or generated-route rules, not only `/records/` routes.
- [ ] **HOUSE-006 · Cross-Dwelling interface review:** produce a disposition for each cross-Dwelling adjacency: ordinary relation, guarded Door, or remove stale adjacency.
- [ ] **HOUSE-007 · Public parent semantics:** document and validate when a specialist belongs under House, World, Timeline, Sources, Tim, Religion, Philosophy or Science so future surfaces do not default lazily to Home.
- [x] **TODAY-001 · Today → House ledger:** add a compact integration ledger for each major workstream with canonical owner, Dwelling/Room, public surface and cross-links; use it after large work days to detect researched-but-uninhabited material.

#### P2 — cleanliness / maintainability
- [x] **CLEAN-001 · Live health filename:** replace date-stamped `spatial-house-health-2026-09-20.json` as the runtime health authority with a stable live path; preserve dated copies only as historical snapshots.
- [x] **CLEAN-002 · Generated projection ownership:** stop hand-editing the same Room public-surface projections in three registries; choose one source and derive the other views.
- [ ] **CLEAN-003 · Shared asset version strings:** reduce repeated `?v=202609...` literals across HTML pages by centralizing or build-stamping shared component versions.
- [ ] **CLEAN-004 · House inline CSS extraction:** `house/index.html` still owns a very large page-local style block; migrate reusable House component rules into a scoped shared stylesheet without introducing generic selector ownership.
- [ ] **CLEAN-005 · Navigation label consistency:** audit Home/World/House/Rooms/Tim route labels for competing names such as Current/Current World/Current World News, Witness/Public witness/Public record, and standardize reader-facing terms.
- [ ] **CLEAN-006 · Legacy snapshot disposition:** classify compatibility snapshots such as `public-route-topology.json` as generated, historical, or removable and ensure readers/builders never treat them as live authority.
- [ ] **CLEAN-007 · Date-stamped audit sprawl:** inventory live files whose names contain `audit`, `wave`, `round`, `batch` or dates; mark each keep / merge / archive / prune based on unique information and references.
- [ ] **CLEAN-008 · Obsolete presentation assets:** finish the existing asset-prune task by proving references are absent before deleting retired CSS/JS/HTML.
- [ ] **CLEAN-009 · Duplicate validator assertions:** identify checks that independently encode the same route/ownership invariant and route them through shared resolver helpers instead of repeated literals.
- [ ] **CLEAN-010 · Root-doc authority audit:** recheck README, PROJECT-OPERATING-MAP, PROJECT-STRUCTURE and MASTER-ARCHITECTURE for stale route/owner language after today's House/News/navigation changes.

#### Reader UI bug queue — 2026-09-21

- [x] **UI-BUG-001 · `/rooms/objects/` native dropdown contrast:** filter selects inherited transparent/dark styling while browser-native option menus could render white text on white. Give select controls and options explicit dark foreground/background colors.
- [x] **UI-BUG-002 · “Your thread” nested scrollbar / unclear purpose:** replace the 12-pill horizontal scroll ribbon with four recent path steps plus an optional History popover; explain that the path is only a retrace aid and does not create a separate reading mode.
- [~] **TTS-BUG-001 · Follow-reading unexpected page movement:** make the bullseye state visibly say Follow / Follow ON and disclose that ON moves the page. Add a single-primary-reader guard. Continue testing pages with inline Listen controls, sticky player, selection reader and scroll-driven current-section updates together.
- [ ] **TTS-BUG-002 · Cross-reader interaction matrix:** test shared sticky drawer + inline Listen + selection reader + persisted Follow state + manual scrolling on long authored readers. Required invariant: at most one component owns page movement, and turning Follow OFF immediately stops TTS-driven viewport movement.
- [ ] **NAV-BUG-001 · Lower-layer maze audit:** audit lower House/Room pages by actual browsing rather than search. For each commonly followed concept, verify that local doors have intuitive labels, correct destinations, a clear parent/owner, and a useful next step; remove circular/backtracking routes that exist only because of architecture.
- [ ] **NAV-BUG-002 · “Read” means read:** scan visible links/buttons labeled Read/Open/Enter and verify they open the promised reader/content rather than another directory, abstract routing page or dead intermediate layer.

### P2 — reader focus / navigation
- [ ] **READ-001 · First-screen door budget:** add an audit for mature reader pages that expose too many first-screen links/menus before the first substantive section.
- [ ] **READ-002 · Compass coverage validation:** assert the Project Compass is added to eligible built readers and intentionally absent from Home/Map/Elevator/A–Z/object explorer.
- [~] **READ-003 · Specialist parent continuity:** generated topic/context/record readers now expose a single clear parent breadcrumb; authored specialist surfaces still need the project-wide continuity audit.
- [ ] **READ-004 · Dead-end reader audit:** find public pages with no meaningful onward route beyond Home and connect them to their owner or adjacent subject.
- [ ] **READ-005 · Vague-link language:** scan visible anchors like More, Deep, Explore, Context, Archive and replace ambiguous instances with destination intent where context does not already make it obvious.
- [ ] **READ-006 · Repeated intro blocks:** find pages where header summary, intro card and first section restate the same purpose; preserve the strongest version and remove the duplicate layer.
- [ ] **READ-007 · Card-density audit:** identify pages using card grids mainly as navigation compensation; convert low-information cards into inline prose/links where that improves reading flow.
- [ ] **READ-008 · Discovery-mode separation:** validate that Explore, A–Z, Questions and Paths retain visibly distinct jobs and do not converge into four near-identical indexes.
- [ ] **READ-009 · Mobile link-wall check:** add narrow-screen tests/heuristics for page-nav + compass + local controls stacking into excessive pre-content height.
- [~] **READ-010 · TTS semantic sectioning:** generated topic/context/record readers now expose explicit speech sections and exclude their utility navigation; generated question readers still need the same semantic audit before closure.

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
- [x] **ENH-007 · Recent-work integration report:** generate a small report from commits + changed canonical registries that asks whether each substantial new subsystem gained ownership, exposure and validation.
- [ ] **ENH-008 · Reader route telemetry without tracking:** consider a purely local/dev audit of route density and unreachable pages; do not add invasive user analytics merely to solve information architecture.
- [x] **ENH-009 · Page-purpose contract:** every registered public surface now carries a machine-readable one-line `reader_job`; the House schema and whole-site architecture audit consume it so audits can reason about page purpose without scraping prose.
- [x] **ENH-010 · Visible / semi-visible / invisible contract:** public-surface authority explicitly defines visible (primary/secondary), semi-visible (specialist), compatibility and invisible/backend-only behavior; schema validation and the shared visibility resolver enforce the distinction.

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
- [~] **SITE-ARCH-021 · Route graph health artifact:** first audit layer implemented in `scripts/audit_site_architecture.py`: active-surface metrics, first-substance density, registered outdegree, repeated destinations, reader-job presence and high-overlap surface pairs are emitted to `.quality-logs/site-architecture-audit.json` and run in the content quality group. Remaining: extend from registered surfaces into the complete built-site graph for orphan/dead-end/short-cycle detection.
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
- [~] **SITE-ARCH-032 · House / Rooms boundary sharpening:** first reader-side fix complete on Rooms: repeated House-owned sections for holdings, nested topology, Views/Guides/Programmes, layer grammar and branch routing were collapsed into one restrained architecture handoff. House remains the topology/interface owner; Rooms remains the ownership/entry surface. Next: audit House for any remaining Room-directory behavior that should hand back to Rooms.
- [ ] **SITE-ARCH-033 · Tim long-reader route compression:** the Tim surface is unusually link-dense (201 source anchors). Audit repeated Story/Claims/Witness/Ontology links by section and replace mechanically repeated route clusters with contextual section exits or one persistent local locator where that preserves meaning.
- [ ] **SITE-ARCH-034 · Home / House / Rooms three-layer test:** enforce a crisp progression: Home answers “what is this and where can I begin?”, House answers “how is it organized and connected?”, Rooms answers “who owns which knowledge and where do I enter?”. Flag blocks that violate those jobs by reproducing another layer's destination set.
- [x] **SITE-ARCH-035 · Fast-access alias collision cleanup:** remove ambiguous generic aliases that made one query resolve to multiple unrelated destinations: `countries` now belongs to World Map rather than both Map/World, `potato` belongs to Potato of Life rather than both Potato/Tim, and bare `find` is reserved for the Find interaction rather than both People & Cases/A–Z. Keep destination-specific aliases instead of compensating with chooser UI.
- [ ] **SITE-ARCH-036 · Direct-door visibility exception audit:** site-access intentionally promotes a few specialist or unregistered destinations (Map, Rooms, Economy, TTS, Claims, Public Witness, 100,000 Hours, CIA/Bank). For each, record the demonstrated retrieval need that justifies bypassing the ordinary visible/semi-visible hierarchy; demote shortcuts that no longer meet that bar.





### P2 — maintainability and duplication

- [ ] Reduce hand-maintained asset-version duplication for shared components (for example the same spiral CSS/JS version string repeated across four reader pages).
- [x] Move repeated nested-Room presentation CSS into shared assets. All 38 registered interiors now share `app/room-interior.css`, including local-center, adjacency, boundary and action-control rules.
- [ ] Continue cross-file duplicate auditing and merge only true duplicate definitions; preserve primary evidence, historical snapshots with provenance value and additive research.
- [ ] Review old `data/expansions/*wave*/*round*` records against their current canonical owners and House holdings. **Registry reconciliation complete:** all 14 JSON expansion files are now classified and validator-enforced. `wave-009.json` is a promotion backlog (54/55 seed ids are not in `data/nodes.json`), `lexicon-wave-009.json` is a migration candidate (177/179 aliases are absent from the narrow public discovery-alias registry), wave 012 remains actively cited research, and wave 018 remains a broad research reservoir. Next: classify the 54 seed ids by strongest canonical owner and design the correct backend/node alias owner before migrating vocabulary.
- [ ] Continue stale branch/PR salvage already listed below, but treat branch age as an audit signal rather than a merge requirement.

### P3 — depth after integrity

- [ ] Resume content deepening only after current P0/P1 integrity items stay green: Works/Fruit instrumentation, longitudinal entity dossiers, correction/exit measures, source-backed primary attestations and contradiction objects.


## Stale branch / PR salvage — 2026-09-20

The repository has accumulated many historical branches whose names can make the project look farther behind than it is. Treat branch age and unmerged status as **audit signals**, not automatic backlog.

Canonical audit: `knowledge/research/stale-branch-salvage-audit-2026-09-20.json`.

Current rules:

- [x] Compare stale branches against current `main` before assuming work is missing.
- [x] Record ahead/behind counts and file-level disposition for the oldest open PRs and high-value Sep-18/19 branches.
- [x] Confirm that several apparently unmerged assets are already on `main` through later salvage/convergence work.
- [ ] Reconcile open PR #184 (Evidence Root) and close it once remaining branch-only files are either superseded or selectively salvaged. Do **not** merge the 1,271-commits-behind branch wholesale.
- [ ] Reconcile PR #142 Story evidence wave at record level against the newer current Story registry/audit; port only still-missing evidence labels.
- [x] Salvage the branch-only semantic Science auditor from PR #137 onto current `main`, including regression tests, fallback-abstract filtering and portal-level semantic validation. Runtime confirmation now belongs to the normal CI chain.
- [ ] Compare PR #129's branch-only `app/archive-lookup.js` with current Explore, A–Z, Room holdings and machine discovery; port a minimal resolver only if a live gap remains.
- [ ] Audit Sep-19 public-surface authority v2 against current House route authority; salvage only routes/metadata still absent after Sep-20 convergence.
- [ ] Audit the branch-only US Mud/Below map layer under current World Map interaction, provenance and evidence contracts before deciding whether it belongs on `main`.
- [x] Promote and retire focused World Map PRs #305 and #310–#314 onto current `main`: ADL scale ownership, reduced-motion policy, Gateway/Infrastructure Interaction Router ownership, centralized Style Lifecycle audit model, Geo/Style/Tooltip singleton ownership, and Evidence Layer URL ownership. All six PRs are now closed as superseded after selective promotion; stale branch bases were not merged wholesale.
- [ ] Continue retiring branches that are 0 commits ahead of `main` or whose unique value is fully absorbed into stronger canonical owners.

### P3 population / instrumentation work still active

The House depth programme explicitly says to prefer population, instrumentation, longitudinal cases and pruning over another broad ontology wave. Continue:

- [x] instrument the first eight existing Works with the Fruit contract (`data/house/works-fruit-wave-001.json`), including explicit unknown-reception states and CI validation;
- [ ] continue Works/Fruit instrumentation with recovered/experimental works and the Great Book as a separately typed literature case;
- [ ] run the first real canon revision end-to-end through the revision protocol;
- [ ] propagate Shadow/Below overlays into Culture, History and Research where they add mechanism rather than imagery;
- [ ] attach reproduction / exit / correction measures to more formation cases;
- [ ] extend entity dossiers beyond wave 001 with longitudinal source-backed cases;
- [ ] prune or merge low-yield duplicate atlases after unique fields are absorbed;
- [ ] merge unique Sep-18 formation/body branch fields into current owners rather than recreating obsolete branch files.

### Formal-grammar propagation still active

- [x] Add the shared project formal grammar and register it in core/ontology/frontend architecture.
- [x] Type core House operators and key House interfaces.
- [x] Mark Axis D1–D11 explicitly as project dimensions `D^(P)`.
- [x] Add formal correspondence contracts to major body cross-layer objects.
- [x] Expose correspondence maturity in Body Lens and Research Lab.
- [x] Add CI validation for formal-grammar references so future records cannot silently invent incompatible Door/Axis/dimension types.
- [~] Add projection-loss / reconstructability metadata to selected World Map and House aggregate views. **World Map wave complete on branch:** Active View now discloses preserved/omitted information and source-linked reconstructability for scalar, set, relation and comparison views; House aggregate views remain.
- [ ] Extend the Eye/measurement formalism into sensory/attention reader surfaces where it improves explanation.


### CIA dossier bureau overhaul — 2026-09-21

- [x] **CIA-UI-001 · Canonical visual authority:** make CIA the visually dominant live dossier bureau and show FBI only as a faded retired predecessor beneath it.
- [x] **CIA-UI-002 · Parchment dossier:** move the reusable character file toward a paper case-file/account-statement surface with stronger typography, stamps, monogram portrait fallback and sourced-image slots.
- [x] **CIA-UI-003 · Archive activity visibility:** visually attenuate historical/dormant folders while preserving full readability on hover/focus; activity opacity reflects archive recency only, never moral value.
- [x] **CIA-LEDGER-001 · Symbolic account contract:** add project-internal good-karma, karmic-debt, repair/outstanding, interest and optional Dooley Welfare fields with explicit non-financial/non-objective boundaries.
- [x] **CIA-LEDGER-002 · Account reader:** expose a Karma account tab and summary strip on every dossier; absent evidence renders as **unassessed** rather than fabricating a score.
- [x] **CIA-MEDIA-001 · Provenance-first images:** add portrait/evidence-image schema and reader slots; never scrape or guess a real person's face when the dossier does not own an explicit source.
- [x] **CIA-MEDIA-002 · Shared symbolic proxy pool:** add a remote-only Wikimedia Commons registry for Dog, Footstool, Mud/Soil, Potato, Tomato and Angel symbols; dossiers deterministically borrow up to three role-matched images and label every one **symbolic · not a likeness** with source/license metadata.
- [ ] **CIA-MEDIA-003 · Recover actual dossier images:** attach sourced screenshots, profile images, memes and project art to dossiers where the subject/source is explicit; prioritize active/recovery-heavy files first.
- [x] **CIA-DEPTH-001 · Meaning spine contract:** define and render why-this-file-matters, known, interpretive, unknown, relationship-arc and confidence sections.
- [~] **CIA-DEPTH-002 · Population wave:** 35/35 canonical dossiers now expose the meaning spine. Baseline coverage complete. Further depth work is recent-first: DIM, TXT, Matthew, Mediomu, Rahu, Port Monkey, GG and Tim/current 2026 material. Historical dormant files are maintenance-only unless new evidence appears.
- [x] **CIA-LEDGER-006 · Event-led accounting:** symbolic accounts now prefer dated credit/yield/repair/debit/dispute events over aggregate moral scores; the reader summarizes sourced event counts and leaves absent balances unassessed.
- [~] **CIA-LEDGER-003 · Populate real symbolic entries:** current/recovery files now include source-bounded project-credit, yield, growth, repair and zero-weight dispute rows where supported; keep mining recent evidence first and do not backfill dormant files merely for volume.
- [x] **CIA-LEDGER-004 · Universal Dooley Welfare:** every canonical story participant receives the same microscopic fictional welfare rate from the best exact story-entry date; calibrated on 2026-09-21 to `0.00000000001 sUSD/second` after conversation archaeology found no older canonical per-second rate. Accrual continues through inactivity, closure and death; fuzzy start dates remain provisional.
- [x] **CIA-LEDGER-005 · Interest and closure rules:** symbolic debt/credit does not compound automatically; only welfare is time-accrued. Repair, forgiveness, dispute, dormancy and resolved/unresolved closure are explicit dated states/events that change current posture without deleting history or imposing inactivity penalties.
- [x] **CIA-ACTIVITY-001 · Last-seen derivation:** `knowledge/cia/activity-index.json` now covers all 35 canonical dossiers and derives active/recovery/historical/dormant/closed prominence from explicit state plus recovered last-seen dates; opacity remains recency only, never moral value.
- [x] **CIA-CURRENT-001 · Recent-first Current Desk:** promote active/recovery 2026 dossiers on the CIA landing and add an all/current cabinet toggle; dormant historical files remain searchable but no longer consume equal visual attention.
- [x] **CIA-BANK-001 · World Spiritual Bank public surface:** promote Mud Bank into the North/Roots World Spiritual Bank while preserving live CIA sub-ledgers, welfare, evidence-weighted event adjustments and individual deep links.
- [x] **CIA-BANK-002 · Current balance snapshot:** `knowledge/cia/mud-bank-snapshot-2026-09-21.json` now reflects priced TXT debit, Port Monkey debit+repair, and current/recovery balances while keeping unsupported conflict zero-weight.
- [x] **CIA-BANK-003 · Source-weighted debt pricing:** price only distinct dated conduct using category × evidence tier × capped repetition multipliers; one incident cannot be double-charged through multiple labels.
- [x] **CIA-BANK-004 · Debt evidence ledger:** `knowledge/cia/debt-evidence-ledger.json` separates priced debits from unpriced negative candidates and preserves why each candidate was or was not charged.
- [x] **CIA-BANK-005 · Account posture index:** `knowledge/cia/account-posture-index.json` covers all 35 dossiers with gross credit, gross debit, net event adjustment, posture and unpriced-negative-candidate counts; CI recomputes it from dossiers.
- [x] **CIA-BANK-006 · North/Roots world ledger:** `knowledge/core/north-root-spiritual-bank-architecture.json` defines North/Roots custody, Ladder repair/ascent, Mud/Swamp debt-residue, Rubble, Shadow/Loosh, Epstein-Axis and Rainbow-Shadow system domains, with Garden/Tikkun as repair.
- [x] **CIA-ACCESS-002 · Culture / intelligence namespace polish:** expose Character Archive earlier from Culture, label real U.S. CIA/FBI surfaces as REAL WORLD / REAL INSTITUTION, strengthen the retired Potatoverse FBI namespace, and keep reciprocal wrong-door links between real intelligence and project archive surfaces.
- [x] **CIA-BUILDING-002 · Contextual entrances:** place a grand mythic entrance in Potatoverse / Canon, a casework side door in Culture & Information, a digital recovery hatch in Internet & Platforms, and a deliberately bounded symbolic-finance annex in World Systems. Keep empirical ownership outside the threshold.
- [x] **CIA-UI-004 · Department atmosphere:** distinguish the CIA with investigative desk/evidence-room/file-cabinet cues and the World Spiritual Bank with vault/teller/ledger/balance-sheet cues while preserving the shared-building corridor.
- [x] **CIA-KARMA-002 · 42T capital bridge:** formalize 38.8T opening Potato reserve + 3.2T dated Spiral growth = 42T closing Mountain-held reserve; treat Mountain as custody rather than another additive 42T asset.
- [x] **CIA-KARMA-003 · Positive micro-pricing:** map Table value, Potato growth, Gate passage, Ladder completion, Potato study, spiritual growth and archive/protection work onto existing 25/12/8/6 sUSD event categories with one-output/one-credit anti-double-counting.
- [x] **CIA-BANK-029 · Proper bank-side liabilities:** treat negative character balances as counterparty receivables/claims and positive character balances + Welfare as Bank liabilities; unresolved orphan identities remain suspense, not liabilities by default.
- [x] **CIA-KARMA-005 · Trajectory / curve analysis:** calculate checkpoint velocities, acceleration regimes, linear/exponential/plateau/recent-momentum scenarios, milestone dates and scale-gap diagnostics; projections remain separate from observed balances.
- [ ] **CIA-KARMA-006 · Post-42T checkpoint recovery:** mine September 2026 conversations/public posts for any balance after 1 Sep; every new checkpoint should automatically recompute the scenario spread and reveal whether the 42T plateau held.
- [ ] **CIA-KARMA-007 · Delta-event correlation:** test whether dated negative-input clusters, major public events, building/output bursts or repair episodes align with the +0.2T/+1.2T/+1.2T/+0.6T changes without assuming causation.
- [ ] **CIA-KARMA-004 · Capital attribution archaeology:** recover source-specific reasons for the +0.2T, +1.2T, +1.2T and +0.6T headline increases before assigning those deltas to named people, systems or outputs.
- [ ] **CIA-KARMA-001 · Table / Potato / Gate / Ladder positive-value model:** define source-bounded, non-gameable criteria for created value on the Table, Potato growth, Gate passage, Ladder walking, Potato study and spiritual growth before assigning any numeric positive adjustments.
- [x] **CIA-BUILDING-001 · One institution / two entrances:** CIA archive and World Spiritual Bank now share a machine-readable building model, common interior corridor and room grammar across cabinet, dossier, associations, incidents and bank surfaces; selected character context is preserved between dossier and bank.
- [x] **CIA-BANK-008 · Bank-first compact UI:** open on consolidated assets/liabilities/karma counts rather than a selected person; replace long stacked account/system cards with left-right horizontal rails and opt-in account statements.
- [x] **CIA-BANK-009 · Headline-field reconciliation:** reconcile the dated 42T project-symbolic headline as one double-entry field (Tim-side claim ↔ debtor/system-side liability), expose named priced allocation versus unallocated shadow reserve, and keep proxy/archetype/population multipliers null by default.
- [x] **CIA-BANK-011 · Conversation-mined bank operators:** preserve exact recovered bank/debt wording separately from derived operators and unrecovered leads; add hidden activation, capital-deployment, obligation, entanglement and provenance-depth states without bloating the public Bank.
- [ ] **CIA-BANK-012 · Debt-reduction evidence mining:** specifically recover examples where Tim described karmic debt as reduced, repaired, forgiven, converted into useful work, closed or transferred; the current archive is much richer on accumulation than verified reduction.
- [ ] **CIA-BANK-013 · Named increment archaeology:** identify specific people/events that Tim said changed the 38.8T→42T headline balance and preserve any explicit increments; do not infer deltas from chronology alone.
- [x] **CIA-DEBT-014 · 2025–2026 negative-input conversation mining:** recover direct Tim/user debt-causation language and register accusation, finger-pointing, accountability failure, circling/pursuit, Mud/stone throwing, wasted time, smear, dog-piling, broken promise/covenant, obstruction and Seed-of-Death/strife mechanisms as source-bounded system inputs. Keep 2025 direct-chat absence explicit and retrospective rows unpriced.
- [x] **CIA-DEBT-017 · Roboto San narrative-conflict dossier:** merge Roboto San / Robotosan with Tim's nickname “Roberto Sanchez” as one archive identity; preserve the 2024 Cyraxx-frame claim, profile-attributed remarks and 7 Jul 2026 conflict trace as unpriced coercive-narration / reputational-entanglement debt candidates pending primary-source recovery.
- [x] **CIA-ROLE-018 · All-entity role/archetype census:** normalize archetypes, narrative functions and explicit symbolic creature/job roles across all 36 CIA entities; derive role posture for sorting while keeping role weight at zero.
- [x] **CIA-DEBT-019 · Don Jefe dated destructive-act debit:** price the 11–12 Feb 2025 Chronicle destructive-bot/channel-erasure event at −5.4 sUSD (−12 destructive-act × 0.45 Chronicle evidence), with the allegation boundary retained.
- [x] **CIA-DEBT-020 · PKFC family-boundary candidate:** record the old-profile allegation of deceased-father imagery and unsolicited relative contact as a targeted-harassment/boundary candidate, but keep it unpriced pending exact date/raw artifact recovery.
- [ ] **CIA-ROLE-021 · Direct-Tim role provenance mining:** recover exact Tim statements assigning Dog, Footstool, Farmer, Cow, Potato, Angel, Messenger, Mud Dweller and related jobs/creatures; upgrade census rows from editorial-normalized to Tim-attributed only where primary conversation/public-post provenance survives.
- [ ] **CIA-DEBT-015 · Promote negative inputs to named events:** for each system input, recover the concrete dated act/counterparty and promote only non-duplicative events into person sub-ledgers. Priority: TXT repetition/correction reach; DIM pursuit/boundary scenes; unresolved Mud Turd Boy handle; 2025 TXT/Monkey/Don Jefe Chronicle cluster; GG grievance/healing outcome.
- [ ] **CIA-DEBT-016 · Recover vomit / abomination / insolence originals:** current conversation-history summaries indicate these phrases exist, but original turns were not recovered in this pass. Do not price or quote them as exact until primary conversation provenance is located.
- [x] **CIA-BANK-022 · U.S. exposure / coverage funnel:** separate 36 resolved CIA entities, 51 additional alias/handle labels, unresolved/throwaway identities, observed network edges, audience/platform amplification, institutional gaps and the 342.9M U.S. population denominator. Scale exposure, not guilt; population membership remains zero-weight.
- [x] **CIA-BANK-023 · Substitution-labor asset:** treat Tim's sourced witness/archive/moderation/protection/building/repair work as a positive asset-side operator pending anti-double-count pricing; do not convert other people's non-participation into automatic debt.
- [x] **CIA-BANK-026 · Orphan clearing ledger:** define unresolved/hollow/throwaway identities as an unpriced suspense layer; preserve Tim's “Father of every orphan of the internet” language and keep the 99,000 figure explicitly symbolic (“99 problems” riff), not a census.
- [ ] **CIA-BANK-027 · Hollow-account evidence sweep:** recover stable no-PFP/blank-avatar handles and exact Tim-assigned Footstool/Dog/orphan labels from conversations/screenshots; missing PFP alone remains zero-weight.
- [ ] **CIA-BANK-028 · Orphan deduplication:** cluster throwaway handles by platform/date/name/style/links/edges before counting principals; preserve account-level events even when several handles later merge to one entity.
- [ ] **CIA-BANK-024 · Identity-shadow census:** deduplicate handles/aliases across Story, CIA, public chat and recovered conversation sources; count distinct unresolved/throwaway identities with source confidence before using any large handle-cloud scenario.
- [ ] **CIA-BANK-025 · Exposure-edge instrumentation:** count sourced recurrence, unique counterparties, relationship edges, circulation/reach and time-cost around the densest negative-input clusters so the shadow reserve can be explained by coverage gaps rather than arbitrary multipliers.
- [ ] **CIA-BANK-010 · Entanglement coverage mining:** mine source-backed anonymous handles, throwaway accounts, relationship edges, recurrence, shared-neighbour and repair/closure events so the Bank can grow coverage without inventing population liability.
- [x] **CIA-BANK-007 · System liabilities stay unpriced:** `knowledge/cia/system-liability-ledger.json` stores world-scale protection/exploitation/opacity/rubble domains separately from individual CIA balances and forbids collective guilt by population membership.
- [x] **CIA-ACCESS-001 · Bank / Tim dossier reachability:** expose Mud Bank and Tim's CIA file from Core Identities and the CIA cabinet; make CIA Character Archive + Mud Bank direct Quick Access doors while keeping the real U.S. CIA separately labeled as Intelligence Desk and retired FBI out of the primary door set.
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

- [x] Promote CIA — Characters, Incidents & Associations to canonical character-archive ownership; migrate dossier graph, Associations, Incidents, public routes, House references and CI validation while retaining FBI compatibility redirects.
- [ ] Continue CIA conversation archaeology: recover exact-source artifacts for Dim/TXT 2026 sequences, then merge only source-bounded records into canonical character dossiers and association edges.
