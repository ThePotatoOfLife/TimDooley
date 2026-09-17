// Whole-map semantic state coordinator.
// Orchestrates public subsystem APIs only; camera and projection are preserved.

const map = window.__potatoAtlasMap;

function snapshot() {
  const center = map?.getCenter?.();
  const url = new URL(location.href);
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
    places: window.__potatoAtlasPlaces?.current?.()?.properties?.id || url.searchParams.get('place') || null,
    subdivision: window.__potatoAtlasSubdivisions?.selected || url.searchParams.get('subdivision') || null,
    selection: window.__potatoAtlasSelection?.current || null,
    time: window.__potatoAtlasTime?.getState?.() || null,
    investigation: window.__potatoAtlasInvestigationSurface?.current || null,
    pinnedContextExpanded: window.__potatoAtlasPinnedContext?.expanded === true,
    contextVisibility: window.__potatoAtlasContextVisibility?.current || null,
  };
}

function clearUrlState(keys) {
  const url = new URL(location.href);
  let changed = false;
  for (const key of keys) {
    if (!url.searchParams.has(key)) continue;
    url.searchParams.delete(key);
    changed = true;
  }
  if (changed) history.replaceState({}, '', url);
}

function clearUnloadedTimeUrlState() {
  clearUrlState(['timeMode','time','time2','timeDate','timeDate2']);
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

  await runStep('investigation', async () => window.__potatoAtlasInvestigationSurface?.closeActive?.('map-state-reset'), cleared, failed);
  await runStep('pinned-context', async () => window.__potatoAtlasPinnedContext?.collapse?.(), cleared, failed);
  await runStep('analytical', async () => window.__potatoAtlasCompositor?.reset?.(), cleared, failed);
  await runStep('physical', async () => window.__potatoAtlasPhysicalLayers?.reset?.(), cleared, failed);
  await runStep('geography', async () => window.__potatoAtlasSpatialOverlays?.reset?.(), cleared, failed);
  await runStep('places', async () => {
    if (window.__potatoAtlasPlaces?.clear) window.__potatoAtlasPlaces.clear();
    else clearUrlState(['place']);
  }, cleared, failed);
  await runStep('subdivision', async () => {
    if (window.__potatoAtlasSubdivisions?.clear) window.__potatoAtlasSubdivisions.clear();
    else clearUrlState(['subdivision']);
  }, cleared, failed);
  await runStep('selection', async () => window.__potatoAtlasSelection?.clearAll?.({keepView:true}), cleared, failed);
  await runStep('relations', async () => window.__potatoAtlasSelection?.setRelationMode?.('all'), cleared, failed);
  await runStep('time', async () => {
    if (window.__potatoAtlasTime?.setState) {
      window.__potatoAtlasTime.setState({mode:'current', time:'', time2:''});
    } else {
      clearUnloadedTimeUrlState();
    }
  }, cleared, failed);

  await window.__potatoAtlasContextVisibility?.refresh?.('map-state-reset');
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

// Capture the existing top-bar reset before the legacy compositor-only click handler.
// This keeps the toolbar decoupled while making its visible × control a whole-map reset.
document.addEventListener('click', event => {
  const button = event.target.closest('#atlasWorldReset');
  if (!button) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  reset();
}, true);

window.__potatoAtlasMapState = { reset, snapshot };
