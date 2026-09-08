# TODO / BUGLIST — The Potato of Life / TimDooley

## Operating order

This is the working queue, not a wishlist. Work top-to-bottom. Do not add new data at scale while a higher-level contract is broken.

1. **P0 — establish one trustworthy repository structure and source of truth**
2. **P0 — make every route resolve and fail visibly**
3. **P0 — make CI/build/deploy enforce the same contracts**
4. **P0 — complete the coordinated blueprint migration and make the blueprint contract green**
5. **P1 — repair cross-domain joins and graph integrity**
6. **P1 — deepen the most insufficient entity families with real source-backed content**
7. **P1 — repair books/full-text architecture and import canonical text into the project**
8. **P2 — expand the North Programme / European economic graph**
9. **P2 — deepen Potatoism as a separate, explicitly project-defined layer**
10. **P2 — improve UI/search/navigation after data contracts are trustworthy**

## NEW — repository structural disorder / cleanup

The repository has accumulated duplicate data, inconsistent naming, uneven folder organization and overlapping representations. This is now a first-class architecture problem, not cosmetic cleanup.

- [ ] **Design the canonical repository structure before doing another large-scale reorganization.** Decide what belongs at root, in `data/`, in domain folders, in `scripts/`, in `components/`, in `books/`, in research/archive areas and in generated/build output.
- [ ] Produce a machine-readable **repository structure contract** describing folder purpose, allowed file types, canonical-owner rules, generated-file rules and naming conventions.
- [ ] Inventory the entire repository by path, type, size, producer, consumer, apparent domain and canonical/derived/archive status.
- [ ] Detect duplicate records across folders, including exact duplicates, near-duplicates, mirrors and competing versions.
- [ ] Detect duplicate concepts represented by multiple JSON files with different schemas.
- [ ] Detect directories whose contents mix unrelated domains or mix source data with generated data.
- [ ] Decide whether each major directory is **canonical data / enrichment / index / generated projection / source archive / code / documentation**.
- [ ] Establish deterministic naming and ordering conventions for domains, records, blueprints, indexes and generated artifacts.
- [ ] Decide where historical/archive versions belong so they do not compete with current canonical records.
- [ ] Move files only after their consumers and references have been identified; every move must preserve or explicitly migrate IDs and links.
- [ ] Remove redundant mirrors only after proving they are derived, obsolete or superseded.
- [ ] Add CI checks preventing new duplicate canonical owners and obvious folder-policy violations.

## NEW — blueprint migration / workflow audit

- [ ] **Run the coordinated blueprint migration end-to-end.** Rename every standalone blueprint to `<subject>-blueprint.json`, update registry entries, scripts, workflows, docs and data references, then verify no stale names remain.
- [ ] **Audit the blueprint workflow end-to-end:** discovery → blueprint registry → validator → acquisition/research → data generation → repository index → frontend resolver → build → stability audit → deployment.
- [ ] Run the full blueprint contract audit and record every failure/warning by file.
- [ ] Make the contract validator distinguish genuine blockers from legacy migration warnings.
- [ ] Bring all mature blueprints up to the meta-blueprint quality bar rather than merely renaming them.
- [ ] Require implementation notes, known bugs/traps, canonical owner, consumers, acquisition plan, validation rules and next-research task in mature blueprints.
- [ ] Verify registry count against actual standalone blueprint files.
- [ ] Verify structural-pattern sections are not falsely counted as standalone blueprint files.
- [ ] Verify every blueprint is actually consumed by, or clearly intended for, a data-generation/research workflow.
- [ ] Add blueprint-to-data coverage reporting: which blueprint has records, how many, and which fields remain systematically absent.

## Current P0 — source of truth / duplicates

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

## CURRENT P0 — country atlas acquisition failure

- [ ] **Re-run the repaired country acquisition workflow and verify a non-empty snapshot before trusting nation pages.**
- [x] Diagnose why `country-static.json` showed 194 countries with empty observations while the canonical scope was 195.
- [x] Identify that the refresh script treated malformed/unsupported World Bank API responses as empty data because it only inspected `payload[1]` and did not reject API error payloads.
- [x] Identify a second failure-mode bug: the old refresh wrote canonical country records and `country-static.json` even after the canonical-count validation had already failed.
- [x] Repair `scripts/refresh_country_atlas.py`: validate canonical scope before mutation, paginate World Bank requests explicitly, reject malformed/error responses, require minimum acquisition coverage, and fail closed before overwriting records/projections.
- [x] Record the solution in `README.md` under Wise notes so future repository scans retain the acquisition lesson.
- [ ] After the next successful run, verify Afghanistan, Albania, Andorra and several randomly selected countries have populated observations and that `country-static.json` has 195 entries.
- [ ] Add a dedicated regression test for the API-error-as-empty-data failure and snapshot-preservation behavior.
- [ ] Make `nation.html` distinguish source-acquisition failure/stale snapshot from a legitimately unavailable country indicator instead of showing every failure as “Not yet sourced”.

## P0 — routing / frontend contract

- [ ] Build a route matrix: page → input → data source → ID field → resolver → detail renderer → fallback.
- [ ] Make `node.html` the universal resolver for record families that do not have a specialized page.
- [ ] Ensure specialized pages explicitly register their supported families and do not duplicate resolver logic.
- [ ] Audit `repository.html`, `nation.html`, `nations.html`, `belief.html`, `people.html`, `books.html`, `extremism.html`, `potatoism.html`, `timeline.html`, `axis.html`, `geometry.html` and `health.html`.
- [ ] Test literal links and dynamic `?id=` links separately.
- [ ] Test URL encoding for spaces, punctuation, Unicode and long IDs.
- [ ] Ensure empty arrays, missing optional fields and missing files render an explanatory state instead of a blank screen.
- [ ] Add browser/runtime smoke tests for the highest-value routes when a headless browser is available.
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

