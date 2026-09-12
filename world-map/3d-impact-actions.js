// Contextual entry points for dependency impact tracing.
// Keeps Impact out of the permanent World Bar and reuses existing surfaces.
const map = window.__potatoAtlasMap;
const trace = window.__potatoAtlasImpactTrace;
const selection = window.__potatoAtlasSelection;
if (!map || !trace) throw new Error('Impact actions require the loaded Impact Trace runtime.');

function countEnhancement() {
  const diagnostics = window.__potatoAtlasDiagnostics;
  if (diagnostics) diagnostics.cardEnhancementPasses = (diagnostics.cardEnhancementPasses || 0) + 1;
}
function syncCountryAction() {
  const card = document.getElementById('atlasCountryCard');
  if (!card || card.hidden) return;
  const actions = card.querySelector('.atlas-country-actions');
  if (!actions) return;
  const code = String(selection?.current?.activeCode || selection?.current?.code || '').toUpperCase();
  if (!/^[A-Z]{3}$/.test(code)) return;
  // The browse-first card now has a native Impact action. Keep legacy injection
  // only for older/custom card surfaces that do not expose it themselves.
  if (actions.querySelector('[data-country-action="impact"]')) return;
  let button = actions.querySelector('[data-impact-entity]');
  if (!button) {
    button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Impact';
    button.title = 'Trace represented dependency impact';
    actions.appendChild(button);
  }
  button.dataset.impactEntity = code;
}

function syncEntityFallbackAction() {
  const card = document.getElementById('atlasCountryCard');
  if (!card || card.hidden || card.querySelector('[data-impact-entity]') || card.querySelector('[data-country-action="impact"]')) return;
  const code = String(selection?.current?.activeCode || selection?.current?.code || '').toUpperCase();
  if (!/^[A-Z]{3}$/.test(code)) return;
  const entitySection = card.querySelector('#atlasEntityContext');
  if (!entitySection) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'atlas-country-tag';
  button.dataset.impactEntity = code;
  button.title = 'Trace represented dependency impact';
  button.textContent = 'Impact';
  entitySection.appendChild(button);
}

function syncChainAction(event = null) {
  const node = document.getElementById('atlasChainContext');
  if (!node) return;
  const id = event?.detail?.id || window.__potatoAtlasChainExplorer?.get?.();
  if (!id) return;
  let button = node.querySelector('[data-impact-chain]');
  if (!button) {
    button = document.createElement('button');
    button.type = 'button';
    button.title = 'Trace represented dependency impact';
    button.textContent = 'Impact';
    button.style.cssText = 'margin-top:6px;padding:3px 7px;border:1px solid #465754;border-radius:999px;background:transparent;color:#b8c4be;cursor:pointer;font-size:9px';
    node.appendChild(button);
  }
  button.dataset.impactChain = id;
}

function injectGatewayAction(event) {
  const feature = event.features?.[0];
  const id = feature?.properties?.id;
  if (!id) return;
  queueMicrotask(() => {
    const popups = [...document.querySelectorAll('.maplibregl-popup-content')];
    const content = popups.at(-1);
    if (!content || content.querySelector('[data-impact-gateway]')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.impactGateway = id;
    button.textContent = 'Impact';
    button.title = 'Trace represented dependency impact';
    button.style.cssText = 'margin-top:5px;padding:3px 7px;border:1px solid #465754;border-radius:999px;background:#111817;color:#c7d2cc;cursor:pointer;font-size:10px';
    content.appendChild(button);
  });
}

function refreshCardActions() {
  countEnhancement();
  syncCountryAction();
  syncEntityFallbackAction();
}

window.addEventListener('potato-atlas-country-card-rendered', () => queueMicrotask(refreshCardActions));
window.addEventListener('potato-atlas-working-selection-change', () => queueMicrotask(refreshCardActions));
window.addEventListener('potato-atlas-chain-change', event => queueMicrotask(() => syncChainAction(event)));
if (map.getLayer('atlas-context-gateways-points')) map.on('click', 'atlas-context-gateways-points', injectGatewayAction);

refreshCardActions();
syncChainAction();

window.__potatoAtlasImpactActions = { syncCountryAction, syncChainAction };