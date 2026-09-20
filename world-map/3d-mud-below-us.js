if (!window.__potatoAtlasUrlState) await import('./3d-url-state.js');
const urlState = window.__potatoAtlasUrlState;
urlState.claim('mud-below', ['projectLayer']);

// U.S. project-symbolic Mud / Below case overlay for the canonical World Map.
// This is a project-interpretive layer. It must never be read as an objective
// classification of people, and its coordinates are broad state-centroid anchors.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Mud / Below overlay requires the core map.');
if (!window.__potatoAtlasMotion) await import('./3d-motion.js');
const motion = window.__potatoAtlasMotion;

const DATA_URL = '../data/world-symbolic/us-mud-below-project-cases.geo.json';
const SOURCE_ID = 'project-mud-below-us';
const POINT_LAYER = 'project-mud-below-points';
const LABEL_LAYER = 'project-mud-below-labels';
const HIT_LAYER = 'project-mud-below-hit';
function interactionRouter() { return window.__potatoAtlasInteraction; }
function inspectorRouter() { return window.__potatoAtlasInspector; }

let enabled = false;
let loaded = false;
let data = { type:'FeatureCollection', features:[] };

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

function casesForSubdivision(id) {
  const key = String(id || '');
  return (data?.features || []).filter(feature => String(feature?.properties?.subdivision_id || '') === key);
}
function renderSubdivisionCasesPanel(id) {
  const rows = casesForSubdivision(id);
  const state = rows[0]?.properties?.state || id;
  const panel = document.getElementById('panel');
  if (!panel) return;
  panel.innerHTML = `
    <div class="eyebrow">Subdivision evidence · Mud / Below</div>
    <h1>${esc(state)}</h1>
    <p class="muted">${rows.length} project case anchor${rows.length===1?'':'s'} associated with this state in the current project-symbolic overlay.</p>
    <div class="card">${rows.map(feature => {
      const p = feature.properties || {};
      return `<button type="button" class="relation-button" data-mud-case="${esc(feature.id || '')}">
        <span><b>${esc(p.label || feature.id || 'Project case')}</b><small>${esc(p.map_role || 'Project case')}</small></span>
        <span>Open</span>
      </button>`;
    }).join('') || '<span class="muted">No project case anchors for this state.</span>'}</div>
    <div class="boundary">These are project-symbolic case anchors, not a census or an objective classification of a state or its residents. Coordinates are broad state centroids.</div>`;
  panel.querySelectorAll?.('[data-mud-case]')?.forEach(button => {
    button.addEventListener('click', () => {
      const feature = (data.features || []).find(row => String(row.id || '') === button.dataset.mudCase);
      if (feature) renderCase(feature);
    });
  });
  window.__potatoAtlasPanelLifecycle?.publish?.();
}
function openSubdivisionCases(id) {
  if (!inspectorRouter()?.open) { renderSubdivisionCasesPanel(id); return true; }
  const current = inspectorRouter()?.current?.();
  if (current?.type !== 'subdivision' || current.id !== id) {
    renderSubdivisionCasesPanel(id);
    return true;
  }
  inspectorRouter()?.open({
    type:'evidence',
    id:`mud-below-us:${id}`,
    owner:'mud-below-us',
    parent:{ type:'subdivision', id },
    render:() => renderSubdivisionCasesPanel(id),
  });
  return true;
}
function registerSubdivisionEvidence() {
  return window.__potatoAtlasSubdivisions?.registerEvidenceProvider?.('mud-below-us', {
    summary(id) {
      if (!enabled) return null;
      const rows = casesForSubdivision(id);
      if (!rows.length) return null;
      return {
        active:true,
        eyebrow:'Active project evidence · Mud / Below',
        primary:rows.length,
        summary:`project case anchor${rows.length===1?'':'s'} associated with this state.`,
        boundary:'Project-symbolic case anchors only; not a census or objective classification of residents.',
        actionLabel:'Open Mud / Below cases',
      };
    },
    open(id) { openSubdivisionCases(id); },
  }) || false;
}

function updateUrl() {
  const current = urlState.read('projectLayer');
  urlState.patch('mud-below', {
    set:{ projectLayer:enabled ? 'mud-below-us' : (current === 'mud-below-us' ? null : current) },
  });
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

function renderCasePanel(feature) {
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

function renderCase(feature) {
  const p = feature?.properties || {};
  if (!inspectorRouter()?.open) { renderCasePanel(feature); return true; }
  let current = inspectorRouter()?.current?.();
  if (!current) {
    inspectorRouter()?.setBaseline({
      type:'country', id:'USA', owner:'country-selection',
      restore:() => window.goCountry?.('USA'),
    });
    current = inspectorRouter()?.current?.();
  }
  const id = String(feature?.id ?? p.id ?? p.label ?? 'mud-below-case');
  inspectorRouter()?.open({
    type:'project-case',
    id,
    owner:'mud-below-us',
    parent:current ? { type:current.type, id:current.id } : { type:'country', id:'USA' },
    render:() => renderCasePanel(feature),
  });
  return true;
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
  if (interactionRouter()?.register) {
    interactionRouter()?.register('project-mud-below-us', {
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
  registerSubdivisionEvidence();
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
    try { motion.fitBounds(map, [[-125,24],[-66,50]], { padding:60, duration:550, maxZoom:4.8 }); } catch {}
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
  openSubdivisionCases,
  casesForSubdivision,
  status(){ return { enabled, loaded, records:data.features.length, metadata:data?.metadata || null }; }
};

const params = new URL(location.href).searchParams;
if (params.get('projectLayer') === 'mud-below-us') {
  window.__potatoAtlasMudBelow.ready.then(()=>setEnabled(true)).catch(error=>console.warn('Mud / Below project layer unavailable:', error));
}
window.dispatchEvent(new CustomEvent('potato-atlas-mud-below-ready'));
