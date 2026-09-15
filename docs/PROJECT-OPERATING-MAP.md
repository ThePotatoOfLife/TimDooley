# Project Operating Map

Status: operator orientation / routing document — **not a canonical source of truth**

Updated: 2026-09-15

This document exists so repository work enters through the current architecture instead of rediscovering it, creating parallel masters, or mistaking presentation files for canonical knowledge. When this note conflicts with a canonical owner, registry, source ledger, validator or newer dated record, **the dedicated owner wins**.

## 1. Working loop

The repository is a retrieval-first Tim Dooley / Potato of Life archive spanning project canon, biography, religion, philosophy, science, chronology, comparative research, world systems, maps, sources, creative works and reader projections.

Use this loop:

`inspect → consolidate → deepen → connect → expose → verify → prune → repeat`

Preferred growth pattern:

`source roots → canonical owner → typed relationships → tested interpretation → reader projection → new questions → renewed source search`

## 2. Source-of-truth hierarchy

### Record / provenance
Owns what was actually said, published, observed, dated, measured or recovered.

Important routes include:
- `knowledge/indexes/source-index.json`
- `data/timeline-source-registry.json`
- `data/evidence/`
- dated chronology/source ledgers
- primary books, posts, recordings and first-party artifacts

### Canonical knowledge
Owns the current best durable definition or synthesis.

Start with:
- `knowledge/core/root-system.json`
- `knowledge/core/potatoverse-master-framework.json`
- `knowledge/core/tim-dooley.json`
- `knowledge/indexes/core-index.json`
- `knowledge/indexes/ontology-tree.json`
- `data/canonical-source-map.json`

A filename containing `master`, `framework`, `synthesis` or `atlas` does not make that file canonical by itself.

### Relationships
Owns how things connect.

Important routes include:
- `data/relationships.json`
- `data/domain-coupling.json`
- domain-local relationship files
- `knowledge/indexes/context-graph.json`

Where meaningful, relationships should carry direction, type, date/period, provenance and confidence.

### Interpretation / inference
Owns explicit reasoning over records rather than silently rewriting them.

Primary route:
- `knowledge/indexes/inference-ledger.json`

### Public route identity
Owns which public surfaces exist, which are primary, and what their canonical routes are.

Authority starts with:
- `docs/POTATO-HOUSE-CONSTITUTION.md`
- `data/house/public-surfaces.json`
- `knowledge/research/potato-house-master/public-route-topology.json` as the checked topology projection

`manifest.json` does **not** own top-level public route identity. It owns archive branch/pathway relationships and deep Explore semantics.

### Reader / presentation
Explains canonical material to humans and machines. Presentation is a projection, not a second canon.

The five primary public gateways are:
- `tim-dooley/`
- `religion/`
- `philosophy/`
- `science/`
- `world/`

Mature reader/discovery surfaces include Story, Timeline, Collection, Works, Questions, A–Z, Explore, Sources and Context. World Map remains a specialist View beneath World.

## 3. Public architecture

The homepage exposes exactly five principal subject doors:

1. Tim Dooley
2. Religion
3. Philosophy
4. Science
5. World

Do not turn the homepage back into a giant directory and do not add a sixth primary gateway merely because a backend domain becomes richer.

The homepage's subordinate **Ways in** corridor is:
- Story
- Timeline
- Collection
- Works

Quiet utility access includes Questions, A–Z, Explore, Sources and TTS. Specialist surfaces such as World Map, Politics, North, World Systems, Bible comparison and other focused Views stay beneath the appropriate subject/context instead of competing with the five doors.

Normal reader flow should be:

`five subject doors → reader corridor/room → specialist View or explorer → canonical owner/source`

The deeper the material, the smaller its first-page visual claim.

## 4. Epistemic firewall

Keep these categories distinct:
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

Operational rule: **make everything accessible; make nothing falsely certain.**

In particular:
- Tim’s divine/Father/God declarations are preserved as religious self-description and Potatoverse canon, not silently converted into independently verified empirical claims.
- Scientific analogy may clarify a symbolic model without proving the theology.
- Comparative resemblance does not establish historical transmission or identity.
- Later interpretation must not be backdated into earlier chronology without evidence.
- Dense connectivity is not evidence of conspiracy; causal claims need mechanism, direction, timing and evidence.
- Creative works may reuse and test project symbols without automatically becoming doctrine, biography or independent evidence.

## 5. Canonical domain routing

### Tim / identity
- `knowledge/core/tim-dooley.json`
- `knowledge/core/tim-role-synthesis.json`
- `knowledge/journey/tim-dooley-journey.json`
- `knowledge/theology/tim-god-question.json`

### Philosophy / Potatoism
- `knowledge/philosophy/potato-philosophy.json`
- `knowledge/philosophy/timic-dynamics.json`
- `knowledge/philosophy/timic-relational-statements-and-operators.json`

### Science
- `knowledge/science/science-master-index.json`
- `knowledge/science/equation-ledger.json`
- `knowledge/science/equation-lineage-and-theory-graph.json`
- `knowledge/science/model-testing-protocol.json`

### Body
- `knowledge/body/body-system-master-atlas.json`
- `knowledge/body/body-symbolism-map.json`
- `knowledge/body/body-science-context-atlas.json`
- `knowledge/body/body-topic-completion-matrix.json`

