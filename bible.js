const CATALOG='data/christianity/bible-kjv.json';
const MIRROR='https://raw.githubusercontent.com/aruljohn/Bible-kjv-1611/main/';
const MIRROR_NAMES={'ecclesiasticus / sirach':'Ecclesiasticus','bel and the dragon':'Bel and the Dragon','prayer of manasses':'Prayer of Manasseh'};
let catalog=null,book=null,chapter=1,bookData=null;
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const params=()=>new URLSearchParams(location.search);
const bookIdFromUrl=()=>params().get('book')||'';
const chapterFromUrl=()=>Math.max(1,Number(params().get('chapter')||1));
const updateUrl=()=>book&&history.replaceState(null,'',`bible.html?book=${encodeURIComponent(book.id)}&chapter=${chapter}`);
function renderBooks(q=''){
  const rows=(catalog.books||[]).filter(b=>b.name.toLowerCase().includes(q.toLowerCase()));
  const groups=[['old','Old Testament'],['apocrypha','Apocrypha'],['new','New Testament']];
  $('bible-books').innerHTML=groups.map(([key,label])=>{
    const group=rows.filter(b=>b.section===key||b.testament===key);if(!group.length)return '';
    return `<section class="bible-book-group"><h3>${label}</h3>${group.map(b=>`<button class="bible-book${book?.id===b.id?' active':''}" data-book="${esc(b.id)}"><span>${esc(b.name)}</span><small>${b.chapters} ch.</small></button>`).join('')}</section>`;
  }).join('')||'<p class="empty-state">No books match.</p>';
  document.querySelectorAll('.bible-book').forEach(x=>x.onclick=()=>selectBook(x.dataset.book));
}
function renderChapterSelect(){
  if(!book)return;
  $('bible-chapter').innerHTML=Array.from({length:book.chapters},(_,i)=>`<option value="${i+1}">Chapter ${i+1}</option>`).join('');
  $('bible-chapter').value=String(chapter);$('bible-chapter').disabled=false;
}
async function selectBook(id,requestedChapter=1){
  const found=catalog.books.find(b=>b.id===id);if(!found)return;
  book=found;chapter=Math.min(Math.max(1,requestedChapter),book.chapters);bookData=null;
  renderBooks($('bible-search').value);renderChapterSelect();updateUrl();
  $('bible-status').textContent=`Loading ${book.name}…`;
  const mirrorName=MIRROR_NAMES[book.name.toLowerCase()]||book.name;
  try{
    const response=await fetch(MIRROR+encodeURIComponent(mirrorName)+'.json',{cache:'force-cache'});
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    bookData=await response.json();renderChapter();
  }catch(error){
    $('bible-status').innerHTML=`The complete catalogue is present, but this particular text could not be fetched from the browser reader mirror. <a href="https://www.gutenberg.org/ebooks/30" target="_blank" rel="noopener">Open the complete KJV source</a>.`;
    $('bible-text').innerHTML=`<div class="reader-error"><h3>${esc(book.name)}</h3><p>The reader source is unavailable from this browser right now; the catalogue itself is not missing.</p><p><a class="bible-source-button" href="https://www.gutenberg.org/ebooks/30" target="_blank" rel="noopener">Open complete KJV →</a></p></div>`;
  }
}
function renderChapter(){
  if(!book||!bookData)return;
  const current=(bookData.chapters||[]).find(c=>Number(c.chapter)===chapter);
  if(!current){$('bible-status').textContent='Chapter data was not found for this catalogue entry.';return;}
  $('bible-location').textContent=`${book.name} ${chapter}`;
  $('bible-title').textContent='King James Version';
  $('bible-status').textContent=`${book.name} · Chapter ${chapter} · 1611 KJV text`;
  $('bible-text').innerHTML=(current.verses||[]).map(v=>`<p class="bible-verse"><sup>${esc(v.verse)}</sup> ${esc(v.text)}</p>`).join('')||'<p>No verse data returned.</p>';
  $('prev-chapter').disabled=chapter<=1;$('next-chapter').disabled=chapter>=book.chapters;$('bible-chapter').value=String(chapter);updateUrl();
}
async function init(){
  try{
    catalog=await fetch(CATALOG,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('catalog');return r.json()});
    $('bible-search').oninput=e=>renderBooks(e.target.value);
    $('bible-chapter').onchange=e=>{chapter=Number(e.target.value);renderChapter()};
    $('prev-chapter').onclick=()=>{if(chapter>1){chapter--;renderChapter()}};
    $('next-chapter').onclick=()=>{if(book&&chapter<book.chapters){chapter++;renderChapter()}};
    $('bible-home').onclick=()=>{history.replaceState(null,'','bible.html');book=null;bookData=null;chapter=1;renderBooks();$('bible-location').textContent='Select a book';$('bible-title').textContent='King James Version';$('bible-status').textContent='Select a book to begin reading.';$('bible-text').innerHTML='<p>Select a book to begin reading.</p>';$('bible-chapter').innerHTML='<option>Chapter</option>';$('bible-chapter').disabled=true};
    renderBooks();
    const initial=bookIdFromUrl();
    if(initial)await selectBook(initial,chapterFromUrl());
  }catch(e){$('bible-status').textContent='The Bible catalogue could not be loaded.';}
}
init();