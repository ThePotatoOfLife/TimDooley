const map = window.__potatoAtlasMap;
const app = document.getElementById('atlasApp');
const mapwrap = document.querySelector('.mapwrap');
const layersPop = document.querySelector('#layersMenu .menu-pop');
const traceMenu = document.getElementById('traceMenu');
const capabilities = window.__potatoAtlasCapabilities;

if (!map || !mapwrap) throw new Error('Selection UI requires the core atlas map.');

const style = document.createElement('style');
style.id = 'atlasSelectionStyle';
style.textContent = `
  #atlasSelectionDock{position:absolute;z-index:9;left:50%;bottom:52px;transform:translateX(-50%);display:flex;align-items:center;gap:4px;max-width:calc(100% - 110px);padding:5px 6px;border:1px solid #324442;border-radius:18px;background:#0b1212f4;box-shadow:0 9px 26px #0008;white-space:nowrap}
  #atlasSelectionDock[hidden]{display:none!important}
  #atlasSelectionDock .selection-name{max-width:170px;overflow:hidden;text-overflow:ellipsis;padding:0 8px;font-weight:700;color:#edf3e9}
  #atlasSelectionDock button{padding:6px 8px;border-radius:999px;background:#14201f;font-size:11px}
  #atlasSelectionDock button.active{color:#a8d4f3;border-color:#5d8bad;background:#142432}
  #atlasSelectionDock button[data-action="change"]{color:#cfb9ef}
  #atlasSelectionDock button[data-action="sources"]{color:#d4dad7}
  #atlasSelectionDock .selection-clear{font-size:16px;line-height:1;padding:4px 7px;color:#aeb9b2}
  .atlas-layer-registry{margin-top:7px;border-top:1px solid var(--line);padding-top:6px}
  .atlas-layer-group{margin:4px 0}.atlas-layer-group>summary{cursor:pointer;padding:6px 2px;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.1em;list-style:none}.atlas-layer-group>summary::-webkit-details-marker{display:none}.atlas-layer-group>summary::after{content:' +';opacity:.6}.atlas-layer-group[open]>summary::after{content:' −'}
  .atlas-layer-group-body>*{display:block;width:100%;margin:4px 0}
  @media(max-width:900px){#atlasSelectionDock{left:8px;right:8px;bottom:48px;transform:none;max-width:none;overflow-x:auto;justify-content:flex-start;border-radius:13px}#atlasSelectionDock .selection-name{max-width:120px;flex:0 0 auto}#atlasSelectionDock button{flex:0 0 auto}}
`;
document.head.appendChild(style);

const dock = document.createElement('div');
dock.id = 'atlasSelectionDock';
dock.hidden = true;
dock.setAttribute('aria-label','Selected country actions');
dock.innerHTML = `
  <span class="selection-name"></span>
  <button data-action="overview" title="Open country overview">Overview</button>
  <button data-action="relations" title="Show this country's relations">Relations</button>
  <button data-action="compare" title="Compare this country">Compare</button>
  <button data-action="change" title="Explore time and change">Change</button>
  <button data-action="sources" title="Inspect evidence and sources">Sources</button>
  <button data-action="focus" title="Fit the selected country">Focus</button>
  <button class="selection-clear" data-action="clear" title="Deselect country" aria-label="Deselect country">×</button>
`;
mapwrap.appendChild(dock);

function currentSelection() {
  return window.__potatoAtlasSelection?.current || { selected:false, code:null, name:null, compareMode:false };
}

function panelOpen() { return !app?.classList.contains('panel-collapsed'); }

function relationsVisible() {
  return document.getElementById('relations')?.classList.contains('active') || window.__potatoAtlasRelations?.getVisible?.() === true;
}

function syncDock() {
  const current = currentSelection();
  dock.hidden = !current.selected || current.compareMode || panelOpen();
  if (!current.selected) return;
  dock.querySelector('.selection-name').textContent = current.name || current.code || 'Country';
  dock.querySelector('[data-action="relations"]')?.classList.toggle('active', relationsVisible());
}

let countryDimensionsRequested = false;
function promoteCountryDimensions() {
  if (countryDimensionsRequested) return;
  const loader = window.__potatoAtlasLoadModule;
  if (typeof loader !== 'function') return;
  countryDimensionsRequested = true;
  loader('Country dimensions', './3d-country-dimensions.js');
}

async function openSources() {
  const loader = window.__potatoAtlasLoadModule;
  if (typeof loader === 'function') await loader('Evidence', './3d-evidence.js');
  window.refreshAtlasEvidence?.();
  window.__potatoAtlasUI?.setPanel?.(true, {persist:false});
}

function openRelations() {
  const relations = document.getElementById('relations');
  if (window.__potatoAtlasRelations?.setVisible) {
    window.__potatoAtlasRelations.setVisible(true);
  } else if (relations && !relations.classList.contains('active')) {
    relations.click();
  }
  window.__potatoAtlasSpatialUI?.openZone?.('relations');
  if (traceMenu && !window.__potatoAtlasSpatialUI) traceMenu.open = true;
}

function openTime() {
  window.__potatoAtlasSpatialUI?.openZone?.('time');
  window.dispatchEvent(new CustomEvent('potato-atlas-selection-time-request', {detail:{selection:currentSelection()}}));
}

function onSelectionChange(event) {
  syncDock();
  if (event?.detail?.selected) promoteCountryDimensions();
}

