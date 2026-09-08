# TODO — The Potato of Life / TimDooley

## Current priority — make the repository load, make the data coherent, then deepen what already exists

The repository is now large enough that **duplication, orphaned layers, shallow mirrors, route failures and competing canonical sources are a bigger risk than simply adding more files**. Work in this order:

1. **P0 — site actually loads and CI deploys**
2. **P0 — canonical data ownership and duplicate-layer audit**
3. **P1 — deepen high-connectivity existing records**
4. **P1 — make Culture/Subculture/Sektur/Swamp analytically useful**
5. **P1 — improve population/geography/network extraction**
6. **P2 — expand long-form research and project canon**
7. **P2 — cosmetic/UI refinement after the data contracts are stable**

The graph is the navigation layer, not a substitute for substance. Every important record must first answer **what is this?**, then origin/context, structure/mechanism, evidence, uncertainty, questions, and directional couplings. No length-padding: missing knowledge remains explicitly missing.

## 0. Repository-wide duplication / overlap audit — NEW PRIORITY

The repository contains many files that appear to represent adjacent or potentially overlapping versions of the same subject. Before adding another dataset, determine whether the existing files should be **merged, layered, indexed, or explicitly separated**.

### High-priority overlap families to investigate

- [ ] **Country stack:** `data/nations.json`, `data/country-atlas.json`, `data/country-nodes.json`, `data/country-static.json`, `data/countries-blueprint.json`, `data/countries/*.json`, `data/countries/*-enrichment.json`, `data/country-enrichment-batch-*.json`, `data/country-nodes-batch-*.json`, `data/country-fallback.json`, `data/country-layer-manifest.json`, `data/country-source-registry.json`, `data/country-enrichment-index.json`.
  - Determine canonical identity versus observations versus enrichment versus snapshots versus generated nodes.
  - Do not duplicate the same country prose across layers.
  - Make one country identity resolve to many evidence/observation layers.

- [ ] **Potatoism stack:** `data/potatoism-lexicon.json`, `data/potatoism-lexicon-expanded.json`, `data/potatoism-glossary.json`, `data/potatoism-dossiers.json`, `data/potatoism-deep-layers.json`, `data/potatoism-cosmology.json`, `data/potatoism-concept-map.json`, `data/potatoism-relationships.json`, `data/potatoism-canonical-corpus.json`, `data/potatoism-public-observations.json`, `data/potatoism-research-expansion.json`, `data/potatoism-deep-extrapolation-atlas.json`.
  - Establish canonical term identity.
  - Make glossary/lexicon aliases point to dossiers instead of repeating definitions.
  - Separate canon, observations, research and extrapolation.

- [ ] **Religion stack:** `data/religious-foundations.json`, `data/religious-foundations/records.json`, `data/religious-foundations/index.json`, `data/religious-comparative-library.json`, `data/religious-lexicon.json`, `data/religious-relationships.json`, `data/religious-sources.json`, `data/religious-text-library.json`, `data/religious-adjacent/records.json`, `data/religious-adjacent/deep-expansions*.json`.
  - One identity record per tradition/formation.
  - Comparison and sources should reference records, not copy them.
  - Preserve internal diversity.

- [ ] **Extremism / movements stack:** `data/extremism-cults-atlas-2026-09.json`, `data/extremism-cults-atlas-expansion-2026-09.json`, `data/extremism-record-enrichments-2026-09.json`, `data/extremist-hate-groups.json`, `data/extremism-terrorism-nrm-expansion.json`, `data/digital-underground-networks.json`, `data/internet-extremism-information-ecology-wave-017.json`.
  - Separate canonical movement identity, enrichment, classifications, online ecology and research waves.
  - Prevent duplicate IDs and contradictory statuses.

- [ ] **Intelligence/security stack:** `data/security-intelligence-organizations.json`, `data/security-intelligence-country-layer.json`, `data/intelligence-security-graph.json`, `data/intelligence-information-ecosystem-atlas-wave-016.json`.
  - Identity → institutional facts → country coupling → graph → research wave.

- [ ] **Swamp stack:** `data/swamp-ecology.json`, `data/swamp-research-seeds.json`, `data/swamp/*`, `docs/FARM-SEKTUR-SWAMP-THEORY.md`, `docs/SWAMP-ATLAS.md`, `docs/SWAMP-DATA-INGESTION.md`, `docs/SWAMP-RESEARCH-2026-09.md`.
  - Define which files are ontology, methodology, research seeds, empirical records and project-symbolic material.
  - Do not turn Swamp into a generic conspiracy bucket.

