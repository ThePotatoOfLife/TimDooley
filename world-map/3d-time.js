const CONTRACT_URL='../data/atlas-time-contract.json';
const NORTH_HISTORY_URL='../data/north-axis-membership-history.json';
const ID='atlasTimeState';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let contract=null;
let northHistory=null;

function parseDate(value){
  if(!value)return null;
  const d=new Date(`${value}T00:00:00Z`);
  return Number.isNaN(d.getTime())?null:d;
}
function isoDate(date){return date?.toISOString().slice(0,10)||'';}
function urlState(){
  const u=new URL(location.href);
  const mode=['current','as_of','changed_between'].includes(u.searchParams.get('timeMode'))?u.searchParams.get('timeMode'):'current';
  return{mode,time:u.searchParams.get('time')||'',time2:u.searchParams.get('time2')||''};
}
function setUrl(state){
  const u=new URL(location.href);
  if(state.mode==='current'){
    u.searchParams.delete('timeMode');u.searchParams.delete('time');u.searchParams.delete('time2');
  }else{
    u.searchParams.set('timeMode',state.mode);
    state.time?u.searchParams.set('time',state.time):u.searchParams.delete('time');
    state.mode==='changed_between'&&state.time2?u.searchParams.set('time2',state.time2):u.searchParams.delete('time2');
  }
  history.replaceState(null,'',u);
}
function exactNorthSnapshot(dateString){
  if(!northHistory||!dateString)return null;
  return (northHistory.snapshots||[]).find(s=>String(s.period||'').startsWith(dateString))||null;
}
function nearestNorthContext(dateString){
  if(!northHistory||!dateString)return[];
  const target=parseDate(dateString);if(!target)return[];
  return(northHistory.snapshots||[]).map(s=>{
    const match=String(s.period||'').match(/(20\d{2}-\d{2}-\d{2})/);
    return{snapshot:s,date:match?parseDate(match[1]):null};
  }).filter(x=>x.date&&x.date<=target).sort((a,b)=>b.date-a.date).slice(0,1).map(x=>x.snapshot);
}
function modeLabel(state){
  if(state.mode==='as_of')return`As of ${state.time||'—'}`;
  if(state.mode==='changed_between')return`${state.time||'—'} → ${state.time2||'—'}`;
  return'Current';
}
function statusText(state){
  if(state.mode==='current')return'Current state';
  if(state.mode==='as_of')return`Historical context · ${state.time||'date needed'}`;
  return`Compare dates · ${state.time||'start'} → ${state.time2||'end'}`;
}
function renderContext(state){
  const panel=document.getElementById('panel');if(!panel)return;
  document.getElementById('atlasTimeCard')?.remove();
  if(state.mode==='current')return;
  const exact=state.mode==='as_of'?exactNorthSnapshot(state.time):null;
  const prior=state.mode==='as_of'&&!exact?nearestNorthContext(state.time):[];
  const card=document.createElement('div');
  card.id='atlasTimeCard';card.className='card';card.style.borderColor='#55656b';
  let north='';
  if(exact){
    const named=exact.explicit_named_arc||[];
    north=`<div class="row"><b>Exact recovered North formulation</b><br><span class="muted">${esc(exact.period)}</span>${exact.headline?`<br>${esc(exact.headline)}`:''}${named.length?`<br><small>${named.slice(0,12).map(esc).join(' · ')}${named.length>12?' · …':''}</small>`:''}</div>`;
  }else if(prior.length){
    north=`<div class="row"><b>Nearest exact recovered North snapshot</b><br><span class="muted">${esc(prior[0].period)}</span><br><small>This is context only; it is not silently projected forward as the selected date's membership.</small></div>`;
  }else{
    north='<div class="row"><b>North history</b><br><span class="muted">No exact dated project-field snapshot is safe to apply automatically at this date.</span></div>';
  }
  card.innerHTML=`<div class="eyebrow">Time · ${esc(modeLabel(state))}</div><h2 style="margin-top:5px">Historical investigation</h2><p class="muted">Time changes which state or evidence was valid or known. It does not change D-level, graph distance or geography.</p>${north}<div class="boundary">Current project Fields and empirical Networks are not automatically rewritten as historical layers. Unknown or approximate dates remain unknown/approximate rather than being forced into precise intervals.</div>`;
  panel.appendChild(card);
  window.__potatoAtlasUI?.setPanel?.(true,{persist:false});
}
function dispatch(state){
  const detail={...state,label:modeLabel(state),exactNorthSnapshot:state.mode==='as_of'?exactNorthSnapshot(state.time):null,unknownDatePolicy:contract?.unknown_date_policy?.default||'flag'};
  window.dispatchEvent(new CustomEvent('atlas-time-change',{detail}));
  const pill=document.getElementById(ID);if(pill){pill.textContent=statusText(state);pill.hidden=state.mode==='current';}
  renderContext(state);
}
function applyFromControls(){
  const mode=document.getElementById('timeMode')?.value||'current';
  const time=document.getElementById('timeDate')?.value||'';
  const time2=document.getElementById('timeDate2')?.value||'';
  const state={mode,time,time2};
  document.getElementById('timeDate').hidden=mode==='current';
  document.getElementById('timeDate2').hidden=mode!=='changed_between';
  setUrl(state);dispatch(state);
}
function installControls(){
  const pop=document.querySelector('#timeMenu .menu-pop');if(!pop)return;
  const initial=urlState();
  const mode=document.getElementById('timeMode'),date1=document.getElementById('timeDate'),date2=document.getElementById('timeDate2');
  mode.value=initial.mode;date1.value=initial.time;date2.value=initial.time2;
  [mode,date1,date2].forEach(node=>node?.addEventListener('change',applyFromControls));
  document.getElementById('timeNow')?.addEventListener('click',()=>{mode.value='current';date1.value='';date2.value='';applyFromControls();});
  applyFromControls();
}
async function boot(){
  const[c,n]=await Promise.all([fetch(CONTRACT_URL),fetch(NORTH_HISTORY_URL)]);
  if(!c.ok)throw new Error('Time contract unavailable');
  contract=await c.json();northHistory=n.ok?await n.json():null;
  installControls();
  window.__potatoAtlasTime={getState:urlState,setState(state){
    const mode=document.getElementById('timeMode');const d1=document.getElementById('timeDate');const d2=document.getElementById('timeDate2');
    if(mode)mode.value=state.mode||'current';if(d1)d1.value=state.time||'';if(d2)d2.value=state.time2||'';applyFromControls();
  }};
}
boot().catch(error=>console.warn('Atlas Time unavailable:',error));
