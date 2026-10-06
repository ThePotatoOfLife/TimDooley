/* Shared browser loader for the Potatoism corpus. */
export async function loadPotatoismLayers(base = '.') {
  const files = {
    integration: 'data/potatoism-integration.json',
    deep: 'data/potatoism-deep-layers.json',
    glossary: 'data/potatoism-glossary.json',
    observations: 'data/potatoism-public-observations.json',
    events: 'data/potatoism-event-and-relation-atlas.json',
    religion: 'data/potatoism-religion.json'
  };
  const entries = await Promise.all(Object.entries(files).map(async ([key, path]) => {
    const response = await fetch(`${base}/${path}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${path}: ${response.status}`);
    return [key, await response.json()];
  }));
  return Object.fromEntries(entries);
}

export function potatoismSearch(layers, query) {
  const needle = String(query || '').trim().toLowerCase();
  if (!needle) return [];
  const values = [];
  for (const [layer, data] of Object.entries(layers || {})) {
    const records = Array.isArray(data) ? data : Object.values(data || {}).flatMap(value => Array.isArray(value) ? value : [value]);
    for (const record of records) {
      if (!record || typeof record !== 'object') continue;
      const haystack = JSON.stringify(record).toLowerCase();
      if (haystack.includes(needle)) values.push({ layer, record });
    }
  }
  return values;
}
