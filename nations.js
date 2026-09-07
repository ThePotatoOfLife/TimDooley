const API = 'https://restcountries.com/v3.1/all?fields=name,cca2,cca3,capital,region,subregion,flag,landlocked,area,population,languages,currencies';
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

let canonical = [];
let liveByIso3 = new Map();

function countryHref(country) {
  return `nation.html?id=${encodeURIComponent(country.id)}&iso3=${encodeURIComponent(country.iso3 || '')}`;
}

function render() {
  const term = $('q').value.trim().toLowerCase();
  const region = $('region').value;
  const subregion = $('sub').value;

  const shown = canonical.filter(country => {
    const live = liveByIso3.get(String(country.iso3 || '').toUpperCase());
    const languages = Object.values(live?.languages || {}).join(' ');
    const haystack = [country.name, country.capital, country.iso2, country.iso3, country.region, country.subregion, languages].join(' ').toLowerCase();
    return (!term || haystack.includes(term)) && (!region || country.region === region) && (!subregion || country.subregion === subregion);
  });

  $('shown').textContent = shown.length;
  $('status').textContent = liveByIso3.size
    ? `${shown.length} of ${canonical.length} canonical countries shown · ${liveByIso3.size} live matches`
    : `${shown.length} of ${canonical.length} canonical countries shown · live enrichment unavailable`;

  $('list').innerHTML = shown.map(country => {
    const live = liveByIso3.get(String(country.iso3 || '').toUpperCase());
    const name = live?.name?.common || country.name;
    const official = live?.name?.official || country.name;
    const capital = live?.capital?.[0] || country.capital || '—';
    const regionName = live?.region || country.region || '—';
    const iso3 = live?.cca3 || country.iso3 || '—';
    const population = live?.population ? Number(live.population).toLocaleString() : '—';
    return `<a class="nation-row" href="${countryHref(country)}">
      <div><strong>${esc(name)}</strong><small>${esc(official)}</small></div>
      <span>${esc(capital)} · ${esc(regionName)}</span>
      <span>${esc(iso3)}</span>
      <span>${population}</span>
      <span>${esc(country.status || 'State')}</span>
    </a>`;
  }).join('') || '<p class="empty-state">No countries match this search.</p>';
}

function populateFilters() {
  const regions = [...new Set(canonical.map(c => c.region).filter(Boolean))].sort();
  const subregions = [...new Set(canonical.map(c => c.subregion).filter(Boolean))].sort();
  $('region').innerHTML = '<option value="">All regions</option>' + regions.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
  $('sub').innerHTML = '<option value="">All subregions</option>' + subregions.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
}

async function init() {
  try {
    const response = await fetch('data/nations.json', {cache:'no-store'});
    if (!response.ok) throw new Error(`Canonical nation data returned HTTP ${response.status}`);
    const data = await response.json();
    canonical = Array.isArray(data.nations) ? data.nations : [];
    if (!canonical.length) throw new Error('Canonical nation directory is empty');

    $('total').textContent = canonical.length;
    $('loaded').textContent = '—';
    $('shown').textContent = canonical.length;
    populateFilters();
    render();

    try {
      const liveResponse = await fetch(API, {cache:'no-store'});
      if (!liveResponse.ok) throw new Error(`REST Countries returned HTTP ${liveResponse.status}`);
      const live = await liveResponse.json();
      liveByIso3 = new Map(live.filter(c => c?.cca3).map(c => [String(c.cca3).toUpperCase(), c]));
      $('loaded').textContent = liveByIso3.size;
      render();
    } catch (error) {
      $('loaded').textContent = '0';
      $('status').textContent = `Canonical directory loaded. Live enrichment unavailable: ${error.message}`;
      render();
    }
  } catch (error) {
    $('status').innerHTML = `<span class="error">World directory could not be loaded: ${esc(error.message)}</span>`;
    $('list').innerHTML = '<p class="empty-state">The canonical country file is unavailable. Open Atlas Health to inspect the project.</p>';
  }
}

$('q').addEventListener('input', render);
$('region').addEventListener('change', render);
$('sub').addEventListener('change', render);
init();
