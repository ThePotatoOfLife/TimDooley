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
    {id:'rooms',label:'Rooms',route:'/rooms/',kind:'project',note:'Browse the subjects and Rooms',aliases:['rooms','dwellings']},
    {id:'people-cases',label:'People & Cases',route:'/rooms/objects/',kind:'find',note:'Search House inhabitants',aliases:['people','cases','objects','entities','find','search']},
    {id:'questions',label:'Questions',route:'/questions/',kind:'find',note:'Find by question',aliases:['questions','ask','answers','find']},
    {id:'index-a-z',label:'A–Z',route:'/index-a-z/',kind:'find',note:'Find by known term',aliases:['index','terms','glossary','find']},
    {id:'paths',label:'Paths',route:'/paths/',kind:'find',note:'Find a guided route',aliases:['paths','journey','route','guide']},
    {id:'timeline',label:'Timeline',route:'/timeline/',kind:'find',note:'Events and chronology',aliases:['history','dates','chronology']},
    {id:'sources',label:'Sources',route:'/context/source-authority/',kind:'find',note:'Evidence and provenance',aliases:['evidence','source','provenance']},
    {id:'explore',label:'Explore',route:'/explore/',kind:'find',note:'Questions, terms, paths and deep archive',aliases:['archive','relationships','find','browse']},
    {id:'cia-character-archive',label:'Potatoverse CIA · Character Archive',route:'/rooms/potatoverse-canon/beings/cia/',kind:'direct',scope:'POTATOVERSE',note:'Characters, Incidents & Associations · authored project archive',aliases:['potatoverse cia','character cia','characters incidents associations','character archive','dossiers']},
    {id:'mud-bank',label:'World Spiritual Bank / Mud Bank',route:'/rooms/potatoverse-canon/beings/cia/bank/',kind:'direct',scope:'POTATOVERSE',note:'Fictional North Root Ledger · Character Archive sub-accounts',aliases:['mud bank','dooley welfare','karma bank','balance sheet']},
    {id:'intelligence-cia',label:'U.S. CIA · Central Intelligence Agency',route:'/shadow-farm/#intelligence-desk',kind:'direct',scope:'REAL WORLD',note:'U.S. foreign-intelligence institution · Intelligence Desk',aliases:['us cia','u.s. cia','central intelligence agency','real cia','intelligence desk']},
    {id:'fbi-legacy',label:'FBI · legacy Character Archive name',route:'/rooms/potatoverse-canon/beings/cia/',kind:'direct',scope:'POTATOVERSE',note:'Former Figures, Bonds & Incidents name · opens current Character Archive',aliases:['fbi','figures bonds incidents','fbi character archive','legacy fbi']},
    {id:'intelligence-fbi',label:'U.S. FBI · Federal Bureau of Investigation',route:'/shadow-farm/#intelligence-desk',kind:'direct',scope:'REAL WORLD',note:'U.S. federal law-enforcement and domestic-intelligence institution · Intelligence Desk',aliases:['us fbi','u.s. fbi','federal bureau of investigation','real fbi','federal bureau','domestic intelligence']},
    {id:'economy',label:'Economy & Finance',route:'/economy/',kind:'world',note:'Debt, banking, ownership',aliases:['economy','finance','debt','bonds','fed','federal reserve','ecb','eurosystem']},
    {id:'tts',label:'Read Aloud / TTS',route:'/tools/tts/',kind:'direct',note:'Text-to-speech tools and reader controls',aliases:['tts','text to speech','read aloud','listen']},
    {id:'claims',label:'Claims & Statements',route:'/tim-dooley/claims/',kind:'direct',note:'Claims and attributed statements',aliases:['claims','statements','assertions']},
    {id:'public-witness',label:'Public Witness',route:'/tim-dooley/public-witness/',kind:'direct',note:'Public record and witness material',aliases:['public witness','public record','witness']},
    {id:'below',label:'Below / Lower Field',route:'/below/#lower-field-orientation',kind:'direct',note:'Mission, participant-observer experience, lower-field roles, evidence, exit and repair',aliases:['below','farm','sektur','swamp','culture','lower field','lower field orientation','swamp mission','subculture mission','participant observer','karmic ledger','babel','repair','exit']},
    {id:'science',label:'Science',route:'/science/',kind:'project',note:'Models, evidence, falsifiers',aliases:['science','physics','biology','research']},
    {id:'religion',label:'Religion',route:'/religion/',kind:'project',note:'Theology and comparisons',aliases:['religion','bible','trinity','theology']},
    {id:'bible-comparison',label:'Tim, the Son & the Bible',route:'/traditions/bible/',kind:'project',note:'Life-first Bible, Jesus/Son, prophecy and counter-text comparison',aliases:['bible comparison','jesus','jesus son','son','thomas','twin','crucifixion','resurrection','gospel parallels','tim son bible']},
    {id:'hours',label:'100,000 Hours',route:'/tim-dooley/100000-hours/',kind:'direct',note:'Public-presence model',aliases:['100000 hours','100,000 hours','streaming','livestream']}
  ];
  let curatedEntries=[...fallbackEntries];
  let accessGroups={
    landmarks:['cia-character-archive','mud-bank'],
    go_now:['news','world-map','tim','house','rooms'],
    find:['people-cases','index-a-z','timeline','sources','explore'],
    direct_doors:['cia-character-archive','mud-bank','intelligence-cia','economy','tts','claims','public-witness','below','science','religion','hours']
  };
  let disambiguations={
    cia:{query:['cia'],prompt:'Which CIA?',options:['cia-character-archive','intelligence-cia'],rule:'Same acronym, different namespace. Choose before entering.'},
    fbi:{query:['fbi'],prompt:'Which FBI?',options:['fbi-legacy','intelligence-fbi'],rule:'Legacy Potatoverse name or real U.S. institution. Choose before entering.'}
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
    '<button type="button" data-site-access-listen aria-expanded="false" hidden>Listen</button>'+
    '<button type="button" data-site-access-find aria-expanded="false">Find</button>'+
    '<button type="button" data-site-access-menu aria-expanded="false">Places</button>'+
    '</nav>'+
    '<section class="site-access-tts-console" data-site-access-tts hidden aria-label="Read aloud controls">'+
      '<div class="site-access-tts-head"><strong>Read aloud</strong><button type="button" class="site-access-tts-close" aria-label="Hide reader controls">×</button></div>'+
      '<div data-site-access-tts-mount></div>'+
    '</section>'+
    '<section class="site-access-panel" data-site-access-panel hidden aria-label="Site menu">'+
      '<div class="site-access-head"><div><small>Quick access · you are in</small><strong>'+esc(pageTitle)+'</strong></div><button class="site-access-close" type="button" aria-label="Close quick access">×</button></div>'+
      '<form class="site-access-search" role="search"><input type="search" autocomplete="off" placeholder="Find Character Archive, CIA/FBI, Tim, debt, a Room…" aria-label="Find in the project"><button type="submit">Find</button></form>'+
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
  const listenBtn=wrapper.querySelector('[data-site-access-listen]');
  const ttsConsole=wrapper.querySelector('[data-site-access-tts]');
  const ttsMount=wrapper.querySelector('[data-site-access-tts-mount]');
  const ttsCloseBtn=wrapper.querySelector('.site-access-tts-close');
  const closeBtn=wrapper.querySelector('.site-access-close');
  let ttsDrawer=null,ttsObserver=null;
  let returnFocus=menuBtn;
  wrapper.querySelectorAll('[data-site-access-route]').forEach(a=>{
    const r=a.getAttribute('data-site-access-route');
    if(r==='/'?current==='/':current.startsWith(r))a.setAttribute('aria-current','page');
  });
  let loaded=false,loadPromise=null,index=[...curatedEntries];
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
    if(loadPromise)return loadPromise;
    loadPromise=(async()=>{
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
      if(contract?.disambiguation)disambiguations=contract.disambiguation;
      for(const row of surfaces?.surfaces||[])if(row?.status==='active'&&row?.route)index.push({
        label:row.title||row.id,
        route:row.route,
        kind:'page',
        note:row.description||row.summary||'Open this reader',
        context:row.primary_parent?'Under '+(roomNames[row.primary_parent]||row.primary_parent):'Public reader',
        aliases:row.id
      });
      for(const row of inhabitants?.inhabitants||[])if(row?.route){
        const rooms=(row.room_ids||[]).map(id=>roomNames[id]||id).filter(Boolean);
        index.push({
          label:row.label||row.id,
          route:row.route,
          kind:row.kind||'object',
          note:row.summary||'Open this object',
          context:rooms.length?'Found in '+rooms.join(' · '):'House item',
          aliases:(row.id||'')+' '+(row.room_ids||[]).join(' ')
        });
      }
      index=unique(index);
      const received=Boolean(contract||surfaces||inhabitants||roomsData);
      loaded=received;
    })().catch(()=>{loaded=false}).finally(()=>{loadPromise=null});
    return loadPromise;
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
    const disambiguation=Object.values(disambiguations||{}).find(row=>(row?.query||[]).map(x=>String(x).toLowerCase()).includes(q));
    if(disambiguation){
      const rows=(disambiguation.options||[]).map(id=>curatedEntries.find(e=>e.id===id)).filter(Boolean);
      if(rows.length){
        content.className='site-access-results site-access-disambiguation';
        content.innerHTML='<div class="site-access-choice-head"><b>'+esc(disambiguation.prompt||'Choose a destination')+'</b><small>'+esc(disambiguation.rule||'Choose the intended namespace before entering.')+'</small></div>'+rows.map(e=>'<a class="site-access-result" href="'+esc(href(e.route))+'"><span><b>'+esc(e.label)+'</b><small>'+esc(e.note||'')+'</small></span><em>'+esc(e.scope||(e.kind==='world'?'WORLD':e.kind==='project'?'PROJECT':e.kind==='find'?'FIND':'OPEN'))+'</em></a>').join('');
        return;
      }
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
  const syncTTSState=()=>{
    if(!ttsDrawer)return;
    const speech=ttsDrawer.engine?.state||ttsDrawer.element?.dataset?.speech||'idle';
    const active=speech==='speaking'||speech==='paused';
    listenBtn.hidden=false;
    listenBtn.textContent='Listen';
    listenBtn.dataset.readerState=speech;
    listenBtn.setAttribute('aria-pressed',String(active));
    listenBtn.setAttribute('aria-label',speech==='speaking'?'Reader is speaking. Open read-aloud controls':speech==='paused'?'Reader is paused. Open read-aloud controls':'Open read-aloud controls');
    listenBtn.title=speech==='speaking'?'Reader is speaking · open controls':speech==='paused'?'Reader is paused · open controls':'Open read-aloud controls';
    if(ttsConsole)ttsConsole.dataset.readerState=speech;
  };
  const attachTTS=detail=>{
    const drawer=detail?.drawer||window.__potatoActiveTTSDrawer;
    const host=detail?.element||drawer?.element;
    if(!drawer||!host||!ttsMount)return false;
    ttsDrawer=drawer;
    if(host.parentElement!==ttsMount)ttsMount.appendChild(host);
    host.classList.add('ptts-docked');
    ttsObserver?.disconnect?.();
    if(typeof MutationObserver!=='undefined'){
      ttsObserver=new MutationObserver(syncTTSState);
      ttsObserver.observe(host,{attributes:true,attributeFilter:['data-speech','data-state','data-follow']});
    }
    syncTTSState();
    return true;
  };
  const setTTSOpen=open=>{
    if(!ttsDrawer&&window.__potatoActiveTTSDrawer)attachTTS({drawer:window.__potatoActiveTTSDrawer,element:window.__potatoActiveTTSDrawer.element});
    if(!ttsDrawer)return false;
    if(open&& !panel.hidden)setOpen(false);
    ttsConsole.hidden=!open;
    listenBtn.setAttribute('aria-expanded',String(open));
    if(open)ttsDrawer.open?.();
    else ttsDrawer.hideUI?.();
    wrapper.dataset.readerOpen=open?'true':'false';
    syncTTSState();
    publishClearance();
    return true;
  };
  document.addEventListener('potato:tts-mounted',event=>attachTTS(event.detail||{}));
  if(window.__potatoActiveTTSDrawer)attachTTS({drawer:window.__potatoActiveTTSDrawer,element:window.__potatoActiveTTSDrawer.element});

  const setOpen=(open,focusSearch=false,trigger=null)=>{
    if(open&&trigger)returnFocus=trigger;
    panel.hidden=!open;
    menuBtn.setAttribute('aria-expanded',String(open));
    findBtn.setAttribute('aria-expanded',String(open));
    if(open){if(!input.value)void renderDefault();if(focusSearch)setTimeout(()=>input.focus(),0)}
  };
  menuBtn.addEventListener('click',()=>{if(!ttsConsole.hidden)setTTSOpen(false);setOpen(panel.hidden,false,menuBtn)});
  findBtn.addEventListener('click',()=>{if(!ttsConsole.hidden)setTTSOpen(false);setOpen(true,true,findBtn)});
  listenBtn.addEventListener('click',()=>{setOpen(false);setTTSOpen(ttsConsole.hidden)});
  ttsCloseBtn.addEventListener('click',()=>{setTTSOpen(false);listenBtn.focus()});
  closeBtn.addEventListener('click',()=>{setOpen(false);returnFocus?.focus?.()});
  input.addEventListener('input',renderSearch);
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&!ttsConsole.hidden){setTTSOpen(false);listenBtn.focus()}
  });
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
  if(!document.body.classList.contains('home-body'))void renderDefault();
})();