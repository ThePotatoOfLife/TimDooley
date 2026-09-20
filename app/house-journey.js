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