// Composable analytical renderer for the World Relational Atlas.
// One scalar owns base fill; categorical memberships occupy a separate pattern
// layer; country selection remains owned by the existing selection subsystem.

const map = window.__potatoAtlasMap;
const layers = window.__potatoAtlasLayers;
if (!map) throw new Error('Atlas compositor requires the core map.');
if (!layers) throw new Error('Atlas compositor requires the layer registry.');

await layers.ready;

const WORLD_URL = '../data/world-relational-map.json';
const DEMOGRAPHY_URL = '../data/world-country-demography.json';
const NEUTRAL = '#566262';
const UNKNOWN = '#303938';
const PATTERN_LAYER = 'atlas-composition-fill';
const PATTERN_NONE = 'atlas-pattern-none';
const QUERY_LAYER = 'atlas-query-outline';

let world = null;
let demography = null;
let queryMode = new URL(location.href).searchParams.get('query') === 'all' ? 'all' : 'any';
let setMemberships = new Map();
let queryMarkedCodes = new Set();
let renderSerial = 0;

async function fetchJson(url) {
  const response = await fetch(url, { cache: 'no-cache' });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}
async function worldData() { if (!world) world = await fetchJson(WORLD_URL); return world; }
async function demographyData() { if (!demography) demography = await fetchJson(DEMOGRAPHY_URL); return demography; }

function hexToRgb(hex) {
  const value = String(hex || '').replace('#', '');
  const full = value.length === 3 ? value.split('').map(x => x + x).join('') : value;
  const parsed = Number.parseInt(full, 16);
  if (!Number.isFinite(parsed)) return [180, 180, 180];
  return [(parsed >> 16) & 255, (parsed >> 8) & 255, parsed & 255];
}

function setBaseFill(expression) {
  for (const layerId of ['countries-fill', 'countries-extrude']) {
    if (!map.getLayer(layerId)) continue;
    const property = layerId === 'countries-fill' ? 'fill-color' : 'fill-extrusion-color';
    map.setPaintProperty(layerId, property, expression);
  }
}

function ensurePatternImage(name, colors = [], highOverlap = 0) {
  if (map.hasImage?.(name)) return;
  const width = 12;
  const height = 12;
  const data = new Uint8Array(width * height * 4);
  const palette = colors.length ? colors.map(hexToRgb) : [[255, 255, 255]];
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      if (!colors.length && !highOverlap) {
        data[offset + 3] = 0;
        continue;
      }
      let rgb;
      let alpha;
      if (highOverlap) {
        const level = Math.min(255, 105 + highOverlap * 24);
        rgb = [240, 224, 157];
        alpha = ((x + y) % 4 < 2) ? level : Math.max(60, level - 80);
      } else {
        const stripe = Math.floor((x + y) / 3) % palette.length;
        rgb = palette[stripe];
        alpha = 190;
      }
      data[offset] = rgb[0];
      data[offset + 1] = rgb[1];
      data[offset + 2] = rgb[2];
      data[offset + 3] = alpha;
    }
  }
  map.addImage(name, { width, height, data });
}

function ensurePatternLayer() {
  ensurePatternImage(PATTERN_NONE);
  if (map.getLayer(PATTERN_LAYER)) return;
  const before = map.getLayer('countries-outline') ? 'countries-outline' : undefined;
  const layer = {
    id: PATTERN_LAYER,
    type: 'fill',
    source: 'countries',
    paint: {
      'fill-pattern': PATTERN_NONE,
      'fill-opacity': 0.82,
      'fill-antialias': true,
    },
  };
  map.addLayer(layer, before);
}

function ensureQueryLayer() {
  if (map.getLayer(QUERY_LAYER)) return;
  const before = map.getLayer('countries-line') ? 'countries-line' : (map.getLayer('countries-outline') ? 'countries-outline' : undefined);
  map.addLayer({
    id: QUERY_LAYER,
    type: 'line',
    source: 'countries',
    paint: {
      'line-color': '#dff1d8',
      'line-width': ['interpolate', ['linear'], ['zoom'], 1, 1.1, 5, 2.4, 8, 3.2],
      'line-opacity': ['case', ['boolean', ['feature-state', 'atlasQueryMatch'], false], 0.72, 0],
      'line-blur': 0.8,
    },
  }, before);
}

function collectIsoArrays(value, target, { excludedKeys = new Set() } = {}) {
  if (!value || typeof value !== 'object') return;
  if (Array.isArray(value)) {
    for (const code of value) if (/^[A-Z]{3}$/.test(String(code || ''))) target.add(code);
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    if (excludedKeys.has(key)) continue;
    collectIsoArrays(child, target, { excludedKeys });
  }
}

function sourceValue(root, path) {
  return String(path || '').split('.').filter(Boolean).reduce((value, key) => value?.[key], root);
}

