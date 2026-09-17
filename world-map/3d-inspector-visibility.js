// Stable visibility owner for the World Map deep inspector.
//
// The broad Progressive UI is optional/legacy, but the two visible Inspect controls
// and selected-country inspector visibility are core browsing behavior. Keep that
// small responsibility here so collapsing the legacy UI cannot strand country data.

function createInspectorVisibility({
  app,
  panelToggle,
  mapInspectorToggle,
  eventTarget,
  storage,
  storageKey = 'atlas:panel-open',
} = {}) {
  let installed = false;

  function isOpen() {
    return Boolean(app && !app.classList.contains('panel-collapsed'));
  }

  function syncButtons(open) {
    for (const button of [panelToggle, mapInspectorToggle]) {
      button?.classList?.toggle?.('active', open);
      button?.setAttribute?.('aria-pressed', String(open));
    }
    if (panelToggle) panelToggle.textContent = open ? 'Close' : 'Inspect';
  }

  function publish(open) {
    if (!eventTarget?.dispatchEvent) return;
    const event = typeof CustomEvent === 'function'
      ? new CustomEvent('potato-atlas-panel-change', { detail:{ open } })
      : { type:'potato-atlas-panel-change', detail:{ open } };
    eventTarget.dispatchEvent(event);
  }

  function setOpen(open, { persist = true } = {}) {
    if (!app) return false;
    const next = Boolean(open);
    app.classList.toggle('panel-collapsed', !next);
    syncButtons(next);
    if (persist) {
      try { storage?.setItem?.(storageKey, next ? '1' : '0'); } catch {}
    }
    publish(next);
    return next;
  }

  function toggle() {
    return setOpen(!isOpen());
  }

  function onSelection(event) {
    if (event?.detail?.selected) setOpen(true, { persist:false });
  }

  function install() {
    if (installed) return api;
    installed = true;
    panelToggle?.addEventListener?.('click', toggle);
    mapInspectorToggle?.addEventListener?.('click', toggle);
    eventTarget?.addEventListener?.('potato-atlas-working-selection-change', onSelection);
    let storedOpen = false;
    try { storedOpen = storage?.getItem?.(storageKey) === '1'; } catch {}
    setOpen(storedOpen, { persist:false });
    return api;
  }

  const api = Object.freeze({ install, isOpen, setOpen, toggle });
  return api;
}

if (typeof window !== 'undefined') {
  const controller = createInspectorVisibility({
    app:document.getElementById('atlasApp'),
    panelToggle:document.getElementById('panelToggle'),
    mapInspectorToggle:document.getElementById('mapInspectorToggle'),
    eventTarget:window,
    storage:window.localStorage,
  });
  controller.install();
  window.__potatoAtlasInspectorVisibility = controller;
}

export { createInspectorVisibility };
