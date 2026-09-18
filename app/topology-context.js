(()=>{
'use strict';
const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const widgets=[...document.querySelectorAll('[data-house-topology-context]')];
if(!widgets.length)return;
const cache=new Map();
async function load(src){
  if(!cache.has(src))cache.set(src,fetch(src).then(r=>{if(!r.ok)throw new Error('topology unavailable');return r.json()}));
  return cache.get(src);
}
function priority(rel,selected){
  const from=selected.has(rel.from),to=selected.has(rel.to);
  if(from&&to)return 0;
  if(from||to)return 1;
  return 2;
}
function render(root,data){
  const ids=(root.dataset.houseConcepts||'').split(',').map(x=>x.trim()).filter(Boolean);
  const selected=new Set(ids);
  const by=Object.fromEntries((data.concepts||[]).map(x=>[x.id,x]));
  const type=Object.fromEntries((data.relation_types||[]).map(x=>[x.id,x]));
  const valid=ids.filter(id=>by[id]);
  if(!valid.length)return;
  const base=root.dataset.houseBase||'../house/';
  const rels=(data.relations||[])
    .filter(r=>selected.has(r.from)||selected.has(r.to))
    .sort((a,b)=>priority(a,selected)-priority(b,selected))
    .slice(0,6);
  const selectedLinks=valid.map(id=>'<a class="topology-context-chip" href="'+esc(base)+'?operator='+encodeURIComponent(id)+'#operators">'+esc(by[id].label)+'</a>').join('');
  const rows=rels.map(r=>{
    const from=by[r.from]?.label||r.from,to=by[r.to]?.label||r.to,label=type[r.type]?.label||r.type;
    return '<li><span><b>'+esc(from)+'</b> <em>'+esc(label)+'</em> <b>'+esc(to)+'</b></span><small>'+esc(r.description)+'</small></li>';
  }).join('');
  root.innerHTML='<div class="topology-context-head"><div><p class="eyebrow">House context</p><h2>How these ideas connect</h2></div><a class="topology-context-house" href="'+esc(base)+'#operators">Open House topology →</a></div><div class="topology-context-chips">'+selectedLinks+'</div>'+(rows?'<ul class="topology-context-relations">'+rows+'</ul>':'')+'<p class="topology-context-boundary">These are typed project relations, not identity claims. Each linked operator keeps its own domain and evidence boundary.</p>';
}
widgets.forEach(root=>{
  const src=root.dataset.topologySrc||'../data/house/concept-topology.json';
  load(src).then(data=>render(root,data)).catch(()=>{});
});
})();
