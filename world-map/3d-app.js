import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

const URL = {
  geo: 'https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json',
  rest: 'https://restcountries.com/v3.1/all?fields=name,cca3,population,area,latlng,capital,region,subregion,borders',
  index: '../data/countries/index.json',
  world: '../data/world-relational-map.json'
};
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const fmt = n => n == null ? '—' : new Intl.NumberFormat('en', {notation: Math.abs(n) > 1e9 ? 'compact' : 'standard', maximumFractionDigits: 1}).format(n);
const title = s => String(s || '').replaceAll('_', ' ').replace(/\b\w/g, m => m.toUpperCase());
const emptyFC = () => ({type:'FeatureCollection', features:[]});

const status = $('#status');
function setStatus(message, kind='info') {
  if (!status) return;
  status.textContent = message;
  status.dataset.kind = kind;
  status.hidden = !message;
}

let geo, rest, index, worldCfg;
try {
  setStatus('Loading geography and canonical country data…');
  [geo, rest, index, worldCfg] = await Promise.all(Object.values(URL).map(async u => {
    const r = await fetch(u);
    if (!r.ok) throw new Error(`${r.status} ${u}`);
    return r.json();
  }));
  setStatus('');
} catch (error) {
  console.error(error);
  setStatus('Atlas data failed to load. Check your connection and reload.', 'error');
  $('#panel').innerHTML = '<div class="eyebrow">Loading error</div><h1>Atlas data unavailable</h1><p class="muted">The renderer could not load one or more geography/data dependencies. The canonical repository data remains unchanged. Reload when connectivity is restored.</p>';
  throw error;
}

const countries = Array.isArray(index) ? index : (index.countries || index.items || []);
const index3 = Object.fromEntries(countries.map(x => [x.iso3 || x.cca3 || x.code, x]).filter(x => x[0]));
const byName = new Map(rest.flatMap(x => [[x.name?.common, x], [x.name?.official, x]].filter(y => y[0])));
const by3 = Object.fromEntries(rest.filter(x => x.cca3).map(x => [x.cca3, x]));
const cache = new Map();

for (const f of geo.features) {
  const r = by3[f.id] || byName.get(f.properties?.name);
  f.properties.iso3 = r?.cca3 || f.id || '';
  f.properties.population = r?.population || 0;
  f.properties.area = r?.area || 0;
  f.properties.capital = (r?.capital || []).join(', ');
  f.properties.region = r?.region || '';
  f.properties.subregion = r?.subregion || '';
}

