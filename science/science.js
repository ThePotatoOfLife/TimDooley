(()=>{
  'use strict';

  const SOURCE='../knowledge/science/';
  const $=id=>document.getElementById(id);
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const get=async url=>{const response=await fetch(url,{cache:'no-cache'});if(!response.ok)throw new Error(`${url}: ${response.status}`);return response.json();};
  const words=query=>String(query||'').toLowerCase().trim().split(/\s+/).filter(Boolean);
  const matches=(text,query)=>words(query).every(word=>String(text||'').toLowerCase().includes(word));

  const presets=[['All',''],['Dynamics','dynamics'],['Quantum','quantum'],['Fields','field higgs'],['Dimensions','dimension'],['Unification','unification'],['Information','information'],['Biology','microtubule'],['Astronomy','astronomy'],['Testing','testing']];

  const maturityGate={
    T0:'Define variables, state space and scope.',
    T1:'Write a minimal mathematical model with dimensions and boundaries.',
    T2:'Calibrate or constrain parameters against real data.',
    T3:'Predeclare a quantitative prediction that differs from the baseline.',
    T4:'Seek independent replication or an independent implementation.',
    T5:'Map limits and failure domains rather than broadening the claim.'
  };

  const conclusions={
    'unified-potato-theory':'UPT is presently best treated as a recoverable effective-field-theory programme, not as a finished unification. Its useful scientific core is the proposed extra sector and its interactions; the decisive move is to choose one gauge-consistent field representation and derive its low-energy consequences.',
    'potato-axis-spiral':'The spiral result itself is mathematically finished: it is a logarithmic spiral with exact golden-ratio scaling every quarter turn. What is not finished is any physical or biological interpretation; each application must define what r and θ measure and then survive comparison with alternative curve families.',
    'potato-dynamics':'Potato Dynamics is currently the most coherent general mathematical framework in the programme. It works best as a typed hybrid/compositional systems language. Its scientific value now depends on benchmark instantiations that outperform or clarify simpler state-space models.',
    'door-handshake':'The Door formulation is scientifically strongest as a two-boundary inference or control model. A literal advanced-wave interpretation is not required by the mathematics and should remain separate unless a physical field model produces a distinct observable.',
    'dimensional-phase-transition':'The dimensional-transition branch has enough structure to become a real toy theory, but it must stop branching into multiple ansätze. One stable action, one transition law and one derived strong-gravity observable would make it substantially more scientific.',
    'eleven-dimensional-projection':'The 11D work is strongest as a projection/coarse-graining grammar. A literal M-theory claim requires a concrete compactification and a recovered four-dimensional spectrum; without that, the formal projection interpretation should remain the default.',
    'spudlight-signal-information':'Spudlight becomes technically useful when photon flux, information gain, attention and social coherence remain separate measured channels. Its strongest result is therefore architectural: it prevents unlike quantities from being collapsed into one number while still allowing explicit causal links between channels.',
    'microtubule-cross-scale':'The defensible route is classical first: fit microtubule dynamics, define a micro-to-neural coarse-graining map, then ask whether an open-quantum extension adds predictive power. Consciousness-level claims cannot substitute for that missing bridge.',
    'higgs-potato-sector':'The Higgs/Potato branch can be made concrete with a minimal scalar portal or a clearly specified gauged U(1) sector. The next scientific result should be a mass/mixing spectrum plus existing experimental bounds, not another symbolic interaction term.',
    'gauge-unification-susy':'SU(4), SU(5), Spin(10) and SUSY are useful constraints and comparison frameworks, not evidence of a Tim-original grand-unified theory. The productive next step is one explicit embedding with representation content, symmetry breaking and numerical coupling running.',
    'timic-unification-program':'The Timic Unification Program is most defensible as a meta-model for composing typed models across domains. Its success criterion is not “everything is one physics”; it is whether explicit interfaces improve reuse, error detection and prediction while preserving domain differences.'
  };

  let models=[];
  let stages=new Map();
  let modelButtons=[];
  let recordCards=[];
  let activeId='';

  function list(items,limit=7){
    if(!Array.isArray(items)||!items.length)return '<p class="empty">Not yet specified.</p>';
    const shown=items.slice(0,limit);
    return `<ul>${shown.map(item=>`<li>${esc(item)}</li>`).join('')}</ul>${items.length>limit?`<p class="empty">+${items.length-limit} more in the source contract.</p>`:''}`;
  }

  function evidenceLabel(classification){
    const text=String(classification||'').toLowerCase();
    if(text.includes('external')||text.includes('established'))return 'external science / comparator';
    if(text.includes('primary')||text.includes('recovered')||text.includes('book-derived')||text.includes('archaeology'))return 'recovered / provenance-led';
    if(text.includes('speculative'))return 'speculative model';
    return 'project model';
  }

  function completion(model){
    const item=model.completion||{};
    const filled=Number(item.filled_contract_fields||0);
    const total=Math.max(Number(item.total_contract_fields||12),1);
    return {filled,total,next:item.next_action||'Complete the missing scientific contract fields.'};
  }

  function searchBlob(model){
    return [model.title,model.short_title,model.classification,model.abstract,conclusions[model.id],...(model.formal_core||[]),...(model.state_variables||[]),...(model.assumptions||[]),...(model.observables||[]),...(model.falsifiers||[]),...(model.baseline||[]),model.calibration_path,...(model.couples_to||[]),...(model.unresolved||[])].join(' ').toLowerCase();
  }

  function renderModel(model){
    const view=$('model-view');
    if(!model){view.innerHTML='<div class="loading">No developed model matches this search.</div>';return;}
    const done=completion(model);
    const stage=stages.get(model.id)||'Science programme';
    const equations=(model.formal_core||[]).map(item=>`<code>${esc(item)}</code>`).join('')||'<p class="empty">No formal core specified yet.</p>';
    const couplingButtons=(model.couples_to||[]).map(id=>{
      const target=models.find(item=>item.id===id);
      return `<button type="button" data-open-model="${esc(id)}">${esc(target?.short_title||target?.title||id)}</button>`;
    }).join('');
    const sourceNames=(model.source_records||[]).join(' · ');

    view.innerHTML=`
      <header class="model-header">
        <div class="model-meta"><span>${esc(stage)}</span><span>${esc(evidenceLabel(model.classification))}</span></div>
        <h3>${esc(model.title)}</h3>
        <p class="model-abstract">${esc(model.abstract||'No abstract specified.')}</p>
        <div class="model-status">
          <div><span>Maturity</span><strong>${esc(model.maturity||'T1')}</strong></div>
          <div><span>Contract</span><strong>${done.filled}/${done.total} fields</strong></div>
          <div><span>Couplings</span><strong>${(model.couples_to||[]).length} explicit</strong></div>
        </div>
      </header>
      <div class="conclusion"><span>Current conclusion</span><p>${esc(conclusions[model.id]||model.abstract||'No current conclusion written yet.')}</p></div>
      <div class="model-core">
        <section class="formal-core"><span class="block-title">Formal core</span>${equations}</section>
        <aside class="next-step"><span class="block-title">Next derivation</span><strong>${esc(done.next)}</strong><p><b>${esc(model.maturity||'T1')} maturity gate:</b> ${esc(maturityGate[model.maturity]||'Define the next measurable requirement.')}</p></aside>
      </div>
      <div class="model-tests">
        <section><span class="block-title">Observable handles</span>${list(model.observables,5)}</section>
        <section><span class="block-title">What would count against it</span>${list(model.falsifiers,5)}</section>
      </div>
      <details class="model-details">
        <summary>Assumptions, variables, baselines and unresolved work</summary>
        <div class="details-grid">
          <section><span class="block-title">State variables</span>${list(model.state_variables)}</section>
          <section><span class="block-title">Assumptions</span>${list(model.assumptions)}</section>
          <section><span class="block-title">Comparison baseline</span>${list(model.baseline)}</section>
          <section><span class="block-title">Unresolved work</span>${list(model.unresolved)}</section>
          <section class="calibration"><span class="block-title">Calibration path</span><p>${esc(model.calibration_path||'Not yet specified.')}</p></section>
        </div>
        ${couplingButtons?`<div class="couplings"><span class="block-title">Open connected model</span>${couplingButtons}</div>`:''}
        ${sourceNames?`<p class="model-source"><b>Source lineage:</b> ${esc(sourceNames)}</p>`:''}
      </details>`;

    view.querySelectorAll('[data-open-model]').forEach(button=>button.addEventListener('click',()=>activateModel(button.dataset.openModel,true)));
  }

  function activateModel(id,scroll=false){
    const model=models.find(item=>item.id===id);
    if(!model)return;
    activeId=id;
    modelButtons.forEach(button=>{
      const active=button.dataset.modelId===id;
      button.classList.toggle('active',active);
      button.setAttribute('aria-pressed',active?'true':'false');
    });
    renderModel(model);
    if(scroll)$('models')?.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function renderModels(registry){
    models=registry.models||[];
    stages=new Map();
    (registry.programme_spine||[]).forEach(stage=>(stage.models||[]).forEach(id=>stages.set(id,stage.stage)));
    $('metric-models').textContent=models.length;
    const listEl=$('model-list');
    listEl.innerHTML=models.map(model=>{
      const done=completion(model);
      return `<button class="model-button" type="button" data-model-id="${esc(model.id)}" data-search="${esc(searchBlob(model))}" aria-pressed="false">
        <span class="model-button-top"><b>${esc(model.short_title||model.title)}</b><em>${esc(model.maturity||'T1')}</em></span>
        <small>${esc(stages.get(model.id)||'programme')} · ${done.filled}/${done.total} contract</small>
      </button>`;
    }).join('');
    modelButtons=[...listEl.querySelectorAll('.model-button')];
    modelButtons.forEach(button=>button.addEventListener('click',()=>activateModel(button.dataset.modelId)));
    if(models.length)activateModel(models[0].id);
  }

  function renderMaster(master){
    const equations=master.root_formalisms||[];
    $('metric-equations').textContent=equations.length;
    $('metric-open').textContent=(master.unresolved_primary_targets||[]).length;
    const listEl=$('equation-list');
    const initial=8;
    listEl.innerHTML=equations.map((equation,index)=>`<div class="equation-row ${index>=initial?'extra':''}"><span>${String(index+1).padStart(2,'0')}</span><code>${esc(equation)}</code></div>`).join('');
    const toggle=$('equation-toggle');
    if(equations.length>initial){
      toggle.hidden=false;
      toggle.textContent=`Show all ${equations.length} equations`;
      toggle.addEventListener('click',()=>{
        const expanded=listEl.classList.toggle('expanded');
        toggle.textContent=expanded?'Show fewer equations':`Show all ${equations.length} equations`;
      });
    }
  }

  function renderFilters(){
    const wrap=$('domain-filters');
    wrap.innerHTML=presets.map(([label,value],index)=>`<button type="button" data-query="${esc(value)}" class="${index===0?'active':''}">${esc(label)}</button>`).join('');
    wrap.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{
      wrap.querySelectorAll('button').forEach(item=>item.classList.remove('active'));
      button.classList.add('active');
      setSearch(button.dataset.query||'');
      if(button.dataset.query)$('record-drawer').open=true;
    }));
  }

  function applySearch(){
    const query=$('science-search').value||'';
    let visibleModels=0;
    let visibleRecords=0;
    let firstModel='';

    modelButtons.forEach(button=>{
      const show=matches(button.dataset.search||button.textContent,query);
      button.hidden=!show;
      if(show){visibleModels++;if(!firstModel)firstModel=button.dataset.modelId;}
    });
    recordCards.forEach(card=>{
      const show=matches(card.dataset.search||card.textContent,query);
      card.hidden=!show;
      if(show)visibleRecords++;
    });

    const currentVisible=modelButtons.some(button=>button.dataset.modelId===activeId&&!button.hidden);
    if(!currentVisible){if(firstModel)activateModel(firstModel);else renderModel(null);}

    $('model-count').textContent=query?`${visibleModels} of ${modelButtons.length}`:`${modelButtons.length} models`;
    $('model-empty').hidden=visibleModels!==0;
    $('record-count').textContent=query?`${visibleRecords} of ${recordCards.length} records`:`${recordCards.length} records`;
    $('catalog-empty').hidden=visibleRecords!==0;
    $('clear-search').hidden=!query;
    $('search-note').textContent=query?`${visibleModels} model${visibleModels===1?'':'s'} and ${visibleRecords} record${visibleRecords===1?'':'s'} match “${query}”.`:'Search filters both developed models and the complete source-record collection.';
  }

  function setSearch(value){
    $('science-search').value=value||'';
    applySearch();
  }

  function wireSearch(){
    recordCards=[...document.querySelectorAll('.catalog-card')];
    $('science-search').addEventListener('input',()=>{
      document.querySelectorAll('#domain-filters button').forEach(button=>button.classList.remove('active'));
      applySearch();
    });
    $('clear-search').addEventListener('click',()=>{
      document.querySelectorAll('#domain-filters button').forEach((button,index)=>button.classList.toggle('active',index===0));
      setSearch('');
    });
    applySearch();
  }

  async function init(){
    renderFilters();
    const results=await Promise.allSettled([
      get(SOURCE+'science-master-index.json'),
      get(SOURCE+'science-model-registry.json'),
      get('./catalog.json')
    ]);
    let failures=0;
    if(results[0].status==='fulfilled')renderMaster(results[0].value);else failures++;
    if(results[1].status==='fulfilled')renderModels(results[1].value);else{failures++;$('model-list').innerHTML='<div class="loading">Model registry unavailable.</div>';$('model-view').innerHTML='<div class="loading">Model registry unavailable; source records remain below.</div>';}
    if(results[2].status==='fulfilled')$('metric-records').textContent=results[2].value.count??document.querySelectorAll('.catalog-card').length;else{failures++;$('metric-records').textContent=document.querySelectorAll('.catalog-card').length||'—';}
    wireSearch();
    const state=$('data-state');
    state.textContent=failures?`Loaded with ${failures} data source${failures===1?'':'s'} unavailable.`:'Models, equations and compiled source records loaded.';
    state.className=failures?'error':'ok';
  }

  document.addEventListener('DOMContentLoaded',init);
})();
