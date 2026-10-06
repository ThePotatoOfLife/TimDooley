// Shared presentation adapter for the World Relational Atlas.
//
// The registry/compositor/runtime remain authoritative. This module only turns
// the current map question into one consistent country-level answer for cards,
// inspectors, legends, comparison surfaces and the Current map view summary.

const layers = window.__potatoAtlasLayers;
const compositor = window.__potatoAtlasCompositor;
const selection = window.__potatoAtlasSelection;
const runtime = window.__potatoAtlasDataRuntime;
const query = window.__potatoAtlasQuery;
if (!layers || !compositor || !selection || !runtime?.ready) {
  throw new Error('Active view requires layer, compositor, selection and data-runtime APIs.');
}
await layers.ready;

const DEMOGRAPHY_URL = '../data/world-country-demography.json';
const VIEW_PROJECTIONS_URL = '../data/world-map-view-projections.json';
let demography = null;
let viewProjections = null;
let current = null;
let refreshSerial = 0;
let timeState = readTimeState();

function fetchJson(url) {
  return fetch(url, { cache:'no-cache' }).then(response => {
    if (!response.ok) throw new Error(`${response.status} ${url}`);
    return response.json();
  });
}
async function demographyData() {
  if (!demography) demography = await fetchJson(DEMOGRAPHY_URL);
  return demography;
}
async function projectionData() {
  if (!viewProjections) viewProjections = await fetchJson(VIEW_PROJECTIONS_URL);
  return viewProjections;
}
function dedupe(values) {
  return [...new Set((values || []).filter(Boolean))];
}
async function projectionSummary({ scalar, sets, relationMode, pinnedCodes }) {
  const data = await projectionData();
  const contracts = [];
  if (scalar) contracts.push(data?.views?.['country-scalar']);
  if (sets?.length) contracts.push(data?.views?.['country-set']);
  if (relationMode && relationMode !== 'all') contracts.push(data?.views?.['active-country-relations']);
  if ((pinnedCodes || []).length > 1) contracts.push(data?.views?.['country-comparison']);
  const active = contracts.filter(Boolean);
  return {
    contractId:data?.id || null,
    contractVersion:data?.version || null,
    views:active.map(item => item.label),
    informationLoss:dedupe(active.flatMap(item => item.information_loss || [])),
    reconstructability:active.length ? (active.every(item => item.reconstructability === 'source-linked') ? 'source-linked' : 'partial') : null,
    sourcePaths:dedupe(active.map(item => item.source_path_back)),
  };
}
function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}
function formatNumber(value, digits = 1) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits:digits }).format(value);
}
function formatCompact(value) {
  return new Intl.NumberFormat(undefined, { notation:'compact', maximumFractionDigits:1 }).format(value);
}
function formatObservation(cell, unitOverride = null) {
  const value = number(cell?.value);
  if (value == null) return 'Unknown';
  const unit = String(unitOverride || cell?.unit || '').trim();
  if (unit.includes('USD') || unit.includes('international $')) {
    return new Intl.NumberFormat(undefined, { style:'currency', currency:'USD', maximumFractionDigits:0 }).format(value);
  }
  if (unit === 'persons') return formatCompact(value);
  if (unit === 'km²' || unit === 'km2' || unit.includes('square kilomet')) return `${formatNumber(value, 0)} km²`;
  if (unit.includes('percent')) return `${formatNumber(value, 1)}%`;
  if (unit.includes('year')) return `${formatNumber(value, 1)} years`;
  return `${formatNumber(value, 1)}${unit ? ` ${unit}` : ''}`;
}
function readTimeState() {
  const direct = window.__potatoAtlasTime?.getState?.();
  if (direct) return direct;
  const url = new URL(location.href);
  const mode = ['current','as_of','changed_between'].includes(url.searchParams.get('timeMode')) ? url.searchParams.get('timeMode') : 'current';
  return { mode, time:url.searchParams.get('time') || '', time2:url.searchParams.get('time2') || '' };
}
function activeEntries() {
  return layers.active().map(id => layers.get(id)).filter(Boolean);
}
function scalarEntry() {
  return activeEntries().find(entry => entry.kind === 'scalar') || null;
}
function setEntries() {
  return activeEntries().filter(entry => entry.kind === 'set');
}
function religionKey(entry) {
  const tail = String(entry?.id || '').split('.').pop();
  return tail === 'other' ? 'other_religions' : tail;
}
async function religionObservation(code, entry) {
  const data = await demographyData();
  const row = data?.countries?.[code]?.religion;
  const value = number(row?.composition?.[religionKey(entry)]);
  if (value == null) return null;
  return {
    value,
    unit:'percent',
    period:row?.year || row?.period || data?.updated || null,
    source:row?.source || data?.source || entry.source_owner,
  };
}
async function scalarObservation(code, entry) {
  if (!entry) return null;
  if (entry.family === 'religion') return religionObservation(code, entry);
  if (entry.runtime_scalar && runtime.scalarObservation) return runtime.scalarObservation(code, entry.runtime_scalar);
  if (entry.id === 'stat.population' && runtime.populationObservation) return runtime.populationObservation(code);
  if (entry.id === 'stat.area' && runtime.areaObservation) return runtime.areaObservation(code);
  if (entry.runtime_metric) return runtime.metric(code, entry.runtime_metric);
  return null;
}
async function setMembership(code, entries) {
  if (!entries.length) return { mode:query?.getMode?.() || 'any', matches:null, memberships:[] };
  const memberships = [];
  for (const entry of entries) {
    let member = false;
    if (entry.runtime_axis) member = (await runtime.axisMembers?.(entry.runtime_axis) || []).includes(code);
    else if (entry.id.startsWith('group.')) member = (await runtime.members?.(entry.id.slice(6)) || []).includes(code);
    else member = Boolean(await query?.matches?.(code));
    memberships.push({ id:entry.id, label:entry.label, member, epistemicType:entry.epistemic_type || null, notes:entry.notes || null });
  }
  const mode = query?.getMode?.() || 'any';
  const states = memberships.map(item => item.member);
  const matches = mode === 'all' ? states.every(Boolean) : states.some(Boolean);
  return { mode, matches, memberships };
}
async function coverageFor(entry) {
  if (!entry) return null;
  if (entry.runtime_metric) return runtime.coverage?.(entry.runtime_metric) || null;
  return null;
}
function sourceLabel(entry, observation) {
  return observation?.source || entry?.source_owner || null;
}
function periodLabel(observation) {
  return observation?.period ?? observation?.year ?? observation?.date ?? null;
}

