// Shared semantic z-order coordinator for optional World Map layers.
// Modules retain ownership of their sources, visibility, paint, and behavior.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Render Stack requires the core map.');

const SLOT_ORDER = Object.freeze([
  'physical-surface',
  'physical-water',
  'physical-line',
  'geography-context',
  'context-network',
  'selection-emphasis',
]);
const SLOT_SET = new Set(SLOT_ORDER);
const entries = new Map();
let scheduled = false;
let reconcileCount = 0;
let lastReason = 'init';

function normalizePriority(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
}

function sorted(slot) {
  return [...entries.values()]
    .filter(entry => entry.slot === slot && map.getLayer(entry.layerId))
    .sort((a, b) => a.priority - b.priority || a.layerId.localeCompare(b.layerId));
}

function styleOrder() {
  return map.getStyle()?.layers?.map(layer => layer.id) || [];
}

function moveRegion(layerIds, anchorId, moved) {
  if (!layerIds.length || !anchorId || !map.getLayer(anchorId)) return;
  let beforeId = anchorId;
  for (const layerId of [...layerIds].reverse()) {
    if (!map.getLayer(layerId)) continue;
    const order = styleOrder();
    const layerIndex = order.indexOf(layerId);
    const beforeIndex = order.indexOf(beforeId);
    if (layerIndex >= 0 && beforeIndex >= 0 && layerIndex + 1 === beforeIndex) {
      beforeId = layerId;
      continue;
    }
    try {
      map.moveLayer(layerId, beforeId);
      moved.push(layerId);
      beforeId = layerId;
    } catch (error) {
      console.warn(`Render Stack could not move ${layerId}:`, error);
    }
  }
}

function firstExisting(ids) {
  return ids.find(id => map.getLayer(id)) || null;
}

function reconcile(reason = 'manual') {
  const moved = [];
  const missing = [...entries.values()].filter(entry => !map.getLayer(entry.layerId)).map(entry => entry.layerId);

  // Broad physical surfaces remain below the country tint.
  moveRegion(sorted('physical-surface').map(entry => entry.layerId), firstExisting(['countries-fill', 'countries-line', 'country-hubs', 'country-labels']), moved);

  // True water surfaces deliberately sit above countries-fill so lakes and seas
  // remain legible. Physical linework and contextual overlays follow them while
  // all remain below the canonical country boundary.
  const middle = [
    ...sorted('physical-water'),
    ...sorted('physical-line'),
    ...sorted('geography-context'),
    ...sorted('context-network'),
  ].map(entry => entry.layerId);
  moveRegion(middle, firstExisting(['countries-line', 'country-hubs', 'country-labels']), moved);

  moveRegion(sorted('selection-emphasis').map(entry => entry.layerId), firstExisting(['country-hubs', 'country-labels']), moved);

  reconcileCount += 1;
  lastReason = reason;
  window.dispatchEvent(new CustomEvent('potato-atlas-render-stack-change', {
    detail:{ reason, moved, registered:entries.size, missing }
  }));
  return { reason, moved, registered:entries.size, missing };
}

function schedule(reason = 'scheduled') {
  lastReason = reason;
  if (scheduled) return;
  scheduled = true;
  queueMicrotask(() => {
    scheduled = false;
    reconcile(lastReason);
  });
}

function register(layerId, options = {}) {
  const id = String(layerId || '').trim();
  const slot = String(options.slot || '').trim();
  if (!id || !SLOT_SET.has(slot)) {
    console.warn('Render Stack rejected invalid registration:', { layerId, slot });
    return false;
  }
  entries.set(id, {
    layerId:id,
    slot,
    priority:normalizePriority(options.priority),
    owner:String(options.owner || ''),
  });
  schedule('register');
  return true;
}

function unregister(layerId) {
  const removed = entries.delete(String(layerId || ''));
  if (removed) schedule('unregister');
  return removed;
}

function state() {
  return {
    entries:[...entries.values()].map(entry => ({...entry, exists:Boolean(map.getLayer(entry.layerId))})),
    lastReason,
    reconcileCount,
  };
}

function slotOrder() { return [...SLOT_ORDER]; }

map.on('styledata', () => schedule('styledata'));
window.addEventListener('potato-atlas-module-ready', () => schedule('module-ready'));

window.__potatoAtlasRenderStack = { register, unregister, reconcile, state, slotOrder };
