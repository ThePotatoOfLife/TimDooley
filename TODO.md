# TODO — The Potato of Life / TimDooley

## Current priority — audit, stabilize, then deepen

The project is an information archive whose graph is the navigation layer. The current canonical filing spine is **ROOT → SPIRIT / MIND / MATTER**; the deeper project mythology may additionally use Door/Axis as transformation and relational coordinates. Filing architecture and symbolic architecture must not be silently conflated.

### Immediate release blockers

- [ ] Complete recursive repository audit across every JSON, HTML, JS, CSS, Python and workflow file.
- [ ] Run the full validator chain after every structural repair and record the resulting commit.
- [ ] Generate and inspect a persistent 2026-09-08 health report from the validators.
- [ ] Resolve or explicitly classify high-connectivity graph orphan IDs.
- [ ] Repair and validate `data/religious-foundations/enriched-records.json` before using it as evidence of coverage.
- [ ] Audit every visible route for substantive content, not merely route existence.
- [ ] Keep manifests, backend endpoints, frontend bridge and consumers synchronized.
- [ ] Fix the current scheduled country-refresh failure before treating automated country acquisition as healthy.

### Findings from 2026-09-08 audit pass

- [x] Inspect the latest commit chain rather than assuming the current branch inherited every previous repair cleanly.
- [x] Confirm the latest Pages deployment succeeded.
- [x] Confirm the Atlas expansion workflow succeeded.
- [x] Confirm a separate country-refresh workflow currently fails during the normalized country observation step; acquisition needs a robustness repair and a successful rerun.
- [x] Register `data/research-carvings-2026-09.json` in both the manifest and backend registry.
- [x] Extend content-integrity validation so the new research layer cannot silently become an unvalidated orphan.
- [ ] Add recursive static-link auditing for nested directories, generated routes, CSS `url()` assets and JavaScript route templates.
- [ ] Add route-contract checks for every page that emits dynamic `node.html?id=...` or `nation.html?id=...` links.

### Canonical navigation architecture

- [x] Add `data/repository-spine.json` as the canonical Root/Spirit/Mind/Matter model.
- [x] Preserve the existing 33-level tree as a deeper vertical scaffold rather than deleting it.
- [x] Rebuild `repository.html` around the canonical repository tree.
- [x] Standardize the public site shell through one canonical `components/header.html` component and a deterministic build step; page-local controls remain in page content rather than the global header.
- [x] Add CI validation so every generated HTML page has exactly one canonical header.
- [x] Remove the unused runtime header loader; GitHub Pages now builds the shared shell before deployment.
- [x] Align `validate_repository_spine.py` with the actual Root/Spirit/Mind/Matter schema instead of the obsolete Root/Spirit/Door/Matter contract.
- [ ] Replace keyword-only classification with explicit layer metadata as records are enriched.
- [ ] Add temporal fields to important records so past/present/future states become machine-readable where applicable.
- [ ] Add cross-layer temporal navigation to important record pages.
- [ ] Explicitly map Spirit/Mind concepts such as geometry, Source and meaning into the repository tree instead of allowing them to disappear because a Matter bucket is unavailable.

### Atlas-wide information density

- [ ] Audit every `node.html?id=...` destination for information density.
- [ ] Any node containing only a title, description or relationship list needs a real dossier.
- [ ] Target at least one full page of substantive reading for every important entry; major subjects should be longer.
- [ ] Never manufacture facts merely to satisfy length.
- [ ] Where information is unavailable, state what is known, what is missing, the uncertainty and the research required.
- [ ] Turn structured JSON into readable sections/cards instead of exposing raw JSON as the only explanation.
- [ ] Preserve canonical IDs while enriching records.
- [ ] Keep graph edges as navigation/context, never as a replacement for content.
- [ ] Rank shallow records by connectivity and importance, then deepen the highest-value records first.

### Definition-first dossier standard

- [ ] Every substantial record begins with an explicit definition: **what is this thing?**
- [ ] Follow definition with origin/context.
- [ ] Follow context with structure, function or mechanism.
- [ ] Then expose directional couplings with relationship verbs where evidence permits.
- [ ] Then expose evidence, questions, failure modes, uncertainty and deeper interpretation.
- [ ] Every coupled record should itself be clickable and independently defined.

### Potatoism long-form standard

- [x] Add long-form Potatoism reading infrastructure.
- [x] Establish 900+ rendered-word target for full Potatoism entries.
- [ ] Populate individually authored long-form records for every canonical term.
- [ ] Ensure each entry covers definition, internal function, symbolic mechanics, relationships, development, comparison, world-facing interpretation, evidence boundary and research questions.
- [ ] Add source trails for external historical/scientific/comparative claims.
- [ ] Add explicit disagreement/uncertainty sections.
- [ ] Add cross-links from every related concept.

