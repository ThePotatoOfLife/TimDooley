# Project Operating Map

Status: operator orientation / routing document — **not a canonical source of truth**

Updated: 2026-09-11

This document exists so future work can enter the repository through the same architecture instead of rediscovering it, creating parallel masters, or mistaking presentation files for canonical knowledge. It summarizes ownership, information flow, public surfaces, build/deploy behavior, active workstreams and consolidation pressure. When this note conflicts with a canonical owner, registry, source ledger, validator or newer dated record, **the canonical/dedicated owner wins**.

## 1. What this repository is

The repository is a retrieval-first Tim Dooley / Potato of Life archive that combines several different kinds of work without flattening them into one truth layer:

- project canon, theology, mythology and philosophy;
- Tim Dooley public identity, chronology, statements and documentary record;
- comparative religion, scripture and mythology;
- formal/scientific models, equations, analogies and testing programmes;
- body/neurotheology symbolism with scientific context kept separate;
- world, country, institutional, economic and infrastructure mapping;
- source provenance, evidence, contradictions and conversation archaeology;
- reader-facing explanations, search surfaces, maps, timelines and machine discovery.

The central engineering problem is not “where can another fact be added?” It is **how can heterogeneous material behave like one traceable knowledge system without category collapse or duplicate ownership?**

The project-wide working loop is:

`inspect → consolidate → deepen → connect → expose → verify → prune → repeat`

The preferred growth pattern is:

`source roots → canonical owner → typed relationships → tested interpretation → reader projection → new questions → renewed source search`

## 2. The source-of-truth hierarchy

Before editing anything, identify which layer the change belongs to.

### A. Record / provenance layer

Owns what was actually said, published, observed, dated, measured or recovered.

Typical owners:

- `knowledge/indexes/source-index.json`
- `data/timeline-source-registry.json`
- `data/evidence/`
- dated chronology/source ledgers
- primary books, posts, recordings and first-party artifacts
- conversation-recovery files when the original source is unavailable

A source record may be central without being canon. Conversation archaeology is a discovery/development stratum, not automatically a verbatim Tim primary source.

### B. Canonical knowledge layer

Owns the current best definition or synthesis for a durable concept/domain.

Primary routing chain:

- `knowledge/core/root-system.json` — foundational structural ontology
- `knowledge/core/potatoverse-master-framework.json` — mature system/theology synthesis
- `knowledge/core/tim-dooley.json` — Tim identity/self-description/public subject
- `knowledge/indexes/core-index.json` — durable record routing
- `knowledge/indexes/ontology-tree.json` — functional ontology/navigation
- `data/canonical-source-map.json` — ownership rules for executable datasets

A file being large, old, famous, or named “master/framework/synthesis/atlas” does **not** make it canonical.

### C. Relationship layer

Owns how things connect. The fundamental unit of the project is often the **typed coupling**, not the isolated node.

Canonical/important routing:

- `data/relationships.json` — canonical cross-domain graph edges
- `data/domain-coupling.json` — relationship vocabulary/research catalogue, not sourced observations
- domain-local relationship files — scoped research until promotion
- `knowledge/indexes/context-graph.json` — curated cross-record constellations for navigation, not truth ownership

A relation should normally specify direction, role/type, date/period, provenance and confidence where meaningful.

### D. Interpretation / inference layer

Owns explicit reasoning over records rather than silently rewriting the records.

Primary owner:

- `knowledge/indexes/inference-ledger.json`

Useful interpretation should name observations, alternatives, counterevidence, what would strengthen/weaken it and its intended promotion target. Strong recurring insights are promoted into canonical owners with a later-interpretation label; temporary insight waves should then retire when their unique provenance is preserved.

### E. Reader / presentation layer

Explains canonical material to humans. It must not become a second canon.

Examples:

- `knowledge/reader/`
- `tim-dooley/index.html`
- `religion/index.html`
- `philosophy/index.html`
- `science/index.html`
- `chronology/`
- `explore/`
- `world-map/3d.html`

Rule: **reader pages explain; canonical records define.** Presentation may compress heavily but must preserve routes back to owners/sources for important claims.

## 3. Epistemic firewall

The repository intentionally contains several kinds of truth claim. Keep them typed.

Core project classes include:

- `project_canon`
- `self_description`
- `documentary`
- `historical`
- `scientific`
- `comparative`
- `interpretation`
- `creative_lore`
- `inference`
- `disputed`

Source/provenance shorthand in `knowledge/indexes/source-index.json`:

