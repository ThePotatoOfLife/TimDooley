import assert from 'node:assert/strict';
import { antimeridianAwareBounds } from '../world-map/3d-geo-kernel.js';
import { createInteractionRouter } from '../world-map/3d-interaction-router.js';
import { createTooltipService } from '../world-map/3d-tooltip.js';
import { createInspectorRouter } from '../world-map/3d-inspector-router.js';
import { createInspectorUrlBridge } from '../world-map/3d-inspector-url.js';

// 1. Wrapped geography must stay local rather than fitting almost the whole world.
const datelineBounds = antimeridianAwareBounds([[179,-3],[-179,4],[178.5,1]]);
assert.equal(datelineBounds.crossesAntimeridian, true);
assert.ok(datelineBounds.spanLongitude < 3, 'dateline-crossing scenario must use the short wrapped interval');

// Shared fake map for hit arbitration and transient-tooltip motion lifecycle.
let rendered = [];
const mapHandlers = new Map();
const canvas = { style:{} };
const map = {
  getLayer(id) { return {id}; },
  getZoom() { return 5.2; },
  queryRenderedFeatures(_point, {layers} = {}) {
    const allowed = new Set(layers || []);
    return rendered.filter(feature => allowed.has(feature.layer.id));
  },
  on(type, handler) { mapHandlers.set(type, handler); },
  getCanvas() { return canvas; },
};
const feature = (layer, id) => ({layer:{id},properties:{id}});

// 2. Overlap arbitration must follow semantic priority, not render/query order.
const clicks = [];
const interaction = createInteractionRouter(map, {bind:false});
interaction.register('country', {layers:['country'],objectType:'country',clickPriority:10,onClick:(_e,f)=>clicks.push(`country:${f.properties.id}`)});
interaction.register('overlay', {layers:['overlay'],objectType:'overlay',clickPriority:40,onClick:(_e,f)=>clicks.push(`overlay:${f.properties.id}`)});
interaction.register('subdivision', {layers:['subdivision'],objectType:'subdivision',clickPriority:60,onClick:(_e,f)=>clicks.push(`subdivision:${f.properties.id}`)});
interaction.register('place', {layers:['place'],objectType:'place',clickPriority:80,onClick:(_e,f)=>clicks.push(`place:${f.properties.id}`)});
rendered = [feature('country','DNK'),feature('overlay','claim'),feature('subdivision','DK-83'),feature('place','place:haderslev')];
const originalEvent = {};
const winner = interaction.dispatch('click',{point:{x:20,y:20},originalEvent});
assert.equal(winner.owner,'place');
assert.deepEqual(clicks,['place:place:haderslev']);
assert.equal(originalEvent.__potatoAtlasOverlayHandled,true,'router must still protect unmigrated compatibility handlers');

// 3. Transient tooltip must invalidate on motion/projection and reject stale async work.
class FakePopup {
  setLngLat(value){this.lngLat=value;return this;}
  setHTML(value){this.html=value;return this;}
  addTo(){this.visible=true;return this;}
  remove(){this.visible=false;return this;}
}
const eventListeners = new Map();
const eventTarget = {
  addEventListener(type,handler){eventListeners.set(type,handler);},
  removeEventListener(type){eventListeners.delete(type);},
  dispatchEvent(event){eventListeners.get(event.type)?.(event);return true;},
};
const tooltip = createTooltipService(map,{PopupClass:FakePopup,eventTarget});
const firstGeneration = tooltip.nextGeneration('place');
assert.equal(tooltip.show('place',{lng:9.49,lat:55.25},'Haderslev',firstGeneration),true);
mapHandlers.get('dragstart')?.();
assert.equal(tooltip.state().visible,false);
const currentGeneration = tooltip.nextGeneration('place');
assert.equal(tooltip.show('place',{lng:9.49,lat:55.25},'stale',firstGeneration),false);
assert.equal(tooltip.state().staleSuppressions,1);
assert.equal(tooltip.show('place',{lng:9.49,lat:55.25},'current',currentGeneration),true);
eventTarget.dispatchEvent({type:'potato-atlas-projection-change'});
assert.equal(tooltip.state().visible,false);

// 4. Inspector history and URL projection must move together through child/back transitions.
let href = 'https://example.test/world-map/?country=DNK';
const inspectorEvents = new Map();
const inspectorEventTarget = {
  addEventListener(type,handler){inspectorEvents.set(type,handler);},
  removeEventListener(type){inspectorEvents.delete(type);},
  dispatchEvent(event){inspectorEvents.get(event.type)?.(event);return true;},
};
const bridge = createInspectorUrlBridge({
  getHref:()=>href,
  replace:url=>{href=String(url);},
  eventTarget:inspectorEventTarget,
});
const inspector = createInspectorRouter({
  emit:detail=>inspectorEventTarget.dispatchEvent({type:'potato-atlas-inspector-change',detail}),
});
const country = {type:'country',id:'DNK',owner:'country'};
const subdivision = {type:'subdivision',id:'DK-83',owner:'subdivisions',parent:{type:'country',id:'DNK'}};
const place = {type:'place',id:'place:haderslev',owner:'places',parent:{type:'subdivision',id:'DK-83'}};
inspector.setBaseline(country);
inspector.open(subdivision);
inspector.open(place);
let url = new URL(href);
assert.equal(url.searchParams.get('inspect'),'country:DNK/subdivision:DK-83/place:place%3Ahaderslev');
assert.equal(url.searchParams.get('country'),'DNK');
assert.equal(url.searchParams.get('subdivision'),'DK-83');
assert.equal(url.searchParams.get('place'),'place:haderslev');
assert.equal(inspector.back(),true);
url = new URL(href);
assert.equal(url.searchParams.get('inspect'),'country:DNK/subdivision:DK-83');
assert.equal(url.searchParams.has('place'),false);
assert.equal(inspector.back(),true);
url = new URL(href);
assert.equal(url.searchParams.get('inspect'),'country:DNK');
assert.equal(url.searchParams.has('subdivision'),false);
bridge.destroy();

console.log('WORLD MAP INTEGRATED BEHAVIORAL SCENARIO PASSED');
