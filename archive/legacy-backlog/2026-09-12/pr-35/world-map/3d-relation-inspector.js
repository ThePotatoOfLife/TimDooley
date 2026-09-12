// Axis-aware relationship inspector for the existing country-relation layer.
//
// This module deliberately leaves the canonical relation renderer alone. The
// core 3d-app continues to draw/trace the curated edges; this enhancement runs
// after a relation click and upgrades the inspector with typed D1-D11 guidance.
// Projection hints come from relationship-family rules and are labelled as such;
// they are not silently promoted to edge-specific facts.

const MATRIX_URL = '../data/relationship-axis-projection-matrix.json';
const SOURCE_ID = 'relation-inspector-selection';
const LAYER_ID = 'relation-inspector-selection';
const PANEL_ID = 'panel';

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({
  '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
}[ch]));
const title = value => String(value || '').replaceAll('_',' ').replaceAll('-',' ').replace(/\b\w/g, m => m.toUpperCase());

const TYPE_FAMILY_HINTS = [
  [/constitutional|government|jurisdiction|realm|membership|eu\b|nato\b|nordic|institution|council|union/i, ['institutional','political']],
  [/fiscal|finance|financial|debt|loan|credit|investment|fund|tax|trade/i, ['financial','functional']],
  [/security|defen[cs]e|alliance|military|strategic|diplom/i, ['political','institutional','functional']],
  [/intelligence|information|data|media|communication/i, ['information','institutional']],
  [/infrastructure|interconnector|pipeline|grid|port|rail|road|cable|corridor/i, ['functional','technological','geographic']],
  [/energy|technology|digital|telecom|standard|license/i, ['technological','functional']],
  [/culture|language|heritage|nordic/i, ['cultural','social']],
  [/migration|diaspora|mobility|people/i, ['social','cultural','geographic']],
  [/religion|faith|church|mosque|temple|belief/i, ['religious','cultural','social']],
  [/research|science|university|education|knowledge/i, ['intellectual','information','institutional']],
  [/ownership|control|parent|subsidiary|shareholder/i, ['financial','institutional']],
  [/arctic|border|maritime|geographic|territor|route/i, ['geographic','functional']],
  [/friend|trust|care|community|social/i, ['social','cultural']],
  [/symbol|myth|project-canon|potato/i, ['symbolic','mythological']]
];

let matrixPromise = null;
let current = null;
let selectedDimension = 4;
let installedMap = null;

async function loadMatrix() {
  if (!matrixPromise) {
    matrixPromise = fetch(MATRIX_URL).then(response => {
      if (!response.ok) throw new Error(`Relationship projection matrix returned HTTP ${response.status}`);
      return response.json();
    });
  }
  return matrixPromise;
}

function parseRaw(properties = {}) {
  try { return JSON.parse(properties.raw || '{}'); }
  catch { return {}; }
}

function edgeTypes(raw, properties = {}) {
  const source = Array.isArray(raw.types) ? raw.types : String(properties.types || '').split('·');
  return [...new Set(source.map(value => String(value).trim()).filter(Boolean))];
}

function inferFamilies(raw, properties, matrix) {
  const tokens = [...edgeTypes(raw, properties), raw.layer || properties.layer || ''];
  const found = new Set();
  for (const token of tokens) {
    for (const [pattern, families] of TYPE_FAMILY_HINTS) {
      if (!pattern.test(token)) continue;
      for (const family of families) if (matrix.families?.[family]) found.add(family);
    }
  }
  return [...found];
}

function projectionGuide(families, matrix) {
  const guide = Object.fromEntries(Array.from({length:11},(_,index)=>[index+1,{primary:[],conditional:[]} ]));
  for (const family of families) {
    const def = matrix.families?.[family];
    if (!def) continue;
    for (const dimension of def.primary || []) guide[dimension]?.primary.push(family);
    for (const dimension of def.conditional || []) guide[dimension]?.conditional.push(family);
  }
  return guide;
}

