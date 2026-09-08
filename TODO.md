# TODO — The Potato of Life / TimDooley

## Operating order

This is the working queue, not a wishlist. Work top-to-bottom. Do not add new data at scale while a higher-level contract is broken.

1. **P0 — establish one trustworthy source of truth for the repository**
2. **P0 — make every route resolve and fail visibly**
3. **P0 — make CI/build/deploy enforce the same contracts**
4. **P1 — finish the blueprint system and migrate every consumer**
5. **P1 — repair cross-domain joins and graph integrity**
6. **P1 — deepen the highest-value entity families**
7. **P1 — make books/full text and research archives robust**
8. **P2 — expand the North Programme / European economic graph**
9. **P2 — deepen Potatoism as a separate, explicitly project-defined layer**
10. **P2 — improve UI/search/navigation after data contracts are trustworthy**

## Current sprint — do these first

- [ ] Run the full CI suite after the latest blueprint and Pages changes; record the first failing job, not just the final red status.
- [ ] Inventory every file in `data/blueprints/` and reconcile the real filenames against `data/blueprint-registry.json`.
- [ ] Remove every stale reference to old blueprint filenames (`*-master.json`, bare blueprint `.json`, old system names) from scripts, data, docs and manifests.
- [ ] Fix the blueprint registry's declared count so it equals the actual contractually registered standalone blueprints; do not count structural sections as files.
- [ ] Audit every blueprint against the meta-blueprint and classify missing fields as required, recommended, optional, derived, unavailable or disputed.
- [ ] Inspect `build_canonical_record_registry.py`; make its output a real ownership/deduplication contract rather than an informational report.
- [ ] Generate a machine-readable canonical-record registry and make CI report duplicate IDs, aliases, slugs and conflicting owners.
- [ ] Audit all `data/religious-foundations*` ownership paths and migrate consumers to the chosen canonical owner.
- [ ] Audit `node.html` against every record family in `repository-index.json`; add explicit route families instead of silently falling through.
- [ ] Add route diagnostics for unknown IDs, malformed IDs, missing data and unsupported record types.
- [ ] Make the Pages deployment run the same essential data/build/stability gates as Atlas CI.
- [ ] Run the deployed site smoke test against the actual GitHub Pages URL after the next successful deployment.

## P0 — repository source-of-truth architecture

- [ ] Define canonical owner / index / enrichment / projection / research / archive roles as a machine-readable contract.
- [ ] Ensure every important ID has one canonical owner or an explicitly documented shared-ID rule.
- [ ] Detect duplicate IDs across unrelated JSON domains.
- [ ] Detect alias and slug collisions that can create ambiguous URLs.
- [ ] Detect records whose declared `blueprint` points to a nonexistent file.
- [ ] Detect records whose `source`, `path`, `owner` or `canonical` references are stale.
- [ ] Detect mirrors that contain competing canonical values rather than derived copies.
- [ ] Add migration metadata when a canonical owner moves.
- [ ] Make generated indexes deterministic in ordering, counts and serialization.
- [ ] Decide which generated files are committed and which are build artifacts; document the rule.

## P0 — routing / frontend contract

- [ ] Build a route matrix: page → input → data source → ID field → resolver → detail renderer → fallback.
- [ ] Make `node.html` the universal resolver for record families that do not have a specialized page.
- [ ] Ensure specialized pages explicitly register their supported families and do not duplicate resolver logic.
- [ ] Audit `repository.html`, `nation.html`, `nations.html`, `belief.html`, `people.html`, `books.html`, `extremism.html`, `potatoism.html`, `timeline.html`, `axis.html`, `geometry.html` and `health.html`.
- [ ] Test literal links and dynamic `?id=` links separately.
- [ ] Test URL encoding for spaces, punctuation, Unicode and long IDs.
- [ ] Ensure empty arrays, missing optional fields and missing files render an explanatory state instead of a blank screen.
- [ ] Add a browser/runtime smoke test for the highest-value routes when a headless browser is available.
- [ ] Verify GitHub Pages base-path behavior for every root-relative asset and fetch URL.
- [ ] Add a small frontend data-loader contract so cache busting, error handling and JSON parsing are consistent.

## P0 — CI / workflow / deployment

