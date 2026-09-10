const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

const toolbar = document.querySelector('.top');
const anchor = $('#tilt');
const input = document.createElement('input');
input.id = 'pathTarget';
input.setAttribute('list', 'country-list');
input.setAttribute('placeholder', 'Path to country…');
input.setAttribute('aria-label', 'Find relationship path to country');
input.title = 'Find the shortest known path from the selected country using the current relation-type filter';
const button = document.createElement('button');
button.id = 'pathFind';
button.textContent = 'Path';
button.title = 'Find shortest typed relationship path';
toolbar.insertBefore(input, anchor);
toolbar.insertBefore(button, anchor);

const style = document.createElement('style');
style.textContent = `.path-result{position:absolute;right:12px;bottom:12px;z-index:4;width:min(520px,calc(100% - 24px));max-height:46%;overflow:auto;background:#080b0bf2;border:1px solid var(--line);border-radius:10px;padding:11px}.path-result[hidden]{display:none}.path-head{display:flex;justify-content:space-between;gap:8px;align-items:center}.path-steps{display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin:9px 0}.path-step{background:var(--panel2);border:1px solid var(--line);color:var(--ink);padding:5px 7px;border-radius:7px}.path-arrow{color:var(--muted)}.path-edge{padding:6px 0;border-top:1px solid var(--line);font-size:12px}@media(max-width:900px){.path-result{position:fixed;bottom:10px;right:10px;left:10px;width:auto;max-height:40vh}}`;
document.head.appendChild(style);

const box = document.createElement('section');
box.id = 'pathResult';
box.className = 'path-result';
box.hidden = true;
document.querySelector('.mapwrap').appendChild(box);

let worldCfg = null;
let countries = [];
let by3 = {};

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return response.json();
}

function normalizeFacts(payload) {
  const rows = payload?.countries || {};
  return Object.entries(rows).map(([cca3, row]) => ({
    cca3,
    name: {
      common: row?.name || cca3,
      official: row?.official_name || row?.name || cca3,
    },
  }));
}

async function loadCountryNames() {
  try {
    const facts = await fetchJson('../data/world-country-facts.json');
    const normalized = normalizeFacts(facts);
    if (normalized.length >= 190) return normalized;
    throw new Error(`local facts coverage too low: ${normalized.length}`);
  } catch (localError) {
    console.warn('Local country facts unavailable for Path; trying REST Countries', localError);
    const live = await fetchJson('https://restcountries.com/v3.1/all?fields=name,cca3');
    if (!Array.isArray(live) || live.filter(x => x?.cca3).length < 190) {
      throw new Error('REST Countries pathfinder coverage unexpectedly low');
    }
    return live;
  }
}

try {
  const [world, countryRows] = await Promise.all([
    fetchJson('../data/world-relational-map.json'),
    loadCountryNames(),
  ]);
  worldCfg = world;
  countries = countryRows;
  by3 = Object.fromEntries(countries.filter(x => x.cca3).map(x => [x.cca3, x]));
} catch (error) {
  console.warn('Path finder unavailable', error);
  button.disabled = true;
  button.title = 'Path finder data could not be loaded';
}

