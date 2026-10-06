(()=>{
  'use strict';

  const BASE='../knowledge/science/';
  const $=id=>document.getElementById(id);
  const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'
  }[char]));

  async function getJson(url){
    const response=await fetch(url,{cache:'no-cache'});
    if(!response.ok) throw new Error(`${url}: ${response.status}`);
    return response.json();
  }

  function renderEquations(master){
    const list=$('equation-list');
    if(!list) return;
    const equations=Array.isArray(master.root_formalisms)?master.root_formalisms:[];
    const initial=12;
    list.innerHTML=equations.map((equation,index)=>
      `<div class="equation-row ${index>=initial?'extra':''}"><span class="eq-no">${String(index+1).padStart(2,'0')}</span><code>${esc(equation)}</code></div>`
    ).join('') || '<div class="loading-card">No canonical equations found.</div>';

    const metric=$('metric-equations');
    if(metric) metric.textContent=equations.length;

    const toggle=$('equation-toggle');
    if(toggle && equations.length>initial){
      toggle.hidden=false;
      toggle.textContent=`Show all ${equations.length} equations`;
      toggle.addEventListener('click',()=>{
        const expanded=list.classList.toggle('expanded');
        toggle.textContent=expanded?'Show fewer equations':`Show all ${equations.length} equations`;
      });
    }
  }

  function renderOpenWork(master){
    const grid=$('open-questions-grid');
    const targets=Array.isArray(master.unresolved_primary_targets)?master.unresolved_primary_targets:[];
    if(grid){
      grid.innerHTML=targets.map((target,index)=>
        `<article class="question-card"><strong>${String(index+1).padStart(2,'0')}</strong> ${esc(target)}</article>`
      ).join('') || '<div class="loading-card">No open targets listed.</div>';
    }
    const metric=$('metric-open');
    if(metric) metric.textContent=targets.length;
    const count=$('open-count');
    if(count) count.textContent=targets.length?`(${targets.length})`:'';
  }

  function wireCatalogSearch(){
    const input=$('catalog-search');
    const count=$('catalog-count');
    const empty=$('catalog-empty');
    const clear=$('clear-search');
    const cards=[...document.querySelectorAll('.catalog-card')];
    if(!input || !cards.length) return;

    const draw=()=>{
      const query=input.value.trim().toLowerCase();
      const tokens=query.split(/\s+/).filter(Boolean);
      let shown=0;
      cards.forEach(card=>{
        const haystack=(card.dataset.search||card.textContent||'').toLowerCase();
        const match=tokens.every(token=>haystack.includes(token));
        card.hidden=!match;
        if(match) shown++;
      });
      if(count) count.textContent=query?`${shown} of ${cards.length} records`:`${cards.length} records`;
      if(empty) empty.hidden=shown!==0;
      if(clear) clear.hidden=!query;
    };

    input.addEventListener('input',draw);
    if(clear) clear.addEventListener('click',()=>{input.value='';draw();input.focus();});
    draw();
  }

  async function init(){
    const state=$('data-state');
    try{
      const [master,catalog]=await Promise.all([
        getJson(BASE+'science-master-index.json'),
        getJson('./catalog.json')
      ]);
      renderEquations(master);
      renderOpenWork(master);
      if(catalog?.count!=null && $('metric-records')) $('metric-records').textContent=catalog.count;
      if(state){state.textContent='Canonical science data loaded.';state.className='data-state ok';}
    }catch(error){
      console.error(error);
      if(state){state.textContent='The static page is available; live data could not be refreshed.';state.className='data-state error';}
    }
    wireCatalogSearch();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();
