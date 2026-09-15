// Scale-aware Places runtime for the World Relational Atlas.
// Owns place data, rendering, selection, lazy country detail and place inspection.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas Places require the core map.');

const DATA_ROOT = '../data/world-places/';
const INDEX_URL = `${DATA_ROOT}index.json`;
const MAJOR_SOURCE = 'atlas-places-major';
const DETAIL_SOURCE = 'atlas-places-detail';
const MAJOR_POINTS = 'atlas-places-major-points';
const MAJOR_LABELS = 'atlas-places-major-labels';
const DETAIL_POINTS = 'atlas-places-detail-points';
const DETAIL_LABELS = 'atlas-places-detail-labels';
const EMPTY_COLLECTION = Object.freeze({ type:'FeatureCollection', features:[] });

let indexPayload = null;
let majorData = EMPTY_COLLECTION;
let selectedId = new URL(location.href).searchParams.get('place') || null;
let visible = true;
let lastError = null;
const featureById = new Map();
const loadedCountries = new Map();

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function number(value) {
  if (value == null || !Number.isFinite(Number(value))) return '—';
  return new Intl.NumberFormat('en', { maximumFractionDigits:0 }).format(Number(value));
}
function placeKind(properties = {}) {
  if (properties.is_national_capital || properties.capital_status === 'national') return 'Capital';
  const population = Number(properties.population);
  return Number.isFinite(population) && population > 0 && population < 50_000 ? 'Town' : 'City';
}
function collection(features = []) {
  return { type:'FeatureCollection', features };
}
function sourceData(sourceId, data) {
  const source = map.getSource(sourceId);
  if (source?.setData) source.setData(data);
}
function indexFeatures(features = []) {
  for (const feature of features) {
    const id = feature?.properties?.id;
    if (id) featureById.set(String(id), feature);
  }
}
function allLoadedFeatures() {
  const features = [...(majorData.features || [])];
  for (const state of loadedCountries.values()) {
    const data = state?.data;
    if (data?.features) features.push(...data.features);
  }
  return features;
}
function syncDetailSource() {
  const seen = new Set();
  const features = [];
  for (const state of loadedCountries.values()) {
    for (const feature of state?.data?.features || []) {
      const id = String(feature?.properties?.id || '');
      if (!id || seen.has(id)) continue;
      seen.add(id);
      features.push(feature);
    }
  }
  sourceData(DETAIL_SOURCE, collection(features));
}
function syncUrl(id) {
  const url = new URL(location.href);
  if (id) url.searchParams.set('place', id);
  else url.searchParams.delete('place');
  history.replaceState({}, '', url);
}
function renderInspector(feature) {
  const panel = document.getElementById('panel');
  if (!panel || !feature) return;
  const p = feature.properties || {};
  const [lon, lat] = feature.geometry?.coordinates || [];
  const populationPeriod = p.population_period || '—';
  const country = p.country_name || p.country_iso3 || '—';
  const admin = [p.admin1_name, p.admin1_code].filter(Boolean).join(' · ');
  panel.innerHTML = `
    <div class="eyebrow">Place</div>
    <h1>${esc(p.name || p.id || 'Place')}</h1>
    <p class="muted">${esc(placeKind(p))} · ${esc(country)}</p>
    <div class="stat-grid">
      <div><span>Population</span><b>${number(p.population)}</b><small>${esc(populationPeriod)}</small></div>
      <div><span>Coordinates</span><b>${Number.isFinite(Number(lat)) ? Number(lat).toFixed(3) : '—'}, ${Number.isFinite(Number(lon)) ? Number(lon).toFixed(3) : '—'}</b></div>
    </div>
    ${admin ? `<p><b>Administrative region</b><br>${esc(admin)}</p>` : ''}
    <p class="muted">Source: ${esc(p.source || 'GeoNames')}<br>Dataset refreshed: ${esc(p.dataset_refresh_date || '—')}</p>
    <div class="panel-actions">
      <button type="button" data-place-open-country>Open country</button>
      <button type="button" data-place-close>Close place</button>
    </div>`;
  panel.querySelector('[data-place-open-country]')?.addEventListener('click', () => {
    const code = String(p.country_iso3 || '').toUpperCase();
    if (code && window.goCountry) window.goCountry(code);
  });
  panel.querySelector('[data-place-close]')?.addEventListener('click', () => clear());
  window.__potatoAtlasPanelLifecycle?.publish?.();
}
function registerLayer(layerId, priority) {
  window.__potatoAtlasRenderStack?.register?.(layerId, {
    slot:'context-network', priority, owner:'places'
  });
}
function installLayers() {
  if (!map.getSource(MAJOR_SOURCE)) map.addSource(MAJOR_SOURCE, { type:'geojson', data:majorData });
  if (!map.getSource(DETAIL_SOURCE)) map.addSource(DETAIL_SOURCE, { type:'geojson', data:EMPTY_COLLECTION });

  if (!map.getLayer(MAJOR_POINTS)) {
    map.addLayer({
      id:MAJOR_POINTS, type:'circle', source:MAJOR_SOURCE,
      paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],1,2.1,4,3.7,8,6.0],
        'circle-color':['case',['boolean',['get','is_national_capital'],false],'#e7c56f','#d7ded9'],
        'circle-stroke-color':'#111716', 'circle-stroke-width':1,
        'circle-opacity':0.92
      }
    });
  }
  if (!map.getLayer(MAJOR_LABELS)) {
    map.addLayer({
      id:MAJOR_LABELS, type:'symbol', source:MAJOR_SOURCE, minzoom:1.2,
      layout:{
        'text-field':['get','name'],
        'text-size':['interpolate',['linear'],['zoom'],1.2,8,5,10.5,8,12],
        'text-offset':[0,1.05], 'text-anchor':'top', 'text-optional':true,
        'text-allow-overlap':false
      },
      paint:{
        'text-color':['case',['boolean',['get','is_national_capital'],false],'#f0d98f','#d7ded9'],
        'text-halo-color':'#080b0b', 'text-halo-width':1.1,
        'text-opacity':0.9
      }
    });
  }
  if (!map.getLayer(DETAIL_POINTS)) {
    map.addLayer({
      id:DETAIL_POINTS, type:'circle', source:DETAIL_SOURCE, minzoom:4.2,
      paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],4.2,2,8,4.4,11,6],
        'circle-color':'#cdd8d2','circle-stroke-color':'#111716','circle-stroke-width':0.9,'circle-opacity':0.88
      }
    });
  }
  if (!map.getLayer(DETAIL_LABELS)) {
    map.addLayer({
      id:DETAIL_LABELS, type:'symbol', source:DETAIL_SOURCE, minzoom:5.0,
      layout:{
        'text-field':['get','name'], 'text-size':['interpolate',['linear'],['zoom'],5,8.5,9,11],
        'text-offset':[0,1.0], 'text-anchor':'top', 'text-optional':true, 'text-allow-overlap':false
      },
      paint:{'text-color':'#d3ddd7','text-halo-color':'#080b0b','text-halo-width':1.0}
    });
  }
  registerLayer(MAJOR_POINTS, 30);
  registerLayer(MAJOR_LABELS, 31);
  registerLayer(DETAIL_POINTS, 32);
  registerLayer(DETAIL_LABELS, 33);
  setVisible(visible, {silent:true});
  bindLayerEvents();
}

