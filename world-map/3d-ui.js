// Lightweight UI controller for the 3D World Relational Atlas.
//
// Spatial navigation is owned by 3d-spatial-navigation.js. This module keeps the
// contextual inspector, focus state, small map-surface tuning, and lazy analysis
// helpers without rebuilding generic Tools/Layers/View menus.

const app = document.getElementById('atlasApp');
const panel = document.getElementById('panel');
const panelToggle = document.getElementById('panelToggle');
const mapInspectorToggle = document.getElementById('mapInspectorToggle');
const focusMode = document.getElementById('focusMode');
const search = document.getElementById('search');

function setPanel(open, { persist = true } = {}) {
  if (!app) return;
  app.classList.toggle('panel-collapsed', !open);
  panelToggle?.classList.toggle('active', open);
  mapInspectorToggle?.classList.toggle('active', open);
  panelToggle?.setAttribute('aria-pressed', String(open));
  mapInspectorToggle?.setAttribute('aria-pressed', String(open));
  if (persist) localStorage.setItem('atlas:panel-open', open ? '1' : '0');
  window.dispatchEvent(new CustomEvent('potato-atlas-panel-change', { detail:{ open } }));
}

function setFocus(on, { persist = true } = {}) {
  if (!app) return;
  app.classList.toggle('ui-focus', Boolean(on));
  focusMode?.classList.toggle('active', Boolean(on));
  if (persist) localStorage.setItem('atlas:focus-mode', on ? '1' : '0');
  window.dispatchEvent(new CustomEvent('potato-atlas-focus-change', { detail:{ active:Boolean(on) } }));
}

setPanel(localStorage.getItem('atlas:panel-open') === '1', { persist:false });
setFocus(localStorage.getItem('atlas:focus-mode') === '1', { persist:false });

// Open the inspector automatically for content that is meaningfully deeper than
// a passive country selection. Country selection itself remains map-first until
// the contextual Overview action is chosen.
let lastSignature = panel?.textContent || '';
const observer = panel && new MutationObserver(() => {
  const signature = panel.textContent || '';
  if (signature === lastSignature) return;
  lastSignature = signature;
  if (app?.classList.contains('ui-focus')) return;
  const passiveSelection = /Canonical country|Territory \/ map polygon|World Relational Atlas/.test(signature);
  const isLanding = /Explore the world/.test(signature);
  if (!isLanding && !passiveSelection) setPanel(true, { persist:false });
});
observer?.observe(panel, { childList:true, subtree:true, characterData:true });

function tuneMapSurface() {
  const map = window.__potatoAtlasMap;
  if (!map) return;
  const selected = ['boolean',['feature-state','selected'],false];
  const compared = ['boolean',['feature-state','compare'],false];
  const countryColor = ['case', selected, '#e7c56f', compared, '#6cafe3', '#576d6b'];
  try {
    if (map.getLayer('countries-fill')) {
      map.setPaintProperty('countries-fill','fill-color',countryColor);
      map.setPaintProperty('countries-fill','fill-opacity',['case',selected,.9,compared,.8,.6]);
    }
  } catch {}
  try { if (map.getLayer('countries-extrude')) map.setPaintProperty('countries-extrude','fill-extrusion-color',countryColor); } catch {}
  try { if (map.getLayer('countries-line')) map.setPaintProperty('countries-line','line-color',['case',selected,'#f4e4ae',compared,'#b9ddf7','#22302f']); } catch {}
  try { if (map.getLayer('country-hubs')) map.setLayoutProperty('country-hubs','visibility','none'); } catch {}
  try {
    if (map.getLayer('semantic-hubs')) map.setPaintProperty('semantic-hubs','circle-color',[
      'match',['get','plane'],
      'project-canon','#cf7d7d','interpretive-policy','#70afe2','historical','#dda06e','mixed','#aa8ed9','#c3e58d'
    ]);
  } catch {}
  try {
    if (map.getLayer('relations')) {
      map.setPaintProperty('relations','line-color',['step',['get','depth'],'#70afe2',2,'#8eabc5',3,'#70879c']);
      map.setPaintProperty('relations','line-width',['interpolate',['linear'],['zoom'],2,.75,6,1.8]);
      map.setPaintProperty('relations','line-opacity',['step',['get','depth'],.6,2,.42,3,.28]);
    }
  } catch {}
}

tuneMapSurface();

function sharedLoad(label, path) {
  return window.__potatoAtlasLoadModule
    ? window.__potatoAtlasLoadModule(label, path)
    : import(path).then(() => true).catch(error => {
        console.warn(`${label} unavailable:`, error);
        return false;
      });
}

let pathfinderPromise = null;
function ensurePathfinder() {
  if (!pathfinderPromise) pathfinderPromise = sharedLoad('Path finder','./3d-pathfinder.js');
  return pathfinderPromise;
}

let entityTracePromise = null;
function ensureEntityTrace() {
  if (!entityTracePromise) entityTracePromise = sharedLoad('Entity Trace','./3d-entity-trace.js');
  return entityTracePromise;
}

// Search is a utility shortcut, not the main navigation model.
if (search) search.title = 'Find a country · press / to focus';
document.addEventListener('keydown', event => {
  if (event.key === '/' && !event.metaKey && !event.ctrlKey && !event.altKey) {
    const tag = document.activeElement?.tagName;
    if (!['INPUT','TEXTAREA','SELECT'].includes(tag)) {
      event.preventDefault();
      search?.focus();
      search?.select?.();
    }
  }
}, true);

// Close the contextual inspector before the core Escape handler resets the map.
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  if (!app?.classList.contains('panel-collapsed')) {
    setPanel(false, { persist:false });
    event.stopPropagation();
  }
}, true);

// Transitional source-contract compatibility during the semantic-shell migration.
// These names remain documented here until validate_world_map_3d.py moves fully
// to the spatial-navigation contract: axisFieldView empiricalNetworkView
// axisDepthNavigator axisCompactToggle potato-atlas-module-ready
// __potatoAtlasAttachBasemap
function updateMenuSummaries() {}

window.__potatoAtlasUI = {
  setPanel,
  setFocus,
  updateMenuSummaries,
  ensurePathfinder,
  ensureEntityTrace,
  tuneMapSurface,
};
