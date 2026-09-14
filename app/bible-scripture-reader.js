(()=>{
'use strict';
const INDEX='../../data/sources/bible-web-book-index.json';
const cache=new Map();
let indexPromise=null;
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cleanHtml=html=>{
  if(typeof DOMParser==='undefined')return String(html||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
  const doc=new DOMParser().parseFromString(String(html||''),'text/html');
  return doc.body.textContent.replace(/\u00a0/g,' ').replace(/^\s*\d+\s*/,'').trim();
};
async function index(){if(!indexPromise)indexPromise=fetch(INDEX).then(r=>{if(!r.ok)throw new Error(`WEB book index: ${r.status}`);return r.json()});return indexPromise}
function bookPrefix(reference,bookNames){
  const ref=String(reference||'').replace(/[–—]/g,'-').trim();
  const names=[...(bookNames||[])].sort((a,b)=>String(b).length-String(a).length);
  const found=names.find(name=>ref===name||ref.startsWith(name+' '));
  if(!found)throw new Error(`Unknown Bible book in reference: ${reference}`);
  return found;
}
function point(chapter,verse){return {chapter:Number(chapter),verse:verse==null?null:Number(verse)}}
function splitReferences(value){return String(value||'').split(';').map(part=>part.replace(/[–—]/g,'-').trim()).filter(Boolean)}
function parseReference(reference,bookNames){
  const ref=String(reference||'').replace(/[–—]/g,'-').trim();
  if(!ref)throw new Error('Empty Bible reference');
  const book=bookPrefix(ref,bookNames),rest=ref.slice(book.length).trim();
  if(!rest)throw new Error(`Missing chapter/verse in reference: ${reference}`);
  const parts=rest.split(',').map(x=>x.trim()).filter(Boolean),selectors=[];
  let inheritedChapter=null;
  for(const raw of parts){
    let m=raw.match(/^(\d+):(\d+)\s*-\s*(\d+):(\d+)$/);
    if(m){selectors.push({start:point(m[1],m[2]),end:point(m[3],m[4])});inheritedChapter=Number(m[3]);continue;}
    m=raw.match(/^(\d+):(\d+)\s*-\s*(\d+)$/);
    if(m){selectors.push({start:point(m[1],m[2]),end:point(m[1],m[3])});inheritedChapter=Number(m[1]);continue;}
    m=raw.match(/^(\d+):(\d+)$/);
    if(m){selectors.push({start:point(m[1],m[2]),end:point(m[1],m[2])});inheritedChapter=Number(m[1]);continue;}
    m=raw.match(/^(\d+)\s*-\s*(\d+)$/);
    if(m&&inheritedChapter){selectors.push({start:point(inheritedChapter,m[1]),end:point(inheritedChapter,m[2])});continue;}
    m=raw.match(/^(\d+)$/);
    if(m&&inheritedChapter){selectors.push({start:point(inheritedChapter,m[1]),end:point(inheritedChapter,m[1])});continue;}
    if(m){const ch=Number(m[1]);selectors.push({start:point(ch,null),end:point(ch,null)});inheritedChapter=ch;continue;}
    throw new Error(`Malformed Bible reference segment: ${raw}`);
  }
  return {book,selectors,reference:ref};
}
function verseRecord(item){const match=String(item.title||'').match(/^(.*?)\s+(\d+):(\d+)$/);return match?{book:match[1],chapter:Number(match[2]),verse:Number(match[3]),text:cleanHtml(item.content)}:null}
async function loadBook(book){
  if(cache.has(book))return cache.get(book);
  const meta=await index(),number=meta.books?.[book];
  if(!number)throw new Error(`Unknown WEB book: ${book}`);
  const url=meta.upstream_template.replace('{book_no}',number);
  const promise=fetch(url).then(r=>{if(!r.ok)throw new Error(`${book}: ${r.status}`);return r.json()}).then(items=>items.map(verseRecord).filter(Boolean));
  cache.set(book,promise);return promise;
}
function cmp(v,p){if(v.chapter!==p.chapter)return v.chapter-p.chapter;if(p.verse==null)return 0;return v.verse-p.verse}
function inSelector(v,s){if(s.start.verse==null&&s.end.verse==null)return v.chapter===s.start.chapter;return cmp(v,s.start)>=0&&cmp(v,s.end)<=0}
function selectVerses(verses,parsed){return (verses||[]).filter(v=>parsed.selectors.some(s=>inSelector(v,s)))}
async function referenceVerses(reference){
  const parts=splitReferences(reference);
  if(!parts.length)throw new Error('Empty Bible reference');
  if(parts.length>1){const groups=await Promise.all(parts.map(referenceVerses));return {reference:String(reference).trim(),book:groups[0]?.book||'',groups,verses:groups.flatMap(group=>group.verses)}}
  const meta=await index(),parsed=parseReference(parts[0],Object.keys(meta.books||{})),verses=await loadBook(parsed.book);
  return {reference:parsed.reference,book:parsed.book,groups:null,verses:selectVerses(verses,parsed)};
}
function spanParts(scene){const reference=splitReferences(scene.canonical_span||scene.book)[0]||scene.book;const parsed=parseReference(reference,Object.keys(scene._bookNames||{[scene.book]:true}));const chapters=parsed.selectors.flatMap(s=>[s.start.chapter,s.end.chapter]);return {book:parsed.book,startChapter:Math.min(...chapters),endChapter:Math.max(...chapters)}}
async function sceneVerses(scene){const reference=scene.canonical_span||scene.book;return (await referenceVerses(reference)).verses}
function renderVersesHTML(result){let lastKey=null;return result.verses.map(v=>{const key=`${v.book}:${v.chapter}`,head=key!==lastKey?(lastKey=key,`<h4 class="inline-scripture-chapter">${esc(v.book)} ${v.chapter}</h4>`):'';return `${head}<p class="scripture-verse"><sup>${v.verse}</sup> ${esc(v.text)}</p>`}).join('')}
function dialog(){let node=document.getElementById('bible-scripture-dialog');if(node)return node;node=document.createElement('dialog');node.id='bible-scripture-dialog';node.className='scripture-dialog';node.innerHTML='<div class="scripture-dialog-inner"><header><div><span class="dossier-kicker">World English Bible · public domain</span><h2 id="scripture-dialog-title">Scripture</h2></div><button type="button" class="scripture-close" aria-label="Close Scripture">×</button></header><div id="scripture-dialog-body" class="scripture-dialog-body"></div></div>';node.querySelector('.scripture-close').addEventListener('click',()=>node.close());node.addEventListener('click',event=>{if(event.target===node)node.close()});document.body.appendChild(node);return node}
async function openReference(reference){const node=dialog(),title=node.querySelector('#scripture-dialog-title'),body=node.querySelector('#scripture-dialog-body');title.textContent=reference;body.innerHTML='<p class="scripture-loading">Loading exact WEB text…</p>';node.showModal();try{const result=await referenceVerses(reference);if(!result.verses.length)throw new Error('No verses resolved');body.innerHTML=renderVersesHTML(result)}catch(error){body.innerHTML=`<p class="scripture-error">Could not load the WEB source text. ${esc(error.message)}</p>`}}
async function openScene(scene){return openReference(scene.canonical_span||scene.title||scene.book)}
const api={loadBook,splitReferences,parseReference,selectVerses,referenceVerses,sceneVerses,openReference,openScene,renderVersesHTML,spanParts};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
if(typeof window!=='undefined')window.BibleScriptureReader=api;
})();
