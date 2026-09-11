// Core-first bootstrap for the 3D World Relational Atlas.
//
// The geographic renderer is the availability boundary. The map and lightweight
// registry/query UI become interactive first. Deeper analytical/enrichment modules
// stay dormant until a user action needs them.

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

  // Ordinary interaction is now registry-driven. Legacy Progressive UI,
  // Selection UI and Lenses are compatibility modules only; they no longer boot
  // into the normal map path because they generated redundant surfaces and a
  // single-fill analytical model.
  await loadAfterPaint('Country selection', './3d-country-selection.js');
  await loadAfterPaint('Layer Registry', './3d-layer-registry.js');
  await loadAfterPaint('Compositor', './3d-compositor.js');
  await loadAfterPaint('World Bar', './3d-world-bar.js');
  await loadAfterPaint('Country Card', './3d-country-card.js');

  setStatus('');
  if (guard()) guard().stage = 'interactive';
  window.__potatoAtlasDiagnostics.interactiveMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-interactive'));

  declareDormant('Progressive UI', './3d-ui.js', 'legacy compatibility');
  declareDormant('Selection UI', './3d-selection-ui.js', 'legacy compatibility');
  declareDormant('Lenses', './3d-lenses.js', 'legacy compatibility');
  declareDormant('Path finder', './3d-pathfinder.js', 'contextual investigation');
  declareDormant('Entity Trace', './3d-entity-trace.js', 'contextual investigation');
  declareDormant('Demography', './3d-demography.js', 'first country inspection');
  declareDormant('Country Pulse', './3d-country-pulse.js', 'first country inspection');
  declareDormant('Evidence', './3d-evidence.js', 'first country inspection');
  declareDormant('Fields', './3d-fields.js', 'contextual advanced layers');
  declareDormant('Networks', './3d-networks.js', 'contextual advanced relations');
  declareDormant('Time', './3d-time.js', 'contextual time action');
  declareDormant('Axis depth', './3d-axis-depth.js', 'contextual Axis action');
  declareDormant('Axis operators', './3d-axis-operators.js', 'contextual Axis action');
  declareDormant('North Axis', './3d-axis.js', 'contextual Axis action');

  const promoteInspection = async () => {
    await Promise.all([
      loadAfterPaint('Demography', './3d-demography.js'),
      loadAfterPaint('Country Pulse', './3d-country-pulse.js'),
      loadAfterPaint('Evidence', './3d-evidence.js'),
    ]);
  };

  let inspectionPromoted = false;
  const promoteInspectionOnce = event => {
    if (inspectionPromoted) return;
    if (event?.detail && !event.detail.selected) return;
    inspectionPromoted = true;
    window.removeEventListener('potato-atlas-working-selection-change', promoteInspectionOnce);
    promoteInspection();
  };
  window.addEventListener('potato-atlas-working-selection-change', promoteInspectionOnce);
  map.once('click', promoteInspectionOnce);
  if (window.__potatoAtlasSelection?.current?.selected) promoteInspectionOnce({ detail: { selected: true } });

  window.__potatoAtlasDiagnostics.bootstrapWiredMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-bootstrap-complete', { detail: window.__potatoAtlasEnhancements }));
} catch (error) {
  console.error('3D atlas core bootstrap failed.', error);
  if (guard()) guard().failures.push(error?.message || String(error));
  setStatus(`Atlas core failed to boot: ${error?.message || error}`, 'error');
}
