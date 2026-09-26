(function(root){
  'use strict';

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

  function resolveSpatialContext(route,projection,roomContract){
    const normalized=normalizeRoute(route);
    const rooms=roomRows(roomContract);
    const roomById=Object.fromEntries(rooms.map(room=>[room.id,room]));
    const dwellings=dwellingRows(projection);
    const dwellingById=Object.fromEntries(dwellings.map(row=>[row.id,row]));

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
      .map(dwelling=>({
        ...roomById[dwelling.id],
        homepage:dwelling.homepage||('/rooms/'+dwelling.id+'/'),
        primaryLevel:dwelling.primary_level||'plane',
        projections:[...dwelling.projections]
      }));
  }

  function stepLevel(levelId,direction){
    const current=LEVELS.indexOf(levelId);
    const index=current<0?1:current;
    const delta=direction==='up'?-1:direction==='down'?1:0;
    return LEVELS[Math.max(0,Math.min(LEVELS.length-1,index+delta))];
  }

  const api={LEVELS,normalizeRoute,resolveSpatialContext,roomsForLevel,stepLevel};
  if(typeof exports==='object'){
    exports.LEVELS=LEVELS;
    exports.normalizeRoute=normalizeRoute;
    exports.resolveSpatialContext=resolveSpatialContext;
    exports.roomsForLevel=roomsForLevel;
    exports.stepLevel=stepLevel;
  }else{
    root.SiteElevator=api;
  }
})(typeof globalThis!=='undefined'?globalThis:this);
