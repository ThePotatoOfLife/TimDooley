# TODO — The Potato of Life / TimDooley

## Operating order

The repository is now large enough that **reliability, canonical ownership and depth matter more than raw file count**. Work in this order:

1. **P0 — site loads and deploys reliably**
2. **P0 — canonical ownership, duplicate paths and route integrity**
3. **P1 — deepen high-connectivity records and close missing joins**
4. **P1 — make People/Dwellers, Culture/Subculture, Religion and Movements analytically useful**
5. **P1 — improve population, geography, network and temporal extraction**
6. **P2 — expand evidence-backed research and project canon**
7. **P2 — UI/cosmetic refinement after contracts remain stable**

## Completed in the current stabilization pass

- [x] Fix the build-site header transformation/escaping failure.
- [x] Replace fragile repository-page multi-fetch loading with the generated repository index.
- [x] Add `scripts/build_repository_index.py` and generate a repository-wide record inventory.
- [x] Fix the site-shell validator so HTML attributes are parsed independently of attribute order.
- [x] Add `scripts/stability_audit.py` for JSON, Python, JavaScript, built-site links and source asset/reference checks.
- [x] Run the stability audit before the deeper Atlas validators in CI.
- [x] Save a stable checkpoint branch for the 2026-09-08 working state.
- [x] Add a dedicated extremism/high-control blueprint.
- [x] Add a dedicated culture/subculture blueprint.
- [x] Add a dedicated technology-system blueprint.
- [x] Expand the blueprint registry to include the new domain specifications.
- [x] Update README with architecture rules and lessons learned.

## P0 — canonical ownership and duplicate cleanup

- [ ] Generate `canonical-record-registry.json` from the complete data tree and expose duplicate-ID candidates in CI.
- [ ] Assign one canonical owner to every important identifier.
- [ ] Distinguish canonical records from indexes, mirrors, enrichments, graph projections, research and archives.
- [ ] Audit stale paths such as `data/religious-foundations.json` versus `data/religious-foundations/records.json`; keep compatibility only where a deliberate contract requires it.
- [ ] Search all HTML/JS/JSON/Markdown references for renamed or superseded files.
- [ ] Detect duplicate IDs across unrelated domains and classify intentional shared identifiers versus collisions.
- [ ] Detect alias/slug collisions that can send two records to the same route.
- [ ] Add a machine-readable ownership manifest for important cross-domain IDs.

## P0 — routing and page integrity

- [ ] Make `node.html` resolve every major record family represented by `repository-index.json`, not only the older core stores.
- [ ] Audit `nation.html`/`nations.html`, `belief.html`, `people.html`, `books.html`, `extremism.html`, `potatoism.html`, `timeline.html`, `axis.html`, `geometry.html` and `health.html` against their actual data contracts.
- [ ] Build a route matrix: page → data source → identifier field → resolver → fallback/error state.
- [ ] Test static route references and dynamic `?id=` routes separately.
- [ ] Ensure unknown IDs produce useful diagnostics rather than blank pages.
- [ ] Ensure every high-value repository record has a reachable human-readable detail page.
- [ ] Check URL encoding for IDs, aliases and Unicode names.
- [ ] Add a small browser/runtime smoke-test layer when a headless browser is available in CI.

## P0 — deployment and generated artifacts

- [ ] Confirm every main-branch Pages run completes through deployment after stabilization commits.
- [ ] Make generated artifacts deterministic: same source tree should produce the same index ordering and counts.
- [ ] Decide which generated files belong in Git and which should exist only in the Pages artifact.
- [ ] Add cache/version strategy consistently to generated JSON fetches.
- [ ] Keep Node.js GitHub Actions on supported runtime versions and remove obsolete workflows when their replacement is authoritative.

## P1 — blueprint system

- [ ] Validate every blueprint's referenced file actually exists.
- [ ] Validate blueprint IDs are unique.
- [ ] Validate each blueprint has identity, evidence, temporal and relationship sections unless an explicit exception is documented.
- [ ] Add acquisition/source/refresh metadata to blueprints that currently lack it.
- [ ] Add validation rules and failure modes to older blueprints so the newer blueprints are not the only deep specifications.
- [ ] Add dedicated blueprints where the structural model is still too generic: media ecosystems, legal cases/jurisprudence, intelligence/security networks, procurement contracts, digital/platform ecosystems, transport/logistics, ports, telecom/cables, science funding, heritage/archaeology and urban systems.
- [ ] Add blueprint inheritance metadata so specialized blueprints can extend common fields without copying them.
- [ ] Add field status vocabulary: required / recommended / optional / derived / unavailable / disputed.
- [ ] Add source-type and confidence requirements per field family where appropriate.

