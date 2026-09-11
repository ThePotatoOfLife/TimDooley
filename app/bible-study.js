(()=>{
'use strict';

const $=id=>document.getElementById(id);
const ROLL_LABEL='ROLL';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const asArray=value=>Array.isArray(value)?value:(value==null?[]:[value]);
const dateOnly=value=>String(value||'').slice(0,10);
const unique=values=>[...new Set(values.filter(Boolean))];
const norm=value=>String(value||'').toLowerCase();
const safeJSON=async url=>{try{const response=await fetch(url);return response.ok?await response.json():null}catch(error){console.warn('Bible study data load failed',url,error);return null}};

const PATHS={
 field:'../../knowledge/traditions/biblical-syncretism-field.json',
 fragments:'../../knowledge/traditions/biblical-passage-fragments.json',
 angelField:'../../knowledge/traditions/biblical-angel-eye-sprout-atlas.json',
 angelFragments:'../../knowledge/traditions/biblical-angel-eye-sprout-fragments.json',
 attestations:'../../knowledge/chronology/tim-biblical-vocabulary-attestation-ledger.json',
 reverse:'../../knowledge/chronology/reverse-biblical-overlap-timeline-2025-2026.json',
 occurrences:'../../data/evidence/rational-potato-x-occurrence-ledger-2024-2026.json',
 timeline:'../../data/timeline-events.json',
 packs:'../../data/timeline-event-packs/index.json'
};

const VIEW_DEFS={
 jesus:{label:'Jesus / Son',terms:['jesus','christ','son','thomas','messiah','lion','lamb','cross','crucif','resurrection','tomb','bread','grain of wheat','cornerstone','son of man']},
 'tim-said':{label:'Tim said it',predicate:(row,ctx)=>ctx.exactFor(row).direct.length>0||['tim-explicit','public-occurrence','conversation-recovery','book-explicit'].includes(row.discovery_mode)},
 'tim-lived':{label:'Tim lived it',terms:['tree ordeal','prison','custody','rejected','outside the gate','death','return','burial','root','garden','stone','footstool','ladder'],predicate:row=>['later-structural-parallel','mixed-explicit-and-later','tim-led-discovery'].includes(row.relation_class)},
 prophecy:{label:'Prophecy / foresight',predicate:row=>['explicit-prediction-before-event','foresight-or-warning-before-event'].includes(row.prophecy_status)||containsTerms(row,['prophecy','foresight','prediction','predicted','warning before'])},
 'father-house':{label:'Father / House',terms:['father','house','gardener','throne','most high','seat','rooms','mansions','source']},
 'door-ladder':{label:'Door / Ladder',terms:['door','gate','ladder','needle','heaven','jacob','guardians']},
 'death-return':{label:'Death / return',terms:['death','dead','crucif','tomb','burial','resurrection','return','grain','seed']},
 'revelation-zion':{label:'Revelation / Zion',terms:['revelation','zion','new jerusalem','144000','144,000','lion','lamb','root of david','throne','river','tree of life','north']},
 'counter-texts':{label:'Counter-texts',predicate:row=>row.relation_class==='counter-text'||Boolean(row.counter_text||row.source_correction)},
 all:{label:'Everything',predicate:()=>true}
};

function relationText(row){return [row.id,row.actor,row.project_anchor,row.discovery_mode,row.relation_class,row.source_direction,row.counter_text,row.source_correction,row.prophecy_status,...asArray(row.biblical_refs),...asArray(row.motifs)].join(' ').toLowerCase()}
function containsTerms(row,terms){const text=relationText(row);return terms.some(term=>text.includes(norm(term)))}
function viewMatches(row,view,ctx){const def=VIEW_DEFS[view]||VIEW_DEFS.jesus;const termsMatch=!def.terms||containsTerms(row,def.terms);const predicateMatch=!def.predicate||def.predicate(row,ctx);if(def.terms&&def.predicate)return termsMatch||predicateMatch;return termsMatch&&predicateMatch}

function bookFromRef(reference){
 const ref=String(reference||'').trim();
 const match=ref.match(/^((?:[1-3]\s+)?[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+\d/);
 if(match)return match[1];
 const known=['Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth','Samuel','Kings','Chronicles','Ezra','Nehemiah','Esther','Job','Psalm','Psalms','Proverbs','Ecclesiastes','Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi','Matthew','Mark','Luke','John','Acts','Romans','Corinthians','Galatians','Ephesians','Philippians','Colossians','Thessalonians','Timothy','Titus','Philemon','Hebrews','James','Peter','Jude','Revelation'];
 return known.find(name=>ref.includes(name))||'';
}

function relationHasBook(row,book){if(!book)return true;return asArray(row.biblical_refs).some(ref=>bookFromRef(ref)===book||norm(ref).includes(norm(book)))}
function fragmentsFor(row,fragments){const refs=asArray(row.biblical_refs);return fragments.filter(fragment=>asArray(fragment.matches||fragment.reference).some(match=>refs.includes(match)))}
function wordingForAttestation(entry){return unique([...asArray(entry.wording),entry.wording_summary,...asArray(entry.signals)].filter(Boolean))}
function ownerHref(owner){const value=String(owner||'');if(!value)return '';if(/^https?:\/\//i.test(value))return value;return '../../'+value.split('/').map(encodeURIComponent).join('/')}

async function loadTimeline(){
 const [base,index]=await Promise.all([safeJSON(PATHS.timeline),safeJSON(PATHS.packs)]);
 const events=[...((base&&base.events)||[])];
 if(index){const packs=await Promise.all(asArray(index.packs).map(name=>safeJSON('../../data/timeline-event-packs/'+encodeURIComponent(name))));packs.filter(Boolean).forEach(pack=>events.push(...asArray(pack.events)))}
 return events;
}

async function init(){
 const relationsEl=$('relations'),statsEl=$('study-count'),activeViewEl=$('active-view');
 try{
  const [field,fragmentData,angelField,angelFragmentData,attestationData,reverseData,occurrenceData,timelineEvents]=await Promise.all([
   safeJSON(PATHS.field),safeJSON(PATHS.fragments),safeJSON(PATHS.angelField),safeJSON(PATHS.angelFragments),safeJSON(PATHS.attestations),safeJSON(PATHS.reverse),safeJSON(PATHS.occurrences),loadTimeline()
  ]);
  if(!field||!fragmentData)throw new Error('canonical Bible field or passage fragments unavailable');

  const rows=[...asArray(field.relations),...asArray(angelField&&angelField.relations)];
  const fragments=[...asArray(fragmentData.fragments),...asArray(angelFragmentData&&angelFragmentData.fragments)];
  const attestations=asArray(attestationData&&attestationData.entries);
  const reverseEvents=asArray(reverseData&&reverseData.events);
  const occurrences=asArray(occurrenceData&&occurrenceData.occurrences);
  const occurrenceById=new Map(occurrences.map(item=>[item.id,item]));
  const eventById=new Map(timelineEvents.map(item=>[item.id,item]));
  const relationClassLabels=new Map(asArray(field.relation_classes).map(item=>[item.id,item.meaning||item.id]));
  const discoveryLabels=new Map(asArray(field.discovery_modes).map(item=>[item.id,item.label||item.id]));
  const occurrenceByDate=groupByDate(occurrences,item=>item.date);
  const attestationByDate=groupByDate(attestations,item=>item.date||item.datetime_utc);
  const reverseByDate=groupByDate(reverseEvents,item=>item.date);
  const timelineByDate=groupByDate(timelineEvents,item=>item.date||item.timestamp);

  const exactFor=row=>{
   const direct=asArray(row.occurrence_ids).map(id=>occurrenceById.get(id)).filter(Boolean);
   const sameDate=occurrenceByDate.get(dateOnly(row.date||row.timestamp))||[];
   return {direct,sameDate};
  };
  const ctx={exactFor};

  const state={
   view:validView(new URLSearchParams(location.search).get('view')),
   query:'',actor:'',mode:'',klass:'',book:'',minStrength:0,exactOnly:false,focusedId:null
  };

  populateSelect($('actor'),unique(rows.map(row=>row.actor)).sort());
  populateSelect($('discovery-mode'),unique(rows.map(row=>row.discovery_mode)).sort(),value=>discoveryLabels.get(value)||value);
  populateSelect($('relation-class'),unique(rows.map(row=>row.relation_class)).sort(),value=>value.replaceAll('-',' '));
  populateSelect($('bible-book'),unique(rows.flatMap(row=>asArray(row.biblical_refs).map(bookFromRef))).sort());

  $('minimum-strength').innerHTML='<option value="0">Any strength</option>'+[1,2,3,4,5].map(n=>`<option value="${n}">${n}+</option>`).join('');
  $('roll-relation').textContent=ROLL_LABEL;

  const render=()=>{
   const filtered=rows.filter(row=>matchesAll(row,state,ctx,{fragments,occurrenceByDate,attestationByDate}));
   activeViewEl.textContent=(VIEW_DEFS[state.view]||VIEW_DEFS.jesus).label;
   statsEl.textContent=`${filtered.length} of ${rows.length} relations`;
   updateViewButtons(state.view);
   relationsEl.innerHTML=filtered.length?filtered.map(row=>renderRelation(row,{fragments,occurrenceByDate,attestationByDate,reverseByDate,timelineByDate,eventById,relationClassLabels,discoveryLabels,state})).join(''):'<div class="empty">No relations match this study state.</div>';
   if(state.focusedId){requestAnimationFrame(()=>focusRelation(state.focusedId,false))}
  };

  $('search').addEventListener('input',event=>{state.query=event.target.value.trim();render()});
  $('clear-search').addEventListener('click',()=>{$('search').value='';state.query='';render()});
  $('actor').addEventListener('change',event=>{state.actor=event.target.value;render()});
  $('discovery-mode').addEventListener('change',event=>{state.mode=event.target.value;render()});
  $('relation-class').addEventListener('change',event=>{state.klass=event.target.value;render()});
  $('bible-book').addEventListener('change',event=>{state.book=event.target.value;render()});
  $('minimum-strength').addEventListener('change',event=>{state.minStrength=Number(event.target.value)||0;render()});
  $('exact-wording-only').addEventListener('change',event=>{state.exactOnly=event.target.checked;render()});
  $('reset-filters').addEventListener('click',()=>{resetFilters(state);syncFilterControls(state);render()});
  $('filter-toggle').addEventListener('click',()=>{const panel=$('bible-filters');panel.hidden=!panel.hidden;$('filter-toggle').setAttribute('aria-expanded',String(!panel.hidden))});

  $('study-modes').querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{
   state.view=validView(button.dataset.view);state.focusedId=null;setViewParam(state.view);render();
  }));

  $('roll-relation').addEventListener('click',()=>{
   const filtered=rows.filter(row=>matchesAll(row,state,ctx,{fragments,occurrenceByDate,attestationByDate}));
   if(!filtered.length)return;
   const chosen=filtered[Math.floor(Math.random()*filtered.length)];state.focusedId=chosen.id;render();requestAnimationFrame(()=>focusRelation(chosen.id,true));
  });

  relationsEl.addEventListener('click',event=>{
   const button=event.target.closest('[data-focus-relation]');if(!button)return;
   state.focusedId=button.dataset.focusRelation;focusRelation(state.focusedId,true);
  });

  syncFilterControls(state);render();
 }catch(error){
  console.error(error);statsEl.textContent='Bible study data unavailable';relationsEl.innerHTML='<div class="empty load-error">The comparison program could not load its canonical data.</div>';
 }
}

function groupByDate(items,getDate){const map=new Map();items.forEach(item=>{const date=dateOnly(getDate(item));if(!date)return;if(!map.has(date))map.set(date,[]);map.get(date).push(item)});return map}
function populateSelect(select,values,labeler=value=>value){values.forEach(value=>{if(!value)return;const option=document.createElement('option');option.value=value;option.textContent=labeler(value);select.appendChild(option)})}
function validView(value){return Object.prototype.hasOwnProperty.call(VIEW_DEFS,value)?value:'jesus'}
function setViewParam(view){const url=new URL(location.href);if(view==='jesus')url.searchParams.delete('view');else url.searchParams.set('view',view);history.replaceState({},'',url)}
function updateViewButtons(view){$('study-modes').querySelectorAll('[data-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view===view)))}
function resetFilters(state){state.query='';state.actor='';state.mode='';state.klass='';state.book='';state.minStrength=0;state.exactOnly=false;state.focusedId=null;$('search').value=''}
function syncFilterControls(state){$('actor').value=state.actor;$('discovery-mode').value=state.mode;$('relation-class').value=state.klass;$('bible-book').value=state.book;$('minimum-strength').value=String(state.minStrength);$('exact-wording-only').checked=state.exactOnly}

function exactEvidenceForSearch(row,context){
 const date=dateOnly(row.date||row.timestamp);
 const exact=[...asArray(row.project_quote),...asArray(row.tim_quote),...asArray(row.quote)];
 const directIds=asArray(row.occurrence_ids);
 const sameDate=context.occurrenceByDate.get(date)||[];
 sameDate.filter(item=>directIds.includes(item.id)).forEach(item=>exact.push(item.quote));
 (context.attestationByDate.get(date)||[]).forEach(item=>exact.push(...wordingForAttestation(item)));
 return unique(exact);
}

function matchesAll(row,state,ctx,context){
 if(!viewMatches(row,state.view,ctx))return false;
 if(state.actor&&row.actor!==state.actor)return false;
 if(state.mode&&row.discovery_mode!==state.mode)return false;
 if(state.klass&&row.relation_class!==state.klass)return false;
 if(state.book&&!relationHasBook(row,state.book))return false;
 if(Number(row.strength||0)<state.minStrength)return false;
 const exact=exactEvidenceForSearch(row,context);
 if(state.exactOnly&&!exact.length)return false;
 if(state.query){
  const matchedFragments=fragmentsFor(row,context.fragments);
  const sameDate=context.occurrenceByDate.get(dateOnly(row.date||row.timestamp))||[];
  const hay=[relationText(row),...exact,...sameDate.map(item=>item.quote),...matchedFragments.map(item=>`${item.reference} ${item.text}`)].join(' ').toLowerCase();
  const terms=state.query.toLowerCase().split(/\s+/).filter(Boolean);if(!terms.every(term=>hay.includes(term)))return false;
 }
 return true;
}

function renderRelation(row,context){
 const date=dateOnly(row.date||row.timestamp);
 const matchedFragments=fragmentsFor(row,context.fragments);
 const explicitQuotes=unique([...asArray(row.project_quote),...asArray(row.tim_quote),...asArray(row.quote)]);
 const directOccurrenceIds=asArray(row.occurrence_ids);
 const sameDateOccurrences=context.occurrenceByDate.get(date)||[];
 const directOccurrences=directOccurrenceIds.map(id=>sameDateOccurrences.find(item=>item.id===id)).filter(Boolean);
 directOccurrences.forEach(item=>explicitQuotes.push(item.quote));
 const exactQuotes=unique(explicitQuotes);
 const sameDateContext=sameDateOccurrences.filter(item=>!directOccurrenceIds.includes(item.id));
 const attestations=context.attestationByDate.get(date)||[];
 const reversals=context.reverseByDate.get(date)||[];
 const explicitEventIds=asArray(row.timeline_event_ids);
 const explicitEvents=explicitEventIds.map(id=>context.eventById.get(id)).filter(Boolean);
 const sameDateEvents=(context.timelineByDate.get(date)||[]).filter(event=>!explicitEventIds.includes(event.id));
 const boundary=row.counter_text||row.source_correction||'';
 const relationMeaning=context.relationClassLabels.get(row.relation_class)||row.relation_class||'';
 const discoveryMeaning=context.discoveryLabels.get(row.discovery_mode)||row.discovery_mode||'';
 const exactChip=exactQuotes.length?' <span class="chip exact">exact wording</span>':'';

 const projectSide=`<section class="side"><h3>Tim / Son / project</h3><span class="summary-label">Canonical relation anchor</span><p class="project-anchor">${esc(row.project_anchor)}</p>${exactQuotes.map(quote=>`<blockquote class="exact-quote">${esc(quote)}<span class="quote-meta">Exact / recovered wording explicitly attached to this relation</span></blockquote>`).join('')}</section>`;
 const scriptureSide=`<section class="side scripture"><h3>Bible</h3>${matchedFragments.length?matchedFragments.map(fragment=>`<blockquote class="bible-quote">${esc(fragment.text)}<cite>${esc(fragment.reference)} · ${esc(fragment.translation||'WEB')}</cite></blockquote>`).join(''):`<p class="no-fragment">This row points to a chapter, narrative or tradition broader than the excerpt registry. Scripture scope remains visible below.</p>`}</section>`;

 const sameDateHtml=sameDateContext.length?`<section class="context-card exact-context full"><h4>Same-date public wording</h4><p class="circumstantial">Circumstantial context only: these are exact public occurrences from the same date. They are not silently treated as direct proof of this relation.</p>${sameDateContext.slice(0,8).map(item=>`<blockquote>${esc(item.quote)}<span class="quote-meta">${esc(item.id)} · ${esc((item.tags||[]).join(' · '))}</span></blockquote>`).join('')}</section>`:'';
 const attestationHtml=attestations.length?`<section class="context-card full"><h4>Biblical vocabulary / revelation context</h4>${attestations.slice(0,8).map(item=>{const wording=wordingForAttestation(item);return `${wording.map(text=>`<blockquote>${esc(text)}</blockquote>`).join('')}${item.development?`<p>${esc(item.development)}</p>`:''}${item.source_class?`<p class="circumstantial">Source class: ${esc(item.source_class)}</p>`:''}`}).join('')}</section>`:'';
 const reverseHtml=reversals.length?`<section class="context-card reverse"><h4>Reverse chronology / later recognition</h4>${reversals.slice(0,5).map(item=>`<p><strong>${esc(item.status||'tim-first chronology')}</strong> ${esc(item.significance||item.finding||'')}</p>`).join('')}</section>`:'';
 const boundaryHtml=boundary?`<section class="context-card boundary"><h4>Mismatch / correction</h4><p>${esc(boundary)}</p></section>`:'';
 const sourceDirectionHtml=row.source_direction?`<section class="context-card"><h4>Which came first?</h4><p>${esc(row.source_direction)}</p></section>`:'';
 const prophecyHtml=row.prophecy_status?`<section class="context-card"><h4>Prophecy / foresight status</h4><p>${esc(row.prophecy_status.replaceAll('-',' '))}</p>${row.prediction_date?`<p>Prediction: ${esc(row.prediction_date)}</p>`:''}${row.target_event_date?`<p>Target event: ${esc(row.target_event_date)}</p>`:''}</section>`:'';
 const ownerHtml=renderOwners(row);
 const timelineHtml=renderTimelineLinks(explicitEvents,sameDateEvents);

 return `<article class="relation${context.state.focusedId===row.id?' is-focus':''}" id="rel-${esc(row.id)}"><div class="relation-head"><div><h2 class="relation-title">${esc(row.project_anchor)}</h2><div class="relation-meta"><span class="chip">${esc(row.date||row.timestamp||'undated')}</span><span class="chip">${esc(row.actor||'unassigned')}</span><span class="chip">${esc(row.discovery_mode||'unclassified')}</span><span class="chip">${esc(row.relation_class||'unclassified')}</span><span class="chip strength">strength ${esc(row.strength||'?')}</span>${exactChip}</div></div><code class="relation-id">${esc(row.id)}</code></div><div class="parallel">${projectSide}${scriptureSide}</div><p class="scope"><strong>Scripture scope:</strong> ${asArray(row.biblical_refs).map(esc).join(' · ')||'broader biblical tradition'}</p><p class="motifs"><strong>Motifs:</strong> ${asArray(row.motifs).map(esc).join(' · ')||'—'}</p><div class="context-grid"><section class="context-card"><h4>How this relation is classified</h4><p><strong>${esc((row.relation_class||'relation').replaceAll('-',' '))}</strong> — ${esc(relationMeaning)}</p><p><strong>${esc(row.discovery_mode||'unknown discovery mode')}</strong> — ${esc(discoveryMeaning)}</p></section>${sourceDirectionHtml}${prophecyHtml}${boundaryHtml}${reverseHtml}${sameDateHtml}${attestationHtml}${timelineHtml}${ownerHtml}</div><div class="card-actions"><button type="button" data-focus-relation="${esc(row.id)}">Focus this relation</button></div></article>`;
}

function renderOwners(row){const owners=unique([...asArray(row.analysis_refs),...asArray(row.source_refs),...asArray(row.owners)]);if(!owners.length)return '';return `<section class="context-card sources full"><h4>Deeper records / source owners</h4><div class="owner-links">${owners.map(owner=>`<a href="${esc(ownerHref(owner))}"><code>${esc(owner)}</code></a>`).join('')}</div></section>`}
function renderTimelineLinks(explicitEvents,sameDateEvents){const all=[...explicitEvents.slice(0,8),...sameDateEvents.slice(0,8)];if(!all.length)return '';return `<section class="context-card full"><h4>Timeline</h4>${explicitEvents.length?'<p class="circumstantial">Explicitly linked timeline event(s) first.</p>':'<p class="circumstantial">Same-date timeline context. This is chronology, not automatic proof of the biblical relation.</p>'}<div class="timeline-links">${all.map(event=>`<a class="event-link" href="../../chronology/?tl_event=${encodeURIComponent(event.id)}">${esc(event.date||'')} · ${esc(event.title||event.id)}</a>`).join('')}</div></section>`}
function focusRelation(id,scroll){document.querySelectorAll('.relation.is-focus').forEach(el=>el.classList.remove('is-focus'));const el=$('rel-'+id);if(!el)return;el.classList.add('is-focus');if(scroll)el.scrollIntoView({behavior:'smooth',block:'start'})}

document.addEventListener('DOMContentLoaded',init);
})();
