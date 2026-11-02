/* Potato Exchange: small, testable paper-trading core. No artificial market prices. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.PotatoEngine=api})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const ok=n=>typeof n==='number'&&Number.isFinite(n);
const round8=n=>Math.round((n+Number.EPSILON)*1e8)/1e8;
function validateSave(s){
  if(!s||typeof s!=='object'||s.version!==1||!['DKK','USD','EUR'].includes(s.currency)||!['real','demo'].includes(s.mode))throw Error('Invalid save header');
  if(!ok(s.cash)||s.cash<0||s.cash>1e16||!ok(s.starting)||s.starting<100||s.starting>1e12)throw Error('Invalid cash or starting balance');
  if(!Array.isArray(s.assets)||s.assets.length>300||!Array.isArray(s.trades)||s.trades.length>10000||!s.positions||Array.isArray(s.positions)||typeof s.positions!=='object')throw Error('Invalid portfolio collections');
  if(s.fees!==undefined&&(!ok(s.fees)||s.fees<0||s.fees>1e16))throw Error('Invalid accumulated fees');
  if(s.realized!==undefined&&(!ok(s.realized)||Math.abs(s.realized)>1e16))throw Error('Invalid realized result');
  const ids=new Set();
  for(const a of s.assets){
    if(!a||typeof a.id!=='string'||!a.id||a.id.length>80||ids.has(a.id)||typeof a.symbol!=='string'||a.symbol.length>40||!a.symbol||typeof a.currency!=='string'||!/^[A-Z]{3}$/.test(a.currency))throw Error('Invalid or duplicate instrument');
    ids.add(a.id);
    if(a.price!==null&&a.price!==undefined&&(!ok(a.price)||a.price<=0))throw Error('Invalid saved quote for '+a.symbol);
    if(a.history!==undefined&&(!Array.isArray(a.history)||a.history.length>3000))throw Error('Invalid price history');
  }
  const holdings=Object.entries(s.positions);
  if(holdings.length>300)throw Error('Too many saved positions');
  for(const [id,p] of holdings){
    if(!ids.has(id)||!p||!ok(p.qty)||p.qty<0||p.qty>1e12||!ok(p.cost)||p.cost<0||p.cost>1e16)throw Error('Invalid holding '+id);
  }
  for(const t of s.trades){
    if(!t||!['buy','sell'].includes(t.side)||!ok(t.qty)||t.qty<=0||t.qty>1e12||!ok(t.price)||t.price<=0||!ok(t.total)||t.total<0||!ok(t.fee)||t.fee<0)throw Error('Invalid saved transaction');
  }
  if(s.snapshots!==undefined&&(!Array.isArray(s.snapshots)||s.snapshots.length>3000))throw Error('Invalid equity history');
  return s;
}
function blockQuote(a,time=Date.now()){
  if(!a)return 'Choose an instrument';
  if(a.source!=='live')return 'A provider quote is required; manual or imported values cannot be traded';
  if(!ok(a.checkedAt)||a.checkedAt<=0||time-a.checkedAt>600000||a.checkedAt-time>60000)return 'Provider has not been checked within ten minutes';
  if(a.provider==='gold')return 'Spot-metal price is indicative; select a tradable metal instrument';
  if(a.provider==='manual')return 'Manual reference prices are display-only';
  if(a.provider==='coingecko'){
    if(a.type!=='crypto')return 'CoinGecko quote cannot execute this asset class';
    if(!ok(a.updatedAt)||a.updatedAt<=0||time-a.updatedAt>300000||a.updatedAt-time>60000)return 'Crypto price observation is over five minutes old';
    return null;
  }
  if(a.provider==='twelve'){
    if(a.marketOpen!==true)return 'Exchange closed or market status unknown';
    if(a.quoteProvider!=='Twelve Data')return 'Verified market source unavailable';
    return null;
  }
  return 'This instrument has no supported paper-trading execution rule';
}
function preview({side,qty,price,rate,feePct=0,slippagePct=0,cash,position}){
  if(!['buy','sell'].includes(side))throw Error('Unknown order side');
  if(!ok(qty)||qty<=0||qty>1e12)throw Error('Invalid quantity');
  if(!ok(price)||price<=0||!ok(rate)||rate<=0)throw Error('Missing quote or FX rate');
  if(!ok(feePct)||feePct<0||feePct>10||!ok(slippagePct)||slippagePct<0||slippagePct>2)throw Error('Invalid fee settings');
  if(!ok(cash)||cash<0||!position||!ok(position.qty)||position.qty<0||!ok(position.cost)||position.cost<0)throw Error('Invalid portfolio state');
  const fill=price*(1+(side==='buy'?1:-1)*slippagePct/100);
  const gross=qty*fill*rate,fee=gross*feePct/100,total=side==='buy'?gross+fee:gross-fee;
  if(!ok(total)||total<=0||total>1e16)throw Error('Order exceeds supported range');
  if(side==='buy'&&total>cash+1e-7)throw Error('Insufficient virtual cash');
  if(side==='sell'&&qty>position.qty+1e-8)throw Error('Insufficient units to sell');
  return {side,qty,fill,gross,fee,total};
}
function settle({cash,position,realized=0,fees=0},order){
  if(!order||!['buy','sell'].includes(order.side))throw Error('Invalid settlement');
  const p={qty:position.qty,cost:position.cost};
  let nextCash=cash,nextRealized=realized;
  if(order.side==='buy'){
    nextCash-=order.total;p.qty=round8(p.qty+order.qty);p.cost+=order.total;
  }else{
    const allocated=p.cost*(order.qty/Math.max(p.qty,1e-8));
    nextCash+=order.total;nextRealized+=order.total-allocated;
    p.qty=round8(Math.max(0,p.qty-order.qty));
    p.cost=Math.max(0,p.cost-allocated);
    if(p.qty<=1e-8){p.qty=0;p.cost=0;}
  }
  if(!ok(nextCash)||nextCash< -1e-6||!ok(p.qty)||!ok(p.cost))throw Error('Settlement failed invariant check');
  return {cash:Math.max(0,nextCash),position:p,realized:nextRealized,fees:fees+order.fee};
}
return Object.freeze({validateSave,blockQuote,preview,settle});
});