- [ ] Run `atlas-check` and Pages after every architectural change until green.
- [ ] Compare `atlas-check.yml` and `pages.yml`; keep their safety gates intentionally aligned without duplicating unrelated audits.
- [ ] Decide whether `backend-coverage.yml`, `expansion-check.yml`, country workflows and text-import workflows overlap or have independent ownership.
- [ ] Keep the disabled legacy Jekyll workflow documented only if it provides useful migration history; otherwise remove it.
- [ ] Ensure workflow permissions are least-privilege.
- [ ] Ensure every generated report has a deterministic path and cannot cause a misleading `upload-artifact` failure after an earlier error.
- [ ] Add CI artifacts for audit reports where they materially help debugging.
- [ ] Add explicit timeouts to long-running workflows.
- [ ] Verify Node 24 compatibility across all JavaScript actions and local JS tooling.
- [ ] Record successful deployment SHA/run IDs in the project log.

## P0 — blueprint contract

- [ ] Enforce the `<subject>-blueprint.json` filename rule for all standalone blueprints.
- [ ] Treat `blueprint-blueprint.json` as the meta-contract, not an ordinary domain blueprint.
- [ ] Reconcile the registry count with the actual files and registry entries.
- [ ] Require purpose, entity, record schema, relationships, evidence, validation and implementation notes unless an explicit exception is recorded.
- [ ] Add inheritance metadata so specialized blueprints can extend shared structures without copying them.
- [ ] Add canonical-owner and frontend-routing metadata to every blueprint.
- [ ] Add acquisition workflow: discovery → source selection → extraction → normalization → validation → provenance → refresh.
- [ ] Add explicit failure modes and known traps to every mature blueprint.
- [ ] Add temporal rules to blueprints where facts change over time.
- [ ] Add uncertainty rules where population, membership, valuation, ownership or attribution cannot be exact.
- [ ] Make each blueprint produce an actionable next-research task, not merely a list of fields.

## P1 — next dedicated blueprints, only where they earn their own contract

Create these in this order, and stop if a structural pattern is sufficient:

1. [ ] `legal-case-jurisprudence-blueprint.json` — cases, courts, parties, issues, judgments, precedent and procedural history.
2. [ ] `transport-logistics-blueprint.json` — corridors, operators, capacity, throughput, chokepoints and dependencies.
3. [ ] `port-terminal-blueprint.json` — terminals, owners/operators, cargo, capacity, concessions and connections.
4. [ ] `telecom-cable-blueprint.json` — cables, landing stations, owners, operators, capacity, route and redundancy.
5. [ ] `science-funding-blueprint.json` — funders, programmes, grants, recipients, amounts, topics, outputs and co-funding.
6. [ ] `digital-platform-ecosystem-blueprint.json` — platforms, owners, users, business models, APIs, data flows, governance and dependencies.
7. [ ] `urban-system-blueprint.json` — metropolitan systems, housing, transport, utilities, fiscal base, jobs and governance.
8. [ ] `heritage-archaeology-blueprint.json` — sites, artifacts, dating, custody, provenance, designation and preservation.
9. [ ] `geopolitical-dependency-blueprint.json` — dependency direction, magnitude, concentration, substitutability and strategic exposure.
10. [ ] `dataset-statistical-series-blueprint.json` — statistical series, methodology, revisions, units, frequency, coverage and breaks.

Do not create separate blueprints for concepts already adequately governed by `structural-patterns-blueprint.json`.

## P1 — canonical joins and graph integrity

- [ ] Build country → population → GDP → debt → trade → energy → infrastructure → ownership → procurement → research joins.
- [ ] Build company → owner/control → asset → country → sector → financing → procurement chains.
- [ ] Build infrastructure → operator → owner → supplier → energy → trade dependency chains.
- [ ] Detect phantom relationship endpoints.
- [ ] Detect unresolved internal IDs versus legitimate external nodes.
- [ ] Detect accidental self-loops.
- [ ] Detect duplicate/conflicting edges.
- [ ] Require relationship type, provenance and time where the relevant graph layer supports them.
- [ ] Produce graph coverage statistics by domain and country.
- [ ] Identify high-connectivity nodes with unusually shallow records and promote them to research priority.

## P1 — People / Dwellers / population

- [ ] Canonically join people-registry, nations, languages, religions, political organizations, culture/subculture and migration layers.
- [ ] Keep nationality, citizenship, residence, ethnicity, language, religion, political affiliation and culture separate.
- [ ] Add reference years to population observations.
- [ ] Detect population claims without a reference year or source.
- [ ] Add resident populations, citizenship groups, language communities, religious communities, cultural communities, political constituencies, occupations, age cohorts and diasporas where evidence supports them.
- [ ] Distinguish population size, audience size, membership and visibility.

## P1 — religion / adjacent research

