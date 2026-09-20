if (!window.__potatoAtlasUrlState) await import('./3d-url-state.js');
const urlState = window.__potatoAtlasUrlState;
urlState.claim('physical-layers', ['physical']);

// Lazy Physical World runtime + first-class World Bar mixer.
// Manifest metadata loads with the core; expensive providers/modules do not.
// Compatibility map: physical.terrain -> __potatoAtlasTerrain.
// Current water map: physical.water.base -> __potatoAtlasPhysicalWater.
// Current hydrology map: physical.water.hydrology -> __potatoAtlasHydrology.
// Current land-cover map: physical.land-cover -> __potatoAtlasLandCover.
// Current deserts map: physical.aridity -> __potatoAtlasDeserts.

const MANIFEST_URL = '../data/world-map-physical-layers.json';
const OPACITY_IDS = new Set(['physical.water.base','physical.water.hydrology','physical.land-cover','physical.aridity']);
const SURFACE_FOCUS_IDS = new Set(['physical.land-cover','physical.aridity']);
const DEFAULT_COUNTRY_OPACITY = 0.60;
const SURFACE_COUNTRY_OPACITY = 0.18;
const SELECTED_COUNTRY_OPACITY = 0.90;
const COMPARED_COUNTRY_OPACITY = 0.80;
const active = new Set();
const statusRecords = new Map();
let manifest = { entries:[] };
let loading = new Map();

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function entries() { return [...(manifest.entries || [])]; }
function get(id) { return entries().find(row => row.id === id) || null; }
function isActive(id) { return active.has(id); }
function activeIds() { return [...active]; }
function clampOpacity(value) { return Math.max(0, Math.min(1, Number(value))); }
function controller(row) { return row?.controller ? window[row.controller] : null; }
function defaultOpacity(row) {
  const value = Number(row?.default_opacity);
  return Number.isFinite(value) ? clampOpacity(value) : 1;
}
function ensureStatus(row) {
  if (!row) return null;
  if (!statusRecords.has(row.id)) {
    statusRecords.set(row.id, {
      id:row.id,
      provider:row.source?.provider || null,
      phase:'idle',
      message:row.status_note || '',
      active:false,
      opacity:defaultOpacity(row),
      retryable:true,
      attempts:0,
      lastSuccessAt:null,
      lastErrorAt:null,
      updatedAt:Date.now(),
    });
  }
  return statusRecords.get(row.id);
}
function setStatus(id, patch = {}) {
  const row = get(id);
  if (!row) return null;
  const record = ensureStatus(row);
  const now = Date.now();
  const next = { ...patch };
  if (next.phase === 'loading') next.attempts = Number(record.attempts || 0) + 1;
  if (next.phase === 'active') next.lastSuccessAt = now;
  if (next.phase === 'error') next.lastErrorAt = now;
  Object.assign(record, next, {
    provider:next.provider || record.provider || row.source?.provider || null,
    updatedAt:now,
    active:active.has(id),
  });
  renderMenu();
  return {...record};
}
function status(id) {
  const row = get(id);
  const record = row ? ensureStatus(row) : null;
  return record ? {...record, active:active.has(id)} : null;
}
function getOpacity(id) {
  return status(id)?.opacity ?? null;
}

function surfaceFocusActive() {
  for (const id of SURFACE_FOCUS_IDS) {
    if (!active.has(id)) continue;
    const row = get(id);
    const opacity = ensureStatus(row)?.opacity ?? defaultOpacity(row);
    if (opacity > 0.02) return true;
  }
  return false;
}
function countryOpacityExpression(surfaceFocus = surfaceFocusActive()) {
  const selected = ['boolean',['feature-state','selected'],false];
  const compared = ['boolean',['feature-state','compare'],false];
  return ['case', selected, SELECTED_COUNTRY_OPACITY, compared, COMPARED_COUNTRY_OPACITY, surfaceFocus ? SURFACE_COUNTRY_OPACITY : DEFAULT_COUNTRY_OPACITY];
}
function syncCountrySurfaceTint() {
  const map = window.__potatoAtlasMap;
  if (!map?.getLayer?.('countries-fill')) return false;
  try {
    map.setPaintProperty('countries-fill', 'fill-opacity', countryOpacityExpression());
    return true;
  } catch (error) {
    console.warn('Physical surface country tint could not be synchronized:', error);
    return false;
  }
}

function persist() {
  const values = activeIds().sort();
  urlState.patch('physical-layers', { set:{ physical:values.length ? values.join(',') : null } });
}

function emit(reason, id) {
  window.dispatchEvent(new CustomEvent('potato-atlas-physical-change', {
    detail:{ reason, id, active:activeIds() }
  }));
  renderMenu();
}

