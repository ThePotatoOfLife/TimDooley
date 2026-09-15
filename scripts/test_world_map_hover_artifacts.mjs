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
      if (escaped) {
        escaped = false;
        continue;
      }
      if (char === '\\') {
        escaped = true;
        continue;
      }
      if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'" || char === '`') {
      quote = char;
      continue;
    }
    if (char === '{') depth += 1;
    if (char === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

const bindCountryHoverSource = extractFunction('bindCountryHover');
const handlers = new Map();
const canvas = { style:{} };
const map = {
  on(event, layer, handler) { handlers.set(`${event}:${layer}`, handler); },
  getCanvas() { return canvas; },
};

const popupRemovals = [];
const popup = { remove() { popupRemovals.push(true); } };
const renders = [];
function showPopup(event, html) {
  renders.push({ html, lngLat:event.lngLat });
}

const pending = [];
function countryHtml(properties) {
  return new Promise(resolve => pending.push({ code:properties.iso3, resolve }));
}

const bindCountryHover = new Function(
  'map', 'showPopup', 'countryHtml', 'popup',
  `"use strict"; ${bindCountryHoverSource}; return bindCountryHover;`,
)(map, showPopup, countryHtml, popup);

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

// Reproduce the reported black/trailing hover artifact: two asynchronous hover
// lookups finish out of order while the pointer has already moved countries.
move(eventFor('USA', -100, 40));
move(eventFor('DNK', 10, 56));
assert.equal(pending.length, 2, 'fixture must create two pending country hover lookups');

pending[1].resolve('<b>Denmark</b>');
await flush();
assert.deepEqual(renders, [
  {html:'<b>Denmark</b>', lngLat:{lng:10, lat:56}},
], 'newest hover should render when it resolves first');

pending[0].resolve('<b>United States</b>');
await flush();
assert.deepEqual(renders, [
  {html:'<b>Denmark</b>', lngLat:{lng:10, lat:56}},
], 'an older asynchronous hover must not yank the popup back to a stale country/position');

// Leaving the country layer must invalidate work already in flight. A late
// scalar lookup must not reopen the dark popup after mouseleave.
move(eventFor('USA', -99, 41));
assert.equal(pending.length, 3);
leave();
const renderedBeforeLateLeave = renders.length;
pending[2].resolve('<b>United States late</b>');
await flush();
assert.equal(renders.length, renderedBeforeLateLeave, 'late hover work must not reopen popup after mouseleave');
assert.ok(popupRemovals.length >= 1, 'mouseleave must remove the popup');
assert.equal(canvas.style.cursor, '', 'mouseleave must restore the map cursor');

// Moving many pixels within one country should not launch one asynchronous
// scalar lookup per mousemove. One lookup should resolve at the latest pointer
// position so the popup can follow the cursor without request churn/flicker.
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
  [{html:'<b>Germany</b>', lngLat:{lng:10, lat:52}}],
  'resolved same-country popup must use the latest pointer location',
);

console.log('WORLD MAP HOVER ARTIFACT REGRESSION PASSED');
