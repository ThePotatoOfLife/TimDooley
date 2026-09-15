import assert from 'node:assert/strict';
import fs from 'node:fs';

const hover = fs.readFileSync(new URL('../world-map/3d-hover.js', import.meta.url), 'utf8');
const lifecycle = fs.readFileSync(new URL('../world-map/3d-panel-lifecycle.js', import.meta.url), 'utf8');

function extractFunction(source, name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.ok(start >= 0, `missing ${name}`);
  const bodyStart = source.indexOf('{', start);
  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let i = bodyStart; i < source.length; i += 1) {
    const char = source[i];
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (char === '\\') { escaped = true; continue; }
      if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'" || char === '`') { quote = char; continue; }
    if (char === '{') depth += 1;
    if (char === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

const canOwnSource = extractFunction(hover, 'placesCanOwnCapitals');
const placesCanOwnCapitals = new Function(`"use strict"; ${canOwnSource}; return placesCanOwnCapitals;`)();
assert.equal(placesCanOwnCapitals({majorCount:3, error:null}), true);
assert.equal(placesCanOwnCapitals({majorCount:0, error:null}), false);
assert.equal(placesCanOwnCapitals({majorCount:3, error:'snapshot unavailable'}), false);

const installSource = extractFunction(hover, 'install');
assert.ok(!installSource.includes('installCapitalsWhenUseful()'), 'core hover install must not eagerly create legacy capital layers');
assert.ok(hover.includes("window.addEventListener('potato-atlas-places-ready'"), 'legacy capitals must be gated by Places readiness');
assert.ok(hover.includes('void installCapitalsWhenUseful()'), 'Places-unavailable path must retain legacy capital fallback');

assert.ok(lifecycle.includes("const placesLoaded = await window.__potatoAtlasLoadModule?.('Places', './3d-places.js')"), 'panel lifecycle must capture Places module load result');
assert.ok(lifecycle.includes('if (!placesLoaded)'), 'panel lifecycle must signal Places module failure');
assert.ok(lifecycle.includes("new CustomEvent('potato-atlas-places-ready'"), 'Places module failure must trigger capital fallback signal');
assert.ok(lifecycle.includes("majorCount:0"), 'fallback signal must report no usable major Places data');

console.log('WORLD MAP CAPITAL OWNERSHIP REGRESSION PASSED');
