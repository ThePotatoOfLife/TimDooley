const REL_URL='../data/relationships.json';
const NODES_URL='../data/nodes.json';
const COUNTRIES_URL='../data/countries/index.json';
const BRIDGE_URL='../data/global-graph-bridge.json';
const CARD_ID='entityTraceCard';
const BUTTON_ID='entityTraceToggle';
const EVIDENCE_ID='entityEvidenceFilter';
const CONFIDENCE_ID='entityConfidenceFilter';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data=null;
let enabled=localStorage.getItem('atlas:entity-trace')==='1';
let evidenceFilter=localStorage.getItem('atlas:entity-evidence')||'all';
let confidenceFilter=localStorage.getItem('atlas:entity-confidence')||'all';
let lastCode=null;

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
function selectedCode(){return new URL(location.href).searchParams.get('country')?.toUpperCase()||null;}
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
  if(row.otherCountry)return `<button onclick="goCountry('${esc(row.otherCountry)}')">Map</button>`;
  if(row.archiveRoute)return `<a href="${esc(row.archiveRoute)}">Archive</a>`;
  return '<span class="muted">inspector only</span>';
}
async function render(){
  removeCard();if(!enabled)return;
  const code=selectedCode();lastCode=code;if(!code)return;
  try{
    const d=await load();if(selectedCode()!==code)return render();
    const country=d.countriesByIso[code];if(!country)return;
    const time=selectedTime(),rows=relationRows(country.id,d,time);
    const panel=document.getElementById('panel');if(!panel)return;
    const counts={};for(const r of rows)counts[r.evidence||'unknown']=(counts[r.evidence||'unknown']||0)+1;
    const valid=rows.filter(r=>r.timeState.kind==='valid').length,unknown=rows.filter(r=>r.timeState.kind==='unknown').length,outside=rows.filter(r=>r.timeState.kind==='outside').length;
    const card=document.createElement('div');card.id=CARD_ID;card.className='card';card.style.borderColor='#435b63';
    const evidenceTags=Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<span class="pill">${esc(k)} · ${v}</span>`).join('');
    const filterSummary=[evidenceFilter!=='all'?`evidence=${evidenceFilter}`:'',confidenceFilter!=='all'?`confidence=${confidenceFilter}`:''].filter(Boolean).join(' · ');
    card.innerHTML=`<div class="eyebrow">Entity Trace · normalized graph</div><h2 style="margin-top:5px">${esc(country.name)} beyond country-only edges</h2><p class="muted">One-hop relationships from <code>data/relationships.json</code>, resolved through the global graph bridge. Nonspatial endpoints remain inspector/archive objects; only canonical country endpoints can jump back to Earth geography.</p>${filterSummary?`<div class="row"><b>Active filter</b><br><span class="muted">${esc(filterSummary)}</span></div>`:''}<div>${evidenceTags||'<span class="muted">No normalized relationships match the active filters.</span>'}</div>${time.mode!=='current'?`<div class="row"><b>Time validity</b><br><span class="muted">${valid} explicitly valid · ${outside} outside interval · ${unknown} unknown validity. A relation's record date is not treated as its start date.</span></div>`:''}<div>${rows.slice(0,24).map(r=>`<div class="row"><span class="muted">${r.outgoing?'→':'←'} ${esc(r.relationship)}</span><br><b>${esc(r.otherName)}</b> ${endpointAction(r)}<br><small>${esc(r.evidence||'unknown')} · ${esc(r.confidence||'unknown')}${r.date?` · recorded ${esc(r.date)}`:''}${time.mode!=='current'?` · ${esc(r.timeState.label)}`:''}</small></div>`).join('')||'<div class="muted">No normalized graph edges touch this country under the active filters.</div>'}</div>${rows.length>24?`<div class="muted">Showing 24 of ${rows.length} one-hop entity relations.</div>`:''}<div class="boundary">Entity Trace expands topology, not geography. Evidence and confidence filters preserve the graph's existing classifications; they are not a truth score. A nonspatial endpoint is never assigned a fake map position merely because it is connected to a country.</div>`;
    panel.appendChild(card);window.__potatoAtlasUI?.setPanel?.(true,{persist:false});
  }catch(error){console.warn('Entity Trace unavailable:',error);}
}
async function installFilters(pop){
  const d=await load();
  if(!document.getElementById(EVIDENCE_ID)){
    const title=document.createElement('div');title.className='menu-title';title.textContent='Entity evidence';pop.appendChild(title);
    const evidence=document.createElement('select');evidence.id=EVIDENCE_ID;evidence.title='Filter normalized entity relationships by evidence class';
    const values=[...new Set(d.relationships.map(r=>r.evidence||'unknown'))].sort();
    evidence.innerHTML='<option value="all">All evidence classes</option>'+values.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
    evidence.value=values.includes(evidenceFilter)?evidenceFilter:'all';evidenceFilter=evidence.value;
    evidence.addEventListener('change',()=>{evidenceFilter=evidence.value;localStorage.setItem('atlas:entity-evidence',evidenceFilter);render();window.__potatoAtlasUI?.updateMenuSummaries?.();});pop.appendChild(evidence);
  }
  if(!document.getElementById(CONFIDENCE_ID)){
    const confidence=document.createElement('select');confidence.id=CONFIDENCE_ID;confidence.title='Filter normalized entity relationships by confidence';
    const values=[...new Set(d.relationships.map(r=>r.confidence||'unknown'))].sort();
    confidence.innerHTML='<option value="all">All confidence levels</option>'+values.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
    confidence.value=values.includes(confidenceFilter)?confidenceFilter:'all';confidenceFilter=confidence.value;
    confidence.addEventListener('change',()=>{confidenceFilter=confidence.value;localStorage.setItem('atlas:entity-confidence',confidenceFilter);render();window.__potatoAtlasUI?.updateMenuSummaries?.();});pop.appendChild(confidence);
  }
}
function install(){
  if(document.getElementById(BUTTON_ID))return;
  const pop=document.querySelector('#traceMenu .menu-pop');if(!pop)return;
  const button=document.createElement('button');button.id=BUTTON_ID;button.textContent=enabled?'Entity graph · on':'Entity graph';button.title='Show normalized country→entity relationships in the inspector';button.classList.toggle('active',enabled);
  button.addEventListener('click',()=>{enabled=!enabled;localStorage.setItem('atlas:entity-trace',enabled?'1':'0');button.textContent=enabled?'Entity graph · on':'Entity graph';button.classList.toggle('active',enabled);render();window.__potatoAtlasUI?.updateMenuSummaries?.();});
  pop.appendChild(button);installFilters(pop).catch(error=>console.warn('Entity Trace filters unavailable:',error));render();
}
const panel=document.getElementById('panel');if(panel)new MutationObserver(()=>{if(enabled&&selectedCode()!==lastCode)queueMicrotask(render);else if(enabled&&selectedCode()&&!document.getElementById(CARD_ID))queueMicrotask(render);}).observe(panel,{childList:true,subtree:false});
window.addEventListener('atlas-time-change',()=>enabled&&render());
new MutationObserver(install).observe(document.body,{childList:true,subtree:true});install();
window.__potatoEntityTrace={render,isEnabled:()=>enabled,getFilters:()=>({evidence:evidenceFilter,confidence:confidenceFilter})};
