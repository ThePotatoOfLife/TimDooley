function createTooltipService(map, options = {}) {
  if (!map?.on) throw new TypeError('tooltip service requires a MapLibre-compatible map');
  const PopupClass = options.PopupClass;
  if (typeof PopupClass !== 'function') throw new TypeError('tooltip service requires a Popup class');
  const eventTarget = options.eventTarget || (typeof window !== 'undefined' ? window : null);
  const popup = new PopupClass({
    closeButton:false,
    closeOnClick:false,
    offset:options.offset ?? 12,
    maxWidth:options.maxWidth || '300px',
  });

  let generation = 0;
  let activeOwner = null;
  let visible = false;
  let lastReason = 'init';
  let invalidations = 0;
  let staleSuppressions = 0;

  function removeVisual() {
    popup.remove?.();
    visible = false;
    activeOwner = null;
  }

  function nextGeneration(owner = null) {
    generation += 1;
    // A new logical hover invalidates the previously visible transient surface
    // immediately; async content for the new target may arrive later.
    if (visible) removeVisual();
    lastReason = owner ? `generation:${owner}` : 'generation';
    return generation;
  }

  function show(owner, lngLat, html, expectedGeneration = generation) {
    const key = String(owner || '').trim();
    if (!key) throw new TypeError('tooltip owner is required');
    if (expectedGeneration !== generation) {
      staleSuppressions += 1;
      return false;
    }
    popup.setLngLat?.(lngLat).setHTML?.(String(html ?? '')).addTo?.(map);
    activeOwner = key;
    visible = true;
    lastReason = 'show';
    return true;
  }

  function invalidate(reason = 'invalidate') {
    generation += 1;
    invalidations += 1;
    lastReason = String(reason || 'invalidate');
    removeVisual();
    return generation;
  }

  function clear(owner = null) {
    if (!visible) return false;
    if (owner != null && String(owner) !== activeOwner) return false;
    invalidate(owner ? `clear:${owner}` : 'clear');
    return true;
  }

  function state() {
    return {
      generation,
      owner:activeOwner,
      visible,
      lastReason,
      invalidations,
      staleSuppressions,
    };
  }

  for (const eventName of ['dragstart','zoomstart','rotatestart','pitchstart']) {
    map.on(eventName, () => invalidate(eventName));
  }
  eventTarget?.addEventListener?.('potato-atlas-projection-change', () => invalidate('projection-change'));
  eventTarget?.addEventListener?.('potato-atlas-style-generation', () => invalidate('style-generation'));

  return Object.freeze({ nextGeneration, show, invalidate, clear, state });
}

if (typeof window !== 'undefined') window.__potatoAtlasCreateTooltipService = createTooltipService;

export { createTooltipService };