- [ ] **Research stack:** `data/research.json`, `data/research-expansion-2026.json`, `data/research-frontier.json`, `data/research-source-expansion-2026.json`, `data/research-carvings-2026-09.json`, `data/research/*`, `data/expansions/*`.
  - Establish source/citation registry versus research claims versus expansion waves.
  - Stop repeating the same research summary in multiple wave files.

- [ ] **Graph stack:** `data/relationships.json`, `data/evidence/relationships.json`, `data/religious-adjacent/relationships.json`, `data/religious-relationships.json`, `data/potatoism-relationships.json`, `data/domain-coupling.json`, `data/cross-domain-couplings.json`, `data/global-graph-bridge.json`, `data/graph-registry.json`.
  - Define canonical edge ownership and derived relationship views.
  - Avoid multiple authoritative copies of the same edge.

- [ ] **Architecture/documentation stack:** `README.md`, `PROJECT-README.md`, `docs/MASTER-ARCHITECTURE.md`, `docs/MASTER-FRAME.md`, `docs/UNFOLDING-ARCHITECTURE.md`, `docs/REPOSITORY-COVERAGE-AND-CARVING-MAP-018.md`, `data/project-workflow.json`.
  - Mark one document as canonical architecture and make the others scoped explainers.

### Duplication rule

- [ ] Every overlap family must declare `canonical_owner`, `derived_from`, `role`, `update_policy` and `do_not_duplicate`.
- [ ] Add an automated duplicate/overlap audit to CI.
- [ ] Prefer references and joins over copying long descriptions between files.
- [ ] If two files genuinely contain different epistemic layers, keep both and make the distinction explicit.

## 1. P0 — immediate engineering blockers

- [x] Harden extremism rendering against scalar/array/object schema differences.
- [ ] Verify the deployed Pages build actually contains the hardened extremism page; do not call the live bug fixed until verified.
- [x] Fix the static route audit so runtime template URLs are not mistaken for literal IDs.
- [ ] Run the full GitHub Actions chain after the audit fix.
- [ ] Verify `repository.html` renders its tree and does not fail on unknown/malformed records.
- [ ] Verify every major page has the canonical header and valid asset paths.
- [ ] Verify dynamic node routing for events, Hawkins, research, geometry, Potatoism and nation records.
- [x] Add initial `scripts/audit_content_depth.py` to rank shallow records; run it and commit its generated report.
- [ ] Add route-contract and schema-normalization checks to CI.
- [ ] Add information-density checks so shallow records are ranked instead of silently accepted.
- [ ] Add a JSON parse sweep over every `data/**/*.json` file.
- [ ] Add duplicate-ID and alias-collision sweep across all registered datasets.
- [ ] Add missing-local-file/reference sweep for manifests, registries and backend entries.
- [ ] Add stale-path sweep for deleted/renamed files.

## 2. P0 — pages and deployment bugs to hunt

- [ ] **Repository page:** verify all fetches, bucket classification, empty datasets, malformed records and dynamic links.
- [ ] **Movements/extremism page:** verify root `extremism-renderer.js` is the deployed renderer; do not accidentally rely on `scripts/extremism-renderer.js` because `build_site.py` excludes `scripts`.
- [ ] **Culture page:** remove remaining inline style blocks and move presentation into CSS; add robust handling for malformed arrays/objects.
- [ ] Audit every HTML page for JavaScript exceptions caused by assuming arrays/strings when data can be objects/scalars.
- [ ] Audit every page for `fetch()` paths that work locally but fail under GitHub Pages base paths.
- [ ] Audit nested pages for incorrect relative asset paths.
- [ ] Audit all `node.html?id=...` routes against actual resolver coverage.
- [ ] Audit nation redirects and nation dossier IDs for aliases such as Turkey/Türkiye and Palestine/State of Palestine.
- [ ] Audit geometry query parameters against `geometry.html` support.
- [ ] Audit book readers for large-text loading, encoding and missing local corpus paths.
- [ ] Audit timeline for continuous zoom, pointer capture and lens rendering failures.
- [ ] Audit header injection so canonical shell is actually applied after build, not just present in source.
- [ ] Remove/disable competing deployment paths if they can produce different `_site` output.

## 3. P0 — deployment architecture

- [ ] Confirm only `pages.yml` deploys production.
- [ ] Confirm legacy Jekyll workflow cannot accidentally deploy a stale site.
- [ ] Run build → shell audit → web audit → Pages artifact → deploy in one successful Actions run.
- [ ] Verify live `repository.html`, `extremism.html`, `culture.html`, `node.html` and `nation.html` after deployment.
- [ ] Record the verified deployment commit in the repository audit.

## 4. P1 — content duplication / canonicalization work

