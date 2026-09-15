# House Convergence Corridors Design

**Status:** approved architectural direction

## Goal

Make the public site and House governance agree with what the project has actually become: keep exactly five primary subject gateways, while adding a coherent second layer of reader-entry modes (Story, Timeline, Collection, Works, Questions, A–Z, Explore, Sources) and eliminating route-authority drift between registries, topology, frontend bridge, discovery builders, and orientation documents.

## Governing rule

**Five subject doors → richer corridors → real reader rooms → specialist views → deep archive → canonical roots.**

Do not add a sixth primary homepage gateway in this wave. Increasing backend sophistication must reduce, not increase, first-page cognitive load.

## Current problems

1. `data/house/public-surfaces.json` recognizes some mature surfaces but not all of the site's real reader surfaces.
2. `knowledge/research/potato-house-master/public-route-topology.json` has already drifted from the registry (for example Culture is registered but absent from topology).
3. `schemas/house-public-surface-registry.schema.json` is hard-capped at exactly 15 surfaces, blocking legitimate future public-surface registration.
4. `data/frontend-atlas-bridge.json` still routes Timeline through `explore/#branch=timeline`, Corporium through Philosophy, and Works through Tim instead of their strongest public reader surfaces.
5. `scripts/build_discovery.py` and `scripts/build_site_authority.py` independently hard-code the five primary routes instead of consuming House route authority.
6. Story is a mature public reader but is not registered as a public surface.
7. Collection (`/corporium/`) is substantial but under-routed.
8. Works is a canonical Domain Room with a rich creative archive but lacks a proper public reader route.
9. Questions and A–Z are real generated public discovery surfaces but are not represented in public-surface authority.
10. `docs/PROJECT-OPERATING-MAP.md`, `docs/PROJECT-STRUCTURE.md`, and parts of `TODO.md` contain stale or over-broad route-authority language.
11. The homepage's current secondary `Other threads` layer is weaker than the project's actual reader forms.

## Protected invariants

- Exactly five primary gateway IDs in this order: `tim`, `religion`, `philosophy`, `science`, `world`.
- Exactly five corresponding canonical routes: `/tim-dooley/`, `/religion/`, `/philosophy/`, `/science/`, `/world/`.
- World Map remains a specialist View under World.
- Domain Rooms remain backend bounded contexts, not required homepage labels.
- Public pages remain projections and never become sole substantive knowledge owners.
- Explore remains the deep archive browser; specialist Views keep their task-specific roles.
- Static semantic HTML remains sufficient for essential navigation.
- Story, Works, Collection, and other reader surfaces must not duplicate canonical knowledge ownership.

## Public-surface expansion

Register the mature public surfaces currently missing from House authority.

### Tim subordinate reader surfaces

- `story` → `/tim-dooley/story/` → `guide` → parent `tim` → Rooms: `potatoverse-canon`, `time-history`, `archive-sources`, `works`, `culture-information`.
- `collection` → `/corporium/` → `guide` → parent `tim` → Rooms: `potatoverse-canon`, `culture-information`, `life-body`, `science-formal-models`, `archive-sources`.
- `works` → `/works/` → `guide` → parent `tim` → Rooms: `works`, `culture-information`, `archive-sources`, `time-history`.

### Secondary global discovery surfaces

- `questions` → `/questions/` → `explorer` → parent `home` → broad discovery across Rooms, no knowledge ownership.
- `index-a-z` → `/index-a-z/` → `explorer` → parent `home` → broad discovery across Rooms.
- `context` → `/context/` → `guide` → parent `home` → primarily `archive-sources` plus cross-Room contextual use.

Existing `timeline`, `explore`, and `sources` remain secondary global surfaces.

`secondary_global_ids` becomes:

```text
timeline
explore
sources
questions
index-a-z
context
```

Story, Collection, and Works are not global utilities; they are reader rooms beneath Tim.

## Schema rule

Remove the fixed `maxItems: 15` surface cap. Retain a sensible `minItems` and rely on explicit gateway invariants plus route uniqueness and schema validation. Extensibility belongs in registered surfaces; primary gateway count remains fixed independently.

## Route-topology rule

Every active public-surface registry entry must have exactly one topology record with matching:

- `surface_id`;
- `surface_type`;
- `canonical_route`;
- participating Room IDs;
- primary hub/parent relationship;
- specialist-view classification where applicable.

No registered active surface may silently disappear from topology.

## Frontend bridge corrections

Keep the bridge as backend-family/branch projection and compatibility output, but correct human/public routes:

- Timeline `global_route` → `timeline/`; archive route may remain `explore/#branch=timeline`.
- Corporium `human_route` → `corporium/`; archive route remains `explore/#branch=corporium`.
- Works `human_route` → `works/`; archive route remains `explore/#branch=works`.
- Culture backend family `global_route` → `context/culture/` rather than generic `context/`.

Do not make these reader routes canonical data owners.

## Works public reader

Create `/works/index.html` as a curated reader over `knowledge/culture/creative-systems-archive.json` and related creative owners.

