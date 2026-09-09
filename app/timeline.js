(()=>{
  const DATA_PATH='data/timeline-events.json';
  const $=s=>document.querySelector(s);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let data=null;
  let state={layers:new Set(),epistemic:'all',subject:'all',query:'',exact:false,detail:true};
  let requestToken=0;

  function layerById(id){return (data?.layers||[]).find(x=>x.id===id)}
  function human(s){return String(s||'').replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
  function sortKey(e){
    if(e.timestamp)return e.timestamp;
    const d=e.date||'';
    if(/^\d{4}-\d{2}-\d{2}$/.test(d))return d+'T12:00:00Z';
    if(/^\d{4}-\d{2}$/.test(d))return d+'-15T12:00:00Z';
    if(/^\d{4}$/.test(d))return d+'-07-01T12:00:00Z';
    return d;
  }
  function yearOf(e){return String(e.date||e.timestamp||'Undated').slice(0,4)}
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
  function searchable(e){return [e.title,e.summary,e.quote,e.subject,e.status,e.epistemic,...(e.layers||[]),...(e.motifs||[]),...(e.comparators||[])].join(' ').toLowerCase()}
  function filteredEvents(){
    const q=state.query.trim().toLowerCase();
    return (data?.events||[]).filter(e=>{
      if(!e.layers?.some(x=>state.layers.has(x)))return false;
      if(state.epistemic!=='all'&&e.epistemic!==state.epistemic)return false;
      if(state.subject!=='all'&&e.subject!==state.subject)return false;
      if(state.exact&&!isExact(e))return false;
      if(q&&!searchable(e).includes(q))return false;
      return true;
    }).sort((a,b)=>sortKey(a).localeCompare(sortKey(b)));
  }
  function layerChip(id){const l=layerById(id);return `<span class="tl-layer tl-layer-${esc(id)}">${esc(l?.label||human(id))}</span>`}
  function eventCard(e){
    const main=e.layers?.includes('main');
    const quote=e.quote?`<blockquote class="tl-quote">“${esc(e.quote)}”</blockquote>`:'';
    const motifs=e.motifs?.length?`<div class="tl-motifs">${e.motifs.map(x=>`<span>${esc(x)}</span>`).join('')}</div>`:'';
    const comps=e.comparators?.length&&state.detail?`<details class="tl-comparators"><summary>Biblical / comparative references (${e.comparators.length})</summary><div>${e.comparators.map(x=>`<span>${esc(x)}</span>`).join('')}</div></details>`:'';
    const direction=e.source_direction&&state.detail?`<div class="tl-direction"><b>Source direction</b> ${esc(e.source_direction)}</div>`:'';
    const sources=e.source_records?.length?`<div class="tl-sources"><span>Sources</span>${e.source_records.map(p=>`<button data-record="${esc(p)}">${esc(p.split('/').pop())}</button>`).join('')}</div>`:'';
    const body=state.detail?`${e.summary?`<p>${esc(e.summary)}</p>`:''}${quote}${motifs}${comps}${direction}${sources}`:`${quote||''}${motifs}`;
    return `<article class="tl-event ${main?'tl-main-event':''}" data-event-id="${esc(e.id)}"><div class="tl-dot" aria-hidden="true"></div><div class="tl-event-card"><div class="tl-event-head"><div><time>${esc(displayDate(e))}</time><span class="tl-precision">${esc(e.precision)}</span></div><div class="tl-event-meta"><span class="tl-epistemic">${esc(human(e.epistemic))}</span><span>${esc(e.subject)}</span></div></div><h4>${esc(e.title)}</h4><div class="tl-layers">${(e.layers||[]).map(layerChip).join('')}</div>${body}</div></article>`;
  }
  function timelineHTML(events){
    if(!events.length)return `<div class="tl-empty"><strong>No events in this view.</strong><span>Turn on another layer, broaden the evidence filter, or clear search.</span></div>`;
    const groups=new Map();
    for(const e of events){const y=yearOf(e);if(!groups.has(y))groups.set(y,[]);groups.get(y).push(e)}
    return [...groups.entries()].map(([year,items])=>`<section class="tl-year"><div class="tl-year-label"><span>${esc(year)}</span><small>${items.length} event${items.length===1?'':'s'}</small></div><div class="tl-year-events">${items.map(eventCard).join('')}</div></section>`).join('');
  }
  function controlsHTML(){
    const subjects=[...new Set((data.events||[]).map(e=>e.subject))].sort();
    const layerButtons=(data.layers||[]).sort((a,b)=>(a.order||0)-(b.order||0)).map(l=>`<button class="tl-toggle ${state.layers.has(l.id)?'active':''}" data-tl-layer="${esc(l.id)}" aria-pressed="${state.layers.has(l.id)}"><span class="tl-toggle-dot tl-dot-${esc(l.id)}"></span>${esc(l.label)}<small>${(data.events||[]).filter(e=>e.layers?.includes(l.id)).length}</small></button>`).join('');
    return `<div class="tl-control-panel"><div class="tl-presets"><button data-tl-preset="main">Main only</button><button data-tl-preset="biblical">Biblical lens</button><button data-tl-preset="creative">Creative works</button><button data-tl-preset="everything">Everything</button></div><div class="tl-layer-grid">${layerButtons}</div><div class="tl-secondary-controls"><label>Search events<input id="tl-query" type="search" value="${esc(state.query)}" placeholder="quote, Door, song, North, seed…"></label><label>Evidence<select id="tl-epistemic"><option value="all">All evidence classes</option>${(data.epistemic_classes||[]).map(x=>`<option value="${esc(x.id)}" ${state.epistemic===x.id?'selected':''}>${esc(x.label)}</option>`).join('')}</select></label><label>Subject<select id="tl-subject"><option value="all">All subjects</option>${subjects.map(x=>`<option ${state.subject===x?'selected':''}>${esc(x)}</option>`).join('')}</select></label><label class="tl-check"><input id="tl-exact" type="checkbox" ${state.exact?'checked':''}> Exact dates only</label><label class="tl-check"><input id="tl-detail" type="checkbox" ${state.detail?'checked':''}> Detailed cards</label></div></div>`;
  }
  function statsHTML(events){
    const exact=events.filter(isExact).length;
    const quotes=events.filter(e=>e.quote).length;
    const biblical=events.filter(e=>e.layers?.includes('biblical-parallel')||e.layers?.includes('biblical-unlock')).length;
    return `<div><strong>${events.length}</strong><span>visible points</span></div><div><strong>${exact}</strong><span>exact/date points</span></div><div><strong>${quotes}</strong><span>quotes</span></div><div><strong>${biblical}</strong><span>biblical points</span></div>`;
  }
  function renderResults(){
    const events=filteredEvents();
    const stats=$('#tl-stats');if(stats)stats.innerHTML=statsHTML(events);
    const list=$('#tl-results');if(list)list.innerHTML=timelineHTML(events);
    document.querySelectorAll('[data-tl-layer]').forEach(b=>{const on=state.layers.has(b.dataset.tlLayer);b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))});
  }
  function bindControls(root){
    root.addEventListener('click',e=>{
      const layer=e.target.closest('[data-tl-layer]');
      if(layer){const id=layer.dataset.tlLayer;state.layers.has(id)?state.layers.delete(id):state.layers.add(id);renderResults();return}
      const preset=e.target.closest('[data-tl-preset]');
      if(preset){
        const p=preset.dataset.tlPreset;
        const sets={main:['main'],biblical:['main','quote','biblical-parallel','biblical-unlock','identity-doctrine'],creative:['main','music','art'],everything:(data.layers||[]).map(x=>x.id)};
        state.layers=new Set(sets[p]||sets.main);renderExplorer();return;
      }
    });
    root.querySelector('#tl-query')?.addEventListener('input',e=>{state.query=e.target.value;renderResults()});
    root.querySelector('#tl-epistemic')?.addEventListener('change',e=>{state.epistemic=e.target.value;renderResults()});
    root.querySelector('#tl-subject')?.addEventListener('change',e=>{state.subject=e.target.value;renderResults()});
    root.querySelector('#tl-exact')?.addEventListener('change',e=>{state.exact=e.target.checked;renderResults()});
    root.querySelector('#tl-detail')?.addEventListener('change',e=>{state.detail=e.target.checked;renderResults()});
  }
  function renderExplorer(){
    const reader=$('#reader');if(!reader||location.hash!=='#branch=chronology')return;
    const events=filteredEvents();
    reader.innerHTML=`<div class="tl-hero"><div><div class="eyebrow">Layered chronology explorer</div><h2>CHRONOLOGY</h2><p class="summary">One time axis, independently toggleable evidence layers. Keep the main life/project arc visible, then add quotes, biblical parallels, later biblical unlocks, songs, public declarations, predictions and archive research without flattening their source status.</p></div><div class="tl-stats" id="tl-stats">${statsHTML(events)}</div></div><div class="tl-help"><strong>How to read it</strong><span>Layer = what kind of datapoint it is. Evidence = how we know it. A dated Tim statement and a later biblical research unlock can therefore appear separately on the same timeline.</span><button data-record="docs/TIMELINE-EVENT-STANDARD.md">Open event standard</button></div>${controlsHTML()}<div class="tl-axis" id="tl-results">${timelineHTML(events)}</div><div class="section"><h3>Underlying chronology records</h3><div class="tl-record-links"><button data-record="data/tim-dooley-timeline.json">Identity-safe master timeline</button><button data-record="knowledge/chronology/reverse-biblical-overlap-timeline-2025-2026.json">Reverse biblical chronology</button><button data-record="data/timeline-events.json">Layered event dataset</button><button data-record="knowledge/creative/tim-dooley-suno-music-archive.json">Music archive</button></div></div><div id="record-detail"></div>`;
    bindControls(reader);
  }
  async function loadAndRender(){
    const token=++requestToken;
    try{
      data=data||await fetch(DATA_PATH).then(r=>{if(!r.ok)throw new Error(`${r.status} ${DATA_PATH}`);return r.json()});
      if(token!==requestToken)return;
      if(!state.layers.size)state.layers=new Set((data.layers||[]).filter(x=>x.default).map(x=>x.id));
      renderExplorer();
    }catch(err){
      const reader=$('#reader');if(reader&&location.hash==='#branch=chronology')reader.insertAdjacentHTML('beforeend',`<div class="status">Layered timeline could not load: ${esc(err.message)}</div>`);
    }
  }
  window.addEventListener('potato:navigation',e=>{if(e.detail?.type==='branch'&&e.detail?.id==='chronology')loadAndRender()});
  window.addEventListener('hashchange',()=>{if(location.hash==='#branch=chronology')setTimeout(loadAndRender,0)});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{if(location.hash==='#branch=chronology')setTimeout(loadAndRender,0)});
  else if(location.hash==='#branch=chronology')setTimeout(loadAndRender,0);
})();