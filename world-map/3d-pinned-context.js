// Compact retained-country context rail.
// One active country keeps the deep inspector; pins stay visible as lightweight context.

const selection = window.__potatoAtlasSelection;
const layout = window.__potatoAtlasUILayout;
if (!selection || !layout) throw new Error('Pinned context requires selection and UI layout APIs.');

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));

let rail = null;
let renderSerial = 0;
let staleSuppressions = 0;
let expanded = false;

function ensureRail() {
  if (rail) return rail;
  const style = document.createElement('style');
  style.id = 'atlasPinnedContextStyle';
  style.textContent = `
    #atlasPinnedContextRail{display:flex;align-items:stretch;gap:6px;width:100%;max-width:760px;padding:6px;border:1px solid #34413f;border-radius:14px;background:#0b1212e8;box-shadow:0 8px 24px #0007;overflow-x:auto;overscroll-behavior-x:contain;scrollbar-width:thin}
    #atlasPinnedContextRail[hidden]{display:none!important}
    .atlas-pinned-card{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:3px 8px;min-width:150px;max-width:210px;padding:7px 9px;border:1px solid #2f3c3a;border-radius:10px;background:#101918;flex:0 0 auto;text-align:left}
    .atlas-pinned-card.active{border-color:#e0bd78;background:#171c18}
    .atlas-pinned-main{min-width:0;border:0;background:transparent;padding:0;text-align:left;cursor:pointer}
    .atlas-pinned-name{display:block;font-size:11px;font-weight:650;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .atlas-pinned-value{display:block;margin-top:3px;font-size:10px;color:#c6d0cc;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .atlas-pinned-population{display:block;margin-top:2px;font-size:9px;color:#aebbb5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .atlas-pinned-meta{display:block;margin-top:2px;font-size:9px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .atlas-pinned-remove{align-self:start;border:0;background:transparent;color:#9fa9a4;padding:0 2px;font-size:14px;cursor:pointer}
    .atlas-pinned-overflow{display:flex;align-items:center;justify-content:center;min-width:76px;padding:7px 9px;border:1px dashed #3a4745;border-radius:10px;color:var(--muted);font-size:10px;flex:0 0 auto;background:#0f1716;cursor:pointer}
    .atlas-pinned-overflow:hover{color:#d7dfdc;border-color:#556563}
    @media(max-width:900px){#atlasPinnedContextRail{max-width:none}.atlas-pinned-card{min-width:138px;max-width:180px;padding:6px 8px}.atlas-pinned-meta{display:none}}
  `;
  document.head.appendChild(style);
  rail = document.createElement('div');
  rail.id = 'atlasPinnedContextRail';
  rail.hidden = true;
  rail.setAttribute('aria-label', 'Pinned country context');
  rail.addEventListener('click', event => {
    const remove = event.target.closest('[data-unpin]');
    if (remove) { selection.unpin?.(remove.dataset.unpin); return; }
    const activate = event.target.closest('[data-activate]');
    if (activate) { selection.activate?.(activate.dataset.activate); return; }
    if (event.target.closest('[data-show-all]')) { expanded = true; void refresh('expand'); return; }
    if (event.target.closest('[data-collapse]')) { expanded = false; void refresh('collapse'); }
  });
  document.querySelector('.mapwrap')?.appendChild(rail);
  layout.register({ id:'pinned-context', zone:'bottom-context', element:rail, priority:20, mode:'context' });
  window.__potatoAtlasPinnedContext = {
    refresh,
    expand() { expanded = true; return refresh('expand-api'); },
    collapse() { expanded = false; return refresh('collapse-api'); },
    get expanded() { return expanded; },
    get element() { return rail; },
  };
  window.dispatchEvent(new CustomEvent('potato-atlas-pinned-context-ready', { detail:{ id:rail.id } }));
  return rail;
}

function activeViewApi() {
  return window.__potatoAtlasActiveView?.forCountry ? window.__potatoAtlasActiveView : null;
}

function cardMeta(view) {
  if (!view) return '';
  if (view.period) return String(view.period);
  if (view.memberships?.memberships?.length) {
    const hits = view.memberships.memberships.filter(item => item.member).map(item => item.label);
    return hits.slice(0,2).join(' · ');
  }
  return view.relationMode && view.relationMode !== 'all' ? `${view.relationMode} connections` : '';
}

function formatPopulation(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { notation:'compact', maximumFractionDigits:1 }).format(number);
}

async function populationObservation(code) {
  try { return await window.__potatoAtlasDataRuntime?.populationObservation?.(code) || null; }
  catch { return null; }
}

