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

// Coordinate application surfaces before adding more optional visual layers.
// Render Stack is tiny and data-free; Physical World still keeps providers lazy.
queueMicrotask(async () => {
  await window.__potatoAtlasLoadModule?.('UI Layout', './3d-ui-layout.js');
  await window.__potatoAtlasLoadModule?.('Render Stack', './3d-render-stack.js');
  await window.__potatoAtlasLoadModule?.('Map State', './3d-map-state.js');
  await window.__potatoAtlasLoadModule?.('Places', './3d-places.js');
  await window.__potatoAtlasLoadModule?.('Physical World', './3d-physical-layers.js');
});

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
