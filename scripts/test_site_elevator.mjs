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

console.log('Site elevator resolver contract passed.');