async function resolveView(api, code) {
  const [view, population] = await Promise.all([
    api ? api.forCountry(code).catch(() => null) : Promise.resolve(null),
    populationObservation(code),
  ]);
  const fallbackPopulation = window.__potatoAtlasDemography?.countries?.[code]?.population?.value;
  return { code, view, population:population?.value ?? fallbackPopulation ?? null, populationPeriod:population?.period || '' };
}

async function refresh(reason = 'refresh') {
  const node = ensureRail();
  const serial = ++renderSerial;
  const snapshot = selection.current || {};
  const pins = [...(snapshot.pinnedCodes || snapshot.selectedCodes || [])];
  const context = window.__potatoAtlasContextVisibility?.current;
  const budget = Math.max(0, Number(context?.budgets?.pinnedCards ?? 4));
  if (!pins.length || !context?.visibility?.showPinnedContext || budget === 0) {
    expanded = false;
    node.hidden = true;
    node.innerHTML = '';
    layout.setVisible?.('pinned-context', false);
    if (window.__potatoAtlasDiagnostics) window.__potatoAtlasDiagnostics.pinnedContextCards = 0;
    return;
  }

  if (pins.length <= budget) expanded = false;
  const api = activeViewApi();
  const visiblePins = expanded ? pins : pins.slice(0, budget);
  const rows = await Promise.all(visiblePins.map(code => resolveView(api, code)));
  if (serial !== renderSerial) {
    staleSuppressions += 1;
    if (window.__potatoAtlasDiagnostics) window.__potatoAtlasDiagnostics.pinnedContextStaleSuppressions = staleSuppressions;
    return;
  }

  const hiddenCount = Math.max(0, pins.length - visiblePins.length);
  const overflow = hiddenCount > 0
    ? `<button type="button" class="atlas-pinned-overflow" data-show-all aria-label="Show ${hiddenCount} more pinned countries">+${hiddenCount} more</button>`
    : expanded && pins.length > budget
      ? '<button type="button" class="atlas-pinned-overflow" data-collapse aria-label="Collapse pinned country context">Collapse</button>'
      : '';

  node.innerHTML = rows.map(({code, view, population, populationPeriod}) => {
    const active = code === snapshot.activeCode;
    const name = selection.countryName?.(code) || code;
    const value = view?.display || (view?.memberships?.memberships?.length ? `${view.memberships.memberships.filter(item => item.member).length} matching sets` : api ? 'Context available' : 'Loading context…');
    const meta = cardMeta(view);
    const populationLabel = `Population · ${formatPopulation(population)}${populationPeriod ? ` (${populationPeriod})` : ''}`;
    return `<article class="atlas-pinned-card${active ? ' active' : ''}" data-country="${esc(code)}"><button type="button" class="atlas-pinned-main" data-activate="${esc(code)}" aria-label="Inspect ${esc(name)}"><span class="atlas-pinned-name">${esc(name)}</span><span class="atlas-pinned-value">${esc(value)}</span><span class="atlas-pinned-population">${esc(populationLabel)}</span>${meta ? `<span class="atlas-pinned-meta">${esc(meta)}</span>` : ''}</button><button type="button" class="atlas-pinned-remove" data-unpin="${esc(code)}" aria-label="Unpin ${esc(name)}">×</button></article>`;
  }).join('') + overflow;
  node.hidden = false;
  layout.setVisible?.('pinned-context', true);
  layout.refresh?.();
  document.getElementById('atlasWorkingSelection')?.setAttribute('hidden', '');
  if (window.__potatoAtlasDiagnostics) {
    window.__potatoAtlasDiagnostics.pinnedContextCards = rows.length;
    window.__potatoAtlasDiagnostics.pinnedContextTotalPins = pins.length;
    window.__potatoAtlasDiagnostics.pinnedContextOverflow = hiddenCount;
    window.__potatoAtlasDiagnostics.pinnedContextExpanded = expanded;
    window.__potatoAtlasDiagnostics.pinnedContextStaleSuppressions = staleSuppressions;
  }
}

for (const eventName of [
  'potato-atlas-pin-change',
  'potato-atlas-working-selection-change',
  'potato-atlas-layer-change',
  'potato-atlas-composition-change',
  'potato-atlas-relation-mode-change',
  'potato-atlas-context-visibility-change',
  'potato-atlas-active-view-change',
  'potato-atlas-module-ready',
  'atlas-time-change',
]) window.addEventListener(eventName, () => queueMicrotask(() => refresh(eventName)));

ensureRail();
await refresh('ready');
