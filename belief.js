const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const pretty = id => String(id || '').replaceAll('-', ' ').replace(/\b\w/g, c => c.toUpperCase());
const loadJson = async path => { const response = await fetch(path, {cache:'no-store'}); if (!response.ok) throw new Error(`${path} returned HTTP ${response.status}`); return response.json(); };
const recordLink = (id, label) => `<a class="belief-record-link" href="belief.html?id=${encodeURIComponent(id)}">${esc(label)}</a>`;

function renderDirectory(political, religious) {
  const items = [
    ...(political.entries || []).map(e => ({id:e[0], name:pretty(e[0]), type:'Political', description:e[1]})),
    ...(religious.entries || []).map(e => ({id:e[0], name:pretty(e[0]), type:'Religious / worldview', description:e[1]})),
    {id:'potatoism', name:'Potatoism', type:'Project-defined symbolic layer', description:'The developing symbolic and mythic framework of The Potato of Life.'}
  ];
  $('app').innerHTML = `<section class="belief-directory-head"><span class="belief-type">IDEAS / REFERENCE LAYER</span><h1>Ideas &amp; beliefs.</h1><p>Political ideologies, religious traditions and project-defined concepts are indexed here as descriptive records. Interpretation stays separate from empirical evidence.</p></section><div class="belief-controls"><input id="belief-search" type="search" placeholder="Search ideas, traditions or definitions…" aria-label="Search ideas"><select id="belief-type" aria-label="Filter ideas"><option value="">All types</option><option value="Political">Political</option><option value="Religious / worldview">Religious / worldview</option><option value="Project-defined symbolic layer">Project-defined</option></select></div><div id="belief-list" class="belief-list"></div>`;
  const draw = () => {
    const q = $('belief-search').value.trim().toLowerCase();
    const type = $('belief-type').value;
    const visible = items.filter(item => (!q || `${item.name} ${item.id} ${item.description}`.toLowerCase().includes(q)) && (!type || item.type === type));
    $('belief-count').textContent = visible.length;
    $('belief-list').innerHTML = visible.map(item => `<article class="belief-row"><div><span class="belief-type">${esc(item.type)}</span><h2>${recordLink(item.id, item.name)}</h2></div><p>${esc(item.description)}</p></article>`).join('') || '<p class="empty-state">No ideas match the current filter.</p>';
  };
  $('belief-search').addEventListener('input', draw);
  $('belief-type').addEventListener('change', draw);
  draw();
}

function renderRecord(id, political, religious, potatoism, foundations) {
  const pe = (political.entries || []).find(e => e[0] === id);
  const re = (religious.entries || []).find(e => e[0] === id);
  const foundation = (foundations.records || []).find(x => x.tradition_id === id);
  if (!pe && !re && id !== 'potatoism') { $('app').innerHTML = `<section class="belief-error"><span class="belief-type">IDEAS</span><h1>Belief not found</h1><p>The requested identifier <code>${esc(id)}</code> is not currently in the atlas.</p><a class="belief-back" href="belief.html">← Browse Ideas</a></section>`; return; }
  if (pe) { document.title = `${pretty(id)} — Political Belief`; $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Political ideology</span><h1>${esc(pretty(id))}</h1><p class="record-lead">${esc(pe[1])}</p><h2>Analytical coordinates</h2><div class="coords"><span>Economic <b>${esc(pe[2])}</b></span><span>Authority <b>${esc(pe[3])}</b></span><span>Quadrant <b>${esc(pe[4])}</b></span></div><p class="note">Coordinates are visualization approximations, not a complete definition of an ideology or its adherents.</p><a class="belief-back" href="belief.html">← All ideas</a></section>`; return; }
  if (id === 'potatoism') { document.title = 'Potatoism — The Potato of Life'; $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Project-defined contemporary religious / mythic system</span><h1>Potatoism</h1><p class="record-lead">${esc(potatoism.epistemic_note || '')}</p><h2>Birth / seed</h2><div class="mini"><strong>${esc(potatoism.birth?.date)}</strong><br>${esc(potatoism.birth?.meaning)}</div><h2>Growing timeline</h2><div class="timeline">${(potatoism.timeline || []).map(x => `<article><strong>${esc(x.period || x.stage)}</strong><p>${esc(x.stage || '')}</p><div>${esc(x.description || '')}</div></article>`).join('')}</div><h2>Symbolic architecture</h2><div class="belief-grid">${Object.entries(potatoism.core_architecture || {}).map(([k,v]) => `<div class="mini"><strong>${esc(k)}</strong><p>${esc(Array.isArray(v) ? v.join(' · ') : JSON.stringify(v))}</p></div>`).join('')}</div><p class="note">The birth marker is treated as the seed of the timeline, not as the date on which the finished architecture existed.</p><a class="belief-back" href="belief.html">← All ideas</a></section>`; return; }
  document.title = `${re[0]} — Religious Worldview`;
  const foundationHtml = foundation ? `<h2>Foundation / emergence</h2><div class="mini"><strong>${esc(foundation.foundation_type)}</strong><p><b>Field:</b> ${esc(foundation.field)}</p><p><b>Substrate:</b> ${esc((foundation.substrate || []).join(' · '))}</p><p><b>Seed:</b> ${esc(foundation.seed)}</p><p><b>Historical emergence:</b> ${esc(foundation.historical_emergence)}</p><p class="note">${esc(foundation.uncertainty)}</p></div>` : '';
  $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Religious tradition / worldview</span><h1>${esc(re[0])}</h1><p class="record-lead">${esc(re[1])}</p>${foundationHtml}<h2>Worldview space</h2><p class="note">The religious cube is an analytical projection. Foundation, history, texts, practices, places, institutions, branches and evidence remain separate layers.</p><a class="belief-back" href="political-compass.html#${encodeURIComponent(id)}">Locate this tradition in Belief Space →</a><br><a class="belief-back" href="belief.html">← All ideas</a></section>`;
}

async function init() {
  const id = new URLSearchParams(location.search).get('id');
  try {
    const [political, religious, potatoism, foundations] = await Promise.all([loadJson('data/political-lexicon.json'), loadJson('data/religious-lexicon.json'), loadJson('data/potatoism-religion.json'), loadJson('data/religious-foundations.json')]);
    if (id) renderRecord(id, political, religious, potatoism, foundations); else renderDirectory(political, religious);
  } catch (error) { $('app').innerHTML = `<section class="belief-error"><span class="belief-type">IDEAS</span><h1>Belief data unavailable</h1><p>A belief data layer could not be loaded: ${esc(error.message)}</p></section>`; }
}
init();
