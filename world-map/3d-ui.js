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
  const capitals=document.getElementById('capitals');
  const field=document.getElementById('axisFieldView')?.value;
  const network=document.getElementById('empiricalNetworkView')?.value;
  const active=[];
  if(capitals&&!capitals.classList.contains('active'))active.push('capitals off');
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
document.addEventListener('click',event=>{if(event.target?.id==='entityTraceToggle')queueMicrotask(updateTraceSummary);if(event.target?.id==='capitals')queueMicrotask(updateLayerSummary);});
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
  button.style.cssText='position:absolute;right:12px;top:44px;z-index:4;border-radius:999px;background:#0b1010f2';
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

const NATURAL_EARTH_CAPITALS = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_110m_populated_places_simple.geojson';
let capitalsVisible = true;

function installSleekSurface(){
  if(document.getElementById('atlasSleekStyle'))return;
  const style=document.createElement('style');
  style.id='atlasSleekStyle';
  style.textContent=`
    .top{min-height:44px!important;padding:5px 8px!important;gap:6px!important}
    .brand b{font-size:16px!important}.brand small{font-size:9px!important;max-width:340px!important}
    .layout{position:relative!important;display:block!important;min-height:0!important;overflow:hidden!important}
    .mapwrap{position:absolute!important;inset:0!important;overflow:hidden!important}
    .panel{position:absolute!important;z-index:6!important;top:10px!important;right:10px!important;bottom:10px!important;width:min(370px,calc(100% - 20px))!important;min-width:0!important;padding:14px!important;border:1px solid var(--line)!important;border-radius:11px!important;box-shadow:0 10px 32px #000a!important;transform:translateX(0);transition:transform .18s ease,opacity .14s ease!important}
    .app.panel-collapsed .panel{transform:translateX(calc(100% + 20px))!important;opacity:0!important;pointer-events:none!important;padding:14px!important;border:1px solid var(--line)!important}
    .hud{left:10px!important;bottom:10px!important;padding:5px 8px!important;background:#0b1010f2!important;max-width:260px!important;pointer-events:none!important}
    .hud .muted{display:none!important}.camera{display:none!important}.map-ui-toggle{display:none!important}
    .menu-pop,.hud,.time-state,#axisCompactToggle{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
    .menu-pop{background:#0d1313!important;border-radius:10px!important;padding:8px!important}
    .atlas-hover:not(.atlas-hover-capital)>div{display:none!important}
    .atlas-hover:not(.atlas-hover-capital)>div:nth-of-type(2){display:block!important;color:var(--muted)!important;font-size:10px!important}
    .maplibregl-popup-content{padding:7px 9px!important;box-shadow:0 4px 14px #0007!important}
    .panel .card{padding:9px 10px!important}.panel .boundary{font-size:11px!important;padding:7px 9px!important}
    @media(max-width:900px){.panel{top:auto!important;left:8px!important;right:8px!important;bottom:8px!important;width:auto!important;max-height:44vh!important}.app.panel-collapsed .panel{transform:translateY(calc(100% + 20px))!important}.brand{display:none!important}}
  `;
  document.head.appendChild(style);
  document.getElementById('mapInspectorToggle')?.remove();
}

function capitalFeatures(payload){
  return (payload?.features||[]).filter(feature=>{
    const p=feature.properties||{};
    return p.adm0cap===1||p.capalt===1;
  }).map(feature=>{
    const p=feature.properties||{};
    return {type:'Feature',properties:{
      iso3:String(p.adm0_a3||p.sov_a3||''),name:p.name||p.nameascii||'Capital',country:p.adm0name||p.sov0name||'',scalerank:Number(p.scalerank??9),primary:p.adm0cap===1
    },geometry:feature.geometry};
  }).filter(feature=>feature.properties.iso3&&feature.geometry?.type==='Point');
}

