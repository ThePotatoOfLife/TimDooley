import { normalizeTimeState, describeTimeWindow } from './3d-time-policy.js';

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
function urlState(){
  const u=new URL(location.href);
  return normalizeTimeState({
    mode:u.searchParams.get('timeMode')||'current',
    time:u.searchParams.get('time')||'',
    time2:u.searchParams.get('time2')||'',
  });
}
function setUrl(input){
  const state=normalizeTimeState(input);
  const u=new URL(location.href);
  if(state.mode==='current'){
    u.searchParams.delete('timeMode');u.searchParams.delete('time');u.searchParams.delete('time2');
  }else{
    u.searchParams.set('timeMode',state.mode);
    state.time?u.searchParams.set('time',state.time):u.searchParams.delete('time');
    state.mode==='changed_between'&&state.time2?u.searchParams.set('time2',state.time2):u.searchParams.delete('time2');
  }
  history.replaceState(null,'',u);
  return state;
}
function exactNorthSnapshot(dateString){
  if(!northHistory||!dateString)return null;
  return(northHistory.snapshots||[]).find(s=>String(s.period||'').startsWith(dateString))||null;
}
function nearestNorthContext(dateString){
  if(!northHistory||!dateString)return[];
  const target=parseDate(dateString);if(!target)return[];
  return(northHistory.snapshots||[]).map(s=>{
    const match=String(s.period||'').match(/(20\d{2}-\d{2}-\d{2})/);
    return{snapshot:s,date:match?parseDate(match[1]):null};
  }).filter(x=>x.date&&x.date<=target).sort((a,b)=>b.date-a.date).slice(0,1).map(x=>x.snapshot);
}
function modeLabel(input){
  const state=describeTimeWindow(input);
  if(state.mode==='as_of')return`As of ${state.time||'—'}`;
  if(state.mode==='changed_between')return state.label;
  return'Current';
}
function statusText(input){
  const state=describeTimeWindow(input);
  if(state.mode==='current')return'Current state';
  if(!state.valid)return`Time needs attention · ${state.issue||'invalid window'}`;
  if(state.mode==='as_of')return`Historical context · ${state.time}`;
  return`Compare dates · ${state.label}${Number.isFinite(state.days)?` · ${state.days} days`:''}`;
}
function issueText(state){
  if(state.valid&&state.issue==='reordered-range')return'<div class="boundary">The comparison dates were reversed, so the Atlas normalized them into chronological order.</div>';
  if(state.valid)return'';
  const labels={
    'missing-date':'Choose a valid date for this Time mode.',
    'invalid-date':'One of the selected dates is not a valid calendar date.',
    'missing-range-end':'Choose both a start and end date for Changed between.',
  };
  return`<div class="boundary">${esc(labels[state.issue]||'The selected Time window is incomplete or invalid.')}</div>`;
}
function renderContext(input){
  const state=describeTimeWindow(input);
  const panel=document.getElementById('panel');if(!panel)return;
  document.getElementById('atlasTimeCard')?.remove();
  if(state.mode==='current')return;
  const exact=state.mode==='as_of'&&state.valid?exactNorthSnapshot(state.time):null;
  const prior=state.mode==='as_of'&&state.valid&&!exact?nearestNorthContext(state.time):[];
  const card=document.createElement('div');
  card.id='atlasTimeCard';card.className='card';card.style.borderColor='#55656b';
  let north='';
  if(!state.valid){
    north='<div class="row"><b>Historical context paused</b><br><span class="muted">The Atlas will not infer dated state until the Time window is valid.</span></div>';
  }else if(exact){
    const named=exact.explicit_named_arc||[];
    north=`<div class="row"><b>Exact recovered North formulation</b><br><span class="muted">${esc(exact.period)}</span>${exact.headline?`<br>${esc(exact.headline)}`:''}${named.length?`<br><small>${named.slice(0,12).map(esc).join(' · ')}${named.length>12?' · …':''}</small>`:''}</div>`;
  }else if(prior.length){
    north=`<div class="row"><b>Nearest exact recovered North snapshot</b><br><span class="muted">${esc(prior[0].period)}</span><br><small>This is context only; it is not silently projected forward as the selected date's membership.</small></div>`;
  }else if(state.mode==='as_of'){
    north='<div class="row"><b>North history</b><br><span class="muted">No exact dated project-field snapshot is safe to apply automatically at this date.</span></div>';
  }
  const rangeInfo=state.mode==='changed_between'&&state.valid?`<div class="row"><b>Comparison window</b><br>${esc(state.label)}${Number.isFinite(state.days)?`<br><span class="muted">${state.days} days</span>`:''}</div>`:'';
  card.innerHTML=`<div class="eyebrow">Time · ${esc(modeLabel(state))}</div><h2 style="margin-top:5px">Historical investigation</h2><p class="muted">Time changes which state or evidence was valid or known. It does not change D-level, graph distance or geography.</p>${issueText(state)}${rangeInfo}${north}<div class="boundary">Current project Fields and empirical Networks are not automatically rewritten as historical layers. Unknown or approximate dates remain unknown/approximate rather than being forced into precise intervals.</div>`;
  panel.appendChild(card);
  window.__potatoAtlasUI?.setPanel?.(true,{persist:false});
}
function dispatch(input){
  const state=describeTimeWindow(input);
  const detail={
    ...state,
    label:modeLabel(state),
    exactNorthSnapshot:state.mode==='as_of'&&state.valid?exactNorthSnapshot(state.time):null,
    unknownDatePolicy:contract?.unknown_date_policy?.default||'flag',
  };
  window.dispatchEvent(new CustomEvent('atlas-time-change',{detail}));
  const pill=document.getElementById(ID);if(pill){pill.textContent=statusText(state);pill.hidden=state.mode==='current';pill.dataset.valid=String(state.valid);}
  renderContext(state);
  return detail;
}
function syncControls(state){
  const mode=document.getElementById('timeMode'),date1=document.getElementById('timeDate'),date2=document.getElementById('timeDate2');
  if(mode)mode.value=state.mode;
  if(date1){date1.value=state.time||'';date1.hidden=state.mode==='current';}
  if(date2){date2.value=state.time2||'';date2.hidden=state.mode!=='changed_between';}
}
function applyFromControls(){
  const requested={
    mode:document.getElementById('timeMode')?.value||'current',
    time:document.getElementById('timeDate')?.value||'',
    time2:document.getElementById('timeDate2')?.value||'',
  };
  const state=setUrl(requested);
  syncControls(state);
  return dispatch(state);
}
function installControls(){
  const pop=document.querySelector('#timeMenu .menu-pop');if(!pop)return;
  const initial=urlState();
  syncControls(initial);
  ['timeMode','timeDate','timeDate2'].forEach(id=>document.getElementById(id)?.addEventListener('change',applyFromControls));
  document.getElementById('timeNow')?.addEventListener('click',()=>{
    const state=setUrl({mode:'current'});syncControls(state);dispatch(state);
  });
  const normalized=setUrl(initial);syncControls(normalized);dispatch(normalized);
}
async function boot(){
  const[c,n]=await Promise.all([fetch(CONTRACT_URL),fetch(NORTH_HISTORY_URL)]);
  if(!c.ok)throw new Error('Time contract unavailable');
  contract=await c.json();northHistory=n.ok?await n.json():null;
  installControls();
  window.__potatoAtlasTime={
    getState:urlState,
    describe(){return describeTimeWindow(urlState());},
    setState(input){const state=setUrl(input);syncControls(state);return dispatch(state);},
  };
}
boot().catch(error=>console.warn('Atlas Time unavailable:',error));
