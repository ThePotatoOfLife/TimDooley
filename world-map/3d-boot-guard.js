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

  window.__potatoAtlasBootGuard = {
    timeoutMs: DEFAULT_TIMEOUT_MS,
    watchdogMs: BOOT_WATCHDOG_MS,
    installedAt: new Date().toISOString(),
    failures: []
  };

  window.fetch = function atlasBoundedFetch(input, init = {}) {
    // Respect an explicit caller-owned AbortSignal; otherwise add a finite deadline.
    if (init?.signal) return nativeFetch(input, init);

    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
    return nativeFetch(input, { ...init, signal: controller.signal })
      .finally(() => window.clearTimeout(timer));
  };

  window.addEventListener('error', event => {
    const message = event?.error?.message || event?.message || 'Unknown JavaScript error';
    window.__potatoAtlasBootGuard.failures.push(message);
    if (!window.__potatoAtlasMap) showFailure(`Atlas boot error: ${message}`);
  });

  window.addEventListener('unhandledrejection', event => {
    const reason = event?.reason;
    const message = reason?.message || String(reason || 'Unknown promise rejection');
    window.__potatoAtlasBootGuard.failures.push(message);
    if (!window.__potatoAtlasMap) showFailure(`Atlas boot error: ${message}`);
  });

  window.setTimeout(() => {
    if (window.__potatoAtlasMap) return;
    const failures = window.__potatoAtlasBootGuard.failures;
    showFailure(failures.length
      ? `Atlas did not finish booting: ${failures.at(-1)}`
      : 'Atlas did not finish booting. The map engine or first application module never became ready.');
    console.error('Atlas boot watchdog fired.', window.__potatoAtlasBootGuard);
  }, BOOT_WATCHDOG_MS);
})();
