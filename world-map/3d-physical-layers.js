// Lazy Physical World runtime + first-class World Bar menu.
// Manifest metadata loads with the core; expensive providers/modules do not.
// Compatibility map: physical.terrain -> __potatoAtlasTerrain.
// Current water map: physical.water.base -> __potatoAtlasPhysicalWater.

const MANIFEST_URL = '../data/world-map-physical-layers.json';
const active = new Set();
let manifest = { entries:[] };
let loading = new Map();

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function entries() { return [...(manifest.entries || [])]; }
function get(id) { return entries().find(row => row.id === id) || null; }
function isActive(id) { return active.has(id); }
function activeIds() { return [...active]; }
function controller(row) {
  return row?.controller ? window[row.controller] : null;
}

function persist() {
  const url = new URL(location.href);
  const values = activeIds().sort();
  if (values.length) url.searchParams.set('physical', values.join(','));
  else url.searchParams.delete('physical');
  history.replaceState({}, '', url);
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

async function activate(id, { persistState = true } = {}) {
  const row = get(id);
  if (!row || row.availability !== 'current') return false;
  if (active.has(id)) return true;
  try {
    if (row.load_policy !== 'on_demand') throw new Error(`Unsupported physical load policy: ${row.load_policy}`);
    if (row.kind !== 'module') throw new Error(`${row.label} provider is not activated yet`);
    const ok = await ensureModule(row);
    if (!ok) throw new Error(`Could not load ${row.label}`);
    const api = controller(row);
    if (!api?.enable) throw new Error(`${row.label} has no controller enable() API`);
    await api.enable();
    active.add(id);
    if (persistState) persist();
    emit('activate', id);
    return true;
  } catch (error) {
    console.warn(`Physical layer unavailable: ${id}`, error);
    emit('error', id);
    return false;
  }
}

async function deactivate(id, { persistState = true } = {}) {
  if (!active.has(id)) return true;
  const row = get(id);
  const api = controller(row);
  try { await api?.disable?.(); } catch (error) { console.warn(`Physical layer disable failed: ${id}`, error); }
  active.delete(id);
  if (persistState) persist();
  emit('deactivate', id);
  return true;
}

async function toggle(id) {
  return isActive(id) ? deactivate(id) : activate(id);
}

function menuHost() {
  return document.getElementById('atlasWorldBar');
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
      const button = event.target.closest('[data-physical-layer]');
      if (!button || button.disabled) return;
      await toggle(button.dataset.physicalLayer);
    });
  }
  const pop = details.querySelector('.atlas-world-menu-pop');
  if (!pop) return false;
  pop.innerHTML = `<div class="atlas-world-static"><span>Physical world</span><small>lazy · stackable</small></div>${entries().map(row => {
    const current = row.availability === 'current';
    const on = isActive(row.id);
    return `<button type="button" class="atlas-world-option${on?' active':''}" data-physical-layer="${esc(row.id)}" aria-pressed="${on?'true':'false'}" ${current?'':'disabled'} title="${esc(row.status_note || '')}"><span>${esc(row.label)}<small>${current ? esc(row.load_policy || '') : 'planned'}</small></span></button>`;
  }).join('')}`;
  details.classList.toggle('active', active.size > 0);
  return true;
}

async function restoreUrlState() {
  const requested = (new URL(location.href).searchParams.get('physical') || '')
    .split(',').map(value => value.trim()).filter(Boolean);
  for (const id of requested) await activate(id, { persistState:false });
  if (requested.length) persist();
}

const ready = fetch(MANIFEST_URL, { cache:'no-cache' })
  .then(response => {
    if (!response.ok) throw new Error(`Physical manifest HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    manifest = data || { entries:[] };
    renderMenu();
    return restoreUrlState();
  })
  .catch(error => {
    console.warn('Physical World manifest unavailable:', error);
    manifest = { entries:[] };
  });

window.addEventListener('potato-atlas-module-ready', () => queueMicrotask(renderMenu));
window.addEventListener('potato-atlas-ui-layout-change', () => queueMicrotask(renderMenu));

window.__potatoAtlasPhysicalLayers = {
  ready,
  entries,
  get,
  isActive,
  activate,
  deactivate,
  toggle,
  active:activeIds,
};
