// Compact ordinary control surface for the World Relational Atlas.
// The registry owns what can appear; this module only renders available ordinary
// controls and keeps the existing specialist machinery out of the normal path.

const layers = window.__potatoAtlasLayers;
const query = window.__potatoAtlasQuery;
if (!layers) throw new Error('World bar requires the layer registry.');
if (!query) throw new Error('World bar requires the query engine.');
await layers.ready;

const AXIS_IDS = ['axis.north', 'axis.west', 'axis.east', 'axis.south'];
const MENU_FAMILIES = [
  ['groups', 'Groups'],
  ['religion', 'Religion'],
  ['stats', 'Stats'],
  ['relations', 'Relations'],
];

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));

function ordinaryEntries(family) {
  return layers.entries(family, { availableOnly: true, ordinaryOnly: true });
}

function createMenu(family, label) {
  const details = document.createElement('details');
  details.className = 'atlas-world-menu';
  details.dataset.family = family;
  const summary = document.createElement('summary');
  summary.textContent = label;
  details.appendChild(summary);
  const pop = document.createElement('div');
  pop.className = 'atlas-world-menu-pop';
  details.appendChild(pop);
  return details;
}

function closeOtherMenus(current) {
  for (const menu of document.querySelectorAll('.atlas-world-menu[open]')) {
    if (menu !== current) menu.removeAttribute('open');
  }
}

async function updateSummary() {
  const node = document.getElementById('atlasWorldResult');
  if (!node) return;
  const setCount = query.activeSetCount();
  const active = layers.active();
  if (!active.length) {
    node.textContent = '';
    node.hidden = true;
    return;
  }
  node.hidden = false;
  if (setCount) {
    try {
      const matches = await query.matchedCountries();
      node.textContent = `${matches.length} countries`;
      return;
    } catch { /* keep a useful fallback */ }
  }
  node.textContent = `${active.length} layer${active.length === 1 ? '' : 's'}`;
}

function sync() {
  for (const id of AXIS_IDS) {
    const button = document.querySelector(`[data-layer-id="${CSS.escape(id)}"]`);
    if (button) button.classList.toggle('active', layers.isActive(id));
  }

  for (const menu of document.querySelectorAll('.atlas-world-menu')) {
    const family = menu.dataset.family;
    const pop = menu.querySelector('.atlas-world-menu-pop');
    if (!pop) continue;
    const rows = ordinaryEntries(family);
    if (family === 'relations') {
      pop.innerHTML = rows.map(entry => `<div class="atlas-world-static"><span>${esc(entry.label)}</span><small>${entry.id === 'relation.auto' ? 'Selected-country context' : esc(entry.availability)}</small></div>`).join('') || '<div class="atlas-world-empty">No current relation views</div>';
      continue;
    }
    pop.innerHTML = rows.map(entry => {
      const active = layers.isActive(entry.id);
      const swatch = entry.color ? `<i style="--layer-color:${esc(entry.color)}"></i>` : '';
      return `<button type="button" class="atlas-world-option${active ? ' active' : ''}" data-layer-option="${esc(entry.id)}">${swatch}<span>${esc(entry.label)}</span></button>`;
    }).join('') || '<div class="atlas-world-empty">No current layers</div>';
  }

  const queryBox = document.getElementById('atlasWorldQuery');
  const setCount = query.activeSetCount();
  if (queryBox) {
    queryBox.hidden = setCount < 2;
    queryBox.querySelectorAll('[data-query-mode]').forEach(button => button.classList.toggle('active', button.dataset.queryMode === query.getMode()));
  }

  document.querySelectorAll('.atlas-world-menu').forEach(menu => {
    const family = menu.dataset.family;
    if (family === 'relations') return;
    const count = ordinaryEntries(family).filter(entry => layers.isActive(entry.id)).length;
    menu.classList.toggle('active', count > 0);
    const summary = menu.querySelector('summary');
    const label = MENU_FAMILIES.find(([id]) => id === family)?.[1] || family;
    if (summary) summary.textContent = count ? `${label} · ${count}` : label;
  });

  updateSummary();
}

