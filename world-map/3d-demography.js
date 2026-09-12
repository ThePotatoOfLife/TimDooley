// Sourced demography enhancement for the World Relational Atlas.
// Population labels are entity-owned: population and placement resolve through the
// same ISO3/map entity rather than mixing a population dataset with REST latlng.

const DEMOGRAPHY_URL = '../data/world-country-demography.json';
const RUNTIME_URL = '../data/world-map-data-runtime.json';
const GEOMETRY_URL = '../data/world-countries.geo.json';
const RELIGION_LABELS = {
  christian: 'Christian', muslim: 'Muslim', hindu: 'Hindu', buddhist: 'Buddhist',
  jewish: 'Jewish', other_religions: 'Other religions', unaffiliated: 'Unaffiliated'
};
const RELIGION_CLASSES = {
  christian: 'religion-christian', muslim: 'religion-muslim', hindu: 'religion-hindu', buddhist: 'religion-buddhist',
  jewish: 'religion-jewish', other_religions: 'religion-other', unaffiliated: 'religion-unaffiliated'
};

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));
const formatPopulation = value => {
  const n = Number(value);
  return Number.isFinite(n) ? new Intl.NumberFormat('en').format(Math.round(n)) : '—';
};
const compactPopulation = value => {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  if (n >= 1e9) return `${(n / 1e9).toFixed(n >= 10e9 ? 0 : 1)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(n >= 10e6 ? 0 : 1)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(n >= 10e3 ? 0 : 1)}K`;
  return String(Math.round(n));
};
const pct = value => {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return `${n < 0.1 && n > 0 ? '<0.1' : n.toFixed(n >= 10 ? 0 : 1)}%`;
};

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}
function waitForMap(timeoutMs = 12000) {
  return new Promise((resolve, reject) => {
    const started = Date.now();
    const tick = () => {
      if (window.__potatoAtlasMap) return resolve(window.__potatoAtlasMap);
      if (Date.now() - started > timeoutMs) return reject(new Error('Atlas map instance unavailable'));
      setTimeout(tick, 60);
    };
    tick();
  });
}