function layerReading(raw, properties = {}) {
  const layer = String(raw.layer || properties.layer || 'curated');
  const lower = layer.toLowerCase();
  if (lower === 'empirical') return {label:'empirical', note:'This edge is curated as empirical context; individual factual claims should still retain source/date provenance.'};
  if (lower.includes('empirical') && lower.includes('project')) return {label:'mixed empirical + project context', note:'The edge intentionally mixes an observable relation with project interpretation. Do not treat the project component as empirical proof.'};
  if (lower.includes('project')) return {label:'project interpretation', note:'This relation is project-context material unless separately evidenced in an empirical layer.'};
  return {label:layer, note:'This is a curated Atlas relation. Inspect its sources before treating any unstated mechanism or motive as fact.'};
}

function existingEndpointNames(raw) {
  const panel = document.getElementById(PANEL_ID);
  const heading = panel?.querySelector('h1')?.textContent || '';
  const names = heading.split('↔').map(value => value.trim()).filter(Boolean);
  return {
    a: names[0] || raw.a || 'A',
    b: names[1] || raw.b || 'B'
  };
}

function statusForDimension(dimension, guide) {
  if (dimension === 4) return 'explicit';
  if (guide[dimension]?.primary?.length) return 'primary';
  if (guide[dimension]?.conditional?.length) return 'conditional';
  return 'none';
}

function statusLabel(status) {
  if (status === 'explicit') return 'edge record';
  if (status === 'primary') return 'family-supported';
  if (status === 'conditional') return 'conditional';
  return 'not yet modeled';
}

function dimensionDetail(dimension, families, guide, matrix, raw) {
  const label = matrix.dimension_key?.[`D${dimension}`] || `Dimension ${dimension}`;
  const primary = guide[dimension]?.primary || [];
  const conditional = guide[dimension]?.conditional || [];

  if (dimension === 4) {
    return `
      <div class="card relation-dimension-card">
        <b>D4 · ${esc(label)}</b>
        <p class="muted">This is the relationship body: the currently rendered edge, its endpoints, curated type tags and layer. D4 does not by itself establish causation, motive, moral value or hidden coordination.</p>
        ${raw.note ? `<div class="row"><span class="muted">Edge note</span><br>${esc(raw.note)}</div>` : ''}
      </div>`;
  }

  if (!primary.length && !conditional.length) {
    return `
      <div class="card relation-dimension-card">
        <b>D${dimension} · ${esc(label)}</b>
        <p class="muted">The current edge tags do not justify a projection here yet. This is intentionally left sparse rather than manufacturing a dimension.</p>
        <p class="muted">An edge-specific <code>vertical_projection</code> or stronger typed relation data could activate this dimension later.</p>
      </div>`;
  }

  const rows = [];
  for (const family of [...new Set([...primary,...conditional])]) {
    const def = matrix.families?.[family];
    if (!def) continue;
    const strength = primary.includes(family) ? 'primary family guidance' : 'conditional family guidance';
    rows.push(`<div class="row"><span class="muted">${esc(title(family))} · ${esc(strength)}</span><br>${esc(def.reading || '')}</div>`);
  }

  const special = dimension === 6
    ? '<p class="muted"><b>Spiral gate:</b> a spiral/helix should only replace the direct edge when comparable dated recurrence or cycle data exists. Turns must encode measured/modelled recurrence, not decoration.</p>'
    : dimension === 8
      ? '<p class="muted"><b>Rooms gate:</b> alliances, institutions and group arrangements may eventually need a higher-order relation rather than pretending every collective rule is only pairwise.</p>'
      : dimension === 10
        ? '<p class="muted"><b>Mountain gate:</b> system effects are derived aggregates. Any future leverage, resilience or burden metric must expose method, inputs, time scope and information loss.</p>'
        : '';

  return `
    <div class="card relation-dimension-card">
      <b>D${dimension} · ${esc(label)}</b>
      <p class="muted">This is family-level projection guidance derived from the edge's curated type tags. It is not an edge-specific factual claim.</p>
      ${rows.join('')}
      ${special}
    </div>`;
}

function axisStrip(guide, matrix) {
  return `<div class="relation-axis-strip" aria-label="Relationship Axis projections">${Array.from({length:11},(_,index)=>{
    const dimension = index + 1;
    const status = statusForDimension(dimension, guide);
    const active = dimension === selectedDimension ? ' active' : '';
    const tooltip = matrix.dimension_key?.[`D${dimension}`] || '';
    return `<button class="relation-axis-d ${status}${active}" data-relation-d="${dimension}" title="D${dimension} · ${esc(tooltip)} · ${esc(statusLabel(status))}"><b>D${dimension}</b><span>${esc(statusLabel(status))}</span></button>`;
  }).join('')}</div>`;
}

