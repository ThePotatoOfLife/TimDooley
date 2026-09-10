const FORMAL_URL = '../data/axis-formal-lenses.json';
const DEPTH_URL = '../data/axis-depths.json';
const CONTROL_ID = 'axisOperatorAction';
const RUN_ID = 'axisOperatorRun';
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

const ACTIONS = {
  earth:{label:'Earth · return',dimension:4,icon:'●'},
  eye:{label:'Eye · observe',icon:'◉'},
  roots:{label:'Roots · provenance',dimension:3,icon:'⌄'},
  swamp:{label:'Swamp · feedback',dimension:2,icon:'≈'},
  door:{label:'Door · threshold',dimension:5,icon:'□'},
  spiral:{label:'Spiral · return/change',dimension:6,icon:'↻'},
  tree:{label:'Tree · expand relations',dimension:7,icon:'Y'},
  garden:{label:'Garden · compose',dimension:8,icon:'⌂'},
  relay:{label:'Relay · transmission',dimension:9,icon:'⇄'},
  mountain:{label:'Mountain · integrate',dimension:10,icon:'△'},
  north:{label:'North · meta-reference',dimension:11,icon:'↑'},
  reflect:{label:'Above / below · reflect',icon:'↕'}
};

function panel(){ return document.getElementById('panel'); }
function currentDimension(){ return window.__potatoAxisDepth?.getDimension?.() || Number(new URL(location.href).searchParams.get('axisD') || 4); }
function currentState(map){
  const center=map.getCenter();
  return {
    dimension: currentDimension(),
    center:[Number(center.lng.toFixed(2)),Number(center.lat.toFixed(2))],
    zoom:Number(map.getZoom().toFixed(2)),
    pitch:Number(map.getPitch().toFixed(1)),
    bearing:Number(map.getBearing().toFixed(1)),
    field:document.getElementById('axisFieldView')?.value || 'n/a',
    network:document.getElementById('empiricalNetworkView')?.value || 'n/a',
    relation:document.getElementById('relationType')?.value || 'all',
    traceDepth:document.getElementById('traceDepth')?.value || 'n/a'
  };
}
function setSelect(id,value){
  const el=document.getElementById(id); if(!el) return false;
  const option=[...el.options].find(o=>o.value===value); if(!option) return false;
  el.value=value; el.dispatchEvent(new Event('change',{bubbles:true})); return true;
}
function ensureActive(id){ const el=document.getElementById(id); if(el && !el.classList.contains('active')) el.click(); }
function setDimension(d,options){ window.__potatoAxisDepth?.setDimension?.(d,options); }
function setOpParam(name){ const url=new URL(location.href); if(name==='earth') url.searchParams.delete('op'); else url.searchParams.set('op',name); history.replaceState(null,'',url); }

function renderOperatorPanel(formal,depths,name,map,extra=''){
  const action=ACTIONS[name]; if(!action||!panel()) return;
  const dimension=action.dimension || currentDimension();
  const lens=formal.dimensions?.[String(dimension)] || null;
  const level=(depths.levels||[]).find(x=>Number(x.dimension)===Number(dimension));
  const state=currentState(map);
  panel().innerHTML=`
    <div class="eyebrow">Executable Atlas operator · ${esc(action.icon)} ${esc(action.label)}</div>
    <h1>${esc(level?.label || action.label)}</h1>
    <p class="muted">${esc(lens?.question || 'Inspect the same graph through a different transformation or representation.')}</p>
    <div class="boundary"><b>Operator boundary:</b> This action changes the Atlas view, filters, camera, graph expansion or interpretive state. It does not physically move reality between dimensions and does not convert mathematical analogy into empirical proof.</div>
    ${lens ? `<div class="card"><b>${esc(lens.label)}</b><p>${esc(lens.atlas_use || '')}</p><p class="muted">${esc(lens.mismatch || '')}</p></div>` : ''}
    ${extra}
    <div class="card"><b>Current observation</b><div class="row">D${state.dimension} · center ${state.center[0]}, ${state.center[1]} · zoom ${state.zoom} · pitch ${state.pitch}° · bearing ${state.bearing}°</div><div class="row">Field · ${esc(state.field)} · network · ${esc(state.network)}</div><div class="row">Relation · ${esc(state.relation)} · trace · ${esc(state.traceDepth)} hops</div></div>
    <div class="actions"><button id="operatorEarth">Return D4</button><button id="operatorDoor">North Door</button><button id="operatorEye">Observe state</button></div>`;
  document.getElementById('operatorEarth')?.addEventListener('click',()=>applyOperator('earth',formal,depths,map));
  document.getElementById('operatorDoor')?.addEventListener('click',()=>applyOperator('door',formal,depths,map));
  document.getElementById('operatorEye')?.addEventListener('click',()=>applyOperator('eye',formal,depths,map));
}

