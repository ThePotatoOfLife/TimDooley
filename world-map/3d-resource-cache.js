// Shared JSON resource cache for the World Map runtime.
// Deduplicates in-flight and completed same-origin/public JSON reads so modules do
// not each fetch + parse the same canonical dataset independently.

const records = new Map();

function absoluteUrl(url) {
  try { return new URL(String(url || ''), location.href).href; }
  catch { return String(url || ''); }
}

function diagnostics() {
  const rows = [...records.values()];
  return {
    resources:rows.length,
    pending:rows.filter(row => row.status === 'loading').length,
    loaded:rows.filter(row => row.status === 'loaded').length,
    failed:rows.filter(row => row.status === 'failed').length,
    hits:rows.reduce((sum,row) => sum + Number(row.hits || 0), 0),
  };
}

function publish() {
  if (window.__potatoAtlasDiagnostics) {
    window.__potatoAtlasDiagnostics.resources = diagnostics();
  }
}

function fetchJson(url, options = {}) {
  const key = absoluteUrl(url);
  const reload = options.reload === true;
  if (!reload && records.has(key)) {
    const row = records.get(key);
    if (row.status !== 'failed' || options.retryFailed === false) {
      row.hits = Number(row.hits || 0) + 1;
      publish();
      return row.promise;
    }
    records.delete(key);
  }

  const row = {
    url:key,
    status:'loading',
    hits:0,
    startedAt:performance.now(),
    completedAt:null,
    error:null,
    promise:null,
  };
  // Shared requests intentionally do not inherit a caller AbortSignal: one consumer
  // must not cancel the canonical in-flight read for every other module.
  row.promise = fetch(key, { cache:options.cache || 'force-cache' })
    .then(response => {
      if (!response.ok) throw new Error(`${response.status} ${key}`);
      return response.json();
    })
    .then(data => {
      row.status = 'loaded';
      row.completedAt = performance.now();
      publish();
      return data;
    })
    .catch(error => {
      row.status = 'failed';
      row.completedAt = performance.now();
      row.error = error?.message || String(error);
      publish();
      if (options.optional) return options.fallback ?? null;
      throw error;
    });
  records.set(key,row);
  publish();
  return row.promise;
}

function forget(url) {
  return records.delete(absoluteUrl(url));
}

function clear() {
  records.clear();
  publish();
}

function state(url = null) {
  if (url) {
    const row = records.get(absoluteUrl(url));
    if (!row) return null;
    const { promise, ...snapshot } = row;
    return {...snapshot};
  }
  return [...records.values()].map(({promise,...row}) => ({...row}));
}

window.__potatoAtlasResources = Object.freeze({ fetchJson, forget, clear, state, diagnostics });
window.dispatchEvent(new CustomEvent('potato-atlas-resources-ready', { detail:diagnostics() }));

export { fetchJson, forget, clear, state, diagnostics };
