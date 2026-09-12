// Contextual functional-chain explorer for the canonical World Map.
// Uses the shared runtime and a dedicated outline feature-state channel.
const map = window.__potatoAtlasMap;
const runtime = window.__potatoAtlasDataRuntime;
if (!map || !runtime) throw new Error('Functional chain explorer requires map and runtime APIs.');
await runtime.ready;

const LAYER_ID = 'atlas-chain-outline';
const MAX_INFRASTRUCTURE_TAGS = 4;
let activeChainId = null;
let markedCodes = new Set();

function countEnhancement() {
  const diagnostics = window.__potatoAtlasDiagnostics;
  if (diagnostics) diagnostics.cardEnhancementPasses = (diagnostics.cardEnhancementPasses || 0) + 1;
}
function ensureLayer() {
  if (map.getLayer(LAYER_ID)) return;
  const before = map.getLayer('countries-line') ? 'countries-line' : (map.getLayer('countries-outline') ? 'countries-outline' : undefined);
  map.addLayer({
    id:LAYER_ID,
    type:'line',
    source:'countries',
    paint:{
      'line-color':'#f0d58c',
      'line-width':['interpolate',['linear'],['zoom'],1,1.5,5,3,8,4.2],
      'line-opacity':['case',['boolean',['feature-state','atlasChainMatch'],false],0.9,0],
      'line-blur':0.3,
    },
  }, before);
}

function persist() {
  const url = new URL(location.href);
  if (activeChainId) url.searchParams.set('chain', activeChainId);
  else url.searchParams.delete('chain');
  history.replaceState({}, '', url);
}

function clearFeatureState() {
  for (const code of markedCodes) {
    try { map.setFeatureState({ source:'countries', id:code }, { atlasChainMatch:false }); } catch {}
  }
  markedCodes = new Set();
}

function strip() { return document.getElementById('atlasChainContext'); }
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function infrastructureHtml(rows) {
  if (!rows?.length) return '';
  const visible = rows.slice(0, MAX_INFRASTRUCTURE_TAGS);
  const remaining = Math.max(0, rows.length - visible.length);
  return `<div class="chain-infrastructure"><small>Infrastructure</small><div class="atlas-country-tags">${visible.map(asset => `<button type="button" class="atlas-country-tag" data-infrastructure-id="${escapeHtml(asset.id)}">${escapeHtml(asset.label || asset.id)}</button>`).join('')}${remaining ? `<span class="atlas-country-tag">+${remaining}</span>` : ''}</div></div>`;
}
async function renderStrip(chain) {
  let node = strip();
  if (!chain) { node?.remove(); return; }
  if (!node) {
    node = document.createElement('aside');
    node.id = 'atlasChainContext';
    node.setAttribute('aria-live','polite');
    document.querySelector('.mapwrap')?.appendChild(node);
  }
  const systems = (chain.systems || []).slice(0,6).map(value => String(value).replaceAll('-',' ')).join(' · ');
  const infrastructure = await runtime.infrastructureForChain?.(activeChainId) || [];
  if (!node.isConnected || activeChainId !== chain.id && chain.id) return;
  node.innerHTML = `<button type="button" data-chain-clear aria-label="Clear functional chain">×</button><small>Functional chain</small><b>${escapeHtml(chain.label || activeChainId)}</b>${systems ? `<span>${escapeHtml(systems)}</span>` : ''}<p>${escapeHtml(chain.description || '')}</p>${infrastructureHtml(infrastructure)}<em>${escapeHtml(chain.epistemic_type || '')}${chain.source_note ? ` · ${escapeHtml(chain.source_note)}` : ''}</em>`;
}

async function setChain(id, { persistState=true } = {}) {
  ensureLayer();
  const chain = id ? await runtime.chain(id) : null;
  clearFeatureState();
  if (!chain) {
    activeChainId = null;
    if (persistState) persist();
    await renderStrip(null);
    syncCardActions();
    window.dispatchEvent(new CustomEvent('potato-atlas-chain-change', { detail:{ id:null, chain:null } }));
    return false;
  }
  activeChainId = id;
  for (const code of chain.members || []) {
    try { map.setFeatureState({ source:'countries', id:code }, { atlasChainMatch:true }); markedCodes.add(code); } catch {}
  }
  if (persistState) persist();
  await renderStrip({ id, ...chain });
  syncCardActions();
  window.dispatchEvent(new CustomEvent('potato-atlas-chain-change', { detail:{ id, chain } }));
  return true;
}

