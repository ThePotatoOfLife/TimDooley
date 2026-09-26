#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require=createRequire(import.meta.url);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const drawer=require(path.join(ROOT,'app/tts-drawer.js'));
const adapter=require(path.join(ROOT,'app/longform-tts-adapter.js'));

const current={id:'current'},container={id:'container'};
assert.equal(adapter.highlightTargetForSection('selection',current,container),null,'selection playback must never own page movement');
assert.equal(adapter.highlightTargetForSection('current',current,container),current,'current playback should target the active section');
assert.equal(adapter.highlightTargetForSection('all',current,container),container,'whole-page playback should target the reader container');
assert.equal(adapter.highlightTargetForSection('other',current,container),null,'unknown scopes must not own page movement');

const scrollCalls=[];
const textNode={nodeValue:'Hello world',parentElement:{closest:()=>null}};
const fakeRange={
  setStart(){},setEnd(){},
  getBoundingClientRect(){return {top:900,height:20};},
};
const highlights={set(){},delete(){}};
const win={
  innerHeight:600,scrollY:100,
  CSS:{highlights},
  Highlight:class Highlight{},
  localStorage:{getItem(){return JSON.stringify({followReading:true});}},
  scrollTo(options){scrollCalls.push(options);},
};
const doc={
  defaultView:win,
  documentElement:{clientHeight:600},
  createTreeWalker(){
    let done=false;
    return {nextNode(){if(done)return null;done=true;return textNode;}};
  },
  createRange(){return {...fakeRange};},
};
const reader={ownerDocument:doc};

const highlighter=drawer.createPageHighlighter({document:doc});
assert.equal(highlighter.highlight(reader,{start:0,end:5},'',false),true);
assert.equal(scrollCalls.length,0,'explicit Follow OFF must override persisted Follow ON and stop TTS-driven scrolling');
assert.equal(highlighter.highlight(reader,{start:0,end:5},'',true),true);
assert.equal(scrollCalls.length,1,'Follow ON should allow exactly one centering scroll for one boundary highlight');

const drawerSource=fs.readFileSync(path.join(ROOT,'app/tts-drawer.js'),'utf8');
const adapterSource=fs.readFileSync(path.join(ROOT,'app/longform-tts-adapter.js'),'utf8');
assert.match(drawerSource,/drawer\.playSection\?\.\('selection'\)/,'selection action must play the selection scope');
assert.match(adapterSource,/drawer\.playSection\?\.\('current'\)/,'inline Listen must play the current section scope');
assert.match(adapterSource,/ttsSuppressed='duplicate-primary'/,'duplicate primary reader hosts must be suppressed');
const movementCalls=(drawerSource.match(/\.scrollTo\(/g)||[]).length+(adapterSource.match(/\.scrollTo\(/g)||[]).length;
assert.equal(movementCalls,1,'shared TTS must have exactly one viewport-moving implementation');

console.log('TTS interaction matrix passed: Follow OFF stops movement, selection is non-moving, inline/current ownership is isolated, duplicate primary readers are suppressed.');
