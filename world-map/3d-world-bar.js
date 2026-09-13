// Unified ordinary control surface for the World Relational Atlas.
const layers = window.__potatoAtlasLayers;
const query = window.__potatoAtlasQuery;
const map = window.__potatoAtlasMap;
if (!layers) throw new Error('World bar requires the layer registry.');
if (!query) throw new Error('World bar requires the query engine.');
if (!map) throw new Error('World bar requires the map instance.');
await layers.ready;

const AXIS_IDS = ['axis.north','axis.west','axis.east','axis.south'];
const MENU_FAMILIES = [['groups','Groups'],['religion','Religion'],['stats','Stats'],['relations','Relations']];
const RELATION_MODES = [['all','All context'],['money','Money'],['systems','Systems'],['institutions','Institutions'],['project','Project'],['other','Other']];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const ordinaryEntries = family => layers.entries(family, { availableOnly:true, ordinaryOnly:true });

const initialUrl = new URL(location.href);
let projectionMode = initialUrl.searchParams.get('projection') === 'globe' ? 'globe' : 'flat';
let activeView = window.__potatoAtlasActiveView?.current || null;
let timeState = null;

function persistProjection() {
  const url = new URL(location.href);
  url.searchParams.set('projection', projectionMode);
  history.replaceState({}, '', url);
}
function syncProjectionButton() {
  const button = document.getElementById('atlasProjectionToggle');
  if (!button) return;
  const globe = projectionMode === 'globe';
  button.classList.toggle('active', globe);
  button.textContent = globe ? '▭' : '◉';
  button.title = globe ? 'Switch to flat map' : 'Switch to globe';
  button.setAttribute('aria-label', button.title);
  button.setAttribute('aria-pressed', globe ? 'true' : 'false');
}
function applyProjection() {
  try {
    map.setProjection({ type: projectionMode === 'globe' ? 'globe' : 'mercator' });
  } catch (error) {
    console.warn('World Map projection unavailable:', error);
    projectionMode = 'flat';
    try { map.setProjection({ type:'mercator' }); } catch {}
  }
  persistProjection();
  syncProjectionButton();
  window.dispatchEvent(new CustomEvent('potato-atlas-projection-change', { detail:{ mode:projectionMode } }));
  renderContext();
  return projectionMode;
}
function setProjectionMode(mode) {
  projectionMode = mode === 'globe' ? 'globe' : 'flat';
  return applyProjection();
}
function toggleProjection() { return setProjectionMode(projectionMode === 'globe' ? 'flat' : 'globe'); }

window.__potatoAtlasProjection = {
  get() { return projectionMode; },
  set: setProjectionMode,
  toggle: toggleProjection,
};

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
function adoptLegacyMenu(id, label, onOpen = null) {
  const details = document.getElementById(id);
  if (!details) return null;
  details.hidden = false;
  details.classList.remove('menu');
  details.classList.add('atlas-world-menu','atlas-world-legacy-menu');
  details.dataset.legacyMenu = id;
  const summary = details.querySelector(':scope > summary');
  if (summary) summary.textContent = label;
  const pop = details.querySelector(':scope > .menu-pop');
  if (pop) pop.classList.add('atlas-world-menu-pop');
  details.addEventListener('toggle', () => {
    if (!details.open) return;
    closeOtherMenus(details);
    onOpen?.();
  });
  return details;
}
async function ensureTime() {
  if (window.__potatoAtlasTime) return true;
  return Boolean(await window.__potatoAtlasLoadModule?.('Time', './3d-time.js'));
}

