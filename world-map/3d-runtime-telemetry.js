function countTypes(rows = []) {
  const counts = new Map();
  for (const row of rows) {
    const type = String(row?.type || 'unknown');
    counts.set(type, (counts.get(type) || 0) + 1);
  }
  return Object.fromEntries([...counts.entries()].sort(([a], [b]) => a.localeCompare(b)));
}

function createRuntimeTelemetry(map, options = {}) {
  if (!map?.getStyle) throw new TypeError('runtime telemetry requires a MapLibre-compatible map');

  const publish = typeof options.publish === 'function'
    ? options.publish
    : snapshot => {
        if (typeof window !== 'undefined' && window.__potatoAtlasDiagnostics) {
          window.__potatoAtlasDiagnostics.runtime = snapshot;
        }
      };
  const getInteraction = typeof options.getInteraction === 'function'
    ? options.getInteraction
    : () => options.interaction;
  const getStyleLifecycle = typeof options.getStyleLifecycle === 'function'
    ? options.getStyleLifecycle
    : () => options.styleLifecycle;

  const listeners = [];
  let sampleCount = 0;
  let current = null;

  function snapshot(reason = 'manual') {
    const style = map.getStyle?.() || {};
    const sourcesObject = style.sources || {};
    const sources = Object.values(sourcesObject);
    const layers = Array.isArray(style.layers) ? style.layers : [];
    const visibleLayers = layers.filter(layer => layer?.layout?.visibility !== 'none');
    return {
      sourceCount:Object.keys(sourcesObject).length,
      layerCount:layers.length,
      visibleLayerCount:visibleLayers.length,
      sourceTypes:countTypes(sources),
      layerTypes:countTypes(layers),
      interaction:getInteraction()?.diagnostics?.() || null,
      style:getStyleLifecycle()?.state?.() || null,
      sampleCount:++sampleCount,
      reason:String(reason || 'manual'),
    };
  }

  function refresh(reason = 'manual') {
    current = snapshot(reason);
    publish(current);
    return current;
  }

  function state() {
    return current;
  }

  function bindEvent(name, reason) {
    if (typeof window === 'undefined') return;
    const handler = () => refresh(reason);
    window.addEventListener(name, handler);
    listeners.push([name, handler]);
  }

  function destroy() {
    if (typeof window !== 'undefined') {
      for (const [name, handler] of listeners) window.removeEventListener(name, handler);
    }
    listeners.length = 0;
  }

  if (options.bind !== false) {
    bindEvent('potato-atlas-module-ready', 'module-ready');
    bindEvent('potato-atlas-style-generation', 'style-generation');
    bindEvent('potato-atlas-ui-layout-change', 'ui-layout');
  }

  refresh('init');
  return Object.freeze({ refresh, state, destroy });
}

if (typeof window !== 'undefined') {
  const map = window.__potatoAtlasMap;
  if (map && !window.__potatoAtlasRuntimeTelemetry) {
    window.__potatoAtlasRuntimeTelemetry = createRuntimeTelemetry(map, {
      getInteraction:() => window.__potatoAtlasInteraction,
      getStyleLifecycle:() => window.__potatoAtlasStyleLifecycle,
    });
  }
}

export { createRuntimeTelemetry };
