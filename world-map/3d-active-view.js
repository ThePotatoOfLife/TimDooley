// Shared presentation adapter for the World Relational Atlas.
//
// The registry/compositor/runtime remain authoritative. This module only turns
// the current map question into one consistent country-level answer for cards,
// inspectors, legends and comparison surfaces.

const layers = window.__potatoAtlasLayers;
const compositor = window.__potatoAtlasCompositor;
const selection = window.__potatoAtlasSelection;
const runtime = window.__potatoAtlasDataRuntime;
if (!layers || !compositor || !selection || !runtime?.ready) {
  throw new Error('Active view requires layer, compositor, selection and data-runtime APIs.');
}
await layers.ready;

const DEMOGRAPHY_URL = '../data/world-country-demography.json';
let demography = null;
let current = null;
let refreshSerial = 0;

async function fetchJson(url) {
  const response = await fetch(url, { cache:'no-cache' });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}
async function demographyData() {
  if (!demography) demography = await fetchJson(DEMOGRAPHY_URL);
  return demography;
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
  if (!entries.length) return { mode:window.__potatoAtlasQuery?.getMode?.() || 'any', matches:null, memberships:[] };
  const memberships = [];
  for (const entry of entries) {
    let member = false;
    if (entry.runtime_axis) member = (await runtime.axisMembers?.(entry.runtime_axis) || []).includes(code);
    else if (entry.id.startsWith('group.')) member = (await runtime.members?.(entry.id.slice(6)) || []).includes(code);
    else member = Boolean(await window.__potatoAtlasQuery?.matches?.(code));
    memberships.push({ id:entry.id, label:entry.label, member, epistemicType:entry.epistemic_type || null, notes:entry.notes || null });
  }
  const mode = window.__potatoAtlasQuery?.getMode?.() || 'any';
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
  const memberships = code ? await setMembership(code, sets) : { mode:window.__potatoAtlasQuery?.getMode?.() || 'any', matches:null, memberships:[] };
  const relationMode = selection.getRelationMode?.() || selection.current?.relationMode || 'all';

  if (!scalar && !sets.length) {
    return {
      status:'neutral', code, scalar:null, sets:[], observation:null, display:null,
      source:null, period:null, coverage:null, memberships, relationMode,
      question:'No analytical overlay',
    };
  }

  if (scalar && value == null) {
    return {
      status: 'unknown', code, scalar, sets, observation:null, display:'Unknown',
      source:sourceLabel(scalar, observation), period:periodLabel(observation), coverage,
      memberships, relationMode, question:`Color: ${scalar.label}`,
    };
  }

  return {
    status:'current', code, scalar, sets, observation,
    display:scalar ? formatObservation(observation, scalar.unit) : null,
    source:sourceLabel(scalar, observation), period:periodLabel(observation), coverage,
    memberships, relationMode,
    question:scalar ? `Color: ${scalar.label}` : `${memberships.mode.toUpperCase()} set view`,
  };
}

async function refresh(reason = 'refresh') {
  const serial = ++refreshSerial;
  const code = selection.current?.activeCode || selection.current?.code || '';
  let next;
  try { next = await forCountry(code); }
  catch (error) {
    console.warn('Active map view context unavailable:', error);
    next = { status: 'unknown', code, scalar:scalarEntry(), sets:setEntries(), display:'Unknown', source:null, period:null, coverage:null, memberships:{ mode:window.__potatoAtlasQuery?.getMode?.() || 'any', matches:null, memberships:[] }, relationMode:selection.getRelationMode?.() || 'all', question:'Map view unavailable' };
  }
  if (serial !== refreshSerial) return current;
  current = { ...next, reason };
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
  window.addEventListener(eventName, event => queueMicrotask(() => refresh(eventName)));
}

await refresh('ready');
