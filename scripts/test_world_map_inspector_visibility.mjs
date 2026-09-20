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
assert.ok(
  !bootstrap.includes("'./3d-ui.js'"),
  'retired broad Progressive UI must not remain in the live bootstrap registry',
);
assert.ok(
  !bootstrap.includes("'./3d-selection-ui.js'"),
  'retired Selection UI must not remain in the live bootstrap registry',
);

const { createInspectorVisibility } = await import(moduleUrl);

function element(initial = []) {
  const classes = new Set(initial);
  const listeners = new Map();
  const attributes = new Map();
  return {
    classList: {
      contains: name => classes.has(name),
      toggle(name, force) {
        const next = force === undefined ? !classes.has(name) : Boolean(force);
        if (next) classes.add(name); else classes.delete(name);
        return next;
      },
    },
    addEventListener(name, fn) { listeners.set(name, fn); },
    click() { listeners.get('click')?.({ preventDefault() {} }); },
    setAttribute(name, value) { attributes.set(name, String(value)); },
    getAttribute(name) { return attributes.get(name); },
    textContent: '',
  };
}

function eventBus() {
  const listeners = new Map();
  return {
    addEventListener(name, fn) {
      if (!listeners.has(name)) listeners.set(name, []);
      listeners.get(name).push(fn);
    },
    emit(name, detail) { for (const fn of listeners.get(name) || []) fn({ detail }); },
    dispatchEvent() {},
  };
}

const app = element(['panel-collapsed']);
const panelToggle = element();
const mapInspectorToggle = element();
const bus = eventBus();
const storageValues = new Map();
const storage = {
  getItem: key => storageValues.get(key) ?? null,
  setItem: (key, value) => storageValues.set(key, String(value)),
};

const visibility = createInspectorVisibility({ app, panelToggle, mapInspectorToggle, eventTarget: bus, storage });
visibility.install();

assert.equal(visibility.isOpen(), false, 'inspector starts collapsed when no persisted preference exists');
panelToggle.click();
assert.equal(visibility.isOpen(), true, 'header Inspect button must open the inspector');
assert.equal(panelToggle.textContent, 'Close');
assert.equal(mapInspectorToggle.getAttribute('aria-pressed'), 'true');

visibility.setOpen(false, { persist: false });
mapInspectorToggle.click();
assert.equal(visibility.isOpen(), true, 'map Inspector button must open the inspector');

visibility.setOpen(false, { persist: false });
bus.emit('potato-atlas-working-selection-change', { selected: true, activeCode: 'DNK' });
assert.equal(visibility.isOpen(), true, 'selecting a country must reveal the inspector that already contains its full country overview');

visibility.setOpen(false, { persist: false });
bus.emit('potato-atlas-working-selection-change', { selected: false, activeCode: null });
assert.equal(visibility.isOpen(), false, 'clearing selection must not force the inspector open');

console.log('World Map inspector visibility regression passed');
