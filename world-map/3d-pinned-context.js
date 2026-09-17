// Compact retained-country context rail.
// Pins are lightweight comparison subjects and consume the same Country Presentation
// adapter as hover and the selected-country card.

const selection = window.__potatoAtlasSelection;
const layout = window.__potatoAtlasUILayout;
const presentation = window.__potatoAtlasCountryPresentation;
if (!selection || !layout || !presentation) throw new Error('Pinned context requires selection, UI layout and Country Presentation APIs.');

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
    #atlasPinnedContextRail[hidden]{display:none!important}.atlas-pinned-card{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:3px 8px;min-width:150px;max-width:220px;padding:7px 9px;border:1px solid #2f3c3a;border-radius:10px;background:#101918;flex:0 0 auto;text-align:left}.atlas-pinned-card.active{border-color:#e0bd78;background:#171c18}.atlas-pinned-main{min-width:0;border:0;background:transparent;padding:0;text-align:left;cursor:pointer}.atlas-pinned-name{display:block;font-size:11px;font-weight:650;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.atlas-pinned-value{display:block;margin-top:3px;font-size:10px;color:#d7d0ae;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.atlas-pinned-population{display:block;margin-top:2px;font-size:9px;color:#aebbb5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.atlas-pinned-meta{display:block;margin-top:2px;font-size:8px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.atlas-pinned-remove{align-self:start;border:0;background:transparent;color:#9fa9a4;padding:0 2px;font-size:14px;cursor:pointer}.atlas-pinned-overflow{display:flex;align-items:center;justify-content:center;min-width:76px;padding:7px 9px;border:1px dashed #3a4745;border-radius:10px;color:var(--muted);font-size:10px;flex:0 0 auto;background:#0f1716;cursor:pointer}.atlas-pinned-overflow:hover{color:#d7dfdc;border-color:#556563}@media(max-width:900px){#atlasPinnedContextRail{max-width:none}.atlas-pinned-card{min-width:138px;max-width:180px;padding:6px 8px}.atlas-pinned-meta{display:none}}
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

function answerLabel(shared) {
  const answer = shared?.answer;
  if (!answer || answer.kind === 'none' || answer.populationPrimary) return '';
  if (answer.kind === 'scalar') return `${answer.label} · ${answer.display || 'Unknown'}`;
  if (answer.kind === 'set') return `${answer.label || 'Set query'} · ${answer.display || 'Outside'}`;
  return '';
}

function cardMeta(shared) {
  const answer = shared?.answer;
  if (!answer) return '';
  if (answer.kind === 'scalar') return [answer.period, answer.source].filter(Boolean).join(' · ');
  if (answer.kind === 'set') {
    const hits = answer.memberships?.memberships?.filter(item => item.member).map(item => item.label) || [];
    return hits.slice(0, 2).join(' · ');
  }
  return '';
}

async function resolveView(code) {
  try { return await presentation.forCountry(code); }
  catch { return null; }
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
  const visiblePins = expanded ? pins : pins.slice(0, budget);
  const rows = await Promise.all(visiblePins.map(code => resolveView(code)));
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

  node.innerHTML = rows.map((shared, index) => {
    const code = visiblePins[index];
    const active = code === snapshot.activeCode;
    const name = shared?.identity?.name || selection.countryName?.(code) || code;
    const value = answerLabel(shared);
    const meta = cardMeta(shared);
    const population = shared?.population?.display || '—';
    const populationPeriod = shared?.population?.period || '';
    const populationLabel = `Population · ${population}${populationPeriod ? ` (${populationPeriod})` : ''}`;
    return `<article class="atlas-pinned-card${active ? ' active' : ''}" data-country="${esc(code)}"><button type="button" class="atlas-pinned-main" data-activate="${esc(code)}" aria-label="Inspect ${esc(name)}"><span class="atlas-pinned-name">${esc(name)}</span>${value ? `<span class="atlas-pinned-value">${esc(value)}</span>` : ''}<span class="atlas-pinned-population">${esc(populationLabel)}</span>${meta ? `<span class="atlas-pinned-meta">${esc(meta)}</span>` : ''}</button><button type="button" class="atlas-pinned-remove" data-unpin="${esc(code)}" aria-label="Unpin ${esc(name)}">×</button></article>`;
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
    window.__potatoAtlasDiagnostics.pinnedContextReason = reason;
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
