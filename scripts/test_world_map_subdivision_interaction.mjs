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
const dispatched = [];
globalThis.dispatchEvent = event => { dispatched.push(event); return true; };

const california = {
  type: 'Feature',
  properties: {
    id: 'US-CA', name: 'California', code: 'CA', subdivision_type: 'state', parent_iso3:'USA', parent_name:'United States of America',
    population: { value: 39431263, period: 2025, source: 'fixture' },
    area_km2: 423967,
  },
  geometry: { type: 'Polygon', coordinates: [[[-124,32],[-114,32],[-114,42],[-124,42],[-124,32]]] },
};

const midtjylland = {
  type:'Feature',
  properties:{id:'DK-1082',name:'Region Midtjylland',code:'1082',subdivision_type:'region',parent_iso3:'DNK',parent_name:'Denmark'},
  geometry:{type:'Polygon',coordinates:[[[8.0,55.7],[10.8,55.7],[10.8,57.8],[8.0,57.8],[8.0,55.7]]]},
};

const handlers = new Map();
const sources = new Map();
const layers = new Map();
let fitCount = 0;
const fetched = [];

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
  fetched.push(text);
  if (text.includes('world-subdivisions/index.json')) {
    return { ok:true, json:async()=>({ partitions:{
      USA:{path:'USA.geo.json',id_prefix:'US-',parent_name:'United States of America',viewport_bounds:{west:-179.5,east:-65,south:17,north:72.5}},
      DNK:{path:'DNK.geo.json',id_prefix:'DK-',parent_name:'Denmark',viewport_bounds:{west:7.5,east:15.3,south:54.4,north:57.9}},
    } }) };
  }
  if (text.includes('world-subdivisions/USA.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[california] }) };
  }
  if (text.includes('world-subdivisions/DNK.geo.json')) {
    return { ok:true, json:async()=>({ type:'FeatureCollection', features:[midtjylland] }) };
  }
  throw new Error(`unexpected fetch ${text}`);
};

await import(new URL('../world-map/3d-subdivisions.js?subdivision-loop-test=3', import.meta.url));

const click = handlers.get('click:atlas-subdivision-hit-USA');
const moveend = handlers.get('moveend:*');
assert.equal(typeof click, 'function', 'state click handler should be installed');
assert.equal(typeof moveend, 'function', 'moveend handler should be installed');

click({ features:[california], originalEvent:{} });
assert.equal(fitCount, 1, 'clicking a state should fit its bounds exactly once');

await moveend();
assert.equal(fitCount,1,'the moveend caused by a state selection must not refit the already-selected state again');

const selectedDenmark = await window.__potatoAtlasSubdivisions.select('DK-1082');
assert.equal(selectedDenmark,true,'a subdivision declared by the index should be selectable without hard-coded country logic');
assert.ok(fetched.some(url => url.includes('DNK.geo.json')),'generic selection should lazy-load the declared Denmark partition');
assert.equal(window.__potatoAtlasSubdivisions.selected,'DK-1082');
assert.equal(fitCount,2,'generic subdivision selection should fit once');

const selectedEvent = dispatched.find(event => event.type === 'potato-atlas-subdivision-select' && event.detail?.id === 'DK-1082');
assert.ok(selectedEvent, 'generic subdivision selection should emit a selection event with feature context');
assert.equal(selectedEvent.detail.properties.parent_iso3, 'DNK');

window.__potatoAtlasSubdivisions.clear();
assert.equal(window.__potatoAtlasSubdivisions.selected, null, 'clear should remove persistent subdivision selection');
const clearEvent = dispatched.find(event => event.type === 'potato-atlas-subdivision-clear' && event.detail?.id === 'DK-1082');
assert.ok(clearEvent, 'clearing a subdivision should emit a lifecycle event so contextual overlays can fall back');

console.log('WORLD MAP SUBDIVISION INTERACTION PASSED');