function applyOperator(name,formal,depths,map){
  const action=ACTIONS[name]||ACTIONS.earth;
  setOpParam(name);
  let extra='';

  if(name==='earth'){
    setDimension(4);
    document.getElementById('world')?.click();
    extra='<div class="card"><b>Earth operator</b><p class="muted">Return to the geographic anchor. Symbolic operators remain available but the base representation is again ordinary world space.</p></div>';
  } else if(name==='eye'){
    const state=currentState(map);
    extra=`<div class="card"><b>Eye · observation map</b><p class="muted">The Eye does not claim omniscience. It snapshots what this interface currently exposes and makes uncertainty/filters explicit.</p><div class="row">Observed representation · D${state.dimension}</div><div class="row">Active field/network · ${esc(state.field)} / ${esc(state.network)}</div><div class="row">Active relation filter · ${esc(state.relation)}</div></div>`;
  } else if(name==='roots'){
    setDimension(3);
    extra='<div class="card"><b>Roots</b><p class="muted">Shift the question from “where is it?” to “what preceded it, what evidence remains, and what alternative causal histories are represented?” D3 provenance tooling remains the preferred factual root view.</p></div>';
  } else if(name==='swamp'){
    setDimension(2);
    ensureActive('relations');
    setSelect('traceDepth','3');
    extra='<div class="card"><b>Feedback expansion</b><p class="muted">Relations are enabled and trace depth is widened to three hops so repeated/third-party structure can become visible. This is a network diagnostic, not a moral stain on places or people.</p></div>';
  } else if(name==='door'){
    setDimension(5);
    window.__potatoAxisDepth?.focusNorth?.();
    extra='<div class="card"><b>Door</b><p class="muted">The camera is returned to the North threshold. A rigorous Door needs an explicit guard or condition before a represented state transition is claimed.</p></div>';
  } else if(name==='spiral'){
    setDimension(6,{silentCamera:true});
    map.easeTo({center:[-36,80],zoom:Math.max(map.getZoom(),2.75),pitch:58,bearing:map.getBearing()+115,duration:1300});
    extra='<div class="card"><b>Return with change</b><p class="muted">The view rotates while remaining anchored to the same North region. Use this operator for repeated historical/system states only when a delta—scale, phase, capability, topology or evidence—can be shown.</p></div>';
  } else if(name==='tree'){
    setDimension(7);
    ensureActive('relations'); ensureActive('interior'); setSelect('traceDepth','3');
    extra='<div class="card"><b>Tree expansion</b><p class="muted">Relations and semantic interior handles are enabled and trace depth is widened. Tree should expand lineage, dependencies, consequences or capabilities from a selected real node rather than draw decorative branches.</p></div>';
  } else if(name==='garden'){
    setDimension(8);
    setSelect('axisFieldView','all');
    extra='<div class="card"><b>Garden composition</b><p class="muted">All project fields are made visible so overlaps and differentiated participation can be compared. A later viability layer can score whether arrangements preserve resilience and autonomous capacity under explicit constraints.</p></div>';
  } else if(name==='relay'){
    setDimension(9);
    ensureActive('relations');
    extra='<div class="card"><b>Relay</b><p class="muted">Relations stay visible because D9 asks what crosses an edge: message, standard, knowledge, resource, obligation or signal—and what is lost or distorted in transmission.</p></div>';
  } else if(name==='mountain'){
    setDimension(10,{silentCamera:true});
    map.easeTo({center:[10,43],zoom:1.45,pitch:60,bearing:18,duration:1200});
    extra='<div class="card"><b>Mountain compression</b><p class="muted">The camera widens toward system scale. This is a many-to-one analytical move: aggregate details into larger systems while explicitly remembering that aggregation loses information.</p></div>';
  } else if(name==='north'){
    setDimension(11,{silentCamera:true});
    map.easeTo({center:[-36,81.5],zoom:2.7,pitch:72,bearing:0,duration:1200});
    extra='<div class="card"><b>Meta-reference</b><p class="muted">North of North asks which criterion survives changes of representation and whether a claimed orientation can descend back into D10 service and D4 observable consequences.</p></div>';
  } else if(name==='reflect'){
    const up=depths.reflection_law?.upward_example||'';
    const down=depths.reflection_law?.downward_example||'';
    extra=`<div class="card"><b>Above / below reflection</b><div class="row">↑ ${esc(up)}</div><div class="row">↓ ${esc(down)}</div><p class="muted">No one-to-one mirrored floor is asserted. The operator compares how the same starting material behaves under integrative versus disintegrative transformations.</p></div>`;
  }

  renderOperatorPanel(formal,depths,name,map,extra);
  window.dispatchEvent(new CustomEvent('atlas-symbolic-operator',{detail:{name,dimension:action.dimension||currentDimension()}}));
}

function installControls(formal,depths,map){
  if(document.getElementById(CONTROL_ID)) return;
  const relation=document.getElementById('relationType');
  const select=document.createElement('select'); select.id=CONTROL_ID; select.title='Execute symbolic/formal Atlas operator';
  select.innerHTML=Object.entries(ACTIONS).map(([id,a])=>`<option value="${id}">${a.icon} ${esc(a.label)}</option>`).join('');
  const run=document.createElement('button'); run.id=RUN_ID; run.textContent='Run'; run.title='Apply selected Atlas operator';
  relation?.insertAdjacentElement('beforebegin',select); select.insertAdjacentElement('afterend',run);
  const requested=new URL(location.href).searchParams.get('op'); if(requested&&ACTIONS[requested]) select.value=requested;
  run.addEventListener('click',()=>applyOperator(select.value,formal,depths,map));
  select.addEventListener('change',()=>applyOperator(select.value,formal,depths,map));
  window.__potatoSymbolicOperators={formal,depths,actions:ACTIONS,apply:name=>applyOperator(name,formal,depths,map),state:()=>currentState(map)};
}

async function boot(){
  const [formalRes,depthRes]=await Promise.all([fetch(FORMAL_URL),fetch(DEPTH_URL)]);
  if(!formalRes.ok||!depthRes.ok) throw new Error('Symbolic operator data unavailable');
  const [formal,depths]=await Promise.all([formalRes.json(),depthRes.json()]);
  for(let i=0;i<140&&!window.__potatoAtlasMap;i+=1) await new Promise(r=>setTimeout(r,50));
  const map=window.__potatoAtlasMap; if(!map) return;
  for(let i=0;i<140&&!window.__potatoAxisDepth;i+=1) await new Promise(r=>setTimeout(r,50));
  installControls(formal,depths,map);
}
boot().catch(error=>console.warn('Executable symbolic operators unavailable:',error));
