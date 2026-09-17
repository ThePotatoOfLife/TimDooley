// Context / Visibility Orchestrator for the World Relational Atlas.
//
// Reads public subsystem state and publishes one deterministic presentation policy.
// It does not own domain data, geometry, analytical semantics or canonical state.

const map = window.__potatoAtlasMap;
const selection = window.__potatoAtlasSelection;
const layers = window.__potatoAtlasLayers;
const scale = window.__potatoAtlasScale;

if (!map || !selection) throw new Error('Context visibility requires map and selection APIs.');

let current = null;
let refreshScheduled = false;
let refreshSerial = 0;
let staleSuppressions = 0;

function timeState() {
  const direct = window.__potatoAtlasTime?.getState?.();
  if (direct) return direct;
  const url = new URL(location.href);
  return {
    mode:['current','as_of','changed_between'].includes(url.searchParams.get('timeMode')) ? url.searchParams.get('timeMode') : 'current',
    time:url.searchParams.get('time') || '',
    time2:url.searchParams.get('time2') || '',
  };
}

function activeLayerEntries() {
  try { return layers?.active?.().map(id => layers.get(id)).filter(Boolean) || []; }
  catch { return []; }
}

function scaleBand() {
  try {
    const direct = scale?.bandForZoom?.(map.getZoom?.());
    if (direct) return direct;
    const state = scale?.current?.();
    if (state?.band) return state.band;
  } catch { /* fall through to semantic default */ }
  return 'world';
}

function evidenceActive() {
  return Boolean(
    document.querySelector('[data-investigation="evidence"].active') ||
    document.getElementById('evidence')?.classList.contains('active') ||
    window.__potatoAtlasInvestigationSurface?.current?.type === 'evidence'
  );
}
function connectionsActive(snapshot) {
  return Boolean(
    snapshot?.relationMode && snapshot.relationMode !== 'all' ||
    document.getElementById('relations')?.classList.contains('active') ||
    window.__potatoAtlasInvestigationSurface?.current?.type === 'trace' ||
    window.__potatoAtlasInvestigationSurface?.current?.type === 'path'
  );
}
function compareActive(snapshot) {
  return Boolean(
    document.getElementById('compare')?.classList.contains('active') ||
    snapshot?.compareMode ||
    (snapshot?.pinnedCodes?.length || 0) > 1 && new URL(location.href).searchParams.get('compare')
  );
}
function investigationMode(snapshot) {
  if (evidenceActive()) return 'evidence';
  if (connectionsActive(snapshot)) return 'connections';
  if (compareActive(snapshot)) return 'compare';
  return 'browse';
}

function budgetsFor(band, mode, pinCount) {
  const narrow = matchMedia?.('(max-width: 900px)')?.matches === true;
  const base = {
    world:{ active:8, pinned:2, total:20, cards:narrow ? 2 : 4 },
    'macro-region':{ active:8, pinned:2, total:22, cards:narrow ? 2 : 4 },
    region:{ active:9, pinned:2, total:24, cards:narrow ? 2 : 4 },
    country:{ active:10, pinned:2, total:26, cards:narrow ? 2 : 5 },
    subnational:{ active:6, pinned:1, total:16, cards:narrow ? 2 : 5 },
    local:{ active:4, pinned:1, total:12, cards:narrow ? 2 : 5 },
  }[band] || { active:8, pinned:2, total:20, cards:narrow ? 2 : 4 };

  if (mode === 'connections') return { ...base, active:Math.min(12, base.active + 2), total:Math.min(32, base.total + 6), pinnedCards:Math.min(base.cards, Math.max(pinCount, 1)), statusSurfaces:3 };
  if (mode === 'compare') return { ...base, active:Math.max(6, base.active - 1), pinned:Math.min(3, base.pinned + 1), pinnedCards:Math.min(base.cards, Math.max(pinCount, 1)), statusSurfaces:3 };
  if (mode === 'evidence') return { ...base, active:Math.max(4, base.active - 2), total:Math.max(12, base.total - 4), pinnedCards:Math.min(base.cards, Math.max(pinCount, 1)), statusSurfaces:4 };
  return { ...base, pinnedCards:Math.min(base.cards, Math.max(pinCount, 1)), statusSurfaces:3 };
}

