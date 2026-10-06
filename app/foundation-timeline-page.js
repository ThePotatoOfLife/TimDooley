(async()=>{
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 async function loadJson(path,fallback,required=false){
   try{
     const response=await fetch(path,{cache:'no-cache'});
     if(!response.ok)throw new Error(path+' '+response.status);
     return {ok:true,value:await response.json()};
   }catch(error){
     if(required)throw error;
     return {ok:false,value:fallback,error};
   }
 }
 let core;
 try{
   core=await loadJson('../../data/house/foundation-timeline-wave-001.json',null,true);
 }catch(error){
   document.getElementById('foundationReadout').textContent='Foundation chronology is temporarily unavailable. The explanatory material and direct source routes on this page remain usable.';
   document.getElementById('foundationTimeline').innerHTML='<section class="year-group"><h2>Direct routes</h2><div class="event-grid"><article class="event"><strong>Religious foundations</strong><p><a href="../../religion/">Open Religion →</a></p></article><article class="event"><strong>Project timeline</strong><p><a href="../">Open Timeline →</a></p></article></div></section>';
   return;
 }
 const [genealogyLoad,placementLoad,roomLoad,lineageLoad,eventLoad]=await Promise.all([
   loadJson('../../data/house/foundation-door-seed-genealogy.json',{records:[]}),
   loadJson('../../data/house/foundation-placement-wave-003.json',{records:[]}),
   loadJson('../../data/house/foundation-room-atlas.json',{rooms:[]}),
   loadJson('../../data/religious-foundation-timeline.json',{events:[]}),
   loadJson('../../data/religious-foundation-events.json',{events:[]})
 ]);
 const data=core.value,genealogy=genealogyLoad.value,placement=placementLoad.value,foundationRooms=roomLoad.value,religiousLineage=lineageLoad.value,religiousEvents=eventLoad.value,events=data.events||[],seedRows=genealogy.records||[],placementBy=Object.fromEntries((placement.records||[]).map(x=>[x.foundation_id,x]));
 const degraded=[];
 if(!genealogyLoad.ok)degraded.push('seed genealogy');
 if(!placementLoad.ok)degraded.push('House placement');
 if(!roomLoad.ok)degraded.push('Foundation Rooms');
 if(!lineageLoad.ok)degraded.push('religious lineages');
 if(!eventLoad.ok)degraded.push('religious event enrichment');
 const filters=document.getElementById('foundationFilters'),root=document.getElementById('foundationTimeline'),readout=document.getElementById('foundationReadout');
 const domains=[...new Set(events.map(x=>x.domain).filter(Boolean))].sort();
 const types=[...new Set(events.map(x=>x.event_type).filter(Boolean))];
 let domain='all',type='all';
 filters.innerHTML='<button class="filter" data-domain="all" aria-pressed="true">All domains</button>'+domains.map(x=>'<button class="filter" data-domain="'+esc(x)+'" aria-pressed="false">'+esc(x)+'</button>').join('')+'<span style="flex-basis:100%"></span><button class="filter" data-type="all" aria-pressed="true">All clocks</button>'+types.map(x=>'<button class="filter" data-type="'+esc(x)+'" aria-pressed="false">'+esc(x.replaceAll('_',' '))+'</button>').join('');
 function render(){
   const rows=events.filter(x=>(domain==='all'||x.domain===domain)&&(type==='all'||x.event_type===type));
   const groups=new Map();
   for(const e of rows){const y=Number.isFinite(e.year_start)?e.year_start:null;const bucket=y==null?'Undated':y<0?Math.abs(y)+' BCE':String(y);if(!groups.has(bucket))groups.set(bucket,[]);groups.get(bucket).push(e)}
   root.innerHTML=[...groups.entries()].map(([y,list])=>'<section class="year-group"><h2>'+esc(y)+'</h2><div class="event-grid">'+list.map(e=>'<article class="event"><strong>'+esc(e.name)+'</strong><em>'+esc(e.event_type.replaceAll('_',' '))+' · '+esc(e.domain)+'</em><p>'+esc(e.date_or_range)+' — '+esc(e.label)+'</p><small>'+esc(e.precision)+' · '+esc(e.status)+'</small></article>').join('')+'</div></section>').join('');
   readout.textContent=rows.length+' foundation-state events visible · '+(domain==='all'?'all domains':domain)+' · '+(type==='all'?'all clocks':type.replaceAll('_',' '));
   filters.querySelectorAll('[data-domain]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.domain===domain)));
   filters.querySelectorAll('[data-type]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.type===type)));
 }
 filters.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.domain){domain=b.dataset.domain}else if(b.dataset.type){type=b.dataset.type}render()});



 const religiousEventFilters=document.getElementById('religiousEventFilters'),religiousEventGrid=document.getElementById('religiousEventGrid'),religiousEventReadout=document.getElementById('religiousEventReadout');
 const majorReligiousEvents=(religiousEvents.events||[]).filter(x=>x.merge_priority==='major');
 const religionFamilies=[...new Set(majorReligiousEvents.map(x=>x.family).filter(Boolean))].sort();
 let religiousEventFamily='all';
 religiousEventFilters.innerHTML='<button class="lineage-filter" data-religion-event-family="all" aria-pressed="true">All traditions</button>'+religionFamilies.map(x=>'<button class="lineage-filter" data-religion-event-family="'+esc(x)+'" aria-pressed="false">'+esc(x.replaceAll('-',' '))+'</button>').join('');
 function renderReligiousEvents(){
   const rows=majorReligiousEvents.filter(x=>religiousEventFamily==='all'||x.family===religiousEventFamily).sort((a,b)=>(a.date?.year_start??99999)-(b.date?.year_start??99999));
   religiousEventGrid.innerHTML=rows.map(x=>'<article class="religion-lineage-card"><h3>'+esc(x.name)+'</h3><em>'+esc((x.event_kind||'event').replaceAll('_',' '))+' · '+esc(x.family||'tradition')+'</em><p><b>'+esc(x.date?.display||'undated')+'</b></p><p>'+esc(x.place||'distributed/uncertain')+'</p><small>'+esc(x.note||'')+(x.source_url?' · <a href="'+esc(x.source_url)+'" target="_blank" rel="noopener">source ↗</a>':'')+'</small></article>').join('');
   religiousEventReadout.textContent=rows.length+' major religious historical clocks · '+(religiousEventFamily==='all'?'all traditions':religiousEventFamily);
   religiousEventFilters.querySelectorAll('[data-religion-event-family]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.religionEventFamily===religiousEventFamily)));
 }
 religiousEventFilters.addEventListener('click',e=>{const b=e.target.closest('[data-religion-event-family]');if(!b)return;religiousEventFamily=b.dataset.religionEventFamily;renderReligiousEvents()});
 renderReligiousEvents();

 const lineageFilters=document.getElementById('religiousLineageFilters'),lineageGrid=document.getElementById('religiousLineageGrid'),lineageReadout=document.getElementById('religiousLineageReadout');
 const lineageEvents=religiousLineage.events||[],notableReligiousEvents=(religiousEvents.events||[]).filter(x=>x.merge_priority==='major'),lineageFamilies=[...new Set(lineageEvents.map(x=>x.family_id).filter(Boolean))];
 let lineageFamily='all';
 lineageFilters.innerHTML='<button class="lineage-filter" data-lineage-family="all" aria-pressed="true">All religious lineages</button>'+lineageFamilies.map(x=>'<button class="lineage-filter" data-lineage-family="'+esc(x)+'" aria-pressed="false">'+esc(x.replaceAll('-lineage','').replaceAll('-',' '))+'</button>').join('');
 const formatHistoricalYear=y=>!Number.isFinite(y)?'undated':y<0?Math.abs(y)+' BCE':y+' CE';
 function renderReligiousLineages(){
   const rows=lineageEvents.filter(x=>lineageFamily==='all'||x.family_id===lineageFamily);
   lineageGrid.innerHTML=rows.map(x=>'<article class="religion-lineage-card"><h3>'+esc(x.name)+'</h3><em>'+esc(x.node_type)+' · '+esc(x.family_id.replaceAll('-lineage','').replaceAll('-',' '))+'</em><p><b>'+esc(x.date_or_range||formatHistoricalYear(x.year_start))+'</b></p><p>'+esc(x.place||'distributed/uncertain')+'</p><div class="lineage-path"><p><b>Relation:</b> '+esc((x.relation_to_parent||'root').replaceAll('_',' '))+(x.parent_ids?.length?' ← '+esc(x.parent_ids.join(', ')):'')+'</p></div><small>'+esc(x.precision||'')+' · '+esc(x.status||'')+(x.notes?' · '+esc(x.notes):'')+'</small></article>').join('');
   lineageReadout.textContent=rows.length+' dated religious lineage nodes · '+notableReligiousEvents.length+' major anchored events · '+(lineageFamily==='all'?'all families':lineageFamily.replaceAll('-lineage','').replaceAll('-',' '));
   lineageFilters.querySelectorAll('[data-lineage-family]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lineageFamily===lineageFamily)));
 }
 lineageFilters.addEventListener('click',e=>{const b=e.target.closest('[data-lineage-family]');if(!b)return;lineageFamily=b.dataset.lineageFamily;renderReligiousLineages()});
 renderReligiousLineages();

 const roomFilters=document.getElementById('foundationRoomFilters'),roomCatalog=document.getElementById('foundationRoomCatalog'),roomReadout=document.getElementById('foundationRoomReadout');
 const roomRows=foundationRooms.rooms||[],ownerRooms=[...new Set(roomRows.map(x=>x.house_location?.primary_room).filter(Boolean))].sort();
 let roomOwner='all',roomMode='all';
 roomFilters.innerHTML='<button class="room-filter" data-room-owner="all" aria-pressed="true">All House Rooms</button>'+ownerRooms.map(x=>'<button class="room-filter" data-room-owner="'+esc(x)+'" aria-pressed="false">'+esc(x)+'</button>').join('')+'<span style="flex-basis:100%"></span><button class="room-filter" data-room-mode="all" aria-pressed="true">All</button><button class="room-filter" data-room-mode="map" aria-pressed="false">Map-ready origin</button><button class="room-filter" data-room-mode="today" aria-pressed="false">Quantified Today</button>';
 const formatValue=m=>{const q=m.qualifier?m.qualifier+' ':'';const v=typeof m.value==='number'?new Intl.NumberFormat('en-US',{notation:m.value>=1000000?'compact':'standard',maximumFractionDigits:1}).format(m.value):String(m.value??'');return q+v+' '+(m.unit||'')};
 function renderFoundationRooms(){
   const rows=roomRows.filter(x=>(roomOwner==='all'||x.house_location?.primary_room===roomOwner)&&(roomMode==='all'||(roomMode==='map'&&x.origin_door?.map_ready)||(roomMode==='today'&&(x.today?.typed_reach||[]).length)));
   roomCatalog.innerHTML=rows.map(x=>{
     const metrics=(x.today?.typed_reach||[]).map(m=>'<i>'+esc(formatValue(m))+'</i>').join('');
     const badges=['House: '+(x.house_location?.primary_room||''),x.house_location?.circle_anchor?.label||'',x.origin_door?.map_ready?'map-ready origin':'non-point / unresolved origin'].filter(Boolean).map(v=>'<span>'+esc(v)+'</span>').join('');
     const st=x.room_status||{},statusHtml='<div class="room-status-ribbon"><div class="status-cell"><b>Origin</b><span>'+esc(st.origin?.label||'')+'</span></div><div class="status-cell"><b>Reproduction</b><span>'+esc(st.reproduction?.label||'')+'</span></div><div class="status-cell"><b>Today</b><span>'+esc(st.today?.label||'')+'</span></div><div class="status-cell"><b>Geography</b><span>'+esc(st.geography?.label||'')+'</span></div></div>',doors=(x.door_history||[]).map(d=>'<article><b>'+esc(d.role||d.event_type||'Door')+'</b><span>'+esc(d.date_or_range||'')+' · '+esc(d.label||'')+'</span></article>').join(''),queue=(x.research_queue||[]).length?'<div class="research-queue"><b>Research queue</b><ul>'+(x.research_queue||[]).map(q=>'<li>'+esc(q)+'</li>').join('')+'</ul></div>':'';return '<article class="foundation-room"><h3>'+esc(x.name)+'</h3><em>'+esc(x.domain)+'</em><div class="room-badges">'+badges+'</div>'+statusHtml+'<div class="room-face"><b>Origin Door</b><span>'+esc(x.origin_door?.event||'')+'</span><small>'+esc(x.origin_door?.time||'')+' · '+esc(x.origin_door?.physical_origin||'distributed/unknown')+' · '+esc(x.origin_door?.place_precision||'')+'</small></div><div class="room-face"><b>House location</b><span>'+esc(x.house_location?.primary_room||'')+' · '+esc(x.house_location?.circle_anchor?.label||'')+'</span><small>'+esc(x.house_location?.circle_anchor?.why||'')+'</small></div><div class="room-face"><b>First reproduction</b><span>'+esc(x.first_reproduction?.evidence?.label||x.first_reproduction?.evidence?.evidence_type||'Not yet recovered')+'</span><small>'+esc(x.first_reproduction?.evidence?.date_or_range||'undated')+' · '+esc(x.first_reproduction?.evidence?.status||'research gap')+'</small></div><div class="room-face"><b>Today</b><span>'+esc(x.today?.continuity_mode||x.today?.current_status||'unresolved')+'</span>'+(metrics?'<div class="room-metrics">'+metrics+'</div>':'<small>'+esc(x.today?.snapshot_coverage||'structural snapshot only')+'</small>')+'</div>'+queue+'<details><summary>Door history & genealogy</summary><div class="door-history">'+doors+'</div><p><b>Root / death-side:</b> '+esc(x.genealogy?.seed_of_death?.summary||'')+'</p><p><b>Sprout / life-side:</b> '+esc(x.genealogy?.seed_of_life?.summary||'')+'</p><p><b>Fall / refoundation:</b> '+esc(x.genealogy?.fall_return_refoundation?.summary||'')+'</p></details></article>';
   }).join('');
   roomReadout.textContent=rows.length+' of '+roomRows.length+' Foundation Rooms visible · '+(roomOwner==='all'?'all House owners':roomOwner)+' · '+(roomMode==='all'?'all snapshot states':roomMode==='map'?'map-ready origins':'quantified Today');
   roomFilters.querySelectorAll('[data-room-owner]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.roomOwner===roomOwner)));
   roomFilters.querySelectorAll('[data-room-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.roomMode===roomMode)));
 }
 roomFilters.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.roomOwner!==undefined)roomOwner=b.dataset.roomOwner;if(b.dataset.roomMode!==undefined)roomMode=b.dataset.roomMode;renderFoundationRooms()});
 renderFoundationRooms();

 const seedFilters=document.getElementById('foundationSeedFilters'),seedRoot=document.getElementById('foundationSeedGrid'),seedReadout=document.getElementById('foundationSeedReadout');
 const seedDomains=[...new Set(seedRows.map(x=>x.domain).filter(Boolean))].sort();let seedDomain='all';
 seedFilters.innerHTML='<button class="seed-toggle" data-seed-domain="all" aria-pressed="true">All Seeds</button>'+seedDomains.map(x=>'<button class="seed-toggle" data-seed-domain="'+esc(x)+'" aria-pressed="false">'+esc(x)+'</button>').join('');
 function renderSeeds(){
   const rows=seedRows.filter(x=>seedDomain==='all'||x.domain===seedDomain);
   seedRoot.innerHTML=rows.map(x=>{
     const places=(x.emergence_places||[]).map(p=>p.clock+' · '+p.place).join(' | ');
     const rise=Array.isArray(x.foundation_rise?.reproduction_basis)?x.foundation_rise.reproduction_basis.join(' · '):String(x.foundation_rise?.reproduction_basis||'');
     const pl=placementBy[x.foundation_id],stage=(pl?.field_projection||[]).map(z=>'<span class="stage-chip"><b>'+esc(z.stage)+'</b> · '+esc(z.plane)+' · '+esc(z.direction)+'</span>').join('');
     return '<article class="seed-card"><h3>'+esc(x.name)+'</h3><em>'+esc(x.domain)+'</em>'+(pl?'<span class="status-chip">'+esc(pl.current_status)+'</span>':'')+'<small>'+esc(places)+'</small><div class="seed-sides"><div class="seed-side"><b>Seed of Death</b><p>'+esc(x.seed_of_death?.summary||'')+'</p><small>'+esc(x.seed_of_death?.time||'')+' · '+esc(x.seed_of_death?.place||'')+' · '+esc(x.seed_of_death?.status||'')+'</small></div><div class="seed-side"><b>Seed of Life</b><p>'+esc(x.seed_of_life?.summary||'')+'</p><small>'+esc(x.seed_of_life?.time||'')+' · '+esc(x.seed_of_life?.place||'')+' · '+esc(x.seed_of_life?.status||'')+'</small></div></div><div class="seed-door"><b>Door crossing</b><p>'+esc(x.door_crossing?.event||'')+'</p><small>'+esc(x.door_crossing?.time||'')+' · '+esc(x.door_crossing?.place||'')+'</small></div><p><b>Foundation rises through:</b> '+esc(rise)+'</p>'+(stage?'<div class="stage-path">'+stage+'</div>':'')+'<p><b>Fall / refoundation:</b> '+esc(x.fall_return_refoundation?.type||'')+' — '+esc(x.fall_return_refoundation?.summary||'')+'</p></article>';
   }).join('');
   seedReadout.textContent=rows.length+' Foundation Seed genealogies visible · '+(seedDomain==='all'?'all domains':seedDomain);
   seedFilters.querySelectorAll('[data-seed-domain]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.seedDomain===seedDomain)));
 }
 seedFilters.addEventListener('click',e=>{const b=e.target.closest('[data-seed-domain]');if(!b)return;seedDomain=b.dataset.seedDomain;renderSeeds()});
 renderSeeds();

 render();
 if(degraded.length){
   foundationReadout.textContent+=' · Reduced detail: '+degraded.join(', ')+' unavailable.';
 }
})().catch(error=>{
 const readout=document.getElementById('foundationReadout');
 if(readout)readout.textContent='Foundation Timeline encountered a rendering error. Static explanation and direct links remain available.';
 console.error(error);
});
