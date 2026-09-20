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
      const [subRes,holdRes,ifRes]=await Promise.all([
        fetch(base+'data/house/subrooms.json'),
        fetch(base+'data/house/holdings.json'),
        fetch(base+'data/house/interfaces.json')
      ]);
      if(!subRes.ok||!holdRes.ok||!ifRes.ok)return;
      const subData=await subRes.json(), holdData=await holdRes.json(), ifData=await ifRes.json();
      const room=(subData.subrooms||[]).find(x=>x.id===roomId);
      const holding=(holdData.holdings||[]).find(x=>x.room_id===roomId);
      if(!room||!holding)return;

      if(!document.getElementById('room-live-knowledge-style')){
        const st=document.createElement('style');st.id='room-live-knowledge-style';st.textContent=`
          .room-live-knowledge{margin:34px 0}.room-live-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:9px;margin-top:14px}
          .room-live-card{border:1px solid var(--site-line,#303830);padding:12px;color:inherit;text-decoration:none;display:block}
          .room-live-card:hover{border-color:#61745b}.room-live-card strong{display:block;color:var(--site-gold,#d5ba74);font:400 17px var(--site-font-serif,serif)}
          .room-live-card small{display:block;color:var(--site-muted,#9ba59a);font-size:8px;line-height:1.4;margin-top:5px}
          .room-live-routes{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}.room-live-routes a{border:1px solid var(--site-line,#303830);border-radius:999px;padding:5px 8px;text-decoration:none;color:var(--site-muted,#9ba59a);font-size:8px}
          .room-live-routes a:hover{color:var(--site-green,#9eb58d);border-color:#61745b}.room-live-meta{color:var(--site-muted,#9ba59a);font-size:9px;margin-top:7px}
        `;document.head.appendChild(st);
      }

      const main=document.querySelector('main');if(!main)return;
      const section=document.createElement('section');section.className='room-live-knowledge';
      const featured=(holding.featured_holdings||[]).slice(0,18);
      const cards=featured.map(x=>{
        const href=base+'explore/#record='+encodeURIComponent(x.path||x.id||'');
        return '<a class="room-live-card" href="'+href+'"><strong>'+esc((x.id||x.path||'record').replace(/-/g,' '))+'</strong><small>'+esc(x.kind||'canonical holding')+'<br>'+esc(x.path||'')+'</small></a>';
      }).join('');
      const neighbors=(room.adjacent_subroom_ids||[]).map(id=>{
        const target=(subData.subrooms||[]).find(x=>x.id===id);
        return target?'<a href="'+base+'rooms/inside/'+encodeURIComponent(id)+'/">'+esc(target.title||id)+'</a>':'';
      }).join('');
      const interfaceIds=new Set((ifData.interfaces||[]).filter(x=>x.from===roomId||x.to===roomId).map(x=>x.id));
      section.innerHTML='<p class="eyebrow">Live Room registry</p><h2>Knowledge held here now</h2>'
        +'<p class="boundary">This panel is generated from the current House registries, so it stays current even when the static Room shell predates newer atlases or corridors.</p>'
        +'<div class="room-live-meta">'+esc(String(holding.primary_file_count||featured.length))+' primary holdings · '+esc(String(interfaceIds.size))+' governed interfaces</div>'
        +'<div class="room-live-grid">'+cards+'</div>'
        +(neighbors?'<p class="eyebrow" style="margin-top:20px">Current governed routes</p><div class="room-live-routes">'+neighbors+'</div>':'');
      main.appendChild(section);
    }catch(e){}
  }

  installRibbon();
  installInhabitants();
  installRoomKnowledge();
})();