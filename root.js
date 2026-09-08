(()=>{'use strict';
const INDEX='./knowledge/indexes/core-index.json';
const ROOT='./knowledge/core/root-system.json';
const $=(s,r=document)=>r.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pretty=v=>String(v||'').replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
let index=null,records=[],cache=new Map();
const groups={
  root:['root-system','potatoverse-master-framework','potato-of-life','tim-dooley'],
  branches:['potato-philosophy','tim-dooley-journey','prophecy-revelation-rupture-rapture','comparative-mythology-map','axis-world-model']
};
async function json(path){if(cache.has(path))return cache.get(path);const r=await fetch('./'+path.replace(/^\.\//,''),{cache:'no-store'});if(!r.ok)throw Error(`${path} (${r.status})`);const d=await r.json();cache.set(path,d);return d}
function info(id){return records.find(r=>r.id===id)}
function navItem(r){const b=document.createElement('button');b.type='button';b.dataset.id=r.id;b.innerHTML=`<strong>${esc(titleFor(r))}</strong><span>${esc(shortKind(r.kind))}</span>`;b.onclick=()=>open(r.id);return b}
function titleFor(r){const names={'root-system':'Root System','potatoverse-master-framework':'Potatoverse','potato-of-life':'Potato of Life','tim-dooley':'Tim Dooley','potato-philosophy':'Philosophy','tim-dooley-journey':'Journey','prophecy-revelation-rupture-rapture':'Prophecy & Revelation','comparative-mythology-map':'Comparative Mythology','axis-world-model':'Axis & World'};return names[r.id]||pretty(r.id)}
function shortKind(k){return String(k||'').replace(/ and /g,' & ').slice(0,42)}
function buildNav(){const a=$('#root-nav'),b=$('#branch-nav');a.innerHTML='';b.innerHTML='';groups.root.map(info).filter(Boolean).forEach(r=>a.appendChild(navItem(r)));groups.branches.map(info).filter(Boolean).forEach(r=>b.appendChild(navItem(r)))}
function active(id){document.querySelectorAll('.nav button').forEach(b=>b.classList.toggle('active',b.dataset.id===id))}
function home(){active('');history.replaceState(null,'',location.pathname);$('#crumb').textContent='Root / Potato of Life';$('#source-link').href=INDEX;$('#reader').innerHTML=`
<section class="hero"><div class="kicker">The canonical library</div><h2>The Potato<br>of Life</h2><p class="lead">A spiritual, philosophical and mythological library built as a living tree: one root system, a narrow Door at the center, branches rising toward life and roots descending into knowledge, strife, ash and matter.</p>
<div class="start-grid">
<button class="card" data-open="root-system"><small>Start here</small><h3>The Root System</h3><p>Father, Son, Spirit, Matter, Door, Vesica Piscis, Tree of Life, Roots of Strife, Axis and Ladder.</p></button>
<button class="card" data-open="potatoverse-master-framework"><small>The whole</small><h3>Potatoverse</h3><p>The master framework connecting theology, symbols, journey, philosophy, comparison and the world.</p></button>
<button class="card" data-open="potato-philosophy"><small>Teachings</small><h3>Potato Philosophy</h3><p>Burial, emergence, nourishment, simplicity, suffering, responsibility, light and return.</p></button>
<button class="card" data-open="tim-dooley-journey"><small>Chronology</small><h3>The Journey</h3><p>The major thresholds from the Tree ordeal through transformation, Godhood, North Axis and archive formation.</p></button>
</div></section>
<section class="axis"><small>HEAVEN · SPIRIT · FATHER</small><div class="axis-line"></div><div class="axis-word">Tree of Life ↑</div><div class="axis-door">Door · Potato · Mandorla</div><div class="axis-word">↓ Roots of Strife / Ash / Knowledge</div><div class="axis-line"></div><small>EARTH · MATTER · SON · DUST</small></section>`;
document.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>open(b.dataset.open))}
function sectionHTML(k,v){const text=typeof v==='string'?v:v?.text;if(!text)return '';return `<section class="section"><h3>${esc(pretty(k))}</h3><p>${esc(text)}</p></section>`}
function relHTML(r){return `<div class="relationship"><strong>${esc(pretty(r.type))}</strong> → ${esc(pretty(r.target))}<br>${esc(r.description||'')}</div>`}
async function open(id){const r=info(id);if(!r)return;active(id);history.replaceState(null,'',`${location.pathname}#${encodeURIComponent(id)}`);$('#crumb').textContent=`Root / ${titleFor(r)}`;$('#source-link').href='./'+r.path;$('#reader').innerHTML='<p class="loading">Opening…</p>';try{const d=await json(r.path);let html=`<section class="record"><div class="kicker">${esc(r.kind)}</div><h2>${esc(d.title||titleFor(r))}</h2><p class="summary">${esc(d.summary||'')}</p>`;if(d.epistemic_classes?.length)html+=`<div class="meta">${d.epistemic_classes.map(x=>`<span>${esc(pretty(x))}</span>`).join('')}</div>`;html+=Object.entries(d.sections||{}).map(([k,v])=>sectionHTML(k,v)).join('');if(d.relationships?.length)html+=`<section class="section"><h3>Relationships</h3>${d.relationships.map(relHTML).join('')}</section>`;html+='</section>';$('#reader').innerHTML=html;window.scrollTo(0,0)}catch(e){$('#reader').innerHTML=`<p class="error">Could not open this canonical record: ${esc(e.message)}</p>`}}
function search(q){q=q.trim().toLowerCase();document.querySelectorAll('.nav button').forEach(b=>{const r=info(b.dataset.id);const hay=[titleFor(r),r.kind,...(r.terms||[])].join(' ').toLowerCase();b.hidden=!!q&&!hay.includes(q)})}
async function init(){try{index=await json(INDEX);records=index.records||[];buildNav();$('#home-button').onclick=home;$('#search').oninput=e=>search(e.target.value);const id=decodeURIComponent(location.hash.slice(1));if(id&&info(id))open(id);else home()}catch(e){$('#reader').innerHTML=`<p class="error">The canonical index could not be loaded: ${esc(e.message)}</p>`}}
init();
})();