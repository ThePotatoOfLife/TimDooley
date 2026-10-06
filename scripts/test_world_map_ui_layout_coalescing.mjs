import assert from 'node:assert/strict';

class FakeElement {
  constructor(tag = 'div') {
    this.tagName = String(tag).toUpperCase();
    this.id = '';
    this.hidden = false;
    this.dataset = {};
    this.children = [];
    this.parentElement = null;
    this.style = {};
    this.textContent = '';
    this.innerHTML = '';
    this.isConnected = true;
  }
  appendChild(node) {
    if (node.parentElement) node.parentElement.children = node.parentElement.children.filter(child => child !== node);
    node.parentElement = this;
    node.isConnected = true;
    this.children.push(node);
    return node;
  }
  append(...nodes) { nodes.forEach(node => this.appendChild(node)); }
  before() {}
  setAttribute() {}
  addEventListener() {}
  querySelector() { return null; }
  closest() { return null; }
}

globalThis.Element = FakeElement;
const elements = new Map();
const head = new FakeElement('head');
const mapwrap = new FakeElement('div');
mapwrap.className = 'mapwrap';
const app = new FakeElement('div'); app.id = 'atlasApp'; elements.set(app.id, app);

function registerElement(node) { if (node.id) elements.set(node.id, node); return node; }

globalThis.document = {
  head,
  createElement(tag) {
    const node = new FakeElement(tag);
    Object.defineProperty(node, 'id', {
      get() { return this._id || ''; },
      set(value) { this._id = value; if (value) elements.set(value, this); },
    });
    return node;
  },
  getElementById(id) { return elements.get(id) || null; },
  querySelector(selector) {
    if (selector === '.mapwrap') return mapwrap;
    if (selector === '#atlasApp') return app;
    if (selector.startsWith('#')) return elements.get(selector.slice(1)) || null;
    return null;
  },
  addEventListener() {},
};

globalThis.window = globalThis;
const listeners = new Map();
window.addEventListener = (type, handler) => {
  if (!listeners.has(type)) listeners.set(type, []);
  listeners.get(type).push(handler);
};
let layoutEvents = 0;
window.dispatchEvent = event => {
  if (event?.type === 'potato-atlas-ui-layout-change') layoutEvents += 1;
  return true;
};
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init = {}) { this.type = type; this.detail = init.detail; }
};

await import(new URL('../world-map/3d-ui-layout.js?coalescing-regression=1', import.meta.url));
const api = window.__potatoAtlasUILayout;
assert.ok(api?.register && api?.refresh, 'UI layout API must install');
const baselineEvents = layoutEvents;

const one = registerElement(new FakeElement()); one.id = 'surface-one'; elements.set(one.id, one);
const two = registerElement(new FakeElement()); two.id = 'surface-two'; elements.set(two.id, two);
const three = registerElement(new FakeElement()); three.id = 'surface-three'; elements.set(three.id, three);

api.register({id:'one', zone:'left-status', element:one, priority:10});
api.register({id:'two', zone:'left-status', element:two, priority:20});
api.register({id:'three', zone:'left-status', element:three, priority:30});

assert.equal(
  layoutEvents,
  baselineEvents,
  'registration burst must schedule rather than synchronously emit repeated layout-change events',
);
await new Promise(resolve => queueMicrotask(resolve));
assert.equal(layoutEvents - baselineEvents, 1, 'registration burst must coalesce into one layout pass/event');

const host = document.getElementById('atlasUILeftStatus');
assert.ok(host, 'left-status host must exist after scheduled refresh');
assert.deepEqual(host.children.map(node => node.id), ['surface-one','surface-two','surface-three']);

const state = api.getState();
assert.equal(state.filter(row => ['one','two','three'].includes(row.id)).length, 3);

console.log('WORLD MAP UI LAYOUT COALESCING REGRESSION PASSED');
