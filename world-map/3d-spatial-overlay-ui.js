// UI for independent sacred/textual/current spatial overlays.
// Installs inside the existing Layers menu so the World Map keeps one stable shell.

const spatial = window.__potatoAtlasSpatialOverlays;
if (!spatial) throw new Error('Spatial overlay UI requires the spatial overlay runtime.');
await spatial.ready;

const app = document.querySelector('#atlasApp');
const panel = document.querySelector('#panel');
const layersMenu = document.querySelector('#layersMenu .menu-pop');
const GROUP_ORDER = [
  'sacred.father-land',
  'sacred.chosen-children-land',
  'current.israel-palestine',
  'conflict.context',
];
const GROUP_LABELS = {
  'sacred.father-land':'Father’s Land / Eden',
  'sacred.chosen-children-land':'Chosen Children’s Land',
  'current.israel-palestine':'Israel / Palestine',
  'conflict.context':'Conflict context',
};
const EPISTEMIC_LABEL = {
  current_observed:'Current observed',
  current_disputed:'Current / disputed',
  historical_reconstruction:'Historical reconstruction',
  textual_reconstruction:'Textual reconstruction',
  political_ideology:'Political ideology',
  project_interpretive:'Project interpretive',
  event_observed:'Observed event context',
  humanitarian_observed:'Humanitarian observed',
};

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function title(value) {
  return String(value || '').replaceAll('_',' ').replace(/\b\w/g, letter => letter.toUpperCase());
}

let host = document.querySelector('#atlasSpatialOverlayHost');
if (!host && layersMenu) {
  const divider = document.createElement('div');
  divider.className = 'menu-sep';
  layersMenu.appendChild(divider);
  host = document.createElement('section');
  host.id = 'atlasSpatialOverlayHost';
  host.setAttribute('aria-label','Sacred and territorial overlays');
  layersMenu.appendChild(host);
}

const style = document.createElement('style');
style.textContent = `
#atlasSpatialOverlayHost{border-top:1px solid #283333;margin-top:8px;padding-top:7px}
#atlasSpatialOverlayHost .spatial-group{margin:7px 0 10px}
#atlasSpatialOverlayHost .spatial-group-title{font-size:9px;text-transform:uppercase;letter-spacing:.12em;color:#aab4aa;margin:3px 2px 5px}
#atlasSpatialOverlayHost .spatial-toggle{display:flex;align-items:flex-start;gap:7px;width:100%;text-align:left;margin:3px 0;padding:6px 7px}
#atlasSpatialOverlayHost .spatial-toggle span{display:block;min-width:0}
#atlasSpatialOverlayHost .spatial-toggle small{display:block;color:#aab4aa;font-size:9px;line-height:1.25;margin-top:2px}
#atlasSpatialOverlayHost .spatial-toggle[disabled]{opacity:.48;cursor:not-allowed}
#atlasSpatialOverlayHost .spatial-status{font-size:9px;color:#aab4aa;margin:5px 2px}
#atlasBoundaryView{width:100%;margin-top:4px}
.atlas-spatial-overlap .spatial-overlap-card{border:1px solid #344343;border-radius:9px;padding:9px;margin:7px 0;background:#151d1d}
.atlas-spatial-overlap .spatial-overlap-card h3{font:400 17px Georgia,serif;margin:2px 0 5px}
.atlas-spatial-overlap .spatial-source{font-size:10px;color:#aab4aa;overflow-wrap:anywhere}
`;
document.head.appendChild(style);

function persistBoundaryView(value) {
  const url = new URL(location.href);
  if (value && value !== 'atlas') url.searchParams.set('boundaryView', value);
  else url.searchParams.delete('boundaryView');
  history.replaceState({},'',url);
  window.dispatchEvent(new CustomEvent('potato-atlas-boundary-view-change',{detail:{value}}));
}

function activeBoundaryView() {
  const value = new URL(location.href).searchParams.get('boundaryView') || 'atlas';
  return ['atlas','iso','israel','palestine'].includes(value) ? value : 'atlas';
}