let eventsBound = false;
function bindLayerEvents() {
  if (eventsBound) return;
  eventsBound = true;
  for (const layerId of [MAJOR_POINTS, DETAIL_POINTS]) {
    map.on('mouseenter', layerId, () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', layerId, () => { map.getCanvas().style.cursor = ''; });
    map.on('click', layerId, event => {
      const feature = event.features?.[0];
      if (!feature) return;
      if (event.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
      const id = feature.properties?.id;
      if (id) focus(id, {feature, fit:false});
    });
  }
}

async function loadIndex() {
  if (indexPayload) return indexPayload;
  const response = await fetch(INDEX_URL, {cache:'force-cache'});
  if (!response.ok) throw new Error(`Places index unavailable (${response.status})`);
  indexPayload = await response.json();
  return indexPayload;
}
async function loadMajor() {
  const index = await loadIndex();
  const path = index?.global_major?.path || 'global-major.geo.json';
  const response = await fetch(`${DATA_ROOT}${path}`, {cache:'force-cache'});
  if (!response.ok) throw new Error(`Global Places snapshot unavailable (${response.status})`);
  const data = await response.json();
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error('Global Places snapshot is not GeoJSON.');
  majorData = data;
  indexFeatures(data.features);
  sourceData(MAJOR_SOURCE, data);
  return data;
}
async function loadCountry(iso3) {
  const code = String(iso3 || '').toUpperCase();
  if (!code) return null;
  if (loadedCountries.has(code)) return loadedCountries.get(code);
  const promise = (async () => {
    const index = await loadIndex();
    const descriptor = index?.countries?.[code];
    if (!descriptor?.path) return { descriptor:null, data:EMPTY_COLLECTION };
    const response = await fetch(`${DATA_ROOT}${descriptor.path}`, {cache:'force-cache'});
    if (!response.ok) throw new Error(`Places partition ${code} unavailable (${response.status})`);
    const data = await response.json();
    if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error(`Places partition ${code} is not GeoJSON.`);
    indexFeatures(data.features);
    return { descriptor, data };
  })();
  loadedCountries.set(code, promise);
  try {
    const state = await promise;
    loadedCountries.set(code, state);
    syncDetailSource();
    return state;
  } catch (error) {
    loadedCountries.delete(code);
    throw error;
  }
}
function findFeature(id) {
  return featureById.get(String(id || '')) || null;
}
async function focus(id, options = {}) {
  let feature = options.feature || findFeature(id);
  if (!feature && options.country) {
    await loadCountry(options.country);
    feature = findFeature(id);
  }
  if (!feature) return false;
  const p = feature.properties || {};
  const coords = feature.geometry?.coordinates;
  selectedId = String(p.id || id);
  syncUrl(selectedId);
  renderInspector(feature);
  if (options.fit !== false && Array.isArray(coords) && coords.length >= 2) {
    map.easeTo({
      center:[Number(coords[0]), Number(coords[1])],
      zoom:Math.max(Number(options.zoom) || 6.2, map.getZoom()),
      pitch:Math.min(map.getPitch(), 45), duration:650
    });
  }
  window.dispatchEvent(new CustomEvent('potato-atlas-place-select', {detail:{id:selectedId, properties:p, feature}}));
  return true;
}
function clear() {
  selectedId = null;
  syncUrl(null);
  window.dispatchEvent(new CustomEvent('potato-atlas-place-clear'));
  return true;
}
function setVisible(next, options = {}) {
  visible = Boolean(next);
  const visibility = visible ? 'visible' : 'none';
  for (const id of [MAJOR_POINTS, MAJOR_LABELS, DETAIL_POINTS, DETAIL_LABELS]) {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
  }
  if (!options.silent) window.dispatchEvent(new CustomEvent('potato-atlas-places-change', {detail:{visible}}));
  return visible;
}
function current() {
  return selectedId ? findFeature(selectedId) : null;
}
function search(query, options = {}) {
  const needle = String(query || '').trim().toLowerCase();
  if (!needle) return [];
  const limit = Math.max(1, Math.min(50, Number(options.limit) || 12));
  const normalized = value => String(value || '').toLowerCase();
  return allLoadedFeatures()
    .map(feature => {
      const p = feature.properties || {};
      const names = [p.name, p.ascii_name, ...(Array.isArray(p.aliases) ? p.aliases : [])].map(normalized);
      const best = Math.min(...names.map(name => name === needle ? 0 : name.startsWith(needle) ? 1 : name.includes(needle) ? 2 : 9));
      return {feature, best};
    })
    .filter(row => row.best < 9)
    .sort((a, b) => a.best - b.best || (b.feature.properties?.population || 0) - (a.feature.properties?.population || 0))
    .slice(0, limit)
    .map(({feature}) => ({
      id:feature.properties?.id,
      name:feature.properties?.name,
      country:feature.properties?.country_iso3,
      type:placeKind(feature.properties || {}),
      feature,
    }));
}
function status() {
  return {
    visible,
    selected:selectedId,
    majorCount:majorData.features?.length || 0,
    loadedCountries:[...loadedCountries.keys()],
    indexReady:Boolean(indexPayload),
    error:lastError ? String(lastError.message || lastError) : null,
  };
}

async function initialize() {
  if (map.loaded()) installLayers();
  else await new Promise(resolve => map.once('load', () => { installLayers(); resolve(); }));
  try {
    await loadMajor();
    const url = new URL(location.href);
    const requested = url.searchParams.get('place');
    const country = url.searchParams.get('country');
    if (requested && !findFeature(requested) && country) await loadCountry(country);
    if (requested) await focus(requested, {country, fit:true});
  } catch (error) {
    lastError = error;
    console.warn('Places data unavailable; country map remains usable.', error);
  }
  const state = status();
  window.dispatchEvent(new CustomEvent('potato-atlas-places-ready', {detail:state}));
  return state;
}

const ready = initialize();
window.__potatoAtlasPlaces = {
  ready,
  setVisible,
  focus,
  current,
  search,
  clear,
  status,
  loadCountry,
  get visible() { return visible; },
};
