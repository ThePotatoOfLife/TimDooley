import assert from 'node:assert/strict';

let href = 'https://example.test/world-map/?country=DNK&unowned=keep';
global.location = { get href() { return href; }, set href(value) { href = String(value); } };
global.history = {
  replaceState(_state, _title, url) { href = String(url); }
};
global.CustomEvent = class CustomEvent {
  constructor(type, options={}) { this.type=type; this.detail=options.detail; }
};
global.window = {
  events:[],
  dispatchEvent(event) { this.events.push(event); return true; },
};

const mod = await import('../world-map/3d-url-state.js');
const urlState = window.__potatoAtlasUrlState;
assert.ok(urlState);

urlState.claim('analytical', ['layers','lens','lensOption']);
urlState.claim('physical', ['physical']);
urlState.claim('evidence', ['evidenceLayer']);
assert.throws(() => urlState.claim('other', ['layers']), /already belongs/);

urlState.patch('analytical', { set:{layers:'stat.population'}, remove:['lens','lensOption'] });
let url = new URL(href);
assert.equal(url.searchParams.get('layers'), 'stat.population');
assert.equal(url.searchParams.get('country'), 'DNK');
assert.equal(url.searchParams.get('unowned'), 'keep');

urlState.patch('physical', { set:{physical:'physical.water.base'} });
url = new URL(href);
assert.equal(url.searchParams.get('layers'), 'stat.population');
assert.equal(url.searchParams.get('physical'), 'physical.water.base');

assert.throws(() => urlState.patch('physical', { set:{layers:'bad'} }), /not owned/);
assert.ok(urlState.snapshot().writeCount >= 2);
assert.equal(urlState.snapshot().claims.layers, 'analytical');

console.log('WORLD MAP URL STATE OWNER REGRESSION PASSED');