- [ ] Finish the religious-foundations canonical-owner migration.
- [ ] Update every religious blueprint reference to the standardized filename contract.
- [ ] Make foundation, architecture, adjacent, mystery-cult and occult records share the same resolver contract.
- [ ] Expand comparative religion records with origins, historical development, doctrine/practice, institutions, geography, population, evidence and uncertainty.
- [ ] Keep historical description, insider theology, academic interpretation and project symbolism explicitly typed.

## P1 — culture / movements / extremism

- [ ] Build the actual culture/subculture data layer from its blueprint.
- [ ] Add origins, turning points, geography, audience/population, institutions, media, practices and diffusion.
- [ ] Connect movements to predecessors, successors, organizations, institutions and media ecosystems.
- [ ] Improve extremist/high-control records with authority/date, membership uncertainty, ideology evidence, organizational history and provenance.
- [ ] Keep designation, allegation, conviction, academic classification and project interpretation distinct.

## P1 — books / full text / archives

- [ ] Validate every book manifest against actual text files.
- [ ] Validate UTF-8, file size, chapter/section offsets and search indexes.
- [ ] Ensure long texts remain readable without artificial truncation.
- [ ] Add edition, translator, publication and source metadata.
- [ ] Make full-text imports idempotent.
- [ ] Detect partial imports and duplicate editions.
- [ ] Keep canonical text separate from derived search/index files.

## P1 — North Programme / European economic graph

- [ ] Complete country-level joins for fiscal, population, trade, energy, infrastructure, ownership, procurement and research.
- [ ] Add reference-year and source metadata to every comparison.
- [ ] Separate stock, flow, nominal, real, market-value and face-value concepts.
- [ ] Improve finance records so issuer, creditor, instrument, currency, maturity and valuation cannot be conflated.
- [ ] Map major European companies to owners/controllers, assets, financing, suppliers, procurement and countries.
- [ ] Map infrastructure chokepoints and strategic dependencies.
- [ ] Add public-budget and tax-expenditure layers before making large fiscal conclusions.

## P2 — research depth

- [ ] Promote high-connectivity shallow records into dossiers.
- [ ] Prefer substantive sections and source diversity over arbitrary word counts.
- [ ] Add explicit known / unknown / disputed / interpretation sections to major dossiers.
- [ ] Record publication and retrieval dates.
- [ ] Build comparative dossiers around mechanisms and relationships, not just biographies.
- [ ] Preserve evidence trails back to source documents.

## P2 — Potatoism / project canon

- [ ] Keep Potatoism vocabulary, cosmology, timeline, relationships and research layers separately addressable.
- [ ] Keep project-defined mythology visibly distinct from empirical evidence.
- [ ] Develop the Great Book of Potato as a coherent library rather than repeated fragments.
- [ ] Cross-reference symbols, geometry, canonical passages and timeline events.
- [ ] Make the symbolic graph use the same relationship discipline as the empirical graph while retaining a different evidence type.

## P2 — UI / information design

- [ ] Keep the front page primarily navigational: clear layers, fast entry points, recent/high-value material and search.
- [ ] Make detail pages prioritize readable substance before decorative graph visualization.
- [ ] Add “what this is / evidence / relationships / timeline / sources / related records” consistently.
- [ ] Avoid AltaVista-style link walls and avoid empty graph-only pages.
- [ ] Make search return useful previews and direct detail routes.
- [ ] Add breadcrumbs and stable back/navigation behavior.
- [ ] Ensure mobile layouts remain usable even for dense dossiers.

## Engineering lessons / rules

- **Ownership before mirroring.** A missing field is not a reason to create another competing record.
- **A graph endpoint is not a node.** Relationships do not define the target by themselves.
- **Missing is a state.** Never invent values to make a page look complete.
- **Time belongs to facts.** A value without a reference period can be misleading.
- **Evidence has type.** Official data, academic interpretation, journalism, insider claims and project symbolism are not interchangeable.
- **Depth is independent of connectivity.** A node can have many edges and still need a real dossier.
- **Blueprints are executable research plans.** If a blueprint does not tell us what to collect, validate and connect next, it is unfinished.
- **Silent failure is worse than visible incompleteness.** Errors should become diagnostics.
- **Generated artifacts need contracts.** Every generated file needs an owner, producer, deterministic format and validation path.
- **Stability before scale.** Fix the architecture that will be exercised by the next thousand records before adding those records.

## Definition of done

A task is done only when the relevant source data validates, ownership is coherent, references are current, the site builds, the route renders meaningful content, CI passes, and deployed behavior is checked where the change affects production.

**See the connections. Read the substance. Preserve the evidence.**
