(function(){
  const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const roots=[...document.querySelectorAll('[data-three-center-map]')];
  if(!roots.length)return;
  roots.forEach(async root=>{
    const src=root.getAttribute('data-three-center-src')||'../data/house/three-center-role-atlas.json';
    try{
      const res=await fetch(src); if(!res.ok) throw new Error('three-center atlas unavailable');
      const d=await res.json(), centers=d.centers||[];
      const order=['C_F','O','C_S'];
      const rows=order.map(id=>centers.find(x=>x.id===id)).filter(Boolean);
      root.innerHTML=
        '<div class="three-center-runtime-plot" aria-label="Three typed centers">'+rows.map((c,i)=>{
          const names=(c.project_names||[]).slice(0,5);
          const comps=(c.comparative_archetypes||[]).slice(0,4).map(x=>x.label);
          return '<article class="three-center-runtime-node" data-center="'+esc(c.id)+'"><div class="three-center-runtime-code">'+esc(c.id)+'</div><h3>'+esc(c.label)+'</h3><b>'+esc(c.primary_anchor?.label||'')+'</b><p>'+esc(c.primary_anchor?.relation||'')+'</p><div class="three-center-runtime-tags">'+names.map(x=>'<span>'+esc(x)+'</span>').join('')+'</div><small><strong>Comparators:</strong> '+esc(comps.join(' · '))+'</small><small><strong>Boundary:</strong> '+esc(c.primary_anchor?.boundary||'')+'</small></article>';
        }).join('<div class="three-center-runtime-arrow" aria-hidden="true">↓</div>')+'</div>'+
        '<p class="three-center-runtime-guard">'+esc(d.governing_rule||'')+' '+esc(d.rights_and_subjecthood?.non_target_rule||'')+'</p>';
    }catch(e){
      root.innerHTML='<p class="boundary">The three-center atlas could not be loaded.</p>';
    }
  });
})();
