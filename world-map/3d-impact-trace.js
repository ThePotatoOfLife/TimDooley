// Evidence-first dependency impact tracing for the World Relational Atlas.
// Dependency edges point dependent -> dependency. This module traverses incoming
// explicit causal edges only; generic connectivity and membership stay context.
const map = window.__potatoAtlasMap;
const runtime = window.__potatoAtlasDataRuntime;
if (!map || !runtime) throw new Error('Impact Trace requires the map and shared runtime APIs.');
await runtime.ready;

const LAYER_ID = 'atlas-impact-outline';
const ROOT_STATE = 'atlasImpactRoot';
const DIRECT_STATE = 'atlasImpactDirect';
const SECOND_STATE = 'atlasImpactSecond';
const MAX_ROWS = 12;
const IMPORTANCE = new Map([['critical',0],['high',1],['medium',2],['low',3]]);
let activeImpactId = null;
let markedCodes = new Set();

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const dataReady = runtime.ready;

runtime.impactNode = async function impactNode(id) {
  const data = await dataReady;
  return data?.impact?.nodes?.[String(id || '')] || null;
};
runtime.impactNodeForEntity = async function impactNodeForEntity(code) {
  const data = await dataReady;
  const key = String(code || '').toUpperCase();
  const countryId = `country:${key}`;
  const territoryId = `territory:${key}`;
  if (data?.impact?.nodes?.[countryId]) return countryId;
  if (data?.impact?.nodes?.[territoryId]) return territoryId;
  return null;
};
runtime.impactNodeForGateway = async function impactNodeForGateway(id) {
  const data = await dataReady;
  const nodeId = `gateway:${String(id || '')}`;
  return data?.impact?.nodes?.[nodeId] ? nodeId : null;
};
runtime.impactNodeForChain = async function impactNodeForChain(id) {
  const data = await dataReady;
  const nodeId = `chain:${String(id || '')}`;
  return data?.impact?.nodes?.[nodeId] ? nodeId : null;
};

function rowOrder(row) {
  const importance = String(row?.edge?.importance || '').toLowerCase();
  return [IMPORTANCE.get(importance) ?? 4, String(row?.node?.label || row?.node?.id || '').toLowerCase(), String(row?.node?.id || '')];
}
function compareRows(a, b) {
  const aa = rowOrder(a), bb = rowOrder(b);
  return aa[0] - bb[0] || aa[1].localeCompare(bb[1]) || aa[2].localeCompare(bb[2]);
}

runtime.impactFor = async function impactFor(id) {
  const data = await dataReady;
  const impact = data?.impact || {};
  const nodes = impact.nodes || {};
  const edges = impact.edges || [];
  const rootId = String(id || '');
  const root = nodes[rootId];
  if (!root) return null;

  const incoming = new Map();
  for (const edge of edges) {
    if (edge?.causal_status !== 'explicit-dependency') continue;
    if (!nodes[edge.source] || !nodes[edge.target]) continue;
    if (!incoming.has(edge.target)) incoming.set(edge.target, []);
    incoming.get(edge.target).push(edge);
  }
  const directAll = [];
  const directIds = new Set();
  for (const edge of incoming.get(rootId) || []) {
    if (edge.source === rootId || directIds.has(edge.source)) continue;
    directIds.add(edge.source);
    directAll.push({ node:nodes[edge.source], edge });
  }
  directAll.sort(compareRows);

  const secondAll = [];
  const secondIds = new Set();
  for (const direct of directAll) {
    const via = direct.node.id;
    for (const edge of incoming.get(via) || []) {
      if (edge.source === rootId || directIds.has(edge.source) || secondIds.has(edge.source)) continue;
      secondIds.add(edge.source);
      secondAll.push({ node:nodes[edge.source], edge, via });
    }
  }
  secondAll.sort(compareRows);

  const alternatives = edges
    .filter(edge => edge?.source === rootId && edge?.causal_status === 'explicit-alternative' && nodes[edge.target])
    .map(edge => ({ node:nodes[edge.target], edge }))
    .sort(compareRows);

  const contextIds = new Set(impact.context_chains?.[rootId] || []);
  for (const row of [...directAll, ...secondAll]) {
    for (const chainId of impact.context_chains?.[row.node.id] || []) contextIds.add(chainId);
  }
  if (root.kind === 'functional-chain') contextIds.add(rootId);
  const contextChains = [...contextIds].map(chainId => nodes[chainId]).filter(Boolean).sort((a,b) => String(a.label).localeCompare(String(b.label)));

  return {
    root,
    direct:directAll.slice(0, MAX_ROWS),
    directOverflow:Math.max(0, directAll.length - MAX_ROWS),
    secondOrder:secondAll.slice(0, MAX_ROWS),
    secondOrderOverflow:Math.max(0, secondAll.length - MAX_ROWS),
    alternatives,
    contextChains,
    boundary:'represented-dependencies-not-forecast',
  };
};

