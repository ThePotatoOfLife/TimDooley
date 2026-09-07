const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const books = [
  {id:'genesis',title:'Genesis',hebrew:'בראשית',ref:'Genesis',chapters:50},
  {id:'exodus',title:'Exodus',hebrew:'שמות',ref:'Exodus',chapters:40},
  {id:'leviticus',title:'Leviticus',hebrew:'ויקרא',ref:'Leviticus',chapters:27},
  {id:'numbers',title:'Numbers',hebrew:'במדבר',ref:'Numbers',chapters:36},
  {id:'deuteronomy',title:'Deuteronomy',hebrew:'דברים',ref:'Deuteronomy',chapters:34}
];
let state = {book:0, chapter:1};
const api = ref => `https://www.sefaria.org/api/v3/texts/${encodeURIComponent(ref)}?version=source&version=translation&return_format=text_only`;
function renderBooks(){
  const q = ($('torah-search').value || '').toLowerCase();
  $('torah-books').innerHTML = books.filter(b => `${b.title} ${b.hebrew}`.toLowerCase().includes(q)).map((b,i) => `<button class="bible-book ${i===state.book?'active':''}" data-book="${i}"><span>${esc(b.title)}</span><small>${esc(b.hebrew)} · ${b.chapters} chapters</small></button>`).join('');
  document.querySelectorAll('[data-book]').forEach(x => x.addEventListener('click', () => { state.book=Number(x.dataset.book); state.chapter=1; renderBooks(); loadChapter(); }));
}
function textFromVersion(version){
  if (!version) return '';
  const text = version.text || version.chapter || version.content || '';
  return Array.isArray(text) ? text.join('\n') : String(text);
}
function renderText(data){
  const versions = data.versions || [];
  const hebrew = versions.find(v => String(v.language||'').toLowerCase().startsWith('hebrew')) || versions.find(v => /hebrew|source/i.test(v.versionTitle||''));
  const english = versions.find(v => String(v.language||'').toLowerCase().startsWith('english')) || versions.find(v => /english|translation/i.test(v.versionTitle||''));
  const blocks = [];
  if (hebrew) blocks.push(`<section class="torah-language torah-hebrew" dir="rtl"><h3>Hebrew · ${esc(hebrew.versionTitle || 'Source text')}</h3><p>${esc(textFromVersion(hebrew))}</p></section>`);
  if (english) blocks.push(`<section class="torah-language"><h3>English · ${esc(english.versionTitle || 'Translation')}</h3><p>${esc(textFromVersion(english))}</p></section>`);
  if (!blocks.length) blocks.push('<p class="empty-state">No text edition was returned for this chapter.</p>');
  $('torah-text').innerHTML = blocks.join('');
  const names = versions.map(v => v.versionTitle).filter(Boolean).join(' · ');
  $('torah-status').textContent = names ? `Text editions returned: ${names}` : 'Text loaded from Sefaria.';
}
async function loadChapter(){
  const book = books[state.book];
  const ref = `${book.ref} ${state.chapter}`;
  $('torah-location').textContent = `${book.title} ${state.chapter} · ${book.hebrew}`;
  $('torah-title').textContent = `${book.title} ${state.chapter}`;
  $('torah-status').textContent = 'Loading text…';
  $('torah-text').innerHTML = '<p>Retrieving the chapter…</p>';
  $('torah-prev').disabled = state.book===0 && state.chapter===1;
  $('torah-next').disabled = state.book===books.length-1 && state.chapter===book.chapters;
  try { const r = await fetch(api(ref), {cache:'no-store'}); if(!r.ok) throw new Error(`HTTP ${r.status}`); renderText(await r.json()); }
  catch(e){ $('torah-status').textContent='Text service unavailable'; $('torah-text').innerHTML=`<p class="empty-state">The Torah catalogue is available, but this chapter could not be retrieved right now. ${esc(e.message)}</p><p><a href="https://www.sefaria.org/${encodeURIComponent(ref)}">Open ${esc(ref)} on Sefaria →</a></p>`; }
}
function move(delta){
  const book=books[state.book];
  if(delta>0){ if(state.chapter<book.chapters) state.chapter++; else if(state.book<books.length-1){state.book++;state.chapter=1;} }
  else { if(state.chapter>1) state.chapter--; else if(state.book>0){state.book--;state.chapter=books[state.book].chapters;} }
  renderBooks(); loadChapter();
}
$('torah-search').addEventListener('input', renderBooks);
$('torah-prev').addEventListener('click',()=>move(-1));
$('torah-next').addEventListener('click',()=>move(1));
renderBooks(); loadChapter();
