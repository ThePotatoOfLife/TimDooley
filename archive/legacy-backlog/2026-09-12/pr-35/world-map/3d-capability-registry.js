// Semantic capability registry for the 3D World Relational Atlas.
//
// UI modules register meaning here once. The spatial navigation shell decides
// where that meaning appears. Registry state describes UI activation only; it
// never changes empirical/project truth layers or converts magnitude into Axis
// height.

const descriptors = new Map();
const VALID_ZONES = new Set(['world', 'relations', 'time', 'axis', 'settings']);
const VALID_STATE_SLOTS = new Set(['baseSurface', 'worldOverlays', 'relationModes', 'axisLens']);

const active = {
  baseSurface: null,
  worldOverlays: new Set(),
  relationModes: new Set(),
  axisLens: null,
};

function serializableActiveState() {
  return {
    baseSurface: active.baseSurface,
    worldOverlays: [...active.worldOverlays],
    relationModes: [...active.relationModes],
    axisLens: active.axisLens,
  };
}

function providerReportsActive(descriptor) {
  try {
    return Boolean(descriptor?.getState?.()?.active);
  } catch {
    return false;
  }
}

function descriptorIsActive(descriptor) {
  if (!descriptor) return false;
  if (descriptor.stateSlot === 'baseSurface') return active.baseSurface === descriptor.id;
  if (descriptor.stateSlot === 'worldOverlays') return active.worldOverlays.has(descriptor.id);
  if (descriptor.stateSlot === 'relationModes') return active.relationModes.has(descriptor.id);
  if (descriptor.stateSlot === 'axisLens') return active.axisLens === descriptor.id;
  return providerReportsActive(descriptor);
}

function availabilityFor(descriptor, context = {}) {
  try {
    const value = typeof descriptor.availability === 'function'
      ? descriptor.availability(context)
      : descriptor.availability;
    if (value == null) return { available: true };
    if (typeof value === 'boolean') return { available: value, reason: value ? '' : 'Unavailable' };
    return {
      available: value.available !== false,
      reason: value.reason || '',
    };
  } catch (error) {
    return { available: false, reason: error?.message || 'Unavailable' };
  }
}

function emitRegistryChange(type, descriptor) {
  window.dispatchEvent(new CustomEvent('potato-atlas-capability-registry-change', {
    detail: {
      type,
      id: descriptor?.id || null,
      descriptor: descriptor || null,
      state: serializableActiveState(),
    },
  }));
}

function emitCapabilityChange(descriptor, isActive, result = null) {
  window.dispatchEvent(new CustomEvent('potato-atlas-capability-change', {
    detail: {
      id: descriptor.id,
      active: Boolean(isActive),
      descriptor,
      result,
      state: serializableActiveState(),
    },
  }));
}

function normalizeDescriptor(input) {
  if (!input || typeof input !== 'object') throw new Error('Atlas capability descriptor must be an object.');
  const descriptor = { ...input };
  if (!descriptor.id || !descriptor.name) throw new Error('Atlas capability requires id and name.');
  if (!VALID_ZONES.has(descriptor.zone)) throw new Error(`Invalid Atlas capability zone: ${descriptor.zone}`);
  if (!descriptor.category) throw new Error(`Atlas capability ${descriptor.id} requires a category.`);
  if (!descriptor.kind) throw new Error(`Atlas capability ${descriptor.id} requires a kind.`);
  if (!descriptor.colorFamily) throw new Error(`Atlas capability ${descriptor.id} requires a colorFamily.`);
  if (!descriptor.description) throw new Error(`Atlas capability ${descriptor.id} requires a description.`);
  if (descriptor.stateSlot && !VALID_STATE_SLOTS.has(descriptor.stateSlot)) {
    throw new Error(`Invalid Atlas capability stateSlot: ${descriptor.stateSlot}`);
  }
  if (typeof descriptor.activate !== 'function' || typeof descriptor.deactivate !== 'function') {
    throw new Error(`Atlas capability ${descriptor.id} requires activate/deactivate functions.`);
  }
  if (typeof descriptor.getState !== 'function') {
    throw new Error(`Atlas capability ${descriptor.id} requires getState().`);
  }
  descriptor.order = Number.isFinite(Number(descriptor.order)) ? Number(descriptor.order) : 999;
  return Object.freeze(descriptor);
}

function setActive(descriptor, on) {
  const id = descriptor.id;
  if (descriptor.stateSlot === 'baseSurface') active.baseSurface = on ? id : (active.baseSurface === id ? null : active.baseSurface);
  else if (descriptor.stateSlot === 'worldOverlays') on ? active.worldOverlays.add(id) : active.worldOverlays.delete(id);
  else if (descriptor.stateSlot === 'relationModes') on ? active.relationModes.add(id) : active.relationModes.delete(id);
  else if (descriptor.stateSlot === 'axisLens') active.axisLens = on ? id : (active.axisLens === id ? null : active.axisLens);
}

