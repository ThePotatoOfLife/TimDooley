(()=>{'use strict';
const BASE='/TimDooley/';
const esc=s=>String(s??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
let manifest,activity,currentDesk,contract,postureIndex,systemLedger,accounts=[],scope='all';
let activeId=new URLSearchParams(location.search).get('character')||'';
async function get(path){const r=await fetch(BASE+path);if(!r.ok)throw new Error(path);return r.json()}
function exactDate(s){return /^\d{4}-\d{2}-\d{2}$/.test(String(s||''))?new Date(String(s)+'T00:00:00Z'):null}
function money(n){
 const v=Number(n||0),a=Math.abs(v);
 const digits=a<.001?11:a<1?6:4;
 return '$'+v.toLocaleString(undefined,{minimumFractionDigits:digits,maximumFractionDigits:digits});
}
function amountFor(e){
 const explicit=e?.project_adjustment_susd;
 if(typeof explicit==='number'&&Number.isFinite(explicit))return explicit;
 const fallback=contract?.event_weights?.[e?.type];
 return typeof fallback==='number'&&Number.isFinite(fallback)?fallback:0;
}
function welfare(start){
 const d=exactDate(start);if(!d)return{exact:false,value:0,seconds:0};
 const seconds=Math.max(0,(Date.now()-d.getTime())/1000),rate=Number(contract?.welfare?.rate_per_second_susd||0);
 return{exact:true,value:seconds*rate,seconds};
}
function bandFor(id){return (activity?.records||[]).find(x=>x.id===id)?.band||'historical'}
function currentIds(){return new Set((currentDesk?.items||[]).map(x=>x.id))}
function buildAccount(meta,d){
 const start=d.symbolic_account?.welfare_start_override||d.cia_record?.presence?.first_recorded||'';
 const w=welfare(start),events=(d.symbolic_account?.entries||[]).map(e=>({...e,amount:amountFor(e)}));
 const posture=(postureIndex?.accounts||[]).find(x=>x.id===meta.id)||{};
 const adjustment=events.reduce((n,e)=>n+e.amount,0);
 return{
  id:meta.id,name:meta.name||d.display_name||meta.id,start,band:bandFor(meta.id),
  welfare:w.value,exact:w.exact,adjustment,balance:w.value+adjustment,events,
  status:d.symbolic_account?.status||'unassessed',posture:posture.posture||'unassessed',
  gross_credit_susd:Number(posture.gross_credit_susd||0),gross_debit_susd:Number(posture.gross_debit_susd||0),
  unpriced_negative_candidates:Number(posture.unpriced_negative_candidates||0)
 };
}
function labelFor(e){return e.label||e.kind||e.type||'ledger event'}
function noteFor(e){return [e.date,e.note,e.summary,e.status,e.source_mode].filter(Boolean).join(' · ')}
function statementRow(e,kind){
 return '<div class="statement-row '+kind+'"><span><b>'+esc(labelFor(e))+'</b><small>'+esc(noteFor(e))+'</small></span><strong>'+money(Math.abs(e.amount||0))+'</strong></div>';
}
function selectedAccount(filtered){
 let a=accounts.find(x=>x.id===activeId);
 if(a&&(!filtered||filtered.some(x=>x.id===a.id)))return a;
 a=(filtered||[])[0]||accounts.find(x=>currentIds().has(x.id))||accounts[0];
 if(a)activeId=a.id;
 return a;
}
function updateUrl(){
 const u=new URL(location.href);
 if(activeId)u.searchParams.set('character',activeId);else u.searchParams.delete('character');
 history.replaceState(null,'',u.pathname+u.search+u.hash);
}
function renderStatement(filtered){
 const box=document.getElementById('accountStatement');if(!box)return;
 const a=selectedAccount(filtered);if(!a){box.innerHTML='';return}
 const positive=a.events.filter(e=>e.amount>0),negative=a.events.filter(e=>e.amount<0),zero=a.events.filter(e=>!e.amount);
 const totalIn=(a.exact?a.welfare:0)+positive.reduce((n,e)=>n+e.amount,0);
 const totalOut=negative.reduce((n,e)=>n+Math.abs(e.amount),0);
 const balance=(a.exact?totalIn-totalOut:a.adjustment);
 const inflows=(a.exact?'<div class="statement-row welfare"><span><b>Dooley Welfare</b><small>continuous from '+esc(a.start)+' · +'+esc(money(contract?.welfare?.rate_per_second_susd||0))+'/second</small></span><strong data-statement-welfare="'+esc(a.id)+'">'+money(a.welfare)+'</strong></div>':'<div class="statement-row provisional"><span><b>Dooley Welfare</b><small>exact story-entry date unresolved</small></span><strong>provisional</strong></div>')+
  (positive.length?positive.map(e=>statementRow(e,'inflow')).join(''):'<p class="statement-empty">No other priced inflows recorded.</p>');
 const outflows=negative.length?negative.map(e=>statementRow(e,'outflow')).join(''):'<p class="statement-empty">No priced outflows recorded.</p>';
 const offbookCount=zero.length+a.unpriced_negative_candidates;
 box.innerHTML='<article class="balance-sheet" data-account="'+esc(a.id)+'">'+
  '<header><div><span>ACCOUNT STATEMENT · NORTH ROOT LEDGER</span><h2>'+esc(a.name)+'</h2><small>Account '+esc(a.id)+' · story entry '+esc(a.start||'unresolved')+' · posture '+esc(a.posture)+'</small></div><div class="statement-actions"><a href="../file/?character='+encodeURIComponent(a.id)+'">Open Character Archive file →</a><button type="button" data-copy-account="'+esc(a.id)+'">Copy account link</button></div></header>'+
  '<div class="position-strip"><div><span>Accrued welfare</span><strong data-statement-welfare-top="'+esc(a.id)+'">'+(a.exact?money(a.welfare):'provisional')+'</strong></div><div><span>Gross event credit</span><strong>'+money(a.gross_credit_susd)+'</strong></div><div><span>Gross event debit</span><strong>'+money(Math.abs(a.gross_debit_susd))+'</strong></div><div class="'+(balance>=0?'positive':'negative')+'"><span>Current position</span><strong data-statement-balance="'+esc(a.id)+'">'+(a.exact?money(balance):money(a.adjustment)+' + welfare')+'</strong></div></div>'+
  '<div class="balance-equation"><div><span>Total inflow</span><strong data-statement-inflow="'+esc(a.id)+'">'+(a.exact?money(totalIn):money(positive.reduce((n,e)=>n+e.amount,0))+' + welfare')+'</strong></div><i>−</i><div><span>Total outflow</span><strong>'+money(totalOut)+'</strong></div><i>=</i><div class="'+(balance>=0?'positive':'negative')+'"><span>Ledger balance</span><strong data-statement-balance-2="'+esc(a.id)+'">'+(a.exact?money(balance):money(a.adjustment)+' + welfare')+'</strong></div></div>'+
  '<div class="statement-columns"><section><h3>IN · value received / created</h3>'+inflows+'<footer><span>Total inflow</span><b>'+(a.exact?money(totalIn):'priced credit + welfare')+'</b></footer></section><section><h3>OUT · priced debits / unresolved movement</h3>'+outflows+'<footer><span>Total outflow</span><b>'+money(totalOut)+'</b></footer></section></div>'+
  (offbookCount?'<div class="offbook"><b>Off-balance-sheet / unpriced</b><span>'+zero.length+' zero-weight ledger item'+(zero.length===1?'':'s')+' · '+a.unpriced_negative_candidates+' unpriced negative candidate'+(a.unpriced_negative_candidates===1?'':'s')+'</span><small>Disputed, interpretive or insufficiently evidenced material remains visible without changing the balance.</small></div>':'')+
  '<p class="statement-boundary">Fictional Potatoverse sUSD statement. It records project events and symbolic accounting; it is not real money, a legal debt, credit report, diagnosis or objective measure of a person.</p></article>';
 const copy=box.querySelector('[data-copy-account]');
 if(copy)copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);copy.textContent='Link copied';setTimeout(()=>copy.textContent='Copy account link',1500)}catch(_){copy.textContent='Use address bar'}});
}
function renderSystemDomains(){
 const box=document.getElementById('systemDomains');if(!box)return;
 box.innerHTML=(systemLedger?.domains||[]).map(x=>'<article class="system-domain"><span>'+esc(x.status||'symbolic-domain')+'</span><h3>'+esc(x.label||x.id)+'</h3><p>'+esc(x.scope||'')+'</p><small>'+esc(x.priced?'priced':'unpriced')+' · '+esc((x.repair_questions||[]).slice(0,2).join(' · '))+'</small></article>').join('')||'<p>No system liability domains loaded.</p>';
}
function render(){
 const input=document.getElementById('bankSearch'),q=input.value.trim().toLowerCase(),cur=currentIds();
 const filtered=accounts.filter(a=>(scope==='all'||cur.has(a.id))&&(!q||(a.name+' '+a.id).toLowerCase().includes(q)));
 if(filtered.length&&!filtered.some(a=>a.id===activeId))activeId=filtered[0].id;
 renderStatement(filtered);
 const box=document.getElementById('accounts');
 box.innerHTML=filtered.map(a=>{
  const eventNote=a.events.length?a.events.length+' explicit ledger event'+(a.events.length===1?'':'s'):'welfare only';
  const postureNote='posture: '+a.posture+' · credit '+money(a.gross_credit_susd)+' · debit '+money(Math.abs(a.gross_debit_susd))+(a.unpriced_negative_candidates?' · '+a.unpriced_negative_candidates+' unpriced candidate'+(a.unpriced_negative_candidates===1?'':'s'):'');
  return '<article class="account '+(a.id===activeId?'selected':'')+'" data-band="'+esc(a.band)+'" data-account-row="'+esc(a.id)+'"><div class="account-name"><span>'+esc(a.band)+' account</span><button class="statement-open" type="button" data-select-account="'+esc(a.id)+'">'+esc(a.name)+'</button><small>Story entry: '+esc(a.start||'unresolved')+' · '+eventNote+'</small><small class="posture-note">'+esc(postureNote)+'</small><a class="dossier-exit" href="../file/?character='+encodeURIComponent(a.id)+'">Character Archive file ↗</a></div>'+
   '<div class="metric '+(a.exact?'positive':'provisional')+'"><b>Dooley Welfare</b><strong data-live-welfare="'+esc(a.id)+'">'+(a.exact?money(a.welfare):'provisional')+'</strong><small>'+(a.exact?'still accruing':'exact start date needed')+'</small></div>'+
   '<div class="metric '+(a.adjustment>0?'positive':a.adjustment<0?'negative':'')+'"><b>Event adjustment</b><strong>'+money(a.adjustment)+'</strong><small>event-led, not a moral score</small></div>'+
   '<div class="metric '+(a.balance>=0?'positive':'negative')+'"><b>Approx balance</b><strong data-live-balance="'+esc(a.id)+'">'+(a.exact?money(a.balance):money(a.adjustment)+' + welfare')+'</strong><small>fictional sUSD</small></div>'+
   '<div class="metric"><b>Status</b><strong>'+esc(a.status)+'</strong><small>'+esc(a.events.map(x=>x.type).slice(0,3).join(' · ')||'welfare only')+'</small></div></article>';
 }).join('')||'<p class="empty-ledger">No accounts match this view.</p>';
 box.querySelectorAll('[data-select-account]').forEach(btn=>btn.addEventListener('click',()=>{
   activeId=btn.dataset.selectAccount;updateUrl();render();document.getElementById('accountStatement')?.scrollIntoView({behavior:'smooth',block:'start'});
 }));
 const exact=filtered.filter(a=>a.exact),sumW=exact.reduce((n,a)=>n+a.welfare,0),sumAdj=filtered.reduce((n,a)=>n+a.adjustment,0),sumBal=exact.reduce((n,a)=>n+a.balance,0);
 document.getElementById('bankSummary').innerHTML=
  '<div class="summary-cell"><b>Visible accounts</b><strong>'+filtered.length+'</strong></div>'+
  '<div class="summary-cell"><b>Exact-start welfare</b><strong>'+money(sumW)+'</strong></div>'+
  '<div class="summary-cell"><b>Event adjustments</b><strong>'+money(sumAdj)+'</strong></div>'+
  '<div class="summary-cell"><b>Exact-start subtotal</b><strong>'+money(sumBal)+'</strong></div>';
 updateUrl();
}
function tick(){
 const rate=Number(contract?.welfare?.rate_per_second_susd||0);
 for(const a of accounts){if(!a.exact)continue;a.welfare+=rate;a.balance+=rate;
  document.querySelectorAll('[data-live-welfare="'+CSS.escape(a.id)+'"],[data-statement-welfare="'+CSS.escape(a.id)+'"],[data-statement-welfare-top="'+CSS.escape(a.id)+'"]').forEach(n=>n.textContent=money(a.welfare));
  document.querySelectorAll('[data-live-balance="'+CSS.escape(a.id)+'"],[data-statement-balance="'+CSS.escape(a.id)+'"],[data-statement-balance-2="'+CSS.escape(a.id)+'"]').forEach(n=>n.textContent=money(a.balance));
  document.querySelectorAll('[data-statement-inflow="'+CSS.escape(a.id)+'"]').forEach(n=>n.textContent=money(a.welfare+a.gross_credit_susd));
 }
}
function setScope(x){scope=x;document.getElementById('bankAll').classList.toggle('active',x==='all');document.getElementById('bankCurrent').classList.toggle('active',x==='current');render()}
(async()=>{
 [manifest,activity,currentDesk,contract,postureIndex,systemLedger]=await Promise.all([
  get('knowledge/cia/manifest.json'),get('knowledge/cia/activity-index.json'),get('knowledge/cia/current-desk.json'),
  get('knowledge/cia/mud-bank-contract.json'),get('knowledge/cia/account-posture-index.json'),get('knowledge/cia/system-liability-ledger.json')
 ]);
 const ds=await Promise.all((manifest.characters||[]).map(async m=>[m,await get(m.path)]));
 accounts=ds.map(([m,d])=>buildAccount(m,d)).sort((a,b)=>{const cur=currentIds(),ac=cur.has(a.id)?0:1,bc=cur.has(b.id)?0:1;return ac-bc||b.balance-a.balance||a.name.localeCompare(b.name)});
 if(!activeId)activeId=accounts.find(a=>currentIds().has(a.id))?.id||accounts[0]?.id||'';
 renderSystemDomains();render();
 document.getElementById('bankSearch').addEventListener('input',render);
 document.getElementById('bankAll').onclick=()=>setScope('all');
 document.getElementById('bankCurrent').onclick=()=>setScope('current');
 setInterval(tick,1000);
})().catch(()=>{document.getElementById('accounts').innerHTML='<p>The symbolic bank could not open all ledgers. Character Archive dossiers remain available individually.</p>';});
})();
