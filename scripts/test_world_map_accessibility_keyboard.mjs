import assert from 'node:assert/strict';

class FakeDetails {
  constructor() {
    this.open = true;
    this.summary = {
      isConnected:true,
      focused:false,
      attrs:new Map(),
      focus(){ this.focused=true; },
      setAttribute(name,value){ this.attrs.set(name,value); },
    };
  }
  matches(selector) { return selector.includes('details'); }
  querySelector(selector) { return selector.includes('summary') ? this.summary : null; }
  closest() { return this; }
}
global.HTMLDetailsElement = FakeDetails;

const openMenu = new FakeDetails();
const secondMenu = new FakeDetails();
secondMenu.open = false;
const listeners = new Map();
global.document = {
  addEventListener(type,handler){ listeners.set(type,handler); },
  querySelectorAll(){ return [openMenu, secondMenu]; },
};
global.CustomEvent = class CustomEvent { constructor(type,options={}){this.type=type;this.detail=options.detail;} };
global.window = {
  addEventListener(){},
  dispatchEvent(){ return true; },
};

await import('../world-map/3d-accessibility.js');
const api = window.__potatoAtlasAccessibility;
assert.ok(api);
api.syncMenuAria(openMenu);
assert.equal(openMenu.summary.attrs.get('aria-expanded'),'true');

let prevented=false;
let stopped=false;
listeners.get('keydown')?.({
  key:'Escape',
  defaultPrevented:false,
  target:openMenu,
  preventDefault(){prevented=true;},
  stopPropagation(){stopped=true;},
});
await Promise.resolve();
assert.equal(openMenu.open,false,'Escape should close the active map menu');
assert.equal(openMenu.summary.attrs.get('aria-expanded'),'false');
assert.equal(openMenu.summary.focused,true,'Escape should restore focus to the menu summary');
assert.equal(prevented,true);
assert.equal(stopped,true);

// Only one map menu should remain open at a time on constrained layouts.
openMenu.open = true;
openMenu.summary.focused = false;
secondMenu.open = true;
listeners.get('toggle')?.({ target:secondMenu });
await Promise.resolve();
assert.equal(secondMenu.open,true,'newly opened menu remains open');
assert.equal(openMenu.open,false,'opening a second map menu closes the previous menu');
assert.equal(openMenu.summary.focused,false,'automatic sibling closure must not steal focus');
assert.equal(openMenu.summary.attrs.get('aria-expanded'),'false');
assert.equal(secondMenu.summary.attrs.get('aria-expanded'),'true');

console.log('WORLD MAP ACCESSIBILITY KEYBOARD REGRESSION PASSED');
