const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const pretty = id => String(id || '').replaceAll('-', ' ').replace(/\b\w/g, c => c.toUpperCase());
const loadJson = async path => { const response = await fetch(path, {cache:'no-store'}); if (!response.ok) throw new Error(`${path} returned HTTP ${response.status}`); return response.json(); };
const optional = async (path, fallback) => { try { return await loadJson(path); } catch { return fallback; } };
const recordLink = (id, label, route='belief.html') => `<a class="belief-record-link" href="${route}?id=${encodeURIComponent(id)}">${esc(label)}</a>`;
const nodeLink = (id, label) => recordLink(id, label, 'node.html');
const uniqueById = records => [...new Map(records.filter(Boolean).map(x => [x.id, x])).values()];

function adjacentRecords(adjBase, ...expansions) {
  return uniqueById([
    ...(adjBase.records || []),
    ...expansions.flatMap(e => e.records || [])
  ]);
}

function renderDirectory(political, religious, foundations, adjacent, foundationIndex) {
  const items = [
    ...(political.entries || []).map(e => ({id:e[0], name:pretty(e[0]), type:'Political', description:e[1], route:'belief.html'})),
    ...(religious.entries || []).map(e => ({id:e[0], name:pretty(e[0]), type:'Religious / worldview', description:e[1], route:'belief.html'})),
    ...(foundations.records || []).map(e => ({id:e.id, name:pretty(e.tradition_id || e.id), type:'Religious foundation', description:e.historical_emergence || e.seed || e.field || 'Foundation / emergence record', route:'node.html'})),
    ...adjacent.map(e => ({id:e.id, name:e.name || pretty(e.id), type:`Religious-adjacent · ${String(e.category || 'research record').replaceAll('_',' ')}`, description:e.field || e.worldview || e.integrity || 'Cultic, mystery, esoteric or related research record.', route:'node.html'})),
    {id:'potatoism', name:'Potatoism', type:'Project-defined symbolic layer', description:'The developing symbolic and mythic framework of The Potato of Life.', route:'belief.html'}
  ];
  $('app').innerHTML = `<section class="belief-directory-head"><span class="belief-type">IDEAS / REFERENCE LAYER</span><h1>Ideas &amp; beliefs.</h1><p>Political ideologies, religious traditions, foundations, cults, mystery traditions, esoteric movements and project-defined concepts are indexed here. Historical reconstruction, community self-description and project symbolism remain separate.</p></section><div class="belief-controls"><input id="belief-search" type="search" placeholder="Search ideas, traditions, cults or definitions…" aria-label="Search ideas"><select id="belief-type" aria-label="Filter ideas"><option value="">All types</option><option value="Political">Political</option><option value="Religious / worldview">Religious / worldview</option><option value="Religious foundation">Religious foundation</option><option value="Religious-adjacent">Religious-adjacent</option><option value="Project-defined symbolic layer">Project-defined</option></select></div><div class="belief-research-summary"><strong>Religious research layers</strong><span>${(foundationIndex.record_count || foundations.records?.length || 0)} foundation/adjacent index records · ${(adjacent.length)} cultic / mystery / esoteric records · ${foundationIndex.deep_expansion_records || 0} deep expansion records</span></div><div id="belief-list" class="belief-list"></div>`;
  const draw = () => {
    const q = $('belief-search').value.trim().toLowerCase();
    const type = $('belief-type').value;
    const visible = items.filter(item => (!q || `${item.name} ${item.id} ${item.description} ${item.type}`.toLowerCase().includes(q)) && (!type || item.type === type || (type === 'Religious-adjacent' && item.type.startsWith('Religious-adjacent'))));
    $('belief-count').textContent = visible.length;
    $('belief-list').innerHTML = visible.map(item => `<article class="belief-row"><div><span class="belief-type">${esc(item.type)}</span><h2>${recordLink(item.id, item.name, item.route)}</h2></div><p>${esc(item.description)}</p></article>`).join('') || '<p class="empty-state">No ideas match the current filter.</p>';
  };
  $('belief-search').addEventListener('input', draw);
  $('belief-type').addEventListener('change', draw);
  draw();
}

