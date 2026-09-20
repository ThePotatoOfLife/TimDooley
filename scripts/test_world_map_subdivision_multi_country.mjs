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

const scaleRuntime = Object.freeze({
  threshold(capability, phase) {
    const values = { subdivisions:{ render:3.4, label:4.25 } };
    const value = values?.[capability]?.[phase];
    if (!Number.isFinite(value)) throw new Error(`unexpected scale threshold ${capability}.${phase}`);
    return value;
  },
  bandThreshold(band) {
    if (band !== 'subnational') throw new Error(`unexpected scale band ${band}`);
    return 5.8;
  },
});
window.__potatoAtlasScale = { ...scaleRuntime, ready:Promise.resolve(scaleRuntime) };

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
        CAN:{ path:'CAN.geo.json', id_prefix:'CA-', viewport_bounds:{west:-141.1,east:-52.5,south:41.6,north:83.2} },
      } }),
    };
  }
  if (text.includes('world-subdivisions/DNK.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[syddanmark] }) };
  }
  if (text.includes('world-subdivisions/USA.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[] }) };
  }
  if (text.includes('world-subdivisions/CAN.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[{
      type:'Feature',
      properties:{id:'CA-ON',name:'Ontario',code:'ON',subdivision_type:'province',parent_iso3:'CAN',parent_name:'Canada'},
      geometry:{type:'Polygon',coordinates:[[[-95,42],[-74,42],[-74,57],[-95,57],[-95,42]]]},
    }] }) };
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

const canadaLoaded = await window.__potatoAtlasSubdivisions.loadPartition('CAN');
assert.equal(canadaLoaded.data.features[0].properties.id, 'CA-ON');
assert.ok(fetched.some(url => url.includes('world-subdivisions/CAN.geo.json')), 'Canada partition must resolve through the generic loader');

console.log('WORLD MAP MULTI-COUNTRY SUBDIVISION REGRESSION PASSED');