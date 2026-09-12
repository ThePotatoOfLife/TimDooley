// Registry-driven analytical state for the World Map.
// Canonical values stay in their source files; this module owns only presentation
// metadata and the user's active analytical layer set.

const REGISTRY_URL = '../data/world-map-layer-registry.json';
const ACTIVE_PARAM = 'layers';

let registry = null;
let loadError = null;
const byId = new Map();
const byFamily = new Map();
const activeIds = new Set();

function normalizeEntries(data) {
  byId.clear();
  byFamily.clear();
  for (const family of data?.families || []) byFamily.set(family.id, { ...family });
  for (const entry of data?.entries || []) {
    const frozen = Object.freeze({ ...entry });
    byId.set(frozen.id, frozen);
    if (!byFamily.has(frozen.family)) byFamily.set(frozen.family, { id: frozen.family, label: frozen.family });
  }
}

function validAvailable(id) {
  const entry = byId.get(id);
  return Boolean(entry && entry.availability === 'current');
}

function persist() {
  const url = new URL(location.href);
  const ids = [...activeIds].filter(validAvailable).sort();
  if (ids.length) url.searchParams.set(ACTIVE_PARAM, ids.join(','));
  else url.searchParams.delete(ACTIVE_PARAM);
  url.searchParams.delete('lens');
  url.searchParams.delete('lensOption');
  history.replaceState({}, '', url);
}

function emit(reason = 'change') {
  const detail = { reason, active: [...activeIds], entries: [...activeIds].map(id => byId.get(id)).filter(Boolean) };
  window.dispatchEvent(new CustomEvent('potato-atlas-layer-change', { detail }));
}

function enforceChannelRules(entry) {
  if (entry.kind !== 'scalar') return;
  for (const id of [...activeIds]) {
    const current = byId.get(id);
    if (current?.kind === 'scalar' && id !== entry.id) activeIds.delete(id);
  }
}

function activate(id, { silent = false } = {}) {
  const entry = byId.get(id);
  if (!entry || entry.availability !== 'current') return false;
  enforceChannelRules(entry);
  activeIds.add(id);
  if (!silent) {
    persist();
    emit('activate');
  }
  return true;
}

function deactivate(id, { silent = false } = {}) {
  const changed = activeIds.delete(id);
  if (changed && !silent) {
    persist();
    emit('deactivate');
  }
  return changed;
}

function toggle(id) {
  return activeIds.has(id) ? deactivate(id) : activate(id);
}

function reset({ silent = false } = {}) {
  if (!activeIds.size) return;
  activeIds.clear();
  if (!silent) {
    persist();
    emit('reset');
  }
}

function entries(family = null, { availableOnly = false, ordinaryOnly = false } = {}) {
  let rows = [...byId.values()];
  if (family) rows = rows.filter(entry => entry.family === family);
  if (availableOnly) rows = rows.filter(entry => entry.availability === 'current');
  if (ordinaryOnly) rows = rows.filter(entry => entry.map_priority === 'ordinary');
  return rows;
}

function family(id) {
  const entry = byId.get(id);
  return entry ? byFamily.get(entry.family) || null : byFamily.get(id) || null;
}

function restoreFromUrl() {
  const params = new URL(location.href).searchParams;
  const requested = (params.get(ACTIVE_PARAM) || '').split(',').map(value => value.trim()).filter(Boolean);
  for (const id of requested) activate(id, { silent: true });
  if (!requested.length) {
    const lens = params.get('lens');
    const option = params.get('lensOption');
    if (lens === 'alignment') activate('axis.north', { silent: true });
    if (lens === 'alliances' && option) activate(`group.${option}`, { silent: true });
    if (lens === 'religion' && option && option !== 'dominant') activate(`religion.${option === 'other_religions' ? 'other' : option}`, { silent: true });
    if (lens === 'metric' && option) activate(`stat.${option}`, { silent: true });
  }
  persist();
}

async function loadRegistry() {
  try {
    const response = await fetch(REGISTRY_URL, { cache: 'no-cache' });
    if (!response.ok) throw new Error(`${response.status} ${REGISTRY_URL}`);
    registry = await response.json();
    normalizeEntries(registry);
    restoreFromUrl();
    emit('ready');
    return registry;
  } catch (error) {
    loadError = error;
    console.warn('World Map layer registry unavailable:', error);
    window.dispatchEvent(new CustomEvent('potato-atlas-layer-registry-error', { detail: { message: error?.message || String(error) } }));
    return null;
  }
}

const ready = loadRegistry();

window.__potatoAtlasLayers = {
  ready,
  get registry() { return registry; },
  get error() { return loadError; },
  get(id) { return byId.get(id) || null; },
  family,
  entries,
  activate,
  deactivate,
  toggle,
  active() { return [...activeIds]; },
  isActive(id) { return activeIds.has(id); },
  reset,
};

export { ready };
