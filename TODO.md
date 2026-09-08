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

## 0. Canonical ownership audit — completed first pass

A first ownership audit has been performed across the requested overlapping families. The detailed machine-readable consolidation map is now `data/canonical-source-map.json`.

### Country

- **Canonical normalized observations:** `data/country-static.json`
- **Identity:** `data/countries/index.json`
- **Schema:** `data/countries-blueprint.json`
- **Join/overlay manifest:** `data/country-layer-manifest.json`
- **Sources:** `data/country-source-registry.json`
- **Enrichment:** `data/countries/*.json`, `data/countries/*-enrichment.json`, `data/country-enrichment-batch-*.json`
- **Derived graph/page views:** `data/country-nodes.json`, batch node files, `data/country-atlas.json`
- **Fallback only:** `data/country-fallback.json`

The manifest says 195 effective enriched countries while `country-static.json` currently reports 194 canonical records. **Resolve this discrepancy before declaring the country family consolidated.** The country architecture itself already says identity → blueprint → sources → normalized record → relationships. fileciteturn789file0 fileciteturn780file0

- [ ] Resolve 194/195 mismatch.
- [ ] Make `nations.json` an identity/compatibility view, not a second country biography store.
- [ ] Build country ID → observation → enrichment → graph/page join table.
- [ ] Migrate unique batch information before retiring batch files.

### Potatoism

- **Canonical long-form records:** `data/potatoism-dossiers.json`
- **Project-canon corpus:** `data/potatoism-canonical-corpus.json`
- **Deep interpretive layer:** `data/potatoism-deep-layers.json`
- **Indexes/derived views:** lexicons, glossary, cosmology, concept map, relationships
- **Observations:** `data/potatoism-public-observations.json`
- **Research/extrapolation:** research expansion and deep extrapolation atlas

The dossiers explicitly define the long-form entry contract, while the canonical corpus explicitly identifies itself as project canon. fileciteturn759file0 fileciteturn770file0

**Bug found:** `data/potatoism-integration.json` references `data/potatoism-master-corpus.json` and `data/potatoism-entities.json`, but those files are not present on main. fileciteturn777file0

- [ ] Fix those stale integration references.
- [ ] Make aliases resolve to canonical dossier IDs.
- [ ] Remove repeated definitions from lookup layers where they duplicate dossiers.
- [ ] Preserve canon, observation, research and extrapolation as distinct epistemic layers.

### Religion

- **Canonical tradition/formation records:** `data/religious-foundations/records.json`
- **Foundation model:** `data/religious-foundations.json`
- **Foundation index:** `data/religious-foundations/index.json`
- **Canonical adjacent records:** `data/religious-adjacent/records.json`
- **Adjacent enrichment:** three deep-expansion files
- **Derived:** comparative library, lexicon and relationship files
- **Sources/corpus:** religious sources and text library

The religious index already explicitly removed the phantom `enriched-records.json` and defines canonical foundation ownership. fileciteturn763file0

**Known relationship issue:** `data/religious-relationships.json` has five unresolved targets. They are deliberately research candidates, not resolved nodes. fileciteturn786file0

- [ ] Promote unresolved targets only after stable records exist.
- [ ] Compare foundation container vs foundation records field-by-field.
- [ ] Keep main religion, adjacent religion, occult, cult/high-control and comparative categories distinct.

### Extremism / movements

- **Canonical movement identity:** `data/extremism-cults-atlas-2026-09.json`
- **Long-form enrichment:** `data/extremism-record-enrichments-2026-09.json`
- **Expansion:** `data/extremism-cults-atlas-expansion-2026-09.json`
- **Source-specific classification index:** `data/extremist-hate-groups.json`
- **Other research layers:** `data/extremism-terrorism-nrm-expansion.json`, `data/digital-underground-networks.json`, `data/internet-extremism-information-ecology-wave-017.json`

The main atlas already distinguishes hate-group, extremist, terrorist and high-control categories. The older hate-group file contains overlapping IDs and should therefore become a classification/evidence view, not another master list. fileciteturn762file0 fileciteturn781file0

- [ ] Build canonical-ID joins.
- [ ] Detect duplicate IDs/status conflicts.
- [ ] Move unique classification evidence into canonical evidence fields.
- [ ] Keep online ecology as context/network research, not a second registry.

### Swamp

- **Canonical ontology/methodology:** `data/swamp-ecology.json`
- **Research reservoirs:** `data/swamp-research-seeds.json`
- **Documentation:** `docs/FARM-SEKTUR-SWAMP-THEORY.md`, `docs/SWAMP-ATLAS.md`, `docs/SWAMP-DATA-INGESTION.md`, `docs/SWAMP-RESEARCH-2026-09.md`

Swamp should **not own the people, organizations, companies, media or security actors inside it**. It is an analytical overlap layer. The existing ontology already separates evidence levels and warns against inferring secret control from proximity. fileciteturn769file0

- [ ] Audit `data/swamp/*` against the ontology.
- [ ] Move actual entity ownership back to domain families.
- [ ] Keep Swamp relationships derived unless independently promoted.
- [ ] Define Sektur/Subculture as overlapping cultural formations, not automatic Swamp membership.

