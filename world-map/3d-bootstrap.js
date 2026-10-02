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
  if (node) { node.hidden = !message; node.dataset.kind = kind; node.textContent = message; }
  if (guard()) guard().stage = message || 'ready';
}
function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
function nextPaint(maxWaitMs = 160) {
  return new Promise(resolve => {
    let done = false;
    const finish = () => { if (done) return; done = true; clearTimeout(timer); resolve(); };
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
function declareDormant(label, path, trigger) { diagnostic(label, { path, status: 'dormant', trigger }); }
function loadOptional(label, path) {
  if (modulePromises.has(label)) return modulePromises.get(label);
  const promise = (async () => {
    const startedAt = now();
    const resolvedPath = versionedModule(path);
    diagnostic(label, { path, resolvedPath, status:'loading', startedAtMs:Math.round(startedAt - window.__potatoAtlasDiagnostics.startedAt) });
    let timer;
    try {
      await Promise.race([
        import(resolvedPath),
        new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(`${label} exceeded the optional-module deadline.`)), OPTIONAL_TIMEOUT_MS); }),
      ]);
      const durationMs = Math.round(now() - startedAt);
      diagnostic(label, { status:'loaded', durationMs });
      if (!window.__potatoAtlasEnhancements.loaded.includes(label)) window.__potatoAtlasEnhancements.loaded.push(label);
      window.dispatchEvent(new CustomEvent('potato-atlas-module-ready', { detail:{ label, path, durationMs } }));
      return true;
    } catch (error) {
      const durationMs = Math.round(now() - startedAt);
      const message = error?.message || String(error);
      diagnostic(label, { status:'failed', durationMs, error:message });
      window.__potatoAtlasEnhancements.failed.push({ label, message });
      console.warn(`${label} enhancement unavailable:`, error);
      return false;
    } finally { clearTimeout(timer); }
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
async function loadBatchAfterPaint(entries = []) {
  if (!entries.length) return [];
  await nextPaint();
  const results = await Promise.all(entries.map(([label, path]) => loadOptional(label, path)));
  await nextPaint();
  return results;
}

window.__potatoAtlasEnhancements = { loaded: [], failed: [] };
window.__potatoAtlasDiagnostics = {
  startedAt:now(), startedAtIso:new Date().toISOString(), deploymentVersion:ATLAS_VERSION || 'unversioned-source',
  coreReadyMs:null, interactiveMs:null, modules:{},
  scalarCompositions:0, scalarFeatureStateBatches:0, countryCardRenders:0, inspectorRenders:0,
  cardEnhancementPasses:0, inspectorEnhancementPasses:0, specialistLazyLoads:0,
};
window.__potatoAtlasReady = false;
window.__potatoAtlasLoadModule = loadAfterPaint;

try {
  setStatus('Loading core atlas…');
  await import(versionedModule('./3d-geometry-aliases.js'));
  await import(versionedModule('./3d-core-interaction-handoff.js'));
  await import(versionedModule('./3d-hover.js'));
  const map = await waitForCore();
  await loadBatchAfterPaint([
    ['Interaction Router', './3d-interaction-router.js'],
    ['URL State', './3d-url-state.js'],
    ['Inspector Router', './3d-inspector-router.js'],
  ]);
  await loadBatchAfterPaint([
    ['Inspector URL', './3d-inspector-url.js'],
    ['Inspector Visibility', './3d-inspector-visibility.js'],
    ['Country selection', './3d-country-selection.js'],
    ['Panel lifecycle', './3d-panel-lifecycle.js'],
    ['Layer Registry', './3d-layer-registry.js'],
  ]);
  await loadAfterPaint('Compositor', './3d-compositor.js');
  await loadBatchAfterPaint([
    ['Spatial Overlays', './3d-spatial-overlays.js'],
    ['Entity Runtime', './3d-entity-runtime.js'],
    ['Active View', './3d-active-view.js'],
    ['Investigation Surface', './3d-investigation-surface.js'],
  ]);
  await loadBatchAfterPaint([
    ['Spatial Overlay UI', './3d-spatial-overlay-ui.js'],
    ['Country Presentation', './3d-country-presentation.js'],
    ['World Bar', './3d-world-bar.js'],
    ['Scalar Runtime Bridge', './3d-scalar-runtime-bridge.js'],
  ]);
  await loadBatchAfterPaint([
    ['Country Hover Presentation', './3d-country-hover-presentation.js'],
    ['Country Card', './3d-country-card.js'],
    ['Runtime Telemetry', './3d-runtime-telemetry.js'],
  ]);

  setStatus('');
  if (guard()) guard().stage = 'interactive';
  window.__potatoAtlasDiagnostics.interactiveMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-interactive'));

  declareDormant('System Intelligence', './3d-gateways.js', 'Country → Context');
  declareDormant('Functional Chains', './3d-chain-explorer.js', 'Country → Context');
  declareDormant('Infrastructure Context', './3d-infrastructure.js', 'Country → Context');
  declareDormant('Impact Trace', './3d-impact-trace.js', 'Country → Impact');
  declareDormant('Impact Actions', './3d-impact-actions.js', 'Country → Impact');
  declareDormant('Path finder', './3d-pathfinder.js', 'Country → Path');
  declareDormant('Entity Trace', './3d-entity-trace.js', 'Country → Trace');
  declareDormant('Demography', './3d-demography.js', 'specialist demographic view');
  declareDormant('Country Pulse', './3d-country-pulse.js', 'Country → Statistics');
  declareDormant('Evidence', './3d-evidence.js', 'Country → More data');
  declareDormant('Time', './3d-time.js', 'contextual time action');
  declareDormant('Axis depth', './3d-axis-depth.js', 'contextual Axis action');
  declareDormant('Axis operators', './3d-axis-operators.js', 'contextual Axis action');
  declareDormant('North Axis', './3d-axis.js', 'contextual Axis action');

  // Specialist country modules are intentionally action-driven.
  // Selecting a country should remain cheap; Statistics, More data, Context,
  // Trace, Path and Impact each load only the module they actually need.
  window.__potatoAtlasDiagnostics.bootstrapWiredMs = Math.round(now() - window.__potatoAtlasDiagnostics.startedAt);
  window.dispatchEvent(new CustomEvent('potato-atlas-bootstrap-complete', { detail:window.__potatoAtlasEnhancements }));
} catch (error) {
  console.error('3D atlas core bootstrap failed.', error);
  if (guard()) guard().failures.push(error?.message || String(error));
  setStatus(`Atlas core failed to boot: ${error?.message || error}`, 'error');
}
