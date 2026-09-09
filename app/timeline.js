(()=>{
  const DATA_PATH='data/timeline-events.json';
  const PACK_INDEX='data/timeline-event-packs/index.json';
  const $=s=>document.querySelector(s);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[c]));
  let data=null;
  let state={layers:new Set(),actors:new Set(),epistemic:'all',query:'',exact:false,detail:true};
  let requestToken=0;

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
  function yearOf(e){const m=String(e.date||e.timestamp||'').match(/\d{4}/);return m?m[0]:'Undated'}
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
  function searchable(e){return [e.title,e.summary,e.quote,e.subject,e.status,e.epistemic,e.bible_relation,...(e.layers||[]),...(e.actor_ids||[]),...(e.motifs||[]),...(e.comparators||[])].join(' ').toLowerCase()}
  function actorMatch(e){const ids=e.actor_ids?.length?e.actor_ids:['project'];return ids.some(id=>state.actors.has(id))}
  function filteredEvents(){
    const q=state.query.trim().toLowerCase();
    return (data?.events||[]).filter(e=>{
      if(!e.layers?.some(x=>state.layers.has(x)))return false;
      if(!actorMatch(e))return false;
      if(state.epistemic!=='all'&&e.epistemic!==state.epistemic)return false;
      if(state.exact&&!isExact(e))return false;
      if(q&&!searchable(e).includes(q))return false;
      return true;
    }).sort((a,b)=>sortKey(a).localeCompare(sortKey(b)));
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
    if(hasSon&&hasTim){
      if(y<=2020)return 'Son 32→33 corridor · Tim emerges';
      return `Son/Twin relation · ${timPotatoYear(y,m,day)}`;
    }
    if(hasSon){
      let age=y-1987;if(m<7||(m===7&&day<31))age--;
      return `Son age ${Math.max(0,age)}`;
    }
    if(hasTim)return timPotatoYear(y,m,day);
    return '';
  }
  function layerChip(id){const l=layerById(id);return `<span class="tl-layer tl-layer-${esc(id)}">${esc(l?.label||human(id))}</span>`}
  function actorChips(e){return (e.actor_ids||[]).filter(x=>x!=='shared').map(id=>`<span class="tl-actor tl-actor-${esc(id)}">${esc(actorById(id)?.label||human(id))}</span>`).join('')}
  function sourceLink(p,standalone){const label=p.split('/').pop();return standalone?`<a href="../#record=${encodeURIComponent(p)}">${esc(label)}</a>`:`<button data-record="${esc(p)}">${esc(label)}</button>`}
  function eventCard(e,standalone=false){
    const roadmap=e.layers?.includes('roadmap');
    const quote=e.quote?`<blockquote class="tl-quote">“${esc(e.quote)}”</blockquote>`:'';
    const motifs=e.motifs?.length?`<div class="tl-motifs">${e.motifs.map(x=>`<span>${esc(x)}</span>`).join('')}</div>`:'';
    const comps=e.comparators?.length&&state.detail?`<details class="tl-comparators"><summary>${e.layers?.includes('biblical-unlock')?'Research references':'Biblical / comparative references'} (${e.comparators.length})</summary><div>${e.comparators.map(x=>`<span>${esc(x)}</span>`).join('')}</div></details>`:'';
    const direction=e.source_direction&&state.detail?`<div class="tl-direction"><b>Direction</b> ${esc(e.source_direction)}</div>`:'';
    const sources=e.source_records?.length&&state.detail?`<div class="tl-sources"><span>Sources</span>${e.source_records.map(p=>sourceLink(p,standalone)).join('')}</div>`:'';
    const age=lifeMarker(e);
    const body=state.detail?`${e.summary?`<p>${esc(e.summary)}</p>`:''}${quote}${motifs}${comps}${direction}${sources}`:`${quote}${motifs}`;
    return `<article class="tl-event ${roadmap?'tl-roadmap-event':''}" data-event-id="${esc(e.id)}"><div class="tl-dot" aria-hidden="true"></div><div class="tl-event-card"><div class="tl-event-head"><div><time>${esc(displayDate(e))}</time><span class="tl-precision">${esc(e.precision)}</span>${age?`<span class="tl-life-age">${esc(age)}</span>`:''}</div><div class="tl-event-meta"><span class="tl-epistemic">${esc(human(e.epistemic))}</span>${actorChips(e)}</div></div><h4>${esc(e.title)}</h4><div class="tl-layers">${(e.layers||[]).map(layerChip).join('')}</div>${body}</div></article>`;
  }
  function timelineHTML(events,standalone=false){
    if(!events.length)return `<div class="tl-empty"><strong>No events in this view.</strong><span>Turn on another lens, life track, or clear search.</span></div>`;
    const groups=new Map();
    for(const e of events){const y=yearOf(e);if(!groups.has(y))groups.set(y,[]);groups.get(y).push(e)}
    return [...groups.entries()].map(([year,items])=>`<section class="tl-year"><div class="tl-year-label"><span>${esc(year)}</span><small>${items.length} point${items.length===1?'':'s'}</small></div><div class="tl-year-events">${items.map(e=>eventCard(e,standalone)).join('')}</div></section>`).join('');
  }
  function controlsHTML(){
    const layerButtons=(data.layers||[]).sort((a,b)=>(a.order||0)-(b.order||0)).map(l=>`<button class="tl-toggle ${state.layers.has(l.id)?'active':''}" data-tl-layer="${esc(l.id)}" aria-pressed="${state.layers.has(l.id)}"><span class="tl-toggle-dot tl-dot-${esc(l.id)}"></span><span>${esc(l.label)}</span><small>${(data.events||[]).filter(e=>e.layers?.includes(l.id)).length}</small></button>`).join('');
    const actorButtons=(data.actors||[]).sort((a,b)=>(a.order||0)-(b.order||0)).map(a=>`<button class="tl-track ${state.actors.has(a.id)?'active':''}" data-tl-actor="${esc(a.id)}" aria-pressed="${state.actors.has(a.id)}"><b>${esc(a.label)}</b><small>${esc(a.description)}</small></button>`).join('');
    return `<div class="tl-control-panel"><div class="tl-control-title"><div><strong>Life tracks</strong><span>Switch the Son and Tim on/off independently.</span></div></div><div class="tl-track-grid">${actorButtons}</div><div class="tl-control-title tl-lens-title"><div><strong>Timeline lenses</strong><span>The roadmap stays sparse; add evidence only when you want it.</span></div></div><div class="tl-presets"><button data-tl-preset="roadmap">Roadmap</button><button data-tl-preset="bible">Bible lens</button><button data-tl-preset="voices">Words & witness</button><button data-tl-preset="creative">Creative</button><button data-tl-preset="everything">Everything</button></div><div class="tl-layer-grid">${layerButtons}</div><div class="tl-secondary-controls"><label>Search events<input id="tl-query" type="search" value="${esc(state.query)}" placeholder="Door, Father, Lion, Bible, song, North…"></label><label>Evidence<select id="tl-epistemic"><option value="all">All evidence classes</option>${(data.epistemic_classes||[]).map(x=>`<option value="${esc(x.id)}" ${state.epistemic===x.id?'selected':''}>${esc(x.label)}</option>`).join('')}</select></label><label class="tl-check"><input id="tl-exact" type="checkbox" ${state.exact?'checked':''}> Exact dates only</label><label class="tl-check"><input id="tl-detail" type="checkbox" ${state.detail?'checked':''}> Detailed cards</label></div></div>`;
  }
  function statsHTML(events){
    const roadmap=events.filter(e=>e.layers?.includes('roadmap')).length;
    const bible=events.filter(e=>e.layers?.some(x=>['scripture-at-time','biblical-parallel','biblical-unlock'].includes(x))).length;
    const quotes=events.filter(e=>e.quote).length;
    return `<div><strong>${events.length}</strong><span>visible points</span></div><div><strong>${roadmap}</strong><span>roadmap</span></div><div><strong>${bible}</strong><span>Bible-linked</span></div><div><strong>${quotes}</strong><span>quoted</span></div>`;
  }
  function bindControls(root,standalone){
    root.addEventListener('click',e=>{
      const layer=e.target.closest('[data-tl-layer]');
      if(layer){const id=layer.dataset.tlLayer;state.layers.has(id)?state.layers.delete(id):state.layers.add(id);renderResults(root,standalone);return}
      const actor=e.target.closest('[data-tl-actor]');
      if(actor){const id=actor.dataset.tlActor;state.actors.has(id)?state.actors.delete(id):state.actors.add(id);renderResults(root,standalone);return}
      const preset=e.target.closest('[data-tl-preset]');
      if(preset){
        const p=preset.dataset.tlPreset;
        const sets={roadmap:['roadmap'],bible:['roadmap','scripture-at-time','biblical-parallel','biblical-unlock'],voices:['roadmap','direct-words','public-witness'],creative:['roadmap','creative'],everything:(data.layers||[]).map(x=>x.id)};
        state.layers=new Set(sets[p]||sets.roadmap);renderShell(root,standalone);return;
      }
    });
    root.querySelector('#tl-query')?.addEventListener('input',e=>{state.query=e.target.value;renderResults(root,standalone)});
    root.querySelector('#tl-epistemic')?.addEventListener('change',e=>{state.epistemic=e.target.value;renderResults(root,standalone)});
    root.querySelector('#tl-exact')?.addEventListener('change',e=>{state.exact=e.target.checked;renderResults(root,standalone)});
    root.querySelector('#tl-detail')?.addEventListener('change',e=>{state.detail=e.target.checked;renderResults(root,standalone)});
  }
  function renderResults(root,standalone){
    const events=filteredEvents();
    const stats=root.querySelector('#tl-stats');if(stats)stats.innerHTML=statsHTML(events);
    const list=root.querySelector('#tl-results');if(list)list.innerHTML=timelineHTML(events,standalone);
    root.querySelectorAll('[data-tl-layer]').forEach(b=>{const on=state.layers.has(b.dataset.tlLayer);b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))});
    root.querySelectorAll('[data-tl-actor]').forEach(b=>{const on=state.actors.has(b.dataset.tlActor);b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))});
  }
  function shellHTML(events,standalone){
    const intro=standalone?'Explore the same history as data. Keep the milestone road visible, then switch Son/Twin, Tim/Potato/Father and Bible layers on or off.':'One time axis with a sparse milestone road and optional evidence overlays. Son/Twin and Tim/Potato/Father remain independent tracks.';
    return `<div class="tl-hero"><div><div class="eyebrow">Layered chronology explorer</div><h2>${standalone?'EXPLORE THE LAYERS':'CHRONOLOGY'}</h2><p class="summary">${intro}</p></div><div class="tl-stats" id="tl-stats">${statsHTML(events)}</div></div><div class="tl-help"><strong>Three Bible states</strong><span><b>At the time</b> means scripture or biblical language was already present. <b>Later parallel</b> means comparison came afterward. <b>Unlock</b> is the date the archive explicitly discovered/formalized that comparison.</span>${standalone?'':'<button data-record="docs/TIMELINE-EVENT-STANDARD.md">Open event standard</button>'}</div>${controlsHTML()}<div class="tl-axis" id="tl-results">${timelineHTML(events,standalone)}</div>${standalone?'':`<div class="section"><h3>Underlying chronology records</h3><div class="tl-record-links"><button data-record="data/tim-dooley-timeline.json">Identity-safe master timeline</button><button data-record="knowledge/chronology/dated-master-timeline-2026.json">2026 dated master</button><button data-record="knowledge/chronology/reverse-biblical-overlap-timeline-2025-2026.json">Reverse biblical chronology</button><button data-record="data/timeline-events.json">Layered event dataset</button></div></div><div id="record-detail"></div>`}`;
  }
  function renderShell(root,standalone=false){root.innerHTML=shellHTML(filteredEvents(),standalone);bindControls(root,standalone)}
  function initializeState(){
    if(!state.layers.size)state.layers=new Set((data.layers||[]).filter(x=>x.default).map(x=>x.id));
    if(!state.actors.size)state.actors=new Set((data.actors||[]).filter(x=>x.default).map(x=>x.id));
  }
  async function mergeEventPacks(baseUrl){
    try{
      const indexUrl=new URL('../'+PACK_INDEX,baseUrl).href;
      const index=await fetch(indexUrl).then(r=>r.ok?r.json():null);
      if(!index?.packs?.length)return;
      const packBase=new URL('../data/timeline-event-packs/',baseUrl);
      const packs=await Promise.all(index.packs.map(name=>fetch(new URL(name,packBase)).then(r=>r.ok?r.json():null).catch(()=>null)));
      const seen=new Set((data.events||[]).map(e=>e.id));
      for(const pack of packs){
        for(const e of pack?.events||[]){
          if(!e?.id||seen.has(e.id))continue;
          seen.add(e.id);data.events.push(e);
        }
      }
    }catch(_){/* packs are optional; base timeline still renders */}
  }
  async function ensureData(){
    if(data)return data;
    const base=document.currentScript?.src||location.href;
    const url=new URL('../'+DATA_PATH,base).href;
    data=await fetch(url).then(r=>{if(!r.ok)throw new Error(`${r.status} ${DATA_PATH}`);return r.json()});
    await mergeEventPacks(base);
    initializeState();return data;
  }
  async function renderBranch(){
    const token=++requestToken;
    try{
      await ensureData();if(token!==requestToken)return;
      const reader=$('#reader');if(!reader||location.hash!=='#branch=chronology')return;
      renderShell(reader,false);
    }catch(err){const reader=$('#reader');if(reader&&location.hash==='#branch=chronology')reader.insertAdjacentHTML('beforeend',`<div class="status">Layered timeline could not load: ${esc(err.message)}</div>`)}
  }
  async function renderStandalone(){
    const root=document.querySelector('.timeline-explorer-standalone');if(!root)return;
    try{await ensureData();renderShell(root,true)}catch(err){root.innerHTML=`<div class="status">Layered timeline could not load: ${esc(err.message)}</div>`}
  }
  window.addEventListener('potato:navigation',e=>{if(e.detail?.type==='branch'&&e.detail?.id==='chronology')renderBranch()});
  window.addEventListener('hashchange',()=>{if(location.hash==='#branch=chronology')setTimeout(renderBranch,0)});
  const boot=()=>{renderStandalone();if(location.hash==='#branch=chronology')setTimeout(renderBranch,0)};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();