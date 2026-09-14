// Shared panel-render lifecycle for the World Relational Atlas.
//
// This is intentionally tiny and always loaded. It owns the one compatibility
// MutationObserver needed for legacy/core panel renders without importing the
// broader progressive UI module or any map-paint side effects.

const panel = document.getElementById('panel');
let lastLifecycleKey = '';
let panelLifecycleScheduled = false;
let coreRevision = 0;

function panelLifecycleKey() {
  if (!panel) return '';
  const eyebrow = panel.querySelector(':scope > .eyebrow')?.textContent?.trim() || '';
  const heading = panel.querySelector(':scope > h1')?.textContent?.trim() || '';
  const selection = window.__potatoAtlasSelection?.current || {};
  const code = String(selection.activeCode || selection.code || new URL(location.href).searchParams.get('country') || '').toUpperCase();
  const compare = new URL(location.href).searchParams.get('compare') || '';
  return [eyebrow, heading, code, compare, coreRevision].join('|');
}

function containsCoreHeading(node) {
  if (!(node instanceof Element)) return false;
  return node.matches('.eyebrow,h1') || Boolean(node.querySelector?.('.eyebrow,h1'));
}

function recordsReplaceCore(records = []) {
  return records.some(record => [...record.removedNodes].some(containsCoreHeading));
}

function publishPanelLifecycle() {
  panelLifecycleScheduled = false;
  if (!panel) return;
  const key = panelLifecycleKey();
  if (!key || key === lastLifecycleKey) return;
  lastLifecycleKey = key;
  const selection = window.__potatoAtlasSelection?.current || {};
  const code = selection.activeCode || selection.code || null;
  if (window.__potatoAtlasDiagnostics) {
    window.__potatoAtlasDiagnostics.panelLifecycleRenders = (window.__potatoAtlasDiagnostics.panelLifecycleRenders || 0) + 1;
    window.__potatoAtlasDiagnostics.inspectorEnhancementPasses = (window.__potatoAtlasDiagnostics.inspectorEnhancementPasses || 0) + 1;
  }
  window.dispatchEvent(new CustomEvent('potato-atlas-panel-rendered', {
    detail:{ key, code, coreRevision }
  }));
}

function schedulePanelLifecycle(records = []) {
  if (recordsReplaceCore(records)) coreRevision += 1;
  if (panelLifecycleScheduled) return;
  panelLifecycleScheduled = true;
  queueMicrotask(publishPanelLifecycle);
}

const observer = panel && new MutationObserver(schedulePanelLifecycle);
observer?.observe(panel, { childList:true, subtree:true, characterData:true });
queueMicrotask(publishPanelLifecycle);

window.__potatoAtlasPanelLifecycle = {
  panelLifecycleKey,
  publish:publishPanelLifecycle,
  get revision() { return coreRevision; },
};

// Register the lightweight physical-context controller after the core paint.
// Elevation and hillshade tiles remain dormant until the user enables Terrain.
queueMicrotask(() => window.__potatoAtlasLoadModule?.('Physical Terrain', './3d-physical-terrain.js'));

// The search controller is small and attaches to the existing input after core
// paint. Its heavier country/subdivision/place records remain dormant until the
// user focuses or types in Search.
queueMicrotask(() => window.__potatoAtlasLoadModule?.('Unified Search', './3d-search.js'));

// Comparable country metrics remain fully dormant until a country is actually
// selected. The controller then reads one same-origin snapshot; it never calls
// World Bank directly from the browser.
let countryMetricsRequested = false;
function maybeLoadCountryMetrics(event) {
  if (countryMetricsRequested) return;
  const current = window.__potatoAtlasSelection?.current || {};
  const selected = event?.detail?.selected ?? current.selected;
  const code = String(event?.detail?.activeCode || event?.detail?.code || current.activeCode || current.code || '').toUpperCase();
  if (!selected || !/^[A-Z]{3}$/.test(code)) return;
  countryMetricsRequested = true;
  window.__potatoAtlasLoadModule?.('Country metrics', './3d-country-metrics.js');
}
window.addEventListener('potato-atlas-selection-change', maybeLoadCountryMetrics);
window.addEventListener('potato-atlas-working-selection-change', maybeLoadCountryMetrics);
queueMicrotask(() => maybeLoadCountryMetrics());

// Administrative detail remains code- and data-dormant at world scale. Load the
// subdivision controller only after regional zoom, or immediately for a deep link.
function maybeLoadSubdivisions() {
  const map = window.__potatoAtlasMap;
  if (!map) return;
  const requested = new URL(location.href).searchParams.has('subdivision');
  if (!requested && map.getZoom() < 3.4) return;
  map.off('zoomend', maybeLoadSubdivisions);
  window.__potatoAtlasLoadModule?.('Subdivisions', './3d-subdivisions.js');
}
queueMicrotask(() => {
  const map = window.__potatoAtlasMap;
  maybeLoadSubdivisions();
  map?.on('zoomend', maybeLoadSubdivisions);
});

// Places follow the same progressive-disclosure rule: remain dormant at global
// scale, then load at regional scale or immediately when a stable place deep link
// explicitly requests one.
function maybeLoadPlaces() {
  const map = window.__potatoAtlasMap;
  if (!map) return;
  const requested = new URL(location.href).searchParams.has('place');
  if (!requested && map.getZoom() < 3.2) return;
  map.off('zoomend', maybeLoadPlaces);
  window.__potatoAtlasLoadModule?.('Places', './3d-places.js');
}
queueMicrotask(() => {
  const map = window.__potatoAtlasMap;
  maybeLoadPlaces();
  map?.on('zoomend', maybeLoadPlaces);
});
