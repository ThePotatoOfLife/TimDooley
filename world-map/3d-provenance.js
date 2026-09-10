const INDEX_URL = '../data/countries/index.json';
const CARD_ID = 'axisProvenanceCard';
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
let indexByCode = null;
let renderToken = 0;

async function countryIndex() {
  if (indexByCode) return indexByCode;
  const response = await fetch(INDEX_URL);
  if (!response.ok) throw new Error('country index unavailable');
  const data = await response.json();
  indexByCode = Object.fromEntries((data.countries || []).map(row => [row.iso3, row]));
  return indexByCode;
}

function currentCountry() {
  return new URL(location.href).searchParams.get('country')?.toUpperCase() || null;
}

function removeCard() {
  document.getElementById(CARD_ID)?.remove();
}

function sourceRows(record) {
  const urls = new Set();
  const labels = [];
  const add = (label, url) => {
    if (!url || urls.has(url)) return;
    urls.add(url);
    labels.push({label:label || url, url});
  };
  for (const [key, observation] of Object.entries(record.observations || {})) {
    if (observation && typeof observation === 'object' && observation.source_url) add(observation.source || key, observation.source_url);
  }
  for (const url of record.history?.source_urls || []) add('History source', url);
  for (const url of record.provenance?.sources || []) add('Provenance source', url);
  return labels;
}

async function renderCountryRoots(code) {
  const token = ++renderToken;
  removeCard();
  if (!code) return;
  const index = await countryIndex();
  const row = index[code];
  if (!row) return;
  const response = await fetch(`../data/countries/${encodeURIComponent(row.id)}.json`);
  if (!response.ok) return;
  const record = await response.json();
  if (token !== renderToken) return;
  const panel = document.getElementById('panel');
  if (!panel) return;

  const observations = Object.values(record.observations || {}).filter(v => v && typeof v === 'object' && Object.prototype.hasOwnProperty.call(v,'value'));
  const relations = record.relationships || [];
  const turns = record.history?.turning_points || [];
  const sources = sourceRows(record);
  const provenance = record.provenance || {};
  const research = record.research_queue || [];

  const card = document.createElement('div');
  card.id = CARD_ID;
  card.className = 'card';
  card.style.borderColor = '#665442';
  card.innerHTML = `
    <div class="eyebrow" style="color:#c9a77e">D3 · country roots / provenance</div>
    <h2 style="margin-top:5px">${esc(record.identity?.name || row.name || code)} · roots</h2>
    <p class="muted">Descend from the present D4 polygon into the record that supports it: observations, relationships, turning points, sources and unresolved research.</p>
    <div class="grid">
      <div class="metric"><span>Record</span><b>${esc(record.record_version || '—')}</b><small>${esc(record.status || 'unknown')}</small></div>
      <div class="metric"><span>Sourced observations</span><b>${observations.length}</b><small>${esc(record.coverage?.research_status || '')}</small></div>
      <div class="metric"><span>Relationships</span><b>${relations.length}</b><small>typed country record edges</small></div>
      <div class="metric"><span>Turning points</span><b>${turns.length}</b><small>historical roots currently recorded</small></div>
    </div>
    <div class="row"><b>Canonical owner</b><br><span class="muted">data/countries/${esc(row.id)}.json</span></div>
    ${provenance.observation_policy ? `<div class="row"><b>Provenance rule</b><br><span class="muted">${esc(provenance.observation_policy)}</span></div>` : ''}
    <div class="row"><b>Root sources · ${sources.length}</b>${sources.slice(0,8).map(source => `<br><a href="${esc(source.url)}" target="_blank" rel="noopener">${esc(source.label)}</a>`).join('')}${sources.length>8?`<br><span class="muted">+ ${sources.length-8} more in canonical record</span>`:''}</div>
    ${turns.length ? `<div class="row"><b>Historical roots</b>${turns.slice(-5).reverse().map(t => `<br><span class="muted">${esc(t.date || '—')} · ${esc(t.event || '')}</span>`).join('')}</div>` : ''}
    ${research.length ? `<div class="row"><b>Unresolved roots / research queue</b>${research.slice(0,6).map(item => `<br><span class="muted">• ${esc(item)}</span>`).join('')}</div>` : ''}
    <div class="boundary">D3 records provenance and residue; it does not infer causation merely because events are adjacent, and it does not assign ancestral or collective guilt.</div>`;
  panel.appendChild(card);
}

async function updateForDimension(dimension) {
  if (Number(dimension) !== 3) {
    removeCard();
    return;
  }
  try { await renderCountryRoots(currentCountry()); }
  catch (error) { console.warn('D3 provenance unavailable:', error); }
}

window.addEventListener('atlas-axis-dimension-change', event => {
  setTimeout(() => updateForDimension(event.detail?.dimension), 0);
});
window.addEventListener('popstate', () => updateForDimension(Number(new URL(location.href).searchParams.get('axisD') || 4)));

const observer = new MutationObserver(() => {
  const dimension = Number(new URL(location.href).searchParams.get('axisD') || 4);
  if (dimension === 3 && !document.getElementById(CARD_ID)) setTimeout(() => updateForDimension(3), 0);
});
const panel = document.getElementById('panel');
if (panel) observer.observe(panel,{childList:true});
updateForDimension(Number(new URL(location.href).searchParams.get('axisD') || 4));
