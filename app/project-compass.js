(function(){
  'use strict';
  if(typeof document==='undefined'||document.querySelector('.project-compass'))return;
  const current=document.currentScript;
  let appBase;
  try{appBase=new URL('./',current?.src||document.baseURI)}catch(_){return}
  const siteBase=new URL('../',appBase);
  const QUIET=['/world-map/','/elevator/','/rooms/objects/','/index-a-z/','/tools/tts/'];
  const path=location.pathname;
  if(QUIET.some(x=>path.includes(x))||/\/3d\.html$/.test(path))return;
  const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const route=()=>{
    try{
      let p=new URL(location.href).pathname;
      const basePath=new URL(siteBase).pathname.replace(/\/$/,'');
      if(basePath&&p.startsWith(basePath))p=p.slice(basePath.length);
      p='/' + p.replace(/^\/+|\/+$/g,'');
      if(p==='/index.html')return '/';
      p=p.replace(/\/index\.html$/,'/').replace(/\/+/g,'/');
      return p==='/'?'/':(p.endsWith('/')||/\.html$/.test(p)?p:p+'/');
    }catch(_){return '/'}
  };
  const here=route();
  fetch(new URL('../data/house/public-surfaces.json',appBase))
    .then(r=>r.ok?r.json():Promise.reject())
    .then(data=>{
      const rows=(data.surfaces||[]).filter(x=>x&&x.status==='active');
      const byId=Object.fromEntries(rows.map(x=>[x.id,x]));
      let currentSurface=rows.find(x=>x.canonical_route===here||x.route===here);
      if(!currentSurface){
        const candidates=rows.filter(x=>x.route&&x.route!=='/'&&here.startsWith(x.route)).sort((a,b)=>b.route.length-a.route.length);
        currentSurface=candidates[0]||byId.home;
      }
      const parent=currentSurface?.primary_parent?byId[currentSurface.primary_parent]:null;
      const gateways=(data.primary_gateway_ids||[]).map(id=>byId[id]).filter(Boolean);
      const utilities=(data.secondary_global_ids||[]).map(id=>byId[id]).filter(x=>x&&x.id!=='house').slice(0,7);
      const href=s=>new URL((s.route||'/').replace(/^\//,''),siteBase).href;
      const currentLabel=currentSurface?.title||document.querySelector('h1')?.textContent?.trim()||document.title;
      const parentText=parent?('Inside '+parent.title):(currentSurface?.surface_type==='home'?'Project entrance':'Project-wide reader');
      const link=(s)=>'<a href="'+esc(href(s))+'"'+(s===currentSurface?' aria-current="page"':'')+'>'+esc(s.title)+'</a>';
      const nav=document.querySelector('main > nav.page-nav,main > nav.nav,main > nav.topnav,main > .page-nav,main > .nav');
      const main=document.querySelector('main');
      if(!main)return;
      const box=document.createElement('aside');
      box.className='project-compass';
      box.setAttribute('data-no-tts','');
      box.setAttribute('aria-label','Project compass');
      box.innerHTML='<details><summary><span><small>Project compass</small><b>'+esc(currentLabel)+'</b></span><small>'+esc(parentText)+'</small></summary><div class="project-compass-body"><div class="project-compass-current"><span>You are here</span><strong>'+esc(currentLabel)+'</strong><p>'+esc(parentText)+'. Use this layer for orientation; the page itself remains the main reader.</p>'+(parent?'<a href="'+esc(href(parent))+'">Up to '+esc(parent.title)+' →</a>':'<a href="'+esc(new URL('',siteBase).href)+'">Project home →</a>')+'</div><div class="project-compass-groups"><div class="project-compass-group"><span>Main gateways</span><nav class="project-compass-links" aria-label="Main project gateways">'+gateways.map(link).join('')+'</nav></div><div class="project-compass-group"><span>Find anything</span><nav class="project-compass-links" aria-label="Project discovery tools">'+utilities.map(link).join('')+'</nav></div></div></div></details>';
      if(nav?.insertAdjacentElement)nav.insertAdjacentElement('afterend',box);
      else main.prepend(box);
    })
    .catch(()=>{});
})();