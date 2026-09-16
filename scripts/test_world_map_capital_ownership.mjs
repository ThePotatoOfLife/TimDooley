import assert from 'node:assert/strict';
import fs from 'node:fs';

const hover = fs.readFileSync(new URL('../world-map/3d-hover.js', import.meta.url), 'utf8');
const lifecycle = fs.readFileSync(new URL('../world-map/3d-panel-lifecycle.js', import.meta.url), 'utf8');

function extractFunction(source, name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.ok(start >= 0, `missing ${name}`);

  const paramsStart = source.indexOf('(', start);
  let paramsDepth = 0;
  let paramsEnd = -1;
  let quote = null;
  let escaped = false;
  for (let i = paramsStart; i < source.length; i += 1) {
    const char = source[i];
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (char === '\\') { escaped = true; continue; }
      if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'" || char === '`') { quote = char; continue; }
    if (char === '(') paramsDepth += 1;
    if (char === ')') {
      paramsDepth -= 1;
      if (paramsDepth === 0) { paramsEnd = i; break; }
    }
  }
  assert.ok(paramsEnd >= 0, `unterminated parameters for ${name}`);

  const bodyStart = source.indexOf('{', paramsEnd);
  assert.ok(bodyStart >= 0, `missing body for ${name}`);
  let depth = 0;
  quote = null;
  escaped = false;
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
const placesCanOwnCapitals = new Function('window', `"use strict"; ${canOwnSource}; return placesCanOwnCapitals;`)({});
assert.equal(placesCanOwnCapitals({majorCount:3, error:null}), true);
assert.equal(placesCanOwnCapitals({majorCount:0, error:null}), false);
assert.equal(placesCanOwnCapitals({majorCount:3, error:'snapshot unavailable'}), false);

const livePlaces = { __potatoAtlasPlaces:{ status:() => ({majorCount:4, error:null}) } };
const liveOwner = new Function('window', `"use strict"; ${canOwnSource}; return placesCanOwnCapitals;`)(livePlaces);
assert.equal(liveOwner({majorCount:0, error:'stale event'}), true, 'live Places status should win over stale event detail');

const installSource = extractFunction(hover, 'install');
assert.ok(!installSource.includes('installCapitalsWhenUseful()'), 'core hover install must not eagerly create legacy capital layers');
assert.ok(hover.includes("window.addEventListener('potato-atlas-places-ready'"), 'legacy capitals must be gated by Places readiness');
assert.ok(hover.includes('void installCapitalsWhenUseful()'), 'Places-unavailable path must retain legacy capital fallback');

assert.ok(hover.includes('async function sharedInteraction()'), 'fallback capitals must be able to acquire the shared Interaction Router on direct loads');
assert.ok(hover.includes("interaction.register('fallback-capitals'"), 'fallback capitals need one semantic interaction owner');
assert.ok(hover.includes("layers:['capital-cities']"), 'fallback capital owner must target the capital point layer');
assert.ok(hover.includes("objectType:'capital'"), 'fallback capitals must declare their semantic object type');
assert.ok(hover.includes('clickPriority:68'), 'fallback capital click must outrank country/hub context while remaining below Infrastructure/Gateways/Places');
assert.ok(hover.includes('hoverPriority:68'), 'fallback capital hover must share the same semantic priority');
assert.ok(hover.includes('enabled:() => capitalsVisible'), 'hidden fallback capitals must not win interaction arbitration');
assert.ok(hover.includes("tooltip.nextGeneration('capital')"), 'fallback capital hover must keep shared tooltip generations');
assert.ok(hover.includes("tooltip.invalidate('capital-leave')"), 'fallback capital leave must invalidate shared tooltip state');
assert.ok(hover.includes('if (code && window.goCountry) void window.goCountry(code);'), 'fallback capital click must preserve country navigation');
for (const direct of [
  "map.on('mousemove', 'capital-cities'",
  "map.on('mouseleave', 'capital-cities'",
  "map.on('click', 'capital-cities'",
]) {
  assert.ok(!hover.includes(direct), `fallback capitals must retire direct layer interaction ownership: ${direct}`);
}
assert.ok(!hover.includes('__potatoAtlasOverlayHandled'), 'fallback capital path must not keep the compatibility event flag alive');

assert.ok(lifecycle.includes("const placesLoaded = await window.__potatoAtlasLoadModule?.('Places', './3d-places.js')"), 'panel lifecycle must capture Places module load result');
assert.ok(lifecycle.includes('if (!placesLoaded)'), 'panel lifecycle must signal Places module failure');
assert.ok(lifecycle.includes("new CustomEvent('potato-atlas-places-ready'"), 'Places module failure must trigger capital fallback signal');
assert.ok(lifecycle.includes("majorCount:0"), 'fallback signal must report no usable major Places data');

console.log('WORLD MAP CAPITAL OWNERSHIP REGRESSION PASSED');
