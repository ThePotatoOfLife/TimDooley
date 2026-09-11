// Lazy sourced metric runtime for the World Relational Atlas.
//
// The map stays fast at boot: this module only loads the canonical country index.
// Rich country records are fetched with bounded same-origin concurrency only when
// a non-geographic metric is requested. Canonical records remain the source of
// truth; this module is a presentation projection, not a second database.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas metrics require the core map.');

const INDEX_URL = '../data/countries/index.json';
const CONCURRENCY = 10;

const REGISTRY = {
  population: { label: 'Population', unit: 'people', native: true, scale: 'magnitude' },
  area: { label: 'Area', unit: 'km²', native: true, scale: 'magnitude' },
  gdp: { label: 'GDP', unit: 'current USD', scale: 'magnitude' },
  gdp_per_capita: { label: 'GDP / person', unit: 'current USD / person', scale: 'magnitude' },
  gdp_per_capita_ppp: { label: 'GDP / person · PPP', unit: 'international $ / person', scale: 'magnitude' },
  real_growth: { label: 'Real GDP growth', unit: '%', scale: 'diverging-zero' },
  inflation: { label: 'Inflation', unit: '%', scale: 'linear' },
  unemployment: { label: 'Unemployment', unit: '%', scale: 'linear' },
  labour_force_participation: { label: 'Labour participation', unit: '%', scale: 'linear' },
  life_expectancy: { label: 'Life expectancy', unit: 'years', scale: 'linear' },
  fertility: { label: 'Fertility', unit: 'births / woman', scale: 'linear' },
  urbanization: { label: 'Urban population', unit: '%', scale: 'linear' },
  poverty: { label: 'National poverty rate', unit: '%', scale: 'linear' },
  internet_penetration: { label: 'Internet use', unit: '%', scale: 'linear' },
  co2_emissions: { label: 'CO₂ / person', unit: 't CO₂ / person', scale: 'linear' },
};

const OBSERVATION_ALIASES = {
  population: ['population'],
  gdp: ['gdp'],
  gdp_per_capita: ['gdp_per_capita'],
  gdp_per_capita_ppp: ['gdp_per_capita_ppp'],
  real_growth: ['real_growth', 'real_gdp_growth'],
  inflation: ['inflation'],
  unemployment: ['unemployment'],
  labour_force_participation: ['labour_force_participation'],
  life_expectancy: ['life_expectancy'],
  fertility: ['fertility'],
  urbanization: ['urbanization'],
  poverty: ['poverty'],
  internet_penetration: ['internet_penetration'],
  co2_emissions: ['co2_emissions'],
};

let indexPromise;
let recordsPromise;
let indexRows = [];
const records = new Map();
const metricCache = new Map();

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

async function loadIndex() {
  if (!indexPromise) {
    indexPromise = fetchJson(INDEX_URL).then(data => {
      indexRows = Array.isArray(data.countries) ? data.countries : [];
      return indexRows;
    });
  }
  return indexPromise;
}

function finite(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}
function periodOf(value, fallback = null) {
  return value?.year ?? value?.reference_period ?? value?.period ?? fallback;
}
function sourceOf(value, fallback = null) {
  return value?.source || fallback;
}
function observation(record, id) {
  const observations = record?.observations || {};
  for (const key of OBSERVATION_ALIASES[id] || [id]) {
    const raw = observations[key];
    if (!raw || typeof raw !== 'object') continue;
    const value = finite(raw.value);
    if (value === null) continue;
    return {
      value,
      unit: raw.unit || '',
      period: periodOf(raw),
      source: sourceOf(raw),
      indicator: raw.indicator || null,
    };
  }
  return null;
}
function scalar(value, unit, period, source) {
  const number = finite(value);
  return number === null ? null : { value: number, unit, period, source };
}
function unitContains(item, token) {
  return String(item?.unit || '').toLowerCase().includes(token.toLowerCase());
}

