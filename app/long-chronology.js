(()=>{
  const $=s=>document.querySelector(s);
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const slug=v=>String(v||'item').toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,80)||'item';
  const fmtYear=y=>{
    if(!Number.isFinite(y)) return 'Undated';
    if(y<0) return Math.abs(y)+' BCE';
    return y+' CE';
  };
  const mid=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)?Math.round((a+b)/2):Number.isFinite(a)?a:Number.isFinite(b)?b:null;
  const parseModernYears=e=>{
    const text=[e.date,e.date_start,e.date_end,e.timestamp].filter(Boolean).join(' ');
    const years=(text.match(/\b(?:1[0-9]{3}|20[0-9]{2})\b/g)||[]).map(Number);
    return years.length?[Math.min(...years),Math.max(...years)]:[null,null];
  };
  const historicalLabel=e=>{
    if(e.display_date) return e.display_date;
    if(e.date_or_range) return e.date_or_range;
    if(e.date) return e.date;
    if(Number.isFinite(e.year_start)&&Number.isFinite(e.year_end)&&e.year_start!==e.year_end) return fmtYear(e.year_start)+'–'+fmtYear(e.year_end);
    return fmtYear(e.year_start);
  };
  const eraFor=y=>{
    if(!Number.isFinite(y)) return 'undated';
    if(y<-500) return 'deep-antiquity';
    if(y<500) return 'classical';
    if(y<1500) return 'medieval';
    if(y<1800) return 'early-modern';
    if(y<1945) return 'industrial';
    if(y<1987) return 'recent-world';
    return 'living-project';
  };
  const eraLabels={
    'deep-antiquity':'Deep antiquity',
    classical:'Classical worlds',
    medieval:'Medieval worlds',
    'early-modern':'Early modern',
    industrial:'Industrial age',
    'recent-world':'Recent world',
    'living-project':'Living project',
    undated:'Undated'
  };
  const sourceLabels={
    project:'Life & project',
    lineage:'Faith lineages',
    figures:'Origin figures',
    foundations:'Foundations'
  };
  const state={
    sources:new Set(['project','lineage','figures','foundations']),
    eras:new Set(Object.keys(eraLabels).filter(x=>x!=='undated')),
    domains:new Set(),
    families:new Set(),
    clocks:new Set(),
    q:'',
    detail:false,
    sort:'asc',
    mode:'arc'
  };
  let rows=[], meta={};

  function unique(arr){return [...new Set(arr.filter(Boolean))]}
  function familyLabel(x){return String(x||'').replace(/-lineage$/,'').replace(/-/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
  function normalizeProject(e){
    const [a,b]=parseModernYears(e);
    return {
      id:e.id,
      title:e.title,
      start:a,end:b,
      label:e.date||e.timestamp||'Undated',
      source:'project',
      domain:'life / project',
      family:'',
      clock:(e.layers||[]).includes('roadmap')?'roadmap':(e.layers||[])[0]||'project event',
      status:e.epistemic||'project',
      place:'',
      summary:e.summary||e.quote||'',
      quote:e.quote||'',
      tags:unique([...(e.layers||[]),...(e.actor_ids||[]),...(e.motifs||[])]),
      isRoadmap:(e.layers||[]).includes('roadmap'),
      url:e.public_url||'',
      sourceRecords:e.source_records||[],
      raw:e
    };
  }
  function normalizeLineage(e,i){
    return {
      id:'lineage-'+(e.node_id||slug(e.name))+'-'+i,
      title:e.name,
      start:e.year_start,end:e.year_end??e.year_start,
      label:e.date_or_range||historicalLabel(e),
      source:'lineage',
      domain:'religion / tradition',
      family:e.family_id||'',
      clock:e.node_type||'lineage',
      status:e.status||'historical',
      place:e.place||'',
      summary:e.notes||'',
      quote:'',
      tags:unique([e.node_type,e.relation_to_parent,...(e.parent_ids||[])]),
      isRoadmap:['trunk','phase'].includes(e.node_type),
      sourceRecords:e.source_ids||[],
      raw:e
    };
  }
  function normalizeFigure(e){
    return {
      id:e.id,
      title:e.title,
      start:e.year_start,end:e.year_end??e.year_start,
      label:e.date||historicalLabel(e),
      source:'figures',
      domain:'religion / philosophy',
      family:(e.family_ids||[])[0]||'',
      clock:e.kind||'origin figure',
      status:e.status||e.epistemic||'research',
      place:e.place||'',
      summary:e.summary||'',
      quote:'',
      tags:unique([e.kind,...(e.family_ids||[]),...(e.related_node_ids||[]),...(e.related_foundation_names||[])]),
      isRoadmap:true,
      urls:e.source_urls||[],
      sourceRecords:e.source_urls||[],
      raw:e
    };
  }
  function normalizeFoundation(e,i){
    return {
      id:'foundation-'+slug(e.name)+'-'+slug(e.event_type)+'-'+i,
      title:e.name,
      start:e.year_start,end:e.year_end??e.year_start,
      label:e.date_or_range||historicalLabel(e),
      source:'foundations',
      domain:e.domain||'foundation',
      family:'',
      clock:(e.event_type||'foundation event').replaceAll('_',' '),
      status:e.status||'historical',
      place:e.place||e.location||'',
      summary:e.label||e.notes||'',
      quote:'',
      tags:unique([e.domain,e.event_type,e.precision]),
      isRoadmap:['seed_idea','first_operation','adoption_signature','refoundation_revision','constitutional_effect'].includes(e.event_type),
      sourceRecords:e.source?[e.source]:[],
      raw:e
    };
  }

  function searchText(r){return [r.title,r.label,r.domain,r.family,r.clock,r.status,r.place,r.summary,...r.tags].join(' ').toLowerCase()}
  function tokenMatch(r,q){
    const toks=[]; const re=/"([^"]+)"|(\S+)/g; let m;
    while((m=re.exec(q))) toks.push((m[1]||m[2]).toLowerCase());
    const h=searchText(r);
    return toks.every(t=>t.startsWith('-')? !h.includes(t.slice(1)):h.includes(t));
  }
  function selected(r){
    if(!state.sources.has(r.source)) return false;
    if(!state.eras.has(eraFor(mid(r.start,r.end)))) return false;
    if(state.domains.size && !state.domains.has(r.domain)) return false;
    if(state.families.size && (!r.family || !state.families.has(r.family))) return false;
    if(state.clocks.size && !state.clocks.has(r.clock)) return false;
    if(state.q.trim()&&!tokenMatch(r,state.q.trim())) return false;
    if(state.mode==='road'&&!r.isRoadmap) return false;
    if(state.mode==='faith'&&!['lineage','figures'].includes(r.source)) return false;
    if(state.mode==='foundations'&&r.source!=='foundations') return false;
    if(state.mode==='project'&&r.source!=='project') return false;
    return true;
  }
  function sorted(){
    return rows.filter(selected).sort((a,b)=>{
      const ay=Number.isFinite(a.start)?a.start:Infinity,by=Number.isFinite(b.start)?b.start:Infinity;
      const d=ay-by||((a.end??ay)-(b.end??by))||a.title.localeCompare(b.title);
      return state.sort==='desc'?-d:d;
    });
  }
  function centuryBucket(y){
    if(!Number.isFinite(y)) return 'Undated';
    if(y<0){
      const c=Math.ceil(Math.abs(y)/100);
      return c+'th century BCE';
    }
    if(y<100) return '1st century CE';
    const c=Math.floor(y/100)+1;
    const n=c%100, suffix=(n>=11&&n<=13)?'th':({1:'st',2:'nd',3:'rd'}[c%10]||'th');
    return c+suffix+' century CE';
  }
  function detailHTML(r){
    if(!state.detail) return '';
    const links=(r.urls||[]).map(u=>/^https?:\/\//.test(u)?'<a href="'+esc(u)+'" target="_blank" rel="noopener">source ↗</a>':'').join('');
    const refs=(r.sourceRecords||[]).filter(x=>!/^https?:\/\//.test(x)).slice(0,4).map(x=>'<code>'+esc(x)+'</code>').join('');
    return '<div class="chron-extra">'+
      (r.summary?'<p>'+esc(r.summary)+'</p>':'')+
      (r.place?'<p><b>Place</b> '+esc(r.place)+'</p>':'')+
      ((links||refs)?'<div class="chron-sources">'+links+refs+'</div>':'')+
      '</div>';
  }
  function card(r){
    const family=r.family?'<span>'+esc(familyLabel(r.family))+'</span>':'';
    const tags=r.tags.slice(0,state.detail?8:3).map(x=>'<i>'+esc(String(x).replaceAll('_',' '))+'</i>').join('');
    return '<article class="chron-event '+(r.isRoadmap?'is-major':'')+'" id="'+esc(r.id)+'">'+
      '<div class="chron-mark"></div><div class="chron-card">'+
      '<div class="chron-head"><time>'+esc(r.label)+'</time><div><span>'+esc(sourceLabels[r.source])+'</span>'+family+'</div></div>'+
      '<h3>'+esc(r.title)+'</h3>'+
      '<div class="chron-meta"><b>'+esc(r.domain)+'</b><span>'+esc(r.clock)+'</span><span>'+esc(r.status)+'</span></div>'+
      (tags?'<div class="chron-tags">'+tags+'</div>':'')+
      detailHTML(r)+
      '</div></article>';
  }
  function timelineHTML(list){
    if(!list.length) return '<div class="chron-empty">No points match this view. Broaden a lens or clear a filter.</div>';
    const groups=new Map();
    for(const r of list){
      const k=centuryBucket(r.start);
      if(!groups.has(k)) groups.set(k,[]);
      groups.get(k).push(r);
    }
    return [...groups.entries()].map(([k,items])=>
      '<section class="chron-period"><header><b>'+esc(k)+'</b><span>'+items.length+' point'+(items.length===1?'':'s')+'</span></header><div class="chron-events">'+items.map(card).join('')+'</div></section>'
    ).join('');
  }
  function button(label,attrs,on,count){
    return '<button '+attrs+' aria-pressed="'+String(on)+'" class="'+(on?'active':'')+'"><span>'+esc(label)+'</span>'+(Number.isFinite(count)?'<small>'+count+'</small>':'')+'</button>';
  }
  function renderControls(){
    const srcCounts=Object.fromEntries(Object.keys(sourceLabels).map(k=>[k,rows.filter(r=>r.source===k).length]));
    $('#chronSources').innerHTML=Object.entries(sourceLabels).map(([k,v])=>button(v,'data-source="'+k+'"',state.sources.has(k),srcCounts[k])).join('');
    $('#chronEras').innerHTML=Object.entries(eraLabels).filter(([k])=>k!=='undated').map(([k,v])=>button(v,'data-era="'+k+'"',state.eras.has(k),rows.filter(r=>eraFor(mid(r.start,r.end))===k).length)).join('');
    const domains=unique(rows.map(r=>r.domain)).sort();
    $('#chronDomain').innerHTML='<option value="">All domains</option>'+domains.map(x=>'<option value="'+esc(x)+'">'+esc(x)+'</option>').join('');
    const families=unique(rows.map(r=>r.family)).sort();
    $('#chronFamily').innerHTML='<option value="">All faith families</option>'+families.map(x=>'<option value="'+esc(x)+'">'+esc(familyLabel(x))+'</option>').join('');
    const clocks=unique(rows.map(r=>r.clock)).sort();
    $('#chronClock').innerHTML='<option value="">All event types</option>'+clocks.map(x=>'<option value="'+esc(x)+'">'+esc(x)+'</option>').join('');
  }
  function render(){
    const list=sorted();
    const ys=list.flatMap(r=>[r.start,r.end]).filter(Number.isFinite);
    $('#chronReadout').innerHTML='<strong>'+list.length+'</strong> visible points · <strong>'+(ys.length?fmtYear(Math.min(...ys))+' → '+fmtYear(Math.max(...ys)):'—')+'</strong> · '+Object.entries(sourceLabels).filter(([k])=>state.sources.has(k)).map(([,v])=>v).join(' + ');
    $('#chronTimeline').innerHTML=timelineHTML(list);
    document.querySelectorAll('[data-source]').forEach(b=>{const on=state.sources.has(b.dataset.source);b.classList.toggle('active',on);b.setAttribute('aria-pressed',on)});
    document.querySelectorAll('[data-era]').forEach(b=>{const on=state.eras.has(b.dataset.era);b.classList.toggle('active',on);b.setAttribute('aria-pressed',on)});
    document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===state.mode));
  }
  function mode(name){
    state.mode=name;
    if(name==='arc'){state.sources=new Set(['project','lineage','figures','foundations'])}
    if(name==='road'){state.sources=new Set(['project','lineage','figures','foundations'])}
    if(name==='faith'){state.sources=new Set(['lineage','figures'])}
    if(name==='foundations'){state.sources=new Set(['foundations'])}
    if(name==='project'){state.sources=new Set(['project'])}
    render();
  }
  async function load(){
    const baseUrl=new URL('../data/timeline-events.json',location.href);
    const packUrl=new URL('../data/timeline-event-packs/index.json',location.href);
    const [baseR,packR,lineR,figR,foundR]=await Promise.all([
      fetch(baseUrl),fetch(packUrl),
      fetch(new URL('../data/religious-foundation-timeline.json',location.href)),
      fetch(new URL('../data/history-origin-figures.json',location.href)),
      fetch(new URL('../data/house/foundation-timeline-wave-001.json',location.href))
    ]);
    if(!baseR.ok||!lineR.ok||!figR.ok||!foundR.ok) throw new Error('A chronology dataset failed to load.');
    const base=await baseR.json(), line=await lineR.json(), figs=await figR.json(), found=await foundR.json();
    const projectEvents=[...(base.events||[])];
    if(packR.ok){
      const idx=await packR.json();
      const packs=await Promise.all((idx.packs||[]).map(async name=>{
        try{const r=await fetch(new URL('../data/timeline-event-packs/'+name,location.href));return r.ok?(await r.json()).events||[]:[]}catch(_){return[]}
      }));
      for(const p of packs) projectEvents.push(...p);
    }
    const seen=new Set();
    rows=[
      ...projectEvents.map(normalizeProject),
      ...(line.events||[]).map(normalizeLineage),
      ...(figs.events||[]).map(normalizeFigure),
      ...(found.events||[]).map(normalizeFoundation)
    ].filter(r=>{if(seen.has(r.id))return false;seen.add(r.id);return true});
    meta={project:projectEvents.length,lineage:(line.events||[]).length,figures:(figs.events||[]).length,foundations:(found.events||[]).length};
    renderControls(); render();
    $('#chronLoading').hidden=true;
  }
  document.addEventListener('click',e=>{
    const s=e.target.closest('[data-source]'); if(s){state.sources.has(s.dataset.source)?state.sources.delete(s.dataset.source):state.sources.add(s.dataset.source);render();return}
    const er=e.target.closest('[data-era]'); if(er){state.eras.has(er.dataset.era)?state.eras.delete(er.dataset.era):state.eras.add(er.dataset.era);render();return}
    const m=e.target.closest('[data-mode]'); if(m){mode(m.dataset.mode);return}
    const reset=e.target.closest('[data-reset]'); if(reset){
      state.sources=new Set(['project','lineage','figures','foundations']);state.eras=new Set(Object.keys(eraLabels).filter(x=>x!=='undated'));state.domains.clear();state.families.clear();state.clocks.clear();state.q='';state.detail=false;state.sort='asc';state.mode='arc';
      $('#chronSearch').value='';$('#chronDomain').value='';$('#chronFamily').value='';$('#chronClock').value='';$('#chronDetail').checked=false;$('#chronSort').value='asc';render();return;
    }
  });
  document.addEventListener('input',e=>{if(e.target.id==='chronSearch'){state.q=e.target.value;render()}});
  document.addEventListener('change',e=>{
    if(e.target.id==='chronDomain'){state.domains=e.target.value?new Set([e.target.value]):new Set();render()}
    if(e.target.id==='chronFamily'){state.families=e.target.value?new Set([e.target.value]):new Set();render()}
    if(e.target.id==='chronClock'){state.clocks=e.target.value?new Set([e.target.value]):new Set();render()}
    if(e.target.id==='chronDetail'){state.detail=e.target.checked;render()}
    if(e.target.id==='chronSort'){state.sort=e.target.value;render()}
  });
  load().catch(err=>{$('#chronLoading').textContent=err.message;$('#chronLoading').classList.add('error')});
})();