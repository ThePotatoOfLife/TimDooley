// ADL H.E.A.T. evidence layer for the canonical World Map.
// Uses the existing U.S. subdivision source for state shading and a separate
// incident point source for locality-level evidence. Source semantics remain
// explicit: these are ADL-derived records, not a generic hate/crime score.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('ADL H.E.A.T. layer requires the core map.');
if (!window.__potatoAtlasMotion) await import('./3d-motion.js');
const motion = window.__potatoAtlasMotion;
if (!window.__potatoAtlasScale?.ready) await import('./3d-scale.js');
const scale = await window.__potatoAtlasScale?.ready;
if (!scale?.threshold || !scale?.capabilityActive) throw new Error('ADL H.E.A.T. requires the shared World Map Scale runtime.');
const pointRenderZoom = scale.threshold('adl-heat-points', 'render');
const pointInteractZoom = scale.threshold('adl-heat-points', 'interact');

const DATA_URL = '../data/world-incidents/adl-heat/incidents.geo.json';
const SUMMARY_URL = '../data/world-incidents/adl-heat/state-summary.json';
const META_URL = '../data/world-incidents/adl-heat/metadata.json';
const STATE_SOURCE = 'atlas-subdivisions-active';
const STATE_LAYER = 'adl-heat-state-fill';
const POINT_SOURCE = 'adl-heat-incidents';
const POINT_LAYER = 'adl-heat-incident-points';
const POINT_HIT = 'adl-heat-incident-hit';
const STATE_KEY = 'adlHeatCount';
const interaction = window.__potatoAtlasInteraction;

let enabled = false;
let loaded = false;
let loadPromise = null;
let stateRefreshQueued = false;
let metadata = null;
let summary = null;
let incidents = null;
let filtered = { type:'FeatureCollection', features:[] };
let selectedYear = 'all';
let selectedType = 'all';
let stateValues = new Map();
let controlsBound = false;

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const fmt = value => new Intl.NumberFormat('en').format(Number(value) || 0);

