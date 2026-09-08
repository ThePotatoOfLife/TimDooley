(() => {
  'use strict';

  const DATA_URL = 'data/repository-index.json';
  const MANIFEST_URL = 'data/root-navigation.json';
  const STORAGE_KEY = 'potato-root-state-v1';

  const $ = (selector, root = document) => root.querySelector(selector);
  const escape = (value) => String(value ?? '').replace(/[&<>\"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
  const slug = (value) => String(value ?? '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

  const state = {
    manifest: null,
    records: [],
    selected: null,
    expanded: new Set(),
    rendered: new Set(),
  };

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        expanded: [...state.expanded],
        selected: state.selected,
      }));
    } catch (_) {}
  }

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      if (Array.isArray(saved.expanded)) saved.expanded.forEach(x => state.expanded.add(x));
      if (saved.selected) state.selected = saved.selected;
    } catch (_) {}
  }

  function setHash(selected) {
    const hash = selected ? `#node=${encodeURIComponent(selected)}` : '';
    history.replaceState(null, '', `${location.pathname}${location.search}${hash}`);
  }

  function readHash() {
    const params = new URLSearchParams(location.hash.replace(/^#/, ''));
    const node = params.get('node');
    return node || null;
  }

  function typeMatches(record, values) {
    return !values?.length || values.includes(String(record.type || '').toLowerCase());
  }

  function familyMatches(record, values) {
    return !values?.length || values.includes(String(record.owner_family || '').toLowerCase());
  }

  function scaleMatches(record, values) {
    return !values?.length || values.includes(String(record.repository_scale || '').toLowerCase());
  }

  function roleMatches(record, value) {
    return !value || String(record.record_role || '').toLowerCase() === value;
  }

  function textMatches(record, terms) {
    if (!terms?.length) return false;
    const haystack = [record.id, record.name, record.description, record.source, record.owner_family, record.repository_layer]
      .join(' ').toLowerCase();
    return terms.some(term => haystack.includes(String(term).toLowerCase()));
  }

  function recordKey(record) {
    return `record:${record.canonical_id || record.id}:${record.source || ''}`;
  }

  function uniqueRecords(records) {
    const seen = new Set();
    return records.filter(record => {
      const key = record.canonical_id || `${record.source}:${record.id}:${JSON.stringify(record.path || [])}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    }).sort((a, b) => String(a.name || a.id).localeCompare(String(b.name || b.id)));
  }

  function recordHref(record) {
    const id = encodeURIComponent(record.canonical_id || record.id || '');
    return `node.html?id=${id}`;
  }

  function selectRecord(record, pathLabel = '') {
    state.selected = record.canonical_id || record.id;
    setHash(state.selected);
    renderDossier(record, pathLabel);
    saveState();
  }

  function renderDossier(record, pathLabel) {
    const dossier = $('#root-dossier');
    if (!dossier) return;
    const description = record.description || 'No description is currently registered for this record.';
    const source = record.source || '';
    const sourceHref = source ? source.replace(/\\/g, '/') : '';
    const deepHref = recordHref(record);
    dossier.innerHTML = `
      <div class="dossier-head">
        <div>
          <div class="eyebrow">${escape(pathLabel || 'record')}</div>
          <h2>${escape(record.name || record.id)}</h2>
        </div>
        <button class="dossier-close" type="button" data-action="close-dossier" aria-label="Close dossier">×</button>
      </div>
      <p class="dossier-description">${escape(description)}</p>
      <dl class="dossier-meta">
        <div><dt>ID</dt><dd>${escape(record.canonical_id || record.id || '')}</dd></div>
        <div><dt>TYPE</dt><dd>${escape(record.type || 'record')}</dd></div>
        <div><dt>ROLE</dt><dd>${escape(record.record_role || 'canonical-candidate')}</dd></div>
        <div><dt>FAMILY</dt><dd>${escape(record.owner_family || 'general')}</dd></div>
        <div><dt>CLASS</dt><dd>${escape(record.repository_root || '')} / ${escape(record.repository_layer || '')} / ${escape(record.repository_scale || '')}</dd></div>
      </dl>
      <div class="dossier-actions">
        <a class="cmd" href="${escape(deepHref)}">OPEN FULL NODE</a>
        ${sourceHref ? `<a class="cmd" href="${escape(sourceHref)}">OPEN SOURCE DATA</a>` : ''}
      </div>
    `;
    dossier.hidden = false;
  }

  function closeDossier() {
    state.selected = null;
    const dossier = $('#root-dossier');
    if (dossier) dossier.hidden = true;
    setHash(null);
    saveState();
  }

  function makeRecordEntry(record, pathLabel) {
    const row = document.createElement('div');
    row.className = 'tree-entry record-entry';
    row.dataset.recordKey = recordKey(record);
    row.innerHTML = `
      <span class="tree-mark">├─</span>
      <button class="tree-button" type="button">${escape(record.name || record.id)}</button>
      <span class="tree-note">${escape(record.description || record.type || record.id || '')}</span>
    `;
    $('.tree-button', row).addEventListener('click', () => selectRecord(record, pathLabel));
    return row;
  }

  function makeLegacyEntry(collection, label = 'DOMAIN VIEW') {
    if (!collection.legacy) return null;
    const row = document.createElement('div');
    row.className = 'tree-entry legacy-entry';
    row.innerHTML = `
      <span class="tree-mark">└─</span>
      <a class="tree-button" href="${escape(collection.legacy)}">${escape(label)}</a>
      <span class="tree-note">open the existing deep view only when a full-page reading surface is useful</span>
    `;
    return row;
  }

  function filterCollection(collection) {
    if (collection.all) return state.records;
    return state.records.filter(record => {
      const type = typeMatches(record, collection.types);
      const family = familyMatches(record, collection.families);
      const scale = scaleMatches(record, collection.scales);
      const role = roleMatches(record, collection.role);
      const terms = textMatches(record, collection.terms);
      const hasTerms = Array.isArray(collection.terms) && collection.terms.length;
      const hasRules = collection.types || collection.families || collection.scales || collection.role || hasTerms;
      if (!hasRules) return false;
      if (hasTerms) return terms;
      return type && family && scale && role;
    });
  }

  function renderCollectionChildren(details, collection, branchId) {
    const key = `collection:${branchId}:${collection.id}`;
    if (state.rendered.has(key)) return;
    state.rendered.add(key);
    const children = $('.tree-children', details);
    children.innerHTML = '';
    const records = uniqueRecords(filterCollection(collection));

    if (records.length > 120) {
      const groups = new Map();
      records.forEach(record => {
        const family = record.owner_family || record.repository_layer || 'general';
        if (!groups.has(family)) groups.set(family, []);
        groups.get(family).push(record);
      });
      [...groups.entries()].sort(([a], [b]) => a.localeCompare(b)).forEach(([family, familyRecords]) => {
        const group = document.createElement('details');
        group.className = 'tree-subdir';
        group.innerHTML = `<summary><span class="tree-mark">│</span><span class="tree-name">${escape(family.toUpperCase())}/</span><span class="tree-note">${familyRecords.length} records</span></summary><div class="tree-children"></div>`;
        const inner = $('.tree-children', group);
        familyRecords.forEach(record => inner.appendChild(makeRecordEntry(record, `${branchId}/${collection.id}/${family}`)));
        children.appendChild(group);
      });
    } else {
      records.forEach(record => children.appendChild(makeRecordEntry(record, `${branchId}/${collection.id}`)));
    }

    const legacy = makeLegacyEntry(collection);
    if (legacy) children.appendChild(legacy);
    if (!children.children.length) {
      children.innerHTML = '<div class="tree-empty">no indexed records in this view</div>';
      if (legacy) children.appendChild(legacy);
    }
  }

  function makeCollectionDetails(collection, branchId) {
    const details = document.createElement('details');
    details.className = 'tree-dir tree-collection';
    const key = `collection:${branchId}:${collection.id}`;
    details.dataset.stateKey = key;
    details.innerHTML = `
      <summary>
        <span class="tree-mark">│</span>
        <span class="tree-name">${escape(collection.label)}</span>
        <span class="tree-note">${escape(collection.description || '')}</span>
        <span class="tree-count">…</span>
      </summary>
      <div class="tree-children"></div>
    `;
    details.addEventListener('toggle', () => {
      if (details.open) {
        state.expanded.add(key);
        renderCollectionChildren(details, collection, branchId);
      } else {
        state.expanded.delete(key);
      }
      saveState();
    });
    if (state.expanded.has(key)) {
      details.open = true;
      renderCollectionChildren(details, collection, branchId);
    }
    return details;
  }

  function makeBranch(branch, collections) {
    const details = document.createElement('details');
    details.className = `tree-dir tree-branch branch-${branch.kind}`;
    const key = `branch:${branch.id}`;
    details.dataset.stateKey = key;
    details.innerHTML = `
      <summary>
        <span class="tree-mark">│</span>
        <span class="tree-name">${escape(branch.label)}</span>
        <span class="tree-note">${escape(branch.description)}</span>
        <span class="tree-count">${collections.length}</span>
      </summary>
      <div class="tree-children branch-children"></div>
    `;
    const children = $('.branch-children', details);
    collections.forEach(collection => children.appendChild(makeCollectionDetails(collection, branch.id)));
    details.addEventListener('toggle', () => {
      if (details.open) state.expanded.add(key); else state.expanded.delete(key);
      saveState();
    });
    if (state.expanded.has(key)) details.open = true;
    return details;
  }

  function renderCenter() {
    const center = $('#root-center');
    if (!center) return;
    const records = state.manifest.center.records || [];
    center.innerHTML = `
      <div class="center-label">NORTH POLE / CENTER</div>
      <div class="center-map" aria-hidden="true">
        <div class="center-axis axis-up">AXIS ↑</div>
        <div class="center-core">
          <div class="center-title">TIM DOOLEY</div>
          <div class="center-subtitle">POTATO OF LIFE</div>
        </div>
        <div class="center-axis axis-down">WORLD ↓</div>
      </div>
      <p class="center-description">${escape(state.manifest.center.description)}</p>
      <div class="center-records">
        ${records.map(record => `<button type="button" class="center-record" data-center-id="${escape(record.id)}">${escape(record.label)}</button>`).join('')}
      </div>
    `;
    records.forEach(record => {
      const button = center.querySelector(`[data-center-id="${CSS.escape(record.id)}"]`);
      if (!button) return;
      button.addEventListener('click', () => {
        const found = state.records.find(r => (r.canonical_id || r.id) === record.id || r.id === record.id);
        if (found) selectRecord(found, `center/${record.id}`);
        else {
          const dossier = $('#root-dossier');
          if (dossier) {
            dossier.hidden = false;
            dossier.innerHTML = `<div class="dossier-head"><div><div class="eyebrow">center</div><h2>${escape(record.label)}</h2></div><button class="dossier-close" type="button" data-action="close-dossier">×</button></div><p class="dossier-description">Open the canonical page for this central corpus entry.</p><div class="dossier-actions"><a class="cmd" href="${escape(record.href)}">OPEN FULL PAGE</a></div>`;
          }
          state.selected = record.id;
          setHash(record.id);
          saveState();
        }
      });
    });
  }

  function renderTree() {
    const tree = $('#root-tree');
    if (!tree) return;
    tree.innerHTML = '';
    tree.appendChild(makeBranch(state.manifest.branches[0], state.manifest.world.collections));
    tree.appendChild(makeBranch(state.manifest.branches[1], state.manifest.axis.collections));
  }

  function restoreSelection() {
    const wanted = readHash() || state.selected;
    if (!wanted) return;
    const record = state.records.find(r => (r.canonical_id || r.id) === wanted || r.id === wanted);
    if (record) renderDossier(record, 'restored selection');
  }

  function collapseAll() {
    document.querySelectorAll('#root-tree details[open]').forEach(d => { d.open = false; });
    state.expanded.clear();
    state.rendered.clear();
    saveState();
  }

  function expandRoots() {
    document.querySelectorAll('#root-tree > details').forEach(d => { d.open = true; });
  }

  async function init() {
    loadState();
    const status = $('#root-status');
    try {
      const [manifestResponse, indexResponse] = await Promise.all([
        fetch(MANIFEST_URL, {cache: 'no-store'}),
        fetch(DATA_URL, {cache: 'no-store'})
      ]);
      if (!manifestResponse.ok) throw new Error(`navigation manifest: HTTP ${manifestResponse.status}`);
      state.manifest = await manifestResponse.json();
      if (indexResponse.ok) {
        const index = await indexResponse.json();
        state.records = Array.isArray(index.records) ? index.records : [];
      } else {
        state.records = [];
      }
      renderCenter();
      renderTree();
      restoreSelection();
      if (status) status.textContent = `${state.records.length.toLocaleString()} indexed records · one center · two root branches`;
    } catch (error) {
      if (status) status.textContent = `navigation data unavailable: ${error.message}`;
      const tree = $('#root-tree');
      if (tree) tree.innerHTML = '<div class="tree-empty">The center is available, but the generated repository index could not be loaded. Build the site before expecting the full corpus tree.</div>';
    }
  }

  document.addEventListener('click', event => {
    const action = event.target.closest('[data-action]')?.dataset.action;
    if (action === 'collapse-all') collapseAll();
    if (action === 'expand-roots') expandRoots();
    if (action === 'reset-root') { collapseAll(); closeDossier(); window.scrollTo({top: 0, behavior: 'smooth'}); }
    if (action === 'close-dossier') closeDossier();
  });

  window.addEventListener('hashchange', () => {
    const wanted = readHash();
    if (!wanted) return closeDossier();
    const record = state.records.find(r => (r.canonical_id || r.id) === wanted || r.id === wanted);
    if (record) renderDossier(record, 'URL selection');
  });

  init();
})();
