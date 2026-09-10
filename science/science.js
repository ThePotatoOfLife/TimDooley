(()=>{
  'use strict';
  const B='../knowledge/science/';
  const $=id=>document.getElementById(id);
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const get=async url=>{const r=await fetch(url,{cache:'no-cache'});if(!r.ok)throw Error(`${url}: ${r.status}`);return r.json();};
  const tokens=q=>String(q||'').toLowerCase().trim().split(/\s+/).filter(Boolean);
  const matches=(text,q)=>{const t=String(text||'').toLowerCase();return tokens(q).every(token=>t.includes(token));};

  const domainPresets=[
    ['All',''],['Dynamics','dynamics'],['Quantum','quantum'],['Fields & Higgs','higgs field'],['Dimensions','dimension'],
    ['Unification','unification'],['Information','information'],['Biology & brain','microtubule'],['Astronomy','astronomy'],
    ['Time & waves','advanced retarded'],['Testing','testing']
  ];

  let modelCards=[];
  let recordCards=[];

  function list(items,limit=6){
    if(!Array.isArray(items)||!items.length)return '<span class="none-note">Not yet specified</span>';
    return `<ul>${items.slice(0,limit).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
  }

  function evidenceFamily(classification){
    const x=String(classification||'').toLowerCase();
    if(x.includes('external')||x.includes('established'))return 'external';
    if(x.includes('primary')||x.includes('recovered')||x.includes('book-derived')||x.includes('archaeology'))return 'recovered';
    if(x.includes('speculative'))return 'speculative';
    return 'project';
  }

  function renderModels(registry){
    const grid=$('model-grid');
    const models=registry.models||[];
    $('metric-models').textContent=models.length;
    grid.innerHTML=models.map(model=>{
      const c=model.completion||{};
      const filled=Number(c.filled_contract_fields||0),total=Number(c.total_contract_fields||12);
      const pct=Math.max(0,Math.min(100,Math.round((filled/Math.max(total,1))*100)));
      const eqs=(model.formal_core||[]).slice(0,3).map(eq=>`<code>${esc(eq)}</code>`).join('');
      const search=[model.title,model.short_title,model.classification,model.abstract,model.maturity,(model.formal_core||[]).join(' '),(model.state_variables||[]).join(' '),(model.couples_to||[]).join(' '),(model.unresolved||[]).join(' ')].join(' ').toLowerCase();
      return `<article class="model-card" data-model-id="${esc(model.id)}" data-search="${esc(search)}" data-evidence="${evidenceFamily(model.classification)}">
        <div class="model-meta"><span>${esc(model.maturity||'T1')}</span><span>${esc(model.classification||'project model')}</span></div>
        <h3>${esc(model.title)}</h3>
        <p class="model-abstract">${esc(model.abstract||'')}</p>
        <div class="completion-row"><span>Contract ${filled}/${total}</span><div class="completion-track"><i style="width:${pct}%"></i></div><b>${pct}%</b></div>
        <p class="next-action"><strong>Next:</strong> ${esc(c.next_action||'Complete the missing model contract fields.')}</p>
        <div class="model-equations">${eqs}</div>
        <details class="model-details"><summary>Open model contract</summary>
          <div class="contract-grid">
            <section><h4>State variables</h4>${list(model.state_variables)}</section>
            <section><h4>Assumptions</h4>${list(model.assumptions)}</section>
            <section><h4>Observables</h4>${list(model.observables)}</section>
            <section><h4>Failure conditions</h4>${list(model.falsifiers)}</section>
            <section><h4>Baseline</h4>${list(model.baseline)}</section>
            <section><h4>Unresolved</h4>${list(model.unresolved)}</section>
          </div>
          <div class="calibration"><strong>Calibration path</strong><p>${esc(model.calibration_path||'Not yet specified.')}</p></div>
          <div class="coupling-row"><strong>Couples to</strong>${(model.couples_to||[]).map(id=>`<button type="button" data-model-filter="${esc(id)}">${esc(id.replaceAll('-',' '))}</button>`).join('')}</div>
          <div class="source-row"><strong>Source records</strong>${(model.source_records||[]).map(file=>`<a href="${B}${encodeURIComponent(file)}">${esc(file.replace('.json',''))}</a>`).join('')}</div>
        </details>
      </article>`;
    }).join('');
    modelCards=[...grid.querySelectorAll('.model-card')];
    grid.querySelectorAll('[data-model-filter]').forEach(button=>button.addEventListener('click',()=>{
      const id=button.dataset.modelFilter||'';
      const target=models.find(m=>m.id===id);
      setSearch(target?.short_title||target?.title||id.replaceAll('-',' '));
    }));
  }

  function renderProgramme(registry){
    const flow=$('programme-flow');
    const spine=registry.programme_spine||[];
    if(!flow||!spine.length)return;
    flow.innerHTML=spine.map((stage,i)=>`${i?'<b>→</b>':''}<article><span>${i+1}</span><strong>${esc(stage.stage)}</strong><p>${esc(stage.role)}</p><small>${(stage.models||[]).length} model${(stage.models||[]).length===1?'':'s'}</small></article>`).join('');
  }

  function renderMaster(master){
    const equations=master.root_formalisms||[];
    $('metric-equations').textContent=equations.length;
    $('metric-open').textContent=(master.unresolved_primary_targets||[]).length;
    const listEl=$('equation-list'),initial=10;
    listEl.innerHTML=equations.map((eq,i)=>`<div class="equation-row ${i>=initial?'extra':''}"><span class="eq-no">${String(i+1).padStart(2,'0')}</span><code>${esc(eq)}</code></div>`).join('');
    const toggle=$('equation-toggle');
    if(equations.length>initial){
      toggle.hidden=false;
      toggle.textContent=`Show all ${equations.length} equations`;
      toggle.onclick=()=>{const open=listEl.classList.toggle('expanded');toggle.textContent=open?'Show fewer equations':`Show all ${equations.length} equations`;};
    }
    const timeline=master.developmental_genealogy||[];
    $('science-timeline').innerHTML=timeline.map((entry,i)=>{
      const concepts=entry.concepts||[];
      return `<article class="timeline-item"><div class="period">${esc(entry.period||`Stage ${i+1}`)}</div><h3>${esc(concepts.slice(0,3).join(' · ')||'Science stratum')}</h3><p>${esc(concepts.slice(3,8).join(' · '))}</p>${entry.status?`<small>${esc(entry.status)}</small>`:''}</article>`;
    }).join('');
    $('open-questions-grid').innerHTML=(master.unresolved_primary_targets||[]).map((item,i)=>`<article class="question-card"><span>${String(i+1).padStart(2,'0')}</span><p>${esc(item)}</p></article>`).join('');
  }

  function renderDomainFilters(){
    const wrap=$('domain-filters');
    wrap.innerHTML=domainPresets.map(([label,q],i)=>`<button type="button" data-domain-query="${esc(q)}" class="${i===0?'active':''}">${esc(label)}</button>`).join('');
    wrap.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{
      wrap.querySelectorAll('button').forEach(x=>x.classList.remove('active'));
      button.classList.add('active');
      setSearch(button.dataset.domainQuery||'');
    }));
  }

  function applySearch(){
    const input=$('catalog-search');
    const q=input?.value||'';
    let modelsShown=0,recordsShown=0;
    modelCards.forEach(card=>{const show=matches(card.dataset.search||card.textContent,q);card.hidden=!show;if(show)modelsShown++;});
    recordCards.forEach(card=>{const show=matches(card.dataset.search||card.textContent,q);card.hidden=!show;if(show)recordsShown++;});
    $('model-empty').hidden=modelsShown!==0;
    $('catalog-empty').hidden=recordsShown!==0;
    $('catalog-count').textContent=q?`${recordsShown} of ${recordCards.length} records`:`${recordCards.length} records`;
    $('search-note').textContent=q?`${modelsShown} flagship model${modelsShown===1?'':'s'} · ${recordsShown} source record${recordsShown===1?'':'s'} match “${q}”.`:'One search filters both flagship models and the complete record library.';
    $('clear-search').hidden=!q;
  }

  function setSearch(value){
    const input=$('catalog-search');
    input.value=value||'';
    document.querySelectorAll('#domain-filters button').forEach(button=>button.classList.toggle('active',(button.dataset.domainQuery||'')===(value||'')));
    applySearch();
    if(value)$('models')?.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function wireSearch(){
    recordCards=[...document.querySelectorAll('.catalog-card')];
    const input=$('catalog-search');
    input.addEventListener('input',()=>{document.querySelectorAll('#domain-filters button').forEach(x=>x.classList.remove('active'));applySearch();});
    $('clear-search').addEventListener('click',()=>setSearch(''));
    applySearch();
  }

  async function init(){
    renderDomainFilters();
    const jobs=[get(B+'science-master-index.json'),get(B+'science-model-registry.json'),get('./catalog.json')];
    const [masterResult,registryResult,catalogResult]=await Promise.allSettled(jobs);
    let failures=0;
    if(masterResult.status==='fulfilled')renderMaster(masterResult.value);else failures++;
    if(registryResult.status==='fulfilled'){renderModels(registryResult.value);renderProgramme(registryResult.value);}else{failures++;$('model-grid').innerHTML='<div class="loading-card">Model registry unavailable; source catalog remains usable.</div>';}
    if(catalogResult.status==='fulfilled')$('metric-records').textContent=catalogResult.value.count??document.querySelectorAll('.catalog-card').length;else{failures++;$('metric-records').textContent=document.querySelectorAll('.catalog-card').length||'—';}
    wireSearch();
    const state=$('data-state');
    state.textContent=failures?`Atlas loaded with ${failures} auxiliary source${failures===1?'':'s'} unavailable.`:'Model registry, equation index and compiled record catalog loaded.';
    state.className='data-state '+(failures?'error':'ok');
  }

  document.addEventListener('DOMContentLoaded',init);
})();
