import assert from 'node:assert/strict';
import fs from 'node:fs';

const places = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url), 'utf8');

for (const marker of [
  'DEFAULT_RUNTIME_BUDGET',
  'partitionCache',
  'inflightCountries',
  'renderedPartitions',
  'cacheBytes',
  'cacheHits',
  'cacheMisses',
  'cacheEvictions',
  'runtimeBudget',
  'evictCache',
  'activateRenderedPartition',
  'removePartitionFeatures',
  'compactSearchRecords',
  'population_rank',
  'renderedPartitions:',
  'renderedBytes:',
  'cachedPartitions:',
  'cachedBytes:',
]) {
  assert.ok(places.includes(marker), `Places bounded runtime missing marker: ${marker}`);
}

assert.ok(
  !places.includes('const loadedCountries = new Map()'),
  'Places must not keep the old unbounded visited-country map',
);
assert.ok(
  !places.includes('for (const state of loadedCountries.values())'),
  'detail rendering/search must not traverse every country ever visited',
);
assert.ok(
  places.includes("rendered_max_partitions: 2") &&
  places.includes("cache_max_partitions: 6") &&
  places.includes("cache_max_bytes: 8_388_608"),
  'runtime fallback budgets must preserve the canonical bounded limits',
);
assert.ok(
  places.includes('majorFeatureIds.has(id)'),
  'eviction must preserve IDs still owned by global-major geometry',
);
assert.ok(
  places.includes('selectedPartitionCode()'),
  'cache/render eviction must be able to protect the selected place partition',
);
assert.ok(
  places.includes('indexPayload?.search_records'),
  'place search must use the compact generated index rather than only resident geometry',
);

console.log('WORLD MAP PLACES BOUNDED RUNTIME REGRESSION PASSED');
