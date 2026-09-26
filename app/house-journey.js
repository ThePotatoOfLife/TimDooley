// Shared reader infrastructure for House-connected surfaces.
(function(){
  if(typeof document==='undefined')return;
  const current=document.currentScript;
  const baseUrl=current?.src||document.baseURI;
  if(!document.querySelector('link[data-house-journey-style]')){
    try{
      const link=document.createElement('link');
      link.rel='stylesheet';
      link.href=new URL('house-journey.css?v=20260926b',baseUrl).href;
      link.dataset.houseJourneyStyle='';
      document.head.appendChild(link);
    }catch(_){}
  }
  if([...document.scripts].some(s=>/\/app\/site-tts\.js(?:\?|$)/.test(s.src||'')))return;
  try{
    const script=document.createElement('script');
    script.src=new URL('site-tts.js',baseUrl).href;
    script.defer=true;
    document.head.appendChild(script);
  }catch(_){}
})();

(()=> {
  const KEY='potato-house-journey-v1';
  const marker='/TimDooley/';
  const pathName=location.pathname;
  const markerIndex=pathName.indexOf(marker);
  const base=markerIndex>=0?pathName.slice(0,markerIndex+marker.length):'/';

  const esc=(v)=>String(v??'').replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
  const viaLabel=(v)=>({
    'dwelling-door':'dwelling',
    'local-door':'local door',
    'wormhole-door':'wormhole',
    'elevator':'elevator',
    'portal':'portal',
    'read':'read',
    'return':'return',
    'object-focus':'object',
    'start':'start'
  })[v]||v||'step';

  const jsonCache=new Map();
  function getJson(path){
    if(!jsonCache.has(path)){
      jsonCache.set(path,fetch(base+path).then(response=>{
        if(!response.ok)throw new Error(path+' '+response.status);
        return response.json();
      }));
    }
    return jsonCache.get(path);
  }

  function loadTrail(){
    try{
      const x=JSON.parse(localStorage.getItem(KEY)||'[]');
      return Array.isArray(x)?x:[];
    }catch(e){return []}
  }

  function elevatorUrl(st={}){
    const q=new URLSearchParams();
    if(st.room)q.set('room',st.room);
    if(st.inner)q.set('inner',st.inner);
    if(st.object)q.set('object',st.object);
    if(st.level&&st.level!=='world')q.set('level',st.level);
    return base+'elevator/'+(q.toString()?'?'+q:'');
  }

  function installRibbon(){
    const trail=loadTrail();
    if(!trail.length)return;

    const ribbon=document.createElement('aside');
    ribbon.className='house-journey-ribbon';
    ribbon.setAttribute('aria-label','Your journey through the House');
    const shown=trail.slice(-2);
    const history=trail.slice().reverse();
    ribbon.innerHTML='<div class="house-journey-ribbon-main"><span class="house-journey-ribbon-title"><b>Your path</b><small>recent places</small></span><div class="house-journey-ribbon-track">'+shown.map(st=>
      '<a href="'+elevatorUrl(st)+'" title="'+esc(st.reason||'Return to this spatial center')+'"><span>'+esc(st.label||'House')+'</span><small>'+esc(viaLabel(st.via))+'</small></a>'
    ).join('')+'</div></div><div class="house-journey-ribbon-actions"><button type="button" data-journey-history aria-expanded="false">History</button><a href="'+base+'elevator/">Elevator</a></div><div class="house-journey-popover" data-journey-popover hidden><p><strong>Your path</strong> remembers places you entered through House/Elevator navigation so you can retrace them. It does not change the page or create a separate reading mode.</p><div class="house-journey-history">'+history.map(st=>
      '<a href="'+elevatorUrl(st)+'"><span>'+esc(st.label||'House')+'</span><small>'+esc(viaLabel(st.via))+'</small></a>'
    ).join('')+'</div></div>';
    document.body.appendChild(ribbon);

    // Keep the journey ribbon clear of the universal fixed access layer.
    // Measure the actual wrapper so mobile wrapping and local institution shortcuts
    // are handled without a brittle hard-coded offset.
    const access=document.querySelector('.site-access');
    const syncFixedClearance=()=>{
      if(!access){ribbon.style.removeProperty('bottom');return}
      const rect=access.getBoundingClientRect();
      const viewportBottomGap=Math.max(0,window.innerHeight-rect.bottom);
      ribbon.style.bottom=Math.ceil(viewportBottomGap+rect.height+6)+'px';
    };
    syncFixedClearance();
    if(access&&typeof ResizeObserver!=='undefined'){
      const observer=new ResizeObserver(syncFixedClearance);
      observer.observe(access);
    }
    window.addEventListener('resize',syncFixedClearance,{passive:true});

    const historyButton=ribbon.querySelector('[data-journey-history]'),popover=ribbon.querySelector('[data-journey-popover]');
    historyButton?.addEventListener('click',()=>{const open=popover.hidden;popover.hidden=!open;historyButton.setAttribute('aria-expanded',String(open));});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&popover&&!popover.hidden){popover.hidden=true;historyButton?.setAttribute('aria-expanded','false')}});
    document.addEventListener('pointerdown',e=>{if(popover&&!popover.hidden&&!ribbon.contains(e.target)){popover.hidden=true;historyButton?.setAttribute('aria-expanded','false')}});
  }

  async function installRoomFloorProjection(){
    const match=location.pathname.match(/\/rooms\/([^/]+)\/(?:index\.html)?$/);
    if(!match)return;
    const roomId=decodeURIComponent(match[1]);
    try{
      const projection=await getJson('data/house/elevator-spatial-projection.json');
      const dwelling=(projection.dwellings||[]).find(row=>row&&row.id===roomId);
      if(!dwelling)return;


      const levels=['heaven','plane','below'];
      const levelLabels={heaven:'Heaven',plane:'Plane',below:'Below'};
      const projections=new Set(dwelling.projections||[]);
      const notes=dwelling.projection_notes||{};
      const cards=levels.map(level=>{
        const primary=dwelling.primary_level===level;
        const projected=projections.has(level);
        const state=primary?'is-primary':projected?'is-projected':'is-absent';
        const stateLabel=primary?'Primary floor':projected?'Projects here':'No governed projection';
        const note=projected
          ?(notes[level]||'This Room has a governed projection on this floor.')
          :'This Room is not currently projected onto this floor, so the elevator leaves it unlit here.';
        return '<article class="room-floor-card '+state+'" data-floor="'+level+'">'
          +'<strong>'+levelLabels[level]+'</strong>'
          +'<small>'+stateLabel+'</small>'
          +'<p>'+esc(note)+'</p>'
          +'</article>';
      }).join('');

      const section=document.createElement('section');
      section.className='room-floor-projection';
      section.dataset.roomId=roomId;
      section.innerHTML='<p class="eyebrow">Three-floor projection</p>'
        +'<h2>How this Room moves through the House</h2>'
        +'<p>The Room remains one governed owner while the elevator changes the vertical lens. Its primary floor is the default orientation; other listed floors are deliberate projections, not duplicate Rooms.</p>'
        +'<div class="room-floor-grid">'+cards+'</div>';

      const main=document.querySelector('main');
      if(!main||main.querySelector('.room-floor-projection'))return;
      const localCenter=main.querySelector('.local-center');
      const actions=main.querySelector('.room-actions');
      if(localCenter) localCenter.insertAdjacentElement('afterend',section);
      else if(actions) main.insertBefore(section,actions);
      else {
        const header=main.querySelector('.page-header');
        if(header) header.insertAdjacentElement('afterend',section);
        else main.prepend(section);
      }
    }catch(e){}
  }


  async function installInhabitants(){
    const match=location.pathname.match(/\/rooms\/inside\/([^/]+)\//);
    if(!match)return;
    const roomId=decodeURIComponent(match[1]);
    try{
      const [inhData,subData]=await Promise.all([
        getJson('data/house/room-inhabitants.json'),
        getJson('data/house/subrooms.json')
      ]);
      const room=(subData.subrooms||[]).find(x=>x.id===roomId);
      const rows=(inhData.inhabitants||[]).filter(x=>(x.room_ids||[]).includes(roomId));
      if(!rows.length||!room)return;


      const main=document.querySelector('main');
      if(!main)return;
      const section=document.createElement('section');
      section.className='room-inhabitants-panel';
      section.innerHTML='<p class="eyebrow">Inhabitants / cases</p><h2>What lives in this Room</h2><p class="boundary">These are objects viewed from this Room. Centering one keeps this Room around it; it does not promote the object into architecture.</p><div class="room-inhabitant-grid">'+rows.map(x=>{
        const q=new URLSearchParams({room:room.parent_room_id,inner:roomId,object:x.id});
        return '<a class="room-inhabitant-card" href="'+base+'elevator/?'+q.toString()+'"><strong>'+esc(x.label)+'</strong><small>'+esc(x.kind||'object')+'</small><span>Place on the center table →</span></a>';
      }).join('')+'</div>';
      main.appendChild(section);
    }catch(e){}
  }


  async function installRoomKnowledge(){
    const match=location.pathname.match(/\/rooms\/inside\/([^/]+)\//);
    if(!match)return;
    const roomId=decodeURIComponent(match[1]);
    try{
      const [subData,holdData,ifData,dossierData,pulseData]=await Promise.all([
        getJson('data/house/subrooms.json'),
        getJson('data/house/holdings.json'),
        getJson('data/house/interfaces.json'),
        getJson('data/house/room-dossiers.json'),
        getJson('data/house/population-pulse.json')
      ]);
      const room=(subData.subrooms||[]).find(x=>x.id===roomId);
      const holding=(holdData.holdings||[]).find(x=>x.room_id===roomId);
      const dossier=(dossierData.dossiers||[]).find(x=>x.room_id===roomId);
      const pulse=(pulseData.rooms||pulseData.records||pulseData.population||pulseData.pulses||[]).find?.(x=>x.room_id===roomId);
      if(!room||!holding||!dossier)return;


      const titleFor=(id)=>String(id||'').replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
      const featured=(dossier.knowledge_holdings?.featured||holding.featured_holdings||[]).slice(0,12);
      const belongs=(dossier.belongs_here||[]).filter(x=>!/^Material rooted in /i.test(x));
      const passages=(dossier.passages||[]).slice(0,8);
      const next=(dossier.next_work||[]).filter(x=>!/^Deepen the Room through its center contribution:/i.test(x)).slice(0,5);
      const receives=dossier.center_pairing?.receives_from||dossier.local_center?.entry_routes||[];
      const hands=dossier.center_pairing?.hands_to||dossier.local_center?.exit_routes||[];
      const publicSurfaces=dossier.public_surfaces||[];
      const primaryCount=dossier.knowledge_holdings?.primary_file_count??holding.primary_file_count??featured.length;
      const interfaceCount=(ifData.interfaces||[]).filter(x=>x.from===roomId||x.to===roomId).length;
      const dataFiles=dossier.data_holdings?.owned_file_count||0;
      const functionText=dossier.local_center?.function||dossier.center_pairing?.contribution||dossier.entrance||room.purpose||'';
      const main=document.querySelector('main');if(!main)return;
      if(main.querySelector('.room-richness'))return;
      const section=document.createElement('section');section.className='room-richness';
      const holdingHtml=featured.length?'<div class="room-holding-list">'+featured.map(x=>{
        const path=x.path||'';
        const href=base+'explore/#record='+encodeURIComponent(path||x.id||'');
        return '<a class="room-holding" href="'+href+'"><strong>'+esc(titleFor(x.id||path.split('/').pop()?.replace(/\.[^.]+$/,'')))+'</strong><small>'+esc(x.kind||'canonical holding')+(path?'<br>'+esc(path):'')+'</small></a>';
      }).join('')+'</div>':'<p>No featured holdings have been promoted yet; that absence is itself a population task for this Room.</p>';
      const passageHtml=passages.length?passages.map(x=>{
        const other=x.other_room_id||x.to||x.from||'another Room';
        return '<div class="room-passage"><b>'+esc(titleFor(x.type||'interface'))+'</b> <em>↔ '+esc(titleFor(other))+'</em><small>'+esc(x.changes||'')+(x.guard?' Boundary: '+esc(x.guard):'')+'</small></div>';
      }).join(''):'<p>No governed cross-Room passage has been promoted yet.</p>';
      const surfaces=publicSurfaces.map(x=>{
        const route=x.route||'';
        if(!route)return '';
        const href=route.startsWith('/')?base+route.replace(/^\//,''):route;
        return '<a href="'+esc(href)+'">'+esc(x.title||x.id||'Public surface')+' →</a>';
      }).join('');
      const signal=pulse?.signals||{};
      const pulseText=pulse?[
        signal.primary_holding_count!=null?signal.primary_holding_count+' holdings':null,
        signal.guarded_interface_count!=null?signal.guarded_interface_count+' guarded interfaces':null,
        signal.related_structural_instance_count?signal.related_structural_instance_count+' related structural instances':null,
        signal.data_file_count?signal.data_file_count+' data files':null
      ].filter(Boolean).join(' · '):'';

      section.innerHTML=
        '<p class="eyebrow">The Room behind the doorway</p><h2>'+esc(dossier.title||room.title||titleFor(roomId))+' is not an empty category</h2>'
        +'<p class="room-richness-intro">'+esc(functionText)+'</p>'
        +'<p>'+esc(dossier.entrance||room.purpose||'')+'</p>'
        +'<div class="room-richness-meta">'+esc(String(primaryCount))+' primary knowledge holdings · '+esc(String(interfaceCount))+' governed interfaces'+(dataFiles?' · '+esc(String(dataFiles))+' owned data files':'')+(pulseText?' · live pulse: '+esc(pulseText):'')+'</div>'
        +(belongs.length?'<div class="room-richness-rule"><h3>What actually belongs here</h3><div class="room-richness-run">'+belongs.map(x=>'<span>'+esc(x)+'</span>').join('')+'</div></div>':'')
        +'<div class="room-richness-rule"><h3>Open the actual material</h3><p>These are current canonical or featured holdings owned by this Room. The list comes from the House registry rather than being hand-written into the page.</p>'+holdingHtml+'</div>'
        +(passages.length?'<div class="room-richness-rule"><h3>What changes when this Room meets another</h3><p>Doors in the House are transformations with guards, not decorative links. These are the current governed passages touching this Room.</p>'+passageHtml+'</div>':'')
        +((receives.length||hands.length)?'<div class="room-richness-rule"><h3>Where the work comes from, and where it goes</h3>'+(receives.length?'<p><strong>Receives:</strong> '+receives.map(titleFor).map(esc).join(' · ')+'</p>':'')+(hands.length?'<p><strong>Hands mature work to:</strong> '+hands.map(titleFor).map(esc).join(' · ')+'</p>':'')+'</div>':'')
        +(next.length?'<div class="room-richness-rule"><h3>What is still unfinished</h3><ul class="room-next">'+next.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul></div>':'')
        +(surfaces?'<div class="room-richness-rule"><h3>Keep reading</h3><p>This Room is one owner inside a larger reader-facing system. These routes project the same material for different questions.</p><div class="room-surface-run">'+surfaces+'</div></div>':'');

      const doorSection=[...main.querySelectorAll('section')].find(x=>/Adjacent Rooms/i.test(x.textContent||''));
      if(doorSection)main.insertBefore(section,doorSection);else main.appendChild(section);
    }catch(e){}
  }

  installRibbon();
  installRoomFloorProjection();
  installInhabitants();
  installRoomKnowledge();
})();