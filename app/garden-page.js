(() => {
  const world = document.querySelector('[data-garden-world]');
  if (!world) return;

  const dialogue = world.querySelector('[data-garden-dialogue]');
  const zones = [...world.querySelectorAll('[data-garden-zone]')];
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
    knowledge: {
      speaker: 'TIM',
      kicker: 'MUD TREE',
      title: 'The darker tree is still inside the Garden.',
      lines: [
        'Genesis calls the second tree the Tree of the Knowledge of Good and Evil. The serpent belongs to the temptation story around it.',
        'Mud Tree is the project’s interpretive name for the shadowed downward vector: appetite, recurrence, muddying, consequence.'
      ],
      note: 'Biblical name and project reading remain distinct.',
      href: '../rooms/inside/symbolic-architecture/',
      label: 'Open symbolic architecture →'
    },
    gate: {
      speaker: 'TIM',
      kicker: 'THE GATE',
      title: 'The boundary is visible.',
      lines: [
        'Genesis gives expulsion and a guarded way back toward the Tree of Life.',
        'The golden Gate is the project’s spatial rendering of that threshold: the bright Garden on one side, consequence beyond it.'
      ],
      note: 'Genesis 3:23–24 + project visualization.',
      href: '../axis/',
      label: 'Open Gate / Door / Axis →'
    },
    house: {
      speaker: 'TIM',
      kicker: 'THE HOUSE',
      title: 'A Garden needs somewhere to dwell.',
      lines: [
        'The House carries rooms, belonging, hospitality, differentiated interiors and exits.',
        'Cultivation without dwelling is exposed. Dwelling without cultivation becomes enclosure.'
      ],
      note: 'Potatoverse / House architecture.',
      href: '../house/',
      label: 'Enter the House →'
    },
    door: {
      speaker: 'TIM',
      kicker: 'THE DOOR',
      title: 'The Door changes access.',
      lines: [
        'The Christian comparison places Christ at the Door. The project uses Door for a threshold that changes relation, access or state.',
        'The House Door and the eastern Gate are deliberately different: one welcomes into dwelling; the other marks expulsion and guarded return.'
      ],
      note: 'Christian comparator + project Door language.',
      href: '../axis/',
      label: 'Follow Door / Axis →'
    },
    dogs: {
      speaker: 'TIM',
      kicker: 'MUD DWELLERS',
      title: 'Below the bright Garden, the ground changes.',
      lines: [
        'The lower muddy world is the project’s consequence-space: darker ground, repetition, burden, and distance from the central Tree.',
        'It is shown as part of one continuous geography, not as a separate universe unrelated to what happens above.'
      ],
      note: 'Potatoverse lower-world layer.',
      href: '../below/',
      label: 'Descend to Below →'
    }
  };

  let active = null;
  let step = 0;

  function render() {
    const entry = entries[active];
    if (!entry) return;
    const lines = entry.lines || [];
    dialogue.dataset.dialogueZone = active || '';
    speaker.textContent = entry.speaker || 'TIM';
    kicker.textContent = entry.kicker || '';
    title.textContent = entry.title || '';
    line.textContent = lines[Math.min(step, lines.length - 1)] || '';
    note.textContent = entry.note || '';
    link.href = entry.href || '#field-notes';
    link.textContent = entry.label || 'Read deeper →';
    const hasNext = step < lines.length - 1;
    next.hidden = !hasNext;
    next.textContent = hasNext ? 'Continue →' : '';
    zones.forEach(zone => zone.classList.toggle('is-active', zone.dataset.gardenZone === active));
  }

  function open(key, focus = false) {
    if (!entries[key]) return;
    if (active === key && !dialogue.hidden) {
      dismiss();
      return;
    }
    active = key;
    step = 0;
    dialogue.hidden = false;
    render();
    if (focus) dialogue.focus({preventScroll:true});
  }

  function dismiss() {
    dialogue.hidden = true;
    dialogue.dataset.dialogueZone = '';
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

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') dismiss();
  });
})();