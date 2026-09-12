// Lightweight country-dimensions enhancement for the 3D World Relational Atlas.
//
// The hover bootstrap already loads the generated same-origin country-facts
// snapshot. This module turns those facts into inspector functionality without
// creating another map layer or another external browser dependency.

const panel = document.getElementById('panel');
const factsData = window.__potatoAtlasCountryFacts || { countries: {} };

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

const compact = value => {
  const n = Number(value);
  return Number.isFinite(n) ? new Intl.NumberFormat('en', { maximumFractionDigits: 1 }).format(n) : '—';
};

const whole = value => {
  const n = Number(value);
  return Number.isFinite(n) ? new Intl.NumberFormat('en', { maximumFractionDigits: 0 }).format(Math.round(n)) : '—';
};

function currentCode() {
  const selection = window.__potatoAtlasSelection?.current;
  const code = String(selection?.code || '').toUpperCase();
  return /^[A-Z]{3}$/.test(code) ? code : null;
}

function factsFor(code) {
  return code ? factsData.countries?.[code] || null : null;
}

function demographyFor(code) {
  return code ? window.__potatoAtlasDemography?.countries?.[code] || null : null;
}

function countryName(code) {
  return factsFor(code)?.name || demographyFor(code)?.name || code;
}

function regionLabel(facts) {
  return [facts?.continent || facts?.region, facts?.subregion].filter(Boolean).join(' · ') || '—';
}

function languageLabel(facts) {
  const values = Array.isArray(facts?.languages) ? facts.languages.filter(Boolean) : [];
  return values.length ? values.slice(0, 8).join(' · ') : '—';
}

function populationDensity(code, facts) {
  const population = Number(demographyFor(code)?.population?.value);
  const area = Number(facts?.area_km2);
  if (!Number.isFinite(population) || population <= 0 || !Number.isFinite(area) || area <= 0) return null;
  return population / area;
}

function neighborsHtml(facts) {
  const neighbors = Array.isArray(facts?.neighbors) ? facts.neighbors.filter(code => factsFor(code)) : [];
  if (!neighbors.length) return '<span class="muted">No land-border neighbors in the current snapshot.</span>';
  return neighbors.map(code => `<button class="country-dimension-neighbor" data-country-code="${esc(code)}" title="Open ${esc(countryName(code))}">${esc(countryName(code))}</button>`).join('');
}

function capitalHtml(code, facts) {
  const name = facts?.capital || '—';
  if (name === '—') return '<b>—</b>';
  const focusable = Boolean(window.__potatoAtlasCapitals?.forCountry?.(code));
  if (!focusable) return `<b>${esc(name)}</b>`;
  return `<button class="country-dimension-capital" data-country-code="${esc(code)}" title="Focus ${esc(name)} on the map">${esc(name)} <span aria-hidden="true">↗</span></button>`;
}

