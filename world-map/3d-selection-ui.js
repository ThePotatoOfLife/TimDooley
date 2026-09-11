const map = window.__potatoAtlasMap;
const app = document.getElementById('atlasApp');
const mapwrap = document.querySelector('.mapwrap');
const layersPop = document.querySelector('#layersMenu .menu-pop');
const tools = document.getElementById('atlasToolsMenu');
const traceMenu = document.getElementById('traceMenu');

if (!map || !mapwrap) throw new Error('Selection UI requires the core atlas map.');

const style = document.createElement('style');
style.id = 'atlasSelectionStyle';
style.textContent = `
  #atlasSelectionDock{position:absolute;z-index:5;left:50%;bottom:10px;transform:translateX(-50%);display:flex;align-items:center;gap:5px;max-width:calc(100% - 24px);padding:5px 6px;border:1px solid #324442;border-radius:999px;background:#0b1212f2;box-shadow:0 7px 20px #0007;white-space:nowrap}
  #atlasSelectionDock[hidden]{display:none!important}
  #atlasSelectionDock .selection-name{max-width:180px;overflow:hidden;text-overflow:ellipsis;padding:0 7px;font-weight:650;color:#edf3e9}
  #atlasSelectionDock button{padding:5px 8px;border-radius:999px;background:#14201f}
  #atlasSelectionDock button.active{color:#8fc6ef;border-color:#5d8bad}
  #atlasSelectionDock .selection-clear{font-size:16px;line-height:1;padding:4px 7px;color:#aeb9b2}
  #atlasSelectionDock .selection-more{position:relative}
  #atlasSelectionDock .selection-more>summary{list-style:none;cursor:pointer;padding:5px 8px;border:1px solid var(--line);border-radius:999px;background:#14201f;color:var(--muted);line-height:1.1}
  #atlasSelectionDock .selection-more>summary::-webkit-details-marker{display:none}
  #atlasSelectionDock .selection-more-pop{position:absolute;left:50%;bottom:calc(100% + 7px);transform:translateX(-50%);min-width:120px;padding:5px;border:1px solid var(--line);border-radius:9px;background:#0d1514;box-shadow:0 8px 22px #0008}
  #atlasSelectionDock .selection-more-pop button{display:block;width:100%;margin:2px 0;text-align:left}
  .atlas-layer-registry{margin-top:7px;border-top:1px solid var(--line);padding-top:6px}
  .atlas-layer-group{margin:4px 0}.atlas-layer-group>summary{cursor:pointer;padding:6px 2px;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.1em;list-style:none}.atlas-layer-group>summary::-webkit-details-marker{display:none}.atlas-layer-group>summary::after{content:' +';opacity:.6}.atlas-layer-group[open]>summary::after{content:' −'}
  .atlas-layer-group-body>*{display:block;width:100%;margin:4px 0}
  @media(max-width:900px){#atlasSelectionDock{bottom:8px;max-width:calc(100% - 16px);overflow-x:auto;justify-content:flex-start;border-radius:12px}#atlasSelectionDock .selection-name{max-width:120px;flex:0 0 auto}}
`;
document.head.appendChild(style);

const dock = document.createElement('div');
dock.id = 'atlasSelectionDock';
dock.hidden = true;
dock.innerHTML = `
  <span class="selection-name"></span>
  <button data-action="details" title="Open country details">Details</button>
  <button data-action="connections" title="Show or hide country connections">Connections</button>
  <details class="selection-more">
    <summary title="More country actions" aria-label="More country actions">•••</summary>
    <div class="selection-more-pop">
      <button data-action="focus" title="Fit the selected country">Focus</button>
      <button data-action="compare" title="Add this country to comparison">Compare</button>
    </div>
  </details>
  <button class="selection-clear" data-action="clear" title="Deselect country" aria-label="Deselect country">×</button>
`;
mapwrap.appendChild(dock);

function currentSelection() {
  return window.__potatoAtlasSelection?.current || { selected: false, code: null, name: null, compareMode: false };
}

