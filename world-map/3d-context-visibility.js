// Context / Visibility Orchestrator for the World Relational Atlas.
//
// Reads public subsystem state and publishes one deterministic presentation policy.
// It does not own domain data, geometry, analytical semantics or canonical state.

import { contextScaleBand, contextBudgets, contextVisibility, contextInvestigationMode } from './3d-context-policy.js';

const map = window.__potatoAtlasMap;
const selection = window.__potatoAtlasSelection;

if (!map || !selection) throw new Error('Context visibility requires map and selection APIs.');

let current = null;
let refreshScheduled = false;
let refreshSerial = 0;
let staleSuppressions = 0;
let stableScaleBand = null;
let relationBudgetSkips = 0;

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
  try {
    const layers = window.__potatoAtlasLayers;
    return layers?.active?.().map(id => layers.get(id)).filter(Boolean) || [];
  } catch { return []; }
}
function activeIds(api) {
  try {
    const values = api?.active?.() || [];
    return Array.isArray(values) ? values.map(value => String(value || '')).filter(Boolean) : [];
  } catch { return []; }
}

function scaleBand() {
  const zoom = Number(map.getZoom?.());
  if (!Number.isFinite(zoom)) return stableScaleBand || 'world';
  stableScaleBand = contextScaleBand(window.__potatoAtlasScale, stableScaleBand, zoom);
  return stableScaleBand;
}

function activeInvestigationId() {
  try {
    const api = window.__potatoAtlasInvestigationSurface;
    if (typeof api?.active === 'function') return api.active();
    return api?.current?.id || null;
  } catch { return null; }
}
function evidenceActive() {
  const id = activeInvestigationId();
  const evidenceLayers = window.__potatoAtlasEvidenceLayers?.active?.() || [];
  return Boolean(
    evidenceLayers.length ||
    id === 'evidence' ||
    document.querySelector('[data-investigation="evidence"].active') ||
    document.getElementById('evidence')?.classList.contains('active') ||
    document.getElementById('evidenceEye')?.classList.contains('active')
  );
}
function specialistConnectionsActive() {
  const id = activeInvestigationId();
  return Boolean(
    document.getElementById('relations')?.classList.contains('active') ||
    ['trace','path','impact','entity-trace','chain-detail'].includes(String(id || ''))
  );
}
function compareActive(snapshot) {
  return Boolean(
    document.getElementById('compare')?.classList.contains('active') ||
    snapshot?.compareMode ||
    ((snapshot?.pinnedCodes?.length || 0) > 1 && new URL(location.href).searchParams.get('compare'))
  );
}
function investigationMode(snapshot) {
  return contextInvestigationMode({
    evidence:evidenceActive(),
    specialistConnections:specialistConnectionsActive(),
    compare:compareActive(snapshot),
    relationFiltered:Boolean(snapshot?.relationMode && snapshot.relationMode !== 'all'),
  });
}
function relationBudgetsEqual(a, b) {
  return Boolean(a && b
    && Number(a.active) === Number(b.active)
    && Number(a.pinned) === Number(b.pinned)
    && Number(a.total) === Number(b.total));
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
  const narrow = typeof matchMedia === 'function' && matchMedia('(max-width: 900px)').matches === true;
  const budgets = contextBudgets({ band, mode, pinCount:pinnedCountries.length, narrow });
  const visibility = contextVisibility({ band, mode });

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
      investigationId:activeInvestigationId(),
    },
    epistemic:{ activeTypes:epistemicTypes },
    layers:{
      physical:activeIds(window.__potatoAtlasPhysicalLayers),
      geography:activeIds(window.__potatoAtlasSpatialOverlays),
      evidence:activeIds(window.__potatoAtlasEvidenceLayers),
    },
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
  const desiredRelationBudget = {
    active:current.visibility.showActiveRelations ? current.budgets.activeRelations : 0,
    pinned:current.visibility.showActiveRelations ? current.budgets.pinnedRelations : 0,
    total:current.visibility.showActiveRelations ? current.budgets.totalRelations : 0,
  };
  const existingRelationBudget = selection.getAutomaticRelationBudget?.();
  if (relationBudgetsEqual(existingRelationBudget, desiredRelationBudget)) {
    relationBudgetSkips += 1;
  } else {
    selection.setAutomaticRelationBudget?.(desiredRelationBudget);
  }
  if (window.__potatoAtlasDiagnostics) {
    window.__potatoAtlasDiagnostics.contextVisibilityRefreshes = (window.__potatoAtlasDiagnostics.contextVisibilityRefreshes || 0) + 1;
    window.__potatoAtlasDiagnostics.contextVisibilityMode = current.question.investigation;
    window.__potatoAtlasDiagnostics.contextVisibilityScale = current.scaleBand;
    window.__potatoAtlasDiagnostics.contextVisibilityBudgets = { ...current.budgets };
    window.__potatoAtlasDiagnostics.contextVisibilityStaleSuppressions = staleSuppressions;
    window.__potatoAtlasDiagnostics.contextRelationBudgetSkips = relationBudgetSkips;
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
  'potato-atlas-evidence-layer-change',
  'potato-atlas-scale-ready',
  'potato-atlas-module-ready',
]) window.addEventListener(eventName, () => scheduleRefresh(eventName));

map.on?.('moveend', () => scheduleRefresh('moveend'));
window.addEventListener('resize', () => scheduleRefresh('resize'));
await refresh('ready');
