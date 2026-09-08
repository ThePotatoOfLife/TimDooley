# TODO — The Potato of Life / TimDooley

## Current priority — audit, stabilize, then deepen

The project is an information archive whose graph is the navigation layer. The canonical filing spine is **ROOT → SPIRIT / MIND / MATTER**; Door/Axis remain transformation and relational coordinates rather than filing branches. Every substantial object is definition-first: define the thing itself, establish context and mechanism, then expose its directional couplings.

### Newly discovered bugs / insufficient-content inventory — 2026-09-08

- [x] **FIXED:** `extremism.html` crashed while rendering because `affiliations` is an array in the main extremism dataset but a string in at least some legacy/base records. Renderer now normalizes scalar/array/object values instead of blindly calling `.join()`.
- [ ] **DEEPEN:** `data/extremism-cults-atlas-2026-09-08.json` — many movement records currently have a compact schema (`id/name/category/status/geography/targets/membership/armed_status/affiliations/sources/notes`) rather than the repository's full definition-first dossier standard. Expand into definition, history, ideology/context, organization, mechanisms, evidence, chronology, relationships, uncertainty, questions and current-status sourcing.
- [ ] **DEEPEN:** `data/extremism-cults-atlas-expansion-2026-09.json` — same compact-record problem; fields such as `targets`/`armed_status` differ from the base dataset's `targets_or_hate`/`armed_or_violent`, making the two layers unnecessarily fragile. Normalize into one explicit schema and preserve source-specific evidence.
- [ ] **DEEPEN:** `extremism.html` — cards currently summarize records but do not yet expose the full dossier. Add links/opening surfaces to substantial individual movement records and show definition, history, evidence, status date, relationships and uncertainty.
- [ ] **DEEPEN:** `data/meaning-layer-symbolic.json` — major symbolic records currently rely on `purpose/context/mechanisms/...` but do not consistently carry an explicit `definition` field. Add explicit definitions and enforce the same depth standard as other major records.
- [ ] **DEEPEN:** `data/meaning-layer.json` — major analytical records are substantially better, but audit every record for explicit definition/context/mechanism/couplings and add missing sections rather than assuming presence because the file is large.
- [ ] **DEEPEN:** `data/potatoism-dossiers.json` — this is currently a contract/coverage description rather than the actual long-form corpus. Audit the canonical Potatoism terms and identify which terms have no corresponding substantive dossier.
- [ ] **DEEPEN:** `data/religious-foundations/records.json` and `data/religious-foundations.json` — foundation records are currently compact structured profiles. Expand important traditions into article-length dossiers with emergence, chronology, texts, doctrine, practice, institutions, people, places, geography, demographic evidence, internal diversity and modern status.
- [ ] **DEEPEN:** `data/religious-adjacent/*.json` — audit all adjacent, mystery, occult, Satanism and anti-religious records for the same definition-first standard; do not let classification labels substitute for substance.
- [ ] **DEEPEN:** `data/nodes.json`, `data/tree-child-records.json`, `data/tree-support-records.json`, `data/tree-concept-records.json` — identify shallow nodes and expand the high-connectivity ones first; graph edges must not be the only content.
- [ ] **DEEPEN:** `data/events.json` — audit events for definition, causes, participants, chronology, consequences, evidence and relationships; event names/descriptions alone are insufficient.
- [ ] **DEEPEN:** `data/nations.json` and country observation layers — identify nations with thin evidence/content and prioritize them for expansion rather than treating 195 identities as 195 complete dossiers.
- [ ] **DEEPEN:** `data/people-registry.json` / people-related datasets — identify people represented only by names, roles or links and create substantive biographical records for high-value actors.
- [ ] **DEEPEN:** `data/geometry-records.json` — expand geometry records beyond formulas/labels into definition, derivation, historical context, applications, limitations and explicit separation between mathematics and project symbolism.
- [ ] **DEEPEN:** `data/hawkins-scale.json` — audit each level for definition, source model, psychological description, action tendency, limitations and evidence boundary; keep the non-physical-frequency guardrail explicit.
- [ ] **DEEPEN:** `data/research-carvings-2026-09.json` — audit for substantive depth and ensure every carving has enough context to stand alone, not merely a citation bundle.
- [ ] **DEEPEN:** `data/global-graph-bridge.json` and `data/relationships.json` — distinguish research-only endpoints from true orphan entities, then create missing first-class records for high-value referenced entities.

### Content-audit engineering

- [ ] Create `scripts/audit_content_depth.py` that scans registered JSON record collections and reports: missing definition, missing context, missing mechanism/function, missing couplings, missing evidence/sources, shallow prose, empty arrays, duplicate records and schema drift.
- [ ] Give every audited record a machine-readable `depth_status`: `stub`, `structured`, `substantive`, `deep`.
- [ ] Produce `data/depth-audit.json` from the scanner so the UI and CI can show where the repository is thin.
- [ ] Add a CI threshold for critical layers while allowing intentionally compact indexes/registries to be exempt by contract.
- [ ] Add schema-normalization checks across datasets that feed the same page. The extremism bug is the model: consumers must not guess whether a field is scalar or array.
- [ ] Add route-contract checks for every content layer so a valid record cannot point to a dead or unsupported page.

