# Legacy consolidation registry

The project now uses canonical owners under `knowledge/`, curated navigation through `manifest.json`, and source/inference indexes rather than multiple competing root-level master files.

This directory records legacy strata that have been superseded, retired, or are awaiting safe migration. A legacy file is never treated as deleted history: Git commit/blob identifiers are retained so the exact historical version can still be recovered.

## Retired

### `knowledge.json`

- Role: early all-in-one Potato of Life / Tim Dooley master snapshot.
- Status: retired from the live branch after its durable identity, chronology, theology, symbolic and epistemic content had been promoted into canonical owners.
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

- `research.json` — dense Great Book/comparative research layer; some formulas still cite it.
- `book-research.json` — important 2024 Great Book extraction/source bridge.
- `2026-master-framework.json` — conversation-developed 2026 synthesis used as historical development evidence.
- `POTATOVERSE-DEEP-RESEARCH.md` and `POTATOVERSE-ALTERNATIVE-RESEARCH.md` — older readable research strata pending unique-content diff.
- `TIM-DOOLEY-LIFE-AND-MYTH-TIMELINE.md` — readable timeline still used by the public chronology layer.
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