function panelOpen() { return !app?.classList.contains('panel-collapsed'); }

function syncDock() {
  const current = currentSelection();
  dock.hidden = !current.selected || current.compareMode || panelOpen();
  if (!current.selected) return;
  dock.querySelector('.selection-name').textContent = current.name || current.code || 'Country';
  dock.querySelector('[data-action="connections"]')?.classList.toggle('active', document.getElementById('relations')?.classList.contains('active'));
}

function openAnalyze() {
  if (tools) tools.open = true;
  if (traceMenu) traceMenu.open = true;
}

dock.addEventListener('click', event => {
  const button = event.target.closest('button[data-action]');
  if (!button) return;
  const action = button.dataset.action;
  if (action === 'details') {
    window.showOverview?.();
    window.__potatoAtlasUI?.setPanel?.(true, { persist: false });
  } else if (action === 'connections') {
    const relations = document.getElementById('relations');
    relations?.click();
    if (relations?.classList.contains('active')) openAnalyze();
  } else if (action === 'compare') {
    window.addCurrentToCompare?.();
  } else if (action === 'focus') {
    window.fitCountry?.();
  } else if (action === 'clear') {
    window.clearCountrySelection?.();
  }
  const more = button.closest('.selection-more');
  if (more) more.open = false;
  queueMicrotask(syncDock);
});

window.addEventListener('potato-atlas-selection-change', syncDock);
window.addEventListener('potato-atlas-panel-change', syncDock);
window.addEventListener('potato-atlas-relations-change', syncDock);
document.addEventListener('click', event => {
  if (event.target?.id === 'compare') queueMicrotask(syncDock);
});

// Future-proof geographic layer registry. New place/object layers should register
// here rather than inventing new top-bar controls. Country knowledge belongs in
// the inspector/module orbit; geographic objects belong in this registry.
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

function registerLayer({ id, label, group = 'Overlays', kind = 'overlay', scope = 'global', minZoom = 0, maxZoom = 24, description = '', getVisible, setVisible, element }) {
  if (!id || registrations.has(id)) return registrations.get(id);
  const body = groupBody(group);
  let control = element || document.createElement('button');
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
  const record = { id, label: label || id, group, kind, scope, minZoom, maxZoom, description, getVisible, setVisible, element: control };
  registrations.set(id, record);
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
  register: registerLayer,
  refresh: refreshLayer,
  get(id) { return registrations.get(id); },
  list() { return [...registrations.values()]; },
};

function adoptExistingControls() {
  const capitals = document.getElementById('capitals');
  if (capitals && !registrations.has('capitals')) {
    registerLayer({
      id: 'capitals', label: 'Capital cities', group: 'Places', element: capitals,
      getVisible: () => window.__potatoAtlasCapitals?.visible !== false,
    });
  }

  const interior = document.getElementById('interior');
  if (interior && !registrations.has('module-orbit')) {
    interior.textContent = 'Module orbit · advanced';
    interior.title = 'Optional semantic country modules on the map. Use the selection dock and Details for normal navigation.';
    registerLayer({ id: 'module-orbit', label: 'Module orbit · advanced', group: 'Country knowledge', element: interior });
  }

  const field = document.getElementById('axisFieldView');
  if (field && !registrations.has('project-fields')) registerLayer({ id: 'project-fields', label: 'Project fields', group: 'Overlays', element: field });
  const network = document.getElementById('empiricalNetworkView');
  if (network && !registrations.has('empirical-networks')) registerLayer({ id: 'empirical-networks', label: 'Empirical networks', group: 'Overlays', element: network });
}

adoptExistingControls();
window.addEventListener('potato-atlas-capitals-ready', () => { adoptExistingControls(); window.__potatoAtlasLayerRegistry.refresh('capitals'); });
window.addEventListener('potato-atlas-capitals-change', () => window.__potatoAtlasLayerRegistry.refresh('capitals'));
window.addEventListener('potato-atlas-module-ready', adoptExistingControls);

syncDock();
