(() => {
  const hydrateBlobImages = async () => {
    const images = [...document.querySelectorAll('img[data-github-blob]')];
    for (const img of images) {
      try {
        const response = await fetch('https://api.github.com/repos/ThePotatoOfLife/TimDooley/git/blobs/' + img.dataset.githubBlob);
        if (!response.ok) continue;
        const payload = await response.json();
        const binary = atob(String(payload.content || '').replace(/\s/g, ''));
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        img.src = URL.createObjectURL(new Blob([bytes], {type: img.dataset.githubMime || 'image/webp'}));
      } catch (_) {}
    }
  };
  hydrateBlobImages();

  const grid = document.querySelector('[data-gallery-grid]');
  const stage = document.querySelector('[data-museum-stage]');
  const plaque = document.querySelector('[data-wall-plaque]');
  const dialog = document.querySelector('#gallery-viewer');
  if (!grid || !stage || !plaque || !dialog) return;

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

  const filters = [...document.querySelectorAll('[data-gallery-filter]')];
  const wallPrev = [...document.querySelectorAll('[data-wall-prev],[data-wall-prev-secondary]')];
  const wallNext = [...document.querySelectorAll('[data-wall-next],[data-wall-next-secondary]')];
  const wallOpen = document.querySelector('[data-wall-open]');
  const plaqueCounter = plaque.querySelector('[data-plaque-counter]');
  const plaqueDate = plaque.querySelector('[data-plaque-date]');
  const plaqueTitle = plaque.querySelector('[data-plaque-title]');
  const plaqueBody = plaque.querySelector('[data-plaque-body]');
  const plaqueMotifs = plaque.querySelector('[data-plaque-motifs]');
  const empty = document.querySelector('[data-gallery-empty]');

  const viewerImage = dialog.querySelector('#gallery-viewer-image');
  const viewerTitle = dialog.querySelector('#gallery-viewer-title');
  const viewerMeta = dialog.querySelector('#gallery-viewer-meta');
  const viewerDescription = dialog.querySelector('#gallery-viewer-description');
  const viewerMotifs = dialog.querySelector('#gallery-viewer-motifs');
  const viewerCounter = dialog.querySelector('#gallery-viewer-counter');
  const viewerClose = dialog.querySelector('[data-gallery-close]');
  const viewerPrev = dialog.querySelector('[data-gallery-prev]');
  const viewerNext = dialog.querySelector('[data-gallery-next]');

  let wallIndex = 0;
  let viewerIndex = -1;

  const visibleCards = () => cards.filter(card => !card.hidden);

  const cardData = card => {
    const img = card.querySelector('img');
    const meta = card.querySelector('em')?.textContent.trim() || '';
    return {
      src: img.currentSrc || img.src,
      alt: img.alt,
      title: card.querySelector('strong')?.textContent.trim() || '',
      meta,
      date: meta.split('·')[0].trim(),
      description: card.dataset.description || card.querySelector('.gallery-card-desc')?.textContent.trim() || '',
      motifs: card.dataset.motifs || ''
    };
  };

  const updatePlaque = (card,index,total) => {
    const data = cardData(card);
    plaqueCounter.textContent = 'Work ' + String(index + 1).padStart(2,'0') + ' / ' + String(total).padStart(2,'0');
    plaqueDate.textContent = data.meta;
    plaqueTitle.textContent = data.title;
    plaqueBody.textContent = data.description;
    plaqueMotifs.textContent = data.motifs;
  };

  // Controlled wall rotation. No wheel handler: document scrolling remains normal.
  const renderWall = () => {
    const visible = visibleCards();
    if (!visible.length) {
      if (empty) empty.hidden = false;
      cards.forEach(card => {
        card.classList.remove('is-active','is-prev','is-next','is-away-left','is-away-right');
        card.setAttribute('aria-hidden','true');
      });
      return;
    }
    if (empty) empty.hidden = true;
    wallIndex = Math.max(0,Math.min(wallIndex,visible.length - 1));
    const active = visible[wallIndex];

    cards.forEach(card => {
      card.classList.remove('is-active','is-prev','is-next','is-away-left','is-away-right');
      card.setAttribute('aria-hidden','true');
    });

    visible.forEach((card,index) => {
      if (index === wallIndex) {
        card.classList.add('is-active');
        card.setAttribute('aria-hidden','false');
      } else if (index === wallIndex - 1) {
        card.classList.add('is-prev');
        card.setAttribute('aria-hidden','false');
      } else if (index === wallIndex + 1) {
        card.classList.add('is-next');
        card.setAttribute('aria-hidden','false');
      } else if (index < wallIndex) {
        card.classList.add('is-away-left');
      } else {
        card.classList.add('is-away-right');
      }
    });

    updatePlaque(active,wallIndex,visible.length);
    const atStart = wallIndex === 0;
    const atEnd = wallIndex === visible.length - 1;
    wallPrev.forEach(button => button.disabled = atStart);
    wallNext.forEach(button => button.disabled = atEnd);
    if (wallOpen) wallOpen.disabled = false;
    history.replaceState(null,'','#' + active.id);
  };

  const moveWall = step => {
    const visible = visibleCards();
    const next = wallIndex + step;
    if (next < 0 || next >= visible.length) return;
    wallIndex = next;
    renderWall();
  };

  wallPrev.forEach(button => button.addEventListener('click',() => moveWall(-1)));
  wallNext.forEach(button => button.addEventListener('click',() => moveWall(1)));

  grid.addEventListener('click', event => {
    const trigger = event.target.closest('[data-gallery-open]');
    if (!trigger) return;
    const card = trigger.closest('.gallery-card');
    const visible = visibleCards();
    const index = visible.indexOf(card);
    if (index < 0) return;
    if (index === wallIndex - 1) {
      wallIndex = index;
      renderWall();
      return;
    }
    if (index === wallIndex + 1) {
      wallIndex = index;
      renderWall();
      return;
    }
    if (index === wallIndex) openViewer(card);
  });

  grid.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      moveWall(-1);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      moveWall(1);
    } else if (event.key === 'Enter') {
      event.preventDefault();
      const active = visibleCards()[wallIndex];
      if (active) openViewer(active);
    }
  });

  let pointerStart = null;
  stage.addEventListener('pointerdown', event => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    pointerStart = {x:event.clientX,y:event.clientY};
  });
  stage.addEventListener('pointerup', event => {
    if (!pointerStart) return;
    const dx = event.clientX - pointerStart.x;
    const dy = event.clientY - pointerStart.y;
    pointerStart = null;
    if (Math.abs(dx) < 45 || Math.abs(dx) < Math.abs(dy) * 1.25) return;
    moveWall(dx < 0 ? 1 : -1);
  });
  stage.addEventListener('pointercancel',() => { pointerStart = null; });

  filters.forEach(button => button.addEventListener('click',() => {
    const filter = button.dataset.galleryFilter;
    filters.forEach(item => item.setAttribute('aria-pressed',String(item === button)));
    cards.forEach(card => {
      card.hidden = filter !== 'all' && card.dataset.category !== filter;
    });
    wallIndex = 0;
    renderWall();
  }));

  const renderViewer = card => {
    const visible = visibleCards();
    const data = cardData(card);
    viewerIndex = visible.indexOf(card);
    viewerImage.src = data.src;
    viewerImage.alt = data.alt;
    viewerTitle.textContent = data.title;
    viewerMeta.textContent = data.meta;
    viewerDescription.textContent = data.description;
    viewerMotifs.textContent = data.motifs;
    viewerCounter.textContent = (viewerIndex + 1) + ' / ' + visible.length;
    viewerPrev.disabled = visible.length < 2;
    viewerNext.disabled = visible.length < 2;
  };

  function openViewer(card) {
    renderViewer(card);
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open','');
  }

  const moveViewer = step => {
    const visible = visibleCards();
    if (!visible.length) return;
    const nextIndex = (viewerIndex + step + visible.length) % visible.length;
    renderViewer(visible[nextIndex]);
  };

  wallOpen?.addEventListener('click',() => {
    const active = visibleCards()[wallIndex];
    if (active) openViewer(active);
  });
  viewerClose?.addEventListener('click',() => dialog.close());
  viewerPrev?.addEventListener('click',() => moveViewer(-1));
  viewerNext?.addEventListener('click',() => moveViewer(1));
  dialog.addEventListener('click',event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('keydown',event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); moveViewer(-1); }
    else if (event.key === 'ArrowRight') { event.preventDefault(); moveViewer(1); }
  });
  dialog.addEventListener('close',() => {
    viewerImage.removeAttribute('src');
    viewerIndex = -1;
  });

  const hashCard = location.hash && document.querySelector(location.hash);
  if (hashCard?.classList.contains('gallery-card')) {
    const index = visibleCards().indexOf(hashCard);
    if (index >= 0) wallIndex = index;
  }
  renderWall();
})();