const featureByCode = code => geo.features.find(x => x.properties.iso3 === code);
const map = new maplibregl.Map({
  container: 'map',
  style: {version:8, sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap contributors'}}, layers:[{id:'osm',type:'raster',source:'osm',paint:{'raster-opacity':.25}}]},
  center:[5,24], zoom:1.5, pitch:0, bearing:0, maxZoom:10
});
map.addControl(new maplibregl.NavigationControl({visualizePitch:true}));

let selected = null;
let selectedFeature = null;
let globe = false;
let showInterior = true;
let showRelations = true;
let currentCanonical = null;
let compareMode = false;
let compareCodes = [];
let relationType = 'all';
let traceDepth = 1;
const TRACE_MAX_DEPTH = 3;
const TRACE_MAX_NODES = 60;
const TRACE_MAX_EDGES = 120;

const HUBS = [
  {id:'religion',label:'Religion / Irreligion',keys:['religion','society_and_culture'],plane:'observable'},
  {id:'government',label:'Government / Law',keys:['political_system','government','law_and_rights','public_administration'],plane:'observable'},
  {id:'economy',label:'Economy / Money',keys:['economy','money_and_finance'],plane:'observable'},
  {id:'debt',label:'Physical Debt / Finance',keys:['public_finance'],plane:'observable'},
  {id:'trade',label:'Trade / Supply Chains',keys:['trade_and_value_chains','international_position'],plane:'observable'},
  {id:'energy',label:'Energy / Resources',keys:['energy','natural_resources_and_ecology'],plane:'observable'},
  {id:'infrastructure',label:'Infrastructure / Mobility',keys:['infrastructure','transport_and_mobility'],plane:'observable'},
  {id:'ownership',label:'Companies / Ownership',keys:['ownership_and_control'],plane:'observable'},
  {id:'security',label:'Security / Alliances',keys:['military_and_security','security','alliances_and_external_relations','intelligence_and_security_relationships'],plane:'observable'},
  {id:'science',label:'Science / Technology',keys:['science_technology_and_innovation','education'],plane:'observable'},
  {id:'migration',label:'Migration / Diaspora',keys:['migration_and_diaspora','population'],plane:'observable'},
  {id:'history',label:'History / Time',keys:['history'],plane:'historical'},
  {id:'relations',label:'Relationships',keys:['relationships'],plane:'mixed'},
  {id:'north',label:'North / Programme',keys:[],plane:'interpretive-policy'},
  {id:'tim',label:'Tim / Project Canon',keys:[],plane:'project-canon'}
];

function mode() {
  const z = map.getZoom();
  return z < 3 ? 'world' : z < 5 ? 'regional' : z < 7 ? 'country' : 'subnational';
}
function relationEdgesFor(code) {
  return (worldCfg.curated_edges || []).filter(e => (e.a === code || e.b === code) && (relationType === 'all' || (e.types || []).includes(relationType)));
}
function edgeKey(edge) {
  return [edge.a, edge.b].sort().join('|') + '|' + (edge.types || []).slice().sort().join(',') + '|' + (edge.layer || '');
}
function traceGraph(root, depth=traceDepth) {
  const maxDepth = Math.max(1, Math.min(TRACE_MAX_DEPTH, Number(depth) || 1));
  const visited = new Map([[root, 0]]);
  const queue = [root];
  const edges = [];
  const seenEdges = new Set();
  const parents = new Map();
  let truncated = false;

  while (queue.length) {
    const code = queue.shift();
    const level = visited.get(code) || 0;
    if (level >= maxDepth) continue;
    for (const edge of relationEdgesFor(code)) {
      const other = edge.a === code ? edge.b : edge.a;
      const key = edgeKey(edge);
      if (!seenEdges.has(key)) {
        seenEdges.add(key);
        edges.push({...edge, trace_level: level + 1, from: code, to: other});
        if (edges.length >= TRACE_MAX_EDGES) { truncated = true; break; }
      }
      if (!visited.has(other)) {
        if (visited.size >= TRACE_MAX_NODES) { truncated = true; continue; }
        visited.set(other, level + 1);
        parents.set(other, {parent: code, edge});
        queue.push(other);
      }
    }
    if (truncated && edges.length >= TRACE_MAX_EDGES) break;
  }
  const nodes = [...visited.entries()].map(([code, level]) => ({code, level, parent: parents.get(code)?.parent || null, via: parents.get(code)?.edge || null}));
  return {root, depth:maxDepth, nodes, edges, truncated};
}
function traceRelationData(code) {
  if (!code) return emptyFC();
  const graph = traceGraph(code);
  const features = [];
  for (const e of graph.edges) {
    const a = by3[e.a]?.latlng, b = by3[e.b]?.latlng;
    if (!a || !b) continue;
    features.push({type:'Feature', properties:{a:e.a,b:e.b,types:(e.types||[]).join(' · '),layer:e.layer||'',depth:e.trace_level,raw:JSON.stringify(e)}, geometry:{type:'LineString',coordinates:[[a[1],a[0]],[b[1],b[0]]]}});
  }
  return {type:'FeatureCollection', features};
}
function traceHubData(code) {
  if (!code || traceDepth <= 1) return emptyFC();
  const graph = traceGraph(code);
  const features = graph.nodes.filter(n => n.code !== code).map(n => {
    const r = by3[n.code];
    if (!r?.latlng) return null;
    return {type:'Feature', properties:{iso3:n.code,name:r.name?.common||n.code,depth:n.level}, geometry:{type:'Point',coordinates:[r.latlng[1],r.latlng[0]]}};
  }).filter(Boolean);
  return {type:'FeatureCollection', features};
}
function updateHud() {
  const m = mode(), r = selected ? by3[selected] : null;
  const graph = selected ? traceGraph(selected) : null;
  $('#camera').textContent = `zoom ${map.getZoom().toFixed(1)} · pitch ${Math.round(map.getPitch())}° · bearing ${Math.round(map.getBearing())}°`;
  $('#hud').innerHTML = `<b>${title(m)} mode${selected?' · '+esc(r?.name?.common||selected):''}${compareMode?' · compare':''}</b><div class="muted">${compareMode?`${compareCodes.length}/4 countries held · click polygons to add/remove.`:m==='world'?'Polygons and global systems dominate.':m==='regional'?'Country hubs and cross-border relations become primary.':m==='country'?'Selected polygon acts as a data shell; interior modules unfold.':'Real geocoded assets should dominate here; semantic hubs remain navigation-only.'}${selected&&showRelations?` · trace depth ${traceDepth}: ${Math.max(0,(graph?.nodes.length||1)-1)} reachable nodes / ${graph?.edges.length||0} edges.`:''}</div>`;
}
async function loadCanonical(code) {
  if (cache.has(code)) return cache.get(code);
  const i = index3[code];
  if (!i) return null;
  try {
    const r = await fetch(`../data/countries/${i.id}.json`);
    if (!r.ok) return null;
    const d = await r.json();
    cache.set(code, d);
    return d;
  } catch { return null; }
}
function getModule(h, record, code) {
  if (h.id === 'north') return worldCfg.curated_country_notes?.[code] || {note:'No curated North/programme context for this country yet.'};
  if (h.id === 'tim') return {plane:'project-canon',note:'Tim/Potatoverse country relations belong here only when a dated statement or project record routes to this country.',country_note:worldCfg.curated_country_notes?.[code]||null};
  const found = {};
  for (const k of h.keys) if (record?.[k] != null) found[k] = record[k];
  return Object.keys(found).length ? found : null;
}
function hubData(code, record) {
  const r = by3[code];
  if (!r?.latlng) return {points:emptyFC(),lines:emptyFC()};
  const lat=r.latlng[0], lon=r.latlng[1], radius=Math.max(.7,Math.min(4.5,Math.sqrt(Math.max(r.area||1,1))/430));
  const available=HUBS.map(h=>({...h,data:getModule(h,record,code)})).filter(h=>h.data);
  const pts=[],lines=[];
  available.forEach((h,i)=>{
    const a=(i/Math.max(available.length,1))*Math.PI*2, dx=Math.cos(a)*radius, dy=Math.sin(a)*radius*.65, coord=[lon+dx,Math.max(-82,Math.min(82,lat+dy))];
    pts.push({type:'Feature',properties:{id:h.id,label:h.label,plane:h.plane,code,idx:i},geometry:{type:'Point',coordinates:coord}});
    lines.push({type:'Feature',properties:{id:h.id,code},geometry:{type:'LineString',coordinates:[[lon,lat],coord]}});
  });
  return {points:{type:'FeatureCollection',features:pts},lines:{type:'FeatureCollection',features:lines}};
}
function compareData() {
  const features=[];
  for (const code of compareCodes) {
    const r=by3[code];
    if (r?.latlng) features.push({type:'Feature',properties:{iso3:code,name:r.name?.common||code},geometry:{type:'Point',coordinates:[r.latlng[1],r.latlng[0]]}});
  }
  return {type:'FeatureCollection',features};
}
function updateSpatial() {
  const hubs=selected&&showInterior&&!compareMode?hubData(selected,currentCanonical):{points:emptyFC(),lines:emptyFC()};
  map.getSource('semantic-hubs')?.setData(hubs.points);
  map.getSource('semantic-links')?.setData(hubs.lines);
  map.getSource('relations')?.setData(selected&&showRelations?traceRelationData(selected):emptyFC());
  map.getSource('trace-hubs')?.setData(selected&&showRelations?traceHubData(selected):emptyFC());
  map.getSource('compare-hubs')?.setData(compareData());
  updateHud();
}
function readable(obj) {
  if (obj==null) return '<div class="muted">No data in this record yet.</div>';
  if (typeof obj!=='object') return esc(obj);
  if (Array.isArray(obj)) return obj.slice(0,25).map(x=>`<div class="row">${typeof x==='object'?esc(JSON.stringify(x)):esc(x)}</div>`).join('')||'<div class="muted">Empty</div>';
  return Object.entries(obj).slice(0,24).map(([k,v])=>`<div class="row"><span class="muted">${esc(title(k))}</span><br>${typeof v==='object'?esc(JSON.stringify(v)):esc(v)}</div>`).join('');
}
function axisBadges(code) {
  const a=worldCfg.project_axis||{},out=[];
  for(const[k,v]of Object.entries(a.north||{})) if(Array.isArray(v)&&v.includes(code)) out.push('North · '+k.replaceAll('_',' '));
  if((a.west?.project_poles||[]).includes(code)) out.push('West · project pole');
  if((a.west?.strongly_western_connected||[]).includes(code)) out.push('West · strong connection');
  if((a.east?.strong_reference_nodes||[]).includes(code)) out.push('East · reference');
  return out;
}
function geometryBounds(f) {
  let minX=180,minY=90,maxX=-180,maxY=-90;
  const walk=x=>{if(!Array.isArray(x))return;if(typeof x[0]==='number'&&typeof x[1]==='number'){minX=Math.min(minX,x[0]);maxX=Math.max(maxX,x[0]);minY=Math.min(minY,x[1]);maxY=Math.max(maxY,x[1]);return}x.forEach(walk)};
  walk(f?.geometry?.coordinates);
  return minX<=maxX?[[minX,minY],[maxX,maxY]]:null;
}
function fitCodes(codes,padding=55) {
  let minX=180,minY=90,maxX=-180,maxY=-90,ok=false;
  for(const code of codes){const b=geometryBounds(featureByCode(code));if(!b)continue;ok=true;minX=Math.min(minX,b[0][0]);minY=Math.min(minY,b[0][1]);maxX=Math.max(maxX,b[1][0]);maxY=Math.max(maxY,b[1][1])}
  if(ok) map.fitBounds([[minX,minY],[maxX,maxY]],{padding,pitch:Math.min(map.getPitch(),45),duration:650,maxZoom:6});
}
function setState(code,key,value){if(!code)return;try{map.setFeatureState({source:'countries',id:code},{[key]:value})}catch{}}
function clearCompareStates(){for(const c of compareCodes)setState(c,'compare',false)}
function updateUrl(){
  const u=new URL(location.href);
  selected?u.searchParams.set('country',selected):u.searchParams.delete('country');
  compareCodes.length?u.searchParams.set('compare',compareCodes.join(',')):u.searchParams.delete('compare');
  relationType!=='all'?u.searchParams.set('rel',relationType):u.searchParams.delete('rel');
  traceDepth!==1?u.searchParams.set('depth',String(traceDepth)):u.searchParams.delete('depth');
  history.replaceState({},'',u);
}
async function toggleCompareCountry(code){
  if(compareCodes.includes(code)){compareCodes=compareCodes.filter(x=>x!==code);setState(code,'compare',false)}
  else{if(compareCodes.length>=4){const removed=compareCodes.shift();setState(removed,'compare',false)}compareCodes.push(code);setState(code,'compare',true)}
  selected=code;selectedFeature=featureByCode(code);currentCanonical=await loadCanonical(code);updateSpatial();renderCompare();updateUrl();
}
async function selectFeature(f,fly=false){
  const code=f.properties.iso3;if(!code)return;
  if(compareMode)return toggleCompareCountry(code);
  if(selected)setState(selected,'selected',false);
  selected=code;selectedFeature=f;setState(code,'selected',true);currentCanonical=await loadCanonical(code);updateSpatial();updateUrl();if(fly)fitCodes([code]);renderCountry();
}
function traceRows(code) {
  const graph=traceGraph(code);
  const groups=[];
  for(let level=1;level<=graph.depth;level++){
    const nodes=graph.nodes.filter(n=>n.level===level);
    if(!nodes.length)continue;
    groups.push(`<div class="trace-level"><b>Hop ${level}</b><span class="pill">${nodes.length} countr${nodes.length===1?'y':'ies'}</span>${nodes.map(n=>{const name=by3[n.code]?.name?.common||n.code;const via=(n.via?.types||[]).slice(0,2).join(' · ')||n.via?.layer||'relation';return `<button class="relation-button" onclick="goCountry('${esc(n.code)}')"><span>${esc(name)}</span><span class="pill">${esc(via)}</span></button>`}).join('')}</div>`);
  }
  return {graph, html:groups.join('')};
}
function renderCountry(){
  if(!selected||!selectedFeature)return;
  const code=selected,r=by3[code]||{},idx=index3[code],rels=relationEdgesFor(code),allRels=(worldCfg.curated_edges||[]).filter(e=>e.a===code||e.b===code),modules=HUBS.map(h=>({...h,data:getModule(h,currentCanonical,code)})).filter(h=>h.data),trace=traceRows(code);
  $('#panel').innerHTML=`<div class="eyebrow">${idx?'Canonical country':'Territory / map polygon'} · ${esc(code)}</div><h1>${esc(idx?.name||r.name?.common||selectedFeature.properties.name||code)}</h1><div>${axisBadges(code).map(x=>`<span class="pill">${esc(x)}</span>`).join('')}</div><div class="actions"><button onclick="fitCountry()">Focus polygon</button><button onclick="fitTrace()">Fit trace</button><button onclick="addCurrentToCompare()">Add to compare</button></div><div class="grid"><div class="metric"><span>Population</span><b>${fmt(r.population)}</b></div><div class="metric"><span>Area km²</span><b>${fmt(r.area)}</b></div><div class="metric"><span>Interior modules</span><b>${modules.length}</b></div><div class="metric"><span>Trace graph</span><b>${Math.max(0,trace.graph.nodes.length-1)} nodes · ${trace.graph.edges.length} edges</b></div></div><div class="card"><b>Data inside this polygon</b>${modules.map(h=>`<div class="row"><button onclick="openModule('${h.id}')">${esc(h.label)}</button> <span class="pill">${esc(h.plane)}</span></div>`).join('')||'<div class="muted">Canonical country record is still sparse.</div>'}</div><div class="card"><b>Trace outward · ${traceDepth} hop${traceDepth===1?'':'s'}</b><div class="muted">Breadth-first traversal follows the current typed relation filter, prevents cycles, and shows each newly reached country at its shortest discovered hop.</div>${trace.html||'<div class="muted">No curated edges match the current relation filter.</div>'}${trace.graph.truncated?'<div class="boundary">Trace hit its browser safety cap. Narrow the relation type or reduce depth.</div>':''}</div><div class="boundary">Interior dots are semantic navigation handles. Trace lines are typed connections, not claims of collective motive, guilt or causation.</div>${idx?`<div class="card"><b>Canonical owner</b><div class="muted">data/countries/${esc(idx.id)}.json</div></div>`:'<div class="card">This polygon is not one of the canonical country records; territory routing still needs its own registry.</div>'}`;
}
async function renderCompare(){
  const rows=await Promise.all(compareCodes.map(async code=>{const r=by3[code]||{},rec=await loadCanonical(code),modules=HUBS.filter(h=>getModule(h,rec,code)).length,rels=(worldCfg.curated_edges||[]).filter(e=>e.a===code||e.b===code).length;return{code,name:r.name?.common||code,pop:r.population,area:r.area,modules,rels,badges:axisBadges(code)}}));
  $('#panel').innerHTML=`<div class="eyebrow">Compare mode · ${rows.length}/4</div><h1>Country comparison</h1><p class="muted">Click countries to add or remove them. Comparison is descriptive: height, graph degree and project-axis labels encode different things.</p><div class="actions"><button onclick="fitCompare()">Fit comparison</button><button onclick="clearCompare()">Clear</button><button onclick="leaveCompare()">Done</button></div>${rows.length?`<div class="card"><table class="compare-table"><thead><tr><th>Country</th><th>Population</th><th>Area km²</th><th>Modules</th><th>Edges</th></tr></thead><tbody>${rows.map(x=>`<tr><td><button onclick="goCountry('${x.code}')">${esc(x.name)}</button><div>${x.badges.slice(0,2).map(b=>`<span class="pill">${esc(b)}</span>`).join('')}</div></td><td>${fmt(x.pop)}</td><td>${fmt(x.area)}</td><td>${x.modules}</td><td>${x.rels}</td></tr>`).join('')}</tbody></table></div>`:'<div class="card muted">No countries held yet. Click up to four polygons.</div>'}<div class="boundary">Compare currently uses fields already loaded by the atlas. GDP, debt, energy dependence and other dated sourced metrics should be added through the metric registry rather than guessed here.</div>`;
}
window.openModule=id=>{const h=HUBS.find(x=>x.id===id);if(!h||!selected)return;const data=getModule(h,currentCanonical,selected);$('#panel').innerHTML=`<div class="eyebrow">${esc(h.plane)} · ${esc(selected)}</div><h1>${esc(h.label)}</h1><div class="actions"><button onclick="showOverview()">Back to country</button></div><div class="boundary">${h.id==='tim'?'Project-canon material is separate from empirical country data.':h.id==='debt'?'This module is for documented physical/public finance. Tim-claimed karmic amounts remain a separate project ledger.':'This is a semantic data module, not a geographic point.'}</div><div class="card">${readable(data)}</div>`};
window.showOverview=()=>renderCountry();
window.fitCountry=()=>selected&&fitCodes([selected]);
window.fitTrace=()=>{if(!selected)return;const codes=traceGraph(selected).nodes.map(n=>n.code);fitCodes(codes,65)};
window.fitCompare=()=>compareCodes.length&&fitCodes(compareCodes,70);
window.clearCompare=()=>{clearCompareStates();compareCodes=[];updateSpatial();renderCompare();updateUrl()};
window.leaveCompare=()=>{compareMode=false;$('#compare').classList.remove('active');if(selected){setState(selected,'selected',true);renderCountry()}else resetWorld(false);updateSpatial();updateUrl()};
window.addCurrentToCompare=async()=>{if(!selected)return;compareMode=true;$('#compare').classList.add('active');if(!compareCodes.includes(selected)){compareCodes.push(selected);setState(selected,'compare',true)}setState(selected,'selected',false);updateSpatial();renderCompare();updateUrl()};
window.goCountry=async code=>{const f=featureByCode(code);if(!f)return;if(compareMode){await toggleCompareCountry(code);fitCodes(compareCodes.length?compareCodes:[code]);return}await selectFeature(f,true)};

function addLayers(){
  map.addSource('countries',{type:'geojson',data:geo,promoteId:'iso3'});
  const color=['case',['boolean',['feature-state','selected'],false],'#e0bd78',['boolean',['feature-state','compare'],false],'#73a7d8','#566262'];
  map.addLayer({id:'countries-fill',type:'fill',source:'countries',paint:{'fill-color':color,'fill-opacity':['case',['boolean',['feature-state','selected'],false],.88,['boolean',['feature-state','compare'],false],.78,.57]}});
  map.addLayer({id:'countries-line',type:'line',source:'countries',paint:{'line-color':['case',['boolean',['feature-state','selected'],false],'#f0e4b2',['boolean',['feature-state','compare'],false],'#b9dcff','#1c2626'],'line-width':['case',['any',['boolean',['feature-state','selected'],false],['boolean',['feature-state','compare'],false]],2.5,.7]}});
  map.addLayer({id:'countries-extrude',type:'fill-extrusion',source:'countries',layout:{visibility:'none'},paint:{'fill-extrusion-color':color,'fill-extrusion-height':['*',250000,['sqrt',['/', ['max',['get','population'],1],1000000]]],'fill-extrusion-opacity':.68}});
  const countryHubs={type:'FeatureCollection',features:rest.filter(x=>x.latlng?.length===2).map(x=>({type:'Feature',properties:{iso3:x.cca3,name:x.name.common},geometry:{type:'Point',coordinates:[x.latlng[1],x.latlng[0]]}}))};
  map.addSource('country-hubs',{type:'geojson',data:countryHubs});
  map.addLayer({id:'country-hubs',type:'circle',source:'country-hubs',minzoom:3.2,paint:{'circle-radius':['interpolate',['linear'],['zoom'],3.2,2.5,7,6],'circle-color':'#bbdc8a','circle-stroke-color':'#101616','circle-stroke-width':1.2,'circle-opacity':.8}});
  map.addLayer({id:'country-labels',type:'symbol',source:'country-hubs',minzoom:4,layout:{'text-field':['get','name'],'text-size':11,'text-offset':[0,1.2]},paint:{'text-color':'#eff4eb','text-halo-color':'#080b0b','text-halo-width':1.3}});
  map.addSource('semantic-links',{type:'geojson',data:emptyFC()});
  map.addLayer({id:'semantic-links',type:'line',source:'semantic-links',minzoom:3.6,paint:{'line-color':'#7e8b82','line-width':1,'line-dasharray':[2,2],'line-opacity':.55}});
  map.addSource('semantic-hubs',{type:'geojson',data:emptyFC()});
  map.addLayer({id:'semantic-hubs',type:'circle',source:'semantic-hubs',minzoom:3.6,paint:{'circle-radius':['interpolate',['linear'],['zoom'],3.6,4,7,8],'circle-color':['match',['get','plane'],'project-canon','#c27878','interpretive-policy','#73a7d8','historical','#d39870','mixed','#a78bd4','#bbdc8a'],'circle-stroke-color':'#101616','circle-stroke-width':1.4,'circle-opacity':.9}});
  map.addLayer({id:'semantic-labels',type:'symbol',source:'semantic-hubs',minzoom:4.6,layout:{'text-field':['get','label'],'text-size':10,'text-offset':[0,1.25]},paint:{'text-color':'#eff4eb','text-halo-color':'#080b0b','text-halo-width':1.2}});
  map.addSource('relations',{type:'geojson',data:emptyFC()});
  map.addLayer({id:'relations',type:'line',source:'relations',minzoom:2,paint:{'line-color':['step',['get','depth'],'#73a7d8',2,'#8ba5bd',3,'#687f94'],'line-width':['interpolate',['linear'],['zoom'],2,1.2,6,3],'line-opacity':['step',['get','depth'],.82,2,.62,3,.44]}});
  map.addSource('trace-hubs',{type:'geojson',data:emptyFC()});
  map.addLayer({id:'trace-hubs',type:'circle',source:'trace-hubs',paint:{'circle-radius':['step',['get','depth'],6,2,5,3,4],'circle-color':['step',['get','depth'],'#bbdc8a',2,'#73a7d8',3,'#8b91b9'],'circle-stroke-color':'#eff4eb','circle-stroke-width':1.2,'circle-opacity':.9}});
  map.addSource('compare-hubs',{type:'geojson',data:emptyFC()});
  map.addLayer({id:'compare-hubs',type:'circle',source:'compare-hubs',paint:{'circle-radius':8,'circle-color':'#73a7d8','circle-stroke-color':'#eff4eb','circle-stroke-width':2,'circle-opacity':.9}});
}
function extrusion(){const v=$('#height').value,extrude=v!=='flat';map.setLayoutProperty('countries-extrude','visibility',extrude?'visible':'none');map.setLayoutProperty('countries-fill','visibility',extrude?'none':'visible');if(v==='population')map.setPaintProperty('countries-extrude','fill-extrusion-height',['*',250000,['sqrt',['/', ['max',['get','population'],1],1000000]]]);if(v==='area')map.setPaintProperty('countries-extrude','fill-extrusion-height',['*',9000,['sqrt',['max',['get','area'],1]]])}
function clickRelation(e){const f=e.features?.[0];if(!f)return;const p=f.properties,raw=JSON.parse(p.raw),a=by3[p.a]?.name?.common||p.a,b=by3[p.b]?.name?.common||p.b;$('#panel').innerHTML=`<div class="eyebrow">Typed country relation · hop ${p.depth||1}</div><h1>${esc(a)} ↔ ${esc(b)}</h1><div class="pill">${esc(p.types||'relationship')}</div><div class="actions"><button onclick="goCountry('${esc(p.a)}')">Open ${esc(a)}</button><button onclick="goCountry('${esc(p.b)}')">Open ${esc(b)}</button><button onclick="showOverview()">Back to root trace</button></div><div class="card"><b>Layer</b><div>${esc(p.layer||'curated')}</div></div><div class="boundary">A relation line describes a typed connection. It does not assign one motive, identity or responsibility to the population of either country.</div><pre class="json">${esc(JSON.stringify(raw,null,2))}</pre>`}
function resetWorld(clearCompare=true){if(selected)setState(selected,'selected',false);selected=null;selectedFeature=null;currentCanonical=null;if(clearCompare){clearCompareStates();compareCodes=[];compareMode=false;$('#compare').classList.remove('active')}updateSpatial();updateUrl();map.easeTo({center:[5,24],zoom:1.5,pitch:0,bearing:0,duration:650});$('#panel').innerHTML='<div class="eyebrow">World mode</div><h1>World Relational Atlas</h1><p class="muted">Search, compare, recursively trace typed relations, rotate and select a polygon to unfold its canonical data modules.</p>'}
function populateControls(){const dl=$('#country-list');for(const r of [...rest].sort((a,b)=>a.name.common.localeCompare(b.name.common))){const o=document.createElement('option');o.value=`${r.name.common} (${r.cca3})`;dl.appendChild(o)}const types=[...new Set((worldCfg.curated_edges||[]).flatMap(e=>e.types||[]))].sort();for(const t of types){const o=document.createElement('option');o.value=t;o.textContent=title(t);$('#relationType').appendChild(o)}}
function findCountry(q){q=q.trim().toLowerCase();const code=q.match(/\(([a-z]{3})\)$/i)?.[1]||q;return rest.find(x=>x.cca3?.toLowerCase()===code||x.name?.common?.toLowerCase()===q||x.name?.official?.toLowerCase()===q)||rest.find(x=>x.name?.common?.toLowerCase().includes(q)||x.name?.official?.toLowerCase().includes(q))}

map.on('load',async()=>{
  addLayers();populateControls();
  map.on('click','countries-fill',e=>e.features?.[0]&&selectFeature(e.features[0],false));
  map.on('click','countries-extrude',e=>e.features?.[0]&&selectFeature(e.features[0],false));
  map.on('click','country-hubs',e=>{const code=e.features?.[0]?.properties?.iso3,f=featureByCode(code);if(f)selectFeature(f,false)});
  map.on('click','semantic-hubs',e=>{const f=e.features?.[0];if(f)window.openModule(f.properties.id)});
  map.on('click','trace-hubs',e=>{const code=e.features?.[0]?.properties?.iso3;if(code)window.goCountry(code)});
  map.on('click','relations',clickRelation);
  ['countries-fill','countries-extrude','country-hubs','semantic-hubs','relations','trace-hubs','compare-hubs'].forEach(id=>{map.on('mouseenter',id,()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave',id,()=>map.getCanvas().style.cursor='')});
  const u=new URL(location.href),rel=u.searchParams.get('rel'),depth=Number(u.searchParams.get('depth'));
  if(rel&&[...$('#relationType').options].some(o=>o.value===rel)){relationType=rel;$('#relationType').value=rel}
  if(Number.isInteger(depth)&&depth>=1&&depth<=TRACE_MAX_DEPTH){traceDepth=depth;$('#traceDepth').value=String(depth)}
  const compare=(u.searchParams.get('compare')||'').split(',').map(x=>x.toUpperCase()).filter(x=>featureByCode(x)).slice(0,4);
  if(compare.length){compareMode=true;$('#compare').classList.add('active');compareCodes=compare;for(const c of compareCodes)setState(c,'compare',true);selected=compareCodes.at(-1);selectedFeature=featureByCode(selected);currentCanonical=await loadCanonical(selected);updateSpatial();renderCompare();fitCodes(compareCodes,70)}
  else{const q=u.searchParams.get('country')?.toUpperCase();if(q){const f=featureByCode(q);if(f)await selectFeature(f,true)}}
  updateHud();
});
map.on('moveend',updateHud);map.on('zoom',updateHud);map.on('pitch',updateHud);map.on('rotate',updateHud);
$('#height').onchange=extrusion;
$('#interior').onclick=()=>{showInterior=!showInterior;$('#interior').classList.toggle('active',showInterior);updateSpatial()};
$('#relations').onclick=()=>{showRelations=!showRelations;$('#relations').classList.toggle('active',showRelations);updateSpatial()};
$('#relationType').onchange=e=>{relationType=e.target.value;updateSpatial();if(compareMode)renderCompare();else if(selected)renderCountry();updateUrl()};
$('#traceDepth').onchange=e=>{traceDepth=Math.max(1,Math.min(TRACE_MAX_DEPTH,Number(e.target.value)||1));updateSpatial();if(selected&&!compareMode)renderCountry();updateUrl()};
$('#fit').onclick=()=>compareMode?window.fitCompare():selected&&traceDepth>1?window.fitTrace():window.fitCountry();
$('#compare').onclick=()=>{compareMode=!compareMode;$('#compare').classList.toggle('active',compareMode);if(compareMode){if(selected&&!compareCodes.includes(selected)){compareCodes.push(selected);setState(selected,'compare',true);setState(selected,'selected',false)}updateSpatial();renderCompare()}else window.leaveCompare();updateUrl()};
$('#tilt').onclick=()=>map.easeTo({pitch:map.getPitch()>20?0:55,duration:500});
$('#globe').onclick=()=>{globe=!globe;try{map.setProjection({type:globe?'globe':'mercator'});$('#globe').classList.toggle('active',globe)}catch(e){console.warn(e)}};
$('#world').onclick=()=>resetWorld(true);
$('#search').addEventListener('keydown',async e=>{if(e.key!=='Enter')return;const r=findCountry(e.target.value);if(!r)return;const f=featureByCode(r.cca3);if(f){if(compareMode)await toggleCompareCountry(r.cca3);else await selectFeature(f,true)}});
document.addEventListener('keydown',e=>{if(e.key==='/'&&document.activeElement?.tagName!=='INPUT'){e.preventDefault();$('#search').focus();$('#search').select()}else if(e.key==='Escape'){if(compareMode)window.leaveCompare();else resetWorld(true)}else if((e.key==='c'||e.key==='C')&&document.activeElement?.tagName!=='INPUT')$('#compare').click()});
