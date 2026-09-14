import assert from 'node:assert/strict';
import {buildSearchRecords, rankSearchRecords, subdivisionSearchRows} from '../world-map/3d-search-core.js';

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

const subdivisionRows = subdivisionSearchRows({
  partitions:{
    USA:{
      path:'USA.geo.json',
      search_records:[
        {id:'US-CA',name:'California',code:'CA',subdivision_type:'state',parent_iso3:'USA',parent_name:'United States'},
      ],
    },
    DNK:{
      path:'DNK.geo.json',
      search_records:[
        {id:'DK-1082',name:'Region Midtjylland',code:'1082',subdivision_type:'region',parent_iso3:'DNK',parent_name:'Denmark'},
      ],
    },
  },
});
assert.equal(subdivisionRows.length,2);
assert.equal(subdivisionRows[0].id,'US-CA');
assert.equal(subdivisionRows[1].id,'DK-1082');
assert.ok(subdivisionRows.every(row => !('geometry' in row)), 'search manifest must stay geometry-free');

console.log('WORLD MAP SEARCH CORE PASSED');
