const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
let canonical = [];

function countryHref(country) {
  return `nation.html?id=${encodeURIComponent(country.id)}&iso3=${encodeURIComponent(country.iso3 || '')}`;
}

function render() {
  const term = $('q').value.trim().toLowerCase();
  const region = $('region').value;
  const subregion = $('sub').value;
  const shown = canonical.filter(country => {
    const haystack = [country.name, country.capital, country.iso2, country.iso3, country.region, country.subregion, country.status].join(' ').toLowerCase();
    return (!term || haystack.includes(term)) && (!region || country.region === region) && (!subregion || country.subregion === subregion);
  });
  $('shown').textContent = shown.length;
  $('status').textContent = `${shown.length} of ${canonical.length} canonical countries shown · repository data`;
  $('list').innerHTML = shown.map(country => `<a class="nation-row" href="${countryHref(country)}">
    <div><strong>${esc(country.name)}</strong><small>${esc(country.name)}</small></div>
    <span>${esc(country.capital || 'Capital not yet sourced')} · ${esc(country.region || 'Region not yet sourced')}</span>
    <span>${esc(country.iso3 || '—')}</span>
    <span>${esc(country.subregion || '—')}</span>
    <span>${esc(country.status || 'State')}</span>
  </a>`).join('') || '<p class="empty-state">No countries match this search.</p>';
}

function populateFilters() {
  const regions = [...new Set(canonical.map(c => c.region).filter(Boolean))].sort();
  const subregions = [...new Set(canonical.map(c => c.subregion).filter(Boolean))].sort();
  $('region').innerHTML = '<option value="">All regions</option>' + regions.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
  $('sub').innerHTML = '<option value="">All subregions</option>' + subregions.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
}

async function init() {
  try {
    const indexResponse = await fetch('data/countries/index.json');
    if (!indexResponse.ok) throw new Error(`Canonical country index returned HTTP ${indexResponse.status}`);
    const index = await indexResponse.json();
    const snapshotResponse = await fetch('data/country-static.json');
    const snapshot = snapshotResponse.ok ? await snapshotResponse.json() : {countries: []};
    const snapshotById = new Map((snapshot.countries || []).map(c => [c.id, c]));
    canonical = (index.countries || []).map(c => ({...c, ...(snapshotById.get(c.id) || {})}));
    if (!canonical.length) throw new Error('Canonical country index is empty');
    $('total').textContent = canonical.length;
    $('loaded').textContent = canonical.length;
    populateFilters();
    render();
  } catch (error) {
    $('status').innerHTML = `<span class="error">World directory could not be loaded: ${esc(error.message)}</span>`;
    $('list').innerHTML = '<p class="empty-state">The canonical country index is unavailable. Open Atlas Health to inspect the project.</p>';
  }
}

$('q').addEventListener('input', render);
$('region').addEventListener('change', render);
$('sub').addEventListener('change', render);
init();
