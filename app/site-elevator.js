(function(root){
  'use strict';

  const runtimeScript=(typeof document!=='undefined')?document.currentScript:null;
  const LEVELS=['heaven','plane','below'];

  function normalizeRoute(pathname,siteBasePath='/'){
    let raw=String(pathname||'/');
    try{
      raw=new URL(raw,'https://example.invalid').pathname;
    }catch(_){}
    let base=String(siteBasePath||'/');
    try{
      base=new URL(base,'https://example.invalid').pathname;
    }catch(_){}
    base='/' + base.replace(/^\/+|\/+$/g,'');
    if(base!=='/'&&raw.startsWith(base+'/'))raw=raw.slice(base.length);
    else if(base!=='/'&&raw===base)raw='/';
    raw='/' + raw.replace(/^\/+|\/+$/g,'');
    if(raw==='/index.html')return '/';
    raw=raw.replace(/\/index\.html$/,'/');
    return raw==='/'?'/':raw.replace(/\/+/g,'/')+'/';
  }

  function roomRows(roomContract){
    return (roomContract&&Array.isArray(roomContract.rooms)?roomContract.rooms:[])
      .filter(row=>row&&row.status==='active'&&row.id);
  }

  function dwellingRows(projection){
    return (projection&&Array.isArray(projection.dwellings)?projection.dwellings:[])
      .filter(row=>row&&row.id);
  }

  function resolveSpatialContext(route,projection,roomContract,subroomContract){
    const normalized=normalizeRoute(route);
    const rooms=roomRows(roomContract);
    const roomById=Object.fromEntries(rooms.map(room=>[room.id,room]));
    const dwellings=dwellingRows(projection);
    const dwellingById=Object.fromEntries(dwellings.map(row=>[row.id,row]));

    const subroomMatch=normalized.match(/^\/rooms\/inside\/([^/]+)(?:\/|$)/);
    if(subroomMatch){
      const subrooms=(subroomContract&&Array.isArray(subroomContract.subrooms)?subroomContract.subrooms:[])
        .filter(row=>row&&row.status==='active'&&row.id&&row.parent_room_id);
      const subroom=subrooms.find(row=>row.id===subroomMatch[1]||row.route_id===subroomMatch[1]);
      if(subroom&&roomById[subroom.parent_room_id]&&dwellingById[subroom.parent_room_id]){
        const roomId=subroom.parent_room_id;
        const dwelling=dwellingById[roomId];
        return {
          levelId:dwelling.primary_level||'plane',
          roomId,
          room:{...roomById[roomId],homepage:dwelling.homepage||('/rooms/'+roomId+'/')},
          subroomId:subroom.id,
          subroom,
          source:'subroom-route'
        };
      }
    }

    const roomMatch=normalized.match(/^\/rooms\/([^/]+)(?:\/|$)/);
    if(roomMatch&&roomById[roomMatch[1]]&&dwellingById[roomMatch[1]]){
      const roomId=roomMatch[1];
      const dwelling=dwellingById[roomId];
      return {
        levelId:dwelling.primary_level||'plane',
        roomId,
        room:{...roomById[roomId],homepage:dwelling.homepage||('/rooms/'+roomId+'/')},
        source:'room-route'
      };
    }

    const contexts=(projection&&Array.isArray(projection.route_contexts)?projection.route_contexts:[])
      .filter(row=>row&&typeof row.match==='string'&&row.level_id)
      .filter(row=>row.match==='/'?normalized==='/':normalized===row.match||normalized.startsWith(row.match))
      .sort((a,b)=>b.match.length-a.match.length);

    if(contexts.length){
      const ctx=contexts[0];
      const roomId=ctx.room_id||null;
      const dwelling=roomId?dwellingById[roomId]:null;
      const room=roomId&&roomById[roomId]?{...roomById[roomId],homepage:dwelling?.homepage||('/rooms/'+roomId+'/')}:null;
      return {levelId:ctx.level_id,roomId,room,source:'route-context'};
    }

    return {levelId:'plane',roomId:null,room:null,source:'fallback'};
  }

  function roomsForLevel(levelId,projection,roomContract){
    if(!LEVELS.includes(levelId))return [];
    const rooms=roomRows(roomContract);
    const roomById=Object.fromEntries(rooms.map(room=>[room.id,room]));
    return dwellingRows(projection)
      .filter(dwelling=>Array.isArray(dwelling.projections)&&dwelling.projections.includes(levelId)&&roomById[dwelling.id])
      .map((dwelling,index)=>({
        ...roomById[dwelling.id],
        homepage:dwelling.homepage||('/rooms/'+dwelling.id+'/'),
        primaryLevel:dwelling.primary_level||'plane',
        projections:[...dwelling.projections],
        isPrimaryProjection:(dwelling.primary_level||'plane')===levelId,
        projectionOrder:index
      }))
      .sort((a,b)=>Number(b.isPrimaryProjection)-Number(a.isPrimaryProjection)||a.projectionOrder-b.projectionOrder);
  }

  function stepLevel(levelId,direction){
    const current=LEVELS.indexOf(levelId);
    const index=current<0?1:current;
    const delta=direction==='up'?-1:direction==='down'?1:0;
    return LEVELS[Math.max(0,Math.min(LEVELS.length-1,index+delta))];
  }

  function inheritParentContext(spatial,parentRoute,projection,roomContract,subroomContract){
    if(!spatial||spatial.source!=='fallback'||!parentRoute)return spatial;
    const parent=resolveSpatialContext(parentRoute,projection,roomContract,subroomContract);
    if(!parent||parent.source==='fallback')return spatial;
    return {...parent,source:'parent-route',parentRoute:normalizeRoute(parentRoute)};
  }

  function browserContext(){
    if(typeof document==='undefined'||typeof window==='undefined')return null;
    const script=runtimeScript||document.currentScript;
    try{
      const appBase=new URL('./',script?.src||document.baseURI);
      const siteBase=new URL('../',appBase);
      return {script,appBase,siteBase};
    }catch(_){
      return null;
    }
  }

  function siteHref(route,siteBase){
    try{
      return new URL(String(route||'/').replace(/^\//,''),siteBase).href;
    }catch(_){
      return String(route||'/');
    }
  }

  function levelLabel(levelId,projection){
    const row=(projection?.levels||[]).find(level=>level?.id===levelId);
    return row?.label||({heaven:'Heaven',plane:'Plane',below:'Below'}[levelId]||'Plane');
  }

  function mount(options={}){
    if(typeof document==='undefined'||typeof window==='undefined')return null;
    if(document.querySelector('.site-elevator'))return document.querySelector('.site-elevator');
    const context=browserContext();
    if(!context||!document.body)return null;

    const header=document.createElement('header');
    header.className='site-elevator';
    header.setAttribute('data-elevator-level','pending');
    header.dataset.elevatorReady='false';
    header.setAttribute('aria-busy','true');
    header.setAttribute('data-no-tts','');
    header.setAttribute('aria-label','House elevator');
    header.setAttribute('aria-keyshortcuts','ArrowUp ArrowDown Home');
    header.tabIndex=0;
    header.innerHTML=
      '<div class="site-elevator-main">'+
        '<div class="site-elevator-controls" aria-label="Change House floor">'+
          '<button class="site-elevator-arrow site-elevator-up" type="button" aria-label="Move elevator up" disabled>↑</button>'+
          '<button class="site-elevator-arrow site-elevator-down" type="button" aria-label="Move elevator down" disabled>↓</button>'+
        '</div>'+
        '<div class="site-elevator-reel" aria-label="Current House floor">'+
          '<div class="site-elevator-floor" aria-live="polite">'+
            '<span class="site-elevator-floor-code" aria-hidden="true">--</span>'+
            '<strong class="site-elevator-floor-label">HOUSE</strong>'+
            '<small class="site-elevator-room-label">Finding your Room…</small>'+
          '</div>'+
        '</div>'+
        '<nav class="site-elevator-room-rail" aria-label="Rooms on selected floor" hidden></nav>'+
      '</div>';

    document.body.insertBefore(header,document.body.firstChild);

    const publishClearance=()=>{
      const rect=header.getBoundingClientRect();
      document.documentElement.style.setProperty('--site-elevator-clearance',Math.ceil(rect.height)+'px');
    };
    publishClearance();
    if(typeof ResizeObserver!=='undefined'){
      const elevatorObserver=new ResizeObserver(publishClearance);
      elevatorObserver.observe(header);
    }
    window.addEventListener('resize',publishClearance,{passive:true});

    const up=header.querySelector('.site-elevator-up');
    const down=header.querySelector('.site-elevator-down');
    const floorCode=header.querySelector('.site-elevator-floor-code');
    const floorLabel=header.querySelector('.site-elevator-floor-label');
    const roomLabel=header.querySelector('.site-elevator-room-label');
    const roomRail=header.querySelector('.site-elevator-room-rail');

    let projection=null;
    let roomContract=null;
    let subroomContract=null;
    let spatial={levelId:'plane',roomId:null,room:null,subroomId:null,source:'fallback'};
    let selectedLevel='plane';

    const renderRooms=()=>{
      if(!projection||!roomContract){
        roomRail.hidden=true;
        roomRail.replaceChildren();
        return;
      }
      const rows=roomsForLevel(selectedLevel,projection,roomContract);
      const fragment=document.createDocumentFragment();
      for(const room of rows){
        const link=document.createElement('a');
        link.className='site-elevator-room '+(room.isPrimaryProjection?'is-primary':'is-secondary');
        link.href=siteHref(room.homepage||('/rooms/'+room.id+'/'),context.siteBase);
        link.textContent=room.title||room.id;
        link.dataset.roomId=room.id;
        if(spatial.roomId===room.id&&selectedLevel===spatial.levelId){
          link.setAttribute('aria-current','location');
          link.classList.add('is-active');
        }
        fragment.appendChild(link);
      }
      roomRail.replaceChildren(fragment);
      roomRail.hidden=!rows.length;
    };

    const render=(direction='')=>{
      header.setAttribute('data-elevator-level',selectedLevel);
      delete header.dataset.elevatorDirection;
      if(direction==='up'||direction==='down'){
        void header.offsetWidth;
        header.dataset.elevatorDirection=direction;
      }
      floorCode.textContent=({heaven:'03',plane:'02',below:'01'}[selectedLevel]||'02');
      floorLabel.textContent=levelLabel(selectedLevel,projection).replace(/\s*\/.*$/,'').toUpperCase();
      const currentRoom=spatial.room;
      roomLabel.textContent=currentRoom&&selectedLevel===spatial.levelId
        ?'HERE'
        :(selectedLevel===spatial.levelId?'HOUSE ORIENTATION':'BROWSING FLOOR');
      up.disabled=selectedLevel==='heaven'||!projection;
      down.disabled=selectedLevel==='below'||!projection;
      renderRooms();
      if(typeof requestAnimationFrame==='function')requestAnimationFrame(publishClearance);
      else publishClearance();
    };

    const move=direction=>{
      if(!projection)return;
      const next=stepLevel(selectedLevel,direction);
      if(next===selectedLevel)return;
      selectedLevel=next;
      render(direction);
    };

    up.addEventListener('click',()=>move('up'));
    down.addEventListener('click',()=>move('down'));
    header.addEventListener('keydown',event=>{
      if(event.target!==header)return;
      if(event.key==='ArrowUp'){
        event.preventDefault();
        move('up');
      }else if(event.key==='ArrowDown'){
        event.preventDefault();
        move('down');
      }else if(event.key==='Home'){
        event.preventDefault();
        selectedLevel='plane';
        render('home');
      }
    });

    render();

    const assetVersion=(()=>{
      try{return new URL(context.script?.src||document.baseURI).searchParams.get('v')||'unversioned';}
      catch(_){return 'unversioned';}
    })();
    const fetchJson=async route=>{
      const href=siteHref(route,context.siteBase);
      const key='site-elevator:'+assetVersion+':'+route;
      try{
        const cached=sessionStorage.getItem(key);
        if(cached)return JSON.parse(cached);
      }catch(_){}
      const response=await fetch(href,{cache:'no-cache'});
      if(!response.ok)throw new Error('Elevator data request failed: '+route+' '+response.status);
      const value=await response.json();
      try{sessionStorage.setItem(key,JSON.stringify(value));}catch(_){}
      return value;
    };

    Promise.all([
      fetchJson('/data/house/elevator-spatial-projection.json'),
      fetchJson('/data/house/rooms.json'),
      fetchJson('/data/house/subrooms.json')
    ]).then(([nextProjection,nextRooms,nextSubrooms])=>{
      projection=nextProjection;
      roomContract=nextRooms;
      subroomContract=nextSubrooms;
      const siteBasePath=new URL(context.siteBase).pathname;
      const currentRoute=normalizeRoute(location.pathname,siteBasePath);
      spatial=resolveSpatialContext(currentRoute,projection,roomContract,subroomContract);
      if(spatial.source==='fallback'){
        const parentLink=document.querySelector('nav[aria-label="Parent"] a[href]');
        if(parentLink){
          try{
            const parentRoute=normalizeRoute(new URL(parentLink.href,document.baseURI).pathname,siteBasePath);
            spatial=inheritParentContext(spatial,parentRoute,projection,roomContract,subroomContract);
          }catch(_){}
        }
      }
      selectedLevel=LEVELS.includes(spatial.levelId)?spatial.levelId:'plane';
      if(spatial.roomId)header.dataset.elevatorRoom=spatial.roomId;
      else delete header.dataset.elevatorRoom;
      header.dataset.elevatorReady='true';
      header.setAttribute('aria-busy','false');
      render('hydrate');
    }).catch(()=>{
      header.dataset.elevatorReady='error';
      header.setAttribute('aria-busy','false');
      selectedLevel='plane';
      render('error');
      roomLabel.textContent='ORIENTATION OFFLINE';
    });

    return header;
  }

  const api={LEVELS,normalizeRoute,resolveSpatialContext,roomsForLevel,stepLevel,inheritParentContext,mount};
  if(typeof exports==='object'){
    exports.LEVELS=LEVELS;
    exports.normalizeRoute=normalizeRoute;
    exports.resolveSpatialContext=resolveSpatialContext;
    exports.roomsForLevel=roomsForLevel;
    exports.stepLevel=stepLevel;
    exports.inheritParentContext=inheritParentContext;
    exports.mount=mount;
  }else{
    root.SiteElevator=api;
    if(typeof document!=='undefined'){
      if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>mount(),{once:true});
      else mount();
    }
  }
})(typeof globalThis!=='undefined'?globalThis:this);
