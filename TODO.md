# TODO — The Potato of Life / TimDooley

## Current priority — audit, stabilize, then deepen

The project is an information archive whose graph is the navigation layer. The canonical filing spine is **ROOT → SPIRIT / MIND / MATTER**; Door/Axis remain transformation and relational coordinates rather than filing branches. Every substantial object is definition-first: define the thing itself, establish context and mechanism, then expose its directional couplings.

### Newly discovered bugs / insufficient-content inventory — 2026-09-08

- [x] **SOURCE FIX:** `extremism.html` has been hardened against scalar, array and object values in `affiliations`, `category`, `geography` and `sources`.
- [ ] **VERIFY DEPLOYMENT:** The live Pages site was still displaying the old `.join()` error after the first fix. Verify the Pages build actually contains the latest `extremism.html` and purge/replace any stale generated copy. Do not mark the live bug closed until the deployed page renders successfully.
- [ ] **DEEPEN:** `data/extremism-cults-atlas-2026-09.json` — many movement records use a compact profile schema rather than a full definition-first dossier. Expand records into definition, history, ideology/context, organization, mechanisms, evidence, chronology, relationships, uncertainty, questions and current-status sourcing.
- [ ] **DEEPEN:** `data/extremism-cults-atlas-expansion-2026-09.json` — normalize schema differences (`targets` vs `targets_or_hate`, `armed_status` vs `armed_or_violent`, scalar vs array affiliations) and preserve source-specific evidence.
- [x] **STARTED DEEPENING:** Added `data/extremism-record-enrichments-2026-09.json` with article-depth companion dossiers for KKK, Patriot Front, Active Club Network, Oath Keepers, Peoples Temple and Aum Shinrikyo.
- [ ] **CONTINUE DEEPENING:** Apply the same dossier treatment to the remaining weakest movement records, prioritizing short records and records with historically important/high-connectivity relationships.
- [ ] **DEEPEN:** `extremism.html` — cards still summarize rather than expose the new dossiers. Add definition/history/evidence/relationships/uncertainty and a full-entry route.
- [ ] **DEEPEN:** `data/meaning-layer-symbolic.json` — major symbolic records currently rely on `purpose/context/mechanisms/...` but do not consistently carry an explicit `definition` field. Add explicit definitions and enforce the same depth standard as other major records.
- [ ] **DEEPEN:** `data/meaning-layer.json` — audit every analytical record for explicit definition/context/mechanism/couplings and add missing sections.
- [ ] **DEEPEN:** `data/potatoism-dossiers.json` — audit canonical Potatoism terms and identify which terms have no substantive dossier.
- [ ] **DEEPEN:** `data/religious-foundations/records.json` and `data/religious-foundations.json` — expand important traditions into article-length dossiers with emergence, chronology, texts, doctrine, practice, institutions, people, places, geography, demographic evidence, internal diversity and modern status.
- [ ] **DEEPEN:** `data/religious-adjacent/*.json` — audit adjacent, mystery, occult, Satanism and anti-religious records for the definition-first standard.
- [ ] **DEEPEN:** `data/nodes.json`, tree record layers — identify shallow high-connectivity nodes and expand them; graph edges cannot substitute for content.
- [ ] **DEEPEN:** `data/events.json` — audit events for definition, causes, participants, chronology, consequences, evidence and relationships.
- [ ] **DEEPEN:** `data/nations.json` and country observation layers — identify thin country dossiers and prioritize them rather than treating 195 identities as complete records.
- [ ] **DEEPEN:** people registries — identify name-only/role-only people and create substantive biographies for high-value actors.
- [ ] **DEEPEN:** geometry records — expand labels/formulas into definition, derivation, history, applications, limitations and a clear boundary between mathematics and project symbolism.
- [ ] **DEEPEN:** Hawkins scale — audit every level for definition, source model, psychological description, action tendency, limitations and evidence boundary.
- [ ] **DEEPEN:** research carvings — ensure each research record stands alone with context, mechanism, evidence and project extrapolation.
- [ ] **DEEPEN:** graph bridge/relationships — distinguish research-only endpoints from true orphan entities and create first-class records for important missing entities.

### Content-audit engineering

- [ ] Create `scripts/audit_content_depth.py` to scan registered record collections for missing definition/context/mechanism/couplings/evidence, shallow prose, empty arrays, duplicates and schema drift.
- [ ] Give every audited record a machine-readable `depth_status`: `stub`, `structured`, `substantive`, `deep`.
- [ ] Produce `data/depth-audit.json` from the scanner.
- [ ] Add CI thresholds for critical layers while exempting intentional compact indexes/registries by contract.
- [ ] Add schema-normalization checks across datasets feeding the same page. The extremism `.join()` failure is the canonical example.
- [ ] Add route-contract checks for every content layer.

### Immediate engineering blockers

- [ ] Add/run route-contract validator covering static pages plus dynamic node/nation/belief/Potatoism/Hawkins/event/research/geometry IDs.
- [ ] Verify node resolver against actual schemas and repair mismatched fields/unsupported routes.
- [ ] Extend recursive web audit to validate canonical-header presence/order on every generated page.
- [ ] Run full validator chain and record exact results in a dated health report.
- [ ] Inspect high-connectivity graph orphan IDs.
- [ ] Fix country-refresh reliability with retry/backoff, source failure handling and snapshot preservation; rerun successfully.

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
- [ ] Add explicit `definition` fields to symbolic meaning records.

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
- [ ] Add named people, texts, places and events as first-class graph entities.

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

- [ ] Deepen country and sector records together.
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
- [ ] Let Repository expose backend-only research without turning the root into a flat haystack.

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