function detailFlags(band, mode) {
  const place = ['country','subnational','local'].includes(band);
  const subdivision = ['subnational','local'].includes(band);
  return {
    showActiveRelations: mode !== 'evidence',
    showPinnedContext: true,
    showPlaceDetail: place,
    showSubdivisionDetail: subdivision,
    emphasizeEvidence: mode === 'evidence',
    suppressDecorativeProjectOverlays: mode === 'evidence',
    reduceAbstractRelations: ['subnational','local'].includes(band) && mode === 'browse',
  };
}

async function buildContext(reason) {
  const serial = ++refreshSerial;
  const snapshot = selection.current || {};
  const activeCountry = snapshot.activeCode || snapshot.code || null;
  const pinnedCountries = [...(snapshot.pinnedCodes || snapshot.selectedCodes || [])];
  const mode = investigationMode(snapshot);
  const band = scaleBand();
  const entries = activeLayerEntries();
  const scalar = entries.find(entry => entry.kind === 'scalar') || null;
  const epistemicTypes = [...new Set(entries.map(entry => entry.epistemic_type).filter(Boolean))];
  const budgets = budgetsFor(band, mode, pinnedCountries.length);
  const visibility = detailFlags(band, mode);

  await Promise.resolve();
  if (serial !== refreshSerial) {
    staleSuppressions += 1;
    return current;
  }

  return {
    reason,
    activeCountry,
    pinnedCountries,
    scaleBand:band,
    time:timeState(),
    question:{
      analytical:scalar?.id || null,
      relationMode:snapshot.relationMode || selection.getRelationMode?.() || 'all',
      investigation:mode,
    },
    epistemic:{ activeTypes:epistemicTypes },
    budgets:{
      activeRelations:budgets.active,
      pinnedRelations:budgets.pinned,
      totalRelations:budgets.total,
      pinnedCards:budgets.pinnedCards,
      statusSurfaces:budgets.statusSurfaces,
    },
    visibility,
    diagnostics:{ staleSuppressions },
  };
}

async function refresh(reason = 'refresh') {
  const next = await buildContext(reason);
  if (!next) return current;
  current = next;
  selection.setAutomaticRelationBudget?.({
    active:current.budgets.activeRelations,
    pinned:current.budgets.pinnedRelations,
    total:current.budgets.totalRelations,
  });
  if (window.__potatoAtlasDiagnostics) {
    window.__potatoAtlasDiagnostics.contextVisibilityRefreshes = (window.__potatoAtlasDiagnostics.contextVisibilityRefreshes || 0) + 1;
    window.__potatoAtlasDiagnostics.contextVisibilityMode = current.question.investigation;
    window.__potatoAtlasDiagnostics.contextVisibilityScale = current.scaleBand;
    window.__potatoAtlasDiagnostics.contextVisibilityBudgets = { ...current.budgets };
    window.__potatoAtlasDiagnostics.contextVisibilityStaleSuppressions = staleSuppressions;
  }
  window.dispatchEvent(new CustomEvent('potato-atlas-context-visibility-change', { detail:current }));
  return current;
}

function scheduleRefresh(reason = 'event') {
  if (refreshScheduled) return;
  refreshScheduled = true;
  queueMicrotask(async () => {
    refreshScheduled = false;
    await refresh(reason);
  });
}

window.__potatoAtlasContextVisibility = {
  get current() { return current; },
  refresh,
  scheduleRefresh,
};

for (const eventName of [
  'potato-atlas-working-selection-change',
  'potato-atlas-pin-change',
  'potato-atlas-relation-mode-change',
  'potato-atlas-layer-change',
  'potato-atlas-composition-change',
  'atlas-time-change',
  'potato-atlas-inspector-change',
  'potato-atlas-investigation-change',
]) window.addEventListener(eventName, () => scheduleRefresh(eventName));

map.on?.('moveend', () => scheduleRefresh('moveend'));
window.addEventListener('resize', () => scheduleRefresh('resize'));
await refresh('ready');