function render(matrix) {
  if (!current) return;
  const panel = document.getElementById(PANEL_ID);
  if (!panel) return;

  const {raw, properties, names} = current;
  const types = edgeTypes(raw, properties);
  const families = inferFamilies(raw, properties, matrix);
  const guide = projectionGuide(families, matrix);
  const layer = layerReading(raw, properties);
  const hop = properties.depth || raw.trace_level || 1;
  const familyText = families.length ? families.map(title).join(' · ') : 'No family inferred from current tags';

  panel.innerHTML = `
    <div class="eyebrow">Relationship inspector · hop ${esc(hop)} · D4 body</div>
    <h1>${esc(names.a)} ↔ ${esc(names.b)}</h1>
    <div>${types.map(type => `<span class="pill">${esc(title(type))}</span>`).join('') || '<span class="pill">Relationship</span>'}</div>
    <div class="grid relation-summary-grid">
      <div class="metric"><span>Layer</span><b>${esc(layer.label)}</b><small>epistemic/context layer</small></div>
      <div class="metric"><span>Direction</span><b>Pairwise / unspecified</b><small>no directional flow inferred</small></div>
      <div class="metric"><span>Families</span><b>${families.length}</b><small>derived from current type tags</small></div>
      <div class="metric"><span>Trace hop</span><b>${esc(hop)}</b><small>from selected root</small></div>
    </div>
    <div class="actions">
      <button data-open-country="${esc(raw.a || properties.a || '')}">Open ${esc(names.a)}</button>
      <button data-open-country="${esc(raw.b || properties.b || '')}">Open ${esc(names.b)}</button>
      <button id="relationBackToTrace">Back to root trace</button>
    </div>
    <div class="card"><b>Relational families</b><div>${esc(familyText)}</div><p class="muted">These are cautious family hints derived from the current edge tags so the Axis can ask better questions. They do not overwrite the canonical edge.</p></div>
    <div class="relation-axis-legend"><span class="explicit">D4 record</span><span class="primary">family-supported</span><span class="conditional">conditional</span><span class="none">not modeled</span></div>
    ${axisStrip(guide, matrix)}
    ${dimensionDetail(selectedDimension, families, guide, matrix, raw)}
    <div class="boundary"><b>Boundary:</b> ${esc(layer.note)} A higher D-level is not a moral promotion, and a lower D-level is not a condemnation. Visibility, evidence, asymmetry, harm and integration remain separate observables.</div>
    <details class="card"><summary><b>Raw curated edge</b></summary><pre class="json">${esc(JSON.stringify(raw,null,2))}</pre></details>`;

  panel.querySelectorAll('[data-relation-d]').forEach(button => button.addEventListener('click', () => {
    selectedDimension = Number(button.dataset.relationD) || 4;
    render(matrix);
    window.dispatchEvent(new CustomEvent('potato-atlas-relation-axis-change', {
      detail: {dimension:selectedDimension, edge:raw, families}
    }));
  }));

  panel.querySelectorAll('[data-open-country]').forEach(button => button.addEventListener('click', () => {
    const code = button.dataset.openCountry;
    if (code && window.goCountry) window.goCountry(code);
  }));
  document.getElementById('relationBackToTrace')?.addEventListener('click', () => window.showOverview?.());
}

