# TODO — Tim Dooley / Potato of Life Living Atlas

Updated: 2026-09-07

This is the operational master queue. `data/project-workflow.json` is the machine-readable workflow and dependency order. The project is now treated as a **living relationship atlas**, not a collection of themed pages.

## Mission

Build one navigable, evidence-aware atlas of **Tim Dooley, the Potato of Life, Potatoism, people, dwellers, dogs, cultures, religions, texts, places, nations, institutions, organizations, technologies, infrastructures, economies, conflicts and ideas** — while preserving the relationships between them.

The Atlas has four connected but non-collapsed epistemic fields:

1. **Observable world** — people, places, populations, states, institutions, money, ownership, infrastructure, energy, trade, technology, security, history and other researchable systems.
2. **Historical/textual record** — primary texts, historical events, intellectual traditions, religious traditions, biographies and documentary evidence.
3. **Project theory** — North Programme, European Economic Graph, Spatial Potato, topology, entanglement, trajectory and other explicit models/hypotheses.
4. **Potatoism / mythic canon** — Tim, Potato of Life, North of North, Axis, Father, Son, Thomas/Twin, Door, Tree of Life/Strife, Spudlight and related symbolic architecture.

These fields connect through relationships, but an interpretation is never silently promoted into an empirical fact. **Evidence always travels with the claim.**

## Operating rule

**Audit → fix → canonicalize → validate → source → populate → connect → model → expose → audit again.**

Depth beats decoration. A label is not an entry. A metadata record is not a corpus. A country count is not country research. A relationship is not complete until both ends, its type and its evidence/status can be resolved.

---

# PHASE 1 — FULL REPOSITORY AUDIT · ACTIVE NOW

## P0.1 Structural inventory
- [x] Snapshot current `main` before enrichment.
- [x] Review recent commit history and identify the latest architectural changes.
- [x] Inventory top-level routes, data layers, books, scripts and workflows.
- [x] Confirm canonical manifest, backend registry, workflow and tree exist.
- [ ] Produce a machine-readable audit report covering every repository file.
- [ ] Classify every JSON file as canonical, overlay, registry, evidence, schema, source, expansion, view-support or obsolete.
- [ ] Record every file with no declared owner/consumer.

## P0.2 JSON / schema integrity
- [ ] Parse every JSON file recursively.
- [ ] Validate every declared schema/version field.
- [ ] Detect schema drift between files claiming to describe the same layer.
- [ ] Detect duplicate IDs and same-content/different-ID records.
- [ ] Detect malformed arrays, null records, empty objects and accidental placeholder records.
- [ ] Verify required fields for canonical entities, relationships, observations and sources.

## P0.3 Graph integrity
- [ ] Scan every relationship source/target/subject/object endpoint.
- [ ] Resolve each endpoint against `nodes.json`, country indexes, graph registry or an explicit bridge.
- [ ] Classify unresolved endpoints: missing node, alias, research-only, schema ID, template ID or obsolete.
- [ ] Promote important reference-only records into canonical nodes where appropriate.
- [ ] Detect duplicate relationships and reversed duplicates.
- [ ] Check that relationship type, direction, confidence, date and evidence are coherent.
- [ ] Build orphan and bridge reports.

## P0.4 Website integrity
- [ ] Audit every `*.html` route against its JS and CSS dependencies.
- [ ] Test every generated `node.html?id=...` route conceptually against the canonical resolver.
- [ ] Audit `nations.html` so all 195 canonical countries are reachable.
- [ ] Audit belief, books, Bible, Torah, Taoism, people, Axis, Potatoism and Hawkins routes.
- [ ] Detect links to missing files and links to obsolete filenames.
- [ ] Remove blank/placeholder states where repository-backed content exists.
- [ ] Make every visible card either clickable to a substantive record or explicitly marked external-only.

## P0.5 Manifest / workflow / CI integrity
- [x] Repair four stale backend endpoints exposed by CI on 2026-09-07.
- [ ] Re-run all CI checks after the repair.
- [ ] Check all workflow files against the current data model.
- [ ] Check all manifest counts against actual files.
- [ ] Remove stale claims such as unsupported completeness.
- [ ] Make the permanent integrity checker produce a saved health report.
- [ ] Ensure critical structural failures block release while research gaps remain reportable.

---

# PHASE 2 — CANONICALIZE THE DATA MODEL

