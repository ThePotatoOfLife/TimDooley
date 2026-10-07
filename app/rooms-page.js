const sharedHouseJson=(path=>{
  const cache=window.__potatoJsonPromiseCache||(window.__potatoJsonPromiseCache=new Map());
  const href=new URL(path,location.href).href;
  if(!cache.has(href)){
    const request=fetch(href,{cache:'default'}).then(response=>{
      if(!response.ok)throw new Error(path+' '+response.status);
      return response.json();
    }).catch(error=>{cache.delete(href);throw error});
    cache.set(href,request);
  }
  return cache.get(href);
});

(async function renderFeaturedDwellingShelves(){
  const tabs=document.getElementById('featuredDwellingTabs'),shelf=document.getElementById('featuredDwellingShelf');
  if(!tabs||!shelf)return;
  const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const labels={
    'potatoverse-canon':'Canon','archive-sources':'Sources','time-history':'Time',
    'traditions-texts':'Traditions','science-formal-models':'Science','life-body':'Life & Body',
    'world-systems':'World','culture-information':'Culture','works':'Works','research-lab':'Forge'
  };
  try{
    const data=await sharedHouseJson('../data/house/dwelling-featured-objects.json'),rows=data.shelves||[];
    let active=rows[0]?.dwelling_id||'';
    function route(href){return href?'../'+String(href).replace(/^\.?\//,''):'../'}
    function draw(){
      const row=rows.find(x=>x.dwelling_id===active)||rows[0];
      tabs.innerHTML=rows.map(x=>'<button type="button" class="featured-tab" data-dwelling="'+esc(x.dwelling_id)+'" aria-pressed="'+String(x.dwelling_id===row.dwelling_id)+'">'+esc(labels[x.dwelling_id]||x.dwelling_id)+'</button>').join('');
      shelf.innerHTML='<h3>'+esc(row.title||labels[row.dwelling_id]||row.dwelling_id)+'</h3><p>'+esc(row.intro||'')+'</p><div class="featured-object-grid">'+
        (row.objects||[]).map(o=>'<a class="featured-object" href="'+esc(route(o.href))+'"><em>'+esc(o.kind||'object')+'</em><strong>'+esc(o.title)+'</strong><span>'+esc(o.summary||'')+'</span></a>').join('')+
        '</div>';
    }
    tabs.addEventListener('click',e=>{const b=e.target.closest('[data-dwelling]');if(!b)return;active=b.dataset.dwelling;draw()});
    draw();
  }catch(e){
    tabs.innerHTML='';
    shelf.innerHTML='<p class="boundary">The curated object shelves could not be loaded. The authored Dwelling material below remains available.</p>';
  }
})();

(()=>{
  const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const href=route=>route?'../'+route:'../';
  async function renderPlanes(){
    const root=document.getElementById('planeStack'); if(!root)return;
    try{
      const [topology,rooms]=await Promise.all([sharedHouseJson('../data/house/topology.json'),sharedHouseJson('../data/house/rooms.json')]);
      const roomTitles=Object.fromEntries((rooms.rooms||[]).map(r=>[r.id,r.title||r.id]));
      const planes=topology.symbolic_planes?.planes||[];
      root.innerHTML=planes.map(p=>{
        const nav=(p.navigation||[]).map(n=>'<a href="'+esc(href(n.route))+'">'+esc(n.label)+'</a>').join('');
        const primary=(p.primary_room_ids||[]).map(id=>roomTitles[id]||id).join(' · ');
        const crossing=(p.crossing_room_ids||[]).map(id=>roomTitles[id]||id).join(' · ');
        return '<article class="plane-disc plane-disc--'+esc(p.id)+'" data-plane="'+esc(p.id)+'"><span class="plane-position">'+esc(p.position)+' plane</span><h3>'+esc(p.label)+'</h3><span class="plane-tree">'+esc(p.tree_position)+'</span><p class="plane-desc">'+esc(p.description)+'</p><nav class="plane-nav" aria-label="'+esc(p.label)+' navigation">'+nav+'</nav><p class="plane-rooms"><b>Primary Rooms</b> · '+esc(primary)+(crossing?'<br><b>Crosses</b> · '+esc(crossing):'')+'</p></article>';
      }).join('')||'<span class="plane-loading">No plane projection is registered.</span>';
    }catch(e){root.innerHTML='<span class="plane-loading">The plane navigation data could not be loaded.</span>'}
  }
  renderPlanes();

  async function renderCompass(){
    const root=document.getElementById('orientationCompass'),detail=document.getElementById('orientationDetail'),tabs=document.getElementById('orientationTabs');
    if(!root||!detail||!tabs)return;
    try{
      const [topo,orientationPopulation]=await Promise.all([sharedHouseJson('../data/house/topology.json'),sharedHouseJson('../data/house/orientation-population.json')]),model=topo.symbolic_compass;if(!model?.directions)throw new Error('compass missing');
      let plane='world-plane',selected='n';
      const planeLabel=p=>p==='world-plane'?'Plane':p.replace('-plane','');
      const planeQuery=p=>p==='world-plane'?'plane':p.replace('-plane','');
      const routeOf=r=>r?'../'+r:'../';
      root.innerHTML=(model.directions||[]).map(d=>'<span class="compass-spoke" style="transform:rotate('+esc(d.bearing-90)+'deg)"></span>').join('')+
        (model.directions||[]).map(d=>{const rad=(Number(d.bearing)||0)*Math.PI/180,x=50+Math.sin(rad)*42,y=50-Math.cos(rad)*42;return '<button class="compass-door" type="button" style="left:'+x.toFixed(2)+'%;top:'+y.toFixed(2)+'%" data-direction="'+esc(d.id)+'" aria-pressed="false"><small>'+esc(d.label)+'</small><b>'+esc(d.title.replace(' & ',' / '))+'</b></button>';}).join('')+
        '<a class="compass-center" href="../axis/#routing"><span><b>Axis</b><small>Center · Forge around it</small></span></a>'+
        '<a class="compass-fruit" href="'+esc(routeOf(model.outer_ring.route))+'">'+esc(model.outer_ring.label)+' ↗</a>';
      function show(id){
        const d=model.directions.find(x=>x.id===id)||model.directions[0],focus=d.focus_by_plane?.[plane]||{};
        selected=d.id;
        root.querySelectorAll('[data-direction]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.direction===selected)));
        tabs.querySelectorAll('[data-plane]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.plane===plane)));
        const topics=(focus.topics||[]).map(x=>'<span>'+esc(x)+'</span>').join('');
        const examples=(focus.examples||[]).length?'<div class="orientation-examples"><b>Examples:</b> '+esc(focus.examples.join(' · '))+'</div>':'';
        const boundary=focus.boundary?'<div class="orientation-examples">'+esc(focus.boundary)+'</div>':'';
        const rooms=(orientationPopulation.room_population||[]).filter(x=>x.compass_direction===d.id&&(x.plane_ids||[]).includes(plane));
        const visibleRooms=rooms.slice(0,6);
        const roomHtml=visibleRooms.map(x=>'<div class="population-item"><b>'+esc(x.title)+'</b><small>'+esc(x.primary_file_count)+' owned files · '+esc((x.tree_zone_ids||[]).join(' / '))+'</small></div>').join('');
        const landmarks=(orientationPopulation.landmarks||[]).filter(x=>x.direction===d.id&&(x.plane_ids||[]).includes(plane)&&x.visibility!=='archive-only').slice(0,7);
        const landmarkHtml=landmarks.map(x=>'<a class="population-landmark" href="'+esc(routeOf(x.route))+'" title="'+esc(x.note)+'">'+esc(x.label)+'</a>').join('');
        const populationHtml=(roomHtml||landmarkHtml)?'<div class="orientation-population"><h4>In this direction</h4>'+(roomHtml?'<div class="population-grid">'+roomHtml+'</div>':'')+(landmarkHtml?'<div class="population-landmarks">'+landmarkHtml+'</div>':'')+(rooms.length>visibleRooms.length?'<div class="population-more">+'+esc(rooms.length-visibleRooms.length)+' more Room'+(rooms.length-visibleRooms.length===1?'':'s')+' in this slice</div>':'')+'</div>':'';
        detail.innerHTML='<span class="bearing">'+esc(d.label)+' · '+esc(planeLabel(plane))+'</span><h3>'+esc(d.title)+'</h3><p><b>'+esc(focus.label||'')+'</b><br>'+esc(d.question)+'</p><div class="orientation-topics">'+topics+'</div>'+examples+boundary+populationHtml+'<div class="orientation-actions"><a href="'+esc(routeOf(d.route))+'">Enter this Door →</a><a href="../house/#nested-rooms">See its nested Rooms</a></div>';
        const u=new URL(location.href);u.searchParams.set('plane',planeQuery(plane));u.searchParams.set('dir',selected);history.replaceState(null,'',u);
      }
      root.addEventListener('click',e=>{const b=e.target.closest('[data-direction]');if(b)show(b.dataset.direction)});
      tabs.addEventListener('click',e=>{const b=e.target.closest('[data-plane]');if(b){plane=b.dataset.plane;show(selected)}});
      const u=new URL(location.href),qp=u.searchParams.get('plane'),qd=u.searchParams.get('dir');
      const candidate=qp==='plane'?'world-plane':qp+'-plane';if(['heaven-plane','world-plane','below-plane'].includes(candidate))plane=candidate;
      if(model.directions.some(x=>x.id===qd))selected=qd;
      show(selected);
    }catch(e){root.innerHTML='<span class="plane-loading">The orientation compass could not be loaded.</span>'}
  }
  renderCompass();
})();

(async function bootPlacementBrowser(){
 const controls=document.getElementById('placementControls'),grid=document.getElementById('placementGrid'),count=document.getElementById('placementCount');if(!controls||!grid)return;
 const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
 try{
  const [layer,branch]=await Promise.all([sharedHouseJson('../data/house/layer-terrain-regime-atlas.json'),sharedHouseJson('../data/house/religious-symbolic-branch-atlas.json')]);
  const structural=(layer.nodes||[]).map(n=>({id:n.id,label:n.label,category:n.category,planes:n.plane_ids||[],note:n.definition||'',source:'structure'}));
  const inhabited=(branch.nodes||[]).map(n=>({id:n.id,label:n.label,category:n.layer_category||'inhabitant',planes:n.planes||[],note:n.note||'',source:'inhabitant'}));
  const rows=[...structural,...inhabited];
  const cats=['all',...Array.from(new Set(rows.map(x=>x.category))).sort()];
  let active='all',plane='all';
  controls.innerHTML='<button class="placement-control" data-kind="plane" data-value="all" aria-pressed="true">All planes</button>'+
    ['heaven-plane','world-plane','below-plane'].map(p=>'<button class="placement-control" data-kind="plane" data-value="'+p+'" aria-pressed="false">'+(p==='world-plane'?'Plane':p.replace('-plane',''))+'</button>').join('')+
    '<span style="width:8px"></span>'+
    cats.map(c=>'<button class="placement-control" data-kind="cat" data-value="'+esc(c)+'" aria-pressed="'+(c==='all'?'true':'false')+'">'+esc(c)+'</button>').join('');
  function render(){
   const seen=new Set();
   const out=rows.filter(x=>(active==='all'||x.category===active)&&(plane==='all'||x.planes.includes(plane))).filter(x=>{const k=x.source+':'+x.id;if(seen.has(k))return false;seen.add(k);return true;}).slice(0,48);
   grid.innerHTML=out.map(x=>'<article class="placement-node"><strong>'+esc(x.label)+'</strong><small>'+esc(x.category)+' · '+esc((x.planes||[]).map(p=>p==='world-plane'?'Plane':p.replace('-plane','')).join(' / ')||'crosscutting')+'</small><p>'+esc(x.note)+'</p></article>').join('')||'<p class="boundary">No nodes in this slice.</p>';
   count.textContent=out.length+' visible node'+(out.length===1?'':'s')+' in this slice';
   controls.querySelectorAll('[data-kind="cat"]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.value===active)));
   controls.querySelectorAll('[data-kind="plane"]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.value===plane)));
  }
  controls.addEventListener('click',e=>{const b=e.target.closest('.placement-control');if(!b)return;if(b.dataset.kind==='cat')active=b.dataset.value;else plane=b.dataset.value;render()});
  render();
 }catch(e){grid.innerHTML='<p class="boundary">Placement atlas could not be loaded.</p>'}
})();

(async function renderRoomInhabitants(){
 const grid=document.getElementById('inhabitantGrid'),kinds=document.getElementById('inhabitantKinds'),search=document.getElementById('inhabitantSearch'),count=document.getElementById('inhabitantCount');
 if(!grid||!kinds||!search)return;
 const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
 try{
  const data=await sharedHouseJson('../data/house/room-inhabitants.json'),rows=data.inhabitants||[];
  const kindCounts={};rows.forEach(x=>kindCounts[x.kind]=(kindCounts[x.kind]||0)+1);
  const topKinds=Object.entries(kindCounts).sort((a,b)=>b[1]-a[1]).slice(0,10).map(x=>x[0]);
  let active='all',q='';
  kinds.innerHTML='<button class="inhabitant-kind" type="button" data-kind="all" aria-pressed="true">All</button>'+topKinds.map(k=>'<button class="inhabitant-kind" type="button" data-kind="'+esc(k)+'" aria-pressed="false">'+esc(k.replaceAll('-',' '))+'</button>').join('');
  const route=r=>{if(!r)return '#';const x=String(r);return x.startsWith('/')?'..'+x:'../'+x.replace(/^\.\//,'')};
  function draw(){
    const needle=q.trim().toLowerCase();
    const out=rows.filter(x=>(active==='all'||x.kind===active)&&(!needle||[x.label,x.kind,x.summary,(x.room_ids||[]).join(' ')].join(' ').toLowerCase().includes(needle))).slice(0,32);
    grid.innerHTML=out.map(x=>'<a class="inhabitant-card" href="'+esc(route(x.route))+'"><em>'+esc((x.kind||'inhabitant').replaceAll('-',' '))+'</em><strong>'+esc(x.label||x.id)+'</strong><span>'+esc(x.summary||'')+'</span><small>'+esc((x.room_ids||[]).map(r=>r.replaceAll('-',' ')).join(' · '))+'</small></a>').join('')||'<p class="boundary">No inhabitants match this view.</p>';
    if(count)count.textContent=out.length+' shown · '+rows.length+' registered inhabitants total';
    kinds.querySelectorAll('[data-kind]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.kind===active)));
  }
  kinds.addEventListener('click',e=>{const b=e.target.closest('[data-kind]');if(!b)return;active=b.dataset.kind;draw()});
  search.addEventListener('input',()=>{q=search.value;draw()});
  draw();
 }catch(e){grid.innerHTML='<p class="boundary">The inhabitant registry could not be loaded.</p>'}
})();