function installStyles() {
  if (document.getElementById('relationInspectorStyles')) return;
  const style = document.createElement('style');
  style.id = 'relationInspectorStyles';
  style.textContent = `
    .relation-summary-grid{margin-top:10px}
    .relation-axis-legend{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 5px;font-size:9px;color:var(--muted)}
    .relation-axis-legend span:before{content:'';display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:4px;border:1px solid #566}
    .relation-axis-legend .explicit:before{background:var(--accent);border-color:var(--accent)}
    .relation-axis-legend .primary:before{background:#73a7d8;border-color:#73a7d8}
    .relation-axis-legend .conditional:before{background:transparent;border-color:#e0bd78}
    .relation-axis-legend .none:before{background:#1b2424;border-color:#465252}
    .relation-axis-strip{display:grid;grid-template-columns:repeat(11,minmax(0,1fr));gap:3px;margin:6px 0 10px}
    .relation-axis-d{min-width:0;padding:5px 2px!important;border-radius:7px!important;text-align:center!important;background:#111919!important;color:#849292!important}
    .relation-axis-d b{display:block;font-size:9px}.relation-axis-d span{display:none}
    .relation-axis-d.explicit{border-color:var(--accent)!important;color:var(--accent)!important;background:#15231c!important}
    .relation-axis-d.primary{border-color:#4e779a!important;color:#9bc8ea!important;background:#121e28!important}
    .relation-axis-d.conditional{border-color:#806c3e!important;color:#dbc27f!important;background:#201c12!important}
    .relation-axis-d.active{outline:2px solid #eff4eb66;transform:translateY(-1px)}
    .relation-axis-d.none{opacity:.5}
    .relation-dimension-card code{font-size:10px}
    @media(max-width:900px){.relation-axis-strip{gap:2px}.relation-axis-d{padding:4px 1px!important}.relation-axis-d b{font-size:8px}}
  `;
  document.head.appendChild(style);
}

function emptySelection() {
  return {type:'FeatureCollection',features:[]};
}

function ensureHighlightLayer(map) {
  if (!map.getSource(SOURCE_ID)) map.addSource(SOURCE_ID,{type:'geojson',data:emptySelection()});
  if (!map.getLayer(LAYER_ID)) {
    map.addLayer({
      id:LAYER_ID,
      type:'line',
      source:SOURCE_ID,
      paint:{
        'line-color':'#f0d77e',
        'line-width':['interpolate',['linear'],['zoom'],2,3.5,6,6],
        'line-opacity':.95,
        'line-blur':.2
      }
    });
  }
}

function setHighlight(map, feature) {
  ensureHighlightLayer(map);
  map.getSource(SOURCE_ID)?.setData(feature ? {type:'FeatureCollection',features:[{
    type:'Feature',
    properties:{selected:true},
    geometry:feature.geometry
  }]} : emptySelection());
}

function clearSelection() {
  current = null;
  selectedDimension = 4;
  if (installedMap) setHighlight(installedMap,null);
}

async function inspectRelation(event) {
  const feature = event.features?.[0];
  if (!feature) return;
  const raw = parseRaw(feature.properties || {});
  const names = existingEndpointNames(raw);
  current = {raw, properties:feature.properties || {}, names, geometry:feature.geometry};
  selectedDimension = 4;
  setHighlight(installedMap,feature);

  const panel = document.getElementById(PANEL_ID);
  if (panel) panel.insertAdjacentHTML('beforeend','<div id="relationInspectorLoading" class="muted">Loading Axis relation model…</div>');

  try {
    const matrix = await loadMatrix();
    if (!current || current.raw !== raw) return;
    render(matrix);
  } catch (error) {
    console.warn('Relationship projection guidance unavailable:',error);
    document.getElementById('relationInspectorLoading')?.remove();
  }
}

async function boot() {
  for (let i=0;i<160&&!window.__potatoAtlasMap;i+=1) await new Promise(resolve=>setTimeout(resolve,50));
  const map = window.__potatoAtlasMap;
  if (!map) return;
  if (!map.loaded()) await new Promise(resolve=>map.once('load',resolve));
  for (let i=0;i<80&&!map.getLayer('relations');i+=1) await new Promise(resolve=>setTimeout(resolve,50));
  if (!map.getLayer('relations')) return;

  installedMap = map;
  installStyles();
  ensureHighlightLayer(map);

  // 3d-app registered its relation click handler first. This handler therefore
  // sees the human-readable endpoint heading produced by core and upgrades the
  // same inspector instead of changing the core renderer contract.
  map.on('click','relations',inspectRelation);
  map.on('click',event=>{
    const hits = map.queryRenderedFeatures(event.point,{layers:['relations']});
    if (!hits.length && current) clearSelection();
  });

  window.__potatoAtlasRelationInspector = {
    clear:clearSelection,
    get selection(){return current;},
    get dimension(){return selectedDimension;}
  };
}

boot().catch(error=>console.warn('Relationship inspector unavailable:',error));
