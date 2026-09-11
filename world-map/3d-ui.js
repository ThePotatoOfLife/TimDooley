const app = document.getElementById('atlasApp');
const panel = document.getElementById('panel');
const panelToggle = document.getElementById('panelToggle');
const mapInspectorToggle = document.getElementById('mapInspectorToggle');
const focusMode = document.getElementById('focusMode');
const search = document.getElementById('search');
const menus = [...document.querySelectorAll('details.menu')];

function setPanel(open, {persist = true} = {}) {
  if (!app) return;
  app.classList.toggle('panel-collapsed', !open);
  panelToggle?.classList.toggle('active', open);
  mapInspectorToggle?.classList.toggle('active', open);
  panelToggle?.setAttribute('aria-pressed', String(open));
  mapInspectorToggle?.setAttribute('aria-pressed', String(open));
  if (panelToggle) panelToggle.textContent = open ? 'Close' : 'Inspect';
  if (persist) localStorage.setItem('atlas:panel-open', open ? '1' : '0');
  window.dispatchEvent(new CustomEvent('potato-atlas-panel-change',{detail:{open}}));
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
  const passiveSelection = /Canonical country|Territory \/ map polygon|World Relational Atlas/.test(signature);
  const isLanding = /Explore the world/.test(signature);
  if (!isLanding && !passiveSelection) setPanel(true, {persist:false});
});
observer?.observe(panel, {childList:true, subtree:true, characterData:true});