function renderControls() {
  if (!host) return;
  const rows = spatial.entries();
  const groups = GROUP_ORDER.map(family => ({ family, rows:rows.filter(row => row.family === family) })).filter(group => group.rows.length);
  host.innerHTML = `<div class="menu-title">Sacred / territorial overlays</div>${groups.map(group => `
    <div class="spatial-group" data-family="${esc(group.family)}">
      <div class="spatial-group-title">${esc(GROUP_LABELS[group.family] || group.family)}</div>
      ${group.rows.map(row => {
        const current = row.availability === 'current';
        const active = spatial.isActive(row.id);
        return `<button class="spatial-toggle${active?' active':''}" data-spatial-overlay="${esc(row.id)}" ${current?'':'disabled'} title="${esc(row.status_note || '')}">
          <span>${active?'✓ ':'}${esc(row.label)}<small>${esc(EPISTEMIC_LABEL[row.epistemic_type] || title(row.epistemic_type))}${current?'':' · planned'}</small></span>
        </button>`;
      }).join('')}
    </div>`).join('')}
    <div class="spatial-group">
      <div class="spatial-group-title">Boundary view</div>
      <select id="atlasBoundaryView" title="Boundary rendering contract">
        <option value="atlas">Atlas / de-facto base</option>
        <option value="iso" disabled>ISO / international coding · source pending</option>
        <option value="israel" disabled>Israel viewpoint · source pending</option>
        <option value="palestine" disabled>Palestine viewpoint · source pending</option>
      </select>
      <div class="spatial-status">Boundary view changes cartographic rendering only. It never changes canonical country identity, theology or project records.</div>
    </div>
    <div class="spatial-status">Overlays may cross borders and overlap each other by design. Their meanings stay independent.</div>`;

  const boundary = host.querySelector('#atlasBoundaryView');
  if (boundary) {
    boundary.value = activeBoundaryView();
    boundary.onchange = event => persistBoundaryView(event.target.value);
  }
  for (const button of host.querySelectorAll('[data-spatial-overlay]')) {
    button.onclick = async () => {
      const id = button.dataset.spatialOverlay;
      await spatial.toggle(id);
      renderControls();
    };
  }
}

function openInspector(features) {
  if (!panel || !features?.length) return;
  if (app) app.classList.remove('panel-collapsed');
  const overlap = features.length > 1;
  panel.innerHTML = `<div class="atlas-spatial-overlap">
    <div class="eyebrow">Spatial overlays · ${features.length} active match${features.length===1?'':'es'}</div>
    <h1>${overlap?'Overlapping geographies':esc(features[0].label)}</h1>
    <p class="muted">${overlap?'These layers occupy the same map location but remain different kinds of claim. Nothing is merged into a new border.':'This feature belongs to an independent map overlay.'}</p>
    ${features.map(feature => {
      const row = feature.overlay || {};
      return `<article class="spatial-overlap-card">
        <div class="eyebrow">${esc(EPISTEMIC_LABEL[feature.epistemic_type] || title(feature.epistemic_type))}</div>
        <h3>${esc(feature.label)}</h3>
        <div><span class="pill">${esc(feature.confidence || 'unknown confidence')}</span><span class="pill">${esc(feature.geometry_version || 'geometry')}</span></div>
        <p>${esc(feature.status_note || row.status_note || '')}</p>
        <div class="spatial-source">Overlay: ${esc(feature.overlay_id)}<br>Feature: ${esc(feature.feature_id)}<br>Sources: ${esc((feature.source_ids || []).join(' · ') || 'source metadata pending')}<br>Measurement policy: ${esc(feature.measurement_policy || 'not specified')}</div>
        <div class="actions"><button data-fit-overlay="${esc(feature.overlay_id)}">Fit overlay</button></div>
      </article>`;
    }).join('')}
    <div class="boundary">Current sovereignty, disputed status, historical reconstruction, scripture and Potatoverse sacred geography never share an unlabeled visual meaning.</div>
  </div>`;
  for (const button of panel.querySelectorAll('[data-fit-overlay]')) button.onclick = () => spatial.fit(button.dataset.fitOverlay);
}

window.addEventListener('potato-atlas-spatial-overlay-change', event => {
  if (event.detail?.reason === 'feature-click' && event.detail.features?.length) openInspector(event.detail.features);
  renderControls();
});

renderControls();
window.__potatoAtlasSpatialOverlayUI = { render:renderControls, inspect:openInspector };
