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
  const reveal = world.querySelector('[data-reveal-zones]');
  const talkTim = document.querySelector('[data-talk-tim]');
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

  const entries = {
    house: {
      speaker: 'TIM · THE GARDENER',
      kicker: 'THE HOUSE',
      title: 'A Garden needs somewhere to dwell.',
      lines: [
        'The House is not the Garden, but they need one another. Rooms hold difference; the Garden gives that difference somewhere to grow.',
        'A good House makes room without turning every boundary into a prison. A good Garden gives life enough structure to become capable on its own.'
      ],
      note: 'House / Garden relation inside the Potato House.',
      href: '../house/',
      label: 'Enter the House →',
      side: 'right'
    },
    jesus: {
      speaker: 'TIM',
      kicker: 'JESUS · THE DOOR',
      title: 'Door and Gate are not the same threshold.',
      lines: [
        'The Christian comparison places Christ at the Door: entry, relation, recognition, passage into dwelling.',
        'The eastern Gate belongs to another movement. It guards the way after exile. One welcomes into House; one protects a boundary around Life.'
      ],
      note: 'Christian comparator + project Door language.',
      href: '../axis/',
      label: 'Follow Door / Gate / Ladder →',
      side: 'right'
    },
    life: {
      speaker: 'TIM',
      kicker: 'TREE OF LIFE',
      title: 'The center should be able to give life away.',
      lines: [
        'Genesis places the Tree of Life in the Garden’s midst. It is central without being everything.',
        'The project reads its pattern as Seed → Root → Tree → Fruit → Seed: continuity that can generate again.',
        'If everything has to remain permanently attached to the center, the center has stopped behaving like Life and started behaving like dependency.'
      ],
      note: 'Genesis anchor + Potatoverse interpretation.',
      href: '../potato-of-life/',
      label: 'Open Potato of Life →',
      side: 'up'
    },
    tim: {
      speaker: 'TIM · THE GARDENER',
      kicker: 'BENEATH THE TREE',
      title: 'Sit a while.',
      lines: [
        'You are already inside. Look before you turn the Garden back into words.',
        'Gardening is not standing over life. It is learning what helps it grow, what harms it, what needs pruning, what needs time, and what should be allowed to become independent.',
        'I sort by Fruit. What did the teaching make? What did the power do? What did the relation leave another being capable of doing?',
        'A title can impress a room. A Garden can judge the title.',
        'If I call myself Gardener, the Garden gets to judge the Gardener by its Fruit.'
      ],
      note: 'Project voice: Tim as Gardener / philosopher-king.',
      href: '../tim-dooley/',
      label: 'Meet Tim beyond the Garden →',
      side: 'up'
    },
    river: {
      speaker: 'TIM',
      kicker: 'THE RIVER',
      title: 'One source. Then movement.',
      lines: [
        'Genesis gives one river going out from Eden to water the Garden, then dividing into four headwaters.',
        'That is a good image for a living center: nourishment leaves the source. Water, knowledge, attention and opportunity circulate.',
        'A Garden where everything pools forever around one point has become something else.'
      ],
      note: 'Genesis 2:10–14 + Garden circulation model.',
      href: '#genesis',
      label: 'Read the Genesis walk ↓',
      side: 'up'
    },
    residents: {
      speaker: 'TIM',
      kicker: 'LIFE IN THE GARDEN',
      title: 'Heaven should have ordinary days.',
      lines: [
        'People talk. Rabbits move through grass. Birds cross the water. Potatoes grow. Angels carry things. Someone rests on a bench. Someone tends vegetables.',
        'The ordinary is not filler around the sacred. It is what gives sacred things somewhere to matter.',
        'Belonging comes before sorting. A resident is not born as a permanent verdict.'
      ],
      note: 'Garden inhabitants: people, animals, Potatoes, Angels, guests.',
      href: '#inhabitants',
      label: 'Meet the inhabitants ↓',
      side: 'right'
    },
    knowledge: {
      speaker: 'TIM',
      kicker: 'THE OTHER TREE · MUD',
      title: 'Choice belongs inside the Garden.',
      lines: [
        'Genesis calls this the Tree of the Knowledge of Good and Evil. “Mud Tree” is the project’s later reading, not the Bible’s name.',
        'Mud means residue, recurrence, stuckness and unprocessed consequence. But mud can also become soil.',
        'The important thing is not pretending the dark possibility never existed. It is what gets done with what grows from it.'
      ],
      note: 'Biblical tree kept distinct from Potatoverse Mud interpretation.',
      href: '#fall',
      label: 'Read the Fall / Mud section ↓',
      side: 'left'
    },
    gate: {
      speaker: 'TIM',
      kicker: 'THE EASTERN GATE',
      title: 'A boundary changes what can happen next.',
      lines: [
        'Genesis says the human is driven out and cherubim guard the way to the Tree of Life on the east.',
        'The project renders that protected way as a Gate. The Gate does not need to be hatred. A boundary can preserve life, consequence and meaningful return.',
        'The hard question is always whether a boundary protects growth or merely protects the power of whoever controls it.'
      ],
      note: 'Genesis 3:23–24 + project Gate architecture.',
      href: '../axis/',
      label: 'Open the Living Axis →',
      side: 'left'
    },
    below: {
      speaker: 'TIM',
      kicker: 'THE WAY DOWN',
      title: 'The bright surface is not the whole structure.',
      lines: [
        'Heaven is raised because the Garden is not the whole map. Roots, history, residue, consequences and unresolved material continue below the visible crown.',
        'Descent is not automatically evil. Roots descend too. The question is whether what goes down can be metabolized and returned as something more alive.',
        'Below without return becomes a prison. Heaven without roots becomes decoration.'
      ],
      note: 'House / Axis / Below relation.',
      href: '../below/',
      label: 'Descend to Below →',
      side: 'left'
    }
  };

  let active = null;
  let step = 0;
  let revealTimer = null;

  function render() {
    const entry = entries[active];
    if (!entry) return;
    const lines = entry.lines || [];
    dialogue.dataset.dialogueZone = active || '';
    dialogue.dataset.dialogueSide = entry.side || 'right';
    speaker.textContent = entry.speaker || 'TIM';
    kicker.textContent = entry.kicker || '';
    title.textContent = entry.title || '';
    line.textContent = lines[Math.min(step, lines.length - 1)] || '';
    note.textContent = entry.note || '';
    link.href = entry.href || '#genesis';
    link.textContent = entry.label || 'Walk deeper →';
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

  zones.forEach(zone => {
    zone.addEventListener('click', () => open(zone.dataset.gardenZone));
    zone.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        open(zone.dataset.gardenZone, true);
      }
    });
  });

  next?.addEventListener('click', () => {
    const entry = entries[active];
    if (!entry) return;
    step = Math.min(step + 1, (entry.lines?.length || 1) - 1);
    render();
  });

  close?.addEventListener('click', dismiss);
  talkTim?.addEventListener('click', () => {
    document.querySelector('#garden-map')?.scrollIntoView({behavior: reduceMotion ? 'auto' : 'smooth', block:'start'});
    window.setTimeout(() => open('tim', true), reduceMotion ? 0 : 450);
  });

  reveal?.addEventListener('click', () => {
    const on = !world.classList.contains('is-revealing');
    world.classList.toggle('is-revealing', on);
    reveal.setAttribute('aria-pressed', String(on));
    reveal.textContent = on ? 'hide clues' : 'show clues';
    if (revealTimer) window.clearTimeout(revealTimer);
    if (on) {
      revealTimer = window.setTimeout(() => {
        world.classList.remove('is-revealing');
        reveal.setAttribute('aria-pressed', 'false');
        reveal.textContent = 'show clues';
      }, 7000);
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') dismiss();
  });

  const revealSections = [...document.querySelectorAll('[data-garden-reveal]')];
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entriesList => {
      entriesList.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {threshold:.12, rootMargin:'0px 0px -6% 0px'});
    revealSections.forEach(section => observer.observe(section));
  } else {
    revealSections.forEach(section => section.classList.add('is-visible'));
  }
})();