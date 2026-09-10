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
  focusMode && (focusMode.textContent = on ? 'Focus mode · on' : 'Focus mode · hide overlays');
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
  summary.textContent=text;summary.classList.toggle('active-state',active);
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
  else summaryText('timeMenu',`Time · compare`,true);
}
function updateViewSummary(){
  const height=document.getElementById('height')?.value||'flat';
  const parts=[];
  if(height!=='flat')parts.push(height);
  if(app?.classList.contains('ui-focus'))parts.push('focus');
  summaryText('viewMenu',parts.length?`View · ${parts.join(' + ')}`:'View',parts.length>0);
}
function updateMenuSummaries(){updateLayerSummary();updateTraceSummary();updateTimeSummary();updateViewSummary();}

document.addEventListener('change',event=>{
  if(['relationType','axisFieldView','empiricalNetworkView','traceDepth','height','timeMode','timeDate','timeDate2'].includes(event.target?.id))queueMicrotask(updateMenuSummaries);
});
document.addEventListener('click',event=>{if(event.target?.id==='entityTraceToggle')queueMicrotask(updateTraceSummary);});
window.addEventListener('atlas-time-change',event=>updateTimeSummary(event.detail));

const layersPop = document.querySelector('#layersMenu .menu-pop');
const relocateInjectedLayerControls = () => {
  for (const id of ['axisFieldView','empiricalNetworkView']) {
    const node = document.getElementById(id);
    if (node && layersPop && node.parentElement !== layersPop) layersPop.appendChild(node);
  }
  updateLayerSummary();
};
new MutationObserver(relocateInjectedLayerControls).observe(document.body, {childList:true, subtree:true});
relocateInjectedLayerControls();

function installAxisToggle() {
  const nav = document.getElementById('axisDepthNavigator');
  if (!nav || document.getElementById('axisCompactToggle')) return;
  nav.hidden = localStorage.getItem('atlas:axis-open') !== '1';
  const button = document.createElement('button');
  button.id = 'axisCompactToggle';
  button.textContent = nav.hidden ? 'Axis' : 'Axis · open';
  button.title = 'Show or hide the D1–D11 Axis navigator';
  button.style.cssText = 'position:absolute;right:12px;top:44px;z-index:4;border-radius:999px;background:#0b1010df;backdrop-filter:blur(8px)';
  button.classList.toggle('active', !nav.hidden);
  button.addEventListener('click', () => {
    nav.hidden = !nav.hidden;
    localStorage.setItem('atlas:axis-open', nav.hidden ? '0' : '1');
    button.textContent = nav.hidden ? 'Axis' : 'Axis · open';
    button.classList.toggle('active', !nav.hidden);
  });
  document.querySelector('.mapwrap')?.appendChild(button);
}
new MutationObserver(installAxisToggle).observe(document.body, {childList:true,subtree:true});
installAxisToggle();

focusMode?.addEventListener('click',()=>queueMicrotask(updateViewSummary));
updateMenuSummaries();

// Entity-aware Trace is an opt-in investigation loaded through the progressive UI,
// not another permanent map overlay.
import('./3d-entity-trace.js').then(()=>updateTraceSummary()).catch(error=>console.warn('Entity Trace enhancement unavailable:',error));

window.__potatoAtlasUI = {setPanel,setFocus,updateMenuSummaries};