### Religious atlas

- [ ] Repair and validate `data/religious-foundations/enriched-records.json`.
- [ ] Establish one canonical owner for every religious dataset.
- [ ] Expand major traditions into long-form comparative records.
- [ ] Expand minor and adjacent traditions where practical.
- [ ] Give each tradition history, emergence, texts, concepts, practices, institutions, branches, geography, demographics, evidence, internal diversity and modern development.
- [ ] Preserve multiple founding/emergence clocks.
- [ ] Link religion entries to textual, comparative and relationship layers.

### World / nations

- [x] Keep 195 canonical nation identities stable.
- [ ] Expand sourced country observations beyond the current narrow validated enrichment base.
- [ ] Give each nation history, political structure, economy, demographics, geography, culture, religion, institutions, strategic relationships and sources where available.
- [ ] Add explicit missing-data states rather than false completeness.
- [ ] Build country → government → agencies → companies → banks → infrastructure → energy → trade → evidence pathways.
- [ ] Repair country-refresh acquisition reliability and preserve prior observations if a source request fails.

### People / organizations / security

- [ ] Give every important person biography/context, roles, affiliations, relationships and source trail.
- [ ] Give every event chronology, participants, causes, consequences, evidence and links.
- [ ] Integrate security/intelligence organizations into the canonical graph.
- [ ] Integrate extremist/hate/high-control movement records without duplicate IDs.
- [ ] Add predecessor/successor/affiliate/overlap edges.
- [ ] Keep formal designation, extremist classification, hate-group classification, terrorist designation, high-control allegations and criminal convictions distinct.
- [ ] Timestamp current-status claims.

### Systems / North Programme / European Economic Graph

- [ ] Deepen country and sector records together rather than as isolated lists.
- [ ] Connect fiscal systems, energy, infrastructure, ownership/control, finance/debt, procurement, technology, labour and research.
- [ ] Model strategic dependencies, bottlenecks, bridges, cycles and trajectories.
- [ ] Keep policy recommendations separate from observed evidence.
- [ ] Keep North Programme theory, Potatoism canon and empirical geopolitical records epistemically distinct while connecting them explicitly.

### Books / full text

- [ ] Treat complete texts as first-class corpus records with stable locators.
- [ ] Link texts → concepts → people → places → institutions → events.
- [ ] Distinguish complete local text, metadata-only record and external copyrighted edition.
- [ ] Add passage search and cross-text navigation where lawful.

### Temporal and relational model

- [ ] Add `valid_from`, `valid_to`, `observed_at`, `published_at`, `supersedes` and relationship-state fields where applicable.
- [ ] Distinguish actual outcomes from forecasts and counterfactuals.
- [ ] Add trajectory and phase transitions to high-value changing relationships.
- [ ] Preserve distance, direction, strength, dependency, coupling, feedback, topology and evidence status.

### UI / reading experience

- [ ] Keep index pages fast and navigational.
- [ ] Make every entry feel like an article/dossier, not a tooltip.
- [ ] Add table of contents to long records where useful.
- [ ] Add estimated reading time / word count.
- [ ] Add “read next” and “related research”.
- [ ] Keep mobile long-form reading comfortable.
- [ ] Let the Repository expose backend-only research without turning the root into a flat haystack.

### Integrity / CI

- [x] Keep backend coverage failures separate from artifact-upload failures.
- [x] Keep GitHub Actions on Node 24-compatible action versions.
- [x] Run Atlas link audit in CI.
- [x] Run web-layer audit in CI.
- [ ] Validator for every canonical lexicon term → valid long-form route.
- [ ] Validator for information-density status.
- [ ] Validator distinguishing missing from intentionally uncertain data.
- [ ] Validator requiring provenance or explicit project-theology status for claims.
- [ ] Validator preventing speculative psychological labels from rendering as diagnoses.
- [ ] Validator for duplicate movement IDs and alias collisions.
- [ ] Validator for predecessor/successor edges.
- [ ] Validator for stale “active” movement sources.
- [ ] Extend link audit beyond top-level HTML into nested pages and runtime-generated route contracts.
- [ ] Add a dedicated country-refresh smoke test before external acquisition is allowed to write a new snapshot.
- [ ] Run all workflows after the next expansion and do not call the repository clean until critical checks pass.

## Research principle

**See the connections. Read the substance.**

The Atlas should never stop at a pretty node. Every important object should open into enough definition, history, explanation, evidence, interpretation, uncertainty and relationships to stand on its own.
