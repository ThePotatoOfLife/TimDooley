const app = document.getElementById('atlasApp');
const panel = document.getElementById('panel');
const panelToggle = document.getElementById('panelToggle');
const mapInspectorToggle = document.getElementById('mapInspectorToggle');
const focusMode = document.getElementById('focusMode');
const menus = [...document.querySelectorAll('details.menu')];

function setPanel(open, {persist = true} = {}) {
  if (!app) return;
  app.classList.toggle('panel-collapsed', !open);
  panelToggle?.classList.toggle('active', open);
  mapInspectorToggle?.classList.toggle('active', open);
  panelToggle?.setAttribute('aria-pressed', String(open));
  mapInspectorToggle?.setAttribute('aria-pressed', String(open));
  if (persist) localStorage.setItem('atlas:panel-open', open ? '1' : '0');
  requestAnimationFrame(() => window.__potatoAtlasMap?.resize?.());
}

function setFocus(on, {persist = true} = {}) {
  if (!app) return;
  app.classList.toggle('ui-focus', on);
  focusMode?.classList.toggle('active', on);
  const label = on ? 'Focus mode · on' : 'Focus mode · hide overlays';
  if (focusMode && focusMode.textContent !== label) focusMode.textContent = label;
  if (persist) localStorage.setItem('atlas:focus-mode', on ? '1' : '0');
}

function closeOtherMenus(current) {
  for (const menu of menus) if (menu !== current) menu.open = false;
}
for (const menu of menus) menu.addEventListener('toggle', () => menu.open && closeOtherMenus(menu));

document.addEventListener('click', event => {
  if (!event.target.closest('details.menu')) for (const menu of menus) menu.open = false;
});

panelToggle?.addEventListener('click', () => setPanel(app?.classList.contains('panel-collapsed')));
mapInspectorToggle?.addEventListener('click', () => setPanel(app?.classList.contains('panel-collapsed')));
focusMode?.addEventListener('click', () => setFocus(!app?.classList.contains('ui-focus')));

setPanel(localStorage.getItem('atlas:panel-open') === '1', {persist:false});
setFocus(localStorage.getItem('atlas:focus-mode') === '1', {persist:false});

let lastSignature = panel?.textContent || '';
const observer = panel && new MutationObserver(() => {
  const signature = panel.textContent || '';
  if (signature === lastSignature) return;
  lastSignature = signature;
  if (app?.classList.contains('ui-focus')) return;
  const isLanding = /Explore the world/.test(signature);
  if (!isLanding) setPanel(true, {persist:false});
});
observer?.observe(panel, {childList:true, subtree:true, characterData:true});

function summaryText(id,text,active=false){
  const summary=document.querySelector(`#${id}>summary`);if(!summary)return;
  // Idempotence matters. Rewriting textContent creates child mutations; the old
  // body-wide observer could feed those mutations back into this function.
  if(summary.textContent!==text) summary.textContent=text;
  summary.classList.toggle('active-state',active);
}
function updateLayerSummary(){
  const relation=document.getElementById('relationType')?.value||'all';
  const field=document.getElementById('axisFieldView')?.value;
  const network=document.getElementById('empiricalNetworkView')?.value;
  const active=[];
  if(field&&field!=='all'&&field!=='off')active.push(field==='brics'?'BRICS':field[0].toUpperCase()+field.slice(1));
  if(network&&network!=='off')active.push(network.replaceAll('_',' '));
  if(relation!=='all')active.push('filtered');
  summaryText('layersMenu',active.length?`Layers · ${active.slice(0,2).join(' + ')}${active.length>2?'…':''}`:'Layers',active.length>0);
}
function updateTraceSummary(){
  const depth=Number(document.getElementById('traceDepth')?.value||1);
  const entity=document.getElementById('entityTraceToggle')?.classList.contains('active');
  const parts=[];if(depth>1)parts.push(`${depth} hops`);if(entity)parts.push('entities');
  summaryText('traceMenu',parts.length?`Trace · ${parts.join(' + ')}`:'Trace',parts.length>0);
}
function updateTimeSummary(state=window.__potatoAtlasTime?.getState?.()){
  if(!state||state.mode==='current'){summaryText('timeMenu','Time',false);return;}
  if(state.mode==='as_of')summaryText('timeMenu',`Time · ${state.time||'As of…'}`,true);
  else summaryText('timeMenu','Time · compare',true);
}
function updateViewSummary(){
  const height=document.getElementById('height')?.value||'flat';
  const parts=[];
  if(height!=='flat')parts.push(height);
  if(app?.classList.contains('ui-focus'))parts.push('focus');
  if(window.__potatoAtlasMap?.__potatoAtlasBasemapAttached)parts.push('basemap');
  summaryText('viewMenu',parts.length?`View · ${parts.join(' + ')}`:'View',parts.length>0);
}
function updateMenuSummaries(){updateLayerSummary();updateTraceSummary();updateTimeSummary();updateViewSummary();}

