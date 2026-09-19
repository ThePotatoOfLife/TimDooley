// First-class specialist Evidence layer coordinator for the World Relational Atlas.
// Canonical evidence records remain in their own datasets/modules. This owner only
// coordinates discoverability, activation, URL hydration and reset state.

const MANIFEST_URL = '../data/world-map-evidence-layers.json';
const activeIds = new Set();
const byId = new Map();
let manifest = null;
let loadError = null;
let installScheduled = false;
let adapterSyncDepth = 0;

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

function globalApi(name) {
  return name ? window[name] : null;
}
function entry(id) { return byId.get(String(id || '')) || null; }
function entries({ availableOnly=false }={}) {
  const rows=[...byId.values()];
  return availableOnly ? rows.filter(row=>row.availability==='current') : rows;
}
function active() { return [...activeIds]; }
function isActive(id) { return activeIds.has(String(id || '')); }

function persist() {
  const url=new URL(location.href);
  const primary=active().find(id=>entry(id)?.url_param==='evidenceLayer') || null;
  if(primary) url.searchParams.set('evidenceLayer', entry(primary)?.url_value || primary);
  else url.searchParams.delete('evidenceLayer');
  history.replaceState({},'',url);
}
function emit(reason,id=null) {
  const detail={reason,id,active:active(),entries:active().map(entry).filter(Boolean)};
  window.dispatchEvent(new CustomEvent('potato-atlas-evidence-layer-change',{detail}));
  renderMenu();
}
async function ensureModule(row) {
  if(!row?.module) return false;
  const ok=await window.__potatoAtlasLoadModule?.(`Evidence · ${row.label || row.id}`,row.module);
  if(!ok) return false;
  return Boolean(globalApi(row.api_global));
}
async function setAdapterEnabled(row,next) {
  const api=globalApi(row?.api_global);
  if(typeof api?.setEnabled!=='function') return true;
  adapterSyncDepth += 1;
  try {
    const requested=Boolean(next);
    const result=await api.setEnabled(requested);
    if(typeof result==='boolean' && result!==requested) {
      throw new Error(`Evidence adapter ${row?.id || 'unknown'} refused ${requested ? 'activation' : 'deactivation'}.`);
    }
    return true;
  } finally {
    adapterSyncDepth=Math.max(0,adapterSyncDepth-1);
  }
}
async function activate(id,{silent=false}={}) {
  const row=entry(id);
  if(!row || row.availability!=='current') return false;
  if(isActive(row.id)) { renderMenu(); return true; }
  if(!(await ensureModule(row))) return false;
  await setAdapterEnabled(row,true);
  activeIds.add(row.id);
  if(!silent) { persist(); emit('activate',row.id); }
  else renderMenu();
  return true;
}
async function deactivate(id,{silent=false}={}) {
  const key=String(id || '');
  const row=entry(key);
  if(!activeIds.has(key)) { renderMenu(); return false; }
  await setAdapterEnabled(row,false);
  const changed=activeIds.delete(key);
  if(changed && !silent) { persist(); emit('deactivate',row?.id || key); }
  else renderMenu();
  return changed;
}
async function toggle(id) {
  return isActive(id) ? deactivate(id) : activate(id);
}
async function reset({silent=false}={}) {
  const ids=active();
  for(const id of ids) await deactivate(id,{silent:true});
  if(!silent) { persist(); emit('reset'); }
  return true;
}

