(() => {
  const CHUNK_COUNT = 41;
  const indexEl = document.getElementById('book-index');
  const contentEl = document.getElementById('book-content');
  const frontEl = document.getElementById('book-front');
  const statusEl = document.getElementById('reader-status');
  const downloadEl = document.getElementById('download-book');
  if (!indexEl || !contentEl) return;

  let loadedPayload = null;

  function renderIndex(manifest) {
    const fragment = document.createDocumentFragment();
    manifest.chapters.forEach((chapter) => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${chapter.anchor}`;
      const num = document.createElement('span');
      num.className = 'num';
      num.textContent = chapter.number;
      const title = document.createElement('span');
      title.className = 'title';
      title.textContent = chapter.title;
      a.append(num, title);
      li.append(a);
      fragment.append(li);
    });
    indexEl.replaceChildren(fragment);
  }

  function renderFrontMatter(manifest) {
    if (!frontEl || !Array.isArray(manifest.front_matter)) return;
    const fragment = document.createDocumentFragment();
    manifest.front_matter.forEach((line, idx) => {
      const value = String(line ?? '').trim();
      if (!value) return;
      const node = idx === 0 || idx === 5 || idx === 8 || idx === 11 || idx === 15
        ? document.createElement('h2')
        : document.createElement('p');
      node.textContent = value;
      fragment.append(node);
    });
    frontEl.replaceChildren(fragment);
  }

  function addChapterNavigation(manifest) {
    manifest.chapters.forEach((chapter, index) => {
      const section = document.getElementById(chapter.anchor);
      if (!section) return;
      const nav = document.createElement('nav');
      nav.className = 'chapter-nav';
      nav.setAttribute('aria-label', `Chapter ${chapter.number} navigation`);
      const previous = manifest.chapters[index - 1];
      const next = manifest.chapters[index + 1];
      const pieces = [];
      if (previous) {
        const a = document.createElement('a');
        a.href = `#${previous.anchor}`;
        a.textContent = `← Chapter ${previous.number}`;
        pieces.push(a);
      }
      const indexLink = document.createElement('a');
      indexLink.href = '#book-index-heading';
      indexLink.textContent = 'Index';
      pieces.push(indexLink);
      const top = document.createElement('a');
      top.href = '#top';
      top.textContent = 'Top';
      pieces.push(top);
      if (next) {
        const a = document.createElement('a');
        a.href = `#${next.anchor}`;
        a.textContent = `Chapter ${next.number} →`;
        pieces.push(a);
      }
      nav.append(...pieces);
      section.append(nav);
    });
  }

  async function decodePayload() {
    const urls = Array.from({ length: CHUNK_COUNT }, (_, index) => `data/book-${String(index + 1).padStart(2, '0')}.b64`);
    const responses = await Promise.all(urls.map((url) => fetch(url)));
    responses.forEach((response, idx) => {
      if (!response.ok) throw new Error(`${urls[idx]} ${response.status}`);
    });
    const chunks = await Promise.all(responses.map((response) => response.text()));
    const encoded = chunks.join('').replace(/\s+/g, '');
    const binary = atob(encoded);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
    if (!('DecompressionStream' in window)) throw new Error('This browser does not support gzip decompression streams.');
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    const text = await new Response(stream).text();
    return JSON.parse(text);
  }

  function resolveHash(manifest) {
    const raw = window.location.hash.slice(1);
    if (!raw || raw === 'download-book') return;
    const direct = document.getElementById(raw);
    if (direct) {
      direct.scrollIntoView({ block: 'start' });
      return;
    }
    const legacy = (manifest.legacy_redirects || []).find((entry) => raw === `chapter-${String(entry.number).replace(/\./g, '-')}`);
    if (legacy) {
      const target = document.getElementById(legacy.target);
      if (target) {
        history.replaceState(null, '', `#${legacy.target}`);
        target.scrollIntoView({ block: 'start' });
      }
    }
  }

  function standaloneHtml(payload) {
    const title = 'The Great Book of Potato v1.2.0.0';
    const index = payload.manifest.chapters.map((chapter) => `<li><a href="#${chapter.anchor}">Chapter ${chapter.number}: ${chapter.title.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</a></li>`).join('');
    return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><style>body{max-width:850px;margin:40px auto;padding:0 20px;font:18px/1.7 Georgia,serif;color:#191914}h1,h2,h3{line-height:1.2}a{color:#315b27}.book-chapter{border-top:1px solid #bbb;padding-top:35px;margin-top:60px}.chapter-number{font:12px system-ui;text-transform:uppercase;letter-spacing:.1em}.chapter-link,.back-index{display:none}ol{font:14px/1.45 system-ui}</style></head><body><h1>${title}</h1><p>Source-preserving presentation edition.</p><h2 id="book-index">Index</h2><ol>${index}</ol>${payload.html}</body></html>`;
  }

  function enableDownload() {
    if (!downloadEl) return;
    downloadEl.addEventListener('click', (event) => {
      if (!loadedPayload) return;
      event.preventDefault();
      const blob = new Blob([standaloneHtml(loadedPayload)], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'The-Great-Book-of-Potato-v1.2.0.0.html';
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }

  async function load() {
    try {
      const payload = await decodePayload();
      loadedPayload = payload;
      renderIndex(payload.manifest);
      renderFrontMatter(payload.manifest);
      contentEl.innerHTML = payload.html;
      addChapterNavigation(payload.manifest);
      if (statusEl) statusEl.remove();
      if (downloadEl) downloadEl.removeAttribute('aria-disabled');
      resolveHash(payload.manifest);
    } catch (error) {
      console.error('Great Book reader failed to load', error);
      if (statusEl) {
        statusEl.className = 'reader-error';
        statusEl.textContent = 'The complete book could not be assembled in this browser. Please use a current browser with gzip DecompressionStream support.';
      }
    }
  }

  window.addEventListener('hashchange', () => {
    const target = document.getElementById(window.location.hash.slice(1));
    if (target) target.scrollIntoView({ block: 'start' });
  });

  enableDownload();
  load();
})();