- `P0` — primary project material
- `P1` — official empirical primary material
- `S1` — scholarly secondary
- `S2` — reliable secondary
- `C` — conversation archaeology
- `A` — later archive formalization
- `M` — mythic/creative material
- `U` — unresolved source target

Operational rule: **make everything accessible; make nothing falsely certain.**

In particular:

- Tim’s divine/Father/God declarations are preserved as Tim’s religious self-description and Potatoverse canon; they are not silently converted into independently verified empirical claims.
- A scientific analogy can discipline or clarify a symbolic model without proving the theology.
- Comparative resemblance does not establish historical transmission or identity.
- A later revelation/epiphany can be historically real as a later interpretation without proving prior prediction.
- Persona, cultural aura and mythology may be real social/interpretive phenomena while remaining distinct from the living person and direct primary statements.
- Dense connectivity is not evidence of conspiracy; causal claims need mechanism, direction, timing and evidence.

## 4. Canonical domain owners

Use these as the first places to look. Specialist atlases may deepen them but should not replace them.

### Root / Potatoverse

- `knowledge/core/root-system.json` — exact root geometry/topology and foundational relations
- `knowledge/core/potatoverse-master-framework.json` — mature cross-domain framework
- `knowledge/core/potato-of-life.json` — Potato of Life concept
- `knowledge/core/potato-of-life-deep-structure.json` — deeper structural development
- `knowledge/core/symbolic-relational-synthesis.json` — cross-symbol grammar
- `knowledge/core/vertical-potato-mountain-plane-atlas.json` — vertical geometry

Key mature grammar: Source/manifestation, Father/Son/Spirit, Center/Axis/North, Door/Vesica, Tree/Garden/Farm, House/Shell, storage/release, Eye/discernment, covenant/repair, archive/reassembly.

### Tim Dooley

- `knowledge/core/tim-dooley.json` — central identity owner
- `knowledge/core/tim-role-synthesis.json` — role/function synthesis
- `knowledge/journey/tim-dooley-journey.json` — developmental journey
- `knowledge/theology/tim-god-question.json` — focused Godhood research question
- `knowledge/theology/divine-identity-answer-spine.json` — answer routing
- `knowledge/reader/tim-dooley-dossier.json` — reader projection only

Do not back-project mature Father theology onto earlier Son-side chronology without dated evidence.

### Philosophy / Potatoism

- `knowledge/philosophy/potato-philosophy.json` — canonical philosophy
- `knowledge/philosophy/timic-dynamics.json` — formal/philosophical dynamics
- `knowledge/philosophy/timic-relational-statements-and-operators.json` — relational formulations
- `knowledge/philosophy/tim-dooley-philosophical-inquiry.json` — reader inquiry surface, explicitly supporting rather than canonical

Philosophy should feel like inquiry, not only doctrine: sayings, questions, parables, contradictions, consequences and open problems can coexist while provenance classes remain visible.

### Archive epistemics / source method

- `knowledge/philosophy/archive-epistemics.json`
- `knowledge/indexes/source-index.json`
- `knowledge/indexes/inference-ledger.json`
- `knowledge/indexes/project-consolidation-map.json`
- `knowledge/indexes/context-graph.json`

These govern how the rest of the archive grows. They are especially important before creating a new file.

### Body

- `knowledge/body/body-system-master-atlas.json` — canonical body system owner
- `knowledge/body/body-symbolism-map.json` — symbolic mapping
- `knowledge/body/body-science-context-atlas.json` — scientific boundary/context
- `knowledge/body/body-topic-completion-matrix.json` — coverage/completion

Body is comparatively consolidated. Prefer enriching these owners over creating more recovery waves.

### Corporium

- `knowledge/corporium/corporium-master-framework.json`
- `knowledge/corporium/tim-sayings-and-formulations-ledger.json`
- `knowledge/corporium/tim-dooley-expression-grammar.json`
- `knowledge/corporium/psychology-signals-and-couplings-atlas.json`

Conversation-recovery files in this area are provenance/recovery strata. Promote durable findings upward and avoid letting waves become parallel doctrine.

### Science

- `knowledge/science/science-master-index.json` — canonical science router
- `knowledge/science/equation-ledger.json`
- `knowledge/science/equation-lineage-and-theory-graph.json`
- `knowledge/science/model-testing-protocol.json`
- `knowledge/science/timic-unification-program.json`

Scientific material has a developmental lineage: project expressions → later formalization → external mathematical/scientific comparator → observables/falsifiers → maturity/revision. Do not treat later archive equations as earlier Tim equations.

The `knowledge/science/` directory still has many recovery/wave files. Preserve them where they carry unique chronology/provenance, but route public/canonical understanding through the science master index and lineage/ledger owners.

