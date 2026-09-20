(function(){
  'use strict';
  if(typeof document==='undefined'||document.querySelector('.site-access'))return;
  const script=document.currentScript;
  let appBase,siteBase;
  try{appBase=new URL('./',script?.src||document.baseURI);siteBase=new URL('../',appBase)}catch(_){return}
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const href=route=>new URL(String(route||'/').replace(/^\//,''),siteBase).href;
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
  const staticEntries=[
    {label:'Home',route:'/',kind:'start',note:'Project entrance',aliases:'start homepage'},
    {label:'Current World',route:'/news/',kind:'world',note:'Live news',aliases:'news headlines current today'},
    {label:'World Map',route:'/world-map/',kind:'world',note:'Interactive atlas',aliases:'map countries atlas'},
    {label:'Tim Dooley',route:'/tim-dooley/',kind:'project',note:'Main portrait',aliases:'tim father potato'},
    {label:'Potato of Life',route:'/potato-of-life/',kind:'project',note:'Semantic center',aliases:'potato center canon'},
    {label:'House',route:'/house/',kind:'project',note:'How the project fits together',aliases:'architecture structure'},
    {label:'Rooms',route:'/rooms/',kind:'project',note:'Knowledge owners',aliases:'dwellings rooms'},
    {label:'People & Cases',route:'/rooms/objects/',kind:'find',note:'Search House inhabitants',aliases:'people cases objects entities find search'},
    {label:'A–Z',route:'/index-a-z/',kind:'find',note:'Known-term lookup',aliases:'index terms glossary find'},
    {label:'Timeline',route:'/timeline/',kind:'find',note:'Events and chronology',aliases:'history dates chronology'},
    {label:'Sources',route:'/context/source-authority/',kind:'find',note:'Evidence and provenance',aliases:'evidence source provenance'},
    {label:'Explore',route:'/explore/',kind:'find',note:'Relationship explorer',aliases:'archive relationships'},
    {label:'Science',route:'/science/',kind:'project',note:'Models, evidence, falsifiers',aliases:'physics biology research'},
    {label:'Religion',route:'/religion/',kind:'project',note:'Theology and comparisons',aliases:'bible trinity tradition'},
    {label:'Philosophy',route:'/philosophy/',kind:'project',note:'Spiral reader and concepts',aliases:'spiral ideas'},
    {label:'World',route:'/world/',kind:'world',note:'Countries and real systems',aliases:'world countries systems'},
    {label:'Economy & Finance',route:'/economy/',kind:'world',note:'Debt, banking, ownership',aliases:'economy finance debt fed ecb banks'},
    {label:'Politics',route:'/politics/',kind:'world',note:'Politics and geopolitics',aliases:'politics geopolitics'},
    {label:'CIA / Intelligence',route:'/shadow-farm/#intelligence-desk',kind:'direct',note:'Intelligence Desk',aliases:'cia central intelligence agency intelligence security'},
    {label:'FBI — Figures, Bonds & Incidents',route:'/rooms/potatoverse-canon/beings/fbi/',kind:'direct',note:'Character dossier bureau',aliases:'fbi figures bonds incidents characters'},
    {label:'100,000 Hours',route:'/tim-dooley/100000-hours/',kind:'direct',note:'Public-presence model',aliases:'100000 hours streaming livestream'},
    {label:'Below / Farm / Sektur',route:'/shadow-farm/',kind:'direct',note:'Lower-system deep reader',aliases:'below farm sektur swamp culture'}
  ];
  const wrapper=document.createElement('div');
  wrapper.className='site-access';
  wrapper.setAttribute('data-no-tts','');
  wrapper.setAttribute('aria-label','Site quick access');
  const pageTitle=(document.querySelector('h1')?.textContent||document.title||'Current page').replace(/\s+/g,' ').trim();
  wrapper.innerHTML='<nav class="site-access-dock" aria-label="Quick access">'+
    '<a data-site-access-route="/" href="'+esc(href('/'))+'">Home</a>'+
    '<a class="site-access-news" data-site-access-route="/news/" href="'+esc(href('/news/'))+'">News</a>'+
    '<a data-site-access-route="/world-map/" href="'+esc(href('/world-map/'))+'">Map</a>'+
    '<button type="button" data-site-access-find aria-expanded="false">Find</button>'+
    '<button type="button" data-site-access-menu aria-expanded="false">Menu</button>'+
    '</nav>'+
    '<section class="site-access-panel" data-site-access-panel hidden aria-label="Site menu">'+
      '<div class="site-access-head"><div><small>Quick access · you are in</small><strong>'+esc(pageTitle)+'</strong></div><button class="site-access-close" type="button" aria-label="Close quick access">×</button></div>'+
      '<form class="site-access-search" role="search"><input type="search" autocomplete="off" placeholder="Find CIA, Tim, debt, Bible, a Room…" aria-label="Find in the project"><button type="submit">Find</button></form>'+
      '<div data-site-access-content></div>'+
    '</section>';
  document.body.appendChild(wrapper);
  const panel=wrapper.querySelector('[data-site-access-panel]');
  const input=wrapper.querySelector('.site-access-search input');
  const content=wrapper.querySelector('[data-site-access-content]');
  const menuBtn=wrapper.querySelector('[data-site-access-menu]');
  const findBtn=wrapper.querySelector('[data-site-access-find]');
  const closeBtn=wrapper.querySelector('.site-access-close');
  wrapper.querySelectorAll('[data-site-access-route]').forEach(a=>{
    const r=a.getAttribute('data-site-access-route');
    if(r==='/'?current==='/':current.startsWith(r))a.setAttribute('aria-current','page');
  });
  let loaded=false,index=[...staticEntries];
  const key=e=>(e.label+' '+(e.aliases||'')+' '+(e.note||'')+' '+(e.kind||'')).toLowerCase();
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
      const [sr,ir]=await Promise.all([
        fetch(href('/data/house/public-surfaces.json')),
        fetch(href('/data/house/room-inhabitants.json'))
      ]);
      if(sr.ok){
        const d=await sr.json();
        for(const s of d.surfaces||[])if(s?.status==='active'&&s?.route)index.push({label:s.title||s.id,route:s.route,kind:'page',note:s.surface_type||'public surface',aliases:s.id});
      }
      if(ir.ok){
        const d=await ir.json();
        for(const x of d.inhabitants||[])if(x?.route)index.push({label:x.label||x.id,route:x.route,kind:x.kind||'object',note:x.summary||'House object',aliases:(x.id||'')+' '+(x.room_ids||[]).join(' ')});
      }
      index=unique(index);
    }catch(_){}
  };
  const group=(title,entries)=>'<div class="site-access-group"><span>'+esc(title)+'</span><div class="site-access-links">'+entries.map(e=>'<a href="'+esc(href(e.route))+'"><b>'+esc(e.label)+'</b><small>'+esc(e.note||'')+'</small></a>').join('')+'</div></div>';
  const renderDefault=()=>{
    content.className='site-access-groups';
    content.innerHTML=
      group('Go now',staticEntries.filter(e=>['Current World','World Map','Tim Dooley','House','Rooms'].includes(e.label)))+
      group('Find',staticEntries.filter(e=>['People & Cases','A–Z','Timeline','Sources','Explore'].includes(e.label)))+
      group('Direct doors',staticEntries.filter(e=>['CIA / Intelligence','Economy & Finance','Science','Religion','FBI — Figures, Bonds & Incidents','100,000 Hours'].includes(e.label)));
  };
  const renderSearch=async()=>{
    const q=input.value.trim().toLowerCase();
    if(!q){renderDefault();return}
    await loadIndex();
    const terms=q.split(/\s+/).filter(Boolean);
    const rows=index.map(e=>{
      const hay=key(e);let score=0;
      for(const t of terms){if(!hay.includes(t))return null;score+=e.label.toLowerCase().startsWith(t)?5:hay.includes(' '+t)?3:1}
      return {e,score};
    }).filter(Boolean).sort((a,b)=>b.score-a.score||a.e.label.localeCompare(b.e.label)).slice(0,12).map(x=>x.e);
    content.className='site-access-results';
    content.innerHTML=rows.length?rows.map(e=>'<a class="site-access-result" href="'+esc(href(e.route))+'"><span><b>'+esc(e.label)+'</b><small>'+esc(e.note||'')+'</small></span><em>'+esc(e.kind||'result')+'</em></a>').join(''):'<div class="site-access-empty">No quick result. Try a broader word or open A–Z / Explore.</div>';
  };
  const setOpen=(open,focusSearch=false)=>{
    panel.hidden=!open;
    menuBtn.setAttribute('aria-expanded',String(open));
    findBtn.setAttribute('aria-expanded',String(open));
    if(open){if(!input.value)renderDefault();if(focusSearch)setTimeout(()=>input.focus(),0)}
  };
  menuBtn.addEventListener('click',()=>setOpen(panel.hidden,false));
  findBtn.addEventListener('click',()=>setOpen(true,true));
  closeBtn.addEventListener('click',()=>setOpen(false));
  input.addEventListener('input',renderSearch);
  wrapper.querySelector('.site-access-search').addEventListener('submit',async e=>{
    e.preventDefault();await renderSearch();
    const first=content.querySelector('.site-access-result');
    if(first)location.href=first.href;
  });
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!panel.hidden){setOpen(false);menuBtn.focus()}});
  document.addEventListener('pointerdown',e=>{if(!panel.hidden&&!wrapper.contains(e.target))setOpen(false)});
  renderDefault();
})();