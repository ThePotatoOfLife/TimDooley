const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas Places requires the core map.');

const CITY_URL = '../data/world-cities.geo.json';
const CAPITAL_URL = '../data/world-capitals.geo.json';
const SOURCE_ID = 'atlas-places';
const CIRCLE_ID = 'atlas-places-circles';
const LABEL_ID = 'atlas-places-labels';
let selectedId = new URL(location.href).searchParams.get('place') || null;
let features = [];
let byId = new Map();

const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = value => value == null ? '—' : new Intl.NumberFormat('en',{maximumFractionDigits:0}).format(Number(value));

async function fetchJson(url) {
  const response = await fetch(url, {cache:'force-cache'});
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

function capitalFallbackFeature(feature) {
  const p = feature?.properties || {};
  const iso3 = String(p.iso3 || '').toUpperCase();
  const name = String(p.name || '').trim();
  if (!iso3 || !name) return null;
  return {
    type:'Feature',
    properties:{
      id:`cap:${iso3}:${name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}`,
      name, iso3, country:p.country || iso3, capital:Boolean(p.primary), source:p.source || 'Committed capital snapshot',
      coordinate_source:p.source || 'Committed capital snapshot', tier:2, minimum_zoom:Number(p.scalerank) <= 2 ? 2.4 : 3.4,
    },
    geometry:feature.geometry,
  };
}

async function loadPlaces() {
  try {
    const payload = await fetchJson(CITY_URL);
    if (payload?.type === 'FeatureCollection' && Array.isArray(payload.features)) return payload;
  } catch (error) {
    console.warn('Major-city runtime unavailable; using capital-only fallback.', error);
  }
  const capitals = await fetchJson(CAPITAL_URL);
  return {type:'FeatureCollection',features:(capitals.features || []).map(capitalFallbackFeature).filter(Boolean)};
}

function installInspector() {
  if (document.getElementById('atlasPlaceCard')) return;
  const card = document.createElement('div');
  card.id = 'atlasPlaceCard';
  card.hidden = true;
  card.style.cssText = 'position:absolute;left:12px;top:54px;z-index:9;width:min(300px,calc(100% - 24px));padding:10px 11px;background:#0b1010ef;border:1px solid #40504d;border-radius:10px;box-shadow:0 8px 28px #0009;backdrop-filter:blur(9px);font-size:11px';
  document.querySelector('.mapwrap')?.appendChild(card);
}

function syncUrl(id) {
  const url = new URL(location.href);
  if (id) url.searchParams.set('place', id); else url.searchParams.delete('place');
  history.replaceState({},'',url);
}

async function openCountry(iso3) {
  const code = String(iso3 || '').toUpperCase();
  if (!code || typeof window.goCountry !== 'function') return false;
  await window.goCountry(code);
  return true;
}

function renderInspector(feature) {
  installInspector();
  const card = document.getElementById('atlasPlaceCard');
  const p = feature?.properties || {};
  if (!card) return;
  const countryAction = p.iso3 ? `<button type="button" data-place-country style="margin-top:8px;width:100%">Open ${esc(p.country || p.iso3)}</button>` : '';
  card.innerHTML = `<div style="display:flex;justify-content:space-between;gap:8px"><div><b style="font-size:14px">${esc(p.name || p.id)}</b><div class="muted">${p.capital ? 'Capital city' : 'City'} · ${esc(p.admin_region || p.country || p.iso3 || '')}</div></div><button type="button" data-place-close>×</button></div><div class="grid" style="margin-top:8px"><div class="metric"><span>Population</span><b>${fmt(p.population)}</b><small>${esc(p.population_period || '')}</small></div><div class="metric"><span>Country</span><b>${esc(p.iso3 || '—')}</b></div></div><div class="muted" style="margin-top:7px">${esc(p.source || '')}</div>${countryAction}`;
  card.hidden = false;
  card.querySelector('[data-place-close]')?.addEventListener('click', clear);
  card.querySelector('[data-place-country]')?.addEventListener('click', () => openCountry(p.iso3));
}

function clear() {
  selectedId = null;
  syncUrl(null);
  const card = document.getElementById('atlasPlaceCard');
  if (card) card.hidden = true;
}

function select(id, options={}) {
  const feature = byId.get(String(id || ''));
  if (!feature) return false;
  selectedId = feature.properties.id;
  syncUrl(selectedId);
  const coords = feature.geometry?.coordinates;
  if (Array.isArray(coords) && options.fly !== false) map.easeTo({center:coords,zoom:Math.max(5.4,map.getZoom()),duration:650,pitch:Math.min(map.getPitch(),45)});
  renderInspector(feature);
  window.dispatchEvent(new CustomEvent('potato-atlas-place-select',{detail:{id:selectedId,feature,properties:feature.properties}}));
  return true;
}

function visibleFeatureCollection() {
  const zoom = map.getZoom();
  return {type:'FeatureCollection',features:features.filter(feature => Number(feature.properties?.minimum_zoom ?? 99) <= zoom)};
}

function refreshVisibility() {
  map.getSource(SOURCE_ID)?.setData(visibleFeatureCollection());
}

function installLayers() {
  if (!map.getSource(SOURCE_ID)) map.addSource(SOURCE_ID,{type:'geojson',data:visibleFeatureCollection()});
  if (!map.getLayer(CIRCLE_ID)) map.addLayer({
    id:CIRCLE_ID,type:'circle',source:SOURCE_ID,
    filter:['!=',['get','capital'],true],
    paint:{'circle-radius':['interpolate',['linear'],['zoom'],2,1.5,5,3.2,8,5.2],'circle-color':'#9cc8d8','circle-stroke-color':'#111717','circle-stroke-width':1,'circle-opacity':0.88},
  });
  if (!map.getLayer(LABEL_ID)) map.addLayer({
    id:LABEL_ID,type:'symbol',source:SOURCE_ID,
    filter:['!=',['get','capital'],true],
    layout:{'text-field':['get','name'],'text-size':['interpolate',['linear'],['zoom'],3,8,7,11],'text-offset':[0,1.05],'text-anchor':'top','text-optional':true,'text-allow-overlap':false},
    paint:{'text-color':'#c8e3eb','text-halo-color':'#080b0b','text-halo-width':1.1},
  });
  map.on('zoomend',refreshVisibility);
  map.on('click',CIRCLE_ID,event=>{if(event?.originalEvent)event.originalEvent.__potatoAtlasOverlayHandled=true;const id=event.features?.[0]?.properties?.id;if(id)select(id,{fly:false});});
  map.on('mouseenter',CIRCLE_ID,()=>{map.getCanvas().style.cursor='pointer';});
  map.on('mouseleave',CIRCLE_ID,()=>{map.getCanvas().style.cursor='';});
}

const data = await loadPlaces();
features = (data.features || []).filter(feature => {
  const p = feature?.properties || {};
  const coords = feature?.geometry?.coordinates;
  return p.id && p.name && p.iso3 && Number.isFinite(Number(p.minimum_zoom)) && Array.isArray(coords) && coords.length >= 2;
});
byId = new Map(features.map(feature => [String(feature.properties.id), feature]));
installLayers();
if (selectedId) queueMicrotask(()=>select(selectedId));

window.__potatoAtlasPlaces = {
  ready:Promise.resolve(true),
  select,
  clear,
  openCountry,
  records(){ return features.map(feature => feature.properties); },
  get selected(){ return selectedId; },
};
window.dispatchEvent(new CustomEvent('potato-atlas-places-ready',{detail:{count:features.length,selected:selectedId}}));
