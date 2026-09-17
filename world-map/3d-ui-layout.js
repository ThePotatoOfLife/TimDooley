// World Map application-surface layout coordinator.
// Owns placement only; domain modules continue to own content and behavior.

const mapwrap = document.querySelector('.mapwrap');
const app = document.getElementById('atlasApp');
const panel = document.getElementById('panel');
const registrations = new Map();
const ZONES = new Set(['top','right-inspector','left-status','bottom-context','canvas-control']);
let refreshScheduled = false;
let refreshing = false;

function ensureStyle() {
  if (document.getElementById('atlasUILayoutStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasUILayoutStyle';
  style.textContent = `
    body.atlas-registry-ui .hud,body.atlas-registry-ui .camera{display:none!important}
    #atlasUILeftStatus{position:absolute;left:10px;bottom:10px;z-index:7;display:flex;flex-direction:column-reverse;align-items:flex-start;gap:6px;width:min(300px,calc(100% - 20px));pointer-events:none}
    #atlasUILeftStatus>*{position:static!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;margin:0!important;max-width:100%;pointer-events:auto}
    #atlasUIBottomContext{position:absolute;left:50%;bottom:10px;z-index:8;transform:translateX(-50%);display:flex;align-items:flex-end;justify-content:center;width:min(760px,calc(100% - 360px));max-width:calc(100% - 24px);pointer-events:none}
    #atlasUIBottomContext>*{position:static!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;transform:none!important;max-width:100%;pointer-events:auto}
    #atlasUILeftStatus #atlasWorldContext{width:min(290px,100%)!important}
    #atlasUILeftStatus #atlasTimeState{width:auto!important}
    #atlasUILeftStatus #atlasLensLegend{width:min(340px,100%)!important}
    #atlasUILeftStatus #axisFieldLegend{width:min(430px,100%)!important;pointer-events:none!important}
    #atlasUILeftStatus #axisOperatorHud{width:min(420px,100%)!important;pointer-events:none!important}
    #axisDepthNavigator[data-layout-hosted="1"]{display:none!important}
    .atlas-axis-inspector-nav{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;margin:9px 0}
    .atlas-axis-inspector-nav button{min-width:0;padding:6px 4px;font-size:9px}
    @media(max-width:900px){
      #atlasUILeftStatus{left:8px;bottom:8px;width:min(250px,calc(100% - 16px));gap:4px}
      #atlasUIBottomContext{left:8px;right:8px;bottom:8px;transform:none;width:auto;max-width:none;justify-content:flex-start}
      body:has(#atlasWorldBar details[open]) #atlasUILeftStatus{opacity:0;pointer-events:none}
      .panel{top:auto!important;left:8px!important;right:8px!important;bottom:8px!important;width:auto!important;max-height:44vh!important}
      body:not(.panel-collapsed) #atlasUIBottomContext{bottom:calc(44vh + 16px)}
    }
  `;
  document.head.appendChild(style);
}

function ensureHost(id, ariaLabel) {
  if (!mapwrap) return null;
  let host = document.getElementById(id);
  if (!host) {
    host = document.createElement('aside');
    host.id = id;
    host.setAttribute('aria-label', ariaLabel);
    mapwrap.appendChild(host);
  }
  return host;
}
function ensureLeftStatusHost() { return ensureHost('atlasUILeftStatus', 'Map status'); }
function ensureBottomContextHost() { return ensureHost('atlasUIBottomContext', 'Pinned map context'); }

function resolveElement(value) {
  if (value instanceof Element) return value;
  if (typeof value === 'string') return document.querySelector(value);
  return null;
}

function upsertRegistration({ id, zone, element, priority = 0, mode = 'persistent' }) {
  if (!id || !ZONES.has(zone)) throw new Error(`Unsupported UI layout registration: ${id || '<missing>'} / ${zone}`);
  const node = resolveElement(element);
  registrations.set(id, { id, zone, element:node, priority:Number(priority)||0, mode, visible:node ? !node.hidden : false });
  return node;
}

function scheduleRefresh() {
  if (refreshScheduled) return;
  refreshScheduled = true;
  queueMicrotask(() => {
    refreshScheduled = false;
    refresh();
  });
}
function register(options) { const node = upsertRegistration(options); scheduleRefresh(); return node; }
function unregister(id) { registrations.delete(id); scheduleRefresh(); }
function setVisible(id, visible) {
  const row = registrations.get(id);
  if (!row) return false;
  row.visible = Boolean(visible);
  if (row.element) row.element.hidden = !row.visible;
  scheduleRefresh();
  return true;
}
function getState() {
  return [...registrations.values()].map(row => ({ id:row.id, zone:row.zone, priority:row.priority, mode:row.mode, visible:row.visible }));
}

function refreshZone(zone, host) {
  if (!host) return;
  const rows = [...registrations.values()]
    .filter(row => row.zone === zone && row.element)
    .sort((a,b) => a.priority - b.priority || a.id.localeCompare(b.id));
  for (const row of rows) if (row.element.parentElement !== host) host.appendChild(row.element);
}
function refreshLeftStatus() { refreshZone('left-status', ensureLeftStatusHost()); }
function refreshBottomContext() { refreshZone('bottom-context', ensureBottomContextHost()); }

function adoptKnownSurfaces() {
  const context = document.getElementById('atlasWorldContext');
  if (context && !registrations.has('world-context')) upsertRegistration({ id:'world-context', zone:'left-status', element:context, priority:30 });
  const time = document.getElementById('atlasTimeState');
  if (time && !registrations.has('time-state')) upsertRegistration({ id:'time-state', zone:'left-status', element:time, priority:20 });
  const lens = document.getElementById('atlasLensLegend');
  if (lens && !registrations.has('lens-legend')) upsertRegistration({ id:'lens-legend', zone:'left-status', element:lens, priority:40 });
  const fieldLegend = document.getElementById('axisFieldLegend');
  if (fieldLegend && !registrations.has('axis-field-legend')) upsertRegistration({ id:'axis-field-legend', zone:'left-status', element:fieldLegend, priority:45 });
  const operatorHud = document.getElementById('axisOperatorHud');
  if (operatorHud && !registrations.has('axis-operator-hud')) upsertRegistration({ id:'axis-operator-hud', zone:'left-status', element:operatorHud, priority:50 });
  if (panel && !registrations.has('main-inspector')) upsertRegistration({ id:'main-inspector', zone:'right-inspector', element:panel, priority:100 });
  const pinned = document.getElementById('atlasPinnedContextRail');
  if (pinned && !registrations.has('pinned-context')) upsertRegistration({ id:'pinned-context', zone:'bottom-context', element:pinned, priority:20 });
  const axisToggle = document.getElementById('axisCompactToggle');
  if (axisToggle && !registrations.has('axis-compact')) upsertRegistration({ id:'axis-compact', zone:'canvas-control', element:axisToggle, priority:50 });
  const axisNav = document.getElementById('axisDepthNavigator');
  if (axisNav) { axisNav.dataset.layoutHosted = '1'; axisNav.hidden = true; }
}

function appendAxisInspectorNavigator() {
  const axis = window.__potatoAxisDepth;
  if (!axis?.data || !panel || panel.querySelector('.atlas-axis-inspector-nav')) return;
  const levels = [...(axis.data.levels || [])].sort((a,b)=>b.dimension-a.dimension);
  const nav = document.createElement('div');
  nav.className = 'atlas-axis-inspector-nav';
  nav.setAttribute('aria-label','Axis dimensions');
  nav.innerHTML = levels.map(level => `<button type="button" data-ui-axis-d="${Number(level.dimension)}">D${Number(level.dimension)}</button>`).join('');
  nav.addEventListener('click', event => {
    const button = event.target.closest('[data-ui-axis-d]');
    if (!button) return;
    axis.setDimension(Number(button.dataset.uiAxisD));
    queueMicrotask(appendAxisInspectorNavigator);
  });
  const actions = panel.querySelector('.actions');
  if (actions) actions.before(nav); else panel.appendChild(nav);
}
function openAxisInspector() {
  const axis = window.__potatoAxisDepth;
  if (!axis?.setDimension) return;
  app?.classList.remove('panel-collapsed');
  axis.setDimension(axis.getDimension?.() || 4, { silentCamera:true });
  queueMicrotask(appendAxisInspectorNavigator);
}

function refresh() {
  if (refreshing) { scheduleRefresh(); return; }
  refreshing = true;
  try {
    ensureStyle();
    adoptKnownSurfaces();
    refreshLeftStatus();
    refreshBottomContext();
    if (window.__potatoAtlasDiagnostics) window.__potatoAtlasDiagnostics.uiLayoutRefreshes = (window.__potatoAtlasDiagnostics.uiLayoutRefreshes || 0) + 1;
    window.dispatchEvent(new CustomEvent('potato-atlas-ui-layout-change', { detail:{ surfaces:getState() } }));
  } finally { refreshing = false; }
}

document.addEventListener('click', event => {
  const button = event.target.closest('#axisCompactToggle');
  if (!button) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  openAxisInspector();
}, true);

window.addEventListener('atlas-axis-dimension-change', () => queueMicrotask(appendAxisInspectorNavigator));
window.addEventListener('potato-atlas-panel-rendered', scheduleRefresh);
window.addEventListener('potato-atlas-module-ready', scheduleRefresh);
window.addEventListener('potato-atlas-pinned-context-ready', scheduleRefresh);
window.addEventListener('atlas-time-change', scheduleRefresh);
window.addEventListener('load', scheduleRefresh, { once:true });

window.__potatoAtlasUILayout = { register, unregister, setVisible, getState, refresh, scheduleRefresh };
refresh();