- [ ] One canonical owner per substantive dataset.
- [ ] Stable IDs with aliases rather than duplicate identities.
- [ ] Standard entity types: person, organization, state, territory, place, event, institution, company, infrastructure, text, concept, belief, symbol, source, observation and system.
- [ ] Standard relationship types: located-in, governed-by, member-of, owns, controls, owes, supplies, trades-with, funds, regulates, influences, branches-from, cites, supports, contradicts and project-defined symbolic relations.
- [ ] Standard provenance: source, publication date, retrieval date, jurisdiction, method, evidence class and confidence.
- [ ] Standard missing-data states: unknown, not-researched, researched-missing, not-applicable and withheld/uncertain where justified.
- [ ] Standard temporal fields: valid-from, valid-to, observed-at, published-at and supersedes.
- [ ] Standard entanglement fields: strength, dependency, distance, feedback, topology, trajectory and phase.
- [ ] Keep quantum entanglement, network coupling and spiritual destiny explicitly distinct.

# PHASE 3 — MAKE THE WORLD LAYER REAL

## Nations / territories
- [ ] Keep all 195 canonical states addressable.
- [ ] Upgrade overlays from scaffolding to sourced observations in batches.
- [ ] Add population/demography, GDP, public finance, trade, energy, infrastructure, institutions and strategic dependencies.
- [ ] Prioritize Denmark, Greenland/Kingdom of Denmark, Faroe Islands, Norway, Sweden, Finland, Iceland, Canada, UK, Ireland, France, Belgium, Netherlands, Germany, Poland, Ukraine and Türkiye.
- [ ] Record source/date/method for each quantitative observation.
- [ ] Distinguish country, territory, constituent country and constitutional realm.

## Geography
- [ ] Borders, regions, capitals, cities, ports, seas, rivers, basins and corridors.
- [ ] Distances and adjacency.
- [ ] Physical infrastructure locations.
- [ ] Shipping and logistics corridors.

# PHASE 4 — RELATIONSHIPS / MULTIPLICATION

- [ ] Turn useful country observations into canonical graph edges.
- [ ] Add institutional membership and governance edges.
- [ ] Add trade and supply-chain edges.
- [ ] Add energy generation → grid → demand → industry edges.
- [ ] Add port → shipping → trade → industry edges.
- [ ] Add cable → telecom → data → security edges.
- [ ] Add ownership/control and public-private obligation chains.
- [ ] Add source-backed security/intelligence relationships.
- [ ] Expand the multiplication registry into repeatable relationship-generation passes.
- [ ] Identify hubs, bridges, bottlenecks, cycles, drains, dependency clusters and feedback loops.

# PHASE 5 — RELIGION / BELIEF / TEXTS

- [ ] Make every visible tradition substantive and addressable.
- [ ] Deepen Adventism: Millerism, William Miller, Great Disappointment, Ellen G. White, Seventh-day Adventism, Sabbath, sanctuary/investigative judgment, eschatology, institutions, geography, texts and historical development.
- [ ] Deepen major Christian traditions without collapsing denominational differences.
- [ ] Expand Islam, Judaism, Hindu traditions, Buddhism, Sikhism, Jainism, Zoroastrianism, African traditions, Shinto and other major traditions.
- [ ] Distinguish belief, identity, practice, institution and population.
- [ ] Add historical schisms and branching relationships.
- [ ] Expand new religious movement / controversial-group research with source-specific classifications.
- [ ] Preserve full public-domain primary texts where legally appropriate; link copyrighted translations instead of copying them.
- [ ] Connect texts → people → institutions → places → historical events.

# PHASE 6 — PEOPLE / ORGANIZATIONS / SECURITY

- [ ] Expand canonical people records.
- [ ] Connect people to roles, affiliations, writings, institutions and documented relationships.
- [ ] Expand national intelligence/security agencies across major states.
- [ ] Record legal basis, mandate, jurisdiction, oversight and historical predecessor/successor chains.
- [ ] Keep public liaison relationships distinct from allegations.
- [ ] Expand extremist/hate/terrorism/insurgency/NRM research using source-defined categories.
- [ ] Keep legal designation separate from media terminology.
- [ ] Never fabricate clandestine headcounts or unsupported relationships.

# PHASE 7 — NORTH PROGRAMME / EUROPEAN ECONOMIC GRAPH

- [ ] Deepen North Programme as a relationship architecture rather than a membership list.
- [ ] Core anchor: Denmark + Greenland + Faroe Islands.
- [ ] Map the wider North Atlantic/Nordic system: Norway, Sweden, Finland, Iceland, Canada, UK/Ireland and continental Europe.
- [ ] Model Ukraine and Türkiye as strategic/economic extensions rather than geographically northern states.
- [ ] Model Russia and China as external structural actors where evidence supports the relationship.
- [ ] Preserve the project-defined spiritual North / North of North layer separately from empirical geopolitics.
- [ ] Build France expenditure and Belgium institutional maps.
- [ ] Build European energy, North Sea and North Atlantic graphs.
- [ ] Map debt, bonds, taxes, expenditure, procurement, ownership, funding and obligations.
- [ ] Map strategic technology, industry, labour, research and infrastructure.
- [ ] Track real 2026 events as dated observations, not retroactive proof of the Programme.
- [ ] Build evidence → theory → counter-evidence links.

