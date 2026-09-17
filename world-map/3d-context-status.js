// Compact orientation surface for the current World Map question.
// Shows derived context only; it owns no map/domain state.

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

function ensureNode() {
  if (node) return node;
  const style = document.createElement('style');
  style.id = 'atlasContextStatusStyle';
  style.textContent = `
    #atlasContextStatus{display:flex;align-items:center;gap:5px;max-width:100%;padding:5px 8px;border:1px solid #33413f;border-radius:999px;background:#0b1212e8;box-shadow:0 5px 16px #0005;color:#c7d0cd;font-size:10px;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    #atlasContextStatus .atlas-context-status-label{color:var(--muted)}
    #atlasContextStatus .atlas-context-status-sep{color:#66726f}
    #atlasContextStatus[data-mode="evidence"]{border-color:#6f775a}
    #atlasContextStatus[data-mode="connections"]{border-color:#486978}
    #atlasContextStatus[data-mode="compare"]{border-color:#6d617e}
    @media(max-width:900px){#atlasContextStatus{max-width:220px;padding:4px 7px;font-size:9px}}
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

function render() {
  const target = ensureNode();
  const context = window.__potatoAtlasContextVisibility?.current;
  if (!context) {
    target.innerHTML = '<span class="atlas-context-status-label">Current view</span><span>Loading…</span>';
    return;
  }
  const mode = context.question?.investigation || 'browse';
  const pinnedCountries = context.pinnedCountries || [];
  const parts = [
    LABELS[mode] || mode,
    LABELS[context.scaleBand] || context.scaleBand,
  ].filter(Boolean);
  if (pinnedCountries.length) parts.push(`${pinnedCountries.length} pin${pinnedCountries.length === 1 ? '' : 's'}`);
  const time = timeLabel(context.time);
  if (time) parts.push(time);
  if (context.question?.relationMode && context.question.relationMode !== 'all') parts.push(context.question.relationMode);

  target.dataset.mode = mode;
  target.innerHTML = `<span class="atlas-context-status-label">Current view</span>${parts.map(part => `<span class="atlas-context-status-sep">·</span><span>${String(part).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]))}</span>`).join('')}`;
  target.title = `Current view: ${parts.join(' · ')}`;
  if (window.__potatoAtlasDiagnostics) window.__potatoAtlasDiagnostics.contextStatus = { mode, scaleBand:context.scaleBand, pins:pinnedCountries.length, time:context.time?.mode || 'current' };
}

for (const eventName of [
  'potato-atlas-context-visibility-change',
  'potato-atlas-working-selection-change',
  'potato-atlas-pin-change',
  'potato-atlas-investigation-change',
  'atlas-time-change',
]) window.addEventListener(eventName, () => queueMicrotask(render));

ensureNode();
render();
window.__potatoAtlasContextStatus = { refresh:render, get element() { return node; } };
