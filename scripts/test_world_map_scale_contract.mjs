import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createScaleRuntime } from '../world-map/3d-scale.js';

const contract = JSON.parse(fs.readFileSync(new URL('../data/world-map-scale-contract.json', import.meta.url), 'utf8'));
const scale = createScaleRuntime(contract);

assert.equal(scale.bandForZoom(0), 'world');
assert.equal(scale.bandForZoom(2.6), 'macro-region');
assert.equal(scale.bandForZoom(3.5), 'region');
assert.equal(scale.bandForZoom(4.3), 'country');
assert.equal(scale.bandForZoom(6), 'subnational');
assert.equal(scale.bandForZoom(8.2), 'local');

assert.equal(scale.threshold('subdivisions', 'load'), 3.4);
assert.equal(scale.threshold('subdivisions', 'render'), 3.4);
assert.equal(scale.threshold('subdivisions', 'label'), 4.25);
assert.equal(scale.threshold('subdivisions', 'interact'), 3.4);
assert.equal(scale.threshold('places-detail', 'load'), 4.2);
assert.equal(scale.threshold('places-detail', 'render'), 4.2);
assert.equal(scale.threshold('places-detail', 'label'), 5.0);
assert.equal(scale.threshold('places-detail', 'interact'), 4.2);

// Raw lookup reports the mathematical band without memory.
assert.equal(scale.bandForZoom(4.21), 'country');

// Hysteresis prevents wheel/pinch jitter from flipping repeatedly around 4.2.
assert.equal(scale.transition('region', 4.21), 'region');
assert.equal(scale.transition('region', 4.31), 'region');
assert.equal(scale.transition('region', 4.32), 'country');
assert.equal(scale.transition('country', 4.15), 'country');
assert.equal(scale.transition('country', 4.08), 'country');
assert.equal(scale.transition('country', 4.07), 'region');

// Capability gates use the same hysteresis when prior state is known.
assert.equal(scale.capabilityActive('places-detail', 'load', 4.21, false), false);
assert.equal(scale.capabilityActive('places-detail', 'load', 4.32, false), true);
assert.equal(scale.capabilityActive('places-detail', 'load', 4.10, true), true);
assert.equal(scale.capabilityActive('places-detail', 'load', 4.07, true), false);
assert.equal(scale.capabilityActive('places-detail', 'load', 4.2, null), true);

assert.equal(scale.atLeast('country', 4.2), true);
assert.equal(scale.atLeast('subnational', 4.2), false);
assert.throws(() => scale.threshold('missing', 'load'), /capability/i);
assert.throws(() => scale.bandForZoom(Number.NaN), /finite/i);

console.log('WORLD MAP SCALE CONTRACT REGRESSION PASSED');
