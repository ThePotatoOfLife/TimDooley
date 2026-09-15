import assert from 'node:assert/strict';

class FakeElement {
  constructor() { this.listeners = new Map(); this.children = []; this.title = ''; this.value = ''; }
  addEventListener(type, fn) { this.listeners.set(type, fn); }
  setAttribute() {}
  appendChild(node) { this.children.push(node); }
  replaceChildren(...nodes) { this.children = nodes; }
}

const input = new FakeElement();
const elements = new Map([['search', input]]);
globalThis.document = {
  body: new FakeElement(),
  getElementById(id) { return elements.get(id) || null; },
  createElement() { return new FakeElement(); },
};
globalThis.window = globalThis;
globalThis.CustomEvent = class CustomEvent { constructor(type, init={}) { this.type = type; this.detail = init.detail; } };
globalThis.dispatchEvent = () => true;

const subdivisionSelections = [];
window.__potatoAtlasSubdivisions = {
  async select(id, options={}) { subdivisionSelections.push({id, options}); return true; },
};
window.__potatoAtlasPlaces = { search() { return []; } };
window.goCountry = () => {};

globalThis.fetch = async url => {
  const text = String(url);
  if (text.includes('data/countries/index.json')) {
    return { ok:true, json:async()=>({countries:[{iso3:'DNK',iso2:'DK',name:'Denmark'},{iso3:'USA',iso2:'US',name:'United States'}]}) };
  }
  if (text.includes('world-subdivisions/index.json')) {
    return { ok:true, json:async()=>({partitions:{
      USA:{search_records:[{id:'US-CA',name:'California',code:'CA',subdivision_type:'state',parent_iso3:'USA',parent_name:'United States'}]},
      DNK:{search_records:[{id:'DK-1083',name:'Region Syddanmark',code:'1083',subdivision_type:'region',parent_iso3:'DNK',parent_name:'Denmark'}]},
    }}) };
  }
  throw new Error(`unexpected fetch ${text}`);
};

await import(new URL('../world-map/3d-search.js?subdivision-search-regression=1', import.meta.url));

const dkResults = await window.__potatoAtlasSearch.search('Syddanmark', {limit:10});
assert.equal(dkResults[0]?.id, 'DK-1083', 'Danish region should be searchable from the unified search');
assert.equal(dkResults[0]?.type, 'Region');
assert.equal(dkResults[0]?.country, 'DNK');
assert.equal(dkResults[0]?.parentName, 'Denmark');

const caResults = await window.__potatoAtlasSearch.search('CA', {limit:10});
assert.equal(caResults[0]?.id, 'US-CA', 'subdivision code should be searchable');
assert.equal(caResults[0]?.type, 'State');

assert.equal(await window.__potatoAtlasSearch.focus(dkResults[0]), true);
assert.deepEqual(subdivisionSelections, [{id:'DK-1083', options:{fit:true}}]);

console.log('WORLD MAP SUBDIVISION SEARCH REGRESSION PASSED');