### Immediate engineering blockers

- [ ] Add and run a route-contract validator covering static pages plus dynamic `node.html`, `nation.html`, `belief.html`, `potatoism-entry.html`, Hawkins, event, research-carving and geometry IDs.
- [ ] Verify the current `node.html` resolver against actual schemas for Hawkins, events, research, geometry and Potatoism; repair mismatched field names or unsupported routes.
- [ ] Extend the recursive web audit to validate canonical-header presence/order on every generated page.
- [ ] Run the full validator chain after the latest commits and record exact results in a dated health report.
- [ ] Inspect and resolve high-connectivity graph orphan IDs, distinguishing true missing entities from intentional research-only endpoints.
- [ ] Fix the scheduled country-refresh failure with retry/backoff, source failure handling and snapshot preservation; rerun successfully.

### Canonical navigation and information architecture

- [x] Add `data/repository-spine.json` as the canonical Root/Spirit/Mind/Matter model.
- [x] Preserve the existing 33-level tree as a deeper vertical scaffold.
- [x] Rebuild `repository.html` around the canonical repository tree.
- [x] Standardize the public site shell through `components/header.html` and build-time injection.
- [x] Add CI validation for exactly one canonical header.
- [x] Remove the unused runtime header-loader architecture.
- [x] Align repository-spine validation with Root/Spirit/Mind/Matter.
- [ ] Replace keyword-only classification with explicit layer metadata as records are enriched.
- [ ] Add machine-readable temporal fields to important records.
- [ ] Add cross-layer temporal navigation to important record pages.
- [ ] Explicitly map Spirit/Mind concepts such as geometry, Source and meaning into the repository tree.
- [ ] Add a stable route registry so navigation does not depend on scattered filename assumptions.

### Atlas-wide information density

- [ ] Audit every dynamic record destination for information density.
- [ ] Any node containing only a title, description or relationship list needs a real dossier.
- [ ] Target at least one full page of substantive reading for every important entry; major subjects should be longer.
- [ ] Never manufacture facts merely to satisfy length.
- [ ] Where information is unavailable, state what is known, what is missing, uncertainty and research required.
- [ ] Turn structured JSON into readable sections/cards instead of exposing raw JSON as the only explanation.
- [ ] Preserve canonical IDs while enriching records.
- [ ] Keep graph edges as navigation/context, never as a replacement for content.
- [ ] Rank shallow records by connectivity and importance, then deepen highest-value records first.

### Definition-first dossier standard

- [ ] Every substantial record begins with an explicit definition: **what is this thing?**
- [ ] Follow definition with origin/context.
- [ ] Follow context with structure, function or mechanism.
- [ ] Then expose directional couplings with relationship verbs where evidence permits.
- [ ] Then expose evidence, questions, failure modes, uncertainty and deeper interpretation.
- [ ] Every coupled record should itself be clickable and independently defined.
- [ ] Add explicit `definition` fields to the symbolic meaning records that currently rely on purpose/context alone.

### Potatoism long-form standard

- [x] Add long-form Potatoism reading infrastructure.
- [x] Establish 900+ rendered-word target for full Potatoism entries.
- [ ] Populate individually authored long-form records for every canonical term.
- [ ] Ensure each entry covers definition, internal function, symbolic mechanics, relationships, development, comparison, world-facing interpretation, evidence boundary and research questions.
- [ ] Add source trails for external historical/scientific/comparative claims.
- [ ] Add explicit disagreement/uncertainty sections.
- [ ] Add cross-links from every related concept.

### Religious atlas

- [x] Establish one canonical owner for the foundation layer and remove the phantom enriched-file dependency.
- [ ] Deep-expand major traditions into long-form comparative records.
- [ ] Expand minor and adjacent traditions where practical.
- [ ] Give each tradition history, emergence, texts, concepts, practices, institutions, branches, geography, demographics, evidence, internal diversity and modern development.
- [ ] Preserve multiple founding/emergence clocks.
- [ ] Link religion entries to textual, comparative and relationship layers.
- [ ] Add named people, texts, places and events as first-class graph entities instead of embedding them only as strings.

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
- [x] Register research-carving coverage in backend/content validators.
- [ ] Validator for every canonical lexicon term → valid long-form route.
- [ ] Validator for information-density status.
- [ ] Validator distinguishing missing from intentionally uncertain data.
- [ ] Validator requiring provenance or explicit project-theology status for claims.
- [ ] Validator preventing speculative psychological labels from rendering as diagnoses.
- [ ] Validator for duplicate movement IDs and alias collisions.
- [ ] Validator for predecessor/successor edges.
- [ ] Validator for stale “active” movement sources.
- [x] Extend static web audit to nested HTML/CSS/JS references.
- [ ] Add dedicated country-refresh smoke test before external acquisition can replace a snapshot.
- [ ] Run all workflows after the next expansion and do not call the repository clean until critical checks pass.

## Research principle

**See the connections. Read the substance.**

The repository should never stop at a pretty node. Every important object must open into enough definition, history, explanation, evidence, interpretation, uncertainty and relationships to stand on its own.
