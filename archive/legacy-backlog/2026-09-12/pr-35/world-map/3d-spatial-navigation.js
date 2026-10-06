// Spatial semantic navigation for the 3D World Relational Atlas.
//
// The map teaches where things live: World on the left, Relations on the right,
// Time along the bottom, Axis above. Domain modules register meaning through the
// capability registry; this controller never owns empirical/project data itself.

const capabilities = window.__potatoAtlasCapabilities;
const mapwrap = document.querySelector('.mapwrap');
const handles = {
  world: document.getElementById('atlasWorldZone'),
  relations: document.getElementById('atlasRelationsZone'),
  time: document.getElementById('atlasTimeZone'),
  axis: document.getElementById('atlasAxisZone'),
};
const panels = {
  world: document.getElementById('atlasWorldDrawer'),
  relations: document.getElementById('atlasRelationsDrawer'),
  time: document.getElementById('atlasTimeZonePanel'),
  axis: document.getElementById('atlasAxisZonePanel'),
};
const settingsTrigger = document.getElementById('atlasSettingsTrigger');
const settingsPanel = document.getElementById('atlasSettingsPanel');
const resetButton = document.getElementById('atlasReset');

if (!capabilities || !mapwrap) throw new Error('Spatial navigation requires the capability registry and map shell.');

const ZONE_COPY = {
  world: {
    title: 'World',
    question: 'What is there?',
    empty: 'Opening World loads place, society, economy, infrastructure, energy, faith and technology surfaces as they become available.',
  },
  relations: {
    title: 'Relations',
    question: 'What connects it?',
    empty: 'Opening Relations loads connections, institutions, flows and network tools as they become available.',
  },
  time: {
    title: 'Time',
    question: 'How did it change?',
    empty: 'Time becomes richer when the active data has dated observations, thresholds or comparable historical states.',
  },
  axis: {
    title: 'Axis',
    question: 'How are we interpreting it?',
    empty: 'Axis lenses apply project and analytical operators over World, Relations and Time without replacing their underlying facts.',
  },
};

const FAMILY_CLASS = {
  world: 'family-world',
  people: 'family-people',
  economy: 'family-economy',
  infrastructure: 'family-infrastructure',
  energy: 'family-energy',
  relations: 'family-relations',
  faith: 'family-faith',
  time: 'family-time',
  evidence: 'family-evidence',
  axis: 'family-axis',
  technology: 'family-infrastructure',
};

let openZoneName = null;
let lastFocusedHandle = null;

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
}[char]));

function availability(descriptor) {
  return capabilities.availabilityFor(descriptor.id, { source:'spatial-navigation' });
}

function descriptorsFor(zone) {
  return capabilities.list({ zone }).sort((a, b) =>
    (a.order ?? 999) - (b.order ?? 999) || a.category.localeCompare(b.category) || a.name.localeCompare(b.name)
  );
}

function grouped(zone) {
  const groups = new Map();
  for (const descriptor of descriptorsFor(zone)) {
    if (!groups.has(descriptor.category)) groups.set(descriptor.category, []);
    groups.get(descriptor.category).push(descriptor);
  }
  return groups;
}

function stateActive(descriptor) {
  const state = capabilities.getActiveState();
  return state.capabilities.some(item => item.id === descriptor.id);
}

function itemButton(descriptor) {
  const status = availability(descriptor);
  const active = stateActive(descriptor);
  const family = FAMILY_CLASS[descriptor.colorFamily] || `family-${descriptor.colorFamily || 'world'}`;
  const disabled = status.available === false;
  return `<button class="atlas-capability ${family}${active ? ' active' : ''}" data-capability-id="${esc(descriptor.id)}" ${disabled ? 'disabled' : ''} aria-pressed="${active ? 'true' : 'false'}">
    <span class="atlas-capability-dot" aria-hidden="true"></span>
    <span class="atlas-capability-copy"><b>${esc(descriptor.name)}</b><small>${esc(disabled ? status.reason || 'Unavailable' : descriptor.description)}</small></span>
  </button>`;
}

function renderZone(zone) {
  const panel = panels[zone];
  if (!panel) return;
  const copy = ZONE_COPY[zone];
  const groups = grouped(zone);
  const body = groups.size
    ? [...groups.entries()].map(([category, items]) => `
        <section class="atlas-zone-group">
          <h3>${esc(category)}</h3>
          <div class="atlas-zone-items">${items.map(itemButton).join('')}</div>
        </section>`).join('')
    : `<div class="atlas-zone-empty"><b>${esc(copy.question)}</b><p>${esc(copy.empty)}</p><span>Capabilities appear here as their lazy modules load.</span></div>`;

  panel.innerHTML = `<div class="atlas-zone-head">
      <div><span>${esc(copy.question)}</span><h2>${esc(copy.title)}</h2></div>
      <button class="atlas-zone-close" data-close-zone="${esc(zone)}" aria-label="Close ${esc(copy.title)}">×</button>
    </div>${body}`;
}