function summaryText(id,text,active=false){
  const summary=document.querySelector(`#${id}>summary`);if(!summary)return;
  if(summary.textContent!==text) summary.textContent=text;
  summary.classList.toggle('active-state',active);
}
function updateLayerSummary(){
  const capitals=document.getElementById('capitals');
  const field=document.getElementById('axisFieldView')?.value;
  const network=document.getElementById('empiricalNetworkView')?.value;
  const active=[];
  if(capitals&&!capitals.classList.contains('active'))active.push('capitals off');
  if(field&&field!=='all'&&field!=='off')active.push(field==='brics'?'BRICS':field[0].toUpperCase()+field.slice(1));
  if(network&&network!=='off')active.push(network.replaceAll('_',' '));
  summaryText('layersMenu',active.length?`Map · ${active.slice(0,2).join(' + ')}${active.length>2?'…':''}`:'Map',active.length>0);
}
function updateTraceSummary(){
  const depth=Number(document.getElementById('traceDepth')?.value||1);
  const entity=document.getElementById('entityTraceToggle')?.classList.contains('active');
  const compare=document.getElementById('compare')?.classList.contains('active');
  const relations=document.getElementById('relations')?.classList.contains('active');
  const relation=document.getElementById('relationType')?.value||'all';
  const parts=[];if(compare)parts.push('compare');if(relations)parts.push('connections');if(relation!=='all')parts.push('filtered');if(depth>1)parts.push(`${depth} hops`);if(entity)parts.push('entities');
  summaryText('traceMenu',parts.length?`Analyze · ${parts.slice(0,3).join(' + ')}${parts.length>3?'…':''}`:'Analyze',parts.length>0);
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
document.addEventListener('click',event=>{
  if(['entityTraceToggle','compare','relations'].includes(event.target?.id))queueMicrotask(updateTraceSummary);
  if(event.target?.id==='capitals')queueMicrotask(updateLayerSummary);
});
window.addEventListener('atlas-time-change',event=>updateTimeSummary(event.detail));
window.addEventListener('potato-atlas-basemap-change',updateViewSummary);
window.addEventListener('potato-atlas-capitals-change',updateLayerSummary);

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
  button.style.cssText='position:absolute;right:12px;top:44px;z-index:4;border-radius:999px;background:#0b1111f2';
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

function installSleekSurface(){
  if(document.getElementById('atlasSleekStyle'))return;
  const style=document.createElement('style');
  style.id='atlasSleekStyle';
  style.textContent=`
    :root{--panel:#101919;--panel2:#162120;--line:#2d3b3a;--accent:#c3e58d;--gold:#e7c56f;--blue:#6cafe3;--red:#cc7d7d}
    .top{min-height:44px!important;padding:5px 8px!important;gap:6px!important;background:#0b1111f4!important}
    .brand b{font-size:16px!important}.brand small{font-size:9px!important;max-width:340px!important}
    .layout{position:relative!important;display:block!important;min-height:0!important;overflow:hidden!important}
    .mapwrap{position:absolute!important;inset:0!important;overflow:hidden!important}
    .panel{position:absolute!important;z-index:6!important;top:10px!important;right:10px!important;bottom:10px!important;width:min(360px,calc(100% - 20px))!important;min-width:0!important;padding:14px!important;border:1px solid var(--line)!important;border-radius:11px!important;box-shadow:0 10px 30px #0009!important;transform:translateX(0);transition:transform .18s ease,opacity .14s ease!important}
    .app.panel-collapsed .panel{transform:translateX(calc(100% + 20px))!important;opacity:0!important;pointer-events:none!important;padding:14px!important;border:1px solid var(--line)!important}
    .hud{left:10px!important;bottom:10px!important;padding:5px 8px!important;background:#0b1111f2!important;max-width:260px!important;pointer-events:none!important}
    .hud .muted{display:none!important}.camera{display:none!important}.map-ui-toggle{display:none!important}
    .menu-pop,.hud,.time-state,#axisCompactToggle{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
    .menu-pop{background:#0e1515!important;border-radius:10px!important;padding:8px!important}
    .atlas-hover:not(.atlas-hover-capital)>div{display:none!important}
    .atlas-hover:not(.atlas-hover-capital)>div:nth-of-type(2){display:block!important;color:var(--muted)!important;font-size:10px!important}
    .maplibregl-popup-content{padding:7px 9px!important;box-shadow:0 4px 14px #0007!important}
    .panel .card{padding:9px 10px!important}.panel .boundary{font-size:11px!important;padding:7px 9px!important}
    .quick-actions{gap:5px!important}.quick-actions button{padding:6px 9px!important}
    .atlas-tools-root>summary{font-weight:650}.atlas-tools-root:has(.active-state)>summary{border-color:#6f8f78;color:var(--accent)}
    .atlas-tools-root>.menu-pop{width:290px;max-width:min(290px,calc(100vw - 20px));max-height:min(72vh,620px);overflow:auto}
    .atlas-tools-hint{font-size:10px;color:var(--muted);padding:2px 4px 7px;border-bottom:1px solid var(--line);margin-bottom:4px}
    .atlas-tools-root>.menu-pop>details.menu{width:100%;margin:0;border-bottom:1px solid #243130}
    .atlas-tools-root>.menu-pop>details.menu:last-child{border-bottom:0}
    .atlas-tools-root>.menu-pop>details.menu>summary{display:flex;align-items:center;justify-content:space-between;width:100%;border:0;background:transparent;border-radius:5px;padding:9px 5px;color:var(--ink);font-weight:620}
    .atlas-tools-root>.menu-pop>details.menu>summary::after{content:'+';color:var(--muted);font-weight:400}
    .atlas-tools-root>.menu-pop>details.menu[open]>summary::after{content:'−'}
    .atlas-tools-root>.menu-pop>details.menu>summary.active-state{color:var(--accent)}
    .atlas-tools-root>.menu-pop>details.menu>.menu-pop{position:static!important;display:block!important;min-width:0!important;max-width:none!important;width:100%!important;border:0!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;padding:0 4px 8px!important;margin:0!important}
    .atlas-tools-root .menu-title{padding-top:6px}.atlas-tools-root .boundary{margin:7px 0}
    @media(max-width:900px){.panel{top:auto!important;left:8px!important;right:8px!important;bottom:8px!important;width:auto!important;max-height:44vh!important}.app.panel-collapsed .panel{transform:translateY(calc(100% + 20px))!important}.brand{display:none!important}.atlas-tools-root>.menu-pop{position:fixed!important;right:8px!important;top:50px!important;width:min(320px,calc(100vw - 16px))!important;max-width:none!important}}
  `;
  document.head.appendChild(style);
  document.getElementById('mapInspectorToggle')?.remove();
}

function installToolbox(){
  if(document.getElementById('atlasToolsMenu'))return;
  const top=document.querySelector('.top');
  const quick=document.querySelector('.quick-actions');
  if(!top||!quick)return;

  const tools=document.createElement('details');
  tools.id='atlasToolsMenu';
  tools.className='menu atlas-tools-root';
  tools.innerHTML='<summary>Tools</summary><div class="menu-pop"><div class="atlas-tools-hint">Map context, analysis, time and display settings.</div></div>';
  quick.after(tools);
  const pop=tools.querySelector('.menu-pop');

  const labels={layersMenu:'Map',traceMenu:'Analyze',timeMenu:'Time',viewMenu:'View',moreMenu:'Links'};
  for(const id of ['layersMenu','traceMenu','timeMenu','viewMenu','moreMenu']){
    const menu=document.getElementById(id);if(!menu)continue;
    const summary=menu.querySelector(':scope>summary');if(summary)summary.textContent=labels[id];
    pop.appendChild(menu);
  }

  const compare=document.getElementById('compare');
  const tracePop=document.querySelector('#traceMenu .menu-pop');
  if(compare&&tracePop){
    compare.textContent='Compare countries';
    const title=tracePop.querySelector('.menu-title');
    if(title)title.after(compare);else tracePop.prepend(compare);
  }
  const relations=document.getElementById('relations');
  const relationType=document.getElementById('relationType');
  if(relations&&tracePop){relations.textContent='Country connections';compare?.after(relations)}
  if(relationType&&tracePop){relations?.after(relationType)}

  tools.addEventListener('toggle',()=>{
    if(!tools.open)return;
    for(const menu of menus)menu.open=false;
  });
  document.addEventListener('click',event=>{if(tools.open&&!event.target.closest('#atlasToolsMenu'))tools.open=false;});
}

function installCapitalsControl(){
  if(document.getElementById('capitals'))return;
  const pop=document.querySelector('#layersMenu .menu-pop');if(!pop)return;
  const button=document.createElement('button');
  button.id='capitals';button.textContent='Capital cities';button.className='active';button.setAttribute('aria-pressed','true');
  button.title='Show or hide capital-city points and labels';
  const title=pop.querySelector('.menu-title');if(title)title.after(button);else pop.prepend(button);
  const sync=()=>{
    const api=window.__potatoAtlasCapitals;
    const visible=api?.visible!==false;
    button.classList.toggle('active',visible);button.setAttribute('aria-pressed',String(visible));
  };
  button.addEventListener('click',()=>{
    const api=window.__potatoAtlasCapitals;
    if(!api?.setVisible)return;
    api.setVisible(!api.visible);sync();
  });
  window.addEventListener('potato-atlas-capitals-ready',sync);
  window.addEventListener('potato-atlas-capitals-change',sync);
  sync();
}

function tuneMapSurface(){
  const map=window.__potatoAtlasMap;if(!map)return;
  const selected=['boolean',['feature-state','selected'],false];
  const compared=['boolean',['feature-state','compare'],false];
  const countryColor=['case',selected,'#e7c56f',compared,'#6cafe3','#576d6b'];
  try{if(map.getLayer('countries-fill')){map.setPaintProperty('countries-fill','fill-color',countryColor);map.setPaintProperty('countries-fill','fill-opacity',['case',selected,.9,compared,.8,.6]);}}catch{}
  try{if(map.getLayer('countries-extrude'))map.setPaintProperty('countries-extrude','fill-extrusion-color',countryColor);}catch{}
  try{if(map.getLayer('countries-line'))map.setPaintProperty('countries-line','line-color',['case',selected,'#f4e4ae',compared,'#b9ddf7','#22302f']);}catch{}
  try{if(map.getLayer('country-hubs'))map.setLayoutProperty('country-hubs','visibility','none');}catch{}
  try{if(map.getLayer('semantic-hubs'))map.setPaintProperty('semantic-hubs','circle-color',['match',['get','plane'],'project-canon','#cf7d7d','interpretive-policy','#70afe2','historical','#dda06e','mixed','#aa8ed9','#c3e58d']);}catch{}
  try{if(map.getLayer('relations')){map.setPaintProperty('relations','line-color',['step',['get','depth'],'#70afe2',2,'#8eabc5',3,'#70879c']);map.setPaintProperty('relations','line-width',['interpolate',['linear'],['zoom'],2,.75,6,1.8]);map.setPaintProperty('relations','line-opacity',['step',['get','depth'],.6,2,.42,3,.28]);}}catch{}
  try{if(map.getLayer('semantic-links')){map.setPaintProperty('semantic-links','line-color','#84948b');map.setPaintProperty('semantic-links','line-width',.75);map.setPaintProperty('semantic-links','line-opacity',.34);}}catch{}
  try{if(map.getLayer('trace-hubs'))map.setPaintProperty('trace-hubs','circle-color',['step',['get','depth'],'#c3e58d',2,'#70afe2',3,'#969bd0']);}catch{}
  try{if(map.getLayer('compare-hubs'))map.setPaintProperty('compare-hubs','circle-color','#6cafe3');}catch{}
  const interior=document.getElementById('interior');
  if(interior){interior.textContent='Module orbit · advanced';interior.title='Optional on-map semantic navigation. The stable selection dock is the primary country interface.'}
}

function installKeyboardNavigation(){
  document.addEventListener('keydown',event=>{
    if(event.key==='/'&&!event.metaKey&&!event.ctrlKey&&!event.altKey){
      const tag=document.activeElement?.tagName;
      if(!['INPUT','TEXTAREA','SELECT'].includes(tag)){
        event.preventDefault();search?.focus();search?.select?.();
      }
    }
    if(event.key==='Escape'){
      const tools=document.getElementById('atlasToolsMenu');if(tools)tools.open=false;
      for(const menu of menus)menu.open=false;
      if(!app?.classList.contains('panel-collapsed'))setPanel(false);
    }
  });
  if(search)search.title='Search countries · press / to focus';
}

installSleekSurface();
installToolbox();
installCapitalsControl();
tuneMapSurface();
installKeyboardNavigation();

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
