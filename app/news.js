(()=>{'use strict';
const CONFIG_URL=(document.currentScript&&document.currentScript.dataset&&document.currentScript.dataset.newsConfig)||null;
const DEFAULT_CONFIG=CONFIG_URL||((location.pathname.includes('/news/'))?'../data/news/sources.json':'data/news/sources.json');
const CACHE_PREFIX='potato-news-v2:';
const CACHE_TTL=10*60*1000;
const $=(sel,root=document)=>root.querySelector(sel);
const $$=(sel,root=document)=>Array.from(root.querySelectorAll(sel));
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const clean=v=>String(v??'').replace(/\s+/g,' ').trim();
const STOP=new Set('a an and are as at be been being but by for from has have had in into is it its of on or that the their this to was were will with after before amid over under new says say said amid about against'.split(' '));
function safeUrl(v){try{const u=new URL(v);return /^https?:$/.test(u.protocol)?u.href:''}catch(_){return''}}
function domain(v){try{return new URL(v).hostname.replace(/^www\./,'')}catch(_){return''}}
function gdeltDate(v){const s=String(v||'');const m=s.match(/^(\d{4})(\d{2})(\d{2})T?(\d{2})(\d{2})(\d{2})Z?$/);if(m)return new Date(Date.UTC(+m[1],+m[2]-1,+m[3],+m[4],+m[5],+m[6]));const d=new Date(s);return isNaN(d)?null:d}
function stamp(v){const d=v instanceof Date?v:new Date(v);return isNaN(d)?0:d.getTime()}
function relativeTime(v){const d=v instanceof Date?v:new Date(v);if(isNaN(d))return'';const a=Math.max(0,Math.round((Date.now()-d.getTime())/1000));if(a<60)return'now';if(a<3600)return Math.floor(a/60)+'m ago';if(a<86400)return Math.floor(a/3600)+'h ago';if(a<604800)return Math.floor(a/86400)+'d ago';return d.toLocaleDateString(undefined,{month:'short',day:'numeric'})}
function horizonMs(config,id){return Number((config.horizons||[]).find(x=>x.id===id)?.milliseconds)||86400000}
function horizonSpan(config,id){return (config.horizons||[]).find(x=>x.id===id)?.gdelt_timespan||'24h'}
function horizonLabel(config,id){return (config.horizons||[]).find(x=>x.id===id)?.label||id}
function trimToHorizon(rows,ms){const cutoff=Date.now()-ms;return rows.filter(r=>!r.published||stamp(r.published)>=cutoff)}
async function fetchJson(url,timeout=9000){const ctrl=new AbortController();const id=setTimeout(()=>ctrl.abort(),timeout);try{const r=await fetch(url,{signal:ctrl.signal,headers:{Accept:'application/json'}});if(!r.ok)throw new Error('HTTP '+r.status);return await r.json()}finally{clearTimeout(id)}}
function readCache(key){try{const raw=localStorage.getItem(CACHE_PREFIX+key);if(!raw)return null;const row=JSON.parse(raw);if(Date.now()-row.saved>CACHE_TTL)return null;return row.value}catch(_){return null}}
function writeCache(key,value){try{localStorage.setItem(CACHE_PREFIX+key,JSON.stringify({saved:Date.now(),value}))}catch(_){}}
async function cached(key,loader,force=false){if(!force){const hit=readCache(key);if(hit)return hit}const value=await loader();writeCache(key,value);return value}
function normalizeGdelt(a){const url=safeUrl(a.url||a.url_mobile);if(!url||!a.title)return null;const date=gdeltDate(a.seendate||a.date||a.datetime);return{id:'gdelt:'+url,title:clean(a.title),url,source:clean(a.domain)||domain(url),provider:'GDELT',providerId:'gdelt',published:date?date.toISOString():'',summary:'',kind:'publisher',language:clean(a.language),country:clean(a.sourcecountry)}}
async function loadGdelt(query,timespan,force){const p=new URLSearchParams({query:query||'(international OR world)',mode:'artlist',maxrecords:'75',format:'json',sort:'datedesc',timespan:timespan||'24h'});return cached('gdelt:'+p.toString(),async()=>{const data=await fetchJson('https://api.gdeltproject.org/api/v2/doc/doc?'+p.toString());return(data.articles||data.results||[]).map(normalizeGdelt).filter(Boolean)},force)}
function plainHtml(value){try{const doc=new DOMParser().parseFromString(String(value||''),'text/html');return clean(doc.body?.textContent||'')}catch(_){return clean(String(value||'').replace(/<[^>]*>/g,' '))}}
function rssImage(item){const candidates=[item?.thumbnail,item?.enclosure?.link,item?.enclosure?.url];for(const value of candidates){const url=safeUrl(value);if(url)return url}return''}
function normalizePublisherRss(item,feed,maxChars=520){
 const url=safeUrl(item?.link);if(!url||!item?.title)return null;
 const summary=plainHtml(item.description||item.content||'').slice(0,maxChars);
 const d=new Date(String(item.pubDate||item.published||''));const published=isNaN(d)?'':d.toISOString();
 return{id:'rss:'+feed.id+':'+(item.guid||url),title:clean(item.title),url,source:feed.name,provider:'Publisher RSS',providerId:'publisher-rss',published,summary,image:rssImage(item),kind:'publisher-excerpt',categories:Array.isArray(item.categories)?item.categories:[],feedId:feed.id};
}
async function loadPublisherRss(config,category,force){
 const feeds=(config.publisher_feeds||[]).filter(feed=>!Array.isArray(feed.categories)||feed.categories.includes(category)||category==='all');
 const maxChars=Number(config.presentation?.publisher_excerpt_max_chars)||520;
 const settled=await Promise.allSettled(feeds.map(feed=>cached('rss:'+feed.id,async()=>{
   const endpoint='https://api.rss2json.com/v1/api.json?rss_url='+encodeURIComponent(feed.feed_url);
   const data=await fetchJson(endpoint,9000);
   if(data.status&&data.status!=='ok')throw new Error(data.message||('RSS adapter '+data.status));
   return(data.items||[]).map(item=>normalizePublisherRss(item,feed,maxChars)).filter(Boolean);
 },force)));
 const successful=settled.filter(x=>x.status==='fulfilled');
 if(feeds.length&&successful.length===0)throw new Error('All publisher RSS feeds failed');
 return successful.flatMap(x=>x.value);
}
function normalizeOfficialRss(item,feed,maxChars=520){
 const row=normalizePublisherRss(item,feed,maxChars);if(!row)return null;
 row.id='official:'+feed.id+':'+(item.guid||row.url);row.provider='Official releases';row.providerId='official-rss';row.kind='primary-source';row.image='';return row;
}
async function loadOfficialRss(config,category,force){
 const feeds=(config.official_feeds||[]).filter(feed=>!Array.isArray(feed.categories)||feed.categories.includes(category));
 const maxChars=Number(config.presentation?.publisher_excerpt_max_chars)||520;
 const settled=await Promise.allSettled(feeds.map(feed=>cached('official-rss:'+feed.id,async()=>{
   const endpoint='https://api.rss2json.com/v1/api.json?rss_url='+encodeURIComponent(feed.feed_url);
   const data=await fetchJson(endpoint,9000);
   if(data.status&&data.status!=='ok')throw new Error(data.message||('RSS adapter '+data.status));
   return(data.items||[]).map(item=>normalizeOfficialRss(item,feed,maxChars)).filter(Boolean);
 },force)));
 const successful=settled.filter(x=>x.status==='fulfilled');
 if(feeds.length&&successful.length===0)throw new Error('All official RSS feeds failed');
 return successful.flatMap(x=>x.value);
}
function normalizeSpace(a){const url=safeUrl(a.url);if(!url||!a.title)return null;return{id:'space:'+String(a.id||url),title:clean(a.title),url,source:clean(a.news_site)||domain(url),provider:'Spaceflight News',providerId:'spaceflight-news',published:a.published_at||a.updated_at||'',summary:clean(a.summary||''),kind:'publisher'}}
async function loadSpace(force){return cached('space',async()=>{const data=await fetchJson('https://api.spaceflightnewsapi.net/v4/articles/?limit=45&ordering=-published_at');return(data.results||[]).map(normalizeSpace).filter(Boolean)},force)}
function normalizeHn(a){if(!a||a.type!=='story'||!a.title)return null;const url=safeUrl(a.url)||('https://news.ycombinator.com/item?id='+encodeURIComponent(a.id));return{id:'hn:'+a.id,title:clean(a.title),url,source:a.url?domain(a.url):'news.ycombinator.com',provider:'Hacker News',providerId:'hacker-news',published:a.time?new Date(a.time*1000).toISOString():'',summary:'',kind:'community'}}
async function loadHn(force){return cached('hn:new',async()=>{const ids=await fetchJson('https://hacker-news.firebaseio.com/v0/newstories.json');const rows=await Promise.allSettled((ids||[]).slice(0,60).map(id=>fetchJson('https://hacker-news.firebaseio.com/v0/item/'+id+'.json',6500)));return rows.filter(x=>x.status==='fulfilled').map(x=>normalizeHn(x.value)).filter(Boolean)},force)}
function dedupe(rows){const seen=new Set();return rows.filter(r=>{const key=(r.url||'').replace(/[?#].*$/,'').replace(/\/$/,'')||r.title.toLowerCase();if(seen.has(key))return false;seen.add(key);return true}).sort((a,b)=>stamp(b.published)-stamp(a.published))}
function tokens(title){return new Set(clean(title).toLowerCase().replace(/[^a-z0-9\s-]/g,' ').split(/\s+/).filter(x=>x.length>2&&!STOP.has(x)))}
function overlap(a,b){let common=0;for(const x of a)if(b.has(x))common++;const union=new Set([...a,...b]).size;return{common,score:union?common/union:0}}
function coverageClusters(rows,maxClusters=6,maxItems=4){const groups=[];for(const row of rows){const t=tokens(row.title);if(t.size<3)continue;let best=null,bestScore=0;for(const g of groups){const o=overlap(t,g.tokens);if(o.common>=3&&o.score>=.28&&o.score>bestScore){best=g;bestScore=o.score}}if(best){best.items.push(row);best.tokens=new Set([...best.tokens,...t])}else{groups.push({tokens:t,items:[row]})}}
 return groups.map(g=>{const byDomain=new Map();for(const row of g.items){const key=row.source||domain(row.url)||row.providerId;if(!byDomain.has(key))byDomain.set(key,row)}const items=[...byDomain.values()].sort((a,b)=>stamp(b.published)-stamp(a.published));return{items,title:items[0]?.title||'',domains:new Set(items.map(x=>x.source)).size,published:items[0]?.published||''}}).filter(g=>g.domains>=2).sort((a,b)=>stamp(b.published)-stamp(a.published)).slice(0,maxClusters).map(g=>({...g,items:g.items.slice(0,maxItems)}))}
async function getConfig(){const r=await fetch(DEFAULT_CONFIG,{headers:{Accept:'application/json'}});if(!r.ok)throw new Error('Could not load news source contract');return r.json()}
function sourceState(host,id,state){const el=$('[data-provider="'+id+'"]',host);if(el)el.dataset.state=state}
async function providerLoad(host,id,query,timespan,force,horizon,config,category){sourceState(host,id,'loading');try{let rows=[];if(id==='gdelt')rows=await loadGdelt(query,timespan,force);else if(id==='publisher-rss')rows=await loadPublisherRss(config,category,force);else if(id==='official-rss')rows=await loadOfficialRss(config,category,force);else if(id==='hacker-news')rows=await loadHn(force);else if(id==='spaceflight-news')rows=await loadSpace(force);rows=trimToHorizon(rows,horizon);sourceState(host,id,'ok');return rows}catch(err){sourceState(host,id,'error');return[]}}
function nearDuplicate(a,b){
 const A=tokens(a.title),B=tokens(b.title);if(A.size<3||B.size<3)return false;
 const o=overlap(A,B);return o.common>=4&&o.score>=.48;
}
function latestRiverRows(rows,limit){
 const out=[];for(const row of rows){if(out.some(prev=>nearDuplicate(prev,row)))continue;out.push(row);if(out.length>=limit)break}return out;
}
function leadRows(rows){
 if(!rows.length)return[];const recentCutoff=Date.now()-12*60*60*1000;
 const readable=rows.find(r=>clean(r.summary).length>=90&&stamp(r.published)>=recentCutoff);
 const first=readable||rows[0],second=rows.find(r=>r!==first&&!nearDuplicate(first,r))||rows.find(r=>r!==first);
 return[first,second].filter(Boolean);
}
function storyCard(r,lead=false){
 const text=clean(r.summary).slice(0,lead?700:620);
 const expandable=text.length>(lead?320:230);
 const summary=text?'<p class="news-story-summary">'+esc(text)+(clean(r.summary).length>text.length?'…':'')+'</p>'+(expandable?'<button class="news-story-expand" type="button" data-news-expand aria-expanded="false">Show full excerpt</button>':''):'';
 const image=r.image?'<img class="news-story-image" src="'+esc(r.image)+'" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">':'';
 const country=r.country?'<span title="GDELT source-country metadata">'+esc(r.country)+'</span>':'';
 const kind=r.kind==='community'?'community link':r.kind==='publisher-excerpt'?'publisher excerpt':r.kind==='primary-source'?'primary source':'publisher link';
 const compact=!text&&!lead;
 return'<article class="news-story'+(lead?' news-story--lead':'')+(compact?' news-story--compact':'')+'">'+image+'<div class="news-story-kicker"><span>'+esc(r.provider)+'</span><i></i><span>'+esc(kind)+'</span></div>'+(lead?'<h2>':'<h3>')+esc(r.title)+(lead?'</h2>':'</h3>')+summary+'<div class="news-story-footer"><span>'+esc(r.source||'source')+'</span>'+country+'<span>'+esc(relativeTime(r.published))+'</span><a href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer">Full report ↗</a></div></article>';
}
function renderLatest(host,rows,maxFeed){const lead=$('[data-news-lead]',host),feed=$('[data-news-list]',host);if(!rows.length){if(lead)lead.innerHTML='';if(feed)feed.innerHTML='<div class="news-empty">No live items reached the browser for this query and time window. Try a broader lens, longer window, or refresh.</div>';return}const river=latestRiverRows(rows,maxFeed),leads=leadRows(river),leadSet=new Set(leads);if(lead)lead.innerHTML=leads.map((row,i)=>storyCard(row,i===0)).join('');if(feed)feed.innerHTML=river.filter(row=>!leadSet.has(row)).map(row=>storyCard(row)).join('')}
function renderClusters(host,clusters){const el=$('[data-news-clusters]',host);if(!el)return;el.innerHTML=clusters.length?clusters.map((g,i)=>'<article class="news-cluster"><div class="news-cluster-head"><div><div class="news-cluster-meta">Repeated coverage · cluster '+(i+1)+'</div><h3>'+esc(g.title)+'</h3></div><div class="news-cluster-count">'+g.domains+'<small>source domains</small></div></div><div class="news-cluster-links">'+g.items.map(r=>'<a class="news-cluster-link" href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer"><span>'+esc(r.source||r.provider)+'</span><b>'+esc(r.title)+'</b><em>'+esc(relativeTime(r.published))+'</em></a>').join('')+'</div></article>').join(''):'<div class="news-empty">No repeated-coverage clusters cleared the current overlap rule in this sample. That does not mean the underlying events are unimportant or unreported.</div>'}
function providerDescription(id){return id==='gdelt'?'Broad publisher discovery via GDELT':id==='publisher-rss'?'Publisher-supplied RSS excerpts and metadata':id==='official-rss'?'First-party economic and policy releases':id==='hacker-news'?'Community technology link stream':id==='spaceflight-news'?'Specialist space reporting index':id}
function providerContract(config,id){return(config.providers||[]).find(row=>row.id===id)||{}}
function publisherFeedRegister(config){
 const feeds=config.publisher_feeds||[];if(!feeds.length)return'';
 return'<div class="news-feed-register"><div class="news-feed-register-title">Publisher feed register</div>'+feeds.map(feed=>{const terms=safeUrl(feed.terms_url);return'<div class="news-feed-contract"><div><b>'+esc(feed.name)+'</b><span>'+esc(feed.scope||'publisher feed')+'</span></div><div><span class="news-contract-chip">'+esc(feed.reuse_mode||'publisher terms')+'</span><p>'+esc(feed.reuse_note||feed.source_note||'Feed use remains subject to the publisher terms.')+'</p>'+(terms?'<a href="'+esc(terms)+'" target="_blank" rel="noopener noreferrer">Terms / source note ↗</a>':'')+'</div></div>'}).join('')+'</div>';
}function officialFeedRegister(config){
 const feeds=config.official_feeds||[];if(!feeds.length)return'';
 return'<div class="news-feed-register"><div class="news-feed-register-title">Official feed register</div>'+feeds.map(feed=>{const terms=safeUrl(feed.terms_url);return'<div class="news-feed-contract"><div><b>'+esc(feed.name)+'</b><span>'+esc(feed.scope||'official feed')+'</span></div><div><span class="news-contract-chip">'+esc(feed.reuse_mode||'official RSS')+'</span><p>'+esc(feed.reuse_note||'First-party institutional release feed.')+'</p>'+(terms?'<a href="'+esc(terms)+'" target="_blank" rel="noopener noreferrer">Official source ↗</a>':'')+'</div></div>'}).join('')+'</div>';
}

function renderSourceLanes(host,rows,providers,limit,config){
 const el=$('[data-news-source-lanes]',host);if(!el)return;
 el.innerHTML=providers.map(id=>{
   const items=rows.filter(r=>r.providerId===id).slice(0,limit),contract=providerContract(config,id);
   const name=contract.name||items[0]?.provider||(id==='spaceflight-news'?'Spaceflight News':id==='hacker-news'?'Hacker News':id==='publisher-rss'?'Publisher RSS':id==='official-rss'?'Official releases':'GDELT');
   const meta='<div class="news-source-contract"><div class="news-source-contract-chips"><span>'+esc(contract.display_mode||contract.source_class||'external source')+'</span><span>'+esc(contract.access||'external access')+'</span></div><p>'+esc(contract.boundary||providerDescription(id))+'</p></div>';
   const register=id==='publisher-rss'?publisherFeedRegister(config):id==='official-rss'?officialFeedRegister(config):'';
   const stories=items.length?items.map(r=>'<a class="news-source-item" href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer"><b>'+esc(r.title)+'</b><span>'+esc(r.source)+' · '+esc(relativeTime(r.published))+'</span></a>').join(''):'<div class="news-empty">No items from this provider in the active view.</div>';
   return'<article class="news-source-lane"><div class="news-source-lane-head"><b>'+esc(name)+'</b><span>'+esc(providerDescription(id))+' · '+items.length+' shown</span></div>'+meta+stories+register+'</article>';
 }).join('');
}
function sourceBalancedBriefing(rows,providers,limit=12){
 const queues=new Map(providers.map(id=>[id,rows.filter(r=>r.providerId===id)]));
 const seenSources=new Set(),out=[];let progress=true;
 while(out.length<limit&&progress){
   progress=false;
   for(const id of providers){
     const queue=queues.get(id)||[];if(!queue.length)continue;
     let index=queue.findIndex(r=>!seenSources.has((r.source||'').toLowerCase()));
     if(index<0)index=0;
     const [row]=queue.splice(index,1);if(!row)continue;
     out.push(row);if(row.source)seenSources.add(row.source.toLowerCase());progress=true;
     if(out.length>=limit)break;
   }
 }
 return out;
}
function renderBriefing(host,rows,providers){
 const el=$('[data-news-briefing]',host);if(!el)return;
 const items=sourceBalancedBriefing(rows,providers,12);
 el.innerHTML=items.length?items.map((r,i)=>'<article class="news-briefing-item"><div class="news-briefing-index">'+String(i+1).padStart(2,'0')+'</div><div><div class="news-story-kicker"><span>'+esc(r.provider)+'</span><i></i><span>'+esc(r.source||'source')+'</span></div><h3>'+esc(r.title)+'</h3>'+(r.summary?'<p>'+esc(r.summary.slice(0,300))+(r.summary.length>300?'…':'')+'</p>':'')+'<div class="news-story-footer"><span>'+esc(relativeTime(r.published))+'</span><a href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer">Full report ↗</a></div></div></article>').join(''):'<div class="news-empty">No stories are available for a briefing in this sample.</div>';
}
function renderPulse(host,rows,clusters,providers){const pulse=$('[data-news-pulse]',host);if(!pulse)return;const domains=new Set(rows.map(r=>r.source).filter(Boolean));const active=new Set(rows.map(r=>r.providerId).filter(Boolean));const readable=rows.filter(r=>clean(r.summary).length>0).length;const newest=rows.length?relativeTime(rows[0].published):'—';const vals=[[rows.length,'items returned'],[readable,'readable here'],[domains.size,'source domains'],[active.size+'/'+providers.length,'active providers'],[clusters.length,'repeated clusters'],[newest,'newest item age']];pulse.innerHTML=vals.map(v=>'<div class="news-pulse-cell"><b>'+esc(v[0])+'</b><span>'+esc(v[1])+'</span></div>').join('')}
function renderPreview(host,rows,limit){const grid=$('[data-news-preview-grid]',host);if(!grid)return;const take=rows.slice(0,limit);grid.innerHTML=take.length?take.map(r=>'<a class="news-preview-item" href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer"><small>'+esc(r.provider)+' · '+esc(r.source)+'</small><b>'+esc(r.title)+'</b><span>'+esc(relativeTime(r.published))+'</span></a>').join(''):'<div class="news-empty">Live preview unavailable. The full News page can retry each source independently.</div>'}
function setView(host,view){Array.from(host.querySelectorAll('[data-news-view]')).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.newsView===view)));Array.from(host.querySelectorAll('[data-news-view-panel]')).forEach(p=>p.classList.toggle('is-active',p.dataset.newsViewPanel===view));const more=$('.news-secondary-drawer',host);if(more&&view!=='latest')more.open=true}
function mergeQueries(a,b){if(a&&b)return'('+a+') AND ('+b+')';return a||b||'(international OR world)'}
async function bootFull(host,config){
 const tabs=$('[data-news-tabs]',host),lenses=$('[data-news-lenses]',host),horizons=$('[data-news-horizons]',host),input=$('[data-news-search]',host),form=$('form.news-search',host),refresh=$('[data-news-refresh]',host),readableToggle=$('[data-news-readable]',host),queryText=$('[data-news-active-query]',host);
 const params=new URLSearchParams(location.search);let category=params.get('category')||host.dataset.newsCategory||'all';let lens=params.get('lens')||'';let horizon=params.get('window')||'24h';let custom=clean(params.get('q')||'');let view=params.get('view')||'latest';let readable=params.get('readable')==='1';let force=false;
 if(!(config.categories||[]).some(x=>x.id===category))category='all';
 if(lens&&!(config.lenses||[]).some(x=>x.id===lens))lens='';
 if(!(config.horizons||[]).some(x=>x.id===horizon))horizon='24h';
 if(!['latest','briefing','clusters','sources'].includes(view))view='latest';
 if(custom){category='all';lens='';readable=false}
 function catRow(){return(config.categories||[]).find(x=>x.id===category)||(config.categories||[])[0]||{}}
 function lensRow(){return(config.lenses||[]).find(x=>x.id===lens)||null}
 function press(){Array.from((tabs||host).querySelectorAll('[data-news-category]')).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.newsCategory===category)));Array.from((lenses||host).querySelectorAll('[data-news-lens]')).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.newsLens===lens)));Array.from((horizons||host).querySelectorAll('[data-news-horizon]')).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.newsHorizon===horizon)));if(readableToggle){const allowed=!custom&&!lens;readableToggle.disabled=!allowed;readableToggle.setAttribute('aria-disabled',String(!allowed));readableToggle.setAttribute('aria-pressed',String(allowed&&readable));readableToggle.title=allowed?'Show only stories with an in-page excerpt':'Readable-here filtering is unavailable for scoped search/lens queries'}setView(host,view)}
 function persist(){const p=new URLSearchParams();if(custom)p.set('q',custom);else if(category!=='all')p.set('category',category);if(lens)p.set('lens',lens);if(horizon!=='24h')p.set('window',horizon);if(view!=='latest')p.set('view',view);if(readable)p.set('readable','1');history.replaceState(null,'',p.toString()?'?'+p.toString():location.pathname)}
 async function run(){
   const cat=catRow(),lr=lensRow(),q=custom||mergeQueries(cat.gdelt_query,lr?.gdelt_query),baseProviders=custom?['gdelt']:[...new Set([...(cat.providers||['gdelt']),...(lr?.providers||[])])],providers=(custom||lr)?baseProviders.filter(id=>id!=='publisher-rss') : baseProviders,ms=horizonMs(config,horizon),timespan=horizonSpan(config,horizon);
   $$('[data-provider]',host).forEach(el=>el.dataset.state=providers.includes(el.dataset.provider)?'loading':'idle');
   if(queryText)queryText.textContent=(custom?'Search: “'+custom+'”':[(cat.label||'All'),lr?.label].filter(Boolean).join(' · '))+' · '+horizonLabel(config,horizon)+(readable?' · readable here only':'');
   const groups=await Promise.all(providers.map(id=>providerLoad(host,id,q,timespan,force,ms,config,category)));force=false;
   const allRows=dedupe(groups.flat()),rows=readable?allRows.filter(r=>clean(r.summary).length>0):allRows,clusters=coverageClusters(rows,config.presentation?.max_clusters||6,config.presentation?.max_cluster_items||4);
   const count=$('[data-news-count]',host),updated=$('[data-news-updated]',host);if(count)count.textContent=rows.length+' items';if(updated)updated.textContent='refreshed '+new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
   renderLatest(host,rows,config.presentation?.max_feed||36);renderBriefing(host,rows,providers);renderClusters(host,clusters);renderSourceLanes(host,rows,providers,config.presentation?.source_lane_items||5,config);renderPulse(host,rows,clusters,providers);
 }
 tabs?.addEventListener('click',e=>{const b=e.target.closest('[data-news-category]');if(!b)return;category=b.dataset.newsCategory;custom='';if(input)input.value='';press();persist();run()});
 lenses?.addEventListener('click',e=>{const b=e.target.closest('[data-news-lens]');if(!b)return;lens=b.dataset.newsLens||'';if(lens)readable=false;press();persist();run()});
 horizons?.addEventListener('click',e=>{const b=e.target.closest('[data-news-horizon]');if(!b)return;horizon=b.dataset.newsHorizon;press();persist();run()});
 $$('[data-news-view]',host).forEach(b=>b.addEventListener('click',()=>{view=b.dataset.newsView;press();persist()}));
 form?.addEventListener('submit',e=>{e.preventDefault();custom=clean(input.value);if(!custom)return;category='all';lens='';readable=false;press();persist();run()});
 host.addEventListener('click',e=>{const expand=e.target.closest('[data-news-expand]');if(!expand)return;const card=expand.closest('.news-story');if(!card)return;const open=!card.classList.contains('is-expanded');card.classList.toggle('is-expanded',open);expand.setAttribute('aria-expanded',String(open));expand.textContent=open?'Collapse excerpt':'Show full excerpt'});
 refresh?.addEventListener('click',()=>{force=true;run()});
 readableToggle?.addEventListener('click',()=>{if(custom||lens)return;readable=!readable;press();persist();run()});
 if(input&&custom)input.value=custom;press();await run();
}
async function bootPreview(host,config){const cat=(config.categories||[]).find(x=>x.id===(host.dataset.newsCategory||'all'))||(config.categories||[])[0]||{};const providers=(host.dataset.newsProviders||'').split(',').map(x=>x.trim()).filter(Boolean);const ids=providers.length?providers:(cat.providers||['gdelt']);const groups=await Promise.all(ids.map(id=>providerLoad(host,id,cat.gdelt_query,'24h',false,86400000,config,cat.id||'all')));renderPreview(host,dedupe(groups.flat()),Math.max(1,Math.min(6,Number(host.dataset.newsLimit)||3)))}
async function boot(){const hosts=$$('[data-news-feed]');if(!hosts.length)return;let config;try{config=await getConfig()}catch(err){hosts.forEach(h=>{const target=$('[data-news-list],[data-news-preview-grid]',h);if(target)target.innerHTML='<div class="news-empty">News configuration could not be loaded.</div>'});return}hosts.forEach(host=>{if(host.dataset.newsMode==='preview')bootPreview(host,config);else bootFull(host,config)})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();