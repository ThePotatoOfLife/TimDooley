// Optional 3D metric extension for the World Relational Atlas.
//
// Adds a sourced graph-density height mode without expanding the persistent UI.
// The value is deliberately named "represented relationships": it counts edges
// present in the repository's curated world graph, not all real-world relations
// and not a country's importance, power, value, or influence.

const map = window.__potatoAtlasMap;
const heightSelect = document.getElementById('height');
const relationTypeSelect = document.getElementById('relationType');
const viewMenu = document.getElementById('viewMenu');

if (!map || !heightSelect) throw new Error('3D metric dimensions require the core atlas map and Height selector.');

const WORLD_GRAPH_URL = '../data/world-relational-map.json';
const HEIGHT_SCALE_METERS = 180000;
let worldGraph = null;
let relationshipOption = null;
let note = null;

function currentTimeState() {
  return window.__potatoAtlasTime?.getState?.() || { mode: 'current' };
}

function activeRelationType() {
  const value = relationTypeSelect?.value || 'all';
  return value || 'all';
}

function edgeMatches(edge, relationType) {
  if (relationType === 'all') return true;
  return Array.isArray(edge?.types) && edge.types.includes(relationType);
}

function relationshipCounts(relationType = activeRelationType()) {
  const counts = new Map();
  for (const edge of worldGraph?.curated_edges || []) {
    if (!edgeMatches(edge, relationType)) continue;
    for (const code of [edge?.a, edge?.b]) {
      if (!/^[A-Z]{3}$/.test(String(code || ''))) continue;
      counts.set(code, (counts.get(code) || 0) + 1);
    }
  }
  return counts;
}

function countExpression(counts) {
  const match = ['match', ['get', 'iso3']];
  for (const [code, count] of [...counts.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    match.push(code, count);
  }
  match.push(0);
  return match;
}

function setRelationshipHeight() {
  if (!worldGraph || !map.getLayer('countries-extrude')) return;
  const counts = relationshipCounts();
  const expression = countExpression(counts);
  map.setPaintProperty('countries-extrude', 'fill-extrusion-height', [
    '*', HEIGHT_SCALE_METERS,
    ['sqrt', ['max', expression, 0]],
  ]);
}

function ensureOption() {
  relationshipOption = [...heightSelect.options].find(option => option.value === 'relationships') || null;
  if (!relationshipOption) {
    relationshipOption = document.createElement('option');
    relationshipOption.value = 'relationships';
    relationshipOption.textContent = 'Height · represented relationships';
    heightSelect.appendChild(relationshipOption);
  }
}

function ensureNote() {
  if (note) return note;
  note = document.createElement('div');
  note.id = 'relationshipHeightNote';
  note.className = 'boundary';
  note.hidden = true;
  note.style.marginTop = '7px';
  note.style.fontSize = '10px';
  heightSelect.insertAdjacentElement('afterend', note);
  return note;
}

function updateNote() {
  const node = ensureNote();
  const active = heightSelect.value === 'relationships';
  node.hidden = !active;
  if (!active) return;
  const type = activeRelationType();
  const counts = relationshipCounts(type);
  const representedCountries = [...counts.values()].filter(value => value > 0).length;
  const representedEdges = (worldGraph?.curated_edges || []).filter(edge => edgeMatches(edge, type)).length;
  const filterText = type === 'all' ? 'all represented types' : `type: ${type}`;
  node.textContent = `Represented graph links · ${representedEdges} curated edges across ${representedCountries} countries · ${filterText}. Height uses √(edge count) scaling. Source: world-relational-map.json. This is dataset coverage/connectivity, not a country rank.`;
}

function applyMode() {
  const historical = currentTimeState().mode !== 'current';
  if (relationshipOption) relationshipOption.disabled = historical;

  if (historical && heightSelect.value === 'relationships') {
    heightSelect.value = 'flat';
    heightSelect.dispatchEvent(new Event('change', { bubbles: true }));
    return;
  }

  if (heightSelect.value === 'relationships') setRelationshipHeight();
  updateNote();
}

async function loadWorldGraph() {
  const response = await fetch(WORLD_GRAPH_URL);
  if (!response.ok) throw new Error(`${WORLD_GRAPH_URL} returned HTTP ${response.status}`);
  const payload = await response.json();
  if (!Array.isArray(payload?.curated_edges)) throw new Error('World relational graph has no curated_edges array.');
  return payload;
}

ensureOption();
ensureNote();
worldGraph = await loadWorldGraph();

// The core renderer's existing Height handler runs first and owns flat,
// population and area. This listener only supplies the extra relationship mode.
heightSelect.addEventListener('change', applyMode);
relationTypeSelect?.addEventListener('change', () => {
  if (heightSelect.value === 'relationships') setRelationshipHeight();
  updateNote();
});
window.addEventListener('atlas-time-change', applyMode);
window.addEventListener('potato-atlas-time-change', applyMode);

// If View was opened to load this module, keep its summary/controller in sync.
viewMenu?.dispatchEvent(new Event('change', { bubbles: true }));
applyMode();

window.__potatoAtlasMetricDimensions = {
  relationshipCounts,
  refresh: applyMode,
  get mode() { return heightSelect.value; },
};
