// Shared panel-render lifecycle for the World Relational Atlas.
//
// This is intentionally tiny and always loaded. It owns the one compatibility
// MutationObserver needed for legacy/core panel renders without importing the
// broader progressive UI module or any map-paint side effects.

const panel = document.getElementById('panel');
let lastLifecycleKey = '';
let panelLifecycleScheduled = false;
let coreRevision = 0;
let controlPlaneReady = null;
let placesDetailScaleActive = null;
let subdivisionsScaleActive = null;

function panelLifecycleKey() {
  if (!panel) return '';
  const eyebrow = panel.querySelector(':scope > .eyebrow')?.textContent?.trim() || '';
  const heading = panel.querySelector(':scope > h1')?.textContent?.trim() || '';
  const selection = window.__potatoAtlasSelection?.current || {};
  const url = new URL(location.href);
  const code = String(selection.activeCode || selection.code || url.searchParams.get('country') || '').toUpperCase();
  const compare = url.searchParams.get('compare') || '';
  const place = url.searchParams.get('place') || '';
  const subdivision = url.searchParams.get('subdivision') || '';
  return [eyebrow, heading, code, compare, place, subdivision, coreRevision].join('|');
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

async function ensureControlPlane() {
  if (!controlPlaneReady) {
    controlPlaneReady = (async () => {
      await window.__potatoAtlasLoadModule?.('Geo Kernel', './3d-geo-kernel.js');
      await window.__potatoAtlasLoadModule?.('Scale', './3d-scale.js');
      await window.__potatoAtlasLoadModule?.('Interaction Router', './3d-interaction-router.js');
      await window.__potatoAtlasLoadModule?.('Inspector Router', './3d-inspector-router.js');
      await window.__potatoAtlasLoadModule?.('Inspector URL', './3d-inspector-url.js');
      const scale = await window.__potatoAtlasScale?.ready;
      if (!scale) throw new Error('World Map Scale runtime unavailable.');
      if (!window.__potatoAtlasInteraction) throw new Error('World Map Interaction Router unavailable.');
      if (!window.__potatoAtlasInspector) throw new Error('World Map Inspector Router unavailable.');
      return scale;
    })();
  }
  return controlPlaneReady;
}

// Coordinate application surfaces before adding more optional visual layers.
// Shared math/scale/interaction/inspector ownership loads first so later geographic
// detail modules consume one wrap policy, one camera scale, one hit-test owner and
// one semantic inspector history.
queueMicrotask(async () => {
  try {
    await ensureControlPlane();
  } catch (error) {
    console.warn('World Map control-plane foundation unavailable:', error);
  }
  await window.__potatoAtlasLoadModule?.('UI Layout', './3d-ui-layout.js');
  await window.__potatoAtlasLoadModule?.('Render Stack', './3d-render-stack.js');
  await window.__potatoAtlasLoadModule?.('Map State', './3d-map-state.js');
  const placesLoaded = await window.__potatoAtlasLoadModule?.('Places', './3d-places.js');
  if (!placesLoaded) {
    window.dispatchEvent(new CustomEvent('potato-atlas-places-ready', {
      detail:{ majorCount:0, error:'Places module unavailable', fallback:true }
    }));
  }
  await window.__potatoAtlasLoadModule?.('Search', './3d-search.js');
  await window.__potatoAtlasLoadModule?.('Physical World', './3d-physical-layers.js');
});

function selectedCountryCode(detail = null) {
  const selection = window.__potatoAtlasSelection?.current || {};
  return String(
    detail?.code || detail?.activeCode ||
    selection.activeCode || selection.code ||
    new URL(location.href).searchParams.get('country') || ''
  ).toUpperCase();
}

async function maybeLoadSelectedPlaces(detail = null) {
  const map = window.__potatoAtlasMap;
  const api = window.__potatoAtlasPlaces;
  if (!map || !api?.loadCountry) return false;
  const code = selectedCountryCode(detail);
  if (!/^[A-Z]{3}$/.test(code)) return false;
  const requested = new URL(location.href).searchParams.has('place');
  if (!requested) {
    let scale;
    try { scale = await ensureControlPlane(); }
    catch { return false; }
    placesDetailScaleActive = scale.capabilityActive('places-detail', 'load', map.getZoom(), placesDetailScaleActive);
    if (!placesDetailScaleActive) return false;
  }
  try {
    await api.loadCountry(code);
    return true;
  } catch (error) {
    console.warn(`Places detail unavailable for ${code}:`, error);
    return false;
  }
}

// Country-detail places stay dormant at world scale. Once a country is the active
// browsing context and the shared scale contract admits detail, load one partition.
window.addEventListener('potato-atlas-country-card-rendered', event => {
  queueMicrotask(() => maybeLoadSelectedPlaces(event?.detail));
});
queueMicrotask(() => {
  const map = window.__potatoAtlasMap;
  maybeLoadSelectedPlaces();
  map?.on('moveend', maybeLoadSelectedPlaces);
});

// Administrative detail remains code- and data-dormant at world scale. The shared
// scale contract owns promotion; deep links bypass the camera threshold.
async function maybeLoadSubdivisions() {
  const map = window.__potatoAtlasMap;
  if (!map) return;
  const requested = new URL(location.href).searchParams.has('subdivision');
  if (!requested) {
    let scale;
    try { scale = await ensureControlPlane(); }
    catch { return; }
    subdivisionsScaleActive = scale.capabilityActive('subdivisions', 'load', map.getZoom(), subdivisionsScaleActive);
    if (!subdivisionsScaleActive) return;
  }
  map.off('zoomend', maybeLoadSubdivisions);
  window.__potatoAtlasLoadModule?.('Subdivisions', './3d-subdivisions.js');
}
queueMicrotask(() => {
  const map = window.__potatoAtlasMap;
  maybeLoadSubdivisions();
  map?.on('zoomend', maybeLoadSubdivisions);
});