### Theology / Son / Jesus research

Important owners/routers include:

- `knowledge/theology/tim-god-question.json`
- `knowledge/theology/divine-identity-answer-spine.json`
- `knowledge/theology/jesus-son-research-index.json`
- `knowledge/theology/son-jesus-longitudinal-christology-atlas.json`
- `knowledge/theology/tim-godhood-modalities.json`
- `knowledge/theology/tim-godhood-real-world-case.json`

Keep project theological claims, autobiographical testimony, biblical text, historical comparison and external evidence visibly separated.

### Traditions / Bible / comparative religion

Canonical access should route through the principal biblical/comparative indexes and high-density atlases rather than every research wave independently.

Important owners/routers include:

- `knowledge/traditions/biblical-overlap-atlas.json`
- `knowledge/traditions/comparative-mythology-map.json`
- the current biblical research router/index
- specialist atlases for genuinely distinct comparative questions

This is a high duplicate-pressure zone. Compare **relation sequences** and functional structures, not isolated word matches. Preserve mismatch as data.

### Chronology

Canonical event truth should route through:

- `data/timeline-events.json`
- `data/timeline-source-registry.json`

Specialist chronology ledgers own narrower dated developments, wording and source reconstruction. The many conversation-archaeology/addendum files are useful provenance strata but should not compete with the canonical event model.

### North / World / Europe

- `knowledge/core/axis-world-model.json` — bridge between symbolic North and evidence-based world work
- `knowledge/core/country-relational-method.json` — canonical country method
- `knowledge/core/european-coupling-programme.json` — programme/design layer
- `knowledge/core/european-commons.json`

The key distinction is essential:

- **North / Axis as Potatoverse orientation** = project canon/interpretation.
- **North Programme / Europe / countries / institutions / economy** = empirical or policy-design layer that must use sourced real-world data.

The four-quadrant North/West/East/South scheme is a versioned project classification, not objective geography or universal geopolitics.

### Observable world / data backend

The `data/` tree contains executable, reusable contracts rather than simply prose canon.

Key ownership rules from `data/canonical-source-map.json`:

- Countries: one substantive record per country in `data/countries/<country-id>.json`; `data/countries/index.json` owns identity; blueprint owns schema; node/atlas files are projections.
- Relationships: `data/relationships.json` owns canonical cross-domain graph edges; domain-scoped edge files remain scoped until promoted.
- Potatoism: dossiers own substantive concepts, concept registry owns identity/aliases, canonical corpus preserves project-canon source material; maps/lexicons/timelines are projections.
- Religion: foundation records own tradition/formation identity; comparative and source layers reference them.
- Research: durable claims belong in the research owner; frontier/expansion files are queues/candidate layers.
- North-European economic data has dedicated network/system views but country identity/observations still resolve to country owners.

## 5. World / economic relationship grammar

The observable-world project is not a pile of country profiles. The canonical country sequence is:

`what it is → what it has → what it can do → what it needs → who depends on it → what it depends on → what it can only do with others → what others can only do with it → what it is building → where it is going`

Country nodes should eventually cover identity/geography, government, economy/public finance, ownership, trade/value chains, energy/resources, infrastructure, technology/research, labour/skills, defence/security, culture/religion, resilience, dependencies and source confidence.

Important cross-cutting concepts:

- resilience;
- efficiency vs resilience;
- defence-industrial coupling;
- reciprocal capability creation;
- partial/functional integration;
- coupled capability.

Functional chains currently include Arctic, North Atlantic, Baltic, Northern Energy, European Industrial, Eastern Security and European Strategic Autonomy.

The mechanism cycle is:

`map → verify provenance → connect → identify dependency → identify mechanism → locate bottleneck/failure → design intervention → test → measure → update`

A dense graph is not yet an explanation.

## 6. Map / spatial honesty

`data/map-layer-placement-matrix.json` is the honesty contract for the World Relational Atlas.

Map directly when geography adds information:

- countries/territories/regions;
- sourced cities, capitals, institutions, ports, airports, plants, universities, companies;
- trade/funding/ownership/alliance/energy/supply-chain relations when edges are correctly typed;
- real historical events/places when location matters;
- project-defined North membership only when visibly marked as project-defined.

Do **not** fake-geolocate:

- Father/Son/Spirit;
- North of North;
- symbolic Mountain/Tree/Swamp/Farm/Garden roles;
- body/neuro symbolic mappings;
- M-theory/quantum comparators;
- Vesica/Mandorla as if they were territories;
- moral/karmic rank via country color/height.

