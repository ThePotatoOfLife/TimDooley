// Minimal country hover for ordinary World Map browsing.
// Hover identifies a temporary subject and answers the current map question; it
// never mutates selection, pins, URL, relations, camera or inspector state.

const interaction = window.__potatoAtlasInteraction;
const presentation = window.__potatoAtlasCountryPresentation;
const tooltip = window.__potatoAtlasTooltip;
if (!interaction || !presentation || !tooltip) {
  throw new Error('Country hover presentation requires Interaction Router, Country Presentation and Tooltip.');
}

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));

let hoverKey = '';
let hoverEvent = null;
let hoverHtml = '';
let hoverGeneration = null;

function codeFromFeature(feature) {
  const properties = feature?.properties || {};
  const code = properties.iso3 || properties.cca3 || properties.ISO_A3 || properties.code || feature?.id || properties.id || '';
  return /^[A-Za-z]{3}$/.test(String(code)) ? String(code).toUpperCase() : '';
}

function fallbackName(feature, code) {
  const properties = feature?.properties || {};
  return properties.name || properties.NAME || properties.ADMIN || code || 'Country';
}

function answerLine(row) {
  const answer = row?.answer;
  if (!answer || answer.kind === 'none' || answer.populationPrimary) return '';
  if (answer.kind === 'scalar') {
    return `<div class="atlas-hover-answer">${esc(answer.label)} · ${esc(answer.display || 'Unknown')}</div>`;
  }
  if (answer.kind === 'set') {
    const memberships = answer.memberships?.memberships || row?.memberships?.memberships || [];
    const detail = memberships.slice(0, 3).map(item => `${item.label} ${item.member ? 'yes' : 'no'}`).join(' · ');
    return `<div class="atlas-hover-answer">${esc(answer.display || 'Outside')}${detail ? ` · ${esc(detail)}` : ''}</div>`;
  }
  return '';
}

function relationLine(row) {
  if (row?.answer?.kind !== 'none') return '';
  const mode = row?.relation?.mode || 'all';
  if (mode === 'all') return '';
  const label = mode.charAt(0).toUpperCase() + mode.slice(1);
  return `<div class="atlas-hover-answer">${esc(label)} · ${Number(row?.relation?.count || 0)} represented connections</div>`;
}

function htmlFor(row, feature, code) {
  const name = row?.identity?.name || fallbackName(feature, code);
  const population = row?.population?.display || '—';
  return `<div class="atlas-hover atlas-hover-country-minimal"><b>${esc(name)}</b>${answerLine(row)}${relationLine(row)}<div>Population · ${esc(population)}</div></div>`;
}

async function renderHover(event, feature) {
  const code = codeFromFeature(feature);
  if (!code) return;
  hoverEvent = event;
  if (code === hoverKey && hoverHtml && hoverGeneration != null) {
    tooltip.show('country', hoverEvent.lngLat, hoverHtml, hoverGeneration);
    return;
  }
  hoverKey = code;
  hoverHtml = '';
  hoverGeneration = tooltip.nextGeneration('country');
  const expectedGeneration = hoverGeneration;
  const row = await presentation.forCountry(code).catch(() => null);
  if (hoverKey !== code || !hoverEvent || expectedGeneration !== hoverGeneration) return;
  hoverHtml = htmlFor(row, feature, code);
  tooltip.show('country', hoverEvent.lngLat, hoverHtml, expectedGeneration);
}

function clearHover() {
  hoverKey = '';
  hoverEvent = null;
  hoverHtml = '';
  hoverGeneration = null;
  tooltip.invalidate('country-leave');
}

interaction.unregister('country-hover');
interaction.register('country-hover-presentation', {
  layers:['countries-fill', 'countries-extrude'],
  objectType:'country',
  clickPriority:0,
  hoverPriority:20,
  claimOverlay:false,
  onHover:(event, feature) => { void renderHover(event, feature); },
  onLeave:clearHover,
});

window.__potatoAtlasCountryHoverPresentation = Object.freeze({ clear:hoverKey ? clearHover : clearHover });
