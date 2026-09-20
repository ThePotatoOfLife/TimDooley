(()=>{'use strict';
const BASE='/TimDooley/';
const esc=s=>String(s??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
let manifest,roleIndex,enhancements;let activeRole='all';
async function get(path){const r=await fetch(BASE+path);if(!r.ok)throw new Error(path);return r.json()}
function dossierHref(id){return 'file/?character='+encodeURIComponent(id)}
function initials(name){return String(name||'?').split(/\s+|\//).filter(Boolean).slice(0,2).map(x=>x[0]?.toUpperCase()||'').join('')||'?'}
function roleFor(id){const out=[];for(const role of roleIndex?.roles||[])if((role.matches||[]).some(x=>x.entity_id===id))out.push(role.label);return out}
function activityBand(f){
 const s=String(f.archive_status||'').toLowerCase();
 if(s.includes('active-2026')||s==='active')return['active','active'];
 if(s.includes('recovery-active'))return['recovery','recovery active'];
 if(s.includes('deceased')||s.includes('closed'))return['closed','archived'];
 if(s.includes('historical'))return['historical','historical'];
 if(f.depth_tier==='index-card'||!s)return['dormant','dormant'];
 return['historical','archive'];
}
function characterSearch(f){return[f.name,...(f.aliases||[]),...(f.archetypes||[]),...roleFor(f.id),f.archive_status,f.depth_tier].filter(Boolean).join(' ').toLowerCase()}
function renderCabinet(){
 const root=document.getElementById('files'),figs=manifest?.characters||[];
 root.innerHTML=figs.map(f=>{
  const aliases=(f.aliases||[]).filter(x=>x&&x!==f.name),roles=roleFor(f.id),activity=activityBand(f);
  const tags=[f.depth_tier,...roles,...(f.archetypes||[])].filter(Boolean).filter((x,i,a)=>a.indexOf(x)===i).slice(0,4);
  const count=Number(f.chronicle_occurrence_count||0),countLabel=count+' Chronicle occurrence'+(count===1?'':'s');
  const detail=aliases.slice(0,3).join(' · ')||[f.archive_status,f.depth_tier].filter(Boolean).join(' · ')||'dossier';
  return '<a class="file" data-activity="'+activity[0]+'" data-character-id="'+esc(f.id)+'" data-search="'+esc(characterSearch(f))+'" href="'+dossierHref(f.id)+'"><span class="activity-label">'+esc(activity[1])+'</span><span class="count">'+esc(countLabel)+'</span><b>'+esc(f.name||f.id)+'</b><small>'+esc(detail)+'</small><div class="tags">'+tags.map(x=>'<span class="tag">'+esc(x)+'</span>').join('')+'</div></a>';
 }).join('');
 document.getElementById('status').textContent=figs.length+' dossiers loaded · dimmed folders indicate archive recency, not moral value';
}
function renderFiles(){
 const q=document.getElementById('search').value.trim().toLowerCase(),role=activeRole==='all'?null:roleIndex?.roles?.find(r=>r.id===activeRole),roleIds=new Set((role?.matches||[]).map(x=>x.entity_id));let visible=0;
 document.querySelectorAll('#files .file[data-character-id]').forEach(card=>{const show=(!q||(card.dataset.search||'').includes(q))&&(activeRole==='all'||roleIds.has(card.dataset.characterId));card.hidden=!show;if(show)visible++});
 document.getElementById('status').textContent=visible+' file'+(visible===1?'':'s')+' visible · '+(manifest?.characters||[]).length+' manifest dossiers total';
}
function renderRolebar(){
 const fav=['all','dog','guardian-dog','farmer','footstool','dweller','mud-dweller','potato','tomato','angel','guardian','builder'];
 document.getElementById('rolebar').innerHTML=fav.map(id=>{const r=id==='all'?{label:'All files'}:roleIndex.roles.find(x=>x.id===id);if(!r)return'';return'<button class="rolebtn '+(id===activeRole?'active':'')+'" data-role="'+id+'">'+esc(r.label)+'</button>'}).join('');
 document.querySelectorAll('.rolebtn').forEach(b=>b.onclick=()=>{activeRole=b.dataset.role;renderRolebar();renderRoleResults();renderFiles()});
}
function renderRoleResults(){
 const box=document.getElementById('roleResults');if(activeRole==='all'){box.className='role-results';box.innerHTML='';return}
 const r=roleIndex.roles.find(x=>x.id===activeRole);if(!r)return;const hits=r.matches||[];
 box.className='role-results show';box.innerHTML='<h2>'+esc(r.label)+'</h2><p>'+esc(r.definition||'')+'</p>'+(hits.length?hits.map(m=>{const known=(manifest.characters||[]).some(f=>f.id===m.entity_id),href=known?dossierHref(m.entity_id):(m.route?BASE+m.route:'#');return'<div class="role-hit"><b>'+esc(m.label)+'</b> <small>'+esc(m.date||'')+' · '+esc(m.status||'')+'</small><p>'+esc(m.note||'')+'</p><a href="'+href+'">Open '+(known?'dossier':'source/room')+' →</a></div>'}).join(''):'<p>No named assignment is currently safe enough to show. Open the role owner instead.</p>')+'<p><a href="'+BASE+(r.owner||'knowledge/world/potatoverse-cast-role-ecology.json')+'">Open role owner →</a></p>';
}
function shuffle(){const figs=manifest.characters||[];if(!figs.length)return;const f=figs[Math.floor(Math.random()*figs.length)];location.href=dossierHref(f.id)}
(async()=>{[manifest,roleIndex,enhancements]=await Promise.all([get('knowledge/cia/manifest.json'),get('knowledge/cia/role-index.json'),get('knowledge/cia/enhancements-index.json')]);renderCabinet();renderRolebar();renderRoleResults();renderFiles();document.getElementById('search').addEventListener('input',renderFiles);document.getElementById('shuffle').onclick=shuffle})().catch(()=>{document.getElementById('status').textContent='Cabinet filters could not initialize; direct dossier links remain usable.'});
})();
