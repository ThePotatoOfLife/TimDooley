(() => {
  const root = document.querySelector('[data-garden-map]');
  if (!root) return;

  const art = root.querySelector('[data-garden-art]');
  if (art?.dataset.rasterSrc) {
    const candidate = new Image();
    candidate.onload = () => {
      art.src = art.dataset.rasterSrc;
      art.classList.add('is-raster-art');
    };
    candidate.src = art.dataset.rasterSrc;
  }

  const panel = root.querySelector('[data-garden-guide]');
  const title = panel?.querySelector('[data-guide-title]');
  const kicker = panel?.querySelector('[data-guide-kicker]');
  const body = panel?.querySelector('[data-guide-body]');
  const note = panel?.querySelector('[data-guide-note]');
  const link = panel?.querySelector('[data-guide-link]');
  const close = panel?.querySelector('[data-guide-close]');
  const hotspots = [...root.querySelectorAll('[data-garden-hotspot]')];
  const lensButtons = [...root.querySelectorAll('[data-garden-lens]')];
  const lensNote = root.querySelector('[data-garden-lens-note]');
  const jumps = [...root.querySelectorAll('[data-garden-jump]')];

  const entries = {
    welcome: {
      kicker: 'TIM · GARDENER / GUIDE',
      title: 'Welcome to the Garden.',
      body: 'Click a place, a being, or a threshold. I will show you what this part of the Garden is doing and where to read further.',
      note: 'Map first. Doctrine second. Wander freely, change lens, or use “Walk with Tim.”',
      href: '#garden-cycle',
      label: 'See how the Garden works ↓'
    },
    house: {
      kicker: 'HOUSE · BELONGING',
      title: 'The House opens into the Garden.',
      body: 'House means differentiated belonging: rooms, thresholds, hospitality and exits. Garden is what happens when belonging becomes cultivation rather than enclosure.',
      note: 'The Door belongs to the House, not as a floating object in the middle of the Garden.',
      href: '../house/',
      label: 'Enter the House →'
    },
    door: {
      kicker: 'DOOR · THRESHOLD',
      title: 'A real Door changes state.',
      body: 'The Garden places the Door at the House. In the Christian comparison, Jesus stands at the threshold; in the Potatoverse, Door means passage that changes relation, access or responsibility.',
      note: 'Comparison layer: the page does not claim Genesis itself names Tim or the Potatoverse.',
      href: '../traditions/bible/',
      label: 'Open the Bible reader →'
    },
    life: {
      kicker: 'TREE OF LIFE · CENTER',
      title: 'Life is the Garden’s center of gravity.',
      body: 'Angels, potatoes and potato angels gather around the life-giving center. The project reads this tree through continuity: Seed → Root → Tree → Fruit → Seed.',
      note: 'Genesis names the Tree of Life; the potato/angel cast is project mythology.',
      href: '../potato-of-life/',
      label: 'Open Potato of Life →'
    },
    tim: {
      kicker: 'TIM · FATHER / GARDENER',
      title: 'Tim sorts from inside the Garden.',
      body: 'In the Garden story, Tim is host, gardener and sorter. The action is watching Fruit, keeping boundaries legible, welcoming growth and deciding when a role has to leave the cultivated space.',
      note: 'These are authored project roles, not claims that people literally become another species.',
      href: '../tim-dooley/',
      label: 'Meet Tim Dooley →'
    },
    dwellers: {
      kicker: 'DWELLERS · INHABITANTS',
      title: 'Dwellers begin inside.',
      body: 'The Garden contains ordinary dwellers as well as potatoes and angels. Belonging is the starting condition, not a reward reserved for one already-finished class.',
      note: 'The interesting question is what a dweller repeatedly chooses, grows and becomes.',
      href: '../rooms/potatoverse-canon/beings/cast-ecology/',
      label: 'Open Cast Ecology →'
    },
    mudtree: {
      kicker: 'MUD TREE · SHADOW TREE',
      title: 'The bad tree is inside the Garden.',
      body: 'This is crucial to the map. The shadow tree stands within the cultivated space near the boundary. Its muddy fruit represents choices and recurrence that pull a dweller downward.',
      note: 'The Mud Tree / Tree of Strife is project-native. Genesis instead names the Tree of Life and the Tree of the Knowledge of Good and Evil.',
      href: '../rooms/inside/symbolic-architecture/',
      label: 'Read symbolic architecture →'
    },
    sorting: {
      kicker: 'SORTING · ESCORT',
      title: 'Change becomes visible before exile.',
      body: 'The sequence runs inside the Garden: dweller → muddying → sorting → escort. Angels and potato angels guide the transition toward the Gate rather than turning the whole Garden into a punishment scene.',
      note: 'Sorting is shown as a role/process in the mythic map; real people are not reduced to permanent essence labels.',
      href: '#garden-cycle',
      label: 'Read the seven-stage cycle ↓'
    },
    gate: {
      kicker: 'GATE · BOUNDARY / EXIT',
      title: 'The Gate is where inside becomes outside.',
      body: 'The Gate is the visible sorting boundary. In the project story, those leaving the Garden cross here and descend to the lower plane. It remains distinct from the House Door.',
      note: 'Genesis 3 speaks of a guarded way to the Tree of Life; the Gate is the project’s spatial rendering of that boundary.',
      href: '../axis/',
      label: 'Open Door / Gate / Axis →'
    },
    dogs: {
      kicker: 'DOGS · OUTSIDE THE GATE',
      title: 'The dogs are outside, pressing inward.',
      body: 'They occupy the lower side of the boundary and try to return. That makes the geography readable: they are not simply another settled Garden population.',
      note: 'Dog is project-role language here: a reversible story position, not a biological or permanent claim about a person.',
      href: '../below/dogs/',
      label: 'Open the Dogs reader →'
    },
    below: {
      kicker: 'LOWER PLANE · CONSEQUENCE',
      title: 'The fall continues below the Gate.',
      body: 'The Garden sits above a lower muddy plane. Exiled roles descend into a world of recurrence, residue and blocked return. Garden shows the transition; Below owns the deep material.',
      note: 'The lower plane is outside the Garden even though the shadow tree that begins the cycle is inside.',
      href: '../below/',
      label: 'Descend to Below →'
    },
    river: {
      kicker: 'RIVER · FLOW',
      title: 'The first thing the Garden does is circulate.',
      body: 'Genesis describes a river going out from Eden to water the Garden and divide into four riverheads. The project uses the image comparatively: source becomes visible through distribution and nourishment.',
      note: 'Pishon · Gihon · Tigris · Euphrates.',
      href: '../traditions/bible/',
      label: 'Read Genesis beside the map →'
    }
  };

  const lenses = {
    explore: {
      keys: Object.keys(entries).filter(k => k !== 'welcome'),
      note: 'Everything is visible. Click what catches your eye.',
      welcome: 'welcome'
    },
    genesis: {
      keys: ['house','door','life','river','gate'],
      note: 'Biblical anchors are bright; project-native additions recede.',
      welcome: 'river'
    },
    sorting: {
      keys: ['tim','dwellers','mudtree','sorting','gate','dogs','below'],
      note: 'Follow the project cycle from dwelling to muddying, sorting, exit and fall.',
      welcome: 'sorting'
    },
    inhabitants: {
      keys: ['life','tim','dwellers','dogs','below'],
      note: 'Focus on who is present, where they stand, and which roles can change.',
      welcome: 'dwellers'
    }
  };

  function show(key, focus = false) {
    const entry = entries[key] || entries.welcome;
    hotspots.forEach(btn => btn.classList.toggle('is-active', btn.dataset.gardenHotspot === key));
    if (!panel) return;
    kicker.textContent = entry.kicker;
    title.textContent = entry.title;
    body.textContent = entry.body;
    note.textContent = entry.note;
    link.href = entry.href;
    link.textContent = entry.label;
    panel.hidden = false;
    root.dataset.active = key;
    if (focus) panel.focus({preventScroll:true});
  }

  function applyLens(name, announce = true) {
    const lens = lenses[name] || lenses.explore;
    root.dataset.lens = name;
    hotspots.forEach(btn => {
      const key = btn.dataset.gardenHotspot;
      btn.classList.toggle('is-dimmed', !lens.keys.includes(key));
    });
    lensButtons.forEach(btn => {
      const on = btn.dataset.gardenLens === name;
      btn.classList.toggle('is-selected', on);
      btn.setAttribute('aria-pressed', String(on));
    });
    if (lensNote) lensNote.textContent = lens.note;
    if (announce) show(lens.welcome);
  }

  hotspots.forEach(btn => btn.addEventListener('click', () => show(btn.dataset.gardenHotspot)));
  jumps.forEach(btn => btn.addEventListener('click', () => show(btn.dataset.gardenJump, true)));
  lensButtons.forEach(btn => btn.addEventListener('click', () => applyLens(btn.dataset.gardenLens)));

  close?.addEventListener('click', () => {
    panel.hidden = true;
    hotspots.forEach(b => b.classList.remove('is-active'));
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && panel) panel.hidden = true;
  });

  const tour = document.querySelector('[data-garden-tour]');
  const order = ['welcome','house','door','river','life','tim','dwellers','mudtree','sorting','gate','dogs','below'];
  let step = 0;
  tour?.addEventListener('click', () => {
    const key = order[step];
    show(key, true);
    step = (step + 1) % order.length;
    tour.textContent = step === 0 ? 'Walk with Tim' : 'Next stop →';
  });

  applyLens('explore', false);
  show('welcome');
})();