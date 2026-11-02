const test=require('node:test');
const assert=require('node:assert/strict');
const E=require('../games/potato-exchange/engine.js');
const at=1_000_000;
const crypto={type:'crypto',provider:'coingecko',source:'live',checkedAt:at,updatedAt:at};
const stock={type:'stock',provider:'twelve',source:'live',checkedAt:at,updatedAt:at-3600_000,marketOpen:true,quoteProvider:'Twelve Data'};
test('crypto: fresh trades; stale and manual quotes never trade',()=>{
 assert.equal(E.blockQuote(crypto,at+60_000),null);
 assert.match(E.blockQuote(crypto,at+360_000),/five minutes/);
 assert.ok(E.blockQuote({...crypto,source:'manual'},at+1_000));
});
test('stocks: session status, provider evidence, quote freshness',()=>{
 assert.equal(E.blockQuote(stock,at+60_000),null);
 assert.match(E.blockQuote({...stock,marketOpen:false},at+60_000),/closed/);
 assert.ok(E.blockQuote({...stock,quoteProvider:''},at+60_000));
 assert.ok(E.blockQuote(stock,at+700_000));
});
test('buy and sell: fees, slippage, cost basis, realized profit and no phantom money',()=>{
 const initial={cash:1000,position:{qty:0,cost:0},realized:0,fees:0};
 const buy=E.preview({side:'buy',qty:2,price:100,rate:1,feePct:.1,slippagePct:.05,...initial});
 assert.ok(Math.abs(buy.total-200.3001)<1e-8);
 const afterBuy=E.settle(initial,buy);
 assert.equal(afterBuy.position.qty,2);
 assert.ok(Math.abs(afterBuy.cash-(1000-buy.total))<1e-7);
 const sell=E.preview({side:'sell',qty:1,price:110,rate:1,feePct:.1,slippagePct:.05,...afterBuy});
 const afterSell=E.settle(afterBuy,sell);
 assert.equal(afterSell.position.qty,1);
 assert.ok(afterSell.realized>0);
 assert.ok(Math.abs(afterSell.position.cost-buy.total/2)<1e-7);
});
test('reject impossible orders',()=>{
 const p={cash:100,position:{qty:1,cost:50}};
 assert.throws(()=>E.preview({side:'buy',qty:1,price:1000,rate:1,...p}),/cash/);
 assert.throws(()=>E.preview({side:'sell',qty:2,price:100,rate:1,...p}),/units/);
 assert.throws(()=>E.preview({side:'buy',qty:-1,price:100,rate:1,...p}),/quantity/);
 assert.throws(()=>E.preview({side:'buy',qty:1,price:0,rate:1,...p}),/quote/);
});
function sampleSave(){
 return {version:1,mode:'real',currency:'DKK',cash:100000,starting:100000,assets:[{id:'a',symbol:'AAPL',currency:'USD',price:null,history:[]}],trades:[],positions:{},snapshots:[]};
}
test('save schema validates legitimate saves; rejects corruption and forged holdings',()=>{
 assert.equal(E.validateSave(sampleSave()).cash,100000);
 assert.throws(()=>E.validateSave({...sampleSave(),cash:-1}),/cash/);
 assert.throws(()=>E.validateSave({...sampleSave(),cash:'1000'}),/cash/);
 assert.throws(()=>E.validateSave({...sampleSave(),positions:{fake:{qty:1,cost:100}}}),/holding/);
 assert.throws(()=>E.validateSave({...sampleSave(),assets:[sampleSave().assets[0],sampleSave().assets[0]]}),/duplicate/);
});