function installStyle() {
  if (document.getElementById('atlasWorldBarStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasWorldBarStyle';
  style.textContent = `
    body.atlas-registry-ui .top .quick-actions,
    body.atlas-registry-ui #layersMenu,
    body.atlas-registry-ui #traceMenu,
    body.atlas-registry-ui #timeMenu,
    body.atlas-registry-ui #viewMenu,
    body.atlas-registry-ui #moreMenu,
    body.atlas-registry-ui #atlasToolsMenu,
    body.atlas-registry-ui #atlasSelectionDock,
    body.atlas-registry-ui #atlasWorkingSelection,
    body.atlas-registry-ui #mapInspectorToggle,
    body.atlas-registry-ui .camera,
    body.atlas-registry-ui .hud{display:none!important}
    body.atlas-registry-ui .top{min-height:44px;padding:5px 9px}
    body.atlas-registry-ui .brand small{display:none}
    body.atlas-registry-ui .brand b{font-size:15px}
    #atlasWorldBar{position:absolute;left:10px;top:10px;z-index:8;display:flex;align-items:center;gap:5px;max-width:calc(100% - 20px);padding:5px;background:#080b0be8;border:1px solid #344343;border-radius:11px;box-shadow:0 8px 26px #0008;backdrop-filter:blur(11px)}
    #atlasWorldBar button,#atlasWorldBar summary{min-height:30px;padding:5px 8px;border-radius:7px;background:#111818;border:1px solid #2d3939;color:#e9efea;font-size:11px;line-height:1;white-space:nowrap}
    #atlasWorldBar button{cursor:pointer}
    #atlasWorldBar button.active,#atlasWorldBar .atlas-world-menu.active>summary,#atlasWorldBar .atlas-world-menu[open]>summary{border-color:#7a9892;color:#dff1d8;background:#172120}
    #atlasWorldBar .atlas-axis-button{font-weight:800;min-width:31px}
    #atlasWorldBar [data-layer-id="axis.north"].active{box-shadow:inset 0 -2px #79D6FF}
    #atlasWorldBar [data-layer-id="axis.west"].active{box-shadow:inset 0 -2px #14558A}
    #atlasWorldBar [data-layer-id="axis.east"].active{box-shadow:inset 0 -2px #C94F32}
    #atlasWorldBar [data-layer-id="axis.south"].active{box-shadow:inset 0 -2px #E8C84A}
    .atlas-world-menu{position:relative}.atlas-world-menu>summary{list-style:none;cursor:pointer}.atlas-world-menu>summary::-webkit-details-marker{display:none}
    .atlas-world-menu-pop{position:absolute;left:0;top:calc(100% + 7px);min-width:210px;max-width:260px;max-height:58vh;overflow:auto;padding:6px;background:#0b1010f7;border:1px solid #344343;border-radius:10px;box-shadow:0 12px 28px #000a}
    .atlas-world-option{display:flex!important;align-items:center;gap:7px;width:100%;margin:2px 0;text-align:left}.atlas-world-option i{width:9px;height:9px;border-radius:3px;background:var(--layer-color);flex:0 0 auto}.atlas-world-option span{overflow:hidden;text-overflow:ellipsis}.atlas-world-option.active:after{content:'✓';margin-left:auto;color:#bbdc8a}
    .atlas-world-static{display:flex;justify-content:space-between;gap:10px;padding:7px 6px;font-size:11px}.atlas-world-static small,.atlas-world-empty{color:#9aa6a0;font-size:9px}
    #atlasWorldQuery{display:flex;gap:2px;padding-left:4px;border-left:1px solid #2d3939}#atlasWorldQuery button{min-width:34px;padding-left:6px;padding-right:6px}
    #atlasWorldResult{padding:0 4px;color:#aab4aa;font-size:10px;white-space:nowrap}
    #atlasWorldReset{color:#aab4aa!important}
    @media(max-width:900px){#atlasWorldBar{left:7px;top:7px;right:7px;max-width:none;overflow-x:auto;overflow-y:visible}.atlas-world-menu-pop{position:fixed;left:8px;right:8px;top:96px;max-width:none}.top{overflow:visible!important}.top input{width:150px;min-width:130px}}
  `;
  document.head.appendChild(style);
}

function install() {
  if (document.getElementById('atlasWorldBar')) return;
  installStyle();
  document.body.classList.add('atlas-registry-ui');
  // The old hidden relation toggle starts active in the legacy HTML. Clear it so
  // the working-selection controller uses its bounded automatic relation context.
  document.getElementById('relations')?.classList.remove('active');
  const host = document.querySelector('.mapwrap');
  if (!host) return;

  const bar = document.createElement('div');
  bar.id = 'atlasWorldBar';
  bar.setAttribute('role', 'toolbar');
  bar.setAttribute('aria-label', 'World map analytical layers');

  for (const id of AXIS_IDS) {
    const entry = layers.get(id);
    if (!entry || entry.availability !== 'current') continue;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'atlas-axis-button';
    button.dataset.layerId = id;
    button.title = entry.label;
    button.setAttribute('aria-label', entry.label);
    button.textContent = entry.label.slice(0, 1).toUpperCase();
    button.addEventListener('click', () => layers.toggle(id));
    bar.appendChild(button);
  }

  for (const [family, label] of MENU_FAMILIES) {
    const menu = createMenu(family, label);
    menu.addEventListener('toggle', () => { if (menu.open) closeOtherMenus(menu); });
    menu.addEventListener('click', event => {
      const button = event.target.closest('[data-layer-option]');
      if (!button) return;
      layers.toggle(button.dataset.layerOption);
    });
    bar.appendChild(menu);
  }

  const queryBox = document.createElement('div');
  queryBox.id = 'atlasWorldQuery';
  queryBox.hidden = true;
  queryBox.innerHTML = '<button type="button" data-query-mode="any">ANY</button><button type="button" data-query-mode="all">ALL</button>';
  queryBox.addEventListener('click', event => {
    const button = event.target.closest('[data-query-mode]');
    if (button) query.setMode(button.dataset.queryMode);
  });
  bar.appendChild(queryBox);

  const result = document.createElement('span');
  result.id = 'atlasWorldResult';
  result.hidden = true;
  bar.appendChild(result);

  const reset = document.createElement('button');
  reset.id = 'atlasWorldReset';
  reset.type = 'button';
  reset.textContent = '×';
  reset.title = 'Clear analytical layers';
  reset.setAttribute('aria-label', 'Clear analytical layers');
  reset.addEventListener('click', () => window.__potatoAtlasCompositor?.reset?.());
  bar.appendChild(reset);

  host.appendChild(bar);
  sync();
}

window.addEventListener('potato-atlas-layer-change', sync);
window.addEventListener('potato-atlas-query-change', sync);
install();