dock.addEventListener('click', event => {
  const button = event.target.closest('button[data-action]');
  if (!button) return;
  const action = button.dataset.action;
  if (action === 'overview') {
    promoteCountryDimensions();
    window.showOverview?.();
    window.__potatoAtlasUI?.setPanel?.(true, {persist:false});
  } else if (action === 'relations') {
    openRelations();
  } else if (action === 'compare') {
    if (window.__potatoAtlasCompare?.startWithCurrent) window.__potatoAtlasCompare.startWithCurrent();
    else window.addCurrentToCompare?.();
  } else if (action === 'change') {
    openTime();
  } else if (action === 'sources') {
    openSources();
  } else if (action === 'focus') {
    window.fitCountry?.();
  } else if (action === 'clear') {
    window.clearCountrySelection?.();
  }
  queueMicrotask(syncDock);
});

window.addEventListener('potato-atlas-selection-change', onSelectionChange);
window.addEventListener('potato-atlas-panel-change', syncDock);
window.addEventListener('potato-atlas-relations-change', syncDock);

// Temporary legacy geographic-layer registry remains for older providers while
// semantic capabilities migrate. It is hidden inside compatibility plumbing.
const registryHost = document.createElement('div');
registryHost.className = 'atlas-layer-registry';
registryHost.innerHTML = '<div class="menu-title">Map layers</div>';
layersPop?.appendChild(registryHost);
const groups = new Map();
const registrations = new Map();

function groupBody(name) {
  if (groups.has(name)) return groups.get(name);
  const details = document.createElement('details');
  details.className = 'atlas-layer-group';
  details.open = name === 'Places';
  const summary = document.createElement('summary');
  summary.textContent = name;
  const body = document.createElement('div');
  body.className = 'atlas-layer-group-body';
  details.append(summary, body);
  registryHost.appendChild(details);
  groups.set(name, body);
  return body;
}

function registerLayer({ id, label, group='Overlays', kind='overlay', scope='global', minZoom=0, maxZoom=24, description='', getVisible, setVisible, element }) {
  if (!id || registrations.has(id)) return registrations.get(id);
  const body = groupBody(group);
  const control = element || document.createElement('button');
  if (!element) {
    control.textContent = label || id;
    control.addEventListener('click', () => {
      const visible = Boolean(getVisible?.());
      setVisible?.(!visible);
      refreshLayer(id);
    });
  }
  if (label && element) control.textContent = label;
  body.appendChild(control);
  const record = {id,label:label||id,group,kind,scope,minZoom,maxZoom,description,getVisible,setVisible,element:control};
  registrations.set(id,record);
  refreshLayer(id);
  return record;
}

function refreshLayer(id) {
  const record = registrations.get(id);
  if (!record) return;
  const visible = record.getVisible ? Boolean(record.getVisible()) : record.element.classList.contains('active');
  record.element.classList.toggle('active', visible);
  record.element.setAttribute('aria-pressed', String(visible));
}

window.__potatoAtlasLayerRegistry = {
  register:registerLayer,
  refresh:refreshLayer,
  get:id=>registrations.get(id),
  list:()=>[...registrations.values()],
};

let capitalsCapabilityRegistered = false;
function registerSemanticCapitals() {
  if (capitalsCapabilityRegistered || !capabilities || !window.__potatoAtlasCapitals?.setVisible) return;
  capabilities.register({
    id:'world:places:capitals',
    name:'Capital cities',
    zone:'world',
    category:'Places',
    kind:'place',
    stateSlot:'worldOverlays',
    colorFamily:'world',
    description:'Show capital-city points and labels.',
    order:10,
    epistemicLayer:'empirical',
    timeSupport:{type:'current-geographic-context'},
    activate:()=>window.__potatoAtlasCapitals.setVisible(true),
    deactivate:()=>window.__potatoAtlasCapitals.setVisible(false),
    getState:()=>({active:window.__potatoAtlasCapitals.visible !== false}),
  });
  capitalsCapabilityRegistered = true;
}

function adoptExistingControls() {
  const capitals = document.getElementById('capitals');
  if (capitals && !registrations.has('capitals')) {
    registerLayer({id:'capitals',label:'Capital cities',group:'Places',element:capitals,getVisible:()=>window.__potatoAtlasCapitals?.visible !== false});
  }
  const interior = document.getElementById('interior');
  if (interior && !registrations.has('module-orbit')) {
    interior.textContent = 'Module orbit · advanced';
    interior.title = 'Optional semantic country modules on the map.';
    registerLayer({id:'module-orbit',label:'Module orbit · advanced',group:'Country knowledge',element:interior});
  }
  const field = document.getElementById('axisFieldView');
  if (field && !registrations.has('project-fields')) registerLayer({id:'project-fields',label:'Project fields',group:'Overlays',element:field});
  const network = document.getElementById('empiricalNetworkView');
  if (network && !registrations.has('empirical-networks')) registerLayer({id:'empirical-networks',label:'Empirical networks',group:'Overlays',element:network});
  registerSemanticCapitals();
}

adoptExistingControls();
window.addEventListener('potato-atlas-capitals-ready', () => {
  adoptExistingControls();
  window.__potatoAtlasLayerRegistry.refresh('capitals');
  capabilities?.refreshFromProviders?.();
});
window.addEventListener('potato-atlas-capitals-change', () => {
  window.__potatoAtlasLayerRegistry.refresh('capitals');
  capabilities?.refreshFromProviders?.();
});
window.addEventListener('potato-atlas-module-ready', adoptExistingControls);

syncDock();
if (currentSelection().selected) promoteCountryDimensions();
