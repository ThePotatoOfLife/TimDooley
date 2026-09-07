/* Canonical Frame data bridge. */
async function loadJSON(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(path+' '+r.status);return r.json();}
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const titleCase=id=>String(id||'').replace(/-/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
const link=(id,name)=>`<a class="record-link" href="node.html?id=${encodeURIComponent(id)}">${esc(name||id)}</a>`;
async function renderFrame(){
 const box=document.getElementById('canonical-tree'); const axis=document.getElementById('axis-levels'); if(!box)return;
 try{
  const [tree,data]=await Promise.all([loadJSON('data/tree.json'),loadJSON('data/nodes.json')]);
  const nodes=new Map((data.nodes||[]).map(n=>[n.id,n])); const levels=tree.levels||[];
  if(axis)axis.innerHTML=levels.map(l=>`<a class="axis-level" href="node.html?id=${encodeURIComponent(l.id)}"><span>${esc(l.roman)}</span><strong>${esc(l.name).toUpperCase()}</strong></a>`).join('');
  box.innerHTML=`<article class="tree-root"><span>ROOT</span><h3>TIM DOOLEY</h3><p>The canonical entrance. The structure below comes directly from data/tree.json.</p></article><div class="tree-branch">${levels.map(l=>{const children=(l.children||[]).map(id=>link(id,nodes.get(id)?.name||titleCase(id))).join('');return `<article><span>${esc(l.roman)}</span><h3>${link(l.id,l.name)}</h3><p>${esc(l.description)}</p><div class="children">${children}</div></article>`}).join('')}</div>`;
 }catch(e){box.innerHTML=`<p class="error">Repository data could not be loaded: ${esc(e.message)}</p>`;}
}
async function renderNorth(){const box=document.getElementById('north-questions');if(!box)return;try{const [tree,data]=await Promise.all([loadJSON('data/tree.json'),loadJSON('data/nodes.json')]);const nodes=new Map((data.nodes||[]).map(n=>[n.id,n]));box.innerHTML=(tree.northQuestions||[]).map(id=>link(id,nodes.get(id)?.name||titleCase(id))).join('')}catch(e){box.textContent=e.message}}
function boot(){renderFrame();renderNorth()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
