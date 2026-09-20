(()=>{'use strict';
const CONFIG_URL=(document.currentScript&&document.currentScript.dataset&&document.currentScript.dataset.newsConfig)||null;
const DEFAULT_CONFIG=CONFIG_URL||((location.pathname.includes('/news/'))?'../data/news/sources.json':'data/news/sources.json');
const CACHE_PREFIX='potato-news-v1:';
const CACHE_TTL=10*60*1000;
const MAX_FEED=28;
const $=(sel,root=document)=>root.querySelector(sel);
const $$=(sel,root=document)=>Array.from(root.querySelectorAll(sel));
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const clean=v=>String(v??'').replace(/\s+/g,' ').trim();
function safeUrl(v){try{const u=new URL(v);return /^https?:$/.test(u.protocol)?u.href:''}catch(_){return''}}
function domain(v){try{return new URL(v).hostname.replace(/^www\./,'')}catch(_){return''}}
function gdeltDate(v){
 const s=String(v||'');
 const m=s.match(/^(\d{4})(\d{2})(\d{2})T?(\d{2})(\d{2})(\d{2})Z?$/);
 if(m)return new Date(Date.UTC(+m[1],+m[2]-1,+m[3],+m[4],+m[5],+m[6]));
 const d=new Date(s);return isNaN(d)?null:d;
}
function relativeTime(value){
 const d=value instanceof Date?value:new Date(value); if(isNaN(d))return'';
 const sec=Math.round((Date.now()-d.getTime())/1000),a=Math.abs(sec);
 if(a<60)return 'now';
 if(a<3600)return Math.floor(a/60)+'m ago';
 if(a<86400)return Math.floor(a/3600)+'h ago';
 if(a<604800)return Math.floor(a/86400)+'d ago';
 return d.toLocaleDateString(undefined,{month:'short',day:'numeric'});
}
function stamp(value){const d=value instanceof Date?value:new Date(value);return isNaN(d)?0:d.getTime()}
async function fetchJson(url,timeout=8500){
 const ctrl=new AbortController();const id=setTimeout(()=>ctrl.abort(),timeout);
 try{const r=await fetch(url,{signal:ctrl.signal,headers:{'Accept':'application/json'}});if(!r.ok)throw new Error('HTTP '+r.status);return await r.json()}
 finally{clearTimeout(id)}
}
function readCache(key){
 try{const raw=localStorage.getItem(CACHE_PREFIX+key);if(!raw)return null;const row=JSON.parse(raw);if(Date.now()-row.saved>CACHE_TTL)return null;return row.value}catch(_){return null}
}
function writeCache(key,value){try{localStorage.setItem(CACHE_PREFIX+key,JSON.stringify({saved:Date.now(),value}))}catch(_){}}
async function cached(key,loader,force=false){if(!force){const hit=readCache(key);if(hit)return hit}const value=await loader();writeCache(key,value);return value}
function normalizeGdelt(a){
 const url=safeUrl(a.url||a.url_mobile);if(!url||!a.title)return null;
 const date=gdeltDate(a.seendate||a.date||a.datetime);
 return {id:'gdelt:'+url,title:clean(a.title),url,source:clean(a.domain)||domain(url),provider:'GDELT',providerId:'gdelt',published:date?date.toISOString():'',summary:'',kind:'publisher',language:clean(a.language),country:clean(a.sourcecountry)};
}
async function loadGdelt(query,force){
 const p=new URLSearchParams({query:query||'(international OR world)',mode:'artlist',maxrecords:'40',format:'json',sort:'datedesc',timespan:'24h'});
 return cached('gdelt:'+p.get('query'),async()=>{const data=await fetchJson('https://api.gdeltproject.org/api/v2/doc/doc?'+p.toString());return (data.articles||data.results||[]).map(normalizeGdelt).filter(Boolean)},force);
}
function normalizeSpace(a){
 const url=safeUrl(a.url);if(!url||!a.title)return null;
 return {id:'space:'+String(a.id||url),title:clean(a.title),url,source:clean(a.news_site)||domain(url),provider:'Spaceflight News',providerId:'spaceflight-news',published:a.published_at||a.updated_at||'',summary:clean(a.summary||''),kind:'publisher'};
}
async function loadSpace(force){
 return cached('space',async()=>{const data=await fetchJson('https://api.spaceflightnewsapi.net/v4/articles/?limit=18&ordering=-published_at');return (data.results||[]).map(normalizeSpace).filter(Boolean)},force);
}
function normalizeHn(a){
 if(!a||a.type!=='story'||!a.title)return null;const url=safeUrl(a.url)||('https://news.ycombinator.com/item?id='+encodeURIComponent(a.id));
 return {id:'hn:'+a.id,title:clean(a.title),url,source:a.url?domain(a.url):'news.ycombinator.com',provider:'Hacker News',providerId:'hacker-news',published:a.time?new Date(a.time*1000).toISOString():'',summary:'',kind:'community'};
}
async function loadHn(force){
 return cached('hn:new',async()=>{const ids=await fetchJson('https://hacker-news.firebaseio.com/v0/newstories.json');const slice=(ids||[]).slice(0,22);const rows=await Promise.allSettled(slice.map(id=>fetchJson('https://hacker-news.firebaseio.com/v0/item/'+id+'.json',6000)));return rows.filter(x=>x.status==='fulfilled').map(x=>normalizeHn(x.value)).filter(Boolean)},force);
}
function dedupe(rows){
 const seen=new Set();return rows.filter(r=>{const key=(r.url||'').replace(/[?#].*$/,'').replace(/\/$/,'')||r.title.toLowerCase();if(seen.has(key))return false;seen.add(key);return true}).sort((a,b)=>stamp(b.published)-stamp(a.published));
}
async function getConfig(){const r=await fetch(DEFAULT_CONFIG,{headers:{'Accept':'application/json'}});if(!r.ok)throw new Error('Could not load news source contract');return r.json()}
function sourceState(host,id,state,label){const el=$('[data-provider="'+id+'"]',host);if(el){el.dataset.state=state;const s=$('span',el);if(s&&label)s.textContent=label}}
async function providerLoad(host,id,query,force){
 sourceState(host,id,'loading');
 try{
   let rows=[];
   if(id==='gdelt')rows=await loadGdelt(query,force);
   else if(id==='hacker-news')rows=await loadHn(force);
   else if(id==='spaceflight-news')rows=await loadSpace(force);
   sourceState(host,id,'ok');return rows;
 }catch(err){sourceState(host,id,'error');return []}
}
function storyCard(r,lead=false){
 const summary=r.summary?'<p>'+esc(r.summary.slice(0,lead?330:190))+(r.summary.length>(lead?330:190)?'…':'')+'</p>':'';
 const country=r.country?'<span>'+esc(r.country)+'</span>':'';
 return '<article class="news-story'+(lead?' news-story--lead':'')+'">'+
 '<div class="news-story-kicker"><span>'+esc(r.provider)+'</span><i></i><span>'+esc(r.kind==='community'?'community link':'publisher link')+'</span></div>'+
 (lead?'<h2>':'<h3>')+esc(r.title)+(lead?'</h2>':'</h3>')+summary+
 '<div class="news-story-footer"><span>'+esc(r.source||'source')+'</span>'+country+'<span>'+esc(relativeTime(r.published))+'</span>'+
 '<a href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer">Original source ↗</a></div></article>';
}
function renderFull(host,rows){
 const lead=$('[data-news-lead]',host),feed=$('[data-news-list]',host),count=$('[data-news-count]',host),updated=$('[data-news-updated]',host);
 if(count)count.textContent=rows.length+' items';
 if(updated)updated.textContent='refreshed '+new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
 if(!rows.length){if(lead)lead.innerHTML='';if(feed)feed.innerHTML='<div class="news-empty">No live items reached the browser from the selected feeds. Try refresh, another category, or the original source links below.</div>';return}
 if(lead)lead.innerHTML=storyCard(rows[0],true)+(rows[1]?storyCard(rows[1],false):'');
 if(feed)feed.innerHTML=rows.slice(2,MAX_FEED).map(r=>storyCard(r,false)).join('');
}
function renderPreview(host,rows,limit){
 const grid=$('[data-news-preview-grid]',host);if(!grid)return;
 const take=rows.slice(0,limit);
 grid.innerHTML=take.length?take.map(r=>'<a class="news-preview-item" href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer"><small>'+esc(r.provider)+' · '+esc(r.source)+'</small><b>'+esc(r.title)+'</b><span>'+esc(relativeTime(r.published))+'</span></a>').join(''):'<div class="news-empty">Live preview unavailable. The full News page can retry each source independently.</div>';
}
async function bootFull(host,config){
 const tabs=$('[data-news-tabs]',host),input=$('[data-news-search]',host),form=$('form.news-search',host),refresh=$('[data-news-refresh]',host);
 const params=new URLSearchParams(location.search);let category=params.get('category')||host.dataset.newsCategory||'all';let custom=clean(params.get('q')||'');let force=false;
 function categoryRow(){return (config.categories||[]).find(x=>x.id===category)||(config.categories||[])[0]}
 function setPressed(){$$('[data-news-category]',tabs).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.newsCategory===category)))}
 async function run(){
   const cat=categoryRow()||{};const query=custom||cat.gdelt_query||'(international OR world)';const providers=custom?['gdelt']:(cat.providers||['gdelt']);
   $$('[data-provider]',host).forEach(el=>{el.dataset.state=providers.includes(el.dataset.provider)?'loading':'idle'});
   const groups=await Promise.all(providers.map(id=>providerLoad(host,id,query,force)));force=false;
   renderFull(host,dedupe(groups.flat()));
 }
 tabs&&tabs.addEventListener('click',e=>{const b=e.target.closest('[data-news-category]');if(!b)return;category=b.dataset.newsCategory;custom='';if(input)input.value='';setPressed();history.replaceState(null,'','?category='+encodeURIComponent(category));run()});
 form&&form.addEventListener('submit',e=>{e.preventDefault();custom=clean(input.value);if(!custom)return;category='custom';setPressed();history.replaceState(null,'','?q='+encodeURIComponent(custom));run()});
 refresh&&refresh.addEventListener('click',()=>{force=true;run()});
 if(input&&custom)input.value=custom;setPressed();await run();
}
async function bootPreview(host,config){
 const cat=(config.categories||[]).find(x=>x.id===(host.dataset.newsCategory||'all'))||(config.categories||[])[0]||{};
 const requested=(host.dataset.newsProviders||'').split(',').map(x=>x.trim()).filter(Boolean);
 const providers=requested.length?requested:(cat.providers||['gdelt']);
 const groups=await Promise.all(providers.map(id=>providerLoad(host,id,cat.gdelt_query,false)));
 renderPreview(host,dedupe(groups.flat()),Math.max(1,Math.min(6,Number(host.dataset.newsLimit)||3)));
}
async function boot(){
 const hosts=$$('[data-news-feed]');if(!hosts.length)return;
 let config;try{config=await getConfig()}catch(err){hosts.forEach(h=>{const target=$('[data-news-list],[data-news-preview-grid]',h);if(target)target.innerHTML='<div class="news-empty">News configuration could not be loaded.</div>'});return}
 hosts.forEach(host=>{if(host.dataset.newsMode==='preview')bootPreview(host,config);else bootFull(host,config)});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();