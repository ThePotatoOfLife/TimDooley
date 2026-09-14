(()=>{
'use strict';
const INDEX='../../data/sources/bible-web-book-index.json';
const cache=new Map();
let indexPromise=null;
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cleanHtml=html=>{const doc=new DOMParser().parseFromString(String(html||''),'text/html');return doc.body.textContent.replace(/\u00a0/g,' ').replace(/^\s*\d+\s*/,'').trim()};
async function index(){if(!indexPromise)indexPromise=fetch(INDEX).then(r=>{if(!r.ok)throw new Error(`WEB book index: ${r.status}`);return r.json()});return indexPromise}
async function loadBook(book){if(cache.has(book))return cache.get(book);const meta=await index(),number=meta.books?.[book];if(!number)throw new Error(`Unknown WEB book: ${book}`);const url=meta.upstream_template.replace('{book_no}',number),promise=fetch(url).then(r=>{if(!r.ok)throw new Error(`${book}: ${r.status}`);return r.json()});cache.set(book,promise);return promise}
function spanParts(scene){
 const book=scene.book,span=String(scene.canonical_span||''),rest=span.startsWith(book)?span.slice(book.length).trim():span;
 const numbers=[...rest.matchAll(/(\d+)(?::(\d+))?/g)].map(match=>({chapter:Number(match[1]),verse:match[2]?Number(match[2]):null}));
 const start=numbers[0]?.chapter||1,end=numbers.length>1&&rest.includes('-')?numbers[numbers.length-1].chapter:start;
 return {book,startChapter:start,endChapter:Math.max(start,end)};
}
function verseRecord(item){const match=String(item.title||'').match(/^(.*?)\s+(\d+):(\d+)$/);return match?{book:match[1],chapter:Number(match[2]),verse:Number(match[3]),text:cleanHtml(item.content)}:null}
async function sceneVerses(scene){const range=spanParts(scene),items=await loadBook(range.book);return items.map(verseRecord).filter(Boolean).filter(v=>v.chapter>=range.startChapter&&v.chapter<=range.endChapter)}
function dialog(){let node=document.getElementById('bible-scripture-dialog');if(node)return node;node=document.createElement('dialog');node.id='bible-scripture-dialog';node.className='scripture-dialog';node.innerHTML='<div class="scripture-dialog-inner"><header><div><span class="dossier-kicker">World English Bible · public domain</span><h2 id="scripture-dialog-title">Scripture</h2></div><button type="button" class="scripture-close" aria-label="Close Scripture">×</button></header><div id="scripture-dialog-body" class="scripture-dialog-body"></div></div>';node.querySelector('.scripture-close').addEventListener('click',()=>node.close());node.addEventListener('click',event=>{if(event.target===node)node.close()});document.body.appendChild(node);return node}
async function openScene(scene){const node=dialog(),title=node.querySelector('#scripture-dialog-title'),body=node.querySelector('#scripture-dialog-body');title.textContent=scene.canonical_span||scene.title;body.innerHTML='<p class="scripture-loading">Loading exact WEB text…</p>';node.showModal();try{const verses=await sceneVerses(scene);if(!verses.length)throw new Error('No verses resolved');let lastChapter=null;body.innerHTML=verses.map(v=>{const head=v.chapter!==lastChapter?(lastChapter=v.chapter,`<h3>${esc(v.book)} ${v.chapter}</h3>`):'';return `${head}<p class="scripture-verse"><sup>${v.verse}</sup> ${esc(v.text)}</p>`}).join('')}catch(error){body.innerHTML=`<p class="scripture-error">Could not load the WEB source text. ${esc(error.message)}</p>`}}
window.BibleScriptureReader={loadBook,sceneVerses,openScene,spanParts};
})();
