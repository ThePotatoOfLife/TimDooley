// Shared keyboard/focus affordances for the World Relational Atlas.
// Native controls keep their native Enter/Space behavior; this module owns
// Escape-to-close semantics for map menus and explicit focus return.

function mapMenus() {
  return [...document.querySelectorAll('#atlasWorldBar details, #atlasSelectionDock details, .top details.menu')];
}

function nearestOpenMenu(target = null) {
  const fromTarget = target?.closest?.('details[open]');
  if (fromTarget?.matches?.('#atlasWorldBar details[open], #atlasSelectionDock details[open], .menu[open]')) return fromTarget;
  const open = mapMenus().filter(details => details.open);
  return open.at(-1) || null;
}

function closeMenu(details, { restoreFocus = true } = {}) {
  if (!details?.open) return false;
  details.open = false;
  const summary = details.querySelector(':scope > summary');
  summary?.setAttribute?.('aria-expanded', 'false');
  if (restoreFocus && typeof summary?.focus === 'function') {
    queueMicrotask(() => summary.isConnected && summary.focus({preventScroll:true}));
  }
  return true;
}

function syncMenuAria(details) {
  const summary = details?.querySelector?.(':scope > summary');
  if (!summary) return false;
  summary.setAttribute('aria-expanded', details.open ? 'true' : 'false');
  return true;
}

function syncAllMenus() {
  mapMenus().forEach(syncMenuAria);
}

function onToggle(event) {
  const details = event.target;
  if (!(details instanceof HTMLDetailsElement)) return;
  if (!details.matches('#atlasWorldBar details, #atlasSelectionDock details, .top details.menu')) return;
  if (details.open) {
    for (const other of mapMenus()) {
      if (other !== details && other.open) closeMenu(other, { restoreFocus:false });
    }
  }
  syncMenuAria(details);
}

function onKeydown(event) {
  if (event.key !== 'Escape' || event.defaultPrevented) return;
  const menu = nearestOpenMenu(event.target);
  if (!menu) return;
  if (closeMenu(menu)) {
    event.preventDefault();
    event.stopPropagation();
  }
}

document.addEventListener('toggle', onToggle, true);
document.addEventListener('keydown', onKeydown, true);
queueMicrotask(syncAllMenus);
window.addEventListener('potato-atlas-module-ready', () => queueMicrotask(syncAllMenus));
window.addEventListener('potato-atlas-ui-layout-change', () => queueMicrotask(syncAllMenus));

window.__potatoAtlasAccessibility = Object.freeze({
  closeMenu,
  syncMenuAria,
  syncAllMenus,
  nearestOpenMenu,
  mapMenus,
});

window.dispatchEvent(new CustomEvent('potato-atlas-accessibility-ready'));
