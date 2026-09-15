// Bound Atlas network requests so a stalled provider cannot leave the map shell loading forever.
// Loaded as a classic script before deferred module execution on the deployed Pages artifact.
(() => {
  const nativeFetch = window.fetch.bind(window);
  const DEFAULT_TIMEOUT_MS = 10000;
  const BOOT_WATCHDOG_MS = 18000;
  const POINTER_DRAG_CLASS = 'potato-atlas-pointer-dragging';
  const POINTER_DRAG_THRESHOLD_PX = 4;

  const status = () => document.querySelector('#status');
  const showFailure = message => {
    const node = status();
    if (!node) return;
    node.hidden = false;
    node.dataset.kind = 'error';
    node.textContent = message;
  };
  const recordDiagnostic = message => {
    const guard = window.__potatoAtlasBootGuard;
    if (!guard) return;
    guard.failures.push(message);
    guard.lastDiagnosticAt = new Date().toISOString();
    guard.lastDiagnostic = message;
    console.warn('Atlas boot diagnostic recorded; waiting for the core readiness boundary before surfacing a failure.', message);
  };

  window.__potatoAtlasBootGuard = {
    timeoutMs: DEFAULT_TIMEOUT_MS,
    watchdogMs: BOOT_WATCHDOG_MS,
    installedAt: new Date().toISOString(),
    stage: 'guard-installed',
    failures: [],
    lastDiagnostic: null,
    lastDiagnosticAt: null,
    pointerDragSuppressions: 0
  };

  // Transient hover surfaces should never appear to be physically attached to
  // geography while the user pans the map. Hide only Atlas hover popups during a
  // real drag; persistent/click-owned popups remain untouched.
  const dragStyle = document.createElement('style');
  dragStyle.textContent = `html.${POINTER_DRAG_CLASS} .maplibregl-popup:has(.atlas-hover){visibility:hidden!important;pointer-events:none!important}`;
  (document.head || document.documentElement).appendChild(dragStyle);

  let pointerOrigin = null;
  let draggingPointerId = null;
  let suppressUntilMove = false;

  function setPointerDragSuppressed(suppressed) {
    const active = Boolean(suppressed);
    const wasActive = document.documentElement.classList.contains(POINTER_DRAG_CLASS);
    document.documentElement.classList.toggle(POINTER_DRAG_CLASS, active);
    if (active && !wasActive && window.__potatoAtlasBootGuard) {
      window.__potatoAtlasBootGuard.pointerDragSuppressions += 1;
    }
  }

  function resetPointer(event, cancelled = false) {
    if (!pointerOrigin || (event?.pointerId != null && event.pointerId !== pointerOrigin.pointerId)) return;
    const dragged = draggingPointerId === pointerOrigin.pointerId;
    pointerOrigin = null;
    draggingPointerId = null;
    if (dragged && !cancelled) {
      // Keep the old hover invisible until the next pointer move gives MapLibre a
      // fresh geographic hit target at the map's new position.
      suppressUntilMove = true;
      return;
    }
    suppressUntilMove = false;
    setPointerDragSuppressed(false);
  }

  window.addEventListener('pointerdown', event => {
    const mapNode = document.querySelector('#map');
    if (!mapNode || !event.target || !mapNode.contains(event.target)) return;
    pointerOrigin = { pointerId:event.pointerId, x:event.clientX, y:event.clientY };
    draggingPointerId = null;
    suppressUntilMove = false;
  }, true);

  window.addEventListener('pointermove', event => {
    if (suppressUntilMove && !pointerOrigin) {
      suppressUntilMove = false;
      setPointerDragSuppressed(false);
      return;
    }
    if (!pointerOrigin || event.pointerId !== pointerOrigin.pointerId) return;
    if (draggingPointerId === pointerOrigin.pointerId) return;
    const dx = Number(event.clientX) - pointerOrigin.x;
    const dy = Number(event.clientY) - pointerOrigin.y;
    if (Math.hypot(dx, dy) < POINTER_DRAG_THRESHOLD_PX) return;
    draggingPointerId = pointerOrigin.pointerId;
    setPointerDragSuppressed(true);
  }, true);

  window.addEventListener('pointerup', event => resetPointer(event), true);
  window.addEventListener('pointercancel', event => resetPointer(event, true), true);

  window.fetch = function atlasBoundedFetch(input, init = {}) {
    // Respect an explicit caller-owned AbortSignal; otherwise add a finite deadline.
    if (init?.signal) return nativeFetch(input, init);

    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
    return nativeFetch(input, { ...init, signal: controller.signal })
      .finally(() => window.clearTimeout(timer));
  };

  // Early browser/module errors can be recoverable because the Atlas has local and
  // optional-module fallbacks. Record them for diagnostics, but do not flash a red
  // fatal banner unless the core itself fails or the watchdog confirms no readiness.
  window.addEventListener('error', event => {
    const message = event?.error?.message || event?.message || 'Unknown JavaScript error';
    recordDiagnostic(message);
  });

  window.addEventListener('unhandledrejection', event => {
    const reason = event?.reason;
    const message = reason?.message || String(reason || 'Unknown promise rejection');
    recordDiagnostic(message);
  });

  window.setTimeout(() => {
    if (window.__potatoAtlasReady) return;
    const failures = window.__potatoAtlasBootGuard.failures;
    const stage = window.__potatoAtlasBootGuard.stage || 'unknown';
    showFailure(failures.length
      ? `Atlas did not finish booting at ${stage}: ${failures.at(-1)}`
      : `Atlas did not finish booting. Last stage: ${stage}.`);
    console.error('Atlas boot watchdog fired.', window.__potatoAtlasBootGuard);
  }, BOOT_WATCHDOG_MS);
})();