async function forCountry(code) {
  code = String(code || '').toUpperCase();
  const scalar = scalarEntry();
  const sets = setEntries();
  const observation = scalar && code ? await scalarObservation(code, scalar) : null;
  const value = number(observation?.value);
  const coverage = await coverageFor(scalar);
  const memberships = code ? await setMembership(code, sets) : { mode:query?.getMode?.() || 'any', matches:null, memberships:[] };
  const relationMode = selection.getRelationMode?.() || selection.current?.relationMode || 'all';
  const pinnedCodes = selection.current?.pinnedCodes || selection.current?.selectedCodes || [];
  const projection = await projectionSummary({ scalar, sets, relationMode, pinnedCodes });

  if (!scalar && !sets.length) {
    return {
      status:'neutral', code, scalar:null, sets:[], observation:null, display:null,
      source:null, period:null, coverage:null, memberships, relationMode,
      projection, timeState, question:'No analytical overlay',
    };
  }

  if (scalar && value == null) {
    return {
      status:'unknown', code, scalar, sets, observation:null, display:'Unknown',
      source:sourceLabel(scalar, observation), period:periodLabel(observation), coverage,
      memberships, relationMode, projection, timeState, question:`Color: ${scalar.label}`,
    };
  }

  return {
    status:'current', code, scalar, sets, observation,
    display:scalar ? formatObservation(observation, scalar.unit) : null,
    source:sourceLabel(scalar, observation), period:periodLabel(observation), coverage,
    memberships, relationMode, projection, timeState,
    question:scalar ? `Color: ${scalar.label}` : `${memberships.mode.toUpperCase()} set view`,
  };
}

async function refresh(reason = 'refresh') {
  const serial = ++refreshSerial;
  const code = selection.current?.activeCode || selection.current?.code || '';
  let next;
  try {
    next = await forCountry(code);
    if (next.sets?.length && query?.matchedCountries) {
      const matched = await query.matchedCountries();
      next.matchCount = matched.length;
    } else {
      next.matchCount = null;
    }
  } catch (error) {
    console.warn('Active map view context unavailable:', error);
    next = {
      status:'unknown', code, scalar:scalarEntry(), sets:setEntries(), display:'Unknown',
      source:null, period:null, coverage:null,
      memberships:{ mode:query?.getMode?.() || 'any', matches:null, memberships:[] },
      relationMode:selection.getRelationMode?.() || 'all',
      projection:{ contractId:null, contractVersion:null, views:[], informationLoss:[], reconstructability:null, sourcePaths:[] },
      timeState,
      matchCount:null, question:'Map view unavailable',
    };
  }
  if (serial !== refreshSerial) return current;
  current = { ...next, timeState, reason };
  window.dispatchEvent(new CustomEvent('potato-atlas-active-view-change', { detail:current }));
  return current;
}

window.__potatoAtlasActiveView = {
  get current() { return current; },
  forCountry,
  refresh,
  formatObservation,
};

for (const eventName of [
  'potato-atlas-layer-change',
  'potato-atlas-composition-change',
  'potato-atlas-working-selection-change',
  'potato-atlas-pin-change',
  'potato-atlas-query-change',
  'potato-atlas-relation-mode-change',
]) {
  window.addEventListener(eventName, () => queueMicrotask(() => refresh(eventName)));
}
window.addEventListener('atlas-time-change', event => {
  timeState = event.detail || readTimeState();
  queueMicrotask(() => refresh('atlas-time-change'));
});

await refresh('ready');
