const REL_URL='../data/relationships.json';
const NODES_URL='../data/nodes.json';
const COUNTRIES_URL='../data/countries/index.json';
const BRIDGE_URL='../data/global-graph-bridge.json';
const CARD_ID='entityTraceCard';
const EVIDENCE_ID='entityEvidenceFilter';
const CONFIDENCE_ID='entityConfidenceFilter';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data=null;
let enabled=localStorage.getItem('atlas:entity-trace')==='1';
let evidenceFilter=localStorage.getItem('atlas:entity-evidence')||'all';
let confidenceFilter=localStorage.getItem('atlas:entity-confidence')||'all';
let lastCode=null;
let rendering=false;
let renderQueued=false;

async function fetchJson(url){const r=await fetch(url);if(!r.ok)throw new Error(`${url} returned HTTP ${r.status}`);return r.json();}
async function load(){
  if(data)return data;
  const[relationships,nodes,countries,bridge]=await Promise.all([fetchJson(REL_URL),fetchJson(NODES_URL),fetchJson(COUNTRIES_URL),fetchJson(BRIDGE_URL)]);
  const countryRows=countries.countries||[];
  data={
    relationships:relationships.relationships||[],
    nodes:Object.fromEntries((nodes.nodes||[]).map(n=>[n.id,n])),
    countriesByIso:Object.fromEntries(countryRows.map(c=>[c.iso3,c])),
    countriesById:Object.fromEntries(countryRows.map(c=>[c.id,c])),
    bridge,
    explicitBridges:Object.fromEntries((bridge.explicit_bridges||[]).map(row=>[row.id,row]))
  };
  return data;
}
function selectedCode(){
  const current=window.__potatoAtlasSelection?.current||{};
  return String(current.activeCode||current.code||new URL(location.href).searchParams.get('country')||'').toUpperCase()||null;
}
function selectedTime(){return window.__potatoAtlasTime?.getState?.()||{mode:'current',time:'',time2:''};}
function endpointName(id,d){return d.nodes[id]?.name||d.countriesById[id]?.name||id.replaceAll('-',' ').replace(/\b\w/g,m=>m.toUpperCase());}
function archiveRoute(id,d){
  const explicit=d.explicitBridges[id]?.route;
  if(explicit)return `../${explicit}`;
  if(d.nodes[id]||d.countriesById[id])return `../${d.bridge.public_reader||'index.html'}#node=${encodeURIComponent(id)}`;
  return null;
}
function temporalState(rel,time){
  if(time.mode==='current')return{kind:'current',label:''};
  const selected=time.time;
  if(!selected)return{kind:'unknown',label:'time date needed'};
  if(rel.valid_from||rel.valid_to){
    const start=rel.valid_from||'0000-01-01',end=rel.valid_to||'9999-12-31';
    return selected>=start&&selected<=end?{kind:'valid',label:'valid at selected date'}:{kind:'outside',label:'outside represented validity interval'};
  }
  return{kind:'unknown',label:'validity unknown'};
}
function passesFilters(rel){
  if(evidenceFilter!=='all'&&(rel.evidence||'unknown')!==evidenceFilter)return false;
  if(confidenceFilter!=='all'&&(rel.confidence||'unknown')!==confidenceFilter)return false;
  return true;
}
function relationRows(countryId,d,time){
  return d.relationships.filter(r=>(r.source===countryId||r.target===countryId)&&passesFilters(r)).map(r=>{
    const outgoing=r.source===countryId,other=outgoing?r.target:r.source,country=d.countriesById[other];
    return{...r,outgoing,other,otherName:endpointName(other,d),otherCountry:country?.iso3||null,archiveRoute:archiveRoute(other,d),timeState:temporalState(r,time)};
  });
}
function removeCard(){document.getElementById(CARD_ID)?.remove();}
function endpointAction(row){
  if(row.otherCountry)return `<button type="button" data-trace-country="${esc(row.otherCountry)}">Map</button>`;
  if(row.archiveRoute)return `<a href="${esc(row.archiveRoute)}">Archive</a>`;
  return '<span class="muted">inspector only</span>';
}
function openInspector(){document.getElementById('atlasApp')?.classList.remove('panel-collapsed');}
function emit(){window.dispatchEvent(new CustomEvent('potato-atlas-entity-trace-change',{detail:{enabled,evidence:evidenceFilter,confidence:confidenceFilter}}));}

function scheduleRender(){
  if(renderQueued)return;
  renderQueued=true;
  queueMicrotask(render);
}

function filterOptions(values,current,allLabel){
  return `<option value="all">${esc(allLabel)}</option>${values.map(v=>`<option value="${esc(v)}"${v===current?' selected':''}>${esc(v)}</option>`).join('')}`;
}

function wireCard(card){
  card.querySelector(`#${EVIDENCE_ID}`)?.addEventListener('change',event=>{
    evidenceFilter=event.target.value||'all';
    localStorage.setItem('atlas:entity-evidence',evidenceFilter);
    scheduleRender();
    emit();
  });
  card.querySelector(`#${CONFIDENCE_ID}`)?.addEventListener('change',event=>{
    confidenceFilter=event.target.value||'all';
    localStorage.setItem('atlas:entity-confidence',confidenceFilter);
    scheduleRender();
    emit();
  });
  card.querySelector('[data-trace-close]')?.addEventListener('click',()=>setEnabled(false));
  card.addEventListener('click',event=>{
    const code=event.target.closest('[data-trace-country]')?.dataset.traceCountry;
    if(code)window.goCountry?.(code);
  });
}

