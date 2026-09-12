// Contextual empirical infrastructure for the World Relational Atlas.
// Canonical data lives in the shared runtime. This module only renders the
// bounded set of physical assets relevant to the user's current investigation.
const map = window.__potatoAtlasMap;
const runtime = window.__potatoAtlasDataRuntime;
const selection = window.__potatoAtlasSelection;
if (!map || !runtime || !selection) throw new Error('Infrastructure context requires map, runtime and selection APIs.');
await runtime.ready;

const SOURCE_ID = 'atlas-infrastructure-context';
const POINT_LAYER = 'atlas-infrastructure-points';
const MAX_CONTEXT_ASSETS = 12;
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

let activeContext = { kind:null, id:null };
let visibleAssets = [];
let activePopup = null;

function emptyGeoJSON() { return { type:'FeatureCollection', features:[] }; }
function humanize(value) { return String(value || '').replaceAll('-', ' ').replace(/\b\w/g, char => char.toUpperCase()); }
function assetId(asset) { return String(asset?.id || ''); }
function sortAssets(rows) {
  return [...(rows || [])].filter(Boolean).sort((a, b) => String(a.type || '').localeCompare(String(b.type || '')) || String(a.label || a.id || '').localeCompare(String(b.label || b.id || '')));
}
function bounded(rows) { return sortAssets(rows).slice(0, MAX_CONTEXT_ASSETS); }
function pointFeature(asset) {
  const location = asset?.location;
  const coords = location?.coordinates;
  if (asset?.geometry_status === 'no-geometry' || location?.type !== 'Point' || !Array.isArray(coords) || coords.length !== 2) return null;
  if (!coords.every(value => Number.isFinite(Number(value)))) return null;
  return {
    type:'Feature',
    geometry:{ type:'Point', coordinates:coords.map(Number) },
    properties:{
      id:assetId(asset),
      label:String(asset.label || asset.id || 'Infrastructure'),
      type:String(asset.type || 'infrastructure'),
      countries:(asset.countries || []).join(','),
      gatewayIds:(asset.gateway_ids || []).join(','),
    },
  };
}

function ensureLayer() {
  if (!map.getSource(SOURCE_ID)) map.addSource(SOURCE_ID, { type:'geojson', data:emptyGeoJSON() });
  if (!map.getLayer(POINT_LAYER)) {
    map.addLayer({
      id:POINT_LAYER,
      type:'circle',
      source:SOURCE_ID,
      paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],1,3.5,5,6.5],
        'circle-color':'#b9d7c8',
        'circle-stroke-color':'#15211e',
        'circle-stroke-width':1.4,
        'circle-opacity':.92,
      },
    });
  }
}

function setVisible(rows, context) {
  ensureLayer();
  visibleAssets = bounded(rows);
  activeContext = context || { kind:null, id:null };
  const features = visibleAssets.map(pointFeature).filter(Boolean);
  map.getSource(SOURCE_ID)?.setData?.({ type:'FeatureCollection', features });
  injectCountryContext(currentEntityCode());
  window.dispatchEvent(new CustomEvent('potato-atlas-infrastructure-change', { detail:{ context:{...activeContext}, assets:[...visibleAssets] } }));
  return visibleAssets;
}

function currentEntityCode() {
  return String(selection.current?.activeCode || selection.current?.code || '').toUpperCase();
}
async function showForEntity(code) {
  const key = String(code || '').toUpperCase();
  const rows = /^[A-Z]{3}$/.test(key) ? await runtime.infrastructureForEntity?.(key) || [] : [];
  return setVisible(rows, key ? {kind:'entity', id:key} : {kind:null, id:null});
}
async function showForGateway(id) {
  const key = String(id || '');
  const rows = key ? await runtime.infrastructureForGateway?.(key) || [] : [];
  return setVisible(rows, key ? {kind:'gateway', id:key} : {kind:null, id:null});
}
async function showForChain(id) {
  const key = String(id || '');
  const rows = key ? await runtime.infrastructureForChain?.(key) || [] : [];
  return setVisible(rows, key ? {kind:'chain', id:key} : {kind:null, id:null});
}
async function showAsset(id) {
  const key = String(id || '');
  const asset = key ? await runtime.infrastructure?.(key) : null;
  if (!asset) return false;
  setVisible([asset], {kind:'asset', id:key});
  const feature = pointFeature(asset);
  if (feature) showPopup(asset, feature.geometry.coordinates);
  return true;
}
function clear() {
  activePopup?.remove?.();
  activePopup = null;
  return setVisible([], {kind:null, id:null});
}
function current() { return { context:{...activeContext}, assets:[...visibleAssets] }; }

