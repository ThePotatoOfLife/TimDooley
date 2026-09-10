const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

const toolbar = document.querySelector('.top');
const anchor = $('#tilt');
const button = document.createElement('button');
button.id = 'evidenceEye';
button.textContent = 'Eye';
button.title = 'Inspect source provenance, observation dates and epistemic layers for the selected country';
toolbar.insertBefore(button, anchor);

const style = document.createElement('style');
style.textContent = `.evidence-eye{position:absolute;left:12px;top:12px;z-index:5;width:min(470px,calc(100% - 24px));max-height:72%;overflow:auto;background:#080b0bf2;border:1px solid var(--line);border-radius:10px;padding:11px}.evidence-eye[hidden]{display:none}.evidence-head{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}.evidence-section{margin-top:10px;padding-top:8px;border-top:1px solid var(--line)}.evidence-kv{display:grid;grid-template-columns:115px minmax(0,1fr);gap:4px 8px;padding:3px 0;font-size:11px}.evidence-kv span:first-child{color:var(--muted)}.evidence-tag{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 6px;margin:2px 2px 2px 0;font-size:10px}.evidence-observed{border-color:#4f8064}.evidence-project{border-color:#8c7350}.evidence-source{font:10px/1.35 ui-monospace,monospace;overflow-wrap:anywhere}@media(max-width:900px){.evidence-eye{position:fixed;left:10px;right:10px;top:76px;width:auto;max-height:54vh}}`;
document.head.appendChild(style);

const box = document.createElement('section');
box.id = 'evidencePanel';
box.className = 'evidence-eye';
box.hidden = true;
document.querySelector('.mapwrap').appendChild(box);

let cache = null;

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return response.json();
}

async function loadEvidenceData() {
  if (cache) return cache;
  const [facts, demography, world] = await Promise.all([
    fetchJson('../data/world-country-facts.json').catch(() => ({countries:{}})),
    fetchJson('../data/world-country-demography.json').catch(() => ({countries:{}})),
    fetchJson('../data/world-relational-map.json'),
  ]);
  cache = {facts, demography, world};
  return cache;
}

function selectedCode() {
  return new URL(location.href).searchParams.get('country')?.toUpperCase() || null;
}

function projectStatuses(world, code) {
  const out = [];
  const axis = world?.project_axis || {};
  for (const [field, config] of Object.entries(axis)) {
    if (!config || typeof config !== 'object') continue;
    for (const [status, value] of Object.entries(config)) {
      if (Array.isArray(value) && value.includes(code)) out.push(`${field}:${status}`);
    }
  }
  return out;
}

function relationsFor(world, code) {
  return (world?.curated_edges || []).filter(edge => edge.a === code || edge.b === code);
}

function sourceRow(label, value) {
  if (!value) return '';
  return `<div class="evidence-kv"><span>${esc(label)}</span><span class="evidence-source">${esc(value)}</span></div>`;
}

function metricRow(label, value) {
  if (value === undefined || value === null || value === '') return '';
  return `<div class="evidence-kv"><span>${esc(label)}</span><span>${esc(value)}</span></div>`;
}

function closeEvidence() {
  box.hidden = true;
  button.classList.remove('active');
}
window.closeAtlasEvidence = closeEvidence;