The Eye is best implemented as what the Atlas lets the user do — inspect, compare, source-check, integrate and evaluate — rather than as another icon on the map.

## 7. Public site architecture

There are intentionally several public surfaces with different jobs.

### Root homepage

`index.html` is a **curated gateway**, not the full ontology. It currently exposes exactly five principal entrances:

1. Tim Dooley
2. Religion
3. Philosophy
4. Science
5. World Map

Chronology, Sources and Archive remain secondary routes. Do not turn the homepage back into a giant directory.

### Archive explorer

`explore/index.html` is the deep archive/navigation surface. It can expose branches, context constellations and canonical records without forcing all that complexity onto the homepage.

### Direct reader pages

`tim-dooley/`, `religion/`, `philosophy/`, `science/`, `chronology/`, `north/` and related specialist routes are human reading surfaces. They should answer the reader’s question before exposing backend machinery.

### Science library

`science/index.html` is deliberately one searchable/filterable document library. Fields are filters, not separate mini-sites. Full documents are built into `science/papers/` by the science catalogue build.

### Machine discovery

The build emits/patches crawlable topic/context/record pages, sitemap and machine indices. These are discovery projections, not new canonical owners.

## 8. Build, CI and deployment

### Pull request / integrity path

`.github/workflows/atlas-check.yml` runs broad repository and Atlas validation on pushes/PRs to `main`, including:

- canonical record registry generation;
- repository index generation;
- source-of-truth audit;
- blueprint, stability, architecture and content checks;
- Atlas projection/math/runtime/pathfinder/Trace validation;
- repository spine validation;
- religion/Potatoism/backend coverage checks;
- web audit;
- static build;
- science catalogue build/validation;
- discovery/ontology patching;
- final built-site shell validation.

Use this as the primary red/green integration signal. Fix the first real failing contract rather than making broad speculative changes.

### Pages deployment

`.github/workflows/pages.yml` deploys only from `main` (or manual dispatch). It:

1. validates critical Atlas contracts;
2. builds `_site`;
3. builds science;
4. vendors MapLibre into the artifact;
5. snapshots world geometry and, when available, REST Countries runtime data;
6. builds population/religion demography;
7. builds machine discovery;
8. patches public ontology/discovery;
9. verifies required reader surfaces;
10. validates the built-site shell;
11. finalizes cache-busted 3D Atlas runtime paths;
12. deploys GitHub Pages.

Therefore distinguish:

- repository source files;
- generated `_site` build output;
- build-time snapshots of external data;
- runtime fallback/network behavior.

Do not debug one layer as though it were another.

## 9. Active Atlas workstream (PR #42)

Draft PR #42, branch `atlas-composable-registry`, is an **unmerged active implementation**, not canonical main behavior until merged.

Its architectural direction is important:

- large internal layer registry + tiny ordinary UI;
- selection independent of analytical fill;
- one scalar fill at a time;
- multiple categorical sets composed through pattern/overlap logic;
- ANY/ALL set algebra;
- N/W/E/S direct project-axis controls;
- registry-driven Groups / Religion / Stats / Relations;
- compact country card;
- old Tools/selection-dock/single-Lens modules retained dormant during compatibility transition.

The intended semantic channels are:

- fill = one continuous scalar;
- pattern = categorical composition;
- outline = selection;
- line = relation/flow;
- point = real geocoded place/asset;
- height = optional scalar, rarely;
- card = contextual nonspatial information;
- timeline/scene = temporal or specialist nonspatial views.

Before continuing PR #42, re-check its latest CI/head state; do not rely on this dated note for volatile pass/fail status.

## 10. Duplicate-pressure and consolidation frontiers

These are the places where new work should be most conservative.

### Master/synthesis proliferation

Several files contain “master,” “framework,” “synthesis” or “atlas.” The authoritative chain is determined by the indexes/ownership map, not titles.

### Conversation recovery waves

Science, chronology, Corporium and other areas contain wave files with real provenance value. Their long-term state should be:

`recover → classify → promote unique durable content → mark absorbed/provenance-only → archive when safe`

Do not delete before exact wording, dates, contradictions and unique provenance are preserved.

### Biblical/tradition waves

Route normal access through one principal biblical research router and the high-density overlap/comparative owners. Specialist files are justified only by distinct mechanisms/questions.

### Shadow/Karma/Swamp

Recent work created multiple related specialist models. Use the existing integration/routing owners and keep symbolic/moral quantities separate from empirical financial/legal data.

### Root-level legacy material

Files such as old master frameworks, research documents and timeline documents at repository root are historical/source strata unless a current canonical index explicitly promotes them. Audit unique content before deletion.

