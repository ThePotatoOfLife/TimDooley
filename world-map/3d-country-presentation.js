// Shared country presentation for the World Relational Atlas.
//
// Country selection owns the persistent subject and Active View owns the analytical
// answer. This module only normalizes those existing owners into one presentation
// shape consumed by hover, the selected-country card, pins and inspector summaries.

const selection = window.__potatoAtlasSelection;
const activeView = window.__potatoAtlasActiveView;
const runtime = window.__potatoAtlasDataRuntime;
const layers = window.__potatoAtlasLayers;

if (!selection || !activeView || !runtime) {
  throw new Error('Country Presentation requires selection, Active View and data runtime APIs.');
}

function formatPopulation(value) {
  if (value == null || value === '') return '—';
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { notation:'compact', maximumFractionDigits:1 }).format(number);
}

function formatArea(value) {
  if (value == null || value === '') return '—';
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return `${new Intl.NumberFormat(undefined, { maximumFractionDigits:0 }).format(number)} km²`;
}

function activeEntries() {
  try { return layers?.active?.().map(id => layers.get(id)).filter(Boolean) || []; }
  catch { return []; }
}

function currentQuestion() {
  const view = activeView.current;
  const entries = activeEntries();
  const scalar = view?.scalar || entries.find(entry => entry.kind === 'scalar') || null;
  const sets = view?.sets || entries.filter(entry => entry.kind === 'set');
  const relationMode = selection.getRelationMode?.() || selection.current?.relationMode || 'all';
  const context = window.__potatoAtlasContextVisibility?.current || null;
  const time = view?.timeState || context?.time || window.__potatoAtlasTime?.getState?.() || { mode:'current', time:'', time2:'' };
  const projection = window.__potatoAtlasProjection?.get?.() || (new URL(location.href).searchParams.get('projection') === 'globe' ? 'globe' : 'flat');

  return {
    primary:scalar
      ? { kind:'scalar', id:scalar.id || '', label:scalar.label || scalar.id || 'Map value' }
      : sets.length
        ? { kind:'set', id:sets.map(entry => entry.id).join(','), label:sets.map(entry => entry.label).join(' + ') }
        : { kind:'none', id:'', label:'' },
    sets:sets.map(entry => ({ id:entry.id, label:entry.label, epistemicType:entry.epistemic_type || null })),
    relations:{ mode:relationMode },
    time,
    projection,
    investigation:context?.question?.investigation || 'browse',
  };
}

function normalizeAnswer(view) {
  if (!view || view.status === 'neutral') {
    return { kind:'none', id:'', label:'', status:'neutral', display:'', period:'', source:'', populationPrimary:false };
  }
  if (view.scalar) {
    const id = String(view.scalar.id || '');
    return {
      kind:'scalar',
      id,
      label:view.scalar.label || id || 'Map value',
      status:view.status || 'current',
      display:view.display || 'Unknown',
      period:view.period || '',
      source:view.source || '',
      populationPrimary:id === 'stat.population',
      observation:view.observation || null,
    };
  }
  const memberships = view.memberships?.memberships || [];
  if (memberships.length) {
    return {
      kind:'set',
      id:(view.sets || []).map(entry => entry.id).join(','),
      label:(view.sets || []).map(entry => entry.label).join(' + ') || 'Set query',
      status:view.memberships?.matches ? 'matches' : 'outside',
      display:view.memberships?.matches ? 'Matches' : 'Outside',
      period:'',
      source:'',
      populationPrimary:false,
      memberships:view.memberships,
    };
  }
  return { kind:'none', id:'', label:'', status:'neutral', display:'', period:'', source:'', populationPrimary:false };
}

function factsFor(code) {
  return window.__potatoAtlasCountryFacts?.countries?.[code] || null;
}

async function forCountry(code) {
  code = String(code || '').toUpperCase();
  if (!/^[A-Z]{3}$/.test(code)) return null;

  const [populationCell, areaCell, view] = await Promise.all([
    Promise.resolve(runtime.populationObservation?.(code)).catch(() => null),
    Promise.resolve(runtime.areaObservation?.(code)).catch(() => null),
    Promise.resolve(activeView.forCountry?.(code)).catch(() => null),
  ]);
  const demo = window.__potatoAtlasDemography?.countries?.[code] || null;
  const facts = factsFor(code);
  const populationValue = populationCell?.value ?? demo?.population?.value ?? null;
  const areaValue = areaCell?.value ?? facts?.area_km2 ?? null;
  const answer = normalizeAnswer(view);
  const relationMode = view?.relationMode || selection.getRelationMode?.() || 'all';
  let relationCount = 0;
  try { relationCount = selection.connectionsFor?.(code, 64)?.length || 0; }
  catch { relationCount = 0; }

  return {
    code,
    identity:{
      name:selection.countryName?.(code) || facts?.name || demo?.name || code,
      capital:facts?.capital || '',
      region:[facts?.region || facts?.continent, facts?.subregion].filter(Boolean).join(' · '),
      area:{ value:areaValue, display:formatArea(areaValue), period:areaCell?.period || '', source:areaCell?.source || facts?.fallback_source || '' },
    },
    population:{
      value:populationValue,
      display:formatPopulation(populationValue),
      period:populationCell?.period || demo?.population?.year || '',
      source:populationCell?.source || demo?.population?.source || '',
    },
    answer,
    memberships:view?.memberships || { mode:'any', matches:null, memberships:[] },
    relation:{ mode:relationMode, count:relationCount },
    active:code === (selection.current?.activeCode || selection.current?.code),
    pinned:selection.isPinned?.(code) === true,
    question:currentQuestion(),
  };
}

window.__potatoAtlasCountryPresentation = Object.freeze({
  forCountry,
  currentQuestion,
  formatPopulation,
  formatArea,
});
window.dispatchEvent(new CustomEvent('potato-atlas-country-presentation-ready'));
