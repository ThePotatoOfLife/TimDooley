// Contextual World Map system intelligence: explicit capabilities, dependencies,
// sourced builds and directly associated empirical gateways. No aggregate scores.
const map = window.__potatoAtlasMap;
const runtime = window.__potatoAtlasDataRuntime;
const selection = window.__potatoAtlasSelection;
if (!map || !runtime || !selection) throw new Error('System intelligence requires map, runtime and selection APIs.');
await runtime.ready;

const SOURCE_ID = 'atlas-context-gateways';
const POINT_LAYER = 'atlas-context-gateways-points';
const LABEL_LAYER = 'atlas-context-gateways-labels';
const MAX_INFRASTRUCTURE_TAGS = 4;
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
let activeGatewayId = null;

runtime.systemContext = async code => {
  const data = await runtime.ready;
  return data?.countries?.[String(code || '').toUpperCase()]?.systems || { capabilities:[], dependencies:[], builds:[], chains:[], gateways:[], resilience:{ evidence_domains:[], policy:'no aggregate score inferred' } };
};
runtime.gatewaysForCountry = async code => {
  const data = await runtime.ready;
  const systems = data?.countries?.[String(code || '').toUpperCase()]?.systems || {};
  return (systems.gateways || []).map(id => ({ id, ...(data?.gateways?.[id] || {}) })).filter(row => row.label);
};
runtime.gateway = async id => {
  const data = await runtime.ready;
  return data?.gateways?.[id] || null;
};
runtime.systemCoverage = async () => {
  const data = await runtime.ready;
  return data?.system_coverage || {};
};

function countEnhancement() {
  const diagnostics = window.__potatoAtlasDiagnostics;
  if (diagnostics) diagnostics.cardEnhancementPasses = (diagnostics.cardEnhancementPasses || 0) + 1;
}
function emptyGeoJSON() { return { type:'FeatureCollection', features:[] }; }
function gatewayFeature(gateway) {
  const obs = gateway.observation || {};
  return {
    type:'Feature',
    geometry:{ type:'Point', coordinates:gateway.coordinates },
    properties:{
      id:gateway.id,
      label:gateway.label,
      type:gateway.type,
      value:obs.value,
      unit:obs.unit || '',
      period:obs.period || '',
      source:obs.source || '',
      source_url:obs.source_url || '',
    },
  };
}

function ensureGatewayLayers() {
  if (!map.getSource(SOURCE_ID)) map.addSource(SOURCE_ID, { type:'geojson', data:emptyGeoJSON() });
  if (!map.getLayer(POINT_LAYER)) {
    map.addLayer({
      id:POINT_LAYER,
      type:'circle',
      source:SOURCE_ID,
      paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],1,4,5,7],
        'circle-color':'#d9bf73',
        'circle-stroke-color':'#17211f',
        'circle-stroke-width':1.4,
        'circle-opacity':0.9,
      },
    });
  }
  if (!map.getLayer(LABEL_LAYER)) {
    map.addLayer({
      id:LABEL_LAYER,
      type:'symbol',
      source:SOURCE_ID,
      minzoom:2.7,
      layout:{
        'text-field':['get','label'],
        'text-size':10,
        'text-offset':[0,1.25],
        'text-anchor':'top',
        'text-allow-overlap':false,
      },
      paint:{ 'text-color':'#e3ddc8','text-halo-color':'#111817','text-halo-width':1.2 },
    });
  }
}

async function updateGatewayPoints(code) {
  ensureGatewayLayers();
  const source = map.getSource(SOURCE_ID);
  if (!source?.setData) return;
  if (!/^[A-Z]{3}$/.test(String(code || ''))) { source.setData(emptyGeoJSON()); return; }
  const gateways = await runtime.gatewaysForCountry(code);
  source.setData({ type:'FeatureCollection', features:gateways.map(gatewayFeature) });
}

function tags(label, rows, formatter = value => value) {
  if (!rows.length) return '';
  const visible = rows.slice(0, label === 'Can' ? 3 : 2);
  const remaining = Math.max(0, rows.length - visible.length);
  return `<div class="atlas-country-row"><span>${esc(label)}</span><b><span class="atlas-country-tags">${visible.map(row => `<span class="atlas-country-tag">${esc(formatter(row))}</span>`).join('')}${remaining ? `<span class="atlas-country-tag">+${remaining}</span>` : ''}</span></b></div>`;
}

function buildLabel(build) {
  const name = String(build?.label || build?.id || '').replace(/\b\w/g, char => char.toUpperCase());
  const value = build?.value;
  const unit = build?.unit || '';
  return value == null || value === '' ? name : `${name} · ${value}${unit ? ` ${unit}` : ''}`;
}

