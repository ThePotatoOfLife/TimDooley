(()=>{
  const body=document.body,root=document.getElementById('houseDepthSwitcher'),explain=document.getElementById('houseDepthExplain');
  if(!root)return;
  const copy={
    overview:'Overview shows the minimum structure needed to understand the House.',
    structure:'Structure reveals the topology, projections, operators and nested Rooms.',
    research:'Research reveals the full maintenance layer: federation, census, interfaces and population diagnostics.'
  };
  function setHouseDepth(depth){
    body.classList.remove('house-depth-overview','house-depth-structure','house-depth-research');
    body.classList.add('house-depth-'+depth);
    root.querySelectorAll('[data-house-depth]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.houseDepth===depth)));
    if(explain)explain.textContent=copy[depth]||copy.overview;
    try{localStorage.setItem('potato-house-depth',depth)}catch(e){}
  }
  root.addEventListener('click',e=>{const b=e.target.closest('[data-house-depth]');if(b)setHouseDepth(b.dataset.houseDepth)});
  let initial='overview';
  try{const saved=localStorage.getItem('potato-house-depth');if(['overview','structure','research'].includes(saved))initial=saved}catch(e){}
  setHouseDepth(initial);
})();

(async()=>{
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  try{
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
    const [subLoad,topoLoad,intLoad,projLoad]=await Promise.all([
      loadJson('../data/house/subrooms.json',null,true),
      loadJson('../data/house/topology.json',null,true),
      loadJson('../data/house/interfaces.json',null,true),
      loadJson('../data/house/projections.json',null,true)
    ]);
    // The Overview is mostly authored HTML. Let it and the critical topology paint
    // before pulling the much heavier research/dossier bundle (~850 KB today).
    await new Promise(resolve=>{
      if('requestIdleCallback' in window) requestIdleCallback(()=>resolve(),{timeout:1200});
      else setTimeout(resolve,0);
    });
    const [conceptLoad,holdLoad,collLoad,dataHoldLoad,dossierLoad,societyLoad,entityLoad,foundationLoad,foundation2Load,foundation3Load]=await Promise.all([
      loadJson('../data/house/concept-topology.json',{concepts:[],relation_types:[],relations:[]}),
      loadJson('../data/house/holdings.json',{holdings:[]}),
      loadJson('../data/house/collections.json',{collections:[]}),
      loadJson('../data/house/data-holdings.json',{bundles:[]}),
      loadJson('../data/house/room-dossiers.json',{dossiers:[]}),
      loadJson('../data/house/society-population.json',{triune_lenses:[],population_families:[],anchors:[]}),
      loadJson('../data/house/entity-dossiers.json',{dossiers:[]}),
      loadJson('../data/house/foundations-wave-001.json',{records:[]}),
      loadJson('../data/house/foundations-wave-002.json',{records:[]}),
      loadJson('../data/house/foundations-wave-003.json',{records:[]})
    ]);
    const sub=subLoad.value,topo=topoLoad.value,interfaces=intLoad.value,projections=projLoad.value,concepts=conceptLoad.value,holdings=holdLoad.value,collections=collLoad.value,dataHoldings=dataHoldLoad.value,dossiers=dossierLoad.value,society=societyLoad.value,entityDossiers=entityLoad.value,foundation1=foundationLoad.value,foundation2=foundation2Load.value,foundation3=foundation3Load.value;
    const degraded=[];
    if(!conceptLoad.ok)degraded.push('concept topology');
    if(!holdLoad.ok)degraded.push('holdings');
    if(!collLoad.ok)degraded.push('collections');
    if(!dataHoldLoad.ok)degraded.push('data holdings');
    if(!dossierLoad.ok)degraded.push('Room dossiers');
    if(!societyLoad.ok)degraded.push('society population');
    if(!entityLoad.ok)degraded.push('entity dossiers');
    if(!foundationLoad.ok||!foundation2Load.ok||!foundation3Load.ok)degraded.push('foundation examples');
    const groups=document.getElementById('houseSubrooms'),corridors=document.getElementById('houseCorridors'),interfaceRoot=document.getElementById('houseInterfaces'),projectionTabs=document.getElementById('houseProjectionTabs'),projectionPanel=document.getElementById('houseProjectionPanel'),operatorRoot=document.getElementById('houseOperators'),operatorRelations=document.getElementById('houseOperatorRelations'),holdingsRoot=document.getElementById('houseHoldingsGrid'),collectionStrip=document.getElementById('houseCollectionStrip');



    const foundationRoot=document.getElementById('foundationExamples');
    if(foundationRoot){
      const combined=[...(foundation1.records||[]),...(foundation2.records||[]),...(foundation3.records||[])];
      const picks=['potatoism-foundation','eu-treaty-foundation','christianity-foundation','university-copenhagen-foundation','tcp-ip-internet-foundation','unicode-foundation','rochdale-cooperative-foundation','rule-of-saint-benedict','newtonian-mechanics-foundation'];
      foundationRoot.innerHTML=picks.map(id=>combined.find(x=>x.id===id)).filter(Boolean).map(x=>{
        const first=(x.clocks||[])[0],repro=x.reproduction_mechanism||((x.foundation_rules||x.load_bearing_rules||[]).slice(0,3).join(' · '));
        return '<article class="foundation-card"><strong>'+esc(x.name)+'</strong><em>'+esc(x.domain)+'</em><p>'+esc(x.why_foundational)+'</p><p><b>First clock:</b> '+esc(first?.date_or_range||'')+' · '+esc(first?.label||'')+'</p><p><b>Reproduces through:</b> '+esc(repro||'')+'</p></article>';
      }).join('');
    }

    const entityTabs=document.getElementById('entityCaseTabs'),entityPanel=document.getElementById('entityCasePanel');
    if(entityTabs&&entityPanel){
      const rows=entityDossiers.dossiers||[];
      entityTabs.innerHTML=rows.map((x,i)=>'<button class="case-tab" type="button" data-case-id="'+esc(x.id)+'" aria-pressed="'+String(i===0)+'">'+esc(x.identity?.name||x.id)+'</button>').join('');
      function renderEntityCase(id){
        const x=rows.find(r=>r.id===id)||rows[0];if(!x)return;
        entityTabs.querySelectorAll('[data-case-id]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.caseId===x.id)));
        const op=(x.operators||[]).map(o=>'<div class="case-operator"><b>'+esc(o.operator)+'</b><span>'+esc(o.why)+'</span><span><strong>Test:</strong> '+esc(o.test)+'</span></div>').join('');
        const qs=(x.discovery_questions||[]).map(q=>'<div class="case-question"><b>Research question</b><span>'+esc(q)+'</span></div>').join('');
        const tensions=(x.tensions||[]).map(t=>'<span>'+esc(t.text)+'</span>').join('');
        const longitudinal=(x.longitudinal_indicators||[]).map(m=>'<article><b>'+esc(m.id.replaceAll('-',' '))+'</b><div class="case-observations">'+(m.observations||[]).map(o=>'<span>'+esc(o.period)+' · '+esc(o.value)+' '+esc(m.unit)+'</span>').join('')+'</div><small><em>'+esc(m.descriptive_change||'')+'</em> · '+esc(m.reading||'')+'</small><small><b>Limit:</b> '+esc(m.limit||'')+'</small></article>').join('');
        entityPanel.innerHTML='<h3>'+esc(x.identity?.name||x.id)+'</h3><div class="case-kicker">'+esc(x.identity?.kind||'entity')+' · '+esc(x.identity?.jurisdiction_or_scope||'')+'</div><div class="case-triad"><article><b>Spirit</b><span>'+esc(x.spirit?.documented_mission||'')+'</span></article><article><b>Mind</b><span>'+esc(x.mind?.decision_system||'')+'</span></article><article><b>Body</b><span>'+esc(x.body?.operational_capacity||'')+'</span></article></div><div class="case-instrument-grid"><article class="case-instrument"><b>Scale</b><span>'+esc(x.scale_profile?.operating_scale||'')+'</span><span><strong>Dependencies:</strong> '+esc((x.scale_profile?.key_dependencies||[]).join(' · '))+'</span></article><article class="case-instrument"><b>Reproduction & correction</b><span>'+esc((x.reproduction_and_correction?.reproduction_mechanisms||[]).slice(0,4).join(' · '))+'</span><span><strong>Observed change:</strong> '+esc(x.reproduction_and_correction?.observed_change||'')+'</span></article><article class="case-instrument"><b>Visibility & access</b><span>'+esc(x.visibility_and_access?.public_observability||'')+'</span><span><strong>Guard:</strong> '+esc(x.visibility_and_access?.status_guard||'')+'</span></article><article class="case-instrument"><b>Scope boundary</b><span>'+esc(x.scale_profile?.scope_boundary||'')+'</span><span><strong>Missingness:</strong> '+esc(x.visibility_and_access?.structural_missingness||'')+'</span></article></div><div class="case-longitudinal"><p class="eyebrow">Observed change over time</p>'+longitudinal+'</div><div class="case-grid"><div><p class="eyebrow">Operators that survive contact with evidence</p><div class="case-operators">'+op+'</div></div><div><p class="eyebrow">Shadow & discovery</p><p class="boundary"><b>Known unknowns:</b> '+esc((x.shadow?.known_unknowns||[]).join(' · '))+'</p><div class="case-questions">'+qs+'</div></div></div><div class="case-meta">'+tensions+'</div>';
      }
      entityTabs.addEventListener('click',e=>{const b=e.target.closest('[data-case-id]');if(b)renderEntityCase(b.dataset.caseId)});
      renderEntityCase(rows[0]?.id);
    }

    const triuneRoot=document.getElementById('societyTriune'),societyTabs=document.getElementById('societyTabs'),societyFamilies=document.getElementById('societyFamilies'),societyAnchors=document.getElementById('societyAnchors');
    if(triuneRoot){
      triuneRoot.innerHTML=(society.triune_lenses||[]).map(x=>'<article class="triune-card"><strong>'+esc(x.label)+'</strong><small>'+esc(x.question)+'</small><p>'+esc((x.contains||[]).join(' · '))+'</p><p><b>Guard:</b> '+esc(x.caution)+'</p></article>').join('');
    }
    if(societyTabs&&societyFamilies){
      const families=society.population_families||[];
      const ids=['all',...families.map(x=>x.id)];
      societyTabs.innerHTML=ids.map((id,i)=>'<button class="society-tab" type="button" data-society-family="'+esc(id)+'" aria-pressed="'+String(i===0)+'">'+esc(id==='all'?'All society':families.find(x=>x.id===id)?.label||id)+'</button>').join('');
      function renderSocietyFamilies(id='all'){
        const rows=families.filter(x=>id==='all'||x.id===id);
        societyFamilies.innerHTML=rows.map(x=>'<article class="society-family"><strong>'+esc(x.label)+'</strong><em>'+esc((x.primary_rooms||[]).join(' · '))+'</em><p>'+esc((x.examples||[]).join(' · '))+'</p><small><b>Relations:</b> '+esc((x.relations||[]).join(' · '))+'</small></article>').join('');
        societyTabs.querySelectorAll('[data-society-family]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.societyFamily===id)));
      }
      societyTabs.addEventListener('click',e=>{const b=e.target.closest('[data-society-family]');if(b)renderSocietyFamilies(b.dataset.societyFamily)});
      renderSocietyFamilies();
    }
    if(societyAnchors){
      societyAnchors.innerHTML=(society.anchors||[]).map(x=>'<article class="society-anchor"><strong>'+esc(x.name)+'</strong><em>'+esc(x.kind)+'</em><p>'+esc(x.summary)+'</p><div class="anchor-lenses"><span><b>Spirit</b>'+esc(x.spirit)+'</span><span><b>Mind</b>'+esc(x.mind)+'</span><span><b>Body</b>'+esc(x.body)+'</span></div><p><b>Relations:</b> '+esc((x.relations||[]).join(' · '))+'</p><a href="'+esc(x.source?.url||'#')+'" rel="noopener noreferrer">Source · '+esc(x.source?.label||'official')+'</a></article>').join('');
    }

    const parentOrder=['potatoverse-canon','archive-sources','time-history','traditions-texts','science-formal-models','life-body','world-systems','culture-information','works','research-lab'];
    const parentLabels={
      'potatoverse-canon':'Potatoverse / Canon','archive-sources':'Archive & Sources','time-history':'Time & History',
      'traditions-texts':'Traditions & Texts','science-formal-models':'Science & Formal Models','life-body':'Life & Body',
      'world-systems':'World Systems','culture-information':'Culture & Information','works':'Works','research-lab':'Research Lab'
    };
    const surfaceHref=id=>({
      tim:'../tim-dooley/',religion:'../religion/',philosophy:'../philosophy/',science:'../science/',world:'../world/',
      axis:'../axis/',house:'../house/',paths:'../paths/',sources:'../context/source-authority/',timeline:'../timeline/',
      history:'../history/',story:'../tim-dooley/story/',bible:'../traditions/bible/',explore:'../explore/',context:'../context/',
      'life-body':'../life-body/','research-lab':'../research-lab/',politics:'../politics/',law:'../law/',economy:'../economy/',
      'world-systems':'../world-systems/','world-map':'../world-map/',north:'../north/',culture:'../context/culture/',works:'../works/',questions:'../questions/'
    }[id]||null);
    const allRows=sub.subrooms||[];
    function renderRooms(coord='all'){
      groups.innerHTML=parentOrder.map(pid=>{
        const rows=allRows.filter(x=>x.parent_room_id===pid&&(coord==='all'||(x.topology_profile?.primary_coordinates||[]).includes(coord)));
        if(!rows.length)return '';
        const chips=rows.map(x=>{
          const sid=(x.public_surface_ids||[]).find(surfaceHref),href=sid&&surfaceHref(sid);
          const profile=x.topology_profile||{};
          const tip=x.purpose+' · '+(profile.primary_coordinates||[]).join(' / ')+' · '+(profile.interface_kinds||[]).join(', ');
          return href?'<a href="'+esc(href)+'" title="'+esc(tip)+'">'+esc(x.title)+'</a>':'<span title="'+esc(tip)+'">'+esc(x.title)+'</span>';
        }).join('');
        return '<div class="subroom-group"><h3>'+esc(parentLabels[pid]||pid)+'</h3><div class="subroom-list">'+chips+'</div></div>';
      }).join('');
      const count=allRows.filter(x=>coord==='all'||(x.topology_profile?.primary_coordinates||[]).includes(coord)).length;
      const readout=document.getElementById('houseTopologyReadout');
      if(readout)readout.textContent=coord==='all'?'Showing all '+count+' nested Rooms. These are relational lenses, not physical coordinates.':'Showing '+count+' nested Rooms whose topology profile uses '+coord.toUpperCase()+'. Ownership and identity do not move when the lens changes.';
      document.querySelectorAll('#houseTopologyLenses [data-coordinate]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.coordinate===coord)));
    }
    renderRooms();
    document.getElementById('houseTopologyLenses')?.addEventListener('click',e=>{const b=e.target.closest('[data-coordinate]');if(b)renderRooms(b.dataset.coordinate)});
    if(holdingsRoot){
      const rows=holdings.holdings||[];
      const dossierMap=new Map((dossiers.dossiers||[]).map(x=>[x.room_id,x]));
      const bundlesByRoom=new Map();(dataHoldings.bundles||[]).forEach(b=>{if(!bundlesByRoom.has(b.primary_room_id))bundlesByRoom.set(b.primary_room_id,[]);bundlesByRoom.get(b.primary_room_id).push(b)});
      holdingsRoot.innerHTML=rows.map(x=>{const bundles=bundlesByRoom.get(x.room_id)||[];const dataFiles=bundles.reduce((n,b)=>n+(b.file_count||0),0);const d=dossierMap.get(x.room_id),p=d?.center_pairing||{};const bundleLine=bundles.length?'<small><b>Datasets:</b> '+esc(bundles.map(b=>b.title).join(' · '))+'</small>':'';const passageLine=d?.passages?.length?'<small><b>Passages:</b> '+esc(d.passages.slice(0,3).map(p=>p.type+' → '+p.other_room_id).join(' · '))+'</small>':'';const collectionLine=d?.collections?.length?'<small><b>Collections:</b> '+esc(d.collections.map(c=>c.title).join(' · '))+'</small>':'';const centerLine=p.contribution?'<small><b>Center contribution:</b> '+esc(p.contribution)+'</small>':'';const testLine=p.shared_tests?.length?'<small><b>Tests:</b> '+esc(p.shared_tests.join(' · '))+'</small>':'';const handoffLine=p.hands_to?.length?'<small><b>Hands mature work to:</b> '+esc(p.hands_to.join(' · '))+'</small>':'';return '<article class="holding-card"><strong>'+esc(x.title)+'</strong><em>'+esc(x.primary_file_count)+' knowledge · '+esc(dataFiles)+' data files</em><small>'+esc(d?.entrance||x.purpose)+'</small>'+centerLine+'<ul>'+((x.featured_holdings||[]).slice(0,4).map(h=>'<li>'+esc(h.id||h.path)+'</li>').join('')||'<li>No featured holding selected yet.</li>')+'</ul>'+testLine+handoffLine+bundleLine+passageLine+collectionLine+'</article>'}).join('');
      if(collectionStrip)collectionStrip.innerHTML=(collections.collections||[]).map(x=>{const label=esc(x.title)+' · '+esc(x.source_file_count)+' files';const tip=esc(x.boundary);const href=x.public_route?'../'+String(x.public_route).replace(/^\\/+/, ''):null;return href?'<a href="'+esc(href)+'" title="'+tip+'">'+label+'</a>':'<span title="'+tip+'">'+label+'</span>';}).join('');
    }
    if(federationRoot){
      federationRoot.innerHTML=(federation.forms||[]).map(x=>'<div class="federation-card"><strong>'+esc(x.label)+'</strong><em>'+esc(x.structural_kind)+'</em><span>'+esc(x.question)+'</span><small>'+esc(x.relation_to_house)+'</small></div>').join('');
    }
    if(pulseRoot){
      const s=pulse.summary||{};
      const cells=[['Nested Rooms',s.nested_rooms],['No guarded interface',s.no_guarded_interface],['Sparse roots',s.sparse_roots],['No reader page',s.no_public_surface],['Adjacent but unguarded',s.adjacent_but_unguarded]];
      pulseRoot.innerHTML=cells.map(x=>'<div class="pulse-cell"><b>'+esc(x[1]??0)+'</b><span>'+esc(x[0])+'</span></div>').join('');
    }
    if(censusTabs&&censusGrid){
      const roleRows=census.role_types||[], instances=census.instances||[];
      const preferred=['field','vineyard','road','path','view','court','table','bridge','gate','door','archive','treasury','foundation','pillar','protocol','state','projection','tabernacle','vessel'];
      const roles=['all',...preferred.filter(id=>roleRows.some(r=>r.id===id))];
      censusTabs.innerHTML=roles.map((id,i)=>'<button class="census-tab" type="button" data-census-role="'+esc(id)+'" aria-pressed="'+String(i===0)+'">'+esc(id==='all'?'All roles':id)+'</button>').join('');
      function renderCensus(role='all'){
        const rows=instances.filter(x=>role==='all'||(x.roles||[]).includes(role));
        censusGrid.innerHTML=rows.map(x=>'<div class="census-card"><strong>'+esc(x.title)+'</strong><em>'+esc((x.roles||[]).join(' · '))+'</em><small>'+esc(x.note||'')+'</small></div>').join('');
        if(censusReadout)censusReadout.textContent=(role==='all'?'Showing all ':('Showing '+role.toUpperCase()+' · '))+rows.length+' registered structures. Structural role does not change knowledge ownership.';
        censusTabs.querySelectorAll('[data-census-role]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.censusRole===role)));
      }
      censusTabs.addEventListener('click',e=>{const b=e.target.closest('[data-census-role]');if(b)renderCensus(b.dataset.censusRole)});
      renderCensus();
    }
    if(projectionTabs&&projectionPanel){
      const rows=projections.projections||[];
      projectionTabs.innerHTML=rows.map((x,i)=>'<button class="projection-tab" type="button" data-projection="'+esc(x.id)+'" aria-pressed="'+String(i===0)+'">'+esc(x.label)+'</button>').join('');
      function renderProjection(id){
        const p=rows.find(x=>x.id===id)||rows[0];if(!p)return;
        projectionTabs.querySelectorAll('[data-projection]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.projection===p.id)));
        projectionPanel.innerHTML='<h3>'+esc(p.label)+'</h3><p>'+esc(p.question)+'</p><div class="projection-meta"><div><b>One</b><span>'+esc(p.one)+'</span></div><div><b>Many</b><span>'+esc(p.many)+'</span></div><div><b>Emphasis</b><span>'+esc((p.emphasis||[]).join(' · '))+'</span></div><div><b>Project use</b><span>'+esc(p.project_mapping)+'</span></div></div><p><b>Guard</b> '+esc(p.guard)+'</p>';
      }
      projectionTabs.addEventListener('click',e=>{const b=e.target.closest('[data-projection]');if(b)renderProjection(b.dataset.projection)});
      renderProjection(rows[0]?.id);
    }
    if(operatorRoot){
      const preferred=['potato-of-life','father','son','spirit','door','plane','axis','cross','eye','face','potato','seed','root','tree','mountain','ladder','spiral','fruit','garden','shell-cube','swamp'];
      const byConcept=Object.fromEntries((concepts.concepts||[]).map(x=>[x.id,x]));
      const typeLabels=Object.fromEntries((concepts.relation_types||[]).map(x=>[x.id,x.label]));
      operatorRoot.innerHTML=preferred.filter(id=>byConcept[id]).map(id=>{const x=byConcept[id];return '<button class="operator-card" type="button" data-operator="'+esc(id)+'" aria-controls="houseOperatorRelations" aria-pressed="false"><b>'+esc(x.label)+'</b><small>'+esc(x.operation)+'</small></button>';}).join('');
      function renderOperator(id,updateUrl=true){
        const x=byConcept[id];if(!x||!operatorRelations)return;
        operatorRoot.querySelectorAll('[data-operator]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.operator===id)));
        const rows=(concepts.relations||[]).filter(r=>r.from===id||r.to===id);
        const rendered=rows.map(r=>{
          const outgoing=r.from===id,target=outgoing?r.to:r.from,other=byConcept[target]?.label||target;
          const direction=outgoing?'→ '+other:'← '+other;
          return '<div class="relation-row"><b>'+esc(direction)+'</b><em>'+esc(typeLabels[r.type]||r.type)+'</em><span>'+esc(r.description)+'</span></div>';
        }).join('');
        const formal=x.formal_type?'<p class="boundary"><b>Formal type:</b> '+esc(x.formal_type.template)+' · '+esc(x.formal_type.schema||'')+(x.formal_type.primary_project_component?' · '+esc(x.formal_type.primary_project_component):'')+'</p>':'';operatorRelations.innerHTML='<h3>'+esc(x.label)+'</h3><p>'+esc(x.operation)+' · <b>Boundary:</b> '+esc(x.boundary)+'</p>'+formal+'<div class="relation-list">'+(rendered||'<span class="boundary">No typed operator relations are registered yet.</span>')+'</div>';
        if(updateUrl){const u=new URL(location.href);u.searchParams.set('operator',id);history.replaceState(null,'',u);}
      }
      operatorRoot.addEventListener('click',e=>{const b=e.target.closest('[data-operator]');if(b)renderOperator(b.dataset.operator)});
      const requestedOperator=new URL(location.href).searchParams.get('operator');
      renderOperator(byConcept[requestedOperator]?requestedOperator:'door',false);
    }
    if(interfaceRoot)interfaceRoot.innerHTML=(interfaces.interfaces||[]).map(x=>'<div class="interface-card"><strong>'+esc(x.from)+' → '+esc(x.to)+'</strong><em>'+esc(x.type)+'</em><small>'+esc(x.changes)+'</small><small><b>Guard:</b> '+esc(x.guard)+'</small></div>').join('');
    corridors.innerHTML=(topo.strong_corridors||[]).map(x=>'<div class="corridor-row"><b>'+esc(parentLabels[x.from]||x.from)+'</b><em>'+esc(x.type)+'</em><b>'+esc(parentLabels[x.to]||x.to)+'</b></div>').join('');
    if(degraded.length){
      const readout=document.getElementById('houseTopologyReadout');
      if(readout)readout.textContent+=' · Reduced detail: '+degraded.join(', ')+' unavailable.';
    }
  }catch(e){
    document.getElementById('houseSubrooms').innerHTML='<p class="boundary">Nested Room data could not be loaded. The ten canonical Dwellings above remain the stable top-level structure.</p>';
    document.getElementById('houseCorridors').innerHTML='';
  }
})();
