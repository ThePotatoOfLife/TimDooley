(() => {
  const root = document.getElementById('text-library');
  const catalogSearch = document.getElementById('catalog-search');
  const queryInput = document.getElementById('text-search');
  const runSearch = document.getElementById('run-text-search');
  const resultsRoot = document.getElementById('text-results');
  let texts = [];
  let corpus = null;
  let bibleCatalog = null;
  const esc = s => String(s ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));

  function renderCatalogue(q='') {
    q = q.trim().toLowerCase();
    const rows = texts.filter(t => !q || [t.tradition,t.work,t.scope,t.completeness,t.language,t.edition].flat().join(' ').toLowerCase().includes(q));
    root.innerHTML = rows.map(t => `<article class="belief-card"><div class="belief-card-kicker">${esc(t.tradition)}</div><h2>${esc(t.work)}</h2><p>${esc(t.scope)}</p><p><strong>Completeness:</strong> ${esc(t.completeness)}</p><p>${esc(t.source_note)}</p><p><strong>Language:</strong> ${esc(t.language)}${t.edition ? ` · <strong>Edition:</strong> ${esc(t.edition)}` : ''}</p><a href="${esc(t.reader)}" target="_blank" rel="noopener">Open reader / source ↗</a></article>`).join('') || '<p>No matching texts.</p>';
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

  async function loadLocalCorpus(){
    corpus = await fetch('data/religious-text-corpus.json',{cache:'no-store'}).then(r=>r.json());
    bibleCatalog = await fetch('data/christianity/bible-kjv.json',{cache:'no-store'}).then(r=>r.json());
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
        const hits=snippets(text,q,5).map(x=>({...x,book:source.id.startsWith('bible-')?locateBibleBook(text,x.index):''}));
        rows.push({source,count,hits});
      }catch(error){ rows.push({source,count:null,hits:[],error:error.message}); }
    }
    const active=rows.filter(r=>r.count!==null && r.count>0);
    const total=active.reduce((n,r)=>n+r.count,0);
    resultsRoot.innerHTML=`<div class="belief-card"><h3>“${esc(q)}” across local editions</h3><p><strong>${active.length}</strong> of ${rows.length} local editions contain the query · <strong>${total}</strong> total exact matches.</p><p>Translations/editions remain separate; this is lexical overlap, not a claim that different words mean the same thing.</p></div>` + rows.map(r=>{
      const title=r.source.work;
      if(r.error)return `<article class="belief-card"><h3>${esc(title)}</h3><p>Could not read local edition: ${esc(r.error)}</p></article>`;
      if(!r.count)return `<article class="belief-card"><h3>${esc(title)}</h3><p>No exact match.</p></article>`;
      return `<article class="belief-card"><div class="belief-card-kicker">${esc(r.source.tradition)} · ${esc(r.source.edition)}</div><h3>${esc(title)}</h3><p><strong>${r.count}</strong> exact matches</p>${r.hits.map(h=>`<p><small>${h.book?`<strong>${esc(h.book)}</strong> · `:''}…${esc(h.text)}…</small></p>`).join('')}</article>`;
    }).join('');
  }

  Promise.all([
    fetch('data/religious-text-library.json').then(r=>r.json()),
    loadLocalCorpus()
  ]).then(([library])=>{
    texts=library.texts||[];
    renderCatalogue();
    catalogSearch?.addEventListener('input',e=>renderCatalogue(e.target.value));
    runSearch?.addEventListener('click',runConcordance);
    queryInput?.addEventListener('keydown',e=>{if(e.key==='Enter')runConcordance()});
    const initial=new URLSearchParams(location.search).get('text');
    if(initial){queryInput.value=initial;runConcordance();}
  }).catch(e=>{
    root.innerHTML=`<p>Could not load text catalogue: ${esc(e.message)}</p>`;
    if(resultsRoot)resultsRoot.innerHTML='<p>The local concordance could not be initialized.</p>';
  });
})();
