(() => {
  const DATA = 'data/taoism/dao-de-jing.json';
  const API = 'https://en.wikisource.org/w/api.php?action=parse&page=Translation:Tao_Te_Ching&prop=text&format=json&origin=*';
  let data, chapters = [], current = 1;
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));
  function renderList(filter='') {
    const q = filter.toLowerCase();
    $('dao-chapters').innerHTML = chapters.filter(c => !q || String(c.number).includes(q) || c.title.toLowerCase().includes(q)).map(c => `<button class="bible-book" data-chapter="${c.number}"><strong>${c.number}</strong><span>${esc(c.title)}</span></button>`).join('');
    $('dao-chapters').querySelectorAll('[data-chapter]').forEach(b => b.addEventListener('click', () => show(Number(b.dataset.chapter))));
  }
  function extractChapter(html, n) {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const headings = [...doc.querySelectorAll('h3')];
    const h = headings.find(x => new RegExp(`Chapter\\s*${n}\\b`, 'i').test(x.textContent));
    if (!h) return null;
    const nodes = [];
    let el = h.nextElementSibling;
    while (el && !(/^H[123]$/.test(el.tagName))) { nodes.push(el.cloneNode(true)); el = el.nextElementSibling; }
    return nodes.map(n => n.outerHTML).join('');
  }
  async function loadText() {
    const r = await fetch(API); if (!r.ok) throw new Error(`Wikisource HTTP ${r.status}`);
    const j = await r.json();
    if (!j.parse || !j.parse.text || !j.parse.text['*']) throw new Error('Wikisource returned no parsed text');
    return j.parse.text['*'];
  }
  async function show(n) {
    current = Math.min(81, Math.max(1, n));
    const meta = chapters[current - 1];
    $('dao-location').textContent = `Chapter ${current} / 81`;
    $('dao-title').textContent = meta ? meta.title : 'Dao De Jing';
    $('dao-text').innerHTML = '<p>Loading the complete chapter from the cited source…</p>';
    try {
      if (!window.__daoHtml) window.__daoHtml = await loadText();
      const body = extractChapter(window.__daoHtml, current);
      $('dao-text').innerHTML = body || `<p>Chapter ${current} could not be parsed automatically. <a href="https://en.wikisource.org/wiki/Translation:Tao_Te_Ching#Chapter_${current}">Open the source chapter.</a></p>`;
    } catch (e) {
      $('dao-text').innerHTML = `<p>Could not load the source automatically. <a href="https://en.wikisource.org/wiki/Translation:Tao_Te_Ching">Read the complete edition at Wikisource.</a></p><p class="bible-status">${esc(e.message)}</p>`;
    }
  }
  Promise.all([fetch(DATA).then(r => r.json()), Promise.resolve()]).then(([d]) => { data=d; chapters=d.chapters; renderList(); show(1); }).catch(e => { $('dao-text').innerHTML = `<p>Catalogue error: ${esc(e.message)}</p>`; });
  $('dao-prev').addEventListener('click', () => show(current - 1));
  $('dao-next').addEventListener('click', () => show(current + 1));
  $('dao-search').addEventListener('input', e => renderList(e.target.value));
})();
