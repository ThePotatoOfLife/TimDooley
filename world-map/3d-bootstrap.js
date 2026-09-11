// Core-first bootstrap for the 3D World Relational Atlas.
//
// The geographic renderer is the availability boundary. The map and lightweight
// UI become interactive first. Every analytical/enrichment module stays dormant
// until a user action actually needs it. This prevents post-paint background work
// from turning a healthy map into "it loaded, then started hanging".

const statusNode = () => document.querySelector('#status');
const guard = () => window.__potatoAtlasBootGuard;
const OPTIONAL_TIMEOUT_MS = 12000;
const modulePromises = new Map();

function now() { return performance.now(); }

function setStatus(message, kind = 'info') {
  const node = statusNode();
  if (node) {
    node.hidden = !message;
    node.dataset.kind = kind;
    node.textContent = message;
  }
  if (guard()) guard().stage = message || 'ready';
}

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

// requestAnimationFrame can be throttled in background tabs. Always retain a
// timer escape hatch so waiting for paint cannot become a new boot deadlock.
function nextPaint(maxWaitMs = 160) {
  return new Promise(resolve => {
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      resolve();
    };
    const timer = setTimeout(finish, maxWaitMs);
    requestAnimationFrame(() => requestAnimationFrame(finish));
  });
}

async function waitForCore(timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const map = window.__potatoAtlasMap;
    if (map?.getLayer?.('countries-fill')) {
      window.__potatoAtlasReady = true;
      window.__potatoAtlasDiagnostics.coreReadyMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
      if (guard()) guard().stage = 'core-ready';
      window.dispatchEvent(new CustomEvent('potato-atlas-core-ready', { detail: { map } }));
      return map;
    }
    await sleep(40);
  }
  throw new Error('Core atlas map did not become ready before the bootstrap deadline.');
}

function diagnostic(label, patch) {
  const current = window.__potatoAtlasDiagnostics.modules[label] || {};
  window.__potatoAtlasDiagnostics.modules[label] = { ...current, ...patch };
}

function declareDormant(label, path, trigger) {
  diagnostic(label, { path, status: 'dormant', trigger });
}

function loadOptional(label, path) {
  if (modulePromises.has(label)) return modulePromises.get(label);

  const promise = (async () => {
    const startedAt = now();
    diagnostic(label, {
      path,
      status: 'loading',
      startedAtMs: Math.round(startedAt - window.__potatoAtlasDiagnostics.startedAt),
    });
    let timer;
    try {
      await Promise.race([
        import(path),
        new Promise((_, reject) => {
          timer = setTimeout(() => reject(new Error(`${label} exceeded the optional-module deadline.`)), OPTIONAL_TIMEOUT_MS);
        }),
      ]);
      const durationMs = Math.round(now() - startedAt);
      diagnostic(label, { status: 'loaded', durationMs });
      if (!window.__potatoAtlasEnhancements.loaded.includes(label)) window.__potatoAtlasEnhancements.loaded.push(label);
      window.dispatchEvent(new CustomEvent('potato-atlas-module-ready', { detail: { label, path, durationMs } }));
      return true;
    } catch (error) {
      const durationMs = Math.round(now() - startedAt);
      const message = error?.message || String(error);
      diagnostic(label, { status: 'failed', durationMs, error: message });
      window.__potatoAtlasEnhancements.failed.push({ label, message });
      console.warn(`${label} enhancement unavailable:`, error);
      return false;
    } finally {
      clearTimeout(timer);
    }
  })();

  modulePromises.set(label, promise);
  return promise;
}

async function loadAfterPaint(label, path) {
  await nextPaint();
  const result = await loadOptional(label, path);
  await nextPaint();
  return result;
}

