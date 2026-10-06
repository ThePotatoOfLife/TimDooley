const INSPECTOR_URL_OWNER = 'selection-inspector';
const INSPECTOR_URL_PARAMS = Object.freeze(['inspect','country','subdivision','place']);
const INSPECTOR_TYPES = Object.freeze(['country','subdivision','place','evidence','evidence-record','project-case','spatial-overlay','axis','axis-depth']);
const TYPE_RANK = new Map(INSPECTOR_TYPES.map((type, index) => [type, index]));

function normalizePathNodes(nodes = []) {
  if (!Array.isArray(nodes) || !nodes.length) return [];
  const normalized = [];
  let previousRank = -1;
  for (const raw of nodes) {
    const type = String(raw?.type || '').trim();
    const id = String(raw?.id || '').trim();
    const rank = TYPE_RANK.get(type);
    if (!Number.isInteger(rank) || !id || rank <= previousRank) return [];
    const parent = normalized.length ? { type:normalized.at(-1).type, id:normalized.at(-1).id } : null;
    normalized.push({ type, id, parent });
    previousRank = rank;
  }
  return normalized;
}
function encodeInspectorPath(stack = []) {
  const nodes = normalizePathNodes(stack);
  if (!nodes.length) return '';
  return nodes.map(node => `${node.type}:${encodeURIComponent(node.id)}`).join('/');
}
function decodeInspectorPath(value = '') {
  const text = String(value || '').trim();
  if (!text) return [];
  const nodes = [];
  try {
    for (const segment of text.split('/')) {
      const split = segment.indexOf(':');
      if (split <= 0) return [];
      nodes.push({ type:segment.slice(0, split), id:decodeURIComponent(segment.slice(split + 1)) });
    }
  } catch { return []; }
  return normalizePathNodes(nodes);
}
function deriveInspectorPathFromUrl(urlLike) {
  const url = urlLike instanceof URL ? new URL(urlLike.href) : new URL(String(urlLike));
  const explicit = decodeInspectorPath(url.searchParams.get('inspect') || '');
  if (explicit.length) return encodeInspectorPath(explicit);
  const nodes = [];
  const country = String(url.searchParams.get('country') || '').trim().toUpperCase();
  const subdivision = String(url.searchParams.get('subdivision') || '').trim();
  const place = String(url.searchParams.get('place') || '').trim();
  if (country) nodes.push({type:'country', id:country});
  if (subdivision) nodes.push({type:'subdivision', id:subdivision});
  if (place) nodes.push({type:'place', id:place});
  return encodeInspectorPath(nodes);
}
function mirrorLegacyParams(url, nodes) {
  const byType = new Map(nodes.map(node => [node.type, node.id]));
  const country = byType.get('country');
  const subdivision = byType.get('subdivision');
  const place = byType.get('place');
  if (country) url.searchParams.set('country', country);
  if (subdivision) url.searchParams.set('subdivision', subdivision);
  else if (nodes.some(node => node.type === 'country')) url.searchParams.delete('subdivision');
  if (place) url.searchParams.set('place', place);
  else if (nodes.some(node => node.type === 'country' || node.type === 'subdivision')) url.searchParams.delete('place');
  return url;
}
function replaceCanonical(url) {
  const state = typeof window !== 'undefined' ? window.__potatoAtlasUrlState : null;
  if (!state?.claim || !state?.patch) throw new Error('Inspector URL bridge requires canonical URL State owner');
  state.claim(INSPECTOR_URL_OWNER, INSPECTOR_URL_PARAMS);
  const set = Object.fromEntries(INSPECTOR_URL_PARAMS.map(param => [param, url.searchParams.get(param)]));
  state.patch(INSPECTOR_URL_OWNER, { set });
}
function createInspectorUrlBridge(options = {}) {
  const getHref = typeof options.getHref === 'function' ? options.getHref : () => location.href;
  const replace = typeof options.replace === 'function' ? options.replace : replaceCanonical;
  const eventTarget = options.eventTarget || (typeof window !== 'undefined' ? window : null);
  let path = '';
  function commit(url, nextPath) { path = nextPath || ''; replace(url); return path; }
  function hydrate() {
    const url = new URL(getHref());
    const explicit = decodeInspectorPath(url.searchParams.get('inspect') || '');
    if (explicit.length) {
      const canonical = encodeInspectorPath(explicit);
      url.searchParams.set('inspect', canonical);
      mirrorLegacyParams(url, explicit);
      return commit(url, canonical);
    }
    const derived = deriveInspectorPathFromUrl(url);
    if (derived) { url.searchParams.set('inspect', derived); return commit(url, derived); }
    path = '';
    return path;
  }
  function syncFromInspector(event) {
    const stack = event?.detail?.stack;
    if (!Array.isArray(stack)) return false;
    const url = new URL(getHref());
    const nextPath = encodeInspectorPath(stack);
    if (!nextPath) { url.searchParams.delete('inspect'); commit(url, ''); return true; }
    const nodes = decodeInspectorPath(nextPath);
    url.searchParams.set('inspect', nextPath);
    mirrorLegacyParams(url, nodes);
    commit(url, nextPath);
    return true;
  }
  function state() { return { path, nodes:decodeInspectorPath(path) }; }
  eventTarget?.addEventListener?.('potato-atlas-inspector-change', syncFromInspector);
  hydrate();
  function destroy() { eventTarget?.removeEventListener?.('potato-atlas-inspector-change', syncFromInspector); }
  return Object.freeze({ hydrate, syncFromInspector, state, destroy });
}

if (typeof window !== 'undefined' && !window.__potatoAtlasInspectorUrl) {
  window.__potatoAtlasInspectorUrl = createInspectorUrlBridge();
}

export { encodeInspectorPath, decodeInspectorPath, deriveInspectorPathFromUrl, createInspectorUrlBridge };
