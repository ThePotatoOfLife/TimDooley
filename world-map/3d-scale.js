const CONTRACT_URL = '../data/world-map-scale-contract.json';
const EPSILON = 1e-9;

function finiteZoom(value, label = 'zoom') {
  const zoom = Number(value);
  if (!Number.isFinite(zoom)) throw new TypeError(`${label} must be finite`);
  return zoom;
}

function validateContract(contract) {
  if (!contract || typeof contract !== 'object') throw new TypeError('scale contract is required');
  if (!Array.isArray(contract.bands) || !contract.bands.length) throw new TypeError('scale contract bands are required');
  const bands = contract.bands.map(row => ({ id:String(row?.id || ''), min_zoom:finiteZoom(row?.min_zoom, 'band min_zoom') }));
  if (bands.some(row => !row.id)) throw new TypeError('scale band id is required');
  bands.sort((a, b) => a.min_zoom - b.min_zoom || a.id.localeCompare(b.id));
  for (let i = 1; i < bands.length; i += 1) {
    if (bands[i].min_zoom <= bands[i - 1].min_zoom) throw new TypeError('scale band min_zoom values must be strictly increasing');
  }
  const hysteresis = finiteZoom(contract.hysteresis ?? 0, 'hysteresis');
  if (hysteresis < 0) throw new RangeError('hysteresis must be non-negative');
  const capabilities = contract.capabilities || {};
  return { contract, bands, hysteresis, capabilities };
}

function createScaleRuntime(contract) {
  const state = validateContract(contract);
  const bandIndex = new Map(state.bands.map((row, index) => [row.id, index]));

  function bandForZoom(value) {
    const zoom = finiteZoom(value);
    let current = state.bands[0];
    for (const band of state.bands) {
      if (zoom + EPSILON < band.min_zoom) break;
      current = band;
    }
    return current.id;
  }

  function atLeast(bandId, value) {
    const requested = bandIndex.get(String(bandId || ''));
    if (requested == null) throw new TypeError(`unknown scale band: ${bandId}`);
    const current = bandIndex.get(bandForZoom(value));
    return current >= requested;
  }

  function bandThreshold(bandId) {
    const index = bandIndex.get(String(bandId || ''));
    if (index == null) throw new TypeError(`unknown scale band: ${bandId}`);
    return state.bands[index].min_zoom;
  }

  function threshold(capability, phase) {
    const row = state.capabilities?.[capability];
    if (!row) throw new TypeError(`unknown scale capability: ${capability}`);
    if (!(phase in row)) throw new TypeError(`unknown scale phase ${phase} for capability ${capability}`);
    return finiteZoom(row[phase], `${capability}.${phase}`);
  }

  function transition(previousBand, value) {
    const zoom = finiteZoom(value);
    const previousIndex = bandIndex.get(String(previousBand || ''));
    if (previousIndex == null) return bandForZoom(zoom);
    const targetIndex = bandIndex.get(bandForZoom(zoom));
    let index = previousIndex;
    if (targetIndex > index) {
      while (index < targetIndex) {
        const boundary = state.bands[index + 1].min_zoom + state.hysteresis;
        if (zoom + EPSILON < boundary) break;
        index += 1;
      }
    } else if (targetIndex < index) {
      while (index > targetIndex) {
        const boundary = state.bands[index].min_zoom - state.hysteresis;
        if (zoom + EPSILON >= boundary) break;
        index -= 1;
      }
    }
    return state.bands[index].id;
  }

  function capabilityActive(capability, phase, value, previousActive = null) {
    const zoom = finiteZoom(value);
    const boundary = threshold(capability, phase);
    if (previousActive == null) return zoom + EPSILON >= boundary;
    if (previousActive) return zoom + EPSILON >= boundary - state.hysteresis;
    return zoom + EPSILON >= boundary + state.hysteresis;
  }

  return Object.freeze({
    contract,
    bands:Object.freeze(state.bands.map(row => Object.freeze({ ...row }))),
    hysteresis:state.hysteresis,
    bandForZoom,
    bandThreshold,
    atLeast,
    threshold,
    transition,
    capabilityActive,
  });
}

async function fetchContract() {
  const response = await fetch(CONTRACT_URL, { cache:'no-cache' });
  if (!response.ok) throw new Error(`World Map scale contract unavailable (${response.status})`);
  return response.json();
}

let ready = null;
if (typeof window !== 'undefined') {
  ready = fetchContract().then(contract => {
    const runtime = createScaleRuntime(contract);
    window.__potatoAtlasScale = { ...runtime, ready:Promise.resolve(runtime) };
    window.dispatchEvent(new CustomEvent('potato-atlas-scale-ready', {
      detail:{ version:contract.version, bands:runtime.bands.map(row => row.id) }
    }));
    return runtime;
  });
  window.__potatoAtlasScale = { ready };
}

export { createScaleRuntime };
