// Canonical World Map URL-state mutation owner.
// Domain modules claim their parameter family, then patch only those parameters.
// Reading location.href remains public; direct history.replaceState ownership does not.

const claims = new Map();
const ownerParams = new Map();
let writeCount = 0;

function normalizeOwner(value) {
  const owner = String(value || '').trim();
  if (!owner) throw new TypeError('URL state owner is required');
  return owner;
}
function normalizeParams(values = []) {
  return [...new Set((values || []).map(value => String(value || '').trim()).filter(Boolean))].sort();
}
function claim(ownerValue, params = []) {
  const owner = normalizeOwner(ownerValue);
  const normalized = normalizeParams(params);
  for (const param of normalized) {
    const existing = claims.get(param);
    if (existing && existing !== owner) {
      throw new Error(`URL parameter "${param}" already belongs to ${existing}; ${owner} cannot claim it.`);
    }
  }
  const set = ownerParams.get(owner) || new Set();
  for (const param of normalized) {
    claims.set(param, owner);
    set.add(param);
  }
  ownerParams.set(owner, set);
  publish('claim', owner, normalized);
  return normalized;
}
function assertOwned(owner, params) {
  for (const param of params) {
    const existing = claims.get(param);
    if (existing !== owner) {
      throw new Error(`URL parameter "${param}" is not owned by ${owner}; current owner: ${existing || 'unclaimed'}.`);
    }
  }
}
function patch(ownerValue, change = {}) {
  const owner = normalizeOwner(ownerValue);
  const setValues = change.set && typeof change.set === 'object' ? change.set : {};
  const remove = normalizeParams(change.remove || []);
  const touched = normalizeParams([...Object.keys(setValues), ...remove]);
  assertOwned(owner, touched);

  const url = new URL(location.href);
  for (const [param, raw] of Object.entries(setValues)) {
    if (raw == null || raw === '') url.searchParams.delete(param);
    else url.searchParams.set(param, String(raw));
  }
  for (const param of remove) url.searchParams.delete(param);

  history.replaceState({}, '', url);
  writeCount += 1;
  publish('patch', owner, touched);
  return url;
}
function read(param) {
  return new URL(location.href).searchParams.get(String(param || ''));
}
function snapshot() {
  return {
    writeCount,
    claims:Object.fromEntries([...claims.entries()].sort(([a],[b]) => a.localeCompare(b))),
    owners:Object.fromEntries([...ownerParams.entries()].sort(([a],[b]) => a.localeCompare(b)).map(([owner, params]) => [owner, [...params].sort()])),
  };
}
function publish(reason, owner, params) {
  if (typeof window === 'undefined' || !window.dispatchEvent) return;
  const detail = { reason, owner:owner || null, params:params || [], diagnostics:snapshot() };
  const event = typeof CustomEvent === 'function'
    ? new CustomEvent('potato-atlas-url-state', { detail })
    : { type:'potato-atlas-url-state', detail };
  window.dispatchEvent(event);
}

const api = Object.freeze({ claim, patch, read, snapshot });
if (typeof window !== 'undefined') {
  window.__potatoAtlasUrlState = window.__potatoAtlasUrlState || api;
  window.dispatchEvent?.(new CustomEvent('potato-atlas-url-state-ready', { detail:{ urlState:window.__potatoAtlasUrlState } }));
}

export { claim, patch, read, snapshot };
