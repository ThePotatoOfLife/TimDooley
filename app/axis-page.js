(()=>{
  const tabs=[...document.querySelectorAll('.path-tabs [role="tab"]')];
  const panels=[...document.querySelectorAll('.path-panel')];
  function select(id,focus=false){
    tabs.forEach(t=>{const on=t.dataset.path===id;t.setAttribute('aria-selected',String(on));if(on&&focus)t.focus()});
    panels.forEach(p=>{const on=p.id==='path-'+id;p.classList.toggle('is-active',on);p.hidden=!on});
    const url=new URL(location.href);if(id==='life')url.searchParams.delete('path');else url.searchParams.set('path',id);history.replaceState(null,'',url);
  }
  tabs.forEach((t,i)=>{
    t.addEventListener('click',()=>select(t.dataset.path));
    t.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();const d=e.key==='ArrowRight'?1:-1;const n=(i+d+tabs.length)%tabs.length;select(tabs[n].dataset.path,true)});
  });
  const requested=new URL(location.href).searchParams.get('path');if(['life','strife','repair','tim'].includes(requested))select(requested);

  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  async function bootTransitions(){
    const statesRoot=document.getElementById('axisTransitionStates');
    const detail=document.getElementById('axisTransitionDetail');
    const tests=document.getElementById('axisTransitionTests');
    const conceptField=document.getElementById('axisConceptField');
    if(!statesRoot||!detail)return;
    try{
      const response=await fetch('../data/axis-flow-contract.json');
      if(!response.ok)throw new Error('transition contract unavailable');
      const data=await response.json();
      const model=data.transition_model;
      if(!model?.state_classes||!Array.isArray(model.transitions))throw new Error('transition grammar missing');
      const states=model.state_classes;
      const concepts=model.concept_traces||{};
      const houseMap=model.house_concept_map||{};
      const conceptRoot=document.getElementById('axisConceptContext');
      const order=['observed','residue','unresolved','capture','closure','threshold','transformed_recurrence','living_root','generative','habitation','transmission','integration','orientation','return'];
      if(conceptField){conceptField.innerHTML=(model.concept_groups||[]).map(group=>{const chips=(group.concepts||[]).filter(id=>concepts[id]).map(id=>'<button class="concept-chip" type="button" data-concept="'+esc(id)+'" aria-pressed="false">'+esc(concepts[id].label)+'</button>').join('');return '<div class="concept-group"><strong>'+esc(group.label)+'</strong><div class="concept-chips">'+chips+'</div></div>';}).join('');}
      statesRoot.innerHTML=order.filter(id=>states[id]).map(id=>{
        const s=states[id],dims=(s.preferred_dimensions||[]).map(d=>'D'+d).join(' · ');
        return '<button class="transition-state" type="button" data-state="'+esc(id)+'" aria-pressed="false"><strong>'+esc(s.label)+'</strong><small>'+esc(dims||'cross-layer')+'</small></button>';
      }).join('');
      if(tests)tests.textContent='Trace rule · '+model.trace_rule;
      function renderState(id){
        const s=states[id];if(!s)return;
        statesRoot.querySelectorAll('.transition-state').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.state===id)));
        const next=model.transitions.filter(t=>t.from===id);
        const questions=(s.questions||[]).map(q=>'<li>'+esc(q)+'</li>').join('');
        const cards=next.length?next.map(t=>{
          const target=states[t.to]?.label||t.to;
          return '<div class="transition-card"><b>→ '+esc(target)+'</b><span class="transition-route">'+esc(t.route||'')+'</span><span class="transition-op">'+esc(t.operator)+'</span><small><b>Condition:</b> '+esc(t.condition)+'</small></div>';
        }).join(''):'<div class="transition-empty">No outgoing transition is defined from this state.</div>';
        detail.innerHTML='<h3>'+esc(s.label)+'</h3><p>'+esc(s.description)+'</p><div class="transition-next">'+cards+'</div>'+(questions?'<div class="transition-tests"><b>Questions to ask here</b><ul>'+questions+'</ul></div>':'');
        const url=new URL(location.href);url.searchParams.set('state',id);history.replaceState(null,'',url);
      }
      statesRoot.addEventListener('click',e=>{const b=e.target.closest('[data-state]');if(b)renderState(b.dataset.state)});
      function conceptHtml(id){
        const concept=concepts[id];if(!concept)return '';
        const houseId=houseMap[id];
        const houseLink=houseId?'<a class="transition-house-link" href="../house/?operator='+encodeURIComponent(houseId)+'#operators">Inspect House topology →</a>':'';
        return '<div class="transition-concept"><span class="kind">'+esc(concept.kind||'concept')+'</span><h3>'+esc(concept.label||id)+'</h3><p>'+esc(concept.function||'')+'</p>'+(concept.question?'<q>'+esc(concept.question)+'</q>':'')+houseLink+'</div>';
      }
      function renderConcept(id){const concept=concepts[id];if(!concept)return false;if(conceptRoot)conceptRoot.innerHTML=conceptHtml(id);conceptField?.querySelectorAll('[data-concept]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.concept===id)));const u=new URL(location.href);u.searchParams.set('concept',id);u.searchParams.delete('state');history.replaceState(null,'',u);renderState(concept.primary_state);return true;}
      conceptField?.addEventListener('click',e=>{const b=e.target.closest('[data-concept]');if(b)renderConcept(b.dataset.concept)});
      const url=new URL(location.href);
      const requestedConcept=url.searchParams.get('concept');
      const concept=concepts[requestedConcept];
      if(concept&&conceptRoot){
        conceptRoot.innerHTML=conceptHtml(requestedConcept);
        conceptField?.querySelectorAll('[data-concept]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.concept===requestedConcept)));
      }
      const requestedState=url.searchParams.get('state');
      renderState(states[requestedState]?requestedState:(concept?.primary_state&&states[concept.primary_state]?concept.primary_state:'residue'));
    }catch(error){
      statesRoot.innerHTML='<span class="transition-empty">The transition grammar could not be loaded. The four narrative paths above remain available.</span>';
      if(tests)tests.textContent='';
    }
  }
  bootTransitions();
})();

