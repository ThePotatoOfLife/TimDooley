import assert from 'node:assert/strict';

class FakeElement {
  constructor() { this.hidden = false; this.style = {}; this.innerHTML = ''; this.id = ''; }
  appendChild() {}
  addEventListener() {}
  querySelector() { return new FakeElement(); }
}

const elements = new Map();
const mapwrap = new FakeElement();
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
  querySelector(selector) { return selector === '.mapwrap' ? mapwrap : null; },
};

globalThis.location = { href: 'https://example.test/world-map/' };
globalThis.history = { replaceState() {} };
globalThis.CustomEvent = class CustomEvent { constructor(type, init={}) { this.type = type; this.detail = init.detail; } };
globalThis.window = globalThis;
globalThis.dispatchEvent = () => true;

const california = {
  type: 'Feature',
  properties: {
    id: 'US-CA', name: 'California', code: 'CA', subdivision_type: 'state',
    population: { value: 39431263, period: 2025, source: 'fixture' }, area_km2: 423967,
  },
  geometry: { type: 'Polygon', coordinates: [[[-124,32],[-114,32],[-114,42],[-124,42],[-124,32]]] },
};

const handlers = new Map();
const sources = new Map();
const layers = new Map();
let fitCount = 0;
const fakeMap = {
  getBounds() { return { getWest:()=>-125, getEast:()=>-66, getSouth:()=>24, getNorth:()=>50 }; },
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
  if (text.includes('world-subdivisions/index.json')) {
    return { ok:true, json:async()=>({ partitions:{ USA:{path:'USA.geo.json'} } }) };
  }
  if (text.includes('world-subdivisions/USA.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[california] }) };
  }
  throw new Error(`unexpected fetch ${text}`);
};

await import(new URL('../world-map/3d-subdivisions.js?freeze-regression=1', import.meta.url));

const click = handlers.get('click:atlas-subdivision-hit');
const moveend = handlers.get('moveend:*');
assert.equal(typeof click, 'function');
assert.equal(typeof moveend, 'function');

await click({ features:[california], originalEvent:{} });
assert.equal(fitCount, 1, 'clicking a state should fit exactly once');
await moveend();
assert.equal(fitCount, 1, 'moveend after state selection must not refit the same state');

console.log('WORLD MAP SUBDIVISION FREEZE REGRESSION PASSED');