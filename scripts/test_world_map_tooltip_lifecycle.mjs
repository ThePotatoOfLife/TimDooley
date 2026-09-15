import assert from 'node:assert/strict';
import { createTooltipService } from '../world-map/3d-tooltip.js';

class FakePopup {
  static instances = [];
  constructor(options = {}) {
    this.options = options;
    this.removed = false;
    FakePopup.instances.push(this);
  }
  setLngLat(value) { this.lngLat = value; return this; }
  setHTML(value) { this.html = value; return this; }
  addTo(map) { this.map = map; this.removed = false; return this; }
  remove() { this.removed = true; return this; }
}

const mapHandlers = new Map();
const map = {
  on(type, handler) { mapHandlers.set(type, handler); },
};
const domHandlers = new Map();
const eventTarget = {
  addEventListener(type, handler) { domHandlers.set(type, handler); },
};

const tooltip = createTooltipService(map, { PopupClass:FakePopup, eventTarget });
assert.equal(FakePopup.instances.length, 1, 'one transient popup instance should serve all hover owners');

const first = tooltip.nextGeneration('country');
assert.equal(tooltip.show('country', {lng:12,lat:55}, '<b>Denmark</b>', first), true);
assert.equal(tooltip.state().visible, true);
assert.equal(tooltip.state().owner, 'country');

const second = tooltip.nextGeneration('country');
assert.equal(tooltip.show('country', {lng:13,lat:56}, 'stale', first), false, 'older async generations must not reopen/move the tooltip');
assert.equal(tooltip.state().staleSuppressions, 1);
assert.equal(tooltip.show('country', {lng:13,lat:56}, '<b>Current</b>', second), true);

mapHandlers.get('dragstart')?.();
assert.equal(tooltip.state().visible, false, 'drag start must invalidate transient hover');
assert.equal(FakePopup.instances[0].removed, true);

const third = tooltip.nextGeneration('country');
tooltip.show('country', {lng:14,lat:57}, 'again', third);
mapHandlers.get('zoomstart')?.();
assert.equal(tooltip.state().visible, false, 'zoom start must invalidate transient hover');

const fourth = tooltip.nextGeneration('axis');
tooltip.show('axis', {lng:0,lat:80}, 'axis', fourth);
domHandlers.get('potato-atlas-projection-change')?.();
assert.equal(tooltip.state().visible, false, 'projection changes must invalidate transient hover');

const fifth = tooltip.nextGeneration('country');
tooltip.show('country', {lng:10,lat:50}, 'country', fifth);
assert.equal(tooltip.clear('axis'), false, 'one owner must not clear another owner tooltip');
assert.equal(tooltip.clear('country'), true);
assert.equal(tooltip.state().visible, false);
assert.ok(tooltip.state().invalidations >= 4);

console.log('WORLD MAP TOOLTIP LIFECYCLE REGRESSION PASSED');