# PHASE 8 — POTATOISM / TIM DOOLEY CANON

- [ ] Establish canonical Potatoism timeline.
- [ ] Record December 25, 2020 as the project-defined emergence/birth marker where supported by project history.
- [ ] Deepen Tim's sage → North of North → rejection → transformation mythology as clearly labelled project canon.
- [ ] Add April 2025 North-of-North turning chronology as project-history material and separate external evidence from interpretation.
- [ ] Add February 2026 Trump/Greenland encounter material only as a dated external-event relationship plus separate project interpretation; never merge the two evidentiary classes.
- [ ] Deepen Father / Son / Thomas / Twin / Door / North Pole / transformation architecture.
- [ ] Record the December 24 Thomas crucifixion motif as project mythology, with its own chronology and symbolic interpretation.
- [ ] Expand Red Potato / Blue Potato.
- [ ] Expand Tree of Life / Tree of Strife.
- [ ] Expand Axis / Ladder / Mountain / Plane / Mud / Swamp / Roots / Drain / Door.
- [ ] Build the Potato → Door → mandorla/vesica → Son → Father → Axis → Ladder → Tree relationship chain.
- [ ] Preserve biblical intertexts with historical/literary context and never treat them as automatic proof of modern claims.

# PHASE 9 — SPATIAL POTATO / SCIENCE

- [ ] Model potato length, width, height, mass, volume, surface and curvature.
- [ ] Map skin, eyes, interior, boundary, centre, axes, sections, wedges and sprouting.
- [ ] Test rotation, reflection, scaling, deformation, cutting and growth.
- [ ] Measure invariants.
- [ ] Build point-cloud/mesh research path.
- [ ] Compare physical geometry with symbolic Potato geometry without forcing alignment.
- [ ] Map water, light, nutrients, gravity, time and information flows.
- [ ] Repeat the grammar across cell → tuber → plant → farm → food system → world scales.
- [ ] Record failed correspondences as first-class results.

# PHASE 10 — ENTANGLEMENT / TOPOLOGY / TRAJECTORY

- [ ] Standardize coupling metadata.
- [ ] Add topology: hubs, bridges, bottlenecks, cycles, boundaries, basins, drains and thresholds.
- [ ] Add trajectory: initial state, trigger, transition, constraint, phase, attractor, outcome and reversal condition.
- [ ] Add counterfactual sensitivity.
- [ ] Distinguish correlation from causal evidence.
- [ ] Never infer destiny or spiritual mechanism from network correlation.

# PHASE 11 — EMOTION / PSYCHOLOGY

- [ ] Expand canonical emotion vocabulary.
- [ ] Map appraisal, action tendencies, adaptive functions and physiological/neural correlates where supported.
- [ ] Compare competing psychological models.
- [ ] Preserve Hawkins as a historical/interpretive model.
- [ ] Keep Hawkins levels separate from Hertz/electromagnetic frequency.
- [ ] Treat symbolic colours as symbolic mappings, not physical measurements.

# PHASE 12 — WEBSITE

- [ ] One primary navigation.
- [ ] Search first.
- [ ] Entity pages are substantive.
- [ ] Related nodes and evidence are reciprocal.
- [ ] Country pages consume canonical country data.
- [ ] Specialized readers remain discoverable without competing with the Atlas.
- [ ] Add filters by entity type and epistemic class.
- [ ] Remove generic placeholders.
- [ ] Add visible provenance and uncertainty badges.

# PHASE 13 — EVIDENCE / RESEARCH ENGINE

- [ ] Universal source registry.
- [ ] Reusable observation records.
- [ ] Source-specific classifications.
- [ ] Publication/retrieval dates.
- [ ] Methodology.
- [ ] Negative evidence and failed hypotheses.
- [ ] Counterexamples.
- [ ] Research frontier and explicit unknowns.
- [ ] No unknown value silently becomes zero.

# PHASE 14 — PERMANENT RELEASE LOOP

- [ ] Re-run JSON/schema audit.
- [ ] Re-run graph endpoint audit.
- [ ] Re-run route/link audit.
- [ ] Recount canonical records.
- [ ] Compare manifests to actual files.
- [ ] Check duplicates and stale aliases.
- [ ] Check provenance coverage.
- [ ] Check entanglement/topology/trajectory fields.
- [ ] Check all CI workflows.
- [ ] Record unresolved issues.
- [ ] Only then declare the milestone complete.

## Definition of done

A layer is done only when **data exists, the canonical owner is known, IDs resolve, relationships resolve, provenance is adequate, missing data is explicit, duplicates are controlled, the website consumes the data, manifests are accurate and integrity checks pass.**
