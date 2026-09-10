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

  const maturityGates={
    T0:['T1','Define the state space, variables, scope and explicit rules.'],
    T1:['T2','Write the minimal equations, dimensions, boundaries and translation maps.'],
    T2:['T3','Choose a parameter set and calibrate or constrain it against real data.'],
    T3:['T4','Predeclare a quantitative prediction that differs from the baseline.'],
    T4:['T5','Obtain independent replication across data, implementation or experiment.'],
    T5:['T5','Map limits, replications and failure domains; do not inflate the claim.']
  };

  let registryModels=[];
  let programmeStageByModel=new Map();
  let modelButtons=[];
  let recordCards=[];
  let activeModelId='';

  function list(items,limit=8){
    if(!Array.isArray(items)||!items.length)return '<span class="none-note">Not yet specified</span>';
    const shown=items.slice(0,limit);
    return `<ul>${shown.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>${items.length>limit?`<small class="list-more">+${items.length-limit} more in the canonical record</small>`:''}`;
  }

  function evidenceFamily(classification){
    const x=String(classification||'').toLowerCase();
    if(x.includes('external')||x.includes('established'))return 'external science';
    if(x.includes('primary')||x.includes('recovered')||x.includes('book-derived')||x.includes('archaeology'))return 'recovered / provenance-led';
    if(x.includes('speculative'))return 'speculative programme';
    return 'project model';
  }

  function completionInfo(model){
    const c=model.completion||{};
    const filled=Number(c.filled_contract_fields||0);
    const total=Math.max(Number(c.total_contract_fields||12),1);
    const pct=Math.max(0,Math.min(100,Math.round((filled/total)*100)));
    return {filled,total,pct,next:c.next_action||'Complete the missing model contract fields.'};
  }

  function searchText(model){
    return [
      model.title,model.short_title,model.classification,model.abstract,model.maturity,
      ...(model.formal_core||[]),...(model.state_variables||[]),...(model.assumptions||[]),
      ...(model.observables||[]),...(model.falsifiers||[]),...(model.baseline||[]),
      model.calibration_path,...(model.couples_to||[]),...(model.unresolved||[]),...(model.source_records||[])
    ].join(' ').toLowerCase();
  }

  function renderDossier(model){
    const dossier=$('model-dossier');
    if(!model){
      dossier.innerHTML='<div class="dossier-empty"><strong>No matching flagship model.</strong><p>Try a broader search, or inspect the source records below.</p></div>';
      return;
    }

    const c=completionInfo(model);
    const stage=programmeStageByModel.get(model.id)||'Unassigned programme layer';
    const [nextMaturity,gate]=maturityGates[model.maturity]||['Next','Define the next measurable theory-quality requirement.'];
    const equations=(model.formal_core||[]).map(eq=>`<code>${esc(eq)}</code>`).join('')||'<span class="none-note">Formal core not yet specified.</span>';
    const couplings=(model.couples_to||[]).map(id=>{
      const target=registryModels.find(item=>item.id===id);
      return `<button type="button" data-open-model="${esc(id)}">${esc(target?.short_title||target?.title||id.replaceAll('-',' '))}</button>`;
    }).join('')||'<span class="none-note">No explicit model coupling declared.</span>';
    const sources=(model.source_records||[]).map(file=>`<a href="${B}${encodeURIComponent(file)}">${esc(file.replace('.json',''))}</a>`).join('')||'<span class="none-note">No source record declared.</span>';

    dossier.innerHTML=`
      <header class="dossier-head">
        <div class="dossier-meta"><span>${esc(stage)}</span><span>${esc(evidenceFamily(model.classification))}</span></div>
        <h3>${esc(model.title)}</h3>
        <p>${esc(model.abstract||'No abstract yet.')}</p>
        <div class="dossier-stats">
          <span><b>${esc(model.maturity||'T1')}</b><small>maturity</small></span>
          <span><b>${c.filled}/${c.total}</b><small>contract fields</small></span>
          <span><b>${c.pct}%</b><small>contract coverage</small></span>
          <span><b>${(model.couples_to||[]).length}</b><small>declared couplings</small></span>
        </div>
      </header>

      <section class="maturity-gate">
        <div><span>Current completion target</span><strong>${esc(c.next)}</strong></div>
        <div><span>${esc(model.maturity||'T1')} → ${esc(nextMaturity)} gate</span><p>${esc(gate)}</p></div>
      </section>

      <section class="dossier-core">
        <div class="formal-core"><h4>Formal core</h4>${equations}</div>
        <div class="test-core">
          <div><h4>Observable handles</h4>${list(model.observables,4)}</div>
          <div><h4>Failure conditions</h4>${list(model.falsifiers,4)}</div>
        </div>
      </section>

      <div class="dossier-links">
        <div><strong>Declared couplings</strong><div class="chip-row">${couplings}</div></div>
        <div><strong>Source lineage</strong><div class="chip-row">${sources}</div></div>
      </div>

      <details class="full-contract">
        <summary>Full scientific contract</summary>
        <div class="contract-grid">
          <section><h4>State variables</h4>${list(model.state_variables)}</section>
          <section><h4>Assumptions</h4>${list(model.assumptions)}</section>
          <section><h4>Observables</h4>${list(model.observables)}</section>
          <section><h4>Failure conditions</h4>${list(model.falsifiers)}</section>
          <section><h4>Comparison baseline</h4>${list(model.baseline)}</section>
          <section><h4>Unresolved work</h4>${list(model.unresolved)}</section>
        </div>
        <div class="calibration"><strong>Calibration path</strong><p>${esc(model.calibration_path||'Not yet specified.')}</p></div>
        <p class="classification-line"><strong>Registry classification:</strong> ${esc(model.classification||'project model')}</p>
      </details>`;

    dossier.querySelectorAll('[data-open-model]').forEach(button=>button.addEventListener('click',()=>activateModel(button.dataset.openModel,true)));
  }

  function activateModel(id,scroll=false){
    const model=registryModels.find(item=>item.id===id);
    if(!model)return;
    activeModelId=id;
    modelButtons.forEach(button=>{
      const active=button.dataset.modelId===id;
      button.classList.toggle('active',active);
      button.setAttribute('aria-pressed',active?'true':'false');
    });
    renderDossier(model);
    if(scroll)$('models')?.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function renderWorkQueue(models){
    const queue=$('model-work-queue');
    if(!queue)return;
    queue.innerHTML=models.map((model,index)=>{
      const c=completionInfo(model);
      const stage=programmeStageByModel.get(model.id)||'Programme';
      const [,gate]=maturityGates[model.maturity]||['','Define the next measurable requirement.'];
      return `<button class="work-item" type="button" data-work-model="${esc(model.id)}">
        <span class="work-no">${String(index+1).padStart(2,'0')}</span>
        <span class="work-copy"><b>${esc(model.short_title||model.title)}</b><small>${esc(stage)} · ${esc(model.maturity||'T1')} · contract ${c.filled}/${c.total}</small><em>${esc(c.next)}</em></span>
        <span class="work-gate">${esc(gate)}</span>
      </button>`;
    }).join('');
    queue.querySelectorAll('[data-work-model]').forEach(button=>button.addEventListener('click',()=>activateModel(button.dataset.workModel,true)));
  }

  function renderModels(registry){
    registryModels=registry.models||[];
    programmeStageByModel=new Map();
    (registry.programme_spine||[]).forEach(stage=>(stage.models||[]).forEach(id=>programmeStageByModel.set(id,stage.stage)));
    $('metric-models').textContent=registryModels.length;

    const index=$('model-index');
    index.innerHTML=registryModels.map(model=>{
      const c=completionInfo(model);
      const stage=programmeStageByModel.get(model.id)||'Programme';
      return `<button class="model-index-item" type="button" data-model-id="${esc(model.id)}" data-search="${esc(searchText(model))}" aria-pressed="false">
        <span class="model-index-top"><b>${esc(model.short_title||model.title)}</b><em>${esc(model.maturity||'T1')}</em></span>
        <span class="model-index-title">${esc(model.title)}</span>
        <small>${esc(stage)} · ${c.filled}/${c.total} contract</small>
      </button>`;
    }).join('');
    modelButtons=[...index.querySelectorAll('.model-index-item')];
    modelButtons.forEach(button=>button.addEventListener('click',()=>activateModel(button.dataset.modelId)));
    renderWorkQueue(registryModels);
    if(registryModels.length)activateModel(registryModels[0].id);
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
    let firstVisibleModel='';

    modelButtons.forEach(button=>{
      const show=matches(button.dataset.search||button.textContent,q);
      button.hidden=!show;
      if(show){modelsShown++;if(!firstVisibleModel)firstVisibleModel=button.dataset.modelId||'';}
    });
    recordCards.forEach(card=>{
      const show=matches(card.dataset.search||card.textContent,q);
      card.hidden=!show;
      if(show)recordsShown++;
    });

    const activeVisible=modelButtons.some(button=>button.dataset.modelId===activeModelId&&!button.hidden);
    if(!activeVisible){
      if(firstVisibleModel)activateModel(firstVisibleModel);
      else renderDossier(null);
    }

    $('model-empty').hidden=modelsShown!==0;
    $('catalog-empty').hidden=recordsShown!==0;
    $('model-index-count').textContent=q?`${modelsShown} of ${modelButtons.length}`:`${modelButtons.length} models`;
    $('catalog-count').textContent=q?`${recordsShown} of ${recordCards.length} records`:`${recordCards.length} records`;
    $('search-note').textContent=q?`${modelsShown} flagship model${modelsShown===1?'':'s'} · ${recordsShown} source record${recordsShown===1?'':'s'} match “${q}”.`:'One search filters the model index and the complete record library.';
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
    if(registryResult.status==='fulfilled'){
      renderProgramme(registryResult.value);
      renderModels(registryResult.value);
    }else{
      failures++;
      $('model-index').innerHTML='<div class="loading-card">Model registry unavailable; source records remain usable.</div>';
      $('model-dossier').innerHTML='<div class="dossier-empty"><strong>Model registry unavailable.</strong><p>The canonical source records remain below.</p></div>';
      $('model-work-queue').innerHTML='<div class="loading-card">Model completion queue unavailable.</div>';
    }
    if(catalogResult.status==='fulfilled')$('metric-records').textContent=catalogResult.value.count??document.querySelectorAll('.catalog-card').length;
    else{failures++;$('metric-records').textContent=document.querySelectorAll('.catalog-card').length||'—';}

    wireSearch();
    const state=$('data-state');
    state.textContent=failures?`Atlas loaded with ${failures} auxiliary source${failures===1?'':'s'} unavailable.`:'Model registry, equation index and compiled record catalog loaded.';
    state.className='data-state '+(failures?'error':'ok');
  }

  document.addEventListener('DOMContentLoaded',init);
})();