function religionRows(religion) {
  const composition = religion?.composition || {};
  const rows = Object.entries(composition).filter(([, value]) => Number.isFinite(Number(value))).sort((a, b) => Number(b[1]) - Number(a[1]));
  if (!rows.length) return '';
  return rows.map(([key, value]) => {
    const width = Math.max(0, Math.min(100, Number(value)));
    return `<div class="religion-row"><div class="religion-line"><span>${esc(RELIGION_LABELS[key] || key)}</span><b>${pct(value)}</b></div><div class="religion-track"><span class="religion-fill ${esc(RELIGION_CLASSES[key] || 'religion-other')}" style="width:${width}%"></span></div></div>`;
  }).join('');
}
function religionCard(code, row, compact = false) {
  const religion = row?.religion;
  if (!religion?.composition || !Object.keys(religion.composition).length) return '';
  const note = religion.classification_note || 'Unaffiliated is a religious-identity category, not a claim about belief or practice.';
  return `<div class="card atlas-demography-card" data-demography-code="${esc(code)}"><div class="demography-heading"><b>Religious composition · ${esc(religion.year || 2020)}</b><span class="pill">Pew / OWID</span></div>${religionRows(religion)}${compact ? '' : `<p class="muted demography-note">${esc(note)}</p><div class="muted demography-source">Source: ${esc(religion.source || 'Pew Research Center / Our World in Data')}</div>`}</div>`;
}
function enhanceCountryPanel(panel, code, row) {
  if (!row) return;
  const existing = panel.querySelector(`.atlas-demography-card[data-demography-code="${CSS.escape(code)}"]`);
  const population = row.population;
  if (population?.value != null) {
    for (const metric of panel.querySelectorAll('.metric')) {
      const label = metric.querySelector('span')?.textContent?.trim().toLowerCase();
      if (label === 'population') {
        const value = metric.querySelector('b');
        if (value && value.textContent !== formatPopulation(population.value)) value.textContent = formatPopulation(population.value);
        if (!metric.querySelector('.demography-pop-source')) {
          const meta = document.createElement('small');
          meta.className = 'muted demography-pop-source';
          meta.textContent = `${population.year || population.reference_date || 'latest'} · ${population.source || 'sourced'}`;
          metric.appendChild(meta);
        }
      }
    }
  }
  if (!existing && row.religion) {
    const grid = panel.querySelector('.grid');
    const holder = document.createElement('div');
    holder.innerHTML = religionCard(code, row);
    const card = holder.firstElementChild;
    if (card) {
      if (grid?.parentNode) grid.parentNode.insertBefore(card, grid.nextSibling);
      else panel.appendChild(card);
    }
  }
}
function enhanceReligionModule(panel, code, row) {
  if (!row?.religion || panel.querySelector(`.atlas-demography-card[data-demography-code="${CSS.escape(code)}"]`)) return;
  const holder = document.createElement('div');
  holder.innerHTML = religionCard(code, row);
  if (holder.firstElementChild) panel.insertBefore(holder.firstElementChild, panel.querySelector('.boundary')?.nextSibling || null);
}
function enhanceComparePanel(panel, data) {
  const url = new URL(location.href);
  const codes = (url.searchParams.get('compare') || '').split(',').map(x => x.trim().toUpperCase()).filter(Boolean).slice(0, 4);
  if (!codes.length || panel.querySelector('.atlas-demography-compare')) return;
  const populated = codes.map(code => [code, data.countries?.[code]]).filter(([, row]) => row?.religion);
  if (!populated.length) return;
  const block = document.createElement('div');
  block.className = 'atlas-demography-compare';
  block.innerHTML = `<h2>Religious composition</h2><p class="muted">2020 identity composition. Percentages are estimates and categories are mutually exclusive.</p>${populated.map(([code, row]) => `<div class="demography-compare-country"><b>${esc(row.name || code)}</b>${religionCard(code, row, true)}</div>`).join('')}`;
  const boundary = panel.querySelector('.boundary');
  if (boundary) panel.insertBefore(block, boundary); else panel.appendChild(block);
}
function currentCode() {
  const code = (new URL(location.href).searchParams.get('country') || '').toUpperCase();
  return /^[A-Z]{3}$/.test(code) ? code : null;
}
function enhancePanel(data) {
  const panel = document.querySelector('#panel');
  if (!panel) return;
  if (/Compare mode/i.test(panel.querySelector('.eyebrow')?.textContent || '')) return enhanceComparePanel(panel, data);
  const code = currentCode();
  if (!code) return;
  const row = data.countries?.[code] || data.entities?.[code];
  if (!row) return;
  if (/Religion \/ Irreligion/i.test(panel.querySelector('h1')?.textContent || '')) enhanceReligionModule(panel, code, row);
  else enhanceCountryPanel(panel, code, row);
}

function ringArea(ring) {
  if (!Array.isArray(ring) || ring.length < 3) return 0;
  let area = 0;
  for (let i = 0; i < ring.length; i += 1) {
    const a = ring[i], b = ring[(i + 1) % ring.length];
    area += Number(a?.[0] || 0) * Number(b?.[1] || 0) - Number(b?.[0] || 0) * Number(a?.[1] || 0);
  }
  return Math.abs(area / 2);
}
function polygonCentroid(ring) {
  let area2 = 0, cx = 0, cy = 0;
  for (let i = 0; i < ring.length; i += 1) {
    const a = ring[i], b = ring[(i + 1) % ring.length];
    const cross = Number(a?.[0] || 0) * Number(b?.[1] || 0) - Number(b?.[0] || 0) * Number(a?.[1] || 0);
    area2 += cross; cx += (Number(a?.[0] || 0) + Number(b?.[0] || 0)) * cross; cy += (Number(a?.[1] || 0) + Number(b?.[1] || 0)) * cross;
  }
  if (Math.abs(area2) < 1e-9) return null;
  return [cx / (3 * area2), cy / (3 * area2)];
}
function pointInRing(point, ring) {
  if (!point || !Array.isArray(ring)) return false;
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = Number(ring[i]?.[0]), yi = Number(ring[i]?.[1]), xj = Number(ring[j]?.[0]), yj = Number(ring[j]?.[1]);
    const intersects = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / ((yj - yi) || 1e-12) + xi);
    if (intersects) inside = !inside;
  }
  return inside;
}
function geometryAnchor(feature) {
  const geometry = feature?.geometry;
  const polygons = geometry?.type === 'Polygon' ? [geometry.coordinates] : geometry?.type === 'MultiPolygon' ? geometry.coordinates : [];
  const candidates = polygons.map(poly => poly?.[0]).filter(ring => Array.isArray(ring) && ring.length >= 3).map(ring => ({ring, area:ringArea(ring)}));
  if (!candidates.length) return null;
  const ring = candidates.sort((a, b) => b.area - a.area)[0].ring;
  const centroid = polygonCentroid(ring);
  if (centroid && pointInRing(centroid, ring)) return centroid;
  const fallback = ring[Math.floor(ring.length / 2)];
  return Array.isArray(fallback) ? [Number(fallback[0]), Number(fallback[1])] : null;
}

