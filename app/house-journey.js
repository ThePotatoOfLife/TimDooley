(()=> {
  const KEY='potato-house-journey-v1';
  let trail=[];
  try{ trail=JSON.parse(localStorage.getItem(KEY)||'[]'); }catch(e){ trail=[]; }
  if(!Array.isArray(trail)||!trail.length) return;

  const base=(()=>{
    const p=location.pathname;
    const marker='/TimDooley/';
    const i=p.indexOf(marker);
    return i>=0?p.slice(0,i+marker.length):'/';
  
  // Level 3: inhabitants / cases inside nested Rooms.
  (async()=>{
    const m=location.pathname.match(/\/rooms\/inside\/([^/]+)\//);
    if(!m)return;
    const roomId=decodeURIComponent(m[1]);
    try{
      const res=await fetch(base+'data/house/room-inhabitants.json');
      if(!res.ok)return;
      const data=await res.json();
      const rows=(data.inhabitants||[]).filter(x=>(x.room_ids||[]).includes(roomId));
      if(!rows.length)return;
      const main=document.querySelector('main');if(!main)return;
      const section=document.createElement('section');
      section.className='room-inhabitants-panel';
      section.innerHTML='<p class="eyebrow">Inhabitants / cases</p><h2>What lives in this Room</h2><p class="boundary">These are objects viewed from this Room, not new Rooms and not new knowledge owners.</p><div class="room-inhabitant-grid">'+rows.map(x=>'<a class="room-inhabitant-card" href="'+base+x.route.replace(/^\//,'')+'"><strong>'+String(x.label).replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]))+'</strong><small>'+String(x.kind||'object').replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]))+'</small></a>').join('')+'</div>';
      main.appendChild(section);
      if(!document.getElementById('room-inhabitant-style')){
        const st=document.createElement('style');st.id='room-inhabitant-style';st.textContent='.room-inhabitants-panel{margin:34px 0 90px}.room-inhabitant-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:9px;margin-top:14px}.room-inhabitant-card{border:1px solid var(--site-line,#303830);padding:12px;text-decoration:none;color:inherit}.room-inhabitant-card strong{display:block;color:var(--site-gold,#d5ba74);font:400 17px var(--site-font-serif,serif)}.room-inhabitant-card small{display:block;color:var(--site-muted,#9ba59a);margin-top:4px;text-transform:uppercase;letter-spacing:.05em;font-size:7px}';document.head.appendChild(st);
      }
    }catch(e){}
  })();

})();
  const elevatorUrl=(st)=>{
    const q=new URLSearchParams();
    if(st.room)q.set('room',st.room);
    if(st.inner)q.set('inner',st.inner);
    if(st.level&&st.level!=='world')q.set('level',st.level);
    return base+'elevator/'+(q.toString()?'?'+q:'');
  };

  const style=document.createElement('style');
  style.textContent=`
  .house-journey-ribbon{position:fixed;left:14px;right:14px;bottom:12px;z-index:9998;border:1px solid var(--site-line,#303830);background:rgba(5,8,6,.94);backdrop-filter:blur(10px);border-radius:14px;padding:8px 10px;display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:9px;align-items:center;box-shadow:0 10px 35px rgba(0,0,0,.28)}
  .house-journey-ribbon>b{font:400 13px var(--site-font-serif,serif);color:var(--site-gold,#d5ba74);white-space:nowrap}
  .house-journey-ribbon-track{display:flex;gap:5px;overflow-x:auto;scrollbar-width:thin}
  .house-journey-ribbon-track a{white-space:nowrap;border:1px solid var(--site-line,#303830);border-radius:999px;padding:4px 7px;color:var(--site-muted,#9ba59a);text-decoration:none;font-size:8px}.house-journey-ribbon-track a small{display:block;font-size:6px;opacity:.65;text-transform:uppercase;letter-spacing:.04em;margin-top:1px}
  .house-journey-ribbon-track a:last-child{color:var(--site-green,#9eb58d);border-color:#61745b}
  .house-journey-ribbon>a{border:1px solid var(--site-line,#303830);border-radius:999px;padding:5px 8px;color:var(--site-muted,#9ba59a);text-decoration:none;font-size:8px;white-space:nowrap}
  @media(max-width:620px){.house-journey-ribbon{grid-template-columns:1fr auto}.house-journey-ribbon>b{display:none}}
  `;
  document.head.appendChild(style);

  const ribbon=document.createElement('aside');
  ribbon.className='house-journey-ribbon';
  ribbon.setAttribute('aria-label','Your journey through the House');
  const shown=trail.slice(-12);
  ribbon.innerHTML='<b>Your thread</b><div class="house-journey-ribbon-track">'+shown.map((st,i)=>'<a href="'+elevatorUrl(st)+'" title="Return to this spatial center">'+String(st.label||'House').replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]))+'</a>').join('')+'</div><a href="'+base+'elevator/">Return to Elevator</a>';
  document.body.appendChild(ribbon);
  const track=ribbon.querySelector('.house-journey-ribbon-track'); if(track)track.scrollLeft=track.scrollWidth;
})();