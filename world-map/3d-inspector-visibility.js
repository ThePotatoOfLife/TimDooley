// Stable visibility owner for the World Map deep inspector.
//
// The broad Progressive UI is optional/legacy, but the two visible Inspect controls
// and selected-country inspector visibility are core browsing behavior. Keep that
// small responsibility here so collapsing the legacy UI cannot strand country data.

function createInspectorVisibility({
  app,
  panel,
  panelToggle,
  mapInspectorToggle,
  eventTarget,
  keyTarget,
  storage,
  storageKey = 'atlas:panel-open',
} = {}) {
  let installed = false;
  let lastTrigger = null;

  function isOpen() {
    return Boolean(app && !app.classList.contains('panel-collapsed'));
  }

  function syncButtons(open) {
    for (const button of [panelToggle, mapInspectorToggle]) {
      button?.classList?.toggle?.('active', open);
      button?.setAttribute?.('aria-pressed', String(open));
      button?.setAttribute?.('aria-expanded', String(open));
      button?.setAttribute?.('aria-controls', 'panel');
    }
    panel?.setAttribute?.('aria-hidden', String(!open));
    panel?.setAttribute?.('tabindex', '-1');
    if (panelToggle) panelToggle.textContent = open ? 'Close' : 'Inspect';
  }

  function publish(open) {
    if (!eventTarget?.dispatchEvent) return;
    const event = typeof CustomEvent === 'function'
      ? new CustomEvent('potato-atlas-panel-change', { detail:{ open } })
      : { type:'potato-atlas-panel-change', detail:{ open } };
    eventTarget.dispatchEvent(event);
  }

  function focusPanel() {
    try { panel?.focus?.({ preventScroll:true }); }
    catch { panel?.focus?.(); }
  }

  function returnFocus() {
    const preferred = lastTrigger || panelToggle || mapInspectorToggle;
    try { preferred?.focus?.({ preventScroll:true }); }
    catch { preferred?.focus?.(); }
  }

  function setOpen(open, {
    persist = true,
    focusPanelOnOpen = false,
    returnFocusOnClose = false,
  } = {}) {
    if (!app) return false;
    const next = Boolean(open);
    app.classList.toggle('panel-collapsed', !next);
    syncButtons(next);
    if (persist) {
      try { storage?.setItem?.(storageKey, next ? '1' : '0'); } catch {}
    }
    publish(next);
    if (next && focusPanelOnOpen) queueMicrotask(focusPanel);
    if (!next && returnFocusOnClose) queueMicrotask(returnFocus);
    return next;
  }

  function toggle(event = null) {
    if (event?.currentTarget) lastTrigger = event.currentTarget;
    const next = !isOpen();
    return setOpen(next, {
      focusPanelOnOpen:next,
      returnFocusOnClose:!next,
    });
  }

  function onSelection(event) {
    if (!event?.detail?.selected) return;
    lastTrigger = null;
    setOpen(true, { persist:false, focusPanelOnOpen:false });
  }

  function onKeydown(event) {
    if (event?.key !== 'Escape' || event.defaultPrevented || !isOpen()) return;
    const target = event.target;
    if (target?.closest?.('input,textarea,select,[contenteditable="true"],[role="dialog"][aria-modal="true"]')) return;
    setOpen(false, { returnFocusOnClose:true });
    event.preventDefault?.();
    event.stopPropagation?.();
  }

  function install() {
    if (installed) return api;
    installed = true;
    panelToggle?.addEventListener?.('click', toggle);
    mapInspectorToggle?.addEventListener?.('click', toggle);
    eventTarget?.addEventListener?.('potato-atlas-working-selection-change', onSelection);
    keyTarget?.addEventListener?.('keydown', onKeydown);
    let storedOpen = false;
    try { storedOpen = storage?.getItem?.(storageKey) === '1'; } catch {}
    setOpen(storedOpen, { persist:false });
    return api;
  }

  const api = Object.freeze({ install, isOpen, setOpen, toggle, returnFocus });
  return api;
}

if (typeof window !== 'undefined') {
  const controller = createInspectorVisibility({
    app:document.getElementById('atlasApp'),
    panel:document.getElementById('panel'),
    panelToggle:document.getElementById('panelToggle'),
    mapInspectorToggle:document.getElementById('mapInspectorToggle'),
    eventTarget:window,
    keyTarget:document,
    storage:window.localStorage,
  });
  controller.install();
  window.__potatoAtlasInspectorVisibility = controller;
}

export { createInspectorVisibility };
