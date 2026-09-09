(()=>{
  'use strict';
  const hubStyle=document.createElement('link');hubStyle.rel='stylesheet';hubStyle.href='./science-hub.css?v=20260910c';document.head.appendChild(hubStyle);
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

  function injectEvidenceAndMap(){
    const scope=document.querySelector('.scope-strip');
    const nav=document.querySelector('.section-nav');
    if(!scope||!nav||$('evidence-map')) return;
    const section=document.createElement('section');
    section.id='evidence-map';
    section.className='section-block evidence-map-section';
    section.innerHTML=`
      <div class="section-head"><div><p class="section-kicker">Evidence + relationship map</p><h2>See what each scientific layer is — and how the layers connect.</h2></div><p>The map shows research lineage and comparison, not proof of equivalence. The evidence legend separates recovered project material, later formalization, established external science, speculative comparison and unresolved targets.</p></div>
      <div class="evidence-legend" aria-label="Science evidence status legend">
        <article data-evidence="primary"><span class="evidence-dot"></span><strong>Primary / project-attested</strong><p>Direct project/public evidence or a strongly recovered first-party equation.</p></article>
        <article data-evidence="book"><span class="evidence-dot"></span><strong>Book-derived</strong><p>Material preserved in the 2024 Great Book science stratum.</p></article>
        <article data-evidence="recovered"><span class="evidence-dot"></span><strong>Conversation archaeology</strong><p>Recovered from dated conversation history; exact original notation may remain incomplete.</p></article>
        <article data-evidence="formalism"><span class="evidence-dot"></span><strong>Project formalism</strong><p>Later mathematical language developed to make recurring structures explicit.</p></article>
        <article data-evidence="archive"><span class="evidence-dot"></span><strong>Archive formalization</strong><p>Repository synthesis or reconstruction; not retroactively treated as original notation.</p></article>
        <article data-evidence="external"><span class="evidence-dot"></span><strong>Established external science</strong><p>Standard mathematics or physics used as constraint, comparator or repair option.</p></article>
        <article data-evidence="speculative"><span class="evidence-dot"></span><strong>Speculative comparator</strong><p>A structured analogy or research possibility, not an established physical result.</p></article>
        <article data-evidence="open"><span class="evidence-dot"></span><strong>Open / unrecovered</strong><p>A transcript, derivation, variable definition, prediction or test the archive does not yet have.</p></article>
      </div>
      <div class="science-connection-shell">
        <svg class="science-connection-map" viewBox="0 0 1180 650" role="img" aria-labelledby="science-map-title science-map-desc">
          <title id="science-map-title">Science Atlas relationship map</title><desc id="science-map-desc">A network connecting Great Book science, Unified Potato Theory, the Potato Axis spiral, Potato Dynamics, dimensions, quantum physics, Standard Model and gauge unification, information, biology, astronomy and theory testing.</desc>
          <defs><marker id="science-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z"></path></marker></defs>
          <g class="connection-edges" marker-end="url(#science-arrow)"><path d="M175 80 C300 80 315 170 430 170"/><path d="M175 80 C305 80 320 280 430 280"/><path d="M175 80 C305 80 320 395 430 395"/><path d="M545 170 C650 170 665 280 755 280"/><path d="M545 280 C650 280 665 280 755 280"/><path d="M545 395 C650 395 665 280 755 280"/><path d="M870 280 C945 280 955 160 1050 160"/><path d="M870 280 C945 280 955 280 1050 280"/><path d="M870 280 C945 280 955 400 1050 400"/><path d="M545 395 C680 395 760 535 890 535"/><path d="M1050 160 C1010 470 990 535 890 535"/><path d="M1050 280 C1010 490 990 535 890 535"/><path d="M1050 400 C1005 485 980 535 890 535"/></g>
          <g class="connection-node" data-science-filter="great book" transform="translate(45 40)"><rect width="260" height="80" rx="16"/><text x="18" y="31">2024 Great Book science</text><text class="connection-sub" x="18" y="55">spiral · fields · quantum · geometry</text></g>
          <g class="connection-node primary" data-science-filter="unified potato theory" transform="translate(365 130)"><rect width="250" height="80" rx="16"/><text x="18" y="31">Unified Potato Theory</text><text class="connection-sub" x="18" y="55">field · symmetry · Lagrangian</text></g>
          <g class="connection-node primary" data-science-filter="spiral axis" transform="translate(365 240)"><rect width="250" height="80" rx="16"/><text x="18" y="31">Potato Axis spiral</text><text class="connection-sub" x="18" y="55">log spiral · φ quarter-turn</text></g>
          <g class="connection-node" data-science-filter="potato dynamics" transform="translate(365 355)"><rect width="250" height="80" rx="16"/><text x="18" y="31">Potato Dynamics</text><text class="connection-sub" x="18" y="55">state · Axis flow · Door maps</text></g>
          <g class="connection-node hub" data-science-filter="dimension 11d" transform="translate(700 240)"><rect width="225" height="80" rx="16"/><text x="18" y="31">Dimensional physics</text><text class="connection-sub" x="18" y="55">5D Door · 11D · black holes</text></g>
          <g class="connection-node" data-science-filter="quantum standard model" transform="translate(960 120)"><rect width="195" height="80" rx="16"/><text x="18" y="31">Quantum + SM</text><text class="connection-sub" x="18" y="55">QFT · Higgs · quarks</text></g>
          <g class="connection-node" data-science-filter="gauge unification supersymmetry" transform="translate(960 240)"><rect width="195" height="80" rx="16"/><text x="18" y="31">Gauge unification</text><text class="connection-sub" x="18" y="55">SU(4) · SU(5) · Spin(10)</text></g>
          <g class="connection-node" data-science-filter="information" transform="translate(960 360)"><rect width="195" height="80" rx="16"/><text x="18" y="31">Information</text><text class="connection-sub" x="18" y="55">entropy · graphs · holography</text></g>
          <g class="connection-node testing" data-science-filter="testing theory everything" transform="translate(765 495)"><rect width="250" height="80" rx="16"/><text x="18" y="31">Testing + TOE audit</text><text class="connection-sub" x="18" y="55">limits · observables · falsifiers</text></g>
        </svg>
        <div class="connection-branches"><strong>Cross-scale branches</strong><button type="button" data-science-filter="microtubule biology consciousness">Life & cognition</button><button type="button" data-science-filter="astronomy galactic cmb celestial">Astronomy & cosmology</button><button type="button" data-science-filter="advanced retarded time">Time symmetry</button><button type="button" data-science-filter="higgs quantum tuber boson">Higgs / Potato sector</button><button type="button" data-science-filter="black hole phase transition">Black-hole transitions</button><button type="button" data-science-filter="">Show the full library</button><p>Clicking a node jumps to the compiled library and filters the canonical records.</p></div>
      </div>`;
    scope.insertAdjacentElement('afterend',section);
    const link=document.createElement('a');link.href='#evidence-map';link.textContent='Evidence + graph';nav.prepend(link);
  }

  function wireMapToCatalog(){
    const input=$('catalog-search');
    if(!input)return;
    document.querySelectorAll('[data-science-filter]').forEach(node=>{
      node.setAttribute('tabindex','0');node.setAttribute('role','button');
      const activate=()=>{input.value=node.dataset.scienceFilter||'';input.dispatchEvent(new Event('input',{bubbles:true}));$('library')?.scrollIntoView({behavior:'smooth'});};
      node.addEventListener('click',activate);node.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate();}});
    });
  }

  function renderMaster(m){
    $('metric-domains').textContent=m.domains?.length??'—';
    $('metric-equations').textContent=m.root_formalisms?.length??'—';
    $('metric-provenance').textContent=m.epistemic_classes?.length??'—';
    const timeline=m.developmental_genealogy||[];
    $('science-timeline').innerHTML=timeline.map((x,i)=>{
      const concepts=Array.isArray(x.concepts)?x.concepts:[];
      return `<article class="timeline-item"><div class="period">${esc(x.period||x.date||`Stage ${i+1}`)}</div><h3>${esc(concepts.slice(0,3).join(' · ')||'Recovered science stratum')}</h3><div class="topic-pills">${concepts.slice(3,11).map(y=>`<span>${esc(y)}</span>`).join('')}</div>${x.status?`<p class="microcopy">${esc(x.status)}</p>`:''}</article>`;
    }).join('');
    const equations=m.root_formalisms||[], list=$('equation-list'), initial=18;
    list.innerHTML=equations.map((x,i)=>`<div class="equation-row ${i>=initial?'extra':''}"><span class="eq-no">${String(i+1).padStart(2,'0')}</span><code>${esc(x)}</code><span class="eq-class">${esc(provenanceClass(x))}</span></div>`).join('');
    const toggle=$('equation-toggle');
    if(equations.length>initial){toggle.hidden=false;toggle.textContent=`Show all ${equations.length} equations`;toggle.onclick=()=>{const expanded=list.classList.toggle('expanded');toggle.textContent=expanded?'Show fewer equations':`Show all ${equations.length} equations`;};}
    const domains=m.domains||[], input=$('domain-search'), grid=$('domain-grid'), empty=$('domain-empty');
    const draw=()=>{const q=input.value.trim().toLowerCase();const matched=domains.filter(x=>`${x.id||''} ${x.title||''} ${(x.topics||[]).join(' ')}`.toLowerCase().includes(q));grid.innerHTML=matched.map(x=>`<article class="domain-card"><span class="domain-id">${esc(x.id||'domain')}</span><h3>${esc(x.title||x.id)}</h3><div class="topics">${(x.topics||[]).slice(0,16).map(y=>`<span>${esc(y)}</span>`).join('')}</div></article>`).join('');empty.hidden=!!matched.length;};
    input.addEventListener('input',draw);draw();
    $('open-questions-grid').innerHTML=(m.unresolved_primary_targets||[]).map((x,i)=>`<article class="question-card"><span class="q-no">Target ${String(i+1).padStart(2,'0')}</span>${esc(x)}</article>`).join('');
  }

  function renderUpt(u){const target=$('upt-terms'),terms=u.term_map||[];target.innerHTML=terms.length?terms.map(x=>`<div class="term-item"><code>${esc(x.term)}</code><span>${esc(x.intended_role)}</span></div>`).join(''):'<p class="microcopy">Term map is in the recovery record.</p>';}
  function renderSpiral(s){const p=s.exact_properties||{},properties=[['Quarter turn',p.quarter_turn_scaling,'Golden-ratio radial scaling after 90°.'],['Half turn',p.half_turn_scaling,'Two quarter-turn scalings combine to φ².'],['Full turn',p.full_turn_scaling,'One full revolution gives φ⁴ radial scaling.'],['Differential form',p.differential_form,'Local radial growth law.'],['Curvature',p.curvature,'Curvature falls inversely with radius.'],['Self-similarity',p.self_similarity,'Rotation plus scaling reproduces the same curve.']].filter(x=>x[1]);if(properties.length)$('spiral-properties').innerHTML=properties.map(([label,value,note])=>`<article><span>${esc(label)}</span><strong>${esc(value)}</strong><p>${esc(note)}</p></article>`).join('');}
  function renderToe(t){const strata=t.unification_strata||t.developmental_strata||[];$('toe-strata').innerHTML=strata.length?strata.map(x=>`<div class="compact-item"><strong>${esc(x.name||x.title||x.period||x.date||'Unification stratum')}</strong><span>${esc(x.date||x.period||x.classification||x.status||'')}</span></div>`).join(''):'<p class="microcopy">See the TOE archaeology record for the full long-arc programme.</p>';const req=t.physical_toe_requirements||t.requirements||[];$('toe-requirements').innerHTML=req.length?req.map(x=>`<li>${esc(typeof x==='string'?x:(x.requirement||x.name||JSON.stringify(x)))}</li>`).join(''):'<li>Recover known physical limits, define observables, and produce testable predictions.</li>';}

  function wireCatalog(){const input=$('catalog-search'),cards=[...document.querySelectorAll('.catalog-card')],count=$('catalog-count'),empty=$('catalog-empty');if(!input||!cards.length)return;const draw=()=>{const q=input.value.trim().toLowerCase();let shown=0;cards.forEach(card=>{const match=!q||(card.dataset.search||card.textContent.toLowerCase()).includes(q);card.hidden=!match;if(match)shown++;});count.textContent=q?`${shown} of ${cards.length} records`:`${cards.length} records`;empty.hidden=shown!==0;};input.addEventListener('input',draw);draw();wireMapToCatalog();}

  async function init(){
    injectEvidenceAndMap();
    const jobs={master:get(B+'science-master-index.json'),upt:get(B+'unified-potato-theory-2025-recovery.json'),spiral:get(B+'april-21-2025-potato-axis-spiral-primary-recovery.json'),toe:get(B+'theory-of-everything-archaeology.json'),catalog:get('./catalog.json')};
    const entries=Object.entries(jobs),results=await Promise.allSettled(entries.map(([,p])=>p)),data={};let failed=0;
    results.forEach((result,i)=>{if(result.status==='fulfilled')data[entries[i][0]]=result.value;else failed++;});
    if(data.master)renderMaster(data.master);if(data.upt)renderUpt(data.upt);if(data.spiral)renderSpiral(data.spiral);if(data.toe)renderToe(data.toe);if(data.catalog?.count!=null)$('metric-records').textContent=data.catalog.count;wireCatalog();
    const state=$('data-state');state.textContent=failed?`Atlas loaded; ${failed} auxiliary data source${failed===1?' is':'s are'} unavailable.`:`Canonical science data loaded · ${data.catalog?.count??'all'} compiled records · master index ${data.master?.updated||'current'}`;state.className='data-state '+(failed?'error':'ok');
  }
  document.addEventListener('DOMContentLoaded',init);
})();