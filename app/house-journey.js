// Shared reader infrastructure for House-connected surfaces.
(function(){
  if(typeof document==='undefined')return;
  if([...document.scripts].some(s=>/\/app\/site-tts\.js(?:\?|$)/.test(s.src||'')))return;
  const current=document.currentScript;
  let src='';
  try{src=new URL('site-tts.js',current?.src||document.baseURI).href}catch(_){return}
  const script=document.createElement('script');script.src=src;script.defer=true;document.head.appendChild(script);
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
    const style=document.createElement('style');
    style.textContent=`
      .house-journey-ribbon{position:fixed;left:14px;right:14px;bottom:12px;z-index:9998;border:1px solid var(--site-line,#303830);background:rgba(5,8,6,.94);backdrop-filter:blur(10px);border-radius:14px;padding:8px 10px;display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:9px;align-items:center;box-shadow:0 10px 35px rgba(0,0,0,.28)}
      .house-journey-ribbon>b{font:400 13px var(--site-font-serif,serif);color:var(--site-gold,#d5ba74);white-space:nowrap}
      .house-journey-ribbon-track{display:flex;gap:5px;overflow-x:auto;scrollbar-width:thin}
      .house-journey-ribbon-track a{white-space:nowrap;border:1px solid var(--site-line,#303830);border-radius:999px;padding:4px 7px;color:var(--site-muted,#9ba59a);text-decoration:none;font-size:8px}
      .house-journey-ribbon-track a small{display:block;font-size:6px;opacity:.65;text-transform:uppercase;letter-spacing:.04em;margin-top:1px}
      .house-journey-ribbon-track a:last-child{color:var(--site-green,#9eb58d);border-color:#61745b}
      .house-journey-ribbon>a{border:1px solid var(--site-line,#303830);border-radius:999px;padding:5px 8px;color:var(--site-muted,#9ba59a);text-decoration:none;font-size:8px;white-space:nowrap}
      @media(max-width:620px){.house-journey-ribbon{grid-template-columns:1fr auto}.house-journey-ribbon>b{display:none}}
    `;
    document.head.appendChild(style);

    const ribbon=document.createElement('aside');
    ribbon.className='house-journey-ribbon';
    ribbon.setAttribute('aria-label','Your journey through the House');
    const shown=trail.slice(-12);
    ribbon.innerHTML='<b>Your thread</b><div class="house-journey-ribbon-track">'+shown.map(st=>
      '<a href="'+elevatorUrl(st)+'" title="'+esc(st.reason||'Return to this spatial center')+'"><span>'+esc(st.label||'House')+'</span><small>'+esc(viaLabel(st.via))+'</small></a>'
    ).join('')+'</div><a href="'+base+'elevator/">Return to Elevator</a>';
    document.body.appendChild(ribbon);
    const track=ribbon.querySelector('.house-journey-ribbon-track');
    if(track)track.scrollLeft=track.scrollWidth;
  }

  async function installInhabitants(){
    const match=location.pathname.match(/\/rooms\/inside\/([^/]+)\//);
    if(!match)return;
    const roomId=decodeURIComponent(match[1]);
    try{
      const [inhRes,subRes]=await Promise.all([
        fetch(base+'data/house/room-inhabitants.json'),
        fetch(base+'data/house/subrooms.json')
      ]);
      if(!inhRes.ok||!subRes.ok)return;
      const inhData=await inhRes.json();
      const subData=await subRes.json();
      const room=(subData.subrooms||[]).find(x=>x.id===roomId);
      const rows=(inhData.inhabitants||[]).filter(x=>(x.room_ids||[]).includes(roomId));
      if(!rows.length||!room)return;

      if(!document.getElementById('room-inhabitant-style')){
        const st=document.createElement('style');
        st.id='room-inhabitant-style';
        st.textContent=`
          .room-inhabitants-panel{margin:34px 0 90px}
          .room-inhabitant-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:9px;margin-top:14px}
          .room-inhabitant-card{border:1px solid var(--site-line,#303830);padding:12px;text-decoration:none;color:inherit;display:block}
          .room-inhabitant-card:hover{border-color:#61745b}
          .room-inhabitant-card strong{display:block;color:var(--site-gold,#d5ba74);font:400 17px var(--site-font-serif,serif)}
          .room-inhabitant-card small{display:block;color:var(--site-muted,#9ba59a);margin-top:4px;text-transform:uppercase;letter-spacing:.05em;font-size:7px}
          .room-inhabitant-card span{display:block;color:var(--site-muted,#9ba59a);font-size:9px;line-height:1.4;margin-top:6px}
        `;
        document.head.appendChild(st);
      }

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
      const [subRes,holdRes,ifRes,dossierRes,pulseRes]=await Promise.all([
        fetch(base+'data/house/subrooms.json'),
        fetch(base+'data/house/holdings.json'),
        fetch(base+'data/house/interfaces.json'),
        fetch(base+'data/house/room-dossiers.json'),
        fetch(base+'data/house/population-pulse.json')
      ]);
      if(!subRes.ok||!holdRes.ok||!ifRes.ok||!dossierRes.ok||!pulseRes.ok)return;
      const subData=await subRes.json(),holdData=await holdRes.json(),ifData=await ifRes.json(),dossierData=await dossierRes.json(),pulseData=await pulseRes.json();
      const room=(subData.subrooms||[]).find(x=>x.id===roomId);
      const holding=(holdData.holdings||[]).find(x=>x.room_id===roomId);
      const dossier=(dossierData.dossiers||[]).find(x=>x.room_id===roomId);
      const pulse=(pulseData.rooms||pulseData.records||pulseData.population||pulseData.pulses||[]).find?.(x=>x.room_id===roomId);
      if(!room||!holding||!dossier)return;

      if(!document.getElementById('room-richness-style')){
        const st=document.createElement('style');st.id='room-richness-style';st.textContent=`
          .room-richness{margin:52px 0 60px;max-width:930px}
          .room-richness-intro{font:400 clamp(20px,2.4vw,29px)/1.5 var(--site-font-serif,serif);color:var(--site-ink,#e7e1d2);max-width:840px;margin:8px 0 24px}
          .room-richness p{color:var(--site-muted,#aab3a8);max-width:850px;line-height:1.65}
          .room-richness-rule{border-top:1px solid var(--site-line,#303830);padding:20px 0}
          .room-richness-rule h3{font:400 24px/1.2 var(--site-font-serif,serif);color:var(--site-gold,#d5ba74);margin:0 0 9px}
          .room-richness-run{display:flex;flex-wrap:wrap;gap:6px 9px;margin:9px 0 3px}
          .room-richness-run span{color:var(--site-muted,#9ba59a);font-size:9px}
          .room-richness-run span:not(:last-child)::after{content:' ·';color:var(--site-line,#596359);margin-left:9px}
          .room-holding-list{margin:7px 0 0;border-top:1px solid rgba(255,255,255,.055)}
          .room-holding{display:grid;grid-template-columns:minmax(180px,.75fr) minmax(0,1.25fr);gap:22px;padding:13px 0;border-bottom:1px solid rgba(255,255,255,.055);text-decoration:none;color:inherit}
          .room-holding:hover strong{color:var(--site-green,#9eb58d)}
          .room-holding strong{font:400 17px var(--site-font-serif,serif);color:var(--site-gold,#d5ba74)}
          .room-holding small{color:var(--site-muted,#9ba59a);font-size:9px;line-height:1.45;overflow-wrap:anywhere}
          .room-passage{padding:13px 0;border-top:1px solid rgba(255,255,255,.055)}
          .room-passage b{color:var(--site-gold,#d5ba74);font-weight:500}.room-passage em{color:var(--site-green,#9eb58d);font-style:normal}
          .room-passage small{display:block;color:var(--site-muted,#9ba59a);margin-top:4px;line-height:1.45}
          .room-next{margin:8px 0 0;padding-left:20px;color:var(--site-muted,#9ba59a)}
          .room-next li{margin:8px 0;max-width:810px}
          .room-surface-run{display:flex;flex-wrap:wrap;gap:7px;margin-top:13px}.room-surface-run a{border-bottom:1px solid var(--site-line,#303830);padding:5px 0;text-decoration:none;color:var(--site-green,#9eb58d);font-size:9px;margin-right:12px}
          .room-richness-meta{font-size:9px;color:var(--site-muted,#9ba59a);margin-top:9px}
          @media(max-width:620px){.room-holding{grid-template-columns:1fr;gap:3px}}
        `;document.head.appendChild(st);
      }

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
  installInhabitants();
  installRoomKnowledge();
})();