async function addPopulationLabels(map, data) {
  const [geometry, runtime] = await Promise.all([getJson(GEOMETRY_URL), getJson(RUNTIME_URL).catch(() => ({entities:{by_id:{}}}))]);
  const featureByCode = new Map((geometry.features || []).map(feature => [String(feature.id || feature.properties?.iso3 || '').toUpperCase(), feature]));
  const features = [];
  const codes = new Set([...Object.keys(data.countries || {}), ...Object.keys(runtime?.entities?.territories || {})]);
  for (const code of codes) {
    const countryRow = data.countries?.[code];
    const entity = runtime?.entities?.by_id?.[code];
    const population = countryRow?.population || entity?.population;
    if (!population?.value) continue;
    const explicit = entity?.label_anchor?.coordinates;
    const mapFeature = featureByCode.get(code);
    const anchor = Array.isArray(explicit) && explicit.length === 2 ? explicit : geometryAnchor(mapFeature);
    if (!Array.isArray(anchor) || anchor.length !== 2 || !anchor.every(Number.isFinite)) continue;
    features.push({
      type:'Feature',
      properties:{
        iso3:code,
        name:countryRow?.name || entity?.name || mapFeature?.properties?.name || code,
        population:Number(population.value),
        population_label:compactPopulation(population.value),
        population_year:String(population.year || population.reference_date || ''),
        anchor_kind:Array.isArray(explicit) ? (entity?.label_anchor?.kind || 'population-label-anchor') : 'population-label-anchor'
      },
      geometry:{type:'Point',coordinates:[Number(anchor[0]),Number(anchor[1])]}
    });
  }
  const sourceData = {type:'FeatureCollection',features};
  if (map.getSource('country-population-labels')) map.getSource('country-population-labels').setData(sourceData);
  else {
    map.addSource('country-population-labels',{type:'geojson',data:sourceData});
    map.addLayer({id:'country-population-labels',type:'symbol',source:'country-population-labels',minzoom:3.2,layout:{'text-field':['get','population_label'],'text-size':['interpolate',['linear'],['zoom'],3.2,9,6,12],'text-offset':[0,2.35],'text-allow-overlap':false},paint:{'text-color':'#dfe8dc','text-halo-color':'#080b0b','text-halo-width':1.2,'text-opacity':0.82}});
  }
}

async function boot() {
  let data;
  try { data = await getJson(DEMOGRAPHY_URL); }
  catch (error) { console.warn('Atlas demography snapshot unavailable; core atlas continues.', error); return; }
  window.__potatoAtlasDemography = data;
  const panel = document.querySelector('#panel');
  if (panel) {
    let scheduled = false;
    const observer = new MutationObserver(() => {
      if (scheduled) return;
      scheduled = true;
      queueMicrotask(() => { scheduled = false; enhancePanel(data); });
    });
    observer.observe(panel,{childList:true,subtree:true});
    enhancePanel(data);
  }
  try {
    const map = await waitForMap();
    const ready = () => addPopulationLabels(map,data).catch(error => console.warn('Population label layer failed.', error));
    if (map.loaded()) ready(); else map.once('load',ready);
  } catch (error) { console.warn('Demography map enhancement skipped.', error); }
}

boot();
