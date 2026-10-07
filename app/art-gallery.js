(() => {
  const hydrateBlobImages = async () => {
    const images = [...document.querySelectorAll('img[data-github-blob]')];
    for (const img of images) {
      try {
        const response = await fetch('https://api.github.com/repos/ThePotatoOfLife/TimDooley/git/blobs/' + img.dataset.githubBlob);
        if (!response.ok) continue;
        const payload = await response.json();
        const binary = atob(String(payload.content || '').replace(/\\s/g, ''));
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        const url = URL.createObjectURL(new Blob([bytes], {type: img.dataset.githubMime || 'image/webp'}));
        img.src = url;
      } catch (_) {}
    }
  };
  hydrateBlobImages();

  const grid = document.querySelector('[data-gallery-grid]');
  const dialog = document.querySelector('#gallery-viewer');
  if (!grid || !dialog) return;

  // Chronological wall ordering: oldest supplied filename date first.
  const parseDate = card => {
    if (card.dataset.date) return Date.parse(card.dataset.date);
    const raw = card.querySelector('em')?.textContent.split('·')[0].trim() || '';
    const parsed = Date.parse(raw);
    return Number.isFinite(parsed) ? parsed : Number.MAX_SAFE_INTEGER;
  };
  const initialCards = [...grid.querySelectorAll('.gallery-card')];
  initialCards.sort((a,b) => parseDate(a) - parseDate(b)).forEach(card => grid.appendChild(card));
  const cards = [...grid.querySelectorAll('.gallery-card')];
  cards.forEach((card,index) => {
    let number = card.querySelector('.museum-number');
    if (!number) {
      number = document.createElement('span');
      number.className = 'museum-number';
      card.querySelector('figcaption')?.prepend(number);
    }
    if (number) number.textContent = 'Work ' + String(index + 1).padStart(2,'0');
  });
  grid.tabIndex = 0;
  grid.setAttribute('aria-label','Chronological visual art wall. Scroll horizontally or use left and right arrow keys.');

  grid.addEventListener('wheel', event => {
    if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) return;
    const max = grid.scrollWidth - grid.clientWidth;
    if (max <= 0) return;
    const right = event.deltaY > 0;
    const canMove = right ? grid.scrollLeft < max - 2 : grid.scrollLeft > 2;
    if (!canMove) return;
    event.preventDefault();
    grid.scrollLeft += event.deltaY;
  }, {passive:false});

  grid.addEventListener('keydown', event => {
    if (!['ArrowLeft','ArrowRight','PageUp','PageDown'].includes(event.key)) return;
    event.preventDefault();
    const direction = (event.key === 'ArrowLeft' || event.key === 'PageUp') ? -1 : 1;
    grid.scrollBy({left: direction * Math.max(320, grid.clientWidth * .78), behavior:'smooth'});
  });
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
    grid.scrollTo({left:0,behavior:'smooth'});
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