function menuHost() { return document.getElementById('atlasWorldBar'); }
function evidenceMenu() {
  const host=menuHost();
  if(!host) return null;
  let details=document.getElementById('atlasEvidenceMenu');
  if(details) return details;
  details=document.createElement('details');
  details.id='atlasEvidenceMenu';
  details.className='atlas-world-menu';
  details.innerHTML='<summary>Evidence</summary><div class="atlas-world-menu-pop"></div>';
  details.addEventListener('toggle',()=>{
    if(!details.open) return;
    document.querySelectorAll('#atlasWorldBar details[open]').forEach(menu=>{ if(menu!==details) menu.removeAttribute('open'); });
    renderMenu();
  });
  details.addEventListener('click',async event=>{
    const button=event.target.closest('[data-evidence-layer]');
    if(!button || button.disabled) return;
    button.disabled=true;
    try { await toggle(button.dataset.evidenceLayer); }
    finally { button.disabled=false; }
  });
  const geography=document.getElementById('atlasGeographyMenu');
  const physical=document.getElementById('atlasPhysicalMenu');
  if(physical?.parentElement===host) physical.insertAdjacentElement('afterend',details);
  else if(geography?.parentElement===host) geography.insertAdjacentElement('afterend',details);
  else host.appendChild(details);
  return details;
}
function renderMenu() {
  const details=evidenceMenu();
  if(!details || !manifest) return;
  const pop=details.querySelector('.atlas-world-menu-pop');
  if(!pop) return;
  const rows=entries().map(row=>{
    const current=row.availability==='current';
    const on=isActive(row.id);
    const note=[row.epistemic_type,row.geography,row.source_owner,row.status_note].filter(Boolean).join(' · ');
    return `<button type="button" class="atlas-world-option${on?' active':''}" data-evidence-layer="${esc(row.id)}" aria-pressed="${on?'true':'false'}" ${current?'':'disabled'} title="${esc(note)}"><span>${esc(row.label)}<small>${esc(row.epistemic_type || '')}${current?'':' · planned'}</small></span></button>`;
  }).join('');
  pop.innerHTML=`<div class="atlas-world-static"><span>Evidence datasets</span><small>${activeIds.size ? `${activeIds.size} active` : 'source-classified · lazy'}</small></div>${rows || '<div class="atlas-world-empty">No evidence layers registered</div>'}<div class="atlas-world-static"><small>Evidence datasets preserve source methodology and snapshot vintage; they do not become generic scores.</small></div>`;
  details.classList.toggle('active',activeIds.size>0);
}

function scheduleInstall() {
  if(installScheduled) return;
  installScheduled=true;
  queueMicrotask(()=>{ installScheduled=false; renderMenu(); });
}
async function hydrateFromUrl() {
  const url=new URL(location.href);
  const requested=url.searchParams.get('evidenceLayer');
  if(!requested) return;
  const row=entries({availableOnly:true}).find(item=>(item.url_value || item.id)===requested);
  if(row) await activate(row.id,{silent:true});
  persist();
  emit('hydrate',row?.id || null);
}
async function load() {
  try {
    const response=await fetch(MANIFEST_URL,{cache:'no-cache'});
    if(!response.ok) throw new Error(`${response.status} ${MANIFEST_URL}`);
    manifest=await response.json();
    byId.clear();
    for(const row of manifest?.entries || []) byId.set(row.id,Object.freeze({...row}));
    scheduleInstall();
    await hydrateFromUrl();
    window.dispatchEvent(new CustomEvent('potato-atlas-evidence-layers-ready',{detail:{count:byId.size}}));
    return manifest;
  } catch(error) {
    loadError=error;
    console.warn('World Map Evidence layer manifest unavailable:',error);
    window.dispatchEvent(new CustomEvent('potato-atlas-evidence-layer-error',{detail:{message:error?.message || String(error)}}));
    return null;
  }
}

window.addEventListener('potato-atlas-module-ready', scheduleInstall);
window.addEventListener('potato-atlas-ui-layout-change', scheduleInstall);
window.addEventListener('potato-atlas-adl-heat-change',event=>{
  if(adapterSyncDepth > 0) return;
  const on=Boolean(event?.detail?.enabled);
  const wasOn=activeIds.has('adl-heat');
  if(on) activeIds.add('adl-heat'); else activeIds.delete('adl-heat');
  if(wasOn===on) { renderMenu(); return; }
  persist();
  emit('adapter-sync','adl-heat');
});

const ready=load();
window.__potatoAtlasEvidenceLayers={
  ready,
  get manifest(){return manifest;},
  get error(){return loadError;},
  get:entry,
  entries,
  active,
  isActive,
  activate,
  deactivate,
  toggle,
  reset,
};
