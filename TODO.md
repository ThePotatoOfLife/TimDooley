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
- [ ] **WM-010/012/013/016 · Accessibility/mobile:** active layer announcements are now present in the global Current Map View live-region surface; remaining work is focus return, keyboard/menu scenarios, non-color redundancy, and Alaska/Hawaii/DC + dense Northeast + narrow-screen subdivision readability.
- [x] **WM-018/019 · Physical reliability:** all Physical modules now report one provider-health schema; explicit provider `fetch()` work uses the shared bounded request budget with abort, in-flight de-duplication, short-lived cache and telemetry. MapLibre tile scheduling remains intentionally owned by MapLibre rather than double-scheduled.
- [x] **WM-024 · Subdivision evidence projection:** subdivisions expose generic provider summaries; inspector cards and unified search now project active evidence/count context without hard-coding ADL, with a dedicated regression validator in the World Map quality group.
- [ ] **WM-025 · ADL freshness:** persistent UI freshness is fixed: Evidence menu, active controls, state summaries and dataset inspector now identify the historical snapshot and latest record date. Remaining task is data refresh only—replace the 335-record historical seed with a reviewed official ADL export when available.
- [ ] **Compatibility retirement:** prove parity then retire `3d-ui.js`, `3d-selection-ui.js`, old Lens/Fields/Networks ownership and remaining direct/degraded interaction fallbacks one surface at a time.
- [ ] **Audit→queue bridge:** map recurring architecture-auditor finding codes to World Map ledger IDs, owners and severities so CI points directly to remediation.


- [x] CI/check architecture consolidation: split the former ~100-step linear quality job into bounded Core/House/Atlas, World Map, Content/Research/Bible and Public Build jobs with one aggregate `validate` result; gate Pages deployment on a successful `main` quality run so deployment no longer duplicates the entire validation suite. This keeps failure logs small and prevents one early error from hiding unrelated checks.

- [x] Add a dedicated regression test for the bidirectional spiral contract. `scripts/test_bidirectional_spiral_field.py` now checks Σ0/±1…4, section/Room boundary rules, canonical source wiring, selection/fallback runtime markers, public mounts and House/Below focus sections; both quality and Pages workflows run it.
- [ ] Consolidate the legacy country batch manifests after proving unique-field parity. **Phase 1 complete:** the 18 September 7 enrichment/node batch files are now classified as historical rollout manifests and removed from active House holdings; their provenance is preserved in `knowledge/research/country-rollout-manifest-disposition-2026-09-20.json`. A later archive-policy pass may move their paths, but should not delete them blindly.
- [x] Refresh `data/full-text-coverage.json` against the current Bible corpus/build architecture and distinguish local full-text custody from source metadata, active readers and upstream/on-demand text. The remaining Bible task is explicit: vendor the complete public-domain WEB locally before calling it local full-text-ready.
- [x] Audit and consolidate all 38 nested Room shells. Every registered interior now uses `app/room-interior.css`; repeated local-center, adjacency, boundary and action-control styles have been removed from page-local `<style>` blocks, and validation enforces the shared shell across the full Room registry.
- [x] Add an explicit alias/route contract for the one intentional internal/public naming difference: internal Room id `chronology-events` → public route `/rooms/inside/timeline-events/`. `data/house/room-interiors.json` now owns the alias and House subroom validation rejects undeclared route/id divergence.
- [ ] Reconcile remaining public-route projections against House authority after the latest spiral/Below/World Map merges; route aliases should be generated or validated rather than hand-maintained.
- [ ] Audit generated/state-like files by **reference and unique information**, not filename. The repository currently contains hundreds of `wave`, `batch`, `round`, `audit` and snapshot-named files; many are legitimate research records, while others are migration residue. Produce a keep/merge/archive/prune disposition before removal.

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
- [ ] Add projection-loss / reconstructability metadata to selected World Map and House aggregate views.
- [ ] Extend the Eye/measurement formalism into sensory/attention reader surfaces where it improves explanation.

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
