(() => {
  const root = document.getElementById('text-library');
  const catalogSearch = document.getElementById('catalog-search');
  const queryInput = document.getElementById('text-search');
  const runSearch = document.getElementById('run-text-search');
  const resultsRoot = document.getElementById('text-results');
  const select = document.getElementById('local-text-select');
  const loadButton = document.getElementById('local-text-load');
  const reader = document.getElementById('local-text-reader');
  const prevButton = document.getElementById('local-prev');
  const nextButton = document.getElementById('local-next');
  const pageStatus = document.getElementById('local-page-status');
  let texts = [];
  let corpus = null;
  let bibleCatalog = null;
  let loadedText = '';
  let page = 0;
  const PAGE_SIZE = 22000;
  const esc = s => String(s ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));

  function renderCatalogue(q='') {
    q = q.trim().toLowerCase();
    const rows = texts.filter(t => !q || [t.tradition,t.work,t.scope,t.completeness,t.language,t.edition].flat().join(' ').toLowerCase().includes(q));
    root.innerHTML = rows.map(t => {
      const local = corpus?.local_full_texts?.find(x => x.id === t.id || x.work === t.work);
      const action = local ? `<button type="button" class="text-open-local" data-text-id="${esc(local.id)}">Read locally</button>` : `<a href="${esc(t.reader)}" target="_blank" rel="noopener">Open library / reader ↗</a>`;
      return `<article class="belief-card"><div class="belief-card-kicker">${esc(t.tradition)}</div><h2>${esc(t.work)}</h2><p>${esc(t.scope)}</p><p><strong>Completeness:</strong> ${esc(t.completeness)}</p><p>${esc(t.source_note)}</p><p><strong>Language:</strong> ${esc(t.language)}${t.edition ? ` · <strong>Edition:</strong> ${esc(t.edition)}` : ''}</p>${action}</article>`;
    }).join('') || '<p>No matching texts.</p>';
    root.querySelectorAll('.text-open-local').forEach(b => b.addEventListener('click', () => {
      select.value = b.dataset.textId;
      loadLocalBook(b.dataset.textId);
      document.getElementById('local-text-reader')?.scrollIntoView({behavior:'smooth',block:'start'});
    }));
  }

  function snippets(text, query, limit=5) {
    const lower=text.toLowerCase(), needle=query.toLowerCase();
    if (!needle) return [];
    const out=[]; let from=0;
    while(out.length<limit){
      const i=lower.indexOf(needle, from); if(i<0) break;
      const start=Math.max(0,i-180), end=Math.min(text.length,i+needle.length+240);
      out.push({index:i, text:text.slice(start,end).replace(/\s+/g,' ').trim()});
      from=i+Math.max(needle.length,1);
    }
    return out;
  }

  function locateBibleBook(text, index) {
    if(!bibleCatalog?.books?.length) return '';
    let best = null;
    for(const b of bibleCatalog.books){
      const candidates=[b.name.toUpperCase(), `THE BOOK OF ${b.name.toUpperCase()}`, `THE GOSPEL ACCORDING TO ${b.name.toUpperCase()}`];
      for(const heading of candidates){
        const pos=text.toUpperCase().lastIndexOf(heading, index);
        if(pos>=0 && (!best || pos>best.pos)) best={pos,name:b.name};
      }
    }
    return best?.name || '';
  }

  function locateGeneric(text, index, source) {
    const before=text.slice(0,index);
    if(source.id.startsWith('bible-')) return locateBibleBook(text,index);
    const patterns=[
      /(?:^|\n)\s*(?:Ch(?:apter)?\.?|Chapter)\s*([0-9]{1,3})\b/gi,
      /(?:^|\n)\s*([0-9]{1,3})\.(?:\s|$)/g
    ];
    let best = null;
    for(const re of patterns){
      let m;
      while((m=re.exec(before))!==null) best=m[1];
    }
    return best ? `Section ${best}` : '';
  }

  async function loadLocalCorpus(){
    corpus = await fetch('data/religious-text-corpus.json',{cache:'no-store'}).then(r=>r.json());
    bibleCatalog = await fetch('data/christianity/bible-kjv.json',{cache:'no-store'}).then(r=>r.json());
  }

  function populateLocalSelect(){
    if(!select) return;
    const local = corpus?.local_full_texts || [];
    select.innerHTML = local.map(s => `<option value="${esc(s.id)}">${esc(s.work)} — ${esc(s.edition)}</option>`).join('') || '<option value="">No local editions</option>';
  }

  async function loadLocalBook(id=select?.value){
    const source = (corpus?.local_full_texts||[]).find(s => s.id === id);
    if(!source) return;
    reader.innerHTML = '<p>Loading the local full text…</p>';
    try{
      loadedText = await fetch(source.path,{cache:'force-cache'}).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.text()});
      page = 0;
      renderLocalPage(source);
    }catch(error){
      reader.innerHTML = `<p>Could not read the repository copy.</p><p class="bible-status">${esc(error.message)}</p>`;
      pageStatus.textContent = 'Load failed';
    }
  }

  function renderLocalPage(source){
    const total = Math.max(1, Math.ceil(loadedText.length / PAGE_SIZE));
    page = Math.min(total-1, Math.max(0,page));
    const start = page * PAGE_SIZE;
    const end = Math.min(loadedText.length, start + PAGE_SIZE);
    const chunk = loadedText.slice(start,end);
    reader.innerHTML = `<h3>${esc(source.work)}</h3><p class="bible-status">${esc(source.edition)} · local repository copy · characters ${start.toLocaleString()}–${end.toLocaleString()} of ${loadedText.length.toLocaleString()}</p><pre style="white-space:pre-wrap;line-height:1.7">${esc(chunk)}</pre>`;
    pageStatus.textContent = `Page ${page+1} / ${total}`;
    prevButton.disabled = page === 0;
    nextButton.disabled = page >= total-1;
  }

  async function runConcordance(){
    const q=queryInput.value.trim();
    if(!q){resultsRoot.innerHTML='<p>Enter a word or phrase first.</p>';return;}
    resultsRoot.innerHTML='<p>Searching locally stored full texts…</p>';
    const rows=[];
    for(const source of (corpus?.local_full_texts||[])){
      try{
        const text=await fetch(source.path,{cache:'force-cache'}).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.text()});
        const lower=text.toLowerCase(), needle=q.toLowerCase();
        let count=0, at=0;
        while((at=lower.indexOf(needle,at))>=0){count++;at+=Math.max(needle.length,1)}
        const hits=snippets(text,q,5).map(x=>({...x,location:locateGeneric(text,x.index,source)}));
        rows.push({source,count,hits});
      }catch(error){ rows.push({source,count:null,hits:[],error:error.message}); }
    }
    const active=rows.filter(r=>r.count!==null && r.count>0);
    const total=active.reduce((n,r)=>n+r.count,0);
    resultsRoot.innerHTML=`<div class="belief-card"><h3>“${esc(q)}” across local editions</h3><p><strong>${active.length}</strong> of ${rows.length} local editions contain the query · <strong>${total}</strong> total exact matches.</p><p>Translations/editions remain separate; this is lexical overlap, not a claim that different words mean the same thing.</p></div>` + rows.map(r=>{
      const title=r.source.work;
      if(r.error)return `<article class="belief-card"><h3>${esc(title)}</h3><p>Could not read local edition: ${esc(r.error)}</p></article>`;
      if(!r.count)return `<article class="belief-card"><h3>${esc(title)}</h3><p>No exact match.</p></article>`;
      return `<article class="belief-card"><div class="belief-card-kicker">${esc(r.source.tradition)} · ${esc(r.source.edition)}</div><h3>${esc(title)}</h3><p><strong>${r.count}</strong> exact matches</p>${r.hits.map(h=>`<p><small>${h.location?`<strong>${esc(h.location)}</strong> · `:''}…${esc(h.text)}…</small></p>`).join('')}</article>`;
    }).join('');
  }

  Promise.all([
    fetch('data/religious-text-library.json').then(r=>r.json()),
    loadLocalCorpus()
  ]).then(([library])=>{
    texts=library.texts||[];
    populateLocalSelect();
    renderCatalogue();
    catalogSearch?.addEventListener('input',e=>renderCatalogue(e.target.value));
    runSearch?.addEventListener('click',runConcordance);
    queryInput?.addEventListener('keydown',e=>{if(e.key==='Enter')runConcordance()});
    loadButton?.addEventListener('click',()=>loadLocalBook());
    prevButton?.addEventListener('click',()=>{page--;renderLocalPage((corpus.local_full_texts||[]).find(s=>s.id===select.value));});
    nextButton?.addEventListener('click',()=>{page++;renderLocalPage((corpus.local_full_texts||[]).find(s=>s.id===select.value));});
    if(select?.value) loadLocalBook(select.value);
    const initial=new URLSearchParams(location.search).get('text');
    if(initial){queryInput.value=initial;runConcordance();}
  }).catch(e=>{
    root.innerHTML=`<p>Could not load text catalogue: ${esc(e.message)}</p>`;
    if(resultsRoot)resultsRoot.innerHTML='<p>The local concordance could not be initialized.</p>';
  });
})();