window.__potatoAtlasEnhancements = { loaded: [], failed: [] };
window.__potatoAtlasDiagnostics = {
  startedAt: now(),
  startedAtIso: new Date().toISOString(),
  coreReadyMs: null,
  interactiveMs: null,
  modules: {},
};
window.__potatoAtlasReady = false;
// One shared loader keeps diagnostics/deduplication intact even when the UI or
// another optional module promotes a dormant feature on demand.
window.__potatoAtlasLoadModule = loadAfterPaint;

try {
  setStatus('Loading core atlas…');

  // 3d-hover owns resilient local-first data routing and imports 3d-app, which
  // constructs the MapLibre renderer and geographic country layers.
  await import('./3d-hover.js');
  const map = await waitForCore();
  await nextPaint();

  // Only the observer-safe UI controller is automatic after core. Pathfinder,
  // demography, Evidence, Fields, Networks, Time and Axis are all true opt-ins.
  await loadAfterPaint('Progressive UI', './3d-ui.js');

  setStatus('');
  if (guard()) guard().stage = 'interactive';
  window.__potatoAtlasDiagnostics.interactiveMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-interactive'));

  declareDormant('Path finder', './3d-pathfinder.js', 'Trace menu');
  declareDormant('Entity Trace', './3d-entity-trace.js', 'Trace menu');
  declareDormant('Demography', './3d-demography.js', 'first country inspection');
  declareDormant('Evidence', './3d-evidence.js', 'first country inspection');
  declareDormant('Fields', './3d-fields.js', 'Layers menu');
  declareDormant('Networks', './3d-networks.js', 'Layers menu');
  declareDormant('Time', './3d-time.js', 'Time menu');
  declareDormant('Axis depth', './3d-axis-depth.js', 'View menu');
  declareDormant('Axis operators', './3d-axis-operators.js', 'View menu');
  declareDormant('North Axis', './3d-axis.js', 'Layers or View menu');

  const promoteLayers = async () => {
    await loadAfterPaint('Fields', './3d-fields.js');
    await loadAfterPaint('Networks', './3d-networks.js');
    await loadAfterPaint('North Axis', './3d-axis.js');
  };
  const promoteTime = () => loadAfterPaint('Time', './3d-time.js');
  const promoteAxis = async () => {
    await loadAfterPaint('Axis depth', './3d-axis-depth.js');
    await loadAfterPaint('Axis operators', './3d-axis-operators.js');
    await loadAfterPaint('North Axis', './3d-axis.js');
  };
  const promoteInspection = async () => {
    await Promise.all([
      loadAfterPaint('Demography', './3d-demography.js'),
      loadAfterPaint('Evidence', './3d-evidence.js'),
    ]);
  };

  const layersMenu = document.getElementById('layersMenu');
  const timeMenu = document.getElementById('timeMenu');
  const viewMenu = document.getElementById('viewMenu');

  const onLayersToggle = () => {
    if (!layersMenu?.open) return;
    layersMenu.removeEventListener('toggle', onLayersToggle);
    promoteLayers();
  };
  const onTimeToggle = () => {
    if (!timeMenu?.open) return;
    timeMenu.removeEventListener('toggle', onTimeToggle);
    promoteTime();
  };
  const onViewToggle = () => {
    if (!viewMenu?.open) return;
    viewMenu.removeEventListener('toggle', onViewToggle);
    promoteAxis();
  };
  layersMenu?.addEventListener('toggle', onLayersToggle);
  timeMenu?.addEventListener('toggle', onTimeToggle);
  viewMenu?.addEventListener('toggle', onViewToggle);

  // Inspector enrichment is attached to an actual country interaction, not to
  // page load. The core remains idle indefinitely if the user simply explores.
  map.once('click', promoteInspection);

  window.__potatoAtlasDiagnostics.bootstrapWiredMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-bootstrap-complete', { detail: window.__potatoAtlasEnhancements }));
} catch (error) {
  console.error('3D atlas core bootstrap failed.', error);
  if (guard()) guard().failures.push(error?.message || String(error));
  setStatus(`Atlas core failed to boot: ${error?.message || error}`, 'error');
}