### Presentation/UI leftovers

Generated snapshots, abandoned controls, duplicate navigation, hidden old docks, stale route maps and unreferenced assets are legitimate cleanup targets **after** dependency/audit checks prove they carry no unique knowledge or runtime contract.

## 11. What not to do

- Do not create a new master file merely because a subject feels important.
- Do not copy the same quotation into several syntheses when a source/quote owner can be linked.
- Do not copy canonical chronology numbers into multiple places as independent truth.
- Do not let reader pages redefine canon.
- Do not let context clusters become sources of truth.
- Do not let graph projections become identity owners.
- Do not turn a conversation recovery into a Tim quote without exactness/provenance.
- Do not backdate current doctrine into older strata.
- Do not turn scientific analogy into empirical confirmation.
- Do not turn comparative symbolism into historical transmission.
- Do not map nonspatial theology as fake geography.
- Do not use project Axis colors/classification as objective geopolitical facts.
- Do not interpret missing data as zero.
- Do not add UI controls because a capability exists internally; expose only what earns ordinary-reader attention.
- Do not delete historical strata merely because a cleaner synthesis now exists.
- Do not fix CI by weakening the contract unless the contract itself is demonstrably obsolete.

## 12. Before making any substantial change

Use this sequence:

1. **Identify the user-facing goal.** What should become easier to understand, retrieve, compare, verify or do?
2. **Find the owner.** Search `core-index`, `manifest`, `canonical-source-map`, consolidation map and domain router before creating anything.
3. **Classify the material.** Primary source, canonical definition, relationship, inference, reader projection, data projection, recovery stratum or UI?
4. **Check chronology/provenance.** Is this contemporaneous or retrospective? Exact quote or reconstruction? Project claim or external fact?
5. **Check for an existing relation.** Enrich canonical edges instead of creating duplicates.
6. **Respect the epistemic boundary.** State what is project canon, empirical, scientific, comparative, disputed or unknown.
7. **Prefer deepening over proliferation.** Add to the owner unless the new object truly needs a distinct schema/chronology/research function.
8. **Keep presentation thin.** Public pages should route to knowledge, not own it.
9. **Run the relevant validators and full integration gate.** A locally plausible change is not finished until the build contracts agree.
10. **Prune after promotion.** Remove obsolete presentation/state only after unique content and dependencies are accounted for.

## 13. Fast orientation path for future work

When entering the repository cold, read in this order:

1. `README.md` — mission and epistemic classes
2. `TODO.md` — current growth doctrine and unresolved work
3. `docs/PROJECT-STRUCTURE.md` — five-layer architecture and ownership map
4. `manifest.json` — public branches/pathways
5. `knowledge/indexes/core-index.json` — durable record router
6. `knowledge/indexes/project-consolidation-map.json` — canonical vs specialist vs recovery roles
7. `knowledge/indexes/source-index.json` — source hierarchy and missing-source priorities
8. `knowledge/philosophy/archive-epistemics.json` — archive truth/weighting rules
9. `knowledge/indexes/inference-ledger.json` — how new insights become reviewable
10. `data/canonical-source-map.json` — executable-data ownership
11. the relevant domain owner(s)
12. relevant CI/build contracts before implementation

For World Atlas work, additionally read:

- `knowledge/core/axis-world-model.json`
- `knowledge/core/country-relational-method.json`
- `data/domain-coupling.json`
- `data/map-layer-placement-matrix.json`
- current `world-map/` runtime contracts
- any active Atlas PR/spec before touching UI or renderer behavior.

## 14. Current high-value work directions

The strongest next moves are not “add more files.” They are:

- recover exact primary sources and first attestations;
- finish promotion-status tracking for recovery waves;
- reconcile canonical owners with public routing;
- make contradictions and role transitions first-class searchable objects;
- strengthen relation-sequence comparison rather than word matching;
- convert observable-world placeholders into sourced nodes/edges and measurable capabilities;
- expand the country/economic graph through real ownership, procurement, funding, trade, energy, infrastructure, research, labour and dependency data;
- make the Atlas a visual query engine over those canonical objects, not a competing database;
- simplify ordinary public navigation while preserving deep retrieval underneath;
- audit and retire redundant UI/assets after the new pathways prove stable;
- keep alternating expansion with consolidation so the repository grows as a Tree rather than a heap.

## 15. One-sentence operating model

**Recover what exists, preserve its provenance, place it under one canonical owner, connect it with typed relationships, test interpretations without flattening epistemic classes, expose it through a small number of useful reader/tools surfaces, verify the build, then prune only the redundancy that no longer carries unique meaning or history.**