function metricFromRecord(record, id) {
  if (!record) return null;
  const obs = observation(record, id);
  const economy = record.economy || {};
  const population = record.population || {};
  const geography = record.geography || {};
  const digital = record.digital || {};
  const environment = record.environment || record.climate || {};

  if (id === 'population') {
    return obs || scalar(population.value, 'people', population.year, population.source);
  }
  if (id === 'area') {
    return scalar(geography.land_area_km2 ?? geography.area_km2, 'km²', record.updated, geography.source || record.provenance?.source);
  }
  if (id === 'gdp') {
    if (obs && (obs.indicator === 'NY.GDP.MKTP.CD' || unitContains(obs, 'usd'))) return obs;
    if (finite(economy.gdp_current_usd) !== null) return scalar(economy.gdp_current_usd, 'current USD', economy.gdp_year, economy.source);
    if (finite(economy.gdp_current_usd_trillion) !== null) return scalar(Number(economy.gdp_current_usd_trillion) * 1e12, 'current USD', economy.gdp_year, economy.source);
    return null; // Never compare local-currency GDP values across countries.
  }
  if (id === 'gdp_per_capita') {
    if (obs && (obs.indicator === 'NY.GDP.PCAP.CD' || unitContains(obs, 'usd'))) return obs;
    return scalar(economy.gdp_per_capita_usd, 'current USD / person', economy.gdp_year, economy.source);
  }
  if (id === 'gdp_per_capita_ppp') {
    if (obs && (obs.indicator === 'NY.GDP.PCAP.PP.CD' || unitContains(obs, 'international'))) return obs;
    return scalar(economy.gdp_per_capita_ppp, 'international $ / person', economy.gdp_year, economy.source);
  }
  if (id === 'real_growth') {
    return obs || scalar(economy.gdp_growth_percent ?? economy.real_growth_percent_2025, '%', economy.gdp_year || 2025, economy.source);
  }
  if (id === 'inflation') {
    return obs || scalar(economy.inflation_percent, '%', economy.inflation_year || economy.gdp_year || record.updated, economy.source);
  }
  if (id === 'unemployment') {
    return obs || scalar(economy.unemployment_percent, '%', economy.unemployment_year || economy.gdp_year || record.updated, economy.source);
  }
  if (id === 'labour_force_participation') {
    return obs || scalar(record.labour?.participation_percent ?? economy.labour_force_participation_percent, '%', record.labour?.year || record.updated, record.labour?.source || economy.source);
  }
  if (id === 'life_expectancy') {
    return obs || scalar(population.life_expectancy, 'years', population.year || record.updated, population.source);
  }
  if (id === 'fertility') {
    return obs || scalar(population.fertility_rate, 'births / woman', population.year || record.updated, population.source);
  }
  if (id === 'urbanization') {
    return obs || scalar(population.urbanization_percent ?? record.society_and_population?.urbanization_percent, '%', population.year || record.updated, population.source);
  }
  if (id === 'poverty') {
    return obs || scalar(economy.poverty_percent ?? record.social?.poverty_percent, '%', economy.poverty_year || record.updated, economy.source || record.social?.source);
  }
  if (id === 'internet_penetration') {
    return obs || scalar(digital.internet_use_percent ?? digital.internet_penetration_percent, '%', digital.year || record.updated, digital.source);
  }
  if (id === 'co2_emissions') {
    return obs || scalar(environment.co2_per_capita ?? environment.co2_tonnes_per_capita, 't CO₂ / person', environment.year || record.updated, environment.source);
  }
  return obs;
}

async function loadAllRecords() {
  if (recordsPromise) return recordsPromise;
  recordsPromise = (async () => {
    const rows = await loadIndex();
    let cursor = 0;
    let completed = 0;
    const total = rows.length;

    async function worker() {
      while (cursor < total) {
        const row = rows[cursor++];
        let record = null;
        try { record = await fetchJson(`../data/countries/${row.id}.json`); }
        catch (error) { console.warn(`Metric record unavailable for ${row.iso3}:`, error); }
        records.set(row.iso3, record);
        completed += 1;
        window.dispatchEvent(new CustomEvent('potato-atlas-metric-progress', { detail: { completed, total, code: row.iso3 } }));
      }
    }

    const workers = Array.from({ length: Math.min(CONCURRENCY, total) }, () => worker());
    await Promise.all(workers);
    window.dispatchEvent(new CustomEvent('potato-atlas-metrics-ready', { detail: { total, loaded: [...records.values()].filter(Boolean).length } }));
    return records;
  })();
  return recordsPromise;
}