async function ensureModule(row) {
  if (!row?.module) throw new Error(`Physical layer ${row?.id || '<unknown>'} has no module`);
  if (controller(row)) return true;
  if (loading.has(row.id)) return loading.get(row.id);
  const promise = Promise.resolve(window.__potatoAtlasLoadModule?.(`Physical · ${row.label}`, row.module))
    .then(result => Boolean(result || controller(row)))
    .finally(() => loading.delete(row.id));
  loading.set(row.id, promise);
  return promise;
}

async function setOpacity(id, value) {
  const row = get(id);
  if (!row || !OPACITY_IDS.has(id)) return false;
  const api = controller(row);
  if (!api?.setOpacity) return false;
  const record = ensureStatus(row);
  const previous = record.opacity;
  const next = clampOpacity(value);
  try {
    const applied = await api.setOpacity(next);
    if (applied === false) throw new Error(`${row.label} rejected opacity update`);
    record.opacity = Number.isFinite(Number(api.getOpacity?.())) ? clampOpacity(api.getOpacity()) : next;
    record.updatedAt = Date.now();
    syncCountrySurfaceTint();
    renderMenu();
    return true;
  } catch (error) {
    record.opacity = previous;
    syncCountrySurfaceTint();
    setStatus(id, { phase:'error', message:`Opacity unavailable · ${error?.message || error}` });
    return false;
  }
}

async function activate(id, { persistState = true } = {}) {
  const row = get(id);
  if (!row || row.availability !== 'current') return false;
  if (active.has(id)) return true;
  setStatus(id, { phase:'loading', message:'Loading…' });
  try {
    if (row.load_policy !== 'on_demand') throw new Error(`Unsupported physical load policy: ${row.load_policy}`);
    if (row.kind !== 'module') throw new Error(`${row.label} provider is not activated yet`);
    const ok = await ensureModule(row);
    if (!ok) throw new Error(`Could not load ${row.label}`);
    const api = controller(row);
    if (!api?.enable) throw new Error(`${row.label} has no controller enable() API`);
    const enableResult = await api.enable();
    if (enableResult === false) throw new Error(`${row.label} provider did not activate`);
    active.add(id);
    const record = ensureStatus(row);
    if (OPACITY_IDS.has(id) && api?.setOpacity) await api.setOpacity(record.opacity);
    if (!['zoom-needed','partial'].includes(record.phase)) setStatus(id, { phase:'active', message:'Active' });
    syncCountrySurfaceTint();
    if (persistState) persist();
    emit('activate', id);
    return true;
  } catch (error) {
    active.delete(id);
    syncCountrySurfaceTint();
    if (persistState) persist();
    console.warn(`Physical layer unavailable: ${id}`, error);
    setStatus(id, { phase:'error', message:error?.message || 'Provider unavailable' });
    emit('error', id);
    return false;
  }
}

async function deactivate(id, { persistState = true, emitChange = true } = {}) {
  if (!active.has(id)) {
    const row = get(id); if (row) setStatus(id, { phase:'idle', message:row.status_note || '' });
    syncCountrySurfaceTint();
    return true;
  }
  const row = get(id);
  const api = controller(row);
  try { await api?.disable?.(); } catch (error) { console.warn(`Physical layer disable failed: ${id}`, error); }
  active.delete(id);
  setStatus(id, { phase:'idle', message:row?.status_note || '' });
  syncCountrySurfaceTint();
  if (persistState) persist();
  if (emitChange) emit('deactivate', id);
  return true;
}

async function toggle(id) {
  return isActive(id) ? deactivate(id) : activate(id);
}

async function reset() {
  const ids = activeIds();
  const failed = [];
  for (const id of ids) {
    try { await deactivate(id, { persistState:false, emitChange:false }); }
    catch (error) { failed.push({id, message:error?.message || String(error)}); active.delete(id); }
  }
  for (const row of entries()) {
    const record = ensureStatus(row);
    record.opacity = defaultOpacity(row);
    record.phase = 'idle';
    record.message = row.status_note || '';
    record.active = false;
    record.updatedAt = Date.now();
    const api = controller(row);
    if (OPACITY_IDS.has(row.id) && api?.setOpacity) {
      try { await api.setOpacity(record.opacity); } catch (error) { failed.push({id:row.id, message:error?.message || String(error)}); }
    }
  }
  active.clear();
  syncCountrySurfaceTint();
  persist();
  emit('reset', null);
  return { ok:failed.length === 0, failed };
}

function menuHost() { return document.getElementById('atlasWorldBar'); }
function phaseLabel(record, row) {
  if (row.availability !== 'current') return 'planned';
  const labels = { idle:'off', loading:'loading', active:'active', 'zoom-needed':'zoom in', partial:'partial', error:'provider unavailable' };
  return labels[record?.phase] || record?.phase || 'off';
}