function nameFor(code) { return by3[code]?.name?.common || code; }
function currentRoot() { return new URL(location.href).searchParams.get('country')?.toUpperCase() || null; }
function currentType() { return $('#relationType')?.value || 'all'; }
function filteredEdges() {
  const type = currentType();
  return (worldCfg?.curated_edges || []).filter(e => type === 'all' || (e.types || []).includes(type));
}
function resolveCountry(query) {
  const q = String(query || '').trim().toLowerCase();
  if (!q) return null;
  const bracket = q.match(/\(([a-z]{3})\)$/i)?.[1];
  const code = (bracket || q).toUpperCase();
  if (by3[code]) return code;
  const exact = countries.find(x => x.name?.common?.toLowerCase() === q || x.name?.official?.toLowerCase() === q);
  if (exact) return exact.cca3;
  return countries.find(x => x.name?.common?.toLowerCase().includes(q) || x.name?.official?.toLowerCase().includes(q))?.cca3 || null;
}
function shortestPath(start, target) {
  if (!start || !target) return null;
  if (start === target) return {codes:[start], edges:[]};
  const adjacency = new Map();
  for (const edge of filteredEdges()) {
    if (!adjacency.has(edge.a)) adjacency.set(edge.a, []);
    if (!adjacency.has(edge.b)) adjacency.set(edge.b, []);
    adjacency.get(edge.a).push({next:edge.b, edge});
    adjacency.get(edge.b).push({next:edge.a, edge});
  }
  const queue = [start];
  const seen = new Set([start]);
  const parent = new Map();
  while (queue.length) {
    const code = queue.shift();
    for (const step of adjacency.get(code) || []) {
      if (seen.has(step.next)) continue;
      seen.add(step.next);
      parent.set(step.next, {code, edge:step.edge});
      if (step.next === target) {
        const codes = [target], edges = [];
        let cursor = target;
        while (cursor !== start) {
          const p = parent.get(cursor);
          if (!p) return null;
          edges.push(p.edge);
          cursor = p.code;
          codes.push(cursor);
        }
        return {codes:codes.reverse(), edges:edges.reverse()};
      }
      queue.push(step.next);
    }
  }
  return null;
}
function closePath() {
  box.hidden = true;
  const u = new URL(location.href);
  u.searchParams.delete('path');
  history.replaceState({}, '', u);
}
window.closeAtlasPath = closePath;
function renderPath(start, target, path) {
  const type = currentType();
  if (!path) {
    box.hidden = false;
    box.innerHTML = `<div class="path-head"><b>No known path</b><button onclick="closeAtlasPath()">×</button></div><p class="muted">No route from ${esc(nameFor(start))} to ${esc(nameFor(target))} exists in the currently curated graph${type === 'all' ? '' : ` with relation type “${esc(type)}”`}. This means “not represented in this dataset,” not “no real-world relationship exists.”</p>`;
    return;
  }
  const steps = path.codes.map((code, i) => `${i ? '<span class="path-arrow">→</span>' : ''}<button class="path-step" onclick="goCountry('${esc(code)}')">${esc(nameFor(code))}</button>`).join('');
  const edgeRows = path.edges.map((edge, i) => `<div class="path-edge"><b>${i + 1}. ${esc(nameFor(path.codes[i]))} ↔ ${esc(nameFor(path.codes[i+1]))}</b><div class="muted">${esc((edge.types || []).join(' · ') || edge.layer || 'relation')} · ${esc(edge.layer || 'curated')}</div></div>`).join('');
  box.hidden = false;
  box.innerHTML = `<div class="path-head"><div><b>Shortest known relationship path</b><div class="muted">${path.edges.length} hop${path.edges.length === 1 ? '' : 's'} · ${type === 'all' ? 'all relation types' : esc(type)}</div></div><button onclick="closeAtlasPath()">×</button></div><div class="path-steps">${steps}</div>${edgeRows}<div class="boundary">This is shortest path in the curated graph under the active filter, not necessarily the shortest or strongest relationship in the real world.</div>`;
}
function runPath(targetValue=input.value, persist=true) {
  const start = currentRoot();
  const target = resolveCountry(targetValue);
  if (!start) {
    box.hidden = false;
    box.innerHTML = '<div class="path-head"><b>Select a starting country first</b><button onclick="closeAtlasPath()">×</button></div><p class="muted">Click or search for a country, then choose a destination.</p>';
    return;
  }
  if (!target) {
    box.hidden = false;
    box.innerHTML = '<div class="path-head"><b>Destination not found</b><button onclick="closeAtlasPath()">×</button></div><p class="muted">Choose a country name or ISO3 code from the suggestions.</p>';
    return;
  }
  input.value = `${nameFor(target)} (${target})`;
  const path = shortestPath(start, target);
  renderPath(start, target, path);
  if (persist) {
    const u = new URL(location.href);
    u.searchParams.set('path', `${start},${target}`);
    history.replaceState({}, '', u);
  }
}
button.addEventListener('click', () => runPath());
input.addEventListener('keydown', e => { if (e.key === 'Enter') runPath(); });
$('#relationType')?.addEventListener('change', () => {
  if (!box.hidden && input.value) runPath(input.value, false);
});

const restored = new URL(location.href).searchParams.get('path');
if (restored && worldCfg) {
  const [start, target] = restored.split(',').map(x => x?.toUpperCase());
  if (start && target) {
    const current = currentRoot();
    if (current === start) runPath(target, false);
  }
}
