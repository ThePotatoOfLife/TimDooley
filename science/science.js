(()=>{
  'use strict';
  const B='../knowledge/science/';
  const $=id=>document.getElementById(id);
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const get=async url=>{const r=await fetch(url,{cache:'no-cache'});if(!r.ok)throw Error(`${url}: ${r.status}`);return r.json()};

  function provenanceClass(value){
    const x=String(value).toLowerCase();
    if(x.includes('established')||x.includes('external')) return 'external / comparator';
    if(x.includes('primary')||x.includes('recovered')||x.includes('great book')||x.includes('upt')) return 'recovered / project';
    if(x.includes('archive')||x.includes('formalization')) return 'archive formalization';
    return 'project formalism';
  }

  function renderMaster(m){
    $('metric-domains').textContent=m.domains?.length??'—';
    $('metric-equations').textContent=m.root_formalisms?.length??'—';
    $('metric-provenance').textContent=m.epistemic_classes?.length??'—';

    const timeline=m.developmental_genealogy||[];
    $('science-timeline').innerHTML=timeline.map((x,i)=>{
      const concepts=Array.isArray(x.concepts)?x.concepts:[];
      return `<article class="timeline-item">
        <div class="period">${esc(x.period||x.date||`Stage ${i+1}`)}</div>
        <h3>${esc(concepts.slice(0,3).join(' · ')||'Recovered science stratum')}</h3>
        <div class="topic-pills">${concepts.slice(3,11).map(y=>`<span>${esc(y)}</span>`).join('')}</div>
        ${x.status?`<p class="microcopy">${esc(x.status)}</p>`:''}
      </article>`;
    }).join('');

    const equations=m.root_formalisms||[];
    const list=$('equation-list');
    const initial=18;
    list.innerHTML=equations.map((x,i)=>`<div class="equation-row ${i>=initial?'extra':''}">
      <span class="eq-no">${String(i+1).padStart(2,'0')}</span>
      <code>${esc(x)}</code>
      <span class="eq-class">${esc(provenanceClass(x))}</span>
    </div>`).join('');
    const toggle=$('equation-toggle');
    if(equations.length>initial){
      toggle.hidden=false;
      toggle.textContent=`Show all ${equations.length} equations`;
      toggle.onclick=()=>{
        const expanded=list.classList.toggle('expanded');
        toggle.textContent=expanded?'Show fewer equations':`Show all ${equations.length} equations`;
      };
    }

    const domains=m.domains||[];
    const input=$('domain-search'), grid=$('domain-grid'), empty=$('domain-empty');
    const draw=()=>{
      const q=input.value.trim().toLowerCase();
      const matched=domains.filter(x=>`${x.id||''} ${x.title||''} ${(x.topics||[]).join(' ')}`.toLowerCase().includes(q));
      grid.innerHTML=matched.map(x=>`<article class="domain-card">
        <span class="domain-id">${esc(x.id||'domain')}</span><h3>${esc(x.title||x.id)}</h3>
        <div class="topics">${(x.topics||[]).slice(0,16).map(y=>`<span>${esc(y)}</span>`).join('')}</div>
      </article>`).join('');
      empty.hidden=!!matched.length;
    };
    input.addEventListener('input',draw); draw();

    $('open-questions-grid').innerHTML=(m.unresolved_primary_targets||[]).map((x,i)=>`<article class="question-card"><span class="q-no">Target ${String(i+1).padStart(2,'0')}</span>${esc(x)}</article>`).join('');
  }

  function renderUpt(u){
    const target=$('upt-terms');
    const terms=u.term_map||[];
    target.innerHTML=terms.length?terms.map(x=>`<div class="term-item"><code>${esc(x.term)}</code><span>${esc(x.intended_role)}</span></div>`).join(''):'<p class="microcopy">Term map is in the recovery record.</p>';
  }

  function renderSpiral(s){
    const p=s.exact_properties||{};
    const properties=[
      ['Quarter turn',p.quarter_turn_scaling,'Golden-ratio radial scaling after 90°.'],
      ['Half turn',p.half_turn_scaling,'Two quarter-turn scalings combine to φ².'],
      ['Full turn',p.full_turn_scaling,'One full revolution gives φ⁴ radial scaling.'],
      ['Differential form',p.differential_form,'Local radial growth law.'],
      ['Curvature',p.curvature,'Curvature falls inversely with radius.'],
      ['Self-similarity',p.self_similarity,'Rotation plus scaling reproduces the same curve.']
    ].filter(x=>x[1]);
    if(properties.length)$('spiral-properties').innerHTML=properties.map(([label,value,note])=>`<article><span>${esc(label)}</span><strong>${esc(value)}</strong><p>${esc(note)}</p></article>`).join('');
  }

  function renderToe(t){
    const strata=t.unification_strata||t.developmental_strata||[];
    $('toe-strata').innerHTML=strata.length?strata.map(x=>`<div class="compact-item"><strong>${esc(x.name||x.title||x.period||x.date||'Unification stratum')}</strong><span>${esc(x.date||x.period||x.classification||x.status||'')}</span></div>`).join(''):'<p class="microcopy">See the TOE archaeology record for the full long-arc programme.</p>';
    const req=t.physical_toe_requirements||t.requirements||[];
    $('toe-requirements').innerHTML=req.length?req.map(x=>`<li>${esc(typeof x==='string'?x:(x.requirement||x.name||JSON.stringify(x)))}</li>`).join(''):'<li>Recover known physical limits, define observables, and produce testable predictions.</li>';
  }

  function wireCatalog(){
    const input=$('catalog-search'), cards=[...document.querySelectorAll('.catalog-card')], count=$('catalog-count'), empty=$('catalog-empty');
    if(!input||!cards.length) return;
    const draw=()=>{
      const q=input.value.trim().toLowerCase(); let shown=0;
      cards.forEach(card=>{const match=!q||(card.dataset.search||card.textContent.toLowerCase()).includes(q);card.hidden=!match;if(match)shown++;});
      count.textContent=q?`${shown} of ${cards.length} records`:`${cards.length} records`;
      empty.hidden=shown!==0;
    };
    input.addEventListener('input',draw); draw();
  }

  async function init(){
    const jobs={
      master:get(B+'science-master-index.json'),
      upt:get(B+'unified-potato-theory-2025-recovery.json'),
      spiral:get(B+'april-21-2025-potato-axis-spiral-primary-recovery.json'),
      toe:get(B+'theory-of-everything-archaeology.json'),
      catalog:get('./catalog.json')
    };
    const entries=Object.entries(jobs), results=await Promise.allSettled(entries.map(([,p])=>p));
    const data={}; let failed=0;
    results.forEach((result,i)=>{if(result.status==='fulfilled')data[entries[i][0]]=result.value;else failed++;});
    if(data.master)renderMaster(data.master);
    if(data.upt)renderUpt(data.upt);
    if(data.spiral)renderSpiral(data.spiral);
    if(data.toe)renderToe(data.toe);
    if(data.catalog?.count!=null)$('metric-records').textContent=data.catalog.count;
    wireCatalog();
    const state=$('data-state');
    state.textContent=failed?`Atlas loaded; ${failed} auxiliary data source${failed===1?' is':'s are'} unavailable.`:`Canonical science data loaded · ${data.catalog?.count??'all'} compiled records · master index ${data.master?.updated||'current'}`;
    state.className='data-state '+(failed?'error':'ok');
  }

  document.addEventListener('DOMContentLoaded',init);
})();