async function injectSystemRole(code) {
  code = String(code || '').toUpperCase();
  const card = document.getElementById('atlasCountryCard');
  if (!card || card.hidden || !/^[A-Z]{3}$/.test(code)) return;
  if (card.querySelector('#atlasCountrySystemRole')) return;
  countEnhancement();
  const systems = await runtime.systemContext(code);
  const gateways = await runtime.gatewaysForCountry(code);
  const capabilities = systems.capabilities || [];
  const dependencies = systems.dependencies || [];
  const builds = systems.builds || [];
  if (!capabilities.length && !dependencies.length && !builds.length && !gateways.length) return;

  const section = document.createElement('div');
  section.id = 'atlasCountrySystemRole';
  section.className = 'atlas-country-section';
  section.innerHTML = `<small>System role · evidence-backed</small>${tags('Can', capabilities)}${tags('Depends', dependencies)}${tags('Building', builds, buildLabel)}${tags('Gateways', gateways, row => row.label)}`;
  const actions = card.querySelector('.atlas-country-actions');
  if (actions) actions.before(section); else card.appendChild(section);
}

function currentCode(detail = null) {
  return String(detail?.activeCode || detail?.code || selection.current?.activeCode || selection.current?.code || '').toUpperCase();
}
function infrastructureHtml(rows) {
  if (!rows?.length) return '';
  const visible = rows.slice(0, MAX_INFRASTRUCTURE_TAGS);
  const remaining = Math.max(0, rows.length - visible.length);
  return `<p><small>Infrastructure</small><br><span class="atlas-country-tags">${visible.map(asset => `<button type="button" class="atlas-country-tag" data-infrastructure-id="${esc(asset.id)}" data-gateway-infrastructure-id="${esc(asset.id)}">${esc(asset.label || asset.id)}</button>`).join('')}${remaining ? `<span class="atlas-country-tag">+${remaining}</span>` : ''}</span></p>`;
}
function emitGateway(id, gateway) {
  activeGatewayId = id || null;
  window.dispatchEvent(new CustomEvent('potato-atlas-gateway-change', { detail:{ id:activeGatewayId, gateway:gateway || null } }));
}

ensureGatewayLayers();
map.on('mouseenter', POINT_LAYER, () => { map.getCanvas().style.cursor = 'pointer'; });
map.on('mouseleave', POINT_LAYER, () => { map.getCanvas().style.cursor = ''; });
map.on('click', POINT_LAYER, async event => {
  const feature = event.features?.[0];
  if (!feature) return;
  const p = feature.properties || {};
  const gateway = await runtime.gateway(p.id) || { id:p.id, label:p.label, type:p.type };
  const infrastructure = await runtime.infrastructureForGateway?.(p.id) || [];
  const value = Number(p.value);
  const observation = Number.isFinite(value) ? `${value} ${p.unit || ''}`.trim() : 'Observation unavailable';
  const popup = new maplibregl.Popup({ closeButton:true, maxWidth:'330px' })
    .setLngLat(feature.geometry.coordinates)
    .setHTML(`<b>${esc(p.label)}</b><br><small>${esc(String(p.type || '').replaceAll('-',' '))}</small><p>${esc(observation)} · ${esc(p.period || '')}</p>${infrastructureHtml(infrastructure)}<small>${esc(p.source || '')}</small><div class="boundary">Gateway-linked Infrastructure is contextual unless an explicit dependency is represented.</div>`)
    .addTo(map);
  emitGateway(p.id, gateway);
  popup.on('close', () => {
    if (activeGatewayId === p.id) emitGateway(null, null);
  });
});

let injectionQueued = false;
function queueInjection(code) {
  if (injectionQueued) return;
  injectionQueued = true;
  setTimeout(async () => { injectionQueued = false; await injectSystemRole(code); }, 0);
}

window.addEventListener('potato-atlas-country-card-rendered', event => queueInjection(currentCode(event?.detail)));
window.addEventListener('potato-atlas-working-selection-change', event => {
  const code = event?.detail?.selected === false ? '' : currentCode(event?.detail);
  updateGatewayPoints(code);
  queueInjection(code);
});
window.addEventListener('potato-atlas-layer-change', () => queueInjection(currentCode()));

const initial = currentCode();
await updateGatewayPoints(initial);
queueInjection(initial);

window.__potatoAtlasSystemIntelligence = { systemContext:runtime.systemContext, gatewaysForCountry:runtime.gatewaysForCountry, systemCoverage:runtime.systemCoverage, updateGatewayPoints, injectSystemRole };