async function toggleChain(id) {
  if (activeChainId === id) return setChain(null);
  return setChain(id);
}
function clear() { return setChain(null); }
function get() { return activeChainId; }

async function upgradeChainTags() {
  const card = document.getElementById('atlasCountryCard');
  if (!card || card.hidden) return;
  countEnhancement();
  const sections = [...card.querySelectorAll('.atlas-country-section')];
  const section = sections.find(node => node.querySelector(':scope > small')?.textContent?.trim() === 'Functional chains');
  if (!section) return;
  const code = String(window.__potatoAtlasSelection?.current?.activeCode || window.__potatoAtlasSelection?.current?.code || '').toUpperCase();
  if (!/^[A-Z]{3}$/.test(code)) return;
  const chains = await runtime.chainsForCountry(code);
  const byLabel = new Map(chains.map(chain => [String(chain.label || '').trim(), chain.id]));
  for (const tag of [...section.querySelectorAll('.atlas-country-tag')]) {
    if (tag.matches('[data-chain-id]')) continue;
    const label = tag.textContent?.trim();
    const id = byLabel.get(label);
    if (!id) continue;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `${tag.className} atlas-chain-action`;
    button.setAttribute('data-chain-id', id);
    button.title = tag.title || `Explore ${label} functional chain`;
    button.textContent = label;
    tag.replaceWith(button);
  }
  syncCardActions();
}

function syncCardActions() {
  document.querySelectorAll('[data-chain-id]').forEach(button => button.classList.toggle('active', button.dataset.chainId === activeChainId));
}

function installStyle() {
  if (document.getElementById('atlasChainExplorerStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasChainExplorerStyle';
  style.textContent = `
    .atlas-chain-action{background:transparent;color:#bec8c3;cursor:pointer}.atlas-chain-action:hover,.atlas-chain-action.active{border-color:#bca666;color:#f0d58c;background:#191a14}
    #atlasChainContext{position:absolute;right:10px;bottom:10px;z-index:7;width:min(330px,calc(100% - 20px));padding:10px 12px;background:#080b0be8;border:1px solid #625a3c;border-radius:10px;box-shadow:0 8px 24px #0008;backdrop-filter:blur(10px)}
    #atlasChainContext small{display:block;color:#8f8a70;font-size:8px;text-transform:uppercase;letter-spacing:.1em}#atlasChainContext b{display:block;margin-top:2px;color:#f0d58c;font-size:13px}#atlasChainContext span{display:block;margin-top:4px;color:#b5b19d;font-size:9px}#atlasChainContext p{margin:6px 0 3px;color:#c7cec8;font-size:10px;line-height:1.35}#atlasChainContext em{display:block;color:#747c76;font-size:8px;font-style:normal}#atlasChainContext [data-chain-clear]{float:right;border:0;background:transparent;color:#9b9e91;cursor:pointer;font-size:15px}.chain-infrastructure{margin:7px 0;padding-top:6px;border-top:1px solid #3b3828}.chain-infrastructure .atlas-country-tags{display:flex;flex-wrap:wrap;gap:4px}.chain-infrastructure .atlas-country-tag{display:inline-block;background:transparent;color:#bec8c3;cursor:pointer}@media(max-width:900px){#atlasChainContext{right:8px;bottom:58px;width:min(300px,calc(100% - 16px))}}
  `;
  document.head.appendChild(style);
}

installStyle();
ensureLayer();
document.addEventListener('click', event => {
  const chainButton = event.target.closest('[data-chain-id]');
  if (chainButton) { toggleChain(chainButton.dataset.chainId); return; }
  if (event.target.closest('[data-chain-clear]')) clear();
});

window.addEventListener('potato-atlas-country-card-rendered', () => queueMicrotask(upgradeChainTags));
window.addEventListener('potato-atlas-working-selection-change', upgradeChainTags);
window.addEventListener('potato-atlas-layer-change', upgradeChainTags);

const requested = new URL(location.href).searchParams.get('chain');
if (requested) await setChain(requested, { persistState:false });
await upgradeChainTags();

window.__potatoAtlasChainExplorer = { set:setChain, toggle:toggleChain, clear, get };