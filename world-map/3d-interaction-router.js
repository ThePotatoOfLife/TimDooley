function createInteractionRouter(map, options = {}) {
  if (!map?.queryRenderedFeatures) throw new TypeError('interaction router requires a MapLibre-compatible map');
  const registrations = new Map();
  const eventTarget = options.eventTarget || (typeof window !== 'undefined' ? window : null);
  let orderClock = 0;
  let activeHover = null;
  let clickDispatches = 0;
  let hoverDispatches = 0;

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

  function publishState(reason) {
    if (!eventTarget?.dispatchEvent) return;
    const detail = { reason:String(reason || 'state'), diagnostics:diagnostics() };
    const event = typeof CustomEvent === 'function'
      ? new CustomEvent('potato-atlas-interaction-state', { detail })
      : { type:'potato-atlas-interaction-state', detail };
    eventTarget.dispatchEvent(event);
  }

  function register(owner, config = {}) {
    const key = String(owner || '').trim();
    if (!key) throw new TypeError('interaction registration owner is required');
    registrations.set(key, { owner:key, ...normalize(config) });
    publishState('register');
    return key;
  }

  function unregister(owner) {
    const key = String(owner || '').trim();
    if (activeHover?.owner === key) clearHover();
    const removed = registrations.delete(key);
    if (removed) publishState('unregister');
    return removed;
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
    if (kind === 'click') clickDispatches += 1;
    else if (kind === 'hover') hoverDispatches += 1;
    const winner = resolve(event.point, kind);
    if (!winner) {
      if (kind === 'hover') clearHover(event);
      publishState(`${kind}-dispatch`);
      return null;
    }
    claim(event, winner);
    if (kind === 'click') {
      winner.registration.onClick?.(event, winner.feature, winner);
      publishState('click-dispatch');
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
    publishState('hover-dispatch');
    return winner;
  }

  function clearHover(event = null) {
    if (activeHover) activeHover.winner?.registration?.onLeave?.(event, activeHover.winner.feature, activeHover.winner);
    activeHover = null;
    const canvas = map.getCanvas?.();
    if (canvas?.style) canvas.style.cursor = '';
    publishState('hover-clear');
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

  function diagnostics() {
    const rows = [...registrations.values()];
    const zoom = Number(map.getZoom?.());
    const enabledRows = rows.filter(row => row.enabled({ kind:'diagnostics', zoom }));
    return {
      registrationCount:rows.length,
      enabledCount:enabledRows.length,
      clickOwnerCount:activeRegistrations('click').length,
      hoverOwnerCount:activeRegistrations('hover').length,
      layerCount:new Set(rows.flatMap(row => row.layers)).size,
      clickDispatches,
      hoverDispatches,
      activeHoverOwner:activeHover?.owner || null,
    };
  }

  if (options.bind !== false) {
    map.on?.('click', event => dispatch('click', event));
    map.on?.('mousemove', event => dispatch('hover', event));
    map.on?.('mouseout', event => clearHover(event));
  }

  return Object.freeze({ register, unregister, resolve, dispatch, clearHover, state, diagnostics });
}

if (typeof window !== 'undefined' && window.__potatoAtlasMap) {
  const created = !window.__potatoAtlasInteraction;
  window.__potatoAtlasInteraction = window.__potatoAtlasInteraction || createInteractionRouter(window.__potatoAtlasMap);
  if (created) {
    window.dispatchEvent(new CustomEvent('potato-atlas-interaction-ready', {
      detail:{ interaction:window.__potatoAtlasInteraction },
    }));
  }
}

export { createInteractionRouter };
