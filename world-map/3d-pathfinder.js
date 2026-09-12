const selection = window.__potatoAtlasSelection;
if (!selection) throw new Error('Path requires current selection API.');

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
let worldCfg = null;
let currentPath = null;

async function fetchJson(url) {
  const response = await fetch(url, { cache:'no-cache' });
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return response.json();
}

try {
  worldCfg = await fetchJson('../data/world-relational-map.json');
} catch (error) {
  console.warn('Path finder unavailable', error);
}

function currentRoot() { return selection.current?.activeCode || selection.current?.code || null; }
function currentMode() { return selection.getRelationMode?.() || 'all'; }
function filteredEdges() {
  const mode = currentMode();
  return (worldCfg?.curated_edges || []).filter(edge => selection.edgeMatchesRelationMode?.(edge, mode) ?? true);
}
function nameFor(code) { return selection.countryName?.(code) || code; }
function resolveCountry(query) {
  const raw = String(query || '').trim();
  if (!raw) return null;
  const bracket = raw.match(/\(([A-Za-z]{3})\)$/)?.[1];
  const direct = String(bracket || raw).toUpperCase();
  const candidates = new Set();
  for (const edge of worldCfg?.curated_edges || []) { candidates.add(edge.a); candidates.add(edge.b); }
  for (const code of selection.current?.selectedCodes || []) candidates.add(code);
  if (/^[A-Z]{3}$/.test(direct) && (candidates.has(direct) || nameFor(direct) !== direct)) return direct;
  const lower = raw.toLowerCase();
  const exact = [...candidates].find(code => String(nameFor(code)).toLowerCase() === lower);
  if (exact) return exact;
  return [...candidates].find(code => String(nameFor(code)).toLowerCase().includes(lower)) || null;
}

function shortestPath(start, target) {
  if (!start || !target) return null;
  if (start === target) return { codes:[start], edges:[] };
  const adjacency = new Map();
  for (const edge of filteredEdges()) {
    if (!adjacency.has(edge.a)) adjacency.set(edge.a, []);
    if (!adjacency.has(edge.b)) adjacency.set(edge.b, []);
    adjacency.get(edge.a).push({ next:edge.b, edge });
    adjacency.get(edge.b).push({ next:edge.a, edge });
  }
  for (const rows of adjacency.values()) rows.sort((a,b) => String(a.next).localeCompare(String(b.next)));
  const queue = [start];
  const seen = new Set([start]);
  const parent = new Map();
  while (queue.length) {
    const code = queue.shift();
    for (const step of adjacency.get(code) || []) {
      if (seen.has(step.next)) continue;
      seen.add(step.next);
      parent.set(step.next, { code, edge:step.edge });
      if (step.next === target) {
        const codes = [target], edges = [];
        let cursor = target;
        while (cursor !== start) {
          const previous = parent.get(cursor);
          if (!previous) return null;
          edges.push(previous.edge);
          cursor = previous.code;
          codes.push(cursor);
        }
        return { codes:codes.reverse(), edges:edges.reverse() };
      }
      queue.push(step.next);
    }
  }
  return null;
}

function install() {
  if (document.getElementById('atlasPathContext')) return;
  const style = document.createElement('style');
  style.id = 'atlasPathStyle';
  style.textContent = `
    #atlasPathContext{position:absolute;right:10px;bottom:10px;z-index:8;width:min(430px,calc(100% - 20px));max-height:min(58vh,560px);overflow:auto;padding:11px 12px;background:#080c0ced;border:1px solid #465754;border-radius:11px;box-shadow:0 10px 28px #0009;backdrop-filter:blur(11px)}#atlasPathContext[hidden]{display:none!important}.path-head{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}.path-head small{display:block;color:#83918b;font-size:8px;text-transform:uppercase;letter-spacing:.1em}.path-head b{display:block;color:#eee2b4;font-size:14px;margin-top:2px}.path-close{border:0;background:transparent;color:#98a49e;font-size:16px;cursor:pointer}.path-form{display:flex;gap:5px;margin-top:9px}.path-form input{flex:1;min-width:0;padding:7px 8px;border:1px solid #344440;border-radius:7px;background:#101616;color:#e8efea}.path-form button{padding:7px 9px;border:1px solid #344440;border-radius:7px;background:#15201e;color:#d9e7df}.path-steps{display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin:9px 0}.path-step{background:#131c1b;border:1px solid #344440;color:#dfe8e3;padding:5px 7px;border-radius:7px;cursor:pointer}.path-arrow{color:#83918b}.path-edge{padding:6px 0;border-top:1px solid #263230;font-size:10px}.path-edge span{display:block;margin-top:2px;color:#8f9c96}.path-boundary{margin-top:9px;padding-top:7px;border-top:1px solid #33413f;color:#77847e;font-size:9px;line-height:1.35}.path-empty{margin-top:9px;color:#9aa6a0;font-size:10px;line-height:1.4}@media(max-width:900px){#atlasPathContext{right:8px;bottom:58px;width:min(400px,calc(100% - 16px));max-height:48vh}}
  `;
  document.head.appendChild(style);
  const box = document.createElement('section');
  box.id = 'atlasPathContext';
  box.hidden = true;
  box.innerHTML = `<div class="path-head"><div><small>Shortest represented path</small><b data-path-title>Select a destination</b></div><button type="button" class="path-close" data-path-clear aria-label="Clear path">×</button></div><form class="path-form" data-path-form><input data-path-target list="country-list" placeholder="Path to country…" aria-label="Find represented relationship path"><button type="submit">Find</button></form><div data-path-result></div>`;
  document.querySelector('.mapwrap')?.appendChild(box);
  box.addEventListener('click', event => {
    if (event.target.closest('[data-path-clear]')) { clear(); return; }
    const code = event.target.closest('[data-path-code]')?.dataset.pathCode;
    if (code) selection.activate?.(code, { add:false });
  });
  box.querySelector('[data-path-form]')?.addEventListener('submit', event => {
    event.preventDefault();
    const value = box.querySelector('[data-path-target]')?.value || '';
    run(value);
  });
}