- [ ] Finish the overlap families above before multiplying more wave files.
- [ ] Build `data/canonical-record-registry.json` mapping every important ID to one canonical record and any derived views.
- [ ] Build `data/canonical-source-map.json` mapping dataset → owner → consumers → update policy.
- [ ] Give every major record an explicit `record_role`: canonical, enrichment, observation, derived, index, source, research, symbolic, extrapolation or archive.
- [ ] Make generated/derived records visibly distinct from authored/canonical records.

## 5. P1 — 40-file deepening programme

The original 40-file programme remains active, but **do not deepen duplicate copies independently**. First establish canonical ownership, then deepen the owner and enrich through references.

Priority order inside the existing programme:

### P1-A — highest-value structural files
1. `repository.html`
2. `data/repository-spine.json`
3. `data/atlas-manifest.json`
4. `data/backend.json`
5. `data/backend-coverage-map.json`
6. `data/global-graph-bridge.json`
7. `data/graph-registry.json`
8. `data/relationships.json`
9. `data/meaning-layer.json`
10. `data/deep-entry-schema.json`

### P1-B — high-connectivity content
11. `data/nodes.json`
12. `data/events.json`
13. `data/people-registry.json`
14. `data/nations.json`
15. `data/country-static.json`
16. `data/country-nodes.json`
17. `data/extremism-cults-atlas-2026-09.json`
18. `data/extremism-record-enrichments-2026-09.json`
19. `data/religious-foundations/records.json`
20. `data/religious-adjacent/records.json`

### P1-C — culture / subculture / Swamp analytical layer
21. `data/culture-ontology.json`
22. `data/cultures-2026-09.json`
23. `data/subculture-research-map.json`
24. `data/swamp-ecology.json`
25. `data/swamp-research-seeds.json`
26. `data/influence-organizations-2026-09.json`
27. `data/security-intelligence-organizations.json`
28. `data/security-intelligence-country-layer.json`
29. `data/population-pass-2026-09.json`
30. `data/cross-domain-couplings.json`

### P1-D — symbolic/research depth
31. `data/meaning-layer-symbolic.json`
32. `data/potatoism-dossiers.json`
33. `data/potatoism-cosmology.json`
34. `data/potatoism-relationships.json`
35. `data/hawkins-scale.json`
36. `data/geometry-records.json`
37. `data/research-carvings-2026-09.json`
38. `data/research.json`
39. `data/religious-comparative-library.json`
40. `data/potatoism-deep-extrapolation-atlas.json`

## 6. Culture — make it analytical, not decorative

- [ ] Define Culture as creation → encoding → transmission → attention → reception → participation → reproduction → mutation → selection → institutionalization → memory → new creation.
- [ ] Add cultural objects: music, film, television, books, journalism, games, art, fashion, food, architecture, rituals, memes, symbols, websites and software.
- [ ] Add participant roles: creator, performer, producer, publisher, distributor, platform, curator, critic, archivist, educator, audience, fan, remixer, sponsor and regulator.
- [ ] Add population concepts: exposure, audience, participant, self-identified member, organizational member, producer and core participant.
- [ ] Add geography: country, region, city, venue/institution where appropriate, diaspora and online space.
- [ ] Add propagation edges: migration, technology, commerce, education, media, social network, imitation, conflict, institution and platform.
- [ ] Model Subculture, Sektur and Swamp as strongly overlapping but non-identical concepts.
- [ ] Add measurable outputs: population, geography, network centrality, clusters, bridges, propagation, fragmentation, emergence, institutionalization and persistence.
- [ ] Add Culture coupling panels to people, nations, religions, movements, organizations, technologies, wars and places.
- [ ] Build a Culture research interface that answers **what is it, who makes it, who consumes it, how does it spread, where is it, who connects it, and what changes because of it?**
- [ ] Expand the current seven/eight culture records before adding a large taxonomy.
- [ ] Add explicit `population_observations`, `geography`, `objects`, `organizations`, `media_channels`, `economic_links`, `historical_phases`, `evidence` and `uncertainties` fields where evidence exists.

## 7. General depth rule

- [ ] Important entries should provide at least one page of substantive reading; major subjects should exceed that where evidence permits.
- [ ] Definition first. Context second. Mechanism third. Couplings fourth. Evidence/uncertainty/questions after that.
- [ ] Graph edges never substitute for the dossier itself.
- [ ] Never invent population numbers, secret relationships, diagnoses or causal claims to fill empty fields.
- [ ] Distinguish documented, observed, self-described, estimated, scholarly, legal finding, government designation, reported, disputed, alleged, symbolic and unknown.
- [ ] Every important coupled entity must resolve to its own record.
- [ ] Do not create a second “deep” copy of a record just to increase word count.

