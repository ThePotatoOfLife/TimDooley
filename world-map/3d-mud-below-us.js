// U.S. project-symbolic Mud / Below case overlay for the canonical World Map.
// This is a project-interpretive layer. It must never be read as an objective
// classification of people, and its coordinates are broad state-centroid anchors.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Mud / Below overlay requires the core map.');

const DATA_URL = '../data/world-symbolic/us-mud-below-project-cases.geo.json';
const SOURCE_ID = 'project-mud-below-us';
const POINT_LAYER = 'project-mud-below-points';
const LABEL_LAYER = 'project-mud-below-labels';
const HIT_LAYER = 'project-mud-below-hit';
const interaction = window.__potatoAtlasInteraction;

let enabled = false;
let loaded = false;
let data = { type:'FeatureCollection', features:[] };

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

function updateUrl() {
  const url = new URL(location.href);
  if (enabled) url.searchParams.set('projectLayer', 'mud-below-us');
  else if (url.searchParams.get('projectLayer') === 'mud-below-us') url.searchParams.delete('projectLayer');
  history.replaceState({}, '', url);
}

function setLayerVisibility(show) {
  const visibility = show ? 'visible' : 'none';
  for (const id of [POINT_LAYER, LABEL_LAYER, HIT_LAYER]) {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
  }
  const button = document.getElementById('mudBelowLayer');
  button?.classList.toggle('active', show);
  button?.setAttribute('aria-pressed', show ? 'true' : 'false');
}

function renderCase(feature) {
  const p = feature?.properties || {};
  const panel = document.getElementById('panel');
  if (!panel) return;
  panel.innerHTML = `
    <div class="eyebrow">Project-symbolic case · Mud / Below</div>
    <h1>${esc(p.label || 'Project case')}</h1>
    <p class="muted">${esc(p.state || '')} · ${esc(p.anchor_precision || 'broad anchor')}</p>
    <div class="card">
      <b>${esc(p.map_role || 'Project case')}</b>
      <p>${esc(p.project_relation || '')}</p>
    </div>
    <div class="boundary">${esc(p.boundary || 'This is Tim/project terminology, not an objective classification of a person.')}</div>
    <p class="muted"><b>Project source:</b> ${esc(p.source_path || '')}</p>
    ${p.supporting_path ? `<p class="muted"><b>Supporting project record:</b> ${esc(p.supporting_path)}</p>` : ''}
    <div class="actions">
      <button type="button" data-mud-state>Open ${esc(p.state || 'state')}</button>
      <a href="../below/">Open Below</a>
    </div>`;
  panel.querySelector('[data-mud-state]')?.addEventListener('click', async () => {
    if (p.subdivision_id) await window.__potatoAtlasSubdivisions?.select?.(p.subdivision_id, { fit:true });
  });
  window.__potatoAtlasPanelLifecycle?.publish?.();
}

function installLayers() {
  if (!map.getSource(SOURCE_ID)) {
    map.addSource(SOURCE_ID, { type:'geojson', data, promoteId:'id' });
  }
  const before = map.getLayer('atlas-subdivision-label') ? 'atlas-subdivision-label' : undefined;
  if (!map.getLayer(POINT_LAYER)) {
    map.addLayer({
      id:POINT_LAYER,
      type:'circle',
      source:SOURCE_ID,
      minzoom:3.2,
      paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],3.2,5,6,8,9,11],
        'circle-color':'#9a7350',
        'circle-opacity':0.9,
        'circle-stroke-color':'#f1d49a',
        'circle-stroke-width':1.25
      }
    }, before);
  }
  if (!map.getLayer(LABEL_LAYER)) {
    map.addLayer({
      id:LABEL_LAYER,
      type:'symbol',
      source:SOURCE_ID,
      minzoom:4.0,
      layout:{
        'text-field':['get','label'],
        'text-size':['interpolate',['linear'],['zoom'],4,9,7,11],
        'text-offset':[0,1.25],
        'text-anchor':'top',
        'text-max-width':16,
        'text-allow-overlap':false
      },
      paint:{
        'text-color':'#f0d7a8',
        'text-halo-color':'#0a0f0f',
        'text-halo-width':1.2,
        'text-opacity':0.92
      }
    });
  }
  if (!map.getLayer(HIT_LAYER)) {
    map.addLayer({
      id:HIT_LAYER,
      type:'circle',
      source:SOURCE_ID,
      minzoom:3.2,
      paint:{'circle-radius':['interpolate',['linear'],['zoom'],3.2,10,8,15],'circle-opacity':0.001}
    });
  }
  if (interaction?.register) {
    interaction.register('project-mud-below-us', {
      layers:[HIT_LAYER],
      objectType:'project-symbolic-case',
      clickPriority:84,
      hoverPriority:84,
      enabled:()=>enabled,
      onClick:(event, feature)=>renderCase(feature)
    });
  }
  setLayerVisibility(false);
}

async function ensureSubdivisions() {
  if (!window.__potatoAtlasSubdivisions) {
    await window.__potatoAtlasLoadModule?.('Subdivisions', './3d-subdivisions.js');
  }
  if (!window.__potatoAtlasSubdivisions) throw new Error('Subdivision runtime unavailable.');
  await window.__potatoAtlasSubdivisions.loadPartition('USA');
}

async function loadData() {
  if (loaded) return;
  const response = await fetch(DATA_URL);
  if (!response.ok) throw new Error(`Mud / Below project cases unavailable (${response.status})`);
  data = await response.json();
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) {
    throw new Error('Mud / Below project cases are not valid GeoJSON.');
  }
  await ensureSubdivisions();
  installLayers();
  loaded = true;
}

async function setEnabled(next) {
  await loadData();
  const requested = Boolean(next);
  if (requested) {
    if (window.__potatoAtlasSubdivisions?.retainPartition) {
      await window.__potatoAtlasSubdivisions.retainPartition('USA', 'mud-below-us');
    } else {
      await window.__potatoAtlasSubdivisions?.refresh?.();
    }
  }
  enabled = requested;
  setLayerVisibility(enabled);
  updateUrl();
  if (enabled) {
    try { map.fitBounds([[-125,24],[-66,50]], { padding:60, duration:550, maxZoom:4.8 }); } catch {}
  } else {
    await window.__potatoAtlasSubdivisions?.releasePartition?.('USA', 'mud-below-us');
  }
  window.dispatchEvent(new CustomEvent('potato-atlas-mud-below-change', {
    detail:{ enabled, records:data.features.length, epistemicType:data?.metadata?.epistemic_type || 'project-interpretive' }
  }));
  return enabled;
}

async function toggle() { return setEnabled(!enabled); }

window.__potatoAtlasMudBelow = {
  ready:loadData(),
  toggle,
  setEnabled,
  renderCase,
  status(){ return { enabled, loaded, records:data.features.length, metadata:data?.metadata || null }; }
};

const params = new URL(location.href).searchParams;
if (params.get('projectLayer') === 'mud-below-us') {
  window.__potatoAtlasMudBelow.ready.then(()=>setEnabled(true)).catch(error=>console.warn('Mud / Below project layer unavailable:', error));
}
window.dispatchEvent(new CustomEvent('potato-atlas-mud-below-ready'));
