// Shared bounded request coordinator for World Map provider-backed runtime work.
// Owns concurrency, in-flight de-duplication, short-lived cache and telemetry.
// It does not replace MapLibre's internal tile scheduler; modules use it for explicit fetch() work.

const DEFAULT_MAX_CONCURRENT = 4;
const DEFAULT_CACHE_MS = 0;

function abortError() {
  const error = new Error('Request aborted');
  error.name = 'AbortError';
  return error;
}

function createRequestBudget({ maxConcurrent = DEFAULT_MAX_CONCURRENT } = {}) {
  let limit = Math.max(1, Math.floor(Number(maxConcurrent) || DEFAULT_MAX_CONCURRENT));
  let active = 0;
  const queue = [];
  const inFlight = new Map();
  const cache = new Map();
  const metrics = {
    started:0,
    completed:0,
    failed:0,
    aborted:0,
    deduplicated:0,
    cacheHits:0,
    queued:0,
    maxObservedConcurrent:0,
  };

  function cacheGet(key) {
    const row = cache.get(key);
    if (!row) return null;
    if (row.expiresAt <= Date.now()) { cache.delete(key); return null; }
    metrics.cacheHits += 1;
    return row.value;
  }

  function pump() {
    while (active < limit && queue.length) {
      const job = queue.shift();
      if (job.signal?.aborted) {
        metrics.aborted += 1;
        job.reject(abortError());
        continue;
      }
      active += 1;
      metrics.maxObservedConcurrent = Math.max(metrics.maxObservedConcurrent, active);
      metrics.started += 1;
      Promise.resolve()
        .then(() => job.task(job.signal))
        .then(value => {
          metrics.completed += 1;
          if (job.cacheMs > 0) cache.set(job.key, { value, expiresAt:Date.now() + job.cacheMs });
          job.resolve(value);
        })
        .catch(error => {
          if (error?.name === 'AbortError') metrics.aborted += 1;
          else metrics.failed += 1;
          job.reject(error);
        })
        .finally(() => {
          active -= 1;
          inFlight.delete(job.key);
          pump();
        });
    }
  }

  function run(key, task, { signal = null, cacheMs = DEFAULT_CACHE_MS } = {}) {
    const requestKey = String(key || '').trim();
    if (!requestKey) return Promise.reject(new Error('Request budget key is required'));
    if (typeof task !== 'function') return Promise.reject(new Error('Request budget task must be a function'));
    if (signal?.aborted) return Promise.reject(abortError());

    const cached = cacheMs > 0 ? cacheGet(requestKey) : null;
    if (cached !== null) return Promise.resolve(cached);

    if (inFlight.has(requestKey)) {
      metrics.deduplicated += 1;
      return inFlight.get(requestKey);
    }

    let resolveJob;
    let rejectJob;
    const promise = new Promise((resolve, reject) => { resolveJob = resolve; rejectJob = reject; });
    inFlight.set(requestKey, promise);
    queue.push({
      key:requestKey,
      task,
      signal,
      cacheMs:Math.max(0, Number(cacheMs) || 0),
      resolve:resolveJob,
      reject:rejectJob,
    });
    metrics.queued += 1;
    pump();
    return promise;
  }

  function clearCache(prefix = '') {
    const needle = String(prefix || '');
    if (!needle) { cache.clear(); return; }
    for (const key of [...cache.keys()]) if (key.startsWith(needle)) cache.delete(key);
  }

  function setMaxConcurrent(value) {
    limit = Math.max(1, Math.floor(Number(value) || DEFAULT_MAX_CONCURRENT));
    pump();
    return limit;
  }

  function snapshot() {
    return {
      maxConcurrent:limit,
      active,
      queued:queue.length,
      inFlight:[...inFlight.keys()],
      cacheEntries:cache.size,
      metrics:{...metrics},
    };
  }

  return Object.freeze({ run, snapshot, clearCache, setMaxConcurrent });
}

if (typeof window !== 'undefined' && !window.__potatoAtlasRequestBudget) {
  window.__potatoAtlasRequestBudget = createRequestBudget();
}

export { createRequestBudget };