## 8. Analytical outputs to build from the data

- [ ] Population/group-size estimates with explicit evidence classes.
- [ ] Geographic concentration maps.
- [ ] Cultural/subcultural cluster analysis.
- [ ] Graph centrality and bridge analysis.
- [ ] Propagation/diffusion timelines.
- [ ] Mainstream ↔ subculture transitions.
- [ ] Organizational overlap and predecessor/successor analysis.
- [ ] Cultural/economic relationships.
- [ ] Political/media/institutional coupling analysis.
- [ ] Historical emergence and fragmentation analysis.
- [ ] Research queues ranked by connectivity × importance × missing depth.
- [ ] Generate derived statistics from canonical records rather than hand-entering totals in multiple files.

## 9. UI / reading experience

- [ ] Repository must load even when optional datasets fail.
- [ ] Every major page needs readable long-form dossiers, not only cards/tooltips.
- [ ] Add table of contents, reading time, word count, related research and read-next where useful.
- [ ] Keep index pages fast; put dense reading in expandable/full-entry views.
- [ ] Standardize the canonical header through the build-time site shell.
- [ ] Keep page-local 2D/3D controls out of the global header.
- [ ] Remove inline styles from new pages and move them to shared/page CSS.

## 10. CI / integrity

- [x] Node 24-compatible GitHub Actions.
- [x] Nested web asset audit.
- [x] Research-carving backend registration.
- [x] Initial content-depth auditor added.
- [ ] Run content-depth auditor and commit current ranked output.
- [ ] Route-contract validator.
- [ ] Duplicate-ID and alias-collision validator.
- [ ] Missing-vs-uncertain data validator.
- [ ] Provenance/project-theology status validator.
- [ ] Stale-current-status validator.
- [ ] Country-refresh smoke test with snapshot preservation.
- [ ] Full validation + build + Pages deployment verification before declaring the repository healthy.

## 11. Bugs/errors discovered or likely — keep adding here

- [ ] Repository tree has a large dynamic classifier; verify every branch is reachable and no valid records silently fall into the generic Worlds bucket.
- [ ] Repository currently loads many optional datasets in parallel; confirm a failed optional fetch cannot erase otherwise valid records.
- [ ] Repository's `arr()` helper currently returns `[]` for object-shaped collections; audit all datasets where `records`/`entries` may be objects or keyed maps.
- [ ] Culture page currently uses extensive inline styling; move to CSS and add robust schema normalization.
- [ ] Extremism has both root `extremism-renderer.js` and `scripts/extremism-renderer.js`; establish one canonical renderer and one build path.
- [ ] Build script excludes `scripts`; any runtime asset stored there will not be deployed unless explicitly copied.
- [ ] Multiple deployment/workflow files exist; verify there is no stale Jekyll output path.
- [ ] Large numbers of country files share nearly identical base sizes; run a content-depth and duplicate-content audit to distinguish useful templates from repeated filler.
- [ ] Many wave/expansion files likely contain repeated descriptions; identify duplicated IDs and copied prose before further enrichment.
- [ ] `data/depth-audit.json` is an audit contract, not a live scan; generate the live audit and compare it to the contract.
- [ ] Verify `node.html` supports every record family that repository/culture/movement pages can link to.
- [ ] Verify geometry routes, nation routes and Hawkins routes against their actual page contracts.
- [ ] Verify all HTML fetch paths under GitHub Pages deployment/base-path conditions.
- [ ] Search for orphaned files that are never registered by any manifest/backend/page.
- [ ] Search for registered files that no longer exist.
- [ ] Search for IDs differing only by aliases, spelling, punctuation or country naming conventions.
- [ ] Search for contradictory current-status fields across datasets.
- [ ] Search for relationship endpoints that exist only in research-wave files but are treated as canonical graph nodes.

## 12. Research / information rule

Before adding information to a file, ask:

1. **What does this let us determine?**
2. **What population can it locate or estimate?**
3. **What geography can it map?**
4. **What relationship can it establish?**
5. **What chronology can it reconstruct?**
6. **What propagation mechanism can it expose?**
7. **What statistic can be derived?**
8. **What uncertainty does it reduce or make explicit?**

If the answer is “nothing beyond making the paragraph longer,” do not add it.

## Research principle

**See the connections. Read the substance.**

The repository should not become a giant pile of facts. Every file must have a purpose, every important record must stand independently, and every relationship must make it possible to answer a question, trace a mechanism, compare systems, locate a population, follow propagation, or understand how one part of the world changes another.
