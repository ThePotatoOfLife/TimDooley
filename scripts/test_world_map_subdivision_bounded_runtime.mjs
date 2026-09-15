import assert from 'node:assert/strict';

class FakeElement {
  constructor() { this.hidden = false; this.style = {}; this.innerHTML = ''; this.id = ''; this.textContent = ''; }
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

globalThis.location = { href: 'https://example.test/world-map/' };
globalThis.history = { replaceState() {} };
globalThis.CustomEvent = class CustomEvent { constructor(type, init={}) { this.type = type; this.detail = init.detail; } };
globalThis.window = globalThis;

const selectedEvents = [];
globalThis.dispatchEvent = event => {
  if (event?.type === 'potato-atlas-subdivision-select') selectedEvents.push(event.detail);
  return true;
};

const california = {
  type: 'Feature',
  properties: {
    id: 'US-CA', name: 'California', code: 'CA', subdivision_type: 'state',
    parent_iso3: 'USA', parent_name: 'United States of America', area_km2: 423970,
    population: { value: 39431263, period: 2025, unit: 'persons', source: 'U.S. Census Bureau' },
    geometry_source: 'U.S. Census Bureau',
  },
  geometry: { type: 'Polygon', coordinates: [[[-124.4,32.5],[-114.1,32.5],[-114.1,42],[-124.4,42],[-124.4,32.5]]] },
};

const syddanmark = {
  type: 'Feature',
  properties: {
    id: 'DK-1083', name: 'Region Syddanmark', code: '1083', subdivision_type: 'region',
    parent_iso3: 'DNK', parent_name: 'Denmark',
    geometry_source: 'Danish Agency for Climate Data (DAWA/Dataforsyningen)',
    geometry_source_url: 'https://api.dataforsyningen.dk/regioner?format=geojson',
  },
  geometry: { type: 'Polygon', coordinates: [[[8.0,54.7],[10.8,54.7],[10.8,55.7],[8.0,55.7],[8.0,54.7]]] },
};

const handlers = new Map();
const sources = new Map();
const layers = new Map();
const fetched = [];
const fakeMap = {
  getBounds() { return { getWest:()=>20, getEast:()=>21, getSouth:()=>0, getNorth:()=>1 }; },
  getCenter() { return { lng:20.5, lat:0.5 }; },
  getSource(id) { return sources.get(id) || null; },
  addSource(id, source) {
    const state = { ...source, setData(data) { this.data = data; } };
    sources.set(id, state);
  },
  getLayer(id) { return layers.get(id) || null; },
  addLayer(layer) { layers.set(layer.id, layer); },
  getCanvas() { return { style:{} }; },
  on(event, layerOrHandler, maybeHandler) {
    const layer = typeof layerOrHandler === 'string' ? layerOrHandler : '*';
    const handler = typeof layerOrHandler === 'function' ? layerOrHandler : maybeHandler;
    handlers.set(`${event}:${layer}`, handler);
  },
  fitBounds() {},
};
window.__potatoAtlasMap = fakeMap;

globalThis.fetch = async url => {
  const text = String(url);
  fetched.push(text);
  if (text.includes('world-subdivisions/index.json')) {
    return {
      ok:true,
      json:async()=>({
        runtime_budget:{
          partition_max_bytes:1500000,
          rendered_max_bytes:3000000,
          rendered_max_partitions:4,
          cache_max_bytes:6000000,
          cache_max_partitions:8,
        },
        partitions:{
          USA:{ path:'USA.geo.json', bytes:389005, id_prefix:'US-', viewport_bounds:{west:-179.5,east:-65,south:17,north:72.5} },
          DNK:{ path:'DNK.geo.json', bytes:551315, id_prefix:'DK-', viewport_bounds:{west:7.5,east:15.3,south:54.4,north:57.9} },
        },
      }),
    };
  }
  if (text.includes('world-subdivisions/USA.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[california] }) };
  }
  if (text.includes('world-subdivisions/DNK.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[syddanmark] }) };
  }
  throw new Error(`unexpected fetch ${text}`);
};

await import(new URL('../world-map/3d-subdivisions.js?bounded-runtime-regression=1', import.meta.url));
await window.__potatoAtlasSubdivisions.loadPartition('USA');
await window.__potatoAtlasSubdivisions.loadPartition('DNK');

assert.deepEqual([...sources.keys()], ['atlas-subdivisions-active'], 'subdivisions must use exactly one shared GeoJSON source');
assert.deepEqual(
  [...layers.keys()].filter(id => id.startsWith('atlas-subdivision')).sort(),
  ['atlas-subdivision-hit', 'atlas-subdivision-label', 'atlas-subdivision-line'],
  'subdivisions must use exactly three shared layers independent of loaded country count',
);

assert.equal(await window.__potatoAtlasSubdivisions.select('US-CA', {fit:false}), true);
assert.equal(selectedEvents.at(-1)?.feature?.properties?.population?.source, 'U.S. Census Bureau', 'selection must preserve raw nested population provenance');
assert.equal(await window.__potatoAtlasSubdivisions.select('DK-1083', {fit:false}), true);
assert.equal(selectedEvents.at(-1)?.feature?.properties?.geometry_source_url, 'https://api.dataforsyningen.dk/regioner?format=geojson', 'selection must preserve raw nested/source provenance');

console.log('WORLD MAP BOUNDED SUBDIVISION RUNTIME REGRESSION PASSED');
