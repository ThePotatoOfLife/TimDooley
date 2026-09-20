import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const moduleUrl = new URL('world-map/3d-inspector-visibility.js', root);
const bootstrap = fs.readFileSync(new URL('world-map/3d-bootstrap.js', root), 'utf8');

assert.ok(fs.existsSync(moduleUrl), 'selected-country inspector visibility controller must exist');
assert.ok(
  bootstrap.includes("loadAfterPaint('Inspector Visibility', './3d-inspector-visibility.js')"),
  'bootstrap must always load the small inspector visibility controller',
);
assert.ok(
  bootstrap.indexOf("loadAfterPaint('Inspector Visibility', './3d-inspector-visibility.js')") <
    bootstrap.indexOf("loadAfterPaint('Country selection', './3d-country-selection.js')"),
  'inspector visibility must be listening before Country selection restores or emits state',
);

function element(initial = []) {
  const classes = new Set(initial);
  const listeners = new Map();
  const attributes = new Map();
  let focusCount = 0;
  const node = {
    classList: {
      contains: name => classes.has(name),
      toggle(name, force) {
        const next = force === undefined ? !classes.has(name) : Boolean(force);
        if (next) classes.add(name); else classes.delete(name);
        return next;
      },
    },
    addEventListener(name, fn) { listeners.set(name, fn); },
    click() { listeners.get('click')?.({ currentTarget:node, preventDefault() {} }); },
    setAttribute(name, value) { attributes.set(name, String(value)); },
    getAttribute(name) { return attributes.get(name); },
    focus() { focusCount += 1; },
    get focusCount() { return focusCount; },
    textContent: '',
  };
  return node;
}

function eventBus() {
  const listeners = new Map();
  return {
    addEventListener(name, fn) {
      if (!listeners.has(name)) listeners.set(name, []);
      listeners.get(name).push(fn);
    },
    emit(name, detail) { for (const fn of listeners.get(name) || []) fn({ detail }); },
    emitEvent(name, event) { for (const fn of listeners.get(name) || []) fn(event); },
    dispatchEvent() {},
  };
}

const { createInspectorVisibility } = await import(moduleUrl);
const app = element(['panel-collapsed']);
const panel = element();
const panelToggle = element();
const mapInspectorToggle = element();
const bus = eventBus();
const keys = eventBus();
const storageValues = new Map();
const storage = {
  getItem: key => storageValues.get(key) ?? null,
  setItem: (key, value) => storageValues.set(key, String(value)),
};

const visibility = createInspectorVisibility({
  app, panel, panelToggle, mapInspectorToggle, eventTarget:bus, keyTarget:keys, storage,
});
visibility.install();

assert.equal(visibility.isOpen(), false, 'inspector starts collapsed');
assert.equal(panel.getAttribute('aria-hidden'), 'true');
assert.equal(panelToggle.getAttribute('aria-controls'), 'panel');
assert.equal(panelToggle.getAttribute('aria-expanded'), 'false');

panelToggle.click();
assert.equal(visibility.isOpen(), true, 'header Inspect button must open inspector');
assert.equal(panelToggle.textContent, 'Close');
assert.equal(panelToggle.getAttribute('aria-expanded'), 'true');
assert.equal(panel.getAttribute('aria-hidden'), 'false');
await Promise.resolve();
assert.equal(panel.focusCount, 1, 'explicit open should move focus into inspector');

let prevented = false, stopped = false;
keys.emitEvent('keydown', {
  key:'Escape',
  defaultPrevented:false,
  target:{ closest:() => null },
  preventDefault(){ prevented = true; },
  stopPropagation(){ stopped = true; },
});
await Promise.resolve();
assert.equal(visibility.isOpen(), false, 'Escape must close inspector');
assert.equal(prevented, true, 'inspector Escape must consume the key');
assert.equal(stopped, true, 'inspector Escape must not fall through to legacy map reset');
assert.equal(panelToggle.focusCount, 1, 'closing must return focus to the control that opened inspector');

mapInspectorToggle.click();
await Promise.resolve();
assert.equal(visibility.isOpen(), true, 'map Inspector button must open inspector');
visibility.setOpen(false, { persist:false, returnFocusOnClose:true });
await Promise.resolve();
assert.equal(mapInspectorToggle.focusCount, 1, 'focus return must preserve the actual opening control');

visibility.setOpen(false, { persist:false });
bus.emit('potato-atlas-working-selection-change', { selected:true, activeCode:'DNK' });
assert.equal(visibility.isOpen(), true, 'country selection must reveal inspector without forcing keyboard focus');
assert.equal(panel.focusCount, 2, 'selection-driven open must not add an extra focus move');

visibility.setOpen(false, { persist:false });
bus.emit('potato-atlas-working-selection-change', { selected:false, activeCode:null });
assert.equal(visibility.isOpen(), false, 'clearing selection must not force inspector open');

console.log('World Map inspector visibility regression passed');
