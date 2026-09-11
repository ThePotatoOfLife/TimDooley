// Bound Atlas network requests so a stalled provider cannot leave the map shell loading forever.
// Loaded as a classic script before deferred module execution on the deployed Pages artifact.
(() => {
  const nativeFetch = window.fetch.bind(window);
  const DEFAULT_TIMEOUT_MS = 10000;

  window.__potatoAtlasBootGuard = {
    timeoutMs: DEFAULT_TIMEOUT_MS,
    installedAt: new Date().toISOString()
  };

  window.fetch = function atlasBoundedFetch(input, init = {}) {
    // Respect an explicit caller-owned AbortSignal; otherwise add a finite deadline.
    if (init?.signal) return nativeFetch(input, init);

    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
    return nativeFetch(input, { ...init, signal: controller.signal })
      .finally(() => window.clearTimeout(timer));
  };
})();
