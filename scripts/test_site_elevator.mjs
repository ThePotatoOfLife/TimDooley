#!/usr/bin/env node
import assert from 'node:assert/strict';

let elevator;
try{
  elevator=await import('../app/site-elevator.js');
}catch(error){
  console.error('Expected RED: app/site-elevator.js does not exist yet');
  throw error;
}

const projection=(await import('../data/house/elevator-spatial-projection.json',{with:{type:'json'}})).default;
const roomContract=(await import('../data/house/rooms.json',{with:{type:'json'}})).default;
const subroomContract=(await import('../data/house/subrooms.json',{with:{type:'json'}})).default;

const cases=[
  ['/', 'plane', 'potatoverse-canon'],
  ['/tim-dooley/', 'plane', 'potatoverse-canon'],
  ['/potato-of-life/', 'heaven', 'potatoverse-canon'],
  ['/religion/', 'heaven', 'traditions-texts'],
  ['/science/', 'plane', 'science-formal-models'],
  ['/politics/', 'plane', 'world-systems'],
  ['/context/culture/', 'plane', 'culture-information'],
  ['/shadow-farm/', 'below', 'culture-information'],
  ['/context/source-authority/', 'below', 'archive-sources'],
  ['/research-lab/', 'below', 'research-lab'],
  ['/works/', 'heaven', 'works'],
  ['/timeline/', 'plane', 'time-history'],
  ['/below/', 'below', null],
  ['/philosophy/', 'heaven', 'potatoverse-canon'],
  ['/philosophy/interpretive-justice.html', 'heaven', 'potatoverse-canon'],
  ['/world/', 'plane', 'world-systems'],
  ['/news/', 'plane', 'world-systems'],
  ['/world-map/', 'plane', 'world-systems'],
  ['/world-systems/', 'plane', 'world-systems'],
  ['/context/', 'below', 'archive-sources'],
  ['/corporium/', 'plane', 'potatoverse-canon'],
  ['/axis/', 'heaven', 'potatoverse-canon'],
  ['/north/', 'heaven', null],
  ['/traditions/bible/', 'heaven', 'traditions-texts'],
  ['/history/', 'plane', 'time-history'],
  ['/law/', 'plane', 'world-systems'],
  ['/life-body/', 'plane', 'life-body'],
  ['/explore/', 'plane', null],
  ['/questions/', 'plane', null],
  ['/index-a-z/', 'plane', null],
  ['/house/', 'plane', null],
  ['/rooms/', 'plane', null],
  ['/rooms/objects/', 'plane', null],
  ['/paths/', 'plane', null],
  ['/elevator/', 'plane', null],
];

for(const [route,levelId,roomId] of cases){
  const ctx=elevator.resolveSpatialContext(route,projection,roomContract);
  assert.equal(ctx.levelId,levelId,route+' level');
  assert.equal(ctx.roomId,roomId,route+' room');
}

const direct=elevator.resolveSpatialContext('/rooms/culture-information/deeper/topic/',projection,roomContract);
assert.equal(direct.levelId,'plane');
assert.equal(direct.roomId,'culture-information');
assert.equal(direct.source,'room-route');

// all direct Room routes must resolve to each Room's primary floor
for(const dwelling of projection.dwellings){
  const ctx=elevator.resolveSpatialContext('/rooms/'+dwelling.id+'/',projection,roomContract);
  assert.equal(ctx.roomId,dwelling.id, dwelling.id+' direct Room route');
  assert.equal(ctx.levelId,dwelling.primary_level, dwelling.id+' must open on its primary floor');
  assert.equal(ctx.source,'room-route', dwelling.id+' must resolve through direct Room ownership');
}

// nested Room inheritance contract
const primaryByRoom=Object.fromEntries(projection.dwellings.map(row=>[row.id,row.primary_level]));
for(const subroom of subroomContract.subrooms.filter(row=>row.status==='active')){
  const ctx=elevator.resolveSpatialContext('/rooms/inside/'+subroom.id+'/',projection,roomContract,subroomContract);
  assert.equal(ctx.roomId,subroom.parent_room_id, subroom.id+' must light its parent Room');
  assert.equal(ctx.levelId,primaryByRoom[subroom.parent_room_id], subroom.id+' must inherit the parent Room primary floor');
  assert.equal(ctx.source,'subroom-route', subroom.id+' must resolve through nested Room ownership');
  assert.equal(ctx.subroomId,subroom.id, subroom.id+' must preserve nested Room identity');
}

