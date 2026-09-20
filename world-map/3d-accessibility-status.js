// Read-only accessible summary of the current World Map state.
// Consumes canonical controllers/events; never mutates map state.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Accessible map status requires the core map.');

const STATUS_ID = 'atlasAccessibleStatus';
let scheduled = false;
let lastText = '';

function ensureStatusNode() {
  let node = document.getElementById(STATUS_ID);
  if (node) return node;
  node = document.createElement('div');
  node.id = STATUS_ID;
  node.setAttribute('role', 'status');
  node.setAttribute('aria-live', 'polite');
  node.setAttribute('aria-atomic', 'true');
  node.className = 'atlas-sr-only';
  document.querySelector('.mapwrap')?.appendChild(node);
  if (!document.getElementById('atlasAccessibleStatusStyle')) {
    const style = document.createElement('style');
    style.id = 'atlasAccessibleStatusStyle';
    style.textContent = '.atlas-sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}';
    document.head.appendChild(style);
  }
  return node;
}

function labels(ids, api) {
  return (ids || []).map(id => api?.get?.(id)?.label || id).filter(Boolean);
}
function timeLabel(state) {
  if (!state || state.mode === 'current') return 'Current';
  if (state.label) return state.label;
  if (state.mode === 'as_of') return `As of ${state.time || 'unknown date'}`;
  return `${state.time || 'unknown date'} to ${state.time2 || 'unknown date'}`;
}
function projectionLabel() {
  const mode = window.__potatoAtlasProjection?.get?.() || new URL(location.href).searchParams.get('projection') || 'flat';
  return mode === 'globe' ? 'Globe' : 'Flat';
}
function scaleLabel() {
  const runtime = window.__potatoAtlasScale;
  const zoom = Number(map.getZoom?.());
  try {
    const scale = runtime?.bandForZoom ? runtime : null;
    if (scale && Number.isFinite(zoom)) return scale.bandForZoom(zoom);
  } catch {}
  return Number.isFinite(zoom) ? `zoom ${zoom.toFixed(1)}` : 'unknown scale';
}
function selectionLabel() {
  const selection = window.__potatoAtlasSelection;
  const code = selection?.current?.activeCode || selection?.current?.code || '';
  if (!code) return 'none';
  return selection?.countryName?.(code) || code;
}
function summary() {
  const layers = window.__potatoAtlasLayers;
  const physical = window.__potatoAtlasPhysicalLayers;
  const spatial = window.__potatoAtlasSpatialOverlays;
  const evidence = window.__potatoAtlasEvidenceLayers;
  const view = window.__potatoAtlasActiveView?.current || {};
  const analytical = labels(layers?.active?.() || [], layers);
  const physicalLabels = labels(physical?.active?.() || [], physical);
  const geographyLabels = labels(spatial?.active?.() || [], spatial);
  const evidenceLabels = labels(evidence?.active?.() || [], evidence);
  const relationMode = view.relationMode || window.__potatoAtlasSelection?.getRelationMode?.() || 'all';
  const currentTime = view.timeState || window.__potatoAtlasTime?.getState?.() || null;
  const parts = [
    `Selected country: ${selectionLabel()}`,
    `Analytical layers: ${analytical.length ? analytical.join(', ') : 'none'}`,
    `Physical layers: ${physicalLabels.length ? physicalLabels.join(', ') : 'none'}`,
    `Geography overlays: ${geographyLabels.length ? geographyLabels.join(', ') : 'none'}`,
    `Evidence layers: ${evidenceLabels.length ? evidenceLabels.join(', ') : 'none'}`,
    `Relations: ${relationMode}`,
    `Projection: ${projectionLabel()}`,
    `Time: ${timeLabel(currentTime)}`,
    `Scale: ${scaleLabel()}`,
  ];
  return `Map state. ${parts.join('. ')}.`;
}
function announce() {
  scheduled = false;
  const node = ensureStatusNode();
  const text = summary();
  if (text === lastText) return text;
  lastText = text;
  node.textContent = text;
  return text;
}
function schedule() {
  if (scheduled) return;
  scheduled = true;
  queueMicrotask(announce);
}

for (const eventName of [
  'potato-atlas-active-view-change',
  'potato-atlas-working-selection-change',
  'potato-atlas-relation-mode-change',
  'potato-atlas-physical-change',
  'potato-atlas-spatial-overlay-change',
  'potato-atlas-evidence-layer-change',
  'potato-atlas-projection-change',
  'atlas-time-change',
  'potato-atlas-map-state-reset',
  'potato-atlas-scale-ready',
]) window.addEventListener(eventName, schedule);
map.on?.('zoomend', schedule);

ensureStatusNode();
queueMicrotask(announce);

window.__potatoAtlasAccessibilityStatus = Object.freeze({
  summary,
  announce,
  get text() { return lastText; },
});
