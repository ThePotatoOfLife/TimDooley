(() => {
  const DATA = 'data/taoism/dao-de-jing.json';
  const LOCAL_ENGLISH = 'data/texts/taoism/tao-teh-king-legge-gutenberg.txt';
  let data, chapters = [], current = 1, localText = '';
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));

  function renderList(filter='') {
    const q = filter.toLowerCase();
    $('dao-chapters').innerHTML = chapters.filter(c => !q || String(c.number).includes(q) || c.title.toLowerCase().includes(q)).map(c => `<button class="bible-book" data-chapter="${c.number}"><strong>${c.number}</strong><span>${esc(c.title)}</span></button>`).join('');
    $('dao-chapters').querySelectorAll('[data-chapter]').forEach(b => b.addEventListener('click', () => show(Number(b.dataset.chapter))));
  }

  function extractChapters(text) {
    const lines = text.replace(/\r/g, '').split('\n');
    const starts = [];
    lines.forEach((line, i) => {
      const trimmed = line.trim();
      let m = trimmed.match(/^Ch\.\s*1\.\s*/i);
      if (m) starts.push({number: 1, index: i, prefix: m[0].length});
      m = trimmed.match(/^([2-9]|[1-7][0-9]|80|81)\.\s*(?:1\.)?\s*$/);
      if (m) starts.push({number: Number(m[1]), index: i, prefix: trimmed.length});
      m = trimmed.match(/^([2-9]|[1-7][0-9]|80|81)\.\s+1\.\s+/);
      if (m) starts.push({number: Number(m[1]), index: i, prefix: m[0].length});
    });
    const unique = [];
    const seen = new Set();
    for (const start of starts) {
      if (start.number >= 1 && start.number <= 81 && !seen.has(start.number)) { seen.add(start.number); unique.push(start); }
    }
    unique.sort((a,b) => a.number-b.number);
    return unique.map((start, i) => {
      const end = i + 1 < unique.length ? unique[i + 1].index : lines.length;
      let body = lines.slice(start.index, end).join('\n').trim();
      body = body.replace(/^(?:Ch\.\s*1\.|\d{1,2}\.)\s*(?:1\.)?\s*/i, '');
      return {number: start.number, text: body};
    }).filter(c => c.text.length > 20);
  }

  function show(n) {
    current = Math.min(81, Math.max(1, n));
    const meta = chapters[current - 1];
    $('dao-location').textContent = `Chapter ${current} / 81`;
    $('dao-title').textContent = meta?.title || 'Dao De Jing';
    const chapter = data?.local_chapters?.find(c => c.number === current) || localChapters.find(c => c.number === current);
    if (!chapter) {
      $('dao-text').innerHTML = '<p>Chapter text is not available in the local edition.</p>';
      return;
    }
    const paragraphs = chapter.text.split(/\n\s*\n/).map(x => x.trim()).filter(Boolean);
    $('dao-text').innerHTML = paragraphs.map(p => `<p>${esc(p).replace(/\n/g, '<br>')}</p>`).join('');
  }

  let localChapters = [];
  Promise.all([
    fetch(DATA).then(r => { if (!r.ok) throw Error(`Catalogue HTTP ${r.status}`); return r.json(); }),
    fetch(LOCAL_ENGLISH, {cache:'force-cache'}).then(r => { if (!r.ok) throw Error(`Local text HTTP ${r.status}`); return r.text(); })
  ]).then(([d, text]) => {
    data = d;
    chapters = d.chapters || [];
    localText = text;
    localChapters = extractChapters(text);
    if (localChapters.length < 81) throw Error(`Local Legge edition yielded ${localChapters.length}/81 chapters`);
    renderList();
    show(1);
  }).catch(e => {
    $('dao-text').innerHTML = `<p>Could not load the local Dao De Jing edition.</p><p class="bible-status">${esc(e.message)}</p>`;
  });

  $('dao-prev').addEventListener('click', () => show(current - 1));
  $('dao-next').addEventListener('click', () => show(current + 1));
  $('dao-search').addEventListener('input', e => renderList(e.target.value));
})();