(async()=>{
  const buttons=document.getElementById('axisRouteCaseButtons'),detail=document.getElementById('axisRouteCaseDetail');
  if(!buttons||!detail)return;
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  try{
    const res=await fetch('../data/house/route-case-matrix.json');if(!res.ok)throw new Error('route cases unavailable');
    const data=await res.json(),rows=data.cases||[];
    buttons.innerHTML=rows.map((x,i)=>'<button type="button" data-route-case="'+esc(x.id)+'" aria-pressed="'+String(i===0)+'">'+esc(x.subject||x.subject_ref||x.id)+'</button>').join('');
    const render=id=>{
      const x=rows.find(r=>r.id===id)||rows[0];if(!x)return;
      buttons.querySelectorAll('[data-route-case]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.routeCase===x.id)));
      detail.innerHTML='<h3>'+esc(x.subject||x.subject_ref||x.id)+'</h3><p><b>Proposed transition:</b> '+esc(x.proposed_transition||'')+'</p><p><b>Operator:</b> '+esc(x.operator||'')+'</p><p><b>Required condition:</b> '+esc(x.condition_required||'')+'</p><ul><li><b>Evidence:</b> '+esc((x.evidence_for_transition||[]).join(' · '))+'</li><li><b>Falsifier:</b> '+esc((x.counterevidence_or_falsifier||[]).join(' · '))+'</li><li><b>World return:</b> '+esc((x.world_return_measure||[]).join(' · '))+'</li></ul><p><b>Status:</b> '+esc(x.status||'')+'</p><p>'+esc(x.route_boundary||'')+'</p>';
    };
    buttons.addEventListener('click',e=>{const b=e.target.closest('[data-route-case]');if(b)render(b.dataset.routeCase)});
    render(rows[0]?.id);
  }catch(e){detail.innerHTML='<h3>Route cases unavailable</h3><p>The route grammar remains available above.</p>'}
})();

(async function renderCanonicalVerticalField(){
 const levels=document.getElementById('axisVerticalLevels'),routes=document.getElementById('axisVerticalRoutes');
 if(!levels||!routes)return;
 const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
 try{
  const res=await fetch('../knowledge/core/source-to-swamp-vertical-field.json');if(!res.ok)throw new Error('vertical field unavailable');
  const data=await res.json();
  levels.innerHTML=(data.levels||[]).sort((a,b)=>a.vertical_order-b.vertical_order).map(x=>
   '<article class="axis-level-live"><div class="n">'+esc(String(x.vertical_order).padStart(2,'0'))+'</div><div><strong>'+esc(x.label)+'</strong><span>'+esc(x.project_function||'')+'</span></div><div><span><b>Inhabits:</b> '+esc((x.inhabitants||[]).join(' · '))+'</span>'+(x.boundary?'<small>'+esc(x.boundary)+'</small>':'')+'</div></article>'
  ).join('');
  routes.innerHTML=Object.entries(data.routes||{}).map(([name,steps])=>
   '<article><b>'+esc(name)+'</b><span>'+esc((steps||[]).join(' → '))+'</span></article>'
  ).join('');
 }catch(e){
  levels.innerHTML='<p class="boundary">The canonical vertical field could not be loaded.</p>';
  routes.innerHTML='';
 }
})();
