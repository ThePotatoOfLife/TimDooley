import assert from 'node:assert/strict';
import fs from 'node:fs';

const hoverUrl = new URL('../world-map/3d-hover.js', import.meta.url);
const source = fs.readFileSync(hoverUrl, 'utf8');

function extractFunction(name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.ok(start >= 0, `missing ${name} in world-map/3d-hover.js`);
  const bodyStart = source.indexOf('{', start);
  assert.ok(bodyStart >= 0, `missing body for ${name}`);

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

assert.ok(source.includes("await import(versionedModule('./3d-tooltip.js'))"), 'hover runtime must load the shared Tooltip service');
assert.ok(source.includes('window.__potatoAtlasTooltip'), 'hover runtime must publish/reuse the shared Tooltip service');
assert.ok(!source.includes('const popup = new maplibregl.Popup'), 'country hover must not own a private transient popup');

const handleCountryHoverSource = extractFunction('handleCountryHover');
const clearCountryHoverSource = extractFunction('clearCountryHover');
const bindCountryHoverSource = extractFunction('bindCountryHover');
const handlers = new Map();
const canvas = { style:{} };
const map = {
  on(event, layer, handler) { handlers.set(`${event}:${layer}`, handler); },
  getCanvas() { return canvas; },
};

const renders = [];
let generation = 0;
let invalidations = 0;
const tooltip = {
  nextGeneration() { generation += 1; return generation; },
  show(owner, lngLat, html, expectedGeneration) {
    if (expectedGeneration !== generation) return false;
    renders.push({ owner, html, lngLat });
    return true;
  },
  invalidate() { generation += 1; invalidations += 1; },
};

const pending = [];
function countryHtml(properties) {
  return new Promise(resolve => pending.push({ code:properties.iso3, resolve }));
}

const bindCountryHover = new Function(
  'map', 'tooltip', 'countryHtml',
  `"use strict";
   let countryHoverKey = '';
   let countryHoverEvent = null;
   let countryHoverHtml = null;
   let countryHoverGeneration = null;
   const directCountryHover = new Map();
   ${handleCountryHoverSource}
   ${clearCountryHoverSource}
   ${bindCountryHoverSource}
   return bindCountryHover;`,
)(map, tooltip, countryHtml);

bindCountryHover('countries-fill');
const move = handlers.get('mousemove:countries-fill');
const leave = handlers.get('mouseleave:countries-fill');
assert.equal(typeof move, 'function');
assert.equal(typeof leave, 'function');

const flush = () => new Promise(resolve => setImmediate(resolve));
const eventFor = (code, lng, lat) => ({
  lngLat:{lng, lat},
  features:[{properties:{iso3:code}}],
});

// Two asynchronous hover lookups finish out of order while the pointer moves.
move(eventFor('USA', -100, 40));
move(eventFor('DNK', 10, 56));
assert.equal(pending.length, 2, 'fixture must create two pending country hover lookups');

pending[1].resolve('<b>Denmark</b>');
await flush();
assert.deepEqual(renders, [
  {owner:'country', html:'<b>Denmark</b>', lngLat:{lng:10, lat:56}},
], 'newest hover should render when it resolves first');

pending[0].resolve('<b>United States</b>');
await flush();
assert.deepEqual(renders, [
  {owner:'country', html:'<b>Denmark</b>', lngLat:{lng:10, lat:56}},
], 'older asynchronous hover must not move/reopen the shared tooltip');

// Leaving the country layer invalidates work already in flight.
move(eventFor('USA', -99, 41));
assert.equal(pending.length, 3);
leave();
const renderedBeforeLateLeave = renders.length;
pending[2].resolve('<b>United States late</b>');
await flush();
assert.equal(renders.length, renderedBeforeLateLeave, 'late hover work must not reopen tooltip after mouseleave');
assert.ok(invalidations >= 1, 'mouseleave must invalidate the shared transient tooltip generation');
assert.equal(canvas.style.cursor, '', 'mouseleave must restore the map cursor');

// Moving many pixels within one country should share one async lookup, while the
// resolved tooltip follows the latest pointer position.
bindCountryHover('countries-extrude');
const moveExtrude = handlers.get('mousemove:countries-extrude');
const pendingBeforeSameCountry = pending.length;
const rendersBeforeSameCountry = renders.length;
moveExtrude(eventFor('DEU', 8, 50));
moveExtrude(eventFor('DEU', 9, 51));
moveExtrude(eventFor('DEU', 10, 52));
assert.equal(
  pending.length - pendingBeforeSameCountry,
  1,
  'same-country mousemove burst must share one asynchronous country lookup',
);
pending[pendingBeforeSameCountry].resolve('<b>Germany</b>');
await flush();
assert.deepEqual(
  renders.slice(rendersBeforeSameCountry),
  [{owner:'country', html:'<b>Germany</b>', lngLat:{lng:10, lat:52}}],
  'resolved same-country tooltip must use the latest pointer location',
);

console.log('WORLD MAP HOVER ARTIFACT REGRESSION PASSED');
