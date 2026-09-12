// First-class map-entity extension for territories and other non-country polygons.
// Keeps the 195-country model intact while exposing entity-aware runtime helpers.

const dataRuntime = window.__potatoAtlasDataRuntime;
if (!dataRuntime?.ready) throw new Error('Entity runtime requires the World Map data runtime.');

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));
const formatNumber = value => Number.isFinite(Number(value)) ? new Intl.NumberFormat('en').format(Math.round(Number(value))) : '—';

async function runtime() { return dataRuntime.ready; }

async function entity(code) {
  const data = await runtime();
  return data?.entities?.by_id?.[String(code || '').toUpperCase()] || null;
}
async function entityName(code) {
  const row = await entity(code);
  return row?.name || null;
}
async function entityType(code) {
  const row = await entity(code);
  return row?.entity_type || null;
}
async function populationObservation(code) {
  const data = await runtime();
  const key = String(code || '').toUpperCase();
  return data?.entities?.by_id?.[key]?.population || data?.countries?.[key]?.population || null;
}
async function labelAnchor(code) {
  const row = await entity(code);
  return row?.label_anchor || null;
}
async function regionalSystems(code) {
  const data = await runtime();
  const key = String(code || '').toUpperCase();
  return data?.africa?.for_country?.[key] || data?.countries?.[key]?.systems?.regional || [];
}

Object.assign(dataRuntime, {
  entity,
  entityName,
  entityType,
  populationObservation,
  labelAnchor,
  regionalSystems,
});

function entityLabel(row) {
  if (!row) return 'Map entity';
  if (row.entity_type === 'self-governing-territory') return 'Self-governing territory';
  return String(row.entity_type || 'Map entity').replaceAll('-', ' ').replace(/\b\w/g, char => char.toUpperCase());
}

async function enhanceSelectedEntity(code) {
  const row = await entity(code);
  if (!row || row.canonical_country !== false) return;
  const panel = document.getElementById('panel');
  if (!panel) return;

  const eyebrow = panel.querySelector('.eyebrow');
  if (eyebrow) eyebrow.textContent = `${entityLabel(row)} · ${code}`;
  const title = panel.querySelector('h1');
  if (title) title.textContent = row.name || code;

  let block = panel.querySelector('.atlas-map-entity-context');
  if (!block) {
    block = document.createElement('div');
    block.className = 'card atlas-map-entity-context';
    const firstCard = panel.querySelector('.card');
    if (firstCard?.parentNode) firstCard.parentNode.insertBefore(block, firstCard);
    else panel.appendChild(block);
  }
  const population = row.population || {};
  const chains = row.systems?.chains || [];
  block.innerHTML = `
    <b>${esc(entityLabel(row))}</b>
    <div class="row"><span class="muted">Capital</span><br>${esc(row.capital || '—')}</div>
    <div class="row"><span class="muted">Population</span><br>${esc(formatNumber(population.value))}${population.reference_date ? ` · ${esc(population.reference_date)}` : ''}</div>
    ${population.source ? `<div class="row"><span class="muted">Population source</span><br>${esc(population.source)}</div>` : ''}
    ${row.sovereignty_context ? `<div class="row"><span class="muted">Constitutional context</span><br>${esc(row.sovereignty_context)}</div>` : ''}
    ${row.constitutional_parent ? `<div class="row"><span class="muted">Constitutional relation</span><br>${esc(row.constitutional_parent)}</div>` : ''}
    ${chains.length ? `<div class="row"><span class="muted">Functional chains</span><br>${chains.map(id => `<span class="pill">${esc(id.replaceAll('-', ' '))}</span>`).join(' ')}</div>` : ''}
    <div class="boundary">This entity is rendered directly on the World Map without being counted as one of the 195 sovereign-country records.</div>`;
}

async function enhanceRegionalContext(code) {
  const rows = await regionalSystems(code);
  if (!rows?.length) return;
  const panel = document.getElementById('panel');
  if (!panel) return;
  let block = panel.querySelector('.atlas-africa-regional-context');
  if (!block) {
    block = document.createElement('div');
    block.className = 'card atlas-africa-regional-context';
    const boundary = panel.querySelector('.boundary');
    if (boundary?.parentNode) boundary.parentNode.insertBefore(block, boundary);
    else panel.appendChild(block);
  }
  const current = rows.filter(row => row.status === 'current');
  const historical = rows.filter(row => row.status !== 'current');
  block.innerHTML = `<b>African regional systems</b><div class="row">${current.slice(0,3).map(row => `<span class="pill" title="${esc(row.source || '')}">${esc(row.label)}</span>`).join(' ')}${current.length > 3 ? ` <span class="pill">+${current.length - 3}</span>` : ''}</div>${historical.length ? `<div class="muted">Historical/transition: ${historical.map(row => `${esc(row.label)} · ${esc(row.status)}${row.effective_date ? ` ${esc(row.effective_date)}` : ''}`).join(' · ')}</div>` : ''}`;
}

async function refresh(code) {
  code = String(code || '').toUpperCase();
  if (!code) return;
  await Promise.all([enhanceSelectedEntity(code), enhanceRegionalContext(code)]);
}

window.addEventListener('potato-atlas-working-selection-change', event => {
  const code = event?.detail?.activeCode || event?.detail?.code;
  if (code) queueMicrotask(() => refresh(code));
});
window.addEventListener('potato-atlas-selection-change', event => {
  const code = event?.detail?.code;
  if (code) queueMicrotask(() => refresh(code));
});

const initial = new URL(location.href).searchParams.get('country');
if (initial) queueMicrotask(() => refresh(initial));

window.__potatoAtlasEntities = { entity, entityName, entityType, populationObservation, labelAnchor, regionalSystems, refresh };
window.dispatchEvent(new CustomEvent('potato-atlas-entities-ready'));
