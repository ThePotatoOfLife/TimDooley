/* Canonical site shell. Pages provide only <div data-site-header></div>. */
(function () {
  const marker = document.querySelector('[data-site-header]');
  if (!marker) return;

  const script = document.currentScript;
  const componentURL = new URL('components/header.html', script.src);
  const pageURL = new URL(window.location.href);
  const repoRoot = new URL('./', componentURL).href.replace(/components\/$/, '');
  const rootPath = new URL(repoRoot).pathname;
  const relativeRoot = rootPath.endsWith('/') ? rootPath : `${rootPath}/`;

  function rootPrefix() {
    const pagePath = pageURL.pathname;
    const depth = Math.max(0, pagePath.slice(relativeRoot.length).split('/').length - 1);
    return depth ? '../'.repeat(depth) : '';
  }

  function currentSection(pathname) {
    const file = pathname.split('/').pop() || 'index.html';
    if (file === 'index.html') return 'home';
    if (file === 'repository.html' || file === 'node.html' || file === 'geometry.html') return 'repository';
    if (file === 'timeline.html') return 'timeline';
    if (file === 'nations.html' || file === 'nation.html') return 'world';
    if (file === 'people.html') return 'people';
    if (file === 'belief.html' || file === 'political-compass.html') return 'ideas';
    if (file === 'books.html' || pathname.includes('/books/')) return 'books';
    if (file === 'potatoism.html' || file === 'potatoism-entry.html') return 'potatoism';
    if (file === 'extremism.html') return 'movements';
    if (file === 'hawkins.html') return 'hawkins';
    return null;
  }

  async function load() {
    try {
      const response = await fetch(componentURL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`header ${response.status}`);
      const html = await response.text();
      const prefix = rootPrefix();
      marker.innerHTML = html.replaceAll('{{ROOT}}', prefix);
      const active = currentSection(pageURL.pathname);
      if (active) {
        const link = marker.querySelector(`[data-nav="${active}"]`);
        if (link) link.setAttribute('aria-current', 'page');
      }
    } catch (error) {
      marker.innerHTML = '<p class="site-header-error">Navigation could not be loaded.</p>';
      console.error('Canonical site header failed:', error);
    }
  }

  load();
})();
