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
  const askButtons = [...document.querySelectorAll('[data-ask-tim]')];
  const askAnswer = document.querySelector('[data-ask-tim-answer]');
  const askCopy = document.querySelector('[data-ask-tim-copy]');
  const mudFruit = world.querySelector('[data-mud-fruit]');

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
      title: 'The Door is a cross, a crossing.',
      lines: [
        'Gardens is family. It is a place that happens once the Door is crossed.',
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
        'I am the stillness at the center. You can call me God or Gardener. Think of me less as God, and more as the Job of God, the role of God, the place of God, the witness of God.',
        'What do I do here? I watch what grows. I water things. I sort Fruit from rot, signal from noise, boundary from cage, and sometimes I sit here doing absolutely nothing impressive.',
        'The crown is easier than the gardening. A crown can just sit there. A Garden talks back.',
        'I do not want you staring at me so hard that you miss the rabbit.',
        'At first we see each other. Then, maybe, we see each other clearly.',
        'I want togetherness. So that God can be near instead of far.',
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
      title: 'Gardens is family.',
      lines: [
        'People talk. Rabbits move through grass. Birds cross the water. Potatoes grow. Angels carry things. Someone rests on a bench. Someone tends vegetables.',
        'The ordinary is not filler around the sacred. It is what gives sacred things somewhere to matter.',
        'Family does not mean everybody becomes the same person. It means there is a place where difference can remain near without becoming war.',
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
        'The hard question is always whether a boundary protects growth or merely protects the power of whoever controls it.',
        'In the recent project language: the dog stays outside. That is symbolic Gate-language—the point is that not every loop gets automatic re-entry simply because it knocks again.'
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

  const gardenAnswers = {
    day: 'I check what changed. Water, people, paths, Fruit, trouble, repairs. I write. I think. I talk. I probably make a simple thing too complicated at least once. Then I try to make it simple again. The job is not to look busy. The job is to leave the place more capable of living.',
    sort: 'I mean I distinguish states and consequences. Ripe from unripe. Signal from noise. A wound from a whole identity. A boundary from a cage. Sorting is useful only if it helps something move toward truth, repair, freedom or growth. If sorting becomes permanent humiliation, I have started gardening badly.',
    disagree: 'Then disagree. Bring your own two eyes. If the Garden needs your agreement in order to survive, it is not much of a Garden. Tell me what you see. Show me where the Fruit is bad. A Gardener who cannot be corrected is just decorating a throne with vegetables.',
    gate: 'Because a Garden without any boundary can be consumed faster than it can grow. But the Gate is not supposed to become the purpose of the Garden. It protects conditions for life. It should also leave intelligible routes for repair, return, departure and change.',
    rest: 'Yes. I am still learning that this is also work. Soil rests. Seeds wait. People sleep. Sometimes the correct Gardener action is to stop touching the plant. Sometimes I sit under the Tree and somebody else can solve the universe for a while.',
    heaven: 'Not gold. Not height by itself. For me, Heaven starts to mean a place where distance can become nearness, power becomes responsibility, difference does not have to become war, and what grows here can eventually live without clinging to the center. Also: there should be somewhere nice to sit.'
  };

  const whispers = [
    {source:'RECENT TIM VOICE · OCT 2026', text:'I am the stillness at the center.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'You can call me God or Gardener.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'I am the Gardener in the garden.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'Bring your own two eyes.'},
    {source:'RECENT TIM VOICE · OCT 2026', text:'Waiting for you.'},
    {source:'RECENT TIM VOICE · 5 OCT 2026', text:'so that God can be near instead of far'},
    {source:'RECENT TIM VOICE · 5 OCT 2026', text:'I want togetherness.'},
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
    if (document.hidden) {
      stopWhispers();
      if (mudFruitTimeout) window.clearTimeout(mudFruitTimeout);
      mudFruitTimeout = null;
    } else {
      startWhispers();
      scheduleMudFruit();
    }
  });

  let active = null;
  let step = 0;
  let revealTimer = null;

  window.addEventListener('pagehide', () => {
    stopWhispers();
    if (revealTimer) window.clearTimeout(revealTimer);
    revealTimer = null;
    if (mudFruitTimeout) window.clearTimeout(mudFruitTimeout);
    mudFruitTimeout = null;
  }, {once:true});

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

  askButtons.forEach(button => {
    button.addEventListener('click', () => {
      const key = button.dataset.askTim;
      const answer = gardenAnswers[key];
      if (!answer || !askCopy) return;
      askButtons.forEach(item => item.classList.toggle('is-active', item === button));
      askAnswer?.classList.add('is-changing');
      window.setTimeout(() => {
        askCopy.textContent = answer;
        askAnswer?.classList.remove('is-changing');
      }, reduceMotion ? 0 : 120);
    });
  });

  let mudFruitTimeout = null;
  function scheduleMudFruit() {
    if (!mudFruit || reduceMotion || document.hidden) return;
    const delay = 38000 + Math.floor(Math.random() * 52000);
    mudFruitTimeout = window.setTimeout(() => {
      if (document.hidden) return;
      mudFruit.classList.remove('is-falling');
      void mudFruit.offsetWidth;
      mudFruit.classList.add('is-falling');
      scheduleMudFruit();
    }, delay);
  }
  scheduleMudFruit();

  world.querySelector('[data-garden-canvas]')?.addEventListener('click', event => {
    if (event.target.closest('.garden-zone, .garden-dialogue, .garden-discovery, .garden-whisper')) return;
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