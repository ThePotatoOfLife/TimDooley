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

const unknown=elevator.resolveSpatialContext('/totally-unknown/',projection,roomContract);
assert.equal(unknown.levelId,'plane');
assert.equal(unknown.roomId,null);

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

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=fs.readFileSync(path.join(ROOT,'app/site-elevator.js'),'utf8');

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
]){
  assert.ok(source.includes(marker),'site elevator visual contract missing '+marker);
}
assert.equal(/history\.(?:pushState|replaceState)/.test(source),false,'floor switching must not mutate history');
assert.equal(/location\.(?:assign|replace)|location\.href\s*=/.test(source),false,'floor switching must not navigate the page');
assert.ok(source.includes("ArrowUp"),'header keyboard contract needs ArrowUp');
assert.ok(source.includes("ArrowDown"),'header keyboard contract needs ArrowDown');
assert.ok(source.includes("Home"),'header keyboard contract needs Home → Plane');
assert.ok(source.includes("disabled"),'boundary arrows must expose disabled state');

console.log('Site elevator resolver + visual contract passed.');
