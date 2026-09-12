(() => {
  const indexEl = document.getElementById('book-index');
  const contentEl = document.getElementById('book-content');
  const frontEl = document.getElementById('book-front');
  const statusEl = document.getElementById('reader-status');
  if (!indexEl || !contentEl) return;

  const manifestUrl = 'book-manifest.json';

  const escapeText = (value) => String(value ?? '');

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
      const value = escapeText(line).trim();
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

  function resolveLegacyHash(manifest) {
    const raw = window.location.hash.slice(1);
    if (!raw) return;
    if (document.getElementById(raw)) {
      document.getElementById(raw).scrollIntoView({ block: 'start' });
      return;
    }
    const legacy = (manifest.legacy_redirects || []).find((entry) => raw === `chapter-${String(entry.number).replace(/\./g, '-')}`);
    if (legacy && document.getElementById(legacy.target)) {
      history.replaceState(null, '', `#${legacy.target}`);
      document.getElementById(legacy.target).scrollIntoView({ block: 'start' });
    }
  }

  async function load() {
    try {
      const manifestResponse = await fetch(manifestUrl);
      if (!manifestResponse.ok) throw new Error(`manifest ${manifestResponse.status}`);
      const manifest = await manifestResponse.json();
      renderIndex(manifest);
      renderFrontMatter(manifest);

      const responses = await Promise.all(manifest.parts.map((part) => fetch(part.path)));
      responses.forEach((response, idx) => {
        if (!response.ok) throw new Error(`${manifest.parts[idx].path} ${response.status}`);
      });
      const htmlParts = await Promise.all(responses.map((response) => response.text()));
      contentEl.innerHTML = htmlParts.join('\n');
      addChapterNavigation(manifest);
      if (statusEl) statusEl.remove();
      resolveLegacyHash(manifest);
    } catch (error) {
      console.error('Great Book reader failed to load', error);
      if (statusEl) {
        statusEl.className = 'reader-error';
        statusEl.textContent = 'The book could not be assembled in this browser. The downloadable edition remains available above.';
      }
    }
  }

  window.addEventListener('hashchange', () => {
    const target = document.getElementById(window.location.hash.slice(1));
    if (target) target.scrollIntoView({ block: 'start' });
  });

  load();
})();
