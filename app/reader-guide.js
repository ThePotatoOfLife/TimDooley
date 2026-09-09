(()=>{
  let guides={};
  let guidesReady=false;

  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  function currentBranch(){
    const hero=document.querySelector('#reader .branchhero[data-branch-view]');
    if(hero?.dataset.branchView)return hero.dataset.branchView;
    const m=location.hash.match(/^#branch=(.+)$/);
    return m?decodeURIComponent(m[1]):null;
  }

  function render(branchId=currentBranch()){
    if(!guidesReady)return;
    const reader=document.querySelector('#reader');
    if(!reader)return;
    const hero=reader.querySelector('.branchhero');
    const existing=reader.querySelector('.reader-guide-panel');
    const g=branchId?guides[branchId]:null;

    if(!hero||!g){
      existing?.remove();
      return;
    }
    if(existing?.dataset.guideBranch===branchId)return;

    const box=document.createElement('section');
    box.className='reader-guide-panel';
    box.dataset.guideBranch=branchId;
    box.innerHTML=`
      <div class="reader-guide-kicker">READ THIS FIRST</div>
      <h3>${esc(g.reader_question)}</h3>
      <p class="reader-guide-answer">${esc(g.short_answer)}</p>
      ${g.learn_first?.length?`<div class="reader-guide-row"><span>Learn first</span><div>${g.learn_first.map(x=>`<b>${esc(x)}</b>`).join('')}</div></div>`:''}
      ${g.do_not_start_with?.length?`<div class="reader-guide-row muted"><span>Skip for now</span><div>${g.do_not_start_with.map(x=>`<b>${esc(x)}</b>`).join('')}</div></div>`:''}
      <div class="reader-guide-actions"><a href="learn/">Back to Start Here</a><span>Then scroll down only when you want the graph, contexts and records.</span></div>`;
    existing?.remove();
    hero.insertAdjacentElement('afterend',box);
  }

  window.addEventListener('potato:navigation',event=>{
    const {type,id}=event.detail||{};
    if(type==='branch')render(id);
  });

  const scriptBase=document.currentScript?.src||location.href;

  // Timeline explorer is a presentation module layered on top of the canonical archive.
  // Loading it here avoids coupling timeline-specific rendering to app.js.
  if(!document.querySelector('link[data-potato-timeline]')){
    const css=document.createElement('link');
    css.rel='stylesheet';
    css.href=new URL('timeline.css',scriptBase).href;
    css.dataset.potatoTimeline='1';
    document.head.appendChild(css);
  }
  if(!document.querySelector('script[data-potato-timeline]')){
    const timeline=document.createElement('script');
    timeline.src=new URL('timeline.js',scriptBase).href;
    timeline.defer=true;
    timeline.dataset.potatoTimeline='1';
    document.head.appendChild(timeline);
  }

  const guideUrl=new URL('../knowledge/guides/branch-reader-guides.json',scriptBase).href;
  fetch(guideUrl)
    .then(r=>r.ok?r.json():Promise.reject(new Error('guide load failed')))
    .then(data=>{
      guides=data.guides||{};
      guidesReady=true;
      render();
    })
    .catch(()=>{});
})();