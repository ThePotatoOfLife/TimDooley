import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const reader=require('../app/bible-scripture-reader.js');
const books=['Genesis','Matthew','John','Revelation','1 John','Song of Solomon'];
assert.deepEqual(reader.parseReference('John 10:7',books).selectors,[{start:{chapter:10,verse:7},end:{chapter:10,verse:7}}]);
assert.deepEqual(reader.parseReference('John 10:7, 9',books).selectors,[{start:{chapter:10,verse:7},end:{chapter:10,verse:7}},{start:{chapter:10,verse:9},end:{chapter:10,verse:9}}]);
assert.deepEqual(reader.parseReference('Genesis 28:10-22',books).selectors,[{start:{chapter:28,verse:10},end:{chapter:28,verse:22}}]);
assert.deepEqual(reader.parseReference('Genesis 28:10–22',books).selectors,[{start:{chapter:28,verse:10},end:{chapter:28,verse:22}}]);
assert.deepEqual(reader.parseReference('Revelation 21:1-22:5',books).selectors,[{start:{chapter:21,verse:1},end:{chapter:22,verse:5}}]);
assert.deepEqual(reader.splitReferences('Matthew 20:20-28; John 13:1-17'),['Matthew 20:20-28','John 13:1-17']);
const verses=[{chapter:10,verse:6},{chapter:10,verse:7},{chapter:10,verse:8},{chapter:10,verse:9},{chapter:10,verse:10}];
assert.deepEqual(reader.selectVerses(verses,reader.parseReference('John 10:7, 9',books)).map(v=>v.verse),[7,9]);
const rendered=reader.renderVersesHTML({verses:[
  {book:'Matthew',chapter:20,verse:20,text:'A'},
  {book:'John',chapter:20,verse:20,text:'B'}
]});
assert.match(rendered,/Matthew 20/);
assert.match(rendered,/John 20/);
console.log('BIBLE SCRIPTURE RANGE TESTS PASSED');
