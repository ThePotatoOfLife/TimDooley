// Compact orientation surface for the current World Map question.
// Shows derived context only; it owns no map/domain state. Hover is an ephemeral
// presentation subject; canonical selection, pins, layers and investigation state
// remain owned by their existing subsystems.

const layout = window.__potatoAtlasUILayout;
if (!layout) throw new Error('Context status requires UI Layout.');

const LABELS = {
  browse:'Browse',
  compare:'Compare',
  connections:'Connections',
  evidence:'Evidence',
  world:'World',
  'macro-region':'Macro-region',
  region:'Region',
  country:'Country',
  subnational:'Subnational',
  local:'Local',
};

let node = null;
let renderGeneration = 0;
let renderScheduled = false;
let lastHoverKey = null;

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[ch]));

function ensureNode() {
  if (node) return node;
  const style = document.createElement('style');
  style.id = 'atlasContextStatusStyle';
  style.textContent = `
    #atlasContextStatus{display:flex;align-items:center;gap:5px;max-width:min(760px,calc(100% - 20px));padding:6px 9px;border:1px solid #33413f;border-radius:12px;background:#0b1212e8;box-shadow:0 5px 16px #0005;color:#c7d0cd;font-size:10px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;backdrop-filter:blur(10px)}
    #atlasContextStatus .atlas-context-status-label{color:var(--muted)}
    #atlasContextStatus .atlas-context-status-country{color:#eef3ef;font-weight:650}
    #atlasContextStatus .atlas-context-status-population{color:#d8e3dc}
    #atlasContextStatus .atlas-context-status-answer{color:#f0dfaa;min-width:0;overflow:hidden;text-overflow:ellipsis}
    #atlasContextStatus .atlas-context-status-selected-ref{color:#a9b6b0;min-width:0;overflow:hidden;text-overflow:ellipsis}
    #atlasContextStatus .atlas-context-status-meta{color:#86938d;min-width:0;overflow:hidden;text-overflow:ellipsis}
    #atlasContextStatus .atlas-context-status-sep{color:#66726f}
    #atlasContextStatus[data-subject="preview"]{border-color:#557b76}
    #atlasContextStatus[data-subject="selected"]{border-color:#596963}
    #atlasContextStatus[data-mode="evidence"]{border-color:#6f775a}
    #atlasContextStatus[data-mode="connections"]{border-color:#486978}
    #atlasContextStatus[data-mode="compare"]{border-color:#6d617e}
    @media(max-width:900px){#atlasContextStatus{max-width:min(92vw,540px);padding:5px 8px;font-size:9px}.atlas-context-status-meta{display:none}}
  `;
  document.head.appendChild(style);
  node = document.createElement('div');
  node.id = 'atlasContextStatus';
  node.setAttribute('role', 'status');
  node.setAttribute('aria-live', 'polite');
  node.innerHTML = '<span class="atlas-context-status-label">Current view</span>';
  document.querySelector('.mapwrap')?.appendChild(node);
  layout.register({ id:'context-status', zone:'left-status', element:node, priority:10, mode:'context' });
  return node;
}

function timeLabel(time = {}) {
  if (time.mode === 'as_of' && time.time) return `As of ${time.time}`;
  if (time.mode === 'changed_between' && time.time && time.time2) return `${time.time} → ${time.time2}`;
  return '';
}

function countryCode(feature) {
  const properties = feature?.properties || {};
  const code = properties.iso3 || properties.cca3 || properties.ISO_A3 || properties.code || feature?.id || properties.id || '';
  return /^[A-Za-z]{3}$/.test(String(code)) ? String(code).toUpperCase() : '';
}

function selectedCountryCode() {
  const selection = window.__potatoAtlasSelection;
  const code = selection?.current?.activeCode || selection?.current?.code || '';
  return /^[A-Za-z]{3}$/.test(String(code)) ? String(code).toUpperCase() : '';
}

function subject() {
  const hover = window.__potatoAtlasInteraction?.currentHover?.();
  const hoverCode = hover?.objectType === 'country' ? countryCode(hover.feature) : '';
  if (hoverCode) {
    const properties = hover.feature?.properties || {};
    return { kind:'preview', label:'Preview', code:hoverCode, fallbackName:properties.name || properties.NAME || properties.ADMIN || hoverCode };
  }
  const selectedCode = selectedCountryCode();
  if (selectedCode) return { kind:'selected', label:'Selected', code:selectedCode, fallbackName:selectedCode };
  return null;
}

function selectedReference(details) {
  if (details?.kind !== 'preview') return null;
  const code = selectedCountryCode();
  if (!code || code === details.code) return null;
  const selection = window.__potatoAtlasSelection;
  return { code, name:selection?.countryName?.(code) || code };
}

function formatPopulation(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { notation:'compact', maximumFractionDigits:1 }).format(number);
}

function activeViewAnswer(view) {
  if (!view || view.status === 'neutral') return '';
  if (view.scalar) {
    const label = view.scalar.label || 'Map value';
    const display = view.display || 'Unknown';
    const detail = [view.period, view.source].filter(Boolean).join(' · ');
    return `${label}: ${display}${detail ? ` · ${detail}` : ''}`;
  }
  const memberships = view.memberships?.memberships || [];
  if (memberships.length) {
    const match = view.memberships.matches ? 'Matches' : 'Outside';
    const labels = memberships.slice(0, 3).map(item => `${item.label}: ${item.member ? 'yes' : 'no'}`).join(' · ');
    return `${match}${labels ? ` · ${labels}` : ''}`;
  }
  return '';
}