function ensureStyle() {
  if (document.getElementById('atlasCountryDimensionsStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasCountryDimensionsStyle';
  style.textContent = `
    .atlas-country-profile{border-color:#3a4744}
    .atlas-country-profile-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:8px}
    .atlas-country-fact{min-width:0;padding:7px 0;border-top:1px solid var(--line)}
    .atlas-country-fact span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.08em}
    .atlas-country-fact b{display:block;margin-top:2px;font-size:12px;overflow-wrap:anywhere}
    .atlas-country-neighbors{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
    .country-dimension-neighbor{padding:4px 7px;border-radius:999px;font-size:11px;background:#101918}
    .country-dimension-capital{display:inline-flex;align-items:center;gap:5px;margin-top:3px;padding:4px 7px;font-size:12px;background:#101918;border-color:#394843;color:var(--ink)}
    .country-dimension-capital span{display:inline;color:var(--gold);font-size:11px;letter-spacing:0;text-transform:none}
    .atlas-country-provenance{font-size:9px;margin-top:8px;line-height:1.35}
    @media(max-width:900px){.atlas-country-profile-grid{grid-template-columns:1fr}}
  `;
  document.head.appendChild(style);
}

function hasMetricLabel(grid, label) {
  const wanted = String(label || '').trim().toLowerCase();
  return [...(grid?.querySelectorAll('.metric span') || [])].some(node => node.textContent?.trim().toLowerCase() === wanted);
}

function addMetric(grid, label, value, title = '') {
  if (!grid || value == null || value === '' || value === '—' || hasMetricLabel(grid, label)) return;
  const key = label.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  if (grid.querySelector(`[data-country-dimension-metric="${CSS.escape(key)}"]`)) return;
  const metric = document.createElement('div');
  metric.className = 'metric';
  metric.dataset.countryDimensionMetric = key;
  if (title) metric.title = title;
  metric.innerHTML = `<span>${esc(label)}</span><b>${esc(value)}</b>`;
  grid.appendChild(metric);
}

function profileCard(code, facts) {
  const sourceOwner = facts?.source_owner || 'canonical country record';
  const fallback = facts?.fallback_source || 'GeoNames countryInfo';
  const areaDefinition = facts?.area_definition ? `Area field: ${facts.area_definition}.` : '';
  const officialName = facts?.official_name && facts.official_name !== facts?.name ? facts.official_name : null;
  return `<div class="card atlas-country-profile" data-country-dimensions-code="${esc(code)}">
    <b>Country profile</b>
    <div class="atlas-country-profile-grid">
      ${officialName ? `<div class="atlas-country-fact"><span>Official name</span><b>${esc(officialName)}</b></div>` : ''}
      <div class="atlas-country-fact"><span>Capital</span>${capitalHtml(code, facts)}</div>
      <div class="atlas-country-fact"><span>Region</span><b>${esc(regionLabel(facts))}</b></div>
      <div class="atlas-country-fact"><span>Currency</span><b>${esc(facts?.currency || '—')}</b></div>
      <div class="atlas-country-fact"><span>Languages</span><b>${esc(languageLabel(facts))}</b></div>
      ${facts?.national_day ? `<div class="atlas-country-fact"><span>National day</span><b>${esc(facts.national_day)}</b></div>` : ''}
      <div class="atlas-country-fact"><span>ISO3</span><b>${esc(code)}</b></div>
    </div>
    <div class="atlas-country-fact"><span>Land-border neighbors</span><div class="atlas-country-neighbors">${neighborsHtml(facts)}</div></div>
    <div class="muted atlas-country-provenance">Display facts prefer ${esc(sourceOwner)} and use ${esc(fallback)} only for missing presentation fields. ${esc(areaDefinition)}</div>
  </div>`;
}

function isCountryOverview(target) {
  const eyebrow = target.querySelector('.eyebrow')?.textContent || '';
  return /Canonical country|Territory \/ map polygon/i.test(eyebrow);
}

function enhancePanel() {
  if (!panel || !isCountryOverview(panel)) return;
  const code = currentCode();
  const facts = factsFor(code);
  if (!code || !facts) return;

  const grid = panel.querySelector('.grid');
  const density = populationDensity(code, facts);
  addMetric(grid, 'Capital', facts.capital || '—');
  addMetric(grid, 'Region', regionLabel(facts));
  addMetric(grid, 'Borders', Array.isArray(facts.neighbors) ? compact(facts.neighbors.length) : '—');
  addMetric(grid, 'Currency', facts.currency || '—');
  addMetric(grid, 'Density', density == null ? '—' : `${whole(density)} / km²`, 'Derived from the current sourced population snapshot divided by the atlas area value.');

  const existing = panel.querySelector(`.atlas-country-profile[data-country-dimensions-code="${CSS.escape(code)}"]`);
  if (!existing) {
    const holder = document.createElement('div');
    holder.innerHTML = profileCard(code, facts);
    const card = holder.firstElementChild;
    const gridNode = panel.querySelector('.grid');
    if (card && gridNode?.parentNode) gridNode.parentNode.insertBefore(card, gridNode.nextSibling);
    else if (card) panel.appendChild(card);
  }
}

function handleProfileClick(event) {
  const neighbor = event.target.closest('.country-dimension-neighbor[data-country-code]');
  if (neighbor) {
    const code = neighbor.dataset.countryCode;
    if (code && window.goCountry) window.goCountry(code);
    return;
  }
  const capital = event.target.closest('.country-dimension-capital[data-country-code]');
  if (capital) {
    window.__potatoAtlasCapitals?.focus?.(capital.dataset.countryCode);
  }
}

ensureStyle();
panel?.addEventListener('click', handleProfileClick);
window.addEventListener('potato-atlas-panel-rendered', enhancePanel);
window.addEventListener('potato-atlas-selection-change', enhancePanel);
window.addEventListener('potato-atlas-module-ready', event => {
  if (event?.detail?.label === 'Demography') enhancePanel();
});
window.addEventListener('potato-atlas-capitals-ready', enhancePanel);
window.__potatoAtlasCountryDimensions = {
  factsFor,
  render: enhancePanel,
  get current() {
    const code = currentCode();
    return code ? { code, facts: factsFor(code), demography: demographyFor(code) } : null;
  },
};

enhancePanel();
