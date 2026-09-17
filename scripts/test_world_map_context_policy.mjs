import assert from 'node:assert/strict';
import { contextScaleBand, contextBudgets, contextVisibility } from '../world-map/3d-context-policy.js';

const calls = [];
const fakeScale = {
  bandForZoom(zoom) { calls.push(['bandForZoom', zoom]); return zoom >= 5 ? 'country' : 'region'; },
  transition(previousBand, zoom) { calls.push(['transition', previousBand, zoom]); return previousBand === 'region' && zoom < 5.25 ? 'region' : this.bandForZoom(zoom); },
};

assert.equal(contextScaleBand(fakeScale, null, 4.9), 'region');
assert.equal(contextScaleBand(fakeScale, 'region', 5.1), 'region', 'context scale should respect scale-runtime hysteresis');
assert.ok(calls.some(call => call[0] === 'transition'), 'context scale must use scale.transition once a prior band exists');

const browseWorld = contextBudgets({ band:'world', mode:'browse', pinCount:3, narrow:false });
assert.deepEqual(
  { active:browseWorld.active, pinned:browseWorld.pinned, total:browseWorld.total, pinnedCards:browseWorld.pinnedCards },
  { active:8, pinned:2, total:20, pinnedCards:3 }
);

const compareRegion = contextBudgets({ band:'region', mode:'compare', pinCount:6, narrow:false });
assert.equal(compareRegion.pinned, 3, 'compare mode should grant pinned countries a larger relation budget');
assert.equal(compareRegion.pinnedCards, 4, 'desktop card budget stays bounded even with many pins');

const narrowBrowse = contextBudgets({ band:'country', mode:'browse', pinCount:5, narrow:true });
assert.equal(narrowBrowse.pinnedCards, 2, 'narrow screens should keep the pinned rail bounded');

const evidence = contextVisibility({ band:'country', mode:'evidence' });
assert.equal(evidence.showActiveRelations, false);
assert.equal(evidence.emphasizeEvidence, true);
assert.equal(evidence.suppressDecorativeProjectOverlays, true);

const localBrowse = contextVisibility({ band:'local', mode:'browse' });
assert.equal(localBrowse.reduceAbstractRelations, true, 'local browse should prioritize physical/local context over abstract global lines');
assert.equal(localBrowse.showPlaceDetail, true);
assert.equal(localBrowse.showSubdivisionDetail, true);

console.log('World Map context policy tests passed');