## P1 — People / Dwellers / populations

- [ ] Build canonical joins among people-registry, nations, languages, religions, political organizations, culture/subculture and migration layers.
- [ ] Separate nationality, citizenship, residence, ethnicity, language, religion, political affiliation and culture in every population dataset.
- [ ] Add time-indexed population observations and reference years.
- [ ] Detect population claims with no reference year or source.
- [ ] Add country intersections: resident populations, citizenship groups, language communities, religious communities, cultural communities, political constituencies, occupational groups, age cohorts and diasporas.

## P1 — Culture / Subculture / Movements

- [ ] Build the culture/subculture data layer from the new blueprint.
- [ ] Add origins, turning points, geography, population/audience, institutions, media, practices and diffusion relationships.
- [ ] Distinguish cultural visibility from population size.
- [ ] Connect movements to their historical predecessors, successor organizations, institutions and media ecosystems.
- [ ] Improve extremism/high-control records with designation authority/date, membership uncertainty, ideology evidence, organizational history and relationship provenance.

## P1 — Religion and adjacent layers

- [ ] Repair all stale religious-foundations references and make `records.json` the clear canonical research owner where appropriate.
- [ ] Make religious foundation, adjacent, mystery-cult and occult records resolve through the same route contract.
- [ ] Expand comparative religion records with origin, historical development, doctrine/practice, institutions, geography, population, sources and uncertainty.
- [ ] Preserve distinctions between historical description, insider theology, academic interpretation and project symbolism.

## P1 — World / North Programme / economic graph

- [ ] Complete canonical country joins for population, GDP, debt, trade, energy, infrastructure, ownership, procurement and research.
- [ ] Detect missing country-level edges across major economic layers.
- [ ] Add reference-year metadata to every country comparison.
- [ ] Build company → owner → asset → country → sector → financing → procurement joins.
- [ ] Build infrastructure → operator → owner → supplier → energy → trade dependency chains.
- [ ] Improve debt/finance records so issuer, creditor, instrument, currency, maturity and valuation are not conflated.

## P1 — books / full text

- [ ] Validate every book manifest against actual text files.
- [ ] Check UTF-8 integrity, file size, chapter/section offsets and search indexes.
- [ ] Ensure long texts remain readable without truncating useful passages.
- [ ] Add source/edition metadata to each text.

## P1 — graph integrity

- [ ] Detect phantom relationship endpoints.
- [ ] Detect self-loops where they are probably accidental.
- [ ] Detect duplicate edges with conflicting metadata.
- [ ] Detect edges with no relationship type, provenance or time where those are expected.
- [ ] Distinguish external graph endpoints from unresolved internal nodes.
- [ ] Add graph coverage statistics by domain and by country.

## P2 — research depth

- [ ] Promote high-connectivity shallow records into independent dossiers.
- [ ] Aim for substantive multi-section records rather than arbitrary word-count inflation.
- [ ] Add explicit “known / unknown / disputed / interpretation” sections to important dossiers.
- [ ] Add source dates and retrieval dates to research records.
- [ ] Build comparative dossiers where multiple traditions, organizations or systems share a mechanism.

## P2 — Potatoism / project canon

- [ ] Keep Potatoism vocabulary, cosmology, timeline, relationships and research layers separately addressable.
- [ ] Ensure project-defined mythology remains explicitly distinguishable from empirical evidence.
- [ ] Continue developing the Great Book of Potato as a coherent library rather than duplicating the same material across many files.
- [ ] Add cross-references between canonical passages, symbols, geometry and timeline events.

## Engineering lessons to preserve

- **Do not solve missing data by making another mirror.** Decide ownership first.
- **A graph endpoint is not automatically a node.** Relationships cannot substitute for definitions.
- **Silent failure is the enemy.** Empty states and diagnostics are better than pretending a page has no data.
- **Blueprints should change collection and validation.** More fields are useful only when they expose mechanisms, evidence, time or relationships.
- **Stability before scale.** Once indexing, validation, routing and deployment are reliable, expansion becomes much safer.

## Completion rule

A change is complete only when the relevant source data validates, canonical ownership remains coherent, the static site builds, the relevant page/route works, CI passes and the deployed behavior is checked. 

**See the connections. Read the substance. Preserve the evidence.**
