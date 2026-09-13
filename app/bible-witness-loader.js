(()=>{
'use strict';

const upstreamFetch=window.fetch.bind(window);
const FIELD_SUFFIX='biblical-syncretism-field.json';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
const uniq=values=>[...new Set(values.filter(Boolean).map(value=>String(value).trim()).filter(Boolean))];
let rows=new Map();

function first(...values){
  for(const value of values){
    if(typeof value==='string'&&value.trim()) return value.trim();
  }
  return '';
}
function quotesFor(row){
  return uniq([
    ...arr(row.project_quote),
    ...arr(row.exact_wording),
    ...arr(row.public_wording),
    ...arr(row.recovered_wording),
    row.quote
  ]);
}
function textList(values){return uniq(values).join(' · ')}
function sequence(values){return uniq(values).join(' → ')}

function projectSceneText(row,scene){
  // Deliberately avoid comparative research-summary fields here.
  // Several current wave records use those fields for later commentary rather than scene evidence.
  return first(
    scene.summary,
    row.project_anchor,
    quotesFor(row)[0],
    row.title
  );
}
function chronologyText(row,scene,discovery){
  const parts=[];
  if(scene.before) parts.push(`Before: ${scene.before}`);
  if(scene.lead_up) parts.push(scene.lead_up);
  if(scene.after) parts.push(`After: ${scene.after}`);
  if(discovery.project_anchor_date && discovery.first_comparison_date &&
     String(discovery.project_anchor_date)!==String(discovery.first_comparison_date)){
    parts.push(`The project-side anchor is dated ${discovery.project_anchor_date}; the comparison is recorded later, on ${discovery.first_comparison_date}.`);
  }
  if(discovery.scripture_explicit_at_time===false){
    parts.push('The cited scripture is not recorded as explicit in the project-side event itself.');
  }else if(discovery.scripture_explicit_at_time===true){
    parts.push('Scriptural language was already explicit in the project-side material at the time.');
  }
  return parts.join(' ');
}
function biblicalSceneText(row,scripture){
  return first(
    scripture.literary_context,
    scripture.canonical_context,
    scripture.historical_context,
    row.biblical_refs?.length ? `Read the cited passages in their own settings: ${textList(row.biblical_refs)}.` : ''
  );
}
function rhymeText(row,argument){
  return first(
    argument.why_dense,
    argument.why_it_matters,
    arr(row.relation_arguments).join(' '),
    row.overlap,
    row.project_value
  );
}
function discoveryText(row,argument,discovery){
  const parts=[];
  if(discovery.source_direction||row.source_direction){
    parts.push(discovery.source_direction||row.source_direction);
  }
  if(discovery.first_comparison_date){
    parts.push(`First recorded comparison: ${discovery.first_comparison_date}.`);
  }
  if(discovery.first_formal_archive_date){
    parts.push(`Formal archive entry: ${discovery.first_formal_archive_date}.`);
  }
  if(argument.project_sequence?.length){
    parts.push(`Project sequence: ${sequence(argument.project_sequence)}.`);
  }
  if(argument.biblical_sequence?.length){
    parts.push(`Biblical sequence: ${sequence(argument.biblical_sequence)}.`);
  }
  return parts.join(' ');
}
function counterpressureText(row,argument){
  return first(
    row.mismatch,
    arr(row.weaknesses).join(' '),
    row.counter_text,
    row.source_correction,
    row.difference,
    row.boundary,
    argument.maximum_claim
  );
}
function sourceStatus(row,scene){
  return first(scene.source_status,row.wording_status,row.evidence_kind,row.discovery_mode,'source status not classified');
}
function p(text,className=''){
  return text?`<p${className?` class="${className}"`:''}>${esc(text)}</p>`:'';
}
function quoteHtml(quotes){
  return quotes.slice(0,3).map(item=>`<blockquote class="witness-quote">${esc(item)}</blockquote>`).join('');
}
function chapter(label,title,body,className=''){
  if(!body) return '';
  return `<section class="witness-chapter ${className}">
    <div class="witness-label">${esc(label)}</div>
    <h3>${esc(title)}</h3>
    ${body}
  </section>`;
}

function witnessFor(row){
  const scene=row.scene_context||{};
  const scripture=row.scripture_context||{};
  const argument=row.relation_argument||{};
  const discovery=row.discovery_history||{};
  const quotes=quotesFor(row);
  return {
    scene,scripture,argument,discovery,quotes,
    project:projectSceneText(row,scene),
    chronology:chronologyText(row,scene,discovery),
    bible:biblicalSceneText(row,scripture),
    rhyme:rhymeText(row,argument),
    discoveryBody:discoveryText(row,argument,discovery),
    pressure:counterpressureText(row,argument),
    refs:textList(row.biblical_refs),
    opening:`${row.date?`${row.date} · `:''}${sourceStatus(row,scene)}. Witness the event first; comparison comes after the project-side material.`
  };
}

function renderWitness(row){
  const w=witnessFor(row);
  const projectBody=[
    p(w.project),
    w.chronology?p(w.chronology,'witness-chronology'):'',
    quoteHtml(w.quotes)
  ].join('');
  const bibleBody=[
    p(w.bible),
    w.refs?p(`Scripture scope: ${w.refs}`,'witness-refs'):''
  ].join('');
  const discoveryBody=[w.rhyme,w.discoveryBody].filter(Boolean).map(text=>p(text)).join('');
  const pressureBody=p(
    w.pressure ||
    'No substantial mismatch or counter-text has yet been recorded for this relation. Keep the comparison provisional where evidence is thin.'
  );

  return `<section class="witness-dossier" data-witness-for="${esc(row.id)}">
    <header class="witness-opening">
      <div class="witness-kicker">Witness dossier</div>
      <h2>${esc(row.title||row.project_anchor||row.id)}</h2>
      <p>${esc(w.opening)}</p>
    </header>
    ${chapter('01','What happened',projectBody,'witness-project')}
    ${chapter('02','What the biblical text does',bibleBody,'witness-bible')}
    ${chapter('03','What becomes visible when they are read together',
      discoveryBody||p('The archive has not yet written a fuller sequence argument for this relation.'),
      'witness-discovery')}
    ${chapter('04','Where the reading is tested',pressureBody,'witness-counterpressure')}
  </section>`;
}

function decorate(){
  const article=document.querySelector('#active-relation .relation[data-relation-id]');
  if(!article) return;
  const id=article.dataset.relationId;
  const row=rows.get(id);
  if(!row) return;

  const old=article.querySelector(':scope > .witness-dossier');
  if(old && old.dataset.witnessFor===id) return;
  if(old) old.remove();

  const shell=document.createElement('div');
  shell.innerHTML=renderWitness(row);
  const witness=shell.firstElementChild;
  if(!witness) return;

  const parallel=article.querySelector('.parallel');
  (parallel||article.firstElementChild)?.before(witness);

  // Existing comparison blocks remain available as secondary/raw evidence,
  // but the witness narrative becomes the primary reading surface.
  article.querySelectorAll('.paired-narrative').forEach(node=>node.classList.add('witness-legacy-secondary'));
  const why=article.querySelector('.why');
  if(why) why.classList.add('witness-legacy-secondary');
  const boundary=article.querySelector('.boundary-callout');
  if(boundary) boundary.classList.add('witness-legacy-secondary');
}

window.fetch=async function(input,init){
  const response=await upstreamFetch(input,init);
  const url=typeof input==='string'?input:input?.url||'';
  if(url.endsWith(FIELD_SUFFIX) && response.ok){
    try{
      const data=await response.clone().json();
      rows=new Map(arr(data.relations).map(row=>[row.id,row]));
      queueMicrotask(decorate);
    }catch(error){
      console.warn('Bible witness relation cache unavailable',error);
    }
  }
  return response;
};

const observer=new MutationObserver(()=>decorate());
function start(){
  const active=document.getElementById('active-relation');
  if(!active) return;
  observer.observe(active,{childList:true,subtree:true});
  decorate();
}
document.readyState==='loading'
  ?document.addEventListener('DOMContentLoaded',start)
  :start();
})();
