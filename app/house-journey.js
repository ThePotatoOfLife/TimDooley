// Shared reader infrastructure for House-connected surfaces.
(function(){
  if(typeof document==='undefined')return;
  const current=document.currentScript;
  const baseUrl=current?.src||document.baseURI;
  const journeyStyle=[...document.querySelectorAll('link[rel="stylesheet"]')].find(link=>
    link.dataset.houseJourneyStyle!==undefined||/\/app\/house-journey\.css(?:\?|$)/.test(link.href||'')
  );
  if(!journeyStyle){
    try{
      const link=document.createElement('link');
      link.rel='stylesheet';
      const cssUrl=new URL('house-journey.css?v=20261007b',baseUrl);
      link.href=cssUrl.href;
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
  if(window.__potatoHouseJourneyBooted)return;
  window.__potatoHouseJourneyBooted=true;
  const marker='/TimDooley/';
  const pathName=location.pathname;
  const markerIndex=pathName.indexOf(marker);
  const base=markerIndex>=0?pathName.slice(0,markerIndex+marker.length):'/';

  const esc=(v)=>String(v??'').replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
  const jsonCache=window.__potatoJsonPromiseCache||(window.__potatoJsonPromiseCache=new Map());
  function getJson(path){
    const href=new URL(base+path,location.href).href;
    if(!jsonCache.has(href)){
      const request=fetch(href,{cache:'default'}).then(response=>{
        if(!response.ok)throw new Error(path+' '+response.status);
        return response.json();
      }).catch(error=>{jsonCache.delete(href);throw error});
      jsonCache.set(href,request);
    }
    return jsonCache.get(href);
  }
  async function getOptionalJson(path,fallback){
    try{return await getJson(path)}catch(_){return fallback}
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
        const stateLabel=primary?'Home floor':projected?'Also appears here':'Not used on this floor';
        const note=projected
          ?(notes[level]||'This Room can also be approached from this floor.')
          :'This Room is not part of this floor\'s current view, so the elevator leaves it dim here.';
        return '<article class="room-floor-card '+state+'" data-floor="'+level+'">'
          +'<strong>'+levelLabels[level]+'</strong>'
          +'<small>'+stateLabel+'</small>'
          +'<p>'+esc(note)+'</p>'
          +'</article>';
      }).join('');

      const section=document.createElement('section');
      section.className='room-floor-projection';
      section.dataset.roomId=roomId;
      section.innerHTML='<p class="eyebrow">Where this Room appears</p>'
        +'<h2>How this subject looks from the three floors</h2>'
        +'<p>The subject stays the same while the floor changes the angle. Its home floor is the natural starting point; another lit floor means the same Room is useful from that perspective too.</p>'
        +'<div class="room-floor-grid">'+cards+'</div>';

      const main=document.querySelector('main');
      if(!main||main.querySelector('.room-floor-projection'))return;
      // Subject first: House projection follows the first authored reader section.
      // Architecture should enrich the subject after the reader has entered it.
      const firstReader=main.querySelector('.dwelling-reader');
      if(firstReader) firstReader.insertAdjacentElement('afterend',section);
      else {
        const header=main.querySelector('.page-header');
        if(header) header.insertAdjacentElement('afterend',section);
        else main.append(section);
      }
    }catch(e){}
  }


  async function installInhabitants(){
    const match=location.pathname.match(/\/rooms\/inside\/([^/]+)\//);
    if(!match)return;
    const roomId=decodeURIComponent(match[1]);
    try{
      const [inhData,subData,featuredData]=await Promise.all([
        getJson('data/house/room-inhabitants.json'),
        getJson('data/house/subrooms.json'),
        getOptionalJson('data/house/room-featured-objects.json',{rooms:[]})
      ]);
      const room=(subData.subrooms||[]).find(x=>x.id===roomId||x.route_id===roomId);
      if(!room)return;
      const canonicalRoomId=room.id;
      const rows=(inhData.inhabitants||[]).filter(x=>(x.room_ids||[]).includes(canonicalRoomId));
      if(!rows.length)return;
      const featureRow=(featuredData.rooms||[]).find(x=>x.room_id===canonicalRoomId);
      const featureIds=new Set(featureRow?.object_ids||[]);
      const featuredRows=(featureRow?.object_ids||[]).map(id=>rows.find(x=>x.id===id)).filter(Boolean);
      const otherRows=rows.filter(x=>!featureIds.has(x.id));

      const main=document.querySelector('main');
      if(!main)return;
      const section=document.createElement('section');
      section.className='room-inhabitants-panel';
      const renderCard=x=>{
        const q=new URLSearchParams({room:room.parent_room_id,inner:canonicalRoomId,object:x.id});
        const rawRoute=String(x.route||'');
        const objectHref=rawRoute
          ?(/^(https?:|#)/.test(rawRoute)?rawRoute:base+rawRoute.replace(/^\//,''))
          :'';
        const actions=(objectHref?'<a class="room-inhabitant-open" href="'+esc(objectHref)+'">Open the thing →</a>':'')
          +'<a class="room-inhabitant-center" href="'+base+'elevator/?'+q.toString()+'">Locate in House →</a>';
        return '<article class="room-inhabitant-card"><strong>'+esc(x.label)+'</strong><small>'+esc(x.kind||'object')+'</small>'
          +(x.summary?'<p>'+esc(x.summary)+'</p>':'')
          +'<div class="room-inhabitant-actions">'+actions+'</div></article>';
      };
      const startHtml=featuredRows.length
        ?'<div class="room-featured-objects"><p class="eyebrow">Start here</p><h3>The strongest objects for understanding this Room</h3><p class="boundary">These are editorial entry points, not a ranking of truth or importance across the whole project.</p><div class="room-inhabitant-grid room-inhabitant-grid--featured">'+featuredRows.map(renderCard).join('')+'</div></div>'
        :'';
      const moreRows=featuredRows.length?otherRows:rows;
      const moreHtml=moreRows.length
        ?'<details class="room-more-objects" '+(featuredRows.length?'':'open')+'><summary>'+(featuredRows.length?'More in this Room · ':'What lives in this Room · ')+moreRows.length+'</summary><div class="room-inhabitant-grid">'+moreRows.map(renderCard).join('')+'</div></details>'
        :'';
      section.innerHTML='<p class="eyebrow">Inhabitants / cases</p><h2>What lives in this Room</h2><p class="boundary">Open an object for its substance; use Locate in House when you want to see what sits around it.</p>'+startHtml+moreHtml;
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
        getOptionalJson('data/house/interfaces.json',{interfaces:[]}),
        getJson('data/house/room-dossiers.json'),
        getOptionalJson('data/house/population-pulse.json',{rooms:[]})
      ]);
      const room=(subData.subrooms||[]).find(x=>x.id===roomId||x.route_id===roomId);
      if(!room)return;
      const canonicalRoomId=room.id;
      const holding=(holdData.holdings||[]).find(x=>x.room_id===canonicalRoomId);
      const dossier=(dossierData.dossiers||[]).find(x=>x.room_id===canonicalRoomId);
      const pulse=(pulseData.rooms||pulseData.records||pulseData.population||pulseData.pulses||[]).find?.(x=>x.room_id===canonicalRoomId);
      if(!holding||!dossier)return;


      const titleFor=(id)=>String(id||'').replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
      const featured=(dossier.knowledge_holdings?.featured||holding.featured_holdings||[]).slice(0,12);
      const belongs=(dossier.belongs_here||[]).filter(x=>!/^Material rooted in /i.test(x));
      const passages=(dossier.passages||[]).slice(0,8);
      const next=(dossier.next_work||[]).filter(x=>!/^Deepen the Room through its center contribution:/i.test(x)).slice(0,5);
      const receives=dossier.center_pairing?.receives_from||dossier.local_center?.entry_routes||[];
      const hands=dossier.center_pairing?.hands_to||dossier.local_center?.exit_routes||[];
      const publicSurfaces=dossier.public_surfaces||[];
      const primaryCount=dossier.knowledge_holdings?.primary_file_count??holding.primary_file_count??featured.length;
      const interfaceCount=(ifData.interfaces||[]).filter(x=>x.from===canonicalRoomId||x.to===canonicalRoomId).length;
      const dataFiles=dossier.data_holdings?.owned_file_count||0;
      const functionText=dossier.local_center?.function||dossier.center_pairing?.contribution||dossier.entrance||room.purpose||'';
      const main=document.querySelector('main');if(!main)return;
      if(main.querySelector('.room-richness'))return;
      const section=document.createElement('section');section.className='room-richness';
      const holdingHtml=featured.length?'<div class="room-holding-list">'+featured.map(x=>{
        const path=x.path||'';
        const href=base+'explore/#record='+encodeURIComponent(path||x.id||'');
        return '<a class="room-holding" href="'+href+'"'+(path?' data-source-path="'+esc(path)+'"':'')+'><strong>'+esc(titleFor(x.id||path.split('/').pop()?.replace(/\.[^.]+$/,'')))+'</strong><small>'+esc(x.kind||'archive material')+'</small></a>';
      }).join('')+'</div>':'<p>No deeper records are highlighted here yet.</p>';
      const passageHtml=passages.length?passages.map(x=>{
        const other=x.other_room_id||x.to||x.from||'another Room';
        return '<div class="room-passage"><b>'+esc(titleFor(x.type||'interface'))+'</b> <em>↔ '+esc(titleFor(other))+'</em><small>'+esc(x.changes||'')+(x.guard?' Boundary: '+esc(x.guard):'')+'</small></div>';
      }).join(''):'<p>No cross-Room connection is highlighted here yet.</p>';
      const surfaces=publicSurfaces.map(x=>{
        const route=x.route||'';
        if(!route)return '';
        const href=route.startsWith('/')?base+route.replace(/^\//,''):route;
        return '<a href="'+esc(href)+'">'+esc(x.title||x.id||'Related reader')+' →</a>';
      }).join('');
      const signal=pulse?.signals||{};
      const pulseText=pulse?[
        signal.primary_holding_count!=null?signal.primary_holding_count+' source records':null,
        signal.guarded_interface_count!=null?signal.guarded_interface_count+' cross-Room links':null,
        signal.related_structural_instance_count?signal.related_structural_instance_count+' related items':null,
        signal.data_file_count?signal.data_file_count+' data files':null
      ].filter(Boolean).join(' · '):'';

      section.innerHTML=
        '<p class="eyebrow">More to inspect</p><h2>Go deeper into '+esc(dossier.title||room.title||titleFor(roomId))+'</h2>'
        +'<p class="room-richness-intro">The reader above gives you the subject. Open this layer when you want source records, provenance, connections to other Rooms or questions that are still unresolved.</p>'
        +'<details class="room-richness-details"><summary><span>Show deeper material</span><small>Show archive structure</small></summary>'
        +'<div class="room-richness-meta">'+esc(String(primaryCount))+' source records · '+esc(String(interfaceCount))+' cross-Room links'+(dataFiles?' · '+esc(String(dataFiles))+' supporting data files':'')+(pulseText?' · current index: '+esc(pulseText):'')+'</div>'
        +(belongs.length?'<div class="room-richness-rule"><h3>Scope &amp; boundaries</h3><div class="room-richness-run">'+belongs.map(x=>'<span>'+esc(x)+'</span>').join('')+'</div></div>':'')
        +'<div class="room-richness-rule"><h3>Source records and deeper material</h3><p>Open these when you want the underlying records or a more detailed view of the subject.</p>'+holdingHtml+'</div>'
        +(passages.length?'<div class="room-richness-rule"><h3>Where this connects</h3><p>These links show what changes when the subject meets another domain.</p>'+passageHtml+'</div>':'')
        +((receives.length||hands.length)?'<div class="room-richness-rule"><h3>What feeds this · where it leads</h3>'+(receives.length?'<p><strong>Draws from:</strong> '+receives.map(titleFor).map(esc).join(' · ')+'</p>':'')+(hands.length?'<p><strong>Continues into:</strong> '+hands.map(titleFor).map(esc).join(' · ')+'</p>':'')+'</div>':'')
        +(next.length?'<div class="room-richness-rule"><h3>Still unresolved</h3><ul class="room-next">'+next.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul></div>':'')
        +(surfaces?'<div class="room-richness-rule"><h3>Other ways to read this</h3><p>These routes approach the same material from a different question or level of detail.</p><div class="room-surface-run">'+surfaces+'</div></div>':'')
        +'</details>';

      const doorSection=[...main.querySelectorAll('section')].find(x=>/Adjacent Rooms/i.test(x.textContent||''));
      if(doorSection)main.insertBefore(section,doorSection);else main.appendChild(section);
    }catch(e){}
  }


  async function installDwellingFeaturedObjects(){
    const match=location.pathname.match(/\/rooms\/([^/]+)\/(?:index\.html)?$/);
    if(!match)return;
    const dwellingId=decodeURIComponent(match[1]);
    try{
      const data=await getJson('data/house/dwelling-featured-objects.json');
      const shelf=(data.shelves||[]).find(row=>row&&row.dwelling_id===dwellingId);
      if(!shelf||!(shelf.objects||[]).length)return;
      const main=document.querySelector('main');
      if(!main||main.querySelector('.dwelling-object-shelf'))return;
      const section=document.createElement('section');
      section.className='dwelling-object-shelf';
      section.dataset.dwellingId=dwellingId;
      const cards=(shelf.objects||[]).map(obj=>{
        const href=String(obj.href||'');
        const resolved=/^(https?:|#)/.test(href)?href:base+href.replace(/^\//,'');
        return '<a class="dwelling-object-card" href="'+esc(resolved)+'">'
          +'<small>'+esc(obj.kind||'featured object')+'</small>'
          +'<strong>'+esc(obj.title||'Untitled')+'</strong>'
          +'<span>'+esc(obj.summary||'')+'</span>'
          +'<em>Open →</em>'
          +'</a>';
      }).join('');
      section.innerHTML='<div class="dwelling-object-head"><div><p class="eyebrow">'+esc(shelf.title||'Things on the table')+'</p>'
        +'<h2>Concrete things worth opening before another hallway</h2></div>'
        +'<p>'+esc(shelf.intro||'A curated shelf of strong objects from this domain.')+'</p></div>'
        +'<div class="dwelling-object-grid">'+cards+'</div>';
      const reader=main.querySelector('.dwelling-reader');
      const boundary=[...main.querySelectorAll('section')].find(x=>/What this Dwelling owns/i.test(x.textContent||''));
      if(reader) reader.insertAdjacentElement('afterend',section);
      else if(boundary) main.insertBefore(section,boundary);
      else {
        const header=main.querySelector('.page-header');
        if(header) header.insertAdjacentElement('afterend',section);
        else main.prepend(section);
      }
    }catch(e){}
  }


  async function installRoomsBestOf(){
    const isRoomsIndex=/\/rooms\/(?:index\.html)?$/.test(location.pathname);
    if(!isRoomsIndex)return;
    try{
      const data=await getJson('data/house/dwelling-featured-objects.json');
      const shelves=data.shelves||[];
      if(!shelves.length)return;
      const main=document.querySelector('main');
      if(!main||main.querySelector('.rooms-best-of'))return;
      const picks=shelves.map(shelf=>({dwelling_id:shelf.dwelling_id,object:(shelf.objects||[])[0]})).filter(x=>x.object);
      const section=document.createElement('section');
      section.className='rooms-best-of';
      section.innerHTML='<div class="rooms-best-head"><div><p class="eyebrow">Start with substance</p><h2>Ten things worth opening before you learn the map</h2></div><p>The Rooms system is filing architecture. These are concrete objects from each Dwelling so the archive becomes useful before the topology becomes familiar.</p></div>'
        +'<div class="rooms-best-grid">'+picks.map(p=>{
          const obj=p.object,href=String(obj.href||''),resolved=/^(https?:|#)/.test(href)?href:base+href.replace(/^\//,'');
          return '<a class="rooms-best-card" href="'+esc(resolved)+'"><small>'+esc(String(p.dwelling_id).replace(/-/g,' '))+'</small><strong>'+esc(obj.title||'Untitled')+'</strong><span>'+esc(obj.summary||'')+'</span><em>Open →</em></a>';
        }).join('')+'</div>';
      const header=main.querySelector('.page-header');
      if(header) header.insertAdjacentElement('afterend',section);
      else main.prepend(section);
    }catch(e){}
  }


  function installRoomSectionGuide(){
    const body=document.querySelector('[data-room-reader-body]');
    if(!body)return;
    const headings=[...body.querySelectorAll(':scope > h2')];
    if(headings.length<4)return;
    const slugify=(text)=>String(text||'section').toLowerCase()
      .normalize('NFKD').replace(/[\u0300-\u036f]/g,'')
      .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,72)||'section';
    const used=new Set();
    headings.forEach((h,index)=>{
      if(h.id){used.add(h.id);return}
      let id=slugify(h.textContent);
      if(used.has(id))id+='-'+(index+1);
      used.add(id);h.id=id;
    });
    if(document.querySelector('.room-section-guide'))return;
    const guide=document.createElement('nav');
    guide.className='room-section-guide surface-pane';
    guide.setAttribute('aria-label','In this Room');
    guide.innerHTML='<div><p class="eyebrow">In this Room</p><strong>'+esc(headings.length)+' sections</strong></div><div class="room-section-links">'
      +headings.map(h=>'<a href="#'+esc(h.id)+'">'+esc(h.textContent.trim())+'</a>').join('')
      +'</div>';
    body.insertAdjacentElement('beforebegin',guide);
  }


  async function annotateAdjacentRoomDoors(){
    const match=location.pathname.match(/\/rooms\/inside\/([^/]+)\//);
    if(!match)return;
    const currentId=decodeURIComponent(match[1]);
    const cards=[...document.querySelectorAll('.adj-grid a.adj')];
    if(!cards.length)return;
    try{
      const [subData,ifData]=await Promise.all([
        getJson('data/house/subrooms.json'),
        getJson('data/house/interfaces.json')
      ]);
      const known=new Set((subData.subrooms||[]).map(x=>x.id));
      const interfaces=ifData.interfaces||[];
      const titleCase=v=>String(v||'').replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
      for(const card of cards){
        const url=new URL(card.getAttribute('href')||'',location.href);
        const m=url.pathname.match(/\/rooms\/inside\/([^/]+)\//);
        if(!m)continue;
        const other=decodeURIComponent(m[1]);
        if(!known.has(other))continue;
        const edge=interfaces.find(x=>(x.from===currentId&&x.to===other)||(x.from===other&&x.to===currentId));
        if(!edge||card.querySelector('.adj-interface'))continue;
        const note=document.createElement('span');
        note.className='adj-interface';
        note.innerHTML='<b>'+esc(titleCase(edge.type||'interface'))+'</b><span>'+esc(edge.changes||'')+'</span>';
        if(edge.guard){
          const guard=document.createElement('small');
          guard.textContent='Guard: '+edge.guard;
          note.appendChild(guard);
        }
        card.appendChild(note);
        card.dataset.governedInterface=edge.id||'';
      }
    }catch(e){}
  }


  async function installRoomArchiveDrawers(){
    const match=location.pathname.match(/\/rooms\/inside\/([^/]+)\//);
    if(!match)return;
    const currentId=decodeURIComponent(match[1]);
    try{
      const data=await getJson('data/house/room-archive-drawers.json');
      const rows=(data.drawers||[]).filter(row=>(row.room_ids||[]).includes(currentId));
      if(!rows.length)return;
      const main=document.querySelector('main');
      if(!main||main.querySelector('.room-archive-drawers'))return;
      const section=document.createElement('section');
      section.className='room-archive-drawers';
      section.innerHTML='<div class="room-archive-head"><div><p class="eyebrow">More source material</p><h2>The larger body of work behind this Room</h2></div><p>Featured objects are the easiest entry points. These collections let you inspect the wider body of material when you want more depth.</p></div>'
        +rows.map(row=>{
          const landing=String(row.landing_href||'');
          const landingHref=landing?(/^(https?:|#)/.test(landing)?landing:base+landing.replace(/^\//,'')):'';
          const entries=(row.entries||[]).map(entry=>{
            const p=String(entry.path||'');
            const href=p?base+'explore/#record='+encodeURIComponent(p):'';
            return '<a class="room-archive-entry" href="'+esc(href)+'"'+(p?' data-source-path="'+esc(p)+'"':'')+'><strong>'+esc(entry.title||p)+'</strong><small>'+esc(entry.kind||'source record')+'</small></a>';
          }).join('');
          return '<article class="room-archive-drawer">'
            +'<div class="room-archive-drawer-title"><div><small>'+esc(String(row.record_count||0))+' records</small><h3>'+esc(row.title||'Collection')+'</h3></div>'
            +(landingHref?'<a href="'+esc(landingHref)+'">Open main reader →</a>':'')+'</div>'
            +'<p>'+esc(row.summary||'')+'</p>'
            +'<div class="room-archive-entry-grid">'+entries+'</div>'
            +(row.boundary?'<p class="room-archive-boundary"><strong>Boundary:</strong> '+esc(row.boundary)+'</p>':'')
            +'</article>';
        }).join('');
      const objects=main.querySelector('.room-inhabitants');
      const reader=main.querySelector('[data-room-reader-body]');
      if(objects) objects.insertAdjacentElement('afterend',section);
      else if(reader) reader.insertAdjacentElement('afterend',section);
      else main.appendChild(section);
    }catch(e){}
  }


  async function installHouseDeepCorpusIndex(){
    const isHouse=/\/house\/(?:index\.html)?$/.test(location.pathname);
    if(!isHouse)return;
    try{
      const [data,coverage]=await Promise.all([
        getJson('data/house/room-archive-drawers.json'),
        getJson('data/house/corpus-surface-coverage.json')
      ]);
      const rows=data.drawers||[];
      if(!rows.length)return;
      const holdings=document.getElementById('holdings');
      const main=document.querySelector('main');
      if(!main||document.getElementById('deep-corpora'))return;
      const total=rows.reduce((n,row)=>n+(Number(row.record_count)||0),0);
      const totals=coverage.totals||{};
      const section=document.createElement('section');
      section.className='page-section house-deep-corpora';
      section.id='deep-corpora';
      section.dataset.depth='structure';
      section.innerHTML='<p class="eyebrow">Deeper collections</p>'
        +'<h2>'+esc(rows.length)+' major collections · '+esc(total)+' records</h2>'
        +'<p class="topology-note">These collections answer a simple question: what substantial bodies of material can I inspect next? <strong>'+esc(totals.current_non_retired_reachable||0)+' / '+esc(totals.current_non_retired_records||0)+'</strong> current records can be reached through the House. '+esc(totals.intentionally_retired_unreachable||0)+' retired FBI records remain intentionally outside the current collection.</p>'
        +'<div class="house-corpus-grid">'+rows.map(row=>{
          const landing=String(row.landing_href||'');
          const href=landing?(/^(https?:|#)/.test(landing)?landing:base+landing.replace(/^\//,'')):'#';
          return '<a class="house-corpus-card" href="'+esc(href)+'">'
            +'<small>'+esc(String(row.record_count||0))+' records</small>'
            +'<strong>'+esc(row.title||row.id)+'</strong>'
            +'<span>'+esc(row.summary||'')+'</span>'
            +'<em>'+esc((row.room_ids||[]).slice(0,4).join(' · '))+'</em>'
            +'</a>';
        }).join('')+'</div>';
      if(holdings) holdings.insertAdjacentElement('afterend',section);
      else main.appendChild(section);
    }catch(e){}
  }


  async function installDwellingArchiveIndex(){
    const match=location.pathname.match(/\/rooms\/([^/]+)\/(?:index\.html)?$/);
    if(!match)return;
    const dwellingId=decodeURIComponent(match[1]);
    try{
      const [subData,drawerData]=await Promise.all([
        getJson('data/house/subrooms.json'),
        getJson('data/house/room-archive-drawers.json')
      ]);
      const roomIds=new Set((subData.subrooms||[]).filter(r=>r.parent_room_id===dwellingId).map(r=>r.id));
      const rows=(drawerData.drawers||[]).filter(d=>(d.room_ids||[]).some(id=>roomIds.has(id)));
      if(!rows.length)return;
      const main=document.querySelector('main');
      if(!main||main.querySelector('.dwelling-archive-index'))return;
      const total=rows.reduce((n,row)=>n+(Number(row.record_count)||0),0);
      const section=document.createElement('section');
      section.className='dwelling-archive-index';
      section.innerHTML='<div class="dwelling-archive-index-head"><div><p class="eyebrow">More to explore in this Dwelling</p><h2>'+esc(rows.length)+' collections · '+esc(total)+' records</h2></div><p>The featured shelf gives you the easiest starting points. These larger collections reveal the research and source material behind the inner Rooms.</p></div>'
        +'<div class="dwelling-archive-index-grid">'+rows.map(row=>{
          const landing=String(row.landing_href||'');
          const href=landing?(/^(https?:|#)/.test(landing)?landing:base+landing.replace(/^\//,'')):'#';
          return '<a class="dwelling-archive-index-card" href="'+esc(href)+'"><small>'+esc(String(row.record_count||0))+' records</small><strong>'+esc(row.title||row.id)+'</strong><span>'+esc(row.summary||'')+'</span></a>';
        }).join('')+'</div>';
      const shelf=main.querySelector('.dwelling-object-shelf');
      if(shelf) shelf.insertAdjacentElement('afterend',section);
      else {
        const reader=main.querySelector('.dwelling-reader');
        if(reader) reader.insertAdjacentElement('afterend',section);
        else main.appendChild(section);
      }
    }catch(e){}
  }

  // Journey history is stored for Elevator replay, but no longer rendered as a
  // persistent site-wide navigation ribbon. The page sub-header owns discovery;
  // the global access dock owns utilities.
  //
  // Keep authored reading and its section guide on the critical path. Nested-Room
  // archive enrichment lives below that content, so hydrate it during idle time
  // instead of competing with first paint, font/layout work and the universal shell.
  installRoomSectionGuide();
  installHouseDeepCorpusIndex();
  installRoomsBestOf();
  installDwellingFeaturedObjects();
  installDwellingArchiveIndex();
  installRoomFloorProjection();

  const isNestedRoom=/\/rooms\/inside\/[^/]+\//.test(location.pathname);
  if(isNestedRoom){
    const hydrateNested=()=>{
      installRoomArchiveDrawers();
      annotateAdjacentRoomDoors();
      installInhabitants();
      installRoomKnowledge();
    };
    if('requestIdleCallback' in window)requestIdleCallback(hydrateNested,{timeout:900});
    else setTimeout(hydrateNested,80);
  }
})();