(()=>{
  let guides={};
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const currentBranch=()=>{
    const m=location.hash.match(/^#branch=(.+)$/);
    return m?decodeURIComponent(m[1]):null;
  };
  function render(){
    const id=currentBranch();
    if(!id||!guides[id])return;
    const reader=document.querySelector('#reader');
    const hero=reader?.querySelector('.branchhero');
    if(!hero)return;
    reader.querySelector('.reader-guide-panel')?.remove();
    const g=guides[id];
    const box=document.createElement('section');
    box.className='reader-guide-panel';
    box.innerHTML=`
      <div class="reader-guide-kicker">READ THIS FIRST</div>
      <h3>${esc(g.reader_question)}</h3>
      <p class="reader-guide-answer">${esc(g.short_answer)}</p>
      ${g.learn_first?.length?`<div class="reader-guide-row"><span>Learn first</span><div>${g.learn_first.map(x=>`<b>${esc(x)}</b>`).join('')}</div></div>`:''}
      ${g.do_not_start_with?.length?`<div class="reader-guide-row muted"><span>Skip for now</span><div>${g.do_not_start_with.map(x=>`<b>${esc(x)}</b>`).join('')}</div></div>`:''}
      <div class="reader-guide-actions"><a href="learn/">Back to Start Here</a><span>Then scroll down only when you want the graph, contexts and records.</span></div>`;
    hero.insertAdjacentElement('afterend',box);
  }
  fetch('knowledge/guides/branch-reader-guides.json')
    .then(r=>r.ok?r.json():Promise.reject(new Error('guide load failed')))
    .then(data=>{guides=data.guides||{};render();const reader=document.querySelector('#reader');if(reader)new MutationObserver(()=>render()).observe(reader,{childList:true,subtree:false});window.addEventListener('hashchange',render)})
    .catch(()=>{});
})();