function setCapitalVisibility(visible){
  capitalsVisible=Boolean(visible);
  const map=window.__potatoAtlasMap;
  for(const id of ['capital-cities','capital-city-major-labels','capital-city-labels'])if(map?.getLayer(id))map.setLayoutProperty(id,'visibility',capitalsVisible?'visible':'none');
  const button=document.getElementById('capitals');
  button?.classList.toggle('active',capitalsVisible);button?.setAttribute('aria-pressed',String(capitalsVisible));
  window.dispatchEvent(new CustomEvent('potato-atlas-capitals-change',{detail:{visible:capitalsVisible}}));
}

async function installCapitals(){
  const map=window.__potatoAtlasMap,layersPop=document.querySelector('#layersMenu .menu-pop');
  if(!map||!layersPop)return;
  let button=document.getElementById('capitals');
  if(!button){
    button=document.createElement('button');button.id='capitals';button.className='active';button.textContent='Capital cities';button.setAttribute('aria-pressed','true');
    const title=layersPop.querySelector('.menu-title');title?.after(button);
    button.addEventListener('click',()=>setCapitalVisibility(!capitalsVisible));
  }
  try{
    if(!map.getSource('capital-cities')){
      const response=await fetch(NATURAL_EARTH_CAPITALS,{cache:'force-cache'});if(!response.ok)throw new Error(`capital snapshot ${response.status}`);
      const features=capitalFeatures(await response.json());if(features.length<160)throw new Error(`capital coverage ${features.length}`);
      map.addSource('capital-cities',{type:'geojson',data:{type:'FeatureCollection',features}});
      map.addLayer({id:'capital-cities',type:'circle',source:'capital-cities',minzoom:0,paint:{'circle-radius':['interpolate',['linear'],['zoom'],1,1.7,3,2.6,6,4.4],'circle-color':'#e0bd78','circle-stroke-color':'#171a18','circle-stroke-width':1,'circle-opacity':.9}});
      map.addLayer({id:'capital-city-major-labels',type:'symbol',source:'capital-cities',minzoom:1.3,maxzoom:3.5,filter:['<=',['get','scalerank'],2],layout:{'text-field':['get','name'],'text-size':9,'text-offset':[0,1.05],'text-anchor':'top','text-allow-overlap':false},paint:{'text-color':'#e8d7a9','text-halo-color':'#080b0b','text-halo-width':1.05}});
      map.addLayer({id:'capital-city-labels',type:'symbol',source:'capital-cities',minzoom:3.2,layout:{'text-field':['get','name'],'text-size':10,'text-offset':[0,1.1],'text-anchor':'top','text-allow-overlap':false},paint:{'text-color':'#f7e8a4','text-halo-color':'#080b0b','text-halo-width':1.1}});
      map.on('click','capital-cities',event=>{const code=event.features?.[0]?.properties?.iso3;if(code&&window.goCountry)window.goCountry(code)});
      map.on('mouseenter','capital-cities',()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave','capital-cities',()=>map.getCanvas().style.cursor='');
    }
    setCapitalVisibility(true);
  }catch(error){
    console.warn('Default capital layer unavailable:',error);button.textContent='Capital cities · unavailable';button.disabled=true;
  }
}

function tuneMapSurface(){
  const map=window.__potatoAtlasMap;if(!map)return;
  try{if(map.getLayer('country-hubs'))map.setLayoutProperty('country-hubs','visibility','none');}catch{}
  try{if(map.getLayer('relations')){map.setPaintProperty('relations','line-width',['interpolate',['linear'],['zoom'],2,.75,6,1.8]);map.setPaintProperty('relations','line-opacity',['step',['get','depth'],.58,2,.4,3,.26]);}}catch{}
  try{if(map.getLayer('semantic-links')){map.setPaintProperty('semantic-links','line-width',.75);map.setPaintProperty('semantic-links','line-opacity',.34);}}catch{}
  const interior=document.getElementById('interior');
  if(interior?.classList.contains('active'))interior.click();
}

installSleekSurface();
tuneMapSurface();
installCapitals();

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