The reader should organize the existing creative corpus into public-safe genres:

1. **Play & Simulation** — Potato growth game, trading game, AI Potato Town, game/quest systems.
2. **Writing & Performance** — poetry/incantatory prose, sermon-comedy, absurdist fiction, performance sequences.
3. **Music & Sound** — Suno/music archive and documented aesthetic directions.
4. **Visual & Symbolic Art** — generated-art lineages, diagrams, visual compositions, symbolic scene systems.
5. **Recovered & Experimental Works** — Mashy Arc, Infinite Potato, Reverse Triangulation, Potato School, recovered prototypes.

Epistemic copy must state that creative artifacts can reuse and test Potatoverse symbols without automatically becoming doctrine, biography, or independent evidence.

The page must link back to Tim and onward to Explore, Sources, Story, and Collection where relevant.

## Homepage corridor

Preserve the five primary gateway rows unchanged in count and role.

Replace the generic `Other threads` editorial row with a deliberately small **Ways in** corridor:

- **Story** — lived/continuous narrative.
- **Timeline** — dated development.
- **Collection** — voice, sayings, recurring formulations, body/experience clues.
- **Works** — games, music, writing, comedy, visual art, simulations.

Quiet utility/footer access should include:

- Questions
- A–Z
- Explore
- Sources
- TTS (if an existing stable route is already public)

The corridor is editorial discovery, not a sixth taxonomy. It must remain visually subordinate to the five primary gateways.

## Discovery authority convergence

`scripts/build_discovery.py` and `scripts/build_site_authority.py` must load the canonical primary gateway IDs/routes/titles from `data/house/public-surfaces.json` rather than maintain independent route dictionaries/tuples.

A small reusable resolver may be introduced under `scripts/` if that reduces duplication without creating a new authority file.

Expected resolver contract:

```python
load_public_surfaces(root: Path) -> dict
primary_gateway_rows(root: Path) -> list[dict]
```

The resolver validates that primary gateway IDs equal exactly:

```python
("tim", "religion", "philosophy", "science", "world")
```

Builders may fail closed when House authority is missing or malformed.

## Validator changes

### House governance

Extend `scripts/validate_house_governance.py` to prove:

- the five gateway IDs/routes remain exact;
- `secondary_global_ids` reference registered surfaces;
- every active registered surface has exactly one topology record;
- topology route/type/Rooms agree with the registry;
- required new surfaces exist: Story, Collection, Works, Questions, A–Z, Context;
- required static source routes exist for source-authored surfaces (`story`, `collection`, `works`, `context`); generated discovery surfaces (`questions`, `index-a-z`) are allowed to be build-generated.

### Public projection

Extend `scripts/validate_public_projection.py` to prove:

- Timeline branch uses `global_route='timeline/'`;
- Corporium uses `human_route='corporium/'`;
- Works uses `human_route='works/'`;
- Culture family uses `global_route='context/culture/'`.

### Homepage

Use existing homepage/reader validators where possible; add only focused assertions needed for:

- exactly five primary gateway rows unchanged;
- Ways in contains Story, Timeline, Collection, Works and valid routes;
- secondary corridor remains distinct from primary gateway markup;
- Explore and Sources remain reachable;
- Questions and A–Z remain reachable quietly.

### Discovery/authority

Tests/validators must prove discovery and site-authority builders derive primary gateways from House authority rather than an independent hard-coded five-route table.

## Orientation-document convergence

Update current operating documentation to state:

- `docs/POTATO-HOUSE-CONSTITUTION.md` + `data/house/public-surfaces.json` own public route identity.
- `manifest.json` owns archive branch/pathway relationships and deep Explore semantics, not top-level public route identity.
- World, not World Map, is the fifth primary gateway.
- `main` is the current deployment base; do not refer to an old consolidation branch as the active workspace.
- Mature reader forms include Story, Timeline, Collection, Works, Questions, A–Z, Explore, Sources.

Historical specs remain historical; do not rewrite old design documents merely to make them look current.

## Non-goals

- No sixth primary homepage gateway.
- No display of all ten Domain Rooms on Home.
- No mass physical folder reorganization.
- No framework rewrite.
- No graph dashboard on Home.
- No automatic homepage ranking from readiness/centrality.
- No migration of canonical creative knowledge into `works/index.html`.
- No rename of `/corporium/` in this wave.
- No deletion of legacy source strata unless a separate exact dependency audit proves them redundant.

## Success criteria

1. Exactly five primary subject doors remain stable.
2. Story, Collection, Works, Questions, A–Z, and Context are registered public surfaces.
3. Public-surface schema is extensible beyond 15 total surfaces.
4. Registry and topology cannot drift silently.
5. Timeline, Collection, Works, and Culture route through their strongest public surfaces.
6. `/works/` provides a useful public reader over the existing creative archive.
7. Home exposes Story/Timeline/Collection/Works as a subordinate Ways-in corridor.
8. Discovery and site-authority builders consume House route authority.
9. Current orientation docs describe the same route authority as the code.
10. Full repository quality checks and exact final `_site` verification remain green.