document.addEventListener('change',event=>{
  if(['relationType','axisFieldView','empiricalNetworkView','traceDepth','height','timeMode','timeDate','timeDate2'].includes(event.target?.id))queueMicrotask(updateMenuSummaries);
});
document.addEventListener('click',event=>{if(event.target?.id==='entityTraceToggle')queueMicrotask(updateTraceSummary);});
window.addEventListener('atlas-time-change',event=>updateTimeSummary(event.detail));
window.addEventListener('potato-atlas-basemap-change',updateViewSummary);

const layersPop = document.querySelector('#layersMenu .menu-pop');
function relocateInjectedLayerControls(){
  let moved=false;
  for(const id of ['axisFieldView','empiricalNetworkView']){
    const node=document.getElementById(id);
    if(node&&layersPop&&node.parentElement!==layersPop){layersPop.appendChild(node);moved=true;}
  }
  if(moved) updateLayerSummary();
}

function installAxisToggle(){
  const nav=document.getElementById('axisDepthNavigator');
  if(!nav||document.getElementById('axisCompactToggle'))return Boolean(nav);
  nav.hidden=localStorage.getItem('atlas:axis-open')!=='1';
  const button=document.createElement('button');
  button.id='axisCompactToggle';
  button.textContent=nav.hidden?'Axis':'Axis · open';
  button.title='Show or hide the D1–D11 Axis navigator';
  button.style.cssText='position:absolute;right:12px;top:44px;z-index:4;border-radius:999px;background:#0b1010df;backdrop-filter:blur(8px)';
  button.classList.toggle('active',!nav.hidden);
  button.addEventListener('click',()=>{
    nav.hidden=!nav.hidden;
    localStorage.setItem('atlas:axis-open',nav.hidden?'0':'1');
    button.textContent=nav.hidden?'Axis':'Axis · open';
    button.classList.toggle('active',!nav.hidden);
  });
  document.querySelector('.mapwrap')?.appendChild(button);
  return true;
}

function installBasemapControl(){
  if(document.getElementById('basemapToggle'))return;
  const pop=document.querySelector('#viewMenu .menu-pop');
  const map=window.__potatoAtlasMap;
  if(!pop||!map?.__potatoAtlasAttachBasemap)return;
  const button=document.createElement('button');
  button.id='basemapToggle';
  button.textContent=map.__potatoAtlasBasemapAttached?'Basemap · on':'Load OSM basemap';
  button.title='Load optional OpenStreetMap raster context. The country atlas works without it.';
  button.classList.toggle('active',map.__potatoAtlasBasemapAttached);
  button.addEventListener('click',()=>{
    const attached=map.__potatoAtlasAttachBasemap();
    button.textContent=attached?'Basemap · on':'Basemap unavailable';
    button.classList.toggle('active',attached);
    button.disabled=attached;
    updateViewSummary();
  });
  pop.appendChild(button);
}

// Optional modules announce themselves when their import is complete. React to
// those events exactly once instead of polling the document every 250 ms for ten
// seconds. This keeps an idle world map genuinely idle.
window.addEventListener('potato-atlas-module-ready',event=>{
  const label=event.detail?.label;
  if(label==='Fields'||label==='Networks')relocateInjectedLayerControls();
  if(label==='Axis depth')installAxisToggle();
  updateMenuSummaries();
});
installBasemapControl();

focusMode?.addEventListener('click',()=>queueMicrotask(updateViewSummary));
updateMenuSummaries();

function sharedLoad(label,path){
  return window.__potatoAtlasLoadModule
    ? window.__potatoAtlasLoadModule(label,path)
    : import(path).then(()=>true).catch(error=>{console.warn(`${label} unavailable:`,error);return false;});
}

let pathfinderPromise=null;
function ensurePathfinder(){
  if(!pathfinderPromise)pathfinderPromise=sharedLoad('Path finder','./3d-pathfinder.js');
  return pathfinderPromise;
}
let entityTracePromise=null;
function ensureEntityTrace(){
  if(!entityTracePromise){
    entityTracePromise=sharedLoad('Entity Trace','./3d-entity-trace.js')
      .then(result=>{updateTraceSummary();return result;});
  }
  return entityTracePromise;
}
const traceMenu=document.getElementById('traceMenu');
traceMenu?.addEventListener('toggle',()=>{
  if(!traceMenu.open)return;
  ensurePathfinder();
  ensureEntityTrace();
});

window.__potatoAtlasUI={setPanel,setFocus,updateMenuSummaries,ensurePathfinder,ensureEntityTrace};
