import assert from 'node:assert/strict';
import {buildSearchRecords, rankSearchRecords} from '../world-map/3d-search-core.js';

const records = buildSearchRecords({
  countries:[{iso3:'GEO',name:'Georgia'},{iso3:'USA',name:'United States'}],
  subdivisions:[{id:'US-CA',name:'California',code:'CA',parent:'United States'}],
  places:[{id:'wd:Q65',name:'Los Angeles',iso3:'USA',admin_region:'California',country:'United States',aliases:['LA']}],
});
assert.equal(rankSearchRecords(records,'Georgia')[0].id,'GEO');
assert.equal(rankSearchRecords(records,'CA')[0].id,'US-CA');
assert.equal(rankSearchRecords(records,'LA')[0].id,'wd:Q65');
assert.match(rankSearchRecords(records,'Los Angeles')[0].display,/City.*California.*United States/);
assert.deepEqual(rankSearchRecords(records,'not-a-place'),[]);
console.log('WORLD MAP SEARCH CORE PASSED');