function renderMenu() {
  const bar = menuHost();
  if (!bar) return false;
  let details = document.getElementById('atlasPhysicalMenu');
  if (!details) {
    details = document.createElement('details');
    details.id = 'atlasPhysicalMenu';
    details.className = 'atlas-world-menu';
    details.innerHTML = '<summary>Physical</summary><div class="atlas-world-menu-pop"></div>';
    const geography = document.getElementById('atlasGeographyMenu');
    if (geography?.nextSibling) bar.insertBefore(details, geography.nextSibling);
    else if (geography) geography.after(details);
    else bar.appendChild(details);
    details.addEventListener('click', async event => {
      const clear = event.target.closest('[data-physical-clear]');
      if (clear) { event.preventDefault(); await reset(); return; }
      if (event.target.closest('[data-physical-opacity]')) return;
      const button = event.target.closest('[data-physical-layer]');
      if (!button || button.disabled) return;
      await toggle(button.dataset.physicalLayer);
    });
    details.addEventListener('input', async event => {
      const slider = event.target.closest('[data-physical-opacity]');
      if (!slider) return;
      event.stopPropagation();
      await setOpacity(slider.dataset.physicalOpacity, Number(slider.value) / 100);
    });
  }
  const pop = details.querySelector('.atlas-world-menu-pop');
  if (!pop) return false;
  const rows = entries().map(row => {
    const current = row.availability === 'current';
    const on = isActive(row.id);
    const record = ensureStatus(row);
    const slider = on && OPACITY_IDS.has(row.id)
      ? `<label class="atlas-physical-opacity"><span>Opacity</span><input type="range" min="0" max="100" step="1" value="${Math.round(record.opacity*100)}" data-physical-opacity="${esc(row.id)}" aria-label="${esc(row.label)} opacity"><output>${Math.round(record.opacity*100)}%</output></label>`
      : '';
    return `<div class="atlas-physical-row"><button type="button" class="atlas-world-option${on?' active':''}" data-physical-layer="${esc(row.id)}" aria-pressed="${on?'true':'false'}" ${current?'':'disabled'} title="${esc(row.status_note || '')}"><span>${esc(row.label)}<small>${esc(phaseLabel(record,row))}</small></span></button>${slider}</div>`;
  }).join('');
  const footer = active.size ? '<button type="button" class="atlas-world-option atlas-physical-clear" data-physical-clear><span>Clear physical<small>disable all Physical layers</small></span></button>' : '';
  pop.innerHTML = `<style>.atlas-physical-row{border-bottom:1px solid #1e2928;padding-bottom:3px}.atlas-physical-opacity{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:6px;padding:0 7px 6px;color:#9eaaa4;font-size:9px}.atlas-physical-opacity input{width:100%;min-width:80px}.atlas-physical-opacity output{min-width:30px;text-align:right}.atlas-physical-clear{margin-top:6px!important}</style><div class="atlas-world-static"><span>Physical world</span><small>${active.size ? `${active.size} active` : 'lazy · stackable'}</small></div>${rows}${footer}`;
  details.classList.toggle('active', active.size > 0);
  return true;
}

async function restoreUrlState() {
  const requested = (new URL(location.href).searchParams.get('physical') || '')
    .split(',').map(value => value.trim()).filter(Boolean);
  for (const id of requested) await activate(id, { persistState:false });
  syncCountrySurfaceTint();
  persist();
}

const ready = fetch(MANIFEST_URL, { cache:'no-cache' })
  .then(response => {
    if (!response.ok) throw new Error(`Physical manifest HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    manifest = data || { entries:[] };
    for (const row of entries()) ensureStatus(row);
    renderMenu();
    return restoreUrlState();
  })
  .catch(error => {
    console.warn('Physical World manifest unavailable:', error);
    manifest = { entries:[] };
  });

window.addEventListener('potato-atlas-physical-layer-status', event => {
  const detail = event.detail || {};
  if (!get(detail.id)) return;
  setStatus(detail.id, {
    phase:detail.phase || 'active',
    message:detail.message || '',
    provider:detail.provider || null,
    retryable:detail.retryable !== false,
  });
});
window.addEventListener('potato-atlas-module-ready', () => queueMicrotask(() => { renderMenu(); syncCountrySurfaceTint(); }));
window.addEventListener('potato-atlas-ui-layout-change', () => queueMicrotask(renderMenu));

window.__potatoAtlasPhysicalLayers = {
  ready,
  entries,
  get,
  isActive,
  activate,
  deactivate,
  toggle,
  reset,
  status,
  setOpacity,
  getOpacity,
  active:activeIds,
};
