(()=>{
  let guides={};
  let observer=null;
  let renderScheduled=false;

  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const currentBranch=()=>{
    const m=location.hash.match(/^#branch=(.+)$/);
    return m?decodeURIComponent(m[1]):null;
  };

  function observe(reader){
    if(!observer||!reader)return;
    observer.takeRecords();
    observer.observe(reader,{childList:true,subtree:false});
  }

  function render(){
    const reader=document.querySelector('#reader');
    if(!reader)return;

    const id=currentBranch();
    const existing=reader.querySelector('.reader-guide-panel');
    const hero=reader.querySelector('.branchhero');

    if(!id||!guides[id]||!hero){
      if(existing)existing.remove();
      return;
    }

    if(existing?.dataset.guideBranch===id)return;

    const g=guides[id];
    const box=document.createElement('section');
    box.className='reader-guide-panel';
    box.dataset.guideBranch=id;
    box.innerHTML=`
      <div class="reader-guide-kicker">READ THIS FIRST</div>
      <h3>${esc(g.reader_question)}</h3>
      <p class="reader-guide-answer">${esc(g.short_answer)}</p>
      ${g.learn_first?.length?`<div class="reader-guide-row"><span>Learn first</span><div>${g.learn_first.map(x=>`<b>${esc(x)}</b>`).join('')}</div></div>`:''}
      ${g.do_not_start_with?.length?`<div class="reader-guide-row muted"><span>Skip for now</span><div>${g.do_not_start_with.map(x=>`<b>${esc(x)}</b>`).join('')}</div></div>`:''}
      <div class="reader-guide-actions"><a href="learn/">Back to Start Here</a><span>Then scroll down only when you want the graph, contexts and records.</span></div>`;

    observer?.disconnect();
    try{
      existing?.remove();
      hero.insertAdjacentElement('afterend',box);
    }finally{
      observe(reader);
    }
  }

  function scheduleRender(){
    if(renderScheduled)return;
    renderScheduled=true;
    requestAnimationFrame(()=>{
      renderScheduled=false;
      render();
    });
  }

  const scriptBase=document.currentScript?.src||location.href;
  const guideUrl=new URL('../knowledge/guides/branch-reader-guides.json',scriptBase).href;
  fetch(guideUrl)
    .then(r=>r.ok?r.json():Promise.reject(new Error('guide load failed')))
    .then(data=>{
      guides=data.guides||{};
      const reader=document.querySelector('#reader');
      if(reader){
        observer=new MutationObserver(scheduleRender);
        observe(reader);
      }
      render();
      window.addEventListener('hashchange',scheduleRender);
    })
    .catch(()=>{});
})();
