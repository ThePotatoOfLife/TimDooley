(() => {
  const root = document.getElementById('text-library');
  const search = document.getElementById('text-search');
  let texts = [];
  const esc = s => String(s ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));
  function render(q='') {
    q = q.trim().toLowerCase();
    const rows = texts.filter(t => !q || [t.tradition,t.work,t.scope,t.completeness,t.language,t.edition].flat().join(' ').toLowerCase().includes(q));
    root.innerHTML = rows.map(t => `<article class="belief-card"><div class="belief-card-kicker">${esc(t.tradition)}</div><h2>${esc(t.work)}</h2><p>${esc(t.scope)}</p><p><strong>Completeness:</strong> ${esc(t.completeness)}</p><p>${esc(t.source_note)}</p><p><strong>Language:</strong> ${esc(t.language)}${t.edition ? ` · <strong>Edition:</strong> ${esc(t.edition)}` : ''}</p><a href="${esc(t.reader)}" target="_blank" rel="noopener">Open reader / source ↗</a></article>`).join('') || '<p>No matching texts.</p>';
  }
  fetch('data/religious-text-library.json').then(r => r.json()).then(d => { texts=d.texts || []; render(); }).catch(e => { root.innerHTML = `<p>Could not load text library: ${esc(e.message)}</p>`; });
  search.addEventListener('input', e => render(e.target.value));
})();