function box() { return document.getElementById('atlasPathContext'); }
function resultNode() { return box()?.querySelector('[data-path-result]'); }
function targetInput() { return box()?.querySelector('[data-path-target]'); }
function titleNode() { return box()?.querySelector('[data-path-title]'); }
function persist(start, target) {
  const url = new URL(location.href);
  if (start && target) url.searchParams.set('path', `${start},${target}`);
  else url.searchParams.delete('path');
  history.replaceState({}, '', url);
}

function renderPath(start, target, path) {
  const node = resultNode();
  if (!node) return;
  const mode = currentMode();
  if (titleNode()) titleNode().textContent = `${nameFor(start)} → ${nameFor(target)}`;
  if (!path) {
    node.innerHTML = `<div class="path-empty">No represented path from ${esc(nameFor(start))} to ${esc(nameFor(target))}${mode === 'all' ? '' : ` under the ${esc(mode)} filter`}. This means “not represented in this dataset,” not “no real-world relationship exists.”</div><div class="path-boundary">This is a shortest path in the represented graph under the active filter, not necessarily the shortest or strongest relationship in the real world.</div>`;
    return;
  }
  const steps = path.codes.map((code, index) => `${index ? '<span class="path-arrow">→</span>' : ''}<button type="button" class="path-step" data-path-code="${esc(code)}">${esc(nameFor(code))}</button>`).join('');
  const rows = path.edges.map((edge, index) => `<div class="path-edge"><b>${index + 1}. ${esc(nameFor(path.codes[index]))} ↔ ${esc(nameFor(path.codes[index + 1]))}</b><span>${esc((edge.types || []).join(' · ') || edge.layer || 'relation')} · ${esc(edge.layer || 'curated')}</span></div>`).join('');
  node.innerHTML = `<div class="path-steps">${steps}</div>${rows}<div class="path-boundary">${path.edges.length} hop${path.edges.length === 1 ? '' : 's'} · ${mode === 'all' ? 'all relation modes' : esc(mode)}. This is a shortest path in the represented graph under the active filter, not necessarily the shortest or strongest relationship in the real world.</div>`;
}

function showFor(sourceCode = currentRoot()) {
  install();
  const source = String(sourceCode || '').toUpperCase();
  if (!source) return false;
  const node = box();
  node.hidden = false;
  currentPath = { source, target:null };
  if (titleNode()) titleNode().textContent = `From ${nameFor(source)}`;
  if (resultNode()) resultNode().innerHTML = '<div class="path-empty">Choose a destination to inspect the shortest represented relationship path.</div>';
  targetInput()?.focus();
  return true;
}

function run(targetValue, { persistState=true } = {}) {
  install();
  const start = currentPath?.source || currentRoot();
  const target = resolveCountry(targetValue);
  const node = box();
  node.hidden = false;
  if (!start) {
    resultNode().innerHTML = '<div class="path-empty">Select a starting country first.</div>';
    return false;
  }
  if (!target) {
    resultNode().innerHTML = '<div class="path-empty">Destination not found in the represented relationship graph.</div>';
    return false;
  }
  const path = shortestPath(start, target);
  currentPath = { source:start, target };
  if (targetInput()) targetInput().value = `${nameFor(target)} (${target})`;
  renderPath(start, target, path);
  if (persistState) persist(start, target);
  window.dispatchEvent(new CustomEvent('potato-atlas-path-change', { detail:{ source:start, target, path, mode:currentMode() } }));
  return true;
}

function clear() {
  currentPath = null;
  if (box()) box().hidden = true;
  persist(null, null);
  window.dispatchEvent(new CustomEvent('potato-atlas-path-change', { detail:{ source:null, target:null, path:null, mode:currentMode() } }));
  return true;
}
function current() { return currentPath ? { ...currentPath } : null; }

install();
window.__potatoAtlasPath = { showFor, run, clear, current, shortestPath };
window.addEventListener('potato-atlas-relation-mode-change', () => {
  if (currentPath?.target) run(currentPath.target, { persistState:false });
});

const restored = new URL(location.href).searchParams.get('path');
if (restored && worldCfg) {
  const [start, target] = restored.split(',').map(value => String(value || '').toUpperCase());
  if (start && target) {
    showFor(start);
    run(target, { persistState:false });
  } else {
    clear();
  }
}
