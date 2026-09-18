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

- `research.json` — **superseded-retained mixed research donor**. Preserve for provenance and unmigrated source-derived material; do not use as a current canonical owner.
- `book-research.json` — **retained source bridge** for the 2024 Great Book extraction. Keep while source citations depend on it.
- `2026-master-framework.json` — **historical donor** recording the conversation-developed 2026 synthesis; current definitions live in dedicated owners.
- `POTATOVERSE-DEEP-RESEARCH.md` and `POTATOVERSE-ALTERNATIVE-RESEARCH.md` — **historical readable research donors** pending final unique-content diff.
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