### Research

- **Durable research claims/facts:** `data/research.json`
- **Research questions/frontier:** `data/research-frontier.json`
- **Source registry:** `data/research-source-expansion-2026.json`
- **Candidate cross-domain expansion:** `data/research-expansion-2026.json`
- **Deep research studies:** `data/research-carvings-2026-09.json`
- **Research/archive directories:** `data/research/`, `data/expansions/`

`research.json` already separates observed evidence from interpretation; research carvings add definition/context/mechanism/dimensions/couplings/sources/extrapolations; the frontier is explicitly a queue rather than a fact store. fileciteturn760file0 fileciteturn778file0 fileciteturn787file0

- [ ] Stop repeating the same research summary across waves.
- [ ] Give claims stable source IDs and canonical target IDs.
- [ ] Promote mature expansion records into canonical nodes only after independent dossiers.
- [ ] Keep frontier questions out of factual counts.

### Relationships

- **Canonical cross-domain edges:** `data/relationships.json`
- **Node/edge schema:** `data/graph-registry.json`
- **Backend-ID bridge:** `data/global-graph-bridge.json`
- **Scoped/derived relationships:** evidence, religious-adjacent, religious, Potatoism, domain-coupling and cross-domain-coupling files

The main relationship registry already holds the broad graph; scoped files should feed or project from it, not compete with it. fileciteturn772file0

- [ ] Add canonical edge IDs and duplicate triple detection.
- [ ] Promote verified/scoped edges into the main registry.
- [ ] Add time/evidence/source fields where appropriate.
- [ ] Generate ranked orphan queues by connectivity.

### Intelligence/security

- **Institutional identity:** `data/security-intelligence-organizations.json`
- **Country coupling:** `data/security-intelligence-country-layer.json`
- **Graph projection:** `data/intelligence-security-graph.json`
- **Research/history:** `data/intelligence-information-ecosystem-atlas-wave-016.json`

The wave is richer in historical cases and public information systems than the compact graph, so it remains a research layer rather than the institutional master. fileciteturn785file0

- [ ] Compare IDs across the four layers.
- [ ] Promote missing agency identities into the canonical organization registry.
- [ ] Keep agency identity, historical cases and allegations separate.

## Consolidation implementation

- [x] Create `data/canonical-source-map.json` with canonical owner, identity, schema, enrichment, derived-view and update-policy assignments.
- [ ] Create `data/canonical-record-registry.json` from actual IDs.
- [ ] Add `record_role` to manifests/datasets: `canonical`, `identity`, `schema`, `observation`, `enrichment`, `derived`, `index`, `source`, `research`, `symbolic`, `extrapolation`, `archive`, `fallback`.
- [ ] Add `derived_from` and `canonical_owner` to layer manifests.
- [ ] Add duplicate-ID, alias-collision and same-claim/same-edge detection.
- [ ] Fix stale paths, starting with Potatoism integration.
- [ ] Migrate unique information before retiring any duplicate-looking layer.
- [ ] Mark retired files rather than silently deleting research history.

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

## 4. P1 — canonicalization and duplication

- [x] Complete first ownership assignment for the seven requested families; see `data/canonical-source-map.json`.
- [ ] Build `data/canonical-record-registry.json` mapping every important ID to one canonical record and derived views.
- [ ] Give every major record an explicit `record_role`.
- [ ] Make generated/derived records visibly distinct from authored/canonical records.
- [ ] Complete migration only after unique information has been compared and preserved.

## 5. P1 — deepening

- [ ] Continue the 40-file programme, but **never deepen duplicate copies independently**.
- [ ] Deepen the canonical owner first, then enrich through references.
- [ ] Prioritize high-connectivity, shallow records over multiplying labels.
- [ ] Use the content-depth audit to rank actual work.

## 6. Culture / Subculture / Sektur / Swamp analytical layer

- [ ] Continue the Culture layer as an analytical system: creation, encoding, transmission, attention, participation, production, consumption, mutation, selection, institutionalization and memory.
- [ ] Add population concepts: exposure, audience, participant, member, producer and core participant.
- [ ] Add geography, organizations, cultural objects, media channels and economic links.
- [ ] Treat Subculture and Sektur as cultural formations that can overlap strongly with Swamp without becoming synonymous with it.
- [ ] Build population, geographic, network, propagation, fragmentation and institutionalization outputs.

## 7. General integrity rules

- [ ] Definition first; context second; mechanism third; couplings fourth; evidence/uncertainty/questions after that.
- [ ] Graph edges never substitute for dossiers.
- [ ] Never invent population numbers, secret relationships, diagnoses or causal claims.
- [ ] Distinguish documented, observed, self-described, estimated, scholarly, legal finding, government designation, reported, disputed, alleged, symbolic and unknown.
- [ ] Every important coupled entity must resolve to its own record.
- [ ] Do not create second “deep” copies merely to increase word count.

## Research principle

**See the connections. Read the substance.** Every file must have a purpose, every important record must stand independently, and every relationship must make it possible to answer a question, trace a mechanism, compare systems, locate a population, follow propagation, or understand how one part of the world changes another.
