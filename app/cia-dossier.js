(()=>{'use strict';
const BASE='/TimDooley/';
const esc=s=>String(s??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const q=new URLSearchParams(location.search);let current=q.get('character')||'marty-biz';
let manifest,roles,roleCensus,stories,associations,incidents,enhancements,dossier,accountContract,mudBankContract,symbolicPool;
async function get(path){const r=await fetch(BASE+path);if(!r.ok)throw new Error(path);return r.json()}
const arr=x=>Array.isArray(x)?x:[];
function route(path){
 const value=String(path||'').trim();if(!value)return'#';
 if(/^https?:/i.test(value))return value;
 if(value===BASE.slice(0,-1)||value.startsWith(BASE))return value;
 return BASE+value.replace(/^\/+/, '');
}
function sourceRef(value,label){
 const path=String(value||'').trim();if(!path)return'<span class="empty">source path unavailable</span>';
 const linkable=/^https?:\/\//i.test(path)||/^(?:\/?(?:data|knowledge|rooms|story-content|docs|context|traditions|world|tim-dooley|religion|philosophy|science|north|axis|below|shadow-farm|great-book)\/)/i.test(path)||/\.(?:json|html|md)(?:[#?].*)?$/i.test(path);
 return linkable?'<a class="route-link" href="'+esc(route(path))+'">'+esc(label||path)+'</a>':'<span class="route-label">'+esc(label||path)+'</span>';
}
function roleMatches(id){const out=[];for(const role of arr(roles?.roles))for(const m of arr(role.matches))if(m.entity_id===id)out.push({role_id:role.id,role_family:role.family,role_definition:role.definition,role:role.label,...m});return out}
function roleCensusFor(id){return arr(roleCensus?.entities).find(x=>x.character_id===id)||null}
function roleBoundary(label){
 const s=String(label||'').toLowerCase();
 if(s.includes('guardian dog'))return'Guardian Dog is the constructive side of the Dog grammar: warning, protection, evidence discipline and a stopping condition. It is still a scene-role, not a permanent identity.';
 if(s.includes('dog'))return'Dog is a Potatoverse relation/archetype about tracking, pursuit, reactive looping or boundary pressure. It is not a literal species claim, diagnosis, criminal label or permanent human identity.';
 if(s.includes('farmer'))return'Farmer is a Potatoverse systems-role about cultivation, enclosure, classification, harvest or extraction. The label alone does not establish literal farming, trafficking, exploitation, criminality or occult identity.';
 if(s.includes('footstool'))return'Footstool is a project topology/relationship image about support, subordination or a lower position containing a possible Door. It is not a statement of human worth.';
 if(s.includes('mud dweller'))return'Mud Dweller is a reversible project state for unresolved entanglement or habitation in Mud. It is not a diagnosis, caste or permanent essence.';
 return'Archive roles are scene-, source- and relationship-bounded. Read the dated exchange or case first; the archetype is an interpretive layer, not a verdict.';
}
const incidentMatches=id=>arr(incidents?.incidents).filter(x=>arr(x.characters).includes(id));
const associationMatches=id=>arr(associations?.associations).filter(x=>x.a===id||x.b===id);
const enhancementFor=id=>enhancements?.characters?.[id]||enhancements?.created_beings?.[id]||null;
const storyMatches=id=>arr(stories?.characters?.[id]);
function activityBand(){
 const s=String(dossier.archive_status||'').toLowerCase();
 if(s.includes('active-2026')||s==='active')return['active','active file'];
 if(s.includes('recovery-active'))return['recovery','recovery active'];
 if(s.includes('deceased')||s.includes('closed'))return['closed','archived / closed'];
 if(s.includes('historical'))return['historical','historical file'];
 return['historical','archive state unresolved'];
}
function initials(name){return String(name||'?').split(/\s+|\//).filter(Boolean).slice(0,2).map(x=>x[0]?.toUpperCase()||'').join('')||'?'}
function stableHash(text){let h=2166136261;for(const ch of String(text||'')){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}
function roleText(){
 const indexed=roleMatches(current).flatMap(x=>[x.role,x.note,x.status]);
 const local=arr(dossier.symbolic_roles).flatMap(x=>[x.role,x.scope,x.note]);
 const census=arr(roleCensusFor(current)?.symbolic_roles);
 const archetypes=arr(dossier.tim_relation?.archetypes);
 return [...indexed,...local,...census,...archetypes].filter(Boolean).join(' ').toLowerCase();
}
function symbolicImages(){
 const hay=roleText(),imgs=arr(symbolicPool?.images).filter(img=>arr(img.role_terms).some(t=>hay.includes(String(t).toLowerCase())));
 if(!imgs.length)return[];
 const offset=stableHash(current)%imgs.length;
 return imgs.slice(offset).concat(imgs.slice(0,offset)).slice(0,3);
}
function renderMug(){
 const box=document.getElementById('mug'),caption=document.getElementById('mugCaption');
 const p=dossier.media?.portrait;
 if(p?.src){box.innerHTML='<img src="'+esc(route(p.src))+'" alt="'+esc(p.alt||('Archive portrait for '+(dossier.display_name||current)))+'">';caption.textContent=p.caption||p.source_ref||'';return}
 const proxy=symbolicImages()[0];
 if(proxy){
   box.innerHTML='<img src="'+esc(proxy.image_url)+'" alt="'+esc(proxy.label+' symbolic proxy image')+'">';
   caption.innerHTML='<b>SYMBOLIC PROXY · NOT A LIKENESS</b><br>'+esc(proxy.label)+' · '+esc(proxy.license)+' · <a href="'+esc(proxy.source_page)+'" target="_blank" rel="noopener">source</a>';
   return;
 }
 box.innerHTML='<div><span class="monogram">'+esc(initials(dossier.display_name||current))+'</span><small>NO SOURCED OR SYMBOLIC IMAGE</small></div>';
 caption.textContent='No role-matched symbolic proxy is currently available.';
}
function accountData(){
 const explicit=dossier.symbolic_account||{};
 const legacy=dossier.cia_record?.debt_and_repair||{};
 const records=arr(explicit.entries).length?arr(explicit.entries):arr(legacy.records);
 const credits=records.filter(x=>['project-credit','yield','repair-attempt'].includes(String(x.type||'')));
 const debits=records.filter(x=>['project-debit'].includes(String(x.type||'')));
 const disputes=records.filter(x=>String(x.type||'')==='dispute');
 const good=explicit.good_karma&&explicit.good_karma!=='event-ledger'?explicit.good_karma:(credits.length?credits.length+' sourced credit/yield event'+(credits.length===1?'':'s'):'unassessed');
 const debt=explicit.karmic_debt&&explicit.karmic_debt!=='event-ledger'?explicit.karmic_debt:(debits.length?debits.length+' sourced debit event'+(debits.length===1?'':'s'):(disputes.length?disputes.length+' disputed item'+(disputes.length===1?'':'s'):'unassessed'));
 return{status:explicit.status||'unassessed',good,debt,welfare:explicit.dooley_welfare||null,outstanding:arr(explicit.outstanding).length?arr(explicit.outstanding):arr(dossier.cia_record?.open_loops||dossier.recovery_leads),entries:records};
}
function exactStoryDate(){
 const raw=dossier.symbolic_account?.welfare_start_override||dossier.cia_record?.presence?.first_recorded||'';
 if(!/^\d{4}-\d{2}-\d{2}$/.test(raw))return null;
 return Date.parse(raw+'T00:00:00Z');
}
function welfareValue(){
 const start=exactStoryDate(),rate=Number(mudBankContract?.welfare?.rate_per_second_susd||0);
 if(!Number.isFinite(start)||!rate)return null;
 return Math.max(0,(Date.now()-start)/1000)*rate;
}
function welfareLabel(){
 const value=welfareValue();
 return value==null?'provisional start':'$'+value.toLocaleString(undefined,{minimumFractionDigits:10,maximumFractionDigits:10});
}
function renderAccountStrip(){
 const a=accountData();
 document.getElementById('accountStrip').innerHTML=
 '<div class="account-cell"><b>Account state</b><strong>'+esc(a.status)+'</strong><p class="account-note">project-internal symbolic ledger</p></div>'+
 '<div class="account-cell"><b>Good karma</b><strong>'+esc(a.good)+'</strong><p class="account-note">only sourced/project-authored credits</p></div>'+
 '<div class="account-cell"><b>Karmic debt</b><strong>'+esc(a.debt)+'</strong><p class="account-note">not legal or financial debt</p></div>'+
 '<div class="account-cell"><b>Dooley welfare</b><strong id="dossierWelfare">'+welfareLabel()+'</strong><p class="account-note">fictional sUSD · universal story-entry drip</p></div>';
}
function meaningHtml(){
 const m=dossier.meaning||{};
 const list=(title,items)=>arr(items).length?'<div class="meaning-col"><h3>'+esc(title)+'</h3><ul>'+arr(items).map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul></div>':'';
 if(!m.why_this_file_matters&&!arr(m.known).length&&!arr(m.unknown).length)return'';
 return '<section class="meaning-spine"><p class="eyebrow-lite">Why this file exists</p><h2>'+esc(m.why_this_file_matters||'This dossier preserves a distinct relation or evidence problem in the archive.')+'</h2><div class="meaning-grid">'+list('Known',m.known)+list('Interpretive',m.interpretive)+list('Unknown / recovery',m.unknown)+'</div>'+(m.relationship_arc?'<p class="relationship-arc"><b>Relationship arc:</b> '+esc(m.relationship_arc)+'</p>':'')+(m.confidence_note?'<p class="confidence-note"><b>Confidence:</b> '+esc(m.confidence_note)+'</p>':'')+'</section>';
}
function overviewHtml(){
 const aliases=arr(dossier.aliases),tr=dossier.tim_relation||{},cp=arr(dossier.top_co_presence).slice(0,8),a=activityBand(),census=roleCensusFor(current),symbolic=arr(census?.symbolic_roles);
 const posture=census?.role_posture?'<p><b>Role posture:</b> '+esc(census.role_posture)+'</p>':'';
 const roleChips=symbolic.length?'<div class="role-list">'+symbolic.map(x=>'<span class="role">'+esc(x)+'</span>').join('')+'</div><p class="muted">Normalized mythic/story role state. Zero weight by itself; concrete acts require their own evidence.</p>':'<p class="empty">No normalized creature/job role currently attached.</p>';
 return '<div class="two"><div><div class="block"><h2>Identity</h2><p><b>Class:</b> '+esc(dossier.entity_class||'unresolved')+'</p><p><b>Archive status:</b> '+esc(dossier.archive_status||'not specified')+'</p><p><b>Aliases:</b> '+(aliases.length?aliases.map(esc).join(' · '):'<span class="empty">none recovered</span>')+'</p><span class="activity-stamp">'+esc(a[1])+' · visual prominence is recency only</span></div><div class="block"><h2>Tim relation</h2><p>'+esc(tr.editorial_reading||'No compact editorial reading yet.')+'</p><p class="muted">'+esc(tr.source_boundary||'Source boundary not yet summarized.')+'</p></div></div><div><div class="block"><h2>Role readout</h2>'+posture+roleChips+'<h3>Archetypes</h3><div class="role-list">'+(arr(tr.archetypes).length?arr(tr.archetypes).map(x=>'<span class="role">'+esc(x)+'</span>').join(''):'<span class="empty">none assigned</span>')+'</div></div><div class="block"><h2>Frequent co-presence</h2>'+(cp.length?cp.map(x=>'<p><b>'+esc(x.name)+'</b> <span class="mono">×'+esc(x.count)+'</span></p>').join(''):'<p class="empty">No social-ledger co-presence recovered.</p>')+'</div></div></div>';
}
function timelineHtml(){
 const all=[];for(const x of arr(dossier.chronology?.cast_period_roles))all.push({date:x.period,title:x.role,summary:'Cast-book period role'});for(const x of arr(dossier.chronology?.recovered_social_days))all.push({date:x.date,title:x.title,summary:x.minimum_event});for(const x of arr(dossier.highlighted_incidents))all.push({date:x.date,title:x.title,summary:x.summary});
 const seen=new Set(),uniq=all.filter(x=>{const k=x.date+'|'+x.title;if(seen.has(k))return false;seen.add(k);return true});
 return'<div class="timeline">'+(uniq.length?uniq.map(x=>'<article class="event"><time>'+esc(x.date)+'</time><h3>'+esc(x.title)+'</h3><p>'+esc(x.summary||'')+'</p></article>').join(''):'<p class="empty">No dated events loaded.</p>')+'</div>';
}
function associationsHtml(){const list=associationMatches(current).sort((a,b)=>(b.count||0)-(a.count||0));return'<div class="block"><h2>Source-derived associations</h2><p class="muted">Co-presence does not itself prove friendship, alliance, motive or conflict.</p>'+(list.length?list.map(e=>{const other=e.a===current?e.b:e.a;return'<article class="event"><h3>'+esc(other)+' <span class="mono">×'+esc(e.count||1)+'</span></h3><p>'+esc(arr(e.contexts).slice(0,4).join(' · ')||e.summary||'')+'</p><small>'+esc(arr(e.dates).join(', '))+'</small></article>'}).join(''):'<p class="empty">No association edges in current network.</p>')+'</div>'}
function storiesHtml(){const list=storyMatches(current),inc=incidentMatches(current);return'<div class="two"><div class="block"><h2>Story appearances</h2>'+(list.length?list.map(s=>'<a class="story-link" href="'+route(s.path)+'"><b>'+esc(s.title)+'</b><br><small>'+esc(s.mode||'')+'</small></a>').join(''):'<p class="empty">No explicit Story links indexed yet.</p>')+'</div><div class="block"><h2>Indexed incidents</h2>'+(inc.length?inc.map(x=>'<article class="event"><time>'+esc(x.date)+'</time><h3>'+esc(x.title)+'</h3><small>'+esc(arr(x.type).join(' / '))+'</small></article>').join(''):'<p class="empty">No CIA incident entries yet.</p>')+'</div></div>'}
function rolesHtml(){
 const list=roleMatches(current),symbolic=arr(dossier.symbolic_roles),census=roleCensusFor(current),casebook=arr(dossier.cia_record?.casebook?.cases).slice(0,6),highlighted=arr(dossier.highlighted_incidents).slice(0,6),cases=casebook.length?casebook:highlighted.map(x=>({date:x.date,title:x.title,what_happened:x.summary,source_mode:'highlighted dossier incident',evidence_status:'Use Timeline/Sources for provenance depth'}));
 const indexed=list.length?list.map(x=>'<article class="role-evidence-card"><div class="role-evidence-head"><h3>'+esc(x.role)+'</h3><span>'+esc(x.role_family||'role')+'</span></div><p>'+esc(x.note||x.role_definition||'')+'</p><small>'+esc(x.date||'date unresolved')+' · '+esc(x.status||'status unresolved')+'</small><p class="role-boundary"><b>Boundary:</b> '+esc(roleBoundary(x.role))+'</p></article>').join(''):'<p class="empty">No indexed role assignment is currently attached to this dossier.</p>';
 const local=symbolic.length?symbolic.map(x=>{const name=typeof x==='string'?x:(x.role||'symbolic role'),scope=typeof x==='string'?'':(x.scope||x.note||''),date=typeof x==='string'?'':(x.date||'');return'<article class="role-evidence-card role-evidence-card--symbolic"><div class="role-evidence-head"><h3>'+esc(name)+'</h3><span>project / mythic</span></div>'+(scope?'<p>'+esc(scope)+'</p>':'')+(date?'<small>'+esc(date)+'</small>':'')+'<p class="role-boundary"><b>Boundary:</b> '+esc(roleBoundary(name))+'</p></article>'}).join(''):'<p class="empty">No dossier-local symbolic-role records.</p>';
 const normalized=census?'<div class="role-synthesis"><p><b>Normalized posture:</b> '+esc(census.role_posture||'unresolved')+'</p><p><b>Narrative functions:</b> '+(arr(census.narrative_functions).length?arr(census.narrative_functions).map(esc).join(' · '):'none normalized')+'</p><div class="role-list">'+arr(census.symbolic_roles).map(x=>'<span class="role">'+esc(x)+'</span>').join('')+'</div><p class="muted">'+esc(census.rule||roleCensus?.accounting_principle||'Role labels do not establish conduct.')+'</p></div>':'<p class="empty">No normalized census row.</p>';
 const context=cases.length?cases.map(x=>'<article class="case-context"><time>'+esc(x.date||'date unresolved')+'</time><h3>'+esc(x.title||'Recovered exchange / case')+'</h3><p>'+esc(x.what_happened||x.summary||'')+'</p><small>'+esc([x.source_mode,x.evidence_status].filter(Boolean).join(' · '))+'</small></article>').join(''):'<p class="empty">No scene-level casebook context loaded. Use Timeline and Sources before treating a role as evidence.</p>';
 return '<p class="ledger-boundary"><b>Role-reading rule:</b> event first, evidence second, relationship change third, current state fourth, archetype last. Dog, Farmer, Footstool, Mud Dweller, Guardian and similar terms are project grammar unless a source explicitly establishes something more concrete.</p><div class="role-evidence-grid"><section class="block"><h2>Normalized role synthesis</h2>'+normalized+'</section><section class="block"><h2>Indexed role evidence</h2>'+indexed+'</section><section class="block"><h2>Dossier symbolic roles</h2>'+local+'</section><section class="block"><h2>Exchange / casebook context</h2><p class="muted">These scenes are the documentary spine near the role material. They contextualize the label; they do not automatically prove the interpretation.</p>'+context+'</section></div>';
}
function accountHtml(){
 const a=accountData(),rows=a.entries;
 return'<div class="block"><h2>Symbolic account statement</h2><p class="ledger-boundary">Potatoverse accounting only. This does not claim objective morality, legal liability, financial debt, guilt or human worth. “Moral bankruptcy” may appear only as an explicitly sourced project phrase, never as an automatic system verdict.</p>'+
 (rows.length?'<table class="ledger"><thead><tr><th>Date</th><th>Entry</th><th>Scale</th><th>Status</th><th>Source</th></tr></thead><tbody>'+rows.map(x=>{const provenance=[x.source_mode||x.source_ref||'project record',x.evidence_tier?('evidence: '+x.evidence_tier):'',x.debt_evidence_id?('debt id: '+x.debt_evidence_id):''].filter(Boolean).join(' · ');return '<tr><td>'+esc(x.date||'—')+'</td><td>'+esc(x.kind||x.type||'entry')+'<br><span class="muted">'+esc(x.note||'')+'</span></td><td>'+esc(x.amount_or_scale||x.amount||'symbolic')+'</td><td>'+esc(x.status||'open')+'</td><td>'+esc(provenance)+'</td></tr>'}).join('')+'</tbody></table>':'<p class="empty">No scored ledger entries. Account remains unassessed rather than inventing a balance.</p>')+
 '<div class="block"><h3>Outstanding / repair / recovery</h3>'+(a.outstanding.length?'<ul>'+a.outstanding.map(x=>'<li>'+esc(typeof x==='string'?x:(x.note||x.condition||JSON.stringify(x)))+'</li>').join('')+'</ul>':'<p class="empty">No open symbolic obligations recorded.</p>')+'</div></div>';
}
function mediaHtml(){
 const media=arr(dossier.media?.evidence_images),symbols=symbolicImages();
 const evidence=media.length?'<div class="media-grid">'+media.map(x=>'<figure class="media-card"><img src="'+esc(route(x.src))+'" alt="'+esc(x.alt||x.caption||'CIA dossier evidence image')+'"><p>'+esc(x.caption||'')+(x.source_ref?'<br>'+esc(x.source_ref):'')+'</p></figure>').join('')+'</div>':'<p class="empty">No sourced documentary/project images attached yet.</p>';
 const proxies=symbols.length?'<h3>Symbolic proxies</h3><p class="ledger-boundary">These are humorous role-symbol illustrations, not portraits or likeness claims about the dossier subject.</p><div class="media-grid">'+symbols.map(x=>'<figure class="media-card proxy-card"><img src="'+esc(x.image_url)+'" alt="'+esc(x.label+' symbolic proxy image')+'"><p><b>'+esc(x.label)+'</b><br>'+esc(x.caption)+'<br>'+esc(x.author)+' · '+esc(x.license)+' · <a href="'+esc(x.source_page)+'" target="_blank" rel="noopener">source</a></p></figure>').join('')+'</div>':'';
 return'<div class="block"><h2>Images & visual evidence</h2><p class="muted">Documentary images require dossier-owned provenance. Symbolic proxies come from the shared Commons pool and are always labeled as non-likeness illustrations.</p>'+evidence+proxies+'</div>';
}
function enhancementsHtml(){const e=enhancementFor(current);if(!e)return'<p class="empty">No enhancement/capability sheet recovered yet.</p>';const ordinary=arr(e.ordinary),creative=arr(e.creative);return'<div class="two"><div class="block"><h2>Ordinary / documentary capabilities</h2>'+(ordinary.length?'<ul>'+ordinary.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':'<p class="empty">none recovered</p>')+'</div><div class="block"><h2>Creative / project enhancements</h2>'+(creative.length?'<ul>'+creative.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':'<p class="empty">none recovered</p>')+'</div></div><p class="stamp">SOURCE BOUNDARY</p><p>'+esc(e.boundary||'Keep documentary and creative traits separate.')+'</p>'}
function sourcesHtml(){const ss=arr(dossier.source_strata),leads=arr(dossier.recovery_leads);return'<div class="two"><div class="block"><h2>Source strata</h2>'+(ss.length?ss.map(s=>sourceRef(s.path,(s.type||'source')+' → '+(s.path||'path unavailable'))).join(''):'<p class="empty">No source routes indexed.</p>')+'</div><div class="block"><h2>Open recovery leads</h2>'+(leads.length?'<ul>'+leads.map(x=>'<li>'+esc(x)+'</li>').join(''):'<p class="empty">No current recovery leads.</p>')+'</div></div>'}
function render(){
 const a=activityBand();document.title=(dossier.display_name||current)+' — CIA File';document.getElementById('sheet').dataset.activity=a[0];document.getElementById('fileId').textContent='FILE '+current.toUpperCase()+' · '+(dossier.entity_class||'ENTITY');document.getElementById('name').textContent=dossier.display_name||current;document.getElementById('summary').textContent=dossier.tim_relation?.editorial_reading||'Persistent Potatoverse dossier.';
 const census=roleCensusFor(current),roleBadges=arr(census?.symbolic_roles).slice(0,2).map(x=>'role: '+x);
 document.getElementById('badges').innerHTML=[dossier.archive_status,dossier.room_policy,...roleBadges,...arr(dossier.tim_relation?.archetypes).slice(0,3)].filter(Boolean).map(x=>'<span class="badge">'+esc(x)+'</span>').join('');
 renderMug();renderAccountStrip();
 document.getElementById('overview').innerHTML=meaningHtml()+overviewHtml();document.getElementById('bankLink').href='../bank/?character='+encodeURIComponent(current);document.getElementById('timeline').innerHTML=timelineHtml();document.getElementById('associations').innerHTML=associationsHtml();document.getElementById('stories').innerHTML=storiesHtml();document.getElementById('roles').innerHTML=rolesHtml();document.getElementById('account').innerHTML=accountHtml();document.getElementById('media').innerHTML=mediaHtml();document.getElementById('enhancements').innerHTML=enhancementsHtml();document.getElementById('sources').innerHTML=sourcesHtml();document.getElementById('rawLink').href=route('knowledge/cia/characters/'+current+'.json');
}
async function load(id){current=id;history.replaceState(null,'','?character='+encodeURIComponent(id));try{dossier=await get('knowledge/cia/characters/'+id+'.json');render()}catch(e){document.getElementById('name').textContent='File not found';document.getElementById('summary').textContent='This entity does not yet have a deep CIA JSON dossier.'}}
function shuffle(){const figs=arr(manifest?.characters).map(x=>x.id).filter(x=>x!==current);if(figs.length)load(figs[Math.floor(Math.random()*figs.length)])}
document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.panel).classList.add('active')}));
document.getElementById('shuffleTop').onclick=shuffle;document.getElementById('shuffleBottom').onclick=shuffle;
(async()=>{[manifest,roles,roleCensus,stories,associations,incidents,enhancements,accountContract,mudBankContract,symbolicPool]=await Promise.all([get('knowledge/cia/manifest.json'),get('knowledge/cia/role-index.json'),get('knowledge/cia/role-archetype-census.json'),get('knowledge/cia/story-links.json'),get('knowledge/cia/associations/network.json'),get('knowledge/cia/incidents/index.json'),get('knowledge/cia/enhancements-index.json'),get('knowledge/cia/symbolic-account-contract.json'),get('knowledge/cia/mud-bank-contract.json'),get('knowledge/cia/symbolic-image-pool.json')]);await load(current);setInterval(()=>{const el=document.getElementById('dossierWelfare');if(el)el.textContent=welfareLabel()},1000)})().catch(()=>{document.getElementById('summary').textContent='The cabinet could not load one of its indexes.'});
})();