async function render(){
  if(rendering){renderQueued=true;return;}
  renderQueued=false;
  rendering=true;
  try{
    removeCard();
    if(!enabled)return;
    const code=selectedCode();lastCode=code;if(!code)return;
    const d=await load();
    if(selectedCode()!==code){scheduleRender();return;}
    const country=d.countriesByIso[code];if(!country)return;
    const time=selectedTime(),rows=relationRows(country.id,d,time);
    const panel=document.getElementById('panel');if(!panel)return;
    openInspector();
    const counts={};for(const r of rows)counts[r.evidence||'unknown']=(counts[r.evidence||'unknown']||0)+1;
    const valid=rows.filter(r=>r.timeState.kind==='valid').length,unknown=rows.filter(r=>r.timeState.kind==='unknown').length,outside=rows.filter(r=>r.timeState.kind==='outside').length;
    const evidenceValues=[...new Set(d.relationships.map(r=>r.evidence||'unknown'))].sort();
    const confidenceValues=[...new Set(d.relationships.map(r=>r.confidence||'unknown'))].sort();
    if(!evidenceValues.includes(evidenceFilter))evidenceFilter='all';
    if(!confidenceValues.includes(confidenceFilter))confidenceFilter='all';
    const card=document.createElement('section');card.id=CARD_ID;card.className='card';card.style.borderColor='#435b63';
    const evidenceTags=Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<span class="pill">${esc(k)} · ${v}</span>`).join('');
    card.innerHTML=`
      <div style="display:flex;justify-content:space-between;gap:10px;align-items:start"><div><div class="eyebrow">Entity Trace · normalized graph</div><h2 style="margin-top:5px">${esc(country.name)} beyond country-only edges</h2></div><button type="button" data-trace-close aria-label="Close entity trace">×</button></div>
      <p class="muted">One-hop relationships from <code>data/relationships.json</code>, resolved through the global graph bridge. Nonspatial endpoints remain inspector/archive objects; only canonical country endpoints can jump back to Earth geography.</p>
      <div class="grid" style="margin:8px 0"><label class="metric"><span>Evidence class</span><select id="${EVIDENCE_ID}" style="width:100%;margin-top:4px">${filterOptions(evidenceValues,evidenceFilter,'All evidence classes')}</select></label><label class="metric"><span>Confidence</span><select id="${CONFIDENCE_ID}" style="width:100%;margin-top:4px">${filterOptions(confidenceValues,confidenceFilter,'All confidence levels')}</select></label></div>
      <div>${evidenceTags||'<span class="muted">No normalized relationships match the active filters.</span>'}</div>
      ${time.mode!=='current'?`<div class="row"><b>Time validity</b><br><span class="muted">${valid} explicitly valid · ${outside} outside interval · ${unknown} unknown validity. A relation's record date is not treated as its start date.</span></div>`:''}
      <div>${rows.slice(0,24).map(r=>`<div class="row"><span class="muted">${r.outgoing?'→':'←'} ${esc(r.relationship)}</span><br><b>${esc(r.otherName)}</b> ${endpointAction(r)}<br><small>${esc(r.evidence||'unknown')} · ${esc(r.confidence||'unknown')}${r.date?` · recorded ${esc(r.date)}`:''}${time.mode!=='current'?` · ${esc(r.timeState.label)}`:''}</small></div>`).join('')||'<div class="muted">No normalized graph edges touch this country under the active filters.</div>'}</div>
      ${rows.length>24?`<div class="muted">Showing 24 of ${rows.length} one-hop entity relations.</div>`:''}
      <div class="boundary">Entity Trace expands topology, not geography. Evidence and confidence filters preserve the graph's existing classifications; they are not a truth score. A nonspatial endpoint is never assigned a fake map position merely because it is connected to a country.</div>`;
    panel.prepend(card);
    wireCard(card);
  }catch(error){
    console.warn('Entity Trace unavailable:',error);
  }finally{
    rendering=false;
    if(renderQueued){renderQueued=false;queueMicrotask(render);}
  }
}

function setEnabled(next){
  enabled=Boolean(next);
  localStorage.setItem('atlas:entity-trace',enabled?'1':'0');
  if(enabled)openInspector();
  scheduleRender();
  emit();
  return enabled;
}
function toggle(){return setEnabled(!enabled);}

// The canonical working selection owns country choice. Trace follows it rather
// than installing a second country selector or depending on a legacy menu.
window.addEventListener('potato-atlas-working-selection-change',event=>{
  const code=String(event?.detail?.activeCode||event?.detail?.code||'').toUpperCase()||null;
  if(code!==lastCode&&enabled)scheduleRender();
});
window.addEventListener('atlas-time-change',()=>enabled&&scheduleRender());

window.__potatoEntityTrace={
  render:scheduleRender,
  isEnabled:()=>enabled,
  getFilters:()=>({evidence:evidenceFilter,confidence:confidenceFilter}),
  setEnabled,
  toggle
};

if(enabled)scheduleRender();
emit();
