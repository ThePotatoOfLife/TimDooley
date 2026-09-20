(()=>{'use strict';
const BASE='/TimDooley/';
const esc=s=>String(s??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
let manifest,activity,currentDesk,contract,accounts=[],scope='all';const selected=new URLSearchParams(location.search).get('character')||'';
async function get(path){const r=await fetch(BASE+path);if(!r.ok)throw new Error(path);return r.json()}
function exactDate(s){return /^\d{4}-\d{2}-\d{2}$/.test(String(s||''))?new Date(String(s)+'T00:00:00Z'):null}
function money(n){return '$'+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:4,maximumFractionDigits:4})}
function eventAdjustment(entries){
 const weights=contract?.event_weights||{};let total=0,credits=0,debits=0,repairs=0;
 for(const e of entries||[]){
  const explicit=Number(e.project_adjustment_susd),fallback=weights[e.type],w=Number.isFinite(explicit)?explicit:fallback;
  if(typeof w==='number'&&Number.isFinite(w)){total+=w;if(w>0)credits++;if(w<0)debits++;if(e.type==='repair-attempt')repairs++;}
 }
 return{total,credits,debits,repairs};
}
function welfare(start){
 const d=exactDate(start);if(!d)return{exact:false,value:0,seconds:0};
 const seconds=Math.max(0,(Date.now()-d.getTime())/1000),rate=Number(contract?.welfare?.rate_per_second_susd||0);
 return{exact:true,value:seconds*rate,seconds};
}
function bandFor(id){return (activity?.records||[]).find(x=>x.id===id)?.band||'historical'}
function currentIds(){return new Set((currentDesk?.items||[]).map(x=>x.id))}
function buildAccount(meta,d){
 const start=d.symbolic_account?.welfare_start_override||d.cia_record?.presence?.first_recorded||'',w=welfare(start),adj=eventAdjustment(d.symbolic_account?.entries||[]);
 return{id:meta.id,name:meta.name||d.display_name||meta.id,start,band:bandFor(meta.id),welfare:w.value,exact:w.exact,adjustment:adj.total,balance:w.value+adj.total,events:(d.symbolic_account?.entries||[]),status:d.symbolic_account?.status||'unassessed'};
}
function render(){
 const q=document.getElementById('bankSearch').value.trim().toLowerCase(),cur=currentIds();
 const filtered=accounts.filter(a=>(scope==='all'||cur.has(a.id))&&(!q||(a.name+' '+a.id).toLowerCase().includes(q)));
 const box=document.getElementById('accounts');
 box.innerHTML=filtered.map(a=>{
  const eventNote=a.events.length?a.events.length+' explicit ledger event'+(a.events.length===1?'':'s'):'no explicit event adjustments';
  return '<article class="account" data-band="'+esc(a.band)+'"><div class="account-name"><span>'+esc(a.band)+' account</span><a href="../file/?character='+encodeURIComponent(a.id)+'">'+esc(a.name)+'</a><small>Story entry: '+esc(a.start||'unresolved')+' · '+eventNote+'</small></div>'+
   '<div class="metric '+(a.exact?'positive':'provisional')+'"><b>Dooley Welfare</b><strong data-live-welfare="'+esc(a.id)+'">'+(a.exact?money(a.welfare):'provisional')+'</strong><small>'+(a.exact?'still accruing':'exact start date needed')+'</small></div>'+
   '<div class="metric '+(a.adjustment>0?'positive':a.adjustment<0?'negative':'')+'"><b>Event adjustment</b><strong>'+money(a.adjustment)+'</strong><small>event-weighted, not moral score</small></div>'+
   '<div class="metric '+(a.balance>=0?'positive':'negative')+'"><b>Approx balance</b><strong data-live-balance="'+esc(a.id)+'">'+(a.exact?money(a.balance):money(a.adjustment)+' + welfare')+'</strong><small>fictional sUSD-equivalent</small></div>'+
   '<div class="metric"><b>Status</b><strong>'+esc(a.status)+'</strong><small>'+esc(a.events.map(x=>x.type).slice(0,3).join(' · ')||'welfare only')+'</small></div></article>';
 }).join('')||'<p>No accounts match this view.</p>';
 const exact=filtered.filter(a=>a.exact),sumW=exact.reduce((n,a)=>n+a.welfare,0),sumAdj=filtered.reduce((n,a)=>n+a.adjustment,0),sumBal=exact.reduce((n,a)=>n+a.balance,0);
 document.getElementById('bankSummary').innerHTML=
  '<div class="summary-cell"><b>Visible accounts</b><strong>'+filtered.length+'</strong></div>'+
  '<div class="summary-cell"><b>Exact-start welfare</b><strong>'+money(sumW)+'</strong></div>'+
  '<div class="summary-cell"><b>Event adjustments</b><strong>'+money(sumAdj)+'</strong></div>'+
  '<div class="summary-cell"><b>Exact-start subtotal</b><strong>'+money(sumBal)+'</strong></div>';
}
function tick(){
 const rate=Number(contract?.welfare?.rate_per_second_susd||0);
 for(const a of accounts){if(!a.exact)continue;a.welfare+=rate;a.balance+=rate;
  const w=document.querySelector('[data-live-welfare="'+CSS.escape(a.id)+'"]'),b=document.querySelector('[data-live-balance="'+CSS.escape(a.id)+'"]');
  if(w)w.textContent=money(a.welfare);if(b)b.textContent=money(a.balance);
 }
}
function setScope(x){scope=x;document.getElementById('bankAll').classList.toggle('active',x==='all');document.getElementById('bankCurrent').classList.toggle('active',x==='current');render()}
(async()=>{
 [manifest,activity,currentDesk,contract]=await Promise.all([get('knowledge/cia/manifest.json'),get('knowledge/cia/activity-index.json'),get('knowledge/cia/current-desk.json'),get('knowledge/cia/mud-bank-contract.json')]);
 const ds=await Promise.all((manifest.characters||[]).map(async m=>[m,await get(m.path)]));
 accounts=ds.map(([m,d])=>buildAccount(m,d)).sort((a,b)=>{const ca=currentIds(),ac=ca.has(a.id)?0:1,bc=ca.has(b.id)?0:1;return ac-bc||b.balance-a.balance||a.name.localeCompare(b.name)});
 if(selected){document.getElementById('bankSearch').value=selected;}render();document.getElementById('bankSearch').addEventListener('input',render);document.getElementById('bankAll').onclick=()=>setScope('all');document.getElementById('bankCurrent').onclick=()=>setScope('current');setInterval(tick,1000);
})().catch(e=>{document.getElementById('accounts').innerHTML='<p>The symbolic bank could not open all ledgers. CIA dossiers remain available individually.</p>';});
})();