async function activateCapability(id) {
  const descriptor = capabilities.get(id);
  if (!descriptor) return;
  const active = stateActive(descriptor);
  const result = active
    ? await capabilities.deactivate(id, { source:'spatial-navigation' })
    : await capabilities.activate(id, { source:'spatial-navigation' });
  if (!result.ok) {
    window.dispatchEvent(new CustomEvent('potato-atlas-status-request', {
      detail:{ message:result.reason || `${descriptor.name} unavailable`, kind:'error' },
    }));
  }
  renderZone(descriptor.zone);
}

function setExpanded(handle, open) {
  handle?.setAttribute('aria-expanded', String(Boolean(open)));
  handle?.classList.toggle('active', Boolean(open));
}

function closeZone(zone = openZoneName, { restoreFocus = true } = {}) {
  if (!zone) return;
  const panel = panels[zone];
  if (panel) panel.hidden = true;
  setExpanded(handles[zone], false);
  if (openZoneName === zone) openZoneName = null;
  document.body.classList.remove(`atlas-zone-open-${zone}`);
  window.dispatchEvent(new CustomEvent('potato-atlas-zone-close', { detail:{ zone } }));
  if (restoreFocus) (lastFocusedHandle || handles[zone])?.focus?.();
}

function closeAll({ restoreFocus = false } = {}) {
  for (const zone of Object.keys(panels)) {
    const panel = panels[zone];
    if (panel) panel.hidden = true;
    setExpanded(handles[zone], false);
    document.body.classList.remove(`atlas-zone-open-${zone}`);
  }
  openZoneName = null;
  if (settingsPanel) settingsPanel.hidden = true;
  settingsTrigger?.setAttribute('aria-expanded', 'false');
  if (restoreFocus) lastFocusedHandle?.focus?.();
}

function openZone(zone) {
  if (!panels[zone] || !handles[zone]) return;
  if (openZoneName === zone && !panels[zone].hidden) {
    closeZone(zone);
    return;
  }
  closeAll({ restoreFocus:false });
  openZoneName = zone;
  lastFocusedHandle = handles[zone];
  renderZone(zone);
  panels[zone].hidden = false;
  setExpanded(handles[zone], true);
  document.body.classList.add(`atlas-zone-open-${zone}`);
  window.dispatchEvent(new CustomEvent('potato-atlas-zone-open', { detail:{ zone } }));
}

function getOpenZone() {
  return openZoneName;
}

function openSettings() {
  if (!settingsPanel) return;
  const opening = settingsPanel.hidden;
  closeAll({ restoreFocus:false });
  settingsPanel.hidden = !opening;
  settingsTrigger?.setAttribute('aria-expanded', String(opening));
  if (opening) {
    settingsPanel.innerHTML = `<div class="atlas-zone-head"><div><span>Display & utilities</span><h2>Settings</h2></div><button class="atlas-zone-close" data-close-settings aria-label="Close Settings">×</button></div>
      <div class="atlas-zone-empty"><b>Advanced display controls live here.</b><p>Tilt, globe, basemap, focus mode, explicit hop limit and semantic module orbit are being migrated here without changing their underlying renderer contracts.</p></div>`;
  }
}

for (const [zone, handle] of Object.entries(handles)) {
  handle?.setAttribute('aria-expanded', 'false');
  handle?.addEventListener('click', () => openZone(zone));
}

for (const panel of Object.values(panels)) {
  panel?.addEventListener('click', event => {
    const close = event.target.closest('[data-close-zone]');
    if (close) {
      closeZone(close.dataset.closeZone);
      return;
    }
    const item = event.target.closest('[data-capability-id]');
    if (item) activateCapability(item.dataset.capabilityId);
  });
}

settingsTrigger?.addEventListener('click', openSettings);
settingsPanel?.addEventListener('click', event => {
  if (event.target.closest('[data-close-settings]')) {
    settingsPanel.hidden = true;
    settingsTrigger?.setAttribute('aria-expanded', 'false');
    settingsTrigger?.focus();
  }
});

resetButton?.addEventListener('click', () => {
  window.__potatoAtlasActiveState?.clearAll?.();
  window.clearCountrySelection?.();
  window.__potatoAtlasUI?.setPanel?.(false, { persist:false });
  closeAll();
});

window.addEventListener('potato-atlas-capability-registry-change', () => {
  if (openZoneName) renderZone(openZoneName);
});
window.addEventListener('potato-atlas-capability-change', event => {
  const zone = event.detail?.descriptor?.zone;
  if (zone && zone === openZoneName) renderZone(zone);
});

document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  if (!settingsPanel?.hidden) {
    settingsPanel.hidden = true;
    settingsTrigger?.setAttribute('aria-expanded', 'false');
    settingsTrigger?.focus();
    event.stopPropagation();
    return;
  }
  if (openZoneName) {
    closeZone(openZoneName);
    event.stopPropagation();
  }
}, true);

window.__potatoAtlasSpatialUI = {
  openZone,
  closeZone,
  closeAll,
  renderZone,
  getOpenZone,
};
