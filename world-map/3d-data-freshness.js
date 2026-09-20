// Shared World Map empirical-data freshness vocabulary.
// Classifies explicit source metadata only; never guesses currentness from age alone.
const LABELS = Object.freeze({
  current:'Current',
  'latest-available':'Latest available',
  delayed:'Delayed',
  historical:'Historical',
  stale:'Stale',
  'unknown-vintage':'Unknown vintage',
  planned:'Planned',
});
const ALIASES = Object.freeze({
  'historical-snapshot':'historical',
  'historical-seed':'historical',
  'current-snapshot':'current',
  latest_available:'latest-available',
  'latest-available':'latest-available',
  'delayed-snapshot':'delayed',
  delayed:'delayed',
  'stale-snapshot':'stale',
  stale:'stale',
  unknown:'unknown-vintage',
  'unknown-vintage':'unknown-vintage',
  planned:'planned',
});
function text(value){ return String(value ?? '').trim(); }
function explicitStatus(meta={}) {
  for (const value of [meta.freshness_status, meta.data_status, meta.freshness]) {
    const raw=text(value).toLowerCase();
    if (ALIASES[raw]) return ALIASES[raw];
    if (LABELS[raw]) return raw;
  }
  const vintage=text(meta.dataset_refresh_date || meta.upstream_refresh_date).toLowerCase();
  if (vintage.includes('unknown') || vintage.includes('exact upstream refresh unknown')) return 'unknown-vintage';
  return 'unknown-vintage';
}
function observation(meta={}) {
  return text(meta.data_through || meta.observed_end || meta.observation_date || meta.reference_period || meta.dataset_refresh_date || meta.upstream_refresh_date) || null;
}
function describe(meta={}) {
  const key=explicitStatus(meta);
  const asOf=observation(meta);
  const label=LABELS[key] || LABELS['unknown-vintage'];
  const detail = key==='current' ? 'Explicitly current for the dataset scope'
    : key==='latest-available' ? 'Latest available observation; not guaranteed current'
    : key==='delayed' ? 'Observation is intentionally delayed'
    : key==='historical' ? 'Historical snapshot; not current coverage'
    : key==='stale' ? 'Outside a declared freshness boundary'
    : key==='planned' ? 'No active dataset on this surface'
    : 'Exact upstream observation/refresh vintage is unknown';
  return Object.freeze({key,label,asOf,detail});
}
window.__potatoAtlasFreshness = Object.freeze({ describe, labels:{...LABELS} });
window.dispatchEvent?.(new CustomEvent('potato-atlas-freshness-ready'));
export { describe };