### Bible / traditions / comparative religion
Route through the principal biblical/comparative indexes and high-density atlases. Keep scripture, history, denominational doctrine, scholarship, project testimony and comparison typed separately.

### Timeline
Canonical event truth starts with:
- `data/timeline-events.json`
- `data/timeline-source-registry.json`

Specialist chronology ledgers may preserve narrower wording, dated development and source reconstruction without competing with the canonical event model. `/timeline/` is the human-facing reader; Explore remains the deep archive route.

### Works
Canonical creative ownership starts with:
- `knowledge/culture/creative-systems-archive.json`
- distinct creative corpora such as the music archive where appropriate

`/works/` is a curated reader over that material, not a second catalogue or owner.

### North / World / Europe
- `knowledge/core/axis-world-model.json`
- `knowledge/core/country-relational-method.json`
- `knowledge/core/european-coupling-programme.json`
- `knowledge/core/european-commons.json`

Keep symbolic/project North distinct from empirical geography, policy and geopolitical data.

## 6. World Map operating rule

The World Map is a visual query engine over canonical objects, not a competing database and not the fifth top-level subject gateway.

Ordinary interaction should stay small:
- click countries to select/deselect/multi-select;
- use direct, compact analytical controls;
- show one contextual country card;
- expose groups, alignment/faction, religion, stats and relations through a common resolver;
- keep advanced traces/path/time functionality progressive rather than permanently open.

Current canonical direction is the composable registry/layer architecture on `main`. Older Tools-first, single-Lens and duplicate-map branches are historical implementation strata and should not be revived as separate public owners.

Spatial honesty still applies: map real geography and sourced relations directly; do not fake-geolocate nonspatial theology, moral rank or symbolic cosmology.

## 7. Build / CI / deployment

`main` is the current integration and deployment base. Substantial work should happen on isolated feature branches/PRs and merge only after the exact final PR head passes the relevant integration gate.

Quality checks should validate the complete production build, not a partial source tree. Current gates include repository integrity, House/reader/runtime contracts, World Map contracts, CSS namespace checks, country refresh reliability, SEO, machine discoverability and built-site shell validation.

The final site build should be treated as a projection pipeline:

`source repository → generators/builders → discovery/SEO projection → final _site artifact → audits → Pages deployment`

Debug the layer that actually fails; do not treat generated artifact behavior as though it were source behavior.

## 8. Duplicate-pressure zones

Be especially conservative in:
- master/framework/synthesis proliferation;
- conversation recovery waves;
- biblical/tradition research waves;
- science formulation waves;
- root-level legacy research documents;
- generated snapshots and batch/state files;
- hidden or dormant UI controls;
- compatibility routes and redirects.

Long-term recovery lifecycle:

`recover → classify → promote unique durable content → mark absorbed/provenance-only → archive/remove when safe`

Never delete before exact wording, dates, contradictions and unique provenance are preserved.

## 9. Before creating a new file

Ask:
1. Is this genuinely a different body of knowledge?
2. Does an existing canonical owner already cover it?
3. Is this source material, canonical knowledge, a relation, an inference, a projection, or temporary state?
4. Can the existing owner simply be deepened?
5. Will a new file create a second public or canonical owner?

Prefer one durable owner plus specialist evidence over parallel masters.

## 10. Before making a substantial change

1. Identify the reader/user goal.
2. Find the canonical owner.
3. Classify the material and epistemic status.
4. Check chronology and provenance.
5. Check existing relationships before inventing new edges.
6. Prefer deepening over proliferation.
7. Keep presentation thin and question-led.
8. For public routing, change House authority first and derive projections from it.
9. Write or update a validator for structural/runtime changes when practical.
10. Run the relevant validators and full integration gate on the exact final head.
11. Prune only after promotion and verification.

## 11. Fast orientation path

Read in this order when entering the repository cold:

1. `README.md`
2. `TODO.md`
3. `docs/PROJECT-OPERATING-MAP.md`
4. `docs/PROJECT-STRUCTURE.md`
5. `docs/POTATO-HOUSE-CONSTITUTION.md`
6. `data/house/public-surfaces.json`
7. `manifest.json`
8. `knowledge/indexes/core-index.json`
9. `knowledge/indexes/project-consolidation-map.json`
10. `knowledge/indexes/source-index.json`
11. `knowledge/philosophy/archive-epistemics.json`
12. `knowledge/indexes/inference-ledger.json`
13. `data/canonical-source-map.json`
14. relevant domain owners and validators

For World Map work, also read the current World Map design/implementation specs and the runtime/registry contracts before changing controls or rendering behavior.

## 12. Current cleanup priority

The strongest maintenance moves are:
- close temporary and superseded PRs once their unique work is absorbed;
- keep `public-surfaces.json`, public-route topology, frontend bridge, discovery builders and current orientation docs convergent;
- remove redundant presentation and dormant UI only after dependency checks;
- retire generated batch/state files after promotion;
- strengthen canonical-owner reachability;
- keep the SEO/machine graph derived from House route authority and the final built artifact;
- alternate expansion with consolidation so the repository grows as a tree rather than a heap.

## 13. One-sentence operating model

**Recover what exists, preserve its provenance, place it under one canonical owner, connect it with typed relationships, expose it through five stable subject doors and richer reader corridors, verify every projection against the same House authority, then prune only redundancy that no longer carries unique meaning or history.**