function ensureLayer() {
  if (map.getLayer(LAYER_ID)) return;
  const before = map.getLayer('countries-line') ? 'countries-line' : (map.getLayer('countries-outline') ? 'countries-outline' : undefined);
  map.addLayer({
    id:LAYER_ID,
    type:'line',
    source:'countries',
    paint:{
      'line-color':['case',
        ['boolean',['feature-state',ROOT_STATE],false], '#f0d58c',
        ['boolean',['feature-state',DIRECT_STATE],false], '#b7d3c4',
        ['boolean',['feature-state',SECOND_STATE],false], '#7f9d96',
        '#7f9d96'],
      'line-width':['case',
        ['boolean',['feature-state',ROOT_STATE],false], 4,
        ['boolean',['feature-state',DIRECT_STATE],false], 3,
        ['boolean',['feature-state',SECOND_STATE],false], 2,
        0],
      'line-opacity':['case',
        ['boolean',['feature-state',ROOT_STATE],false], .95,
        ['boolean',['feature-state',DIRECT_STATE],false], .82,
        ['boolean',['feature-state',SECOND_STATE],false], .55,
        0],
      'line-blur':.35,
    },
  }, before);
}

function nodeCode(node) {
  return ['country','territory'].includes(node?.kind) && /^[A-Z]{3}$/.test(String(node?.code || '')) ? node.code : null;
}
function setState(code, patch) {
  if (!code) return;
  try { map.setFeatureState({ source:'countries', id:code }, patch); } catch {}
  markedCodes.add(code);
}
function clearStates() {
  for (const code of markedCodes) {
    try { map.setFeatureState({ source:'countries', id:code }, { [ROOT_STATE]:false, [DIRECT_STATE]:false, [SECOND_STATE]:false }); } catch {}
  }
  markedCodes = new Set();
}
function applyStates(result) {
  clearStates();
  setState(nodeCode(result?.root), { [ROOT_STATE]:true, [DIRECT_STATE]:false, [SECOND_STATE]:false });
  for (const row of result?.direct || []) setState(nodeCode(row.node), { [ROOT_STATE]:false, [DIRECT_STATE]:true, [SECOND_STATE]:false });
  for (const row of result?.secondOrder || []) setState(nodeCode(row.node), { [ROOT_STATE]:false, [DIRECT_STATE]:false, [SECOND_STATE]:true });
}

function persist(id) {
  const url = new URL(location.href);
  if (id) url.searchParams.set('impact', id);
  else url.searchParams.delete('impact');
  history.replaceState({}, '', url);
}
function panel() { return document.getElementById('atlasImpactContext'); }
function ensurePanel() {
  let node = panel();
  if (node) return node;
  const style = document.createElement('style');
  style.id = 'atlasImpactTraceStyle';
  style.textContent = `
    #atlasImpactContext{position:absolute;right:10px;bottom:10px;z-index:8;width:min(370px,calc(100% - 20px));max-height:min(65vh,600px);overflow:auto;padding:11px 12px;background:#080c0ced;border:1px solid #465754;border-radius:11px;box-shadow:0 10px 28px #0009;backdrop-filter:blur(11px)}#atlasImpactContext[hidden]{display:none!important}
    .impact-head{display:flex;justify-content:space-between;gap:8px}.impact-head small,.impact-section>small{display:block;color:#83918b;font-size:8px;text-transform:uppercase;letter-spacing:.1em}.impact-head b{display:block;color:#eee2b4;font-size:14px;margin-top:2px}.impact-close{border:0;background:transparent;color:#98a49e;font-size:16px;cursor:pointer}.impact-section{margin-top:9px;padding-top:7px;border-top:1px solid #263230}.impact-row{padding:5px 0;border-bottom:1px solid #1e2927}.impact-row:last-child{border:0}.impact-row b{display:block;font-size:10px}.impact-row span{display:block;margin-top:2px;color:#8f9c96;font-size:9px;line-height:1.35}.impact-more{color:#77847e;font-size:9px;margin-top:4px}.impact-tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:5px}.impact-tag{border:1px solid #344440;border-radius:999px;padding:2px 6px;color:#b8c4be;font-size:9px}.impact-boundary{margin-top:10px;padding-top:7px;border-top:1px solid #33413f;color:#77847e;font-size:9px;line-height:1.35}@media(max-width:900px){#atlasImpactContext{right:8px;bottom:58px;width:min(340px,calc(100% - 16px));max-height:52vh}}
  `;
  document.head.appendChild(style);
  node = document.createElement('aside');
  node.id = 'atlasImpactContext';
  node.hidden = true;
  node.setAttribute('aria-live','polite');
  document.querySelector('.mapwrap')?.appendChild(node);
  return node;
}