const unknown=elevator.resolveSpatialContext('/totally-unknown/',projection,roomContract,subroomContract);
assert.equal(unknown.levelId,'plane');
assert.equal(unknown.roomId,null);

const archiveRecord=elevator.resolveSpatialContext('/records/archive-epistemics/',projection,roomContract,subroomContract);
const archiveInherited=elevator.inheritParentContext(
  archiveRecord,
  '/context/source-authority/',
  projection,
  roomContract,
  subroomContract
);
assert.equal(archiveInherited.levelId,'below');
assert.equal(archiveInherited.roomId,'archive-sources');
assert.equal(archiveInherited.source,'parent-route');
assert.equal(archiveInherited.parentRoute,'/context/source-authority/');

const scienceKnown=elevator.resolveSpatialContext('/science/',projection,roomContract,subroomContract);
assert.equal(
  elevator.inheritParentContext(scienceKnown,'/religion/',projection,roomContract,subroomContract),
  scienceKnown,
  'known route context must not be overridden by a Parent link'
);

assert.equal(elevator.stepLevel('heaven','up'),'heaven');
assert.equal(elevator.stepLevel('heaven','down'),'plane');
assert.equal(elevator.stepLevel('plane','up'),'heaven');
assert.equal(elevator.stepLevel('plane','down'),'below');
assert.equal(elevator.stepLevel('below','down'),'below');

const cultureBelow=elevator.roomsForLevel('below',projection,roomContract).map(room=>room.id);
assert.ok(cultureBelow.includes('culture-information'));
const cultureHeaven=elevator.roomsForLevel('heaven',projection,roomContract).map(room=>room.id);
assert.equal(cultureHeaven.includes('culture-information'),false);

// primary Room ordering contract
const planeRooms=elevator.roomsForLevel('plane',projection,roomContract);
const firstSecondaryIndex=planeRooms.findIndex(room=>room.primaryLevel!=='plane');
assert.ok(firstSecondaryIndex>0,'Plane must expose at least one primary Room before secondary projections');
assert.ok(planeRooms.slice(0,firstSecondaryIndex).every(room=>room.primaryLevel==='plane'),'primary Plane Rooms must lead the rail');
assert.ok(planeRooms.slice(firstSecondaryIndex).every(room=>room.primaryLevel!=='plane'),'secondary cross-floor projections must follow primary Plane Rooms');
assert.ok(planeRooms.every(room=>typeof room.isPrimaryProjection==='boolean'),'Room rows must expose projection priority');
assert.ok(planeRooms.slice(0,firstSecondaryIndex).every(room=>room.isPrimaryProjection===true),'primary Rooms must be marked primary');
assert.ok(planeRooms.slice(firstSecondaryIndex).every(room=>room.isPrimaryProjection===false),'secondary Rooms must be marked secondary');

// every governed Room must be visible on its resolved primary floor so it can be highlighted in place
for(const dwelling of projection.dwellings){
  const visible=elevator.roomsForLevel(dwelling.primary_level,projection,roomContract);
  assert.ok(visible.some(room=>room.id===dwelling.id), dwelling.id+' must appear on its primary floor rail');
}

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=fs.readFileSync(path.join(ROOT,'app/site-elevator.js'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'app/site-elevator.css'),'utf8');

