/* Dedicated Elevator runtime. The query floor is applied before data hydration so
   Heaven/Plane/Below atmosphere matches the requested stop as early as possible. */
{
  const requested=new URLSearchParams(location.search).get('level');
  if(['heaven','plane','below'].includes(requested)){
    document.documentElement.dataset.siteFloor=requested;
    if(document.body)document.body.dataset.elevatorLevel=requested;
  }
}
(async()=>{
const root=(p)=>'..'+p;
const rot=document.getElementById('rotunda'),lc=document.getElementById('levelControls'),sign=document.getElementById('levelSign'),portals=document.getElementById('levelPortals'),copy=document.getElementById('localCopy'),textGrid=document.getElementById('textGrid'),crumbs=document.getElementById('depthCrumbs'),innerBadge=document.getElementById('innerBadge'),journeyTrack=document.getElementById('journeyTrack'),journeyDetail=document.getElementById('journeyDetail'),objectTable=document.getElementById('objectTable'),axisCar=document.getElementById('axisCar'),centerBtn=document.getElementById('centerBtn'),rotateLeft=document.getElementById('rotateLeft'),rotateRight=document.getElementById('rotateRight'),journeyBack=document.getElementById('journeyBack'),journeyReplay=document.getElementById('journeyReplay'),journeyClear=document.getElementById('journeyClear'),journeyCount=document.getElementById('journeyCount'),consoleTitle=document.getElementById('consoleTitle'),consoleHint=document.getElementById('consoleHint');

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

let coreLoad;
try{
 coreLoad=await loadJson('../data/house/elevator-spatial-projection.json',null,true);
}catch(error){
 copy.innerHTML='<b>Spatial orientation unavailable</b><span>The core House projection could not be loaded. The readable site is still available through these direct routes.</span>';
 textGrid.innerHTML='<a href="../rooms/"><strong>All Rooms</strong><small>Open the canonical Room directory</small></a><a href="../house/"><strong>House</strong><small>Read the architecture</small></a><a href="../"><strong>Home</strong><small>Return to the project entrance</small></a>';
 journeyDetail.textContent='Spatial data is offline; direct readable routes remain available.';
 return;
}

const [subLoad,interiorLoad,inhabitantLoad]=await Promise.all([
 loadJson('../data/house/subrooms.json',{subrooms:[]}),
 loadJson('../data/house/room-interiors.json',{interiors:[]}),
 loadJson('../data/house/room-inhabitants.json',{inhabitants:[]})
]);
const data=coreLoad.value, subData=subLoad.value, interiorData=interiorLoad.value, inhabitantData=inhabitantLoad.value;
const degraded=[];
if(!subLoad.ok)degraded.push('nested Rooms');
if(!interiorLoad.ok)degraded.push('Room routes');
if(!inhabitantLoad.ok)degraded.push('inhabitants');
const params=new URLSearchParams(location.search);
let local=params.get('room')||null, inner=params.get('inner')||null, objectId=params.get('object')||null, yaw=0;
const initialInner=inner?(subData.subrooms||[]).find(row=>row&&row.id===inner):null;
if(initialInner)local=initialInner.parent_room_id;
else if(inner){inner=null;objectId=null}
const initialDwelling=local?(data.dwellings||[]).find(row=>row&&row.id===local):null;
if(local&&!initialDwelling){local=null;inner=null;objectId=null}
const validLevelIds=new Set((data.levels||[]).map(row=>row.id));
let level=initialDwelling?.primary_level||params.get('level')||'plane';
if(!validLevelIds.has(level))level=initialDwelling?.primary_level||'plane';
const JOURNEY_KEY='potato-house-journey-v1';
let suppressJourney=false;
function readJourney(){
 try{
   const rows=JSON.parse(localStorage.getItem(JOURNEY_KEY)||'[]');
   return Array.isArray(rows)?rows.map(st=>({...st,level:st?.level==='world'?'plane':st?.level})).filter(Boolean):[];
 }catch(e){return []}
}
let journey=readJourney();
function labelForState(st){
 if(st.object&&inhabitantById[st.object])return inhabitantById[st.object].label;
 if(st.inner&&subById[st.inner])return subById[st.inner].title;
 if(st.room&&roomById[st.room])return roomById[st.room].label;
 const L=data.levels.find(x=>x.id===st.level);return (L?.label||'Door / Axis');
}
function currentState(type='space'){return {level,room:local,inner,object:objectId,label:labelForState({level,room:local,inner,object:objectId}),type}}
function transitionMeta(prev,next){
  if(!prev)return {via:'start',reason:'You began at this remembered center.'};
  if(next.type==='read')return {via:'read',reason:'You opened a readable public surface from the current spatial center.'};
  if(next.type==='portal')return {via:'portal',reason:'You left the rotunda through a plane landmark rather than a Room door.'};
  if(prev.object&&!next.object)return {via:'return',reason:'You removed the inhabitant from the center table and returned attention to the containing Room.'};
  if(next.object&&next.object!==prev.object)return {via:'object-focus',reason:'You placed an inhabitant on the center table while keeping its Room as the architectural context.'};
  if((prev.level||'plane')!==(next.level||'plane')&&!next.room&&!next.inner)return {via:'elevator',reason:'You changed vertical projection along the same global Axis.'};
  if(next.inner){
    const N=subById[next.inner], P=prev.inner?subById[prev.inner]:null;
    if(P&&N&&P.parent_room_id!==N.parent_room_id){
      const fromFloor=roomById[P.parent_room_id]?.primary_level||prev.level;
      const toFloor=roomById[N.parent_room_id]?.primary_level||next.level;
      return fromFloor===toFloor
        ?{via:'wormhole-door',reason:'A registered cross-Dwelling adjacency connected two Rooms on the same floor.'}
        :{via:'wormhole-elevator',reason:'A registered cross-Dwelling adjacency crossed floors and moved the elevator to the destination Room.'};
    }
    return {via:'local-door',reason:'You moved into a nested Room within the active local context.'};
  }
  if(next.room){
    if(prev.inner||prev.room)return {via:'dwelling-door',reason:'You recentered the House on a canonical Dwelling.'};
    return {via:'dwelling-door',reason:'You entered a canonical Dwelling from the Door / Axis.'};
  }
  return {via:'return',reason:'You moved outward toward the parent context or global Door / Axis.'};
}
function viaLabel(v){return ({start:'start','dwelling-door':'dwelling door','local-door':'local door','wormhole-door':'wormhole','wormhole-elevator':'wormhole + elevator','elevator':'elevator','portal':'portal','read':'read exit','object-focus':'object focus','return':'return'})[v]||v||'step';}
function sameState(a,b){return a&&b&&a.level===b.level&&(a.room||null)===(b.room||null)&&(a.inner||null)===(b.inner||null)&&(a.object||null)===(b.object||null)&&a.type===b.type}
function saveJourney(){try{localStorage.setItem(JOURNEY_KEY,JSON.stringify(journey.slice(-48)))}catch(e){}}
function recordJourney(type='space',labelOverride=null){
 if(suppressJourney)return;
 const st=currentState(type);if(labelOverride)st.label=labelOverride;
 const last=journey[journey.length-1];
 const meta=transitionMeta(last,st);st.via=meta.via;st.reason=meta.reason;
 if(!sameState(last,st)||last?.label!==st.label){journey.push(st);journey=journey.slice(-48);saveJourney();}
}
function restoreJourney(st){
 suppressJourney=true;
 local=st.room||null;inner=st.inner||null;objectId=st.object||null;
 const S=inner?subById[inner]:null;if(S)local=S.parent_room_id;
 const R=local?roomById[local]:null;
 if(local&&!R){local=null;inner=null;objectId=null}
 level=R?.primary_level||(validLevelIds.has(st.level)?st.level:'plane');
 yaw=0;render();suppressJourney=false
}
function renderJourney(){
 journeyTrack.innerHTML='';
 const cur=currentState('space');
 journey.forEach((st,i)=>{
   const wrap=document.createElement('span');wrap.className='journey-bead'+(sameState(st,cur)?' current':'')+(st.type==='read'?' read':'');
   const b=document.createElement('button');b.type='button';
   b.innerHTML='<span>'+String(st.label||labelForState(st)).replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]))+'</span><small>'+viaLabel(st.via)+'</small>';
   b.title=st.reason||'Return to this spatial center';
   b.onclick=()=>{restoreJourney(st);journeyDetail.innerHTML='<b>'+viaLabel(st.via)+'</b> · '+(st.reason||'Recorded journey step.')};
   wrap.appendChild(b);journeyTrack.appendChild(wrap)
 });
 journeyTrack.scrollLeft=journeyTrack.scrollWidth;
 const last=journey[journey.length-1];
 journeyDetail.innerHTML=last?'<b>'+viaLabel(last.via)+'</b> · '+(last.reason||'Recorded journey step.'):'Your path will explain itself as you move.';
}
const roomById=Object.fromEntries(data.dwellings.map(x=>[x.id,x]));
const subById=Object.fromEntries(subData.subrooms.map(x=>[x.id,x]));
const interiorBySubroom=Object.fromEntries((interiorData.interiors||[]).map(x=>[x.subroom_id,x]));
const inhabitantById=Object.fromEntries((inhabitantData.inhabitants||[]).map(x=>[x.id,x]));
function routeFor(r){return root(r)}
function subPublicRoute(S){const I=interiorBySubroom[S.id];return root(I?.route||('/rooms/inside/'+S.id+'/'))}
function writeUrl(){const q=new URLSearchParams();if(local)q.set('room',local);if(inner)q.set('inner',inner);if(objectId)q.set('object',objectId);if(level!=='plane')q.set('level',level);history.replaceState(null,'',location.pathname+(q.toString()?'?'+q:''))}
function renderLevels(){
 lc.innerHTML='';
 data.levels.forEach(L=>{
   const b=document.createElement('button');
   b.type='button';
   b.textContent=L.label.replace(/\s*\/.*$/,'');
   b.dataset.level=L.id;
   b.setAttribute('aria-pressed',String(L.id===level));
   b.setAttribute('aria-label','Go to '+L.label);
   b.onclick=()=>{
     if(L.id===level&&!local&&!inner&&!objectId)return;
     stopReplay();level=L.id;local=null;inner=null;objectId=null;yaw=0;render();recordJourney();renderJourney();
   };
   lc.appendChild(b);
 });
}
function visibleItems(){
 if(inner){
   const S=subById[inner]; if(!S)return [];
   const ids=[S.id,...(S.adjacent_subroom_ids||[])];
   return ids.map(id=>subById[id]).filter(Boolean).map(x=>({kind:'inner',id:x.id,label:x.title,subtitle:x.local_role||'nested room',homepage:subPublicRoute(x),obj:x}));
 }
 if(local){
   const R=roomById[local]; if(!R)return [];
   const children=subData.subrooms.filter(s=>s.parent_room_id===local);
   const primary={kind:'dwelling',id:R.id,label:R.label,subtitle:R.local_center_label,homepage:root(R.homepage),obj:R};
   const childItems=children.map(x=>({kind:'inner',id:x.id,label:x.title,subtitle:x.local_role||'nested room',homepage:subPublicRoute(x),obj:x}));
   return [primary,...childItems];
 }
 return data.dwellings.filter(r=>(r.primary_level||'plane')===level).map(R=>({kind:'dwelling',id:R.id,label:R.label,subtitle:R.local_center_label,homepage:root(R.homepage),obj:R}));
}
function setLocal(item){stopReplay();objectId=null;
 if(item.kind==='dwelling'){
   local=item.id;inner=null;level=item.obj.primary_level||level;
 }else{
   local=item.obj.parent_room_id;inner=item.id;
   const destination=roomById[local];
   if(destination?.primary_level)level=destination.primary_level;
 }
 yaw=0;render();recordJourney();renderJourney();
}
function renderDoors(){
 rot.innerHTML=''; const items=visibleItems(); const n=Math.max(items.length,1);
 items.forEach((I,i)=>{
   const selected=(I.kind==='inner'&&inner===I.id)||(I.kind==='dwelling'&&!inner&&local===I.id);
   const activeParent=inner?(subById[inner]?.parent_room_id):local;
   const wormhole=I.kind==='inner'&&activeParent&&I.obj.parent_room_id!==activeParent;
   const d=document.createElement('div');d.className='door'+(selected?' is-local':'')+(I.kind==='inner'?' is-inner':'')+(wormhole?' is-wormhole':'');d.dataset.id=I.id;
   d.style.setProperty('--angle',((360/n)*i)+'deg');
   const a=document.createElement('a');a.href=I.homepage;
   a.innerHTML='<small>'+ (selected?'LOCAL CENTER':wormhole?'WORMHOLE DOOR':I.kind==='inner'?'INNER ROOM':'DWELLING') +'</small><strong>'+I.label+'</strong><span>'+I.subtitle+'</span>';
   a.addEventListener('mouseenter',()=>{copy.innerHTML='<b>'+I.label+'</b><span>'+I.subtitle+' · open the readable room, or center the spatial view here.</span>'});
   a.addEventListener('mouseleave',renderLocalCopy);
   a.addEventListener('click',()=>{recordJourney('read','Read: '+I.label);renderJourney()});
   d.appendChild(a);
   const hit=document.createElement('button');
   hit.type='button';
   hit.className='door-center';
   hit.textContent=selected?'current center':'center here';
   hit.title=selected?I.label+' is already the local center':'Make '+I.label+' the local center';
   hit.disabled=selected;
   hit.onclick=e=>{e.preventDefault();setLocal(I)};
   d.appendChild(hit);
   rot.appendChild(d);
 });
 rot.style.transform='rotateY('+yaw+'deg)';
}
function renderObject(){
 const O=objectId?inhabitantById[objectId]:null;
 if(!O){objectTable.classList.remove('active');objectTable.innerHTML='';axisCar.classList.remove('object-hidden');return;}
 if(!inner||!(O.room_ids||[]).includes(inner)){objectId=null;objectTable.classList.remove('active');axisCar.classList.remove('object-hidden');return;}
 const activeRoom=subById[inner];
 const other=(O.room_ids||[]).filter(id=>id!==inner&&subById[id]);
 const lensButtons=other.map(id=>'<button type="button" data-object-lens="'+id+'">'+subById[id].title+'</button>').join('');
 const related=(inhabitantData.inhabitants||[]).filter(x=>x.id!==O.id&&(x.room_ids||[]).includes(inner)).slice(0,6);
 const relatedButtons=related.map(x=>'<button type="button" data-related-object="'+x.id+'">'+x.label+'<br><small>'+String(x.kind||'object')+'</small></button>').join('');
 const facetEntries=Object.entries(O.facets||{}).filter(([k,v])=>v&&(Array.isArray(v)?v.length:Object.keys(v||{}).length));
 const facetTabs=facetEntries.map(([k])=>'<button type="button" data-facet="'+k+'">'+k.replace(/_/g,' ')+'</button>').join('');
 objectTable.classList.add('active');axisCar.classList.add('object-hidden');
 objectTable.innerHTML='<p class="eyebrow">Center table · '+String(O.kind||'object')+'</p><h2>'+O.label+'</h2><p><strong>Active Room:</strong> '+activeRoom.title+'</p>'+(O.summary?'<p>'+O.summary+'</p>':'<p>This object is being inspected through the active Room lens. It remains an inhabitant, not a Room or global center.</p>')+'<div class="object-meta"><span>'+String(O.kind||'object')+'</span><span>'+((O.room_ids||[]).length)+' room lens'+((O.room_ids||[]).length===1?'':'es')+'</span></div>'+(O.status_note?'<p><strong>Status boundary:</strong> '+O.status_note+'</p>':'')+(O.evidence_note?'<p><strong>Evidence rule:</strong> '+O.evidence_note+'</p>':'')+(lensButtons?'<p><strong>Other Room lenses</strong></p><div class="object-lenses">'+lensButtons+'</div>':'')+(relatedButtons?'<p><strong>Other inhabitants in this Room</strong></p><div class="object-related">'+relatedButtons+'</div>':'')+(facetTabs?'<div class="object-facets"><p><strong>Inspect facets</strong></p><div class="object-facet-tabs">'+facetTabs+'</div><div class="object-facet-body" id="objectFacetBody"><p>Select a facet to inspect.</p></div></div>':'')+'<div class="object-actions"><a href="'+root(O.route)+'" id="objectRead">Open readable dossier →</a><button type="button" id="objectClose">Return to Room</button></div>';
 objectTable.querySelector('#objectClose').onclick=()=>{objectId=null;render();recordJourney();renderJourney()};
 const read=objectTable.querySelector('#objectRead');if(read)read.addEventListener('click',()=>{recordJourney('read','Read: '+O.label);renderJourney()});
 objectTable.querySelectorAll('[data-object-lens]').forEach(b=>b.onclick=()=>{const id=b.dataset.objectLens;const S=subById[id];if(!S)return;inner=id;local=S.parent_room_id;const destination=roomById[local];if(destination?.primary_level)level=destination.primary_level;objectId=O.id;yaw=0;render();recordJourney('space',O.label+' in '+S.title);renderJourney()});
 objectTable.querySelectorAll('[data-related-object]').forEach(b=>b.onclick=()=>{const id=b.dataset.relatedObject;if(!inhabitantById[id])return;objectId=id;render();recordJourney('space',inhabitantById[id].label);renderJourney()});
 const facetBody=objectTable.querySelector('#objectFacetBody');
 function facetHtml(v){
   if(Array.isArray(v))return '<ul>'+v.map(x=>'<li>'+facetHtml(x)+'</li>').join('')+'</ul>';
   if(v&&typeof v==='object')return Object.entries(v).map(([k,val])=>'<div><b>'+k.replace(/_/g,' ')+'</b>: '+(typeof val==='object'?facetHtml(val):String(val))+'</div>').join('');
   return String(v??'');
 }
 objectTable.querySelectorAll('[data-facet]').forEach(b=>b.onclick=()=>{objectTable.querySelectorAll('[data-facet]').forEach(x=>x.classList.toggle('active',x===b));if(facetBody)facetBody.innerHTML=facetHtml(O.facets[b.dataset.facet]);});
}
function renderLocalCopy(){
 const L=data.levels.find(x=>x.id===level)||data.levels[1];
 if(inner){
   const S=subById[inner];
   copy.innerHTML='<b>'+S.title+'</b><span>'+S.purpose+' This nested Room is locally central; registered adjacent Rooms surround it.</span>';
 }else if(local){
   const R=roomById[local];
   copy.innerHTML='<b>'+R.label+'</b><span>'+R.local_center_label+' · this Dwelling is locally central. Its nested Rooms now surround it.</span>';
 }else{
   copy.innerHTML='<b>Door / Axis</b><span>You are at the global center on '+L.label+'. Choose a Dwelling to enter its local interior.</span>';
 }
}
function renderSign(){
 const L=data.levels.find(x=>x.id===level)||data.levels[1];
 document.documentElement.dataset.siteFloor=level;
 document.body.dataset.elevatorLevel=level;
 sign.innerHTML='<b>'+L.label+'</b><span>'+L.description+'</span>';
 if(consoleTitle)consoleTitle.textContent=L.label;
 if(consoleHint)consoleHint.textContent=local||inner?'The floor follows the active Dwelling. Return to Axis to choose another floor.':'Choose a floor, then choose a Dwelling. Reading links open the full page; Center Here keeps you in the spatial viewer.';
 portals.innerHTML=(!local&&!inner?(L.landmarks||[]):[]).map(x=>'<a href="'+routeFor(x.route)+'" data-portal-label="'+x.label.replace(/\"/g,'&quot;')+'">'+x.label+'</a>').join('');
 portals.querySelectorAll('a[data-portal-label]').forEach(a=>a.addEventListener('click',()=>{recordJourney('portal','Portal: '+a.dataset.portalLabel);renderJourney()}));
 if(inner){
   const S=subById[inner],P=roomById[S?.parent_room_id];innerBadge.hidden=false;innerBadge.textContent='inside '+(P?.label||'Dwelling')+' · nested room';
 }else if(local){
   const R=roomById[local];innerBadge.hidden=false;innerBadge.textContent='inside '+R.label;
 }else{
   innerBadge.hidden=true;
 }
 renderLocalCopy();
}
function renderCrumbs(){
 crumbs.innerHTML='';
 const make=(label,fn,current=false)=>{const b=document.createElement('button');b.type='button';b.textContent=label;b.disabled=current;b.onclick=fn;crumbs.appendChild(b)};
 make('Door / Axis',()=>{local=null;inner=null;yaw=0;render();recordJourney();renderJourney()},!local&&!inner);
 if(local){const R=roomById[local];make(R.label,()=>{inner=null;yaw=0;render();recordJourney();renderJourney()},!!local&&!inner)}
 if(inner){const S=subById[inner];make(S.title,()=>{objectId=null;render();recordJourney();renderJourney()},!objectId)}
 if(objectId&&inhabitantById[objectId]){make(inhabitantById[objectId].label,()=>{},true)}
}
function renderText(){
 textGrid.innerHTML='';
 if(inner){
   const S=subById[inner];const ids=[S.id,...(S.adjacent_subroom_ids||[])];
   ids.map(id=>subById[id]).filter(Boolean).forEach(x=>{const a=document.createElement('a');a.href=subPublicRoute(x);a.innerHTML='<strong>'+x.title+'</strong><small>'+x.local_role+'</small>';textGrid.appendChild(a)});return;
 }
 if(local){
   subData.subrooms.filter(s=>s.parent_room_id===local).forEach(x=>{const a=document.createElement('a');a.href=subPublicRoute(x);a.innerHTML='<strong>'+x.title+'</strong><small>'+x.local_role+'</small>';textGrid.appendChild(a)});return;
 }
 data.dwellings.filter(R=>(R.primary_level||'plane')===level).forEach(R=>{const a=document.createElement('a');a.href=root(R.homepage);a.innerHTML='<strong>'+R.label+'</strong><small>'+R.local_center_label+'</small>';textGrid.appendChild(a)});
}
function renderControlState(){
 const atCenter=!objectId&&!inner&&!local;
 centerBtn.disabled=atCenter;
 centerBtn.textContent=objectId?'Return to Room':inner?'Back to Dwelling':local?'Return to Axis':'At Door / Axis';
 const canRotate=visibleItems().length>1;
 rotateLeft.disabled=!canRotate;
 rotateRight.disabled=!canRotate;
 journeyBack.disabled=journey.length<2;
 journeyReplay.disabled=journey.length<2;
 journeyClear.disabled=journey.length<=1;
 if(journeyCount)journeyCount.textContent=journey.length+' step'+(journey.length===1?'':'s');
}
function render(){
 renderLevels();renderDoors();renderObject();renderSign();renderCrumbs();renderText();writeUrl();renderJourney();renderControlState();
 if(degraded.length)journeyDetail.innerHTML='<b>Reduced detail</b> · Core floor/Room navigation is available; unavailable optional data: '+degraded.join(', ')+'.';
}
centerBtn.onclick=()=>{
 stopReplay();
 if(objectId)objectId=null;
 else if(inner)inner=null;
 else if(local)local=null;
 else return;
 yaw=0;render();recordJourney();renderJourney();renderControlState();
};
rotateLeft.onclick=()=>{if(rotateLeft.disabled)return;yaw-=35;rot.style.transform='rotateY('+yaw+'deg)'};
rotateRight.onclick=()=>{if(rotateRight.disabled)return;yaw+=35;rot.style.transform='rotateY('+yaw+'deg)'};
function stepFloor(direction){
 const ids=(data.levels||[]).map(row=>row.id);
 const index=Math.max(0,ids.indexOf(level));
 const delta=direction==='up'?-1:direction==='down'?1:0;
 return ids[Math.max(0,Math.min(ids.length-1,index+delta))]||'plane';
}
function moveFloor(direction){
 const next=stepFloor(direction);if(next===level)return;
 level=next;local=null;inner=null;objectId=null;yaw=0;render();recordJourney();renderJourney();
}
document.addEventListener('keydown',e=>{
 const interactive=e.target.closest?.('button,a,summary,input,select,textarea');
 if(interactive&&e.key!=='Escape')return;
 if(e.key==='ArrowLeft'&&!rotateLeft.disabled){yaw-=35;rot.style.transform='rotateY('+yaw+'deg)'}
 if(e.key==='ArrowRight'&&!rotateRight.disabled){yaw+=35;rot.style.transform='rotateY('+yaw+'deg)'}
 if(e.key==='ArrowUp'){e.preventDefault();moveFloor('up')}
 if(e.key==='ArrowDown'){e.preventDefault();moveFloor('down')}
 if(e.key==='Escape'){
   if(objectId)objectId=null;
   else if(inner)inner=null;
   else if(local)local=null;
   else return;
   yaw=0;render();recordJourney();renderJourney();renderControlState();
 }
});
let replayTimer=null;
function stopReplay(){if(replayTimer){clearInterval(replayTimer);replayTimer=null}journeyReplay.textContent='Replay route';renderControlState()}
function replayJourney(){
 stopReplay(); if(!journey.length)return;
 let i=0; journeyReplay.textContent='Stop replay';journeyReplay.disabled=false;
 const tick=()=>{if(i>=journey.length){stopReplay();return}const st=journey[i++];restoreJourney(st);journeyDetail.innerHTML='<b>Replay '+i+'/'+journey.length+'</b> · '+(st.label||labelForState(st))+' via '+viaLabel(st.via)+'. '+(st.reason||'');};
 tick(); replayTimer=setInterval(tick,1300);
}
journeyReplay.onclick=()=>{replayTimer?stopReplay():replayJourney()};
journeyBack.onclick=()=>{if(journey.length<2)return;journey.pop();saveJourney();const st=journey[journey.length-1];restoreJourney(st);renderJourney();renderControlState()};
journeyClear.onclick=()=>{if(journey.length<=1)return;journey=[];saveJourney();recordJourney();renderJourney();renderControlState()};
window.addEventListener('pagehide',stopReplay,{once:true});
render();recordJourney();renderJourney();renderControlState();
})();