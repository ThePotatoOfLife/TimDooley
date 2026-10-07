(() => {
  const grid = document.querySelector('[data-gallery-grid]');
  const dialog = document.querySelector('#gallery-viewer');
  if (!grid || !dialog) return;

  const cards = [...grid.querySelectorAll('.gallery-card')];
  const filters = [...document.querySelectorAll('[data-gallery-filter]')];
  const image = dialog.querySelector('#gallery-viewer-image');
  const title = dialog.querySelector('#gallery-viewer-title');
  const meta = dialog.querySelector('#gallery-viewer-meta');
  const description = dialog.querySelector('#gallery-viewer-description');
  const motifs = dialog.querySelector('#gallery-viewer-motifs');
  const counter = dialog.querySelector('#gallery-viewer-counter');
  const close = dialog.querySelector('[data-gallery-close]');
  const prev = dialog.querySelector('[data-gallery-prev]');
  const next = dialog.querySelector('[data-gallery-next]');
  const empty = document.querySelector('[data-gallery-empty]');
  let currentIndex = -1;

  const visibleCards = () => cards.filter(card => !card.hidden);

  const cardData = card => {
    const img = card.querySelector('img');
    return {
      src: img.currentSrc || img.src,
      alt: img.alt,
      title: card.querySelector('strong')?.textContent.trim() || '',
      meta: card.querySelector('em')?.textContent.trim() || '',
      description: card.dataset.description || '',
      motifs: card.dataset.motifs || ''
    };
  };

  const render = card => {
    const visible = visibleCards();
    const data = cardData(card);
    currentIndex = visible.indexOf(card);
    image.src = data.src;
    image.alt = data.alt;
    title.textContent = data.title;
    meta.textContent = data.meta;
    description.textContent = data.description;
    motifs.textContent = data.motifs;
    counter.textContent = `${currentIndex + 1} / ${visible.length}`;
    prev.disabled = visible.length < 2;
    next.disabled = visible.length < 2;
  };

  const openCard = card => {
    render(card);
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
  };

  const move = step => {
    const visible = visibleCards();
    if (!visible.length) return;
    const nextIndex = (currentIndex + step + visible.length) % visible.length;
    render(visible[nextIndex]);
  };

  grid.addEventListener('click', event => {
    const trigger = event.target.closest('[data-gallery-open]');
    if (!trigger) return;
    const card = trigger.closest('.gallery-card');
    if (card) openCard(card);
  });

  filters.forEach(button => button.addEventListener('click', () => {
    const filter = button.dataset.galleryFilter;
    filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    cards.forEach(card => {
      card.hidden = filter !== 'all' && card.dataset.category !== filter;
    });
    const count = visibleCards().length;
    if (empty) empty.hidden = count !== 0;
  }));

  close?.addEventListener('click', () => dialog.close());
  prev?.addEventListener('click', () => move(-1));
  next?.addEventListener('click', () => move(1));

  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });

  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      move(-1);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      move(1);
    }
  });

  dialog.addEventListener('close', () => {
    image.removeAttribute('src');
    currentIndex = -1;
  });

  const hashCard = location.hash && document.querySelector(location.hash);
  if (hashCard?.classList.contains('gallery-card')) {
    hashCard.scrollIntoView({block:'center'});
  }
})();