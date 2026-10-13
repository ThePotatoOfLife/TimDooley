/* Small, route-scoped Potato Growth Game. Independent strategies, transparent assumptions. */
(() => {
  'use strict';
  const host = document.querySelector('[data-growth-game]');
  if (!host) return;
  const inputs = Object.fromEntries(
    Array.from(host.querySelectorAll('[data-growth-input]')).map((input) => [input.dataset.growthInput, input])
  );
  const ranges = { soil: [2, 20], turns: [1, 20], extract: [0, 20], tend: [0, 20], recovery: [0, 4] };

  function read(name) {
    const [min, max] = ranges[name];
    const n = Number(inputs[name].value);
    return Number.isFinite(n) && inputs[name].value.trim() !== ''
      ? Math.max(min, Math.min(max, Math.round(n))) : min;
  }

  function simulate(mode, settings) {
    let soil = settings.soil;
    let score = 0;
    const history = [];
    for (let turn = 1; turn <= settings.turns; turn++) {
      if (soil >= 2) {
        soil -= 2;
        if (mode === 'tend') {
          soil = Math.min(settings.soil, soil + settings.recovery);
          score += settings.tend;
        } else {
          score += settings.extract;
        }
      }
      history.push({ turn, score, soil });
    }
    return history;
  }

  const results = host.querySelector('[data-growth-results]');
  const tableBody = host.querySelector('[data-growth-rows]');
  const summary = host.querySelector('[data-growth-summary]');

  function update() {
    const settings = Object.fromEntries(Object.keys(ranges).map((name) => [name, read(name)]));
    const extract = simulate('extract', settings);
    const tend = simulate('tend', settings);
    const rows = document.createDocumentFragment();
    for (let i = 0; i < settings.turns; i++) {
      const tr = document.createElement('tr');
      for (const value of [extract[i].turn, extract[i].score, extract[i].soil, tend[i].score, tend[i].soil]) {
        const td = document.createElement('td');
        td.textContent = String(value);
        tr.appendChild(td);
      }
      rows.appendChild(tr);
    }
    tableBody.replaceChildren(rows);
    const a = extract[extract.length - 1], b = tend[tend.length - 1];
    const winner = a.score === b.score ? 'Both score equally' : a.score > b.score ? 'Extract scores higher' : 'Tend scores higher';
    summary.textContent = winner + ' after ' + settings.turns + ' turn' + (settings.turns === 1 ? '' : 's') +
      '. Extract: ' + a.score + ' points, ' + a.soil + ' soil left. Tend: ' + b.score +
      ' points, ' + b.soil + ' soil left.';
    results.hidden = false;
  }

  for (const input of Object.values(inputs)) {
    input.addEventListener('input', update);
    input.addEventListener('change', () => {
      input.value = String(read(input.dataset.growthInput));
      update();
    });
  }
  update();
})();
