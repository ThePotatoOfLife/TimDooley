# World Map Performance Budget Wave 1 Design

## Purpose

Keep extending the World Relational Atlas without allowing browsing cost, MapLibre style complexity, or generated artifacts to grow without bound. This wave is intentionally limited to subdivision data/rendering and the common budget contract. Places cache/search shards, render-stack micro-optimization, compatibility retirement, and additional geography are separate later waves.

## Measured baseline

Current committed subdivision artifacts:

- `data/world-subdivisions/USA.geo.json`: 389,005 bytes, 51 first-order units.
- `data/world-subdivisions/DNK.geo.json`: 551,315 bytes, 5 first-order regions.
- `data/world-subdivisions/index.json`: 13,645 bytes.

The current runtime creates one GeoJSON source plus hit/line/label layers per loaded country partition and retains every loaded partition for the page lifetime. That is acceptable for two partitions but scales linearly with browsing history.

## Invariants

1. Browsing cost is a function of the current viewport/selection, not the number of countries previously visited.
2. Subdivision rendering uses a fixed number of MapLibre sources/layers independent of the number of country partitions loaded over time.
3. Search remains geometry-free and continues to read `search_records` from the subdivision index.
4. `?subdivision=` deep links, the canonical `#panel` inspector, `window.__potatoAtlasSubdivisions.select()`, one-shot camera fitting, and country-opening behavior remain compatible.
5. Missing population stays missing; no optimization may invent or coerce unknown values to zero.
6. Existing USA and Denmark geometry/provenance remain byte-for-byte unchanged in this wave.
7. No polling and no additional `MutationObserver` are introduced.
8. Generated artifact budgets and runtime memory/render budgets are explicit, validated, and inspectable.

## Artifact and runtime budget contract

The subdivision index gains a top-level `runtime_budget` object:

```json
{
  "partition_max_bytes": 1500000,
  "rendered_max_bytes": 3000000,
  "rendered_max_partitions": 4,
  "cache_max_bytes": 6000000,
  "cache_max_partitions": 8
}
```

Each partition descriptor gains an exact `bytes` field matching the committed file size. Validation fails when metadata diverges from disk or when a single presentation partition exceeds `partition_max_bytes`.

These numbers are derived from the measured first wave rather than arbitrary country counts: the largest current partition is 551,315 bytes, so 1.5 MB provides about 2.7× per-partition headroom; a 3 MB active-render budget allows several comparable partitions in one regional viewport; a 6 MB warm cache keeps useful recent data without unbounded accumulation. Future data waves may adjust the numbers only through an explicit design/validator change.

## Fixed-cost subdivision renderer

`world-map/3d-subdivisions.js` changes from per-country MapLibre infrastructure to one shared rendering surface:

- source: `atlas-subdivisions-active`
- hit layer: `atlas-subdivision-hit`
- line layer: `atlas-subdivision-line`
- label layer: `atlas-subdivision-label`

Country partitions remain independent same-origin GeoJSON files. Loading a partition places its raw FeatureCollection in a bounded JavaScript cache. Only a budgeted set of relevant partitions is merged into the shared active source.

Click handling resolves the raw feature by stable subdivision id through the index/cache rather than trusting MapLibre's rendered feature properties. This preserves nested provenance/population objects for the inspector.

## Relevance and deterministic math

For each reconciliation:

1. A pending deep-link partition ranks first.
2. The currently selected partition ranks second.
3. Remaining viewport-overlapping partitions rank by squared distance from the current map center to the center of their declared `viewport_bounds`.
4. Ties break lexicographically by partition id.
5. Candidates are admitted until either `rendered_max_partitions` or `rendered_max_bytes` would be exceeded.
6. A deep-linked/selected partition is mandatory and therefore admitted first; the per-partition hard limit guarantees one mandatory partition cannot exceed the active byte budget by itself.

Squared geographic distance is used only for deterministic ordering, so no square root is required. It is not presented as geodesic distance.

## Bounded LRU cache

The raw partition cache tracks `lastUsed` and descriptor bytes. After every load/reconciliation, least-recently-used partitions are evicted until both `cache_max_partitions` and `cache_max_bytes` are satisfied.

Never evict:

- the currently selected partition;
- a partition currently rendered in the shared source;
- a partition needed by the pending deep link.

If protected entries alone exceed a cache budget, keep them and expose the over-budget condition through diagnostics rather than breaking selection. The hard per-partition validator and rendered budget make this an exceptional state.

## Diagnostics

`window.__potatoAtlasSubdivisions.status()` returns at least:

- `selected`
- `renderedPartitions`
- `renderedBytes`
- `cachedPartitions`
- `cacheBytes`
- `cacheHits`
- `cacheMisses`
- `cacheEvictions`
- budget values

The shared global diagnostics object mirrors cumulative cache hit/miss/eviction counters when available. This allows later performance work to be evidence-driven.

## Error handling

- Index/partition fetch failures remain non-fatal to the country map.
- A failed partition is removed from in-flight/cache state so a later retry is possible.
- A missing descriptor/path returns a clear error for explicit `select()` while viewport reconciliation logs and skips it.
- Active-source reconciliation is atomic at the FeatureCollection level: the source receives one final merged collection rather than repeated per-feature updates.

## Testing

TDD coverage must prove:

1. Budget metadata matches committed bytes and current artifacts remain below hard limits.
2. Loading USA then Denmark still creates exactly one subdivision source and exactly three subdivision layers.
3. Denmark deep-link fits exactly once and does not refit on `moveend`.
4. `select('US-CA')` and `select('DK-1083')` continue to work.
5. More candidate partitions than allowed by synthetic budget fixtures do not increase rendered partition/layer count past the budget.
6. LRU eviction removes an old unprotected cached partition while preserving selected/rendered partitions.
7. Existing USA 51/51, Denmark 5/5, provenance, missing-population, and syntax validations remain green.

## Non-goals

- Do not change the original USA or Denmark geometry files.
- Do not add new countries in this PR.
- Do not implement Places LRU/search shards in this PR.
- Do not switch to vector tiles in this PR.
- Do not retire `3d-ui.js` or other compatibility modules in this PR.
- Do not redesign the map panel, world bar, search UI, or map-state URL schema.