async function membershipFor(entry) {
  if (setMemberships.has(entry.id)) return setMemberships.get(entry.id);
  const result = new Set();
  const data = await worldData();

  if (entry.id === 'axis.north') {
    collectIsoArrays(data?.project_axis?.north, result, { excludedKeys: new Set(['external', 'excluded_current_version', 'future_reconnection']) });
  } else if (entry.id === 'axis.west') {
    collectIsoArrays(data?.project_axis?.west, result);
  } else if (entry.id === 'axis.east') {
    collectIsoArrays(data?.project_axis?.east, result);
  } else if (entry.id === 'axis.south') {
    // Only explicit ISO arrays count. Candidate-region prose is deliberately ignored.
    collectIsoArrays(data?.project_axis?.south, result);
  } else if (entry.id.startsWith('group.')) {
    const keyMap = {
      'group.nato': 'NATO',
      'group.brics': 'BRICS',
      'group.aukus': 'AUKUS',
      'group.five-eyes': 'Five_Eyes',
    };
    const group = data?.empirical_memberships?.[keyMap[entry.id]] || sourceValue(data, entry.source_path);
    collectIsoArrays(group?.members || [], result);
    collectIsoArrays(group?.partners || [], result);
  }
  setMemberships.set(entry.id, result);
  return result;
}

function religionKey(entry) {
  const tail = entry.id.split('.').pop();
  return tail === 'other' ? 'other_religions' : tail;
}

async function applyReligionScalar(entry) {
  const data = await demographyData();
  const key = religionKey(entry);
  for (const [code, row] of Object.entries(data?.countries || {})) {
    const raw = row?.religion?.composition?.[key];
    const value = Number(raw);
    try {
      map.setFeatureState({ source: 'countries', id: code }, {
        atlasScalarHas: Number.isFinite(value),
        atlasScalarValue: Number.isFinite(value) ? value : 0,
      });
    } catch { /* some territories may not exist in the polygon source */ }
  }
  const color = entry.color || '#7fa7a0';
  setBaseFill([
    'case',
    ['boolean', ['feature-state', 'atlasScalarHas'], false],
    ['interpolate', ['linear'], ['feature-state', 'atlasScalarValue'], 0, '#1e2928', 20, '#3c5551', 50, color, 80, '#dfd49c', 100, '#fff0bf'],
    UNKNOWN,
  ]);
}

function applyGeographicScalar(entry) {
  const key = entry.id === 'stat.area' ? 'area' : 'population';
  if (key === 'area') {
    setBaseFill(['case', ['>', ['get', 'area'], 0], ['step', ['get', 'area'], '#263432', 10000, '#36514b', 100000, '#527466', 500000, '#78977d', 1000000, '#a7b87f', 5000000, '#d0c77e'], UNKNOWN]);
  } else {
    setBaseFill(['case', ['>', ['get', 'population'], 0], ['step', ['get', 'population'], '#263432', 1000000, '#36514b', 10000000, '#527466', 50000000, '#78977d', 100000000, '#a7b87f', 500000000, '#d0c77e'], UNKNOWN]);
  }
}

async function applyScalar(entries) {
  const scalar = entries.find(entry => entry.kind === 'scalar') || null;
  if (!scalar) {
    setBaseFill(NEUTRAL);
    return;
  }
  if (scalar.family === 'religion') return applyReligionScalar(scalar);
  if (scalar.id === 'stat.population' || scalar.id === 'stat.area') return applyGeographicScalar(scalar);
  // Planned scalar ids cannot become active through the registry API, but keep a
  // safe neutral fallback for future migrations and stale URLs.
  setBaseFill(NEUTRAL);
}

function hashString(input) {
  let hash = 5381;
  for (const char of input) hash = ((hash << 5) + hash) ^ char.charCodeAt(0);
  return (hash >>> 0).toString(36);
}

async function applyPatterns(setEntries) {
  ensurePatternLayer();
  if (!setEntries.length) {
    map.setPaintProperty(PATTERN_LAYER, 'fill-pattern', PATTERN_NONE);
    return;
  }

  const memberships = new Map();
  const allCodes = new Set();
  for (const entry of setEntries) {
    const members = await membershipFor(entry);
    memberships.set(entry.id, members);
    for (const code of members) allCodes.add(code);
  }

  const patternByCode = {};
  for (const code of allCodes) {
    const matches = setEntries.filter(entry => memberships.get(entry.id)?.has(code));
    if (!matches.length) continue;
    if (matches.length <= 3) {
      const signature = matches.map(entry => entry.id).sort().join('|');
      const name = `atlas-p-${hashString(signature)}`;
      ensurePatternImage(name, matches.map(entry => entry.color || '#d8d8d8'));
      patternByCode[code] = name;
    } else {
      const name = `atlas-overlap-${matches.length}`;
      ensurePatternImage(name, [], matches.length);
      patternByCode[code] = name;
    }
  }

  const expression = ['match', ['get', 'iso3']];
  for (const [code, name] of Object.entries(patternByCode).sort(([a], [b]) => a.localeCompare(b))) expression.push(code, name);
  expression.push(PATTERN_NONE);
  map.setPaintProperty(PATTERN_LAYER, 'fill-pattern', expression);
}