function contextParts(context) {
  if (!context) return [];
  const mode = context.question?.investigation || 'browse';
  const pinnedCountries = context.pinnedCountries || [];
  const parts = [LABELS[mode] || mode, LABELS[context.scaleBand] || context.scaleBand].filter(Boolean);
  if (pinnedCountries.length) parts.push(`${pinnedCountries.length} pin${pinnedCountries.length === 1 ? '' : 's'}`);
  const time = timeLabel(context.time);
  if (time) parts.push(time);
  if (context.question?.relationMode && context.question.relationMode !== 'all') parts.push(context.question.relationMode);
  return parts;
}

async function subjectDetails(currentSubject) {
  if (!currentSubject) return null;
  const code = currentSubject.code;
  const selection = window.__potatoAtlasSelection;
  const runtime = window.__potatoAtlasDataRuntime;
  const activeView = window.__potatoAtlasActiveView;
  const [populationCell, view] = await Promise.all([
    runtime?.populationObservation?.(code) || null,
    activeView?.forCountry?.(code) || null,
  ]);
  const fallbackPopulation = window.__potatoAtlasDemography?.countries?.[code]?.population?.value;
  return {
    ...currentSubject,
    name:selection?.countryName?.(code) || currentSubject.fallbackName || code,
    population:populationCell?.value ?? fallbackPopulation ?? null,
    populationPeriod:populationCell?.period || window.__potatoAtlasDemography?.countries?.[code]?.population?.year || '',
    view,
  };
}

async function render() {
  const generation = ++renderGeneration;
  const target = ensureNode();
  const context = window.__potatoAtlasContextVisibility?.current;
  const currentSubject = subject();
  const details = await subjectDetails(currentSubject);
  if (generation !== renderGeneration) return;

  const mode = context?.question?.investigation || 'browse';
  const parts = contextParts(context);
  target.dataset.mode = mode;

  if (details) {
    target.dataset.subject = details.kind;
    const populationPeriod = details.populationPeriod ? ` (${esc(details.populationPeriod)})` : '';
    const answer = activeViewAnswer(details.view);
    const selected = selectedReference(details);
    const selectedHtml = selected ? `<span class="atlas-context-status-sep">·</span><span class="atlas-context-status-selected-ref">Selected · ${esc(selected.name)}</span>` : '';
    target.innerHTML = `<span class="atlas-context-status-label">${esc(details.label)}</span><span class="atlas-context-status-country">${esc(details.name)}</span><span class="atlas-context-status-sep">·</span><span class="atlas-context-status-population">Population · ${esc(formatPopulation(details.population))}${populationPeriod}</span>${answer ? `<span class="atlas-context-status-sep">·</span><span class="atlas-context-status-answer">${esc(answer)}</span>` : ''}${selectedHtml}${parts.length ? `<span class="atlas-context-status-sep">·</span><span class="atlas-context-status-meta">Current view · ${esc(parts.join(' · '))}</span>` : ''}`;
    target.title = `${details.label}: ${details.name} · Population ${formatPopulation(details.population)}${answer ? ` · ${answer}` : ''}${selected ? ` · Selected: ${selected.name}` : ''}${parts.length ? ` · Current view: ${parts.join(' · ')}` : ''}`;
  } else {
    delete target.dataset.subject;
    if (!context) {
      target.innerHTML = '<span class="atlas-context-status-label">Current view</span><span>Loading…</span>';
      target.title = 'Current view loading';
    } else {
      target.innerHTML = `<span class="atlas-context-status-label">Current view</span>${parts.map(part => `<span class="atlas-context-status-sep">·</span><span>${esc(part)}</span>`).join('')}`;
      target.title = `Current view: ${parts.join(' · ')}`;
    }
  }

  if (window.__potatoAtlasDiagnostics) {
    window.__potatoAtlasDiagnostics.contextStatus = {
      mode,
      scaleBand:context?.scaleBand || '',
      pins:context?.pinnedCountries?.length || 0,
      time:context?.time?.mode || 'current',
      subject:details ? { kind:details.kind, code:details.code } : null,
      selectedReference:details ? selectedReference(details)?.code || null : null,
    };
  }
}

function scheduleRender() {
  if (renderScheduled) return;
  renderScheduled = true;
  queueMicrotask(() => {
    renderScheduled = false;
    void render();
  });
}

for (const eventName of [
  'potato-atlas-context-visibility-change',
  'potato-atlas-working-selection-change',
  'potato-atlas-pin-change',
  'potato-atlas-investigation-change',
  'potato-atlas-active-view-change',
  'atlas-time-change',
]) window.addEventListener(eventName, scheduleRender);

window.addEventListener('potato-atlas-interaction-state', () => {
  const hoverKey = window.__potatoAtlasInteraction?.currentHover?.()?.key || '';
  if (hoverKey === lastHoverKey) return;
  lastHoverKey = hoverKey;
  scheduleRender();
});

ensureNode();
void render();
window.__potatoAtlasContextStatus = { refresh:render, get element() { return node; } };
