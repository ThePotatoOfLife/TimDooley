// Whole-map semantic state coordinator.
// Orchestrates public subsystem APIs only; camera and projection are preserved.

const map = window.__potatoAtlasMap;

function snapshot() {
  const center = map?.getCenter?.();
  return {
    camera: map ? {
      center: center ? [center.lng, center.lat] : null,
      zoom: map.getZoom?.(),
      bearing: map.getBearing?.(),
      pitch: map.getPitch?.(),
    } : null,
    projection: window.__potatoAtlasProjection?.get?.() || null,
    physical: window.__potatoAtlasPhysicalLayers?.active?.() || [],
    overlays: window.__potatoAtlasSpatialOverlays?.active?.() || [],
    selection: window.__potatoAtlasSelection?.current || null,
    time: window.__potatoAtlasTime?.getState?.() || null,
  };
}

function clearUnloadedTimeUrlState() {
  const url = new URL(location.href);
  for (const key of ['timeMode','time','time2','timeDate','timeDate2']) url.searchParams.delete(key);
  history.replaceState({}, '', url);
}

async function runStep(name, fn, cleared, failed) {
  try {
    await fn();
    cleared.push(name);
  } catch (error) {
    failed.push({ subsystem:name, message:error?.message || String(error) });
    console.warn(`Map state reset failed for ${name}:`, error);
  }
}

async function reset() {
  const before = snapshot();
  const cleared = [];
  const failed = [];

  await runStep('analytical', async () => window.__potatoAtlasCompositor?.reset?.(), cleared, failed);
  await runStep('physical', async () => window.__potatoAtlasPhysicalLayers?.reset?.(), cleared, failed);
  await runStep('geography', async () => window.__potatoAtlasSpatialOverlays?.reset?.(), cleared, failed);
  await runStep('selection', async () => window.__potatoAtlasSelection?.clearAll?.({keepView:true}), cleared, failed);
  await runStep('relations', async () => window.__potatoAtlasSelection?.setRelationMode?.('all'), cleared, failed);
  await runStep('time', async () => {
    if (window.__potatoAtlasTime?.setState) {
      window.__potatoAtlasTime.setState({mode:'current', time:'', time2:''});
    } else {
      clearUnloadedTimeUrlState();
    }
  }, cleared, failed);

  const result = {
    ok: failed.length === 0,
    cleared,
    failed,
    preserved: { camera:true, projection:true },
    before,
    after:snapshot(),
  };
  window.dispatchEvent(new CustomEvent('potato-atlas-map-state-reset', {detail:result}));
  window.__potatoAtlasUILayout?.refresh?.();
  window.__potatoAtlasActiveView?.refresh?.('map-state-reset');
  return result;
}

window.__potatoAtlasMapState = { reset, snapshot };
