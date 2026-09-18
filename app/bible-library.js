(()=>{
'use strict';

const CATALOG='../../data/christianity/bible-kjv.json';
const WEB_INDEX='../../data/sources/bible-web-book-index.json';
const $=selector=>document.querySelector(selector);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const groups=[
  {id:'pentateuch',label:'Torah (Pentateuch)',description:'Genesis through Deuteronomy: creation, ancestors, Exodus, covenant and Torah.',books:['genesis','exodus','leviticus','numbers','deuteronomy']},
  {id:'history',label:'Historical Books',description:'Israel, monarchy, exile and return in the Protestant Old Testament ordering.',books:['joshua','judges','ruth','1-samuel','2-samuel','1-kings','2-kings','1-chronicles','2-chronicles','ezra','nehemiah','esther']},
  {id:'wisdom',label:'Poetry and Wisdom',description:'Prayer, wisdom, suffering, love poetry and reflection.',books:['job','psalms','proverbs','ecclesiastes','song-of-solomon']},
  {id:'major-prophets',label:'Major Prophets',description:'Isaiah through Daniel, grouped by traditional Christian ordering.',books:['isaiah','jeremiah','lamentations','ezekiel','daniel']},
  {id:'minor-prophets',label:'Twelve Prophets',description:'Hosea through Malachi: the twelve shorter prophetic books.',books:['hosea','joel','amos','obadiah','jonah','micah','nahum','habakkuk','zephaniah','haggai','zechariah','malachi']},
  {id:'apocrypha',label:'KJV Apocrypha',description:'The fourteen-book Apocrypha section printed between the Testaments in the 1611 KJV tradition.',section:'apocrypha'},
  {id:'gospels',label:'Gospels',description:'Four narrative witnesses to Jesus: Matthew, Mark, Luke and John.',books:['matthew','mark','luke','john']},
  {id:'acts',label:'Acts',description:'The early Jesus movement, mission and expansion after the resurrection narratives.',books:['acts']},
  {id:'pauline',label:'Pauline Letters',description:'Romans through Philemon in traditional New Testament ordering.',books:['romans','1-corinthians','2-corinthians','galatians','ephesians','philippians','colossians','1-thessalonians','2-thessalonians','1-timothy','2-timothy','titus','philemon']},
  {id:'general',label:'Hebrews and General Letters',description:'Hebrews, James, Peter, John and Jude. Hebrews is kept separate from Pauline authorship claims.',books:['hebrews','james','1-peter','2-peter','1-john','2-john','3-john','jude']},
  {id:'apocalypse',label:'Revelation',description:'Revelation: letters, visions, judgment, renewal and the New Jerusalem.',books:['revelation']}
];

const state={catalog:null,web:null,section:'all',search:'',selected:null,chapter:1};

function groupFor(book){
  return groups.find(group=>group.section===book.section || group.books?.includes(book.id)) || null;
}

function webReadable(book){
  return Boolean(state.web?.books?.[book.name]);
}

function sectionLabel(section){
  return section==='old'?'Old Testament':section==='new'?'New Testament':'Apocrypha';
}

function filteredBooks(){
  const q=state.search.trim().toLowerCase();
  return state.catalog.books.filter(book=>{
    const sectionOk=state.section==='all'||book.section===state.section;
    const group=groupFor(book);
    const text=`${book.name} ${group?.label||''}`.toLowerCase();
    return sectionOk && (!q||text.includes(q));
  });
}

function renderSummary(){
  const books=state.catalog.books;
  const old=books.filter(book=>book.section==='old').length;
  const apoc=books.filter(book=>book.section==='apocrypha').length;
  const next=books.filter(book=>book.section==='new').length;
  const web=books.filter(webReadable).length;
  $('#bible-library-summary').innerHTML='<strong>'+books.length+' books</strong> in the 1611 KJV arrangement · '+web+' available in the WEB reader · '+apoc+' Apocrypha books kept distinct';
}

function renderGroups(){
  const host=$('#bible-library-groups');
  host.innerHTML=groups.map(group=>{
    const count=state.catalog.books.filter(book=>group.section===book.section||group.books?.includes(book.id)).length;
    return `<button class="bible-group-card" type="button" data-group="${esc(group.id)}">
      <span class="bible-group-count">${count}</span>
      <strong>${esc(group.label)}</strong>
      <span>${esc(group.description)}</span>
    </button>`;
  }).join('');
  host.querySelectorAll('[data-group]').forEach(button=>button.addEventListener('click',()=>{
    const group=groups.find(item=>item.id===button.dataset.group);
    if(!group)return;
    state.section=group.section||'all';
    state.search='';
    const input=$('#bible-book-search'); if(input)input.value='';
    renderTabs();
    renderBooks(group);
  }));
}

function renderTabs(){
  document.querySelectorAll('[data-bible-section]').forEach(button=>{
    const active=button.dataset.bibleSection===state.section;
    button.classList.toggle('is-active',active);
    button.setAttribute('aria-pressed',active?'true':'false');
  });
}

function renderBooks(group=null){
  let books=filteredBooks();
  if(group?.books) books=books.filter(book=>group.books.includes(book.id));
  if(group?.section) books=books.filter(book=>book.section===group.section);
  const host=$('#bible-book-grid');
  $('#bible-book-count').textContent=`${books.length} book${books.length===1?'':'s'}`;
  host.innerHTML=books.length?books.map(book=>{
    const active=state.selected?.id===book.id;
    const groupName=groupFor(book)?.label||sectionLabel(book.section);
    return `<button class="bible-book-card${active?' is-selected':''}" type="button" data-book="${esc(book.id)}">
      <span class="book-section">${esc(groupName)}</span>
      <strong>${esc(book.name)}</strong>
      <span class="book-meta">${book.chapters} chapter${book.chapters===1?'':'s'} · ${webReadable(book)?'WEB text':'catalogue only'}</span>
    </button>`;
  }).join(''):'<p class="bible-library-empty">No books match this filter.</p>';
  host.querySelectorAll('[data-book]').forEach(button=>button.addEventListener('click',()=>selectBook(button.dataset.book,1,true)));
}

function updateUrl(){
  if(!state.selected)return;
  const url=new URL(location.href);
  url.searchParams.set('libraryBook',state.selected.id);
  url.searchParams.set('libraryChapter',String(state.chapter));
  history.replaceState(null,'',url);
}

function renderSelected(){
  const book=state.selected;
  const panel=$('#bible-library-reader');
  if(!book){panel.hidden=true;return}
  panel.hidden=false;
  const group=groupFor(book);
  $('#bible-reader-book').textContent=book.name;
  $('#bible-reader-meta').textContent=`${sectionLabel(book.section)} · ${group?.label||'Book'} · ${book.chapters} chapter${book.chapters===1?'':'s'}`;
  const chapter=$('#bible-reader-chapter');
  chapter.innerHTML=Array.from({length:book.chapters},(_,i)=>`<option value="${i+1}">Chapter ${i+1}</option>`).join('');
  chapter.value=String(Math.min(Math.max(state.chapter,1),book.chapters));
  state.chapter=Number(chapter.value);
  const readable=webReadable(book);
  const read=$('#bible-read-chapter');
  read.disabled=!readable;
  read.textContent=readable?'Read exact WEB chapter':'WEB text unavailable';
  $('#bible-reader-source').innerHTML=readable
    ?'Exact chapter text opens from the <strong>World English Bible</strong> public-domain source. The 80-book catalogue itself records the <strong>1611 KJV arrangement</strong>; these source layers are deliberately not conflated.'
    :'This book is catalogued in the <strong>1611 KJV Apocrypha</strong> section, but it is not in the current 66-book WEB reader index. The atlas keeps that difference visible rather than substituting another text silently.';
  document.querySelectorAll('[data-book]').forEach(button=>button.classList.toggle('is-selected',button.dataset.book===book.id));
  updateUrl();
}

function selectBook(id,chapter=1,update=true){
  const book=state.catalog.books.find(item=>item.id===id);
  if(!book)return;
  state.selected=book;
  state.chapter=Math.min(Math.max(Number(chapter)||1,1),book.chapters);
  renderSelected();
  renderBooks();
  if(update)updateUrl();
}

function openSelected(){
  if(!state.selected||!webReadable(state.selected))return;
  window.BibleScriptureReader?.openReference(`${state.selected.name} ${state.chapter}`);
}

function initEvents(){
  document.querySelectorAll('[data-bible-section]').forEach(button=>button.addEventListener('click',()=>{
    state.section=button.dataset.bibleSection;
    renderTabs(); renderBooks();
  }));
  $('#bible-book-search').addEventListener('input',event=>{state.search=event.target.value;renderBooks()});
  $('#bible-reader-chapter').addEventListener('change',event=>{state.chapter=Number(event.target.value)||1;updateUrl()});
  $('#bible-read-chapter').addEventListener('click',openSelected);
  $('#bible-reference-form').addEventListener('submit',event=>{
    event.preventDefault();
    const value=$('#bible-reference-input').value.trim();
    if(value)window.BibleScriptureReader?.openReference(value);
  });
}

async function init(){
  const root=$('#bible-library');
  if(!root)return;
  try{
    const [catalogResponse,webResponse]=await Promise.all([fetch(CATALOG),fetch(WEB_INDEX)]);
    if(!catalogResponse.ok||!webResponse.ok)throw new Error('Bible catalogue source unavailable');
    state.catalog=await catalogResponse.json();
    state.web=await webResponse.json();
    renderSummary(); renderGroups(); renderTabs(); renderBooks(); initEvents();
    const params=new URL(location.href).searchParams;
    const initial=params.get('libraryBook')||'john';
    const chapter=Number(params.get('libraryChapter'))||1;
    selectBook(initial,chapter,false);
    root.classList.add('is-ready');
  }catch(error){
    root.querySelector('.bible-library-loading').textContent=`Bible library could not load: ${error.message}`;
  }
}

window.BibleLibrary={
  selectBook,
  selectByName:(name,chapter=1)=>{
    if(!state.catalog)return false;
    const book=state.catalog.books.find(item=>item.name===name);
    if(!book)return false;
    selectBook(book.id,chapter,true);
    return true;
  },
  selected:()=>state.selected
};

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();