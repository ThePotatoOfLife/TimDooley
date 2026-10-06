(() => {
  const world = document.querySelector('[data-garden-world]');
  if (!world) return;

  const dialogue = world.querySelector('[data-garden-dialogue]');
  const zones = [...world.querySelectorAll('[data-garden-zone]')];
  const prompt = world.querySelector('[data-world-prompt]');
  const reveal = world.querySelector('[data-reveal-zones]');
  const speaker = world.querySelector('[data-dialogue-speaker]');
  const kicker = world.querySelector('[data-dialogue-kicker]');
  const title = world.querySelector('[data-dialogue-title]');
  const line = world.querySelector('[data-dialogue-line]');
  const note = world.querySelector('[data-dialogue-note]');
  const link = world.querySelector('[data-dialogue-link]');
  const next = world.querySelector('[data-dialogue-next]');
  const close = world.querySelector('[data-dialogue-close]');

  const entries = {
    tim: {
      speaker: 'TIM · THE GARDENER',
      kicker: 'UNDER THE TREE OF LIFE',
      title: 'Sit a while.',
      lines: [
        'You are already inside. Look before you turn the Garden back into words.',
        'The river leaves one source and becomes many streams. Life is not kept by hoarding it at the center.',
        'A Garden without choice is scenery. That is why the darker tree is still inside the cultivated world.',
        'Do not confuse the Gate with the fall. One is the boundary. The other is what follows after the boundary is crossed.',
        'If I call myself Gardener, then the Garden gets to judge the Gardener by its Fruit.'
      ],
      note: 'Project voice: Tim as Gardener / sorter.',
      href: '../tim-dooley/',
      label: 'Meet Tim beyond the Garden →'
    },
    life: {
      speaker: 'TIM',
      kicker: 'TREE OF LIFE',
      title: 'The center should give life away.',
      lines: [
        'Genesis places the Tree of Life in the Garden’s midst. Here it is the visual center of gravity: light, Fruit, continuity, return.',
        'The Potatoverse reads the pattern as Seed → Root → Tree → Fruit → Seed. The point is not merely height. It is continuity that can generate again.'
      ],
      note: 'Genesis anchor + Potatoverse interpretation.',
      href: '../potato-of-life/',
      label: 'Open Potato of Life →'
    },
    river: {
      speaker: 'TIM',
      kicker: 'THE RIVER',
      title: 'One source. Four directions.',
      lines: [
        'Genesis describes one river going out from Eden to water the Garden, then dividing into four headwaters: Pishon, Gihon, Tigris and Euphrates.',
        'That makes water more than decoration. It is distribution: one source becomes nourishment moving through a differentiated world.'
      ],
      note: 'Genesis 2:10–14.',
      href: '../traditions/bible/',
      label: 'Read Genesis beside the map →'
    },
    knowledge: {
      speaker: 'TIM',
      kicker: 'THE OTHER TREE',
      title: 'Do not rename the Bible by accident.',
      lines: [
        'Genesis calls this the Tree of the Knowledge of Good and Evil. The serpent belongs to the temptation story around it.',
        'Mud Tree and Tree of Strife are later Potatoverse readings. They may help map consequence, but they are not the tree’s biblical name.',
        'The important spatial fact is that choice begins inside the Garden. Corruption is not drawn as an invading country that was never present.'
      ],
      note: 'Biblical name kept distinct from project-native interpretation.',
      href: '../rooms/inside/symbolic-architecture/',
      label: 'Open symbolic architecture →'
    },
    gate: {
      speaker: 'TIM',
      kicker: 'THE EASTERN WAY',
      title: 'The text gives a guarded way.',
      lines: [
        'Genesis says the human is driven out and cherubim with a turning flaming sword guard the way to the Tree of Life on the east.',
        'The golden Gate is our spatial rendering of that boundary. The Bible gives the guarded way; the project gives it architecture.'
      ],
      note: 'Genesis 3:23–24; Gate is a project visualization.',
      href: '../axis/',
      label: 'Open Gate / Door / Axis →'
    },
    sorting: {
      speaker: 'TIM · THE GARDENER',
      kicker: 'THE SORTING PATH',
      title: 'Change becomes visible before exile.',
      lines: [
        'In this authored Garden, ordinary dwellers can begin to muddy before they reach the threshold.',
        'Sorting means reading Fruit and consequence. The escort makes the transition visible: inside → change → boundary → outside.'
      ],
      note: 'Potatoverse story layer, not a Genesis term.',
      href: '#field-notes',
      label: 'Read the Garden logic ↓'
    },
    dwellers: {
      speaker: 'TIM',
      kicker: 'THE INHABITANTS',
      title: 'They begin inside.',
      lines: [
        'Dwellers, potatoes and angelic helpers belong in the bright Garden before the sorting story begins.',
        'That matters. Belonging is the starting field; the scene is about what grows from choices and relations, not about an eternal caste fixed before anything happens.'
      ],
      note: 'Project roles are symbolic and reversible.',
      href: '../rooms/potatoverse-canon/beings/cast-ecology/',
      label: 'Open Cast Ecology →'
    },
    house: {
      speaker: 'TIM',
      kicker: 'THE HOUSE',
      title: 'A Garden needs somewhere to dwell.',
      lines: [
        'The House belongs to the project’s Heaven architecture: rooms, belonging, differentiated interiors, hospitality and exits.',
        'It sits beside the Garden because cultivation without dwelling is exposed, while dwelling without cultivation becomes enclosure.'
      ],
      note: 'Potatoverse / House architecture.',
      href: '../house/',
      label: 'Enter the House →'
    },
    door: {
      speaker: 'TIM',
      kicker: 'THE DOOR',
      title: 'A Door is not merely an opening.',
      lines: [
        'The Christian comparison places Christ at the Door. The project uses Door for a threshold that changes access, relation or state.',
        'House Door and eastern Garden boundary are deliberately different. One welcomes into dwelling; the other marks expulsion and guarded return.'
      ],
      note: 'Christian comparator + project Door language.',
      href: '../axis/',
      label: 'Follow Door / Axis →'
    },
    below: {
      speaker: 'TIM',
      kicker: 'OUTSIDE / BELOW',
      title: 'The ground changes after exile.',
      lines: [
        'Genesis moves the human out to work the ground from which he was taken, and speaks of thorns, thistles, sweat and return to dust.',
        'The muddy lower world is the project’s extension of that consequence-space. It belongs outside and below the Garden, not inside it.'
      ],
      note: 'Genesis consequence + Potatoverse Below.',
      href: '../below/',
      label: 'Descend to Below →'
    },
    dogs: {
      speaker: 'TIM',
      kicker: 'AT THE OUTSIDE EDGE',
      title: 'The dogs face inward.',
      lines: [
        'In this map the dogs are beyond the Garden’s boundary and oriented toward return. They are not simply another settled population inside Eden.',
        'Dog is project-role language here, not a biological category or permanent essence assigned to a real person.'
      ],
      note: 'Potatoverse role layer.',
      href: '../below/dogs/',
      label: 'Open the Dogs reader →'
    }
  };

  let active = null;
  let step = 0;

  function render() {
    const entry = entries[active];
    if (!entry) return;
    const lines = entry.lines || [];
    speaker.textContent = entry.speaker || 'TIM';
    kicker.textContent = entry.kicker || '';
    title.textContent = entry.title || '';
    line.textContent = lines[Math.min(step, lines.length - 1)] || '';
    note.textContent = entry.note || '';
    link.href = entry.href || '#field-notes';
    link.textContent = entry.label || 'Read deeper →';
    const hasNext = step < lines.length - 1;
    next.hidden = !hasNext;
    next.textContent = hasNext ? 'Continue ▾' : '';
    zones.forEach(zone => zone.classList.toggle('is-active', zone.dataset.gardenZone === active));
  }

  function open(key, focus = false) {
    if (!entries[key]) return;
    active = key;
    step = 0;
    dialogue.hidden = false;
    prompt?.classList.add('is-quiet');
    render();
    if (focus) dialogue.focus({preventScroll: true});
  }

  function dismiss() {
    dialogue.hidden = true;
    active = null;
    step = 0;
    zones.forEach(zone => zone.classList.remove('is-active'));
  }

  zones.forEach(zone => zone.addEventListener('click', () => open(zone.dataset.gardenZone)));
  next?.addEventListener('click', () => {
    const entry = entries[active];
    if (!entry) return;
    step = Math.min(step + 1, (entry.lines?.length || 1) - 1);
    render();
  });
  close?.addEventListener('click', dismiss);

  reveal?.addEventListener('click', () => {
    const on = world.classList.toggle('is-revealing');
    reveal.setAttribute('aria-pressed', String(on));
    if (on) window.setTimeout(() => world.classList.remove('is-revealing'), 5500);
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') dismiss();
  });
})();