// Bound Atlas network requests so a stalled provider cannot leave the map shell loading forever.
// Loaded as a classic script before deferred module execution on the deployed Pages artifact.
(() => {
  const nativeFetch = window.fetch.bind(window);
  const DEFAULT_TIMEOUT_MS = 10000;
  const BOOT_WATCHDOG_MS = 18000;
  const REST_COUNTRIES_PREFIX = 'https://restcountries.com/v3.1/all';
  const LOCAL_COUNTRY_RUNTIME = '../data/world-country-runtime.json';

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
    stage: 'guard-installed',
    failures: []
  };

  window.fetch = function atlasBoundedFetch(input, init = {}) {
    const url = typeof input === 'string' ? input : input?.url || String(input);
    // REST Countries is useful at build/research time but should not be part of
    // interactive camera performance. Route runtime calls to the compact,
    // checked-in same-origin snapshot before any later resilience wrappers run.
    const target = url.startsWith(REST_COUNTRIES_PREFIX) ? LOCAL_COUNTRY_RUNTIME : input;

    // Respect an explicit caller-owned AbortSignal; otherwise add a finite deadline.
    if (init?.signal) return nativeFetch(target, init);

    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
    return nativeFetch(target, { ...init, signal: controller.signal })
      .finally(() => window.clearTimeout(timer));
  };

  window.addEventListener('error', event => {
    const message = event?.error?.message || event?.message || 'Unknown JavaScript error';
    window.__potatoAtlasBootGuard.failures.push(message);
    if (!window.__potatoAtlasReady) showFailure(`Atlas boot error: ${message}`);
  });

  window.addEventListener('unhandledrejection', event => {
    const reason = event?.reason;
    const message = reason?.message || String(reason || 'Unknown promise rejection');
    window.__potatoAtlasBootGuard.failures.push(message);
    if (!window.__potatoAtlasReady) showFailure(`Atlas boot error: ${message}`);
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