function relationLabel(mode) {
  return RELATION_MODES.find(([id]) => id === mode)?.[1] || mode || 'All context';
}
function timeLabel(state) {
  if (!state || state.mode === 'current') return 'Current';
  if (state.label) return state.label;
  if (state.mode === 'as_of') return `As of ${state.time || '—'}`;
  return `${state.time || '—'} → ${state.time2 || '—'}`;
}
function currentPinnedCodes() {
  const selection = window.__potatoAtlasSelection;
  return selection?.current?.pinnedCodes || selection?.current?.selectedCodes || [];
}
function renderContext(view = activeView) {
  const node = document.getElementById('atlasWorldContext');
  if (!node) return;
  const entries = layers.active().map(id => layers.get(id)).filter(Boolean);
  const scalar = view?.scalar || entries.find(entry => entry.kind === 'scalar') || null;
  const sets = view?.sets || entries.filter(entry => entry.kind === 'set');
  const pinnedCodes = currentPinnedCodes();
  const relationMode = view?.relationMode || window.__potatoAtlasSelection?.getRelationMode?.() || 'all';
  const resolvedTime = view?.timeState || timeState;
  const hasTime = resolvedTime && resolvedTime.mode && resolvedTime.mode !== 'current';
  if (!entries.length && !pinnedCodes.length && relationMode === 'all' && !hasTime) {
    node.hidden = true;
    node.innerHTML = '';
    return;
  }

  const lines = [];
  if (scalar) {
    lines.push(`<div><span>Color</span><b>${esc(scalar.label)}</b></div>`);
    const coverage = view?.coverage;
    if (coverage) {
      const covered = Number(coverage.coverage ?? 0);
      const countries = Number(coverage.countries ?? coverage.country_count ?? 0);
      if (countries) lines.push(`<div><span>Coverage</span><b>${esc(covered)}/${esc(countries)} countries</b></div>`);
      if (coverage.period_min || coverage.period_max) {
        const period = coverage.period_min === coverage.period_max ? coverage.period_max : `${coverage.period_min || '?'}–${coverage.period_max || '?'}`;
        lines.push(`<div><span>Period</span><b>${esc(period)}</b></div>`);
      }
    }
  }
  if (sets.length) {
    const labels = sets.slice(0, 3).map(entry => entry.label).join(' · ');
    lines.push(`<div><span>Sets</span><b>${esc(labels)}${sets.length > 3 ? ` +${sets.length - 3}` : ''}</b></div>`);
    const mode = (view?.memberships?.mode || query.getMode() || 'any').toUpperCase();
    const count = Number(view?.matchCount);
    lines.push(`<div><span>Matches</span><b>${esc(mode)} · ${Number.isFinite(count) ? esc(count) + ' countries' : 'calculating…'}</b></div>`);
  }
  if (view?.code) lines.push(`<div><span>Active</span><b>${esc(view.code)}</b></div>`);
  if (pinnedCodes.length) lines.push(`<div><span>Pinned</span><b>${pinnedCodes.length} countr${pinnedCodes.length === 1 ? 'y' : 'ies'}</b></div>`);
  lines.push(`<div><span>Connections</span><b>${esc(relationLabel(relationMode))}</b></div>`);
  lines.push(`<div><span>Projection</span><b>${projectionMode === 'globe' ? 'Globe' : 'Flat'}</b></div>`);
  if (resolvedTime) lines.push(`<div><span>Time</span><b>${esc(timeLabel(resolvedTime))}</b></div>`);
  node.innerHTML = `<small>Current map view</small>${lines.join('')}`;
  node.hidden = false;
}
function renderSummary(view = activeView) {
  const node = document.getElementById('atlasWorldResult');
  if (!node) return;
  const active = layers.active();
  if (!active.length) { node.textContent = ''; node.hidden = true; return; }
  node.hidden = false;
  const setCount = query.activeSetCount();
  if (setCount) {
    const count = Number(view?.matchCount);
    node.textContent = Number.isFinite(count) ? `${count} countries` : '…';
    return;
  }
  node.textContent = `${active.length} layer${active.length === 1 ? '' : 's'}`;
}

function syncDynamicMenus() {
  for (const id of AXIS_IDS) {
    const button = document.querySelector(`[data-layer-id="${CSS.escape(id)}"]`);
    if (button) button.classList.toggle('active', layers.isActive(id));
  }
  syncProjectionButton();
  for (const menu of document.querySelectorAll('.atlas-world-menu')) {
    const family = menu.dataset.family;
    const pop = menu.querySelector('.atlas-world-menu-pop');
    if (!pop || !family) continue;
    if (family === 'relations') {
      const mode = window.__potatoAtlasSelection?.getRelationMode?.() || 'all';
      pop.innerHTML = `<div class="atlas-world-static"><span>Active-country connections</span><small>bounded context</small></div>${RELATION_MODES.map(([id,label]) => `<button type="button" class="atlas-world-option${mode === id ? ' active' : ''}" data-relation-mode="${esc(id)}"><span>${esc(label)}</span></button>`).join('')}`;
      menu.classList.toggle('active', mode !== 'all');
      const summary = menu.querySelector(':scope > summary');
      if (summary) {
        const activeLabel = relationLabel(mode);
        summary.textContent = mode === 'all' ? 'Relations' : `Relations · ${activeLabel}`;
      }
      continue;
    }
    const rows = ordinaryEntries(family);
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
  for (const menu of document.querySelectorAll('.atlas-world-menu')) {
    if (!menu.dataset.family || menu.dataset.family === 'relations') continue;
    const family = menu.dataset.family;
    const count = ordinaryEntries(family).filter(entry => layers.isActive(entry.id)).length;
    menu.classList.toggle('active', count > 0);
    const summary = menu.querySelector(':scope > summary');
    const label = MENU_FAMILIES.find([[id]] => id === family)?.[1] || family;
    if (summary) summary.textContent = count ? `${label} · ${count}` : label;
  }
  renderSummary();
  renderContext();
}

function installStyle() {
  if (document.getElementById('atlasWorldBarStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasWorldBarStyle';
  style.textContent = `body.atlas-registry-ui .mnu-hidden blah