function quantile(sorted, fraction) {
  if (!sorted.length) return null;
  const index = (sorted.length - 1) * fraction;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return sorted[lower];
  const weight = index - lower;
  return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

function summarize(id, rows) {
  const values = rows.map(row => row.item?.value).filter(Number.isFinite).sort((a, b) => a - b);
  const definition = REGISTRY[id] || { label: id, unit: '', scale: 'linear' };
  const maxAbs = values.length ? Math.max(Math.abs(values[0]), Math.abs(values.at(-1))) : 0;
  return {
    id,
    label: definition.label,
    unit: definition.unit,
    scale: definition.scale,
    coverage: values.length,
    total: indexRows.length,
    min: values[0] ?? null,
    q25: quantile(values, .25),
    median: quantile(values, .5),
    q75: quantile(values, .75),
    max: values.at(-1) ?? null,
    maxAbs,
  };
}

function setMetricState(code, item) {
  try {
    map.setFeatureState({ source: 'countries', id: code }, {
      metricValue: item?.value ?? 0,
      metricHas: Boolean(item && Number.isFinite(item.value)),
      metricPeriod: item?.period == null ? '' : String(item.period),
      metricSource: item?.source || '',
    });
  } catch { /* territories or still-settling polygon sources may not expose an id */ }
}

async function prepare(id) {
  if (!REGISTRY[id]) throw new Error(`Unknown metric: ${id}`);
  if (REGISTRY[id].native) return { ...REGISTRY[id], id, native: true, coverage: null, total: null };
  if (metricCache.has(id)) {
    const cached = metricCache.get(id);
    for (const row of cached.rows) setMetricState(row.code, row.item);
    return cached.summary;
  }

  await loadAllRecords();
  const rows = indexRows.map(row => ({ code: row.iso3, item: metricFromRecord(records.get(row.iso3), id) }));
  for (const row of rows) setMetricState(row.code, row.item);
  const summary = summarize(id, rows);
  metricCache.set(id, { rows, summary });
  return summary;
}

function forCountry(code, id) {
  code = String(code || '').toUpperCase();
  if (!REGISTRY[id]) return null;
  if (REGISTRY[id].native) return null;
  const cached = metricCache.get(id);
  return cached?.rows.find(row => row.code === code)?.item || metricFromRecord(records.get(code), id);
}

function formatValue(value, id) {
  const number = finite(value);
  if (number === null) return '—';
  if (id === 'gdp') return new Intl.NumberFormat('en', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 2 }).format(number);
  if (id === 'gdp_per_capita' || id === 'gdp_per_capita_ppp') return `$${new Intl.NumberFormat('en', { maximumFractionDigits: 0 }).format(number)}`;
  if (['real_growth','inflation','unemployment','labour_force_participation','urbanization','poverty','internet_penetration'].includes(id)) return `${new Intl.NumberFormat('en', { maximumFractionDigits: 1 }).format(number)}%`;
  if (id === 'life_expectancy') return `${new Intl.NumberFormat('en', { maximumFractionDigits: 1 }).format(number)} yr`;
  if (id === 'fertility') return new Intl.NumberFormat('en', { maximumFractionDigits: 2 }).format(number);
  if (id === 'co2_emissions') return `${new Intl.NumberFormat('en', { maximumFractionDigits: 2 }).format(number)} t`;
  return new Intl.NumberFormat('en', { notation: Math.abs(number) >= 1e6 ? 'compact' : 'standard', maximumFractionDigits: 2 }).format(number);
}

await loadIndex();

window.__potatoAtlasMetrics = {
  registry: REGISTRY,
  prepare,
  forCountry,
  formatValue,
  get loadedRecords() { return records.size; },
  get totalCountries() { return indexRows.length; },
};
