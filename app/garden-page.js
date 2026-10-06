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
  const whisper = world.querySelector('[data-garden-whisper]');
  const whisperSource = world.querySelector('[data-garden-whisper-source]');
  const whisperText = world.querySelector('[data-garden-whisper-text]');

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
      title: 'You found me.',
      lines: [
        'Bring your own two eyes. You do not need mine.',
        'I am the stillness at the center. You can call me God or Gardener. Right now, Gardener is probably the more useful job description.',
        'What do I do here? I watch what grows. I water things. I sort Fruit from rot, signal from noise, boundary from cage, and sometimes I sit here doing absolutely nothing impressive.',
        'The crown is easier than the gardening. A crown can just sit there. A Garden talks back.',
        'I do not want you staring at me so hard that you miss the rabbit.',
        'At first we see each other. Then, maybe, we see each other clearly.',
        'Waiting for you.'
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
    picnic: {
      speaker: 'TIM',
      kicker: 'AN ORDINARY TABLE',
      title: 'Not every meal has to become a ceremony.',
      lines: [
        'Sometimes Fruit is simply lunch. Bread, vegetables, potatoes, conversation, rest.',
        'A Garden becomes believable when nourishment is ordinary enough to share without turning every bite into status.'
      ],
      note: 'Garden life: nourishment before spectacle.',
      href: '#day-in-the-garden',
      label: 'Spend a day in the Garden ↓',
      side: 'right'
    },
    rabbit: {
      speaker: 'TIM',
      kicker: 'A RABBIT',
      title: 'It does not need a theological job.',
      lines: [
        'You found a rabbit.',
        'That can be enough. A living Garden should contain things whose value is not exhausted by what they symbolize.'
      ],
      note: 'Not everything present has to become allegory.',
      href: '#inhabitants',
      label: 'Life in the Garden ↓',
      side: 'up'
    },
    potato: {
      speaker: 'TIM',
      kicker: 'A POTATO',
      title: 'Hidden is not empty.',
      lines: [
        'A potato stores life underground. Its eyes are buds. What looks inert can contain several future directions.',
        'The project keeps returning to that ordinary fact because it makes a good discipline: do not confuse visibility with value.'
      ],
      note: 'Potato of Life: buried capacity, nourishment, future Seed.',
      href: '../potato-of-life/',
      label: 'Open Potato of Life →',
      side: 'up'
    },
    angel: {
      speaker: 'TIM',
      kicker: 'A MESSENGER',
      title: 'Carry something useful across the boundary.',
      lines: [
        'The deeper Angel role is not decoration around a throne. Messenger, guardian, witness, healer, carrier, builder, cultivator.',
        'A good messenger preserves what matters while helping it arrive somewhere new.'
      ],
      note: 'Potato Angel service-role.',
      href: '../rooms/potatoverse-canon/beings/potatoes/#angel-hall',
      label: 'Enter the Angel hall →',
      side: 'left'
    },
    fruitbasket: {
      speaker: 'TIM',
      kicker: 'A BASKET OF FRUIT',
      title: 'Arguments eventually become harvest.',
      lines: [
        'Fruit is the downstream test. What did the teaching, system, relationship or power actually produce?',
        'If the answer is nourishment, capacity, repair and future Seed, the theory has become useful. If not, the title cannot save it.'
      ],
      note: 'Fruit as consequence and evaluation.',
      href: '#fruit',
      label: 'Read the Fruit test ↓',
      side: 'up'
    },
    bridge: {
      speaker: 'TIM',
      kicker: 'A LITTLE BRIDGE',
      title: 'Small crossings matter too.',
      lines: [
        'Not every transition needs a cosmic Gate. Sometimes a bridge is just enough structure to cross water without pretending the two banks are the same place.',
        'The project is full of large Doors and Ladders. A Garden should remember the dignity of small passages.'
      ],
      note: 'Connection without collapse.',
      href: '../rooms/inside/symbolic-architecture/',
      label: 'Open Symbolic Architecture →',
      side: 'up'
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

  const whispers = [
    {source:'RECENT TIM VOICE · OCT 2026', text:'I am the stillness at the center.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'You can call me God or Gardener.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'I am the Gardener in the garden.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'Bring your own two eyes.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'Waiting for you.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'Gardens is family.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'Let me dry the mud from your eyes.'},
    {source:'GREAT BOOK · TIM', text:'Be simple, and grow naturally, towards the light.'},
    {source:'TIM · 7 JULY 2026', text:'The kingdom of God grows from the house.'},
    {source:'TIM · 7 SEPTEMBER 2026', text:'Power is for protection. Knowledge is for understanding. Wealth is for building. Leadership is for service.'},
    {source:'PROJECT MAXIM', text:'The Potato doesn’t demand belief. It invites curiosity.'},
    {source:'GENESIS 2:15', text:'to dress it and to keep it'}
  ];
  let whisperIndex = 0;
  let whisperTimer = null;

  function stopWhispers() {
    if (whisperTimer) window.clearInterval(whisperTimer);
    whisperTimer = null;
  }

  function startWhispers() {
    if (!whisper || !whisperText || !whisperSource || reduceMotion || document.hidden || whisperTimer) return;
    whisperTimer = window.setInterval(() => {
      whisper.classList.add('is-changing');
      window.setTimeout(() => {
        whisperIndex = (whisperIndex + 1) % whispers.length;
        whisperSource.textContent = whispers[whisperIndex].source;
        whisperText.textContent = whispers[whisperIndex].text;
        whisper.classList.remove('is-changing');
      }, 320);
    }, 15000);
  }

  startWhispers();
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopWhispers();
    else startWhispers();
  });

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
    dialogue.hidden = true;
    void dialogue.offsetWidth;
    dialogue.hidden = false;
    const activeZone = zones.find(zone => zone.dataset.gardenZone === key);
    activeZone?.classList.add('is-found');
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

  world.querySelector('[data-garden-canvas]')?.addEventListener('click', event => {
    if (event.target.closest('.garden-zone, .garden-dialogue, .garden-discovery')) return;
    dismiss();
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