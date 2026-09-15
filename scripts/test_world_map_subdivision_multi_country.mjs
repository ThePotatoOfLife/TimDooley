import assert from 'node:assert/strict';

class FakeElement {
  constructor() { this.hidden = false; this.style = {}; this.innerHTML = ''; this.id = ''; }
  appendChild() {}
  addEventListener() {}
  querySelector() { return new FakeElement(); }
}

const elements = new Map();
globalThis.document = {
  head: new FakeElement(),
  getElementById(id) { return elements.get(id) || null; },
  createElement() {
    const element = new FakeElement();
    Object.defineProperty(element, 'id', {
      get() { return this._id || ''; },
      set(value) { this._id = value; if (value) elements.set(value, this); },
    });
    return element;
  },
};

globalThis.location = { href: 'https://example.test/world-map/?subdivision=DK-1083' };
globalThis.history = { replaceState() {} };
globalThis.CustomEvent = class CustomEvent { constructor(type, init={}) { this.type = type; this.detail = init.detail; } };
globalThis.window = globalThis;
globalThis.dispatchEvent = () => true;

const syddanmark = {
  type: 'Feature',
  properties: {
    id: 'DK-1083', name: 'Region Syddanmark', code: '1083', subdivision_type: 'region',
    parent_iso3: 'DNK', parent_name: 'Denmark',
    geometry_source: 'Danish Agency for Climate Data (DAWA/Dataforsyningen)',
  },
  geometry: { type: 'Polygon', coordinates: [[[8.0,54.7],[10.8,54.7],[10.8,55.7],[8.0,55.7],[8.0,54.7]]] },
};

const handlers = new Map();
const sources = new Map();
const layers = new Map();
const fetched = [];
let fitCount = 0;
const fakeMap = {
  getBounds() { return { getWest:()=>7.7, getEast:()=>12.9, getSouth:()=>54.4, getNorth:()=>57.9 }; },
  getSource(id) { return sources.get(id) || null; },
  addSource(id, source) { sources.set(id, source); },
  getLayer(id) { return layers.get(id) || null; },
  addLayer(layer) { layers.set(layer.id, layer); },
  getCanvas() { return { style:{} }; },
  on(event, layerOrHandler, maybeHandler) {
    const layer = typeof layerOrHandler === 'string' ? layerOrHandler : '*';
    const handler = typeof layerOrHandler === 'function' ? layerOrHandler : maybeHandler;
    handlers.set(`${event}:${layer}`, handler);
  },
  fitBounds() { fitCount += 1; },
};
window.__potatoAtlasMap = fakeMap;

globalThis.fetch = async url => {
  const text = String(url);
  fetched.push(text);
  if (text.includes('world-subdivisions/index.json')) {
    return {
      ok:true,
      json:async()=>({ partitions:{
        USA:{ path:'USA.geo.json', id_prefix:'US-', viewport_bounds:{west:-179.5,east:-65,south:17,north:72.5} },
        DNK:{ path:'DNK.geo.json', id_prefix:'DK-', viewport_bounds:{west:7.5,east:15.3,south:54.4,north:57.9} },
      } }),
    };
  }
  if (text.includes('world-subdivisions/DNK.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[syddanmark] }) };
  }
  if (text.includes('world-subdivisions/USA.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[] }) };
  }
  throw new Error(`unexpected fetch ${text}`);
};

await import(new URL('../world-map/3d-subdivisions.js?multi-country-regression=1', import.meta.url));

assert.ok(fetched.some(url => url.includes('world-subdivisions/DNK.geo.json')), 'DK deep link must load the DNK partition');
assert.equal(fitCount, 1, 'DK deep link should fit exactly once');
const moveend = handlers.get('moveend:*');
assert.equal(typeof moveend, 'function');
await moveend();
assert.equal(fitCount, 1, 'moveend after DK deep-link selection must not refit');
assert.equal(window.__potatoAtlasSubdivisions.selected, 'DK-1083');

console.log('WORLD MAP MULTI-COUNTRY SUBDIVISION REGRESSION PASSED');