function yearOptions() {
  return [...new Set((incidents?.features || []).map(f => Number(f?.properties?.year)).filter(Number.isFinite))].sort((a,b)=>b-a);
}
function incidentTypeTokens(value) {
  return String(value || '').split(';').map(token => token.trim()).filter(Boolean);
}
function typeOptions() {
  return [...new Set((incidents?.features || []).flatMap(feature => incidentTypeTokens(feature?.properties?.incident_type)))].sort();
}
function activeFeatures() {
  return (incidents?.features || []).filter(feature => {
    const p = feature.properties || {};
    const yearOk = selectedYear === 'all' || String(p.year) === String(selectedYear);
    const typeOk = selectedType === 'all' || incidentTypeTokens(p.incident_type).includes(selectedType);
    return yearOk && typeOk;
  });
}
function aggregateStateCount(row) {
  if (!row) return 0;
  if (selectedYear === 'all' && selectedType === 'all') return Number(row.total) || 0;
  if (selectedYear !== 'all' && selectedType === 'all') return Number(row.by_year?.[String(selectedYear)]) || 0;
  if (selectedYear === 'all' && selectedType !== 'all') return Number(row.by_type_token?.[selectedType]) || 0;
  return Number(row.by_year_type_token?.[String(selectedYear)]?.[selectedType]) || 0;
}
function recomputeStateValues() {
  stateValues = new Map();
  for (const [id, row] of Object.entries(summary?.states || {})) {
    stateValues.set(id, aggregateStateCount(row));
  }
}
function maxCount() {
  return Math.max(1, ...stateValues.values());
}
function stateColorExpression() {
  const max = maxCount();
  const ratio = ['/', ['to-number', ['coalesce', ['feature-state', STATE_KEY], 0]], max];
  return [
    'interpolate', ['linear'], ratio,
    0, 'rgba(194,120,120,0)',
    0.02, 'rgba(194,120,120,0.18)',
    0.34, 'rgba(194,120,120,0.36)',
    0.67, 'rgba(194,120,120,0.56)',
    1, 'rgba(194,120,120,0.76)'
  ];
}
function updateStateFeatureState() {
  let failures = 0;
  for (const code of Object.keys(summary?.states || {})) {
    const count = stateValues.get(code) || 0;
    try { map.setFeatureState({ source:STATE_SOURCE, id:code }, { [STATE_KEY]:count }); }
    catch { failures += 1; }
  }
  if (map.getLayer(STATE_LAYER)) map.setPaintProperty(STATE_LAYER, 'fill-color', stateColorExpression());
  if (failures && enabled) map.once?.('idle', scheduleStateFeatureState);
}
function scheduleStateFeatureState() {
  if (!enabled || !loaded || stateRefreshQueued) return;
  stateRefreshQueued = true;
  queueMicrotask(() => {
    stateRefreshQueued = false;
    if (enabled) updateStateFeatureState();
  });
}
window.addEventListener('potato-atlas-subdivisions-source-change', scheduleStateFeatureState);
map.on('sourcedata', event => {
  if (event?.sourceId === STATE_SOURCE && event?.isSourceLoaded) scheduleStateFeatureState();
});
function updatePointSource() {
  const source = map.getSource(POINT_SOURCE);
  if (source?.setData) source.setData(filtered);
}
function updateFilterUrl() {
  const url = new URL(location.href);
  if (enabled) {
    if (selectedYear !== 'all') url.searchParams.set('adlYear', selectedYear); else url.searchParams.delete('adlYear');
    if (selectedType !== 'all') url.searchParams.set('adlType', selectedType); else url.searchParams.delete('adlType');
  } else {
    url.searchParams.delete('adlYear');
    url.searchParams.delete('adlType');
  }
  history.replaceState({}, '', url);
}
function setLayerVisibility(show) {
  const visibility = show ? 'visible' : 'none';
  for (const id of [STATE_LAYER, POINT_LAYER, POINT_HIT]) {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
  }
  const button = document.getElementById('adlHeatLayer');
  button?.classList.toggle('active', show);
  button?.setAttribute('aria-pressed', show ? 'true' : 'false');
}
function applyFilters() {
  filtered = { type:'FeatureCollection', features:activeFeatures() };
  recomputeStateValues();
  updatePointSource();
  updateStateFeatureState();
  renderControls();
  updateFilterUrl();
  window.dispatchEvent(new CustomEvent('potato-atlas-adl-heat-change', {
    detail:{ enabled, year:selectedYear, incidentType:selectedType, records:filtered.features.length }
  }));
}
function sourceStatusText() {
  const snap = metadata?.snapshot || {};
  const dates = [snap.exact_min_date, snap.exact_max_date].filter(Boolean).join(' → ');
  return `${snap.status || 'snapshot'} · ${snap.dataset || 'ADL H.E.A.T.'}${dates ? ` · ${dates}` : ''}`;
}
function ensureControlSurface() {
  const button = document.getElementById('adlHeatLayer');
  if (!button) return null;
  let surface = document.getElementById('adlHeatControls');
  if (!surface) {
    surface = document.createElement('div');
    surface.id = 'adlHeatControls';
    surface.className = 'adl-heat-controls';
    surface.hidden = true;
    button.insertAdjacentElement('afterend', surface);
  }
  return surface;
}
function renderControls() {
  const surface = ensureControlSurface();
  if (!surface) return;
  surface.hidden = !enabled;
  if (!enabled) return;
  const years = yearOptions();
  const types = typeOptions();
  surface.innerHTML = `
    <div class="menu-title">ADL H.E.A.T. filters</div>
    <select data-adl-year aria-label="ADL H.E.A.T. year">
      <option value="all">All years</option>
      ${years.map(year => `<option value="${year}"${String(year)===String(selectedYear)?' selected':''}>${year}</option>`).join('')}
    </select>
    <select data-adl-type aria-label="ADL H.E.A.T. incident type">
      <option value="all">All incident types</option>
      ${types.map(type => `<option value="${esc(type)}"${type===selectedType?' selected':''}>${esc(type)}</option>`).join('')}
    </select>
    <div class="boundary"><b>${fmt(filtered.features.length)} records shown</b><br>${esc(sourceStatusText())}<br>Counts are records in this ADL-derived snapshot, not a general hate score or crime score.</div>
    <div class="muted">State shading = filtered record count. Canonical state borders/labels remain above the shading. Gold dots = geocoded source records; zoom in for individual incidents.</div>
    <button type="button" data-adl-focus>Focus U.S.</button>
    <button type="button" data-adl-source>Source / methodology</button>`;
  surface.querySelector('[data-adl-year]')?.addEventListener('change', event => {
    selectedYear = event.target.value || 'all';
    applyFilters();
  });
  surface.querySelector('[data-adl-type]')?.addEventListener('change', event => {
    selectedType = event.target.value || 'all';
    applyFilters();
  });
  surface.querySelector('[data-adl-focus]')?.addEventListener('click', () => {
    try { motion.fitBounds(map, [[-125,24],[-66,50]], { padding:60, duration:550, maxZoom:4.8 }); } catch {}
  });
  surface.querySelector('[data-adl-source]')?.addEventListener('click', () => renderDatasetInspector());
}
function renderDatasetInspector() {
  const panel = document.getElementById('panel');
  if (!panel) return;
  const snap = metadata?.snapshot || {};
  panel.innerHTML = `
    <div class="eyebrow">Evidence dataset · ADL H.E.A.T.</div>
    <h1>U.S. incident evidence layer</h1>
    <p class="muted">Source owner: ${esc(metadata?.source_organization || 'Anti-Defamation League')}</p>
    <div class="card"><b>Snapshot</b><p>${esc(sourceStatusText())}</p><p>${fmt(snap.record_count)} source records · ${fmt(snap.geocoded_record_count)} geocoded</p></div>
    <div class="boundary">${esc(metadata?.methodology?.display_semantics || '')}</div>
    <h2>Refresh contract</h2>
    <p>The renderer accepts the official ADL H.E.A.T. CSV through <code>${esc(metadata?.refresh?.importer || 'scripts/import_adl_heat.py')}</code>. The committed seed is historical and visibly labelled as such.</p>
    <p class="muted">${esc(snap.limitation || '')}</p>
    <div class="actions"><a href="${esc(metadata?.official_source_url || '#')}" target="_blank" rel="noopener">Open ADL source</a></div>`;
  window.__potatoAtlasPanelLifecycle?.publish?.();
}
function renderIncident(feature) {
  const p = feature?.properties || {};
  const panel = document.getElementById('panel');
  if (!panel) return;
  panel.innerHTML = `
    <div class="eyebrow">ADL H.E.A.T. record</div>
    <h1>${esc(p.city || p.state_name || 'Incident')}</h1>
    <p class="muted">${esc(p.date || 'Undated')} · ${esc(p.state_name || p.state || '')}</p>
    <div class="card"><b>${esc(p.incident_type || p.dataset || 'Incident')}</b>
      ${p.ideology ? `<p><b>ADL ideology field:</b> ${esc(p.ideology)}</p>` : ''}
      ${p.subideology ? `<p><b>Subideology:</b> ${esc(p.subideology)}</p>` : ''}
      ${p.group ? `<p><b>Group:</b> ${esc(p.group)}</p>` : ''}
      ${p.description ? `<p>${esc(p.description)}</p>` : ''}
    </div>
    <div class="boundary">Classification and description are presented as fields from the ADL-derived source snapshot. Location is the source record coordinate.</div>
    <p class="muted">${esc(p.source_status || '')}</p>
    <div class="actions">
      <button type="button" data-adl-state>Open ${esc(p.state_name || p.state || 'state')}</button>
      <button type="button" data-adl-source>Dataset methodology</button>
    </div>`;
  panel.querySelector('[data-adl-state]')?.addEventListener('click', () => openStateEvidence(p.subdivision_id));
  panel.querySelector('[data-adl-source]')?.addEventListener('click', renderDatasetInspector);
  window.__potatoAtlasPanelLifecycle?.publish?.();
}
function topEntries(obj = {}, limit = 6) {
  return Object.entries(obj).sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0])).slice(0,limit);
}
async function openStateEvidence(id, options={}) {
  if (!id) return false;
  if (window.__potatoAtlasSubdivisions?.select) {
    try { await window.__potatoAtlasSubdivisions.select(id, { fit:options.fit !== false }); }
    catch (error) { console.warn(`ADL state selection unavailable: ${id}`, error); }
  }
  renderStateInspector(id);
  return true;
}
function renderStateInspector(id) {
  const row = summary?.states?.[id] || null;
  const panel = document.getElementById('panel');
  if (!panel || !row) return;
  const visible = filtered.features.filter(f => f?.properties?.subdivision_id === id);
  const filteredCount = aggregateStateCount(row);
  const byType = {};
  const byYear = {};
  for (const feature of visible) {
    const p = feature.properties || {};
    byType[p.incident_type || 'Unknown'] = (byType[p.incident_type || 'Unknown'] || 0) + 1;
    if (p.year) byYear[p.year] = (byYear[p.year] || 0) + 1;
  }
  panel.innerHTML = `
    <div class="eyebrow">Subdivision evidence · ADL H.E.A.T.</div>
    <h1>${esc(row.name)}</h1>
    <p class="muted">${fmt(filteredCount)} records under the active filters · ${fmt(row.total)} in the full committed snapshot</p>
    <div class="grid">
      <div class="metric"><span>Filtered records</span><b>${fmt(filteredCount)}</b></div>
      <div class="metric"><span>Snapshot total</span><b>${fmt(row.total)}</b></div>
    </div>
    <h2>Incident-type fields</h2>
    <div class="card">${topEntries(byType).map(([name,count])=>`<div class="row"><b>${fmt(count)}</b> ${esc(name)}</div>`).join('') || '<span class="muted">No records under current filters.</span>'}</div>
    <h2>Years</h2>
    <div class="card">${topEntries(byYear,10).map(([year,count])=>`<div class="row"><b>${esc(year)}</b> · ${fmt(count)}</div>`).join('') || '<span class="muted">No dated records under current filters.</span>'}</div>
    <div class="boundary">These counts describe records in an ADL dataset snapshot. They are not population-normalized and should not be read as a ranking of residents, state character, or total hate crime.</div>
    <div class="actions"><button type="button" data-adl-source>Source / methodology</button></div>`;
  panel.querySelector('[data-adl-source]')?.addEventListener('click', renderDatasetInspector);
  window.__potatoAtlasPanelLifecycle?.publish?.();
}
function installLayers() {
  if (!map.getSource(POINT_SOURCE)) map.addSource(POINT_SOURCE, { type:'geojson', data:filtered, promoteId:'id' });
  const before = map.getLayer('atlas-subdivision-line') ? 'atlas-subdivision-line' : (map.getLayer('countries-line') ? 'countries-line' : undefined);
  if (!map.getLayer(STATE_LAYER)) map.addLayer({
    id:STATE_LAYER,type:'fill',source:STATE_SOURCE,
    filter:['==',['get','parent_iso3'],'USA'],
    paint:{'fill-color':stateColorExpression(),'fill-opacity':1}
  }, before);
  if (!map.getLayer(POINT_LAYER)) map.addLayer({
    id:POINT_LAYER,type:'circle',source:POINT_SOURCE,minzoom:pointRenderZoom,
    paint:{
      'circle-radius':['interpolate',['linear'],['zoom'],pointRenderZoom,2.8,7,5.5,10,8],
      'circle-color':'#e0bd78','circle-opacity':0.76,
      'circle-stroke-color':'#101616','circle-stroke-width':1
    }
  });
  if (!map.getLayer(POINT_HIT)) map.addLayer({
    id:POINT_HIT,type:'circle',source:POINT_SOURCE,minzoom:pointInteractZoom,
    paint:{'circle-radius':['interpolate',['linear'],['zoom'],pointInteractZoom,8,8,12],'circle-opacity':0.001}
  });
  window.__potatoAtlasRenderStack?.register?.(STATE_LAYER, {
    slot:'subnational-fill', priority:20, owner:'evidence:adl-heat'
  });
  window.__potatoAtlasRenderStack?.register?.(POINT_LAYER, {
    slot:'context-network', priority:70, owner:'evidence:adl-heat'
  });
  if (interaction?.register) {
    interaction.register('adl-heat-incidents', {
      layers:[POINT_HIT], objectType:'evidence-record', clickPriority:85, hoverPriority:85,
      enabled:()=>enabled && scale.capabilityActive('adl-heat-points', 'interact', map.getZoom()),
      onClick:(event, feature)=>renderIncident(feature)
    });
    interaction.register('adl-heat-states', {
      layers:[STATE_LAYER], objectType:'subdivision-evidence', clickPriority:65, hoverPriority:20,
      enabled:()=>enabled,
      onClick:(event, feature)=>openStateEvidence(String(feature?.properties?.id || feature?.id || ''), { fit:false })
    });
  }
  setLayerVisibility(false);
}
function registerSubdivisionEvidence() {
  return window.__potatoAtlasSubdivisions?.registerEvidenceProvider?.('adl-heat', {
    summary(id) {
      const row = window.__potatoAtlasAdlHeat?.stateEvidence?.(id);
      if (!row?.enabled) return null;
      return {
        active:true,
        eyebrow:'Active evidence · ADL H.E.A.T.',
        primary:row.filteredCount,
        summary:`records under active filters · ${fmt(row.snapshotTotal)} in snapshot.`,
        boundary:'Source-attributed evidence; not a population-normalized score or characterization of residents.',
        actionLabel:'Open ADL evidence',
      };
    },
    open(id) { renderStateInspector(id); },
  }) || false;
}
async function ensureSubdivisions() {
  if (!window.__potatoAtlasSubdivisions) {
    await window.__potatoAtlasLoadModule?.('Subdivisions', './3d-subdivisions.js');
  }
  if (!window.__potatoAtlasSubdivisions) throw new Error('Subdivision runtime unavailable.');
  await window.__potatoAtlasSubdivisions.loadPartition('USA');
  registerSubdivisionEvidence();
  await window.__potatoAtlasSubdivisions.refresh?.();
}
async function loadData() {
  if (loaded) return true;
  if (loadPromise) return loadPromise;
  loadPromise = (async () => {
    const [metaResponse, summaryResponse, incidentResponse] = await Promise.all([META_URL,SUMMARY_URL,DATA_URL].map(url=>fetch(url)));
    for (const response of [metaResponse,summaryResponse,incidentResponse]) if (!response.ok) throw new Error(`ADL H.E.A.T. data unavailable (${response.status})`);
    [metadata,summary,incidents] = await Promise.all([metaResponse.json(),summaryResponse.json(),incidentResponse.json()]);
    const params = new URL(location.href).searchParams;
    selectedYear = params.get('adlYear') || 'all';
    selectedType = params.get('adlType') || 'all';
    filtered = { type:'FeatureCollection', features:activeFeatures() };
    recomputeStateValues();
    await ensureSubdivisions();
    installLayers();
    loaded = true;
    return true;
  })();
  try {
    return await loadPromise;
  } catch (error) {
    loadPromise = null;
    throw error;
  }
}
async function setEnabled(next) {
  await loadData();
  const requested = Boolean(next);
  if (requested) {
    if (window.__potatoAtlasSubdivisions?.retainPartition) {
      await window.__potatoAtlasSubdivisions.retainPartition('USA', 'adl-heat');
    } else {
      await window.__potatoAtlasSubdivisions?.refresh?.();
    }
  }
  enabled = requested;
  setLayerVisibility(enabled);
  applyFilters();
  renderControls();
  if (enabled) {
    try {
      motion.fitBounds(map, [[-125,24],[-66,50]], { padding:60, duration:550, maxZoom:4.8 });
    } catch {}
  } else {
    await window.__potatoAtlasSubdivisions?.releasePartition?.('USA', 'adl-heat');
  }
  return enabled;
}
async function toggle() { return setEnabled(!enabled); }

window.__potatoAtlasAdlHeat = {
  ready:loadData(),
  toggle,
  setEnabled,
  applyFilters,
  renderDatasetInspector,
  renderStateInspector,
  stateEvidence(id){
    const row = summary?.states?.[id] || null;
    if (!row) return null;
    return {
      id,
      enabled,
      filteredCount:aggregateStateCount(row),
      snapshotTotal:Number(row.total)||0,
      year:selectedYear,
      incidentType:selectedType,
      dataset:metadata?.snapshot?.dataset || metadata?.title || 'ADL H.E.A.T.',
      sourceStatus:metadata?.snapshot?.status || null,
    };
  },
  status(){ return { enabled, loaded, year:selectedYear, incidentType:selectedType, records:filtered.features.length, snapshot:metadata?.snapshot || null }; }
};

const params = new URL(location.href).searchParams;
if (params.get('evidenceLayer') === 'adl-heat' && !window.__potatoAtlasEvidenceLayers) {
  window.__potatoAtlasAdlHeat.ready.then(()=>setEnabled(true)).catch(error=>console.warn('ADL H.E.A.T. layer unavailable:', error));
}
window.dispatchEvent(new CustomEvent('potato-atlas-adl-heat-ready'));
