// Core-first bootstrap for the 3D World Relational Atlas.
//
// The geographic renderer is the availability boundary. The map is allowed to
// paint and accept interaction before secondary overlays start doing work.
// Optional modules are loaded one at a time during browser idle periods, and
// their timings remain inspectable in window.__potatoAtlasDiagnostics.

const statusNode = () => document.querySelector('#status');
const guard = () => window.__potatoAtlasBootGuard;
const OPTIONAL_TIMEOUT_MS = 12000;
const modulePromises = new Map();

function now() {
  return performance.now();
}

function setStatus(message, kind = 'info') {
  const node = statusNode();
  if (node) {
    node.hidden = !message;
    node.dataset.kind = kind;
    node.textContent = message;
  }
  if (guard()) guard().stage = message || 'ready';
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function nextPaint() {
  return new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}

function idle(timeout = 1000) {
  if ('requestIdleCallback' in window) {
    return new Promise(resolve => window.requestIdleCallback(resolve, { timeout }));
  }
  return sleep(32);
}

async function waitForCore(timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const map = window.__potatoAtlasMap;
    if (map?.getLayer?.('countries-fill')) {
      window.__potatoAtlasReady = true;
      const elapsed = now() - window.__potatoAtlasDiagnostics.startedAt;
      window.__potatoAtlasDiagnostics.coreReadyMs = Math.round(elapsed);
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

function loadOptional(label, path) {
  if (modulePromises.has(label)) return modulePromises.get(label);

  const promise = (async () => {
    const startedAt = now();
    diagnostic(label, { path, status: 'loading', startedAtMs: Math.round(startedAt - window.__potatoAtlasDiagnostics.startedAt) });
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
      window.__potatoAtlasEnhancements.loaded.push(label);
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
  return loadOptional(label, path);
}

async function loadDuringIdle(label, path) {
  diagnostic(label, { path, status: 'queued' });
  await idle();
  const result = await loadOptional(label, path);
  // Always yield after an enhancement too. Even healthy modules can add several
  // map layers and style recalculations; batching all of them into one task is
  // unnecessary jank.
  await nextPaint();
  return result;
}

window.__potatoAtlasEnhancements = { loaded: [], failed: [] };
window.__potatoAtlasDiagnostics = {
  startedAt: now(),
  startedAtIso: new Date().toISOString(),
  coreReadyMs: null,
  modules: {},
};
window.__potatoAtlasReady = false;

try {
  setStatus('Loading core atlas…');

  // 3d-hover owns resilient data routing and imports 3d-app, which constructs
  // the MapLibre map. Keeping this first preserves the last-known-working core
  // topology from before optional layers multiplied.
  await import('./3d-hover.js');
  await waitForCore();

  // Let the newly created country map actually reach the screen before doing
  // any post-core setup.
  await nextPaint();

  // Keep the small, historically stable helpers near the core. The UI is now
  // observer-safe and loads early so menus stay usable while deeper layers are
  // still queued.
  await loadAfterPaint('Path finder', './3d-pathfinder.js');
  await loadAfterPaint('Demography', './3d-demography.js');
  await loadAfterPaint('Progressive UI', './3d-ui.js');

  // From here the atlas is fully usable. Do not present background enrichment
  // as a blocking loading phase.
  setStatus('');
  if (guard()) guard().stage = 'interactive';
  window.__potatoAtlasDiagnostics.interactiveMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-interactive'));

  const deferred = [
    ['Evidence', './3d-evidence.js'],
    ['Fields', './3d-fields.js'],
    ['Networks', './3d-networks.js'],
    ['Time', './3d-time.js'],
    ['Axis depth', './3d-axis-depth.js'],
    ['Axis operators', './3d-axis-operators.js'],
    ['North Axis', './3d-axis.js'],
  ];

  // User intent can promote a queued group immediately. This keeps startup
  // light while preserving fast access to controls when a menu is opened.
  const promoteLayers = () => {
    loadOptional('Evidence', './3d-evidence.js');
    loadOptional('Fields', './3d-fields.js');
    loadOptional('Networks', './3d-networks.js');
    loadOptional('North Axis', './3d-axis.js');
  };
  const promoteTime = () => loadOptional('Time', './3d-time.js');
  const promoteAxis = () => {
    loadOptional('Axis depth', './3d-axis-depth.js');
    loadOptional('Axis operators', './3d-axis-operators.js');
    loadOptional('North Axis', './3d-axis.js');
  };

  const layersMenu = document.getElementById('layersMenu');
  const timeMenu = document.getElementById('timeMenu');
  const viewMenu = document.getElementById('viewMenu');
  layersMenu?.addEventListener('toggle', () => layersMenu.open && promoteLayers(), { once: true });
  timeMenu?.addEventListener('toggle', () => timeMenu.open && promoteTime(), { once: true });
  viewMenu?.addEventListener('toggle', () => viewMenu.open && promoteAxis(), { once: true });

  for (const [label, path] of deferred) {
    await loadDuringIdle(label, path);
  }

  window.__potatoAtlasDiagnostics.completeMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-bootstrap-complete', {
    detail: window.__potatoAtlasEnhancements,
  }));
} catch (error) {
  console.error('3D atlas core bootstrap failed.', error);
  if (guard()) guard().failures.push(error?.message || String(error));
  setStatus(`Atlas core failed to boot: ${error?.message || error}`, 'error');
}
