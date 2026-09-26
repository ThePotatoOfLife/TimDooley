(function(){
  'use strict';
  if(typeof document==='undefined'||document.querySelector('.site-access'))return;
  const script=document.currentScript;
  let appBase,siteBase;
  try{appBase=new URL('./',script?.src||document.baseURI);siteBase=new URL('../',appBase)}catch(_){return}
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const href=route=>new URL(String(route||'/').replace(/^\//,''),siteBase).href;
  const assetVersion=(()=>{
    try{return new URL(script?.src||document.baseURI).searchParams.get('v')||'unversioned';}
    catch(_){return 'unversioned';}
  })();
  const fetchJson=async route=>{
    const key='site-access:'+assetVersion+':'+route;
    try{
      const cached=sessionStorage.getItem(key);
      if(cached)return JSON.parse(cached);
    }catch(_){}
    try{
      const response=await fetch(href(route),{cache:'no-cache'});
      if(!response.ok)return null;
      const data=await response.json();
      try{sessionStorage.setItem(key,JSON.stringify(data));}catch(_){}
      return data;
    }catch(_){return null}
  };
  const routePath=()=>{
    try{
      let p=location.pathname,base=new URL(siteBase).pathname.replace(/\/$/,'');
      if(base&&p.startsWith(base))p=p.slice(base.length);
      p='/' + p.replace(/^\/+|\/+$/g,'');
      if(p==='/index.html')return '/';
      return p.replace(/\/index\.html$/,'/').replace(/\/+/g,'/') || '/';
    }catch(_){return '/'}
  };
  const current=routePath();
  const institutionContext=current.startsWith('/rooms/potatoverse-canon/beings/cia/');
  const institutionZone=current.startsWith('/rooms/potatoverse-canon/beings/cia/bank/')?'bank':
    current.startsWith('/rooms/potatoverse-canon/beings/cia/file/')?'dossier':
    current.startsWith('/rooms/potatoverse-canon/beings/cia/associations/')?'associations':
    current.startsWith('/rooms/potatoverse-canon/beings/cia/incidents/')?'incidents':
    institutionContext?'archive':'';
  const fallbackEntries=[
    {id:'home',label:'Home',route:'/',kind:'start',note:'Project entrance',aliases:['start','homepage']},
    {id:'news',label:'Current World',route:'/news/',kind:'world',note:'Live news',aliases:['news','headlines','current','today']},
    {id:'world-map',label:'World Map',route:'/world-map/',kind:'world',note:'Interactive atlas',aliases:['map','countries','atlas']},
    {id:'tim',label:'Tim Dooley',route:'/tim-dooley/',kind:'project',note:'Main portrait',aliases:['tim','father','potato']},
    {id:'house',label:'House',route:'/house/',kind:'project',note:'How the project fits together',aliases:['house','architecture','structure']},
    {id:'rooms',label:'Rooms',route:'/rooms/',kind:'project',note:'Knowledge owners',aliases:['rooms','dwellings']},
    {id:'people-cases',label:'People & Cases',route:'/rooms/objects/',kind:'find',note:'Search House inhabitants',aliases:['people','cases','objects','entities','find','search']},
    {id:'index-a-z',label:'A–Z',route:'/index-a-z/',kind:'find',note:'Known-term lookup',aliases:['index','terms','glossary','find']},
    {id:'timeline',label:'Timeline',route:'/timeline/',kind:'find',note:'Events and chronology',aliases:['history','dates','chronology']},
    {id:'sources',label:'Sources',route:'/context/source-authority/',kind:'find',note:'Evidence and provenance',aliases:['evidence','source','provenance']},
    {id:'explore',label:'Explore',route:'/explore/',kind:'find',note:'Relationship explorer',aliases:['archive','relationships']},
    {id:'cia-character-archive',label:'Potatoverse CIA · Character Archive',route:'/rooms/potatoverse-canon/beings/cia/',kind:'direct',scope:'POTATOVERSE',note:'Characters, Incidents & Associations · authored project archive',aliases:['potatoverse cia','character cia','characters incidents associations','character archive','dossiers']},
    {id:'mud-bank',label:'World Spiritual Bank / Mud Bank',route:'/rooms/potatoverse-canon/beings/cia/bank/',kind:'direct',scope:'POTATOVERSE',note:'Fictional North Root Ledger · Character Archive sub-accounts',aliases:['mud bank','dooley welfare','karma bank','balance sheet']},
    {id:'intelligence-cia',label:'U.S. CIA · Central Intelligence Agency',route:'/shadow-farm/#intelligence-desk',kind:'direct',scope:'REAL WORLD',note:'U.S. foreign-intelligence institution · Intelligence Desk',aliases:['us cia','u.s. cia','central intelligence agency','real cia','intelligence desk']},
    {id:'fbi-legacy',label:'FBI — retired character-bureau predecessor',route:'/rooms/potatoverse-canon/beings/fbi/',kind:'direct',note:'Read-only migration history',aliases:['fbi','figures bonds incidents']},
    {id:'economy',label:'Economy & Finance',route:'/economy/',kind:'world',note:'Debt, banking, ownership',aliases:['economy','finance','debt','bonds','fed','federal reserve','ecb','eurosystem']},
    {id:'tts',label:'Read Aloud / TTS',route:'/tools/tts/',kind:'direct',note:'Text-to-speech tools and reader controls',aliases:['tts','text to speech','read aloud','listen']},
    {id:'claims',label:'Claims & Statements',route:'/tim-dooley/claims/',kind:'direct',note:'Claims and attributed statements',aliases:['claims','statements','assertions']},
    {id:'public-witness',label:'Public Witness',route:'/tim-dooley/public-witness/',kind:'direct',note:'Public record and witness material',aliases:['public witness','public record','witness']},
    {id:'science',label:'Science',route:'/science/',kind:'project',note:'Models, evidence, falsifiers',aliases:['science','physics','biology','research']},
    {id:'religion',label:'Religion',route:'/religion/',kind:'project',note:'Theology and comparisons',aliases:['religion','bible','trinity','theology']},
    {id:'hours',label:'100,000 Hours',route:'/tim-dooley/100000-hours/',kind:'direct',note:'Public-presence model',aliases:['100000 hours','100,000 hours','streaming','livestream']}
  ];
  let curatedEntries=[...fallbackEntries];
  let accessGroups={
    landmarks:['cia-character-archive','mud-bank'],
    go_now:['news','world-map','tim','house','rooms'],
    find:['people-cases','index-a-z','timeline','sources','explore'],
    direct_doors:['cia-character-archive','mud-bank','intelligence-cia','economy','tts','claims','public-witness','science','religion','hours']
  };
  const wrapper=document.createElement('div');
  wrapper.className='site-access';
  wrapper.setAttribute('data-no-tts','');
  wrapper.setAttribute('aria-label','Site quick access');
  const pageTitle=(document.querySelector('h1')?.textContent||document.title||'Current page').replace(/\s+/g,' ').trim();
  const institutionShortcuts=institutionContext?'<nav class="site-access-local-shortcuts" aria-label="Character Archive building shortcuts">'+
    '<span>You are in '+esc(institutionZone||'the building')+'</span>'+
    '<a'+(institutionZone==='archive'?' aria-current="page"':'')+' href="'+esc(href('/rooms/potatoverse-canon/beings/cia/'))+'">Archive</a>'+
    '<a'+(institutionZone==='bank'?' aria-current="page"':'')+' href="'+esc(href('/rooms/potatoverse-canon/beings/cia/bank/'))+'">Bank</a>'+
    '</nav>':'';
  wrapper.innerHTML=institutionShortcuts+'<nav class="site-access-dock" aria-label="Quick access">'+
    '<a data-site-access-route="/" href="'+esc(href('/'))+'">Home</a>'+
    '<a class="site-access-news" data-site-access-route="/news/" href="'+esc(href('/news/'))+'">News</a>'+
    '<a data-site-access-route="/world-map/" href="'+esc(href('/world-map/'))+'">Map</a>'+
    '<button type="button" data-site-access-find aria-expanded="false">Find</button>'+
    '<button type="button" data-site-access-menu aria-expanded="false">Places</button>'+
    '</nav>'+
    '<section class="site-access-panel" data-site-access-panel hidden aria-label="Site menu">'+
      '<div class="site-access-head"><div><small>Quick access · you are in</small><strong>'+esc(pageTitle)+'</strong></div><button class="site-access-close" type="button" aria-label="Close quick access">×</button></div>'+
      '<form class="site-access-search" role="search"><input type="search" autocomplete="off" placeholder="Find Character Archive, U.S. CIA, Tim, debt, a Room…" aria-label="Find in the project"><button type="submit">Find</button></form>'+
      '<div data-site-access-content></div>'+
    '</section>';
  document.body.appendChild(wrapper);
  const publishClearance=()=>{
    const rect=wrapper.getBoundingClientRect();
    const bottomGap=Math.max(0,window.innerHeight-rect.bottom);
    document.documentElement.style.setProperty('--site-access-clearance',Math.ceil(bottomGap+rect.height)+'px');
  };
  publishClearance();
  if(typeof ResizeObserver!=='undefined'){
    const accessObserver=new ResizeObserver(publishClearance);
    accessObserver.observe(wrapper);
  }
  window.addEventListener('resize',publishClearance,{passive:true});

  const panel=wrapper.querySelector('[data-site-access-panel]');
  const input=wrapper.querySelector('.site-access-search input');
  const content=wrapper.querySelector('[data-site-access-content]');
  const menuBtn=wrapper.querySelector('[data-site-access-menu]');
  const findBtn=wrapper.querySelector('[data-site-access-find]');
  const closeBtn=wrapper.querySelector('.site-access-close');
  let returnFocus=menuBtn;
  wrapper.querySelectorAll('[data-site-access-route]').forEach(a=>{
    const r=a.getAttribute('data-site-access-route');
    if(r==='/'?current==='/':current.startsWith(r))a.setAttribute('aria-current','page');
  });
  let loaded=false,index=[...curatedEntries];
  const aliasText=e=>Array.isArray(e.aliases)?e.aliases.join(' '):(e.aliases||'');
  const key=e=>(e.label+' '+aliasText(e)+' '+(e.note||'')+' '+(e.kind||'')).toLowerCase();
  const priority=e=>({object:5,'case-ready':5,direct:4,world:3,project:2,page:1,find:1,start:0}[e.kind]??1);
  const unique=rows=>{
    const seen=new Set();
    return rows.filter(x=>{
      const k=(x.label||'')+'|'+(x.route||'');
      if(!x.label||!x.route||seen.has(k))return false;
      seen.add(k);return true;
    });
  };
  const loadIndex=async()=>{
    if(loaded)return;
    loaded=true;
    try{
      const [contract,surfaces,inhabitants,roomsData]=await Promise.all([
        fetchJson('/data/house/site-access.json'),
        fetchJson('/data/house/public-surfaces.json'),
        fetchJson('/data/house/room-inhabitants.json'),
        fetchJson('/data/house/rooms.json')
      ]);
      const roomNames=Object.fromEntries((roomsData?.rooms||[]).filter(x=>x?.id).map(x=>[x.id,x.title||x.id]));
      if(Array.isArray(contract?.entries)&&contract.entries.length){
        curatedEntries=contract.entries;
        index=[...curatedEntries];
      }
      if(contract?.groups)accessGroups=contract.groups;
      for(const row of surfaces?.surfaces||[])if(row?.status==='active'&&row?.route)index.push({
        label:row.title||row.id,
        route:row.route,
        kind:'page',
        note:row.surface_type||'public surface',
        context:row.primary_parent?'Under '+row.primary_parent:'Public surface',
        aliases:row.id
      });
      for(const row of inhabitants?.inhabitants||[])if(row?.route){
        const rooms=(row.room_ids||[]).map(id=>roomNames[id]||id).filter(Boolean);
        index.push({
          label:row.label||row.id,
          route:row.route,
          kind:row.kind||'object',
          note:row.summary||'House object',
          context:rooms.length?'Rooms: '+rooms.join(' · '):'House object',
          aliases:(row.id||'')+' '+(row.room_ids||[]).join(' ')
        });
      }
      index=unique(index);
    }catch(_){}
  };
  const group=(title,entries)=>'<div class="site-access-group"><span>'+esc(title)+'</span><div class="site-access-links">'+entries.map(e=>'<a href="'+esc(href(e.route))+'"><b>'+esc(e.label)+'</b>'+(e.scope?'<i class="site-access-scope">'+esc(e.scope)+'</i>':'')+'<small>'+esc(e.note||'')+'</small></a>').join('')+'</div></div>';
  const landmarkCards=entries=>'<section class="site-access-landmarks" aria-label="Project landmarks"><div class="site-access-landmark-head"><b>Project landmarks</b><small>Go by name. You do not need to remember the House hierarchy.</small></div><div class="site-access-landmark-grid">'+entries.map(e=>{
    const kind=e.id==='mud-bank'?'BANK':'FILES';
    const short=e.id==='mud-bank'?'Spiritual Bank':'Character Archive';
    return '<a class="site-access-landmark" href="'+esc(href(e.route))+'"><em>'+kind+'</em><span><b>'+short+'</b><small>'+esc(e.note||'')+'</small></span><i>→</i></a>';
  }).join('')+'</div></section>';
  const renderDefault=async()=>{
    await loadIndex();
    content.className='site-access-groups';
    const byId=id=>curatedEntries.find(e=>e.id===id);
    const rows=ids=>(ids||[]).map(byId).filter(Boolean);
    content.innerHTML=
      landmarkCards(rows(accessGroups.landmarks||['cia-character-archive','mud-bank']))+
      '<div class="site-access-group-grid">'+
      group('Go now',rows(accessGroups.go_now))+
      group('Find',rows(accessGroups.find))+
      group('More places',rows((accessGroups.direct_doors||[]).filter(id=>!(accessGroups.landmarks||[]).includes(id))))+
      '</div>';
  };
  const renderSearch=async()=>{
    const q=input.value.trim().toLowerCase();
    if(!q){await renderDefault();return}
    await loadIndex();
    if(q==='cia'){
      const ids=['cia-character-archive','intelligence-cia'];
      const rows=ids.map(id=>curatedEntries.find(e=>e.id===id)).filter(Boolean);
      content.className='site-access-results site-access-disambiguation';
      content.innerHTML='<div class="site-access-choice-head"><b>Which CIA?</b><small>Same acronym, different namespace. Choose before entering.</small></div>'+rows.map(e=>'<a class="site-access-result" href="'+esc(href(e.route))+'"><span><b>'+esc(e.label)+'</b><small>'+esc(e.note||'')+'</small></span><em>'+esc(e.scope||e.kind||'result')+'</em></a>').join('');
      return;
    }
    const terms=q.split(/\s+/).filter(Boolean);
    const rows=index.map(e=>{
      const hay=key(e),label=e.label.toLowerCase(),aliases=aliasText(e).toLowerCase();let score=0;
      for(const t of terms){
        if(!hay.includes(t))return null;
        if(label===t)score+=30;
        else if(label.startsWith(t))score+=16;
        else if(aliases.split(/\s+/).includes(t))score+=12;
        else if(aliases.includes(t))score+=7;
        else if(hay.includes(' '+t))score+=4;
        else score+=1;
      }
      score+=priority(e);
      return {e,score};
    }).filter(Boolean).sort((a,b)=>b.score-a.score||priority(b.e)-priority(a.e)||a.e.label.localeCompare(b.e.label)).slice(0,12).map(x=>x.e);
    content.className='site-access-results';
    content.innerHTML=rows.length?rows.map(e=>'<a class="site-access-result" href="'+esc(href(e.route))+'"><span><b>'+esc(e.label)+'</b><small>'+esc(e.note||'')+'</small>'+(e.context?'<small class="site-access-context">'+esc(e.context)+'</small>':'')+'</span><em>'+esc(e.kind||'result')+'</em></a>').join(''):'<div class="site-access-empty">No quick result. Try a broader word or open A–Z / Explore.</div>';
  };
  const setOpen=(open,focusSearch=false,trigger=null)=>{
    if(open&&trigger)returnFocus=trigger;
    panel.hidden=!open;
    menuBtn.setAttribute('aria-expanded',String(open));
    findBtn.setAttribute('aria-expanded',String(open));
    if(open){if(!input.value)void renderDefault();if(focusSearch)setTimeout(()=>input.focus(),0)}
  };
  menuBtn.addEventListener('click',()=>setOpen(panel.hidden,false,menuBtn));
  findBtn.addEventListener('click',()=>setOpen(true,true,findBtn));
  closeBtn.addEventListener('click',()=>{setOpen(false);returnFocus?.focus?.()});
  input.addEventListener('input',renderSearch);
  const resultLinks=()=>[...content.querySelectorAll('.site-access-result')];
  const focusResult=(index)=>{
    const rows=resultLinks();if(!rows.length)return false;
    const safe=Math.max(0,Math.min(rows.length-1,index));
    rows[safe].focus();return true;
  };
  const moveResultFocus=(direction)=>{
    const rows=resultLinks();if(!rows.length)return false;
    const currentIndex=rows.indexOf(document.activeElement);
    const next=currentIndex<0?(direction>0?0:rows.length-1):(currentIndex+direction+rows.length)%rows.length;
    rows[next].focus();return true;
  };
  input.addEventListener('keydown',e=>{
    if(e.key==='ArrowDown'){if(focusResult(0))e.preventDefault();}
    else if(e.key==='ArrowUp'){const rows=resultLinks();if(rows.length){rows[rows.length-1].focus();e.preventDefault();}}
  });
  content.addEventListener('keydown',e=>{
    if(!e.target.closest('.site-access-result'))return;
    if(e.key==='ArrowDown'){if(moveResultFocus(1))e.preventDefault();}
    else if(e.key==='ArrowUp'){if(moveResultFocus(-1))e.preventDefault();}
    else if(e.key==='Home'){if(focusResult(0))e.preventDefault();}
    else if(e.key==='End'){const rows=resultLinks();if(rows.length){rows[rows.length-1].focus();e.preventDefault();}}
  });
  wrapper.querySelector('.site-access-search').addEventListener('submit',async e=>{
    e.preventDefault();await renderSearch();
    const first=content.querySelector('.site-access-result');
    if(first)location.href=first.href;
  });
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!panel.hidden){setOpen(false);returnFocus?.focus?.()}});
  document.addEventListener('pointerdown',e=>{if(!panel.hidden&&!wrapper.contains(e.target))setOpen(false)});
  void renderDefault();
})();