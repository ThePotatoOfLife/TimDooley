const MOVEMENT_DATA_FILES = [
  'data/extremism-cults-atlas-2026-09.json',
  'data/extremism-cults-atlas-expansion-2026-09.json',
  'data/extremism-record-enrichments-2026-09.json'
];

const movementText = (value) => {
  if (value === null || value === undefined || value === '') return '';
  if (Array.isArray(value)) return value.map(movementText).filter(Boolean).join(', ');
  if (typeof value === 'object') return Object.values(value).map(movementText).filter(Boolean).join(', ');
  return String(value);
};

const movementList = (value) => {
  if (value === null || value === undefined || value === '') return [];
  if (Array.isArray(value)) return value.flatMap(movementList).filter(Boolean);
  if (typeof value === 'object') return Object.values(value).flatMap(movementList).filter(Boolean);
  return [String(value)];
};

const movementEscape = (value) => movementText(value).replace(/[&<>"']/g, c => ({
  '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
}[c]));

const movementRecordsFromDocument = (document) => {
  if (Array.isArray(document)) return document;
  if (document && Array.isArray(document.records)) return document.records;
  if (document && Array.isArray(document.movements)) return document.movements;
  if (document && Array.isArray(document.entries)) return document.entries;
  return [];
};

async function loadMovementDocuments() {
  const results = await Promise.allSettled(
    MOVEMENT_DATA_FILES.map(path => fetch(`${path}?v=20260908-2`, { cache: 'no-store' }).then(response => {
      if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
      return response.json();
    }))
  );
  const failures = results.filter(result => result.status === 'rejected');
  const documents = results.filter(result => result.status === 'fulfilled').map(result => result.value);
  if (!documents.length) throw new Error(failures.map(result => result.reason?.message || String(result.reason)).join(' | '));
  return { documents, failures };
}

function renderMovementPage() {
  const search = document.querySelector('#search');
  const status = document.querySelector('#status');
  const category = document.querySelector('#category');
  const grid = document.querySelector('#grid');
  const summary = document.querySelector('#summary');
  if (!search || !status || !category || !grid || !summary) return;

  loadMovementDocuments().then(({ documents, failures }) => {
    const records = documents.flatMap(movementRecordsFromDocument);
    const byId = new Map();
    for (const record of records) {
      if (!record || typeof record !== 'object') continue;
      const id = movementText(record.id || record.slug || record.name || record.title);
      if (!id) continue;
      byId.set(id, { ...byId.get(id), ...record });
    }
    const merged = [...byId.values()];

    const statuses = [...new Set(merged.flatMap(r => movementList(r.status)))].sort();
    const categories = [...new Set(merged.flatMap(r => movementList(r.category)))].sort();
    for (const value of statuses) status.insertAdjacentHTML('beforeend', `<option value="${movementEscape(value)}">${movementEscape(value)}</option>`);
    for (const value of categories) category.insertAdjacentHTML('beforeend', `<option value="${movementEscape(value)}">${movementEscape(value)}</option>`);

    function render() {
      const query = search.value.toLowerCase().trim();
      const wantedStatus = status.value;
      const wantedCategory = category.value;
      const rows = merged.filter(record => {
        const haystack = JSON.stringify(record).toLowerCase();
        return (!query || haystack.includes(query)) &&
          (!wantedStatus || movementList(record.status).includes(wantedStatus)) &&
          (!wantedCategory || movementList(record.category).includes(wantedCategory));
      });

      summary.textContent = `${rows.length} records shown · ${merged.length} indexed` + (failures.length ? ` · ${failures.length} optional layer(s) unavailable` : '');
      grid.innerHTML = rows.map(record => {
        const categories = movementList(record.category);
        const affiliations = movementList(record.affiliations ?? record.affiliation);
        const sources = movementList(record.sources);
        const dossier = movementText(record.definition || record.context || record.notes || record.description);
        const relationships = movementList(record.relationships || record.couplings);
        return `<article class="movement-card">
          <div class="movement-top"><span class="movement-status">${movementEscape(record.status || 'Unspecified')}</span><span>${movementEscape(categories.join(' · '))}</span></div>
          <h2>${movementEscape(record.name || record.title || record.id)}</h2>
          <p>${movementEscape(dossier || movementText(record.targets_or_hate ?? record.targets) || 'No substantive public description recorded yet.')}</p>
          <dl>
            <dt>Geography</dt><dd>${movementEscape(movementText(record.geography) || 'Not specified.')}</dd>
            <dt>Membership</dt><dd>${movementEscape(movementText(record.membership) || 'No reliable public estimate.')}</dd>
            <dt>Armed / violent status</dt><dd>${movementEscape(movementText(record.armed_or_violent ?? record.armed_status) || 'Not specified.')}</dd>
            <dt>Affiliations</dt><dd>${movementEscape(affiliations.join(', ') || 'None recorded.')}</dd>
            ${relationships.length ? `<dt>Relationships</dt><dd>${movementEscape(relationships.join(', '))}</dd>` : ''}
          </dl>
          <div class="movement-sources">${sources.map(source => `<a href="${movementEscape(source)}" target="_blank" rel="noopener">Source</a>`).join('')}</div>
        </article>`;
      }).join('') || '<p class="muted">No records match the current filters.</p>';
    }

    search.addEventListener('input', render);
    status.addEventListener('change', render);
    category.addEventListener('change', render);
    render();
  }).catch(error => {
    summary.textContent = 'Movement research layer unavailable';
    grid.innerHTML = `<p class="error">Could not load the movement research layer: ${movementEscape(error?.message || error)}</p>`;
  });
}

document.addEventListener('DOMContentLoaded', renderMovementPage);