function renderRecord(id, political, religious, potatoism, foundations, adjacent) {
  const pe = (political.entries || []).find(e => e[0] === id);
  const re = (religious.entries || []).find(e => e[0] === id);
  const foundation = (foundations.records || []).find(x => x.tradition_id === id || x.id === id);
  const adjacentRecord = adjacent.find(x => x.id === id);
  if (!pe && !re && !foundation && !adjacentRecord && id !== 'potatoism') { $('app').innerHTML = `<section class="belief-error"><span class="belief-type">IDEAS</span><h1>Belief not found</h1><p>The requested identifier <code>${esc(id)}</code> is not currently in the atlas.</p><a class="belief-back" href="belief.html">← Browse Ideas</a></section>`; return; }
  if (pe) { document.title = `${pretty(id)} — Political Belief`; $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Political ideology</span><h1>${esc(pretty(id))}</h1><p class="record-lead">${esc(pe[1])}</p><h2>Analytical coordinates</h2><div class="coords"><span>Economic <b>${esc(pe[2])}</b></span><span>Authority <b>${esc(pe[3])}</b></span><span>Quadrant <b>${esc(pe[4])}</b></span></div><p class="note">Coordinates are visualization approximations, not a complete definition of an ideology or its adherents.</p><a class="belief-back" href="belief.html">← All ideas</a></section>`; return; }
  if (id === 'potatoism') { document.title = 'Potatoism — The Potato of Life'; $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Project-defined contemporary religious / mythic system</span><h1>Potatoism</h1><p class="record-lead">${esc(potatoism.epistemic_note || '')}</p><h2>Birth / seed</h2><div class="mini"><strong>${esc(potatoism.birth?.date)}</strong><br>${esc(potatoism.birth?.meaning)}</div><h2>Growing timeline</h2><div class="timeline">${(potatoism.timeline || []).map(x => `<article><strong>${esc(x.period || x.stage)}</strong><p>${esc(x.stage || '')}</p><div>${esc(x.description || '')}</div></article>`).join('')}</div><h2>Symbolic architecture</h2><div class="belief-grid">${Object.entries(potatoism.core_architecture || {}).map(([k,v]) => `<div class="mini"><strong>${esc(k)}</strong><p>${esc(Array.isArray(v) ? v.join(' · ') : JSON.stringify(v))}</p></div>`).join('')}</div><p class="note">The birth marker is treated as the seed of the timeline, not as the date on which the finished architecture existed.</p><a class="belief-back" href="belief.html">← All ideas</a></section>`; return; }
  if (adjacentRecord) { document.title = `${adjacentRecord.name} — Religious-Adjacent Research`; const summary = typeof adjacentRecord.worldview === 'string' ? adjacentRecord.worldview : adjacentRecord.field || adjacentRecord.integrity || ''; const categories = Object.entries(adjacentRecord).filter(([k,v]) => !['id','name','category','period','field','worldview','integrity','description'].includes(k) && v !== null && v !== undefined && v !== '').slice(0,12); $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Religious-adjacent research · ${esc(String(adjacentRecord.category || 'research').replaceAll('_',' '))}</span><h1>${esc(adjacentRecord.name || pretty(id))}</h1><p class="record-lead">${esc(summary || 'A populated research record in the religious-adjacent layer.')}</p><div class="mini"><strong>Historical scope</strong><p>${esc(adjacentRecord.period || 'Period recorded in the research layer')}</p><p>${esc(adjacentRecord.field || '')}</p></div><h2>Research record</h2><div class="belief-grid">${categories.map(([k,v]) => `<div class="mini"><strong>${esc(pretty(k))}</strong><p>${esc(Array.isArray(v) ? v.join(' · ') : typeof v === 'object' ? JSON.stringify(v) : v)}</p></div>`).join('')}</div><p class="note">This classification is analytical. “Cult”, “occult”, “sect” and related categories do not by themselves imply legitimacy, danger or truth. Ancient practices, modern revivals and outsider accusations are kept separate.</p><p><a class="belief-back" href="node.html?id=${encodeURIComponent(id)}">Open full Atlas record →</a></p><a class="belief-back" href="belief.html">← All ideas</a></section>`; return; }
  if (foundation) { document.title = `${pretty(foundation.tradition_id || foundation.id)} — Religious Foundation`; const foundationHtml = `<h2>Foundation / emergence</h2><div class="mini"><strong>${esc(foundation.foundation_type || 'historical formation')}</strong><p><b>Field:</b> ${esc(foundation.field)}</p><p><b>Substrate:</b> ${esc((foundation.substrate || []).join(' · '))}</p><p><b>Seed:</b> ${esc(foundation.seed)}</p><p><b>Historical emergence:</b> ${esc(foundation.historical_emergence)}</p><p class="note">${esc(foundation.uncertainty)}</p></div>`; $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Religious foundation layer</span><h1>${esc(pretty(foundation.tradition_id || foundation.id))}</h1><p class="record-lead">A time-aware emergence record. A tradition may have multiple clocks rather than one founding moment.</p>${foundationHtml}<p><a class="belief-back" href="node.html?id=${encodeURIComponent(foundation.id)}">Open full foundation record →</a></p><a class="belief-back" href="belief.html">← All ideas</a></section>`; return; }
  const foundationHtml = foundation ? `<h2>Foundation / emergence</h2><div class="mini"><strong>${esc(foundation.foundation_type)}</strong><p><b>Field:</b> ${esc(foundation.field)}</p><p><b>Substrate:</b> ${esc((foundation.substrate || []).join(' · '))}</p><p><b>Seed:</b> ${esc(foundation.seed)}</p><p><b>Historical emergence:</b> ${esc(foundation.historical_emergence)}</p><p class="note">${esc(foundation.uncertainty)}</p></div>` : '';
  document.title = `${re[0]} — Religious Worldview`;
  $('app').innerHTML = `<section class="belief-record"><span class="belief-type">Religious tradition / worldview</span><h1>${esc(re[0])}</h1><p class="record-lead">${esc(re[1])}</p>${foundationHtml}<h2>Research layers</h2><p class="note">The main lexicon supplies the concise definition. Foundation, history, texts, practices, places, institutions, branches and evidence live in separate layers.</p><p><a class="belief-back" href="node.html?id=${encodeURIComponent(id)}">Open full Atlas record →</a></p><a class="belief-back" href="political-compass.html#${encodeURIComponent(id)}">Locate this tradition in Belief Space →</a><br><a class="belief-back" href="belief.html">← All ideas</a></section>`;
}