// VISUAL CONTRACT
for(const marker of [
  'site-elevator-controls',
  'site-elevator-up',
  'site-elevator-down',
  'site-elevator-reel',
  'site-elevator-room-rail',
  'aria-live',
  'aria-current',
  'data-elevator-level',
  'is-primary',
  'is-secondary',
  "if(event.target!==header)return",
]){
  assert.ok(source.includes(marker),'site elevator visual contract missing '+marker);
}
assert.equal(/history\.(?:pushState|replaceState)/.test(source),false,'floor switching must not mutate history');
assert.equal(/location\.(?:assign|replace)|location\.href\s*=/.test(source),false,'floor switching must not navigate the page');
assert.ok(source.includes("ArrowUp"),'header keyboard contract needs ArrowUp');
assert.ok(source.includes("ArrowDown"),'header keyboard contract needs ArrowDown');
assert.ok(source.includes("Home"),'header keyboard contract needs Home → Plane');
assert.ok(source.includes("disabled"),'boundary arrows must expose disabled state');

assert.ok(css.includes('grid-template-columns:repeat(auto-fit,minmax('),'Room rail must pack into a responsive wrapped terminal grid');
assert.ok(css.includes('overflow:visible'),'Room rail must expose wrapped lines');
assert.equal(css.includes('overflow-x:auto'),false,'Room rail must not horizontally scroll');
assert.equal(css.includes('scrollbar-width'),false,'Room rail must not render a scrollbar');
assert.ok(css.includes('.site-elevator-arrow::before'),'arrow controls should use metallic line detailing without button blocks');
assert.ok(css.includes('.site-elevator-floor-code'),'terminal board needs a numbered floor code');
assert.ok(css.includes('[data-elevator-level="heaven"]::before'),'Heaven needs a distinct pixel-biome layer');
assert.ok(css.includes('[data-elevator-level="plane"]::before'),'Plane needs a distinct pixel-biome layer');
assert.ok(css.includes('[data-elevator-level="below"]::before'),'Below needs a distinct pixel-biome layer');
assert.ok(css.includes('border-radius:0'),'terminal Room tiles should not drift back into pill styling');
assert.ok(css.includes('content:"HERE"'),'actual Room tile needs an explicit HERE terminal marker');
assert.ok(css.includes('border-style:dashed'),'secondary projected Rooms must remain visually subordinate');
assert.ok(css.includes('[data-elevator-level="plane"] .site-elevator-room'),'Plane Room tiles need block-earth material styling');
assert.ok(css.includes('[data-elevator-level="heaven"] .site-elevator-room'),'Heaven Room tiles need sky material styling');
assert.ok(css.includes('[data-elevator-level="below"] .site-elevator-room'),'Below Room tiles need underground material styling');
assert.ok(css.includes('background:transparent'),'arrow controls must float without metallic button blocks');
assert.ok(css.includes('display:block!important'),'elevator shell must survive page-level header display overrides');
assert.ok(css.includes('display:grid!important'),'Room rail must survive page-level nav display overrides');
assert.ok(css.includes('margin:0!important'),'elevator shell must reset page-level header/nav margins');
assert.ok(css.includes('align-self:start'),'elevator controls must stay pinned when Room grid wraps');
assert.ok(css.includes('height:42px'),'desktop elevator controls need a fixed one-row height');
assert.ok(css.includes('.site-elevator-reel{\n  align-self:start;'),'floor board must stay pinned when Room grid wraps');
assert.ok(css.includes('grid-auto-rows:minmax(26px,auto)'),'wrapped Room rows must stay compact and predictable');
assert.ok(css.includes('.site-elevator-up::before{content:"△"}'),'up arrow needs triangle framing');
assert.ok(css.includes('.site-elevator-down::before{content:"▽"}'),'down arrow needs inverted triangle framing');
assert.ok(css.includes('font:400 21px/1'),'triangle framing should be slightly larger on desktop');
assert.ok(source.includes('site-elevator-floor-code'),'runtime must render terminal floor code');
assert.ok(source.includes('header.dataset.elevatorRoom=spatial.roomId'),'runtime must publish the current Room on the header');
assert.ok(source.includes("selectedLevel===spatial.levelId"),'active Room highlight must only appear on the actual floor');
assert.ok(source.includes("'HERE · '"),'actual floor must expose HERE label');
assert.ok(source.includes("'BROWSING FLOOR'"),'non-actual floor must be clearly marked as browsing');

console.log('Site elevator resolver + visual contract passed.');