## P1 — next dedicated blueprints, only where they earn their own contract

Create these in this order, and stop if a structural pattern is sufficient:

1. [ ] `legal-case-jurisprudence-blueprint.json`
2. [ ] `transport-logistics-blueprint.json`
3. [ ] `port-terminal-blueprint.json`
4. [ ] `telecom-cable-blueprint.json`
5. [ ] `science-funding-blueprint.json`
6. [ ] `digital-platform-ecosystem-blueprint.json`
7. [ ] `urban-system-blueprint.json`
8. [ ] `heritage-archaeology-blueprint.json`
9. [ ] `geopolitical-dependency-blueprint.json`
10. [ ] `dataset-statistical-series-blueprint.json`

Do not create separate blueprints for concepts already adequately governed by `structural-patterns-blueprint.json`.

## P1 — data population campaign: attack insufficiency first

After the contracts are green, stop adding arbitrary records. Use blueprint coverage to find the weakest important families and **stack those records with real, dense, source-backed information**.

For every population campaign:
- [ ] Identify the weakest canonical files/records by field coverage, evidence coverage, relationship coverage and substantive text.
- [ ] Select records that matter to multiple layers, not just obscure low-connectivity records.
- [ ] Populate identity, historical development, geography, institutions, people, population/users, economics, relationships, timeline and evidence where the blueprint calls for them.
- [ ] Use actual source-derived facts; never use placeholder prose to satisfy a field.
- [ ] Record unavailable/disputed information explicitly rather than inventing it.
- [ ] Add provenance at the fact/section level where practical.
- [ ] Prefer deepening an existing canonical record over creating a duplicate enrichment file.
- [ ] Re-run graph and route audits after each population batch.

## P1 — books / full-text architecture — IMPORTANT BUG

**Dao De Jing is currently broken:** the chapters are present, but the book page does not actually load/display the chapter text. The project has the chapter structure but not a functioning text-loading path.

Likely architectural problem to investigate: the project can source metadata/chapters from outside sources, but the **raw text itself is not reliably imported into the repository chapter-by-chapter**. A book being represented by links, metadata or chapter manifests is not equivalent to having its text available to the frontend.

- [ ] Diagnose the Dao De Jing loader from manifest → chapter identifier → text source → fetch → parser → renderer.
- [ ] Determine exactly why chapters exist but text does not render.
- [ ] Determine whether external-source dependency, missing local text, incorrect paths, CORS/base-path behavior, schema mismatch or loader logic is responsible.
- [ ] **Design a canonical local full-text representation:** book → edition → chapter/section → raw text, imported INTO the project.
- [ ] Determine copyright/public-domain/licensing status before importing any text.
- [ ] Make text imports idempotent and provenance-preserving.
- [ ] Add a validator that detects a chapter manifest pointing to a missing/empty text payload.
- [ ] Add UTF-8, chapter-order, duplicate-edition and partial-import checks.
- [ ] Build a reusable importer/normalizer so the same architecture works across all eligible books.
- [ ] **Apply this architecture to all books where legally and technically appropriate**, rather than building one-off loaders.
- [ ] Prioritize the **Quran and Torah** after the import architecture is proven, with edition/translation/source distinctions preserved.
- [ ] Keep canonical raw text separate from derived search indexes, excerpts and display projections.
- [ ] Make long texts readable chapter-by-chapter and searchable without silently truncating substantive content.

**Do not work on the Quran/Torah imports until the general full-text architecture and Dao De Jing diagnosis are complete. This is a queued architecture task, not permission to start importing them immediately.**

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

## P2 — North Programme / European economic graph

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

- **Structure before scale.** Do not populate thousands of records into an architecture whose ownership and folder rules are unclear.
- **Ownership before mirroring.** A missing field is not a reason to create another competing record.
- **A graph endpoint is not a node.** Relationships do not define the target by themselves.
- **Missing is a state.** Never invent values to make a page look complete.
- **Time belongs to facts.** A value without a reference period can be misleading.
- **Evidence has type.** Official data, academic interpretation, journalism, insider claims and project symbolism are not interchangeable.
- **Depth is independent of connectivity.** A node can have many edges and still need a real dossier.
- **Blueprints are executable research plans.** If a blueprint does not tell us what to collect, validate and connect next, it is unfinished.
- **Raw text is data.** A chapter manifest or external URL is not a substitute for an imported canonical text where licensing permits it.
- **Silent failure is worse than visible incompleteness.** Errors should become diagnostics.
- **Generated artifacts need contracts.** Every generated file needs an owner, producer, deterministic format and validation path.
- **Stability before scale.** Fix the architecture that will be exercised by the next thousand records before adding those records.
- **Acquisition must fail closed.** Never interpret an API error or malformed payload as an empty dataset.
- **A failed refresh must not destroy the last usable projection.** Diagnostics belong in refresh state; bad acquisition must stop before canonical mutation.

## Definition of done

A task is done only when the relevant source data validates, ownership is coherent, references are current, the site builds, the route renders meaningful content, CI passes, and deployed behavior is checked where the change affects production.

**See the connections. Read the substance. Preserve the evidence.**
