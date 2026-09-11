// Core-first bootstrap for the 3D World Relational Atlas.
//
// The geographic renderer is the availability boundary. Optional overlays load
// only after the core map has constructed and installed its country layers, so
// an Axis/evidence/network/UI enhancement can fail without blanking the world.

const statusNode = () => document.querySelector('#status');
const guard = () => window.__potatoAtlasBootGuard;

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

async function waitForCore(timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const map = window.__potatoAtlasMap;
    if (map && window.__potatoAtlasReady && map.getLayer?.('countries-fill')) return map;
    await sleep(40);
  }
  throw new Error('Core atlas map did not become ready before the bootstrap deadline.');
}

async function loadOptional(label, path) {
  try {
    await import(path);
    window.__potatoAtlasEnhancements.loaded.push(label);
  } catch (error) {
    window.__potatoAtlasEnhancements.failed.push({ label, message: error?.message || String(error) });
    console.warn(`${label} enhancement unavailable:`, error);
  }
}

window.__potatoAtlasEnhancements = { loaded: [], failed: [] };

try {
  setStatus('Loading core atlas…');

  // 3d-hover owns resilient data routing and imports 3d-app, which constructs
  // the MapLibre map. Keeping this first preserves the last-known-working core
  // boot topology from before optional layers multiplied.
  await import('./3d-hover.js');
  await waitForCore();

  setStatus('Core atlas ready…');

  // The first two modules were part of the last-known-working composition.
  // Everything else is deliberately optional and isolated behind the core map.
  const modules = [
    ['Path finder', './3d-pathfinder.js'],
    ['Demography', './3d-demography.js'],
    ['Evidence', './3d-evidence.js'],
    ['Fields', './3d-fields.js'],
    ['Networks', './3d-networks.js'],
    ['Time', './3d-time.js'],
    ['Axis depth', './3d-axis-depth.js'],
    ['Axis operators', './3d-axis-operators.js'],
    ['North Axis', './3d-axis.js'],
    ['Progressive UI', './3d-ui.js'],
  ];

  for (const [label, path] of modules) {
    await loadOptional(label, path);
  }

  setStatus('');
  window.dispatchEvent(new CustomEvent('potato-atlas-bootstrap-complete', {
    detail: window.__potatoAtlasEnhancements,
  }));
} catch (error) {
  console.error('3D atlas core bootstrap failed.', error);
  if (guard()) guard().failures.push(error?.message || String(error));
  setStatus(`Atlas core failed to boot: ${error?.message || error}`, 'error');
}
