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

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=fs.readFileSync(path.join(ROOT,'app/site-elevator.js'),'utf8');

// VISUAL CONTRACT
for(const marker of [
  'site-elevator-up',
  'site-elevator-down',
  'site-elevator-reel',
  'site-elevator-room-rail',
  'aria-live',
  'aria-current',
  'data-elevator-level',
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