function activeSetEntries() {
  return layers.active().map(id => layers.get(id)).filter(entry => entry?.kind === 'set' && entry.queryable);
}

async function membershipSnapshot() {
  const entries = activeSetEntries();
  const result = new Map();
  for (const entry of entries) result.set(entry.id, await membershipFor(entry));
  return { entries, result };
}

async function matchedCountries() {
  const { entries, result } = await membershipSnapshot();
  if (!entries.length) return [];
  const universe = new Set();
  for (const members of result.values()) for (const code of members) universe.add(code);
  return [...universe].filter(code => {
    const states = entries.map(entry => result.get(entry.id)?.has(code) || false);
    return queryMode === 'all' ? states.every(Boolean) : states.some(Boolean);
  }).sort();
}

async function matches(iso3) {
  const { entries, result } = await membershipSnapshot();
  if (!entries.length) return true;
  const states = entries.map(entry => result.get(entry.id)?.has(iso3) || false);
  return queryMode === 'all' ? states.every(Boolean) : states.some(Boolean);
}

async function applyQueryHighlight() {
  ensureQueryLayer();
  const activeSets = activeSetEntries();
  const matched = activeSets.length ? await matchedCountries() : [];
  const next = new Set(matched);
  const touched = new Set([...queryMarkedCodes, ...next]);
  for (const code of touched) {
    try {
      map.setFeatureState({ source: 'countries', id: code }, { atlasQueryMatch: next.has(code) });
    } catch { /* some registry codes may not exist in the polygon source */ }
  }
  queryMarkedCodes = next;
  window.dispatchEvent(new CustomEvent('potato-atlas-query-result-change', {
    detail: {
      mode: queryMode,
      activeSetCount: activeSets.length,
      countries: matched,
      count: matched.length,
    },
  }));
}

async function render() {
  const serial = ++renderSerial;
  const entries = layers.active().map(id => layers.get(id)).filter(Boolean);
  try {
    await applyScalar(entries);
    if (serial !== renderSerial) return;
    await applyPatterns(entries.filter(entry => entry.kind === 'set'));
    if (serial !== renderSerial) return;
    await applyQueryHighlight();
    if (serial !== renderSerial) return;
    window.dispatchEvent(new CustomEvent('potato-atlas-composition-change', {
      detail: { active: entries.map(entry => entry.id), scalar: entries.find(entry => entry.kind === 'scalar')?.id || null, sets: entries.filter(entry => entry.kind === 'set').map(entry => entry.id) },
    }));
  } catch (error) {
    console.warn('Atlas composition unavailable:', error);
    if (serial === renderSerial) {
      setBaseFill(NEUTRAL);
      try {
        ensurePatternLayer();
        map.setPaintProperty(PATTERN_LAYER, 'fill-pattern', PATTERN_NONE);
        await applyQueryHighlight();
      } catch { /* core geography remains usable */ }
    }
  }
}

function persistQuery() {
  const url = new URL(location.href);
  const count = activeSetEntries().length;
  if (count >= 2) url.searchParams.set('query', queryMode);
  else url.searchParams.delete('query');
  history.replaceState({}, '', url);
}

function setQueryMode(mode) {
  const next = mode === 'all' ? 'all' : 'any';
  if (queryMode === next) return;
  queryMode = next;
  persistQuery();
  window.dispatchEvent(new CustomEvent('potato-atlas-query-change', { detail: { mode: queryMode } }));
  render();
}

window.__potatoAtlasQuery = {
  setMode: setQueryMode,
  getMode() { return queryMode; },
  matches,
  matchedCountries,
  activeSetCount() { return activeSetEntries().length; },
};

window.__potatoAtlasCompositor = {
  render,
  state() {
    const entries = layers.active().map(id => layers.get(id)).filter(Boolean);
    return { active: entries.map(entry => entry.id), scalar: entries.find(entry => entry.kind === 'scalar')?.id || null, sets: entries.filter(entry => entry.kind === 'set').map(entry => entry.id), queryMode };
  },
  reset() { layers.reset(); setQueryMode('any'); },
};

window.addEventListener('potato-atlas-layer-change', () => { persistQuery(); render(); });
ensurePatternLayer();
ensureQueryLayer();
await render();