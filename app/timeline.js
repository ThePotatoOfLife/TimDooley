(()=>{
  const DATA_PATH='data/timeline-events.json';
  const PACK_INDEX='data/timeline-event-packs/index.json';
  const SCRIPT_URL=document.currentScript?.src||location.href;
  const $=s=>document.querySelector(s);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl=s=>/^https?:\/\//i.test(String(s||''))?String(s):'';
  let data=null;
  let state={layers:new Set(),actors:new Set(),epistemic:'all',query:'',exact:false,detail:true,from:'',to:'',sort:'asc'};
  let requestToken=0;
  let urlStateRead=false;
  let urlLayerOverride=false;
  let urlActorOverride=false;
  let pendingEventId='';

  function layerById(id){return (data?.layers||[]).find(x=>x.id===id)}
  function actorById(id){return (data?.actors||[]).find(x=>x.id===id)}
  function human(s){return String(s||'').replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
  function sortKey(e){
    if(e.timestamp)return e.timestamp;
    const d=e.date||'';
    const m=d.match(/^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/);
    if(!m)return d;
    return `${m[1]}-${m[2]||'07'}-${m[3]||'01'}T12:00:00Z`;
  }
  function eventYears(e){
    const values=String(e.timestamp||e.date||'').match(/\b(?:19|20)\d{2}\b/g)||[];
    const years=values.map(Number).filter(Number.isFinite);
    if(!years.length)return [null,null];
    return [Math.min(...years),Math.max(...years)];
  }
  function yearOf(e){const [y]=eventYears(e);return y?String(y):'Undated'}
  function allYears(){
    const set=new Set();
    for(const e of data?.events||[]){const [a,b]=eventYears(e);if(a)for(let y=a;y<=(b||a);y++)set.add(y)}
    return [...set].sort((a,b)=>a-b);
  }
  function displayDate(e){
    const p=e.precision||'date';
    if(e.timestamp&&['second','minute','hour'].includes(p))return e.timestamp.replace('T',' ').replace(/([+-]\d\d:\d\d|Z)$/,' $1');
    if(p==='month'&&/^\d{4}-\d{2}$/.test(e.date||'')){
      const [y,m]=e.date.split('-');
      return new Intl.DateTimeFormat('en',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(Date.UTC(+y,+m-1,1)));
    }
    return e.date||'Undated';
  }
  function isExact(e){return ['second','minute','hour','date'].includes(e.precision)}
  function searchable(e){
    return [e.id,e.title,e.summary,e.quote,e.subject,e.status,e.epistemic,e.bible_relation,e.source_direction,e.platform,e.public_url,...(e.layers||[]),...(e.actor_ids||[]),...(e.motifs||[]),...(e.comparators||[]),...(e.source_records||[])].join(' ').toLowerCase();
  }
  function queryTokens(q){
    const out=[];const re=/"([^"]+)"|(\S+)/g;let m;
    while((m=re.exec(q)))out.push((m[1]||m[2]).toLowerCase());
    return out;
  }
  function queryMatch(e,q){
    const hay=searchable(e);const tokens=queryTokens(q);
    return tokens.every(t=>t.startsWith('-')&&t.length>1?!hay.includes(t.slice(1)):hay.includes(t));
  }
  function actorMatch(e){const ids=e.actor_ids?.length?e.actor_ids:['project'];return ids.some(id=>state.actors.has(id))}
  function yearMatch(e){
    const [a,b]=eventYears(e);if(!a)return !state.from&&!state.to;
    const from=state.from?+state.from:-Infinity,to=state.to?+state.to:Infinity;
    return (b||a)>=from&&a<=to;
  }
  function filteredEvents(){
    return (data?.events||[]).filter(e=>{
      if(!e.layers?.some(x=>state.layers.has(x)))return false;
      if(!actorMatch(e))return false;
      if(state.epistemic!=='all'&&e.epistemic!==state.epistemic)return false;
      if(state.exact&&!isExact(e))return false;
      if(!yearMatch(e))return false;
      if(state.query.trim()&&!queryMatch(e,state.query.trim()))return false;
      return true;
    }).sort((a,b)=>state.sort==='desc'?sortKey(b).localeCompare(sortKey(a)):sortKey(a).localeCompare(sortKey(b)));
  }
  function timPotatoYear(y,m,day){
    let age=y-2020;if(m<12||(m===12&&day<25))age--;
    return age<=0?'Tim · Potato birth year':`Tim · Potato year ${age}`;
  }
  function lifeMarker(e){
    const actors=e.actor_ids||[];
    const d=(e.timestamp||e.date||'').match(/^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/);
    if(!d)return '';
    const y=+d[1],m=+(d[2]||7),day=+(d[3]||1);
    const hasSon=actors.includes('son'),hasTim=actors.includes('tim');
    if(hasSon&&hasTim){if(y<=2020)return 'Son 32→33 corridor · Tim emerges';return `Son/Twin relation · ${timPotatoYear(y,m,day)}`}
    if(hasSon){let age=y-1987;if(m<7||(m===7&&day<31))age--;return `Son age ${Math.max(0,age)}`}
    if(hasTim)return timPotatoYear(y,m,day);
    return '';
  }
  function layerChip(id){const l=layerById(id);return `<span class="tl-layer tl-layer-${esc(id)}">${esc(l?.label||human(id))}</span>`}
  function actorChips(e){return (e.actor_ids||[]).filter(x=>x!=='shared').map(id=>`<span class="tl-actor tl-actor-${esc(id)}">${esc(actorById(id)?.label||human(id))}</span>`).join('')}
  function sourceLink(p,standalone){const label=String(p).split('/').pop();return standalone?`<a href="../#record=${encodeURIComponent(p)}">${esc(label)}</a>`:`<button data-record="${esc(p)}">${esc(label)}</button>`}
  function bibleRelation(e){
    if(!e.bible_relation)return '';
    const labels={
      'explicit-at-time':'Bible explicit at time',
      'explicit-context-at-time':'Biblical context at time',
      'explicit-symbolic-at-time':'Biblical symbol at time',
      'explicit-Christian-vocabulary-at-time':'Christian vocabulary at time',
      'mixed-explicit-and-later':'Explicit + later parallel',
      'mixed-explicit-scriptural-vocabulary':'Mixed scriptural vocabulary'
    };
    return `<span class="tl-bible-relation">${esc(labels[e.bible_relation]||human(e.bible_relation))}</span>`;
  }
  function relatedLinks(e){
    if(!state.detail||!e.related_event_ids?.length)return '';
    return `<div class="tl-related"><span>Related</span>${e.related_event_ids.map(id=>`<button data-tl-event="${esc(id)}">${esc(id.replace(/^evt-/,''))}</button>`).join('')}</div>`;
  }
  function eventCard(e,standalone=false){
    const roadmap=e.layers?.includes('roadmap');
    const quote=e.quote?`<blockquote class="tl-quote">“${esc(e.quote)}”</blockquote>`:'';
    const motifs=e.motifs?.length?`<div class="tl-motifs">${e.motifs.map(x=>`<span>${esc(x)}</span>`).join('')}</div>`:'';
    const comps=e.comparators?.length&&state.detail?`<details class="tl-comparators"><summary>${e.layers?.includes('biblical-unlock')?'Research references':'Biblical / comparative references'} (${e.comparators.length})</summary><div>${e.comparators.map(x=>`<span>${esc(x)}</span>`).join('')}</div></details>`:'';
    const direction=e.source_direction&&state.detail?`<div class="tl-direction"><b>Source direction</b> ${esc(e.source_direction)}</div>`:'';
    const sources=e.source_records?.length&&state.detail?`<div class="tl-sources"><span>Sources</span>${e.source_records.map(p=>sourceLink(p,standalone)).join('')}</div>`:'';
    const external=safeUrl(e.public_url)&&state.detail?`<div class="tl-public-source"><a href="${esc(e.public_url)}" target="_blank" rel="noopener">Open ${esc(e.platform||'public source')} ↗</a></div>`:'';
    const age=lifeMarker(e);
    const body=state.detail?`${e.summary?`<p>${esc(e.summary)}</p>`:''}${quote}${motifs}${comps}${direction}${external}${sources}${relatedLinks(e)}`:`${quote}${motifs}`;
    return `<article id="${esc(e.id)}" class="tl-event ${roadmap?'tl-roadmap-event':''}" data-event-id="${esc(e.id)}"><div class="tl-dot" aria-hidden="true"></div><div class="tl-event-card"><div class="tl-event-head"><div><time>${esc(displayDate(e))}</time><span class="tl-precision">${esc(e.precision)}</span>${age?`<span class="tl-life-age">${esc(age)}</span>`:''}</div><div class="tl-event-meta"><span class="tl-epistemic">${esc(human(e.epistemic))}</span>${bibleRelation(e)}${actorChips(e)}</div></div><div class="tl-title-row"><h4>${esc(e.title)}</h4><button class="tl-event-link" data-tl-share-event="${esc(e.id)}" aria-label="Copy link to ${esc(e.title)}" title="Copy event link">#</button></div><div class="tl-layers">${(e.layers||[]).map(layerChip).join('')}</div>${body}</div></article>`;
  }
  function timelineHTML(events,standalone=false){
    if(!events.length)return `<div class="tl-empty"><strong>No events in this view.</strong><span>Clear a filter, widen the year range, or turn on another lens/life track.</span><button data-tl-reset>Reset timeline</button></div>`;
    const groups=new Map();
    for(const e of events){const y=yearOf(e);if(!groups.has(y))groups.set(y,[]);groups.get(y).push(e)}
    return [...groups.entries()].map(([year,items])=>`<section class="tl-year" data-tl-year="${esc(year)}"><div class="tl-year-label"><span>${esc(year)}</span><small>${items.length} point${items.length===1?'':'s'}</small></div><div class="tl-year-events">${items.map(e=>eventCard(e,standalone)).join('')}</div></section>`).join('');
  }
  function yearOptions(selected,placeholder){return `<option value="">${placeholder}</option>${allYears().map(y=>`<option value="${y}" ${String(selected)===String(y)?'selected':''}>${y}</option>`).join('')}`}
  function controlsHTML(){
    const layerButtons=(data.layers||[]).sort((a,b)=>(a.order||0)-(b.order||0)).map(l=>`<button class="tl-toggle ${state.layers.has(l.id)?'active':''}" data-tl-layer="${esc(l.id)}" aria-pressed="${state.layers.has(l.id)}"><span class="tl-toggle-dot tl-dot-${esc(l.id)}"></span><span>${esc(l.label)}</span><small>${(data.events||[]).filter(e=>e.layers?.includes(l.id)).length}</small></button>`).join('');
    const actorButtons=(data.actors||[]).sort((a,b)=>(a.order||0)-(b.order||0)).map(a=>`<button class="tl-track ${state.actors.has(a.id)?'active':''}" data-tl-actor="${esc(a.id)}" aria-pressed="${state.actors.has(a.id)}"><b>${esc(a.label)}</b><small>${esc(a.description)}</small></button>`).join('');
    return `<div class="tl-control-panel"><div class="tl-control-title"><div><strong>Life tracks</strong><span>Switch Son, Tim, shared transitions and later project research independently.</span></div><button class="tl-reset" data-tl-reset>Reset</button></div><div class="tl-track-grid">${actorButtons}</div><div class="tl-control-title tl-lens-title"><div><strong>Timeline lenses</strong><span>Presets change the evidence layers; they never rewrite the underlying events.</span></div></div><div class="tl-presets"><button data-tl-preset="roadmap">Roadmap</button><button data-tl-preset="public">Public trajectory</button><button data-tl-preset="bible">Bible lens</button><button data-tl-preset="research">Research</button><button data-tl-preset="creative">Creative</button><button data-tl-preset="everything">Everything</button></div><div class="tl-layer-grid">${layerButtons}</div><div class="tl-secondary-controls"><label>Search events<input id="tl-query" type="search" value="${esc(state.query)}" placeholder='Door Father "World Axis" -dog'></label><label>Evidence<select id="tl-epistemic"><option value="all">All evidence classes</option>${(data.epistemic_classes||[]).map(x=>`<option value="${esc(x.id)}" ${state.epistemic===x.id?'selected':''}>${esc(x.label)}</option>`).join('')}</select></label><label>From year<select id="tl-from">${yearOptions(state.from,'Earliest')}</select></label><label>To year<select id="tl-to">${yearOptions(state.to,'Latest')}</select></label><label>Order<select id="tl-sort"><option value="asc" ${state.sort==='asc'?'selected':''}>Oldest first</option><option value="desc" ${state.sort==='desc'?'selected':''}>Newest first</option></select></label><label>Jump to year<select id="tl-jump"><option value="">Choose year</option>${allYears().map(y=>`<option value="${y}">${y}</option>`).join('')}</select></label><label class="tl-check"><input id="tl-exact" type="checkbox" ${state.exact?'checked':''}> Exact dates only</label><label class="tl-check"><input id="tl-detail" type="checkbox" ${state.detail?'checked':''}> Detailed cards</label></div><div class="tl-query-help">Search uses AND matching. Put phrases in quotes; prefix a term with <code>-</code> to exclude it. Filters are reflected in the URL so the current view can be shared.</div></div>`;
  }
  function statsHTML(events){
    const roadmap=events.filter(e=>e.layers?.includes('roadmap')).length;
    const bible=events.filter(e=>e.layers?.some(x=>['scripture-at-time','biblical-parallel','biblical-unlock'].includes(x))).length;
    const years=events.flatMap(e=>eventYears(e)).filter(Boolean);const span=years.length?`${Math.min(...years)}–${Math.max(...years)}`:'—';
    return `<div><strong>${events.length}</strong><span>visible points</span></div><div><strong>${roadmap}</strong><span>roadmap</span></div><div><strong>${bible}</strong><span>Bible-linked</span></div><div><strong>${esc(span)}</strong><span>visible span</span></div>`;
  }
  function readURLState(){
    if(urlStateRead)return;urlStateRead=true;
    const p=new URLSearchParams(location.search);
    state.query=p.get('tl_q')||state.query;
    state.epistemic=p.get('tl_epistemic')||state.epistemic;
    state.exact=p.get('tl_exact')==='1';
    if(p.has('tl_detail'))state.detail=p.get('tl_detail')!=='0';
    state.from=p.get('tl_from')||'';state.to=p.get('tl_to')||'';
    state.sort=p.get('tl_sort')==='desc'?'desc':'asc';
    if(p.has('tl_layers')){urlLayerOverride=true;const raw=p.get('tl_layers')||'';state.layers=new Set(raw==='none'?[]:raw.split(',').filter(Boolean))}
    if(p.has('tl_actors')){urlActorOverride=true;const raw=p.get('tl_actors')||'';state.actors=new Set(raw==='none'?[]:raw.split(',').filter(Boolean))}
    pendingEventId=p.get('tl_event')||'';
  }
  function syncURL(eventId=pendingEventId){
    const u=new URL(location.href);const p=u.searchParams;
    const set=(k,v,empty='')=>{v===empty||v==null?p.delete('tl_'+k):p.set('tl_'+k,String(v))};
    set('q',state.query);set('epistemic',state.epistemic,'all');set('exact',state.exact?'1':'','');set('detail',state.detail?'':'0','');set('from',state.from);set('to',state.to);set('sort',state.sort,'asc');
    const defaultLayers=(data?.layers||[]).filter(x=>x.default).map(x=>x.id).sort().join(',');
    const currentLayers=[...state.layers].sort().join(',');if(currentLayers===defaultLayers)p.delete('tl_layers');else p.set('tl_layers',currentLayers||'none');
    const defaultActors=(data?.actors||[]).filter(x=>x.default).map(x=>x.id).sort().join(',');
    const currentActors=[...state.actors].sort().join(',');if(currentActors===defaultActors)p.delete('tl_actors');else p.set('tl_actors',currentActors||'none');
    set('event',eventId||'');
    history.replaceState(null,'',u.pathname+(p.toString()?`?${p}`:'')+u.hash);
  }
  function resetState(){
    state={layers:new Set((data.layers||[]).filter(x=>x.default).map(x=>x.id)),actors:new Set((data.actors||[]).filter(x=>x.default).map(x=>x.id)),epistemic:'all',query:'',exact:false,detail:true,from:'',to:'',sort:'asc'};
    urlLayerOverride=false;urlActorOverride=false;pendingEventId='';
  }
  function revealEvent(id,root,standalone){
    const ev=(data.events||[]).find(e=>e.id===id);if(!ev)return;
    state.query='';state.epistemic='all';state.exact=false;state.from='';state.to='';
    for(const l of ev.layers||[])state.layers.add(l);
    for(const a of ev.actor_ids||[])state.actors.add(a);
    pendingEventId=id;renderShell(root,standalone);syncURL(id);
    requestAnimationFrame(()=>document.getElementById(id)?.scrollIntoView({behavior:'smooth',block:'center'}));
  }
  async function copyEventLink(id,button){
    pendingEventId=id;syncURL(id);
    try{await navigator.clipboard.writeText(location.href);if(button){const old=button.textContent;button.textContent='✓';setTimeout(()=>button.textContent=old,1200)}}catch(_){/* URL remains available in the address bar */}
  }
  function handleClick(root,standalone,e){
    const layer=e.target.closest('[data-tl-layer]');
    if(layer){const id=layer.dataset.tlLayer;state.layers.has(id)?state.layers.delete(id):state.layers.add(id);pendingEventId='';renderResults(root,standalone);syncURL('');return}
    const actor=e.target.closest('[data-tl-actor]');
    if(actor){const id=actor.dataset.tlActor;state.actors.has(id)?state.actors.delete(id):state.actors.add(id);pendingEventId='';renderResults(root,standalone);syncURL('');return}
    const preset=e.target.closest('[data-tl-preset]');
    if(preset){
      const p=preset.dataset.tlPreset;
      const sets={roadmap:['roadmap'],public:['roadmap','direct-words','public-witness'],bible:['roadmap','scripture-at-time','biblical-parallel','biblical-unlock'],research:['roadmap','formalization','biblical-unlock'],creative:['roadmap','creative'],everything:(data.layers||[]).map(x=>x.id)};
      state.layers=new Set(sets[p]||sets.roadmap);pendingEventId='';renderShell(root,standalone);syncURL('');return;
    }
    const reset=e.target.closest('[data-tl-reset]');if(reset){resetState();renderShell(root,standalone);syncURL('');return}
    const related=e.target.closest('[data-tl-event]');if(related){revealEvent(related.dataset.tlEvent,root,standalone);return}
    const share=e.target.closest('[data-tl-share-event]');if(share){copyEventLink(share.dataset.tlShareEvent,share)}
  }
  function bindControls(root,standalone){
    root.onclick=e=>handleClick(root,standalone,e);
    root.querySelector('#tl-query')?.addEventListener('input',e=>{state.query=e.target.value;pendingEventId='';renderResults(root,standalone);syncURL('')});
    root.querySelector('#tl-epistemic')?.addEventListener('change',e=>{state.epistemic=e.target.value;pendingEventId='';renderResults(root,standalone);syncURL('')});
    root.querySelector('#tl-from')?.addEventListener('change',e=>{state.from=e.target.value;if(state.to&&state.from&&+state.from>+state.to)state.to=state.from;renderShell(root,standalone);syncURL('')});
    root.querySelector('#tl-to')?.addEventListener('change',e=>{state.to=e.target.value;if(state.to&&state.from&&+state.to<+state.from)state.from=state.to;renderShell(root,standalone);syncURL('')});
    root.querySelector('#tl-sort')?.addEventListener('change',e=>{state.sort=e.target.value;renderShell(root,standalone);syncURL(pendingEventId)});
    root.querySelector('#tl-jump')?.addEventListener('change',e=>{const y=e.target.value;if(y)root.querySelector(`[data-tl-year="${CSS.escape(y)}"]`)?.scrollIntoView({behavior:'smooth',block:'start'});e.target.value=''});
    root.querySelector('#tl-exact')?.addEventListener('change',e=>{state.exact=e.target.checked;pendingEventId='';renderResults(root,standalone);syncURL('')});
    root.querySelector('#tl-detail')?.addEventListener('change',e=>{state.detail=e.target.checked;renderResults(root,standalone);syncURL(pendingEventId)});
  }
  function renderResults(root,standalone){
    const events=filteredEvents();
    const stats=root.querySelector('#tl-stats');if(stats)stats.innerHTML=statsHTML(events);
    const list=root.querySelector('#tl-results');if(list)list.innerHTML=timelineHTML(events,standalone);
    root.querySelectorAll('[data-tl-layer]').forEach(b=>{const on=state.layers.has(b.dataset.tlLayer);b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))});
    root.querySelectorAll('[data-tl-actor]').forEach(b=>{const on=state.actors.has(b.dataset.tlActor);b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))});
  }
  function shellHTML(events,standalone){
    const intro=standalone?'Explore one canonical event dataset with optional evidence overlays, source direction and public-witness layers.':'One time axis with a sparse milestone road and optional evidence overlays. Son/Twin and Tim/Potato/Father remain independent tracks.';
    const meta=data?._pack_meta||{};const loadNote=meta.loaded?`Base timeline + ${meta.loaded} curated event pack${meta.loaded===1?'':'s'} loaded${meta.failed?.length?` · ${meta.failed.length} pack load issue${meta.failed.length===1?'':'s'}`:''}.`:'';
    return `<div class="tl-hero"><div><div class="eyebrow">Layered timeline explorer</div><h2>${standalone?'EXPLORE THE LAYERS':'TIMELINE'}</h2><p class="summary">${intro}</p>${loadNote?`<div class="tl-load-note">${esc(loadNote)}</div>`:''}</div><div class="tl-stats" id="tl-stats">${statsHTML(events)}</div></div><div class="tl-help"><strong>Source direction matters</strong><span><b>At the time</b> means scripture or vocabulary was already present. <b>Later parallel</b> means comparison came afterward. <b>Unlock</b> is when the archive explicitly discovered/formalized that comparison.</span>${standalone?'':'<button data-record="docs/TIMELINE-EVENT-STANDARD.md">Open event standard</button>'}</div>${controlsHTML()}<div class="tl-axis" id="tl-results">${timelineHTML(events,standalone)}</div>${standalone?'':`<div class="section"><h3>Underlying timeline records</h3><div class="tl-record-links"><button data-record="data/tim-dooley-timeline.json">Identity-safe master timeline</button><button data-record="knowledge/timeline/dated-master-timeline-2026.json">2026 dated master</button><button data-record="knowledge/timeline/reverse-biblical-overlap-timeline-2025-2026.json">Reverse biblical timeline</button><button data-record="data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json">Public X occurrence ledger</button><button data-record="data/timeline-events.json">Layered event dataset</button></div></div><div id="record-detail"></div>`}`;
  }
  function renderShell(root,standalone=false){root.innerHTML=shellHTML(filteredEvents(),standalone);bindControls(root,standalone)}
  function initializeState(){
    readURLState();
    if(!state.layers.size&&!urlLayerOverride)state.layers=new Set((data.layers||[]).filter(x=>x.default).map(x=>x.id));
    if(!state.actors.size&&!urlActorOverride)state.actors=new Set((data.actors||[]).filter(x=>x.default).map(x=>x.id));
    state.layers=new Set([...state.layers].filter(id=>layerById(id)));
    state.actors=new Set([...state.actors].filter(id=>actorById(id)));
  }
  async function mergeEventPacks(baseUrl){
    const meta={requested:0,loaded:0,failed:[],duplicates:0};data._pack_meta=meta;
    try{
      const indexUrl=new URL('../'+PACK_INDEX,baseUrl).href;
      const index=await fetch(indexUrl).then(r=>r.ok?r.json():null);
      if(!index?.packs?.length)return;
      meta.requested=index.packs.length;
      const packBase=new URL('../data/timeline-event-packs/',baseUrl);
      const packs=await Promise.all(index.packs.map(async name=>{try{const r=await fetch(new URL(name,packBase));if(!r.ok)throw new Error(String(r.status));return [name,await r.json()]}catch(err){meta.failed.push(`${name}: ${err.message}`);return [name,null]}}));
      const seen=new Set((data.events||[]).map(e=>e.id));
      for(const [,pack] of packs){
        if(!pack)continue;meta.loaded++;
        for(const e of pack.events||[]){
          if(!e?.id)continue;
          if(seen.has(e.id)){meta.duplicates++;continue}
          seen.add(e.id);data.events.push(e);
        }
      }
    }catch(err){meta.failed.push(err.message)}
  }
  async function ensureData(){
    if(data)return data;
    const url=new URL('../'+DATA_PATH,SCRIPT_URL).href;
    data=await fetch(url).then(r=>{if(!r.ok)throw new Error(`${r.status} ${DATA_PATH}`);return r.json()});
    await mergeEventPacks(SCRIPT_URL);initializeState();return data;
  }
  function focusPending(root){
    if(!pendingEventId)return;
    const id=pendingEventId;requestAnimationFrame(()=>{const el=root.querySelector(`#${CSS.escape(id)}`)||document.getElementById(id);if(el)el.scrollIntoView({behavior:'smooth',block:'center'})});
  }
  function exposePendingEvent(){
    if(!pendingEventId)return;
    const ev=data.events.find(e=>e.id===pendingEventId);if(!ev)return;
    for(const l of ev.layers||[])state.layers.add(l);
    for(const a of ev.actor_ids||[])state.actors.add(a);
  }
  async function renderBranch(){
    const token=++requestToken;
    try{
      await ensureData();if(token!==requestToken)return;
      const reader=$('#reader');if(!reader||location.hash!=='#branch=timeline')return;
      exposePendingEvent();renderShell(reader,false);focusPending(reader);
    }catch(err){const reader=$('#reader');if(reader&&location.hash==='#branch=timeline')reader.insertAdjacentHTML('beforeend',`<div class="status">Layered timeline could not load: ${esc(err.message)}</div>`)}
  }
  async function renderStandalone(){
    const root=document.querySelector('.timeline-explorer-standalone');if(!root)return;
    try{await ensureData();exposePendingEvent();renderShell(root,true);focusPending(root)}catch(err){root.innerHTML=`<div class="status">Layered timeline could not load: ${esc(err.message)}</div>`}
  }
  window.addEventListener('potato:navigation',e=>{if(e.detail?.type==='branch'&&e.detail?.id==='timeline')renderBranch()});
  window.addEventListener('hashchange',()=>{if(location.hash==='#branch=timeline')setTimeout(renderBranch,0)});
  const boot=()=>{renderStandalone();if(location.hash==='#branch=timeline')setTimeout(renderBranch,0)};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();