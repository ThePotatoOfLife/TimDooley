// Deferred data projections for the homepage. Loaded only near the relevant sections.
const initHomeProjection=async()=>{
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  try{
    const unavailable=new Set();
    const loadJson=async path=>{
      try{
        const res=await fetch(path);
        if(!res.ok)throw new Error('HTTP '+res.status);
        return await res.json();
      }catch(_){
        unavailable.add(path);
        return null;
      }
    };
    const [rooms,cases,below,routeMatrix,foundationLandscape,foundationRooms]=await Promise.all([
      loadJson('data/house/subrooms.json'),
      loadJson('data/house/entity-dossiers.json'),
      loadJson('data/house/lower-plane-population-atlas.json'),
      loadJson('data/house/route-case-matrix.json'),
      loadJson('data/house/foundation-landscape-synthesis.json'),
      loadJson('data/house/foundation-room-atlas.json')
    ]);
    const routeTabs=document.getElementById('homeRouteTabs'),routePanel=document.getElementById('homeRoutePanel'),routeCases=document.getElementById('homeRouteCases'),routeCasePanel=document.getElementById('homeRouteCasePanel');
    const contrasts=routeMatrix?.mechanism_contrasts||[],routeCaseRows=routeMatrix?.cases||[];
    const renderContrast=(id)=>{
      const x=contrasts.find(c=>c.id===id)||contrasts[0];if(!x||!routePanel)return;
      if(routeTabs)routeTabs.querySelectorAll('[data-route-contrast]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.routeContrast===x.id)));
      const branches=(x.routes||[]).map(r=>'<article class="route-branch"><b>'+esc(r.route||'route')+'</b><em>'+esc(r.operator||'')+'</em><span>'+esc((r.sequence||[]).join(' → '))+'</span><span><strong>Test:</strong> '+esc(r.transition_test||'')+'</span><small><strong>Fails if:</strong> '+esc((r.failure_signs||[]).join(' · '))+'</small></article>').join('');
      routePanel.innerHTML='<h3>'+esc((x.id||'route').replaceAll('-',' '))+'</h3><p>'+esc(x.starting_material||'')+'</p><p class="teaching-question">Shared root: '+esc((x.shared_root||[]).join(' → '))+'</p><div class="route-columns">'+branches+'</div>'+(x.lesson?'<p class="axis-rule">'+esc(x.lesson)+'</p>':'');
    };
    if(routeTabs&&contrasts.length){
      routeTabs.addEventListener('click',e=>{const b=e.target.closest('[data-route-contrast]');if(b)renderContrast(b.dataset.routeContrast)});
      renderContrast('knowledge-fork');
    }else if(routeTabs){routeTabs.hidden=true}
    const renderRouteCase=(id)=>{
      const x=routeCaseRows.find(c=>c.id===id)||routeCaseRows[0];if(!x||!routeCasePanel)return;
      if(routeCases)routeCases.querySelectorAll('[data-route-case]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.routeCase===x.id)));
      routeCasePanel.innerHTML='<b>'+esc(x.subject||x.subject_ref||x.id)+'</b><span><strong>Proposed route:</strong> '+esc(x.proposed_transition||'')+'</span><span><strong>Operator:</strong> '+esc(x.operator||'')+'</span><span><strong>Required:</strong> '+esc(x.condition_required||'')+'</span><small><strong>Falsifier:</strong> '+esc((x.counterevidence_or_falsifier||[]).join(' · '))+'</small><small><strong>World return:</strong> '+esc((x.world_return_measure||[]).join(' · '))+'</small><small><strong>Status:</strong> '+esc(x.status||'')+' · '+esc(x.route_boundary||'')+'</small>';
    };
    if(routeCases&&routeCaseRows.length){
      routeCases.innerHTML=routeCaseRows.map((x,i)=>'<button class="route-case-btn" type="button" data-route-case="'+esc(x.id)+'" aria-pressed="'+String(i===0)+'">'+esc(x.subject||x.subject_ref||x.id)+'</button>').join('');
      routeCases.addEventListener('click',e=>{const b=e.target.closest('[data-route-case]');if(b)renderRouteCase(b.dataset.routeCase)});
      renderRouteCase(routeCaseRows[0]?.id);
    }else if(routeCases){routeCases.hidden=true}
    const foundationPatterns=document.getElementById('homeFoundationPatterns'),foundationPatternPanel=document.getElementById('homeFoundationPatternPanel');
    if(foundationPatterns&&foundationPatternPanel){
      const patterns=foundationLandscape?.trajectory_archetypes||[],recordBy=Object.fromEntries((foundationLandscape?.records||[]).map(x=>[x.foundation_id,x]));
      const renderFoundationPattern=id=>{
        const p=patterns.find(x=>x.id===id)||patterns[0];if(!p)return;
        foundationPatterns.querySelectorAll('[data-foundation-pattern]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.foundationPattern===p.id)));
        const path=(p.pattern||'').split('→').map((x,i,a)=>'<b>'+esc(x.trim())+'</b>'+(i<a.length-1?'<i>→</i>':'')).join('');
        const examples=(p.examples||[]).map(fid=>recordBy[fid]).filter(Boolean).map(x=>'<article class="foundation-example"><b>'+esc(x.name)+'</b><em>'+esc(x.domain_family||x.domain)+'</em><span><strong>Door:</strong> '+esc(x.door_summary||'')+'</span><small>'+esc(x.door_time||'')+' · '+esc(x.door_place||'')+'</small><small><strong>Reproduction:</strong> '+esc(x.reproduction_family||'')+' · <strong>Continuity:</strong> '+esc(x.continuity_mode||'')+'</small></article>').join('');
        foundationPatternPanel.innerHTML='<h3>'+esc(p.label||p.id)+'</h3><p>'+esc(p.lesson||'')+'</p><div class="foundation-path">'+path+'</div><div class="foundation-example-grid">'+examples+'</div><a class="teaching-link" href="timeline/foundations/">Open full Foundation Timeline →</a>';
      };
      if(!patterns.length){foundationPatterns.hidden=true}else foundationPatterns.addEventListener('click',e=>{const b=e.target.closest('[data-foundation-pattern]');if(b)renderFoundationPattern(b.dataset.foundationPattern)});
      if(patterns.length)renderFoundationPattern(foundationLandscape?.homepage_projection?.default_archetype||patterns[0]?.id);
    }
    const foundationRoomRoot=document.getElementById('homeFoundationRooms'),foundationRoomSummary=document.getElementById('homeFoundationRoomSummary');
    if(foundationRoomRoot){
      const roomById=Object.fromEntries((foundationRooms?.rooms||[]).map(x=>[x.foundation_id,x]));
      const featured=(foundationRooms?.homepage_projection?.featured_foundation_ids||[]).map(id=>roomById[id]).filter(Boolean);
      const formatValue=m=>{
        const q=m.qualifier?m.qualifier+' ':'';
        const v=typeof m.value==='number'?new Intl.NumberFormat('en-US',{notation:m.value>=1000000?'compact':'standard',maximumFractionDigits:1}).format(m.value):String(m.value??'');
        return q+v+' '+(m.unit||'');
      };
      if(featured.length)foundationRoomRoot.innerHTML=featured.map(x=>{
        const metrics=(x.today?.typed_reach||[]).slice(0,2).map(m=>'<i>'+esc(formatValue(m))+'</i>').join('');
        return '<article class="foundation-room-card"><h3>'+esc(x.name)+'</h3><em>'+esc(x.domain)+'</em><div class="foundation-room-face"><b>Origin Door</b><span>'+esc(x.origin_door?.event||'')+'</span><small>'+esc(x.origin_door?.time||'')+' · '+esc(x.origin_door?.physical_origin||'distributed/unknown')+(x.origin_door?.map_ready?' · map-ready':'')+'</small></div><div class="foundation-room-face"><b>House</b><span>'+esc(x.house_location?.primary_room||'')+' · '+esc(x.house_location?.circle_anchor?.label||'')+'</span><small>'+esc(x.house_location?.circle_anchor?.why||'')+'</small></div><div class="foundation-room-face"><b>First reproduction</b><span>'+esc(x.first_reproduction?.evidence?.label||x.first_reproduction?.evidence?.evidence_type||'Not yet recovered')+'</span><small>'+esc(x.first_reproduction?.evidence?.date_or_range||'undated')+' · '+esc(x.first_reproduction?.evidence?.status||'research gap')+'</small></div><div class="foundation-room-face"><b>Today</b><span>'+esc(x.today?.continuity_mode||x.today?.current_status||'unresolved')+'</span>'+(metrics?'<div class="foundation-room-metrics">'+metrics+'</div>':'<small>'+esc(x.today?.snapshot_coverage||'structural continuity only')+'</small>')+'</div></article>';
      }).join('');
    }
    if(foundationRoomSummary&&foundationRooms){
      foundationRoomSummary.innerHTML='<span><b>'+esc(foundationRooms.summary?.total_rooms||0)+'</b> Foundation Rooms</span><span><b>'+esc(foundationRooms.summary?.map_ready_origins||0)+'</b> map-ready origin anchors</span><span><b>'+esc(foundationRooms.summary?.current_quantitative_snapshots||0)+'</b> current quantified snapshots</span>';
    }
    const setStat=(id,value)=>{const el=document.querySelector('[data-home-stat="'+id+'"]');if(el)el.textContent=value};
    if(rooms)setStat('rooms',(rooms.subrooms||[]).length);
    if(cases)setStat('cases',(cases.dossiers||[]).length);
    if(below)setStat('below',(below.zones||[]).length);
    if(foundationRooms)setStat('foundations',foundationRooms.summary?.total_rooms||foundationRooms.population||0)
    const root=document.getElementById('homeRealityCases');
    if(root&&cases){
      const rows=(cases.dossiers||[]).slice(0,4);
      root.innerHTML=rows.map(x=>{
        const m=(x.longitudinal_indicators||[])[0],obs=(m?.observations||[]),latest=obs[obs.length-1]||{},src=(x.sources||[]).find(s=>s.id===latest.source);
        const metric=m?'<div class="case-observation"><strong>'+esc(latest.value??'')+'</strong><b>'+esc(m.unit||'')+'</b><small><em>'+esc(m.descriptive_change||'')+'</em> · '+esc(m.reading||'')+'</small><small>'+esc(m.limit||'')+'</small>'+(src?.url?'<a class="case-source" href="'+esc(src.url)+'" rel="noopener noreferrer">Official source ↗</a>':'')+'</div>':'';
        return '<article class="reality-card"><span class="case-kind">'+esc(x.identity?.kind||'entity')+'</span><h3>'+esc(x.identity?.name||x.id)+'</h3><p class="case-scale">'+esc(x.scale_profile?.operating_scale||'')+'</p>'+metric+'<a class="case-source" href="house/#crystallized-cases">Open full House case →</a></article>';
      }).join('');
    }
    document.documentElement.dataset.homeProjection=unavailable.size?'partial':'live';
  }catch(e){
    document.documentElement.dataset.homeProjection='fallback';
  }
};
initHomeProjection();