async function renderEvidence() {
  const code = selectedCode();
  if (!code) {
    box.hidden = false;
    button.classList.add('active');
    box.innerHTML = `<div class="evidence-head"><div><div class="eyebrow">Eye · Evidence</div><b>Select a country first</b></div><button onclick="closeAtlasEvidence()">×</button></div><p class="muted">Eye inspects how the Atlas knows what it is showing. Select a country, then reopen Eye.</p>`;
    return;
  }
  box.hidden = false;
  button.classList.add('active');
  box.innerHTML = `<div class="evidence-head"><div><div class="eyebrow">Eye · Evidence</div><b>Loading ${esc(code)}…</b></div><button onclick="closeAtlasEvidence()">×</button></div>`;

  try {
    const {facts, demography, world} = await loadEvidenceData();
    const fact = facts?.countries?.[code] || {};
    const demo = demography?.countries?.[code] || {};
    const population = demo.population || {};
    const religion = demo.religion || {};
    const edges = relationsFor(world, code);
    const layerCounts = {};
    const typeCounts = {};
    for (const edge of edges) {
      const layer = edge.layer || 'unknown';
      layerCounts[layer] = (layerCounts[layer] || 0) + 1;
      for (const type of edge.types || []) typeCounts[type] = (typeCounts[type] || 0) + 1;
    }
    const statuses = projectStatuses(world, code);
    const factsSources = fact.field_sources || {};
    const fullReligion = Object.keys(religion.composition || {}).length;
    const geographicLabel = fact.region || fact.subregion || fact.continent;
    const geographicSource = fact.region ? factsSources.region : fact.subregion ? factsSources.subregion : factsSources.continent;

    const layerTags = Object.entries(layerCounts).sort((a,b)=>b[1]-a[1]).map(([name,count]) => `<span class="evidence-tag evidence-observed">${esc(name)} · ${count}</span>`).join('') || '<span class="muted">No curated country edges yet.</span>';
    const projectTags = statuses.map(value => `<span class="evidence-tag evidence-project">${esc(value)}</span>`).join('') || '<span class="muted">No current project-axis status in this registry.</span>';
    const typeTags = Object.entries(typeCounts).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([name,count]) => `<span class="evidence-tag">${esc(name)} · ${count}</span>`).join('');

    box.innerHTML = `
      <div class="evidence-head"><div><div class="eyebrow">Eye · Evidence</div><b>${esc(fact.name || demo.name || code)} · ${esc(code)}</b><div class="muted">Source provenance and epistemic context</div></div><button onclick="closeAtlasEvidence()">×</button></div>
      <div class="evidence-section"><b>Observed country facts</b>
        ${sourceRow('Identity owner', fact.source_owner)}
        ${metricRow('Capital', fact.capital)}${sourceRow('Capital source', factsSources.capital)}
        ${metricRow('Area', fact.area_km2 != null ? `${Number(fact.area_km2).toLocaleString()} km²` : '')}${sourceRow('Area source', factsSources.area_km2)}${metricRow('Area definition', fact.area_definition)}
        ${metricRow('Region', geographicLabel)}${sourceRow('Region source', geographicSource)}
        ${metricRow('Currency', fact.currency)}${sourceRow('Currency source', factsSources.currency)}
      </div>
      <div class="evidence-section"><b>Population observation</b>
        ${metricRow('Value', population.value != null ? Number(population.value).toLocaleString() : '')}
        ${metricRow('Reference year', population.year)}
        ${sourceRow('Source', population.source)}
        ${sourceRow('Source URL', population.source_url)}
        ${metricRow('Confidence', population.confidence)}
      </div>
      <div class="evidence-section"><b>Religion observation</b>
        ${metricRow('Reference year', religion.year)}
        ${metricRow('Coverage', fullReligion ? `${fullReligion}/7 broad categories` : '')}
        ${sourceRow('Source', religion.source)}
        ${sourceRow('Original source', religion.original_source_url)}
      </div>
      <div class="evidence-section"><b>Curated relationship evidence</b><div>${layerTags}</div>${typeTags ? `<div style="margin-top:5px">${typeTags}</div>` : ''}<div class="muted" style="margin-top:5px">${edges.length} represented edge${edges.length === 1 ? '' : 's'} touch this country in the current curated world graph.</div></div>
      <div class="evidence-section"><b>Project interpretation</b><div>${projectTags}</div><div class="muted" style="margin-top:5px">These badges are project-axis classifications. They are not treaty memberships, borders or empirical alignment scores.</div></div>
      <div class="boundary">Eye reports what sources and classifications the Atlas currently uses. Missing coverage means “not represented here yet,” not “false.” Repetition is not corroboration, project interpretation is not empirical evidence, and a source date is not automatically the start date of the phenomenon.</div>`;
  } catch (error) {
    box.innerHTML = `<div class="evidence-head"><div><div class="eyebrow">Eye · Evidence</div><b>Evidence data unavailable</b></div><button onclick="closeAtlasEvidence()">×</button></div><p class="muted">${esc(error.message || error)}</p>`;
  }
}

button.addEventListener('click', () => box.hidden ? renderEvidence() : closeEvidence());
window.refreshAtlasEvidence = () => { if (!box.hidden) renderEvidence(); };
window.addEventListener('popstate', window.refreshAtlasEvidence);
document.querySelector('#map')?.addEventListener('click', () => setTimeout(window.refreshAtlasEvidence, 160));