async function impactNodeForAsset(id) {
  const data = await runtime.ready;
  const nodeId = `infrastructure:${String(id || '')}`;
  return data?.impact?.nodes?.[nodeId] ? nodeId : null;
}
function latestObservation(asset) {
  const observations = Array.isArray(asset?.observations) ? asset.observations : [];
  return observations[0] || null;
}
async function showPopup(asset, coordinates) {
  activePopup?.remove?.();
  const observation = latestObservation(asset);
  const impactNode = await impactNodeForAsset(asset.id);
  const sourceLink = asset.source_url ? `<a href="${esc(asset.source_url)}" target="_blank" rel="noopener noreferrer">${esc(asset.source || 'Source')}</a>` : esc(asset.source || 'Source unavailable');
  const linked = [
    ...(asset.gateway_ids || []).map(id => `Gateway: ${humanize(id)}`),
    ...(asset.chain_ids || []).map(id => `Chain: ${humanize(id)}`),
  ];
  const observationHtml = observation ? `<p><small>${esc(observation.label || observation.type || 'Observation')}</small><br>${esc(observation.value ?? '—')} ${esc(observation.unit || '')}${observation.period ? ` · ${esc(observation.period)}` : ''}</p>` : '';
  const impactButton = impactNode ? `<button type="button" data-infrastructure-impact="${esc(asset.id)}">Impact</button>` : '';
  activePopup = new maplibregl.Popup({ closeButton:true, maxWidth:'330px' })
    .setLngLat(coordinates)
    .setHTML(`<div class="atlas-infrastructure-popup"><b>${esc(asset.label || asset.id)}</b><br><small>${esc(humanize(asset.type))}</small>${asset.operator ? `<p><small>Operator / authority</small><br>${esc(asset.operator)}</p>` : ''}${linked.length ? `<p><small>Context</small><br>${linked.map(esc).join(' · ')}</p>` : ''}${observationHtml}<p><small>${sourceLink}</small></p>${impactButton}<div class="boundary">Infrastructure association is contextual unless an explicit sourced dependency is represented.</div></div>`)
    .addTo(map);
}

async function injectCountryContext(code = currentEntityCode()) {
  const card = document.getElementById('atlasCountryCard');
  if (!card || card.hidden || !/^[A-Z]{3}$/.test(String(code || ''))) return;
  const rows = bounded(await runtime.infrastructureForEntity?.(code) || []);
  let section = card.querySelector('#atlasCountryInfrastructureContext');
  if (!rows.length) {
    section?.remove();
    return;
  }
  if (!section) {
    section = document.createElement('div');
    section.id = 'atlasCountryInfrastructureContext';
    section.className = 'atlas-country-section';
    const actions = card.querySelector('.atlas-country-actions');
    if (actions) actions.before(section); else card.appendChild(section);
  }
  const nextHtml = `<small>Infrastructure context</small><div class="atlas-country-tags">${rows.slice(0,4).map(asset => `<button type="button" class="atlas-country-tag" data-infrastructure-id="${esc(asset.id)}">${esc(asset.label || asset.id)}</button>`).join('')}${rows.length > 4 ? `<span class="atlas-country-tag">+${rows.length - 4}</span>` : ''}</div><div class="atlas-country-source">Sourced physical context · association does not imply dependency</div>`;
  if (section.innerHTML !== nextHtml) section.innerHTML = nextHtml;
}

function fallBackContext() {
  const code = currentEntityCode();
  return code ? showForEntity(code) : clear();
}

document.addEventListener('click', async event => {
  const assetButton = event.target.closest('[data-infrastructure-id]');
  if (assetButton) { await showAsset(assetButton.dataset.infrastructureId); return; }
  const impactButton = event.target.closest('[data-infrastructure-impact]');
  if (impactButton) {
    const nodeId = await impactNodeForAsset(impactButton.dataset.infrastructureImpact);
    if (nodeId) window.__potatoAtlasImpactTrace?.show?.(nodeId);
  }
});

ensureLayer();
map.on('mouseenter', POINT_LAYER, () => { map.getCanvas().style.cursor = 'pointer'; });
map.on('mouseleave', POINT_LAYER, () => { map.getCanvas().style.cursor = ''; });
map.on('click', POINT_LAYER, async event => {
  const id = event.features?.[0]?.properties?.id;
  const asset = id ? await runtime.infrastructure?.(id) : null;
  if (asset) await showPopup(asset, event.features[0].geometry.coordinates);
});

const cardHost = document.getElementById('atlasCountryCard');
if (cardHost) new MutationObserver(() => {
  if (!cardHost.querySelector('#atlasCountryInfrastructureContext')) queueMicrotask(() => injectCountryContext());
}).observe(cardHost, {childList:true, subtree:false});

window.addEventListener('potato-atlas-working-selection-change', event => {
  if (activeContext.kind && activeContext.kind !== 'entity') return;
  const code = event?.detail?.selected === false ? '' : String(event?.detail?.activeCode || event?.detail?.code || '').toUpperCase();
  showForEntity(code);
});
window.addEventListener('potato-atlas-chain-change', event => {
  const id = event?.detail?.id || event?.detail?.chainId || null;
  if (id) showForChain(id); else if (activeContext.kind === 'chain') fallBackContext();
});
window.addEventListener('potato-atlas-gateway-change', event => {
  const id = event?.detail?.id || event?.detail?.gatewayId || null;
  if (id) showForGateway(id); else if (activeContext.kind === 'gateway') fallBackContext();
});

window.__potatoAtlasInfrastructure = { showForEntity, showForGateway, showForChain, showAsset, clear, current };
await fallBackContext();
