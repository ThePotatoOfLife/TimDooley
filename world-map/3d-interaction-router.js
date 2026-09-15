function createInteractionRouter(map, options = {}) {
  if (!map?.queryRenderedFeatures) throw new TypeError('interaction router requires a MapLibre-compatible map');
  const registrations = new Map();
  let orderClock = 0;
  let activeHover = null;

  function normalize(config = {}) {
    const layers = [...new Set((config.layers || []).map(String).filter(Boolean))];
    if (!layers.length) throw new TypeError('interaction registration requires at least one layer');
    return {
      layers,
      objectType:String(config.objectType || 'map-feature'),
      clickPriority:Number(config.clickPriority) || 0,
      hoverPriority:Number(config.hoverPriority ?? config.clickPriority) || 0,
      cursor:String(config.cursor || 'pointer'),
      enabled:typeof config.enabled === 'function' ? config.enabled : () => config.enabled !== false,
      onClick:typeof config.onClick === 'function' ? config.onClick : null,
      onHover:typeof config.onHover === 'function' ? config.onHover : null,
      onLeave:typeof config.onLeave === 'function' ? config.onLeave : null,
      claimOverlay:config.claimOverlay !== false,
      order:++orderClock,
    };
  }

  function register(owner, config = {}) {
    const key = String(owner || '').trim();
    if (!key) throw new TypeError('interaction registration owner is required');
    registrations.set(key, { owner:key, ...normalize(config) });
    return key;
  }

  function unregister(owner) {
    const key = String(owner || '').trim();
    if (activeHover?.owner === key) clearHover();
    return registrations.delete(key);
  }

  function activeRegistrations(kind) {
    const priorityKey = kind === 'hover' ? 'hoverPriority' : 'clickPriority';
    return [...registrations.values()]
      .filter(row => row.enabled({ kind, zoom:Number(map.getZoom?.()) }))
      .filter(row => kind !== 'hover' || row.onHover || row.cursor)
      .filter(row => kind !== 'click' || row.onClick)
      .map(row => ({ ...row, priority:row[priorityKey] }));
  }

  function resolve(point, kind = 'click') {
    if (!point) return null;
    const rows = activeRegistrations(kind);
    if (!rows.length) return null;
    const layerIds = [...new Set(rows.flatMap(row => row.layers).filter(layerId => map.getLayer?.(layerId)))];
    if (!layerIds.length) return null;
    const features = map.queryRenderedFeatures(point, { layers:layerIds }) || [];
    if (!features.length) return null;
    const registrationsByLayer = new Map();
    for (const row of rows) {
      for (const layerId of row.layers) {
        if (!registrationsByLayer.has(layerId)) registrationsByLayer.set(layerId, []);
        registrationsByLayer.get(layerId).push(row);
      }
    }
    const candidates = [];
    for (const feature of features) {
      const layerId = feature?.layer?.id;
      for (const row of registrationsByLayer.get(layerId) || []) {
        candidates.push({
          owner:row.owner,
          objectType:row.objectType,
          feature,
          layerId,
          priority:row.priority,
          registration:row,
        });
      }
    }
    candidates.sort((a, b) => b.priority - a.priority || a.registration.order - b.registration.order || a.owner.localeCompare(b.owner));
    return candidates[0] || null;
  }

  function claim(event, winner) {
    if (winner?.registration?.claimOverlay && event?.originalEvent) {
      event.originalEvent.__potatoAtlasOverlayHandled = true;
    }
  }

  function dispatch(kind, event = {}) {
    const winner = resolve(event.point, kind);
    if (!winner) {
      if (kind === 'hover') clearHover(event);
      return null;
    }
    claim(event, winner);
    if (kind === 'click') {
      winner.registration.onClick?.(event, winner.feature, winner);
      return winner;
    }
    const featureId = winner.feature?.id ?? winner.feature?.properties?.id ?? '';
    const key = `${winner.owner}|${winner.layerId}|${featureId}`;
    if (activeHover?.key !== key) {
      clearHover(event);
      activeHover = { key, owner:winner.owner, winner };
    }
    const canvas = map.getCanvas?.();
    if (canvas?.style) canvas.style.cursor = winner.registration.cursor;
    winner.registration.onHover?.(event, winner.feature, winner);
    return winner;
  }

  function clearHover(event = null) {
    if (activeHover) activeHover.winner?.registration?.onLeave?.(event, activeHover.winner.feature, activeHover.winner);
    activeHover = null;
    const canvas = map.getCanvas?.();
    if (canvas?.style) canvas.style.cursor = '';
  }

  function state() {
    return [...registrations.values()]
      .map(row => ({
        owner:row.owner,
        objectType:row.objectType,
        layers:[...row.layers],
        clickPriority:row.clickPriority,
        hoverPriority:row.hoverPriority,
        enabled:Boolean(row.enabled({ kind:'state', zoom:Number(map.getZoom?.()) })),
      }))
      .sort((a, b) => b.clickPriority - a.clickPriority || a.owner.localeCompare(b.owner));
  }

  if (options.bind !== false) {
    map.on?.('click', event => dispatch('click', event));
    map.on?.('mousemove', event => dispatch('hover', event));
    map.on?.('mouseout', event => clearHover(event));
  }

  return Object.freeze({ register, unregister, resolve, dispatch, clearHover, state });
}

if (typeof window !== 'undefined' && window.__potatoAtlasMap) {
  window.__potatoAtlasInteraction = window.__potatoAtlasInteraction || createInteractionRouter(window.__potatoAtlasMap);
}

export { createInteractionRouter };