async function init() {
  const id = new URLSearchParams(location.search).get('id');
  try {
    const [political, religious, potatoism, foundations, foundationIndex, adjacentBase, adjacent1, adjacent2, adjacent3] = await Promise.all([
      loadJson('data/political-lexicon.json'),
      loadJson('data/religious-lexicon.json'),
      loadJson('data/potatoism-religion.json'),
      loadJson('data/religious-foundations.json'),
      optional('data/religious-foundations/index.json', {}),
      optional('data/religious-adjacent/records.json', {records:[]}),
      optional('data/religious-adjacent/deep-expansions.json', {records:[]}),
      optional('data/religious-adjacent/deep-expansions-2.json', {records:[]}),
      optional('data/religious-adjacent/deep-expansions-3.json', {records:[]})
    ]);
    const adjacent = adjacentRecords(adjacentBase, adjacent1, adjacent2, adjacent3);
    if (id) renderRecord(id, political, religious, potatoism, foundations, adjacent); else renderDirectory(political, religious, foundations, adjacent, foundationIndex);
  } catch (error) { $('app').innerHTML = `<section class="belief-error"><span class="belief-type">IDEAS</span><h1>Belief data unavailable</h1><p>A belief data layer could not be loaded: ${esc(error.message)}</p></section>`; }
}
init();
