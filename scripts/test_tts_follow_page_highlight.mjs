import assert from 'node:assert/strict';
import fs from 'node:fs';
import drawer from '../app/tts-drawer.js';

const source=fs.readFileSync(new URL('../app/tts-drawer.js',import.meta.url),'utf8');

// The drawer's duplicate reading view must never move the document viewport.
assert.ok(!source.includes("mark?.scrollIntoView?.({block:followReading?'center':'nearest',inline:'nearest'})"),
  'drawer copy must not compete with the real page highlight for scrolling');

// Follow-reading is a strict page lock: the DOM range for the real highlighted
// word is centered immediately, so the viewport follows the page content itself.
const scrolls=[];
const win={innerHeight:800,scrollY:300,scrollTo:opts=>scrolls.push(opts),matchMedia:()=>({matches:false})};
const doc={documentElement:{clientHeight:800}};
const range={getBoundingClientRect:()=>({top:360,height:20})};
assert.equal(drawer.centerDomRange(win,doc,range),true,'highlighted page word must be actively recentered');
assert.deepEqual(scrolls,[{top:270,behavior:'auto'}],'real highlighted word should land at exact viewport center without smooth-scroll lag');

console.log('tts page-highlight follow contract: ok');
