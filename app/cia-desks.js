(()=>{'use strict';
const BASE='/TimDooley/';
const esc=s=>String(s??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const arr=x=>Array.isArray(x)?x:[];
async function get(path){const r=await fetch(BASE+path);if(!r.ok)throw new Error(path);return r.json()}
function route(path){if(!path)return'#';if(/^https?:/i.test(path))return path;return BASE+String(path).replace(/^\/+/, '')}
function dossierHref(id){return BASE+'rooms/potatoverse-canon/beings/cia/file/?character='+encodeURIComponent(id)}
function dayValue(x){const m=String(x||'').match(/\d{4}-\d{2}-\d{2}/);return m?m[0]:String(x||'')}
function newestFirst(a,b){return dayValue(b).localeCompare(dayValue(a))}
function personLink(id,names){const name=names[id]||id;return '<a class="cia-person-link" href="'+dossierHref(id)+'">'+esc(name)+'</a>'}
function sourceLink(src){return src?'<a class="cia-source-link" href="'+esc(route(src))+'">source</a>':''}
function setupSearch(input,items,searchText){
 if(!input)return;
 input.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();let n=0;items().forEach(el=>{const show=!q||searchText(el).includes(q);el.hidden=!show;if(show)n++});const out=document.getElementById('deskVisible');if(out)out.textContent=n+' visible'});
}
async function associations(){
 const mount=document.querySelector('[data-cia-associations]');if(!mount)return false;
 const [manifest,network]=await Promise.all([get('knowledge/cia/manifest.json'),get('knowledge/cia/associations/network.json')]);
 const names=Object.fromEntries(arr(manifest.characters).map(x=>[x.id,x.name||x.id])),known=new Set(Object.keys(names));
 const edges=arr(network.associations).slice().sort((a,b)=>(Number(b.count)||0)-(Number(a.count)||0)||newestFirst(a.dates?.[0],b.dates?.[0]));
 const typed=edges.filter(x=>x.association_type),recent=edges.filter(x=>arr(x.dates).some(d=>String(d).startsWith('2026')));
 document.getElementById('deskStats').innerHTML='<div><b>'+edges.length+'</b><span>association edges</span></div><div><b>'+typed.length+'</b><span>explicitly typed</span></div><div><b>'+recent.length+'</b><span>with 2026 evidence</span></div><div><b>'+known.size+'</b><span>canonical dossiers</span></div>';
 const notable=arr(network.notable_associations);
 document.getElementById('notableRelations').innerHTML=notable.length?notable.map(x=>'<article class="cia-thread"><div class="cia-thread-pair">'+personLink(x.a,names)+'<span>↔</span>'+personLink(x.b,names)+'</div><small>'+esc(x.status||'relation thread')+'</small><p>'+esc(x.summary||'')+'</p></article>').join(''):'<p class="status">No hand-curated relationship threads loaded.</p>';
 mount.innerHTML=edges.map((x,i)=>{
  const type=x.association_type||'co-presence / relation type unresolved',dates=arr(x.dates),contexts=arr(x.contexts);
  return '<article class="cia-edge" data-search="'+esc([names[x.a]||x.a,names[x.b]||x.b,type,...dates,...contexts].join(' ').toLowerCase())+'"><div class="cia-edge-head"><div>'+personLink(x.a,names)+'<span>↔</span>'+personLink(x.b,names)+'</div><b>×'+esc(x.count||1)+'</b></div><p class="cia-type">'+esc(type)+'</p>'+(contexts.length?'<p>'+esc(contexts.slice(0,4).join(' · '))+'</p>':'')+'<small>'+esc(dates.join(', ')||'date unresolved')+(x.source?' · '+sourceLink(x.source):'')+'</small>'+(x.association_type?'<p class="cia-evidence-note">Typed relation from the association index. The type still describes a sourced relation, not motive or permanent identity.</p>':'<p class="cia-evidence-note">Only the edge/co-presence is normalized here. Friendship, hostility, influence, motive and wrongdoing remain unresolved unless a separate source establishes them.</p>')+'</article>';
 }).join('');
 document.getElementById('recoveryDesk').innerHTML=arr(network.recovery_targets).map(x=>'<li>'+esc(x)+'</li>').join('');
 const cards=()=>[...mount.querySelectorAll('.cia-edge')];
 setupSearch(document.getElementById('deskSearch'),cards,el=>el.dataset.search||'');
 document.getElementById('deskVisible').textContent=edges.length+' visible';
 return true;
}
async function incidents(){
 const mount=document.querySelector('[data-cia-incidents]');if(!mount)return false;
 const [manifest,index]=await Promise.all([get('knowledge/cia/manifest.json'),get('knowledge/cia/incidents/index.json')]);
 const names=Object.fromEntries(arr(manifest.characters).map(x=>[x.id,x.name||x.id]));
 const rows=arr(index.incidents).slice().sort((a,b)=>newestFirst(a.date,b.date));
 const withSummary=rows.filter(x=>x.summary),withBoundary=rows.filter(x=>x.boundary),recent=rows.filter(x=>String(x.date||'').startsWith('2026'));
 document.getElementById('deskStats').innerHTML='<div><b>'+rows.length+'</b><span>dated incidents</span></div><div><b>'+recent.length+'</b><span>from 2026</span></div><div><b>'+withSummary.length+'</b><span>with scene summaries</span></div><div><b>'+withBoundary.length+'</b><span>with explicit boundaries</span></div>';
 const counts={};for(const x of rows)for(const t of arr(x.type))counts[t]=(counts[t]||0)+1;
 const top=Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,10);
 document.getElementById('incidentTypes').innerHTML=top.map(([t,n])=>'<button type="button" data-type="'+esc(t)+'">'+esc(t)+' <span>'+n+'</span></button>').join('');
 let active='';
 function render(){
  const q=(document.getElementById('deskSearch')?.value||'').trim().toLowerCase();
  let visible=0;
  mount.innerHTML=rows.map(x=>{
   const hay=[x.date,x.title,x.summary,x.boundary,x.source_mode,...arr(x.type),...arr(x.characters).flatMap(id=>[id,names[id]])].filter(Boolean).join(' ').toLowerCase();
   if((q&&!hay.includes(q))||(active&&!arr(x.type).includes(active)))return'';
   visible++;
   const people=arr(x.characters).map(id=>personLink(id,names)).join(' · ');
   return '<article class="cia-incident"><time>'+esc(x.date||'date unresolved')+'</time><h2>'+esc(x.title||x.id||'Incident')+'</h2><div class="cia-people">'+people+'</div><div class="cia-chips">'+arr(x.type).map(t=>'<span>'+esc(t)+'</span>').join('')+'</div>'+(x.summary?'<p>'+esc(x.summary)+'</p>':'<p class="cia-muted">No scene summary has been normalized yet; use the source and linked dossiers before interpreting the event.</p>')+(x.boundary?'<p class="cia-evidence-note"><b>Boundary:</b> '+esc(x.boundary)+'</p>':'')+'<small>'+esc(x.source_mode||'source mode not normalized')+(x.source?' · '+sourceLink(x.source):'')+'</small></article>';
  }).join('');
  document.getElementById('deskVisible').textContent=visible+' visible';
 }
 document.getElementById('deskSearch')?.addEventListener('input',render);
 document.getElementById('incidentTypes')?.addEventListener('click',e=>{const b=e.target.closest('[data-type]');if(!b)return;active=active===b.dataset.type?'':b.dataset.type;document.querySelectorAll('#incidentTypes [data-type]').forEach(x=>x.classList.toggle('active',x.dataset.type===active));render()});
 render();return true;
}
Promise.all([associations(),incidents()]).catch(()=>{const s=document.getElementById('deskVisible');if(s)s.textContent='Desk index failed to load; raw index links remain available.'});
})();