function register(input) {
  const descriptor = normalizeDescriptor(input);
  const existing = descriptors.get(descriptor.id);
  if (existing && existing !== descriptor) descriptors.delete(descriptor.id);
  descriptors.set(descriptor.id, descriptor);
  if (providerReportsActive(descriptor)) setActive(descriptor, true);
  emitRegistryChange(existing ? 'replace' : 'register', descriptor);
  return descriptor;
}

function unregister(id) {
  const descriptor = descriptors.get(id);
  if (!descriptor) return false;
  descriptors.delete(id);
  if (active.baseSurface === id) active.baseSurface = null;
  if (active.axisLens === id) active.axisLens = null;
  active.worldOverlays.delete(id);
  active.relationModes.delete(id);
  emitRegistryChange('unregister', descriptor);
  return true;
}

function list(filters = {}) {
  return [...descriptors.values()].filter(descriptor => {
    if (filters.zone && descriptor.zone !== filters.zone) return false;
    if (filters.category && descriptor.category !== filters.category) return false;
    if (filters.kind && descriptor.kind !== filters.kind) return false;
    return true;
  });
}

function get(id) {
  return descriptors.get(id) || null;
}

async function deactivate(id, context = {}) {
  const descriptor = descriptors.get(id);
  if (!descriptor) return { ok: false, reason: `Unknown Atlas capability: ${id}` };
  try {
    const result = await descriptor.deactivate(context);
    setActive(descriptor, false);
    emitCapabilityChange(descriptor, false, result);
    return { ok: true, result };
  } catch (error) {
    const reason = error?.message || String(error);
    emitCapabilityChange(descriptor, descriptorIsActive(descriptor), { error: reason });
    return { ok: false, reason };
  }
}

async function activate(id, context = {}) {
  const descriptor = descriptors.get(id);
  if (!descriptor) return { ok: false, reason: `Unknown Atlas capability: ${id}` };

  const availability = availabilityFor(descriptor, context);
  if (!availability.available) return { ok: false, reason: availability.reason || 'Unavailable' };

  if (descriptor.lazyModule && typeof window.__potatoAtlasLoadModule === 'function') {
    const loaded = await window.__potatoAtlasLoadModule(descriptor.name, descriptor.lazyModule);
    if (loaded === false) return { ok: false, reason: `${descriptor.name} failed to load.` };
  }

  if (descriptor.stateSlot === 'baseSurface' && active.baseSurface && active.baseSurface !== id) {
    await deactivate(active.baseSurface, { ...context, replacedBy: id });
  }
  if (descriptor.stateSlot === 'axisLens' && active.axisLens && active.axisLens !== id) {
    await deactivate(active.axisLens, { ...context, replacedBy: id });
  }

  try {
    const result = await descriptor.activate(context);
    setActive(descriptor, true);
    emitCapabilityChange(descriptor, true, result);
    return { ok: true, result };
  } catch (error) {
    const reason = error?.message || String(error);
    emitCapabilityChange(descriptor, descriptorIsActive(descriptor), { error: reason });
    return { ok: false, reason };
  }
}

function getActiveState() {
  const state = serializableActiveState();
  state.capabilities = [...descriptors.values()]
    .filter(descriptorIsActive)
    .map(descriptor => ({
      id: descriptor.id,
      name: descriptor.name,
      zone: descriptor.zone,
      category: descriptor.category,
      kind: descriptor.kind,
      colorFamily: descriptor.colorFamily,
      state: descriptor.getState?.() || {},
    }));
  return state;
}

function refreshFromProviders() {
  active.baseSurface = null;
  active.axisLens = null;
  active.worldOverlays.clear();
  active.relationModes.clear();
  for (const descriptor of descriptors.values()) {
    if (providerReportsActive(descriptor)) setActive(descriptor, true);
  }
  emitRegistryChange('refresh', null);
  return getActiveState();
}

window.__potatoAtlasCapabilities = {
  register,
  unregister,
  list,
  get,
  activate,
  deactivate,
  getActiveState,
  refreshFromProviders,
  availabilityFor: (id, context = {}) => {
    const descriptor = descriptors.get(id);
    return descriptor ? availabilityFor(descriptor, context) : { available: false, reason: `Unknown Atlas capability: ${id}` };
  },
};

window.dispatchEvent(new CustomEvent('potato-atlas-capability-registry-ready', {
  detail: { state: getActiveState() },
}));
