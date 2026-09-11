// Core-first bootstrap for the 3D World Relational Atlas.
//
// The geographic renderer is the availability boundary. The map and lightweight
// semantic navigation become interactive first. Analytical/enrichment modules
// stay dormant until a user opens the World, Relations, Time or Axis zone (or an
// older compatibility control requests the same module).

const statusNode = () => document.querySelector('#status');
const guard = () => window.__potatoAtlasBootGuard;
const OPTIONAL_TIMEOUT_MS = 12000;
const modulePromises = new Map();
const ATLAS_VERSION = new URL(import.meta.url).searchParams.get('v') || '';

function versionedModule(path) {
  if (!ATLAS_VERSION) return path;
  const url = new URL(path, import.meta.url);
  url.searchParams.set('v', ATLAS_VERSION);
  return url.href;
}

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
    const resolvedPath = versionedModule(path);
    diagnostic(label, {
      path,
      resolvedPath,
      status: 'loading',
      startedAtMs: Math.round(startedAt - window.__potatoAtlasDiagnostics.startedAt),
    });
    let timer;
    try {
      await Promise.race([
        import(resolvedPath),
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
  deploymentVersion: ATLAS_VERSION || 'unversioned-source',
  coreReadyMs: null,
  interactiveMs: null,
  modules: {},
};
window.__potatoAtlasReady = false;
window.__potatoAtlasLoadModule = loadAfterPaint;

try {
  setStatus('Loading core atlas…');

  await import(versionedModule('./3d-hover.js'));
  const map = await waitForCore();
  await nextPaint();

  await loadAfterPaint('Capability registry', './3d-capability-registry.js');
  await loadAfterPaint('Progressive UI', './3d-ui.js');
  await loadAfterPaint('Spatial navigation', './3d-spatial-navigation.js');
  await loadAfterPaint('Selection UI', './3d-selection-ui.js');

  setStatus('');
  if (guard()) guard().stage = 'interactive';
  window.__potatoAtlasDiagnostics.interactiveMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-interactive'));

  declareDormant('Path finder', './3d-pathfinder.js', 'Relations zone');
  declareDormant('Entity Trace', './3d-entity-trace.js', 'Relations zone');
  declareDormant('Relationship inspector', './3d-relation-inspector.js', 'Relations zone');
  declareDormant('Demography', './3d-demography.js', 'first country inspection');
  declareDormant('Demography facets', './3d-demography-facets.js', 'World zone');
  declareDormant('Evidence', './3d-evidence.js', 'first country inspection');
  declareDormant('Fields', './3d-fields.js', 'Axis zone');
  declareDormant('Networks', './3d-networks.js', 'Relations zone');
  declareDormant('Time', './3d-time.js', 'Time zone');
  declareDormant('Metric dimensions', './3d-metric-dimensions.js', 'World zone');
  declareDormant('Axis depth', './3d-axis-depth.js', 'Axis zone');
  declareDormant('Axis operators', './3d-axis-operators.js', 'Axis zone');
  declareDormant('North Axis', './3d-axis.js', 'Axis zone');

  const promoteWorld = async () => {
    await Promise.all([
      loadAfterPaint('Metric dimensions', './3d-metric-dimensions.js'),
      loadAfterPaint('Demography facets', './3d-demography-facets.js'),
    ]);
  };
  const promoteRelations = async () => {
    await Promise.all([
      loadAfterPaint('Networks', './3d-networks.js'),
      loadAfterPaint('Path finder', './3d-pathfinder.js'),
      loadAfterPaint('Entity Trace', './3d-entity-trace.js'),
      loadAfterPaint('Relationship inspector', './3d-relation-inspector.js'),
    ]);
  };
  const promoteTime = () => loadAfterPaint('Time', './3d-time.js');
  const promoteAxis = async () => {
    await Promise.all([
      loadAfterPaint('Fields', './3d-fields.js'),
      loadAfterPaint('Axis depth', './3d-axis-depth.js'),
      loadAfterPaint('Axis operators', './3d-axis-operators.js'),
      loadAfterPaint('North Axis', './3d-axis.js'),
    ]);
  };
  const promoteInspection = async () => {
    await Promise.all([
      loadAfterPaint('Demography', './3d-demography.js'),
      loadAfterPaint('Evidence', './3d-evidence.js'),
    ]);
  };

  window.addEventListener('potato-atlas-zone-open', event => {
    const zone = event.detail?.zone;
    if (zone === 'world') promoteWorld();
    else if (zone === 'relations') promoteRelations();
    else if (zone === 'time') promoteTime();
    else if (zone === 'axis') promoteAxis();
  });

  // Compatibility controls remain hidden while providers migrate. They trigger
  // the same semantic promotion functions instead of owning a second UI model.
  const layersMenu = document.getElementById('layersMenu');
  const traceMenu = document.getElementById('traceMenu');
  const timeMenu = document.getElementById('timeMenu');
  const viewMenu = document.getElementById('viewMenu');

  const onLayersToggle = () => {
    if (!layersMenu?.open) return;
    layersMenu.removeEventListener('toggle', onLayersToggle);
    Promise.all([promoteWorld(), promoteAxis(), loadAfterPaint('Networks', './3d-networks.js')]);
  };
  const onTraceToggle = () => {
    if (!traceMenu?.open) return;
    traceMenu.removeEventListener('toggle', onTraceToggle);
    promoteRelations();
  };
  const onTimeToggle = () => {
    if (!timeMenu?.open) return;
    timeMenu.removeEventListener('toggle', onTimeToggle);
    promoteTime();
  };
  const onViewToggle = () => {
    if (!viewMenu?.open) return;
    viewMenu.removeEventListener('toggle', onViewToggle);
    Promise.all([promoteWorld(), promoteAxis()]);
  };
  layersMenu?.addEventListener('toggle', onLayersToggle);
  traceMenu?.addEventListener('toggle', onTraceToggle);
  timeMenu?.addEventListener('toggle', onTimeToggle);
  viewMenu?.addEventListener('toggle', onViewToggle);

  if (new URL(location.href).searchParams.get('religion')) {
    loadAfterPaint('Demography facets', './3d-demography-facets.js');
  }

  map.once('click', promoteInspection);

  window.__potatoAtlasDiagnostics.bootstrapWiredMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-bootstrap-complete', { detail: window.__potatoAtlasEnhancements }));
} catch (error) {
  console.error('3D atlas core bootstrap failed.', error);
  if (guard()) guard().failures.push(error?.message || String(error));
  setStatus(`Atlas core failed to boot: ${error?.message || error}`, 'error');
}