function detailFor(row) {
  const bits = [];
  if (row?.edge?.importance) bits.push(String(row.edge.importance));
  if (row?.edge?.mechanism) bits.push(String(row.edge.mechanism));
  if (row?.via) bits.push(`via ${row.via.split(':').slice(1).join(':')}`);
  return bits.join(' · ');
}
function rowsHtml(rows, overflow = 0) {
  if (!rows?.length) return '<div class="impact-row"><span>No explicit represented dependency reaches this node at this depth.</span></div>';
  return `${rows.map(row => `<div class="impact-row"><b>${esc(row.node.label || row.node.id)}</b>${detailFor(row) ? `<span>${esc(detailFor(row))}</span>` : ''}</div>`).join('')}${overflow ? `<div class="impact-more">+${overflow} more represented dependencies</div>` : ''}`;
}
function alternativesHtml(rows) {
  if (!rows?.length) return '';
  return `<div class="impact-section"><small>Known alternatives</small>${rows.map(row => `<div class="impact-row"><b>${esc(row.node.label || row.node.id)}</b><span>${esc(row.edge.note || row.edge.status || 'Explicitly represented alternative')}</span></div>`).join('')}</div>`;
}
function contextHtml(chains) {
  if (!chains?.length) return '';
  return `<div class="impact-section"><small>Context</small><div class="impact-tags">${chains.map(chain => `<span class="impact-tag">${esc(chain.label || chain.id)}</span>`).join('')}</div></div>`;
}
function render(result) {
  const node = ensurePanel();
  node.hidden = false;
  node.innerHTML = `<div class="impact-head"><div><small>Dependency impact</small><b>${esc(result.root.label || result.root.id)}</b></div><button type="button" class="impact-close" data-impact-clear aria-label="Clear impact trace">×</button></div>
    <div class="impact-section"><small>Directly exposed</small>${rowsHtml(result.direct, result.directOverflow)}</div>
    <div class="impact-section"><small>Second-order</small>${rowsHtml(result.secondOrder, result.secondOrderOverflow)}</div>
    ${alternativesHtml(result.alternatives)}${contextHtml(result.contextChains)}
    <div class="impact-boundary">This traces represented dependencies, not a forecast of real-world failure. Missing edges mean not represented in the current dataset.</div>`;
}

async function show(id, { persistState=true } = {}) {
  ensureLayer();
  const result = await runtime.impactFor(id);
  if (!result) {
    clear();
    return false;
  }
  activeImpactId = String(id);
  applyStates(result);
  render(result);
  if (persistState) persist(activeImpactId);
  window.dispatchEvent(new CustomEvent('potato-atlas-impact-change', { detail:{ id:activeImpactId, result } }));
  return true;
}
async function showEntity(code) {
  const id = await runtime.impactNodeForEntity(code);
  return id ? show(id) : false;
}
async function showGateway(id) {
  const nodeId = await runtime.impactNodeForGateway(id);
  return nodeId ? show(nodeId) : false;
}
async function showChain(id) {
  const nodeId = await runtime.impactNodeForChain(id);
  return nodeId ? show(nodeId) : false;
}
function clear() {
  activeImpactId = null;
  clearStates();
  panel()?.setAttribute('hidden','');
  persist(null);
  window.dispatchEvent(new CustomEvent('potato-atlas-impact-change', { detail:{ id:null, result:null } }));
  return true;
}
function current() { return activeImpactId; }

ensureLayer();
ensurePanel();
document.addEventListener('click', event => {
  if (event.target.closest('[data-impact-clear]')) { clear(); return; }
  const entity = event.target.closest('[data-impact-entity]');
  if (entity) { showEntity(entity.dataset.impactEntity); return; }
  const gateway = event.target.closest('[data-impact-gateway]');
  if (gateway) { showGateway(gateway.dataset.impactGateway); return; }
  const chain = event.target.closest('[data-impact-chain]');
  if (chain) { showChain(chain.dataset.impactChain); }
});

window.__potatoAtlasImpactTrace = { show, showEntity, showGateway, showChain, clear, current };

const restored = new URL(location.href).searchParams.get('impact');
if (restored) {
  const ok = await show(restored, { persistState:false });
  if (!ok) clear();
}
