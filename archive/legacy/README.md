# Legacy consolidation registry

The project now uses canonical owners under `knowledge/`, curated navigation through `manifest.json`, and source/inference indexes rather than multiple competing root-level master files.

This directory records legacy strata that have been superseded, retired, or are awaiting safe migration. A legacy file is never treated as deleted history: Git commit/blob identifiers are retained so the exact historical version can still be recovered.

## Retired

### `knowledge.json`

- Role: early all-in-one Potato of Life / Tim Dooley master snapshot.
- Status: retired from the live branch after its durable identity, timeline, theology, symbolic and epistemic content had been promoted into canonical owners.
- Last live blob: `e7b838692eb86230c8ca9adba2197bab88f8b9fd`.
- Canonical successors include:
  - `knowledge/core/potatoverse-master-framework.json`
  - `knowledge/core/tim-dooley.json`
  - `knowledge/core/root-system.json`
  - `knowledge/core/potato-of-life-deep-structure.json`
  - `knowledge/core/symbolic-relational-synthesis.json`
  - `knowledge/indexes/source-index.json`
  - `knowledge/indexes/inference-ledger.json`

## Still live as legacy/source strata

These files remain at repository root until their unique content and downstream references have been fully migrated:

- `TIM-DOOLEY-LIFE-AND-MYTH-TIMELINE.md` — **retained timeline/source stratum** used for provenance and early roadmap context; canonical event identity lives in the timeline data owners.
- `THE-TURNING-APRIL-2025.md` — dedicated Turning document; remains a distinct historical/interpretive artifact.

## Migration rule

Before retiring any legacy file:

1. identify every unique claim, date, source and relation;
2. promote durable content into its canonical owner;
3. rewire live references;
4. preserve the final blob/commit identifier here;
5. remove the duplicate from live navigation;
6. only then delete it from the current branch.

The goal is less clutter **without provenance loss**.

## Retired research staging projections — 2026-09-18

### `data/potatoverse-alternative-directions.json`

- Role: structured 30-finding alternative Potato research staging layer.
- Status: retired after empirical biology, human ecology, food-system history and boundary material was promoted into `knowledge/science/potato-biology-ecology-development-canon.json` and the practice projection.
- Last live blob: `08b0469b3606af33879266a260509c46bf00f131`.
- Successors: `knowledge/science/potato-biology-ecology-development-canon.json`, `knowledge/biology/potato-growth-principles.json`, `knowledge/philosophy/potato-philosophy.json`.

### `data/potatoverse-alternative-links.json`

- Role: 30-edge staging relation graph keyed to the retired `ad01…ad30` finding IDs.
- Status: retired with its finding layer. The graph was not promoted wholesale because its endpoints were staging concepts rather than canonical graph identities; durable relations are preserved in the science/system synthesis instead.
- Last live blob: `640bfd1934542cc93210a2f6761336a3987b6687`.


### `data/potatoverse-deep-research.json`

- Role: 36-finding structured Deep Research staging corpus spanning project role synthesis, Thomas/Didymus comparison, potato biology and relational interpretation.
- Status: retired after durable material was absorbed by core role/symbolic owners, dedicated Thomas/Bible owners, the canonical potato science record and timeline/provenance layers.
- Last live blob: `2303206c6b5f80ac5f1e2790ce54e54fb89cfada`.
- Readable historical donor retained: `POTATOVERSE-DEEP-RESEARCH.md`.

### `data/potatoverse-deep-links.json`

- Role: 28-edge `drXX` staging relation graph tied only to the retired Deep Research corpus.
- Status: retired with its source layer; its staging endpoints were not promoted as a parallel canonical graph taxonomy.
- Last live blob: `c7ab44bec91d7cb96d3333a09444aafc7741ca44`.


### `POTATOVERSE-DEEP-RESEARCH.md`

- Role: readable Deep Research donor that originally summarized mixed Potato biology, Thomas/Didymus, symbolic and project-role findings.
- Status: retired after unique material was promoted into current science, philosophy, core, timeline and traditions owners; live staging JSON had already been retired.
- Last live blob: `d2acb04b954b83b13ac941f36c14252c89e55450`.

### `POTATOVERSE-ALTERNATIVE-RESEARCH.md`

- Role: readable Alternative Research donor covering potato evolution, diversity, domestication, food systems, stewardship and systems interpretation.
- Status: retired after externally sourced biology/human-ecology material was promoted into `knowledge/science/potato-biology-ecology-development-canon.json` and practice/symbolic owners.
- Last live blob: `7297ba28bb7a3ae05f3902948c57984faac3bf39`.


### `research.json`

- Role: former root mixed Great Book/comparative research layer.
- Status: retired after every substantive section was routed/promoted to current specialist owners and all open questions moved to `data/research-frontier.json`.
- Last live blob: `353678889ad4b46890319c812951ae494cf1e791`.
- Major successors include `knowledge/philosophy/potato-philosophy.json`, `knowledge/core/symbolic-relational-synthesis.json`, `knowledge/core/potatoverse-master-framework.json`, `knowledge/philosophy/timic-dynamics.json`, `knowledge/core/center-living-metabolism-expanded-atlas.json`, `knowledge/traditions/alchemy-transmutation-symbol-atlas.json`, `knowledge/traditions/adversarial-underworld-judgment-atlas.json`, `knowledge/timeline/developmental-genealogy.json`, and `data/research-frontier.json`.


### `2026-master-framework.json`

- Role: former root 2026 conversation-developed master synthesis.
- Status: retired after formula/model consumers and live source lists were rewired to current core, science, timeline, theology and world owners.
- Last live blob: `796c32f54109fafb611c83838b45ac5b3f56a43a`.
- Major successors include `knowledge/core/potatoverse-master-framework.json`, `knowledge/core/root-system.json`, `knowledge/core/tim-role-synthesis.json`, `knowledge/core/axis-world-model.json`, `knowledge/philosophy/timic-dynamics.json`, `knowledge/core/symbolic-relational-synthesis.json`, and `knowledge/science/tim-dooley-science-formalisms.json`.
- Historical specs/plans may still name this file because they document the repository at the time they were written.


### `book-research.json`

- Role: former root location of the 2024 Great Book extraction/provenance bridge.
- Status: root path retired after the full extraction was relocated intact to `knowledge/research/great-book-2024-source-extraction.json` and live consumers were rewired.
- Last live root blob: `9168248304e821b4af092c5c5f9c506b7db51fb1`.
- Current extraction owner: `knowledge/research/great-book-2024-source-extraction.json`.
- Note: this is a path retirement, not a content deletion. The extraction remains live because it preserves cross-domain source archaeology from the 2024 Great Book.


### `relational-objects.json`

- Role: orphaned root relational-symbol theory for Grave/Tomb/Mirror/Door/Vessel and observer-dependent semantics.
- Status: retired after the Law of Positional Meaning and temporal reinterpretation-as-graph-growth rules were promoted into `knowledge/core/symbolic-relational-synthesis.json` and `knowledge/philosophy/timic-dynamics.json`.
- Last live blob: `806538c82dcda0d00128f8841cfc7ca704ac5298`.
- No live consumer or canonical-source-map ownership remained at retirement.
