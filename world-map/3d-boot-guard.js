// Bound Atlas network requests so a stalled provider cannot leave the map shell loading forever.
// Loaded as a classic script before deferred module execution on the deployed Pages artifact.
(() => {
  const nativeFetch = window.fetch.bind(window);
  const DEFAULT_TIMEOUT_MS = 10000;
  const BOOT_WATCHDOG_MS = 18000;

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
  };

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
