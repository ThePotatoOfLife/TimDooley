const DATA_URL = '../data/axis-operators.json';
const FORMAL_URL = '../data/axis-formal-lenses.json';
const FLOW_URL = '../data/axis-flow-contract.json';
const HUD_ID = 'axisOperatorHud';
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const ATLAS_VERSION = new URL(import.meta.url).searchParams.get('v') || '';
let provenancePromise = null;
let symbolicPromise = null;

function versionedModule(path) {
  if (!ATLAS_VERSION) return path;
  const url = new URL(path, import.meta.url);
  url.searchParams.set('v', ATLAS_VERSION);
  return url.href;
}

function dimensionFromUrl() {
  const url = new URL(location.href);
  return Number(url.searchParams.get('axisD') || 4);
}

function ensureHud() {
  let hud = document.getElementById(HUD_ID);
  if (hud) return hud;
  const wrap = document.querySelector('.mapwrap');
  if (!wrap) return null;
  hud = document.createElement('div');
  hud.id = HUD_ID;
  hud.style.cssText = 'position:absolute;left:12px;top:78px;z-index:3;width:min(420px,calc(100% - 190px));background:#080b0be6;border:1px solid #304040;border-radius:10px;padding:9px 11px;backdrop-filter:blur(7px);box-shadow:0 6px 24px rgba(0,0,0,.22);font-size:11px;line-height:1.35;pointer-events:none';
  wrap.appendChild(hud);
  return hud;
}

function flowSummary(flow, dimension) {
  const f = flow?.dimensions?.[String(dimension)] || null;
  if (!f) return '';
  const inflow = (f.inflow || []).slice(0,4).join(' · ');
  const outflow = (f.outflow || []).slice(0,4).join(' · ');
  return `<div style="margin-top:6px;border-top:1px solid #2f3c3c;padding-top:5px;color:#b8c8c3">
    <div style="display:flex;justify-content:space-between;gap:8px"><b style="color:#d7e7dc">Flow · ${esc(f.flow_behavior || '')}</b><span style="color:#9fb4ae;font-size:9px;text-transform:uppercase;letter-spacing:.08em">${esc(f.polarity || '')}</span></div>
    ${inflow ? `<div><span style="color:#98aaa4">↘ In:</span> ${esc(inflow)}</div>` : ''}
    ${outflow ? `<div><span style="color:#b8d6bf">↗ Out:</span> ${esc(outflow)}</div>` : ''}
    ${f.risk ? `<div style="color:#a8a09a"><b>Risk:</b> ${esc(f.risk)}</div>` : ''}
    <small style="color:#718181">Project-symbolic Axis flow · empirical quantities keep their own units, dates and sources</small>
  </div>`;
}

function render(data, formal, flow, dimension) {
  const hud = ensureHud();
  if (!hud) return;
  const d = data.dimensions?.[String(dimension)] || data.dimensions?.['4'];
  const lens = formal?.dimensions?.[String(dimension)] || null;
  if (!d) return;
  const inputs = (d.inputs || []).slice(0,4).join(' · ');
  const outputs = (d.outputs || []).slice(0,4).join(' · ');
  const content = (d.content_types || []).slice(0,4).join(' · ');
  const neighbors = (lens?.formal_neighbors || []).slice(0,3).join(' · ');
  hud.innerHTML = `
    <div style="display:flex;justify-content:space-between;gap:10px;align-items:baseline"><b style="color:#dff8ff">${esc(d.label)}</b><span style="color:#9fe8ff;text-transform:uppercase;letter-spacing:.1em;font-size:9px">${esc(d.operator)}</span></div>
    <div style="color:#aab4aa;margin-top:4px"><b style="color:#d6dfdf">Input:</b> ${esc(inputs)}</div>
    <div style="color:#aab4aa"><b style="color:#d6dfdf">→ Output:</b> ${esc(outputs)}</div>
    <div style="color:#aab4aa"><b style="color:#d6dfdf">Belongs here:</b> ${esc(content)}</div>
    <div style="margin-top:5px;border-top:1px solid #263232;padding-top:5px;color:#c8d0d0"><b>Test:</b> ${esc(d.diagnostic_test)}</div>
    ${flowSummary(flow, dimension)}
    ${lens ? `<div style="margin-top:6px;border-top:1px dashed #314343;padding-top:5px;color:#aebcbc"><b style="color:#bdd9de">Formal lens:</b> ${esc(lens.label)}<br><span>${esc(lens.question)}</span>${neighbors ? `<br><small style="color:#879797">Neighbors · ${esc(neighbors)}</small>` : ''}<br><small style="color:#718181">Comparator/project formalism · not physical proof of the D-layer</small></div>` : ''}`;

  if (dimension === 4) hud.style.borderColor = '#3b4a44';
  else if (dimension >= 5) hud.style.borderColor = '#477987';
  else hud.style.borderColor = '#5b4d3e';
}

function ensureProvenance() {
  if (!provenancePromise) {
    provenancePromise = import(versionedModule('./3d-provenance.js'))
      .catch(error => { console.warn('D3 provenance enhancement unavailable:', error); return null; });
  }
  return provenancePromise;
}

function ensureSymbolicOperators() {
  if (!symbolicPromise) {
    symbolicPromise = import(versionedModule('./3d-symbolic-operators.js'))
      .catch(error => { console.warn('Executable symbolic operators unavailable:', error); return null; });
  }
  return symbolicPromise;
}

async function boot() {
  const [operatorResponse, formalResponse, flowResponse] = await Promise.all([fetch(DATA_URL), fetch(FORMAL_URL), fetch(FLOW_URL)]);
  if (!operatorResponse.ok) throw new Error('Axis operator model unavailable');
  const data = await operatorResponse.json();
  const formal = formalResponse.ok ? await formalResponse.json() : null;
  const flow = flowResponse.ok ? await flowResponse.json() : null;
  render(data, formal, flow, dimensionFromUrl());
  window.addEventListener('atlas-axis-dimension-change', event => {
    const dimension = Number(event.detail?.dimension || 4);
    render(data, formal, flow, dimension);
    // The deeper tooling is not part of map startup. It becomes relevant only
    // after the user actually navigates the symbolic Axis away from Earth.
    if (dimension !== 4) ensureSymbolicOperators();
    if (dimension === 3) ensureProvenance();
  });
  window.__potatoAxisOperators = {data, formal, flow, render, ensureProvenance, ensureSymbolicOperators};
}

boot().catch(error => console.warn('Axis operator HUD unavailable:', error));
